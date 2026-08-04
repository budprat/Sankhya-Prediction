# ABOUTME: Does the cos-fold mirror crossing carry predictive content, or is it just
# ABOUTME: a faithful redraw of the author's graph? Same corpus/protocol as mining v2.
#
# Run from tools/astgraf:  uv run python scripts/mirror_lifts.py
# Reads out/signatures-m7-v2/{signatures,controls}.csv for their jd columns —
# the SAME declustered post-1900 events and time-uniform controls the audited
# v2 mining used — recomputes each chart, and scores mirror predicates
# (|lon_a + lon_b| ≡ 0) with the same add-one smoothed lift and the same
# permutation-calibrated bar that retired the mined aspect rules.
# Writes out/mirror-lifts/summary.txt.
import csv
import math
import random
import statistics
from pathlib import Path

from astgraf.aspects import mirror_offset
from astgraf.bands import real_longitude
from astgraf.ephemeris import compute_raw
from astgraf.grid import jd_to_calendar
from astgraf.signatures import BAND_BODIES, REAL_BODIES

BASE = Path(__file__).resolve().parent.parent
DIR = BASE / "out" / "signatures-m7-v2"
OUT = BASE / "out" / "mirror-lifts" / "summary.txt"
ORBS = (3.0, 1.0)
N_PERM = 200

lines: list[str] = []


def say(msg: str) -> None:
    print(msg)
    lines.append(msg)


def chart(jd):
    jdn = math.floor(jd + 0.5)
    y, m, d = jd_to_calendar(jdn)
    return compute_raw(y, m, d, (jd + 0.5 - jdn) * 24, 0.0, 0.0, 0.0,
                       True, True)


def mirror_features(jd):
    """|mirror offset| for every pair — observed, and real-giant vs observed."""
    c = chart(jd)
    p = {b: c.positions[b].longitude for b in BAND_BODIES}
    out = {}
    for i, a in enumerate(BAND_BODIES):
        for b in BAND_BODIES[i + 1:]:
            out[f"mir:{a}-{b}"] = abs(mirror_offset(p[a], p[b]))
    for g in REAL_BODIES:
        rg = real_longitude(c, g)
        for b in BAND_BODIES:
            if b != g:
                out[f"rmir:{g}-{b}"] = abs(mirror_offset(rg, p[b]))
    return out


def lifts(events, controls, keys, orb, min_event_rate=0.02):
    res = []
    for key in keys:
        eh = sum(1 for s in events if s[key] <= orb)
        if eh / len(events) < min_event_rate:
            continue
        ch = sum(1 for s in controls if s[key] <= orb)
        lift = (((eh + 1) / (len(events) + 2))
                / ((ch + 1) / (len(controls) + 2)))
        res.append({"predicate": key, "event_hits": eh,
                    "event_rate": round(eh / len(events), 4),
                    "control_rate": round(ch / len(controls), 4),
                    "lift": round(lift, 3)})
    res.sort(key=lambda r: -r["lift"])
    return res


def permutation_max_lift(events, controls, keys, orb, n_perm, seed=42):
    """Shuffle which pooled charts count as events; record the best lift any
    mirror predicate reaches by chance — the bar an observed lift must clear."""
    rows = events + controls
    n_e, n = len(events), len(events) + len(controls)
    hit_sets = {k: [s[k] <= orb for s in rows] for k in keys}
    rng = random.Random(seed)
    out = []
    idx = list(range(n))
    for _ in range(n_perm):
        rng.shuffle(idx)
        ev = set(idx[:n_e])
        best = 0.0
        for k in keys:
            h = hit_sets[k]
            eh = sum(1 for i in ev if h[i])
            if eh / n_e < 0.02:
                continue
            ch = sum(h) - eh
            lift = (((eh + 1) / (n_e + 2))
                    / ((ch + 1) / (n - n_e + 2)))
            best = max(best, lift)
        out.append(best)
    return out


def main():
    with open(DIR / "signatures.csv", newline="") as fh:
        ev_jd = [float(r["jd"]) for r in csv.DictReader(fh)]
    with open(DIR / "controls.csv", newline="") as fh:
        ct_jd = [float(r["jd"]) for r in csv.DictReader(fh)]
    say(f"mirror predicates over the v2 corpus: {len(ev_jd)} declustered "
        f"post-1900 events vs {len(ct_jd)} time-uniform controls")
    events = [mirror_features(j) for j in ev_jd]
    controls = [mirror_features(j) for j in ct_jd]
    keys = sorted(events[0])
    say(f"{len(keys)} mirror predicates (55 observed pairs + real-giant pairs)")

    for orb in ORBS:
        # Aggregate first: does an event chart carry MORE mirror hits at all?
        e_counts = [sum(1 for k in keys if s[k] <= orb) for s in events]
        c_counts = [sum(1 for k in keys if s[k] <= orb) for s in controls]
        say("")
        say(f"--- orb {orb} deg ---")
        say(f"mirror hits per chart: events mean {statistics.mean(e_counts):.3f} "
            f"(median {statistics.median(e_counts)}), controls mean "
            f"{statistics.mean(c_counts):.3f} (median {statistics.median(c_counts)})")

        table = lifts(events, controls, keys, orb)
        if not table:
            say("no predicate clears the 2% event-rate floor")
            continue
        say("top 5 by smoothed lift:")
        for r in table[:5]:
            say(f"   {r['predicate']:26s} lift {r['lift']:5.2f}  "
                f"events {r['event_rate']:.4f}  controls {r['control_rate']:.4f}"
                f"  (n={r['event_hits']})")
        null = permutation_max_lift(events, controls, keys, orb, N_PERM)
        obs = table[0]["lift"]
        p = sum(1 for x in null if x >= obs) / len(null)
        say(f"permutation null ({N_PERM} perms): observed max lift {obs:.3f} vs "
            f"null median {statistics.median(null):.3f}, "
            f"95th pct {sorted(null)[int(0.95 * len(null))]:.3f} — p = {p:.3f}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
