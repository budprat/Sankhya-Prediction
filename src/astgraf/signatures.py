# ABOUTME: Stage 2 of the inverse-learning system: extract geometric signatures at past
# ABOUTME: events' instants (plus matched controls) and screen features by lift.

import csv
import math
from pathlib import Path

from .bands import BAND_BODIES, circular_spread, division_of, real_longitude
from .ephemeris import compute_raw
from .grid import label_for_jd
from .locator import LIGHT_MINUTES, locate
from .models import ChartResult

# Deterministic control displacements (days): break astronomical alignment while
# keeping era and time-of-day structure. Three controls per event.
CONTROL_OFFSETS_DAYS = (-912, 456, 1368)

REAL_BODIES = ("Uranus", "Neptune")

ASPECTS = {"conj": 0.0, "sq": 90.0, "tri": 120.0, "opp": 180.0}
ASPECT_ORB = 3.0


def _sep(a: float, b: float) -> float:
    d = abs(a - b) % 360.0
    return min(d, 360.0 - d)


def _gc_km(lat1, lon1, lat2, lon2) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dl = math.radians(lon2 - lon1)
    x = math.sin(p1) * math.sin(p2) + math.cos(p1) * math.cos(p2) * math.cos(dl)
    return 6371.0 * math.acos(min(1.0, max(-1.0, x)))


def pair_keys() -> list[str]:
    keys = []
    for i, a in enumerate(BAND_BODIES):
        for b in BAND_BODIES[i + 1:]:
            keys.append(f"sep:{a}-{b}")
    for a in REAL_BODIES:
        for b in BAND_BODIES:
            if b != a:
                keys.append(f"rsep:{a}-{b}")
    return keys


def extract_signature(chart: ChartResult, event_lat: float | None = None,
                      event_lon: float | None = None) -> dict:
    p = {name: chart.positions[name].longitude for name in BAND_BODIES}
    real = {name: real_longitude(chart, name) for name in REAL_BODIES}
    sig: dict = {"jd": chart.jd}
    for i, a in enumerate(BAND_BODIES):
        for b in BAND_BODIES[i + 1:]:
            sig[f"sep:{a}-{b}"] = round(_sep(p[a], p[b]), 3)
    for a in REAL_BODIES:
        for b in BAND_BODIES:
            if b != a:
                sig[f"rsep:{a}-{b}"] = round(_sep(real[a], p[b]), 3)
    for name in BAND_BODIES:
        sig[f"band:{name}"] = division_of(p[name], 0)
    bands = [sig[f"band:{name}"] for name in BAND_BODIES]
    sig["stack_max"] = max(bands.count(b) for b in set(bands))
    sig["mkm_spread"] = round(circular_spread([p["Moon"], p["Ketu"], p["Mars"]]), 3)
    for name in ("Jupiter", "Saturn", "Uranus", "Neptune"):
        sig[f"dist:{name}"] = round(chart.positions[name].distance, 6)
    for body in LIGHT_MINUTES:
        spot = locate(chart, body)
        sig[f"spot_lat:{body}"] = round(spot.event_latitude_north, 3)
        sig[f"spot_lon:{body}"] = round(spot.event_longitude_east, 3)
        if event_lat is not None and event_lon is not None:
            sig[f"loc_km:{body}"] = round(_gc_km(event_lat, event_lon,
                                                 spot.event_latitude_north,
                                                 spot.event_longitude_east), 1)
    return sig


def _chart_for_time(iso: str, day_offset: int = 0) -> ChartResult:
    year, month, day = int(iso[0:4]), int(iso[5:7]), int(iso[8:10])
    hours = int(iso[11:13]) + int(iso[14:16]) / 60 + float(iso[17:23] or 0) / 3600
    return compute_raw(year, month, day + day_offset, hours, 0.0, 0.0, 0.0, True, True)


def run_corpus(catalog_path: str, out_dir: str) -> tuple[int, int]:
    with open(catalog_path, newline="") as fh:
        rows = [r for r in csv.DictReader(fh)
                if r.get("time") and r.get("latitude") and r.get("longitude")]
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    event_sigs, control_sigs = [], []
    for r in rows:
        lat, lon = float(r["latitude"]), float(r["longitude"])
        chart = _chart_for_time(r["time"])
        sig = extract_signature(chart, event_lat=lat, event_lon=lon)
        sig.update({"id": r.get("id", ""), "label": label_for_jd(chart.jd),
                    "mag": r.get("mag", ""), "place": r.get("place", ""),
                    "lat": lat, "lon": lon})
        event_sigs.append(sig)
        for offset in CONTROL_OFFSETS_DAYS:
            control = extract_signature(_chart_for_time(r["time"], offset))
            control.update({"id": f"{r.get('id', '')}~{offset:+d}d"})
            control_sigs.append(control)

    def write(path, sigs):
        keys: list[str] = []
        for s in sigs:
            for k in s:
                if k not in keys:
                    keys.append(k)
        with open(path, "w", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=keys)
            writer.writeheader()
            writer.writerows(sigs)

    write(out / "signatures.csv", event_sigs)
    write(out / "controls.csv", control_sigs)
    return len(event_sigs), len(control_sigs)


def mine_lifts(events: list[dict], controls: list[dict],
               pair_keys: list[str], min_event_rate: float = 0.02) -> list[dict]:
    """Screening lifts: aspect predicates over pair-separation features."""
    results = []
    for key in pair_keys:
        for aspect, target in ASPECTS.items():
            def hit(sig):
                value = sig.get(key)
                if value in (None, ""):
                    return False
                return abs(float(value) - target) <= ASPECT_ORB
            event_hits = sum(1 for s in events if hit(s))
            event_rate = event_hits / len(events) if events else 0.0
            if event_rate < min_event_rate:
                continue
            control_hits = sum(1 for s in controls if hit(s))
            control_rate = control_hits / len(controls) if controls else 0.0
            lift = (event_rate / control_rate) if control_rate else float("inf")
            results.append({"predicate": f"{key}@{aspect}", "event_hits": event_hits,
                            "event_rate": round(event_rate, 4),
                            "control_rate": round(control_rate, 4),
                            "lift": round(lift, 3) if lift != float("inf") else lift})
    results.sort(key=lambda r: -(r["lift"] if r["lift"] != float("inf") else 1e9))
    return results
