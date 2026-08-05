# ABOUTME: The configuration-similarity engine and recurrence calendar (NU's recurrence
# ABOUTME: principle): find when an anchor's slow pattern re-forms, triggers to the minute.
#
# Two-layer doctrine, as machinery: an anchor's PATTERN is its slow layer — the
# doctrine-orb contacts at the anchor instant, excluding Moon pairs (the fast
# hand). An EPISODE is a span where the whole pattern (or --min-match of it)
# stands simultaneously within orb again; its tightest instant is refined below
# one minute. Within an episode, the anchor's own Moon contacts are completed
# and refined to the minute — the fast hand dating the window, exactly as in
# the taught instances. Timing only: no spots (location layer is experimental,
# WATCHLIST amendment v5).

import argparse
import csv
import json
from pathlib import Path

from .anchors import (ANCHORS_PATH, Anchor, chart_at, contacts_at, iso_jd,
                      jd_iso_minute, load_anchors)
from .bands import (BAND_BODIES, circular_spread, division_of,
                    real_longitude, vyuha_state)
from .signatures import ASPECT_ORB, ASPECTS

MINUTE = 1.0 / 1440.0
FAST_SCAN_BODIES = {"Sun", "Mercury", "Venus"}


def _sep(a: float, b: float) -> float:
    d = abs(a - b) % 360.0
    return min(d, 360.0 - d)


def _delta(chart, contact) -> float:
    """Distance from exactness for one contact at one chart."""
    if contact["kind"] == "rsep":
        lon_a = real_longitude(chart, contact["a"])
    else:
        lon_a = chart.positions[contact["a"]].longitude
    lon_b = chart.positions[contact["b"]].longitude
    return abs(_sep(lon_a, lon_b) - ASPECTS[contact["aspect"]])


def anchor_pattern(anchor: Anchor) -> list[dict]:
    """The anchor's slow pattern: doctrine-orb contacts at its instant, Moon
    pairs excluded (the Moon is the fast hand, not the configuration)."""
    return [c for c in contacts_at(iso_jd(anchor.time))
            if c["within_doctrine_orb"] and "Moon" not in (c["a"], c["b"])]


def composite_conditions(anchor: Anchor) -> dict:
    """The anchor's OTHER layers at its instant — the state a contact pattern
    alone cannot express (recurrence gap 'composite multi-condition matching').
    Contacts say which pairs are locked; these say what the band table and the
    fourfold array were doing while they were."""
    chart = chart_at(iso_jd(anchor.time))
    p = {n: chart.positions[n].longitude for n in BAND_BODIES}
    bands = [division_of(lon, 0) for lon in p.values()]
    # NOT rounded: a rounded-down threshold makes the anchor fail its own
    # test (Nepal/vyuham self-match by 0.00025 deg). Round at display only.
    return {
        "mkm_spread": circular_spread([p["Moon"], p["Ketu"], p["Mars"]]),
        "stack_max": max(bands.count(b) for b in set(bands)),
        "vyuha_level": vyuha_state(chart).level,
    }


def composite_match_at(conditions: dict, jd: float) -> bool:
    """Do the other layers stand as they did at the anchor? The vyuha level
    must match exactly (it is categorical); the band quantities must be at
    least as tight as the anchor's (a tighter stack is a stronger instance,
    never a mismatch)."""
    chart = chart_at(jd)
    p = {n: chart.positions[n].longitude for n in BAND_BODIES}
    bands = [division_of(lon, 0) for lon in p.values()]
    spread = circular_spread([p["Moon"], p["Ketu"], p["Mars"]])
    return (vyuha_state(chart).level == conditions["vyuha_level"]
            and spread <= conditions["mkm_spread"]
            and max(bands.count(b) for b in set(bands)) >= conditions["stack_max"])


def match_at(pattern: list[dict], jd: float) -> dict:
    chart = chart_at(jd)
    deltas = [_delta(chart, c) for c in pattern]
    return {"count": sum(1 for d in deltas if d <= ASPECT_ORB),
            "total": len(pattern),
            "tightness": round(sum(deltas), 3),
            "deltas": [round(d, 3) for d in deltas]}


