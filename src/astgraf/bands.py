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


class TriggerState(BaseModel):
    fired: bool
    level: str                  # none | disruptive | catastrophic
    band: int = 0
    nakshatra: str = ""
    members: list[str] = []
    giants: list[str] = []


class Episode(BaseModel):
    start_jd: float
    end_jd: float
    start_label: str
    end_label: str
    band: int
    nakshatra: str
    level: str
    giants: list[str]


def band_of(longitude: float) -> int:
    return int((longitude % 360.0) // DIVISION_SPAN) + 1


def band_table(result: ChartResult) -> dict[int, list[str]]:
    table: dict[int, list[str]] = {}
    for name in BAND_BODIES:
        if name in result.positions:
            table.setdefault(band_of(result.positions[name].longitude), []).append(name)
    return table


def trigger_state(result: ChartResult) -> TriggerState:
    table = band_table(result)
    for band, members in table.items():
        if TRIGGER_SET <= set(members):
            giants = [g for g in GIANTS if g in members]
            return TriggerState(
                fired=True, level="catastrophic" if giants else "disruptive",
                band=band, nakshatra=HORARY_NAKSHATRAS_28[band - 1],
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
