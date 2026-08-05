# ABOUTME: Power check for the site-angle grading — inject a KNOWN location signal of
# ABOUTME: known size and confirm the rank test recovers it, so the null is meaningful.
#
# Run from tools/astgraf:  uv run python scripts/angle_power.py
# Writes out/angle-grade/power.txt.
#
# WHY THIS EXISTS. angle_grade.py returned a flat null over the M7+ catalog. A
# null is only evidence if the instrument can detect the thing it failed to
# find, so this builds synthetic "events" whose epicenters are placed ON the
# meridian where a chosen body culminates, blurs that placement by a stated
# number of degrees, and re-runs the identical rank machinery. The jitter sweep
# converts the null into a quantitative statement: a real rule of THIS shape
# with residuals up to N degrees would have shown up, so the catalog rules it
# out at that scale.
import csv
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# These must follow the sys.path insert above — the point of this script is to
# reuse angle_grade's EXACT statistic, not a re-typed copy of it.
from angle_grade import K_CONTROLS, POLAR_LIMIT, angle_seps, rank_report  # noqa: I001
from astgraf.angles import body_longitudes, site_chart

BASE = Path(__file__).resolve().parent.parent
SIG = BASE / "out" / "signatures-m7-v2" / "signatures.csv"
OUT = BASE / "out" / "angle-grade" / "power.txt"

BODY = "Mars"            # the body whose culmination we plant the epicenter on
JITTERS = (0.0, 1.0, 3.0, 6.0, 12.0, 25.0)
N_EVENTS = 600           # enough for a stable z, small enough to sweep 6 levels

lines: list[str] = []


def say(msg: str) -> None:
    print(msg)
    lines.append(msg)


def _wrap(x: float) -> float:
    return (x + 180.0) % 360.0 - 180.0


def lon_for_mc(jd: float, target: float, iters: int = 12) -> float:
    """Observer longitude that puts `target` on the MC. The MC tracks observer
    longitude near 1:1, so plain fixed-point iteration converges geometrically;
    the residual is returned to the caller's assertion rather than assumed."""
    lon = 0.0
    for _ in range(iters):
        mc = site_chart(jd, 0.0, lon).cusps[0]
        lon = _wrap(lon + _wrap(target - mc))
    return lon


def main() -> None:
    with open(SIG, newline="") as fh:
        rows = [r for r in csv.DictReader(fh)
                if r.get("lat") and r.get("lon")
                and abs(float(r["lat"])) <= POLAR_LIMIT]
    rng = random.Random(5)
    sample = rng.sample(range(len(rows)), min(N_EVENTS, len(rows)))
    jds = [float(rows[i]["jd"]) for i in sample]
    lats = [float(rows[i]["lat"]) for i in sample]
    pool = [(float(r["lat"]), float(r["lon"])) for r in rows]

    say(f"power check for the site-angle rank test — {len(sample)} synthetic "
        f"events, control places drawn from the same {len(pool)} real epicenters")
    say(f"construction: epicenter longitude set so {BODY} culminates there, "
        "then displaced by the stated jitter; latitude left as the real one")

    # verify the planting actually plants: residual of the solved meridian
    resid = []
    solved = []
    for jd in jds:
        c = site_chart(jd, 0.0, 0.0)
        target = body_longitudes(c)[BODY]
        lon = lon_for_mc(jd, target)
        mc = site_chart(jd, 0.0, lon).cusps[0]
        resid.append(abs(_wrap(mc - target)))
        solved.append(lon)
    say(f"meridian solver residual: max {max(resid):.2e} deg over "
        f"{len(resid)} events")
    if max(resid) > 0.01:
        say("SOLVER DID NOT CONVERGE — power result below is not trustworthy")

    say("")
    say(f"{'jitter':>8s} {'mean rank':>10s} {'P(tightest)':>12s} {'z':>9s}  verdict")
    for jit in JITTERS:
        jrng = random.Random(int(jit * 100) + 3)
        ranks = []
        for n, jd in enumerate(jds):
            lon = _wrap(solved[n] + jrng.uniform(-jit, jit))
            lat = lats[n]
            true = angle_seps(jd, lat, lon)[BODY]
            ctrl = [angle_seps(jd, *pool[j])[BODY]
                    for j in jrng.sample(range(len(pool)), K_CONTROLS)]
            ranks.append(1 + sum(1 for c in ctrl if c < true))
        rep = rank_report(BODY, ranks, K_CONTROLS)
        verdict = "DETECTED" if rep["z"] < -3.0 else "not detected"
        say(f"{jit:8.1f} {rep['mean_rank']:10.4f} {rep['tightest']:12.4f} "
            f"{rep['z']:9.2f}  {verdict}")

    say("")
    say("Read this against angle_grade.py's observed best z of -2.27 (Mars, "
        "15 bodies): any rule that places events on a body's angle to within "
        "the largest DETECTED jitter above would have been found. It was not.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
