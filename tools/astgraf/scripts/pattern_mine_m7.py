# ABOUTME: Mines REPEATED PATTERNS — co-occurring configurations, not single predicates —
# ABOUTME: over every M7+ quake in the tree, grades them, and writes them out as loadable rules.
#
# Run from tools/astgraf:  uv run python scripts/pattern_mine_m7.py
# Writes out/pattern-mine-m7/{report.txt, patterns.csv} and atlas-patterns.toml.
#
# ===========================================================================
# WHAT IS NEW HERE, AND WHY IT IS WORTH RUNNING AGAIN
#
# Every previous screen in this project (RESULTS.md #1, #12) tested SINGLE
# predicates: "is Neptune on Ketu", "is the Moon in band 18". But the taught
# doctrine is not built from single predicates — every worked instance NU
# gives is a CONJUNCTION of conditions:
#
#   Nepal      real-Neptune on Ketu AND real-Uranus on the Sun
#   Hyderabad  a body on Rahu AND a body on Ketu AND Sun conj Jupiter
#   Vyuham     two oppositions AND a 90-degree cross AND a nodal lock
#
# A single-predicate screen is structurally blind to that shape: if the real
# rule is "A and B together", each of A and B alone may sit at lift ~1.0 and
# never surface. So this miner searches the space the doctrine actually lives
# in — PAIRS and TRIPLES of co-occurring predicates — which no pass over this
# corpus has done.
#
# THE PRICE, PAID EXPLICITLY. Going from ~500 singles to ~125,000 pairs
# multiplies the multiplicity problem by 250x. The largest of 125,000 noisy
# lifts is very large indeed. So the family-wise null is computed over the
# ENTIRE searched space — singles, pairs and triples together — and that is
# the only number the verdict may rest on. A pattern's own p-value is
# reported for information and is worthless on its own.
#
# CORPUS: every M7+ quake in the tree, unified across all three catalogs that
# carry them and deduplicated (3 d / 300 km) — the USGS M7+ file, the
# NCEI/WDS deaths-selected rows whose notes carry Mw >= 7.0, and the curated
# majors. This is a LARGER M7+ set than any previous run used, because the
# deaths-selected file contains M7+ events the USGS magnitude file misses.
# M6 is excluded by instruction: the doctrine speaks about major events.
#
# OUTPUT CONTRACT: surviving patterns are written to atlas-patterns.toml in
# the project's own rule schema, so they LOAD with triggers.load_rules() and
# sweep with astgraf-bands like any other rule file. Each carries its measured
# lift, support, p, and a status label. A pattern that fails the family-wise
# bar is written with status = "NOT SUPPORTED" rather than silently dropped —
# mined-triggers.toml was retired for exactly this reason and its history is
# the reason the labels are mandatory.
# ===========================================================================

import csv
import datetime as dt
import math
import random
import re
from itertools import combinations
from pathlib import Path

from astgraf.anchors import chart_at
from astgraf.bands import (BAND_BODIES, GIANTS, REAL_POSITION_OFFSETS,
                           circular_spread, division_of, real_longitude,
                           vyuha_state)
from astgraf.ephemeris import julian_day_number
from astgraf.horary import HORARY_NAKSHATRAS_28
from astgraf.signatures import ASPECT_ORB, ASPECTS, decluster
from astgraf.validation import (Claim, era_matched_controls, poisson_sigma,
                                smoothed_lift)

BASE = Path(__file__).resolve().parent.parent
OUT = BASE / "out" / "pattern-mine-m7"
TOML_OUT = BASE / "atlas-patterns.toml"

MIN_YEAR = 1900
MIN_MAG = 7.0
CONTROLS_PER_EVENT = 3
MIN_SUPPORT = 0.01          # a pattern must hold at >= 1% of events
# Why 1% and not lower: a lift estimated on fewer than ~15 events is not
# estimable, it is noise with a ratio printed next to it. The cost is stated
# in the report — the TAUGHT patterns are rarer than this floor (nepal-double
# fires at 0.1%), so no screen on this corpus can validate them either way.
N_PERM = 2000
MIN_DISCRIMINATION = 0.90   # a predicate whose slots never vary is untestable
MIN_EPOCHS = 8              # distinct years; fewer means pseudo-replication
SEED = 42
DEDUPE_DAYS, DEDUPE_KM = 3.0, 300.0


