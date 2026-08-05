# ABOUTME: Grades the author's dwell-time claim — "dwell > 3 s creates MAJOR SHOCK
# ABOUTME: WAVES" — against the M7+ catalog, time-uniform controls and magnitude.
#
# Run from tools/astgraf:  uv run python scripts/dwell_grade.py
# Reads out/signatures-m7-v2/{signatures,controls}.csv, writes
# out/dwell-grade/summary.txt.
#
# THE CONSTRUCTION, and how it was arrived at. The author states only two
# things numerically: the threshold ("dwell time more than 3 seconds, for above
# that MAJOR SHOCK WAVES can be created") and one worked case ("In Nepal the
# dwell time has been 4 minutes - because both Uranus and Neptune crossed Ketu
# position one after another"). At the Gorkha instant exactly two taught
# contacts are in force — real-Uranus on the Sun at 0.692 deg and real-Neptune
# on Ketu at 0.342 deg — and 0.692 + 0.342 = 1.034 deg, which at his own 4 min
# per degree is 4.14 minutes. That reproduces his 4 minutes AND his phrase "one
# after another" (a sum of two sequential crossings), so dwell is taken as
#     dwell = SUM over active crossings of pair separation, x 4 min/deg
# with the caveat recorded plainly: this is one confirming instance, and his
# prose attributes both crossings to Ketu whereas the chart puts real-Uranus on
# the Sun, 26.5 deg from Ketu. The number fits; the attribution does not.
#
# WHAT MAKES IT FALSIFIABLE. Under this reading a WIDER pair yields a LONGER
# dwell, so the doctrine predicts that looser configurations drive bigger
# events — the opposite of the conventional orb intuition. Two consequences
# are testable: event charts should carry more dwell than time-uniform
# controls, and dwell should rise with magnitude.
import csv
import math
import random
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# Must follow the sys.path insert.
from angle_grade import acting_contacts  # noqa: I001,F401
from astgraf.validation import Claim
from astgraf.angles import body_longitudes, site_chart

BASE = Path(__file__).resolve().parent.parent
DIR = BASE / "out" / "signatures-m7-v2"
OUT = BASE / "out" / "dwell-grade" / "summary.txt"

MIN_PER_DEG = 4.0
TARGETS = ("Sun", "Rahu", "Ketu")
TAUGHT_GIANTS = ("Uranus", "Neptune")
ALL_GIANTS = ("Jupiter", "Saturn", "Uranus", "Neptune")
ORBS = (3.0, 1.0)
THRESHOLD_MIN = 3.0 / 60.0          # his 3 seconds, in minutes
N_PERM = 2000

lines: list[str] = []


def say(msg: str) -> None:
    print(msg)
    lines.append(msg)


def _sep(a: float, b: float) -> float:
    d = abs(a - b) % 360.0
    return min(d, 360.0 - d)


def dwell(jd: float, giants, orb: float) -> tuple[float, int]:
    """(dwell in minutes, number of active crossings) at this instant."""
    pos = body_longitudes(site_chart(jd, 0.0, 0.0))
    total, k = 0.0, 0
    for g in giants:
        for t in TARGETS:
            s = _sep(pos[f"real-{g}"], pos[t])
            if s <= orb:
                total += s
                k += 1
    return total * MIN_PER_DEG, k


def spearman(x: list[float], y: list[float]) -> float:
    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r

    rx, ry = rank(x), rank(y)
    mx, my = statistics.mean(rx), statistics.mean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx)
                    * sum((b - my) ** 2 for b in ry))
    return num / den if den else 0.0


def perm_p_corr(x, y, obs, rng, n_perm=N_PERM):
    """Two-sided permutation p for a rank correlation."""
    ys = list(y)
    hits = 0
    for _ in range(n_perm):
        rng.shuffle(ys)
        if abs(spearman(x, ys)) >= abs(obs):
            hits += 1
    return hits / n_perm


def perm_p_means(a, b, rng, n_perm=N_PERM):
    """Two-sided permutation p for a difference in means."""
    obs = statistics.mean(a) - statistics.mean(b)
    pool = list(a) + list(b)
    na = len(a)
    hits = 0
    for _ in range(n_perm):
        rng.shuffle(pool)
        d = statistics.mean(pool[:na]) - statistics.mean(pool[na:])
        if abs(d) >= abs(obs):
            hits += 1
    return obs, hits / n_perm



