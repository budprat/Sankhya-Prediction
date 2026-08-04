# ABOUTME: Retrospective backtest of the location layer over signatures-m7-v2:
# ABOUTME: spot-vs-epicenter distances against a shuffled null, plus the Nepal anchor.
#
# Run from tools/astgraf:  uv run python scripts/loc_backtest.py
# Reads out/signatures-m7-v2/signatures.csv (generator: astgraf-signatures),
# writes out/loc-backtest/summary.txt. Three conventions tested:
#   A) nearest of the four giants' spots at the event instant (arrival-corrected
#      light-time-earlier chart, as stored in the signatures sweep);
#   B) doctrine-conditional: only events where a taught real-giant contact
#      (real-Ura/Nep vs Sun/Rahu/Ketu) is in force, acting giant's spot only;
#   C) the Nepal taught anchor at the crossings' exactness instants (the
#      forward-watchlist convention);
#   D) the author's scalar-pulse reading (2026-08-05 briefing): light-time only
#      converts observed -> REAL (the ahead-offsets), the impulse is immediate,
#      no propagation rotation — spot = sub-REAL-planet point at the instant.
import csv
import random
import statistics
from pathlib import Path

from astgraf.anchors import chart_at, iso_jd, jd_iso_minute, refine_exactness
from astgraf.bands import REAL_POSITION_OFFSETS
from astgraf.locator import _wrap180, equatorial, light_minutes_for, locate
from astgraf.signatures import _gc_km

BASE = Path(__file__).resolve().parent.parent
SIG = BASE / "out" / "signatures-m7-v2" / "signatures.csv"
OUT = BASE / "out" / "loc-backtest" / "summary.txt"
GIANTS = ["Jupiter", "Saturn", "Uranus", "Neptune"]
TARGETS = ["Sun", "Rahu", "Ketu"]
NEPAL = (28.2305, 84.7314)

lines: list[str] = []


def say(msg: str) -> None:
    print(msg)
    lines.append(msg)


