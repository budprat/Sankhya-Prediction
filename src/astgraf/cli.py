# ABOUTME: astgraf CLI: computes a stellar-position period grid and writes the modern
# ABOUTME: replacements for ASTROC.GRF and the GRAPHDO screen: CSV, JSON, SVGs, aspects.

import argparse
import csv
import json
import re
from pathlib import Path

from .aspects import find_events
from .ephemeris import BODY_ORDER
from .grid import build_rows, label_for_jd, make_chart_at_jd, make_pos_at_jd
from .horary import find_sub_crossings, horary_position
from .locator import locate
from .precession import render_precession_wheel, report_lines
from .scope import render_scope
from .models import (ChartMoment, GridSpec, PeriodUnit,
                     parse_latitude, parse_longitude, parse_utc_offset)
from .svgplot import render, render_sequence

ACCURACY_NOTE = ("Keplerian mean elements calibrated near epoch 1900: minute-level timing "
                 "near the modern era; positions drift by degrees at tens of millennia, so "
                 "deep-time plots are qualitative (cycle shapes), not minute-accurate.")


def _parse_time(text: str) -> tuple[int, int]:
    match = re.fullmatch(r"(\d{1,2}):(\d{2})", text.strip())
    if not match:
        raise argparse.ArgumentTypeError("time must be HH:MM (24h)")
    return int(match.group(1)), int(match.group(2))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="astgraf",
                                description="Stellar-position period graphs "
                                            "(modern ASTGRAF/GRAPHDO)")
    p.add_argument("--year", type=int, required=True,
                   help="start year (astronomical numbering; negatives allowed)")
    p.add_argument("--month", type=int, default=1)
    p.add_argument("--day", type=int, default=1)
    p.add_argument("--time", default="12:00", help="local time HH:MM (24h)")
    p.add_argument("--unit", choices=[u.value for u in PeriodUnit], default="year")
    p.add_argument("--step", type=float, default=1.0)
    p.add_argument("--count", type=int, default=60)
    p.add_argument("--utc-offset", default="+00:00", help="e.g. +05:30")
    p.add_argument("--lon", default="0", help="longitude, e.g. 76:57E or -76.95")
    p.add_argument("--lat", default="0", help="latitude, e.g. 28:48N or 28.8")
    p.add_argument("--tropical", action="store_true",
                   help="tropical zodiac (default is sidereal with the suite ayanamsa)")
    p.add_argument("--koch", action="store_true",
                   help="Koch-style Ascendant (real obliquity); default is the equal path")
    p.add_argument("--style", choices=["wrapped", "cosine"], default="wrapped")
    p.add_argument("--locate", action="store_true",
                   help="write locations.csv: the light-time event spot for each aspect "
                        "event involving Jupiter/Saturn/Uranus/Neptune")
    p.add_argument("--precession", type=float, default=None, metavar="YEAR",
                   help="print the 25,739-year precession clock for YEAR and write "
                        "precession_wheel.svg (28-sector wheel with the equinox needle)")
    p.add_argument("--precession-zero", type=float, default=1996.0, metavar="YEAR",
                   help="anchor year when the equinox sat at wheel 0 (default 1996, "
                        "from the Secrets of Sankhya arithmetic)")
    p.add_argument("--scope", action="store_true",
                   help="render scope-chart wheels (aspect lines within orb): one per "
                        "period row plus one at each refined aspect-event moment")
    p.add_argument("--orb", type=float, default=3.0,
                   help="aspect orb in degrees for scope wheels (default 3.0)")
    p.add_argument("--horary", action="store_true",
                   help="write the 252-division horary grid (horary.csv) and "
                        "sub-boundary crossing events (horary_events.csv)")
    p.add_argument("--ayanamsa-rate", type=float, default=None, metavar="ARCSEC",
                   help="ayanamsa arcsec/year override (e.g. 50.35); default keeps "
                        "the suite formula 151/10800 deg/yr")
    p.add_argument("--ayanamsa-zero", type=int, default=294, metavar="YEAR",
                   help="ayanamsa zero year for the rate override (default 294)")
    p.add_argument("--no-aspects", action="store_true")
    p.add_argument("--aspect-bodies", default=None, metavar="A,B,...",
                   help="restrict aspect detection to these bodies "
                        "(e.g. Uranus,Neptune,Ketu); plotting is unaffected")
    p.add_argument("--out", default="astgraf-out")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    hour, minute = _parse_time(args.time)
    start = ChartMoment(
        year=args.year, month=args.month, day=args.day, hour=hour, minute=minute,
        utc_offset_hours=parse_utc_offset(args.utc_offset),
        longitude_east=parse_longitude(args.lon),
        latitude_north=parse_latitude(args.lat),
        sidereal=not args.tropical, equal_houses=not args.koch,
        ayanamsa_rate_arcsec=args.ayanamsa_rate, ayanamsa_zero_year=args.ayanamsa_zero)
    spec = GridSpec(unit=PeriodUnit(args.unit), step=args.step, count=args.count)

    aspect_bodies = None
    if args.aspect_bodies is not None:
        aspect_bodies = [b.strip() for b in args.aspect_bodies.split(",") if b.strip()]
        unknown = [b for b in aspect_bodies if b not in BODY_ORDER]
        if unknown:
            build_parser().error(f"unknown aspect bodies: {', '.join(unknown)} "
                                 f"(choose from {', '.join(BODY_ORDER)})")

    rows = build_rows(start, spec)
    events = []
    if not args.no_aspects:
        events = find_events(rows, pos_at_jd=make_pos_at_jd(start), bodies=aspect_bodies)
        for e in events:
            e.label = label_for_jd(e.jd)

    out = Path(args.out)
    (out / "svg").mkdir(parents=True, exist_ok=True)

    with open(out / "positions.csv", "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["index", "label", "jd", *BODY_ORDER])
        for r in rows:
            writer.writerow([r.index, r.label, f"{r.jd:.6f}",
                             *(f"{p.longitude:.6f}" for p in r.positions)])

    payload = {
        "params": {
            "year": args.year, "month": args.month, "day": args.day, "time": args.time,
            "utc_offset": args.utc_offset, "longitude_east": start.longitude_east,
            "latitude_north": start.latitude_north,
            "zodiac": "tropical" if args.tropical else "sidereal",
            "houses": "koch" if args.koch else "equal",
            "unit": spec.unit.value, "step": spec.step, "count": spec.count,
            "ayanamsa_formula": "(year - 294) * 151 / 10800",
            "accuracy_note": ACCURACY_NOTE,
        },
        "rows": [r.model_dump() for r in rows],
        "aspect_events": [e.model_dump() for e in events],
    }
    (out / "positions.json").write_text(json.dumps(payload, indent=2))

    if not args.no_aspects:
        with open(out / "aspects.csv", "w", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow(["body_a", "body_b", "kind", "jd", "label"])
            for e in events:
                writer.writerow([e.body_a, e.body_b, e.kind, f"{e.jd:.6f}", e.label])

    if args.horary:
        with open(out / "horary.csv", "w", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow(["index", "label", "jd", "body", "longitude", "division",
                             "nakshatra", "division_lord", "sub", "sub_lord",
                             "subsub", "subsub_lord"])
            for r in rows:
                for p in r.positions:
                    h = horary_position(p.longitude)
                    writer.writerow([r.index, r.label, f"{r.jd:.6f}", p.name,
                                     f"{p.longitude:.6f}", h.division, h.nakshatra,
                                     h.division_lord, h.sub, h.sub_lord,
                                     h.subsub, h.subsub_lord])
        crossings = find_sub_crossings(rows, pos_at_jd=make_pos_at_jd(start),
                                       bodies=aspect_bodies)
        with open(out / "horary_events.csv", "w", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow(["body", "from_sub", "to_sub", "boundary_deg", "jd", "label"])
            for c in crossings:
                writer.writerow([c.body, c.from_sub, c.to_sub,
                                 f"{c.boundary_deg:.6f}", f"{c.jd:.6f}",
                                 label_for_jd(c.jd)])
        print(f"  horary: {len(rows) * len(BODY_ORDER)} grid rows, "
              f"{len(crossings)} sub crossings")

    if args.locate:
        if not events:
            print("  locate: no aspect events (is --no-aspects set?); nothing to locate")
        else:
            chart_at = make_chart_at_jd(start)
            located = []
            for e in events:
                result = chart_at(e.jd)
                for body in (e.body_a, e.body_b):
                    spot = locate(result, body)
                    if spot:
                        located.append((e, spot))
            with open(out / "locations.csv", "w", newline="") as fh:
                writer = csv.writer(fh)
                writer.writerow(["jd", "label", "body_a", "kind", "body_b", "body",
                                 "light_minutes", "culmination_longitude_east",
                                 "event_longitude_east", "event_latitude_north"])
                for e, s in located:
                    writer.writerow([f"{e.jd:.6f}", e.label, e.body_a, e.kind, e.body_b,
                                     s.body, s.light_minutes,
                                     f"{s.culmination_longitude_east:.4f}",
                                     f"{s.event_longitude_east:.4f}",
                                     f"{s.event_latitude_north:.4f}"])
            print(f"  locate: {len(located)} event spots -> {out / 'locations.csv'}")
            for e, s in located[:6]:
                ew = "E" if s.event_longitude_east >= 0 else "W"
                ns = "N" if s.event_latitude_north >= 0 else "S"
                print(f"    {e.label}  {e.body_a} {e.kind} {e.body_b}: {s.body} spot "
                      f"{abs(s.event_longitude_east):.2f}{ew} "
                      f"{abs(s.event_latitude_north):.2f}{ns}")

    if args.precession is not None:
        for line in report_lines(args.precession, zero_year=args.precession_zero):
            print(line)
        (out / "precession_wheel.svg").write_text(
            render_precession_wheel(args.precession, zero_year=args.precession_zero))
        print(f"  wrote {out / 'precession_wheel.svg'}")

    if args.scope:
        scope_dir = out / "scope"
        scope_dir.mkdir(parents=True, exist_ok=True)
        for r in rows:
            positions = {p.name: p.longitude for p in r.positions}
            (scope_dir / f"row_{r.index:02d}.svg").write_text(
                render_scope(positions, title=r.label, orb=args.orb))
        event_cap = 100
        if events:
            pos_at = make_pos_at_jd(start)
            for i, e in enumerate(events[:event_cap]):
                title = f"{e.label} — {e.body_a} {e.kind} {e.body_b}"
                stem = f"event_{i:03d}_{e.body_a}-{e.kind}-{e.body_b}"
                (scope_dir / f"{stem}.svg").write_text(
                    render_scope(pos_at(e.jd), title=title, orb=args.orb))
            if len(events) > event_cap:
                print(f"  scope: rendered first {event_cap} of {len(events)} event "
                      "wheels; narrow with --aspect-bodies for full coverage")
        print(f"  scope: {len(rows)} row wheels + "
              f"{min(len(events), event_cap)} event wheels -> {scope_dir}")

    for stem, svg in render_sequence(rows, BODY_ORDER, style=args.style, events=events):
        (out / "svg" / f"{stem}.svg").write_text(svg)
    combined = render(rows, BODY_ORDER, style=args.style, events=events,
                      title=f"astgraf — {rows[0].label} to {rows[-1].label}")
    (out / "svg" / "combined.svg").write_text(combined)

    print(f"astgraf: {len(rows)} periods ({spec.unit.value} x {spec.step}), "
          f"{rows[0].label} -> {rows[-1].label}")
    print(f"  wrote {out / 'positions.csv'}, positions.json, "
          f"{len(BODY_ORDER)} sequence SVGs + combined.svg")
    if not args.no_aspects:
        print(f"  {len(events)} aspect events -> {out / 'aspects.csv'}")
        for e in events[:10]:
            print(f"    {e.label}  {e.body_a} {e.kind} {e.body_b}")
        if len(events) > 10:
            print(f"    ... and {len(events) - 10} more")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
