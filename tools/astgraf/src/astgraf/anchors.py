# ABOUTME: The anchor library (NU's recurrence principle): dossiers of past major events —
# ABOUTME: every fired contact with its trigger instant refined to the minute, plus the site timetable.

import argparse
import functools
import json
import math
import tomllib
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from .bands import BAND_BODIES, circular_spread, division_of, real_longitude, vyuha_state
from .ephemeris import compute_raw, julian_day_number
from .grid import jd_to_calendar
from .signatures import ASPECT_ORB, ASPECTS

ANCHORS_PATH = str(Path(__file__).resolve().parents[2] / "anchors.toml")
LIST_ORB = 5.0            # contacts listed (the vyuha cross orb); doctrine firing stays 3.0
# All four giants since the 2026-08-04 Rs/Ro decode (Jupiter/Saturn offsets
# PROVISIONAL — see bands.REAL_POSITION_OFFSETS).
REAL_BODIES = ("Jupiter", "Saturn", "Uranus", "Neptune")
MINUTE = 1.0 / 1440.0


class Anchor(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    category: str
    time: str                       # ISO UTC
    place: str
    lat: float | None = None
    lon: float | None = None
    mag: float | None = None
    taught: bool = False
    utc_offset: float = 0.0         # display only
    time_quality: str = "exact"     # "exact" | "approximate"
    source: str = ""
    notes: str = ""


def load_anchors(path: str = ANCHORS_PATH) -> list[Anchor]:
    with open(path, "rb") as fh:
        data = tomllib.load(fh)
    tables = data.get("anchor", [])
    if not tables:
        raise ValueError(f"{path}: no [[anchor]] tables found")
    return [Anchor(**t) for t in tables]


def iso_jd(iso: str) -> float:
    year, month, day = int(iso[0:4]), int(iso[5:7]), int(iso[8:10])
    seconds = float(iso[17:19]) if len(iso) > 18 else 0.0
    if len(iso) > 20 and iso[19] == ".":
        seconds = float(iso[17:].rstrip("Z"))
    hours = int(iso[11:13]) + int(iso[14:16]) / 60 + seconds / 3600
    return julian_day_number(year, month, day) + hours / 24 - 0.5


def jd_iso_minute(jd: float) -> str:
    jdn = math.floor(jd + 0.5)
    total = round((jd + 0.5 - jdn) * 1440)
    if total >= 1440:
        jdn, total = jdn + 1, total - 1440
    year, month, day = jd_to_calendar(jdn)
    return f"{year:04d}-{month:02d}-{day:02d}T{total // 60:02d}:{total % 60:02d}Z"


@functools.lru_cache(maxsize=300000)
def _chart(jd_r: float):
    """Geocentric tropical chart (positions only, lat/lon 0)."""
    jdn = math.floor(jd_r + 0.5)
    year, month, day = jd_to_calendar(jdn)
    return compute_raw(year, month, day, (jd_r + 0.5 - jdn) * 24,
                       0.0, 0.0, 0.0, False, False)


def chart_at(jd: float):
    return _chart(round(jd, 7))


def _site_chart(jd: float, lat: float, lon_east: float):
    """Tropical Koch chart at the site — the physical rising/culmination frame."""
    jdn = math.floor(jd + 0.5)
    year, month, day = jd_to_calendar(jdn)
    return compute_raw(year, month, day, (jd + 0.5 - jdn) * 24,
                       0.0, -lon_east, lat, False, False)


def _sep(a: float, b: float) -> float:
    d = abs(a - b) % 360.0
    return min(d, 360.0 - d)


def _lon(chart, body: str, kind: str) -> float:
    if kind == "rsep":
        return real_longitude(chart, body)
    return chart.positions[body].longitude


def pair_separation(a: str, b: str, kind: str, jd: float) -> float:
    chart = chart_at(jd)
    return _sep(_lon(chart, a, kind), chart.positions[b].longitude)


def contacts_at(jd: float) -> list[dict]:
    chart = chart_at(jd)
    out = []
    pairs = [(a, b, "sep") for i, a in enumerate(BAND_BODIES)
             for b in BAND_BODIES[i + 1:]
             if {a, b} != {"Rahu", "Ketu"}]     # opposite by construction
    pairs += [(a, b, "rsep") for a in REAL_BODIES for b in BAND_BODIES if b != a]
    for a, b, kind in pairs:
        s = _sep(_lon(chart, a, kind), chart.positions[b].longitude)
        for aspect, target in ASPECTS.items():
            delta = abs(s - target)
            if delta <= LIST_ORB:
                out.append({"a": a, "b": b, "kind": kind, "aspect": aspect,
                            "sep": round(delta, 3),
                            "within_doctrine_orb": delta <= ASPECT_ORB})
    out.sort(key=lambda c: c["sep"])
    return out


def refine_exactness(a: str, b: str, kind: str, target: float, jd0: float) -> dict:
    """The instant where the pair stands exactly at `target`, refined below one
    minute — the trigger instant of a fired rule (the substratum acts at the
    crossing, not at the catalog arrival)."""
    fast, mid = {"Moon"}, {"Sun", "Mercury", "Venus"}
    members = {a, b}
    if members & fast:
        window, step = 3.0, 0.25 / 24.0
    elif members & mid:
        window, step = 15.0, 1.0 / 24.0
    else:
        window, step = 120.0, 0.5

    def f(jd):
        return abs(pair_separation(a, b, kind, jd) - target)

    n = int(window / step)
    grid = [jd0 + k * step for k in range(-n, n + 1)]
    best = min(grid, key=f)
    edge = abs(abs(best - jd0) - window) <= step
    while step > 0.3 * MINUTE:
        step /= 8.0
        local = [best + k * step for k in range(-8, 9)]
        best = min(local, key=f)
    return {"jd": best, "residual": round(f(best), 4), "edge": edge}


def asc_crossings(jd_center: float, lat: float, lon_east: float) -> list[dict]:
    """Every instant within +-12 h where the site Ascendant conjoins a body
    (observed 11 + real-Uranus/Neptune), refined below one minute — the site
    timetable of the taught Ascendant channel (Ulsoor, Hyderabad)."""
    bodies = list(BAND_BODIES) + ["rJupiter", "rSaturn", "rUranus", "rNeptune"]

    def diffs(jd):
        chart = _site_chart(jd, lat, lon_east)
        asc = chart.positions["Ascendant"].longitude
        row = {}
        for body in bodies:
            if body.startswith("r"):
                lon = real_longitude(chart, body[1:])
            else:
                lon = chart.positions[body].longitude
            row[body] = ((asc - lon + 180.0) % 360.0) - 180.0
        return row

    step = 10.0 * MINUTE
    samples = []
    jd = jd_center - 0.5
    while jd <= jd_center + 0.5 + 1e-9:
        samples.append((jd, diffs(jd)))
        jd += step

    out = []
    for (jd_a, da), (jd_b, db) in zip(samples, samples[1:]):
        for body in bodies:
            x, y = da[body], db[body]
            if x < 0.0 <= y and abs(x) < 40.0 and abs(y) < 40.0:
                lo, hi = jd_a, jd_b
                for _ in range(18):
                    mid_jd = (lo + hi) / 2.0
                    if diffs(mid_jd)[body] < 0.0:
                        lo = mid_jd
                    else:
                        hi = mid_jd
                cross = (lo + hi) / 2.0
                out.append({"body": body, "jd": cross,
                            "utc": jd_iso_minute(cross)})
    out.sort(key=lambda c: c["jd"])
    return out


def dossier(anchor: Anchor, refine: bool = True) -> dict:
    jd0 = iso_jd(anchor.time)
    chart = chart_at(jd0)
    found = contacts_at(jd0)
    if refine:
        for c in found:
            if not c["within_doctrine_orb"]:
                continue
            ex = refine_exactness(c["a"], c["b"], c["kind"],
                                  ASPECTS[c["aspect"]], jd0)
            c["exact_utc"] = jd_iso_minute(ex["jd"])
            c["exact_offset_hours"] = round((ex["jd"] - jd0) * 24.0, 2)
            c["exact_residual"] = ex["residual"]
            c["exact_at_window_edge"] = ex["edge"]

    p = {name: chart.positions[name].longitude for name in BAND_BODIES}
    bands = {"mkm_spread": round(circular_spread([p["Moon"], p["Ketu"], p["Mars"]]), 3),
             "bands": {name: division_of(lon, 0) for name, lon in p.items()}}
    stacks = list(bands["bands"].values())
    bands["stack_max"] = max(stacks.count(v) for v in set(stacks))

    site = None
    if anchor.lat is not None and anchor.lon is not None:
        try:
            site = asc_crossings(jd0, anchor.lat, anchor.lon)
            for c in site:
                local = ((c["jd"] + anchor.utc_offset / 24.0 + 0.5) % 1.0) * 24.0
                c["local"] = f"{int(local):02d}:{int(round((local % 1) * 60)) % 60:02d}"
        except ValueError:
            site = None        # circumpolar site: the canon cannot cast the chart

    return {"anchor": anchor.model_dump(), "contacts": found, "bands": bands,
            "vyuha": vyuha_state(chart).model_dump(), "asc_crossings": site}


def render_text(d: dict) -> str:
    a = d["anchor"]
    lines = [f"ANCHOR {a['id']}  [{a['category']}]  {a['place']}",
             f"  time {a['time']} ({a['time_quality']})"
             + (f"  mag {a['mag']}" if a["mag"] else "")
             + ("  TAUGHT" if a["taught"] else ""),
             f"  {a['notes']}" if a["notes"] else "", ""]
    lines.append("  contacts (orb<=5; * = doctrine orb 3, with trigger instant):")
    for c in d["contacts"]:
        mark = "*" if c["within_doctrine_orb"] else " "
        row = (f"  {mark} {c['kind']}:{c['a']}-{c['b']}@{c['aspect']}"
               f"  {c['sep']:.2f} deg")
        if "exact_utc" in c:
            row += (f"  exact {c['exact_utc']} ({c['exact_offset_hours']:+.1f} h,"
                    f" residual {c['exact_residual']:.3f}"
                    + (", window edge" if c["exact_at_window_edge"] else "") + ")")
        lines.append(row)
    b = d["bands"]
    lines.append(f"  bands: mkm_spread {b['mkm_spread']} deg, stack_max {b['stack_max']}")
    v = d["vyuha"]
    lines.append(f"  vyuha: {'FIRED ' + v['level'] if v['fired'] else 'silent'}")
    if d["asc_crossings"] is not None:
        lines.append("  site timetable (Asc conjunctions, +-12 h):")
        for c in d["asc_crossings"]:
            lines.append(f"    {c['utc']}  local {c['local']}  Asc = {c['body']}")
    lines.append("")
    return "\n".join(lines)


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(
        description="Anchor-event dossiers: fired contacts with minute-refined "
                    "trigger instants, band state, vyuha, site timetable.")
    parser.add_argument("--data", default=ANCHORS_PATH)
    parser.add_argument("--anchor", help="single anchor id (default: all)")
    parser.add_argument("--list", action="store_true", help="list anchors and exit")
    parser.add_argument("--out", help="directory for per-anchor .json/.txt dossiers")
    args = parser.parse_args(argv)

    anchors = load_anchors(args.data)
    if args.list:
        for a in anchors:
            print(f"{a.id:<16} {a.category:<14} {a.time}  {a.place}")
        return
    if args.anchor:
        anchors = [a for a in anchors if a.id == args.anchor]
        if not anchors:
            raise SystemExit(f"unknown anchor: {args.anchor}")

    for a in anchors:
        d = dossier(a)
        text = render_text(d)
        if args.out:
            out = Path(args.out)
            out.mkdir(parents=True, exist_ok=True)
            (out / f"{a.id}.json").write_text(json.dumps(d, indent=2))
            (out / f"{a.id}.txt").write_text(text)
            print(f"wrote {out / a.id}.json/.txt")
        else:
            print(text)


if __name__ == "__main__":
    main()
