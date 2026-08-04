# ABOUTME: The cos-fold mirror crossing — GRAPHDO/JS plot y=cos(lon), so traces also
# ABOUTME: cross when lon_a + lon_b = 360k. Tests the offset, the finder, and the rule.

import math

import pytest

from astgraf.anchors import chart_at, iso_jd
from astgraf.aspects import find_events, find_mirror_events, mirror_offset
from astgraf.grid import build_rows, make_pos_at_jd
from astgraf.models import ChartMoment, GridSpec, PeriodUnit

NEPAL_JD = iso_jd("2015-04-25T06:11:25.950Z")


def _window():
    """A 48 h tropical window around the Gorkha quake, 6-hourly."""
    start = ChartMoment(year=2015, month=4, day=24, hour=0, minute=0,
                        utc_offset_hours=0.0, longitude_east=0.0,
                        latitude_north=0.0, sidereal=False)
    return start, build_rows(start, GridSpec(unit=PeriodUnit.HOUR, step=6, count=9))


def test_mirror_offset_is_zero_on_the_equinox_axis_mirror():
    # cos(l) == cos(-l): the fold pairs a longitude with 360 - itself.
    assert mirror_offset(10.0, 350.0) == pytest.approx(0.0)
    assert mirror_offset(120.0, 240.0) == pytest.approx(0.0)
    assert mirror_offset(0.0, 0.0) == pytest.approx(0.0)
    assert mirror_offset(180.0, 180.0) == pytest.approx(0.0)
    # and the offset is the signed miss, wrapped to (-180, 180]
    assert mirror_offset(10.0, 20.0) == pytest.approx(30.0)
    assert mirror_offset(10.0, 330.0) == pytest.approx(-20.0)


def test_mirrored_pair_has_equal_graph_height():
    # The whole point: GRAPHDO plots y = cos(lon)*200 + 240, so a mirror pair
    # sits at the SAME height and its traces visibly cross.
    for a, b in ((10.0, 350.0), (75.0, 285.0), (200.0, 160.0)):
        assert mirror_offset(a, b) == pytest.approx(0.0, abs=1e-9)
        ya = math.cos(math.radians(a)) * 200 + 240
        yb = math.cos(math.radians(b)) * 200 + 240
        assert ya == pytest.approx(yb, abs=1e-9)


def test_nepal_moon_saturn_mirror_is_the_gap_the_aspect_engine_misses():
    # At the Gorkha quake the Moon and Saturn stood 0.067 deg from the mirror —
    # a crossing on the author's own graph. In the classical aspect frame the
    # pair is 127 deg apart: no conjunction, square, trine or opposition.
    c = chart_at(NEPAL_JD)
    moon = c.positions["Moon"].longitude
    saturn = c.positions["Saturn"].longitude
    # Signed: negative means the sum sits just SHORT of 360 (approaching).
    assert mirror_offset(moon, saturn) == pytest.approx(-0.0667, abs=0.005)
    assert abs(mirror_offset(moon, saturn)) < 0.1
    sep = abs((moon - saturn + 180) % 360 - 180)
    for target in (0.0, 90.0, 120.0, 180.0):
        assert abs(abs(sep) - target) > 3.0


def test_find_mirror_events_refines_a_real_crossing():
    start, rows = _window()
    events = find_mirror_events(rows, pos_at_jd=make_pos_at_jd(start),
                                bodies=["Moon", "Saturn"])
    assert events, "the Moon-Saturn mirror crossing falls inside this window"
    e = events[0]
    assert e.kind == "mirror"
    assert {e.body_a, e.body_b} == {"Moon", "Saturn"}
    # At the reported instant the pair must sit ON the mirror.
    pos = make_pos_at_jd(start)(e.jd)
    assert mirror_offset(pos["Moon"], pos["Saturn"]) == pytest.approx(0.0, abs=1e-4)
    # and it is genuinely near the quake day, not an artifact of the grid
    assert abs(e.jd - NEPAL_JD) < 1.5


