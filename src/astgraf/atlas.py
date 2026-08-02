# ABOUTME: The deep-time atlas: one SVG timeline of the 25,739-year precession clock,
# ABOUTME: doctrine epochs, and the modern conjunction cycles with their event returns.

from xml.sax.saxutils import escape

from .horary import HORARY_NAKSHATRAS_28
from .precession import DEFAULT_ZERO_YEAR, SECTOR_YEARS, sector_occupancy

# Engine-census results (regenerable: astgraf-bands --rules doctrine-triggers.toml
# over 1600-2030 and the 1900-2026 vyuha census; documented in the ledger).
URA_NEP_CLUSTERS = [(1649, 1652), (1820, 1823), (1991, 1994)]
JUP_SAT_YEARS = [1603, 1623, 1643, 1663, 1682, 1702, 1723, 1742, 1762, 1782,
                 1802, 1821, 1842, 1861, 1881, 1901, 1921, 1940, 1961, 1981,
                 2000, 2020]
EVENT_MARKS = [(1883, "Krakatoa 1883"), (2004, "2004 tsunami"),
               (2016, "Chatur Vyuham 2016")]

DEEP_START, DEEP_END = -46000, 2100
MODERN_START, MODERN_END = 1600, 2100


def _x(year: float, start: float, end: float, left: float, width: float) -> float:
    return left + (year - start) / (end - start) * width


def sector_for_interval_end(end_year: float) -> str:
    """Equinox sector for the passage ENDING at end_year: precession is
    retrograde, so the walk counts sectors BACK from the 1996 Aswini exit
    (consistent with precession.sector_occupancy)."""
    back = round((DEFAULT_ZERO_YEAR - end_year) / SECTOR_YEARS)
    return HORARY_NAKSHATRAS_28[back % 28]


