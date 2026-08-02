# ABOUTME: astgraf-bands CLI: sweep the Predict.pdf 28x11 band table over a date range,
# ABOUTME: merge trigger episodes, locate catastrophic ones, score against a catalog xlsx.

import argparse
import csv
import datetime as dt
from pathlib import Path

from .bands import (BAND_BODIES, find_episodes, find_vyuha_episodes,
                    parse_event_window, score_events, trigger_state, vyuha_state)
from .ephemeris import compute_raw
from .grid import label_for_jd
from .locator import locate

# Koch Ascendant path throughout (NU ruling 2026-08-02, matching the BAS blank
# E/W answer and the tropical/Koch oracle charts the Asc rules were tuned on).
SITE_FREE = dict(engine_gmt=0.0, engine_longitude=0.0, latitude_north=0.0,
                 sidereal=True, equal_houses=False)


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
    p.add_argument("--rules", default=None, metavar="FILE.toml",
                   help="sweep every declarative trigger rule in the file "
                        "(see doctrine-triggers.toml) instead of built-in modes")
    p.add_argument("--site-lon", default=None, metavar="76:57E",
                   help="site longitude for Ascendant-based rules (rules "
                        "mentioning the Ascendant are skipped without a site)")
    p.add_argument("--site-lat", default=None, metavar="12:59N")
    p.add_argument("--utc-offset", default="+00:00",
                   help="sweep clock offset (labels stay UT)")
    p.add_argument("--vyuha", action="store_true",
                   help="detect Chatur Vyuham instead of band triggers: Sun-Saturn "
                        "and Jupiter-Neptune/Uranus oppositions crossing at 90 deg, "
                        "nodal-axis lock as aggravator (daily steps suffice)")
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
    if args.vyuha:
        step_hours = args.step_hours or 24.0
    else:
        step_hours = args.step_hours or {0: 12.0, 1: 1.0, 2: 0.2}[args.level]
    steps = int(args.days * 24 / step_hours)
    step_days = step_hours / 24.0

    if args.rules:
        return run_rules(args, start, steps, step_hours, step_days)
    if args.vyuha:
        return run_vyuha(args, start, steps, step_hours, step_days)

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


class _Span:
    def __init__(self, jd, label, level):
        self.start_jd = jd
        self.end_jd = jd
        self.start_label = label
        self.end_label = label
        self.level = level


