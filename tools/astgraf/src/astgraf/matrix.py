# ABOUTME: The Predict.pdf 28x11 matrix as an event-synchronisation library: per-cell
# ABOUTME: event rates vs controls from signature CSVs, rendered as a heatmap SVG.

import csv
import math
from pathlib import Path
from xml.sax.saxutils import escape

from .bands import BAND_BODIES
from .horary import HORARY_NAKSHATRAS_28


def build_matrix(events: list[dict], controls: list[dict]) -> list[dict]:
    rows = []
    for body in BAND_BODIES:
        key = f"band:{body}"
        ev = [int(float(s[key])) for s in events if s.get(key) not in (None, "")]
        ct = [int(float(s[key])) for s in controls if s.get(key) not in (None, "")]
        for band in range(1, 29):
            ec, cc = ev.count(band), ct.count(band)
            er = ec / len(ev) if ev else 0.0
            cr = cc / len(ct) if ct else 0.0
            lift = (er / cr) if cr > 0 else (math.inf if er > 0 else 1.0)
            rows.append({"body": body, "band": band,
                         "nakshatra": HORARY_NAKSHATRAS_28[band - 1],
                         "event_count": ec, "event_rate": round(er, 4),
                         "control_rate": round(cr, 4),
                         "lift": round(lift, 3) if lift != math.inf else lift})
    return rows


def _cell_color(lift: float, event_count: int) -> str:
    if event_count == 0:
        return "#f4f4f4"
    if lift == math.inf:
        return "#7a0d0d"
    clamped = max(0.5, min(2.0, lift))
    if clamped >= 1.0:
        t = (clamped - 1.0) / 1.0        # 1..2 -> red
        return f"#{int(255 - 100 * t):02x}{int(235 - 180 * t):02x}{int(230 - 190 * t):02x}"
    t = (1.0 - clamped) / 0.5            # 1..0.5 -> blue
    return f"#{int(235 - 180 * t):02x}{int(240 - 140 * t):02x}{int(255 - 60 * t):02x}"


def render_matrix_svg(rows: list[dict], title: str = "") -> str:
    cell_w, cell_h = 74, 22
    left, top = 120, 90
    width = left + cell_w * len(BAND_BODIES) + 40
    height = top + cell_h * 28 + 60
    by_key = {(r["body"], r["band"]): r for r in rows}
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
             f'height="{height}" viewBox="0 0 {width} {height}">',
             f'<rect width="{width}" height="{height}" fill="white"/>',
             f'<text x="{left}" y="28" font-size="16" fill="#222">'
             f'{escape(title or "28 x 11 event-synchronisation matrix (events vs controls)")}</text>',
             f'<text x="{left}" y="48" font-size="11" fill="#777">red = band '
             'occupied at events above chance, blue = below; count shown per cell; '
             'outer-planet columns are baseline-confounded (slow bands)</text>']
    for j, body in enumerate(BAND_BODIES):
        parts.append(f'<text x="{left + j * cell_w + cell_w / 2}" y="{top - 8}" '
                     f'font-size="11" fill="#333" text-anchor="middle">{escape(body)}</text>')
    for i, name in enumerate(HORARY_NAKSHATRAS_28):
        y = top + i * cell_h
        parts.append(f'<text x="{left - 8}" y="{y + cell_h - 7}" font-size="10" '
                     f'fill="#333" text-anchor="end">{i + 1} {escape(name)}</text>')
        for j, body in enumerate(BAND_BODIES):
            r = by_key[(body, i + 1)]
            x = left + j * cell_w
            parts.append(f'<rect class="cell" x="{x}" y="{y}" width="{cell_w - 2}" '
                         f'height="{cell_h - 2}" fill="{_cell_color(r["lift"], r["event_count"])}" '
                         f'stroke="#ddd"/>')
            if r["event_count"]:
                parts.append(f'<text x="{x + cell_w / 2 - 1}" y="{y + cell_h - 7}" '
                             f'font-size="10" fill="#222" text-anchor="middle">'
                             f'{r["event_count"]}</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def main(argv: list[str] | None = None) -> int:
    import argparse
    p = argparse.ArgumentParser(prog="astgraf-matrix",
                                description="28x11 event-synchronisation matrix")
    p.add_argument("--signatures", required=True,
                   help="directory with signatures.csv and controls.csv")
    p.add_argument("--out", default="matrix-out")
    args = p.parse_args(argv)
    src = Path(args.signatures)
    events = list(csv.DictReader(open(src / "signatures.csv")))
    controls = list(csv.DictReader(open(src / "controls.csv")))
    rows = build_matrix(events, controls)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "matrix.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (out / "matrix.svg").write_text(render_matrix_svg(
        rows, title=f"28 x 11 matrix — {len(events)} events vs {len(controls)} controls"))

    scored = [r for r in rows if r["event_count"] >= 8 and r["lift"] != math.inf
              and r["control_rate"] > 0]
    scored.sort(key=lambda r: -abs(math.log(r["lift"])) if r["lift"] > 0 else 0)
    print(f"astgraf-matrix: {len(events)} events, {len(controls)} controls -> "
          f"{out / 'matrix.svg'}")
    print("  strongest cells (>=8 events; inner bodies most meaningful):")
    for r in scored[:10]:
        print(f"    {r['body']:8s} band {r['band']:2d} {r['nakshatra']:12s} "
              f"events {r['event_count']:3d}  lift {r['lift']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
