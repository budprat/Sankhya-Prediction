# ABOUTME: Tests the anchor library: schema-guarded loading, dossiers whose contacts
# ABOUTME: reproduce NU's taught numbers, and trigger instants refined to the minute.

import json

import pytest

from astgraf.anchors import (ANCHORS_PATH, asc_crossings, dossier, iso_jd,
                             load_anchors, main, refine_exactness)

IST = 5.5 / 24.0


def by_id(anchors, aid):
    return next(a for a in anchors if a.id == aid)


def contact(d, a, b, kind):
    for c in d["contacts"]:
        if c["a"] == a and c["b"] == b and c["kind"] == kind:
            return c
    raise AssertionError(f"contact {kind}:{a}-{b} missing: "
                         f"{[(c['kind'], c['a'], c['b']) for c in d['contacts']]}")


def test_load_anchors_ships_the_taught_and_m9_set():
    anchors = load_anchors(ANCHORS_PATH)
    ids = {a.id for a in anchors}
    for required in ("nepal-2015", "hyderabad-2016", "ulsoor-2016", "vyuham-2016",
                     "valdivia-1960", "alaska-1964", "kamchatka-1952",
                     "sumatra-2004", "tohoku-2011", "krakatoa-1883"):
        assert required in ids, f"{required} missing from the shipped library"
    nepal = by_id(anchors, "nepal-2015")
    assert nepal.taught and nepal.category == "earthquake"
    assert nepal.lat == pytest.approx(28.2305)
    vy = by_id(anchors, "vyuham-2016")
    assert vy.lat is None and vy.lon is None    # a configuration, not a place


def test_load_anchors_rejects_unknown_and_missing_keys(tmp_path):
    bad = tmp_path / "bad.toml"
    bad.write_text('[[anchor]]\nid = "x"\ncategory = "earthquake"\n'
                   'time = "2000-01-01T00:00:00Z"\nplace = "y"\nbogus = 1\n')
    with pytest.raises(ValueError, match="bogus"):
        load_anchors(str(bad))
    missing = tmp_path / "missing.toml"
    missing.write_text('[[anchor]]\nid = "x"\ncategory = "earthquake"\n')
    with pytest.raises(ValueError):
        load_anchors(str(missing))


def test_nepal_dossier_reproduces_the_taught_double_signature():
    nepal = by_id(load_anchors(ANCHORS_PATH), "nepal-2015")
    d = dossier(nepal, refine=False)
    ura_sun = contact(d, "Uranus", "Sun", "rsep")
    nep_ketu = contact(d, "Neptune", "Ketu", "rsep")
    assert ura_sun["aspect"] == "conj" and nep_ketu["aspect"] == "conj"
    assert ura_sun["sep"] == pytest.approx(0.69, abs=0.07)   # FRAMEWORK: 0.7
    assert nep_ketu["sep"] == pytest.approx(0.34, abs=0.07)  # FRAMEWORK: 0.34
    assert ura_sun["within_doctrine_orb"] and nep_ketu["within_doctrine_orb"]
    # Mean nodes are opposite BY CONSTRUCTION - the degenerate pair must not
    # be listed as a contact.
    assert not any(c["kind"] == "sep" and {c["a"], c["b"]} == {"Rahu", "Ketu"}
                   for c in d["contacts"])


def test_nepal_exactness_instants_resolve_to_the_minute():
    nepal = by_id(load_anchors(ANCHORS_PATH), "nepal-2015")
    jd0 = iso_jd(nepal.time)
    # The taught reading: real-Uranus reaches the Sun exactly ~18 h AFTER the
    # quake (the Sun closes the 0.69 gap at ~1 deg/day).
    ex = refine_exactness("Uranus", "Sun", "rsep", 0.0, jd0)
    assert not ex["edge"]
    assert 12.0 < (ex["jd"] - jd0) * 24.0 < 26.0
    assert ex["residual"] < 0.02
    # Minute resolution: one minute to either side must NOT beat the returned
    # instant.
    from astgraf.anchors import pair_separation
    here = pair_separation("Uranus", "Sun", "rsep", ex["jd"])
    for djd in (-1.5 / 1440.0, 1.5 / 1440.0):
        assert pair_separation("Uranus", "Sun", "rsep", ex["jd"] + djd) >= here - 1e-9


