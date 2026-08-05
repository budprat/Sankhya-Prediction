# ABOUTME: PLAN.md 3.1 — which Uranus-Neptune clock (163.5 / 164.5 / 171.0 y) do the
# ABOUTME: flood records support? Answer: none is discriminable, and here is the arithmetic.
#
# ============================ PRE-REGISTRATION ============================
# Written and COMMITTED BEFORE the inferential test was run. The commit that
# adds this file contains no results. Verifiable in git.
#
# PLAN.md 3.1 called this "the highest value" test still runnable without new
# input from NU. Working the design out honestly shows it is TWO questions,
# and only one of them is answerable:
#
#   Q1 WHICH CLOCK?  Deterministic arithmetic, no inference involved, so no
#      pre-registration is possible or needed — the answer follows from the
#      record length and the candidate periods alone. Reported as PART 1.
#
#   Q2 IS FLOOD INCIDENCE ELEVATED NEAR THE CONJUNCTION AT ALL?  Genuinely
#      inferential, and pre-registered below as PART 2.
#
# ---------------------------------------------------------------------------
# PART 1 — the discrimination limit (arithmetic, measured while designing)
#
# Candidate clocks on record: Neptune tropical 163.5 y, Neptune sidereal
# 164.5 y, Uranus-Neptune synodic 171.0 y. Over the systematic record
# (HANZE, 1871-2025 = 154 years) the accumulated PHASE difference between
# any two of them is:
#     163.5 vs 164.5   0.0057 cycles =  2.1 deg
#     163.5 vs 171.0   0.0413 cycles = 14.9 deg
#     164.5 vs 171.0   0.0356 cycles = 12.8 deg
# The record covers 0.90-0.94 of ONE cycle. Two periods cannot be told apart
# from less than one cycle unless their phase separation exceeds the precision
# with which the incidence maximum can be located — and flood reporting
# density rises ~12x across this span (36 events/decade in the 1870s to 447 in
# the 2000s), which blurs that location by far more than 15 degrees.
#
# CONCLUSION, fixed before any test: Q1 IS NOT ANSWERABLE with existing data.
# This is a structural limit, not a null result, and it is reported as such.
#
# ---------------------------------------------------------------------------
# PART 2 — the pre-registered inferential test
#
# HYPOTHESIS: flood incidence, after detrending for reporting rate, is
#   ELEVATED in the years around a Uranus-Neptune conjunction.
# DIRECTION PREDICTED: higher inside the conjunction window than outside.
#
# CORPUS: data/floods-hanze-europe.csv, day precision, 1871-2025 (n = 2,724).
#   HANZE is used ALONE and deliberately: it is the only systematically
#   collected flood catalogue here. The 88-event curated file is hand-picked
#   with no completeness model, and mixing a curated set into an incidence
#   test would import exactly the selection the test is trying to control.
#
# DETRENDING — the load-bearing step. Raw counts cannot be used: reporting
#   density rises ~12x across the span, so ANY window in the recent half wins
#   on archival grounds alone. Incidence is therefore expressed as a ratio to
#   a smooth local baseline (centred moving average of annual counts,
#   half-width 25 y, edge-truncated). The statistic is computed on that ratio.
#
# WINDOW: +-8 years of the 1993 conjunction epoch (the 1993 event was a TRIPLE
#   — Feb 2 / Aug 19 / Oct 25, all in Poorvashada pada 4 — so the "epoch" is
#   the year, not an instant). +-8 y is fixed in advance as roughly the span
#   over which the pair stays within the 3 deg census dwell orb.
#
# STATISTIC: mean detrended incidence ratio inside the window.
# NULL: every other +-8 y window the record can hold, stepped by one year
#   (a circular-shift null over the detrended series). p = the fraction of
#   candidate windows scoring at or above the conjunction window.
# VERDICT: p < 0.05.
#
# *** POWER LIMIT, REGISTERED IN ADVANCE AND BINDING ***
#   The systematic record contains EXACTLY ONE conjunction epoch (1993). The
#   1821 and 1650 conjunctions have ZERO usable events within +-10 years in
#   either corpus, curated included. So n = 1 INDEPENDENT EPOCH, whatever the
#   event count inside it — 670 HANZE events near 1993 are 670 observations of
#   one epoch, not 670 observations of the clock.
#
#   This is the same pseudo-replication that produced a false positive in
#   scripts/pattern_mine_m7.py earlier today (17 events, 3 epochs, family-wise
#   p = 0.010, dead on split-half). Registered consequence:
#     * A SIGNIFICANT result here is NOT evidence for the clock. It would say
#       the 1990s were a flood-rich decade relative to trend, which one
#       coincidence cannot separate from a real 171-year period.
#     * A NULL result IS informative in one direction only — it would mean the
#       single available epoch shows no elevation, which weakly disfavours a
#       large effect.
#   Either way the verdict on the DOCTRINE is "untested", and the honest
#   output of this script is the power statement, not the p-value.
#
# WHAT WOULD MAKE Q1 ANSWERABLE, stated so the blocker is actionable:
#   a systematically collected flood catalogue covering the 1821 conjunction
#   with a usable completeness model — i.e. reaching ~1780-1860 at day
#   precision. That is precisely the "1,000-year records list" NU has
#   mentioned but not yet shared (FRAMEWORK.md open question 7). Two epochs
#   would not settle the period either, but they would at least make the
#   question inferential rather than arithmetic.
#
# ONE TEST. NO RE-TUNING.
# ==========================================================================

