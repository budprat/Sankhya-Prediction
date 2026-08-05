# ABOUTME: Is ANY ground rotation the right one? Scans the rotation angle for each giant
# ABOUTME: against the M7+ catalog and marks where the Mathcad and prose offsets fall.
#
# Run from tools/astgraf:  uv run python scripts/rotation_spectrum.py
# Reads out/signatures-m7-v2/signatures.csv, writes out/rotation-spectrum/summary.txt.
#
# WHY A SPECTRUM AND NOT TWO POINTS. NU's 2026-08-05 reading of the author's
# briefing found that his prose light-times (Jup 40, Sat 80, Ura 150, Nep 240
# min -> 10/20/37.5/60 deg of rotation) reproduce his own stated displacements
# (1000/2000/4000/8000 km), while the Mathcad offsets we implemented
# (3.34/7.87/17.86/29.09 deg) are about a third of that. Testing just those two
# candidates would answer "which of two", when the question that matters is
# "does ANY rotation carry location signal". So the rotation is scanned right
# round the circle: if the doctrine is right, the statistic must dip somewhere,
# and the dip should sit near the physical light-time value. A flat spectrum
# retires the whole family regardless of which offsets are correct.
#
# THE STATISTIC is the one the angle layer was graded with: at each event the
# true epicenter and K leave-one-out control epicenters are exchangeable under
# the null, so the rank of the true place among K+1 is exactly uniform. Control
# places are other events' epicenters, matching seismicity geography exactly.
#
# The spots do not depend on the place, so one chart per event serves the whole
# sweep — the scan is arithmetic after 1435 chart solves.
import csv
import random
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# Must follow the sys.path insert; reuses angle_grade's EXACT rank statistic.
from angle_grade import K_CONTROLS, rank_report  # noqa: I001
from astgraf.validation import Claim
from astgraf.anchors import chart_at
from astgraf.locator import ROTATION_DEGREES, _wrap180, equatorial
from astgraf.signatures import _gc_km

BASE = Path(__file__).resolve().parent.parent
SIG = BASE / "out" / "signatures-m7-v2" / "signatures.csv"
OUT = BASE / "out" / "rotation-spectrum" / "summary.txt"

GIANTS = ("Jupiter", "Saturn", "Uranus", "Neptune")
PROSE_MINUTES = {"Jupiter": 40.0, "Saturn": 80.0, "Uranus": 150.0,
                 "Neptune": 240.0}
PROSE = {b: m / 4.0 for b, m in PROSE_MINUTES.items()}      # 4 min per degree
MATHCAD = dict(ROTATION_DEGREES)
STEP = 5.0
NEPAL = (28.2305, 84.7314)

lines: list[str] = []


def say(msg: str) -> None:
    print(msg)
    lines.append(msg)


def subpoints(jd: float) -> dict[str, tuple[float, float]]:
    """(declination, un-rotated sub-point longitude) for each giant."""
    c = chart_at(jd)
    out = {}
    for b in GIANTS:
        p = c.positions[b]
        ra, dec = equatorial(p.longitude, p.ecliptic_latitude, c.obliquity)
        out[b] = (dec, _wrap180(ra - c.gmst))
    return out



# --- Design of record (ported onto the validation framework) ---
CLAIM = Claim(
    name="rotation-spectrum",
    hypothesis="If the light-time ground rotation is real, SOME rotation "
               "angle must locate events — and the best one should sit near "
               "the physical light-time value for each giant.",
    direction="lower",
    statistic="leave-one-out epicentre rank z, swept at 5 deg steps right "
              "round the circle for each of the four giants (288 tests)",
    control="place — the same 49 leave-one-out epicentres per event used by "
            "the site-angle grading, at the same instant",
    corpus="declustered post-1900 M7+ events from out/signatures-m7-v2",
    verdict="a dip below z = -3.7 (the bar for 288 tests), clustered near "
            "the physical light-time value",
    power="plant synthetic epicentres at a known 100 deg rotation and confirm "
          "the scan recovers it in the exact 5 deg bin",
    preregistered=False,
    notes="RETROSPECTIVE declaration (2026-08-05 port). Result on record: "
          "the spectrum is FLAT — deepest dip anywhere is Neptune at 25 deg, "
          "z = -2.32. Per-body minima (Jup 270, Sat 170, Ura 60, Nep 25) are "
          "scattered, not clustered near light-time. Power: the planted "
          "100 deg rotation is recovered in the exact bin at z = -64, and "
          "still at z = -60 with +-30 deg jitter. This retires the rotation "
          "idea across its ENTIRE parameter space, not at one point.",
)

