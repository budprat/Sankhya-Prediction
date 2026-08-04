# ABOUTME: Tests the per-event galactic reference: Magha axis and Punarvasu crossover
# ABOUTME: as fixed sidereal directions, separations per body, frame handling.

import pytest

from astgraf.ephemeris import compute_raw
from astgraf.galactic import (MAGHA_AXIS_SIDEREAL, PUNARVASU_CROSSOVER_SIDEREAL,
                              galactic_separations, marker_longitudes)


def test_frame_constants_come_from_the_28_sector_clock():
    # ASTGRAF.BAS carries no Abhijit and no 28-division data (verified): the
    # galactic markers belong to the book's 28-sector precession layer —
    # Punarvasu crossover = sector-7 start, Magha axis = sector-10 center.
    assert PUNARVASU_CROSSOVER_SIDEREAL == pytest.approx(6 * 360 / 28)
    assert MAGHA_AXIS_SIDEREAL == pytest.approx(9.5 * 360 / 28)


def test_sidereal_chart_uses_markers_directly():
    chart = compute_raw(2015, 1, 2, 5.0, 0.0, 0.0, 0.0, True, False)
    cross, magha = marker_longitudes(chart)
    assert cross == pytest.approx(PUNARVASU_CROSSOVER_SIDEREAL)
    assert magha == pytest.approx(MAGHA_AXIS_SIDEREAL)


def test_tropical_chart_shifts_markers_by_the_ayanamsa():
    from astgraf.ephemeris import ayanamsa
    chart = compute_raw(2015, 1, 2, 5.0, 0.0, 0.0, 0.0, False, False)
    cross, magha = marker_longitudes(chart)
    assert cross == pytest.approx(
        (PUNARVASU_CROSSOVER_SIDEREAL + ayanamsa(2015)) % 360, abs=1e-9)
    assert magha == pytest.approx(
        (MAGHA_AXIS_SIDEREAL + ayanamsa(2015)) % 360, abs=1e-9)


def test_separations_point_and_axis_semantics():
    chart = compute_raw(2015, 1, 2, 5.0, 0.0, 0.0, 0.0, True, False)
    seps = galactic_separations(chart)
    assert set(seps) == set(chart.positions)
    for body, s in seps.items():
        lon = chart.positions[body].longitude
        point = abs((lon - PUNARVASU_CROSSOVER_SIDEREAL + 180) % 360 - 180)
        assert s["crossover_sep"] == pytest.approx(point, abs=1e-5)
        # Magha is an AXIS: distance folds at 180, never exceeds 90.
        assert 0 <= s["magha_axis_sep"] <= 90
        d = abs((lon - MAGHA_AXIS_SIDEREAL) % 180)
        assert s["magha_axis_sep"] == pytest.approx(min(d, 180 - d), abs=1e-5)


def test_precession_report_prints_the_how_much_lines():
    from astgraf.precession import report_lines
    lines = "\n".join(report_lines(2016))
    assert "Punarvasu crossover" in lines
    assert "Magha axis" in lines
    assert "years of drift" in lines
