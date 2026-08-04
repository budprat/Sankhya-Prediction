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


def test_axis_cross_uses_both_endpoints_order_independent():
    # Audit findings 19/29: anchoring on each axis's FIRST body made marginal
    # firings depend on the declared order. The midline of both endpoints is
    # order-independent: Sun 73/Saturn 251 -> axis 72; Jup 163/Nep 345 -> 164;
    # cross = 92 deg — same verdict both ways, at any orb.
    r = make_result({"Sun": 73.0, "Saturn": 251.0,
                     "Jupiter": 163.0, "Neptune": 345.0})

    def fired(axes, orb):
        rule = TriggerRule(name="x", conditions=[
            Condition(type="axis_cross", axes=axes, angle=90.0, orb=orb)])
        return evaluate_rule(r, rule).fired
    fwd = [["Sun", "Saturn"], ["Jupiter", "Neptune"]]
    swap = [["Saturn", "Sun"], ["Neptune", "Jupiter"]]
    for orb in (0.5, 2.5):
        assert fired(fwd, orb) == fired(swap, orb), orb
    assert not fired(fwd, 0.5)      # midline cross is 92, not 90
    assert fired(fwd, 2.5)


def test_in_band_accepts_a_band_list():
    # Sector membership (Java-family encoding): Aswini..Kritika = bands 1-3.
    r = make_result({"Jupiter": 30.0})          # 30 deg = band 3 (Kritika)
    rule = TriggerRule(name="b", conditions=[
        Condition(type="in_band", bodies=["Jupiter"],
                  band=["Aswini", "Bharani", "Kritika"])])
    assert evaluate_rule(r, rule).fired
    out = make_result({"Jupiter": 260.0})       # Abhijit — outside the family
    assert not evaluate_rule(out, rule).fired


def test_jupiter_saturn_rule_requires_the_java_family_sector():
    # Audit F-medium: the rule described the ~120-y same-position Java family
    # but fired on EVERY ~20-y conjunction. It must fire on 2000-05 (Kritika,
    # -> 2004 tsunami family) and NOT on 2020-12 (Uthrashada).
    rules = {r.name: r for r in load_rules(DOCTRINE)}
    rule = rules["jupiter-saturn-conjunction"]
    kritika = compute_raw(2000, 5, 28, 12.0, 0.0, 0.0, 0.0, True, False)
    assert evaluate_rule(kritika, rule).fired
    uthrashada = compute_raw(2020, 12, 21, 12.0, 0.0, 0.0, 0.0, True, False)
    assert not evaluate_rule(uthrashada, rule).fired


def test_chatur_vyuham_uranus_partner_rule_exists():
    # Audit F-medium: doctrine accepts Uranus as Jupiter's opposition partner
    # (bands.py vyuha_state does); the TOML now carries both variants.
    rules = {r.name: r for r in load_rules(DOCTRINE)}
    assert "chatur-vyuham-uranus" in rules
    axes = [ax for c in rules["chatur-vyuham-uranus"].conditions
            for ax in c.axes]
    assert ["Jupiter", "Uranus"] in axes or ["Uranus", "Jupiter"] in axes


def test_toml_schema_guards_reject_silent_traps(tmp_path):
    # Audit findings 12/23/30/48: typo keys, empty rulesets, unknown bodies,
    # and offset-less real: prefixes must FAIL the load, not no-op silently.
    def load(text):
        f = tmp_path / "r.toml"
        f.write_text(text)
        return load_rules(str(f))

    good = load('[[rule]]\nname="ok"\nconditions=[{type="conjunction",'
                'bodies=["real:Uranus","Saturn"], orb=3.0}]\n')
    assert len(good) == 1
    assert good[0].name == "ok"
    with pytest.raises(Exception, match="max_spred|[Ee]xtra"):
        load('[[rule]]\nname="t"\nconditions=[{type="cluster",'
             'bodies=["Moon","Mars"], max_spred=5.0}]\n')
    with pytest.raises(ValueError, match="no \\[\\[rule\\]\\]"):
        load('[[rules]]\nname="wrong-table"\n')
    with pytest.raises(ValueError, match="unknown body"):
        load('[[rule]]\nname="t"\nconditions=[{type="conjunction",'
             'bodies=["Moom","Mars"], orb=3.0}]\n')
    # real:Jupiter/Saturn became legal with the 2026-08-04 Rs/Ro decode;
    # the guard still fires for bodies with no doctrinal offset.
    with pytest.raises(ValueError, match="no doctrinal offset"):
        load('[[rule]]\nname="t"\nconditions=[{type="conjunction",'
             'bodies=["real:Mars","Saturn"], orb=3.0}]\n')
    with pytest.raises(Exception, match="needs at least"):
        load('[[rule]]\nname="t"\nconditions=[{type="in_band", band="Rohini"}]\n')
    assert load_rules(DOCTRINE), "the doctrine file must still load clean"


