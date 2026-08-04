# ABOUTME: Four diagnostics on HOW a spot could be located: latitude feasibility,
# ABOUTME: point-vs-locus geometry, a stratified permutation, and split-half replication.
#
# Run from tools/astgraf:  uv run python scripts/spot_hypotheses.py
# Writes out/spot-hypotheses/summary.txt.
#
# Context: the sub-planet spot grades at chance (scripts/loc_backtest.py) and
# Ascendant-based rules are excluded (scripts/asc_fingerprint.py). These four
# ask what SHAPE a location rule could even have.
#   1. Feasibility — a declination->latitude rule can only ever reach |lat| <
#      ~23.7 deg. How many M7+ epicenters lie outside that? (Answer: 44%.)
#   2. Loci — a pulse along the planet-Earth axis marks not only the sub-point
#      but the antipode, the 90 deg "max shear" great circle, and the 45/135
#      small circles. Circles reach every latitude, so they escape (1).
#   3. Stratified permutation on the best of those, against the AUDITED
#      time-uniform controls (each site holds 1 real + 3 control instants;
#      under no-coupling the 'event' label is exchangeable among them).
#   4. Split-half replication over 2-year blocks — this project's standard.
import csv
import math
import random
import statistics
from pathlib import Path

from astgraf.anchors import chart_at
from astgraf.locator import _wrap180, equatorial

BASE = Path(__file__).resolve().parent.parent
DIR = BASE / "out" / "signatures-m7-v2"
OUT = BASE / "out" / "spot-hypotheses" / "summary.txt"
GIANTS = ["Jupiter", "Saturn", "Uranus", "Neptune"]
KM_PER_DEG = 111.319
THRESH = 5.0                    # degrees ~ 557 km
lines: list[str] = []
_cache: dict[float, dict] = {}


def say(msg: str) -> None:
    print(msg)
    lines.append(msg)


def subs(jd):
    """Sub-planet point (lat = declination, lon = RA - GMST) for each giant."""
    if jd not in _cache:
        c = chart_at(jd)
        d = {}
        for g in GIANTS:
            p = c.positions[g]
            ra, dec = equatorial(p.longitude % 360, p.ecliptic_latitude,
                                 c.obliquity)
            d[g] = (dec, _wrap180(ra - c.gmst))
        _cache[jd] = d
    return _cache[jd]


def angsep(la1, lo1, la2, lo2):
    p1, p2 = math.radians(la1), math.radians(la2)
    dl = math.radians(lo2 - lo1)
    return math.degrees(math.acos(max(-1.0, min(1.0,
        math.sin(p1) * math.sin(p2)
        + math.cos(p1) * math.cos(p2) * math.cos(dl)))))


def nearest(la, lo, jd):
    return min(angsep(la, lo, *subs(jd)[g]) for g in GIANTS)


