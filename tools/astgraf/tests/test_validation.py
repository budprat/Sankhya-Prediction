# ABOUTME: Tests the validation framework: a Claim cannot run without its design
# ABOUTME: declared, and the shared control/verdict primitives behave as specified.

import pytest

from astgraf.validation import (Claim, block_permutation_p, era_matched_controls,
                                place_controls, power_curve, smoothed_lift)


def test_claim_requires_its_full_design_up_front():
    # Pre-registration must be STRUCTURAL, not a comment convention: a Claim
    # that omits any element of its design cannot be constructed.
    ok = Claim(name="x", hypothesis="events carry P more than controls",
               direction="higher", statistic="smoothed lift",
               control="era-matched", verdict="p < 0.05 and lift > 1",
               power="plant P into 2/5/10% of events", corpus="n=100 declustered")
    assert ok.registered_at is None      # stamped only when it is run
    for missing in ("hypothesis", "direction", "statistic", "control",
                    "verdict", "power", "corpus"):
        kwargs = dict(name="x", hypothesis="h", direction="higher",
                      statistic="s", control="c", verdict="v", power="p",
                      corpus="n")
        kwargs[missing] = ""
        with pytest.raises(ValueError, match=missing):
            Claim(**kwargs)


def test_claim_rejects_an_unknown_direction():
    with pytest.raises(ValueError, match="direction"):
        Claim(name="x", hypothesis="h", direction="sideways", statistic="s",
              control="c", verdict="v", power="p", corpus="n")


def test_era_matched_controls_hold_the_epoch_and_exclude_the_event():
    jds = [2440000.0, 2450000.0]
    out = era_matched_controls(jds, k=5, window_days=365.0,
                               exclude_days=7.0, seed=1)
    assert [len(b) for b in out] == [5, 5]
    for jd, block in zip(jds, out):
        for c in block:
            assert 7.0 < abs(c - jd) <= 365.0
    # deterministic under the same seed, different under another
    assert out == era_matched_controls(jds, 5, 365.0, 7.0, seed=1)
    assert out != era_matched_controls(jds, 5, 365.0, 7.0, seed=2)


def test_place_controls_are_other_real_epicentres():
    places = [(10.0, 20.0), (-5.0, 100.0), (40.0, -70.0), (0.0, 0.0)]
    out = place_controls(places, k=2, seed=3)
    assert len(out) == 4
    for i, block in enumerate(out):
        assert len(block) == 2
        assert places[i] not in block, "an event's own place cannot be its control"
        assert all(p in places for p in block), "controls must be REAL places"


def test_smoothed_lift_is_finite_at_zero_control_hits():
    assert smoothed_lift(10, 10, 0, 30) == pytest.approx((11 / 12) / (1 / 32))
    assert smoothed_lift(0, 10, 0, 30) > 0


def test_block_permutation_recovers_a_planted_effect_and_not_noise():
    # 200 blocks of 1 event + 5 controls. Planted: the event fires in 40
    # blocks where controls never do.
    planted = [[True] + [False] * 5 for _ in range(40)]
    planted += [[False] * 6 for _ in range(160)]
    obs = smoothed_lift(40, 200, 0, 1000)
    p = block_permutation_p(planted, obs, n_perm=500, seed=5)
    assert p < 0.01

def test_block_permutation_is_calibrated_under_the_null():
    # The property that matters for a validation framework: under pure noise
    # the p-values must be CALIBRATED, i.e. p < 0.05 about 5% of the time.
    # (Asserting that one noise draw gives p > 0.05 would itself be a coin
    # flip — the first version of this test did exactly that and failed on a
    # seed whose draw happened to reach lift 1.42.)
    import random
    false_positives = 0
    trials = 60
    for t in range(trials):
        rng = random.Random(1000 + t)
        blocks = []
        for _ in range(150):
            row = [False] * 6
            if rng.random() < 0.20:          # a firing lands anywhere at random
                row[rng.randrange(6)] = True
            blocks.append(row)
        eh = sum(b[0] for b in blocks)
        ch = sum(sum(b[1:]) for b in blocks)
        obs = smoothed_lift(eh, 150, ch, 750)
        if block_permutation_p(blocks, obs, n_perm=200, seed=t) < 0.05:
            false_positives += 1
    rate = false_positives / trials
    assert rate <= 0.20, f"null is anti-conservative: {rate:.2f} false positives"


def test_power_curve_reports_recovery_at_each_planted_fraction():
    blocks = [[False] * 6 for _ in range(500)]
    curve = power_curve(blocks, fractions=(0.10, 0.02), n_perm=200, seed=7)
    assert [row["fraction"] for row in curve] == [0.10, 0.02]
    assert all(row["p"] < 0.05 for row in curve), curve
    assert curve[0]["lift"] > curve[1]["lift"] > 1.0
