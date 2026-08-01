# ABOUTME: Tests the 252-division horary grid (28 equal nakshatras x 9 equal subs x 9
# ABOUTME: sub-subs = 2268), lord cycling, boundary-crossing events, ayanamsa override.

import pytest

from astgraf.ephemeris import ayanamsa_value, compute_chart
from astgraf.horary import (HORARY_NAKSHATRAS_28, LORD_CYCLE, find_sub_crossings,
                            horary_position)
from astgraf.models import BodyPosition, ChartMoment, PeriodRow


def test_twenty_eight_names_with_abhijit_inserted():
    assert len(HORARY_NAKSHATRAS_28) == 28
    assert HORARY_NAKSHATRAS_28[0] == "Aswini"
    assert HORARY_NAKSHATRAS_28[20] == "Uthrashada"
    assert HORARY_NAKSHATRAS_28[21] == "Abhijit"
    assert HORARY_NAKSHATRAS_28[22] == "Sravana"
    assert HORARY_NAKSHATRAS_28[27] == "Revathy"


def test_lord_cycle_is_vimshottari_order():
    assert LORD_CYCLE == ["Ketu", "Venus", "Sun", "Moon", "Mars",
                          "Rahu", "Jupiter", "Saturn", "Mercury"]


def test_zero_longitude_is_first_division():
    p = horary_position(0.0)
    assert (p.division, p.sub, p.subsub) == (1, 1, 1)
    assert p.nakshatra == "Aswini"
    assert p.division_lord == "Ketu"
    assert p.sub_lord == "Ketu"
    assert p.subsub_lord == "Ketu"


def test_sample_ascendant_falls_in_punarvasu_with_jupiter_lord():
    # 80.1068 deg: the 1987 reference Ascendant. Division 7 = Punarvasu, whose
    # cycle lord is Jupiter — matching the reference printout's C.Planet.
    p = horary_position(80.1068)
    assert p.division == 7
    assert p.nakshatra == "Punarvasu"
    assert p.division_lord == "Jupiter"
    assert p.sub == 57
    assert p.subsub == 505


def test_top_of_circle_is_last_divisions():
    p = horary_position(359.999)
    assert (p.division, p.sub, p.subsub) == (28, 252, 2268)
    assert p.nakshatra == "Revathy"
    p0 = horary_position(360.0)
    assert p0.division == 1


def test_abhijit_division():
    assert horary_position(270.1).nakshatra == "Abhijit"


def _rows(samples):
    rows = []
    for i, (jd, lon) in enumerate(samples):
        rows.append(PeriodRow(index=i, label=f"r{i}", jd=jd, positions=[
            BodyPosition(name="Body", longitude=lon, retrograde=False)]))
    return rows


def test_sub_boundary_crossing_detected_and_refined():
    # Boundary between subs 56 and 57 sits at exactly 80.0 deg (56 * 360/252).
    def pos(jd):
        return {"Body": 79.9 + 0.1 * jd}
    rows = _rows([(0.0, pos(0.0)["Body"]), (4.0, pos(4.0)["Body"])])
    events = find_sub_crossings(rows, pos_at_jd=pos)
    assert len(events) == 1
    e = events[0]
    assert e.jd == pytest.approx(1.0, abs=1e-6)
    assert (e.from_sub, e.to_sub) == (56, 57)
    assert e.boundary_deg == pytest.approx(80.0)


def test_retrograde_crossing_direction():
    def pos(jd):
        return {"Body": 80.3 - 0.1 * jd}
    rows = _rows([(0.0, pos(0.0)["Body"]), (4.0, pos(4.0)["Body"])])
    events = find_sub_crossings(rows, pos_at_jd=pos)
    assert len(events) == 1
    assert (events[0].from_sub, events[0].to_sub) == (57, 56)


def test_wrap_crossing_at_zero():
    def pos(jd):
        return {"Body": (359.9 + 0.1 * jd) % 360}
    rows = _rows([(0.0, 359.9), (4.0, 0.3)])
    events = find_sub_crossings(rows, pos_at_jd=pos)
    assert len(events) == 1
    assert (events[0].from_sub, events[0].to_sub) == (252, 1)


def test_ayanamsa_override_shifts_all_longitudes_uniformly():
    base = ChartMoment(year=1987, month=8, day=28, hour=2, minute=55,
                      utc_offset_hours=5.5, longitude_east=76.95, latitude_north=28.8)
    custom = base.model_copy(update={"ayanamsa_rate_arcsec": 50.35})
    default_nam = ayanamsa_value(1987, None, 294)
    custom_nam = ayanamsa_value(1987, 50.35, 294)
    assert custom_nam == pytest.approx((1987 - 294) * 50.35 / 3600, abs=1e-12)
    shift = (default_nam - custom_nam)
    a = compute_chart(base).positions["Sun"].longitude
    b = compute_chart(custom).positions["Sun"].longitude
    assert (b - a) % 360 == pytest.approx(shift % 360, abs=1e-9)