# --- Design of record (ported onto the validation framework) ---
CLAIM = Claim(
    name="dwell-doctrine",
    hypothesis="The author's dwell reading (sum of active crossing "
               "separations x 4 min/deg) has two separable halves: events "
               "carry MORE dwell than ordinary instants (trigger half), and "
               "wider crossings drive BIGGER events (magnitude half).",
    direction="higher",
    statistic="trigger half: mean dwell difference, events vs controls. "
              "magnitude half: Spearman rho of dwell against magnitude",
    control="time-uniform controls over the corpus span (the climatology), "
            "3 per event, from out/signatures-m7-v2",
    corpus="declustered post-1900 M7+ events; the magnitude arm inspects "
           "four taught-giant / orb cells",
    verdict="p < 0.05 with the predicted sign, family-wise across the four "
            "correlation cells",
    power="inject a known rank correlation into the same cell and confirm "
          "recovery; 12 draws per target",
    preregistered=False,
    notes="RETROSPECTIVE declaration (2026-08-05 port). Result on record: "
          "trigger half VACUOUS (3 s IS 1/81 deg, so every in-orb crossing "
          "clears it) and null (+0.054 min at orb 3, p = 0.42, sign reverses "
          "at orb 1). Magnitude half rho = +0.322 (n = 44), family-wise "
          "p = 0.042 — then DIED on pre-registered held-out M6.0-6.99 "
          "(rho = -0.040, p = 0.77). See scripts/dwell_holdout.py.",
)

