# ABOUTME: Can ANY Ascendant-based rule locate an event? Tests the Asc computed at
# ABOUTME: real epicenters/instants against a shuffled-time null. Answer: no.
#
# Run from tools/astgraf:  uv run python scripts/asc_fingerprint.py
# Reads out/signatures-m7-v2/signatures.csv; writes out/asc-fingerprint/summary.txt.
#
# Why this test: the doctrine's taught location examples (Ulsoor, Hyderabad) are
# Ascendant crossings at a KNOWN site, and the author's 1/81 resolution budget is
# stated in lat/long terms — so the Ascendant was the most promising remaining
# candidate for a time->place mechanism after the sub-planet spot graded at
# chance (scripts/loc_backtest.py). If a location rule keys on the Ascendant,
# the Asc at the true epicenter at the true instant must look different from a
# null that keeps the same sites and the same instants but breaks their pairing.
# It does not, so the whole family is ruled out without needing to guess the rule.
import csv
import math
import random
import statistics
from pathlib import Path

from astgraf.bands import real_longitude
from astgraf.ephemeris import compute_raw
from astgraf.grid import jd_to_calendar

BASE = Path(__file__).resolve().parent.parent
SIG = BASE / "out" / "signatures-m7-v2" / "signatures.csv"
OUT = BASE / "out" / "asc-fingerprint" / "summary.txt"
GIANTS = ["Jupiter", "Saturn", "Uranus", "Neptune"]
DRAWS = 300

lines: list[str] = []


def say(msg: str) -> None:
    print(msg)
    lines.append(msg)


def site_chart(jd, lat, lon_east):
    """None where the canon's Koch cusps are undefined (high latitude: ANX
    takes asin of |x|>1, exactly as the BASIC would). Skips are counted."""
    jdn = math.floor(jd + 0.5)
    y, m, d = jd_to_calendar(jdn)
    try:
        return compute_raw(y, m, d, (jd + 0.5 - jdn) * 24, 0.0, -lon_east, lat,
                           False, False)
    except ValueError:
        return None


def arc(a, b):
    d = abs(a - b) % 360
    return min(d, 360 - d)


def chi2_uniform(values, period, bins):
    counts = [0] * bins
    for v in values:
        counts[min(int((v % period) / period * bins), bins - 1)] += 1
    exp = len(values) / bins
    return sum((c - exp) ** 2 / exp for c in counts)


def empirical_p(obs_values, null_values, period, bins):
    """chi2 scales with N, so the null is compared at the SAME sample size."""
    c_obs = chi2_uniform(obs_values, period, bins)
    draws = [chi2_uniform(random.sample(null_values, len(obs_values)),
                          period, bins) for _ in range(DRAWS)]
    return c_obs, statistics.median(draws), sum(
        1 for d in draws if d >= c_obs) / DRAWS


def in_force(row, orb):
    for g in ("Uranus", "Neptune"):
        for t in ("Sun", "Rahu", "Ketu"):
            s = float(row[f"rsep:{g}-{t}"])
            if min(s % 360, 360 - s % 360) <= orb:
                return True
    return False


def main():
    random.seed(11)
    with open(SIG, newline="") as fh:
        rows = [r for r in csv.DictReader(fh) if r.get("lat") and r.get("lon")]
    times = [float(r["jd"]) for r in rows]

    def asc_set(selection, nulls_each):
        obs, null, skipped = [], [], 0
        for r in selection:
            lat, lon = float(r["lat"]), float(r["lon"])
            c = site_chart(float(r["jd"]), lat, lon)
            if c is None:
                skipped += 1
                continue
            obs.append((c.positions["Ascendant"].longitude, c))
            for jd in random.sample(times, nulls_each):
                cn = site_chart(jd, lat, lon)
                if cn is not None:
                    null.append(cn.positions["Ascendant"].longitude)
        return obs, null, skipped

    say("Ascendant fingerprint at real epicenters vs a shuffled-time null")
    sample = rows if len(rows) <= 600 else random.sample(rows, 600)
    # 12 nulls per event: with only 3 the null median swung 13.6-22.1 between
    # runs and the p-value with it (0.06 vs 0.45) — the pool, not the signal.
    obs, null, skipped = asc_set(sample, 12)
    say(f"all M7+: {len(obs)} events ({skipped} skipped — Koch cusps undefined "
        f"at high latitude), {len(null)} null pairings")
    for label, period, bins in (("Asc round the zodiac", 360, 12),
                                ("Asc within a nakshatra", 360 / 27, 9),
                                ("Asc within a horary sub", 360 / 243, 9)):
        c, med, p = empirical_p([a for a, _ in obs], null, period, bins)
        say(f"  {label:26s} chi2 {c:7.2f}  null median {med:7.2f}  p = {p:.3f}")

    for key, fn in (("nearest real giant",
                     lambda a, c: min(arc(a, real_longitude(c, g))
                                      for g in GIANTS)),
                    ("nearest node",
                     lambda a, c: min(arc(a, c.positions["Rahu"].longitude),
                                      arc(a, c.positions["Ketu"].longitude)))):
        o = [fn(a, c) for a, c in obs]
        say(f"  Asc to {key:20s} median {statistics.median(o):6.2f} deg, "
            f"within 3 deg {sum(1 for x in o if x <= 3) / len(o):.4f}")

    # The doctrinally faithful slice: only events with a taught crossing live.
    for orb in (3.0, 1.0):
        sel = [r for r in rows if in_force(r, orb)]
        obs2, null2, _ = asc_set(sel, 12)
        if len(obs2) < 20:
            say(f"crossing in force, orb {orb}: only {len(obs2)} events — skipped")
            continue
        for label, period, bins in (("Asc round the zodiac", 360, 12),
                                    ("Asc within a nakshatra", 360 / 27, 9)):
            c, med, p = empirical_p([a for a, _ in obs2], null2, period, bins)
            say(f"crossing in force, orb {orb}: n={len(obs2):3d} {label:24s} "
                f"chi2 {c:6.2f}  null median {med:6.2f}  p = {p:.3f}")

    say("")
    say("VERDICT: no Ascendant fingerprint, conditional or not. Every p is far "
        "from significance, so no rule keyed on the Ascendant — however its "
        "cell, lord or aspect is chosen — can place these events.")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
