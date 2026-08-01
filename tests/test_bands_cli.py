# ABOUTME: End-to-end test of astgraf-bands: real engine sweep, artifact files, and
# ABOUTME: catalog scoring against a small xlsx written in the catalog's own format.

import csv

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
