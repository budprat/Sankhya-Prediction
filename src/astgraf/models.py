# ABOUTME: Typed models and input parsing. Modern conventions at the boundary (east-positive
# ABOUTME: longitude, UTC offsets) with explicit conversion to the BASIC engine's east-negative core.

import re
from enum import Enum

from pydantic import BaseModel, Field, model_validator


def _parse_dm(text: str, positive: str, negative: str) -> float:
    """Parse 'DD:MM<E|W|N|S>' or a signed decimal into signed decimal degrees."""
    text = text.strip()
    match = re.fullmatch(rf"(\d+):(\d+)([{positive}{negative}])", text, re.IGNORECASE)
    if match:
        degrees = int(match.group(1)) + int(match.group(2)) / 60
        return degrees if match.group(3).upper() == positive else -degrees
    return float(text)


def parse_longitude(text: str) -> float:
    """East-positive decimal degrees from '76:57E', '76:57W', or a decimal string."""
    return _parse_dm(text, "E", "W")


def parse_latitude(text: str) -> float:
    """North-positive decimal degrees from '28:48N', '10:30S', or a decimal string."""
    return _parse_dm(text, "N", "S")


def parse_utc_offset(text: str) -> float:
    """Decimal hours from '+05:30', '-08:00', '5:30', or a decimal string."""
    text = text.strip()
    match = re.fullmatch(r"([+-]?)(\d+):(\d+)", text)
    if match:
        hours = int(match.group(2)) + int(match.group(3)) / 60
        return -hours if match.group(1) == "-" else hours
    return float(text)


class PeriodUnit(str, Enum):
    YEAR = "year"
    MONTH = "month"
    DAY = "day"
    HOUR = "hour"


class ChartMoment(BaseModel):
    """One chart instant plus site, in modern conventions."""
    year: int
    month: int = Field(ge=1, le=12)
    day: int = Field(ge=1, le=31)
    hour: int = Field(ge=0, le=23)
    minute: int = Field(ge=0, le=59)
    utc_offset_hours: float = Field(ge=-14, le=14)
    longitude_east: float = Field(ge=-180, le=180)
    latitude_north: float = Field(ge=-90, le=90)
    sidereal: bool = True
    equal_houses: bool = True
    # Ayanamsa override: None keeps the suite formula (151/10800 deg/yr, zero 294 CE).
    # NU's alternative reckoning is 50.35 arcsec/yr from the Aswini zero.
    ayanamsa_rate_arcsec: float | None = None
    ayanamsa_zero_year: int = 294

    @property
    def local_decimal_hours(self) -> float:
        return self.hour + self.minute / 60

    @property
    def engine_gmt_hours(self) -> float:
        """The BASIC suite treats east as negative; UTC+5:30 becomes -5.5."""
        return -self.utc_offset_hours

    @property
    def engine_longitude(self) -> float:
        """East-negative degrees, the suite's convention."""
        return -self.longitude_east


class GridSpec(BaseModel):
    unit: PeriodUnit
    step: float = Field(gt=0)
    count: int = Field(ge=1, le=2000)

    @model_validator(mode="after")
    def _year_month_steps_are_whole(self):
        # Calendar arithmetic (the JD-normalization trick) needs whole year/month steps.
        if self.unit in (PeriodUnit.YEAR, PeriodUnit.MONTH) and self.step != int(self.step):
            raise ValueError("year/month steps must be whole numbers")
        return self


class BodyPosition(BaseModel):
    name: str
    longitude: float
    retrograde: bool
    # Ecliptic latitude in degrees (planets only; 0 for Sun/Moon/nodes/Ascendant,
    # which the BASIC suite never computes it for). Used by the event-locator.
    ecliptic_latitude: float = 0.0
    # Geocentric distance in the engine's scaled units (ratios are meaningful,
    # absolute values are not — the suite scales AU by pi/180). 0 when undefined.
    distance: float = 0.0


class PeriodRow(BaseModel):
    index: int
    label: str
    jd: float
    positions: list[BodyPosition]

    def longitude_of(self, body: str) -> float:
        for position in self.positions:
            if position.name == body:
                return position.longitude
        raise KeyError(body)


class ChartResult(BaseModel):
    positions: dict[str, BodyPosition]
    ayanamsa: float
    jd: float
    gmst: float = 0.0        # Greenwich mean sidereal time, degrees
    obliquity: float = 0.0   # real obliquity at the instant, degrees


class AspectEvent(BaseModel):
    body_a: str
    body_b: str
    kind: str
    jd: float
    label: str = ""
