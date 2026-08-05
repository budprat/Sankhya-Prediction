# ABOUTME: Tests the configuration-similarity engine and recurrence calendar: an anchor's
# ABOUTME: slow pattern, its re-formation episodes, and fast-hand triggers to the minute.

import csv

from astgraf.anchors import ANCHORS_PATH, iso_jd, load_anchors
from astgraf.recurrence import (anchor_pattern, find_episodes, main, match_at,
                                moon_triggers)


def anchor(aid):
    return next(a for a in load_anchors(ANCHORS_PATH) if a.id == aid)


def keys(pattern):
    return {f"{c['kind']}:{c['a']}-{c['b']}@{c['aspect']}" for c in pattern}


def test_anchor_pattern_is_the_slow_layer_without_the_moon():
    pattern = anchor_pattern(anchor("nepal-2015"))
    got = keys(pattern)
    assert "rsep:Uranus-Sun@conj" in got
    assert "rsep:Neptune-Ketu@conj" in got
    assert not any("Moon" in k for k in got), "the fast hand is not the pattern"


def test_match_at_the_anchor_instant_is_full():
    a = anchor("nepal-2015")
    pattern = anchor_pattern(a)
    m = match_at(pattern, iso_jd(a.time))
    assert m["count"] == m["total"] == len(pattern) >= 3


def test_find_episodes_recovers_the_anchor_own_instant():
    a = anchor("nepal-2015")
    pattern = anchor_pattern(a)
    jd0 = iso_jd(a.time)
    episodes = find_episodes(pattern, iso_jd("2015-03-01T00:00:00Z"),
                             iso_jd("2015-07-01T00:00:00Z"))
    hit = [e for e in episodes if e["start_jd"] - 1.0 <= jd0 <= e["end_jd"] + 1.0]
    assert hit, f"anchor instant not inside any episode: {episodes}"
    e = hit[0]
    assert e["count"] == e["total"]
    assert e["best_utc"].endswith("Z") and ":" in e["best_utc"]   # a calendar minute
    # Bounds are day-resolution scan samples; the tightest instant may sit up
    # to one scan step outside the first/last in-orb sample.
    assert e["start_jd"] - 1.0 <= e["best_jd"] <= e["end_jd"] + 1.0


def test_vyuham_pattern_does_not_reform_in_2017():
    # Jupiter left the Neptune opposition after 2016 - a full re-formation in
    # 2017 is geometrically impossible.
    pattern = anchor_pattern(anchor("vyuham-2016"))
    episodes = find_episodes(pattern, iso_jd("2017-01-01T00:00:00Z"),
                             iso_jd("2018-01-01T00:00:00Z"))
    assert episodes == []


def test_vyuham_episode_carries_the_moon_trigger_to_the_minute():
    a = anchor("vyuham-2016")
    pattern = anchor_pattern(a)
    episodes = find_episodes(pattern, iso_jd("2016-05-20T00:00:00Z"),
                             iso_jd("2016-06-15T00:00:00Z"))
    assert episodes, "the June 2016 array must be found"
    e = episodes[0]
    trig = moon_triggers(a, e)
    mm = [t for t in trig if t["key"] == "sep:Moon-Mercury@conj"]
    assert mm, f"Moon-Mercury trigger missing: {trig}"
    assert mm[0]["utc"].endswith("Z") and ":" in mm[0]["utc"]
    assert e["start_jd"] - 0.5 <= mm[0]["jd"] <= e["end_jd"] + 0.5


