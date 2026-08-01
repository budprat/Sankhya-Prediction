# ABOUTME: The Predict.pdf band-coincidence method: 28 equal bands x 11 bodies, trigger on
# ABOUTME: Moon+Ketu+Mars sharing a band, Uranus/Neptune escalation, episodes and scoring.

import calendar
import datetime as dt
import re

from pydantic import BaseModel

from .ephemeris import julian_day_number
from .horary import DIVISION_SPAN, HORARY_NAKSHATRAS_28
from .models import ChartResult

# The PDF's table columns, verbatim (no Pluto, no Ascendant — the scan is site-free).
BAND_BODIES = ["Sun", "Moon", "Rahu", "Ketu", "Mercury", "Venus",
               "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"]

TRIGGER_SET = {"Moon", "Ketu", "Mars"}
GIANTS = ("Uranus", "Neptune")

# Predict.pdf refinement ladder: band, band/9, band/63 ("1/63rd fraction").
LEVEL_DIVISORS = {0: 1, 1: 9, 2: 63}


def level_span(level: int) -> float:
    return DIVISION_SPAN / LEVEL_DIVISORS[level]


class TriggerState(BaseModel):
    fired: bool
    level: str                  # none | disruptive | catastrophic
    band: int = 0               # parent 28-band, for naming
    division: int = 0           # division index at the scan's grid level
    nakshatra: str = ""
    members: list[str] = []
    giants: list[str] = []
    spread_deg: float = 0.0     # proximity mode: circular spread of the trigger trio


class Episode(BaseModel):
    start_jd: float
    end_jd: float
    start_label: str
    end_label: str
    band: int
    division: int = 0
    nakshatra: str
    level: str
    giants: list[str]


