# ABOUTME: The 25,739-year precession clock from Secrets of Sankhya: equinox drift at
# ABOUTME: 50.352"/yr over the 28-sector wheel, sector occupancy epochs, and a wheel SVG.

# Doctrine (NU, Secrets of Sankhya ch.1): drift 1/(70.47 x 365.25) = 1/25739 of a cycle
# per year (= 50.35"/yr); 25739/28 = 919.25 years per nakshatra passage; the book's own
# arithmetic (written ~1996) puts the equinox at wheel zero (Aswini start) in its current
# period — Kritika 2 sectors back (~158 CE), Punarvasu 7 back (~4438 BC), Magha 10 back
# (the flood epoch), two-cycle Punarvasu zero ~30,170 BC. Anchor is overridable.
import math
from xml.sax.saxutils import escape

from pydantic import BaseModel

from .horary import HORARY_NAKSHATRAS_28
from .scope import wheel_xy

CYCLE_YEARS = 25739
SECTORS = 28
SECTOR_YEARS = CYCLE_YEARS / SECTORS
SECTOR_SPAN = 360.0 / SECTORS
RATE_DEG_PER_YEAR = 360.0 / CYCLE_YEARS
RATE_ARCSEC_PER_YEAR = RATE_DEG_PER_YEAR * 3600

DEFAULT_ZERO_YEAR = 1996.0

MARKER_SECTORS = {"Punarvasu": "doctrinal starting point (zero azimuth & ecliptic)",
                  "Abhijit": "opposition marker (Vega), spread now < 1 deg",
                  "Magha": "flood-epoch marker (galactic axis)"}


class EquinoxSector(BaseModel):
    year: float
    longitude: float
    sector: int            # 1..28
    nakshatra: str
    entered_year: float    # equinox crossed the sector's upper boundary (retrograde)
    exits_year: float      # equinox reaches the sector's lower boundary


def equinox_longitude(year: float, zero_year: float = DEFAULT_ZERO_YEAR,
                      zero_longitude: float = 0.0) -> float:
    """Equinox position on the fixed 28-sector wheel; precession is retrograde."""
    return (zero_longitude - (year - zero_year) * RATE_DEG_PER_YEAR) % 360.0