def main() -> None:
    say(CLAIM.banner())
    say("")
    with open(DIR / "signatures.csv", newline="") as fh:
        rows = list(csv.DictReader(fh))
    with open(DIR / "controls.csv", newline="") as fh:
        ctl = [float(r["jd"]) for r in csv.DictReader(fh)]
    ev_jd = [float(r["jd"]) for r in rows]
    # mags is indexed BY EVENT POSITION throughout, so a filtered comprehension
    # here would silently misalign every correlation. Require the column.
    missing = sum(1 for r in rows if not r.get("mag"))
    if missing:
        raise SystemExit(f"{missing} rows lack 'mag'; positional indexing of "
                         "magnitudes would misalign — regenerate the corpus")
    mags = [float(r["mag"]) for r in rows]
    say(f"dwell grading — {len(ev_jd)} declustered post-1900 M7+ events vs "
        f"{len(ctl)} time-uniform controls")
    say("dwell = sum of active crossing separations x 4 min/deg "
        "(derivation and its single-instance caveat: see header)")

    # sanity: reproduce his Nepal number before grading anything
    from astgraf.anchors import iso_jd
    nd, nk = dwell(iso_jd("2015-04-25T06:11:25.950Z"), TAUGHT_GIANTS, 3.0)
    say("")
    say(f"Nepal check: {nk} active crossings, dwell {nd:.2f} min "
        f"(he says 4 minutes) — {'reproduced' if abs(nd - 4) < 0.5 else 'DOES NOT MATCH'}")

    rng = random.Random(19)
    for label, giants in (("taught giants (Ura/Nep)", TAUGHT_GIANTS),
                          ("all four giants", ALL_GIANTS)):
        for orb in ORBS:
            e = [dwell(j, giants, orb) for j in ev_jd]
            c = [dwell(j, giants, orb) for j in ctl]
            ed = [d for d, _ in e]
            cd = [d for d, _ in c]
            say("")
            say(f"--- {label}, orb {orb} deg ---")
            say(f"active-crossing rate: events "
                f"{sum(1 for _, k in e if k):>5}/{len(e)} "
                f"({sum(1 for _, k in e if k) / len(e):.4f}), controls "
                f"{sum(1 for _, k in c if k) / len(c):.4f}")
            say(f"his 3-second threshold (dwell > {THRESHOLD_MIN:.4f} min): "
                f"events {sum(1 for d in ed if d > THRESHOLD_MIN) / len(ed):.4f}, "
                f"controls {sum(1 for d in cd if d > THRESHOLD_MIN) / len(cd):.4f}"
                " — a crossing in orb at all almost always clears it")
            diff, p = perm_p_means(ed, cd, rng)
            say(f"mean dwell: events {statistics.mean(ed):.3f} min, controls "
                f"{statistics.mean(cd):.3f} min; difference {diff:+.3f}, "
                f"permutation p = {p:.3f}")

            # magnitude: does a longer dwell mean a bigger quake?
            pairs = [(d, m) for (d, _), m in zip(e, mags) if d > 0]
            if len(pairs) > 20:
                xs = [d for d, _ in pairs]
                ys = [m for _, m in pairs]
                rho = spearman(xs, ys)
                pc = perm_p_corr(xs, ys, rho, rng)
                say(f"dwell vs magnitude over {len(pairs)} events with an "
                    f"active crossing: Spearman rho = {rho:+.4f}, "
                    f"permutation p = {pc:.3f}")
            else:
                say(f"only {len(pairs)} events with an active crossing — "
                    "too few to correlate against magnitude")

    # --- multiplicity: four correlation cells were inspected, not one -----
    # One cell (taught giants, orb 1) reached rho = +0.32, p = 0.028 in the
    # doctrine's own direction. Four cells were looked at, and neighbouring
    # cells disagree in SIGN, so the family-wise bar is what decides it: the
    # magnitudes are shuffled ACROSS ALL EVENTS and every cell recomputed, so
    # the null is the largest |rho| any cell reaches by chance.
    say("")
    say("--- family-wise test over the four correlation cells ---")
    cells = []
    for label, giants in (("taught", TAUGHT_GIANTS), ("all4", ALL_GIANTS)):
        for orb in ORBS:
            d_all = [dwell(j, giants, orb)[0] for j in ev_jd]
            idx = [i for i, d in enumerate(d_all) if d > 0]
            cells.append((f"{label}/orb{orb:.0f}", d_all, idx))
    obs = []
    for name, d_all, idx in cells:
        r = spearman([d_all[i] for i in idx], [mags[i] for i in idx])
        obs.append((abs(r), name, r, len(idx)))
    obs.sort(reverse=True)
    for a, name, r, k in obs:
        say(f"   {name:12s} rho {r:+.4f}  (n = {k})")
    rng2 = random.Random(23)
    shuffled = list(mags)
    null_max = []
    for _ in range(N_PERM):
        rng2.shuffle(shuffled)
        null_max.append(max(
            abs(spearman([d_all[i] for i in idx],
                         [shuffled[i] for i in idx]))
            for _, d_all, idx in cells))
    best = obs[0][0]
    p_fw = sum(1 for x in null_max if x >= best) / len(null_max)
    say(f"largest |rho| observed {best:.4f} ({obs[0][1]}); null median "
        f"{statistics.median(null_max):.4f}, 95th pct "
        f"{sorted(null_max)[int(0.95 * len(null_max))]:.4f}")
    say(f"family-wise permutation p = {p_fw:.3f}")

    # --- is it dwell, or just the COUNT of crossings? ---------------------
    # dwell = sum of separations, so it rises with how MANY pairs are active
    # as well as how wide they are. Those are different claims: "more
    # crossings" is not the author's, "wider crossings" is. Decomposed here,
    # plus a split-half, because a 44-event cell that just clears a bar is
    # exactly where a winner's curse lives.
    say("")
    say("--- is the hit dwell, or the crossing COUNT? (taught / orb 1) ---")
    dk = [dwell(j, TAUGHT_GIANTS, 1.0) for j in ev_jd]
    idx = [i for i, (d, _) in enumerate(dk) if d > 0]
    ks = [dk[i][1] for i in idx]
    ds = [dk[i][0] for i in idx]
    ms = [mags[i] for i in idx]
    say(f"crossing count vs magnitude: rho {spearman(ks, ms):+.4f}  "
        f"(counts present: {sorted(set(ks))})")
    for kv in sorted(set(ks)):
        sub_d = [d for d, k in zip(ds, ks) if k == kv]
        sub_m = [m for m, k in zip(ms, ks) if k == kv]
        if len(sub_d) >= 8:
            say(f"   within count={kv} (n={len(sub_d):3d}): "
                f"dwell vs magnitude rho {spearman(sub_d, sub_m):+.4f}")
        else:
            say(f"   within count={kv} (n={len(sub_d):3d}): too few to test")

    say("")
    say("--- split-half in time (does it hold in both halves?) ---")
    med = statistics.median([ev_jd[i] for i in idx])
    for half, keep in (("earlier", lambda i: ev_jd[i] <= med),
                       ("later", lambda i: ev_jd[i] > med)):
        sel = [i for i in idx if keep(i)]
        r = spearman([dk[i][0] for i in sel], [mags[i] for i in sel])
        say(f"   {half:8s} n={len(sel):3d}  rho {r:+.4f}")

    # --- power: can this find a dwell/magnitude link that IS there? -------
    # The injection is built on the RANKS of dwell, not its raw value: dwell
    # is heavily skewed, so a slope in raw units concentrates the signal in a
    # handful of points and produces a non-monotone, useless power curve (an
    # earlier version of this block did exactly that). Detection rate is
    # averaged over seeds rather than read off a single draw.
    say("")
    say("--- power: inject a known rank correlation and try to recover it ---")
    _, d_all, idx = cells[1]                       # taught / orb 1, the n=44 cell
    n_k = len(idx)
    say(f"(using the {n_k}-event cell that produced the nominal hit)")
    xs = [d_all[i] for i in idx]
    rx = spearman(xs, xs)                          # sanity: perfect self-rho
    assert abs(rx - 1.0) < 1e-9, "rank machinery broken"
    order = sorted(range(n_k), key=lambda i: xs[i])
    norm = [0.0] * n_k
    for pos, i in enumerate(order):
        norm[i] = (pos + 0.5) / n_k - 0.5          # uniform, mean 0
    for target in (0.20, 0.30, 0.45):
        det, rhos = 0, []
        for seed in range(12):
            prng = random.Random(seed * 31 + int(target * 100))
            fake = [target * v * math.sqrt(12)
                    + prng.gauss(0, math.sqrt(1 - target ** 2))
                    for v in norm]
            r = spearman(xs, fake)
            rhos.append(r)
            if perm_p_corr(xs, fake, r, prng, 400) < 0.05:
                det += 1
        say(f"target rho {target:.2f} -> mean recovered "
            f"{statistics.mean(rhos):+.3f}, detected in {det}/12 draws")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
