# ABOUTME: Tests automated outcome logging: USGS window checks around registered spots,
# ABOUTME: pending/hit/clear verdicts, and the outcomes CSV — network injected, offline.

import csv

from astgraf.outcomes import main


def make_episodes(path):
    with open(path, "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["rule", "start", "end", "level", "exact_instant",
                         "acting", "spot_lon_east", "spot_lat_north"])
        writer.writerow(["r-hit", "2026-01-10 00:00 UT", "2026-01-12 00:00 UT",
                         "disruptive", "2026-01-11 06:00 UT", "Uranus",
                         "80.50", "4.70"])
        writer.writerow(["r-clear", "2026-02-01 00:00 UT", "2026-02-02 00:00 UT",
                         "disruptive", "2026-02-01 12:00 UT", "Neptune",
                         "-140.00", "21.00"])
        writer.writerow(["r-pending", "2099-01-01 00:00 UT", "2099-01-02 00:00 UT",
                         "disruptive", "2099-01-01 12:00 UT", "Uranus",
                         "10.00", "10.00"])
        writer.writerow(["r-no-spot", "2026-03-01 00:00 UT", "2026-03-02 00:00 UT",
                         "disruptive", "", "", "", ""])


def fake_fetch(url):
    if "latitude=4.7" in url:
        return {"features": [{"properties": {"mag": 6.1, "place": "off Sri Lanka",
                                             "time": 1767072000000},
                              "geometry": {"coordinates": [80.2, 4.9, 30]}}]}
    return {"features": []}


def test_outcomes_verdicts_and_csv(tmp_path):
    episodes = tmp_path / "rules_episodes.csv"
    make_episodes(episodes)
    calls = []

    def counting_fetch(url):
        calls.append(url)
        return fake_fetch(url)

    corpus = tmp_path / "corpus.csv"
    with open(corpus, "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["time", "latitude", "longitude", "mag"])
        writer.writerow(["2011-03-11T05:46:24.000Z", "4.9", "80.3", "7.0"])
        writer.writerow(["2004-12-26T00:58:53.000Z", "-60.0", "-170.0", "7.1"])
    rc = main(["--episodes", str(episodes), "--today", "2026-08-02",
               "--corpus", str(corpus),
               "--out", str(tmp_path / "outcomes.csv")], fetch=counting_fetch)
    assert rc == 0
    with open(tmp_path / "outcomes.csv", newline="") as fh:
        rows = {r["rule"]: r for r in csv.DictReader(fh)}
    assert rows["r-hit"]["verdict"] == "hit"
    assert "6.1" in rows["r-hit"]["quakes"]
    # Spatial chance: 1 of 2 corpus events sits within 1000 km of the r-hit
    # spot — the base rate is written next to the verdict (audit 22/31).
    assert rows["r-hit"]["spatial_chance"] == "0.5000"
    assert rows["r-clear"]["verdict"] == "clear"
    assert rows["r-pending"]["verdict"] == "pending"
    # No-spot windows stay on the ledger as unassessed (audit finding 24).
    assert rows["r-no-spot"]["verdict"] == "unassessed (no spot)"
    # Pending windows must not hit the network.
    assert all("latitude=10.0" not in url for url in calls)