def test_hyderabad_asc_crossings_match_the_taught_minutes():
    # FRAMEWORK (NU 2026-08-02): the local Ascendant crossed the Mercury-held
    # Rahu end ~04:49 IST and the Neptune-held Ketu end ~17:04 IST each flood
    # day. Sep 23 2016, Hyderabad 17.385N 78.487E.
    day = iso_jd("2016-09-23T06:30:00Z")            # local noon IST
    crossings = asc_crossings(day, 17.385, 78.487)
    rahu = min((c for c in crossings if c["body"] == "Rahu"),
               key=lambda c: abs(c["jd"] - (iso_jd("2016-09-22T23:19:00Z"))))
    ketu = min((c for c in crossings if c["body"] == "Ketu"),
               key=lambda c: abs(c["jd"] - (iso_jd("2016-09-23T11:34:00Z"))))
    rahu_ist = ((rahu["jd"] + IST + 0.5) % 1.0) * 24.0
    ketu_ist = ((ketu["jd"] + IST + 0.5) % 1.0) * 24.0
    assert rahu_ist == pytest.approx(4 + 49 / 60, abs=5 / 60), f"Rahu at {rahu_ist:.3f}"
    assert ketu_ist == pytest.approx(17 + 4 / 60, abs=5 / 60), f"Ketu at {ketu_ist:.3f}"


def test_ulsoor_asc_sweep_matches_the_taught_window():
    # FRAMEWORK: at Bengaluru's dawn the Asc swept Neptune -> Sun -> Ketu ->
    # Uranus, exact crossings 06:12 and 08:20 IST (2016-03-07).
    day = iso_jd("2016-03-07T06:30:00Z")
    crossings = {c["body"]: c["jd"] for c in asc_crossings(day, 12.98, 77.62)
                 if c["body"] in ("Neptune", "Sun", "Ketu", "Uranus")
                 and 0.0 < ((c["jd"] + IST + 0.5) % 1.0) * 24.0 < 12.0}
    assert list(sorted(crossings, key=crossings.get)) == \
        ["Neptune", "Sun", "Ketu", "Uranus"]
    nep_ist = ((crossings["Neptune"] + IST + 0.5) % 1.0) * 24.0
    ura_ist = ((crossings["Uranus"] + IST + 0.5) % 1.0) * 24.0
    assert nep_ist == pytest.approx(6 + 12 / 60, abs=5 / 60), f"Neptune at {nep_ist:.3f}"
    assert ura_ist == pytest.approx(8 + 20 / 60, abs=5 / 60), f"Uranus at {ura_ist:.3f}"


def test_dossier_refines_every_fired_contact_to_the_minute():
    nepal = by_id(load_anchors(ANCHORS_PATH), "nepal-2015")
    d = dossier(nepal)
    fired = [c for c in d["contacts"] if c["within_doctrine_orb"]]
    assert fired, "Nepal must fire doctrine contacts"
    for c in fired:
        assert "exact_utc" in c and c["exact_utc"].endswith("Z")
        assert ":" in c["exact_utc"]                 # calendar minute, not a jd
        assert "exact_offset_hours" in c
        assert c["exact_residual"] < 3.0
    assert d["vyuha"]["fired"] is False
    assert d["asc_crossings"], "located anchor gets its site timetable"


def test_dossier_of_an_unlocated_anchor_skips_the_site_layer():
    vy = by_id(load_anchors(ANCHORS_PATH), "vyuham-2016")
    d = dossier(vy)
    assert d["asc_crossings"] is None
    assert d["vyuha"]["fired"] is True               # June 2016: the one firing


def test_cli_writes_dossiers(tmp_path):
    main(["--out", str(tmp_path), "--anchor", "nepal-2015"])
    payload = json.loads((tmp_path / "nepal-2015.json").read_text())
    assert payload["anchor"]["id"] == "nepal-2015"
    assert (tmp_path / "nepal-2015.txt").exists()


