# ABOUTME: The validation framework — one audited set of control designs, statistics and
# ABOUTME: verdict machinery, so every claim in this project is graded the same way.
#
# WHY THIS MODULE EXISTS (NU, 2026-08-05: "your testing framework must be
# authentic for our usecase"). Eleven claims were graded before this file
# existed, each script inventing its own controls, statistic and null. The
# variation was partly principled — a LOCATION claim needs place-controls, a
# TIMING claim needs time-controls — but that principle lived in prose, not in
# code, and seven of the eleven were never formally pre-registered.
#
# The framework makes three things structural rather than conventional:
#
#   1. PRE-REGISTRATION IS A TYPE. A Claim cannot be constructed without its
#      hypothesis, direction, statistic, control design, verdict rule, power
#      plan and corpus. You cannot run a test here without having declared
#      what would refute it.
#
#   2. CONTROLS MATCH THE CLAIM'S KIND. Two designs, and the choice is forced
#      by what is being claimed:
#        * TIMING claims ("this configuration accompanies events") take
#          ERA-MATCHED time controls: instants near the event, so the
#          catalogue's completeness regime and the slow bodies' epoch are held
#          fixed. Uniform controls once promoted an era-locked predicate to
#          lift 55 on nothing but the catalogue's reporting gradient.
#        * LOCATION claims ("this points at a place") take PLACE controls:
#          other real epicentres at the SAME instant. Random points on a
#          sphere are not a null for seismicity, which lives on belts.
#
#   3. A NULL WITHOUT POWER IS SILENCE. power_curve() plants a known effect
#      and reports recovery, so "we found nothing" can be distinguished from
#      "we could not have found anything".
#
# See TESTING.md for the protocol and RESULTS.md for every graded claim.

import math
import random
from dataclasses import dataclass, field

DIRECTIONS = ("higher", "lower")


@dataclass
class Claim:
    """A pre-registration. Every field is required; an empty one raises, so a
    test cannot be run with its design left implicit."""
    name: str
    hypothesis: str          # what the doctrine asserts, as a falsifiable claim
    direction: str           # "higher" | "lower" — fixed BEFORE seeing data
    statistic: str           # the one number that decides it
    control: str             # era-matched | place | same-size | label-permutation
    verdict: str             # the rule, e.g. "p < 0.05 and lift > 1"
    corpus: str              # what it is measured on, with n
    power: str               # how a null will be distinguished from blindness
    registered_at: str | None = None      # stamped by the runner, not the author
    notes: str = ""
    _required: tuple = field(default=(), repr=False, compare=False)

    def __post_init__(self):
        for f in ("name", "hypothesis", "direction", "statistic", "control",
                  "verdict", "corpus", "power"):
            if not str(getattr(self, f)).strip():
                raise ValueError(f"Claim is missing '{f}': a design element "
                                 f"cannot be left implicit")
        if self.direction not in DIRECTIONS:
            raise ValueError(f"direction must be one of {DIRECTIONS}, "
                             f"got {self.direction!r}")

    def banner(self) -> str:
        return (f"CLAIM {self.name}\n"
                f"  hypothesis : {self.hypothesis}\n"
                f"  direction  : {self.direction}\n"
                f"  statistic  : {self.statistic}\n"
                f"  controls   : {self.control}\n"
                f"  corpus     : {self.corpus}\n"
                f"  verdict    : {self.verdict}\n"
                f"  power      : {self.power}")


# --------------------------------------------------------------------------
# Control designs
# --------------------------------------------------------------------------

def era_matched_controls(jds, k: int, window_days: float = 365.0,
                         exclude_days: float = 7.0,
                         seed: int = 42) -> list[list[float]]:
    """TIMING controls: k instants per event drawn from +-window_days of it,
    excluding +-exclude_days. Holds the catalogue's completeness regime and
    the slow bodies' epoch fixed; the fast bodies still sweep freely."""
    rng = random.Random(seed)
    out = []
    for jd in jds:
        block = []
        while len(block) < k:
            off = rng.uniform(-window_days, window_days)
            if abs(off) > exclude_days:
                block.append(jd + off)
        out.append(block)
    return out


