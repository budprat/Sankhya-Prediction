# ABOUTME: Tests the ASTROC.GRF reader against the author's own program output in
# ABOUTME: canon/ — the end-to-end oracle for the port (header, stepping, positions).

import pytest

from astgraf.ephemeris import BODY_ORDER, compute_raw
from astgraf.grf import load_grf

CANON = "../../canon/ASTROC.GRF"


def _delta(a, b):
    return abs((a - b + 180) % 360 - 180)


def test_grf_header_and_shape():
    grf = load_grf(CANON)
    assert (grf.day, grf.month, grf.year) == (1, 1, 2015)
    assert grf.step == 1 and grf.unit == "D"
    assert grf.local_hours == pytest.approx(5.0)   # packed 5.00 -> 5h00m
    assert len(grf.rows) == 41
    assert list(grf.rows[0].keys()) == BODY_ORDER  # DR column order


def test_engine_reproduces_the_authors_own_run():
    # The author's file IS the oracle: tropical, blank site (0/0, GMT 0),
    # daily steps — and the BASIC pre-increment: row k = start + k steps
    # (the file's first row is 2015-01-02, not 01-01; audit Part III item on
    # grid semantics, now confirmed by the canon output itself).
    grf = load_grf(CANON)
    planets = [b for b in BODY_ORDER if b not in ("Ascendant", "Moon")]
    worst = 0.0
    for k, row in enumerate(grf.rows, start=1):
        chart = compute_raw(grf.year, grf.month, grf.day + k * grf.step,
                            grf.local_hours, 0.0, 0.0, 0.0, False, False)
        for body in planets:
            worst = max(worst, _delta(chart.positions[body].longitude, row[body]))
    # 11 bodies x 41 rows inside the GRF's own 0.1-deg print resolution
    # (plus compiled-single-precision noise).
    assert worst <= 0.12, worst


def test_moon_and_ascendant_residuals_are_the_recorded_open_question():
    # Moon sits ~0.6 deg and the Ascendant ~13 deg from the blank-site
    # reproduction — consistent with run inputs (site/GMT/exact time) the GRF
    # format does not store. Pinned loosely so a regression or a future
    # answer from the author is caught either way.
    grf = load_grf(CANON)
    row = grf.rows[0]
    chart = compute_raw(2015, 1, 2, 5.0, 0.0, 0.0, 0.0, False, False)
    assert _delta(chart.positions["Moon"].longitude, row["Moon"]) < 1.5
    assert _delta(chart.positions["Ascendant"].longitude, row["Ascendant"]) < 20.0