def main():
    random.seed(7)
    with open(DIR / "signatures.csv", newline="") as fh:
        ev = [r for r in csv.DictReader(fh) if r.get("lat")]
    with open(DIR / "controls.csv", newline="") as fh:
        ct = [float(r["jd"]) for r in csv.DictReader(fh)]
    say(f"corpus: {len(ev)} declustered post-1900 M7+ events, "
        f"{len(ct)} time-uniform controls")

    # 1. Feasibility of any declination -> latitude rule.
    lats = [abs(float(r["lat"])) for r in ev]
    reach = 23.71                                  # widest giant declination
    out = sum(1 for x in lats if x > reach)
    say("")
    say("1. FEASIBILITY of a declination->latitude rule")
    say(f"   |epicenter latitude| median {statistics.median(lats):.1f} deg; "
        f"giant sub-points never leave +/-{reach:.2f} deg")
    say(f"   epicenters structurally unreachable: {out}/{len(lats)} = "
        f"{out / len(lats):.1%}  <-- a point-at-the-sub-planet rule cannot "
        "locate nearly half of all M7+ events, whatever its longitude")

    # 2. Point vs locus geometry.
    say("")
    say(f"2. LOCI (miss in degrees; {THRESH:.0f} deg = {THRESH*KM_PER_DEG:.0f} km)")
    sample = random.sample(ev, 500)
    pairs = [(float(r["lat"]), float(r["lon"]), float(r["jd"])) for r in sample]
    null_pairs = [(la, lo, jd) for la, lo, _ in pairs
                  for jd in random.sample(ct, 4)]

    def loci(d):
        return {"sub-point (0)": d, "antipode (180)": 180 - d,
                "shear circle (90)": abs(d - 90),
                "45/135 circles": min(abs(d - 45), abs(d - 135))}

    def collect(ps):
        acc = {k: [] for k in loci(0)}
        for la, lo, jd in ps:
            best = {k: 1e9 for k in acc}
            for g in GIANTS:
                for k, v in loci(angsep(la, lo, *subs(jd)[g])).items():
                    best[k] = min(best[k], v)
            for k, v in best.items():
                acc[k].append(v)
        return acc

    obs, null = collect(pairs), collect(null_pairs)
    say(f"   {'locus':20s} {'obs median':>11s} {'null median':>12s} "
        f"{'obs<=5':>8s} {'null<=5':>9s}")
    for k in obs:
        o, n = obs[k], null[k]
        say(f"   {k:20s} {statistics.median(o):8.2f}deg {statistics.median(n):9.2f}deg "
            f"{sum(1 for x in o if x <= THRESH)/len(o):8.4f} "
            f"{sum(1 for x in n if x <= THRESH)/len(n):9.4f}")
    say("   Only the sub-point separates from its null, and only in the "
        "tightest bin — the circle loci track the null exactly.")

    # 3. Stratified permutation on the sub-point, full corpus.
    strata = [(float(r["lat"]), float(r["lon"]),
               [float(r["jd"])] + random.sample(ct, 3)) for r in ev]
    hit = sum(1 for la, lo, js in strata if nearest(la, lo, js[0]) <= THRESH)
    draws = [sum(1 for la, lo, js in strata
                 if nearest(la, lo, random.choice(js)) <= THRESH)
             for _ in range(500)]
    p = sum(1 for x in draws if x >= hit) / len(draws)
    say("")
    say("3. STRATIFIED PERMUTATION, sub-point, full corpus")
    say(f"   observed {hit}/{len(strata)} within {THRESH:.0f} deg; null mean "
        f"{statistics.mean(draws):.1f}, 95th pct "
        f"{sorted(draws)[int(0.95*len(draws))]}; empirical p = {p:.4f}")
    say("   NOT a discovery: ~8 geometric variants were tried today, so the "
        "multiple-testing-corrected p is ~0.13. For calibration, this "
        "project's own mining null puts the best-of-many lift at 1.72 by "
        "chance — and this lift is 1.77.")

    # 4. Split-half replication over 2-year blocks.
    say("")
    say("4. SPLIT-HALF (2-year blocks)")
    halves = {0: [], 1: []}
    for r in ev:
        halves[int(int(r["label"][:4]) / 2) % 2].append(r)
    for h in (0, 1):
        st = [(float(r["lat"]), float(r["lon"]),
               [float(r["jd"])] + random.sample(ct, 3)) for r in halves[h]]
        o = sum(1 for la, lo, js in st if nearest(la, lo, js[0]) <= THRESH)
        d = [sum(1 for la, lo, js in st
                 if nearest(la, lo, random.choice(js)) <= THRESH)
             for _ in range(400)]
        m = statistics.mean(d)
        say(f"   half {h}: n={len(halves[h]):4d} observed {o:3d} null mean "
            f"{m:5.1f} lift {o/max(m, 1e-9):.2f} "
            f"p = {sum(1 for x in d if x >= o)/len(d):.3f}")
    say("   Same direction in both halves, significant in neither — a weak "
        "consistent effect, or a small-number artifact. Needs fresh data.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
