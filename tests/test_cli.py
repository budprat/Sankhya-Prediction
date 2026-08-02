# ABOUTME: End-to-end CLI test: a real run over NU's 2000-2016 yearly example writing
# ABOUTME: every artifact (CSV, JSON, SVG sequence, aspects) with real computed data.

import csv
import json

import defusedxml.ElementTree as ET
import pytest

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


def test_locate_writes_event_spots(tmp_path):
    rc = main([
        "--year", "2000", "--month", "1", "--day", "1", "--time", "12:00",
        "--unit", "year", "--step", "1", "--count", "17",
        "--utc-offset", "+05:30", "--lon", "76:57E", "--lat", "28:48N",
        "--aspect-bodies", "Uranus,Neptune,Ketu", "--locate",
        "--out", str(tmp_path),
    ])
    assert rc == 0
    with open(tmp_path / "locations.csv", newline="") as fh:
        spots = list(csv.DictReader(fh))
    assert spots, "Uranus/Neptune events must yield located spots"
    for s in spots:
        assert s["body"] in ("Uranus", "Neptune")   # Ketu has no light-time entry
        assert -180 < float(s["event_longitude_east"]) <= 180
        assert -90 <= float(s["event_latitude_north"]) <= 90
        # Distance-true light-times: rotation = actual light-minutes x 0.25 deg,
        # bounded by each planet's physical near/far range.
        lo, hi = {"Uranus": (35.9, 44.0), "Neptune": (59.5, 65.5)}[s["body"]]
        delta = (float(s["culmination_longitude_east"])
                 - float(s["event_longitude_east"])) % 360
        assert lo <= delta <= hi


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


def test_horary_default_is_classical_27(tmp_path):
    # NU ruling 2026-08-02: --horary follows ASTGRAF.BAS exactly — the classical
    # 27-star nakshatra/pada/navam labeling; the 28-ladder is opt-in.
    rc = main([
        "--year", "1987", "--month", "8", "--day", "28", "--time", "02:55",
        "--utc-offset", "+05:30", "--lon", "76:57E", "--lat", "28:48N",
        "--unit", "hour", "--step", "6", "--count", "3",
        "--horary", "--no-aspects", "--equal",
        "--out", str(tmp_path),
    ])
    assert rc == 0
    with open(tmp_path / "horary.csv", newline="") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
        fields = reader.fieldnames
    assert len(rows) == 3 * 13
    assert "nakshatra" in fields and "pada" in fields and "navam" in fields
    assert "sub" not in fields and "division" not in fields
    payload = json.loads((tmp_path / "positions.json").read_text())
    assert payload["params"]["houses"] == "equal"
    asc = next(r for r in rows if r["index"] == "0" and r["body"] == "Ascendant")
    # 80.1068 deg sidereal: 25th pada -> Punarvasu 1, navamsa cycle restarts at Ari.
    assert asc["nakshatra"] == "Punarvasu"
    assert asc["pada"] == "1"
    assert asc["navam"] == "Ari"
    # No 252-boundary event file in classical mode.
    assert not (tmp_path / "horary_events.csv").exists()


def test_ladder_without_horary_errors(tmp_path):
    with pytest.raises(SystemExit) as exc:
        main(["--year", "2000", "--ladder", "28", "--no-aspects",
              "--out", str(tmp_path)])
    assert exc.value.code == 2


def test_horary_ladder_28_flag_restores_252_grid(tmp_path):
    rc = main([
        "--year", "1987", "--month", "8", "--day", "28", "--time", "02:55",
        "--utc-offset", "+05:30", "--lon", "76:57E", "--lat", "28:48N",
        "--unit", "hour", "--step", "6", "--count", "3",
        "--horary", "--ladder", "28", "--no-aspects", "--equal",
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


def test_rasi_output_at_nepal_quake_moment(tmp_path):
    # End to end: the QUAKE.pdf chart moment (tropical) must yield the PDF's
    # own RASI/NAVAMSAM placements from live engine positions.
    # No house flag: Koch must be the DEFAULT (NU ruling 2026-08-02, matching
    # ASTGRAF.BAS line 45 EQL$ = "KOCH") — the PDF placements depend on it.
    rc = main([
        "--year", "2015", "--month", "4", "--day", "25", "--time", "11:40",
        "--utc-offset", "+05:30", "--lon", "86:00E", "--lat", "28:00N",
        "--tropical", "--unit", "hour", "--step", "6", "--count", "1",
        "--rasi", "--no-aspects",
        "--out", str(tmp_path),
    ])
    assert rc == 0
    payload = json.loads((tmp_path / "positions.json").read_text())
    assert payload["params"]["houses"] == "koch"
    lines = (tmp_path / "rasi_navamsam.txt").read_text().splitlines()
    # File layout: label, blank, 21-line RASI box, blank, 21-line NAVAMSAM box.
    rasi_box, nav_box = lines[2:23], lines[24:45]
    assert "  RASI   " in rasi_box[10] and "NAVAMSAM " in nav_box[10]
    # RASI: Sun/Mer/Mar share Tau's top slot line (fixed 4-char columns), and
    # the Koch-path Asc (129.0 in the PDF) sits in Leo (mid2-right) with Jupiter.
    assert rasi_box[1][35:51] == "Sun Mer     Mar "
    assert rasi_box[12][52:55] == "Jup"
    assert rasi_box[14][52:55] == "Asc"
    # NAVAMSAM: Asc lands in Gem (top band, 4th cell); the BAS blanks slots
    # 7-9 — no outer planets anywhere on page 2 of the printout.
    assert nav_box[4][52:55] == "Asc"
    nav_text = "\n".join(nav_box)
    assert "Ura" not in nav_text
    assert "Nep" not in nav_text
    assert "Plu" not in nav_text


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
