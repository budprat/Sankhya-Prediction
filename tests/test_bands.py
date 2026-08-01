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
    (2013, "July ", "July 8 and 9.", (dt.date(2013, 7, 8), dt.date(2013, 7, 8), "day")),
    (2015, "October", " 26 October 2015,", (dt.date(2015, 10, 26), dt.date(2015, 10, 26), "day")),
    (2014, "", "", (dt.date(2014, 1, 1), dt.date(2014, 12, 31), "year")),
])
def test_parse_event_window_handles_catalog_formats(year, month, date, expected):
    assert parse_event_window(year, month, date) == expected


def test_score_events_hits_and_chance_baseline():
    # One episode Jan 10-12 2014; event A overlaps, event B (March) does not.
    episodes = find_episodes([], step_days=0.5)  # empty ok
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
