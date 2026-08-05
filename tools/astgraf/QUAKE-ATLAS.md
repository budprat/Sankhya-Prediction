# The M7+ Quake Atlas — every event chart, and every pattern graded

Generator: `scripts/quake_atlas.py` (~70 s). Run 2026-08-05.

**Corpus.** USGS M7+ 1850–2020, restricted to post-1900 (engine drift
disqualifies earlier events) and declustered 7 d / 500 km keep-largest:
**1,435 mainshocks**, magnitude 7.0–9.5, median 7.3.

**What was cast.** One full chart per event, **at the epicenter** at the
catalog instant — 1,434 of 1,435 sited (one polar event falls past the
canon's cusp-chain limit at 66.56° and is cast site-free).

## Artifacts

| Artifact | Location | Tracked |
|---|---|---|
| All 1,435 event charts, 87 columns | `data/quake-charts-m7.csv` | ✅ |
| M8.5+ chart wheels (16 SVGs) | `charts/great-quakes/` | ✅ |
| All 1,435 chart wheels | `out/quake-atlas/wheels/` | ❌ (12 MB, regenerable) |
| Descriptive census | `out/quake-atlas/census.txt` | ❌ |
| Full graded table (524 predicates) | `out/quake-atlas/lifts.csv` | ❌ |
| Grading report | `out/quake-atlas/patterns.txt` | ❌ |

Each chart row carries: 13 body longitudes + retrograde flags, nakshatra /
pada per body, 28-band occupancy, the four giants' doctrinal real positions
and their bands, band stack height, Moon–Ketu–Mars spread, Chatur Vyuham
state, band-trigger level, which doctrine rules fired, and every
doctrine-orb (3°) contact with its separation.

---

## Part A — The census (descriptive; no claim)

### Band occupancy — the most-occupied band per body

| Body | Top band | n | observed | uniform |
|---|---|---:|---:|---:|
| Sun | 25 Satabhisa | 66 | 4.6% | 3.6% |
| Moon | 18 Jyestha | 71 | 4.9% | 3.6% |
| Rahu | 16 Visaka | 69 | 4.8% | 3.6% |
| Ketu | 2 Bharani | 69 | 4.8% | 3.6% |
| Mercury | 18 Jyestha | 66 | 4.6% | 3.6% |
| Venus | 6 Rudra | 71 | 4.9% | 3.6% |
| Mars | 17 Anuradha | 66 | 4.6% | 3.6% |
| Jupiter | 18 Jyestha | 72 | 5.0% | 3.6% |
| Saturn | 28 Revathy | 74 | 5.2% | 3.6% |
| **Uranus** | **22 Uthrashada** | **93** | **6.5%** | 3.6% |
| **Neptune** | **24 Dhanishta** | **94** | **6.6%** | 3.6% |

### Most frequent doctrine-orb contacts

| Contact | n | % of events |
|---|---:|---:|
| Sun ☌ Mercury | 103 | 7.2% |
| Mercury ☌ Venus | 72 | 5.0% |
| Sun ☌ Venus | 69 | 4.8% |
| Moon □ Uranus | 65 | 4.5% |
| real-Jupiter □ Rahu / Ketu | 65 | 4.5% |
| real-Uranus △ Sun | 64 | 4.5% |
| real-Saturn △ Neptune | 64 | 4.5% |

### Structural states

- **Contacts per event:** mean 9.02 (min 1, max 24)
- **Band stack height:** 1→6.8% · 2→70.3% · 3→20.3% · 4→2.5% · 5→0.1%
- **Chatur Vyuham:** fires at **0 of 1,435** events
- **Band trigger (proximity):** 9 disruptive, 3 catastrophic — 0.8%
- **Doctrine rules fired:** Uranus–Neptune conj 2.9% · nodes-doubly-occupied
  1.5% · Neptune-on-Ketu 1.1% · band-trigger 0.8% · Jupiter–Saturn conj 0.6% ·
  **nepal-double 1 event (0.1%)**

---

## Part B — Grading (the same patterns, vs era-matched controls)

**Design.** 4,305 era-matched control charts (3 per event, ±365 d excluding
±7 d), add-one smoothed lift, within-block permutation null, power curve —
all through `astgraf.validation`. 679 predicates screened; 524 clear the 2%
event-rate floor.

### The two census standouts are sky base rates, not signal

This is the whole reason controls exist:

| Predicate | event rate | **control rate** | lift |
|---|---:|---:|---:|
| `band:Uranus=22` | 6.5% | **6.6%** | **0.996** |
| `band:Neptune=24` | 6.6% | **6.4%** | **1.032** |
| `sep:Sun-Mercury@conj` | 7.2% | **9.2%** | **0.783** |

Uranus at 6.5% looked like a 1.8× enrichment over uniform. Ordinary
moments in the same years show **6.6%** — the excess is Uranus's 84-year
period making its band distribution lumpy over a 120-year window, exactly
the confound `matrix.py` warns about. And Sun ☌ Mercury, *the most frequent
contact in the entire census*, is **less** common at earthquakes than at
control instants: Mercury never exceeds ~28° elongation, so the conjunction
is common everywhere.

### The top of the screened space

| Predicate | lift | ev% | ctl% | n | p (raw) |
|---|---:|---:|---:|---:|---:|
| `sep:Moon-Venus@conj` | 1.665 | 2.0% | 1.2% | 29 | 0.028 |
| `band:Moon=18` | 1.575 | 4.9% | 3.2% | 71 | 0.000 |
| `sep:Sun-Neptune@conj` | 1.549 | 2.1% | 1.4% | 30 | 0.048 |
| `rsep:Neptune-Mercury@opp` | 1.499 | 2.0% | 1.4% | 29 | 0.036 |
| `sep:Saturn-Uranus@opp` | 1.499 | 2.9% | 1.9% | 41 | 0.012 |

Those raw p-values look like a discovery. They are not — see below.

### The family-wise bar

Permuting block labels 500× across all 524 predicates and recording the
**maximum** lift reached each time:

```
observed max lift : 1.665   [sep:Moon-Venus@conj]
null median       : 1.609
null 95th pct     : 1.823
FAMILY-WISE p     : 0.302
```

The best predicate out of 524 reaches 1.665. Screening 524 *pure-noise*
predicates typically produces a best of **1.609**, and 1.823 five percent of
the time. The winner is unremarkable against its own screen. Its count check
is 29 firings vs 17.7 expected — **2.10 σ**, on the single largest of 524
cells.

The full distribution says the same thing: across all 524 graded predicates
the **median lift is 1.013** and 53% sit above 1.0. That is a null
distribution centred on 1.

### The screen is not blind

| plant | lift | p |
|---|---:|---:|
| 10% of events | 9.602 | 0.0000 |
| 5% | 5.606 | 0.0000 |
| **2%** | **3.219** | **0.0000** |

An effect present in just **2%** of events would surface at lift 3.2 and
p < 0.0001. Nothing of that size is there.

### Magnitude stratification

| Tier | n | contacts/event | stack | M–K–M spread |
|---|---:|---:|---:|---:|
| M7.0–7.4 | 981 | 9.04 | 2.20 | 137.8° |
| M7.5–7.9 | 360 | 9.04 | 2.16 | 136.7° |
| M8.0–8.4 | 78 | 8.69 | 2.23 | 136.4° |
| M8.5+ | 16 | — | — | too few to grade |

Flat. No monotone trend — which is the shape a real magnitude coupling would
take, and the shape `RESULTS.md` #8 found on M7+ before it died on held-out
M6 data.

---

## Verdict

**NOT SUPPORTED** at the pre-stated bar (family-wise p < 0.05).

No configuration in the doctrine's own predicate vocabulary — 524 screened
aspect, real-position, band-occupancy and structural predicates — separates
M7+ mainshock instants from era-matched ordinary instants. The instrument
demonstrably could have found an effect present in 2% of events.

This is the **fourth** independent screen over this corpus to return null
(`RESULTS.md` #1 records three). It differs from those in using era-matched
rather than time-uniform controls, adding band-occupancy and structural
predicates to the space, and casting charts at the epicenter rather than
site-free. Same answer.

### What the atlas is still good for

The null applies to *screening for new patterns*. It does not touch:

- **The chart record itself** — 1,435 verified event charts are now a
  reusable asset for any future test, including ones needing the epicenter's
  own Ascendant/MC.
- **The taught instances**, which reproduce to the minute and are
  retrodictions, not screen results.
- **The rarity census** — Chatur Vyuham firing at 0/1,435 and nepal-double
  at 1/1,435 quantifies how selective those doctrine rules are, which is
  information the forward watchlist needs regardless of this verdict.

### One honest caveat

This run was **exploratory, at the user's request — not pre-registered**.
Under the project's own standing rules that makes anything here a lead
requiring held-out confirmation, never a result. Since it found nothing, the
distinction costs nothing this time; it would have mattered enormously had
the winner cleared the bar.
