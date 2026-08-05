# Plan — what is done, what is open, and what is blocked

Status 2026-08-05, end of session. Companion to `FRAMEWORK.md` (the theory),
`WATCHLIST.md` (registered forward windows), `data/README-floods.md` (the
flood corpora), and `.claude/tasks/ASTGRAF_TOOL.md` (every ruling, dated).
248 tests passing, from any working directory.

## 1. The one-line state

**The engine predicts *when* with tested precision and cannot predict *where*
at all.** Both halves are measured, not impressions: every taught instant
reproduces to 1–2 minutes, and **eight independent channels have been built
and graded null** — six location families, the mining channel, the dwell
doctrine, and now the taught flood signature tested in its own category —
each with a power check proving the instrument could see the effect it
failed to find.

## 2. Closed — do not reopen without new input

| Channel | Passes | Verdict |
|---|---|---|
| Location — rotation spots | full 0–360° sweep per giant | flat everywhere |
| Location — Ascendant rules | cell / lord / nakshatra / sub | p = 0.12–0.99 |
| Location — site angles | leave-one-out epicenter controls | z ≈ 0 |
| Location — tangent ring | 18 radius bins vs 20 nulls | flat; 90° bin at 0.997 |
| Location — cell→region table | pre-registered, his own design | p = 0.166 |
| Statistical mining | 3 passes, richest space 380 predicates | max lift 1.705 vs null 1.748, p = 0.65 |
| Dwell doctrine | trigger + magnitude halves | vacuous; and dead on held-out M6.0–6.99 |
| **Taught flood signature** (Neptune on Ketu, tested in its OWN category) | 1,886 declustered flood events, era-matched controls | **lift 1.012, p = 0.57** |
| **Predict.pdf's band trigger** (Moon+Ketu+Mars, its headline claim) | 1,435 quakes exact-instant + 1,886 floods, era-matched | **lift 1.804, p = 0.069** — fails the bar; rests on 12 firings vs 7 expected (1.4 σ). Floods point the other way (0.937) |

The geometric location route is exhausted **by derivation**, not merely by
testing: a slow–slow crossing cannot define a meridian (crossings last days;
meridians sweep 360°/day), so geometric longitude needs a fast body — and
every fast-body channel is tested and null. Latitude has one geometric
source, declination, capped at 23.71° for the located set against Nepal's
28.23°N.

## 3. Runnable now — nothing further needed from NU

The flood corpora (2,812 events: 88 curated global + 2,724 HANZE Europe)
unblocked four tests that were previously impossible. **All four are
pre-registration candidates** — write the design, commit it, then run.

### 3.1 The long-cycle clock test — highest value

**Question.** NU's flood family recurs at a Uranus–Neptune period. Three
candidate clocks are on record: Neptune tropical **163.5 y**, Neptune
sidereal **164.5 y**, Uranus–Neptune synodic **171.0 y**. Which one do the
records support?

**Data available.** 2,757 dated flood events since 1871; 326 of them in the
1988–1998 window around the 1993 triple conjunction (Feb 2 / Aug 19 / Oct 25,
all in Poorvashada pada 4).

**Design sketch.** Phase-fold flood incidence against each candidate period,
measure concentration, compare to the incidence baseline. **The hard part is
the null, and it must be built first:** flood reporting density rises steeply
with time and toward Europe, so a raw fold will find structure that is
archival, not astronomical. Detrend on reporting rate before folding, and
use the same catalogue as its own null.

⚠️ **Honest limit.** A 155-year record covers **less than one cycle** of any
candidate. This test can rule a clock *out* by phase mismatch; it cannot
confirm one. Say so in the pre-registration.

### 3.2 The taught flood signature — DONE 2026-08-05, null

Ran and closed the same day it became possible. 1,886 declustered
day-precision flood events against 9,430 era-matched controls:
**real-Neptune on Ketu fires at 0.0159 of flood dates and 0.0161 of control
instants — lift 1.012, p = 0.57**, sitting exactly on the null median. No
secondary variant survives multiplicity (family max 1.353, p = 0.38).
Power: planting the predicate into just 2% of events gives lift 2.22 at
p = 0.0000, so the instrument is not blind.

**This mattered because it was the first test of a taught rule in the
category it was taught in** — every prior grading used the quake corpus, so
"wrong catalogue" was a live excuse. It is now spent.

### 3.2b The band trigger — DONE 2026-08-05, does not clear its bar

Predict.pdf's headline rule, given its first properly powered test (it had
been scored once, on 31 episodes). Quakes with exact instants are the primary
corpus because the rule contains the Moon, which crosses a full band in a day.
**Lift 1.804 at p = 0.069** — the closest any primary predicate has come in
this project, and still short of the pre-registered p < 0.05.

⚠️ Do not read it as a near miss. The result rests on **12 firings against 7.0
expected — a 1.4 σ excess**. The predicate is rare (0.84% of events), so
n = 1,435 still yields single digits. **It is decidable with more events**:
n ≈ 3,000 → 2.3 σ, n ≈ 6,000 → 3.2 σ, n ≈ 12,000 → 4.6 σ if the effect is
real. An M6+ quake corpus would settle it, and we already know how to fetch
one (12,212 rows came from USGS FDSN for the dwell test).