import csv
from collections import Counter

from astgraf.validation import Claim

HANZE = "data/floods-hanze-europe.csv"
CONJUNCTION_YEAR = 1993          # the triple: Feb 2 / Aug 19 / Oct 25
WINDOW = 8                       # +-years
BASELINE_HALFWIDTH = 25          # years, for the reporting-rate trend
CLOCKS = {"Neptune tropical": 163.5, "Neptune sidereal": 164.5,
          "Uranus-Neptune synodic": 171.0}
OUT = "out/flood-clock/summary.txt"


CLAIM = Claim(
    name="flood-uranus-neptune-clock",
    hypothesis="Flood incidence, detrended for reporting rate, is elevated in "
               "the years around a Uranus-Neptune conjunction.",
    direction="higher",
    statistic="mean detrended incidence ratio inside a +-8 y window",
    control="circular-shift — every other +-8 y window in the detrended "
            "series, stepped by one year",
    corpus="HANZE Europe day-precision floods 1871-2025 (n = 2,724), the only "
           "systematically collected flood catalogue in the tree",
    verdict="p < 0.05",
    power="ONE independent conjunction epoch (1993) in the systematic record; "
          "1821 and 1650 have zero usable events within +-10 y. The test "
          "cannot distinguish a real 171-y period from one flood-rich decade",
    preregistered=True,
    notes="PLAN.md 3.1. Part 1 (which clock?) is arithmetic, not inference: "
          "the three candidates differ by at most 14.9 deg of phase across a "
          "record covering 0.9 of one cycle, so they are not discriminable. "
          "Part 2 is this claim. Whatever it returns, the doctrine verdict is "
          "UNTESTED.",
)


def annual_counts() -> dict[int, int]:
    rows = [r for r in csv.DictReader(open(HANZE))
            if r.get("date_precision") == "day" and r.get("time")]
    return Counter(int(r["time"][:4]) for r in rows)


def detrended(counts: dict[int, int]) -> dict[int, float]:
    """Incidence as a ratio to a centred moving average — the reporting-rate
    trend removed. Years whose baseline window is truncated at an edge keep
    the truncated mean; the circular-shift null sees the same treatment, so
    the comparison stays fair."""
    years = sorted(counts)
    lo, hi = years[0], years[-1]
    out = {}
    for y in range(lo, hi + 1):
        lo_w, hi_w = max(lo, y - BASELINE_HALFWIDTH), min(hi, y + BASELINE_HALFWIDTH)
        base = sum(counts.get(k, 0) for k in range(lo_w, hi_w + 1)) / (hi_w - lo_w + 1)
        out[y] = (counts.get(y, 0) / base) if base > 0 else 0.0
    return out


def window_score(series: dict[int, float], centre: int) -> float | None:
    ys = [centre + d for d in range(-WINDOW, WINDOW + 1)]
    vals = [series[y] for y in ys if y in series]
    if len(vals) < 2 * WINDOW + 1:
        return None                      # only fully-covered windows compete
    return sum(vals) / len(vals)


