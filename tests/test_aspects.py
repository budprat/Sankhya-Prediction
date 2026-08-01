# ABOUTME: Tests aspect-event detection (conjunction/square/trine/opposition) including
# ABOUTME: zodiac wrap handling and bisection refinement of the crossing time.

import pytest

from astgraf.aspects import find_events, signed_separation
from astgraf.models import BodyPosition, PeriodRow


def make_rows(samples):
    """samples: list of (jd, {body: lon})."""
    rows = []
    for i, (jd, lons) in enumerate(samples):
        rows.append(PeriodRow(
            index=i, label=f"r{i}", jd=jd,
            positions=[BodyPosition(name=n, longitude=v, retrograde=False)
                       for n, v in lons.items()]))
    return rows


def test_signed_separation_wraps():
    assert signed_separation(10, 350) == pytest.approx(20)
    assert signed_separation(350, 10) == pytest.approx(-20)
    assert signed_separation(190, 10) == pytest.approx(180)


def test_trine_detected_and_refined():
    # A fixed at 10; B linear 100 -> 140 over jd 0..10, so B-A crosses 120 at jd 7.5.
    def pos(jd):
        return {"A": 10.0, "B": 100.0 + 4.0 * jd}
    rows = make_rows([(0.0, pos(0.0)), (10.0, pos(10.0))])
    events = [e for e in find_events(rows, pos_at_jd=pos) if e.kind == "trine"]
    assert len(events) == 1
    assert events[0].jd == pytest.approx(7.5, abs=1e-6)
    assert {events[0].body_a, events[0].body_b} == {"A", "B"}


def test_conjunction_across_zero_wrap():
    # A fixed at 350; B moves 340 -> 356, conjunction at B=350 (jd 5).
    def pos(jd):
        return {"A": 350.0, "B": 340.0 + 2.0 * jd}
    rows = make_rows([(0.0, pos(0.0)), (8.0, pos(8.0))])
    events = [e for e in find_events(rows, pos_at_jd=pos) if e.kind == "conjunction"]
    assert len(events) == 1
    assert events[0].jd == pytest.approx(5.0, abs=1e-6)


def test_opposition_through_wrap_of_separation():
    # A fixed at 0; B moves 175 -> 185: separation wraps +180/-180 at B=180 (jd 2.5).
    def pos(jd):
        return {"A": 0.0, "B": 175.0 + 2.0 * jd}
    rows = make_rows([(0.0, pos(0.0)), (5.0, pos(5.0))])
    events = [e for e in find_events(rows, pos_at_jd=pos) if e.kind == "opposition"]
    assert len(events) == 1
    assert events[0].jd == pytest.approx(2.5, abs=1e-6)


def test_no_event_when_nothing_crosses():
    def pos(jd):
        return {"A": 10.0, "B": 20.0 + 0.1 * jd}
    rows = make_rows([(0.0, pos(0.0)), (10.0, pos(10.0))])
    assert find_events(rows, pos_at_jd=pos) == []


def test_events_sorted_by_time():
    # B sweeps 100 -> 260 past A=10: trine at 130 (jd 1.875), opposition at 190 (jd 5.625),
    # then descending separation trine again? No: separation rises 90 -> 250 wrapping at 190.
    def pos(jd):
        return {"A": 10.0, "B": 100.0 + 16.0 * jd}
    rows = make_rows([(0.0, pos(0.0)), (10.0, pos(10.0))])
    events = find_events(rows, pos_at_jd=pos)
    jds = [e.jd for e in events]
    assert jds == sorted(jds)
    assert len(jds) >= 2
