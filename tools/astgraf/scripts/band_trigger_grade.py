# ABOUTME: Pre-registered grading of Predict.pdf's headline rule — Moon+Ketu+Mars in one
# ABOUTME: band, giants escalating — against 1,435 quakes and 1,886 floods, era-matched.
#
# ============================ PRE-REGISTRATION ============================
# Written and COMMITTED BEFORE the test was run (standing method ruling).
#
# WHY. This is the author's OWN primary predictive claim, stated in
# Predict.pdf: "if Moon, Knode and Mars calculated position is in Aswin
# 0-12.8 deg band we can anticipate a disruptive event. If Uranus and Neptune
# too is present there can be catastrophic events in the making." It has been
# scored ONCE, against a 31-episode disaster spreadsheet (grid mode 0/31 vs
# 0.63 expected; proximity mode 1/31 vs 1.79) — a sample far too small to
# detect anything short of an enormous effect. We now hold ~3,300 events.
#
# HYPOTHESIS: events carry the Moon-Ketu-Mars band coincidence more often
# than era-matched instants do. DIRECTION PREDICTED: lift > 1.
#
# PRIMARY CORPUS — QUAKES, and the reason matters: the rule contains the
# MOON, which moves 13.2 deg/day = one full band span per day. Only exact
# instants can test it. USGS M7+ 1850-2020, post-1900, declustered 7d/500km:
# n = 1,435 with catalog instants to the second.
#
# SECONDARY CORPUS — FLOODS (1,886 declustered day-precision events), run and
# reported but NOT the verdict: their times are nominal 12:00 UTC, so the
# Moon carries +-6.6 deg of uncertainty (half a band). Any flood result here
# is indicative only, and that caveat is part of the registration, not an
# excuse added afterwards.
#
# PREDICATES (fixed in advance):
#   P1 PRIMARY  proximity mode, NU's ruling: circular spread of
#               {Moon, Ketu, Mars} <= 12.857142857 deg (one band span),
#               grid-free — fixed cells quantize away real convergences.
#   P2          grid mode: all three share one of the 28 divisions.
#   P3          escalated: P1 AND a giant (Uranus or Neptune) within one band
#               span of any trio member — the "catastrophic" form.
#   Only P1 carries the verdict; P2 and P3 are reported with a family-wise p.
#
# CONTROLS: era-matched, exactly as the flood-signature test — 5 instants per
#   event drawn uniformly from +-365 days, excluding +-7 days. This holds the
#   catalogue's completeness regime fixed (quake detection improves sharply
#   after 1960; flood reporting rises ~12x across its span), while the Moon
#   sweeps the whole zodiac many times inside the window. Seed 42.
#
# STATISTIC: add-one smoothed lift. VERDICT: within-block permutation (which
#   of the 1 event + 5 controls is the event), 2,000 shuffles, p < 0.05 with
#   lift > 1 supports the rule.
#
# POWER CHECK (mandatory): plant the predicate into 10/5/2% of events.
# ==========================================================================

import csv
import random

from astgraf.validation import Claim, smoothed_lift
from astgraf.anchors import chart_at
from astgraf.bands import GIANTS, circular_spread, division_of
from astgraf.ephemeris import julian_day_number
from astgraf.signatures import decluster

BAND_SPAN = 360.0 / 28.0
TRIO = ("Moon", "Ketu", "Mars")
QUAKES = "data/usgs-m7-1850-2020.csv"
FLOODS = ("data/floods-historical.csv", "data/floods-hanze-europe.csv")
CONTROLS_PER_EVENT = 5
WINDOW, EXCLUDE = 365.0, 7.0
N_PERM = 2000
SEED = 42


def _sep(a, b):
    d = abs(a - b) % 360.0
    return min(d, 360.0 - d)


def quake_jds():
    with open(QUAKES, newline="") as fh:
        rows = [r for r in csv.DictReader(fh)
                if r.get("time") and r.get("latitude") and r.get("longitude")
                and int(r["time"][0:4]) >= 1900]
    rows = decluster(rows)
    out = []
    for r in rows:
        t = r["time"]
        h = int(t[11:13]) + int(t[14:16]) / 60 + float(t[17:19]) / 3600
        out.append(julian_day_number(int(t[:4]), int(t[5:7]), int(t[8:10]))
                   + h / 24 - 0.5)
    return out


def flood_jds():
    rows = []
    for f in FLOODS:
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
    return [jd(r) for r in kept]


