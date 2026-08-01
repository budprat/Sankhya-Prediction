# ABOUTME: Tests the declarative trigger-rule system: primitives, escalation, TOML
# ABOUTME: loading, and the doctrine rules firing on NU's real ground-truth dates.

import pytest

from astgraf.ephemeris import compute_raw
from astgraf.models import BodyPosition, ChartResult
from astgraf.triggers import Condition, TriggerRule, evaluate_rule, load_rules

DOCTRINE = "doctrine-triggers.toml"


def make_result(lons: dict[str, float]) -> ChartResult:
    return ChartResult(positions={n: BodyPosition(name=n, longitude=v, retrograde=False)
                                  for n, v in lons.items()}, ayanamsa=0.0, jd=0.0)


def test_condition_primitives():
    r = make_result({"A": 10.0, "B": 190.5, "C": 100.2, "D": 11.0})
    assert evaluate_rule(r, TriggerRule(name="opp", conditions=[
        Condition(type="opposition", bodies=["A", "B"], orb=1.0)])).fired
    assert evaluate_rule(r, TriggerRule(name="sq", conditions=[
        Condition(type="square", bodies=["A", "C"], orb=1.0)])).fired
    assert evaluate_rule(r, TriggerRule(name="conj", conditions=[
        Condition(type="conjunction", bodies=["A", "D"], orb=1.5)])).fired
    assert not evaluate_rule(r, TriggerRule(name="tight", conditions=[
        Condition(type="conjunction", bodies=["A", "D"], orb=0.5)])).fired


def test_axis_cross_and_cluster_and_bands():
    r = make_result({"Sun": 73.0, "Saturn": 253.0, "Jupiter": 163.0, "Neptune": 343.0,
                     "Moon": 40.1, "Ketu": 40.6, "Mars": 41.0})
    assert evaluate_rule(r, TriggerRule(name="x", conditions=[
        Condition(type="axis_cross", axes=[["Sun", "Saturn"], ["Jupiter", "Neptune"]],
                  angle=90.0, orb=1.0)])).fired
    assert evaluate_rule(r, TriggerRule(name="cl", conditions=[
        Condition(type="cluster", bodies=["Moon", "Ketu", "Mars"],
                  max_spread=1.0)])).fired
    assert evaluate_rule(r, TriggerRule(name="band", conditions=[
        Condition(type="same_band", bodies=["Moon", "Ketu", "Mars"], level=0)])).fired
    assert evaluate_rule(r, TriggerRule(name="rohini", conditions=[
        Condition(type="in_band", bodies=["Moon"], band="Rohini")])).fired
    assert not evaluate_rule(r, TriggerRule(name="aswini", conditions=[
        Condition(type="in_band", bodies=["Moon"], band="Aswini")])).fired


def test_escalation_level():
    r = make_result({"Moon": 40.1, "Ketu": 40.6, "Mars": 41.0, "Uranus": 45.0})
    rule = TriggerRule(name="e", conditions=[
        Condition(type="cluster", bodies=["Moon", "Ketu", "Mars"], max_spread=2.0)],
        escalate=[Condition(type="cluster",
                            bodies=["Moon", "Ketu", "Mars", "Uranus"], max_spread=6.0)])
    assert evaluate_rule(r, rule).level == "catastrophic"


def test_doctrine_rules_load_and_fire_on_ground_truths():
    rules = {r.name: r for r in load_rules(DOCTRINE)}
    assert set(rules) == {"chatur-vyuham", "band-trigger", "neptune-on-ketu",
                          "nepal-double"}

    june2016 = compute_raw(2016, 6, 3, 12.0, 0.0, 0.0, 0.0, True, True)
    state = evaluate_rule(june2016, rules["chatur-vyuham"])
    assert state.fired and state.level == "catastrophic"

    hyderabad = compute_raw(2016, 9, 23, 14.0, -5.5, -78.483, 17.385, True, True)
    assert evaluate_rule(hyderabad, rules["neptune-on-ketu"]).fired

    nepal = compute_raw(2015, 4, 25, 11 + 40 / 60, -5.5, -86.0, 28.0, False, False)
    assert evaluate_rule(nepal, rules["nepal-double"]).fired

    quiet = compute_raw(2010, 2, 1, 12.0, 0.0, 0.0, 0.0, True, True)
    for rule in rules.values():
        assert not evaluate_rule(quiet, rule).fired, rule.name


def test_mined_rules_load_and_trine_works():
    rules = {r.name: r for r in load_rules("mined-triggers.toml")}
    assert set(rules) == {"mined-real-uranus-saturn-conj",
                          "mined-real-neptune-mercury-opp",
                          "mined-real-uranus-sun-trine"}
    r = make_result({"Uranus": 100.0, "Sun": 237.9})  # real:Uranus 117.86, sep 120.0
    assert evaluate_rule(r, rules["mined-real-uranus-sun-trine"]).fired


def test_real_prefix_resolves_offsets():
    r = make_result({"Neptune": 339.5, "Ketu": 8.6})
    rule = TriggerRule(name="rn", conditions=[
        Condition(type="conjunction", bodies=["real:Neptune", "Ketu"], orb=0.5)])
    assert evaluate_rule(r, rule).fired  # 339.5 + 29.09 = 8.59
