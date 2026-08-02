# ABOUTME: Tests the 25,739-year precession clock against Secrets of Sankhya's own
# ABOUTME: arithmetic: 919.25 y/sector, Kritika 158 CE, Punarvasu 4438 BC, Magha flood epoch.

import defusedxml.ElementTree as ET
import pytest

from astgraf.precession import (CYCLE_YEARS, RATE_ARCSEC_PER_YEAR, SECTOR_YEARS,
                                equinox_longitude, render_precession_wheel,
                                sector_occupancy, sector_of)


def test_cycle_constants_match_the_book():
    assert CYCLE_YEARS == 25739
    assert RATE_ARCSEC_PER_YEAR == pytest.approx(50.35, abs=0.01)
    assert SECTOR_YEARS == pytest.approx(919.25, abs=0.01)


def test_equinox_at_wheel_zero_at_anchor_year():
    assert equinox_longitude(1996) == pytest.approx(0.0, abs=1e-9)
    # Precession is retrograde: earlier years sit at higher longitudes.
    assert equinox_longitude(1000) > equinox_longitude(1500) > 0


def test_kritika_exit_matches_the_books_1838_years():
    entry, exit_ = sector_occupancy("Kritika")
    assert exit_ == pytest.approx(1996 - 2 * SECTOR_YEARS, abs=1e-6)   # ~157.5 CE
    assert entry == pytest.approx(1996 - 3 * SECTOR_YEARS, abs=1e-6)   # ~762 BC


def test_punarvasu_entry_matches_the_books_6433_years():
    entry, exit_ = sector_occupancy("Punarvasu")
    assert entry == pytest.approx(1996 - 7 * SECTOR_YEARS, abs=1e-6)   # ~4438 BC
    assert exit_ == pytest.approx(1996 - 6 * SECTOR_YEARS, abs=1e-6)


def test_two_cycle_punarvasu_zero_is_about_30170_bc():
    entry, _ = sector_occupancy("Punarvasu", cycles_back=1)
    assert entry == pytest.approx(1996 - 7 * SECTOR_YEARS - CYCLE_YEARS, abs=1e-6)
    assert entry == pytest.approx(-30177.75, abs=1.0)  # the book's ~30,169/32,165 figures


def test_magha_occupancy_is_the_flood_epoch():
    entry, exit_ = sector_occupancy("Magha")  # NU ruling: Magha (BASIC's Makha is the variant)
    assert entry == pytest.approx(1996 - 10 * SECTOR_YEARS, abs=1e-6)  # ~7196 BC
    assert exit_ == pytest.approx(1996 - 9 * SECTOR_YEARS, abs=1e-6)   # ~6277 BC


def test_sector_of_reports_position_and_bounds():
    s = sector_of(1500)  # equinox ~ +6.94 deg, inside Aswini
    assert s.nakshatra == "Aswini"
    assert 0 < s.longitude < 12.857142857142858
    assert s.entered_year == pytest.approx(1996 - SECTOR_YEARS, abs=1e-6)
    assert s.exits_year == pytest.approx(1996, abs=1e-6)


def test_anchor_override_shifts_the_clock():
    assert equinox_longitude(2915, zero_year=2915) == pytest.approx(0.0, abs=1e-9)


def test_wheel_svg_marks_sectors_needle_and_markers():
    svg = render_precession_wheel(2026)
    root = ET.fromstring(svg)
    assert root.tag.endswith("svg")
    for name in ("Punarvasu", "Abhijit", "Magha", "Aswini", "Revathy"):
        assert name in svg
    assert any((el.get("class") or "") == "equinox-needle" for el in root.iter())
