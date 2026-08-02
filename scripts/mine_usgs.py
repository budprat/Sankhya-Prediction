# ABOUTME: Stage 2/3 driver (v2, audit batch 3): declustered corpus, circular controls,
# ABOUTME: 2-year-block split, smoothed lifts, and a permutation-calibrated verdict.
import csv

from astgraf.signatures import (mine_lifts, pair_keys, permutation_max_lift,
                                run_corpus)

BLOCK_DAYS = 730.5      # split blocks: 2 years >= slow-aspect episode length

ne, nc = run_corpus("data/usgs-m7-1850-2020.csv", "out/signatures-m7-v2",
                    decluster_events=True, min_year=1900)
print(f"extracted {ne} declustered post-1900 event signatures, "
      f"{nc} time-uniform controls")

events = list(csv.DictReader(open("out/signatures-m7-v2/signatures.csv")))
controls = list(csv.DictReader(open("out/signatures-m7-v2/controls.csv")))
events.sort(key=lambda r: float(r["jd"]))

# 2-year-block alternating split (audit finding 14: even/odd events leaked —
# slow-planet episodes span both halves; blocks longer than an episode do not).
jd0 = float(events[0]["jd"])
half_a = [e for e in events if int((float(e["jd"]) - jd0) // BLOCK_DAYS) % 2 == 0]
half_b = [e for e in events if int((float(e["jd"]) - jd0) // BLOCK_DAYS) % 2 == 1]
# Grid controls split by the SAME time blocks as the events.
ctrl_a = [c for c in controls
          if int((float(c["jd"]) - jd0) // BLOCK_DAYS) % 2 == 0]
ctrl_b = [c for c in controls
          if int((float(c["jd"]) - jd0) // BLOCK_DAYS) % 2 == 1]

keys = pair_keys()
lifts_a = mine_lifts(half_a, ctrl_a, keys)
print(f"\nscreened {len(keys) * 4} predicates on block-half A "
      f"({len(half_a)} events vs {len(ctrl_a)} controls); top 10 by lift:")
print(f"{'predicate':34s} {'liftA':>7s} {'evA%':>6s} {'ctA%':>6s} {'liftB':>7s} {'evB%':>6s}")
top = lifts_a[:10]
b_index = {r["predicate"]: r for r in mine_lifts(half_b, ctrl_b, keys, min_event_rate=0.0)}
for r in top:
    b = b_index.get(r["predicate"], {})
    lb = b.get("lift", "-")
    print(f"{r['predicate']:34s} {r['lift']:>7} {100*r['event_rate']:6.1f} "
          f"{100*r['control_rate']:6.1f} {str(lb):>7s} {100*b.get('event_rate',0):6.1f}")

# Permutation-calibrated verdict on the FULL set (audit finding 15): the max
# smoothed lift any predicate reaches under label shuffling is the bar.
full_lifts = mine_lifts(events, controls, keys)
observed_max = full_lifts[0]["lift"]
null = permutation_max_lift(events, controls, keys, n_perm=200, seed=42)
null_sorted = sorted(null)
p = sum(1 for v in null if v >= observed_max) / len(null)
print(f"\npermutation null (200 perms): observed max lift {observed_max} "
      f"[top predicate {full_lifts[0]['predicate']}]")
print(f"null median {null_sorted[len(null)//2]:.3f}, "
      f"95th pct {null_sorted[int(0.95*len(null))]:.3f}, p = {p:.3f}")

# Locator null check: real epicenter-vs-own-spots minimum distance, against a
# shuffled pairing (event i's epicenter vs event i+37's spots).
from astgraf.signatures import _gc_km


def min_loc(row):
    vals = [float(row[f"loc_km:{b}"]) for b in ("Jupiter", "Saturn", "Uranus", "Neptune")]
    return min(vals)


real = sorted(min_loc(e) for e in events)
median_real = real[len(real) // 2]
n = len(events)
shuffled = []
for i, e in enumerate(events):
    other = events[(i + 37) % n]
    dists = [_gc_km(float(e["lat"]), float(e["lon"]),
                    float(other[f"spot_lat:{b}"]), float(other[f"spot_lon:{b}"]))
             for b in ("Jupiter", "Saturn", "Uranus", "Neptune")]
    shuffled.append(min(dists))
shuffled.sort()
print(f"\nlocator: median nearest-spot distance {median_real:.0f} km "
      f"(shuffled-null median {shuffled[len(shuffled)//2]:.0f} km)")
