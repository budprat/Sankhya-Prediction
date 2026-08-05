# ABOUTME: Declarative trigger rules: position patterns as data (TOML), one generic
# ABOUTME: evaluator — NU adds trigger inputs as rules, no new detector code needed.

import tomllib
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .bands import (_arc_distance, axis_angle, circular_spread, division_of,
                    real_longitude)
from .horary import HORARY_NAKSHATRAS_28
from .models import ChartResult


class Condition(BaseModel):
    """One geometric predicate. Body names may be prefixed 'real:' to use the
    doctrinal ahead-position (Mathcad-QUAKE offsets)."""
    # extra="forbid" (audit finding 12): a misspelled TOML key must fail the
    # load, not silently produce a vacuous condition.
    model_config = ConfigDict(extra="forbid")
    type: Literal["conjunction", "opposition", "square", "trine", "axis_cross",
                  "cluster", "same_band", "in_band", "nodes_occupied", "near_any",
                  "mirror"]
    bodies: list[str] = []
    targets: list[str] = []             # near_any: bodies measured against these
    axes: list[list[str]] = []          # axis_cross: [[A,B],[C,D]]
    angle: float = 90.0                 # axis_cross target (0 = axes aligned)
    orb: float = 3.0
    max_spread: float | None = None     # cluster
    level: int = 0                      # same_band grid level
    band: str | int | list[str | int] | None = None  # in_band target(s)
    require: Literal["both", "either"] = "both"   # nodes_occupied: which node ends

    @model_validator(mode="after")
    def _structurally_complete(self):
        """A condition missing its operative fields must fail the load, not
        evaluate vacuously true (audit finding 12)."""
        needs = {"conjunction": 2, "opposition": 2, "square": 2, "trine": 2,
                 "cluster": 2, "same_band": 2, "nodes_occupied": 1, "in_band": 1,
                 "near_any": 1, "mirror": 2}
        n = needs.get(self.type)
        if n is not None and len(self.bodies) < n:
            raise ValueError(f"{self.type} needs at least {n} bodies")
        if self.type == "near_any" and not self.targets:
            raise ValueError("near_any needs targets")
        if self.type == "in_band" and self.band is None:
            raise ValueError("in_band needs a band")
        if self.type == "axis_cross" and (
                len(self.axes) != 2 or any(len(ax) != 2 for ax in self.axes)):
            raise ValueError("axis_cross needs two axes of two bodies")
        return self


class TriggerRule(BaseModel):
    model_config = ConfigDict(extra="forbid")
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


def _axis_dir(result: ChartResult, axis: list[str]) -> float:
    """Axis direction from BOTH declared endpoints — the midline — so the
    verdict cannot depend on the listed order (audit findings 19/29)."""
    a = _lon(result, axis[0])
    if len(axis) < 2:
        return a
    b = _lon(result, axis[1]) + 180.0
    d = (b - a + 180.0) % 360.0 - 180.0
    return (a + d / 2.0) % 360.0


def _holds(result: ChartResult, c: Condition) -> bool:
    if c.type in ("conjunction", "opposition", "square", "trine"):
        a, b = (_lon(result, n) for n in c.bodies)
        sep = _arc_distance(a, b)
        target = {"conjunction": 0.0, "opposition": 180.0,
                  "square": 90.0, "trine": 120.0}[c.type]
        return abs(sep - target) <= c.orb
    if c.type == "mirror":
        # The heritage cos-fold crossing (GRAPHDO plots y = cos(lon)): the pair
        # meets on the graph when lon_a + lon_b is a multiple of 360.
        from .aspects import mirror_offset
        a, b = (_lon(result, n) for n in c.bodies)
        return abs(mirror_offset(a, b)) <= c.orb
    if c.type == "axis_cross":
        cross = axis_angle(_axis_dir(result, c.axes[0]),
                           _axis_dir(result, c.axes[1]))
        return abs(cross - c.angle) <= c.orb
    if c.type == "cluster":
        spread = circular_spread([_lon(result, n) for n in c.bodies])
        return spread <= (c.max_spread if c.max_spread is not None else c.orb)
    if c.type == "near_any":
        # The validated scanner's giant escalation (bands.py GIANTS): ANY of
        # `bodies` within `orb` arc-distance of ANY of `targets`.
        return any(_arc_distance(_lon(result, b), _lon(result, t)) <= c.orb
                   for b in c.bodies for t in c.targets)
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
        bands = c.band if isinstance(c.band, list) else [c.band]
        indices = {HORARY_NAKSHATRAS_28.index(b) + 1 if isinstance(b, str)
                   else int(b) for b in bands}
        return all(division_of(_lon(result, n), 0) in indices for n in c.bodies)
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


