# ABOUTME: Event-locator per NU's confirmed light-time rule: the crossing acts instantly
# ABOUTME: in the substratum; the marker arrives at light speed. Rotate the culmination
# ABOUTME: meridian west by light-time x 15 deg/hour; latitude from the declination.

import math

from pydantic import BaseModel

from .models import ChartResult

# NU's doctrinal light-travel times (minutes), confirmed 2026-08-01 as the
# planet-to-Earth light times: rotation west = minutes x 0.25 deg.
LIGHT_MINUTES = {"Jupiter": 40.0, "Saturn": 80.0, "Uranus": 150.0, "Neptune": 240.0}


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
    minutes = LIGHT_MINUTES.get(body)
    if minutes is None:
        return None
    position = result.positions[body]
    tropical = (position.longitude + result.ayanamsa) % 360
    ra, dec = equatorial(tropical, position.ecliptic_latitude, result.obliquity)
    culmination = _wrap180(ra - result.gmst)
    event_longitude = _wrap180(culmination - minutes * 0.25)
    return EventLocation(body=body, light_minutes=minutes,
                         culmination_longitude_east=culmination,
                         event_longitude_east=event_longitude,
                         event_latitude_north=dec)