# --------------------------------------------------------------------------
# Corpus: every M7+ quake in the tree, unified and deduplicated
# --------------------------------------------------------------------------

def _mw(notes: str | None) -> float | None:
    if not notes:
        return None
    m = re.search(r"Mw\s*~?\s*([0-9]+(?:\.[0-9]+)?)", notes)
    return float(m.group(1)) if m else None


def _gc_km(a, b, c, d) -> float:
    p1, p2 = math.radians(a), math.radians(c)
    dl = math.radians(d - b)
    x = math.sin(p1) * math.sin(p2) + math.cos(p1) * math.cos(p2) * math.cos(dl)
    return 6371.0 * math.acos(min(1.0, max(-1.0, x)))


def jd_of(iso: str) -> float:
    y, m, d = int(iso[0:4]), int(iso[5:7]), int(iso[8:10])
    num = ""
    for ch in iso[17:]:
        if ch.isdigit() or ch == ".":
            num += ch
        else:
            break
    sec = float(num) if num else 0.0
    hours = int(iso[11:13]) + int(iso[14:16]) / 60 + sec / 3600
    return julian_day_number(y, m, d) + hours / 24 - 0.5


def build_corpus(say) -> list[dict]:
    pool = []
    for r in csv.DictReader(open(BASE / "data/usgs-m7-1850-2020.csv")):
        if r.get("mag") and float(r["mag"]) >= MIN_MAG and r.get("latitude"):
            pool.append({"src": "usgs-m7", "time": r["time"],
                         "latitude": r["latitude"], "longitude": r["longitude"],
                         "mag": r["mag"], "id": r["id"],
                         "place": r.get("place", ""), "prec": "minute"})
    n_usgs = len(pool)
    n_ncei = 0
    for r in csv.DictReader(open(BASE / "data/quakes-ncei-deaths.csv")):
        mw = _mw(r.get("notes"))
        if mw and mw >= MIN_MAG and r.get("latitude"):
            pool.append({"src": "ncei", "time": r["time"],
                         "latitude": r["latitude"], "longitude": r["longitude"],
                         "mag": str(mw), "id": r["id"],
                         "place": r.get("place", ""),
                         "prec": r.get("date_precision", "day")})
            n_ncei += 1
    n_hist = 0
    for r in csv.DictReader(open(BASE / "data/quakes-historical.csv")):
        mw = _mw(r.get("notes"))
        if ((mw and mw >= MIN_MAG) or r.get("tier") == "largest") and r.get("latitude"):
            pool.append({"src": "hist", "time": r["time"],
                         "latitude": r["latitude"], "longitude": r["longitude"],
                         "mag": str(mw or 8.4), "id": r["id"],
                         "place": r.get("place", ""),
                         "prec": r.get("date_precision", "day")})
            n_hist += 1
    say(f"  candidates: usgs-m7 {n_usgs}, ncei M7+ {n_ncei}, hist M7+ {n_hist}")

    # Cross-catalog dedupe. Preference order matters: USGS minute-precision
    # instants win over day-precision death-catalogue rows for the SAME event,
    # because the Moon moves 13.2 deg/day and a day-precision time cannot
    # place it.
    rank = {"usgs-m7": 0, "ncei": 1, "hist": 2}
    pool.sort(key=lambda r: (rank[r["src"]], 0 if r["prec"] == "minute" else 1))
    kept: list[dict] = []
    dups = 0
    for c in pool:
        try:
            cj = jd_of(c["time"])
        except (ValueError, IndexError):
            continue
        lat, lon = float(c["latitude"]), float(c["longitude"])
        if any(abs(cj - k["_jd"]) <= DEDUPE_DAYS
               and _gc_km(lat, lon, float(k["latitude"]), float(k["longitude"]))
               <= DEDUPE_KM for k in kept):
            dups += 1
            continue
        c["_jd"] = cj
        kept.append(c)
    say(f"  cross-catalog duplicates merged: {dups}")
    say(f"  unique M7+ events: {len(kept)}")
    kept = [k for k in kept if int(k["time"][:4]) >= MIN_YEAR]
    say(f"  post-{MIN_YEAR}: {len(kept)}")
    kept = decluster(kept)
    say(f"  declustered (7 d / 500 km keep-largest): {len(kept)}")
    return kept


