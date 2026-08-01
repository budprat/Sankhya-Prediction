# ABOUTME: SVG renderer replacing GRAPHDO's SCREEN 12 plot: wrapped-longitude view (default,
# ABOUTME: unambiguous) plus the heritage cosine fold, cumulative one-by-one sequence, aspects.

import math
from xml.sax.saxutils import escape

from .models import AspectEvent, PeriodRow

WIDTH, HEIGHT = 1200, 700
LEFT, RIGHT, TOP, BOTTOM = 70, 160, 50, 60
PLOT_W = WIDTH - LEFT - RIGHT
PLOT_H = HEIGHT - TOP - BOTTOM

# GRAPHDO's VGA palette, mapped to hex and adjusted for a white background.
PALETTE = {
    "Ascendant": "#0000AA", "Sun": "#00AA00", "Moon": "#00AAAA", "Mars": "#AA0000",
    "Mercury": "#AA00AA", "Jupiter": "#C8A200", "Venus": "#FF5555", "Saturn": "#444444",
    "Rahu": "#777777", "Ketu": "#555555", "Uranus": "#5555FF", "Neptune": "#55AA55",
    "Pluto": "#00AACC",
}

SIGNS = ["Ari", "Tau", "Gem", "Can", "Leo", "Vir",
         "Lib", "Sco", "Sag", "Cap", "Aqu", "Pis"]

GLYPHS = {"conjunction": "☌", "square": "□",
          "trine": "△", "opposition": "☍"}


def wrapped_y(lon: float, top: float = float(TOP), height: float = float(PLOT_H)) -> float:
    """0/360 deg at the bottom, 360 at the top; SVG y grows downward."""
    return top + (360.0 - (lon % 360.0)) / 360.0 * height


def cosine_y(lon: float, top: float = float(TOP), height: float = float(PLOT_H)) -> float:
    """The heritage GRAPHDO fold: y from cos(longitude); 0/360 bottom, 180 top."""
    return top + (1 + math.cos(math.radians(lon))) / 2 * height


def _x_for(jd: float, jd0: float, jd1: float) -> float:
    if jd1 == jd0:
        return LEFT + PLOT_W / 2
    return LEFT + (jd - jd0) / (jd1 - jd0) * PLOT_W


def _axis(style: str) -> list[str]:
    parts = [f'<rect x="{LEFT}" y="{TOP}" width="{PLOT_W}" height="{PLOT_H}" '
             'fill="none" stroke="#999"/>']
    if style == "wrapped":
        for k in range(13):
            deg = k * 30
            y = TOP + PLOT_H - deg / 360 * PLOT_H
            parts.append(f'<line x1="{LEFT}" y1="{y:.1f}" x2="{LEFT + PLOT_W}" '
                         f'y2="{y:.1f}" stroke="#ddd"/>')
            parts.append(f'<text x="{LEFT - 8}" y="{y + 4:.1f}" text-anchor="end" '
                         f'font-size="10" fill="#555">{deg}</text>')
        for k, sign in enumerate(SIGNS):
            y = TOP + PLOT_H - (k * 30 + 15) / 360 * PLOT_H
            parts.append(f'<text x="{LEFT + 4}" y="{y + 3:.1f}" font-size="9" '
                         f'fill="#aaa">{sign}</text>')
    else:
        for deg, label in ((0, "0/360"), (90, "90/270"), (180, "180")):
            y = cosine_y(deg)
            parts.append(f'<line x1="{LEFT}" y1="{y:.1f}" x2="{LEFT + PLOT_W}" '
                         f'y2="{y:.1f}" stroke="#ddd"/>')
            parts.append(f'<text x="{LEFT - 8}" y="{y + 4:.1f}" text-anchor="end" '
                         f'font-size="10" fill="#555">{label}</text>')
    return parts


