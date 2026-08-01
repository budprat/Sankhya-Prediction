# ABOUTME: Tests Stage 2 of the inverse-learning system: geometric signature extraction
# ABOUTME: at event instants, matched controls, and the screening lift miner.

import csv

import pytest

from astgraf.ephemeris import compute_raw
from astgraf.signatures import (CONTROL_OFFSETS_DAYS, extract_signature,
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
    assert len(controls) == 2 * len(CONTROL_OFFSETS_DAYS)
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
    assert top["lift"] == pytest.approx(8.0)
