# ABOUTME: Tests Stage 2 of the inverse-learning system: geometric signature extraction
# ABOUTME: at event instants, matched controls, and the screening lift miner.

import csv

import pytest

from astgraf.ephemeris import compute_raw
from astgraf.signatures import (CONTROLS_PER_EVENT, extract_signature,
                                mine_lifts, run_corpus)


def chart_at(y, m, d, h):
    return compute_raw(y, m, d, h, 0.0, 0.0, 0.0, True, True)


def test_signature_contains_pair_and_context_features():
    sig = extract_signature(chart_at(2016, 6, 3, 12.0))
    assert sig["sep:Sun-Saturn"] == pytest.approx(179.75, abs=0.1)
    assert sig["sep:Jupiter-Neptune"] == pytest.approx(178.05, abs=0.1)
    assert sig["rsep:Neptune-Ketu"] != sig["sep:Ketu-Neptune"]  # real offset applied
    assert 1 <= sig["band:Moon"] <= 28
    assert sig["mkm_spread"] > 0
    assert sig["stack_max"] >= 1
    assert sig["dist:Saturn"] > 0


def test_signature_inverse_locator_features_need_location():
    hyderabad = compute_raw(2016, 9, 23, 8.5, 0.0, 0.0, 0.0, True, True)
    sig = extract_signature(hyderabad, event_lat=17.385, event_lon=78.487)
    for body in ("Jupiter", "Saturn", "Uranus", "Neptune"):
        assert 0 <= sig[f"loc_km:{body}"] <= 20016  # half circumference
    assert extract_signature(hyderabad).get("loc_km:Jupiter") is None


def test_run_corpus_writes_events_and_controls(tmp_path):
    catalog = tmp_path / "mini.csv"
    with open(catalog, "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["time", "latitude", "longitude", "depth", "mag", "magType",
                         "nst", "gap", "dmin", "rms", "net", "id", "updated", "place",
                         "type"])
        writer.writerow(["2011-03-11T05:46:24.000Z", "38.297", "142.373", "29", "9.1",
                         "mw", "", "", "", "", "us", "tohoku", "", "Tohoku", "earthquake"])
        writer.writerow(["2004-12-26T00:58:53.000Z", "3.295", "95.982", "30", "9.1",
                         "mw", "", "", "", "", "us", "sumatra", "", "Sumatra", "earthquake"])
    run_corpus(str(catalog), str(tmp_path / "out"))
    with open(tmp_path / "out" / "signatures.csv", newline="") as fh:
        events = list(csv.DictReader(fh))
    with open(tmp_path / "out" / "controls.csv", newline="") as fh:
        controls = list(csv.DictReader(fh))
    assert len(events) == 2
    assert len(controls) == 2 * CONTROLS_PER_EVENT
    assert float(events[0]["loc_km:Jupiter"]) > 0
    assert "sep:Sun-Saturn" in events[0]
    assert controls[0].get("loc_km:Jupiter") in ("", None)  # controls carry no epicenter


def test_mine_lifts_flags_planted_pattern():
    # Synthetic: a conjunction predicate present in most events, rare in controls.
    events = [{"sep:A-B": 1.0}] * 8 + [{"sep:A-B": 50.0}] * 2
    controls = [{"sep:A-B": 120.0}] * 27 + [{"sep:A-B": 2.0}] * 3
    lifts = mine_lifts(events, controls, pair_keys=["sep:A-B"])
    top = lifts[0]
    assert top["predicate"] == "sep:A-B@conj"
    assert top["event_rate"] == pytest.approx(0.8)
    assert top["control_rate"] == pytest.approx(0.1)
    # Add-one smoothed lift: (9/12)/(4/32) = 6.0 — and never infinite.
    assert top["lift"] == pytest.approx(6.0)
    zero_ctrl = mine_lifts([{"sep:A-B": 1.0}] * 10,
                           [{"sep:A-B": 120.0}] * 30, pair_keys=["sep:A-B"])
    assert zero_ctrl[0]["lift"] != float("inf")