def band_of(longitude: float) -> int:
    return int((longitude % 360.0) // DIVISION_SPAN) + 1


def division_of(longitude: float, level: int = 0) -> int:
    return int((longitude % 360.0) // level_span(level)) + 1


def band_table(result: ChartResult, level: int = 0) -> dict[int, list[str]]:
    table: dict[int, list[str]] = {}
    for name in BAND_BODIES:
        if name in result.positions:
            division = division_of(result.positions[name].longitude, level)
            table.setdefault(division, []).append(name)
    return table


class VyuhaState(BaseModel):
    """Chatur Vyuham (NU, 2026-08-01): two oppositions crossing at 90 deg —
    Sun-Saturn x Jupiter-Neptune/Uranus — with the nodal axis locked into the
    cross as the aggravator, and Saturn's closeness as the final weight."""
    fired: bool
    level: str                    # none | vyuha | vyuha+nodes
    partner: str = ""             # Neptune or Uranus on Jupiter's axis
    sun_saturn_sep: float = 0.0
    partner_sep: float = 0.0
    cross_deg: float = 0.0
    node_align_deg: float = 0.0   # node axis to nearest arm (mod 90 alignment)
    saturn_distance: float = 0.0


class VyuhaEpisode(BaseModel):
    start_jd: float
    end_jd: float
    start_label: str
    end_label: str
    level: str
    partner: str
    best_cross_deg: float         # closest approach to a perfect 90
    min_saturn_distance: float


def axis_angle(a: float, b: float) -> float:
    """Angle between two axes (each defined mod 180)."""
    d = abs(a - b) % 180.0
    return min(d, 180.0 - d)


def vyuha_state(result: ChartResult, orb_opp: float = 3.0, orb_cross: float = 5.0,
                orb_node: float = 5.0) -> VyuhaState:
    p = {name: result.positions[name].longitude for name in result.positions}
    saturn_distance = result.positions["Saturn"].distance if "Saturn" in result.positions else 0.0
    sun_saturn = _arc_distance(p["Sun"], p["Saturn"])
    if abs(sun_saturn - 180.0) > orb_opp:
        return VyuhaState(fired=False, level="none", saturn_distance=saturn_distance)
    partner = ""
    partner_sep = 0.0
    for candidate in ("Neptune", "Uranus"):
        sep_c = _arc_distance(p["Jupiter"], p[candidate])
        if abs(sep_c - 180.0) <= orb_opp:
            partner, partner_sep = candidate, sep_c
            break
    if not partner:
        return VyuhaState(fired=False, level="none", saturn_distance=saturn_distance)
    cross = axis_angle(p["Sun"], p["Jupiter"])
    if abs(cross - 90.0) > orb_cross:
        return VyuhaState(fired=False, level="none", saturn_distance=saturn_distance)
    node_align = min(axis_angle(p["Rahu"], p["Sun"]), axis_angle(p["Rahu"], p["Jupiter"]))
    nodes_locked = node_align <= orb_node
    return VyuhaState(
        fired=True, level="vyuha+nodes" if nodes_locked else "vyuha",
        partner=partner, sun_saturn_sep=sun_saturn, partner_sep=partner_sep,
        cross_deg=cross, node_align_deg=node_align, saturn_distance=saturn_distance)


def find_vyuha_episodes(samples: list[tuple[float, str, VyuhaState]],
                        step_days: float) -> list[VyuhaEpisode]:
    episodes: list[VyuhaEpisode] = []
    current: VyuhaEpisode | None = None
    for jd, label, state in samples:
        if state.fired:
            if current is not None and jd - current.end_jd <= step_days * 1.5:
                current.end_jd = jd
                current.end_label = label
                if state.level == "vyuha+nodes":
                    current.level = "vyuha+nodes"
                if abs(state.cross_deg - 90) < abs(current.best_cross_deg - 90):
                    current.best_cross_deg = state.cross_deg
                current.min_saturn_distance = min(current.min_saturn_distance,
                                                  state.saturn_distance)
            else:
                if current is not None:
                    episodes.append(current)
                current = VyuhaEpisode(start_jd=jd, end_jd=jd, start_label=label,
                                       end_label=label, level=state.level,
                                       partner=state.partner,
                                       best_cross_deg=state.cross_deg,
                                       min_saturn_distance=state.saturn_distance)
    if current is not None:
        episodes.append(current)
    return episodes


def circular_spread(longitudes: list[float]) -> float:
    """Smallest arc containing all points: 360 minus the largest gap."""
    angles = sorted(lon % 360.0 for lon in longitudes)
    gaps = [angles[i + 1] - angles[i] for i in range(len(angles) - 1)]
    gaps.append(360.0 - angles[-1] + angles[0])
    return 360.0 - max(gaps)


def _arc_distance(a: float, b: float) -> float:
    d = abs(a - b) % 360.0
    return min(d, 360.0 - d)


def trigger_state(result: ChartResult, level: int = 0,
                  proximity: bool = False) -> TriggerState:
    if proximity:
        # NU ruling (2026-08-01): the twang is about closeness, not grid cells —
        # fire when the trio's spread fits within the level's span, wherever the
        # boundaries fall; a giant escalates when within one span of the cluster.
        span = level_span(level)
        trio = {name: result.positions[name].longitude for name in TRIGGER_SET}
        spread = circular_spread(list(trio.values()))
        if spread <= span:
            giants = [g for g in GIANTS
                      if g in result.positions and min(
                          _arc_distance(result.positions[g].longitude, lon)
                          for lon in trio.values()) <= span]
            moon = result.positions["Moon"].longitude
            band = band_of(moon)
            return TriggerState(
                fired=True, level="catastrophic" if giants else "disruptive",
                band=band, division=division_of(moon, level),
                nakshatra=HORARY_NAKSHATRAS_28[band - 1],
                members=sorted(set(trio) | set(giants)), giants=giants,
                spread_deg=spread)
        return TriggerState(fired=False, level="none", spread_deg=spread)

    table = band_table(result, level)
    for division, members in table.items():
        if TRIGGER_SET <= set(members):
            giants = [g for g in GIANTS if g in members]
            band = (division - 1) // LEVEL_DIVISORS[level] + 1
            return TriggerState(
                fired=True, level="catastrophic" if giants else "disruptive",
                band=band, division=division,
                nakshatra=HORARY_NAKSHATRAS_28[band - 1],
                members=sorted(members), giants=giants)
    return TriggerState(fired=False, level="none")


def find_episodes(samples: list[tuple[float, str, TriggerState]],
                  step_days: float) -> list[Episode]:
    """Merge consecutive fired samples (gap <= 1.5 steps) into episodes."""
    episodes: list[Episode] = []
    current: Episode | None = None
    for jd, label, state in samples:
        if state.fired:
            if current is not None and jd - current.end_jd <= step_days * 1.5:
                current.end_jd = jd
                current.end_label = label
                if state.level == "catastrophic":
                    current.level = "catastrophic"
                    current.giants = sorted(set(current.giants) | set(state.giants))
            else:
                if current is not None:
                    episodes.append(current)
                current = Episode(start_jd=jd, end_jd=jd, start_label=label,
                                  end_label=label, band=state.band,
                                  division=state.division,
                                  nakshatra=state.nakshatra, level=state.level,
                                  giants=list(state.giants))
    if current is not None:
        episodes.append(current)
    return episodes


_MONTHS = {m.lower(): i for i, m in enumerate(calendar.month_name) if m}
_MONTHS.update({m.lower(): i for i, m in enumerate(calendar.month_abbr) if m})
_MONTH_RE = "|".join(sorted(_MONTHS, key=len, reverse=True))


def parse_event_window(year_cell, month_cell, date_cell) -> tuple[dt.date, dt.date, str]:
    """Best-effort window from the catalog's free-text date columns."""
    year = int(str(year_cell).strip())
    text = f"{date_cell or ''}".strip() or f"{month_cell or ''}".strip()
    lowered = text.lower()

    dates: list[dt.date] = []
    # "Month 18(th)(, 2014)" and "18(th) Month (2014)"; (?!\d) stops the day pattern
    # from eating the first digits of a four-digit year ("October 2015" is not day 20).
    for m in re.finditer(rf"({_MONTH_RE})\.?\s+(\d{{1,2}})(?:st|nd|rd|th)?(?!\d)(?:\s*,?\s*(\d{{4}}))?",
                         lowered):
        dates.append(dt.date(int(m.group(3) or year), _MONTHS[m.group(1)], int(m.group(2))))
    for m in re.finditer(rf"(\d{{1,2}})(?:st|nd|rd|th)?(?!\d)\s+({_MONTH_RE})\.?,?\s*(\d{{4}})?",
                         lowered):
        dates.append(dt.date(int(m.group(3) or year), _MONTHS[m.group(2)], int(m.group(1))))
    if dates:
        return min(dates), max(dates), "day"

    months: list[tuple[int, int]] = []
    for m in re.finditer(rf"({_MONTH_RE})[a-z]*\.?\s*(\d{{4}})?", lowered):
        months.append((int(m.group(2) or year), _MONTHS[m.group(1)]))
    if months:
        y0, m0 = min(months)
        y1, m1 = max(months)
        return (dt.date(y0, m0, 1),
                dt.date(y1, m1, calendar.monthrange(y1, m1)[1]), "month")

    return dt.date(year, 1, 1), dt.date(year, 12, 31), "year"


def _date_to_jd(day: dt.date) -> float:
    return julian_day_number(day.year, day.month, day.day) - 0.5  # midnight UT


def score_events(episodes: list[Episode], events: list[dict], margin_days: float,
                 sweep_start: dt.date, sweep_end: dt.date):
    """Per-event hit rows plus honest chance-baseline summary (independence approx.)."""
    total_days = (sweep_end - sweep_start).days + 1
    trigger_days = sum(e.end_jd - e.start_jd + 1 for e in episodes)
    p_day = min(1.0, trigger_days / total_days) if total_days else 0.0

    rows = []
    expected = 0.0
    hits = 0
    for event in events:
        start, end, precision = event["window"]
        lo = _date_to_jd(start) - margin_days
        hi = _date_to_jd(end) + 1 + margin_days
        hit = any(e.start_jd <= hi and e.end_jd >= lo for e in episodes)
        window_days = (end - start).days + 1 + 2 * margin_days
        p_chance = 1 - (1 - p_day) ** window_days
        expected += p_chance
        hits += hit
        rows.append({**event, "hit": hit, "precision": precision,
                     "p_chance": round(p_chance, 4)})
    summary = {"events": len(rows), "hits": hits,
               "trigger_day_fraction": round(p_day, 4),
               "expected_hits_by_chance": round(expected, 2)}
    return rows, summary