def render_atlas() -> str:
    width, left, panel_w = 1500, 90, 1350
    deep_top, deep_h = 70, 150
    modern_top, modern_h = 320, 170
    height = 560
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
             f'height="{height}" viewBox="0 0 {width} {height}">',
             f'<rect width="{width}" height="{height}" fill="white"/>',
             f'<text x="{left}" y="30" font-size="17" fill="#222">The deep-time atlas '
             '— 25,739-year precession clock and the modern conjunction cycles</text>',
             f'<text x="{left}" y="50" font-size="11" fill="#777">precession layer is '
             'exact by construction (linear clock); planetary layers shown only in the '
             'modern engine-validated window; deep-time planetary positions are '
             'qualitative</text>']

    # ---- Deep panel: equinox sector stripes across ~52 passages.
    parts.append(f'<text x="{left}" y="{deep_top - 8}" font-size="12" fill="#333">'
                 f'{DEEP_START} … {DEEP_END}: equinox sector passages '
                 f'({SECTOR_YEARS:.0f} y each)</text>')
    boundaries = []
    year = DEFAULT_ZERO_YEAR
    while year > DEEP_START - SECTOR_YEARS:
        boundaries.append(year)
        year -= SECTOR_YEARS
    boundaries.reverse()  # ascending years; sector k of each passage
    marker_names = {"Punarvasu", "Magha", "Aswini", "Abhijit"}
    for i in range(len(boundaries) - 1):
        y0, y1 = boundaries[i], boundaries[i + 1]
        name = sector_for_interval_end(y1)
        x0 = _x(y0, DEEP_START, DEEP_END, left, panel_w)
        x1 = _x(y1, DEEP_START, DEEP_END, left, panel_w)
        fill = "#f6e7c8" if name in marker_names else ("#f0f0f0" if i % 2 else "#fafafa")
        parts.append(f'<rect class="sector" x="{x0:.1f}" y="{deep_top}" '
                     f'width="{max(x1 - x0, 0.5):.1f}" height="{deep_h}" fill="{fill}" '
                     f'stroke="#e2e2e2"/>')
        if name in marker_names:
            parts.append(f'<text x="{(x0 + x1) / 2:.1f}" y="{deep_top + 14}" '
                         f'font-size="8" fill="#7a5a10" text-anchor="middle" '
                         f'transform="rotate(-90 {(x0 + x1) / 2:.1f} {deep_top + 26})">'
                         f'{escape(name)}</text>')
    epochs = [(-30178, "Punarvasu zero (2 cycles)"), (-4439, "Punarvasu zero"),
              (158, "Kritika passage 158 CE"), (1996, "Aswini zero 1996")]
    magha = sector_occupancy("Magha")
    parts.append(f'<rect x="{_x(magha[0], DEEP_START, DEEP_END, left, panel_w):.1f}" '
                 f'y="{deep_top}" width="{_x(magha[1], DEEP_START, DEEP_END, left, panel_w) - _x(magha[0], DEEP_START, DEEP_END, left, panel_w):.1f}" '
                 f'height="{deep_h}" fill="#cfe3ff" opacity="0.8"/>')
    parts.append(f'<text x="{_x(magha[0], DEEP_START, DEEP_END, left, panel_w):.1f}" '
                 f'y="{deep_top + deep_h + 16}" font-size="11" fill="#1c4d8f">'
                 'Magha flood epoch</text>')
    for year, label in epochs:
        x = _x(year, DEEP_START, DEEP_END, left, panel_w)
        parts.append(f'<line x1="{x:.1f}" y1="{deep_top}" x2="{x:.1f}" '
                     f'y2="{deep_top + deep_h}" stroke="#a33" stroke-width="1.5"/>')
        parts.append(f'<text x="{x + 4:.1f}" y="{deep_top + 34}" font-size="10" '
                     f'fill="#a33" transform="rotate(-60 {x + 4:.1f} {deep_top + 34})">'
                     f'{escape(label)}</text>')

    # ---- Modern panel: conjunction cycles + event returns.
    parts.append(f'<text x="{left}" y="{modern_top - 10}" font-size="12" fill="#333">'
                 f'{MODERN_START} … {MODERN_END}: Jupiter–Saturn (~20 y ticks) and '
                 'Uranus–Neptune (~171 y synodic clusters, engine census)</text>')
    parts.append(f'<rect x="{left}" y="{modern_top}" width="{panel_w}" '
                 f'height="{modern_h}" fill="none" stroke="#999"/>')
    for year in range(MODERN_START, MODERN_END + 1, 50):
        x = _x(year, MODERN_START, MODERN_END, left, panel_w)
        parts.append(f'<text x="{x:.1f}" y="{modern_top + modern_h + 18}" '
                     f'font-size="10" fill="#555" text-anchor="middle">{year}</text>')
    for year in JUP_SAT_YEARS:
        x = _x(year, MODERN_START, MODERN_END, left, panel_w)
        parts.append(f'<line x1="{x:.1f}" y1="{modern_top + 95}" x2="{x:.1f}" '
                     f'y2="{modern_top + 130}" stroke="#2e7d32" stroke-width="1.5"/>')
    parts.append(f'<text x="{left + 6}" y="{modern_top + 126}" font-size="10" '
                 'fill="#2e7d32">Jup–Sat conjunctions</text>')
    for y0, y1 in URA_NEP_CLUSTERS:
        x0 = _x(y0 - 1, MODERN_START, MODERN_END, left, panel_w)
        x1 = _x(y1 + 1, MODERN_START, MODERN_END, left, panel_w)
        parts.append(f'<rect x="{x0:.1f}" y="{modern_top + 20}" '
                     f'width="{x1 - x0:.1f}" height="45" fill="#5555dd" opacity="0.65"/>')
    parts.append(f'<text x="{_x(1991, MODERN_START, MODERN_END, left, panel_w):.1f}" '
                 f'y="{modern_top + 14}" font-size="10" fill="#3333aa" '
                 'text-anchor="middle">Ura-Nep 1991-94</text>')
    x_edge = _x(2100, MODERN_START, MODERN_END, left, panel_w)
    parts.append(f'<text x="{x_edge - 4:.1f}" y="{modern_top + 40}" font-size="10" '
                 'fill="#3333aa" text-anchor="end">next ~2165 →</text>')
    for year, label in EVENT_MARKS:
        x = _x(year, MODERN_START, MODERN_END, left, panel_w)
        parts.append(f'<circle cx="{x:.1f}" cy="{modern_top + 80}" r="4" fill="#a33"/>')
        parts.append(f'<text x="{x:.1f}" y="{modern_top + 70}" font-size="10" '
                     f'fill="#a33" text-anchor="middle">{escape(label)}</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def main(argv: list[str] | None = None) -> int:
    import argparse
    p = argparse.ArgumentParser(prog="astgraf-atlas", description="deep-time atlas SVG")
    p.add_argument("--out", default="out/atlas.svg")
    args = p.parse_args(argv)
    from pathlib import Path
    path = Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_atlas())
    print(f"astgraf-atlas -> {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
