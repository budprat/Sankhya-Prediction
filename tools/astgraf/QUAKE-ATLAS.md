# The Quake Atlas — every catalog, every chart, every pattern graded

Generator: `scripts/quake_atlas.py --corpus all` (~11 min). Run 2026-08-05.

**13,339 event charts** cast across **all four quake catalogs in the tree**,
each at its own epicenter at the catalog instant, plus **40,017 era-matched
control charts** — 53,356 charts in total.

| Corpus | raw | declustered ≥1900 | selected on |
|---|---:|---:|---|
| `usgs-m7-1850-2020` | 1,548 | **1,435** | magnitude (M7.0–9.5) |
| `usgs-m6-1900-2020` | 12,212 | **10,324** | magnitude (M6.0–6.99) |
| `quakes-ncei-deaths` | 1,981 | **1,553** | **deaths** |
| `quakes-historical` | 39 | **27** | curation (three tiers) |

Declustering is 7 d / 500 km keep-largest throughout. The deaths-selected and
curated files carry no magnitude column, so for them keep-largest degenerates
to keep-earliest — stated, not hidden.

## Artifacts

| Artifact | Location | Tracked |
|---|---|---|
| M7+ charts (1,435 × 87 cols) | `data/quake-charts-m7.csv` | ✅ |
| Deaths-selected charts (1,553) | `data/quake-charts-ncei.csv` | ✅ |
| Curated-majors charts (27) | `data/quake-charts-hist.csv` | ✅ |
| M6 charts (10,324) | `out/quake-atlas/m6/charts.csv` | ❌ 7.7 MB, regenerable |
| 16 M8.5+ wheels | `charts/great-quakes/` | ✅ |
| 10 deadliest-event wheels | `charts/deadliest/` | ✅ |
| All 13,339 wheels | `out/quake-atlas/*/wheels/` | ❌ 117 MB |
| Census, graded tables, reports | `out/quake-atlas/<corpus>/` | ❌ |

Regenerate everything: `uv run python scripts/quake_atlas.py --corpus all`.

---

## The headline: four catalogs, four nulls

Each screen is the doctrine's **full predicate vocabulary** — pair aspects,
real-position (`rsep:`) aspects, 28-band occupancy, band stacking,
Moon–Ketu–Mars spread, vyuha, giant-on-node — graded against era-matched
controls, with the **family-wise maximum-lift permutation null** as the bar.

| Corpus | n | predicates | best lift | null median | **family-wise p** | verdict |
|---|---:|---:|---:|---:|---:|---|
| M7+ | 1,435 | 524 | 1.665 | 1.609 | **0.302** | not supported |
| **M6.0–6.99** | **10,324** | 513 | 1.233 | 1.188 | **0.080** | not supported |
| Deaths-selected | 1,553 | ~520 | 1.686 | 1.569 | **0.162** | not supported |
| Curated majors | 27 | — | 11.448 | 11.448 | 0.610 | *uninterpretable* |

**Every screen carries a power check and every one passes it.** Planting an
effect into just 2% of events recovers it at p < 0.0001 in all three real
corpora (M7+ lift 3.22, M6 2.32, deaths 3.14). These are nulls, not blindness.

⚠️ **The 27-event curated corpus is uninterpretable, not null.** Its
"observed max" and its null median are the *same number* (11.448) — with
n = 27 and zero control hits the smoothed lift is dominated by the +1
smoothing, and even a 10% planted effect only reaches p = 0.004. Reported
for completeness; it carries no evidential weight in either direction.

---

## Result 1 — The band trigger is settled, and it was a small-count fluctuation

`PLAN.md` §3.2c called this "the one open question data can settle". It is now
closed. Pre-registered in `scripts/band_trigger_m6.py`, **committed before the
run** (git timestamp `11:23:59Z`, results at `11:26`).

| | M7+ (n = 1,435) | **M6.0–6.99 (n = 10,324)** |
|---|---|---|
| P1 primary | lift 1.804, p = 0.069 | **lift 0.915, p = 0.76** |
| firings vs expected | 12 vs 7.0 (**+1.4 σ**) | **38 vs 42.4 (−0.71 σ)** |
| P2 grid mode | — | 0.759 (11 vs 15.6) |
| P3 giant-escalated | — | 1.091 (11 vs 10.8) |

Wrong direction on the primary, wrong direction on grid mode, flat on
escalated. Family-wise p = 1.00. Power: a 2% planted effect gives lift 5.75
at p < 0.0001.

**And the atlas shows exactly what happened at M7.** The trigger's firing rate:

- M7+ events: 12 / 1,435 = **0.84%**
- M6 events: 38 / 10,324 = **0.37%**
- M6 era-matched controls: 212 / 51,620 = **0.41%**

The true base rate is ~0.41%. The M7+ figure of 0.84% was a **2× upward
fluctuation on twelve events** — which is precisely what "1.4 σ" was telling
us at the time. The rule's most promising result dissolves into counting
statistics.

