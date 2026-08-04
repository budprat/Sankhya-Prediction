# ABOUTME: The site-angle location layer: an event stands where the crossing pair sits
# ABOUTME: on a chart ANGLE — MC fixes a meridian, Ascendant fixes a curve, two give a point.

# Why this and not the sub-planet spot (NU, 2026-08-05): every ecliptic body's
# sub-point is capped at |lat| <= the obliquity (23.44 deg — that IS the
# definition of the tropics), while Gorkha is 28.23 N, Tohoku 38.3, Alaska
# 60.9. The sub-planet construction cannot express the latitude of 44% of M7+
# events. The taught anchors instead all show the CROSSING PAIR on an angle of
# the site's own chart, which is the author's own language:
#   Nepal      Sun 2.00 deg and real-Uranus 2.69 deg from the MC
#              (his taught pair is "real-Uranus on the Sun")
#   Hyderabad  Neptune 0.56 and Ketu 0.59 from the Asc, Rahu 0.59 from the Desc
#              (his "Jup and Nep are at the ket and Rahu nodes")
#   Ulsoor     Neptune 0.09 from the Asc, Saturn 1.51 from the MC
#              (his "the Asc swept Neptune -> Sun -> Ketu -> Uranus")
#
# SELECTIVITY, measured before believing any of it: "SOME body within 3 deg of
# SOME angle" is nearly vacuous — 66% of random site/instant pairs satisfy it,
# median tightest 1.11 deg. Against that bar Nepal's 2.00 deg is unremarkable
# (53% of random sites do better), Hyderabad's 0.56 is top-22%, Ulsoor's 0.09
# is top-3.7%. The rule therefore carries content ONLY in its specified form:
# the pair NAMED BY THE CROSSING must be the pair on the angle — a specific
# body landing within 0.6 deg of a specific angle is a ~1.3% coincidence, and
# it holds for the taught body at Hyderabad and Ulsoor. Do not quote the
# unspecified version as evidence.
#
# CONDITIONING, the honest limit: the MC depends only on sidereal time, so
# "body on the MC" fixes longitude sharply (1 deg of residual = 1 deg of
# longitude). The Ascendant moves only ~0.35 deg per degree of LATITUDE, so a
# 1 deg Asc residual becomes ~3 deg of latitude (~330 km). Latitude is
# therefore intrinsically the weak axis — which is exactly why the author's
# 3-second dwell quantum matters: 3 s of rotation is 0.0125 deg of Asc, i.e.
# ~4 km of latitude. The rule can reach his claimed precision only when the
# crossing instant and the angle condition are both exact.
import math

from .ephemeris import compute_raw
from .grid import jd_to_calendar

ANGLES = ("Asc", "Desc", "MC", "IC")


def site_chart(jd: float, lat: float, lon_east: float):
    jdn = math.floor(jd + 0.5)
    y, m, d = jd_to_calendar(jdn)
    return compute_raw(y, m, d, (jd + 0.5 - jdn) * 24, 0.0, -lon_east, lat,
                       False, False)


def _sep(a: float, b: float) -> float:
    d = abs(a - b) % 360.0
    return min(d, 360.0 - d)


def _wrap(x: float) -> float:
    return (x + 180.0) % 360.0 - 180.0


def angles_at(jd: float, lat: float, lon_east: float) -> dict[str, float]:
    """The four angles of the site chart, in tropical longitude."""
    c = site_chart(jd, lat, lon_east)
    asc = c.positions["Ascendant"].longitude
    mc = c.cusps[0]
    return {"Asc": asc, "Desc": (asc + 180) % 360,
            "MC": mc, "IC": (mc + 180) % 360}


def bodies_on_angles(jd: float, lat: float, lon_east: float,
                     orb: float = 3.0) -> list[tuple[float, str, str]]:
    """(separation, angle, body) for every body within `orb` of an angle —
    the signature that identifies a site as the event's place."""
    c = site_chart(jd, lat, lon_east)
    ax = angles_at(jd, lat, lon_east)
    from .bands import REAL_POSITION_OFFSETS, real_longitude
    pos = {b: p.longitude for b, p in c.positions.items() if b != "Ascendant"}
    for g in REAL_POSITION_OFFSETS:
        pos[f"real-{g}"] = real_longitude(c, g)
    out = [(_sep(v, p), k, b) for k, v in ax.items() for b, p in pos.items()
           if _sep(v, p) <= orb]
    return sorted(out)


def meridian_of(jd: float, target_longitude: float,
                lat_probe: float = 20.0) -> float | None:
    """Longitude where `target_longitude` stands on the MC — a meridian, the
    sharply-determined half of the fix."""
    def f(lon):
        return _wrap(site_chart(jd, lat_probe, lon).cusps[0] - target_longitude)

    step = 0.5
    lon = -180.0
    while lon < 180.0:
        a, b = f(lon), f(min(lon + step, 180.0))
        if a * b <= 0 and abs(b - a) < 10:
            lo, hi = lon, min(lon + step, 180.0)
            for _ in range(50):
                mid = (lo + hi) / 2
                if f(lo) * f(mid) <= 0:
                    hi = mid
                else:
                    lo = mid
            return (lo + hi) / 2
        lon += step
    return None


def latitude_on_meridian(jd: float, lon_east: float,
                         target_longitude: float) -> float | None:
    """Latitude on that meridian where `target_longitude` is on the Ascendant.
    The weak axis — see the conditioning note at the top of this module."""
    def g(lat):
        return _wrap(site_chart(jd, lat, lon_east).positions["Ascendant"].longitude
                     - target_longitude)

    lo, hi = -66.0, 66.0
    if g(lo) * g(hi) > 0:
        return None
    for _ in range(60):
        mid = (lo + hi) / 2
        if g(lo) * g(mid) <= 0:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2
