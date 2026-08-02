# ABOUTME: End-to-end test of astgraf-bands: real engine sweep, artifact files, and
# ABOUTME: catalog scoring against a small xlsx written in the catalog's own format.

import csv

import pytest

from astgraf.bands_cli import main


def make_catalog(path):
    import openpyxl
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["SNO", "YEAR OF EVENT", "MONTH", "DATE", "PLACE OF EVENT", "DESCRIPTION"])
    ws.append([1, 2014, "APRIL", "April 18th, 2014", "Mount Everest avalanche", "..."])
    ws.append([2, 2014, "MAY", "May 2nd, 2014", "Afghan mudslides", "..."])
    wb.save(path)


def test_sweep_and_catalog_scoring(tmp_path):
    catalog = tmp_path / "catalog.xlsx"
    make_catalog(catalog)
    rc = main([
        "--start", "2014-04-10", "--days", "30", "--step-hours", "12",
        "--catalog", str(catalog),
        "--out", str(tmp_path / "scan"),
    ])
    assert rc == 0

    with open(tmp_path / "scan" / "sweep.csv", newline="") as fh:
        sweep = list(csv.DictReader(fh))
    assert len(sweep) == 60  # 30 days x 2 samples
    assert all(row["level"] in ("none", "disruptive", "catastrophic") for row in sweep)

    with open(tmp_path / "scan" / "catalog_score.csv", newline="") as fh:
        score = list(csv.DictReader(fh))
    assert [r["place"] for r in score] == ["Mount Everest avalanche", "Afghan mudslides"]
    assert score[0]["window_start"] == "2014-04-18"
    assert all(r["hit"] in ("True", "False") for r in score)

    assert (tmp_path / "scan" / "episodes.csv").exists()


def test_rules_cli_sweeps_doctrine_file(tmp_path):
    rc = main([
        "--start", "2016-05-25", "--days", "15",
        "--rules", "doctrine-triggers.toml",
        "--out", str(tmp_path / "rules"),
    ])
    assert rc == 0
    with open(tmp_path / "rules" / "rules_episodes.csv", newline="") as fh:
        episodes = list(csv.DictReader(fh))
    vyuha = [e for e in episodes if e["rule"] == "chatur-vyuham"]
    assert vyuha, "the June 2016 array must fire from the rules file"
    assert vyuha[0]["level"] == "catastrophic"
    assert vyuha[0]["start"] <= "2016-06-03" <= vyuha[0]["end"]


def test_ascendant_rule_resolves_at_default_step(tmp_path):
    # Audit HIGH (design-gaps 1): at the default 12h step the Hyderabad
    # ground-truth window reported 0 nodes-held-ascendant-cross episodes.
    # Ascendant rules must now sweep on their own fine step automatically.
    rc = main([
        "--start", "2016-09-22", "--days", "2",
        "--rules", "doctrine-triggers.toml",
        "--site-lon", "78:29E", "--site-lat", "17:23N",
        "--utc-offset", "+05:30",
        "--out", str(tmp_path / "hyd"),
    ])
    assert rc == 0
    with open(tmp_path / "hyd" / "rules_episodes.csv", newline="") as fh:
        rows = [r for r in csv.DictReader(fh)
                if r["rule"] == "nodes-held-ascendant-cross"]
    assert rows, "Hyderabad dawn/evening windows must appear at the default step"
    assert any(r["exact_instant"] for r in rows)


def test_band_episode_spots_stable_across_steps(tmp_path):
    # Audit HIGH (locator 1 / design-gaps 2): episode giant spots were located
    # at the sweep-quantized first sample — 12h vs 3h steps published spots
    # ~135 deg apart for the same 2017-01 episode. Now both must refine to the
    # tightest instant and agree.
    spots = {}
    for step in ("12", "3"):
        rc = main([
            "--start", "2017-01-01", "--days", "4", "--step-hours", step,
            "--out", str(tmp_path / f"s{step}"),
        ])
        assert rc == 0
        with open(tmp_path / f"s{step}" / "episodes.csv", newline="") as fh:
            rows = [r for r in csv.DictReader(fh) if r["giant_spots"]]
        assert rows, f"step {step}: the 2017-01 Neptune episode must appear"
        assert rows[0]["tight_instant"]
        spots[step] = rows[0]["giant_spots"]

    def lon_of(spot_text):
        import re as _re
        m = _re.search(r"Neptune:(\d+\.\d+)([EW])", spot_text)
        assert m, spot_text
        return float(m.group(1)) * (1 if m.group(2) == "E" else -1)
    lon12, lon3 = lon_of(spots["12"]), lon_of(spots["3"])
    assert abs((lon12 - lon3 + 180) % 360 - 180) < 3.0, (lon12, lon3)


def test_vyuha_cli_finds_june_2016(tmp_path):
    rc = main([
        "--start", "2016-05-15", "--days", "31", "--vyuha",
        "--out", str(tmp_path / "vyuha"),
    ])
    assert rc == 0
    with open(tmp_path / "vyuha" / "vyuha_episodes.csv", newline="") as fh:
        episodes = list(csv.DictReader(fh))
    assert len(episodes) == 1
    e = episodes[0]
    assert e["level"] == "vyuha+nodes"
    assert e["partner"] == "Neptune"
    assert e["start"] <= "2016-06-03" <= e["end"]
    assert abs(float(e["best_cross_deg"]) - 90) < 1


def test_utc_offset_shifts_the_band_scan_clock(tmp_path):
    # Audit finding 51: --utc-offset was silently ignored outside --rules.
    jds = {}
    for tag, offset in (("z", "+00:00"), ("e", "+06:00")):
        rc = main(["--start", "2014-04-10", "--days", "1", "--step-hours", "24",
                   "--utc-offset", offset, "--out", str(tmp_path / tag)])
        assert rc == 0
        with open(tmp_path / tag / "sweep.csv", newline="") as fh:
            jds[tag] = float(next(csv.DictReader(fh))["jd"])
    assert jds["z"] - jds["e"] == pytest.approx(0.25, abs=1e-6)


def test_level1_defaults_to_hourly_steps(tmp_path):
    rc = main([
        "--start", "2014-04-10", "--days", "2", "--level", "1",
        "--out", str(tmp_path / "scan1"),
    ])
    assert rc == 0
    with open(tmp_path / "scan1" / "sweep.csv", newline="") as fh:
        sweep = list(csv.DictReader(fh))
    assert len(sweep) == 48  # 2 days at the level-1 default 1h step
    assert "division" in sweep[0]