# --------------------------------------------------------------------------
# Predicate vocabulary — each carries the TOML condition it maps to
# --------------------------------------------------------------------------

def predicate_conditions(chart) -> dict[str, dict]:
    """Every predicate true of this chart, keyed by name, valued by the rule
    condition that expresses it — so a mined pattern can be written back out
    as a loadable rule rather than as an opaque string."""
    out: dict[str, dict] = {}
    p = {n: chart.positions[n].longitude for n in BAND_BODIES}
    real = {g: real_longitude(chart, g) for g in REAL_POSITION_OFFSETS}

    def sep(a, b):
        d = abs(a - b) % 360.0
        return min(d, 360.0 - d)

    aspect_type = {"conj": "conjunction", "opp": "opposition",
                   "sq": "square", "tri": "trine"}
    names = list(BAND_BODIES)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if {a, b} == {"Rahu", "Ketu"}:
                continue
            s = sep(p[a], p[b])
            for asp, tgt in ASPECTS.items():
                if abs(s - tgt) <= ASPECT_ORB:
                    out[f"sep:{a}-{b}@{asp}"] = {
                        "type": aspect_type[asp], "bodies": [a, b],
                        "orb": ASPECT_ORB}
    for g, rl in real.items():
        for b in names:
            if b == g:
                continue
            s = sep(rl, p[b])
            for asp, tgt in ASPECTS.items():
                if abs(s - tgt) <= ASPECT_ORB:
                    out[f"rsep:{g}-{b}@{asp}"] = {
                        "type": aspect_type[asp], "bodies": [f"real:{g}", b],
                        "orb": ASPECT_ORB}
    for b in names:
        band = division_of(p[b], 0)
        out[f"band:{b}={band}"] = {
            "type": "in_band", "bodies": [b],
            "band": HORARY_NAKSHATRAS_28[band - 1]}
    spread = circular_spread([p["Moon"], p["Ketu"], p["Mars"]])
    for lim, tag in ((12.857142857142858, "12.86"), (30.0, "30"), (60.0, "60")):
        if spread <= lim:
            out[f"mkm<={tag}"] = {"type": "cluster",
                                  "bodies": ["Moon", "Ketu", "Mars"],
                                  "max_spread": lim}
    if any(sep(p[g], p[n]) <= 3.0 for g in GIANTS for n in ("Rahu", "Ketu")):
        out["giant-on-node"] = {"type": "nodes_occupied",
                                "bodies": list(GIANTS), "orb": 3.0,
                                "require": "either"}
    if vyuha_state(chart).fired:
        out["vyuha"] = None            # detector-only; no single condition
    return out


# --------------------------------------------------------------------------

