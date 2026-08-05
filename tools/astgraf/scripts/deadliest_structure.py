# ABOUTME: Pre-registered test of whether DEATHS-selected earthquakes share configuration
# ABOUTME: structure more than MAGNITUDE-selected ones — a different population, same method.
#
# ============================ PRE-REGISTRATION ============================
# Written and COMMITTED BEFORE the test was run (standing method ruling).
#
# WHY THIS AND NOT A RERUN. The pinned corpus (USGS M7+) is MAGNITUDE-selected.
# The doctrine speaks about catastrophic events — human catastrophe, not
# seismic moment. Tangshan (Mw 7.5, ~300,000 dead) and Haiti (Mw 7.0,
# ~200,000 dead) are minor by magnitude and enormous by consequence; the M9
# shared-structure test (2026-08-05, null) could not see them because it
# selected on magnitude. data/quakes-historical.csv gives, for the first time,
# a DEATHS-selected tier. If the doctrine tracks catastrophe rather than
# moment, this is the population where it should show.
#
# HYPOTHESIS: the deadliest earthquakes share fired-contact structure with one
# another more than same-size samples of magnitude-selected events do.
# DIRECTION PREDICTED: mean pairwise similarity HIGHER than the null.
#
# SET UNDER TEST: rows of quakes-historical.csv with tier == "deadliest",
#   date_precision in (minute, day), year >= 1700. n = 12 (counted while
#   writing this design).
#
# *** POWER WARNING, REGISTERED IN ADVANCE ***
#   n = 12 gives 66 pairs. This is a SMALL test. It is run because the
#   population is new and the statistic is cheap, NOT because it can settle
#   the question. A null here means "no effect large enough for 12 events to
#   reveal", never "no effect". A positive here would need replication on a
#   larger deaths-selected catalogue (NCEI holds >5,700 such events) before it
#   means anything — the dwell finding died exactly this way at n = 44.
#
# STATISTIC: mean pairwise Jaccard similarity of fired-contact SETS. A contact
#   is any (kind, body-a, body-b, aspect) within ASPECT_ORB at the event
#   instant, exactly as the anchor dossiers compute them, Moon pairs included
#   (minute-precision rows support the Moon; day-precision rows do not, so the
#   Moon is EXCLUDED throughout for comparability — registered here, not
#   chosen later).
#
# NULL: 2,000 random same-size (n = 12) samples drawn WITHOUT replacement from
#   the 1,435 declustered post-1900 M7+ corpus, scored identically. Seed 42.
#
# VERDICT: p = fraction of null samples whose mean similarity >= observed.
#   p < 0.05 supports the hypothesis.
#
# POWER CHECK (mandatory): score a set of 12 events drawn from a single
#   12-month window — where the slow bodies are nearly identical by
#   construction — and confirm the statistic registers that as high.
# ==========================================================================

import csv
import random

from astgraf.anchors import contacts_at, iso_jd
from astgraf.ephemeris import julian_day_number
from astgraf.signatures import decluster

HIST = "data/quakes-historical.csv"
USGS = "data/usgs-m7-1850-2020.csv"
N_NULL = 2000
SEED = 42


def jd_of_iso(t):
    h = 0.0
    if len(t) > 12:
        h = int(t[11:13]) + int(t[14:16]) / 60 + float(t[17:19]) / 3600
    return julian_day_number(int(t[:4]), int(t[5:7]), int(t[8:10])) + h / 24 - 0.5


def contact_set(jd):
    """Fired contacts at an instant, Moon pairs excluded (day-precision rows
    cannot place the Moon: it crosses a full band in a day)."""
    return frozenset(
        (c["kind"], c["a"], c["b"], c["aspect"])
        for c in contacts_at(jd)
        if c["within_doctrine_orb"] and "Moon" not in (c["a"], c["b"]))


def mean_pairwise_jaccard(sets):
    tot = n = 0
    for i in range(len(sets)):
        for j in range(i + 1, len(sets)):
            u = len(sets[i] | sets[j])
            tot += (len(sets[i] & sets[j]) / u) if u else 0.0
            n += 1
    return tot / n if n else 0.0


def main():
    rows = list(csv.DictReader(open(HIST)))
    deadliest = [r for r in rows
                 if r["tier"] == "deadliest"
                 and r["date_precision"] in ("minute", "day")
                 and int(r["time"][:4]) >= 1700]
    k = len(deadliest)
    print(f"deaths-selected set under test: n = {k}")
    obs_sets = [contact_set(jd_of_iso(r["time"])) for r in deadliest]
    obs = mean_pairwise_jaccard(obs_sets)
    print(f"mean pairwise Jaccard similarity: {obs:.4f}  ({k*(k-1)//2} pairs)")

    with open(USGS, newline="") as fh:
        pool = [r for r in csv.DictReader(fh)
                if r.get("time") and r.get("latitude") and r.get("longitude")
                and int(r["time"][0:4]) >= 1900]
    pool = decluster(pool)
    pool_jd = [jd_of_iso(r["time"]) for r in pool]
    print(f"null pool: {len(pool)} magnitude-selected declustered M7+ events")

    cache = {}

    def cached(jd):
        if jd not in cache:
            cache[jd] = contact_set(jd)
        return cache[jd]

    rng = random.Random(SEED)
    null = []
    for _ in range(N_NULL):
        pick = rng.sample(pool_jd, k)
        null.append(mean_pairwise_jaccard([cached(j) for j in pick]))
    null.sort()
    p = sum(1 for v in null if v >= obs) / N_NULL
    print(f"null: median {null[N_NULL//2]:.4f}, 95th {null[int(N_NULL*0.95)]:.4f}")
    print(f"VERDICT: p = {p:.4f}")

    print("\npower check — 12 events inside one 12-month window "
          "(slow bodies near-identical by construction):")
    best = None
    for i in range(len(pool_jd) - k):
        span = pool_jd[i + k - 1] - pool_jd[i]
        if best is None or span < best[0]:
            best = (span, i)
    span, i = best
    tight = [cached(j) for j in pool_jd[i:i + k]]
    t = mean_pairwise_jaccard(tight)
    print(f"  tightest {k}-event window in the corpus spans {span:.0f} days: "
          f"similarity {t:.4f}, p = {sum(1 for v in null if v >= t)/N_NULL:.4f}")


if __name__ == "__main__":
    main()
