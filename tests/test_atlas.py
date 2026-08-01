# ABOUTME: Tests the deep-time atlas SVG: precession-sector stripes over 48,000 years,
# ABOUTME: doctrine epochs, and the modern conjunction-cycle panel.

import defusedxml.ElementTree as ET

from astgraf.atlas import render_atlas


def test_atlas_is_wellformed_with_both_panels():
    svg = render_atlas()
    root = ET.fromstring(svg)
    assert root.tag.endswith("svg")
    for label in ("Punarvasu zero", "Magha flood epoch", "Kritika",
                  "Krakatoa 1883", "2004 tsunami", "Chatur Vyuham 2016",
                  "Ura-Nep 1991-94", "next ~2159"):
        assert label in svg, label


def test_atlas_sector_stripes_span_deep_time():
    svg = render_atlas()
    root = ET.fromstring(svg)
    stripes = [el for el in root.iter() if (el.get("class") or "") == "sector"]
    # ~48,000 years / 919.25 y per sector spans ~52 sectors.
    assert 45 <= len(stripes) <= 60