def main() -> None:
    lines: list[str] = []

    def say(s=""):
        lines.append(s)
        print(s)

    OUT.mkdir(parents=True, exist_ok=True)
    claim = Claim(
        name="m7-pattern-mine",
        hypothesis="Some CO-OCCURRING configuration (pair or triple of "
                   "predicates) accompanies M7+ quakes more than era-matched "
                   "instants — the conjunction-of-conditions shape every "
                   "taught instance actually has.",
        direction="higher",
        statistic="add-one smoothed lift; family-wise max over singles+pairs+triples",
        control="era-matched, 3 per event, +-365 d excluding +-7 d",
        corpus="every M7+ quake in the tree, unified across 3 catalogs, "
               "deduplicated 3 d / 300 km, post-1900, declustered",
        verdict="family-wise p < 0.05 against the permutation max-lift null",
        power="plant a synthetic pattern into 10/5/2% of events",
        preregistered=False,
        notes="EXPLORATORY by request. Pair/triple space has never been "
              "searched on this corpus; multiplicity is 250x the single-"
              "predicate screens and the family-wise null accounts for it.",
    )
    say("=" * 74)
    say("M7+ PATTERN MINE — co-occurring configurations")
    say("=" * 74)
    say(claim.banner())
    say()

    say("CORPUS")
    rows = build_corpus(say)
    say()

    jds = [jd_of(r["time"]) for r in rows]
    control_blocks = era_matched_controls(jds, CONTROLS_PER_EVENT, seed=SEED)
    say(f"casting {len(jds)} event charts and "
        f"{sum(len(b) for b in control_blocks)} era-matched control charts")

    ev_preds, cond_map = [], {}
    for jd in jds:
        d = predicate_conditions(chart_at(jd))
        ev_preds.append(set(d))
        for k, v in d.items():
            if v is not None:
                cond_map.setdefault(k, v)
    ct_preds = [[set(predicate_conditions(chart_at(cj))) for cj in blk]
                for blk in control_blocks]
    n_e = len(ev_preds)
    n_c = sum(len(b) for b in ct_preds)
    say(f"  cast {n_e} event + {n_c} control charts")
    say()

    # ---- bitsets, one per BLOCK SLOT so the permutation can relabel properly ----
    # Slot 0 is the event, slots 1..k are its era-matched controls. Bit i of
    # slot s is "predicate holds at event i's slot-s instant". Keeping the
    # slots separate is what makes a genuine within-block permutation possible;
    # a flattened control axis cannot express which control belongs to which
    # event.
    support_floor = int(MIN_SUPPORT * n_e)
    singles = sorted({k for s in ev_preds for k in s})
    slots: dict[str, list[int]] = {}
    for k in singles:
        row = [0] * (CONTROLS_PER_EVENT + 1)
        for i, s in enumerate(ev_preds):
            if k in s:
                row[0] |= 1 << i
        for i, blk in enumerate(ct_preds):
            for j, s in enumerate(blk):
                if k in s:
                    row[j + 1] |= 1 << i
        if row[0].bit_count() >= support_floor:
            slots[k] = row

    # ---- TESTABILITY FILTER (added after the first run returned a false
    # positive; see the report). A within-block permutation can only test a
    # predicate whose value VARIES across the slots of a block. If the event
    # and all its controls always agree, that block contributes zero variance
    # to the null while still contributing to the observed lift — the null max
    # collapses and an ordinary fluctuation reads as significant.
    #
    # This is not hypothetical: the first run of this miner returned
    # "SUPPORTED, family-wise p = 0.0067" on `band:Neptune=24 + mkm<=60`, whose
    # 18 events ALL fall in 1996-2002 — one Neptune band-dwell. Neptune moves
    # 7.7 deg/yr and a band is 12.86 deg, so a +-365 d control cannot leave the
    # band: 96.8% of its blocks were constant. The predicate was not a
    # configuration, it was the string "was it 1996-2002".
    #
    # Measured discrimination (fraction of live blocks whose slots differ):
    #   band:Neptune 0.46, band:Uranus 0.64  <- untestable at this window
    #   band:Saturn 0.95, everything else >= 0.99
    # So the filter removes exactly the two slow-giant band families and
    # nothing else. The alternative — widening the control window until Neptune
    # decorrelates (~2 yr) — would break era-matching, which exists to hold the
    # catalogue's completeness gradient fixed. The predicate is simply not
    # testable against this catalogue, and saying so is the honest move.
    dropped = []
    for k, row in list(slots.items()):
        live = disc = 0
        for i in range(n_e):
            st = [(row[s] >> i) & 1 for s in range(CONTROLS_PER_EVENT + 1)]
            if any(st):
                live += 1
                if not all(st):
                    disc += 1
        if live and disc / live < MIN_DISCRIMINATION:
            dropped.append((k, disc / live))
            del slots[k]
    e_bits = {k: v[0] for k, v in slots.items()}
    keys = sorted(e_bits)
    say("SEARCH SPACE")
    say(f"  predicates dropped as UNTESTABLE (slots constant within blocks, "
        f"discrimination < {MIN_DISCRIMINATION}): {len(dropped)}")
    for k, d in sorted(dropped, key=lambda x: x[1])[:6]:
        say(f"      {k:<24} discrimination {d:.3f}")
    if len(dropped) > 6:
        say(f"      ... and {len(dropped) - 6} more (all band:Neptune / band:Uranus)")
    say(f"  singles with support >= {support_floor} ({MIN_SUPPORT:.0%}): {len(keys)}")

    # A pattern's slot-s bitset is the AND of its members' slot-s bitsets:
    # "all conditions hold simultaneously at that instant".
    def combine(names: list[str]) -> list[int]:
        row = list(slots[names[0]])
        for nm in names[1:]:
            other = slots[nm]
            row = [row[s] & other[s] for s in range(CONTROLS_PER_EVENT + 1)]
        return row

    space = [(k, slots[k], 1) for k in keys]
    pair_rows = []
    for a, b in combinations(keys, 2):
        row = combine([a, b])
        if row[0].bit_count() >= support_floor:
            pair_rows.append(([a, b], row))
            space.append((f"{a} + {b}", row, 2))
    say(f"  pairs clearing the same floor: {len(pair_rows)}")
    seen = {frozenset(m) for m, _ in pair_rows}
    n_tri = 0
    for members, prow in pair_rows:
        for k in keys:
            if k in members:
                continue
            key = frozenset(members + [k])
            if key in seen:
                continue
            other = slots[k]
            row = [prow[s] & other[s] for s in range(CONTROLS_PER_EVENT + 1)]
            if row[0].bit_count() >= support_floor:
                seen.add(key)
                space.append((" + ".join(sorted(key)), row, 3))
                n_tri += 1
    say(f"  triples clearing the same floor: {n_tri}")
    say(f"  TOTAL searched: {len(space)}")
    say()

    # ---- INDEPENDENCE + REPLICATION diagnostics, computed for every pattern.
    # A slow-body predicate is constant for months to years, so several events
    # in one epoch are ONE observation of the configuration, not several. The
    # permutation treats each event as independent and therefore overstates
    # significance wherever a pattern's support is concentrated in a few
    # epochs. Two guards, both from the project's own standing rules:
    #   EPOCHS   distinct calendar years carrying the pattern. The first run's
    #            winner had 17 events in THREE years (1931, 1989, 1990) — two
    #            epochs wearing a lift of 2.70.
    #   HALVES   2-year-block alternating split, the project's standard. That
    #            same winner gave 0.998 / 3.394: entirely inside one half.
    years = [int(r["time"][:4]) for r in rows]
    order_idx = sorted(range(n_e), key=lambda i: jds[i])
    jd0 = jds[order_idx[0]]
    half_of = {i: int((jds[i] - jd0) // 730.5) % 2 for i in range(n_e)}
    hA = [i for i in range(n_e) if half_of[i] == 0]
    hB = [i for i in range(n_e) if half_of[i] == 1]

    def half_lift(row, idx):
        eh = sum(1 for i in idx if (row[0] >> i) & 1)
        ch = sum(1 for i in idx for s in range(1, CONTROLS_PER_EVENT + 1)
                 if (row[s] >> i) & 1)
        return smoothed_lift(eh, len(idx), ch, CONTROLS_PER_EVENT * len(idx))

    scored = []
    for name, row, order in space:
        eh = row[0].bit_count()
        ch = sum(row[s].bit_count() for s in range(1, CONTROLS_PER_EVENT + 1))
        hits = [i for i in range(n_e) if (row[0] >> i) & 1]
        epochs = len({years[i] for i in hits})
        la, lb = half_lift(row, hA), half_lift(row, hB)
        scored.append({"name": name, "order": order, "eh": eh, "ch": ch,
                       "er": eh / n_e, "cr": ch / n_c,
                       "lift": smoothed_lift(eh, n_e, ch, n_c),
                       "epochs": epochs, "liftA": la, "liftB": lb,
                       "replicates": la > 1.0 and lb > 1.0,
                       "independent": epochs >= MIN_EPOCHS})
    scored.sort(key=lambda r: -r["lift"])

    say("TOP 20 BY RAW LIFT — with the independence and replication columns")
    say("  epochs = distinct years; A/B = 2-year-block split-half lifts.")
    say("  A pattern failing either column is pseudo-replication, not a finding.")
    say(f"  {'#':>3} {'lift':>6} {'n':>4} {'ep':>3} {'A':>6} {'B':>6} {'ok':>3}  pattern")
    for i, r in enumerate(scored[:20], 1):
        ok = "yes" if (r["replicates"] and r["independent"]) else "NO"
        say(f"  {i:>3} {r['lift']:>6.3f} {r['eh']:>4} {r['epochs']:>3} "
            f"{r['liftA']:>6.3f} {r['liftB']:>6.3f} {ok:>3}  {r['name'][:46]}")
    say()
    survivors = [r for r in scored if r["replicates"] and r["independent"]]
    say(f"PATTERNS SURVIVING INDEPENDENCE + REPLICATION: {len(survivors)} "
        f"of {len(scored)}")
    for r in survivors[:10]:
        say(f"    lift {r['lift']:.3f}  n={r['eh']:>3}  epochs={r['epochs']:>3}  "
            f"A/B {r['liftA']:.2f}/{r['liftB']:.2f}  {r['name'][:44]}")
    say()

    # ---- family-wise null over the ENTIRE searched space ----
    say("FAMILY-WISE NULL (over every pattern searched, not just the winner)")
    # Within each block, which of (1 event + k controls) is labelled the event?
    # Build a mask per slot: bit i set means block i nominated that slot. Then
    # the permuted event count is sum_s popcount(row[s] & mask[s]), and the
    # permuted control count is the block total minus it — so every block keeps
    # its own composition and era/geography cannot leak into the null.
    rng = random.Random(SEED + 1)
    n_slots = CONTROLS_PER_EVENT + 1
    maxes = []
    for _ in range(N_PERM):
        masks = [0] * n_slots
        for i in range(n_e):
            masks[rng.randrange(n_slots)] |= 1 << i
        best = 0.0
        for name, row, order in space:
            total = sum(row[s].bit_count() for s in range(n_slots))
            eh = sum((row[s] & masks[s]).bit_count() for s in range(n_slots))
            L = smoothed_lift(eh, n_e, total - eh, n_c)
            if L > best:
                best = L
        maxes.append(best)
    maxes.sort()
    obs = scored[0]["lift"]
    fw_p = sum(1 for m in maxes if m >= obs) / len(maxes)
    say(f"  observed max lift : {obs:.3f}  [{scored[0]['name'][:52]}]")
    say(f"  null median       : {maxes[len(maxes)//2]:.3f}")
    say(f"  null 95th pct     : {maxes[int(0.95*len(maxes))]:.3f}")
    say(f"  FAMILY-WISE p     : {fw_p:.4f}")
    exp = scored[0]["cr"] * n_e
    say(f"  count check       : {scored[0]['eh']} firings vs {exp:.1f} expected "
        f"= {poisson_sigma(scored[0]['eh'], exp):.2f} sigma")
    say()
    best_surv = survivors[0] if survivors else None
    supported = bool(fw_p < 0.05 and best_surv
                     and best_surv["lift"] >= obs - 1e-9)
    say("VERDICT")
    say(f"  family-wise p          : {fw_p:.4f}")
    say(f"  raw winner             : {scored[0]['name'][:50]}")
    say(f"    epochs {scored[0]['epochs']}, halves "
        f"{scored[0]['liftA']:.2f}/{scored[0]['liftB']:.2f} -> "
        f"{'replicates' if scored[0]['replicates'] else 'DOES NOT REPLICATE'}")
    if best_surv:
        say(f"  best surviving pattern : {best_surv['name'][:50]}")
        say(f"    lift {best_surv['lift']:.3f}, epochs {best_surv['epochs']}, "
            f"halves {best_surv['liftA']:.2f}/{best_surv['liftB']:.2f}")
    else:
        say("  best surviving pattern : NONE")
    say()
    say(f"  ==> {'SUPPORTED' if supported else 'NOT SUPPORTED'} "
        f"(bar: {claim.verdict}, AND the winner must replicate)")
    if not supported and fw_p < 0.05:
        say("      The family-wise p clears its bar, but the pattern that")
        say("      achieved it is concentrated in a handful of epochs and")
        say("      fails split-half replication. The permutation treats each")
        say("      event as independent; for a slow-body predicate they are")
        say("      not. The p-value is measuring pseudo-replication.")
    say()

    with open(OUT / "patterns.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["rank", "order", "pattern", "lift", "event_hits",
                    "event_rate", "control_rate"])
        for i, r in enumerate(scored, 1):
            w.writerow([i, r["order"], r["name"], f"{r['lift']:.4f}", r["eh"],
                        f"{r['er']:.4f}", f"{r['cr']:.4f}"])
    say(f"wrote {OUT / 'patterns.csv'} ({len(scored)} patterns)")

    write_toml(scored[:20], survivors, cond_map, fw_p, supported, n_e, say)
    (OUT / "report.txt").write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT / 'report.txt'}")