def test_find_events_still_reports_only_classical_aspects():
    # The new finder must not perturb the audited aspect stream.
    start, rows = _window()
    events = find_events(rows, pos_at_jd=make_pos_at_jd(start),
                         bodies=["Moon", "Saturn"])
    assert all(e.kind in ("conjunction", "square", "trine", "opposition")
               for e in events)


def test_mirror_rule_primitive_fires_at_nepal(tmp_path):
    from astgraf.triggers import evaluate_rule, load_rules
    path = tmp_path / "mirror.toml"
    path.write_text(
        '[[rule]]\nname = "moon-saturn-mirror"\n'
        'description = "cos-fold crossing"\n'
        '[[rule.conditions]]\ntype = "mirror"\n'
        'bodies = ["Moon", "Saturn"]\norb = 1.0\n')
    rule = load_rules(str(path))[0]
    state = evaluate_rule(chart_at(NEPAL_JD), rule)
    assert state.fired is True
    assert state.level == "disruptive"
    # a day later the Moon has moved 13 deg: the mirror no longer holds
    assert evaluate_rule(chart_at(NEPAL_JD + 1.0), rule).fired is False


def test_mirror_rule_publishes_an_acting_body_like_every_other_pair_rule():
    # Self-audit gap: a mirror rule refined to its instant but named no
    # locatable body, so its episodes carried no spot — unlike every other
    # pair primitive. The pair's light-time body acts when it is within orb.
    from astgraf.triggers import Condition, TriggerRule, acting_body_at
    chart = chart_at(NEPAL_JD)
    # Uranus and Neptune genuinely stood on the mirror at Nepal (offset -2.971).
    rule = TriggerRule(name="ura-nep-mirror", conditions=[
        Condition(type="mirror", bodies=["Uranus", "Neptune"], orb=3.0)])
    assert acting_body_at(rule, chart) == "Uranus"
    # ...the tight Moon-Saturn mirror (0.067 deg) names Saturn, the only one
    # of that pair carrying a light-time
    tight = TriggerRule(name="moon-saturn-mirror", conditions=[
        Condition(type="mirror", bodies=["Moon", "Saturn"], orb=1.0)])
    assert acting_body_at(tight, chart) == "Saturn"
    # ...a pair with no light-time body at all names none
    plain = TriggerRule(name="moon-mars-mirror", conditions=[
        Condition(type="mirror", bodies=["Moon", "Mars"], orb=180.0)])
    assert acting_body_at(plain, chart) is None
    # ...and a giant outside the orb must not publish a spot for that window
    far = TriggerRule(name="far", conditions=[
        Condition(type="mirror", bodies=["Uranus", "Neptune"], orb=1.0)])
    assert acting_body_at(far, chart) is None


def test_scope_chart_draws_mirror_crossings():
    from astgraf.scope import render_scope
    svg = render_scope({"Moon": 116.374, "Saturn": 243.559}, mirrors=True, orb=1.0)
    assert 'data-mirror=' in svg
    assert "mirror" in svg
    plain = render_scope({"Moon": 116.374, "Saturn": 243.559}, orb=1.0)
    assert 'data-mirror=' not in plain


def test_cli_mirror_flag_writes_the_crossings(tmp_path):
    import csv

    from astgraf.cli import main
    rc = main([
        "--year", "2015", "--month", "4", "--day", "24", "--time", "00:00",
        "--utc-offset", "+00:00", "--lon", "0:00E", "--lat", "0:00N",
        "--unit", "hour", "--step", "6", "--count", "9",
        "--tropical", "--aspect-bodies", "Moon,Saturn",
        "--mirror", "--no-aspects", "--out", str(tmp_path),
    ])
    assert rc == 0
    with open(tmp_path / "mirror.csv", newline="") as fh:
        found = list(csv.DictReader(fh))
    assert found, "the Moon-Saturn mirror crossing is inside this window"
    row = found[0]
    assert {row["body_a"], row["body_b"]} == {"Moon", "Saturn"}
    assert abs(float(row["offset"])) < 1e-4
    assert abs(float(row["jd"]) - NEPAL_JD) < 1.5
