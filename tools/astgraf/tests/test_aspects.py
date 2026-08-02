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


def test_antipode_never_reported_as_opposite_kind():
    # Audit finding 2/10: bisection used to converge onto the +-180 jump and
    # report a "conjunction" at the true opposition. B sweeps 30 -> 330 past
    # A=0: squares at jd 2/8, trine 3, opposition 5, trine 7 — NO conjunction.
    def pos(jd):
        return {"A": 0.0, "B": (30.0 + 30.0 * jd) % 360}
    rows = make_rows([(0.0, pos(0.0)), (10.0, pos(10.0))])
    events = find_events(rows, pos_at_jd=pos)
    from astgraf.aspects import ASPECT_ANGLES
    assert all(e.kind != "conjunction" for e in events)
    opp = [e for e in events if e.kind == "opposition"]
    assert len(opp) == 1 and opp[0].jd == pytest.approx(5.0, abs=1e-6)
    assert sum(1 for e in events if e.kind == "square") == 2
    assert sum(1 for e in events if e.kind == "trine") == 2
    # Every emitted event must be exact at its own refined instant.
    for e in events:
        sep = abs(signed_separation(pos(e.jd)["B"], pos(e.jd)["A"]))
        assert abs(sep - ASPECT_ANGLES[e.kind]) < 1e-6, e.kind


def test_multiple_crossings_in_one_interval_all_found():
    # Audit finding 1: even-count crossings inside one grid interval used to
    # cancel at the endpoints and fire nothing. B oscillates through A six
    # times inside a single 365-day interval.
    import math

    def pos(jd):
        return {"A": 0.0, "B": (15.0 * math.sin(2 * math.pi * jd / 120)) % 360}
    rows = make_rows([(0.0, pos(0.0)), (365.0, pos(365.0))])
    conj = [e for e in find_events(rows, pos_at_jd=pos)
            if e.kind == "conjunction"]
    assert len(conj) == 6            # zeros at jd 60, 120, ..., 360
    for e in conj:
        assert abs(signed_separation(pos(e.jd)["B"], pos(e.jd)["A"])) < 1e-6


def test_jupiter_saturn_yearly_grid_finds_the_triple_opposition():
    # Audit ground truth 2005-2015: 8 exact trines, 3 squares, 3 oppositions
    # (incl. the 2010-11 triple). The yearly grid used to report 1/1/1.
    from astgraf.aspects import ASPECT_ANGLES
    from astgraf.grid import build_rows, make_pos_at_jd
    from astgraf.models import ChartMoment, GridSpec, PeriodUnit
    start = ChartMoment(year=2005, month=1, day=1, hour=12, minute=0,
                        utc_offset_hours=0.0, longitude_east=0.0,
                        latitude_north=0.0)
    rows = build_rows(start, GridSpec(unit=PeriodUnit.YEAR, step=1, count=11))
    pos = make_pos_at_jd(start)
    events = find_events(rows, pos_at_jd=pos, bodies=["Jupiter", "Saturn"])
    kinds = {}
    for e in events:
        kinds[e.kind] = kinds.get(e.kind, 0) + 1
    assert kinds.get("opposition") == 3
    assert kinds.get("trine") == 8
    assert kinds.get("square") == 3
    for e in events:
        sep = abs(signed_separation(pos(e.jd)["Saturn"], pos(e.jd)["Jupiter"]))
        assert abs(sep - ASPECT_ANGLES[e.kind]) < 0.01


def test_ascendant_pairs_guarded_by_step_speed():
    # Audit finding 3: Ascendant (~361 deg/day) aliased into garbage at coarse
    # steps. Now: skipped (with a note) at yearly steps, valid at daily steps.
    from astgraf.aspects import ASPECT_ANGLES
    from astgraf.grid import build_rows, make_pos_at_jd
    from astgraf.models import ChartMoment, GridSpec, PeriodUnit
    start = ChartMoment(year=2015, month=4, day=1, hour=6, minute=0,
                        utc_offset_hours=0.0, longitude_east=77.0,
                        latitude_north=13.0)
    pos = make_pos_at_jd(start)

    yearly = build_rows(start, GridSpec(unit=PeriodUnit.YEAR, step=1, count=3))
    skipped: list[str] = []
    events = find_events(yearly, pos_at_jd=pos,
                         bodies=["Ascendant", "Sun"], skipped=skipped)
    assert events == []
    assert skipped and "Ascendant" in skipped[0]

    daily = build_rows(start, GridSpec(unit=PeriodUnit.DAY, step=1, count=3))
    skipped2: list[str] = []
    events2 = find_events(daily, pos_at_jd=pos,
                          bodies=["Ascendant", "Sun"], skipped=skipped2)
    assert skipped2 == []
    assert events2, "Asc-Sun aspects occur several times per day"
    for e in events2:
        lons = pos(e.jd)
        sep = abs(signed_separation(lons["Sun"], lons["Ascendant"]))
        assert abs(sep - ASPECT_ANGLES[e.kind]) < 0.05, e.kind


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