def _refine_tightest(pattern, jd_lo, jd_hi, jd_start, need):
    """Minimize total separation SUBJECT TO the match level: an unconstrained
    sum drifts outside the episode (Valdivia 1960: the 4/5 sum minimum beats
    every 5/5 instant), so instants below `need` carry a step penalty."""
    def f(jd):
        m = match_at(pattern, jd)
        return m["tightness"] + 1000.0 * max(0, need - m["count"])
    best, step = jd_start, 0.25
    while step > 0.3 * MINUTE:
        local = [min(max(best + k * step, jd_lo), jd_hi) for k in range(-8, 9)]
        best = min(local, key=f)
        step /= 8.0
    return best


def find_episodes(pattern: list[dict], jd_start: float, jd_end: float,
                  min_match: int | None = None,
                  step: float | None = None,
                  anchor: Anchor | None = None) -> list[dict]:
    """Spans inside [jd_start, jd_end] where at least min_match (default: all)
    of the pattern's contacts stand within orb simultaneously; each with its
    tightest instant refined below one minute. The JOINT window of several
    contacts can be far narrower than any single contact's — windows shorter
    than the scan step are missed (Valdivia 1960's full window is < 1 day),
    so exhaustive scans should pass a finer `step` (0.25 d recovers it).

    Pass `anchor` for COMPOSITE matching: the other layers (band spread,
    stack, vyuha level) must also stand as they did at the anchor, so a
    composite episode set is always a subset of the contact-only one."""
    if not pattern:
        return []
    need = len(pattern) if min_match is None else min_match
    conditions = composite_conditions(anchor) if anchor is not None else None
    bodies = {c["a"] for c in pattern} | {c["b"] for c in pattern}
    if step is None:
        step = 1.0 if bodies & FAST_SCAN_BODIES else 5.0

    samples = []
    jd = jd_start
    while jd <= jd_end + 1e-9:
        samples.append((jd, match_at(pattern, jd)))
        jd += step

    episodes = []
    run = []
    for jd, m in samples + [(None, {"count": -1})]:
        if (m["count"] >= need and conditions is not None
                and not composite_match_at(conditions, jd)):
            m = {**m, "count": -1}          # contacts hold, other layers do not
        if m["count"] >= need:
            run.append((jd, m))
            continue
        if run:
            lo, hi = run[0][0], run[-1][0]
            seed = min(run, key=lambda r: r[1]["tightness"])[0]
            best = _refine_tightest(pattern, lo - step, hi + step, seed, need)
            best_m = match_at(pattern, best)
            episodes.append({
                "start_jd": lo, "end_jd": hi,
                "start_utc": jd_iso_minute(lo)[:10],
                "end_utc": jd_iso_minute(hi)[:10],
                "best_jd": best, "best_utc": jd_iso_minute(best),
                "count": best_m["count"], "total": best_m["total"],
                "tightness": best_m["tightness"],
                "contacts": [
                    {"key": f"{c['kind']}:{c['a']}-{c['b']}@{c['aspect']}",
                     "delta": d}
                    for c, d in zip(pattern, best_m["deltas"])]})
            run = []
    return episodes


def moon_triggers(anchor: Anchor, episode: dict) -> list[dict]:
    """The anchor's own Moon contacts completed inside the episode, each
    refined below one minute — the fast hand dating the window."""
    moon_contacts = [c for c in contacts_at(iso_jd(anchor.time))
                     if c["within_doctrine_orb"] and "Moon" in (c["a"], c["b"])]
    out = []
    step = 0.5 / 24.0
    lo, hi = episode["start_jd"] - 0.5, episode["end_jd"] + 0.5
    for c in moon_contacts:
        grid = []
        jd = lo
        while jd <= hi + 1e-9:
            grid.append((jd, _delta(chart_at(jd), c)))
            jd += step
        for (jd_p, d_p), (jd_c, d_c), (jd_n, d_n) in zip(grid, grid[1:], grid[2:]):
            if d_c <= d_p and d_c < d_n and d_c < ASPECT_ORB:
                best, s = jd_c, step
                while s > 0.3 * MINUTE:
                    local = [best + k * s for k in range(-8, 9)]
                    best = min(local, key=lambda j: _delta(chart_at(j), c))
                    s /= 8.0
                out.append({"key": f"{c['kind']}:{c['a']}-{c['b']}@{c['aspect']}",
                            "jd": best, "utc": jd_iso_minute(best),
                            "delta": round(_delta(chart_at(best), c), 3)})
    out.sort(key=lambda t: t["jd"])
    return out


