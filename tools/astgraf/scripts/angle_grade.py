# ABOUTME: Does the site-angle rule actually pick the PLACE? Grades angles.py over the
# ABOUTME: M7+ catalog against leave-one-out epicenter controls at the same instant.
#
# Run from tools/astgraf:  uv run python scripts/angle_grade.py
# Reads out/signatures-m7-v2/signatures.csv for jd/lat/lon (generator:
# astgraf-signatures), writes out/angle-grade/summary.txt.
#
# WHY THE CONTROLS ARE PLACES, NOT TIMES. Every other channel in this suite was
# graded against TIME-uniform controls, because those channels claim an instant.
# The site-angle rule claims a PLACE, so holding the instant fixed and varying
# the place is the only test that can falsify it. Control places are drawn from
# the other events' own epicenters (leave-one-out), which matches the geography
# of seismicity exactly — the test therefore asks the one question a location
# layer has to answer: given that a quake happened somewhere in the belt, does
# the angle condition say WHICH place?
#
# WHY THE RANK TEST IS PRIMARY. At a fixed instant the true epicenter and its K
# controls are exchangeable under the null, so the rank of the true place among
# the K+1 is exactly uniform — no asymptotics, no calibration needed. Lifts are
# also reported so the number is comparable with the mined-aspect and mirror
# channels, but the rank is the honest statistic here.
import csv
import math
import random
import statistics
from pathlib import Path

from astgraf.validation import Claim
from astgraf.anchors import refine_exactness
from astgraf.angles import angles_from_chart, body_longitudes, site_chart
from astgraf.bands import BAND_BODIES

BASE = Path(__file__).resolve().parent.parent
SIG = BASE / "out" / "signatures-m7-v2" / "signatures.csv"
OUT = BASE / "out" / "angle-grade" / "summary.txt"

K_CONTROLS = 49          # rank resolution 1/50 = 2%
# The BAS cusp chain sets xx = sin(RA)*tan(obliquity)*tan(lat) and then takes
# sqrt(1 - xx*xx), so it is undefined once |xx| >= 1. Places past that are
# excluded from BOTH arms and the exclusion is reported — a property of the
# canon routine, not of this script.
#
# TWO CORRECTIONS to the reasoning as first written (2026-08-05, measured):
#   * The threshold is NOT the fixed 66.56 deg quoted here originally. That
#     figure assumes sin(RA) = 1; because RA moves with sidereal time the real
#     limit depends on the INSTANT as well as the place (at RA 120 the chain
#     is fine at 67 N and fails at 70). 66.56 is the WORST CASE, i.e. the
#     latitude below which the chain is defined at every RA.
#   * "The angles simply do not exist up there" was wrong. The Ascendant and
#     the MC remain defined past the limit — measured at 85 N, both compute.
#     Only the twelve cusps do not. See angles.POLAR_SAFE_LIMIT.
# POLAR_LIMIT stays at the conservative 66.0 deliberately: it is what the
# recorded grading used, it excludes symmetrically from events and controls,
# and loosening it would move a published result for one event in 1,548.
POLAR_LIMIT = 66.0
ORBS = (3.0, 1.0)
REAL_GIANTS = ("Jupiter", "Saturn", "Uranus", "Neptune")
TARGETS = ("Sun", "Rahu", "Ketu")
TAUGHT = {"Nepal": (28.2305, 84.7314), "Hyderabad": (17.385, 78.487),
          "Ulsoor": (12.98, 77.62)}
# The bodies each anchor was actually read on — the SPECIFIED form. Scoring the
# anchor on min-over-all-bodies would grade the vacuous version of the rule.
TAUGHT_BODIES = {"Nepal": ("Sun", "real-Uranus"),
                 "Hyderabad": ("Neptune", "Ketu"),
                 "Ulsoor": ("Neptune",)}

lines: list[str] = []


def say(msg: str) -> None:
    print(msg)
    lines.append(msg)


def _sep(a: float, b: float) -> float:
    d = abs(a - b) % 360.0
    return min(d, 360.0 - d)


SCORED = list(BAND_BODIES) + [f"real-{g}" for g in REAL_GIANTS]


def angle_seps(jd: float, lat: float, lon: float) -> dict[str, float]:
    """Separation from each SCORED body to the NEAREST of the four angles.
    body_longitudes() also returns Pluto, which is outside BAND_BODIES and
    outside the doctrine; it is filtered here so that every test in this file
    — including the min-over-bodies ones — scores the same body set."""
    c = site_chart(jd, lat, lon)
    ax = angles_from_chart(c).values()
    pos = body_longitudes(c)
    return {b: min(_sep(v, pos[b]) for v in ax) for b in SCORED}


def acting_contacts(jd: float) -> list[tuple[str, str]]:
    """(real giant, target) pairs whose taught contact is in force, orb <= 3.
    Recomputed live — the stored rsep columns are not consulted."""
    c = site_chart(jd, 0.0, 0.0)
    pos = body_longitudes(c)
    return [(g, t) for g in ("Uranus", "Neptune") for t in TARGETS
            if _sep(pos[f"real-{g}"], pos[t]) <= 3.0]


