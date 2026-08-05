# ABOUTME: The site-angle location layer against NU's three taught anchors — the
# ABOUTME: crossing pair stands on a chart angle at Nepal, Hyderabad and Ulsoor.

import random
import statistics

import pytest

from astgraf.anchors import iso_jd
from astgraf.angles import (
    angles_at,
    angles_from_chart,
    bodies_on_angles,
    body_longitudes,
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


def _nearest_angle(jd, lat, lon, body):
    c = site_chart(jd, lat, lon)
    p = body_longitudes(c)[body]
    return min(min(abs(a - p) % 360, 360 - abs(a - p) % 360)
               for a in angles_from_chart(c).values())


def test_rank_statistic_can_detect_a_planted_location_signal():
    # scripts/angle_grade.py graded this layer over the M7+ catalog and found
    # nothing. A null is only evidence if the statistic can see a signal, so
    # plant epicenters on the meridian where Mars culminates and confirm the
    # rank collapses to 1, while places drawn at random sit at chance.
    rng = random.Random(3)
    jds = [iso_jd("2015-04-25T06:11:25.950Z") + 37.0 * i for i in range(12)]
    pool = [(rng.uniform(-55, 55), rng.uniform(-180, 180)) for _ in range(25)]
    planted_ranks, chance_ranks = [], []
    for jd in jds:
        mars = body_longitudes(site_chart(jd, 0.0, 0.0))["Mars"]
        lon = meridian_of(jd, mars)
        assert lon is not None, "Mars must culminate on some meridian"
        ctrl = [_nearest_angle(jd, la, lo, "Mars") for la, lo in pool]
        planted = _nearest_angle(jd, 0.0, lon, "Mars")
        planted_ranks.append(1 + sum(1 for s in ctrl if s < planted))
        loose = _nearest_angle(jd, rng.uniform(-55, 55),
                               rng.uniform(-180, 180), "Mars")
        chance_ranks.append(1 + sum(1 for s in ctrl if s < loose))
    # a planted place is always the tightest — the statistic is not blind
    assert planted_ranks == [1] * len(jds)
    # and an unplanted place lands mid-pack, so the statistic is calibrated
    mean_chance = statistics.mean((r - 1) / len(pool) for r in chance_ranks)
    assert 0.25 < mean_chance < 0.75
