# ABOUTME: Casts the full event chart for every declustered M7+ mainshock, saves each one,
# ABOUTME: and grades every pattern the census surfaces against era-matched controls.
#
# Run from tools/astgraf:  uv run python scripts/quake_atlas.py
# Writes out/quake-atlas/{charts.csv, wheels/*.svg, census.txt, patterns.txt}.
#
# ===========================================================================
# WHAT THIS IS, AND WHAT IT IS NOT
#
# It is TWO things, kept strictly apart, because mixing them is how a project
# talks itself into a discovery:
#
#   PART A — THE ATLAS (descriptive).  One chart per event, cast AT THE
#   EPICENTER at the catalog instant: 13 body longitudes, retrograde flags,
#   nakshatra/pada/navamsam, 28-band occupancy, the four giants' doctrinal
#   real positions, the Moon-Ketu-Mars spread, band stack height, the Chatur
#   Vyuham state, every doctrine-orb contact, and which doctrine rules fire.
#   This is a RECORD. It makes no claim. Every number in it is true of the
#   catalog by construction.
#
#   PART B — THE GRADING (inferential).  Every regularity Part A surfaces is
#   then measured against ERA-MATCHED CONTROLS through astgraf.validation:
#   add-one smoothed lift, within-block permutation null, and a power curve.
#   Nothing from Part A is reported as a finding until it has been through
#   Part B.
#
# WHY THE SEPARATION IS THE WHOLE POINT.  A census of 1,435 charts will always
# produce striking-looking regularities: some nakshatra holds the most Moons,
# some pair aspects more often than the rest. Those are facts about the
# catalog AND about the sky's own base rates — Jupiter spends ~1 year per
# band whatever happens on Earth, so "Jupiter clusters in band N" measures
# Jupiter's period, not earthquakes. Only the event-vs-control contrast can
# separate the two, which is why every cell in Part B carries a control rate
# next to its event rate.
#
# MULTIPLICITY IS THE REAL ADVERSARY HERE. This screens hundreds of
# predicates. The largest of hundreds of noisy lifts is large by construction,
# so the per-predicate p is meaningless on its own; the honest bar is the
# FAMILY-WISE one — the null distribution of the MAXIMUM lift over the same
# predicate set under permutation. That is computed and reported, and it is
# the number the verdict rests on.
#
# PRIOR (stated so this run cannot be quoted as independent): three mining
# passes over this same corpus already returned null (RESULTS.md #1, max lift
# 1.705 vs null median 1.748, p = 0.65). This run is EXPLORATORY BY REQUEST
# and is not pre-registered. Anything it turns up is a lead requiring
# held-out confirmation, never a result — the standing lesson of the dwell
# doctrine, which survived three kill attempts and two replications and was
# still false (RESULTS.md #8).
# ===========================================================================

import argparse
import csv
import math
from collections import Counter
from pathlib import Path

from astgraf.anchors import contacts_at
from astgraf.bands import (BAND_BODIES, GIANTS, REAL_POSITION_OFFSETS,
                           circular_spread, division_of, real_longitude,
                           trigger_state, vyuha_state)
from astgraf.ephemeris import BODY_ORDER, compute_raw, julian_day_number
from astgraf.grid import jd_to_calendar
from astgraf.horary import HORARY_NAKSHATRAS_28, star_position
from astgraf.scope import render_scope
from astgraf.signatures import ASPECT_ORB, ASPECTS, decluster
from astgraf.triggers import evaluate_rule, load_rules
from astgraf.validation import (Claim, block_permutation_p, era_matched_controls,
                                poisson_sigma, power_curve, smoothed_lift)

BASE = Path(__file__).resolve().parent.parent

