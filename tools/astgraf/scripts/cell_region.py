# ABOUTME: Pre-registered test of the author's own location design: do the 28x11 matrix
# ABOUTME: cells prefer geographic regions? (Predict.pdf's "confirmed event synchronisation".)
#
# ============================ PRE-REGISTRATION ============================
# Written and committed BEFORE the test was run (NU standing method ruling,
# 2026-08-05: pre-register cell, direction and statistic; one test, no
# re-tuning).
#
# HYPOTHESIS (the author's, Predict.pdf + briefing): each of the 28x11
#   band-by-body matrix cells accumulates "confirmed event synchronisation
#   factors from areas of our interest" — i.e. a cell, when it fires, prefers
#   particular AREAS on Earth. This is a LEARNED table, not a geometric
#   construction, and therefore is not subject to the sub-planet declination
#   ceiling that kills every geometric family (44.4% of M7+ unreachable by the
#   four giants; 38.5% even with lunar latitude restored).
#
# CORPUS: data/usgs-m7-1850-2020.csv, post-1900, declustered 7d/500km — the
#   same 1,435 mainshocks every other grading used. M7+ ONLY (NU ruling
#   2026-08-05: "we will stick to only major events above M7").
#
# CELL: (body, band) with band = division_of(longitude, level 0) = the 28
#   equal 12.857-degree divisions of Predict.pdf's own table, evaluated at the
#   event instant. 11 BAND_BODIES x 28 bands = 308 possible cells. Every event
#   fires exactly 11 cells (one per body).
#
# STATISTIC: spherical concentration of a cell's epicenters — the resultant
#   length R = |sum of unit vectors| / n, in [0,1]; R=1 means all events at one
#   point, R~0 means dispersed. DIRECTION PREDICTED: real R HIGHER than null.
#
# QUALIFYING CELLS: n >= 15 events (fixed in advance; scanning all 308 and
#   taking the winner is exactly the winner's curse that killed the dwell
#   finding at n=44).
#
# FAMILY STATISTIC: max R over qualifying cells (one number, so the
#   multiplicity across cells is handled by construction).
#
# NULL: shuffle EPICENTERS across events, holding each event's band-vector
#   fixed. This preserves the catalog's own geography exactly (the same set of
#   epicenters, same seismic belts) and the cell sizes exactly, destroying only
#   the sky-to-place pairing. 500 shuffles, seed 42.
#
# VERDICT RULE: p = fraction of shuffles whose max R >= the observed max R.
#   p < 0.05 => the cell-region table has content; otherwise the author's
#   empirical location design is refuted on M7+ like the five geometric ones.
#
# POWER CHECK (run in the same script, so a null cannot be mistaken for
#   blindness): plant a known region preference into a synthetic cell and
#   confirm the same statistic recovers it.
# ==========================================================================

import csv
import math
import random

from astgraf.anchors import chart_at
from astgraf.bands import BAND_BODIES, division_of
from astgraf.ephemeris import julian_day_number
from astgraf.signatures import decluster

CATALOG = "data/usgs-m7-1850-2020.csv"
MIN_COUNT = 15
N_SHUFFLES = 500
SEED = 42


def jd_of(iso):
    y, m, d = int(iso[0:4]), int(iso[5:7]), int(iso[8:10])
    h = int(iso[11:13]) + int(iso[14:16]) / 60 + float(iso[17:19]) / 3600
    return julian_day_number(y, m, d) + h / 24 - 0.5


def unit(lat, lon):
    p, l = math.radians(lat), math.radians(lon)
    return (math.cos(p) * math.cos(l), math.cos(p) * math.sin(l), math.sin(p))


def resultant(vecs):
    n = len(vecs)
    sx = sum(v[0] for v in vecs)
    sy = sum(v[1] for v in vecs)
    sz = sum(v[2] for v in vecs)
    return math.sqrt(sx * sx + sy * sy + sz * sz) / n


def main():
    with open(CATALOG, newline="") as fh:
        rows = [r for r in csv.DictReader(fh)
                if r.get("time") and r.get("latitude") and r.get("longitude")
                and int(r["time"][0:4]) >= 1900]
    rows = decluster(rows)
    print(f"corpus: {len(rows)} declustered M7+ mainshocks (post-1900)")

    vecs = [unit(float(r["latitude"]), float(r["longitude"])) for r in rows]
    # each event's cell vector: one (body, band) key per body
    cellvecs = []
    for r in rows:
        c = chart_at(jd_of(r["time"]))
        cellvecs.append(tuple((b, division_of(c.positions[b].longitude, 0))
                              for b in BAND_BODIES))

    def cell_index(assignment):
        """assignment[i] = index of the epicenter given to event i."""
        cells = {}
        for i, keys in enumerate(cellvecs):
            for k in keys:
                cells.setdefault(k, []).append(vecs[assignment[i]])
        return cells

    ident = list(range(len(rows)))
    cells = cell_index(ident)
    qualifying = {k: v for k, v in cells.items() if len(v) >= MIN_COUNT}
    print(f"cells: {len(cells)} populated, {len(qualifying)} with n >= {MIN_COUNT}")

    scored = sorted(((resultant(v), k, len(v)) for k, v in qualifying.items()),
                    reverse=True)
    obs = scored[0][0]
    print("\ntop 8 cells by concentration R:")
    for R, k, n in scored[:8]:
        print(f"  {k[0]:<9} band {k[1]:>2}   n {n:>4}   R {R:.4f}")

    rng = random.Random(SEED)
    worse = 0
    null_max = []
    for _ in range(N_SHUFFLES):
        perm = ident[:]
        rng.shuffle(perm)
        c = cell_index(perm)
        m = max(resultant(v) for k, v in c.items() if len(v) >= MIN_COUNT)
        null_max.append(m)
        if m >= obs:
            worse += 1
    null_max.sort()
    p = worse / N_SHUFFLES
    print(f"\nVERDICT: observed max R {obs:.4f}   null median "
          f"{null_max[N_SHUFFLES // 2]:.4f}   null 95th "
          f"{null_max[int(N_SHUFFLES * 0.95)]:.4f}   p = {p:.3f}")

    # ---- power check: plant a real region preference and re-measure ----
    print("\npower check — plant a region preference into one cell:")
    target = scored[len(scored) // 2][1]          # a mid-ranked real cell
    members = [i for i, keys in enumerate(cellvecs) if target in keys]
    for frac in (0.5, 0.3):
        planted = ident[:]
        # give a fraction of that cell's events epicenters from one tight area
        tight = [i for i, r in enumerate(rows)
                 if 30 <= float(r["latitude"]) <= 40
                 and 135 <= float(r["longitude"]) <= 145]
        if not tight:
            print("  (no tight donor region found)")
            break
        k = int(len(members) * frac)
        for j, i in enumerate(members[:k]):
            planted[i] = tight[j % len(tight)]
        c = cell_index(planted)
        m = max(resultant(v) for kk, v in c.items() if len(v) >= MIN_COUNT)
        hits = sum(1 for v in null_max if v >= m)
        print(f"  {int(frac*100)}% of cell {target} moved to Japan trench: "
              f"max R {m:.4f}, p = {hits / N_SHUFFLES:.3f}")


if __name__ == "__main__":
    main()
