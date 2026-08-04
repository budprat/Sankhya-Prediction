# ABOUTME: The per-event galactic reference the author ties to the ayanamsa: Magha
# ABOUTME: (galactic axis) and Punarvasu (earth-Galaxy ecliptic crossover) vs planets.

# Frame ruling (2026-08-05): ASTGRAF.BAS carries no Abhijit and no 28-division
# data (its 27-name STAR$ list is read and never used), so the galactic frame
# cannot come from the BAS — it comes from Secrets of Sankhya's own 28-sector
# precession layer, the same layer that defines the markers: the Punarvasu
# crossover is the start of sector 7 ("zero ascension in Punarvasu", the
# 30,000-year anchor), the Magha axis the center of sector 10. Both are FIXED
# SIDEREAL directions; in a tropical chart they shift forward by the ayanamsa.
import math

from .models import ChartResult

SECTOR = 360.0 / 28
PUNARVASU_CROSSOVER_SIDEREAL = 6 * SECTOR      # 77.142857 deg — sector-7 start
MAGHA_AXIS_SIDEREAL = 9.5 * SECTOR             # 122.142857 deg — sector-10 center


def marker_longitudes(result: ChartResult) -> tuple[float, float]:
    """(crossover, magha_axis) in the CHART's own frame."""
    if result.ayanamsa:                        # sidereal chart: markers as-is
        shift = 0.0
    else:                                      # tropical: sidereal + ayanamsa
        from .ephemeris import ayanamsa
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