def render_text(anchor_id: str, episodes: list[dict],
                triggers: dict[int, list[dict]]) -> str:
    lines = [f"RECURRENCE — {anchor_id}: {len(episodes)} episode(s)"]
    for i, e in enumerate(episodes):
        lines.append(f"  {e['start_utc']} .. {e['end_utc']}  "
                     f"match {e['count']}/{e['total']}  "
                     f"tightest {e['best_utc']} (sum {e['tightness']:.2f} deg)")
        for c in e["contacts"]:
            lines.append(f"      {c['key']:<28} {c['delta']:.2f} deg")
        for t in triggers.get(i, []):
            lines.append(f"      fast hand: {t['key']}  exact {t['utc']}  "
                         f"(residual {t['delta']:.3f})")
    lines.append("")
    return "\n".join(lines)


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(
        description="Recurrence calendar: when does an anchor's slow pattern "
                    "re-form? Episodes with tightest instants and Moon "
                    "triggers to the minute. Timing only — no spots.")
    parser.add_argument("--data", default=ANCHORS_PATH)
    parser.add_argument("--anchor", help="anchor id (default: every anchor)")
    parser.add_argument("--category",
                        help="restrict to one anchor category "
                             "(earthquake | flood | biological | volcanic | "
                             "configuration) — Predict.pdf's design is "
                             "explicitly per category")
    parser.add_argument("--composite", action="store_true",
                        help="require the anchor's OTHER layers (band "
                             "spread, stack, vyuha level) to stand too")
    parser.add_argument("--start", required=True, help="YYYY-MM-DD")
    parser.add_argument("--end", help="YYYY-MM-DD (or use --years)")
    parser.add_argument("--years", type=float, help="span from --start")
    parser.add_argument("--min-match", type=int,
                        help="contacts required simultaneously (default: all)")
    parser.add_argument("--out", help="directory for recurrence.csv/.txt/.json")
    args = parser.parse_args(argv)

    jd_start = iso_jd(args.start + "T00:00:00Z")
    if args.end:
        jd_end = iso_jd(args.end + "T00:00:00Z")
    elif args.years:
        jd_end = jd_start + args.years * 365.25
    else:
        raise SystemExit("need --end or --years")

    anchors = load_anchors(args.data)
    if args.category:
        known = sorted({a.category for a in anchors})
        if args.category not in known:
            raise SystemExit(f"unknown category: {args.category} (have: "
                             + ", ".join(known) + ")")
        anchors = [a for a in anchors if a.category == args.category]
    if args.anchor:
        anchors = [a for a in anchors if a.id == args.anchor]
        if not anchors:
            raise SystemExit(f"unknown anchor: {args.anchor}")

    calendar = []
    texts = []
    for a in anchors:
        pattern = anchor_pattern(a)
        episodes = find_episodes(pattern, jd_start, jd_end, args.min_match,
                                 anchor=a if args.composite else None)
        triggers = {i: moon_triggers(a, e) for i, e in enumerate(episodes)}
        texts.append(render_text(a.id, episodes, triggers))
        for i, e in enumerate(episodes):
            calendar.append({
                "anchor": a.id, "category": a.category,
                "start": e["start_utc"], "end": e["end_utc"],
                "best_utc": e["best_utc"], "match": e["count"],
                "total": e["total"], "tightness": e["tightness"],
                "contacts": "; ".join(f"{c['key']}={c['delta']:.2f}"
                                      for c in e["contacts"]),
                "fast_triggers": "; ".join(f"{t['key']}@{t['utc']}"
                                           for t in triggers[i])})
    calendar.sort(key=lambda r: r["best_utc"])

    text = "\n".join(texts)
    if args.out:
        out = Path(args.out)
        out.mkdir(parents=True, exist_ok=True)
        with open(out / "recurrence.csv", "w", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=[
                "anchor", "category", "start", "end", "best_utc", "match", "total",
                "tightness", "contacts", "fast_triggers"])
            writer.writeheader()
            writer.writerows(calendar)
        (out / "recurrence.txt").write_text(text)
        (out / "recurrence.json").write_text(json.dumps(calendar, indent=2))
        print(f"wrote {out}/recurrence.csv/.txt/.json ({len(calendar)} rows)")
    else:
        print(text)


if __name__ == "__main__":
    main()
