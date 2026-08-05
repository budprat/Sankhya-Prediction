# ABOUTME: Stage 2 of the inverse-learning system: extract geometric signatures at past
# ABOUTME: events' instants (plus matched controls) and screen features by lift.

import csv
import math
import re
from pathlib import Path

from .bands import BAND_BODIES, circular_spread, division_of, real_longitude
from .ephemeris import compute_raw
from .grid import label_for_jd
from .locator import LIGHT_MINUTES, locate
from .models import ChartResult
from .validation import smoothed_lift

# Controls are a TIME-UNIFORM grid over the corpus span (audit batch 3): the
# old -912/+456/+1368 offsets were aliased with the scanned pairs' alignment
# periods, and event-shifted controls of any kind inherit the catalog's
# completeness gradient (a circular-shift pilot promoted "was it 1905-12" —
# the Ura-opp-Nep era — to lift 55). A uniform grid IS the climatology.
CONTROLS_PER_EVENT = 3

REAL_BODIES = ("Jupiter", "Saturn", "Uranus", "Neptune")

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
                      event_lon: float | None = None, chart_at=None) -> dict:
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
        # Forward-model consistency (audit batch 3, finding 11): the catalog
        # instant is the ARRIVAL; the acting chart is light-time EARLIER.
        # Locating the arrival chart double-counts the rotation (~63 deg for
        # Neptune). With chart_at, the spot is taken from the trigger chart.
        base = chart
        if chart_at is not None:
            from .locator import light_minutes_for
            minutes = light_minutes_for(chart, body) or 0.0
            base = chart_at(chart.jd - minutes / 1440.0)
        spot = locate(base, body)
        sig[f"spot_lat:{body}"] = round(spot.event_latitude_north, 3)
        sig[f"spot_lon:{body}"] = round(spot.event_longitude_east, 3)
        if event_lat is not None and event_lon is not None:
            sig[f"loc_km:{body}"] = round(_gc_km(event_lat, event_lon,
                                                 spot.event_latitude_north,
                                                 spot.event_longitude_east), 1)
    return sig


def _chart_for_time(iso: str, day_offset: int = 0) -> ChartResult:
    year, month, day = int(iso[0:4]), int(iso[5:7]), int(iso[8:10])
    # Robust seconds parse (audit finding 52): "…:24Z" (no milliseconds) is a
    # legal USGS timestamp and used to crash the fixed-width slice.
    m = re.match(r"(\d{2}(?:\.\d+)?)", iso[17:])
    seconds = float(m.group(1)) if m else 0.0
    hours = int(iso[11:13]) + int(iso[14:16]) / 60 + seconds / 3600
    return compute_raw(year, month, day + day_offset, hours, 0.0, 0.0, 0.0, True, True)


def _chart_at_jd(jd: float) -> ChartResult:
    from .grid import jd_to_calendar
    jdn = math.floor(jd + 0.5)
    year, month, day = jd_to_calendar(jdn)
    return compute_raw(year, month, day, (jd + 0.5 - jdn) * 24,
                       0.0, 0.0, 0.0, True, True)


def decluster(rows: list[dict], days: float = 7.0, km: float = 500.0) -> list[dict]:
    """Drop fore/aftershock-like rows: within `days` AND `km` of a retained
    LARGER event (audit batch 3, finding 33; keep-largest greedy — a
    keep-first walk silently dropped the 1960 Valdivia and 2011 Tohoku
    mainshocks in favor of their foreshocks)."""
    def jd_of(r):
        return _chart_for_time(r["time"]).jd
    candidates = [(float(r.get("mag") or 0), jd_of(r),
                   float(r["latitude"]), float(r["longitude"]), i, r)
                  for i, r in enumerate(rows)]
    kept: list[tuple[float, float, float, float, int, dict]] = []
    for cand in sorted(candidates, key=lambda c: (-c[0], c[1])):
        _, jd, lat, lon, _, _ = cand
        clustered = any(abs(jd - kjd) <= days and _gc_km(lat, lon, klat, klon) <= km
                        for _, kjd, klat, klon, _, _ in kept)
        if not clustered:
            kept.append(cand)
    return [r for *_, r in sorted(kept, key=lambda c: c[1])]


