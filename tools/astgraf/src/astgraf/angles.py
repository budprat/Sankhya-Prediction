# ABOUTME: Chart angles (Asc/Desc/MC/IC) and the solvers that invert them. The location
# ABOUTME: rule built on them was graded against the catalog and RETIRED — see below.

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
# GRADED AND RETIRED AS A PREDICTOR (2026-08-05, scripts/angle_grade.py).
# Over the 1434 declustered post-1900 M7+ events with epicenters, scored against
# 49 leave-one-out epicenter control PLACES per event at the same instant:
#   - no body's angle separation prefers the true epicenter. Best of 15 bodies
#     was Mars at z = -2.27, short of the z = -3.0 multiplicity bar.
#   - the SPECIFIED form (only the acting taught real-giant contact) over 314
#     instances: z = -0.35 at the catalog origin time, and z = +1.20 at the
#     crossing exactness instant — the instant a forward run would actually
#     use. Neither direction shows anything.
#   - the unspecified form is vacuous as warned below: lift 1.050 at orb 3 deg.
# The null is not blindness: scripts/angle_power.py plants epicenters where a
# body sits exactly on an angle — on the MC AND on the Ascendant, since the
# taught Hyderabad/Ulsoor readings are Ascendant ones — and the SAME statistic
# recovers the signal after +-25 deg of jitter (z = -17.9 MC, -17.1 Asc).
# A rule of this shape, that loose, on either angle, would have been found.
# It is not in the catalog.
# The three-anchor fit below is therefore a fit, not evidence — Nepal's
# specified bodies rank 5/50 among control places (top-10%, the sort of thing
# ~1 event in 10 shows), while its unspecified tightest body ranks 25/50, dead
# median. Keep this module for reading a chart's angles; do not use it to
# claim a location.
#
# SELECTIVITY, measured before believing any of it (figures re-measured over
# the 15 SCORED bodies — an earlier pass leaked Pluto in, which is outside
# BAND_BODIES and outside the doctrine): "SOME body within 3 deg of SOME angle"
# is nearly vacuous — 60.8% of random site/instant pairs satisfy it, median
# tightest 2.23 deg. Against that bar Nepal's 2.00 deg is unremarkable (46% of
# random sites do better), Hyderabad's 0.56 is top-16%, Ulsoor's 0.09 is
# top-2.9%. The rule therefore carries content ONLY in its specified form:
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

from .bands import REAL_POSITION_OFFSETS, real_longitude
from .ephemeris import compute_raw
from .grid import jd_to_calendar


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


def angles_from_chart(chart) -> dict[str, float]:
    """The four angles of an already-computed site chart, in tropical longitude.
    Grading sweeps re-solve one chart per (instant, place) pair, so callers that
    already hold the chart must not pay for a second one."""
    asc = chart.positions["Ascendant"].longitude
    mc = chart.cusps[0]
    return {"Asc": asc, "Desc": (asc + 180) % 360,
            "MC": mc, "IC": (mc + 180) % 360}


def angles_at(jd: float, lat: float, lon_east: float) -> dict[str, float]:
    """The four angles of the site chart, in tropical longitude."""
    return angles_from_chart(site_chart(jd, lat, lon_east))


def body_longitudes(chart) -> dict[str, float]:
    """Every plotted body plus its real (light-time-corrected) counterpart.
    The Ascendant is dropped — it IS an angle, so it would score zero.
    Note this includes Pluto, which is NOT in BAND_BODIES: callers scoring
    against the doctrine's body set must filter, not assume."""
    pos = {b: p.longitude for b, p in chart.positions.items()
           if b != "Ascendant"}
    for g in REAL_POSITION_OFFSETS:
        pos[f"real-{g}"] = real_longitude(chart, g)
    return pos


def bodies_on_angles(jd: float, lat: float, lon_east: float,
                     orb: float = 3.0) -> list[tuple[float, str, str]]:
    """(separation, angle, body) for every body within `orb` of an angle.
    This DESCRIBES a chart; it does not identify a place — the location claim
    built on it was graded against the catalog and failed (header)."""
    c = site_chart(jd, lat, lon_east)
    ax = angles_from_chart(c)
    pos = body_longitudes(c)
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