Registered in advance and still binding: a null at M6 does not refute a
mechanism that only switches on above M7. But since the M7+ result was itself
1.4 σ, the honest summary is **unsupported at every magnitude tested** — not
*refuted*.

## Result 2 — Selecting on deaths instead of magnitude changes nothing

`data/README-floods.md` and `scripts/deadliest_structure.py` raise a real
objection: the pinned corpus is **magnitude**-selected, but the doctrine
speaks about *catastrophe*. Tangshan (Mw 7.5, ~100,000+ dead) and Haiti
(Mw 7.0, ~100,000+ dead) are minor by seismic moment and enormous by
consequence. `deadliest_structure.py` could only test this at n = 12.

With 1,553 deaths-selected events, the two populations are now directly
comparable — and they are **indistinguishable**:

| Doctrine rule | deaths-selected | magnitude-selected |
|---|---:|---:|
| uranus-neptune-conjunction | 3.0% | 2.9% |
| nodes-doubly-occupied | 1.4% | 1.5% |
| neptune-on-ketu | 1.6% | 1.1% |
| band-trigger | 0.8% | 0.8% |
| jupiter-saturn-conjunction | 0.6% | 0.6% |
| nepal-double | 0.1% | 0.1% |

Structural states likewise: mean contacts per event 9.21 vs 9.02; band-stack
distributions match to within a percentage point at every height.

**The "wrong population" excuse is now spent.** It was the last substantive
one available — the flood corpus closed "wrong category" (RESULTS #9), M6
closed "no held-out data" (#11), and this closes "wrong selection variable".

## Result 3 — The census is dominated by sky base rates, and the controls prove it

The descriptive census throws up regularities that look compelling until you
put a control rate beside them:

| Predicate | event rate | **control rate** | lift |
|---|---:|---:|---:|
| `band:Uranus=22` (M7+) | 6.5% | **6.6%** | **0.996** |
| `band:Neptune=24` (M7+) | 6.6% | **6.4%** | **1.032** |
| `sep:Sun-Mercury@conj` (M7+) | 7.2% | **9.2%** | **0.783** |

Uranus's most-occupied band holds 1.8× the uniform share — and exactly the
same share of ordinary moments in the same years. That is an 84-year orbital
period sampled over 120 years, not seismicity. Sun ☌ Mercury is *the single
most frequent contact in the entire census* and is **rarer** at earthquakes
than at control instants, because Mercury never exceeds ~28° elongation.

Across all 524 M7+ predicates the **median lift is 1.013** with 53% above
1.0 — a null distribution centred on 1.

**The multiplicity trap, concretely.** The M6 winner `rsep:Saturn-Mars@opp`
posts a raw p of **0.002** and a 2.84 σ count excess (232 firings vs 188.7).
It looks like a discovery. Against the family-wise null over the same 513
predicates it is unremarkable: screening that many noisy predicates typically
produces a best of 1.188, and this one reached 1.233. Per-predicate p-values
in a screen this wide are not evidence.

## Result 4 — Rarity census of the doctrine rules

Not a claim, but the number the forward watchlist needs:

| Rule | M7+ | M6 | deaths |
|---|---:|---:|---:|
| Chatur Vyuham | **0 / 1,435** | 3 / 10,324 | 1 / 1,553 |
| nepal-double | 1 / 1,435 | — | 2 / 1,553 |
| band-trigger (catastrophic) | 3 / 1,435 | 11 / 10,324 | 4 / 1,553 |

The fourfold array is genuinely once-in-a-century rare, as claimed — it simply
does not coincide with earthquakes when it fires.

---

## Verdict

**Not supported, on every quake catalog in the project.** Thirteen thousand
event charts, four independent screens, one pre-registered confirmatory test,
and every power check passing. No configuration in the doctrine's own
vocabulary separates earthquake instants from era-matched ordinary instants —
at M6, at M7+, or when events are selected by human death toll instead of
seismic moment.

### What survives

- **The chart record.** 13,339 verified event charts, each with the
  epicenter's own Ascendant/MC, is a reusable asset for any future test.
- **The taught instances**, which reproduce to the minute. Those are
  retrodictions of specific charts, untouched by a screen over catalogs.
- **The rarity census**, which quantifies how selective the doctrine rules are.

### What is now closed

The last question answerable with data alone. What remains open in `PLAN.md`
§5 is blocked on NU — the latitude question above all — not on compute or
corpus.

### Two honest caveats

1. The four-corpus screen was **exploratory at the user's request, not
   pre-registered**. It found nothing, so the distinction costs nothing here;
   it would have mattered enormously had a winner cleared the bar. The M6
   band-trigger test *was* pre-registered and is the only confirmatory result
   in this document.
2. **The M6 holdout is now spent.** It was the project's only strictly
   disjoint band and has been used twice (dwell, RESULTS #8; band trigger,
   #11). Future confirmatory work needs a genuinely new corpus.