def predicates(jd):
    c = chart_at(jd)
    p = {b: c.positions[b].longitude for b in TRIO}
    spread = circular_spread([p[b] for b in TRIO])
    p1 = spread <= BAND_SPAN
    bands = {division_of(p[b], 0) for b in TRIO}
    p2 = len(bands) == 1
    esc = any(_sep(c.positions[g].longitude, p[b]) <= BAND_SPAN
              for g in GIANTS for b in TRIO)
    return p1, p2, (p1 and esc)


def lift(e, n_e, c, n_c):                  # one implementation, in validation
    return smoothed_lift(e, n_e, c, n_c)


def grade(name, events, note=""):
    rng = random.Random(SEED)
    controls = []
    for jd in events:
        blk = []
        while len(blk) < CONTROLS_PER_EVENT:
            off = rng.uniform(-WINDOW, WINDOW)
            if abs(off) > EXCLUDE:
                blk.append(jd + off)
        controls.append(blk)
    n_e = len(events)
    n_c = n_e * CONTROLS_PER_EVENT
    ev = [predicates(jd) for jd in events]
    ct = [[predicates(j) for j in blk] for blk in controls]
    print(f"\n=== {name}: {n_e} events, {n_c} era-matched controls {note}")

    results = []
    for k, label in ((0, "P1 proximity (PRIMARY)"), (1, "P2 grid"),
                     (2, "P3 escalated (giant present)")):
        eh = sum(e[k] for e in ev)
        ch = sum(x[k] for blk in ct for x in blk)
        L = lift(eh, n_e, ch, n_c)
        blocks = [[ev[i][k]] + [x[k] for x in ct[i]] for i in range(n_e)]
        rng2 = random.Random(SEED + 1)
        null = []
        for _ in range(N_PERM):
            e2 = c2 = 0
            for flags in blocks:
                j = rng2.randrange(len(flags))
                e2 += flags[j]
                c2 += sum(flags) - flags[j]
            null.append(lift(e2, n_e, c2, n_c))
        p = sum(1 for v in null if v >= L) / N_PERM
        null.sort()
        print(f"  {label:<30} ev {eh:>4}/{n_e} = {eh/n_e:.4f}  "
              f"ctl {ch/n_c:.4f}  lift {L:.3f}  null med {null[N_PERM//2]:.3f}"
              f"  p = {p:.4f}")
        results.append((L, blocks))

    print("  power check (plant into events, P1):")
    base_c = sum(x[0] for blk in ct for x in blk)
    for frac in (0.10, 0.05, 0.02):
        planted = [e[0] for e in ev]
        k = int(n_e * frac)
        for i in [i for i in range(n_e) if not planted[i]][:k]:
            planted[i] = True
        L = lift(sum(planted), n_e, base_c, n_c)
        pb = [[planted[i]] + [x[0] for x in ct[i]] for i in range(n_e)]
        rng3 = random.Random(SEED + 3)
        pn = []
        for _ in range(500):
            e2 = c2 = 0
            for flags in pb:
                j = rng3.randrange(len(flags))
                e2 += flags[j]
                c2 += sum(flags) - flags[j]
            pn.append(lift(e2, n_e, c2, n_c))
        print(f"    +{int(frac*100):>2}% -> lift {L:.3f}, "
              f"p = {sum(1 for v in pn if v >= L)/500:.4f}")



# --- Design of record (ported onto the validation framework) ---
CLAIM = Claim(
    name="band-trigger-m7",
    hypothesis="Events carry the Moon-Ketu-Mars band coincidence more often "
               "than era-matched instants do.",
    direction="higher",
    statistic="add-one smoothed lift on P1 (trio spread <= one band span)",
    control="era-matched, 5 per event, +-365 d excluding +-7 d, seed 42",
    corpus="1,435 declustered M7+ at exact instants (primary) + 1,886 "
           "declustered day-precision floods (secondary, indicative only)",
    verdict="p < 0.05 and lift > 1",
    power="plant the predicate into 10/5/2% of events",
    notes="Result on record: lift 1.804, p = 0.069 — fails the bar, resting "
          "on 12 firings vs 7.0 expected (1.4 sigma). Floods point the other "
          "way (0.937). Settled by scripts/band_trigger_m6.py: null.",
    preregistered=True,
)

def main():
    print(CLAIM.banner())
    print()
    grade("QUAKES M7+ (PRIMARY — exact instants)", quake_jds())
    grade("FLOODS (SECONDARY — nominal 12:00 UTC)", flood_jds(),
          note="[Moon +-6.6 deg uncertain: indicative only]")


if __name__ == "__main__":
    main()
