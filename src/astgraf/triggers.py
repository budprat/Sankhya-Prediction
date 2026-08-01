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
                  "cluster", "same_band", "in_band"]
    bodies: list[str] = []
    axes: list[list[str]] = []          # axis_cross: [[A,B],[C,D]]
    angle: float = 90.0                 # axis_cross target (0 = axes aligned)
    orb: float = 3.0
    max_spread: float | None = None     # cluster
    level: int = 0                      # same_band grid level
    band: str | int | None = None       # in_band target (name or 1..28)


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


def load_rules(path: str) -> list[TriggerRule]:
    with open(path, "rb") as fh:
        data = tomllib.load(fh)
    return [TriggerRule(**raw) for raw in data.get("rule", [])]
