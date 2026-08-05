# ABOUTME: Event-locator per NU's confirmed light-time rule: the crossing acts instantly
# ABOUTME: in the substratum; the marker arrives at light speed. Rotate the culmination
# ABOUTME: meridian west by light-time x 15 deg/hour; latitude from the declination.

import math

from pydantic import BaseModel

from .bands import REAL_POSITION_OFFSETS
from .models import ChartResult

# NU RULING 2026-08-05: "Mathcad version is the one" — the ground rotation
# during light travel is the Mathcad quantity (a/2-1)*500/240, which is ALREADY
# expressed in degrees (500 s per AU of travel, 240 s per degree of rotation).
# So the offsets in bands.REAL_POSITION_OFFSETS ARE "rotate the long to suit",
# and the light-time is simply offset x 4 minutes.
#
# THIS SUPERSEDES TWO EARLIER READINGS, both on record:
#  * the prose figures 40/80/150/240 min (= nearest-approach (a-1) AU, giving
#    10/20/37.5/60 deg) that this module used until now;
#  * the 2026-08-02 distance-true refinement — the Mathcad is defined on the
#    orbital radius, not the instantaneous distance, so the rotation is FIXED.
# Ground scale at the equator: Jup ~371 km, Sat ~875, Ura ~1987, Nep ~3238.

# CAUTION: Jupiter's and Saturn's entries are PROVISIONAL (canon-axis derived,
# NU ruling 2026-08-04) pending NU's exact Sankhya NR values — so under this
# rule they set SPOT LONGITUDES too, not just real positions. When the exact
# values land, regenerate every published Jupiter/Saturn longitude (expected
# shift <= 0.02 deg). Uranus/Neptune are the Mathcad's own digits.
ROTATION_DEGREES = dict(REAL_POSITION_OFFSETS)
MINUTES_PER_DEGREE = 4.0                  # Earth turns 1 deg in 4 minutes
LIGHT_MINUTES = {b: d * MINUTES_PER_DEGREE for b, d in ROTATION_DEGREES.items()}


def light_minutes_for(result: ChartResult, body: str) -> float | None:
    """Light time as the Mathcad defines it — a constant of the orbit, so the
    chart's instantaneous distance is deliberately not consulted."""
    return LIGHT_MINUTES.get(body)


class EventLocation(BaseModel):
    body: str
    light_minutes: float
    culmination_longitude_east: float
    event_longitude_east: float
    event_latitude_north: float


def _wrap180(x: float) -> float:
    d = x % 360
    return d - 360 if d > 180 else d


def equatorial(lambda_deg: float, beta_deg: float, eps_deg: float) -> tuple[float, float]:
    """Ecliptic (tropical) -> equatorial: right ascension and declination, degrees."""
    lam, bet, eps = (math.radians(v) for v in (lambda_deg, beta_deg, eps_deg))
    ra = math.atan2(math.sin(lam) * math.cos(eps) - math.tan(bet) * math.sin(eps),
                    math.cos(lam))
    dec = math.asin(math.sin(bet) * math.cos(eps)
                    + math.cos(bet) * math.sin(eps) * math.sin(lam))
    return math.degrees(ra) % 360, math.degrees(dec)


def locate(result: ChartResult, body: str) -> EventLocation | None:
    """The event's spot for one planet at one instant; None if no light-time is defined."""
    minutes = light_minutes_for(result, body)
    if minutes is None:
        return None
    position = result.positions[body]
    tropical = (position.longitude + result.ayanamsa) % 360
    ra, dec = equatorial(tropical, position.ecliptic_latitude, result.obliquity)
    culmination = _wrap180(ra - result.gmst)
    # The rotation IS the Mathcad offset — say so here rather than deriving it
    # back out of the minutes (identical value, but the rule stays visible).
    event_longitude = _wrap180(culmination - ROTATION_DEGREES[body])
    return EventLocation(body=body, light_minutes=minutes,
                         culmination_longitude_east=culmination,
                         event_longitude_east=event_longitude,
                         event_latitude_north=dec)