def place_controls(places, k: int, seed: int = 42) -> list[list[tuple]]:
    """LOCATION controls: k OTHER real epicentres per event, leave-one-out.
    Random points on a sphere are not a null for seismicity — it lives on
    belts, so the controls must inherit that geography."""
    rng = random.Random(seed)
    out = []
    for i, _ in enumerate(places):
        others = places[:i] + places[i + 1:]
        out.append(rng.sample(others, min(k, len(others))))
    return out


# --------------------------------------------------------------------------
# Statistic and verdict
# --------------------------------------------------------------------------

def smoothed_lift(e_hits: int, n_e: int, c_hits: int, n_c: int) -> float:
    """Add-one smoothed rate ratio: zero control hits must not read as
    infinite evidence (audit finding 53)."""
    return ((e_hits + 1) / (n_e + 2)) / ((c_hits + 1) / (n_c + 2))


def block_permutation_p(blocks, observed: float, n_perm: int = 2000,
                        seed: int = 43) -> float:
    """Null by re-labelling WITHIN each block: which of the (1 event + k
    controls) instants was the event? This preserves every block's own
    composition, so era, geography and seasonality cannot leak into the null."""
    if not blocks:
        return 1.0
    n_e = len(blocks)
    n_c = sum(len(b) - 1 for b in blocks)
    rng = random.Random(seed)
    worse = 0
    for _ in range(n_perm):
        eh = ch = 0
        for flags in blocks:
            j = rng.randrange(len(flags))
            eh += flags[j]
            ch += sum(flags) - flags[j]
        if smoothed_lift(eh, n_e, ch, n_c) >= observed:
            worse += 1
    return worse / n_perm


def power_curve(blocks, fractions=(0.10, 0.05, 0.02), n_perm: int = 500,
                seed: int = 44) -> list[dict]:
    """Plant the predicate into a fraction of events and report recovery. A
    null is only evidence if this shows the effect WOULD have been seen."""
    n_e = len(blocks)
    n_c = sum(len(b) - 1 for b in blocks)
    base_c = sum(sum(b[1:]) for b in blocks)
    rows = []
    for frac in fractions:
        planted = [list(b) for b in blocks]
        k = int(n_e * frac)
        for i in [i for i in range(n_e) if not planted[i][0]][:k]:
            planted[i][0] = True
        eh = sum(b[0] for b in planted)
        L = smoothed_lift(eh, n_e, base_c, n_c)
        rows.append({"fraction": frac, "lift": L,
                     "p": block_permutation_p(planted, L, n_perm, seed)})
    return rows


def report(claim: Claim, observed: float, p: float, power: list[dict],
           extra: str = "") -> str:
    """One rendering for every claim, so results cannot be presented in
    shapes that flatter them."""
    verdict = "SUPPORTED" if p < 0.05 else "NOT SUPPORTED"
    lines = [claim.banner(), "",
             f"  observed {claim.statistic}: {observed:.4f}",
             f"  p = {p:.4f}   ->  {verdict} (bar: {claim.verdict})"]
    if extra:
        lines.append(f"  {extra}")
    lines.append("  power:")
    for row in power:
        lines.append(f"    plant {int(row['fraction']*100):>3}% -> "
                     f"lift {row['lift']:.3f}, p = {row['p']:.4f}")
    weakest = max(power, key=lambda r: r["p"]) if power else None
    if weakest and weakest["p"] >= 0.05:
        lines.append("    WARNING: the instrument did not recover a planted "
                     "effect — this result is UNDERPOWERED, not a refutation.")
    return "\n".join(lines)


def poisson_sigma(observed: int, expected: float) -> float:
    """How many Poisson sd is an excess? Guards against reading a big ratio on
    a tiny count as a finding (the band trigger: 12 vs 7.0 is 1.4 sd)."""
    return (observed - expected) / math.sqrt(observed) if observed else 0.0