def _metric_for(rule: TriggerRule):
    """Rule-specific exactness scalar (smaller = tighter); None if undefined.

    Audit batch 2: every rule type gets a tightest-instant metric, not only
    aspect pairs — cluster spread, axis-cross gap, node-holding tightness.
    """
    target = aspect_target(rule)
    if target is not None:
        name_a, name_b, angle, _ = target
        return lambda r: abs(
            _arc_distance(_lon(r, name_a), _lon(r, name_b)) - angle)
    for c in rule.conditions:
        if c.type == "mirror":
            from .aspects import mirror_offset
            name_a, name_b = c.bodies[0], c.bodies[1]
            return lambda r: abs(mirror_offset(_lon(r, name_a), _lon(r, name_b)))
        if c.type == "cluster":
            bodies = list(c.bodies)
            return lambda r: circular_spread([_lon(r, n) for n in bodies])
        if c.type == "axis_cross":
            ax, ang = c.axes, c.angle
            return lambda r: abs(
                axis_angle(_lon(r, ax[0][0]), _lon(r, ax[1][0])) - ang)
        if c.type == "nodes_occupied":
            bodies, req = list(c.bodies), c.require

            def node_gap(r, bodies=bodies, req=req):
                rahu = r.positions["Rahu"].longitude
                ketu = r.positions["Ketu"].longitude
                dr = min(_arc_distance(_lon(r, n), rahu) for n in bodies)
                dk = min(_arc_distance(_lon(r, n), ketu) for n in bodies)
                return max(dr, dk) if req == "both" else min(dr, dk)
            return node_gap
    return None


def acting_body_at(rule: TriggerRule, result: ChartResult) -> str | None:
    """The locatable body acting at this instant: the aspect pair's light-time
    body, or the nearest light-time body of a near_any / nodes condition."""
    from .locator import LIGHT_MINUTES
    static = acting_body(rule)
    if static:
        return static
    for c in list(rule.escalate) + list(rule.conditions):
        names = [n.removeprefix("real:") for n in c.bodies]
        cands = [n for n in names if n in LIGHT_MINUTES]
        if not cands:
            continue
        if c.type == "near_any" and c.targets:
            def gap(b):
                return min(_arc_distance(_lon(result, b), _lon(result, t))
                           for t in c.targets)
        elif c.type == "nodes_occupied":
            rahu = result.positions["Rahu"].longitude
            ketu = result.positions["Ketu"].longitude

            def gap(b):
                return min(_arc_distance(_lon(result, b), rahu),
                           _arc_distance(_lon(result, b), ketu))
        elif c.type == "mirror":
            # The cos-fold pair locates like any other pair: its light-time
            # body acts, measured by how far the pair sits from the mirror.
            # Measured on the condition's own specs, so a `real:` prefix is
            # honoured — the doctrinal ahead-position is what stands there.
            from .aspects import mirror_offset
            specs = list(c.bodies)

            def gap(b, specs=specs):
                i = next(k for k, s in enumerate(specs)
                         if s.removeprefix("real:") == b)
                return min(abs(mirror_offset(_lon(result, specs[i]),
                                             _lon(result, o)))
                           for k, o in enumerate(specs) if k != i)
        else:
            continue
        best = min(cands, key=gap)
        # Only a body actually WITHIN the condition's orb acts — a distant
        # giant must not publish a spot for a window it did not join.
        if gap(best) <= c.orb:
            return best
    return None


