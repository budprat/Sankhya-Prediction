# ABOUTME: Tests the SVG renderer: well-formed output, wrap-aware segment breaking,
# ABOUTME: the heritage cosine fold geometry, and the one-by-one cumulative sequence.

import defusedxml.ElementTree as ET
import pytest

from astgraf.models import AspectEvent, BodyPosition, PeriodRow
from astgraf.svgplot import PALETTE, cosine_y, render, render_sequence, wrapped_y


def make_rows():
    sun = [10, 20, 30, 40, 50]
    moon = [350, 355, 2, 8, 15]  # crosses the 360/0 wrap between samples 2 and 3
    rows = []
    for i in range(5):
        rows.append(PeriodRow(
            index=i, label=f"2000-0{i + 1}-01 12:00", jd=2451545.0 + i * 30,
            positions=[
                BodyPosition(name="Sun", longitude=sun[i], retrograde=(i == 2)),
                BodyPosition(name="Moon", longitude=moon[i], retrograde=False),
            ]))
    return rows


def test_wrapped_axis_has_zero_at_bottom():
    assert wrapped_y(0) > wrapped_y(180)
    assert wrapped_y(0) == pytest.approx(wrapped_y(360))


def test_cosine_fold_matches_graphdo_geometry():
    assert cosine_y(0) > cosine_y(180)          # 0/360 at the bottom, 180 at the top
    assert cosine_y(90) == pytest.approx(cosine_y(270))  # the heritage ambiguity


def test_render_is_wellformed_and_breaks_at_wrap():
    svg = render(make_rows(), bodies=["Sun", "Moon"])
    root = ET.fromstring(svg)
    assert root.tag.endswith("svg")
    polys = [el for el in root.iter() if el.tag.endswith("polyline")
             and el.get("data-body")]
    sun_segments = [p for p in polys if p.get("data-body") == "Sun"]
    moon_segments = [p for p in polys if p.get("data-body") == "Moon"]
    assert len(sun_segments) == 1
    assert len(moon_segments) == 2  # broken at the 355 -> 2 wrap


def test_render_marks_retrograde_and_events():
    event = AspectEvent(body_a="Sun", body_b="Moon", kind="conjunction",
                        jd=2451545.0 + 60, label="2000-03-01")
    svg = render(make_rows(), bodies=["Sun", "Moon"], events=[event])
    root = ET.fromstring(svg)
    classes = [el.get("class") for el in root.iter()]
    assert "retro" in classes
    assert "aspect-marker" in classes


def test_sequence_is_cumulative():
    seq = render_sequence(make_rows(), bodies=["Sun", "Moon"])
    assert [name for name, _ in seq] == ["step_01_Sun", "step_02_Moon"]
    first_root = ET.fromstring(seq[0][1])
    second_root = ET.fromstring(seq[1][1])
    bodies_in = lambda root: {el.get("data-body") for el in root.iter()
                              if el.get("data-body")}
    assert bodies_in(first_root) == {"Sun"}
    assert bodies_in(second_root) == {"Sun", "Moon"}


def test_palette_covers_all_thirteen_bodies():
    for body in ("Ascendant", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus",
                 "Saturn", "Rahu", "Ketu", "Uranus", "Neptune", "Pluto"):
        assert body in PALETTE
        assert PALETTE[body].startswith("#")
