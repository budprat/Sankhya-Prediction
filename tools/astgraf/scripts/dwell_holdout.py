# ABOUTME: Held-out test of the dwell->magnitude lead on M6.0-6.9, a band disjoint from
# ABOUTME: the M7+ corpus that produced it. One pre-registered cell, no re-tuning.
#
# Run from tools/astgraf:  uv run python scripts/dwell_holdout.py
# Reads data/usgs-m6-1900-2020.csv (USGS FDSN, minmag 6.0 maxmag 6.99),
# writes out/dwell-holdout/summary.txt.
#
# PRE-REGISTERED BEFORE RUNNING (NU, 2026-08-05). scripts/dwell_grade.py found
# dwell vs magnitude rho = +0.322 (n = 44) in the taught-giants/orb-1 cell,
# family-wise p = 0.042 over four cells. That cell was ONE of four inspected
# and the dwell construction was fitted to a single anchor, so the finding
# needs data it cannot have touched. The M6.0-6.9 band is disjoint from M7+ by
# construction.
#   PRIMARY TEST: exactly one cell — taught giants (real-Uranus, real-Neptune)
#   against Sun/Rahu/Ketu at orb 1 deg, dwell = SUM of active separations,
#   Spearman against magnitude, one-sided (the direction was predicted).
#   PREDICTION: rho > 0, of order +0.3.
# Everything after the primary test is secondary and labelled as such.
#
# KNOWN ATTENUATION, stated in advance so it cannot be used as an excuse after
# the fact: this band spans 0.99 magnitude units against the M7+ corpus's 2.5,
# and range restriction shrinks a real correlation. The power arm therefore
# measures what is detectable AT THIS n and THIS spread, so a null can be read
# as a null rather than as lost dynamic range.
import csv
import random
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# Must follow the sys.path insert; reuses dwell_grade's EXACT dwell + statistic.
from dwell_grade import TAUGHT_GIANTS, dwell, perm_p_corr, spearman  # noqa: I001
from astgraf.signatures import _chart_for_time, decluster

BASE = Path(__file__).resolve().parent.parent
CAT = BASE / "data" / "usgs-m6-1900-2020.csv"
OUT = BASE / "out" / "dwell-holdout" / "summary.txt"
ORB = 1.0
N_PERM = 5000

lines: list[str] = []


def say(msg: str) -> None:
    print(msg)
    lines.append(msg)