def test_flood_corpus_is_well_formed():
    # The flood catalogue (NU, 2026-08-05) unblocks the flood/site channel.
    # Guard the invariants any test built on it will assume.
    import csv as _csv
    from pathlib import Path
    path = Path(ANCHORS_PATH).parent / "data" / "floods-historical.csv"
    rows = list(_csv.DictReader(open(path)))
    assert len(rows) >= 80
    ids = [r["id"] for r in rows]
    assert len(ids) == len(set(ids)), "duplicate ids"
    for r in rows:
        assert r["date_precision"] in ("day", "month", "year", "century",
                                       "millennium"), r["id"]
        assert r["loc_precision"] in ("point", "city", "region"), r["id"]
        assert -90 <= float(r["latitude"]) <= 90, r["id"]
        assert -180 <= float(r["longitude"]) <= 180, r["id"]
    # the taught instance must be present and agree with anchors.toml
    hyd = next(r for r in rows if r["id"] == "hyderabad-2016")
    anchor = next(a for a in load_anchors(ANCHORS_PATH) if a.id == "hyderabad-2016")
    assert float(hyd["latitude"]) == pytest.approx(anchor.lat)
    assert float(hyd["longitude"]) == pytest.approx(anchor.lon)
    # the chart-usable subset must be non-trivial
    def year(r):
        return int(r["time"].split("-")[0]) if not r["time"].startswith("-") else -1
    usable = [r for r in rows
              if r["date_precision"] in ("day", "month") and year(r) >= 1700]
    assert len(usable) >= 30, f"only {len(usable)} chart-usable flood events"


def test_hanze_corpus_matches_the_shared_schema():
    # The imported European catalogue (Zenodo 20478847, CC-BY-4.0) must be
    # interoperable with the curated file and fully day-dated.
    import csv as _csv
    from pathlib import Path
    base = Path(ANCHORS_PATH).parent / "data"
    hanze = list(_csv.DictReader(open(base / "floods-hanze-europe.csv")))
    curated = list(_csv.DictReader(open(base / "floods-historical.csv")))
    assert len(hanze) > 2500
    assert list(hanze[0].keys()) == list(curated[0].keys()), "schema drift"
    assert len({r["id"] for r in hanze}) == len(hanze), "duplicate ids"
    assert all(r["date_precision"] == "day" for r in hanze)
    assert all(r["loc_precision"] == "country" for r in hanze)
    years = [int(r["time"][:4]) for r in hanze]
    assert min(years) >= 1870 and max(years) <= 2026


def test_historical_quake_corpus_is_well_formed():
    # The curated quake compilation (NU, 2026-08-05) adds a DEATHS-selected
    # tier the pinned magnitude-selected corpus cannot express.
    import csv as _csv
    from pathlib import Path
    base = Path(ANCHORS_PATH).parent / "data"
    rows = list(_csv.DictReader(open(base / "quakes-historical.csv")))
    floods = list(_csv.DictReader(open(base / "floods-historical.csv")))
    assert list(rows[0].keys()) == list(floods[0].keys()), "schema drift"
    assert len({r["id"] for r in rows}) == len(rows), "duplicate ids"
    assert {r["tier"] for r in rows} == {"pre-instrumental", "largest", "deadliest"}
    for r in rows:
        assert r["date_precision"] in ("minute", "day", "month"), r["id"]
        assert -90 <= float(r["latitude"]) <= 90, r["id"]
        assert -180 <= float(r["longitude"]) <= 180, r["id"]
    # the anchors that also live in anchors.toml must agree on coordinates
    anchors = {a.id: a for a in load_anchors(ANCHORS_PATH)}
    for r in rows:
        a = anchors.get(r["id"])
        if a and a.lat is not None:
            assert float(r["latitude"]) == pytest.approx(a.lat, abs=0.6), r["id"]
    deadliest = [r for r in rows if r["tier"] == "deadliest"]
    assert len(deadliest) >= 10
