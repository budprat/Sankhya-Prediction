# ABOUTME: Declarative trigger rules: position patterns as data (TOML), one generic
# ABOUTME: evaluator — NU adds trigger inputs as rules, no new detector code needed.

import tomllib
from typing import Literal

from pydantic import BaseModel, Field

from .bands import (_arc_distance, axis_angle, circular_spread, division_of,
                    real_longitude)
from .horary import HORARY_NAKSHATRAS_28
from .models import ChartResult


class Condition(BaseModel):
    """One geometric predicate. Body names may be prefixed 'real:' to use the
    doctrinal ahead-position (Mathcad-QUAKE offsets)."""
    type: Literal["conjunction", "opposition", "square", "trine", "axis_cross",
                  "cluster", "same_band", "in_band", "nodes_occupied"]
    bodies: list[str] = []
    axes: list[list[str]] = []          # axis_cross: [[A,B],[C,D]]
    angle: float = 90.0                 # axis_cross target (0 = axes aligned)
    orb: float = 3.0
    max_spread: float | None = None     # cluster
    level: int = 0                      # same_band grid level
    band: str | int | None = None       # in_band target (name or 1..28)
    require: Literal["both", "either"] = "both"   # nodes_occupied: which node ends


class TriggerRule(BaseModel):
    name: str
    description: str = ""
    conditions: list[Condition] = Field(min_length=1)
    escalate: list[Condition] = []      # base + these -> "catastrophic"


class RuleState(BaseModel):
    rule: str
    fired: bool
    level: str                          # none | disruptive | catastrophic


def _lon(result: ChartResult, name: str) -> float:
    if name.startswith("real:"):
        return real_longitude(result, name.removeprefix("real:"))
    return result.positions[name].longitude


def _holds(result: ChartResult, c: Condition) -> bool:
    if c.type in ("conjunction", "opposition", "square", "trine"):
        a, b = (_lon(result, n) for n in c.bodies)
        sep = _arc_distance(a, b)
        target = {"conjunction": 0.0, "opposition": 180.0,
                  "square": 90.0, "trine": 120.0}[c.type]
        return abs(sep - target) <= c.orb
    if c.type == "axis_cross":
        cross = axis_angle(_lon(result, c.axes[0][0]), _lon(result, c.axes[1][0]))
        return abs(cross - c.angle) <= c.orb
    if c.type == "cluster":
        spread = circular_spread([_lon(result, n) for n in c.bodies])
        return spread <= (c.max_spread if c.max_spread is not None else c.orb)
    if c.type == "same_band":
        divisions = {division_of(_lon(result, n), c.level) for n in c.bodies}
        return len(divisions) == 1
    if c.type == "nodes_occupied":
        # Hyderaba-floods.docx pattern (2026-08-02): the nodal axis held at both
        # ends — some body conjunct Rahu AND some body conjunct Ketu, within orb.
        # require="either" relaxes to one end (used for giant escalation).
        rahu = result.positions["Rahu"].longitude
        ketu = result.positions["Ketu"].longitude
        held_rahu = any(_arc_distance(_lon(result, n), rahu) <= c.orb
                        for n in c.bodies)
        held_ketu = any(_arc_distance(_lon(result, n), ketu) <= c.orb
                        for n in c.bodies)
        return (held_rahu or held_ketu) if c.require == "either" \
            else (held_rahu and held_ketu)
    if c.type == "in_band":
        index = (HORARY_NAKSHATRAS_28.index(c.band) + 1
                 if isinstance(c.band, str) else int(c.band))
        return all(division_of(_lon(result, n), 0) == index for n in c.bodies)
    raise ValueError(c.type)


def evaluate_rule(result: ChartResult, rule: TriggerRule) -> RuleState:
    if not all(_holds(result, c) for c in rule.conditions):
        return RuleState(rule=rule.name, fired=False, level="none")
    escalated = bool(rule.escalate) and all(_holds(result, c) for c in rule.escalate)
    return RuleState(rule=rule.name, fired=True,
                     level="catastrophic" if escalated else "disruptive")


_ASPECT_TARGETS = {"conjunction": 0.0, "opposition": 180.0,
                   "square": 90.0, "trine": 120.0}


def aspect_target(rule: TriggerRule):
    """(body_a, body_b, target_deg, orb) of the rule's first pair condition."""
    for c in rule.conditions:
        if c.type in _ASPECT_TARGETS:
            return c.bodies[0], c.bodies[1], _ASPECT_TARGETS[c.type], c.orb
    return None


def acting_body(rule: TriggerRule) -> str | None:
    """The rule's locatable planet: first light-time body in a pair condition."""
    from .locator import LIGHT_MINUTES
    target = aspect_target(rule)
    if target is None:
        return None
    for name in target[:2]:
        bare = name.removeprefix("real:")
        if bare in LIGHT_MINUTES:
            return bare
    return None


def refine_episode_instant(chart_at, jd_lo: float, jd_hi: float,
                           rule: TriggerRule, step_days: float = 1 / 96):
    """Exact-aspect instant within an episode: minimum |sep - target| on a
    15-minute grid (handles both crossings and grazing approaches)."""
    target = aspect_target(rule)
    if target is None:
        return None
    name_a, name_b, angle, _ = target

    def gap_at(jd: float) -> float:
        result = chart_at(jd)
        return abs(_arc_distance(_lon(result, name_a), _lon(result, name_b)) - angle)

    def scan(lo: float, hi: float, step: float):
        best = None
        jd = lo
        while jd <= hi:
            gap = gap_at(jd)
            if best is None or gap < best[0]:
                best = (gap, jd)
            jd += step
        return best

    coarse = scan(jd_lo, jd_hi, step_days)
    if coarse is None:
        return None
    # Second stage: one-minute resolution around the coarse minimum, so the
    # located longitude is good to ~0.1 deg (15 deg/hour of Earth rotation).
    fine = scan(coarse[1] - step_days, coarse[1] + step_days, 1 / 1440)
    return fine[1]


def load_rules(path: str) -> list[TriggerRule]:
    with open(path, "rb") as fh:
        data = tomllib.load(fh)
    return [TriggerRule(**raw) for raw in data.get("rule", [])]