def run_rules(args, start, steps, step_hours, step_days) -> int:
    from .grid import make_chart_at_jd
    from .models import (ChartMoment, parse_latitude, parse_longitude,
                         parse_utc_offset)
    from .triggers import (acting_body, evaluate_rule, load_rules,
                           mentions_ascendant, refine_episode_instant)
    rules = load_rules(args.rules)
    has_site = args.site_lon is not None and args.site_lat is not None
    skipped = [r.name for r in rules if mentions_ascendant(r) and not has_site]
    if skipped:
        print(f"  site-specific rules skipped (no --site-lon/--site-lat): "
              f"{', '.join(skipped)}")
        rules = [r for r in rules if r.name not in skipped]
    site_lon = parse_longitude(args.site_lon) if has_site else 0.0
    site_lat = parse_latitude(args.site_lat) if has_site else 0.0
    utc_offset = parse_utc_offset(args.utc_offset)
    moment = ChartMoment(year=start.year, month=start.month, day=start.day,
                         hour=0, minute=0, utc_offset_hours=utc_offset,
                         longitude_east=site_lon, latitude_north=site_lat,
                         equal_houses=False)
    chart_at = make_chart_at_jd(moment)
    spans: dict[str, list[_Span]] = {r.name: [] for r in rules}
    for k in range(steps):
        result = compute_raw(start.year, start.month, start.day, k * step_hours,
                             -utc_offset, -site_lon, site_lat, True, False)
        label = label_for_jd(result.jd)
        for rule in rules:
            state = evaluate_rule(result, rule)
            if not state.fired:
                continue
            existing = spans[rule.name]
            if existing and result.jd - existing[-1].end_jd <= step_days * 1.5:
                existing[-1].end_jd = result.jd
                existing[-1].end_label = label
                if state.level == "catastrophic":
                    existing[-1].level = "catastrophic"
            else:
                existing.append(_Span(result.jd, label, state.level))

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    rule_by_name = {r.name: r for r in rules}
    with open(out / "rules_episodes.csv", "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["rule", "start", "end", "level", "exact_instant",
                         "acting", "spot_lon_east", "spot_lat_north"])
        for name, episodes in spans.items():
            rule = rule_by_name[name]
            actor = acting_body(rule)
            for e in episodes:
                instant = spot_lon = spot_lat = ""
                if actor:
                    jd = refine_episode_instant(
                        chart_at, e.start_jd - step_days, e.end_jd + step_days, rule)
                    if jd is not None:
                        spot = locate(chart_at(jd), actor)
                        instant = label_for_jd(jd)
                        spot_lon = f"{spot.event_longitude_east:.2f}"
                        spot_lat = f"{spot.event_latitude_north:.2f}"
                writer.writerow([name, e.start_label, e.end_label, e.level,
                                 instant, actor or "", spot_lon, spot_lat])

    print(f"astgraf-bands --rules: {steps} samples ({args.start} +{args.days}d @ "
          f"{step_hours:g}h), {len(rules)} rules")
    for name, episodes in spans.items():
        print(f"  {name}: {len(episodes)} episodes")
        for e in episodes[:8]:
            print(f"    {e.start_label} -> {e.end_label}  {e.level}")

    if args.catalog:
        events = load_catalog(args.catalog)
        for name, episodes in spans.items():
            _, summary = score_events(episodes, events, args.window_days,
                                      start, start + dt.timedelta(days=args.days))
            print(f"  score[{name}]: {summary['hits']}/{summary['events']} hits, "
                  f"expected by chance ≈ {summary['expected_hits_by_chance']}")
    return 0


def run_vyuha(args, start, steps, step_hours, step_days) -> int:
    samples = []
    for k in range(steps):
        result = compute_raw(start.year, start.month, start.day,
                             k * step_hours, **SITE_FREE)
        samples.append((result.jd, label_for_jd(result.jd), vyuha_state(result)))

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "vyuha.csv", "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["jd", "label", "level", "partner", "sun_saturn_sep",
                         "partner_sep", "cross_deg", "node_align_deg",
                         "saturn_distance"])
        for jd, label, s in samples:
            writer.writerow([f"{jd:.5f}", label, s.level, s.partner,
                             f"{s.sun_saturn_sep:.3f}", f"{s.partner_sep:.3f}",
                             f"{s.cross_deg:.3f}", f"{s.node_align_deg:.3f}",
                             f"{s.saturn_distance:.6f}"])

    episodes = find_vyuha_episodes(samples, step_days=step_days)
    with open(out / "vyuha_episodes.csv", "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["start", "end", "level", "partner", "best_cross_deg",
                         "min_saturn_distance"])
        for e in episodes:
            writer.writerow([e.start_label, e.end_label, e.level, e.partner,
                             f"{e.best_cross_deg:.3f}",
                             f"{e.min_saturn_distance:.6f}"])

    fired = sum(1 for _, _, s in samples if s.fired)
    print(f"astgraf-bands --vyuha: {steps} samples ({args.start} +{args.days}d @ "
          f"{step_hours:g}h), {fired} fired, {len(episodes)} episodes")
    for e in episodes:
        print(f"  {e.start_label} -> {e.end_label}  {e.level}  Jupiter opp "
              f"{e.partner}, best cross {e.best_cross_deg:.2f} deg")

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
        print(f"  catalog: {summary['events']} events, {summary['hits']} hit "
              f"(±{args.window_days:g}d); trigger-day fraction "
              f"{summary['trigger_day_fraction']}, expected by chance ≈ "
              f"{summary['expected_hits_by_chance']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