def write_toml(top, survivors, cond_map, fw_p, supported, n_e, say) -> None:
    """Emit the mined patterns in the project's own rule schema, each labelled
    with its measured status. Patterns that fail are written WITH their
    failure, never dropped — mined-triggers.toml was retired for that."""
    status = "SUPPORTED" if supported else "NOT SUPPORTED"
    out = [
        "# ATLAS-MINED PATTERNS — generated by scripts/pattern_mine_m7.py",
        f"# Run {dt.date.today().isoformat()} over every M7+ quake in the tree",
        f"# ({n_e} declustered post-1900 events, unified across 3 catalogs).",
        "#",
        "# STATUS OF THIS ENTIRE FILE: " + status,
        "# Family-wise p over the whole searched space (singles + pairs +",
        f"# triples) = {fw_p:.4f}. The bar was p < 0.05.",
        "#",
        "# READ THIS BEFORE USING ANY RULE BELOW. These are the highest-lift",
        "# patterns found, and a lift is not evidence: screening this many",
        "# combinations produces large lifts from noise by construction. The",
        "# per-pattern numbers are recorded so the file is auditable, NOT",
        "# because they are significant. mined-triggers.toml was retired for",
        "# exactly this mistake and its three rules still carry the scars.",
        "#",
        "# They are kept loadable so they can be swept, watched and graded",
        "# forward like any other rule — as a falsifiable experiment, not as",
        "# doctrine. Doctrine lives in doctrine-triggers.toml.",
        "",
    ]
    if survivors:
        out.insert(len(out) - 1,
                   f"# {len(survivors)} pattern(s) also survived independence "
                   f"(>= {MIN_EPOCHS} distinct epochs) and split-half\n"
                   "# replication; they are marked SURVIVOR in their description.")
    else:
        out.insert(len(out) - 1,
                   "# NOTE: ZERO patterns survived the independence and split-half\n"
                   "# replication filters. Every rule below is recorded for audit\n"
                   "# only. None of them should be used to predict anything.")
    surv_names = {r["name"] for r in survivors}
    written = 0
    for i, r in enumerate(top, 1):
        parts = r["name"].split(" + ")
        conds = [cond_map.get(p) for p in parts]
        if any(c is None for c in conds):
            continue           # detector-only predicate (vyuha) has no condition
        out.append("[[rule]]")
        out.append(f'name = "atlas-{i:02d}"')
        tag = "SURVIVOR" if r["name"] in surv_names else "FAILS REPLICATION"
        desc = (f"MINED — {tag}. family-wise p = {fw_p:.3f}. "
                f"lift {r['lift']:.3f} on {r['eh']}/{n_e} events "
                f"({100*r['er']:.1f}%) vs {100*r['cr']:.1f}% of era-matched "
                f"controls; {r['epochs']} distinct epochs; split-half lifts "
                f"{r['liftA']:.2f}/{r['liftB']:.2f}. Order-{r['order']}: {r['name']}")
        out.append(f'description = "{desc}"')
        out.append("conditions = [")
        for c in conds:
            items = ", ".join(
                f'{k} = {_toml_val(v)}' for k, v in c.items())
            out.append(f"  {{ {items} }},")
        out.append("]")
        out.append("")
        written += 1
    TOML_OUT.write_text("\n".join(out) + "\n")
    say(f"wrote {TOML_OUT} ({written} rules, all labelled {status})")


def _toml_val(v):
    if isinstance(v, str):
        return f'"{v}"'
    if isinstance(v, list):
        return "[" + ", ".join(_toml_val(x) for x in v) + "]"
    return repr(v)


if __name__ == "__main__":
    main()
