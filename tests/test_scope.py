# ABOUTME: Tests the scope chart: the traditional wheel with conjunction/square/trine/
# ABOUTME: opposition lines drawn between bodies within orb — significance at a glance.

import defusedxml.ElementTree as ET
import pytest

from astgraf.scope import aspects_in_orb, render_scope, wheel_xy


def test_wheel_geometry_aries_zero_at_left_counterclockwise():
    cx = cy = 400.0
    x0, y0 = wheel_xy(0.0, 300.0, cx, cy)
    assert x0 < cx and abs(y0 - cy) < 1e-6          # 0 deg Aries at 9 o'clock
    x90, y90 = wheel_xy(90.0, 300.0, cx, cy)
    assert abs(x90 - cx) < 1e-6 and y90 > cy        # counterclockwise: 90 deg at bottom
    x180, y180 = wheel_xy(180.0, 300.0, cx, cy)
    assert x180 > cx and abs(y180 - cy) < 1e-6      # opposition point at 3 o'clock


def test_aspects_in_orb_detects_all_four_kinds():
    positions = {"A": 10.0, "B": 130.5, "C": 190.2, "D": 101.0, "E": 12.0}
    found = {(a, b, kind) for a, b, kind, _ in aspects_in_orb(positions, orb=3.0)}
    assert ("A", "B", "trine") in found          # sep 120.5
    assert ("A", "C", "opposition") in found     # sep 180.2
    assert ("A", "D", "square") in found         # sep 91.0
    assert ("A", "E", "conjunction") in found    # sep 2.0
    assert not any(k == "trine" and {a, b} == {"B", "C"} for a, b, k, _ in
                   aspects_in_orb(positions, orb=3.0))  # B-C sep 59.7: no aspect


def test_aspects_in_orb_respects_orb_and_wrap():
    tight = aspects_in_orb({"A": 10.0, "B": 134.0}, orb=3.0)
    assert tight == []
    loose = aspects_in_orb({"A": 10.0, "B": 134.0}, orb=5.0)
    assert [(a, b, k) for a, b, k, _ in loose] == [("A", "B", "trine")]
    wrapped = aspects_in_orb({"A": 359.0, "B": 2.0}, orb=3.0)
    assert [(a, b, k) for a, b, k, _ in wrapped] == [("A", "B", "conjunction")]


def test_render_scope_is_wellformed_with_bodies_and_aspect_lines():
    positions = {"Uranus": 290.0, "Neptune": 280.0, "Ketu": 281.0, "Sun": 110.5}
    svg = render_scope(positions, title="test wheel", orb=3.0)
    root = ET.fromstring(svg)
    assert root.tag.endswith("svg")
    bodies = {el.get("data-body") for el in root.iter() if el.get("data-body")}
    assert bodies == set(positions)
    classes = [el.get("class") or "" for el in root.iter()]
    # Neptune-Ketu sep 1.0 -> conjunction; Sun-Neptune sep 169.5: nothing; Sun at
    # 110.5 vs Uranus 290.0 sep 179.5 -> opposition line must be drawn.
    assert any("aspect-line conjunction" in c for c in classes)
    assert any("aspect-line opposition" in c for c in classes)
    # Sign ring labels present.
    text = svg
    for sign in ("Ari", "Can", "Lib", "Cap"):
        assert sign in text


def test_render_scope_lists_exact_aspects_in_legend():
    svg = render_scope({"A": 10.0, "B": 130.0}, title="t", orb=3.0)
    assert "A trine B" in svg