def main() -> None:
    with open(SIG, newline="") as fh:
        rows = [r for r in csv.DictReader(fh)
                if r.get("lat") and r.get("lon")]
    say(f"location-layer backtest — {len(rows)} M7+ events with epicenters "
        "(out/signatures-m7-v2)")

    # A) nearest-of-four at the event instant, vs leave-one-out shuffled null.
    # Computed LIVE from locate(): the loc_km columns stored in signatures.csv
    # predate the 2026-08-05 Mathcad-rotation ruling and would be stale here.
    def live_km(lat, lon, jd):
        c = chart_at(jd)
        return min(_gc_km(lat, lon, (loc := locate(c, g)).event_latitude_north,
                          loc.event_longitude_east) for g in GIANTS)

    mins = [live_km(float(r["lat"]), float(r["lon"]), float(r["jd"]))
            for r in rows]
    def live_spots_at(jd):
        c = chart_at(jd)
        out = {}
        for g in GIANTS:
            loc = locate(c, g)
            out[g] = (loc.event_latitude_north, loc.event_longitude_east)
        return out

    live_spots = [live_spots_at(float(r["jd"])) for r in rows]
    null = []
    for i, r in enumerate(rows):
        la, lo = float(r["lat"]), float(r["lon"])
        for j, sp in enumerate(live_spots):
            if i != j:
                null.append(min(_gc_km(la, lo, a, b) for a, b in sp.values()))

    def frac(xs, km):
        return sum(1 for x in xs if x <= km) / len(xs)

    say("A) nearest-of-four-giants at event instant:")
    say(f"   observed: median {statistics.median(mins):.0f} km; within "
        f"1000/2000/3000 km {frac(mins, 1000):.4f}/{frac(mins, 2000):.4f}/"
        f"{frac(mins, 3000):.4f}")
    say(f"   shuffled null ({len(null)} pairings): median "
        f"{statistics.median(null):.0f} km; {frac(null, 1000):.4f}/"
        f"{frac(null, 2000):.4f}/{frac(null, 3000):.4f}")

    # B) doctrine-conditional acting-giant spots.
    for orb in (1.0, 3.0):
        acting = []
        for r, sp in zip(rows, live_spots):
            for g in ("Uranus", "Neptune"):
                for t in TARGETS:
                    s = float(r[f"rsep:{g}-{t}"])
                    if min(s % 360, 360 - s % 360) <= orb:
                        acting.append(_gc_km(float(r["lat"]), float(r["lon"]),
                                             *sp[g]))
        say(f"B) acting real-giant contact in force, orb <= {orb}: "
            f"{len(acting)} contacts; median {statistics.median(acting):.0f} km; "
            f"within 1000/2000/3000 km "
            f"{sum(1 for x in acting if x <= 1000)}/"
            f"{sum(1 for x in acting if x <= 2000)}/"
            f"{sum(1 for x in acting if x <= 3000)} of {len(acting)}")
    say("   single-spot null rates (within 1000/2000/3000 km): "
        "0.0071/0.0314/0.0671 (seed-7 sample, see ledger 2026-08-05)")

    # C) the Nepal taught anchor, all conventions.
    say("C) Nepal 2015-04-25 (Gorkha, taught anchor):")
    for r, sp in zip(rows, live_spots):
        if "Nepal" in r.get("place", "") and r["label"].startswith("2015-04-25"):
            for g in GIANTS:
                say(f"   event-instant {g}: spot {sp[g][0]:.2f}N {sp[g][1]:.2f}E "
                    f"-> {_gc_km(*NEPAL, *sp[g]):.0f} km")
    jd_q = iso_jd("2015-04-25T06:11:25.950Z")
    for a, b in (("Uranus", "Sun"), ("Neptune", "Ketu")):
        ex = refine_exactness(a, b, "rsep", 0.0, jd_q)
        chart = chart_at(ex["jd"])
        base = chart_at(ex["jd"] - (light_minutes_for(chart, a) or 0.0) / 1440.0)
        spot = locate(base, a)
        d = _gc_km(*NEPAL, spot.event_latitude_north, spot.event_longitude_east)
        say(f"   exactness {a}x{b} ({jd_iso_minute(ex['jd'])}): spot "
            f"{spot.event_latitude_north:.2f}N {spot.event_longitude_east:.2f}E "
            f"-> {d:.0f} km")

    # D) scalar-pulse reading: sub-REAL-planet spot, no propagation rotation.
    def spot_real(jd, body):
        c = chart_at(jd)
        p = c.positions[body]
        real = (p.longitude + c.ayanamsa + REAL_POSITION_OFFSETS[body]) % 360
        ra, dec = equatorial(real, p.ecliptic_latitude, c.obliquity)
        return dec, _wrap180(ra - c.gmst)

    spots = [{g: spot_real(float(r["jd"]), g) for g in GIANTS} for r in rows]
    mins_d = [min(_gc_km(float(r["lat"]), float(r["lon"]), la, lo)
                  for la, lo in sp.values()) for r, sp in zip(rows, spots)]
    null_d = []
    for i, r in enumerate(rows):
        la0, lo0 = float(r["lat"]), float(r["lon"])
        for j, sp in enumerate(spots):
            if i != j:
                null_d.append(min(_gc_km(la0, lo0, la, lo)
                                  for la, lo in sp.values()))
    say("D) scalar-pulse reading (sub-REAL-planet spot, no rotation):")
    say(f"   observed: median {statistics.median(mins_d):.0f} km; within "
        f"1000/2000/3000 km {frac(mins_d, 1000):.4f}/{frac(mins_d, 2000):.4f}/"
        f"{frac(mins_d, 3000):.4f}")
    say(f"   shuffled null: median {statistics.median(null_d):.0f} km; "
        f"{frac(null_d, 1000):.4f}/{frac(null_d, 2000):.4f}/"
        f"{frac(null_d, 3000):.4f}")
    for r in rows:
        if "Nepal" in r.get("place", "") and r["label"].startswith("2015-04-25"):
            for g in GIANTS:
                la, lo = spot_real(float(r["jd"]), g)
                say(f"   Nepal {g}: {la:.2f}N {lo:.2f}E -> "
                    f"{_gc_km(*NEPAL, la, lo):.0f} km")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    random.seed(7)
    main()
