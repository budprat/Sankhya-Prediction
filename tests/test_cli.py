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
