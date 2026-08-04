# ABOUTME: The per-event galactic reference the author ties to the ayanamsa: Magha
# ABOUTME: (galactic axis) and Punarvasu (earth-Galaxy ecliptic crossover) vs planets.

# Frame ruling (2026-08-05): ASTGRAF.BAS carries no Abhijit and no 28-division
# data (its 27-name STAR$ list is read and never used), so the galactic frame
# cannot come from the BAS — it comes from Secrets of Sankhya's own 28-sector
# precession layer. Both markers are treated as FIXED directions that a
# tropical chart shifts forward by the ayanamsa — but see the note on Magha
# below: only the crossover has been verified to be a true sidereal value.
#
# CROSSOVER (NU ruling 2026-08-05): "crossover" means the galactic-ecliptic
# NODE — where the galactic plane actually cuts the ecliptic — so the constant
# is measured, not taken from a sector edge. From the IAU J2000 galactic pole
# (RA 192.85948, Dec +27.12825) the pole sits at ecliptic 180.02322/+29.81144,
# putting the two nodes at ecliptic 90.02322 (ASCENDING) and 270.02322 — the
# solstice points to within 0.02 deg, the planes standing 60.1886 deg apart.
# The ascending node is the one the equinox last reached (mid-5th millennium
# BC — the author's "zero ascension in Punarvasu", one cycle back).
#
# Why the sidereal value is not a sector edge: the name "Punarvasu" records
# where the EQUINOX stood on the 28-sector wheel when it crossed the node, not
# where the node sits on today's zodiac. The wheel's zero is the 1996 equinox
# while the suite's sidereal zero is ~23.8 deg away (ayanamsa), so the same
# direction reads 89.967 on the wheel (= the Punarvasu sector boundary at
# 90.0, 0.033 deg out) and 66.171 in suite-sidereal — one sky direction, two
# frames. precession.marker_on_wheel() does that conversion.
import math

from .ephemeris import ayanamsa
from .models import ChartResult

SECTOR = 360.0 / 28
CROSSOVER_TROPICAL_J2000 = 90.02322            # measured ascending node
# Derived, not hand-copied, so the two can never drift apart: 66.170810 deg.
PUNARVASU_CROSSOVER_SIDEREAL = (CROSSOVER_TROPICAL_J2000 - ayanamsa(2000)) % 360
MAGHA_AXIS_SIDEREAL = 9.5 * SECTOR             # 122.142857 deg — sector-10 center
# ^ Magha is NOT ruled: it remains the book's sector-10 center, which makes it
# a WHEEL value despite the _SIDEREAL name (precession.equinox_offsets uses it
# as-is for that reason, while marker_longitudes below still treats it as
# sidereal — the same frame mismatch the crossover carried until 2026-08-05,
# left in place because fixing it means choosing a frame).
# THE FORK, in full in FRAMEWORK.md open question 9: sector-10 centre
# (122.143, in force) vs the galactic CENTRE, Sgr A* at suite-sidereal 243.00
# (folded 63.00) — 59 deg apart, so no orb hides the choice.


def marker_longitudes(result: ChartResult) -> tuple[float, float]:
    """(crossover, magha_axis) in the CHART's own frame."""
    if result.ayanamsa:                        # sidereal chart: markers as-is
        shift = 0.0
    else:                                      # tropical: sidereal + ayanamsa
        from .grid import jd_to_calendar
        shift = ayanamsa(jd_to_calendar(math.floor(result.jd + 0.5))[0])
    return ((PUNARVASU_CROSSOVER_SIDEREAL + shift) % 360,
            (MAGHA_AXIS_SIDEREAL + shift) % 360)


def galactic_separations(result: ChartResult) -> dict[str, dict[str, float]]:
    """Per body: point separation from the crossover, axis distance from Magha."""
    cross, magha = marker_longitudes(result)
    out: dict[str, dict[str, float]] = {}
    for name, pos in result.positions.items():
        lon = pos.longitude
        point = abs((lon - cross + 180) % 360 - 180)
        d = abs((lon - magha) % 180)
        out[name] = {"crossover_sep": round(point, 6),
                     "magha_axis_sep": round(min(d, 180 - d), 6)}
    return out
