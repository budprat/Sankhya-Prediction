# ABOUTME: Tests the family-grain recurrence channel: slow-pair conjunction series with
# ABOUTME: canon nakshatra sectors, member-sector return flags, and the family calendar.

import csv

from astgraf.anchors import iso_jd
from astgraf.families import (FAMILIES_PATH, conjunction_series, family_calendar,
                              load_families, main)

import pytest


def jd(year):
    return iso_jd(f"{year}-01-01T00:00:00Z")


def family(name):
    return next(f for f in load_families(FAMILIES_PATH) if f.name == name)


def test_load_families_ships_the_taught_families():
    families = load_families(FAMILIES_PATH)
    java = family("java-jupiter-saturn")
    assert java.pair == ["Jupiter", "Saturn"]
    sectors = {m.sector: m.anchor for m in java.members}
    assert sectors.get("Aswini") == "krakatoa-1883"      # NU: 1881 -> Krakatoa
    assert sectors.get("Kritika") == "sumatra-2004"      # NU: 2000 -> 2004 tsunami
    assert any(f.name == "flood-uranus-neptune" and f.pair == ["Uranus", "Neptune"]
               for f in families)


def test_load_families_rejects_unknown_keys(tmp_path):
    bad = tmp_path / "f.toml"
    bad.write_text('[[family]]\nname="x"\npair=["Jupiter","Saturn"]\nbogus=1\n')
    with pytest.raises(ValueError, match="bogus"):
        load_families(str(bad))


def test_java_taught_members_reproduce_with_canon_sectors():
    # NU's taught members are the oracles: the 1881 conjunction falls in
    # Aswini, the 2000 conjunction in Kritika (canon star names/arithmetic).
    old = conjunction_series("Jupiter", "Saturn", jd(1880), jd(1882))
    assert len(old) == 1 and old[0]["star"] == "Aswini"
    modern = conjunction_series("Jupiter", "Saturn", jd(1999), jd(2001))
    assert len(modern) == 1 and modern[0]["star"] == "Kritika"
    assert modern[0]["utc"].startswith("2000-05")
    assert ":" in modern[0]["utc"]                        # minute-refined


def test_triple_conjunction_is_not_collapsed():
    # 1980-81: the Jupiter-Saturn TRIPLE conjunction - three crossings, not one.
    triple = conjunction_series("Jupiter", "Saturn", jd(1980), jd(1982))
    assert len(triple) == 3


def test_next_java_member_appears_forward():
    ahead = conjunction_series("Jupiter", "Saturn", jd(2039), jd(2042))
    assert len(ahead) >= 1
    row = ahead[0]
    assert set(row) >= {"jd", "utc", "sidereal_lon", "star", "pada", "band"}


def test_family_calendar_flags_member_sector_returns():
    java = family("java-jupiter-saturn")
    hit = family_calendar(java, jd(1999), jd(2001))
    assert hit[0]["member_return"] is True
    assert "sumatra-2004" in hit[0]["member_anchors"]
    miss = family_calendar(java, jd(1980), jd(1982))
    assert all(r["member_return"] is False for r in miss)


def test_uranus_neptune_returns():
    past = conjunction_series("Uranus", "Neptune", jd(1990), jd(1996))
    assert len(past) >= 1 and past[0]["utc"].startswith("1993")
    # The next synodic return ~2165; engine drift at that range is degrees-
    # level, so assert presence in a wide window, not a date.
    ahead = conjunction_series("Uranus", "Neptune", jd(2158), jd(2172))
    assert len(ahead) >= 1


def test_cli_writes_the_family_calendar(tmp_path):
    main(["--family", "java-jupiter-saturn", "--start", "1999", "--end", "2001",
          "--out", str(tmp_path)])
    with open(tmp_path / "families.csv", newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert rows and rows[0]["family"] == "java-jupiter-saturn"
    assert rows[0]["star"] == "Kritika"
    assert (tmp_path / "families.txt").exists()
