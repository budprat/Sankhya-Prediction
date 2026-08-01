# ABOUTME: Pins the Python ephemeris port against the family canon: PRATEEK.docx output
# ABOUTME: (the ASTROLOG.BAS-era oracle) plus the honest engine-computed Moon longitude.

import pytest

from astgraf.ephemeris import ayanamsa, compute_chart
from astgraf.models import ChartMoment

PRATEEK = ChartMoment(
    year=1987, month=8, day=28, hour=2, minute=55,
    utc_offset_hours=5.5,
    longitude_east=76 + 57 / 60,
    latitude_north=28 + 48 / 60,
    sidereal=True, equal_houses=True,
)

# Absolute sidereal longitudes from PRATEEK.docx (sign + deg + min -> degrees).
# The docx truncates minutes, so each body gets a one-arcminute-plus tolerance.
DOCX_ORACLE = {
    "Sun": 130.4,
    "Mercury": 137 + 47 / 60,
    "Venus": 131 + 40 / 60,
    "Mars": 129 + 33 / 60,
    "Jupiter": 6 + 2 / 60,
    "Saturn": 230 + 52 / 60,
    "Rahu": 340 + 10 / 60,
    "Ketu": 160 + 10 / 60,
    "Uranus": 239 + 2 / 60,
    "Neptune": 251 + 39 / 60,
    "Pluto": 194 + 4 / 60,
    "Ascendant": 80.1,
}

# Canon Moon. The docx prints 41' where canon computes 40.16' — 0.014 deg apart,
# inside the truncation tolerance; plausibly single-precision drift in the original
# GW-BASIC run, so the Moon is pinned to the double-precision canon instead.
HONEST_MOON = 168.66934322

# Full-precision cross-implementation oracle captured 2026-08-01 by running the app's
# JS engine headless (node vm harness, DOM stubbed, report callback intercepted) with
# its ss2 array corrected to the ASTROLOG.BAS DATA canon — the shipped engine drops
# Sun's two zero T^2 rows, shifting Mercury +16" and Venus +21". The corrected run
# matches this Python port to 10 decimals on all 13 bodies; matching also requires
# the suite's truncated pi (3.141592654).
JS_ORACLE = {
    "Sun": 130.4049192468, "Mercury": 137.7989135630, "Venus": 131.6804811752,
    "Mars": 129.5634143188, "Jupiter": 6.0402862683, "Saturn": 230.8687801326,
    "Uranus": 239.0432207265, "Neptune": 251.6615980984, "Pluto": 194.0696228950,
    "Moon": 168.6693432205, "Rahu": 340.1737455607, "Ketu": 160.1737455607,
    "Ascendant": 80.1068047095,
}


@pytest.fixture(scope="module")
def chart():
    return compute_chart(PRATEEK)


def test_ayanamsa_closed_form():
    assert ayanamsa(1987) == pytest.approx((1987 - 294) * 151 / 10800, abs=1e-12)
    assert ayanamsa(1987) == pytest.approx(23.670648148, abs=1e-6)


def test_bodies_match_docx(chart):
    for body, expected in DOCX_ORACLE.items():
        assert chart.positions[body].longitude == pytest.approx(expected, abs=0.02), body


def test_moon_matches_honest_engine_value(chart):
    assert chart.positions["Moon"].longitude == pytest.approx(HONEST_MOON, abs=1e-6)


def test_all_bodies_match_js_engine_oracle(chart):
    for body, expected in JS_ORACLE.items():
        assert chart.positions[body].longitude == pytest.approx(expected, abs=1e-6), body


def test_retrograde_flags_match_docx(chart):
    retro = {name: p.retrograde for name, p in chart.positions.items()}
    assert retro["Jupiter"] and retro["Uranus"] and retro["Neptune"]
    for body in ("Sun", "Mercury", "Venus", "Mars", "Saturn", "Pluto"):
        assert not retro[body], body
    # Sun, Moon, nodes and Ascendant never carry a retrograde flag.
    for body in ("Moon", "Rahu", "Ketu", "Ascendant"):
        assert not retro[body], body


def test_all_longitudes_normalized(chart):
    for name, p in chart.positions.items():
        assert 0 <= p.longitude < 360, name


def test_quake_pdf_tropical_koch_oracle():
    """QUAKE.pdf: the suite's own tropical (ayanamsa 0) Koch-path printout of the
    2015 Nepal earthquake chart — the only canon oracle exercising the W/W path."""
    moment = ChartMoment(year=2015, month=4, day=25, hour=11, minute=40,
                         utc_offset_hours=5.5, longitude_east=86.0,
                         latitude_north=28.0, sidereal=False, equal_houses=False)
    chart = compute_chart(moment)
    expected = {
        "Ascendant": 129.0, "Sun": 34 + 44 / 60, "Moon": 116 + 22 / 60,
        "Mars": 48.0 - 2 / 60, "Mercury": 50 + 35 / 60, "Jupiter": 133.0,
        "Venus": 75 + 44 / 60, "Saturn": 243 + 33 / 60, "Rahu": 188 + 53 / 60,
        "Ketu": 8 + 53 / 60, "Uranus": 17 + 34 / 60, "Neptune": 339 + 27 / 60,
        "Pluto": 285 + 56 / 60,
    }
    for body, value in expected.items():
        assert chart.positions[body].longitude == pytest.approx(value, abs=0.03), body
    assert chart.positions["Saturn"].retrograde
    assert chart.positions["Pluto"].retrograde
    assert not chart.positions["Jupiter"].retrograde


def test_tropical_differs_by_exactly_the_ayanamsa():
    tropical = compute_chart(PRATEEK.model_copy(update={"sidereal": False}))
    sidereal = compute_chart(PRATEEK)
    for body in ("Sun", "Saturn", "Pluto", "Moon"):
        delta = (tropical.positions[body].longitude
                 - sidereal.positions[body].longitude) % 360
        assert delta == pytest.approx(ayanamsa(1987) % 360, abs=1e-9), body