def test_refine_episode_instant_works_for_cluster_rules_and_clamps():
    # Audit batch 2: band/cluster rules got no exact instant (empty CSV fields).
    # Tightest instant = minimum circular spread; result must stay in-window.
    from astgraf.triggers import refine_episode_instant
    rule = TriggerRule(name="c", conditions=[
        Condition(type="cluster", bodies=["Moon", "Ketu", "Mars"],
                  max_spread=13.0)])

    def chart_at(jd):
        # Moon closes on the Ketu/Mars pair, tightest at jd = 2.0, then leaves
        # (kept outside the pair's own span so the spread minimum is strict).
        return make_result({"Moon": 45.0 + 5.0 * abs(jd - 2.0),
                            "Ketu": 40.0, "Mars": 41.0})
    jd = refine_episode_instant(chart_at, 0.0, 4.0, rule)
    assert jd == pytest.approx(2.0, abs=1e-3)
    # Minimum at the window edge must clamp, not escape (audit finding 49).
    jd_edge = refine_episode_instant(chart_at, 2.5, 4.0, rule)
    assert 2.5 <= jd_edge <= 4.0


def test_refine_prefers_the_earliest_exact_crossing_deterministically():
    # Finding 13: a retrograde episode can hold TWO equally-exact crossings;
    # the choice used to fall to 1e-5-degree ephemeris noise (61-deg spot
    # jitter). The earliest crossing now wins within a 1e-6 tolerance.
    from astgraf.triggers import refine_episode_instant
    rule = TriggerRule(name="p", conditions=[
        Condition(type="conjunction", bodies=["A", "B"], orb=3.0)])

    def chart_at(jd):
        gap = min(abs(jd - 1.0), abs(jd - 5.0))
        if abs(jd - 1.0) < abs(jd - 5.0):
            gap += 5e-7        # noise makes the EARLIER zero microscopically worse
        return make_result({"A": 0.0, "B": gap})
    jd = refine_episode_instant(chart_at, 0.0, 6.0, rule)
    assert jd == pytest.approx(1.0, abs=2e-3)


def test_acting_body_at_picks_the_near_giant():
    from astgraf.triggers import acting_body_at, load_rules
    rules = {r.name: r for r in load_rules(DOCTRINE)}
    rule = rules["band-trigger"]
    base = {"Moon": 40.1, "Ketu": 40.6, "Mars": 41.0}
    nep = make_result({**base, "Neptune": 50.0, "Uranus": 200.0})
    assert acting_body_at(rule, nep) == "Neptune"
    ura = make_result({**base, "Uranus": 45.0, "Neptune": 200.0})
    assert acting_body_at(rule, ura) == "Uranus"
    # A distant giant must NOT act: disruptive windows publish no spot.
    far = make_result({**base, "Uranus": 200.0, "Neptune": 120.0})
    assert acting_body_at(rule, far) is None


def test_acting_body_at_nodes_prefers_the_holder_on_the_node():
    # 2027 pattern: Jupiter exactly on Ketu; giants nowhere near a node — the
    # escalate block's distant giants must not shadow the true holder.
    from astgraf.triggers import acting_body_at, load_rules
    rules = {r.name: r for r in load_rules(DOCTRINE)}
    rule = rules["nodes-doubly-occupied"]
    r = make_result({"Rahu": 10.0, "Ketu": 190.0, "Jupiter": 190.04,
                     "Mercury": 11.3, "Sun": 32.6, "Venus": 27.5,
                     "Mars": 100.0, "Saturn": 63.8, "Uranus": 112.3,
                     "Neptune": 54.0})
    assert acting_body_at(rule, r) == "Jupiter"


def test_near_any_primitive_matches_scanner_escalation():
    # bands.py GIANTS semantics: escalation when a giant is within `orb` of ANY
    # of the target bodies (min arc-distance <= one 28-band span).
    span = 12.857142857142858
    cond = Condition(type="near_any", bodies=["Uranus", "Neptune"],
                     targets=["Moon", "Ketu", "Mars"], orb=span)
    near = make_result({"Moon": 40.1, "Ketu": 40.6, "Mars": 41.0,
                        "Uranus": 200.0, "Neptune": 50.0})
    assert evaluate_rule(near, TriggerRule(name="n", conditions=[cond])).fired
    far = make_result({"Moon": 40.1, "Ketu": 40.6, "Mars": 41.0,
                       "Uranus": 200.0, "Neptune": 120.0})
    assert not evaluate_rule(far, TriggerRule(name="n", conditions=[cond])).fired


def test_band_trigger_escalates_on_either_giant():
    # Predict.pdf p.1 names Uranus AND Neptune; the validated scanner escalates
    # on either giant. The TOML must not silently drop Neptune (audit F1).
    rules = {r.name: r for r in load_rules(DOCTRINE)}
    rule = rules["band-trigger"]
    base = {"Moon": 40.1, "Ketu": 40.6, "Mars": 41.0}
    neptune_only = make_result({**base, "Neptune": 50.0, "Uranus": 200.0})
    assert evaluate_rule(neptune_only, rule).level == "catastrophic"
    uranus_only = make_result({**base, "Uranus": 50.0, "Neptune": 200.0})
    assert evaluate_rule(uranus_only, rule).level == "catastrophic"
    neither = make_result({**base, "Uranus": 200.0, "Neptune": 120.0})
    assert evaluate_rule(neither, rule).level == "disruptive"