### 3.3 Category-tagged recurrence, graded

`astgraf-recur --category flood` now has events to grade against. Do flood
anchors' patterns re-form near flood dates more than chance? The 130-year
sweep found zero re-formations for quake anchors — this asks whether that
holds for a category with 30× the event density.

### 3.4 Site channel in its own category — *limited*

⚠️ Only **13 events** are day-precision, modern, *and* point/city located.
HANZE gives country centroids only, which cannot support a site test. This
is underpowered by construction; run it for completeness, not for a verdict,
and state n = 13 in the pre-registration.

## 4. Open engineering debts

| # | Debt | Impact | Fix |
|---|---|---|---|
| 1 | ~~21 tests fail from the repo root~~ | — | **CLOSED 2026-08-05**: `triggers._resolve_rules_path` falls back to the package root for bare filenames (explicit paths still raise); the GRF test resolves from `__file__`. 248 pass from both directories |
| 2 | **HANZE has country-centroid locations only** | No site/point tests on 2,724 of 2,812 flood events | Geocode NUTS-3 → centroid, or find a DFO mirror (its own URLs are HTTP 410 Gone as of 2026-08-05) |
| 3 | **Flood corpora ship undeclustered with no completeness model** | Any test on them is biased toward recent Europe (reporting density rises ~12× across the span) | Partially handled: §3.2 declustered in-script (3-day temporal) and used era-matched controls. A reusable declusterer + reporting-rate model is still needed before §3.1 |
| 4 | **Canon has no lunar latitude** (`PX = LL + ML`, no `sin(F)` series) | Moon declination is identically 0 ecliptic latitude; caps Moon sub-points at 23.44° instead of 28.58° | Not a bug — canon fidelity. Any Moon-declination work needs a clearly-labelled modern addition and an NU ruling |
| 5 | **Jupiter/Saturn offsets are provisional** (3.3363593021° / 7.8672056771°) | Under rule v3 they set spot longitudes too | **NU ruled 2026-08-05: not needed for now, current values stand.** Parked, not blocking |
| 6 | **Pre-1582 flood dates are Julian, unconverted** | Medieval rows carry a ~10-day offset | Irrelevant while engine drift already disqualifies pre-1700 events; fix if that ever changes |
| 7 | **firecrawl exhausted** (−1 / 1,000 credits) | The news/outcome channel for flood and biological categories cannot run | Credits, or a curl-able alternative |

## 5. Blocked on NU — ranked by what each unlocks

| # | Input | Unlocks |
|---|---|---|
| 1 | **The latitude question, put to the author** | The only thing that could reopen location. His recipe has three longitude mechanisms and one latitude mechanism capped at 23.71°, against Nepal's own 28.23°N. Six families died against that wall |
| 2 | **Navamsam event-reading rules** | The one generated output the engine still cannot interpret for events |
| 3 | **The Java-family reading** | 2040 falls in Chitra (not a member sector); the next member-sector return is 2060 in Kritika. Which carries the family's claim? And is the 1941 Bharani triple a member — was there a Java-arc event in 1940–41? |
| 4 | **Abhijit-28 decision** | Unparks the 28-equal ladder behind `--ladder 28` |
| 5 | **7-level Vimshottari lords** | Completes the 1764 instant ladder |
| 6 | **`precess.mcd`** | Cross-check for the precession clock |

## 6. Running on its own — the autumn season

The first live forward test in the project's history. Registered instants,
verbatim commands in `WATCHLIST.md`, graded automatically with spatial base
rates:

| Run on | Grades |
|---|---|
| **2026-10-07** | Sept 30 – Oct 4 (real-Nep ☍ Mercury, exact Oct 2 04:43 UT) |
| **2026-10-22** | Oct 13 – 19 (real-Ura △ Sun, exact Oct 16 09:19 UT) |
| **2026-11-06** | Nov 2 – 3 (band trigger, tightest Nov 3 01:00 UT) |
| **2026-11-23** | Nov 15 – 20 (anchor-recurrence, alaska-1964 row, annotated) |

⚠️ Read the base rates with the results: the first window's spot sits in the
equatorial Pacific with `spatial_chance` 0.0000 — a hit there would be
extraordinary, a clear is near-certain and carries almost no information.
**The instants are the claim; the spots are a registered experiment.**

## 7. Standing method rulings

1. **Pre-register cell, direction and statistic before running**, and commit
   the pre-registration before the result exists.
2. **Every null needs a power check.** A null without demonstrated power is
   silence, not evidence.
3. **Replication is not confirmation.** The dwell finding survived three kill
   attempts and two independent replications and was still false. Only
   held-out data settled it.
4. **Held-out sets must be strictly disjoint** (M6+ contains M7+; the test
   used M6.0–6.99).
5. **Honest negatives stay on the record**, with their numbers.
6. **Verify before claiming.** Check exit codes directly; regenerate
   artifacts with their generators; reconcile completion claims item by item.
