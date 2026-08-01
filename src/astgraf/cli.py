# ABOUTME: astgraf CLI: computes a stellar-position period grid and writes the modern
# ABOUTME: replacements for ASTROC.GRF and the GRAPHDO screen: CSV, JSON, SVGs, aspects.

import argparse
import csv
import json
import re
from pathlib import Path

from .aspects import find_events
from .ephemeris import BODY_ORDER
from .grid import build_rows, label_for_jd, make_pos_at_jd
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
    p.add_argument("--no-aspects", action="store_true")
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
        sidereal=not args.tropical, equal_houses=not args.koch)
    spec = GridSpec(unit=PeriodUnit(args.unit), step=args.step, count=args.count)

    rows = build_rows(start, spec)
    events = []
    if not args.no_aspects:
        events = find_events(rows, pos_at_jd=make_pos_at_jd(start))
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
