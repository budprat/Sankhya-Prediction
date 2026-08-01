# ABOUTME: astgraf-bands CLI: sweep the Predict.pdf 28x11 band table over a date range,
# ABOUTME: merge trigger episodes, locate catastrophic ones, score against a catalog xlsx.

import argparse
import csv
import datetime as dt
from pathlib import Path

from .bands import (BAND_BODIES, find_episodes, parse_event_window,
                    score_events, trigger_state)
from .ephemeris import compute_raw
from .grid import label_for_jd
from .locator import locate

SITE_FREE = dict(engine_gmt=0.0, engine_longitude=0.0, latitude_north=0.0,
                 sidereal=True, equal_houses=True)


def load_catalog(path: str) -> list[dict]:
    import openpyxl
    sheet = openpyxl.load_workbook(path, data_only=True).active
    events = []
    for row in sheet.iter_rows(min_row=2, values_only=True):
        try:
            year = int(str(row[1]).strip())
        except (TypeError, ValueError):
            continue
        events.append({"place": str(row[4] or "").strip(),
                       "window": parse_event_window(year, row[2], row[3])})
    return events


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="astgraf-bands",
                                description="Predict.pdf band-coincidence scanner")
    p.add_argument("--start", required=True, help="sweep start date YYYY-MM-DD")
    p.add_argument("--days", type=int, required=True)
    p.add_argument("--level", type=int, choices=(0, 1, 2), default=0,
                   help="grid level: 0=28 bands, 1=/9 (1.43 deg), 2=/63 (0.20 deg)")
    p.add_argument("--step-hours", type=float, default=None,
                   help="sweep step; defaults to 12h/1h/0.2h for levels 0/1/2 "
                        "(must resolve the Moon's dwell in one division)")
    p.add_argument("--proximity", action="store_true",
                   help="fire on the trio's circular spread <= the level span, "
                        "grid-free (NU ruling); giants escalate within one span")
    p.add_argument("--catalog", default=None, help="disaster catalog .xlsx to score")
    p.add_argument("--window-days", type=float, default=3.0)
    p.add_argument("--out", default="bands-out")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    start = dt.date.fromisoformat(args.start)
    step_hours = args.step_hours or {0: 12.0, 1: 1.0, 2: 0.2}[args.level]
    steps = int(args.days * 24 / step_hours)
    step_days = step_hours / 24.0

    samples = []
    results = {}
    for k in range(steps):
        hours = k * step_hours
        result = compute_raw(start.year, start.month, start.day, hours, **SITE_FREE)
        state = trigger_state(result, level=args.level, proximity=args.proximity)
        samples.append((result.jd, label_for_jd(result.jd), state))
        if state.fired:
            results[result.jd] = result

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "sweep.csv", "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["jd", "label", "level", "band", "division", "nakshatra",
                         "members", "giants", "spread_deg"])
        for jd, label, state in samples:
            writer.writerow([f"{jd:.5f}", label, state.level, state.band or "",
                             state.division or "", state.nakshatra,
                             " ".join(state.members), " ".join(state.giants),
                             f"{state.spread_deg:.3f}" if state.spread_deg else ""])

    episodes = find_episodes(samples, step_days=step_days)
    with open(out / "episodes.csv", "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["start", "end", "band", "division", "nakshatra", "level",
                         "giants", "giant_spots"])
        for e in episodes:
            spots = []
            for giant in e.giants:
                spot = locate(results[e.start_jd], giant)
                if spot:
                    spots.append(f"{giant}:{spot.event_longitude_east:.2f}E,"
                                 f"{spot.event_latitude_north:.2f}N")
            writer.writerow([e.start_label, e.end_label, e.band, e.division,
                             e.nakshatra, e.level, " ".join(e.giants),
                             "; ".join(spots)])

    fired = sum(1 for _, _, s in samples if s.fired)
    print(f"astgraf-bands: {steps} samples ({args.start} +{args.days}d @ "
          f"{step_hours:g}h, level {args.level}), {fired} fired, "
          f"{len(episodes)} episodes")
    for e in episodes:
        extra = f" + {'/'.join(e.giants)}" if e.giants else ""
        division = f" div {e.division}" if args.level else ""
        mode = " proximity" if args.proximity else ""
        print(f"  {e.start_label} -> {e.end_label}  band {e.band}{division} "
              f"({e.nakshatra}) {e.level}{mode}{extra}")

    if args.catalog:
        events = load_catalog(args.catalog)
        rows, summary = score_events(episodes, events, args.window_days,
                                     start, start + dt.timedelta(days=args.days))
        with open(out / "catalog_score.csv", "w", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow(["place", "window_start", "window_end", "precision",
                             "hit", "p_chance"])
            for r in rows:
                w = r["window"]
                writer.writerow([r["place"], w[0], w[1], r["precision"],
                                 r["hit"], r["p_chance"]])
        print(f"  catalog: {summary['events']} events, {summary['hits']} hit by a "
              f"trigger episode (±{args.window_days:g}d)")
        print(f"  trigger-day fraction {summary['trigger_day_fraction']}, "
              f"expected hits by chance ≈ {summary['expected_hits_by_chance']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