def refine_episode_instant(chart_at, jd_lo: float, jd_hi: float,
                           rule: TriggerRule, step_days: float = 1 / 96):
    """Tightest instant within an episode: minimum of the rule's exactness
    metric on a 15-minute grid, then a one-minute pass — clamped to the
    window (audit finding 49)."""
    metric = _metric_for(rule)
    if metric is None:
        return None

    def gap_at(jd: float) -> float:
        return metric(chart_at(jd))

    def scan(lo: float, hi: float, step: float):
        best = None
        jd = lo
        while jd <= hi:
            gap = gap_at(jd)
            # Earliest-within-tolerance (finding 13): when a retrograde loop
            # holds several equally-exact crossings, ephemeris noise must not
            # pick among them — the first one wins deterministically.
            if best is None or gap < best[0] - 1e-6:
                best = (gap, jd)
            jd += step
        return best

    coarse = scan(jd_lo, jd_hi, step_days)
    if coarse is None:
        return None
    # Second stage: one-minute resolution around the coarse minimum, so the
    # located longitude is good to ~0.1 deg (15 deg/hour of Earth rotation).
    fine = scan(max(jd_lo, coarse[1] - step_days),
                min(jd_hi, coarse[1] + step_days), 1 / 1440)
    return min(max(fine[1], jd_lo), jd_hi)


def mentions_ascendant(rule: TriggerRule) -> bool:
    """Site-specific rules: the Ascendant only means something at a real site."""
    for c in rule.conditions + rule.escalate:
        names = list(c.bodies) + [n for axis in c.axes for n in axis]
        if any(n.removeprefix("real:") == "Ascendant" for n in names):
            return True
    return False


def _resolve_rules_path(path: str) -> str:
    """A shipped rule file may be named bare ("doctrine-triggers.toml") from
    any directory: fall back to the package root, where the TOMLs live. An
    explicit path that does not exist still raises, so typos stay loud."""
    from pathlib import Path
    p = Path(path)
    if p.exists() or p.is_absolute() or len(p.parts) > 1:
        return path
    shipped = Path(__file__).resolve().parents[2] / p.name
    return str(shipped) if shipped.exists() else path


def load_rules(path: str) -> list[TriggerRule]:
    path = _resolve_rules_path(path)
    with open(path, "rb") as fh:
        data = tomllib.load(fh)
    rules = [TriggerRule(**raw) for raw in data.get("rule", [])]
    if not rules:
        raise ValueError(f"{path}: no [[rule]] tables found "
                         f"(top-level keys: {sorted(data) or 'none'})")
    # Load-time name guards (audit findings 23/30): a 'real:' prefix on a body
    # without a doctrinal offset would silently evaluate the observed position;
    # an unknown body name would only fail (or pass vacuously) at run time.
    from .bands import REAL_POSITION_OFFSETS
    from .ephemeris import BODY_ORDER
    for rule in rules:
        for c in rule.conditions + rule.escalate:
            names = list(c.bodies) + list(c.targets) + [n for ax in c.axes
                                                        for n in ax]
            for name in names:
                bare = name.removeprefix("real:")
                if bare not in BODY_ORDER:
                    raise ValueError(f"rule '{rule.name}': unknown body {name!r}")
                if name.startswith("real:") and bare not in REAL_POSITION_OFFSETS:
                    raise ValueError(
                        f"rule '{rule.name}': 'real:{bare}' has no doctrinal "
                        f"offset (defined: {sorted(REAL_POSITION_OFFSETS)})")
    return rules