# Every quake catalog in the tree. `decluster` needs magnitudes to pick the
# largest of a cluster; the deaths-selected and curated files carry none, so
# they are declustered on time/space alone with a constant magnitude — noted
# per corpus rather than silently applied.
CORPORA = {
    "m7": {"path": "data/usgs-m7-1850-2020.csv", "mag": True,
           "label": "USGS M7+ 1850-2020 (magnitude-selected)"},
    "m6": {"path": "data/usgs-m6-1900-2020.csv", "mag": True,
           "label": "USGS M6.0-6.99 1901-2020 (held-out band)"},
    "ncei": {"path": "data/quakes-ncei-deaths.csv", "mag": False,
             "label": "NCEI/WDS deaths-selected 1702-2025"},
    "hist": {"path": "data/quakes-historical.csv", "mag": False,
             "label": "curated majors 856-2023 (three tiers)"},
}

OUT_ROOT = BASE / "out" / "quake-atlas"

MIN_YEAR = 1900          # engine drift disqualifies earlier events
CONTROLS_PER_EVENT = 3   # era-matched, +-365 d excluding +-7 d
N_PERM = 2000
POLAR_LIMIT = 66.0       # the BAS cusp chain is undefined past the polar circle


# --------------------------------------------------------------------------
# Chart casting
# --------------------------------------------------------------------------

def jd_of(iso: str) -> float:
    y, m, d = int(iso[0:4]), int(iso[5:7]), int(iso[8:10])
    sec = 0.0
    tail = iso[17:]
    if tail:
        num = ""
        for ch in tail:
            if ch.isdigit() or ch == ".":
                num += ch
            else:
                break
        sec = float(num) if num else 0.0
    hours = int(iso[11:13]) + int(iso[14:16]) / 60 + sec / 3600
    return julian_day_number(y, m, d) + hours / 24 - 0.5


def chart_at_site(jd: float, lat: float, lon_east: float):
    """Sidereal chart cast AT THE EPICENTER — bands and nakshatras are sidereal,
    and the site fixes a real Ascendant/MC. Beyond the polar circle the canon's
    cusp chain is undefined (sqrt(1-xx^2)), so those fall back to site-free."""
    jdn = math.floor(jd + 0.5)
    y, m, d = jd_to_calendar(jdn)
    hours = (jd + 0.5 - jdn) * 24
    if abs(lat) > POLAR_LIMIT:
        return compute_raw(y, m, d, hours, 0.0, 0.0, 0.0, True, True), False
    return compute_raw(y, m, d, hours, 0.0, -lon_east, lat, True, False), True


def chart_site_free(jd: float):
    jdn = math.floor(jd + 0.5)
    y, m, d = jd_to_calendar(jdn)
    return compute_raw(y, m, d, (jd + 0.5 - jdn) * 24, 0.0, 0.0, 0.0, True, True)


def chart_record(row: dict, jd: float, rules) -> dict:
    lat, lon = float(row["latitude"]), float(row["longitude"])
    chart, sited = chart_at_site(jd, lat, lon)
    p = {n: chart.positions[n].longitude for n in BAND_BODIES}
    rec = {
        "id": row.get("id", ""), "time": row["time"], "mag": row.get("mag", ""),
        "lat": lat, "lon": lon, "place": row.get("place", ""),
        "depth": row.get("depth", ""), "jd": round(jd, 6),
        "site_chart": sited,
    }
    for name in BODY_ORDER:
        pos = chart.positions[name]
        s = star_position(pos.longitude)
        rec[f"lon:{name}"] = round(pos.longitude, 4)
        rec[f"retro:{name}"] = pos.retrograde
        rec[f"nak:{name}"] = s.nakshatra
        rec[f"pada:{name}"] = s.pada
        if name in BAND_BODIES:
            rec[f"band:{name}"] = division_of(pos.longitude, 0)
    for g in REAL_POSITION_OFFSETS:
        rl = real_longitude(chart, g)
        rec[f"rlon:{g}"] = round(rl, 4)
        rec[f"rband:{g}"] = division_of(rl, 0)
    bands = [rec[f"band:{n}"] for n in BAND_BODIES]
    rec["stack_max"] = max(bands.count(b) for b in set(bands))
    rec["mkm_spread"] = round(circular_spread([p["Moon"], p["Ketu"], p["Mars"]]), 3)
    v = vyuha_state(chart)
    rec["vyuha"] = v.level
    rec["band_trigger"] = trigger_state(chart, level=0, proximity=True).level
    fired = [r.name for r in rules if evaluate_rule(chart, r).fired]
    rec["rules_fired"] = " ".join(fired)
    contacts = [c for c in contacts_at(jd) if c["within_doctrine_orb"]]
    rec["n_contacts"] = len(contacts)
    rec["contacts"] = "; ".join(
        f"{c['kind']}:{c['a']}-{c['b']}@{c['aspect']}={c['sep']}" for c in contacts[:12])
    return rec, chart, contacts


