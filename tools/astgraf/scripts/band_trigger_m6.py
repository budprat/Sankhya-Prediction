# ABOUTME: The decisive test of Predict.pdf's band trigger — the same predicate that
# ABOUTME: reached p = 0.069 on 1,435 M7+ events, now on 12,212 held-out M6.0-6.99 events.
#
# ============================ PRE-REGISTRATION ============================
# Written and COMMITTED BEFORE the test was run (standing method ruling 1).
# The commit that adds this file contains NO results. Verifiable in git.
#
# WHY THIS TEST, AND WHY NOW. PLAN.md 3.2c names this "the one open question
# data can settle". The author's headline rule was graded on 2026-08-05 over
# 1,435 M7+ mainshocks and returned lift 1.804 at p = 0.069 — the closest any
# primary predicate has come in this project, and still short of its bar. The
# reason it could not be settled was never corpus size but PREDICATE RARITY:
# the trigger fires on 0.84% of events, so 1,435 events yield 12 firings
# against 7.0 expected, a 1.4 sigma excess. The arithmetic of the fix was
# stated at the time: if the 1.80 lift is real, n = 6,000 gives 3.2 sigma and
# n = 12,000 gives 4.6 sigma. We hold 12,212 M6.0-6.99 events. This test is
# therefore powered to settle a question that has stood open since the rule
# was first written down.
#
# THE POPULATION DECISION, MADE HERE AND NOT AFTER THE RESULT. Predict.pdf's
# claim is about MAJOR events ("disruptive"/"catastrophic"), and M6.0-6.99 is
# a different population from M7+. That cuts BOTH ways and both are binding:
#   * A POSITIVE result here would be strong evidence, because the rule was
#     never fitted to this band.
#   * A NULL here does NOT by itself refute the doctrine, because a mechanism
#     that switches on only above M7 would not appear at M6. That caveat is
#     registered in advance so it cannot be dismissed as special pleading
#     afterwards.
#   * BUT the M7+ result is itself only 1.4 sigma. So if M6 is null, the rule
#     is left resting on a 1.4 sigma excess and nothing else, and the honest
#     summary becomes "unsupported at every magnitude tested" rather than
#     "refuted".
#
# THE HOLDOUT COST, ACKNOWLEDGED. M6.0-6.99 is this project's only strictly
# disjoint held-out band (RESULTS.md #8 used it to kill the dwell doctrine).
# Spending it needs a question worth the price; this is that question. After
# this run the band is no longer clean for future confirmatory use, and that
# fact is recorded here rather than discovered later.
#
# HYPOTHESIS: M6.0-6.99 events carry the Moon-Ketu-Mars band coincidence more
#   often than era-matched instants do.
# DIRECTION PREDICTED: lift > 1. Predicted magnitude: ~1.80 if the M7+ point
#   estimate is real; anything at or below 1.0 refutes it for this band.
#
# CORPUS: data/usgs-m6-1900-2020.csv (USGS FDSN, minmag 6.0 maxmag 6.99,
#   1901-2020, n = 12,212), declustered 7 d / 500 km keep-largest, the
#   identical rule every other grading in this project used.
#
# PREDICATES, fixed in advance and IDENTICAL to scripts/band_trigger_grade.py
#   so the M6 and M7+ numbers are directly comparable:
#     P1 PRIMARY  circular spread of {Moon, Ketu, Mars} <= 12.857142857 deg
#                 (one band span), proximity mode, grid-free — NU's ruling.
#     P2          grid mode: all three share one of the 28 divisions.
#     P3          P1 AND a giant (Uranus/Neptune) within one band span of any
#                 trio member — the "catastrophic" form.
#   ONLY P1 CARRIES THE VERDICT. P2 and P3 are reported with a family-wise p
#   over the three, and are secondary by registration.
#
# CONTROLS: era-matched, 5 per event, +-365 d excluding +-7 d, seed 42 —
#   identical to the M7+ run. Holds the catalogue's completeness regime fixed
#   (M6 detection improves sharply with the WWSSN in the 1960s and again with
#   digital networks) while the Moon sweeps the zodiac many times inside the
#   window.
#
# STATISTIC: add-one smoothed lift (astgraf.validation.smoothed_lift).
# VERDICT RULE: within-block permutation null, 2,000 shuffles,
#   p < 0.05 AND lift > 1 supports the rule. Anything else does not.
# POWER CHECK (mandatory): plant P1 into 10/5/2% of events; a null is only
#   evidence if the instrument recovers a planted effect.
# SIGMA CHECK: poisson_sigma on the firing count, because a lift ratio on a
#   small count is how the M7+ run nearly fooled us.
#
# ONE TEST. NO RE-TUNING. NO SECOND LOOK AT A DIFFERENT ORB.
# ==========================================================================

import csv

from astgraf.anchors import chart_at
from astgraf.bands import GIANTS, circular_spread, division_of
from astgraf.ephemeris import julian_day_number
from astgraf.signatures import decluster
from astgraf.validation import (Claim, block_permutation_p, era_matched_controls,
                                poisson_sigma, power_curve, smoothed_lift)

CORPUS = "data/usgs-m6-1900-2020.csv"
TRIO = ("Moon", "Ketu", "Mars")
BAND_SPAN = 360.0 / 28
CONTROLS_PER_EVENT = 5
N_PERM = 2000
SEED = 42
OUT = "out/band-trigger-m6/summary.txt"


