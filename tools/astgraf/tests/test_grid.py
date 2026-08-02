# ABOUTME: Tests period stepping: the BASIC trick of letting the Julian-day formula
# ABOUTME: normalize overflowed months/days, hourly spacing, labels, and JD roundtrips.

import pytest

from astgraf.ephemeris import julian_day_number
from astgraf.grid import build_rows, jd_to_calendar, jd_value
from astgraf.models import ChartMoment, GridSpec, PeriodUnit

START = ChartMoment(year=2000, month=1, day=1, hour=12, minute=0,
                    utc_offset_hours=0.0, longitude_east=76.95, latitude_north=28.8)


def test_month_overflow_normalizes_through_jd():
    # January + 13 extra months must be the same instant as February next year.
    assert julian_day_number(2000, 14, 1) == julian_day_number(2001, 2, 1)
    assert julian_day_number(2000, 1, 62) == julian_day_number(2000, 3, 2)


def test_yearly_rows_count_and_first_row():
    rows = build_rows(START, GridSpec(unit=PeriodUnit.YEAR, step=1, count=17))
    assert len(rows) == 17
    assert rows[0].label.startswith("2000")
    assert rows[-1].label.startswith("2016")
    jds = [r.jd for r in rows]
    assert jds == sorted(jds)
    assert all(len(r.positions) == 13 for r in rows)


def test_hourly_rows_are_evenly_spaced():
    rows = build_rows(START, GridSpec(unit=PeriodUnit.HOUR, step=2, count=5))
    deltas = [rows[i + 1].jd - rows[i].jd for i in range(4)]
    for d in deltas:
        assert d == pytest.approx(2 / 24, abs=1e-9)


def test_jd_calendar_roundtrip():
    for y, m, d in [(2000, 1, 1), (1987, 8, 28), (1600, 3, 15), (-3100, 2, 17)]:
        j = julian_day_number(y, m, d)
        assert jd_to_calendar(j) == (y, m, d)


def test_jd_value_matches_known_epoch():
    # 2000-01-01 12:00 UT is JD 2451545.0 by definition.
    j = julian_day_number(2000, 1, 1)
    assert jd_value(j, 0.5) == pytest.approx(2451545.0)


def test_deep_time_rows_compute():
    deep = START.model_copy(update={"year": -30000, "month": 3, "day": 1})
    rows = build_rows(deep, GridSpec(unit=PeriodUnit.YEAR, step=800, count=5))
    assert len(rows) == 5
    for row in rows:
        for pos in row.positions:
            assert 0 <= pos.longitude < 360
