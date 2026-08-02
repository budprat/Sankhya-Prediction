# ABOUTME: Tests both nakshatra layers: the classical 27-star position (ASTGRAF.BAS
# ABOUTME: canon, default) and the parked 252/1764 ladder (28 x 9 x 7, --ladder 28).

import pytest

from astgraf.ephemeris import ayanamsa_value, compute_chart
from astgraf.horary import (HORARY_NAKSHATRAS_28, LORD_CYCLE, NAKSHATRAS_27,
                            SIGNS_12, find_sub_crossings, horary_position,
                            star_position)
from astgraf.models import BodyPosition, ChartMoment, PeriodRow


def test_twenty_seven_names_follow_astgraf_bas_order():
    # NU ruling 2026-08-02: "follow exactly whats in ASTGRAF.BAS" — DATA lines
    # 348-351, 27 names, no Abhijit (decision parked). One ruled exception:
    # "Magha" spelling kept where the BAS prints "Makha".
    assert len(NAKSHATRAS_27) == 27
    assert NAKSHATRAS_27[0] == "Aswini"
    assert NAKSHATRAS_27[9] == "Magha"
    assert NAKSHATRAS_27[19] == "Poorvashada"
    assert NAKSHATRAS_27[20] == "Uthrashada"
    assert "Abhijit" not in NAKSHATRAS_27
    assert NAKSHATRAS_27[26] == "Revathy"


def test_star_position_matches_quake_pdf_report():
    # Oracle: the QUAKE.pdf planet table (an ASTROLOG.BAS printout, ayanamsa
    # 0.000) — longitude -> Nakshatra / Pada / Navam columns, all 12 rows.
    cases = [
        (34.7, "Kritika", 3, "Aqu"),       # Sun
        (116.4, "Ashlesha", 3, "Aqu"),     # Moon
        (48.0, "Rohini", 3, "Gem"),        # Mars
        (50.6, "Rohini", 4, "Can"),        # Mercury
        (133.0, "Magha", 4, "Can"),        # Jupiter (PDF prints "Makha")
        (75.7, "Rudra", 3, "Aqu"),         # Venus
        (243.6, "Moola", 2, "Tau"),        # Saturn
        (188.9, "Swathy", 1, "Sag"),       # Rahu
        (8.9, "Aswini", 3, "Gem"),         # Ketu
        (17.6, "Bharani", 2, "Vir"),       # Uranus
        (339.5, "Uthra Badra", 2, "Vir"),  # Neptune
        (285.9, "Sravana", 2, "Tau"),      # Pluto
    ]
    for lon, star, pada, navam in cases:
        s = star_position(lon)
        assert (s.nakshatra, s.pada, s.navam) == (star, pada, navam), lon


def test_star_position_edges_and_wrap():
    s0 = star_position(0.0)
    assert (s0.nakshatra, s0.starcount, s0.pada, s0.navam) == ("Aswini", 1, 1, "Ari")
    # Failure/edge case: negative input normalizes; 359 deg is Revathy's last pada.
    s = star_position(-1.0)
    assert (s.nakshatra, s.pada, s.navam) == ("Revathy", 4, "Pis")
    assert star_position(360.0).nakshatra == "Aswini"
    assert len(SIGNS_12) == 12 and SIGNS_12[0] == "Ari" and SIGNS_12[11] == "Pis"


def test_twenty_eight_names_with_abhijit_twenty_first():
    # NU ruling 2026-08-02: Abhijit is the 21st division (257.14-270) — exactly
    # opposite Punarvasu (7th), per the book's opposition argument and the
    # Atharvaveda order. Predict.pdf's own table said 22nd; overridden.
    assert len(HORARY_NAKSHATRAS_28) == 28
    assert HORARY_NAKSHATRAS_28[0] == "Aswini"
    assert HORARY_NAKSHATRAS_28[19] == "Poorvashada"
    assert HORARY_NAKSHATRAS_28[20] == "Abhijit"
    assert HORARY_NAKSHATRAS_28[21] == "Uthrashada"
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


def test_sample_ascendant_falls_in_punarvasu_with_jupiter_lord():
    # 80.1068 deg: the 1987 reference Ascendant. Division 7 = Punarvasu, whose
    # cycle lord is Jupiter — matching the reference printout's C.Planet.
    p = horary_position(80.1068)
    assert p.division == 7
    assert p.nakshatra == "Punarvasu"
    assert p.division_lord == "Jupiter"
    assert p.sub == 57
    assert p.subsub == 393  # 1764-grid (28 x 9 x 7, the PDF's 1/63 ladder)


def test_top_of_circle_is_last_divisions():
    p = horary_position(359.999)
    assert (p.division, p.sub, p.subsub) == (28, 252, 1764)
    assert p.nakshatra == "Revathy"
    p0 = horary_position(360.0)
    assert p0.division == 1


def test_abhijit_division_is_opposite_punarvasu():
    assert horary_position(260.0).nakshatra == "Abhijit"     # 257.14-270
    assert horary_position(270.1).nakshatra == "Uthrashada"
    # Exact opposition: Abhijit's start = Punarvasu's start + 180.
    assert horary_position(77.15).nakshatra == "Punarvasu"
    assert horary_position(77.15 + 180).nakshatra == "Abhijit"


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