def _sep(a, b):
    d = abs(a - b) % 360.0
    return min(d, 360.0 - d)


def jd_of(iso: str) -> float:
    y, m, d = int(iso[0:4]), int(iso[5:7]), int(iso[8:10])
    tail, num = iso[17:], ""
    for ch in tail:
        if ch.isdigit() or ch == ".":
            num += ch
        else:
            break
    sec = float(num) if num else 0.0
    hours = int(iso[11:13]) + int(iso[14:16]) / 60 + sec / 3600
    return julian_day_number(y, m, d) + hours / 24 - 0.5


def predicates(jd):
    c = chart_at(jd)
    p = {b: c.positions[b].longitude for b in TRIO}
    spread = circular_spread([p[b] for b in TRIO])
    p1 = spread <= BAND_SPAN
    p2 = len({division_of(p[b], 0) for b in TRIO}) == 1
    esc = any(_sep(c.positions[g].longitude, p[b]) <= BAND_SPAN
              for g in GIANTS for b in TRIO)
    return p1, p2, (p1 and esc)


def main() -> None:
    lines = []

    def say(s=""):
        lines.append(s)
        print(s)

    claim = Claim(
        name="band-trigger-m6",
        hypothesis="M6.0-6.99 events carry the Moon-Ketu-Mars band coincidence "
                   "more often than era-matched instants do.",
        direction="higher",
        statistic="add-one smoothed lift on P1 (trio spread <= one band span)",
        control="era-matched, 5 per event, +-365 d excluding +-7 d, seed 42",
        corpus="USGS M6.0-6.99 1901-2020, declustered 7d/500km",
        verdict="p < 0.05 and lift > 1",
        power="plant P1 into 10/5/2% of events and confirm recovery",
        preregistered=True,
        notes="Held-out band, disjoint from the M7+ corpus by construction. "
              "Only P1 carries the verdict.",
    )
    say(claim.banner())
    say()

    rows = [r for r in csv.DictReader(open(CORPUS))
            if r.get("time") and r.get("latitude") and r.get("longitude")]
    say(f"loaded {len(rows)} M6.0-6.99 events")
    rows = decluster(rows)
    say(f"declustered (7 d / 500 km keep-largest): {len(rows)}")

    jds = [jd_of(r["time"]) for r in rows]
    control_jds = era_matched_controls(jds, CONTROLS_PER_EVENT, seed=SEED)

    ev = [predicates(jd) for jd in jds]
    ct = [[predicates(cj) for cj in block] for block in control_jds]
    n_e = len(ev)
    n_c = sum(len(b) for b in ct)
    say(f"cast {n_e} event charts and {n_c} era-matched control charts")
    say()

    results = []
    for k, name in enumerate(("P1 PRIMARY  trio spread <= one band span",
                              "P2          trio share one of the 28 divisions",
                              "P3          P1 + a giant within one band span")):
        eh = sum(1 for e in ev if e[k])
        ch = sum(1 for b in ct for c in b if c[k])
        L = smoothed_lift(eh, n_e, ch, n_c)
        blocks = [[ev[i][k]] + [c[k] for c in ct[i]] for i in range(n_e)]
        p = block_permutation_p(blocks, L, N_PERM)
        expected = (ch / n_c) * n_e if n_c else 0.0
        sig = poisson_sigma(eh, expected)
        results.append({"name": name, "lift": L, "p": p, "eh": eh, "ch": ch,
                        "expected": expected, "sigma": sig, "blocks": blocks})
        say(f"{name}")
        say(f"    events   {eh:>6} / {n_e}  ({100*eh/n_e:.2f}%)")
        say(f"    controls {ch:>6} / {n_c}  ({100*ch/n_c:.2f}%)")
        say(f"    lift {L:.3f}   p = {p:.4f}   "
            f"{eh} firings vs {expected:.1f} expected = {sig:.2f} sigma")
        say()

    p1 = results[0]
    say("-- power check on P1 (a null without power is silence) --")
    for row in power_curve(p1["blocks"]):
        say(f"    plant {int(row['fraction']*100):>3}% -> lift {row['lift']:.3f}, "
            f"p = {row['p']:.4f}")
    say()

    fam_p = min(1.0, 3 * min(r["p"] for r in results))     # Bonferroni over 3
    say(f"-- family-wise p over the three predicates (Bonferroni): {fam_p:.4f}")
    say()

    supported = p1["p"] < 0.05 and p1["lift"] > 1.0
    say(f"VERDICT on P1: {'SUPPORTED' if supported else 'NOT SUPPORTED'} "
        f"(bar: {claim.verdict})")
    say("  M7+ comparison (RESULTS.md #10): lift 1.804, p = 0.069, "
        "12 firings vs 7.0 expected (1.4 sigma)")
    say(f"  M6 result here:                  lift {p1['lift']:.3f}, "
        f"p = {p1['p']:.4f}, {p1['eh']} firings vs {p1['expected']:.1f} "
        f"expected ({p1['sigma']:.2f} sigma)")
    say()
    say("  Registered in advance: a null here does not refute a mechanism that")
    say("  switches on only above M7 — but it leaves the M7+ result resting on")
    say("  its own 1.4 sigma and nothing else.")

    import pathlib
    path = pathlib.Path(OUT)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
