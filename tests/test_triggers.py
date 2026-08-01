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
                          "nepal-double", "uranus-neptune-conjunction",
                          "jupiter-saturn-conjunction", "nodes-doubly-occupied",
                          "uranus-neptune-combo-on-ascendant"}

    # The long-cycle families fire on their historical instances.
    conj_1993 = compute_raw(1993, 9, 1, 12.0, 0.0, 0.0, 0.0, True, True)
    assert evaluate_rule(conj_1993, rules["uranus-neptune-conjunction"]).fired
    great_2000 = compute_raw(2000, 5, 28, 12.0, 0.0, 0.0, 0.0, True, True)
    assert evaluate_rule(great_2000, rules["jupiter-saturn-conjunction"]).fired

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


def test_acting_body_and_aspect_target():
    from astgraf.triggers import acting_body, aspect_target, load_rules
    rules = {r.name: r for r in load_rules("mined-triggers.toml")}
    assert acting_body(rules["mined-real-uranus-sun-trine"]) == "Uranus"
    assert acting_body(rules["mined-real-neptune-mercury-opp"]) == "Neptune"
    a, b, target, orb = aspect_target(rules["mined-real-uranus-sun-trine"])
    assert (a, b, target) == ("real:Uranus", "Sun", 120.0)
    doctrine = {r.name: r for r in load_rules("doctrine-triggers.toml")}
    assert acting_body(doctrine["chatur-vyuham"]) == "Saturn"
    assert acting_body(doctrine["band-trigger"]) is None  # cluster: no light-time body


def test_rules_cli_emits_exact_instant_and_spot(tmp_path):
    from astgraf.bands_cli import main
    import csv as _csv
    rc = main([
        "--start", "2026-10-10", "--days", "12",
        "--rules", "mined-triggers.toml",
        "--out", str(tmp_path / "w"),
    ])
    assert rc == 0
    with open(tmp_path / "w" / "rules_episodes.csv", newline="") as fh:
        rows = list(_csv.DictReader(fh))
    trine = [r for r in rows if r["rule"] == "mined-real-uranus-sun-trine"]
    assert trine, "the Oct 2026 real-Uranus trine Sun window must fire"
    e = trine[0]
    assert e["exact_instant"].startswith("2026-10-16")
    assert e["acting"] == "Uranus"
    # Rule v2 (distance-true light-time): Uranus at ~156 light-minutes in
    # mid-October shifts the spot ~1.5 deg west of the fixed-150 value.
    assert float(e["spot_lon_east"]) == pytest.approx(-140.33, abs=0.5)
    assert float(e["spot_lat_north"]) == pytest.approx(21.0, abs=0.2)


def test_nodes_occupied_primitive():
    base = {"Rahu": 161.5, "Ketu": 341.5, "Mercury": 165.2, "Neptune": 340.3,
            "Sun": 181.6, "Mars": 268.0}
    both = make_result(base)
    rule = TriggerRule(name="n", conditions=[
        Condition(type="nodes_occupied",
                  bodies=["Sun", "Mercury", "Mars", "Neptune"], orb=4.0)])
    assert evaluate_rule(both, rule).fired
    # Only Ketu held -> no fire under require="both".
    one = make_result({**base, "Mercury": 100.0})
    assert not evaluate_rule(one, rule).fired
    either = TriggerRule(name="e", conditions=[
        Condition(type="nodes_occupied", bodies=["Neptune"], orb=4.0,
                  require="either")])
    assert evaluate_rule(one, either).fired  # Neptune still on Ketu


def test_nodes_doubly_occupied_rule_fires_on_hyderabad_not_nepal():
    rules = {r.name: r for r in load_rules(DOCTRINE)}
    rule = rules["nodes-doubly-occupied"]
    hyderabad = compute_raw(2016, 9, 24, 10.0, -5.5, -78.0, 16.0, False, False)
    state = evaluate_rule(hyderabad, rule)
    assert state.fired and state.level == "catastrophic"  # Neptune holds Ketu
    nepal = compute_raw(2015, 4, 25, 11 + 40 / 60, -5.5, -86.0, 28.0, False, False)
    assert not evaluate_rule(nepal, rule).fired  # Rahu was empty (observed)
    quiet = compute_raw(2010, 2, 1, 12.0, 0.0, 0.0, 0.0, True, True)
    assert not evaluate_rule(quiet, rule).fired


def test_giants_combo_on_ascendant_rule():
    rules = {r.name: r for r in load_rules(DOCTRINE)}
    rule = rules["uranus-neptune-combo-on-ascendant"]
    # Ulsoor Lake dawn, 2016-03-07 07:00 IST: Asc inside the Neptune-Uranus arc.
    dawn = compute_raw(2016, 3, 7, 7.0, -5.5, -77.617, 12.98, False, False)
    assert evaluate_rule(dawn, rule).fired
    # Midday: the Ascendant has left the arc.
    noon = compute_raw(2016, 3, 7, 12.0, -5.5, -77.617, 12.98, False, False)
    assert not evaluate_rule(noon, rule).fired
    # 1960: Uranus and Neptune ~84 deg apart - the combo does not exist as an arc.
    era = compute_raw(1960, 3, 7, 7.0, -5.5, -77.617, 12.98, False, False)
    assert not evaluate_rule(era, rule).fired


def test_rules_cli_site_awareness(tmp_path):
    from astgraf.bands_cli import main
    import csv as _csv
    rc = main([
        "--start", "2016-03-07", "--days", "1", "--step-hours", "0.5",
        "--rules", "doctrine-triggers.toml",
        "--site-lon", "77:37E", "--site-lat", "12:59N", "--utc-offset", "+05:30",
        "--out", str(tmp_path / "u"),
    ])
    assert rc == 0
    with open(tmp_path / "u" / "rules_episodes.csv", newline="") as fh:
        rows = [r for r in _csv.DictReader(fh)
                if r["rule"] == "uranus-neptune-combo-on-ascendant"]
    assert rows, "the dawn combo traversal must appear as an episode"
    assert any(r["start"] <= "2016-03-07 01:00" <= r["end"] or
               "2016-03-07 0" in r["start"] for r in rows)


def test_real_prefix_resolves_offsets():
    r = make_result({"Neptune": 339.5, "Ketu": 8.6})
    rule = TriggerRule(name="rn", conditions=[
        Condition(type="conjunction", bodies=["real:Neptune", "Ketu"], orb=0.5)])
    assert evaluate_rule(r, rule).fired  # 339.5 + 29.09 = 8.59