def main() -> None:
    with open(CAT, newline="") as fh:
        rows = [r for r in csv.DictReader(fh)
                if r.get("time") and r.get("latitude") and r.get("longitude")
                and r.get("mag")]
    mags_all = [float(r["mag"]) for r in rows]
    if max(mags_all) >= 7.0:
        raise SystemExit("catalog is not disjoint from the M7+ corpus")
    say(f"held-out dwell test — {len(rows)} M6.0-{max(mags_all):.2f} events "
        "1900-2020 (USGS FDSN), disjoint from the M7+ corpus by construction")

    say("declustering with the same 7 d / 500 km keep-largest rule ...")
    kept = decluster(rows)
    say(f"{len(kept)} events after declustering")

    jds = [_chart_for_time(r["time"]).jd for r in kept]
    mags = [float(r["mag"]) for r in kept]
    say(f"magnitude spread: {min(mags):.2f}-{max(mags):.2f} "
        f"(sd {statistics.pstdev(mags):.3f}) vs the M7+ corpus's 7.0-9.5")

    say("computing dwell ...")
    dw = [dwell(j, TAUGHT_GIANTS, ORB) for j in jds]
    idx = [i for i, (d, _) in enumerate(dw) if d > 0]
    xs = [dw[i][0] for i in idx]
    ys = [mags[i] for i in idx]
    say(f"{len(idx)} events carry an active taught crossing at orb {ORB} deg "
        f"({len(idx) / len(kept):.4f} of the corpus)")

    # ---------------- PRIMARY, pre-registered ----------------------------
    rng = random.Random(31)
    rho = spearman(xs, ys)
    ys_shuf = list(ys)
    ge = 0
    for _ in range(N_PERM):
        rng.shuffle(ys_shuf)
        if spearman(xs, ys_shuf) >= rho:
            ge += 1
    p_one = ge / N_PERM
    p_two = perm_p_corr(xs, ys, rho, rng, N_PERM)
    say("")
    say("=== PRIMARY (pre-registered): taught giants, orb 1, dwell vs mag ===")
    say(f"n = {len(idx)}   rho = {rho:+.4f}")
    say(f"one-sided permutation p = {p_one:.4f}   (two-sided {p_two:.4f})")
    say("M7+ found rho = +0.3223 (n = 44). Prediction was rho > 0, order +0.3.")
    say(f"VERDICT: {'REPLICATES' if p_one < 0.05 and rho > 0 else 'DOES NOT REPLICATE'}")

    # ---------------- SECONDARY ------------------------------------------
    say("")
    say("--- secondary (not pre-registered, read with that in mind) ---")
    ks = [dw[i][1] for i in idx]
    say(f"crossing count vs magnitude: rho {spearman(ks, ys):+.4f}")
    for kv in sorted(set(ks)):
        sd_ = [x for x, k in zip(xs, ks) if k == kv]
        sm_ = [y for y, k in zip(ys, ks) if k == kv]
        if len(sd_) >= 20:
            say(f"   within count={kv} (n={len(sd_):4d}): rho "
                f"{spearman(sd_, sm_):+.4f}")
    med = statistics.median([jds[i] for i in idx])
    for half, keep in (("earlier", lambda i: jds[i] <= med),
                       ("later", lambda i: jds[i] > med)):
        sel = [i for i in idx if keep(i)]
        say(f"   {half:8s} n={len(sel):4d}  rho "
            f"{spearman([dw[i][0] for i in sel], [mags[i] for i in sel]):+.4f}")
    post = [i for i in idx if _chart_for_time(kept[i]['time']).jd and
            int(kept[i]["time"][0:4]) >= 1970]
    say(f"   1970+ only (M6 completeness) n={len(post):4d}  rho "
        f"{spearman([dw[i][0] for i in post], [mags[i] for i in post]):+.4f}")

    # --- pooled, to remove the range-restriction excuse entirely ---------
    # The M6 band spans 0.99 magnitude units, so a null there could in
    # principle be attenuation rather than absence. Pooling M6 with the M7+
    # corpus gives the full 6.0-9.5 range at maximum n: if dwell scales
    # magnitude at all, this is where it must show.
    say("")
    say("--- pooled M6 + M7+ (full 6.0-9.5 range, maximum dynamic range) ---")
    sig = BASE / "out" / "signatures-m7-v2" / "signatures.csv"
    with open(sig, newline="") as fh:
        m7 = [(float(r["jd"]), float(r["mag"])) for r in csv.DictReader(fh)]
    px, py = list(xs), list(ys)
    for j, m in m7:
        d, _k = dwell(j, TAUGHT_GIANTS, ORB)
        if d > 0:
            px.append(d)
            py.append(m)
    rho_p = spearman(px, py)
    p_pool = perm_p_corr(px, py, rho_p, random.Random(41), N_PERM)
    say(f"n = {len(px)} (M6 {len(xs)} + M7+ {len(px) - len(xs)}), "
        f"magnitude {min(py):.1f}-{max(py):.1f}")
    say(f"rho = {rho_p:+.4f}, two-sided permutation p = {p_pool:.4f}")

    # ---------------- POWER ----------------------------------------------
    say("")
    say("--- power at THIS n and THIS magnitude spread ---")
    n_k = len(xs)
    order = sorted(range(n_k), key=lambda i: xs[i])
    norm = [0.0] * n_k
    for pos, i in enumerate(order):
        norm[i] = (pos + 0.5) / n_k - 0.5
    for target in (0.05, 0.10, 0.20, 0.32):
        det, rr = 0, []
        for seed in range(12):
            prng = random.Random(seed * 17 + int(target * 100))
            fake = [target * v * 3.464
                    + prng.gauss(0, (1 - target ** 2) ** 0.5) for v in norm]
            r = spearman(xs, fake)
            rr.append(r)
            if perm_p_corr(xs, fake, r, prng, 400) < 0.05:
                det += 1
        say(f"true rho {target:.2f} -> recovered {statistics.mean(rr):+.3f}, "
            f"detected {det}/12")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
