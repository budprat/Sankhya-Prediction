# ABOUTME: The site-angle location layer against NU's three taught anchors — the
# ABOUTME: crossing pair stands on a chart angle at Nepal, Hyderabad and Ulsoor.

import pytest

from astgraf.anchors import iso_jd
from astgraf.angles import (
    angles_at,
    bodies_on_angles,
    latitude_on_meridian,
    meridian_of,
    site_chart,
)

NEPAL = (28.2305, 84.7314, "2015-04-25T06:11:25.950Z")
HYDERABAD = (17.385, 78.487, "2016-09-23T11:34:00Z")
ULSOOR = (12.98, 77.62, "2016-03-07T00:42:00Z")


def _hits(anchor, orb=3.0):
    lat, lon, iso = anchor
    return bodies_on_angles(iso_jd(iso), lat, lon, orb)


def test_nepal_puts_the_taught_pair_on_the_meridian():
    # The taught Nepal signature is "real-Uranus on the Sun" — and at Gorkha
    # that pair is culminating: both within 3 deg of the MC.
    on = {(b, k): s for s, k, b in _hits(NEPAL)}
    assert ("Sun", "MC") in on
    assert ("real-Uranus", "MC") in on
    assert on[("Sun", "MC")] == pytest.approx(2.00, abs=0.1)
    assert on[("real-Uranus", "MC")] == pytest.approx(2.69, abs=0.1)


def test_hyderabad_puts_the_node_pair_on_the_horizon():
    # NU's taught Hyderabad pattern: Neptune on Ketu at the node axis — and at
    # the site that axis lies along the horizon.
    on = {(b, k): s for s, k, b in _hits(HYDERABAD)}
    assert on[("Neptune", "Asc")] == pytest.approx(0.56, abs=0.1)
    assert on[("Ketu", "Asc")] == pytest.approx(0.59, abs=0.1)
    assert on[("Rahu", "Desc")] == pytest.approx(0.59, abs=0.1)


def test_ulsoor_puts_neptune_on_the_ascendant():
    # NU's taught Ulsoor statement: "the Asc swept Neptune -> Sun -> Ketu ->
    # Uranus". Neptune sits 0.09 deg off the Ascendant — 10 km of arc.
    on = {(b, k): s for s, k, b in _hits(ULSOOR)}
    assert on[("Neptune", "Asc")] == pytest.approx(0.09, abs=0.05)
    assert on[("Saturn", "MC")] == pytest.approx(1.51, abs=0.1)


def test_every_taught_anchor_has_a_body_on_an_angle():
    # The rule must hold at all three, not just the one it was noticed on.
    for anchor in (NEPAL, HYDERABAD, ULSOOR):
        assert _hits(anchor), "no body within 3 deg of any angle"


def test_meridian_of_recovers_the_culminating_longitude():
    # "Body on the MC" fixes a meridian: solving it at Nepal's Sun longitude
    # must land within a couple of degrees of Gorkha.
    lat, lon, iso = NEPAL
    jd = iso_jd(iso)
    sun = site_chart(jd, lat, lon).positions["Sun"].longitude
    got = meridian_of(jd, sun)
    assert got is not None
    assert abs(((got - lon + 180) % 360) - 180) < 3.0
    # and the recovered meridian really does put the Sun on the MC there
    assert abs(((angles_at(jd, lat, got)["MC"] - sun + 180) % 360) - 180) < 0.05


def test_latitude_axis_is_the_weakly_conditioned_one():
    # The honest limit: the Ascendant moves ~0.35 deg per degree of latitude,
    # so latitude is recovered far less sharply than longitude. Pin the
    # sensitivity itself so a future change cannot quietly claim more.
    _lat, lon, iso = NEPAL
    jd = iso_jd(iso)
    a20 = angles_at(jd, 20.0, lon)["Asc"]
    a30 = angles_at(jd, 30.0, lon)["Asc"]
    d_asc_per_deg_lat = (a30 - a20) / 10.0
    assert 0.2 < d_asc_per_deg_lat < 0.6
    # solving for a latitude still works, it is just soft
    got = latitude_on_meridian(jd, lon, a20)
    assert got == pytest.approx(20.0, abs=0.5)