def test_cli_writes_the_recurrence_calendar(tmp_path):
    main(["--anchor", "nepal-2015", "--start", "2015-03-01", "--end", "2015-07-01",
          "--out", str(tmp_path)])
    with open(tmp_path / "recurrence.csv", newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert rows and rows[0]["anchor"] == "nepal-2015"
    assert rows[0]["best_utc"].endswith("Z")
    assert (tmp_path / "recurrence.txt").exists()


def test_fine_step_catches_sub_day_full_windows():
    # valdivia-1960's FULL 5-contact window is shorter than one day - the
    # daily grid misses it entirely (found by the 130-year sweep, 2026-08-04:
    # the JOINT window of several contacts can be far narrower than any
    # single contact's). A 0.25 d step must recover the anchor's own instant.
    a = anchor("valdivia-1960")
    pattern = anchor_pattern(a)
    jd0 = iso_jd(a.time)
    fine = find_episodes(pattern, iso_jd("1960-04-01T00:00:00Z"),
                         iso_jd("1960-07-01T00:00:00Z"), step=0.25)
    hit = [e for e in fine if e["start_jd"] - 0.5 <= jd0 <= e["end_jd"] + 0.5]
    assert hit, f"valdivia self-recovery failed at 0.25 d: {fine}"
    assert hit[0]["count"] == hit[0]["total"] == len(pattern)


def test_composite_conditions_capture_the_other_layers():
    from astgraf.recurrence import composite_conditions
    nepal = composite_conditions(anchor("nepal-2015"))
    vy = composite_conditions(anchor("vyuham-2016"))
    assert nepal["vyuha_level"] == "none"          # Nepal: vyuha silent
    assert vy["vyuha_level"] == "vyuha+nodes"      # June 2016: the one firing
    assert nepal["mkm_spread"] > 100               # band trigger correctly wide
    assert nepal["stack_max"] >= 1


def test_composite_matching_requires_the_other_layers_too():
    from astgraf.recurrence import composite_match_at, composite_conditions
    a = anchor("vyuham-2016")
    cond = composite_conditions(a)
    # holds at its own instant, fails a year later (Jupiter left the opposition)
    assert composite_match_at(cond, iso_jd(a.time))
    assert not composite_match_at(cond, iso_jd("2017-06-03T12:00:00Z"))


def test_composite_episodes_are_a_subset_of_contact_episodes():
    a = anchor("nepal-2015")
    pattern = anchor_pattern(a)
    lo, hi = iso_jd("2015-03-01T00:00:00Z"), iso_jd("2015-07-01T00:00:00Z")
    plain = find_episodes(pattern, lo, hi)
    comp = find_episodes(pattern, lo, hi, anchor=a)
    assert plain, "the contact-only scan must find Nepal's window"
    assert len(comp) <= len(plain)
    for e in comp:
        # bounds are scan samples, so the tightest instant may sit one step
        # outside them (same tolerance as the sub-day-window test above)
        assert any(p["start_jd"] - 1.0 <= e["best_jd"] <= p["end_jd"] + 1.0
                   for p in plain)


def test_cli_filters_by_category_and_tags_output(tmp_path):
    main(["--category", "earthquake", "--start", "2015-03-01", "--end",
          "2015-07-01", "--out", str(tmp_path)])
    with open(tmp_path / "recurrence.csv", newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert rows, "the earthquake category must yield Nepal's episode"
    assert all(r["category"] == "earthquake" for r in rows)
    assert any(r["anchor"] == "nepal-2015" for r in rows)


def test_cli_rejects_an_unknown_category():
    import pytest as _p
    with _p.raises(SystemExit):
        main(["--category", "no-such-category", "--start", "2015-01-01",
              "--end", "2015-02-01"])


def test_composite_conditions_match_at_their_own_anchor_instant():
    # Regression: storing a ROUNDED mkm_spread made every anchor fail its own
    # composite test by ~0.00025 deg (the rounded threshold sits below the
    # live value). Self-match is the minimum an anchor's conditions must do.
    from astgraf.recurrence import composite_conditions, composite_match_at
    for aid in ("nepal-2015", "vyuham-2016", "hyderabad-2016", "tohoku-2011"):
        a = anchor(aid)
        assert composite_match_at(composite_conditions(a), iso_jd(a.time)), aid