def test_escalation_level():
    r = make_result({"Moon": 40.1, "Ketu": 40.6, "Mars": 41.0, "Uranus": 45.0})
    rule = TriggerRule(name="e", conditions=[
        Condition(type="cluster", bodies=["Moon", "Ketu", "Mars"], max_spread=2.0)],
        escalate=[Condition(type="cluster",
                            bodies=["Moon", "Ketu", "Mars", "Uranus"], max_spread=6.0)])
    assert evaluate_rule(r, rule).level == "catastrophic"


def test_doctrine_rules_load_and_fire_on_ground_truths():
    rules = {r.name: r for r in load_rules(DOCTRINE)}
    assert set(rules) == {"chatur-vyuham", "chatur-vyuham-uranus", "band-trigger",
                          "neptune-on-ketu", "nepal-double",
                          "uranus-neptune-conjunction",
                          "jupiter-saturn-conjunction", "nodes-doubly-occupied",
                          "uranus-neptune-combo-on-ascendant",
                          "nodes-held-ascendant-cross"}

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
    # Rule v3 (NU ruling 2026-08-05, "Mathcad version is the one"): the
    # rotation is Uranus's fixed 17.856 deg, not the ~39 deg the distance-true
    # prose reading gave — so this registered spot moves 21.1 deg east.
    assert float(e["spot_lon_east"]) == pytest.approx(-119.24, abs=0.5)
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


def test_nodes_held_ascendant_cross_site_trigger():
    rules = {r.name: r for r in load_rules(DOCTRINE)}
    rule = rules["nodes-held-ascendant-cross"]
    # Hyderabad 2016-09-23 ~04:49 IST: Asc on the Mercury-held Rahu end.
    dawn = compute_raw(2016, 9, 23, 4.82, -5.5, -78.483, 17.385, False, False)
    state = evaluate_rule(dawn, rule)
    assert state.fired and state.level == "catastrophic"
    # Evening ~17:04 IST: Asc on the Neptune-held Ketu end.
    evening = compute_raw(2016, 9, 23, 17.07, -5.5, -78.483, 17.385, False, False)
    assert evaluate_rule(evening, rule).fired
    # Midday: constraint stands but the Asc is away from both ends.
    noon = compute_raw(2016, 9, 23, 12.0, -5.5, -78.483, 17.385, False, False)
    assert not evaluate_rule(noon, rule).fired
    # Nodes unheld (2010): Asc on a node alone must not fire.
    empty = compute_raw(2010, 2, 1, 12.0, 0.0, 0.0, 0.0, True, True)
    assert not evaluate_rule(empty, rule).fired


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


def test_observed_rule_asc_trine_real_neptune_fires_on_nepal_tropical_only():
    # NU ruling 2026-08-04: the Nepal observation (site Asc trine real-Neptune,
    # 0.26 deg at the catalog minute/epicenter) is a rule in TESTING status.
    # Frame guard: it holds on the TROPICAL site chart (physical rising frame);
    # the canon's sidereal mode shifts the angles by ayanamsa in RA space
    # (sidereal delta 3.2 deg), so the rule must not fire there at orb 1.
    from astgraf.ephemeris import compute_raw
    rules = load_rules("observed-triggers.toml")
    rule = next(r for r in rules if r.name == "asc-trine-real-neptune")
    args = (2015, 4, 25, 6 + 11 / 60 + 25.95 / 3600, 0.0, -84.7314, 28.2305)
    assert evaluate_rule(compute_raw(*args, False, False), rule).fired
    assert not evaluate_rule(compute_raw(*args, True, False), rule).fired


def test_observed_rules_from_the_hyderabad_reading_fire_on_their_ground_truth():
    # NU ruling 2026-08-05: real-Uranus-trine-node (Hyderabad 0.20 deg, Rahu
    # end) and Saturn-square-nodes (0.38 deg) join the TESTING channel. The
    # square rule is ONE rule (square to Rahu = square to Ketu by axis
    # symmetry); the trine is end-specific, so a variant pair like the two
    # chatur-vyuham rules. Negative control: the Nepal chart fires neither.
    from astgraf.ephemeris import compute_raw
    rules = {r.name: r for r in load_rules("observed-triggers.toml")}
    hyd = compute_raw(2016, 9, 24, 4.5, 0.0, 0.0, 0.0, False, False)
    nepal = compute_raw(2015, 4, 25, 6 + 11 / 60, 0.0, 0.0, 0.0, False, False)
    assert evaluate_rule(hyd, rules["real-uranus-trine-rahu"]).fired
    assert "real-uranus-trine-ketu" in rules          # the untested variant
    assert evaluate_rule(hyd, rules["saturn-square-nodes"]).fired
    assert not evaluate_rule(nepal, rules["real-uranus-trine-rahu"]).fired
    assert not evaluate_rule(nepal, rules["saturn-square-nodes"]).fired
