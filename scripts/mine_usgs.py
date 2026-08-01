# ABOUTME: Stage 2/3 driver: extract signatures for the USGS M7+ corpus, screen
# ABOUTME: predicates by lift on half A, validate survivors on held-out half B.
import csv
from astgraf.signatures import mine_lifts, pair_keys, run_corpus

ne, nc = run_corpus("data/usgs-m7-1850-2020.csv", "out/signatures-m7")
print(f"extracted {ne} event signatures, {nc} controls")

events = list(csv.DictReader(open("out/signatures-m7/signatures.csv")))
controls = list(csv.DictReader(open("out/signatures-m7/controls.csv")))
events.sort(key=lambda r: float(r["jd"]))

half_a = events[0::2]
half_b = events[1::2]
ids_a = {e["id"] for e in half_a}
ctrl_a = [c for c in controls if c["id"].split("~")[0] in ids_a]
ctrl_b = [c for c in controls if c["id"].split("~")[0] not in ids_a]

keys = pair_keys()
lifts_a = mine_lifts(half_a, ctrl_a, keys)
print(f"\nscreened {len(keys) * 4} predicates on half A "
      f"({len(half_a)} events vs {len(ctrl_a)} controls); top 10 by lift:")
print(f"{'predicate':34s} {'liftA':>7s} {'evA%':>6s} {'ctA%':>6s} {'liftB':>7s} {'evB%':>6s}")
top = lifts_a[:10]
b_index = {r["predicate"]: r for r in mine_lifts(half_b, ctrl_b, keys, min_event_rate=0.0)}
for r in top:
    b = b_index.get(r["predicate"], {})
    lb = b.get("lift", "-")
    print(f"{r['predicate']:34s} {r['lift']:>7} {100*r['event_rate']:6.1f} "
          f"{100*r['control_rate']:6.1f} {str(lb):>7s} {100*b.get('event_rate',0):6.1f}")

# Locator null check: real epicenter-vs-own-spots minimum distance, against a
# shuffled pairing (event i's epicenter vs event i+37's spots).
import math
def min_loc(row):
    vals = [float(row[f"loc_km:{b}"]) for b in ("Jupiter","Saturn","Uranus","Neptune")]
    return min(vals)
real = sorted(min_loc(e) for e in events)
median_real = real[len(real)//2]
n = len(events)
from astgraf.signatures import _gc_km
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
