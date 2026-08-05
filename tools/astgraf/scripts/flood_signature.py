# ABOUTME: Pre-registered test of the TAUGHT flood signature in its own category:
# ABOUTME: does "Neptune on Ketu" fire at flood dates more than at era-matched controls?
#
# ============================ PRE-REGISTRATION ============================
# Written and COMMITTED BEFORE the test was run (standing method ruling).
#
# WHY THIS TEST. Every doctrine grading so far has used the QUAKE corpus.
# "Giant on a node — Neptune on Ketu" is taught as a FLOOD constraint
# (Hyderabad 2016: 1.15 deg observed; Nepal 2015: 0.34 deg real). Until the
# flood corpora existed (2026-08-05) it had never been tested in the category
# it was taught in. This is that test.
#
# HYPOTHESIS (NU's doctrine, stated as a falsifiable claim):
#   Flood dates carry the Neptune-on-Ketu contact more often than instants
#   drawn from the same era do.
# DIRECTION PREDICTED: event rate HIGHER than control rate (lift > 1).
#
# CORPUS: data/floods-historical.csv + data/floods-hanze-europe.csv, rows with
#   date_precision == "day" and year >= 1700 (day precision puts every acting
#   body except the Moon inside a 3 deg orb; the engine drifts to
#   degrees-level before ~1700). n = 2,750 before declustering.
#
# DECLUSTERING: events within 3 days of a retained event collapse to one,
#   keeping the higher fatality count. TEMPORAL ONLY — HANZE locations are
#   country centroids, so spatial declustering is meaningless here, and one
#   European episode otherwise appears as several country rows on adjacent
#   days. n = 1,886 after declustering (measured while writing this design).
#
# CONTROLS — the load-bearing choice. Flood reporting density rises ~12x
#   across the span (36 events/decade in the 1870s to 447 in the 2000s), so
#   UNIFORM controls would hand any era-locked slow-body predicate a trivial
#   win — exactly the artifact that once promoted sep:Uranus-Neptune@opp to
#   lift 55 in this project. Controls are therefore ERA-MATCHED: for each
#   retained event, 5 instants drawn uniformly from +-365 days of it,
#   excluding +-7 days. This holds the era (and thus the reporting regime and
#   the slow bodies' epoch) fixed, while the Neptune-Ketu separation still
#   sweeps ~27 deg/year — ample against a 3 deg orb. Seed 42.
#
# PRIMARY PREDICATE (one, fixed): real-Neptune conjunct Ketu, orb 3.0 deg
#   (ASPECT_ORB). "real-" is the Mathcad ahead-position, the doctrine's own
#   timing channel.
#
# STATISTIC: add-one smoothed lift = (e+1)/(E+2) / ((c+1)/(C+2)).
# VERDICT: permutation p over 2,000 shuffles of the event/control labels
#   within era blocks; p < 0.05 with lift > 1 supports the doctrine.
#
# SECONDARY (reported, NOT the verdict, and multiplicity-corrected as a
#   family): observed-Neptune on Ketu; real-Neptune on Rahu; real-Uranus on
#   Ketu/Rahu; and the pair at orb 1.0. These exist to show the shape of the
#   result, not to be mined for a winner — the family max carries its own
#   permutation p.
#
# POWER CHECK (mandatory, same script): plant the predicate into a known
#   fraction of events and confirm the statistic recovers it.
# ==========================================================================

import csv
import math
import random

from astgraf.anchors import chart_at
from astgraf.bands import real_longitude
from astgraf.ephemeris import julian_day_number
from astgraf.signatures import ASPECT_ORB

FILES = ("data/floods-historical.csv", "data/floods-hanze-europe.csv")
CONTROLS_PER_EVENT = 5
CONTROL_WINDOW_DAYS = 365.0
CONTROL_EXCLUDE_DAYS = 7.0
N_PERM = 2000
SEED = 42
PRIMARY = ("real:Neptune", "Ketu", ASPECT_ORB)
SECONDARY = [("Neptune", "Ketu", ASPECT_ORB), ("real:Neptune", "Rahu", ASPECT_ORB),
             ("real:Uranus", "Ketu", ASPECT_ORB), ("real:Uranus", "Rahu", ASPECT_ORB),
             ("real:Neptune", "Ketu", 1.0)]


def _sep(a, b):
    d = abs(a - b) % 360.0
    return min(d, 360.0 - d)


def _lon(chart, name):
    if name.startswith("real:"):
        return real_longitude(chart, name[5:])
    return chart.positions[name].longitude


def fires(jd, a, b, orb):
    chart = chart_at(jd)
    return _sep(_lon(chart, a), _lon(chart, b)) <= orb