def run_corpus(catalog_path: str, out_dir: str,
               decluster_events: bool = False,
               min_year: int | None = None) -> tuple[int, int]:
    with open(catalog_path, newline="") as fh:
        rows = [r for r in csv.DictReader(fh)
                if r.get("time") and r.get("latitude") and r.get("longitude")]
    if min_year is not None:
        rows = [r for r in rows if int(r["time"][0:4]) >= min_year]
    if decluster_events:
        rows = decluster(rows)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    jds = [_chart_for_time(r["time"]).jd for r in rows]
    span_lo, span_len = min(jds), max(jds) - min(jds)

    event_sigs, control_sigs = [], []
    for r, jd in zip(rows, jds):
        lat, lon = float(r["latitude"]), float(r["longitude"])
        chart = _chart_for_time(r["time"])
        sig = extract_signature(chart, event_lat=lat, event_lon=lon,
                                chart_at=_chart_at_jd)
        sig.update({"id": r.get("id", ""), "label": label_for_jd(chart.jd),
                    "mag": r.get("mag", ""), "place": r.get("place", ""),
                    "lat": lat, "lon": lon})
        event_sigs.append(sig)

    # Golden-ratio low-discrepancy sequence, NOT a uniform stride: a strict
    # span/N stride sat at a near 3:8 commensurability with the lunar cycle,
    # so control Moon phases formed a drifting comb whose holes landed on the
    # aspect zones (a fake p=0 "discovery"). frac(k*phi) is equidistributed
    # and non-resonant with every periodic signal, and stays deterministic.
    phi = 0.6180339887498949
    n_controls = CONTROLS_PER_EVENT * len(rows)
    for k in range(n_controls):
        control_jd = span_lo + span_len * ((k * phi) % 1.0)
        control = extract_signature(_chart_at_jd(control_jd),
                                    chart_at=_chart_at_jd)
        control.update({"id": f"grid~{k}"})
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
            # Add-one smoothed lift (audit finding 53): zero control hits must
            # not rank as infinite evidence. One implementation, in validation.
            lift = smoothed_lift(event_hits, len(events),
                                 control_hits, len(controls))
            results.append({"predicate": f"{key}@{aspect}", "event_hits": event_hits,
                            "event_rate": round(event_rate, 4),
                            "control_rate": round(control_rate, 4),
                            "lift": round(lift, 3)})
    results.sort(key=lambda r: -r["lift"])
    return results


def permutation_max_lift(events: list[dict], controls: list[dict],
                         keys: list[str], n_perm: int = 200, seed: int = 42,
                         min_event_rate: float = 0.02) -> list[float]:
    """Null distribution of the maximum screening lift under label permutation
    (audit finding 15): shuffle which pooled signatures count as 'events' and
    record the best smoothed lift any predicate reaches by chance."""
    import random
    rows = events + controls
    n, n_e = len(rows), len(events)
    n_c = n - n_e
    masks = []
    for key in keys:
        for target in ASPECTS.values():
            m = 0
            for i, s in enumerate(rows):
                v = s.get(key)
                if v not in (None, "") and abs(float(v) - target) <= ASPECT_ORB:
                    m |= 1 << i
            masks.append(m)
    full = (1 << n) - 1
    rng = random.Random(seed)
    indices = list(range(n))
    maxes = []
    for _ in range(n_perm):
        rng.shuffle(indices)
        em = 0
        for i in indices[:n_e]:
            em |= 1 << i
        cm = full & ~em
        best = 0.0
        for m in masks:
            eh = (m & em).bit_count()
            if eh / n_e < min_event_rate:
                continue
            ch = (m & cm).bit_count()
            best = max(best, ((eh + 1) / (n_e + 2)) / ((ch + 1) / (n_c + 2)))
        maxes.append(best)
    return maxes
