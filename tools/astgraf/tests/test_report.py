# ABOUTME: Tests the full horoscope report page against the QUAKE.pdf printout: Koch
# ABOUTME: house cusps, MC, sidereal time, ruler/retro columns, Dasa/Bukti, boxes.

import pytest

from astgraf.ephemeris import compute_chart
from astgraf.models import ChartMoment
from astgraf.report import dasa_bukti, render_report, ruler_status, sidereal_hms

QUAKE = ChartMoment(year=2015, month=4, day=25, hour=11, minute=40,
                    utc_offset_hours=5.5, longitude_east=86.0, latitude_north=28.0,
                    sidereal=False, equal_houses=False)


def test_quake_cusps_mc_and_sidereal_time_match_pdf():
    chart = compute_chart(QUAKE)
    # QUAKE.pdf cusp table, all 12 (Tenth..Third, then opposites), degrees.
    expected = [33.7, 70.9, 101.2, 129.0, 156.8, 185.4,
                213.7, 250.9, 281.2, 309.0, 336.8, 5.4]
    for got, want in zip(chart.cusps, expected):
        assert got == pytest.approx(want, abs=0.06), want
    # First-house cusp IS the Ascendant on the Koch path.
    assert chart.cusps[3] == pytest.approx(
        chart.positions["Ascendant"].longitude, abs=1e-6)
    assert chart.mc == pytest.approx(33.7, abs=0.06)
    assert sidereal_hms(chart.sidereal_time_deg) == (2, 6, 47)


def test_dasa_bukti_arithmetic_from_pdf_moon():
    # ASTROLOG.BAS 5840-6030 on the PDF's Moon (116 deg 22 min): Dasa lord Mer,
    # 4y 7m; Bukti lord Jup, 1y 0m — matching the printout's lords/years/months.
    # Day fields move ~1 day per 0.005 deg of Moon, so they are pinned to this
    # exact input, not to the PDF's (whose Moon differs at sub-arcminute level).
    dasa, bukti = dasa_bukti(116 + 22 / 60)
    assert dasa == ("Mer", 4, 7, 17)
    assert bukti == ("Jup", 1, 0, 9)


def test_co920_deg_sign_min_split():
    from astgraf.report import co920
    # PDF pins: Asc 128.971 -> 8 deg Leo 58 min (ANW rescues 7.999.. -> 8);
    # Sun 34.74 -> 4 deg Tau 44 min; wrap edge 0.0 -> 0 deg Ari 0 min.
    assert co920(128.9713216854766) == (5, 8, 58)
    assert co920(34.74049) == (2, 4, 44)
    assert co920(0.0) == (1, 0, 0)


def test_ruler_status_table():
    # LUCK rows (ASTGRAF.BAS DATA 352-353): slots 1/2 RULER, 3 EXALTED, 4 WEAK.
    assert ruler_status(1, 5) == "RULER"      # Sun in Leo
    assert ruler_status(1, 1) == "EXALTED"    # Sun in Aries
    assert ruler_status(1, 7) == "WEAK"       # Sun in Libra
    assert ruler_status(1, 3) == ""           # Sun in Gemini
    assert ruler_status(10, 4) == "RULER"     # Moon in Cancer (PDF flags it)
    assert ruler_status(8, 12) == "RULER"     # Neptune in Pisces (PDF flags it)
    assert ruler_status(13, 5) == ""          # Ascendant: never flagged


def test_quake_report_page_text():
    chart = compute_chart(QUAKE)
    text = render_report(chart, QUAKE, name="QUAKE", place="NEPAL")
    assert " Horoscope " in text
    assert "Full name..: QUAKE" in text
    assert "Place of birth...: NEPAL" in text
    assert "Date of birth ...:  25-04-2015" in text
    assert "Time of birth ...: 11 H 40 M." in text and " AM" in text
    assert "Siderial time....:  2 H  6 M 47 S" in text
    assert "Ayanamsa.........:" in text and "0.000" in text
    assert "The house cusps  in degrees and minutes" in text
    for cusp_name in ("Tenth", "Elevent", "Twelth", "First",
                      "Fourth", "Ninth"):
        assert cusp_name in text
    # Planet table: Moon row carries RULER + Ashlesha 3 Aqu; Saturn is retro.
    moon_row = next(ln for ln in text.splitlines() if " Moo " in ln)
    assert "RULER" in moon_row and "Ashlesha" in moon_row
    assert "Aqu" in moon_row
    sat_row = next(ln for ln in text.splitlines() if " Sat " in ln)
    assert " R " in sat_row and "Moola" in sat_row
    assert "Dasa at birth Mer" in text
    assert "Bukti at birth Jup" in text
    assert "Nakshatra at birth :Ashlesha" in text
    # The report page ends with both box charts.
    assert "  RASI   " in text and "NAVAMSAM " in text


def test_report_edge_south_and_pm():
    # Failure/edge case: southern latitude flips the sidereal time by 180 and
    # the header prints South/PM/West without crashing.
    moment = ChartMoment(year=2015, month=4, day=25, hour=15, minute=5,
                         utc_offset_hours=-3.0, longitude_east=-46.6,
                         latitude_north=-23.5, sidereal=False,
                         equal_houses=False)
    chart = compute_chart(moment)
    text = render_report(chart, moment, name="X", place="Y")
    assert " PM" in text and "South" in text and "West" in text
    h, m, s = sidereal_hms(chart.sidereal_time_deg)
    # m can reach 60: the canon rounds the float minutes for display (USING ##).
    assert 0 <= h <= 24 and 0 <= m <= 60 and 0 <= s < 60


def test_explode_docx_oracle_2013():
    """EXPLODE.docx: the author's own cast of 07-07-2013 06:00, 76E 11N,
    GMT +5:30, tropical/Koch, place "WORLD" — the day of the Bodhgaya
    explosions, one day after Lac-Megantic and the Asiana SFO crash. A FIFTH
    oracle and the first covering a 2013 epoch; it sat unused in the repo,
    referenced by no document, until 2026-08-05."""
    from astgraf.ephemeris import compute_chart
    from astgraf.models import ChartMoment
    moment = ChartMoment(year=2013, month=7, day=7, hour=6, minute=0,
                         utc_offset_hours=5.5, longitude_east=76.0,
                         latitude_north=11.0, sidereal=False, equal_houses=False)
    chart = compute_chart(moment)
    expected = {
        "Ascendant": 102 + 16 / 60, "Sun": 105 + 5 / 60, "Moon": 91 + 7 / 60,
        "Mars": 85 + 34 / 60, "Mercury": 109 + 26 / 60, "Jupiter": 92 + 25 / 60,
        "Venus": 131 + 17 / 60, "Saturn": 214 + 47 / 60, "Rahu": 223 + 41 / 60,
        "Ketu": 43 + 41 / 60, "Uranus": 12 + 31 / 60, "Neptune": 335 + 22 / 60,
        "Pluto": 280 + 33 / 60,
    }
    for body, value in expected.items():
        # 0.03 deg covers the canon's single-precision Moon (his 91d07 vs 91d06)
        assert chart.positions[body].longitude == pytest.approx(value, abs=0.03), body
    for body in ("Mercury", "Saturn", "Neptune", "Pluto"):
        assert chart.positions[body].retrograde, body
    assert chart.mc == pytest.approx(9.4, abs=0.05)
    assert chart.cusps[3] == pytest.approx(102.3, abs=0.05)   # First cusp
