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


def _solve_lon(f, target: float, step: float = 2.0) -> float | None:
    """Longitude where f(lon) == target, by scan then bisection on the wrapped
    difference. Used for both angles: the Ascendant's response to longitude
    varies far too much with latitude for fixed-point iteration to be safe."""
    def d(lon):
        return _wrap(f(lon) - target)

    lon = -180.0
    while lon < 180.0:
        hi_lon = min(lon + step, 180.0)
        a, b = d(lon), d(hi_lon)
        if a * b <= 0 and abs(b - a) < 90:
            lo, hi = lon, hi_lon
            for _ in range(50):
                mid = (lo + hi) / 2
                if d(lo) * d(mid) <= 0:
                    hi = mid
                else:
                    lo = mid
            return (lo + hi) / 2
        lon += step
    return None


def lon_for_angle(jd: float, lat: float, target: float, angle: str):
    """Observer longitude putting `target` on `angle` at latitude `lat`.
    MC is latitude-free; Asc is not, which is the whole point of testing both."""
    if angle == "MC":
        return _solve_lon(lambda lo: site_chart(jd, 0.0, lo).cusps[0], target)
    return _solve_lon(
        lambda lo: site_chart(jd, lat, lo).positions["Ascendant"].longitude,
        target)


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
    say(f"construction: epicenter longitude set so {BODY} sits exactly on the "
        "stated angle there, then displaced by the jitter; latitude left real")

    # BOTH angles are planted. An earlier version tested only the MC and then
    # generalised the verdict to "any angle rule" — but the taught Hyderabad
    # and Ulsoor anchors are ASCENDANT readings, and the Ascendant is the
    # weakly-conditioned axis. The Asc arm is the one that actually covers them.
    for angle in ("MC", "Asc"):
        resid, solved, keep = [], [], []
        for n, jd in enumerate(jds):
            target = body_longitudes(site_chart(jd, 0.0, 0.0))[BODY]
            lon = lon_for_angle(jd, lats[n], target, angle)
            if lon is None:
                continue
            got = (site_chart(jd, 0.0, lon).cusps[0] if angle == "MC"
                   else site_chart(jd, lats[n], lon).positions["Ascendant"].longitude)
            resid.append(abs(_wrap(got - target)))
            solved.append(lon)
            keep.append(n)
        if max(resid) > 0.01:
            raise SystemExit(
                f"{angle} solver residual {max(resid):.3g} deg — a power result "
                "from an unconverged planting would be worthless, refusing to "
                "print one")
        say("")
        say(f"--- planted on the {angle} ({len(keep)}/{len(jds)} events solved, "
            f"max residual {max(resid):.1e} deg) ---")
        say(f"{'jitter':>8s} {'mean rank':>10s} {'P(tightest)':>12s} {'z':>9s}"
            "  verdict")
        for jit in JITTERS:
            jrng = random.Random(int(jit * 100) + 3)
            ranks = []
            for slot, n in enumerate(keep):
                jd = jds[n]
                lon = _wrap(solved[slot] + jrng.uniform(-jit, jit))
                true = angle_seps(jd, lats[n], lon)[BODY]
                ctrl = [angle_seps(jd, *pool[j])[BODY]
                        for j in jrng.sample(range(len(pool)), K_CONTROLS)]
                ranks.append(1 + sum(1 for c in ctrl if c < true))
            rep = rank_report(BODY, ranks, K_CONTROLS)
            verdict = "DETECTED" if rep["z"] < -3.0 else "not detected"
            say(f"{jit:8.1f} {rep['mean_rank']:10.4f} {rep['tightest']:12.4f} "
                f"{rep['z']:9.2f}  {verdict}")

    say("")
    say("Read this against angle_grade.py's observed best z of -2.27 (Mars, "
        "15 bodies). Both angles are covered, so a rule placing events on "
        "either a culmination meridian or a rising line, to within the largest "
        "DETECTED jitter, would have been found. It was not.")
    say(f"Power here is measured on {N_EVENTS} events; the real grading uses "
        "1434, and z grows with sqrt(n), so this understates the true bar.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
