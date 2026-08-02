# ABOUTME: Tests the 28x11 event-synchronisation matrix: per-cell rates and lifts
# ABOUTME: from signature CSVs, and the heatmap SVG rendering.

import defusedxml.ElementTree as ET
import pytest

from astgraf.matrix import build_matrix, render_matrix_svg


def make_sigs(band_by_body: dict[str, int], n: int) -> list[dict]:
    return [{f"band:{b}": str(v) for b, v in band_by_body.items()}] * n


def test_build_matrix_counts_and_lift():
    events = make_sigs({"Mars": 4, "Sun": 9}, 8) + make_sigs({"Mars": 7, "Sun": 9}, 2)
    controls = make_sigs({"Mars": 4, "Sun": 9}, 5) + make_sigs({"Mars": 20, "Sun": 2}, 15)
    rows = build_matrix(events, controls)
    cell = next(r for r in rows if r["body"] == "Mars" and r["band"] == 4)
    assert cell["event_count"] == 8
    assert cell["event_rate"] == pytest.approx(0.8)
    assert cell["control_rate"] == pytest.approx(0.25)
    assert cell["lift"] == pytest.approx(3.2)
    empty = next(r for r in rows if r["body"] == "Mars" and r["band"] == 1)
    assert empty["event_count"] == 0


def test_render_matrix_svg_structure():
    events = make_sigs({"Mars": 4, "Sun": 9, "Moon": 1}, 10)
    controls = make_sigs({"Mars": 5, "Sun": 9, "Moon": 2}, 30)
    svg = render_matrix_svg(build_matrix(events, controls))
    root = ET.fromstring(svg)
    assert root.tag.endswith("svg")
    cells = [el for el in root.iter() if (el.get("class") or "") == "cell"]
    assert len(cells) == 28 * 11
    for name in ("Aswini", "Magha", "Abhijit", "Revathy", "Mars", "Neptune"):
        assert name in svg
