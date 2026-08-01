# ABOUTME: End-to-end CLI test: a real run over NU's 2000-2016 yearly example writing
# ABOUTME: every artifact (CSV, JSON, SVG sequence, aspects) with real computed data.

import csv
import json

import defusedxml.ElementTree as ET

from astgraf.cli import main


def test_full_run_writes_all_artifacts(tmp_path):
    rc = main([
        "--year", "2000", "--month", "1", "--day", "1", "--time", "12:00",
        "--unit", "year", "--step", "1", "--count", "17",
        "--utc-offset", "+05:30", "--lon", "76:57E", "--lat", "28:48N",
        "--out", str(tmp_path),
    ])
    assert rc == 0

    with open(tmp_path / "positions.csv", newline="") as fh:
        rows = list(csv.reader(fh))
    assert rows[0][:3] == ["index", "label", "jd"]
    assert rows[0][3] == "Ascendant"
    assert len(rows) == 18  # header + 17 periods
    for cell in rows[1][3:]:
        assert 0 <= float(cell) < 360

    payload = json.loads((tmp_path / "positions.json").read_text())
    assert payload["params"]["unit"] == "year"
    assert payload["params"]["zodiac"] == "sidereal"
    assert "accuracy_note" in payload["params"]
    assert len(payload["rows"]) == 17
    first = payload["rows"][0]
    assert len(first["positions"]) == 13
    assert isinstance(first["positions"][0]["retrograde"], bool)

    svg_dir = tmp_path / "svg"
    steps = sorted(svg_dir.glob("step_*.svg"))
    assert len(steps) == 13
    combined = svg_dir / "combined.svg"
    assert combined.exists()
    ET.fromstring(combined.read_text())  # must be well-formed XML

    aspects = (tmp_path / "aspects.csv").read_text().splitlines()
    assert aspects[0] == "body_a,body_b,kind,jd,label"


def test_aspect_bodies_filter_limits_events(tmp_path):
    rc = main([
        "--year", "2000", "--month", "1", "--day", "1", "--time", "12:00",
        "--unit", "year", "--step", "1", "--count", "17",
        "--utc-offset", "+05:30", "--lon", "76:57E", "--lat", "28:48N",
        "--aspect-bodies", "Uranus,Neptune,Ketu",
        "--out", str(tmp_path),
    ])
    assert rc == 0
    with open(tmp_path / "aspects.csv", newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert rows, "slow-body events must still be found"
    allowed = {"Uranus", "Neptune", "Ketu"}
    for row in rows:
        assert row["body_a"] in allowed and row["body_b"] in allowed


def test_aspect_bodies_rejects_unknown_name(tmp_path):
    import pytest
    with pytest.raises(SystemExit):
        main(["--year", "2000", "--aspect-bodies", "Vulcan", "--out", str(tmp_path)])


def test_precession_report_and_wheel(tmp_path, capsys):
    rc = main([
        "--year", "2026", "--count", "1", "--no-aspects",
        "--precession", "2026",
        "--out", str(tmp_path),
    ])
    assert rc == 0
    printed = capsys.readouterr().out
    assert "Precession clock" in printed
    assert "Punarvasu zero (two cycles back):" in printed
    wheel = tmp_path / "precession_wheel.svg"
    assert wheel.exists()
    ET.fromstring(wheel.read_text())


def test_scope_wheels_for_rows_and_events(tmp_path):
    rc = main([
        "--year", "2000", "--month", "1", "--day", "1", "--time", "12:00",
        "--unit", "year", "--step", "1", "--count", "17",
        "--utc-offset", "+05:30", "--lon", "76:57E", "--lat", "28:48N",
        "--aspect-bodies", "Uranus,Neptune,Ketu", "--scope",
        "--out", str(tmp_path),
    ])
    assert rc == 0
    scope = tmp_path / "scope"
    row_wheels = sorted(scope.glob("row_*.svg"))
    assert len(row_wheels) == 17
    event_wheels = sorted(scope.glob("event_*.svg"))
    with open(tmp_path / "aspects.csv", newline="") as fh:
        events = list(csv.DictReader(fh))
    assert len(event_wheels) == min(len(events), 100)
    assert events, "slow-body events expected in 2000-2016"
    root = ET.fromstring(event_wheels[0].read_text())
    assert root.tag.endswith("svg")
    assert any(el.get("data-body") == "Uranus" for el in root.iter())


def test_horary_grid_and_crossings(tmp_path):
    rc = main([
        "--year", "1987", "--month", "8", "--day", "28", "--time", "02:55",
        "--utc-offset", "+05:30", "--lon", "76:57E", "--lat", "28:48N",
        "--unit", "hour", "--step", "6", "--count", "3",
        "--horary", "--no-aspects",
        "--out", str(tmp_path),
    ])
    assert rc == 0
    with open(tmp_path / "horary.csv", newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 3 * 13
    asc = next(r for r in rows if r["index"] == "0" and r["body"] == "Ascendant")
    assert asc["nakshatra"] == "Punarvasu"
    assert asc["sub"] == "57"
    assert asc["division_lord"] == "Jupiter"

    with open(tmp_path / "horary_events.csv", newline="") as fh:
        events = list(csv.DictReader(fh))
    # The Moon moves ~6.6 deg in 12 hours: several 1/252 boundaries must be crossed.
    assert any(e["body"] == "Moon" for e in events)
    for e in events:
        assert abs(int(e["to_sub"]) - int(e["from_sub"])) in (1, 251)


def test_cosine_style_and_no_aspects(tmp_path):
    rc = main([
        "--year", "2010", "--month", "6", "--day", "15", "--time", "06:00",
        "--unit", "day", "--step", "10", "--count", "6",
        "--utc-offset", "+00:00", "--lon", "0", "--lat", "0",
        "--style", "cosine", "--no-aspects",
        "--out", str(tmp_path),
    ])
    assert rc == 0
    assert not (tmp_path / "aspects.csv").exists()
    assert (tmp_path / "svg" / "combined.svg").exists()
