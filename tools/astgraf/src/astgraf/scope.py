# ABOUTME: The scope chart: a traditional wheel with conjunction/square/trine/opposition
# ABOUTME: lines drawn between bodies within orb — NU's "real guides" made visible.

import math
from xml.sax.saxutils import escape

from .aspects import ASPECT_ANGLES, signed_separation
from .svgplot import PALETTE, SIGNS

SIZE = 800
CX = CY = SIZE / 2
R_OUTER = 340.0
R_SIGN_LABEL = 318.0
R_SIGN_INNER = 296.0
R_BODY = 268.0
R_ASPECT = 248.0

ASPECT_COLORS = {"conjunction": "#666666", "square": "#cc3333",
                 "trine": "#2e7d32", "opposition": "#772222"}


def wheel_xy(longitude: float, radius: float, cx: float = CX, cy: float = CY) -> tuple[float, float]:
    """0 deg Aries at 9 o'clock, longitudes counterclockwise (traditional wheel)."""
    phi = math.radians(180.0 + longitude)
    return cx + radius * math.cos(phi), cy - radius * math.sin(phi)


def aspects_in_orb(positions: dict[str, float], orb: float) -> list[tuple[str, str, str, float]]:
    """(body_a, body_b, kind, separation) for every pair within orb of an aspect angle."""
    names = list(positions)
    found = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            sep = abs(signed_separation(positions[b], positions[a]))
            for kind, angle in ASPECT_ANGLES.items():
                if abs(sep - angle) <= orb:
                    found.append((a, b, kind, sep))
    return found


def render_scope(positions: dict[str, float], title: str = "", orb: float = 3.0,
                 galactic_axes: tuple[float, float] | None = None) -> str:
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{SIZE}" height="{SIZE}" '
             f'viewBox="0 0 {SIZE} {SIZE}">',
             f'<rect width="{SIZE}" height="{SIZE}" fill="white"/>',
             f'<text x="{CX}" y="26" font-size="15" fill="#222" text-anchor="middle">'
             f'{escape(title or "scope chart")}</text>',
             f'<circle cx="{CX}" cy="{CY}" r="{R_OUTER}" fill="none" stroke="#333"/>',
             f'<circle cx="{CX}" cy="{CY}" r="{R_SIGN_INNER}" fill="none" stroke="#999"/>']
    if galactic_axes is not None:
        # The author's galactic reference: Punarvasu crossover (a direction)
        # and the Magha axis (both ends), dashed under everything else.
        cross, magha = galactic_axes
        for name, lon, both_ends in (("crossover", cross, False),
                                     ("magha", magha, True)):
            ends = (lon, lon + 180) if both_ends else (lon,)
            for end in ends:
                x, y = wheel_xy(end, R_OUTER)
                parts.append(f'<line data-galactic="{name}" x1="{CX}" y1="{CY}" '
                             f'x2="{x:.1f}" y2="{y:.1f}" stroke="#8855aa" '
                             f'stroke-width="1.2" stroke-dasharray="6 4"/>')
            lx, ly = wheel_xy(ends[0], R_OUTER + 14)
            label = "Punarvasu X" if name == "crossover" else "Magha axis"
            parts.append(f'<text x="{lx:.1f}" y="{ly:.1f}" font-size="10" '
                         f'fill="#8855aa" text-anchor="middle">{label}</text>')
    for k in range(12):
        x1, y1 = wheel_xy(k * 30.0, R_SIGN_INNER)
        x2, y2 = wheel_xy(k * 30.0, R_OUTER)
        parts.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                     'stroke="#999"/>')
        lx, ly = wheel_xy(k * 30.0 + 15.0, R_SIGN_LABEL)
        parts.append(f'<text x="{lx:.1f}" y="{ly:.1f}" font-size="13" fill="#555" '
                     f'text-anchor="middle" dominant-baseline="middle">{SIGNS[k]}</text>')

    aspects = aspects_in_orb(positions, orb)
    for a, b, kind, _sep in aspects:
        x1, y1 = wheel_xy(positions[a], R_ASPECT)
        x2, y2 = wheel_xy(positions[b], R_ASPECT)
        parts.append(f'<line class="aspect-line {kind}" x1="{x1:.1f}" y1="{y1:.1f}" '
                     f'x2="{x2:.1f}" y2="{y2:.1f}" '
                     f'stroke="{ASPECT_COLORS[kind]}" stroke-width="1.6"/>')

    # Bodies, with labels staggered when neighbors crowd within 6 degrees.
    ordered = sorted(positions.items(), key=lambda kv: kv[1])
    staggers = []
    stagger = 0
    prev_lon = None
    for _, lon in ordered:
        if prev_lon is not None and (lon - prev_lon) % 360 < 6:
            stagger = (stagger + 1) % 3
        else:
            stagger = 0
        staggers.append(stagger)
        prev_lon = lon
    # Wrap seam (audit finding 43): bodies straddling 0 Aries crowd too — if
    # the first shares the last one's stagger, re-walk the leading crowd.
    if (len(ordered) > 1 and (ordered[0][1] - ordered[-1][1]) % 360 < 6
            and staggers[0] == staggers[-1]):
        stagger = staggers[-1]
        prev_lon = ordered[-1][1] - 360
        for i, (_, lon) in enumerate(ordered):
            if (lon - prev_lon) % 360 >= 6:
                break
            stagger = (stagger + 1) % 3
            staggers[i] = stagger
            prev_lon = lon
    for (name, lon), stagger in zip(ordered, staggers):
        color = PALETTE.get(name, "#000")
        bx, by = wheel_xy(lon, R_BODY)
        lx, ly = wheel_xy(lon, R_BODY - 26 - 20 * stagger)
        parts.append(f'<circle data-body="{escape(name)}" cx="{bx:.1f}" cy="{by:.1f}" '
                     f'r="5" fill="{color}"/>')
        parts.append(f'<text x="{lx:.1f}" y="{ly:.1f}" font-size="11" fill="{color}" '
                     f'text-anchor="middle" dominant-baseline="middle">'
                     f'{escape(name[:3])}</text>')

    # Exact-aspect legend, bottom-left.
    y = SIZE - 16 - 15 * (len(aspects) - 1) if aspects else SIZE - 16
    for a, b, kind, sep in aspects:
        parts.append(f'<text x="14" y="{y}" font-size="12" '
                     f'fill="{ASPECT_COLORS[kind]}">'
                     f'{escape(f"{a} {kind} {b}")} ({sep:.2f}°)</text>')
        y += 15
    parts.append("</svg>")
    return "\n".join(parts)
