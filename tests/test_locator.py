# ABOUTME: Tests the event-locator: NU's confirmed light-time rule — from the planet's
# ABOUTME: culmination meridian at the crossing instant, rotate west by light-time x 15deg/h.

import pytest

from astgraf.ephemeris import compute_chart
from astgraf.locator import LIGHT_MINUTES, equatorial, locate
from astgraf.models import BodyPosition, ChartMoment, ChartResult


def make_result(body: str, sidereal_lon: float, beta: float = 0.0,
                gmst: float = 0.0, ayanamsa: float = 0.0,
                obliquity: float = 23.44) -> ChartResult:
    return ChartResult(
        positions={body: BodyPosition(name=body, longitude=sidereal_lon,
                                      retrograde=False, ecliptic_latitude=beta)},
        ayanamsa=ayanamsa, jd=0.0, gmst=gmst, obliquity=obliquity)


def test_doctrinal_light_minutes():
    assert LIGHT_MINUTES == {"Jupiter": 40.0, "Saturn": 80.0,
                             "Uranus": 150.0, "Neptune": 240.0}


def test_equatorial_transform_anchors():
    ra, dec = equatorial(0.0, 0.0, 23.44)
    assert ra == pytest.approx(0.0, abs=1e-9)
    assert dec == pytest.approx(0.0, abs=1e-9)
    ra, dec = equatorial(90.0, 0.0, 23.44)
    assert ra == pytest.approx(90.0, abs=1e-9)
    assert dec == pytest.approx(23.44, abs=1e-9)   # solstice point sits at +obliquity
    ra, dec = equatorial(180.0, 0.0, 23.44)
    assert ra % 360 == pytest.approx(180.0, abs=1e-9)
    assert dec == pytest.approx(0.0, abs=1e-9)


def test_locate_rotates_west_by_light_time():
    # Body culminating over Greenwich (RA = GMST = 0): Jupiter's 40 min -> 10 deg west.
    loc = locate(make_result("Jupiter", 0.0), "Jupiter")
    assert loc.culmination_longitude_east == pytest.approx(0.0, abs=1e-9)
    assert loc.event_longitude_east == pytest.approx(-10.0, abs=1e-9)
    assert loc.event_latitude_north == pytest.approx(0.0, abs=1e-9)
    # Neptune's 240 min -> 60 deg west of the culmination meridian.
    loc = locate(make_result("Neptune", 90.0), "Neptune")
    assert loc.culmination_longitude_east == pytest.approx(90.0, abs=1e-9)
    assert loc.event_longitude_east == pytest.approx(30.0, abs=1e-9)
    assert loc.event_latitude_north == pytest.approx(23.44, abs=1e-6)


def test_locate_uses_gmst_and_wraps():
    # GMST 30: RA 90 culminates at 60E. Rotation past -180 wraps into the east.
    loc = locate(make_result("Saturn", 90.0, gmst=30.0), "Saturn")
    assert loc.culmination_longitude_east == pytest.approx(60.0, abs=1e-9)
    loc = locate(make_result("Neptune", 190.0, gmst=360.0 - 0.0), "Neptune")
    assert -180 < loc.event_longitude_east <= 180


def test_locate_adds_ayanamsa_back_for_the_physical_sky():
    # Sidereal 66.33 + ayanamsa 23.67 = tropical 90 -> declination +obliquity.
    loc = locate(make_result("Uranus", 66.33, ayanamsa=23.67), "Uranus")
    assert loc.event_latitude_north == pytest.approx(23.44, abs=1e-6)


def test_locate_returns_none_for_bodies_without_light_time():
    assert locate(make_result("Ketu", 100.0), "Ketu") is None
    assert locate(make_result("Moon", 100.0), "Moon") is None


def test_distance_true_light_minutes():
    # NU 2026-08-02: displacement follows the planet's actual distance ("figures
    # are for the nearest position"). Engine distances calibrate via the AU quirk.
    from astgraf.locator import light_minutes_for
    chart = compute_chart(ChartMoment(
        year=2016, month=6, day=3, hour=12, minute=0, utc_offset_hours=0.0,
        longitude_east=0.0, latitude_north=0.0))
    sun_au = chart.positions["Sun"].distance * 180 / 3.141592654
    assert 0.98 < sun_au < 1.03
    assert 32 < light_minutes_for(chart, "Jupiter") < 55
    assert 66 < light_minutes_for(chart, "Saturn") < 93
    assert 143 < light_minutes_for(chart, "Uranus") < 176
    assert 238 < light_minutes_for(chart, "Neptune") < 262
    assert light_minutes_for(chart, "Moon") is None
    # Synthetic results without distances fall back to the doctrine constants.
    assert light_minutes_for(make_result("Jupiter", 0.0), "Jupiter") == 40.0


def test_engine_exposes_gmst_obliquity_and_planet_latitudes():
    chart = compute_chart(ChartMoment(
        year=1987, month=8, day=28, hour=2, minute=55, utc_offset_hours=5.5,
        longitude_east=76 + 57 / 60, latitude_north=28 + 48 / 60))
    assert 0 <= chart.gmst < 360
    assert chart.obliquity == pytest.approx(23.4409, abs=0.001)
    assert chart.positions["Sun"].ecliptic_latitude == 0.0
    for planet in ("Jupiter", "Saturn", "Uranus", "Neptune"):
        beta = chart.positions[planet].ecliptic_latitude
        assert 0 < abs(beta) < 3.0, planet
    # Neptune in sidereal Sagittarius sits south of the equator.
    loc = locate(chart, "Neptune")
    assert loc.event_latitude_north < 0
