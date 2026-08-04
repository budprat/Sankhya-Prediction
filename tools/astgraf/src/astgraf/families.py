# ABOUTME: The family-grain recurrence channel: slow-pair conjunction series with canon
# ABOUTME: nakshatra sectors, member-return flags, and the long-cycle family calendar.
#
# The doctrine's recurrence that actually repeats lives at nakshatra-sector
# grain (NU's Java family: 1881 Aswini -> Krakatoa 1883, 2000 Kritika -> 2004
# Sumatra), not at contact-fingerprint grain (which the 130-year sweep showed
# never re-forms). A family is DATA (families.toml); this module computes its
# conjunction calendar: every pair conjunction in a span, minute-refined, with
# the canon star/pada/band of the conjunction degree and a flag when it
# returns to a taught member's sector. Timing only - no spots.

import argparse
import csv
import functools
import json
import math
import tomllib
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from .anchors import iso_jd, jd_iso_minute
from .bands import BAND_BODIES, division_of
from .ephemeris import compute_raw
from .grid import jd_to_calendar
from .horary import star_position

FAMILIES_PATH = str(Path(__file__).resolve().parents[2] / "families.toml")
MINUTE = 1.0 / 1440.0


class FamilyMember(BaseModel):
    model_config = ConfigDict(extra="forbid")
    year: int
    sector: str = ""            # canon nakshatra name; empty = unconfirmed
    anchor: str = ""            # anchors.toml id
    note: str = ""


class Family(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    pair: list[str]
    category: str = ""
    members: list[FamilyMember] = []
    notes: str = ""

    def model_post_init(self, _ctx) -> None:
        if len(self.pair) != 2 or any(b not in BAND_BODIES for b in self.pair):
            raise ValueError(f"family '{self.name}': pair must be two known bodies")


def load_families(path: str = FAMILIES_PATH) -> list[Family]:
    with open(path, "rb") as fh:
        data = tomllib.load(fh)
    tables = data.get("family", [])
    if not tables:
        raise ValueError(f"{path}: no [[family]] tables found")
    return [Family(**t) for t in tables]


@functools.lru_cache(maxsize=200000)
def _chart(jd_r: float):
    """Sidereal chart (positions only) - the star sectors are sidereal."""
    jdn = math.floor(jd_r + 0.5)
    year, month, day = jd_to_calendar(jdn)
    return compute_raw(year, month, day, (jd_r + 0.5 - jdn) * 24,
                       0.0, 0.0, 0.0, True, False)


def _signed_sep(jd: float, body_a: str, body_b: str) -> float:
    chart = _chart(round(jd, 7))
    d = chart.positions[body_a].longitude - chart.positions[body_b].longitude
    return ((d + 180.0) % 360.0) - 180.0


def conjunction_series(body_a: str, body_b: str,
                       jd_lo: float, jd_hi: float) -> list[dict]:
    """Every conjunction of the pair in [jd_lo, jd_hi], minute-refined, with
    the canon star/pada and 28-band of the conjunction degree. Sign-change
    detection on the signed separation (|sep| < 90 guard keeps the
    opposition's ±180 wrap out), so retrograde triples stay three events."""
    step = 20.0
    out = []
    prev_jd, prev = jd_lo, _signed_sep(jd_lo, body_a, body_b)
    jd = jd_lo + step
    while jd <= jd_hi + step:
        cur = _signed_sep(jd, body_a, body_b)
        if prev * cur <= 0.0 and prev != cur and abs(prev) < 90 and abs(cur) < 90:
            lo, hi, f_lo = prev_jd, jd, prev
            for _ in range(30):
                mid = (lo + hi) / 2.0
                f_mid = _signed_sep(mid, body_a, body_b)
                if f_lo * f_mid <= 0.0:
                    hi = mid
                else:
                    lo, f_lo = mid, f_mid
            cross = (lo + hi) / 2.0
            if jd_lo <= cross <= jd_hi:
                chart = _chart(round(cross, 7))
                lon_a = chart.positions[body_a].longitude
                lon = (lon_a - _signed_sep(cross, body_a, body_b) / 2.0) % 360.0
                star = star_position(lon)
                out.append({"jd": cross, "utc": jd_iso_minute(cross),
                            "sidereal_lon": round(lon, 4),
                            "star": star.nakshatra, "pada": star.pada,
                            "band": division_of(lon, 0)})
        prev_jd, prev = jd, cur
        jd += step
    return out


def family_calendar(family: Family, jd_lo: float, jd_hi: float) -> list[dict]:
    rows = conjunction_series(family.pair[0], family.pair[1], jd_lo, jd_hi)
    sectors = {m.sector: m for m in family.members if m.sector}
    for r in rows:
        member = sectors.get(r["star"])
        r["family"] = family.name
        r["member_return"] = member is not None
        r["member_anchors"] = member.anchor if member else ""
    return rows


def render_text(family: Family, rows: list[dict]) -> str:
    lines = [f"FAMILY {family.name}  [{family.category}]  "
             f"{family.pair[0]}-{family.pair[1]} conjunctions",
             f"  members: " + ", ".join(
                 f"{m.year} {m.sector or '?'}"
                 + (f" -> {m.anchor}" if m.anchor else "")
                 for m in family.members)]
    for r in rows:
        flag = f"  << MEMBER-SECTOR RETURN ({r['member_anchors']})" \
            if r["member_return"] else ""
        lines.append(f"  {r['utc']}  {r['sidereal_lon']:8.3f}  "
                     f"{r['star']} pada {r['pada']} band {r['band']}{flag}")
    if not rows:
        lines.append("  (no conjunctions in span)")
    lines.append("")
    return "\n".join(lines)


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(
        description="Long-cycle family calendars: slow-pair conjunctions with "
                    "canon nakshatra sectors and member-return flags. "
                    "Timing only - no spots.")
    parser.add_argument("--data", default=FAMILIES_PATH)
    parser.add_argument("--family", help="family name (default: all)")
    parser.add_argument("--start", required=True, type=int, help="start year")
    parser.add_argument("--end", required=True, type=int, help="end year")
    parser.add_argument("--out", help="directory for families.csv/.txt/.json")
    args = parser.parse_args(argv)

    jd_lo = iso_jd(f"{args.start}-01-01T00:00:00Z")
    jd_hi = iso_jd(f"{args.end}-01-01T00:00:00Z")
    families = load_families(args.data)
    if args.family:
        families = [f for f in families if f.name == args.family]
        if not families:
            raise SystemExit(f"unknown family: {args.family}")

    all_rows, texts = [], []
    for f in families:
        rows = family_calendar(f, jd_lo, jd_hi)
        texts.append(render_text(f, rows))
        all_rows.extend(rows)
    all_rows.sort(key=lambda r: r["jd"])

    text = "\n".join(texts)
    if args.out:
        out = Path(args.out)
        out.mkdir(parents=True, exist_ok=True)
        fields = ["family", "utc", "sidereal_lon", "star", "pada", "band",
                  "member_return", "member_anchors", "jd"]
        with open(out / "families.csv", "w", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=fields)
            writer.writeheader()
            writer.writerows(all_rows)
        (out / "families.txt").write_text(text)
        (out / "families.json").write_text(json.dumps(all_rows, indent=2))
        print(f"wrote {out}/families.csv/.txt/.json ({len(all_rows)} rows)")
    else:
        print(text)


if __name__ == "__main__":
    main()