# --------------------------------------------------------------------------
# Predicate space (identical definition for events and controls)
# --------------------------------------------------------------------------

def predicates(chart) -> set[str]:
    """Every geometric predicate this atlas screens, as a set of string keys."""
    out = set()
    p = {n: chart.positions[n].longitude for n in BAND_BODIES}
    real = {g: real_longitude(chart, g) for g in REAL_POSITION_OFFSETS}

    def sep(a, b):
        d = abs(a - b) % 360.0
        return min(d, 360.0 - d)

    names = list(BAND_BODIES)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if {a, b} == {"Rahu", "Ketu"}:
                continue
            s = sep(p[a], p[b])
            for asp, tgt in ASPECTS.items():
                if abs(s - tgt) <= ASPECT_ORB:
                    out.add(f"sep:{a}-{b}@{asp}")
    for g, rl in real.items():
        for b in names:
            if b == g:
                continue
            s = sep(rl, p[b])
            for asp, tgt in ASPECTS.items():
                if abs(s - tgt) <= ASPECT_ORB:
                    out.add(f"rsep:{g}-{b}@{asp}")
    # Band occupancy: body in nakshatra-band N (the Predict.pdf 28x11 matrix).
    for b in names:
        out.add(f"band:{b}={division_of(p[b], 0)}")
    # Structural states.
    bands = [division_of(p[b], 0) for b in names]
    stack = max(bands.count(x) for x in set(bands))
    out.add(f"stack>={min(stack, 5)}")
    for k in range(2, min(stack, 5) + 1):
        out.add(f"stack>={k}")
    spread = circular_spread([p["Moon"], p["Ketu"], p["Mars"]])
    for lim in (12.857, 30.0, 60.0, 90.0):
        if spread <= lim:
            out.add(f"mkm<={lim}")
    v = vyuha_state(chart)
    if v.fired:
        out.add("vyuha")
    if any(sep(p[g], p[n]) <= 3.0 for g in GIANTS for n in ("Rahu", "Ketu")):
        out.add("giant-on-node")
    return out


# --------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description="Cast and grade every quake chart")
    ap.add_argument("--corpus", default="m7", choices=sorted(CORPORA) + ["all"])
    ap.add_argument("--no-wheels", action="store_true",
                    help="skip SVG rendering (the CSV is the chart record)")
    args = ap.parse_args()
    names = sorted(CORPORA) if args.corpus == "all" else [args.corpus]
    for name in names:
        run_corpus(name, wheels=not args.no_wheels)


