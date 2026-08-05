# ABOUTME: Tests the Predict.pdf band-coincidence scanner: 28-band x 11-body table,
# ABOUTME: Moon+Ketu+Mars trigger with Uranus/Neptune escalation, episodes, catalog scoring.

import datetime as dt

import pytest

from astgraf.bands import (BAND_BODIES, band_of, band_table, find_episodes,
                           parse_event_window, score_events, trigger_state)
from astgraf.models import BodyPosition, ChartResult


def make_result(lons: dict[str, float]) -> ChartResult:
    positions = {name: BodyPosition(name=name, longitude=lon, retrograde=False)
                 for name, lon in lons.items()}
    return ChartResult(positions=positions, ayanamsa=0.0, jd=0.0)


def scatter(**overrides):
    """All 11 bodies in distinct bands unless overridden."""
    lons = {name: i * 25.0 + 1.0 for i, name in enumerate(BAND_BODIES)}
    lons.update(overrides)
    return lons


def test_band_bodies_are_the_pdf_columns():
    assert BAND_BODIES == ["Sun", "Moon", "Rahu", "Ketu", "Mercury", "Venus",
                          "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"]


def test_band_of_matches_28_division_grid():
    assert band_of(0.0) == 1
    assert band_of(12.856) == 1
    assert band_of(12.858) == 2
    assert band_of(80.1068) == 7
    assert band_of(359.9) == 28


def test_band_table_groups_bodies():
    table = band_table(make_result(scatter(Moon=5.0, Ketu=6.0)))
    assert set(table[1]) == {"Sun", "Moon", "Ketu"}  # Sun default lon 1.0 shares band 1


def test_trigger_fires_on_moon_ketu_mars_same_band():
    state = trigger_state(make_result(scatter(Moon=40.0, Ketu=41.0, Mars=42.0)))
    assert state.fired and state.level == "disruptive"
    assert state.band == 4
    assert state.giants == []


def test_trigger_escalates_with_uranus_or_neptune():
    state = trigger_state(make_result(scatter(
        Moon=40.0, Ketu=41.0, Mars=42.0, Neptune=43.0)))
    assert state.level == "catastrophic"
    assert state.giants == ["Neptune"]


def test_no_trigger_when_scattered():
    state = trigger_state(make_result(scatter()))
    assert not state.fired and state.level == "none"


def test_level1_divisions_match_the_horary_sub_grid():
    from astgraf.bands import division_of
    from astgraf.horary import horary_position
    for lon in (0.5, 80.1068, 200.3, 359.9):
        assert division_of(lon, level=1) == horary_position(lon).sub


def test_level2_is_the_pdf_one_sixty_third():
    from astgraf.bands import division_of, level_span
    assert level_span(2) == pytest.approx(360 / 1764)
    assert division_of(0.5, level=2) == 3


def test_real_longitude_applies_doctrine_offsets():
    from astgraf.bands import real_longitude
    from astgraf.ephemeris import compute_raw
    # The Nepal-quake chart (QUAKE.pdf, tropical): real-Neptune lands on Ketu,
    # real-Uranus on the Sun, per Mathcad-QUAKE.pdf.
    r = compute_raw(2015, 4, 25, 11 + 40 / 60, -5.5, -86.0, 28.0, False, False)
    ketu = r.positions["Ketu"].longitude
    sun = r.positions["Sun"].longitude
    assert abs(real_longitude(r, "Neptune") - ketu) < 0.5
    assert abs(real_longitude(r, "Uranus") - sun) < 0.8
    assert real_longitude(r, "Moon") == r.positions["Moon"].longitude
    from astgraf.bands import vyuha_state
    shape = make_result(scatter(Sun=73.0, Saturn=253.0, Jupiter=163.0,
                                Neptune=343.0, Rahu=166.0, Ketu=346.0))
    state = vyuha_state(shape)
    assert state.fired and state.level == "vyuha+nodes"
    assert state.partner == "Neptune"
    assert state.cross_deg == pytest.approx(90.0)
    assert state.node_align_deg == pytest.approx(3.0)