def test_decluster_drops_near_repeats():
    from astgraf.signatures import decluster
    rows = [
        {"time": "2011-03-11T05:46:24.000Z", "latitude": "38.3", "longitude": "142.4"},
        {"time": "2011-03-11T06:15:00.000Z", "latitude": "36.2", "longitude": "141.1"},
        {"time": "2011-03-13T01:00:00.000Z", "latitude": "39.0", "longitude": "143.0"},
        {"time": "2011-03-12T00:00:00.000Z", "latitude": "-30.0", "longitude": "-70.0"},
        {"time": "2011-06-01T00:00:00.000Z", "latitude": "38.3", "longitude": "142.4"},
    ]
    kept = decluster(rows)
    # The two Tohoku aftershocks (within 7 d / 500 km) drop; the far-away
    # Chile event and the June repeat (outside 7 d) survive.
    assert len(kept) == 3
    assert kept[0]["time"].startswith("2011-03-11T05")


def test_controls_wrap_inside_the_corpus_span(tmp_path):
    import math
    from astgraf.signatures import _chart_for_time
    catalog = tmp_path / "mini.csv"
    with open(catalog, "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["time", "latitude", "longitude", "mag", "id", "place"])
        writer.writerow(["2011-03-11T05:46:24.000Z", "38.3", "142.4", "9.1",
                         "tohoku", "Tohoku"])
        writer.writerow(["2004-12-26T00:58:53.000Z", "3.3", "95.98", "9.1",
                         "sumatra", "Sumatra"])
    run_corpus(str(catalog), str(tmp_path / "out"))
    with open(tmp_path / "out" / "controls.csv", newline="") as fh:
        controls = list(csv.DictReader(fh))
    lo = _chart_for_time("2004-12-26T00:58:53.000Z").jd
    hi = _chart_for_time("2011-03-11T05:46:24.000Z").jd
    for c in controls:
        assert lo - 1e-6 <= float(c["jd"]) <= hi + 1e-6
    assert not math.isclose(float(controls[0]["jd"]),
                            float(controls[1]["jd"]))


def test_spot_features_match_the_forward_model():
    # Audit finding 11: the catalog instant is the ARRIVAL — the spot must come
    # from the trigger chart (light-time earlier), exactly as locate() is used
    # forward. Without chart_at the legacy (double-counted) value differs by
    # ~ light-minutes x 0.25 deg.
    from astgraf.locator import light_minutes_for, locate
    from astgraf.signatures import _chart_at_jd
    chart = chart_at(2016, 9, 23, 8.5)
    fixed = extract_signature(chart, chart_at=_chart_at_jd)
    minutes = light_minutes_for(chart, "Neptune")
    expected = locate(_chart_at_jd(chart.jd - minutes / 1440.0), "Neptune")
    assert fixed["spot_lon:Neptune"] == pytest.approx(
        expected.event_longitude_east, abs=1e-3)
    legacy = extract_signature(chart)
    delta = abs((fixed["spot_lon:Neptune"] - legacy["spot_lon:Neptune"] + 180)
                % 360 - 180)
    assert 50 <= delta <= 70      # ~60 deg for Neptune's ~4 h of rotation


def test_chart_for_time_accepts_timestamps_without_milliseconds():
    # Audit finding 52: "…:24Z" (no .000) is a legal USGS timestamp.
    from astgraf.signatures import _chart_for_time
    plain = _chart_for_time("2011-03-11T05:46:24Z")
    with_ms = _chart_for_time("2011-03-11T05:46:24.000Z")
    assert plain.jd == pytest.approx(with_ms.jd, abs=1e-9)


def test_permutation_null_flags_a_real_plant():
    from astgraf.signatures import permutation_max_lift
    events = [{"sep:A-B": 1.0} for _ in range(20)]
    controls = [{"sep:A-B": 120.0} for _ in range(60)]
    observed = mine_lifts(events, controls, pair_keys=["sep:A-B"])[0]["lift"]
    null = permutation_max_lift(events, controls, ["sep:A-B"], n_perm=99, seed=7)
    assert len(null) == 99
    p = sum(1 for v in null if v >= observed) / len(null)
    assert p < 0.05
    # Determinism: same seed, same null.
    again = permutation_max_lift(events, controls, ["sep:A-B"], n_perm=99, seed=7)
    assert null == again