def main() -> None:
    say(CLAIM.banner())
    say("")
    with open(SIG, newline="") as fh:
        rows = [r for r in csv.DictReader(fh) if r.get("lat") and r.get("lon")]
    places = [(float(r["lat"]), float(r["lon"])) for r in rows]
    jds = [float(r["jd"]) for r in rows]
    n = len(rows)
    say(f"rotation spectrum — {n} declustered post-1900 M7+ events with "
        "epicenters (out/signatures-m7-v2)")
    say(f"controls: {K_CONTROLS} leave-one-out epicenters per event, same "
        "instant, same spots — only the PLACE varies")

    say("computing one chart per event ...")
    sub = [subpoints(j) for j in jds]

    rng = random.Random(11)
    ctrl_idx = [rng.sample([j for j in range(n) if j != i], K_CONTROLS)
                for i in range(n)]

    def ranks_for(body: str, rot: float) -> list[int]:
        out = []
        for i in range(n):
            dec, lon0 = sub[i][body]
            slon = _wrap180(lon0 - rot)
            true = _gc_km(places[i][0], places[i][1], dec, slon)
            out.append(1 + sum(1 for j in ctrl_idx[i]
                               if _gc_km(places[j][0], places[j][1], dec, slon)
                               < true))
        return out

    say("")
    say("--- the spectrum: z of the rank statistic vs ground rotation ---")
    say("(negative z = true epicenter nearer the spot than control places)")
    best_overall = None
    for body in GIANTS:
        curve = []
        r = 0.0
        while r < 360.0:
            z = rank_report(body, ranks_for(body, r), K_CONTROLS)["z"]
            curve.append((z, r))
            r += STEP
        z_best, r_best = min(curve)
        z_m = rank_report(body, ranks_for(body, MATHCAD[body]),
                          K_CONTROLS)["z"]
        z_p = rank_report(body, ranks_for(body, PROSE[body]), K_CONTROLS)["z"]
        z_0 = rank_report(body, ranks_for(body, 0.0), K_CONTROLS)["z"]
        say(f"{body:9s} best z {z_best:6.2f} at {r_best:5.1f} deg  |  "
            f"mathcad {MATHCAD[body]:5.2f} deg z {z_m:5.2f}  |  "
            f"prose {PROSE[body]:5.1f} deg z {z_p:5.2f}  |  "
            f"no rotation z {z_0:5.2f}")
        spread = max(c[0] for c in curve) - z_best
        say(f"{'':9s} spectrum spans z {z_best:.2f} .. "
            f"{max(c[0] for c in curve):.2f} (range {spread:.2f})")
        if best_overall is None or z_best < best_overall[0]:
            best_overall = (z_best, body, r_best)
    say("")
    say(f"deepest dip anywhere: {best_overall[1]} at {best_overall[2]:.1f} deg, "
        f"z = {best_overall[0]:.2f}")
    say(f"with {len(GIANTS)} bodies x {int(360 / STEP)} angles = "
        f"{len(GIANTS) * int(360 / STEP)} tests, the multiplicity-corrected bar "
        "is about z = -3.7")

    # nearest-of-four under each named convention
    say("")
    say("--- nearest-of-four-giants, by convention ---")
    for name, conv in (("mathcad (current)", MATHCAD), ("prose (40/80/150/240 min)", PROSE),
                       ("no rotation", {b: 0.0 for b in GIANTS})):
        rk, hits = [], []
        for i in range(n):
            spots = [(dec, _wrap180(lon0 - conv[b]))
                     for b, (dec, lon0) in sub[i].items()]
            true = min(_gc_km(places[i][0], places[i][1], d, s)
                       for d, s in spots)
            hits.append(true)
            rk.append(1 + sum(
                1 for j in ctrl_idx[i]
                if min(_gc_km(places[j][0], places[j][1], d, s)
                       for d, s in spots) < true))
        rep = rank_report("nearest4", rk, K_CONTROLS)
        within = sum(1 for x in hits if x <= 1000) / n
        say(f"{name:28s} median {statistics.median(hits):5.0f} km  "
            f"within 1000 km {within:.4f}  mean rank {rep['mean_rank']:.4f}  "
            f"z {rep['z']:6.2f}")

    # the taught anchor under each convention
    say("")
    say("--- Nepal 2015-04-25 (Gorkha) under each convention ---")
    ni = next((i for i, r in enumerate(rows)
               if "Nepal" in r.get("place", "")
               and r["label"].startswith("2015-04-25")), None)
    if ni is None:
        say("Nepal not located in the corpus — skipped")
    else:
        for name, conv in (("mathcad", MATHCAD), ("prose", PROSE),
                           ("none", {b: 0.0 for b in GIANTS})):
            ds = {b: _gc_km(*NEPAL, dec, _wrap180(lon0 - conv[b]))
                  for b, (dec, lon0) in sub[ni].items()}
            best = min(ds, key=ds.get)
            say(f"{name:8s} " + "  ".join(f"{b} {ds[b]:6.0f}" for b in GIANTS)
                + f"   -> nearest {best} at {ds[best]:.0f} km")

    # --- power: does the spectrum find a rotation that IS there? ----------
    # A flat spectrum is only evidence if a planted rotation produces a dip.
    # Synthetic epicenters are placed at Uranus's sub-point rotated by a known
    # angle chosen to sit near no convention, then blurred; controls stay the
    # real epicenter pool, so the null geography is unchanged.
    say("")
    say("--- power: plant a known rotation and see whether the scan finds it ---")
    PLANT, BODY = 100.0, "Uranus"
    for jit in (0.0, 10.0, 30.0):
        prng = random.Random(int(jit) + 4)
        synth = []
        for i in range(n):
            dec, lon0 = sub[i][BODY]
            synth.append((dec + prng.uniform(-jit, jit) * 0.5,
                          _wrap180(lon0 - PLANT + prng.uniform(-jit, jit))))
        curve = []
        r = 0.0
        while r < 360.0:
            rk = []
            for i in range(n):
                dec, lon0 = sub[i][BODY]
                slon = _wrap180(lon0 - r)
                true = _gc_km(synth[i][0], synth[i][1], dec, slon)
                rk.append(1 + sum(1 for j in ctrl_idx[i]
                                  if _gc_km(places[j][0], places[j][1], dec, slon)
                                  < true))
            curve.append((rank_report(BODY, rk, K_CONTROLS)["z"], r))
            r += STEP
        z_best, r_best = min(curve)
        err = abs(_wrap180(r_best - PLANT))
        say(f"planted {PLANT:.0f} deg, jitter +-{jit:4.0f} deg -> scan finds "
            f"{r_best:5.1f} deg (off by {err:4.1f}), z {z_best:7.2f}  "
            f"{'RECOVERED' if z_best < -3.7 and err <= 15 else 'missed'}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