def test_vyuha_needs_both_axes_and_the_cross():
    from astgraf.bands import vyuha_state
    no_axis_b = make_result(scatter(Sun=73.0, Saturn=253.0, Jupiter=163.0,
                                    Neptune=320.0))
    assert not vyuha_state(no_axis_b).fired
    no_cross = make_result(scatter(Sun=93.0, Saturn=273.0, Jupiter=163.0,
                                   Neptune=343.0))
    assert not vyuha_state(no_cross).fired  # axes only 70 deg apart


def test_vyuha_without_nodes_is_base_level():
    from astgraf.bands import vyuha_state
    shape = make_result(scatter(Sun=73.0, Saturn=253.0, Jupiter=163.0,
                                Neptune=343.0, Rahu=120.0, Ketu=300.0))
    state = vyuha_state(shape)
    assert state.fired and state.level == "vyuha"


def test_vyuha_real_engine_finds_june_2016():
    # NU's ground truth: the Chatur Vyuham of end-May/June 2016.
    from astgraf.bands import vyuha_state
    from astgraf.ephemeris import compute_raw
    june3 = compute_raw(2016, 6, 3, 12.0, 0.0, 0.0, 0.0, True, True)
    state = vyuha_state(june3)
    assert state.fired and state.level == "vyuha+nodes"
    assert state.partner == "Neptune"
    assert abs(state.cross_deg - 90) < 2
    assert state.saturn_distance > 0
    march = compute_raw(2016, 3, 1, 12.0, 0.0, 0.0, 0.0, True, True)
    assert not vyuha_state(march).fired


def test_engine_exposes_geocentric_distances():
    from astgraf.ephemeris import compute_raw
    r = compute_raw(2016, 6, 3, 12.0, 0.0, 0.0, 0.0, True, True)
    jup = r.positions["Jupiter"].distance
    sat = r.positions["Saturn"].distance
    nep = r.positions["Neptune"].distance
    assert 0 < jup < sat < nep  # scaled units; ordering is what matters


def test_proximity_spread_math():
    from astgraf.bands import circular_spread
    assert circular_spread([10.0, 11.0, 12.0]) == pytest.approx(2.0)
    assert circular_spread([359.0, 0.5, 1.0]) == pytest.approx(2.0)  # wraps zero
    assert circular_spread([0.0, 120.0, 240.0]) == pytest.approx(240.0)


def test_proximity_fires_across_grid_boundary():
    # The 2018-09-20 shape: spread 0.76 deg but straddling the level-1 cell line.
    shape = make_result(scatter(Mars=278.54, Ketu=279.30, Moon=279.27))
    assert not trigger_state(shape, level=1).fired            # grid mode misses
    prox = trigger_state(shape, level=1, proximity=True)      # proximity fires
    assert prox.fired and prox.level == "disruptive"
    assert prox.spread_deg == pytest.approx(0.76, abs=0.01)
    assert prox.band == band_of(279.27)                       # named from the Moon


def test_proximity_escalates_when_giant_is_near_cluster():
    near = make_result(scatter(Mars=278.54, Ketu=279.30, Moon=279.27, Uranus=280.0))
    state = trigger_state(near, level=1, proximity=True)
    assert state.level == "catastrophic" and state.giants == ["Uranus"]
    far = make_result(scatter(Mars=278.54, Ketu=279.30, Moon=279.27, Uranus=300.0))
    assert trigger_state(far, level=1, proximity=True).giants == []


def test_proximity_respects_level_threshold():
    shape = make_result(scatter(Mars=10.0, Ketu=10.5, Moon=10.4))
    assert trigger_state(shape, level=2, proximity=True).fired is False  # 0.5 > 0.204
    assert trigger_state(shape, level=1, proximity=True).fired is True


