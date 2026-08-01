# ABOUTME: Automated outcome logging - the assiduous-search step of the method: query
# ABOUTME: the USGS catalog around each passed watch window's spot and log the verdict.

import argparse
import csv
import datetime as dt
import json
import urllib.request
from pathlib import Path

USGS = ("https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson"
        "&starttime={start}&endtime={end}&latitude={lat}&longitude={lon}"
        "&maxradiuskm={radius}&minmagnitude={mag}")


def _default_fetch(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=30) as response:
        return json.load(response)


def check_spot(lat: float, lon: float, start: dt.date, end: dt.date,
               radius_km: float, min_mag: float, fetch) -> list[dict]:
    url = USGS.format(start=start, end=end, lat=lat, lon=lon,
                      radius=radius_km, mag=min_mag)
    payload = fetch(url)
    quakes = []
    for feature in payload.get("features", []):
        props = feature.get("properties", {})
        coords = feature.get("geometry", {}).get("coordinates", [None, None])
        quakes.append({"mag": props.get("mag"), "place": props.get("place"),
                       "lon": coords[0], "lat": coords[1]})
    return quakes


def main(argv: list[str] | None = None, fetch=None) -> int:
    p = argparse.ArgumentParser(prog="astgraf-outcomes",
                                description="log objective outcomes for passed "
                                            "watch windows (USGS quake channel)")
    p.add_argument("--episodes", required=True,
                   help="rules_episodes.csv with exact_instant and spot columns")
    p.add_argument("--today", default=None, help="override current date (YYYY-MM-DD)")
    p.add_argument("--window-days", type=float, default=3.0)
    p.add_argument("--radius-km", type=float, default=1000.0)
    p.add_argument("--min-mag", type=float, default=5.5)
    p.add_argument("--out", default="outcomes.csv")
    args = p.parse_args(argv)
    fetch = fetch or _default_fetch
    today = dt.date.fromisoformat(args.today) if args.today else dt.date.today()

    with open(args.episodes, newline="") as fh:
        episodes = [r for r in csv.DictReader(fh)
                    if r.get("exact_instant") and r.get("spot_lon_east")]

    results = []
    for e in episodes:
        instant = dt.date.fromisoformat(e["exact_instant"][:10])
        lo = instant - dt.timedelta(days=args.window_days)
        hi = instant + dt.timedelta(days=args.window_days)
        if hi >= today:
            results.append({**e, "verdict": "pending", "quakes": ""})
            continue
        quakes = check_spot(float(e["spot_lat_north"]), float(e["spot_lon_east"]),
                            lo, hi + dt.timedelta(days=1),
                            args.radius_km, args.min_mag, fetch)
        summary = "; ".join(f"M{q['mag']} {q['place']}" for q in quakes)
        results.append({**e, "verdict": "hit" if quakes else "clear",
                        "quakes": summary})

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(results[0].keys()) if results else ["rule", "verdict", "quakes"]
    with open(out, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    counts = {}
    for r in results:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
    print(f"astgraf-outcomes: {len(results)} windows -> {out}  "
          + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))
    for r in results:
        if r["verdict"] == "hit":
            print(f"  HIT {r['rule']} {r['exact_instant']}: {r['quakes']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
