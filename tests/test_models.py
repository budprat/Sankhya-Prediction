# ABOUTME: Tests modern-convention input parsing (east-positive, UTC offsets) and the
# ABOUTME: conversion to the BASIC engine's east-negative internals — the sign-bug hotspot.

import pytest
from pydantic import ValidationError

from astgraf.models import (
    ChartMoment, GridSpec, PeriodUnit,
    parse_latitude, parse_longitude, parse_utc_offset,
)


def test_parse_longitude_east_west_and_decimal():
    assert parse_longitude("76:57E") == pytest.approx(76.95)
    assert parse_longitude("76:57W") == pytest.approx(-76.95)
    assert parse_longitude("82.5") == pytest.approx(82.5)
    assert parse_longitude("-10.25") == pytest.approx(-10.25)


def test_parse_latitude_north_south():
    assert parse_latitude("28:48N") == pytest.approx(28.8)
    assert parse_latitude("10:30S") == pytest.approx(-10.5)


def test_parse_utc_offset_formats():
    assert parse_utc_offset("+05:30") == pytest.approx(5.5)
    assert parse_utc_offset("-08:00") == pytest.approx(-8.0)
    assert parse_utc_offset("5:30") == pytest.approx(5.5)
    assert parse_utc_offset("0") == pytest.approx(0.0)


def test_engine_conversion_is_east_negative():
    m = ChartMoment(year=1987, month=8, day=28, hour=2, minute=55,
                    utc_offset_hours=5.5, longitude_east=76.95, latitude_north=28.8)
    assert m.engine_longitude == pytest.approx(-76.95)
    assert m.engine_gmt_hours == pytest.approx(-5.5)
    assert m.local_decimal_hours == pytest.approx(2 + 55 / 60)


def test_moment_validation_rejects_bad_values():
    base = dict(year=2000, month=1, day=1, hour=0, minute=0,
                utc_offset_hours=0.0, longitude_east=0.0, latitude_north=0.0)
    with pytest.raises(ValidationError):
        ChartMoment(**{**base, "minute": 60})
    with pytest.raises(ValidationError):
        ChartMoment(**{**base, "hour": 24})
    with pytest.raises(ValidationError):
        ChartMoment(**{**base, "latitude_north": 90.5})
    with pytest.raises(ValidationError):
        ChartMoment(**{**base, "month": 13})


def test_grid_spec_bounds():
    spec = GridSpec(unit=PeriodUnit.YEAR, step=800, count=60)
    assert spec.count == 60
    with pytest.raises(ValidationError):
        GridSpec(unit=PeriodUnit.DAY, step=0, count=10)
    with pytest.raises(ValidationError):
        GridSpec(unit=PeriodUnit.DAY, step=1, count=0)