def test_level1_trigger_requires_same_fine_division():
    # All three within one 1.43-deg sub-division: fires at level 1 and level 0.
    tight = make_result(scatter(Moon=40.1, Ketu=40.2, Mars=40.3))
    assert trigger_state(tight, level=1).fired
    assert trigger_state(tight, level=1).division == 29
    assert trigger_state(tight, level=1).band == 4
    # Same 28-band but different sub-divisions: level 0 fires, level 1 does not.
    loose = make_result(scatter(Moon=40.1, Ketu=41.9, Mars=40.3))
    assert trigger_state(loose, level=0).fired
    assert not trigger_state(loose, level=1).fired


def test_score_events_is_step_honest_and_range_aware():
    # Findings 21/38: the old baseline charged every episode a full day
    # regardless of sweep step (120x inflation at level 2) and scored catalog
    # events entirely OUTSIDE the sweep as chance-weighted misses.
    from astgraf.bands import Episode, score_events
    ep = Episode(start_jd=2457029.5, end_jd=2457029.5, start_label="s",
                 end_label="s", band=1, nakshatra="Aswini",
                 nakshatras=["Aswini"], level="disruptive", giants=[])
    in_range = {"place": "in", "window": (dt.date(2015, 1, 7),
                                          dt.date(2015, 1, 7), "day")}
    out_range = {"place": "out", "window": (dt.date(2020, 6, 1),
                                            dt.date(2020, 6, 1), "day")}
    rows, summary = score_events([ep], [in_range, out_range], 3.0,
                                 dt.date(2014, 12, 20), dt.date(2015, 1, 20),
                                 step_days=0.2 / 24)
    # A single 0.2h-step episode is ~0.0083 trigger days, not 1 full day.
    assert summary["trigger_day_fraction"] < 0.001
    assert summary["out_of_range"] == 1
    assert summary["events"] == 1              # only the in-range event scored
    by_place = {r["place"]: r for r in rows}
    assert by_place["out"]["p_chance"] == 0
    assert by_place["out"]["hit"] is False
    assert 0 < by_place["in"]["p_chance"] < 1


def test_episodes_merge_consecutive_firings():
    def s(fired, jd):
        state = trigger_state(make_result(
            scatter(Moon=40.0, Ketu=41.0, Mars=42.0) if fired else scatter()))
        return jd, f"L{jd}", state
    samples = [s(False, 0.0), s(True, 0.5), s(True, 1.0), s(False, 1.5),
               s(True, 3.0), s(False, 3.5)]
    episodes = find_episodes(samples, step_days=0.5)
    assert len(episodes) == 2
    assert episodes[0].start_jd == 0.5 and episodes[0].end_jd == 1.0
    assert episodes[1].start_jd == 3.0 and episodes[1].end_jd == 3.0


def test_episode_keeps_band_history_across_merge():
    # Audit finding 28: a merged episode froze the FIRST band/nakshatra even
    # when the trio moved into the next band mid-episode.
    def s(jd, moon):
        state = trigger_state(make_result(
            scatter(Moon=moon, Ketu=moon + 0.5, Mars=moon + 1.0)))
        return jd, f"L{jd}", state
    # Band 4 (Rohini) then band 5 (Mirgasirsa): 51.4286 is the 4/5 boundary.
    samples = [s(0.0, 40.0), s(0.5, 50.0), s(1.0, 52.0)]
    episodes = find_episodes(samples, step_days=0.5)
    assert len(episodes) == 1
    assert episodes[0].nakshatra == "Rohini"
    assert episodes[0].nakshatras == ["Rohini", "Mirgasirsa"]