def sector_of(year: float, zero_year: float = DEFAULT_ZERO_YEAR,
              zero_longitude: float = 0.0) -> EquinoxSector:
    lon = equinox_longitude(year, zero_year, zero_longitude)
    index = int(lon // SECTOR_SPAN)
    upper = (index + 1) * SECTOR_SPAN
    lower = index * SECTOR_SPAN
    return EquinoxSector(
        year=year, longitude=lon, sector=index + 1,
        nakshatra=HORARY_NAKSHATRAS_28[index],
        entered_year=year - (upper - lon) / RATE_DEG_PER_YEAR,
        exits_year=year + (lon - lower) / RATE_DEG_PER_YEAR)


def sector_occupancy(nakshatra: str, cycles_back: int = 0,
                     zero_year: float = DEFAULT_ZERO_YEAR,
                     zero_longitude: float = 0.0) -> tuple[float, float]:
    """(entry_year, exit_year) of the most recent occupancy at or before the anchor."""
    index = HORARY_NAKSHATRAS_28.index(nakshatra)
    upper = (index + 1) * SECTOR_SPAN
    lower = index * SECTOR_SPAN
    exit_year = zero_year - ((lower - zero_longitude) % 360.0) / RATE_DEG_PER_YEAR
    entry_year = exit_year - (upper - lower) / RATE_DEG_PER_YEAR
    return entry_year - cycles_back * CYCLE_YEARS, exit_year - cycles_back * CYCLE_YEARS


def report_lines(year: float, zero_year: float = DEFAULT_ZERO_YEAR,
                 zero_longitude: float = 0.0) -> list[str]:
    s = sector_of(year, zero_year, zero_longitude)
    punarvasu2 = sector_occupancy("Punarvasu", 1, zero_year, zero_longitude)[0]
    lines = [
        f"Precession clock — cycle {CYCLE_YEARS} y, {RATE_ARCSEC_PER_YEAR:.3f}\"/yr, "
        f"{SECTOR_YEARS:.2f} y/sector; anchor: equinox at {zero_longitude:.3f} deg "
        f"in {zero_year:.0f}",
        f"  year {year:.0f}: equinox at {s.longitude:.4f} deg — {s.nakshatra} "
        f"(sector {s.sector}), entered {s.entered_year:.0f}, exits {s.exits_year:.0f}",
        f"  Punarvasu zero (two cycles back): {punarvasu2:.0f} "
        f"({year - punarvasu2:.0f} years before {year:.0f})",
    ]
    for name, note in MARKER_SECTORS.items():
        entry, exit_ = sector_occupancy(name, 0, zero_year, zero_longitude)
        lines.append(f"  {name}: last occupied {entry:.0f} to {exit_:.0f} — {note}")
    return lines


def render_precession_wheel(year: float, zero_year: float = DEFAULT_ZERO_YEAR,
                            zero_longitude: float = 0.0) -> str:
    size = 800
    cx = cy = size / 2
    r_outer, r_label, r_inner = 340.0, 314.0, 288.0
    s = sector_of(year, zero_year, zero_longitude)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
             f'viewBox="0 0 {size} {size}">',
             f'<rect width="{size}" height="{size}" fill="white"/>',
             f'<text x="{cx}" y="26" font-size="15" fill="#222" text-anchor="middle">'
             f'{escape(f"Precession clock — year {year:.0f}: equinox in {s.nakshatra}")}'
             '</text>',
             f'<circle cx="{cx}" cy="{cy}" r="{r_outer}" fill="none" stroke="#333"/>',
             f'<circle cx="{cx}" cy="{cy}" r="{r_inner}" fill="none" stroke="#999"/>']
    for k in range(SECTORS):
        x1, y1 = wheel_xy(k * SECTOR_SPAN, r_inner, cx, cy)
        x2, y2 = wheel_xy(k * SECTOR_SPAN, r_outer, cx, cy)
        parts.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                     'stroke="#bbb"/>')
        name = HORARY_NAKSHATRAS_28[k]
        mid = k * SECTOR_SPAN + SECTOR_SPAN / 2
        lx, ly = wheel_xy(mid, r_label, cx, cy)
        color = "#a05a00" if name in MARKER_SECTORS else "#666"
        angle = math.degrees(math.atan2(cy - ly, lx - cx))
        parts.append(f'<text x="{lx:.1f}" y="{ly:.1f}" font-size="9" fill="{color}" '
                     f'text-anchor="middle" dominant-baseline="middle" '
                     f'transform="rotate({-angle + 90:.1f} {lx:.1f} {ly:.1f})">'
                     f'{escape(name)}</text>')
    for name in MARKER_SECTORS:
        k = HORARY_NAKSHATRAS_28.index(name)
        mx, my = wheel_xy(k * SECTOR_SPAN + SECTOR_SPAN / 2, r_inner - 16, cx, cy)
        parts.append(f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="4" fill="#a05a00"/>')
    nx, ny = wheel_xy(s.longitude, r_inner, cx, cy)
    parts.append(f'<line class="equinox-needle" x1="{cx}" y1="{cy}" x2="{nx:.1f}" '
                 f'y2="{ny:.1f}" stroke="#c00" stroke-width="2.5"/>')
    parts.append(f'<text x="{cx}" y="{size - 14}" font-size="12" fill="#444" '
                 f'text-anchor="middle">{escape(f"equinox {s.longitude:.4f} deg — entered {s.entered_year:.0f}, exits {s.exits_year:.0f}")}</text>')
    parts.append("</svg>")
    return "\n".join(parts)