def run_corpus(name: str, wheels: bool = True) -> None:
    spec = CORPORA[name]
    out = OUT_ROOT / name
    out.mkdir(parents=True, exist_ok=True)
    rules = load_rules("doctrine-triggers.toml")
    rules = [r for r in rules if "Ascendant" not in str(r)]   # site-free rules only

    print("\n" + "#" * 74)
    print(f"# CORPUS {name}: {spec['label']}")
    print("#" * 74)
    rows = [r for r in csv.DictReader(open(BASE / spec["path"]))
            if r.get("time") and r.get("latitude") and r.get("longitude")
            and int(r["time"][:4]) >= MIN_YEAR]
    if not spec["mag"]:
        # No magnitude column: decluster on time/space only. Stated, not hidden —
        # keep-largest degenerates to keep-earliest for these corpora.
        for r in rows:
            r.setdefault("mag", "0")
    rows = decluster(rows)
    print(f"corpus: {len(rows)} declustered events >= {MIN_YEAR}")

    # ---------------- PART A: the atlas ----------------
    records, charts, all_contacts, jds = [], [], [], []
    for r in rows:
        jd = jd_of(r["time"])
        rec, chart, contacts = chart_record(r, jd, rules)
        records.append(rec)
        charts.append(chart)
        all_contacts.append(contacts)
        jds.append(jd)

    keys = []
    for rec in records:
        for k in rec:
            if k not in keys:
                keys.append(k)
    with open(out / "charts.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        w.writerows(records)
    print(f"wrote {out / 'charts.csv'} ({len(records)} event charts)")

    if wheels:
        wdir = out / "wheels"
        wdir.mkdir(parents=True, exist_ok=True)
        for rec, chart in zip(records, charts):
            pos = {n: chart.positions[n].longitude for n in BODY_ORDER}
            stem = f"{rec['time'][:10]}_{rec['id'] or 'na'}".replace("/", "-")
            mag = f"M{rec['mag']}" if rec["mag"] else ""
            title = f"{rec['time'][:16]}Z  {mag}  {rec['place'][:44]}"
            (wdir / f"{stem}.svg").write_text(
                render_scope(pos, title=title, orb=3.0))
        print(f"wrote {len(records)} chart wheels -> {wdir}")

    census(records, all_contacts, out, spec["label"])

    # ---------------- PART B: grading ----------------
    grade(charts, jds, records, out)


def census(records, all_contacts, out, label) -> None:
    L = []

    def say(s=""):
        L.append(s)
        print(s)

    say("=" * 74)
    say(f"PART A — THE ATLAS: {label}")
    say("=" * 74)
    say(f"events: {len(records)}")
    mags = [float(r["mag"]) for r in records if r["mag"] and float(r["mag"]) > 0]
    if mags:
        say(f"magnitude: min {min(mags):.1f}  "
            f"median {sorted(mags)[len(mags)//2]:.1f}  max {max(mags):.1f}")
    else:
        say("magnitude: not carried by this corpus (deaths/curation-selected)")
    sited = sum(1 for r in records if r["site_chart"])
    say(f"charts cast at the epicenter: {sited}/{len(records)} "
        f"({len(records)-sited} polar, cast site-free)")
    say()

    say("-- band occupancy, most-occupied band per body (28 bands, uniform = 3.6%) --")
    say(f"  {'body':<9} {'top band':<16} {'n':>5} {'obs%':>6} {'unif%':>6}")
    for b in BAND_BODIES:
        c = Counter(r[f"band:{b}"] for r in records)
        band, n = c.most_common(1)[0]
        say(f"  {b:<9} {str(band) + ' ' + HORARY_NAKSHATRAS_28[band-1]:<16} {n:>5} "
            f"{100*n/len(records):>5.1f}% {100/28:>5.1f}%")
    say()

    say("-- contact frequency (doctrine orb 3 deg), top 15 of the screened space --")
    cc = Counter()
    for contacts in all_contacts:
        for c in contacts:
            cc[f"{c['kind']}:{c['a']}-{c['b']}@{c['aspect']}"] += 1
    for key, n in cc.most_common(15):
        say(f"  {key:<34} {n:>5}  {100*n/len(records):>5.1f}% of events")
    say()

    say("-- structural states --")
    ncon = [r["n_contacts"] for r in records]
    say(f"  contacts per event: mean {sum(ncon)/len(ncon):.2f}  "
        f"min {min(ncon)}  max {max(ncon)}")
    sc = Counter(r["stack_max"] for r in records)
    say("  band stack height: " + "  ".join(
        f"{k}:{v} ({100*v/len(records):.1f}%)" for k, v in sorted(sc.items())))
    vc = Counter(r["vyuha"] for r in records)
    say("  vyuha: " + "  ".join(f"{k}:{v}" for k, v in vc.most_common()))
    bt = Counter(r["band_trigger"] for r in records)
    say("  band trigger (proximity): "
        + "  ".join(f"{k}:{v}" for k, v in bt.most_common()))
    rf = Counter()
    for r in records:
        for name in r["rules_fired"].split():
            rf[name] += 1
    say("  doctrine rules fired:")
    for name, n in rf.most_common():
        say(f"    {name:<34} {n:>5}  {100*n/len(records):>5.1f}%")
    say()

    (out / "census.txt").write_text("\n".join(L) + "\n")


def grade(charts, jds, records, out) -> None:
    L = []

    def say(s=""):
        L.append(s)
        print(s)

    claim = Claim(
        name="quake-atlas-screen",
        hypothesis="Some geometric configuration in the doctrine's own predicate "
                   "space accompanies M7+ mainshocks more often than instants "
                   "drawn from the same era do.",
        direction="higher",
        statistic="add-one smoothed lift, family-wise max over the screened space",
        control="era-matched, 3 per event, +-365 d excluding +-7 d",
        corpus=f"USGS M7+ 1850-2020, post-1900, declustered 7d/500km: n = {len(charts)}",
        verdict="family-wise p < 0.05 against the permutation max-lift null",
        power="plant the winning predicate into 10/5/2% of events and confirm recovery",
        notes="EXPLORATORY, not pre-registered — leads only, never results.",
    )
    say("=" * 74)
    say("PART B — GRADING (every pattern above, vs era-matched controls)")
    say("=" * 74)
    say(claim.banner())
    say()

    control_jds = era_matched_controls(jds, CONTROLS_PER_EVENT)
    event_preds = [predicates(c) for c in charts]
    control_preds = [[predicates(chart_site_free(cj)) for cj in block]
                     for block in control_jds]
    say(f"cast {len(charts)} event charts and "
        f"{sum(len(b) for b in control_preds)} era-matched control charts")

    universe = set()
    for s in event_preds:
        universe |= s
    universe = sorted(universe)
    n_e = len(event_preds)
    n_c = sum(len(b) for b in control_preds)
    say(f"screened predicate space: {len(universe)}")
    say()

    scored = []
    blocks_by_pred = {}
    for key in universe:
        eh = sum(1 for s in event_preds if key in s)
        if eh / n_e < 0.02:                     # 2% event-rate floor
            continue
        ch = sum(1 for b in control_preds for s in b if key in s)
        lift = smoothed_lift(eh, n_e, ch, n_c)
        blocks = [[key in event_preds[i]] + [key in s for s in control_preds[i]]
                  for i in range(n_e)]
        blocks_by_pred[key] = blocks
        scored.append({"key": key, "eh": eh, "ch": ch,
                       "er": eh / n_e, "cr": ch / n_c, "lift": lift})
    scored.sort(key=lambda r: -r["lift"])
    say(f"predicates clearing the 2% event-rate floor: {len(scored)}")
    say()

    # The full graded table, so any census regularity can be looked up against
    # its control rate — the only way to tell a sky base rate from an effect.
    with open(out / "lifts.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["predicate", "lift", "event_hits", "event_rate",
                    "control_rate"])
        for r in scored:
            w.writerow([r["key"], f"{r['lift']:.4f}", r["eh"],
                        f"{r['er']:.4f}", f"{r['cr']:.4f}"])

    say("-- top 20 by smoothed lift (event rate vs era-matched control rate) --")
    say(f"  {'predicate':<34} {'lift':>6} {'ev%':>6} {'ctl%':>6} {'n_ev':>5} {'p_raw':>7}")
    for r in scored[:20]:
        p_raw = block_permutation_p(blocks_by_pred[r["key"]], r["lift"], 500)
        r["p_raw"] = p_raw
        say(f"  {r['key']:<34} {r['lift']:>6.3f} {100*r['er']:>5.1f}% "
            f"{100*r['cr']:>5.1f}% {r['eh']:>5} {p_raw:>7.3f}")
    say()

    # ---- family-wise null: the MAXIMUM lift over the same space, permuted ----
    say("-- family-wise multiplicity null (the honest bar) --")
    say(f"  permuting block labels {N_PERM} times over all {len(scored)} predicates,")
    say("  recording the MAXIMUM lift reached by any predicate each time.")
    import random
    rng = random.Random(97)
    keys = [r["key"] for r in scored]
    flag_matrix = [blocks_by_pred[k] for k in keys]
    maxes = []
    for _ in range(N_PERM // 4):
        picks = [rng.randrange(CONTROLS_PER_EVENT + 1) for _ in range(n_e)]
        best = 0.0
        for flags in flag_matrix:
            eh = ch = 0
            for i, blk in enumerate(flags):
                j = picks[i]
                eh += blk[j]
                ch += sum(blk) - blk[j]
            best = max(best, smoothed_lift(eh, n_e, ch, n_c))
        maxes.append(best)
    maxes.sort()
    observed_max = scored[0]["lift"]
    null_median = maxes[len(maxes) // 2]
    null_95 = maxes[int(0.95 * len(maxes))]
    fw_p = sum(1 for m in maxes if m >= observed_max) / len(maxes)
    say(f"  observed max lift : {observed_max:.3f}  [{scored[0]['key']}]")
    say(f"  null median       : {null_median:.3f}")
    say(f"  null 95th pct     : {null_95:.3f}")
    say(f"  FAMILY-WISE p     : {fw_p:.4f}")
    say()

    expected = scored[0]["cr"] * n_e
    sigma = poisson_sigma(scored[0]["eh"], expected)
    say(f"  count check on the winner: {scored[0]['eh']} firings vs "
        f"{expected:.1f} expected = {sigma:.2f} sigma")
    say()

    say("-- power: could this screen have seen a real effect? --")
    for row in power_curve(blocks_by_pred[scored[0]["key"]]):
        say(f"    plant {int(row['fraction']*100):>3}% -> lift {row['lift']:.3f}, "
            f"p = {row['p']:.4f}")
    say()

    verdict = ("SUPPORTED" if fw_p < 0.05 else "NOT SUPPORTED")
    say(f"VERDICT: {verdict} (bar: {claim.verdict})")
    if fw_p >= 0.05:
        say("  The largest lift in the screened space is within the range the same")
        say("  space reaches by chance. No configuration in the doctrine's own")
        say("  predicate vocabulary separates M7+ instants from era-matched ones.")
    say()

    # ---- magnitude stratification: does the great-quake tier differ? ----
    say("-- magnitude stratification (are the giants a different population?) --")
    tiers = [("M7.0-7.4", 7.0, 7.5), ("M7.5-7.9", 7.5, 8.0),
             ("M8.0-8.4", 8.0, 8.5), ("M8.5+", 8.5, 10.0)]
    for label, lo, hi in tiers:
        idx = [i for i, r in enumerate(records)
               if r["mag"] and lo <= float(r["mag"]) < hi]
        if len(idx) < 20:
            say(f"  {label:<10} n = {len(idx):<5} (too few to grade)")
            continue
        ncon = [records[i]["n_contacts"] for i in idx]
        stack = [records[i]["stack_max"] for i in idx]
        mkm = [records[i]["mkm_spread"] for i in idx]
        say(f"  {label:<10} n = {len(idx):<5} contacts {sum(ncon)/len(ncon):>5.2f}  "
            f"stack {sum(stack)/len(stack):>4.2f}  mkm spread {sum(mkm)/len(mkm):>6.1f} deg")
    say("  (all-event baselines above; a real magnitude coupling would show as a")
    say("   monotone trend across the tiers — read it against RESULTS.md #8, where")
    say("   exactly such a trend appeared on M7+ and died on held-out M6.)")
    say()

    (out / "patterns.txt").write_text("\n".join(L) + "\n")
    print(f"wrote {out / 'census.txt'} and {out / 'patterns.txt'}")


if __name__ == "__main__":
    main()