def _body_elements(rows: list[PeriodRow], body: str, style: str,
                   jd0: float, jd1: float) -> list[str]:
    color = PALETTE.get(body, "#000")
    points = [(r.jd, r.longitude_of(body),
               next(p.retrograde for p in r.positions if p.name == body)) for r in rows]
    parts: list[str] = []
    segment: list[str] = []
    prev_lon: float | None = None

    def flush():
        if len(segment) >= 2:
            parts.append(f'<polyline data-body="{escape(body)}" fill="none" '
                         f'stroke="{color}" stroke-width="1.6" '
                         f'points="{" ".join(segment)}"/>')
        segment.clear()

    for jd, lon, retro in points:
        y = wrapped_y(lon) if style == "wrapped" else cosine_y(lon)
        if style == "wrapped" and prev_lon is not None and abs(lon - prev_lon) > 180:
            flush()
        segment.append(f"{_x_for(jd, jd0, jd1):.1f},{y:.1f}")
        prev_lon = lon
        if retro:
            parts.append(f'<circle class="retro" cx="{_x_for(jd, jd0, jd1):.1f}" '
                         f'cy="{y:.1f}" r="3" fill="none" stroke="{color}"/>')
    flush()
    return parts


def _event_elements(events: list[AspectEvent], style: str,
                    jd0: float, jd1: float) -> list[str]:
    parts = []
    for e in events:
        if not jd0 <= e.jd <= jd1:
            continue
        x = _x_for(e.jd, jd0, jd1)
        glyph = GLYPHS.get(e.kind, "?")
        text = escape(f"{glyph} {e.body_a}-{e.body_b}")
        parts.append(
            f'<g class="aspect-marker"><line x1="{x:.1f}" y1="{TOP}" x2="{x:.1f}" '
            f'y2="{TOP + PLOT_H}" stroke="#c66" stroke-dasharray="4 4" opacity="0.5"/>'
            f'<text x="{x:.1f}" y="{TOP - 6}" font-size="9" fill="#c66" '
            f'text-anchor="middle">{text}</text></g>')
    return parts


def render(rows: list[PeriodRow], bodies: list[str], style: str = "wrapped",
           events: list[AspectEvent] | None = None, title: str = "") -> str:
    jd0, jd1 = rows[0].jd, rows[-1].jd
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" '
             f'height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">',
             f'<rect width="{WIDTH}" height="{HEIGHT}" fill="white"/>',
             f'<text x="{LEFT}" y="24" font-size="15" fill="#222">'
             f'{escape(title or "astgraf stellar positions")}</text>']
    parts += _axis(style)
    for body in bodies:
        parts += _body_elements(rows, body, style, jd0, jd1)
    if events:
        parts += _event_elements(events, style, jd0, jd1)
    # X tick labels (at most 8) and the right-hand legend.
    ticks = rows if len(rows) <= 8 else [rows[i] for i in
                                         range(0, len(rows), max(1, len(rows) // 8))]
    for r in ticks:
        x = _x_for(r.jd, jd0, jd1)
        parts.append(f'<text x="{x:.1f}" y="{TOP + PLOT_H + 16}" font-size="9" '
                     f'fill="#555" text-anchor="middle">{escape(r.label)}</text>')
    for i, body in enumerate(bodies):
        y = TOP + 14 * i
        color = PALETTE.get(body, "#000")
        parts.append(f'<rect x="{LEFT + PLOT_W + 14}" y="{y - 8}" width="10" '
                     f'height="10" fill="{color}"/>')
        parts.append(f'<text x="{LEFT + PLOT_W + 30}" y="{y}" font-size="11" '
                     f'fill="#222">{escape(body)}</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def render_sequence(rows: list[PeriodRow], bodies: list[str], style: str = "wrapped",
                    events: list[AspectEvent] | None = None) -> list[tuple[str, str]]:
    """One-by-one reveal: the k-th document draws the first k bodies cumulatively."""
    out = []
    for k in range(1, len(bodies) + 1):
        shown = bodies[:k]
        title = f"astgraf — {', '.join(shown)}"
        svg = render(rows, shown, style=style,
                     events=events if k == len(bodies) else None, title=title)
        out.append((f"step_{k:02d}_{bodies[k - 1]}", svg))
    return out