@pytest.mark.parametrize("year,month,date,expected", [
    (2014, "APRIL", "April 18th, 2014", (dt.date(2014, 4, 18), dt.date(2014, 4, 18), "day")),
    (2013, "FEBRUARY", " 6th February 2013 ", (dt.date(2013, 2, 6), dt.date(2013, 2, 6), "day")),
    (2013, "OCTOBER", "Oct. 4,", (dt.date(2013, 10, 4), dt.date(2013, 10, 4), "day")),
    (2013, "SEPTEMBER", "September 12, 2013\nDissipated September 17, 2013",
     (dt.date(2013, 9, 12), dt.date(2013, 9, 17), "day")),
    (2014, "DEC 2013 TO APRIL 2014", "December 2013 to April 2014",
     (dt.date(2013, 12, 1), dt.date(2014, 4, 30), "month")),
    (2015, "November", "November Mid", (dt.date(2015, 11, 1), dt.date(2015, 11, 30), "month")),
    (2015, "Jan", "Early Jan 2015 ", (dt.date(2015, 1, 1), dt.date(2015, 1, 31), "month")),
    (2014, "", "September", (dt.date(2014, 9, 1), dt.date(2014, 9, 30), "month")),
    (2013, "July ", "July 8 and 9.", (dt.date(2013, 7, 8), dt.date(2013, 7, 9), "day")),
    # Audit findings 18/36/37/39: standalone month tokens only, no year/
    # magnitude digit tearing, range tails kept, cross-year ranges upright.
    (1999, "AUGUST", "Marmara region, Turkey",
     (dt.date(1999, 8, 1), dt.date(1999, 8, 31), "month")),
    (2011, "JUNE", "Junction city event",
     (dt.date(2011, 6, 1), dt.date(2011, 6, 30), "month")),
    (2015, "MAY", "M7.8 May 12", (dt.date(2015, 5, 12), dt.date(2015, 5, 12), "day")),
    (2015, "OCTOBER", "2015 October 26",
     (dt.date(2015, 10, 26), dt.date(2015, 10, 26), "day")),
    (2004, "DECEMBER", "December 28 - January 3",
     (dt.date(2004, 12, 28), dt.date(2005, 1, 3), "day")),
    (2015, "October", " 26 October 2015,", (dt.date(2015, 10, 26), dt.date(2015, 10, 26), "day")),
    (2014, "", "", (dt.date(2014, 1, 1), dt.date(2014, 12, 31), "year")),
])
def test_parse_event_window_handles_catalog_formats(year, month, date, expected):
    assert parse_event_window(year, month, date) == expected


def test_score_events_hits_and_chance_baseline():
    # One episode Jan 10-12 2014; event A overlaps, event B (March) does not.
    assert find_episodes([], step_days=0.5) == []   # no samples -> no episodes
    from astgraf.bands import Episode
    ep = Episode(start_jd=2456667.5, end_jd=2456669.5, start_label="", end_label="",
                 band=4, nakshatra="Rohini", level="disruptive", giants=[])
    events = [
        {"place": "A", "window": (dt.date(2014, 1, 11), dt.date(2014, 1, 11), "day")},
        {"place": "B", "window": (dt.date(2014, 3, 1), dt.date(2014, 3, 31), "month")},
    ]
    rows, summary = score_events([ep], events, margin_days=3,
                                 sweep_start=dt.date(2014, 1, 1),
                                 sweep_end=dt.date(2014, 12, 31))
    assert rows[0]["hit"] is True
    assert rows[1]["hit"] is False
    assert summary["events"] == 2 and summary["hits"] == 1
    assert 0 <= summary["trigger_day_fraction"] <= 1
    assert summary["expected_hits_by_chance"] >= 0