def load_events():
    rows = []
    for f in FILES:
        rows += list(csv.DictReader(open(f)))

    def year(r):
        return int(r["time"][:4]) if not r["time"].startswith("-") else -1

    def jd(r):
        t = r["time"]
        return float(julian_day_number(int(t[:4]), int(t[5:7]), int(t[8:10])))

    use = [r for r in rows if r["date_precision"] == "day" and year(r) >= 1700]
    use.sort(key=jd)
    kept = []
    for r in use:
        if not kept or jd(r) - jd(kept[-1]) > 3:
            kept.append(r)
        elif int(r["deaths"] or 0) > int(kept[-1]["deaths"] or 0):
            kept[-1] = r
    return [jd(r) for r in kept], len(use)


def lift(e_hits, n_e, c_hits, n_c):
    return ((e_hits + 1) / (n_e + 2)) / ((c_hits + 1) / (n_c + 2))


def main():
    events, raw = load_events()
    rng = random.Random(SEED)
    controls = []          # controls[i] = list of jds era-matched to events[i]
    for jd in events:
        block = []
        while len(block) < CONTROLS_PER_EVENT:
            off = rng.uniform(-CONTROL_WINDOW_DAYS, CONTROL_WINDOW_DAYS)
            if abs(off) > CONTROL_EXCLUDE_DAYS:
                block.append(jd + off)
        controls.append(block)
    n_e, n_c = len(events), sum(len(b) for b in controls)
    print(f"flood events: {raw} day-precision >= 1700 -> {n_e} after "
          f"3-day declustering; controls {n_c} (era-matched +-1 y)")

    def score(a, b, orb):
        ev = [fires(jd, a, b, orb) for jd in events]
        ct = [[fires(jd, a, b, orb) for jd in blk] for blk in controls]
        return ev, ct

    ev, ct = score(*PRIMARY)
    e_hits, c_hits = sum(ev), sum(sum(b) for b in ct)
    obs = lift(e_hits, n_e, c_hits, n_c)
    print(f"\nPRIMARY  real-Neptune conj Ketu @ {ASPECT_ORB} deg")
    print(f"  events {e_hits}/{n_e} = {e_hits/n_e:.4f}   "
          f"controls {c_hits}/{n_c} = {c_hits/n_c:.4f}   lift {obs:.3f}")

    # Permutation WITHIN era blocks: shuffle which of the 6 instants in each
    # block (1 event + 5 controls) is labelled the event.
    def perm_lift(rng2, blocks):
        eh = ch = 0
        for flags in blocks:
            k = rng2.randrange(len(flags))
            eh += flags[k]
            ch += sum(flags) - flags[k]
        return lift(eh, n_e, ch, n_c)

    blocks = [[ev[i]] + ct[i] for i in range(n_e)]
    rng2 = random.Random(SEED + 1)
    null = [perm_lift(rng2, blocks) for _ in range(N_PERM)]
    p = sum(1 for v in null if v >= obs) / N_PERM
    null.sort()
    print(f"  null median {null[N_PERM//2]:.3f}, 95th {null[int(N_PERM*0.95)]:.3f}"
          f"   ->  p = {p:.4f}")

    print("\nSECONDARY (reported, not the verdict):")
    fam = []
    for a, b, orb in SECONDARY:
        e2, c2 = score(a, b, orb)
        eh2, ch2 = sum(e2), sum(sum(x) for x in c2)
        L = lift(eh2, n_e, ch2, n_c)
        fam.append((L, [[e2[i]] + c2[i] for i in range(n_e)]))
        print(f"  {a} - {b} @ {orb}: ev {eh2/n_e:.4f} ctl {ch2/n_c:.4f} lift {L:.3f}")
    fam_obs = max(L for L, _ in fam + [(obs, blocks)])
    rng3 = random.Random(SEED + 2)
    fam_null = []
    all_blocks = [blocks] + [b for _, b in fam]
    for _ in range(N_PERM // 4):
        fam_null.append(max(perm_lift(rng3, blk) for blk in all_blocks))
    fp = sum(1 for v in fam_null if v >= fam_obs) / len(fam_null)
    print(f"  family max lift {fam_obs:.3f}, family-wise p = {fp:.4f}")

    print("\nPOWER CHECK — plant the predicate into a fraction of events:")
    for frac in (0.10, 0.05, 0.02):
        planted = list(ev)
        k = int(n_e * frac)
        idx = [i for i in range(n_e) if not planted[i]][:k]
        for i in idx:
            planted[i] = True
        pb = [[planted[i]] + ct[i] for i in range(n_e)]
        L = lift(sum(planted), n_e, c_hits, n_c)
        rng4 = random.Random(SEED + 3)
        pn = [perm_lift(rng4, pb) for _ in range(500)]
        print(f"  +{int(frac*100):>2}% of events -> lift {L:.3f}, "
              f"p = {sum(1 for v in pn if v >= L)/500:.4f}")


if __name__ == "__main__":
    main()