def rank_report(name: str, ranks: list[int], k: int) -> dict:
    """Rank of the true place among K+1 exchangeable places. Uniform under the
    null, so mean normalised rank 0.5 and P(tightest) = 1/(K+1) are exact."""
    n = len(ranks)
    u = [(r - 1) / k for r in ranks]
    mean_u = statistics.mean(u)
    tightest = sum(1 for r in ranks if r == 1) / n
    # exact null variance of one rank: u is uniform on {0, 1/k, ..., 1}
    var1 = sum((i / k - 0.5) ** 2 for i in range(k + 1)) / (k + 1)
    z = (mean_u - 0.5) / math.sqrt(var1 / n)
    return {"body": name, "n": n, "mean_rank": round(mean_u, 4),
            "tightest": round(tightest, 4), "expect_tightest": round(1 / (k + 1), 4),
            "z": round(z, 2)}



# --- Design of record (ported onto the validation framework) ---
CLAIM = Claim(
    name="site-angle-location",
    hypothesis="An event stands where the crossing pair sits on an ANGLE "
               "(Asc/Desc/MC/IC) of the site's own chart — so the true "
               "epicentre should show a tighter body-to-angle separation than "
               "other real epicentres do at the same instant.",
    direction="lower",
    statistic="mean rank of the true epicentre among 1 + K control places "
              "(uniform under the null), reported as a z",
    control="place — 49 leave-one-out epicentres per event at the SAME "
            "instant, drawn from the corpus so the controls inherit the "
            "geography of seismicity exactly",
    corpus="1,434 declustered post-1900 M7+ events carrying epicentres",
    verdict="z < -3.0 (the multiplicity bar for 15 bodies scored)",
    power="scripts/angle_power.py plants epicentres on a chosen body's angle "
          "and re-runs the identical rank machinery under jitter",
    preregistered=False,
    notes="RETROSPECTIVE declaration (2026-08-05 port). Result on record: "
          "best body Mars z = -2.27; the SPECIFIED form z = -0.35 at the "
          "catalog instant and +1.20 at the crossing exactness instant; "
          "family p = 0.25. Power arm recovered a planted signal at "
          "z = -17.9 (MC) / -17.1 (Asc), so the null is not blindness.",
)

