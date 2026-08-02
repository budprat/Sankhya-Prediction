# ABOUTME: Tests the deep-time atlas SVG: precession-sector stripes over 48,000 years,
# ABOUTME: doctrine epochs, and the modern conjunction-cycle panel.

import defusedxml.ElementTree as ET

from astgraf.atlas import render_atlas, sector_for_interval_end


def test_deep_stripe_walk_is_retrograde():
    # Precession walks BACKWARD through the nakshatras: k sectors back from the
    # 1996 Aswini-exit anchor (audit Part II F2 — the shipped walk was inverted).
    assert sector_for_interval_end(1996.0) == "Aswini"
    assert sector_for_interval_end(1076.75) == "Bharani"
    assert sector_for_interval_end(157.5) == "Kritika"
    assert sector_for_interval_end(-3519.5) == "Punarvasu"   # 7th, ~4438 BC exit
    assert sector_for_interval_end(-6277.25) == "Magha"      # matches precession.py


def test_atlas_is_wellformed_with_both_panels():
    svg = render_atlas()
    root = ET.fromstring(svg)
    assert root.tag.endswith("svg")
    for label in ("Punarvasu zero", "Magha flood epoch", "Kritika",
                  "Krakatoa 1883", "2004 tsunami", "Chatur Vyuham 2016",
                  "Ura-Nep 1991-94", "next ~2165"):
        assert label in svg, label
    assert "171" in svg and "167.6" not in svg


def test_atlas_sector_stripes_span_deep_time():
    svg = render_atlas()
    root = ET.fromstring(svg)
    stripes = [el for el in root.iter() if (el.get("class") or "") == "sector"]
    # ~48,000 years / 919.25 y per sector spans ~52 sectors.
    assert 45 <= len(stripes) <= 60