def test_real_offsets_extend_to_jupiter_saturn_provisionally():
    # NU ruling 2026-08-04: with (Rs/Ro) = 213.3266821 the Mathcad formula
    # decodes to offset = (a/2 - 1) * 500/240. Jupiter/Saturn adopt the
    # CANON's own semi-major axes as PROVISIONAL a-values (options weighed:
    # canon vs astronomical differ by <= 0.0025 deg; the Sankhya-vs-canon gap
    # is the real unknown, ~0.02 deg by the Ura/Nep deviation trend) until
    # NU's exact NR values arrive. Ura/Nep stay the Mathcad-given digits.
    import pytest as _pytest
    from astgraf.bands import REAL_POSITION_OFFSETS
    assert REAL_POSITION_OFFSETS["Uranus"] == 17.8562342478      # unchanged
    assert REAL_POSITION_OFFSETS["Neptune"] == 29.0917753653     # unchanged
    assert REAL_POSITION_OFFSETS["Jupiter"] == _pytest.approx(
        (5.20290493 / 2 - 1) * 500 / 240, abs=1e-9)
    assert REAL_POSITION_OFFSETS["Saturn"] == _pytest.approx(
        (9.55251745 / 2 - 1) * 500 / 240, abs=1e-9)


def test_real_prefix_rules_accept_jupiter_and_saturn(tmp_path):
    from astgraf.triggers import load_rules
    f = tmp_path / "r.toml"
    f.write_text('[[rule]]\nname = "rj"\nconditions = [\n'
                 '  { type = "conjunction", bodies = ["real:Jupiter", "Sun"], orb = 3.0 },\n'
                 '  { type = "conjunction", bodies = ["real:Saturn", "Sun"], orb = 3.0 },\n'
                 ']\n')
    rules = load_rules(str(f))
    assert rules[0].name == "rj"


def test_author_orbs_by_body_class():
    # THE AUTHOR, 2026-08-05: "Minor planet conjunctions lasts 2 degrees
    # whereas major one lasts for 18 degrees (fresnel angle of simultaneous
    # states)." Every pair in his Hiroshima reading that needs the wide orb
    # involves a GIANT, so the orb is set by body CLASS, not by aspect type.
    from astgraf.bands import MAJOR_BODIES, MAJOR_ORB, MINOR_ORB, doctrine_orb
    assert MINOR_ORB == 2.0 and MAJOR_ORB == 18.0
    assert {"Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"} == set(MAJOR_BODIES)
    assert doctrine_orb("Jupiter", "Neptune") == MAJOR_ORB      # both major
    assert doctrine_orb("Uranus", "Mars") == MAJOR_ORB          # one major
    assert doctrine_orb("Saturn", "Moon") == MAJOR_ORB
    assert doctrine_orb("Neptune", "Ascendant") == MAJOR_ORB
    assert doctrine_orb("Mercury", "Venus") == MINOR_ORB        # neither major
    assert doctrine_orb("Sun", "Moon") == MINOR_ORB
    assert doctrine_orb("real:Uranus", "Sun") == MAJOR_ORB      # prefix-tolerant


def test_hiroshima_reading_needs_the_authors_orbs():
    # His stated reading of 6 Aug 1945 08:16 JST: "Asc / Nep / Jup crosses,
    # Sat con moon and Uranus conjunct Mars." At the 3-deg orb this project
    # used for fifteen graded channels, FOUR of the five pairs are invisible.
    from astgraf.bands import doctrine_orb
    from astgraf.ephemeris import compute_raw

    def sep(a, b):
        d = abs(a - b) % 360
        return min(d, 360 - d)
    c = compute_raw(1945, 8, 6, 8 + 16 / 60, -9.0, -132.4553, 34.3853, False, False)
    p = {b: c.positions[b].longitude for b in
         ("Ascendant", "Moon", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune")}
    pairs = [("Jupiter", "Neptune"), ("Jupiter", "Ascendant"),
             ("Neptune", "Ascendant"), ("Saturn", "Moon"), ("Uranus", "Mars")]
    for a, b in pairs:
        s = sep(p[a], p[b])
        assert s <= doctrine_orb(a, b), f"{a}-{b} {s:.2f} outside the author's orb"
    # and the mis-scoping this exposes: only ONE survives a 3-degree orb
    assert sum(1 for a, b in pairs if sep(p[a], p[b]) <= 3.0) == 1
    assert sep(p["Saturn"], p["Moon"]) == pytest.approx(0.13, abs=0.05)