def main() -> None:
    say(CLAIM.banner())
    say("")
    with open(SIG, newline="") as fh:
        located = [r for r in csv.DictReader(fh) if r.get("lat") and r.get("lon")]
    rows = [r for r in located if abs(float(r["lat"])) <= POLAR_LIMIT]
    jds = [float(r["jd"]) for r in rows]
    places = [(float(r["lat"]), float(r["lon"])) for r in rows]
    say(f"site-angle location grading — {len(rows)} declustered post-1900 M7+ "
        f"events with epicenters (out/signatures-m7-v2)")
    say(f"excluded {len(located) - len(rows)} of {len(located)} for |lat| > "
        f"{POLAR_LIMIT} deg: the BAS cusp chain is undefined there, for "
        "events AND controls alike (conservative fixed bound; the true limit "
        "moves with sidereal time — see angles.POLAR_SAFE_LIMIT)")
    say(f"controls: {K_CONTROLS} leave-one-out epicenters per event at the SAME "
        "instant (seismicity geography matched by construction)")

    bodies = SCORED
    say(f"bodies scored: {len(bodies)} ({', '.join(bodies)})")

    rng = random.Random(11)
    true_seps: list[dict[str, float]] = []
    ctrl_seps: list[list[dict[str, float]]] = []
    for i, jd in enumerate(jds):
        true_seps.append(angle_seps(jd, *places[i]))
        pool = rng.sample([j for j in range(len(places)) if j != i], K_CONTROLS)
        ctrl_seps.append([angle_seps(jd, *places[j]) for j in pool])

    # --- T1: per-body rank test, the primary statistic -------------------
    say("")
    say("--- T1: is the true epicenter tighter to an angle than control places? ---")
    say(f"{'body':16s} {'mean rank':>10s} {'P(tightest)':>12s} {'expect':>8s} {'z':>7s}")
    reports = []
    for b in bodies:
        ranks = [1 + sum(1 for cs in ctrl_seps[i] if cs[b] < true_seps[i][b])
                 for i in range(len(rows))]
        rep = rank_report(b, ranks, K_CONTROLS)
        reports.append(rep)
        say(f"{b:16s} {rep['mean_rank']:10.4f} {rep['tightest']:12.4f} "
            f"{rep['expect_tightest']:8.4f} {rep['z']:7.2f}")
    best = min(reports, key=lambda r: r["z"])
    say(f"most-negative z (tightest-at-epicenter direction): {best['body']} "
        f"z = {best['z']:.2f}; with {len(bodies)} bodies tested the "
        f"multiplicity-corrected bar is about z = -3.0")

    # --- T2: lifts, for comparability with the other channels ------------
    say("")
    say("--- T2: hit-rate lifts (same add-one smoothing as the other channels) ---")
    for orb in ORBS:
        table = []
        n_c = len(rows) * K_CONTROLS
        for b in bodies:
            eh = sum(1 for s in true_seps if s[b] <= orb)
            ch = sum(1 for cs in ctrl_seps for s in cs if s[b] <= orb)
            lift = ((eh + 1) / (len(rows) + 2)) / ((ch + 1) / (n_c + 2))
            table.append((lift, b, eh / len(rows), ch / n_c))
        table.sort(reverse=True)
        say(f"orb {orb} deg — top 4 of {len(bodies)}:")
        for lift, b, er, cr in table[:4]:
            say(f"   {b:16s} lift {lift:5.3f}  events {er:.4f}  controls {cr:.4f}")

    # --- T3: the specified form — only the acting taught contact ---------
    say("")
    say("--- T3: specified form (taught real-giant contact in force, orb<=3) ---")
    spec_ranks: list[int] = []
    spec_bodies: list[str] = []
    for i, jd in enumerate(jds):
        for g, t in acting_contacts(jd):
            for b in (f"real-{g}", t):
                r = 1 + sum(1 for cs in ctrl_seps[i] if cs[b] < true_seps[i][b])
                spec_ranks.append(r)
                spec_bodies.append(b)
    if spec_ranks:
        rep = rank_report("acting pair", spec_ranks, K_CONTROLS)
        say(f"{len(spec_ranks)} acting-body instances over "
            f"{len(set(spec_bodies))} distinct bodies")
        say(f"mean rank {rep['mean_rank']:.4f} (null 0.5), P(tightest) "
            f"{rep['tightest']:.4f} (null {rep['expect_tightest']:.4f}), "
            f"z = {rep['z']:.2f}")
    else:
        say("no acting contacts in the corpus at orb 3")

    # --- T4: the unspecified form, kept on the record as vacuous ---------
    say("")
    say("--- T4: unspecified form (ANY body on ANY angle) ---")
    for orb in ORBS:
        e = sum(1 for s in true_seps if min(s.values()) <= orb) / len(rows)
        c = sum(1 for cs in ctrl_seps for s in cs
                if min(s.values()) <= orb) / (len(rows) * K_CONTROLS)
        say(f"orb {orb} deg: events {e:.4f}, control places {c:.4f} — "
            f"lift {e / c:.3f}")

    # --- T5: the taught anchors against their own control sets -----------
    say("")
    say("--- T5: the taught anchors, ranked against the same control places ---")
    for name, (lat, lon) in TAUGHT.items():
        hits = [(i, r) for i, r in enumerate(rows)
                if abs(float(r["lat"]) - lat) < 0.5
                and abs(float(r["lon"]) - lon) < 0.5]
        if not hits:
            say(f"{name}: not in the M7+ corpus (below threshold) — skipped")
            continue
        i, r = hits[0]
        tight = min(true_seps[i].items(), key=lambda kv: kv[1])
        rk = 1 + sum(1 for cs in ctrl_seps[i]
                     if min(cs.values()) < min(true_seps[i].values()))
        say(f"{name} ({r['label'][:10]}): tightest body {tight[0]} at "
            f"{tight[1]:.2f} deg; rank {rk}/{K_CONTROLS + 1} among control places")
        # and the SPECIFIED form — the bodies the anchor was read on
        for b in TAUGHT_BODIES.get(name, ()):
            br = 1 + sum(1 for cs in ctrl_seps[i] if cs[b] < true_seps[i][b])
            say(f"   specified body {b:14s} {true_seps[i][b]:5.2f} deg — rank "
                f"{br}/{K_CONTROLS + 1}")

    # --- T6: the doctrinal instant, the one a forward run would use ------
    say("")
    say("--- T6: same test at the CROSSING EXACTNESS instant, not the origin ---")
    say("(forward prediction only knows the crossing instant, so this is the "
        "version the watchlist would actually run)")
    ex_ranks: list[int] = []
    for i, jd in enumerate(jds):
        for g, t in acting_contacts(jd):
            ex = refine_exactness(g, t, "rsep", 0.0, jd)
            tj = ex["jd"]
            for b in (f"real-{g}", t):
                true = angle_seps(tj, *places[i])[b]
                pool = rng.sample([j for j in range(len(places)) if j != i],
                                  K_CONTROLS)
                ctrl = [angle_seps(tj, *places[j])[b] for j in pool]
                ex_ranks.append(1 + sum(1 for c in ctrl if c < true))
    if ex_ranks:
        rep = rank_report("acting pair @ exactness", ex_ranks, K_CONTROLS)
        say(f"{len(ex_ranks)} acting-body instances at their exactness instants")
        say(f"mean rank {rep['mean_rank']:.4f} (null 0.5), P(tightest) "
            f"{rep['tightest']:.4f} (null {rep['expect_tightest']:.4f}), "
            f"z = {rep['z']:.2f}")
    else:
        say("no acting contacts to refine")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
