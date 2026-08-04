# ABOUTME: Tests the per-event galactic reference: Magha axis and Punarvasu crossover
# ABOUTME: as fixed sidereal directions, separations per body, frame handling.

import pytest

from astgraf.ephemeris import compute_raw
from astgraf.galactic import (MAGHA_AXIS_SIDEREAL, PUNARVASU_CROSSOVER_SIDEREAL,
                              galactic_separations, marker_longitudes)


def test_crossover_is_the_real_galactic_ecliptic_node():
    # NU ruling 2026-08-05: "crossover" means the galactic-ecliptic node — the
    # ASCENDING node of the galactic plane on the ecliptic, measured from the
    # IAU J2000 galactic pole (RA 192.85948, Dec +27.12825): tropical 90.0232
    # at J2000, which is suite-sidereal 66.1708.
    from astgraf.ephemeris import ayanamsa
    assert PUNARVASU_CROSSOVER_SIDEREAL == pytest.approx(66.1708, abs=0.001)
    assert (PUNARVASU_CROSSOVER_SIDEREAL + ayanamsa(2000)) % 360 == pytest.approx(
        90.0232, abs=0.002)
    # A fixed inertial direction keeps a near-constant sidereal longitude, so
    # its tropical longitude must track precession across epochs.
    for year, tropical in ((1900, 88.6263), (2026, 90.3864), (2100, 91.4201)):
        assert (PUNARVASU_CROSSOVER_SIDEREAL + ayanamsa(year)) % 360 == pytest.approx(
            tropical, abs=0.01)


def test_magha_axis_still_comes_from_the_28_sector_clock():
    # Unruled: the Magha axis remains the book's sector-10 center pending NU.
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


def test_equinox_offset_from_the_crossover_vanishes_at_the_crossing_epoch():
    # The oracle: the equinox last stood ON the galactic node in the mid-5th
    # millennium BC. The report's offset is a wheel-frame comparison, so the
    # sidereal marker must be converted with the anchor year's ayanamsa — get
    # that wrong and the offset is out by the ayanamsa (~23.8 deg).
    from astgraf.precession import equinox_offsets
    now_cross, _ = equinox_offsets(2026)
    then_cross, _ = equinox_offsets(-4440)
    assert then_cross < 0.6, f"equinox should sit on the node here, got {then_cross}"
    assert now_cross > 80, "and be most of a quadrant away today"
