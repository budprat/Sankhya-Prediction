# ABOUTME: Period stepping and calendar/JD conversion. Mirrors ASTGRAF's trick of stepping
# ABOUTME: raw calendar fields and letting the Julian-day formula normalize the overflow.

import math

from .ephemeris import BODY_ORDER, compute_raw
from .models import ChartMoment, GridSpec, PeriodRow, PeriodUnit


def jd_value(jdn: float, day_fraction: float) -> float:
    """True Julian date from the suite's noon-based day number and a UT day fraction."""
    return jdn + day_fraction - 0.5


def jd_to_calendar(jdn: float) -> tuple[int, int, int]:
    """Inverse of julian_day_number (Fliegel-Van Flandern, Gregorian/Julian switch)."""
    j = math.floor(jdn)
    if j >= 2299161:
        a = j + 32044
        b = (4 * a + 3) // 146097
        c = a - 146097 * b // 4
    else:
        b = 0
        c = j + 32082
    d = (4 * c + 3) // 1461
    e = c - 1461 * d // 4
    m = (5 * e + 2) // 153
    day = e - (153 * m + 2) // 5 + 1
    month = m + 3 - 12 * (m // 10)
    year = 100 * b + d - 4800 + m // 10
    return year, month, day


def label_for_jd(jd: float) -> str:
    jdn = math.floor(jd + 0.5)
    year, month, day = jd_to_calendar(jdn)
    frac = jd + 0.5 - jdn
    minutes = round(frac * 24 * 60)
    hour, minute = divmod(minutes, 60)
    if hour == 24:  # rounding across midnight
        hour = 0
        year, month, day = jd_to_calendar(jdn + 1)
    return f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d} UT"


def build_rows(start: ChartMoment, spec: GridSpec) -> list[PeriodRow]:
    year, month = start.year, start.month
    day: float = start.day
    hours = start.local_decimal_hours
    rows: list[PeriodRow] = []
    for index in range(spec.count):
        result = compute_raw(year, month, day, hours,
                             start.engine_gmt_hours, start.engine_longitude,
                             start.latitude_north, start.sidereal, start.equal_houses,
                             start.ayanamsa_rate_arcsec, start.ayanamsa_zero_year)
        rows.append(PeriodRow(
            index=index, label=label_for_jd(result.jd), jd=result.jd,
            positions=[result.positions[name] for name in BODY_ORDER]))
        if spec.unit is PeriodUnit.YEAR:
            year += int(spec.step)
        elif spec.unit is PeriodUnit.MONTH:
            month += int(spec.step)
        elif spec.unit is PeriodUnit.DAY:
            day += spec.step
        else:
            hours += spec.step
    return rows


def make_chart_at_jd(start: ChartMoment):
    """Continuous full-chart function over JD (locator, refinement)."""
    def chart(jd: float):
        jdn = math.floor(jd + 0.5)
        year, month, day = jd_to_calendar(jdn)
        ut_hours = (jd + 0.5 - jdn) * 24
        local_hours = ut_hours - start.engine_gmt_hours
        return compute_raw(year, month, day, local_hours,
                           start.engine_gmt_hours, start.engine_longitude,
                           start.latitude_north, start.sidereal, start.equal_houses,
                           start.ayanamsa_rate_arcsec, start.ayanamsa_zero_year)
    return chart


def make_pos_at_jd(start: ChartMoment):
    """Continuous position function over JD, for aspect refinement."""
    chart = make_chart_at_jd(start)

    def pos(jd: float) -> dict[str, float]:
        return {name: p.longitude for name, p in chart(jd).positions.items()}
    return pos