def main() -> None:
    lines: list[str] = []

    def say(s=""):
        lines.append(s)
        print(s)

    say(CLAIM.banner())
    say()
    say("=" * 74)
    say("PART 1 — WHICH CLOCK? (arithmetic; not answerable with this record)")
    say("=" * 74)
    counts = annual_counts()
    years = sorted(counts)
    span = years[-1] - years[0]
    say(f"  systematic record: {years[0]}-{years[-1]} = {span} years, "
        f"{sum(counts.values())} day-precision events")
    say(f"  {'clock':<26} {'period':>8} {'cycles covered':>15}")
    for name, p in CLOCKS.items():
        say(f"  {name:<26} {p:>7.1f}y {span/p:>14.2f}")
    say()
    say("  pairwise phase separation accumulated over the whole record:")
    names = list(CLOCKS)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            d = span * abs(1 / CLOCKS[a] - 1 / CLOCKS[b])
            say(f"    {a} vs {b}: {d:.4f} cycles = {d*360:.1f} deg")
    say()
    say("  VERDICT ON PART 1: NOT ANSWERABLE. Less than one cycle is covered,")
    say("  and the largest separation between any two candidates is under 15")
    say("  degrees of phase — far below the precision with which an incidence")
    say("  maximum can be located in a record whose reporting density rises")
    say("  ~12x across the same span. This is a structural limit of the data,")
    say("  not a null result about the doctrine.")
    say()

    say("=" * 74)
    say("PART 2 — IS INCIDENCE ELEVATED NEAR THE ONE AVAILABLE CONJUNCTION?")
    say("=" * 74)
    series = detrended(counts)
    obs = window_score(series, CONJUNCTION_YEAR)
    if obs is None:
        say("  the conjunction window is not fully covered; no test possible")
        return
    nulls = []
    for centre in range(years[0] + WINDOW, years[-1] - WINDOW + 1):
        if abs(centre - CONJUNCTION_YEAR) <= WINDOW:
            continue                     # overlapping windows are not controls
        s = window_score(series, centre)
        if s is not None:
            nulls.append((s, centre))
    nulls.sort(reverse=True)
    p = sum(1 for s, _ in nulls if s >= obs) / len(nulls)
    say(f"  detrending: incidence / centred {2*BASELINE_HALFWIDTH+1}-year mean")
    say(f"  conjunction window {CONJUNCTION_YEAR}+-{WINDOW}: "
        f"mean detrended incidence {obs:.4f}")
    say(f"  null: {len(nulls)} non-overlapping +-{WINDOW} y windows")
    say(f"    best {nulls[0][0]:.4f} (centre {nulls[0][1]}), "
        f"median {nulls[len(nulls)//2][0]:.4f}, "
        f"worst {nulls[-1][0]:.4f} (centre {nulls[-1][1]})")
    say(f"  p = {p:.4f}   ->  "
        f"{'SUPPORTED' if p < 0.05 else 'NOT SUPPORTED'} (bar: {CLAIM.verdict})")
    say()
    say("  rank of the conjunction window among all candidate windows: "
        f"{sum(1 for s, _ in nulls if s >= obs) + 1} of {len(nulls) + 1}")
    say()

    say("=" * 74)
    say("WHAT THIS DOES AND DOES NOT SETTLE")
    say("=" * 74)
    say("  The systematic record holds ONE conjunction epoch (1993). The 1821")
    say("  and 1650 conjunctions carry ZERO usable events within +-10 years in")
    say("  either corpus. So whatever Part 2 returned, it rests on n = 1")
    say("  independent epoch: the 670 HANZE events near 1993 are 670")
    say("  observations of one epoch, not 670 observations of a clock.")
    say("  Registered in advance, and binding: the doctrine verdict is")
    say("  UNTESTED, not supported and not refuted.")
    say()
    say("  UNBLOCKER: a systematically collected flood catalogue reaching")
    say("  ~1780-1860 at day precision, with a completeness model — i.e. the")
    say("  1,000-year records list NU has mentioned (FRAMEWORK open question")
    say("  7). Two epochs would still not fix the period, but they would make")
    say("  the question inferential rather than arithmetic.")

    import pathlib
    path = pathlib.Path(OUT)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
