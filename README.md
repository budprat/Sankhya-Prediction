# astgraf

**A prediction program**: event timing through transit patterns — aspect
geometry, 252-division horary crossings, and the 25,739-year precession
clock. Built on the family BASIC suite's transit-graph pair, ported verbatim:
**ASTGRAF.BAS** (positions over N periods → `ASTROC.GRF`) + **GRAPHDO.BAS**
(SCREEN 12 cosine plot). Same computation core, modern I/O. Natal chart
reading stays in the SankhyaHoroscope app; this tool predicts.

Documents: theory in `FRAMEWORK.md` · forward windows in `WATCHLIST.md` ·
trigger rules in `doctrine-triggers.toml` / `mined-triggers.toml` ·
training corpus in `data/` · decision ledger in `.claude/tasks/ASTGRAF_TOOL.md`.

## Run

```bash
cd tools/astgraf
uv run astgraf --year 2000 --month 1 --day 1 --time 12:00 \
  --unit year --step 1 --count 17 \
  --utc-offset +05:30 --lon 76:57E --lat 28:48N \
  --out out/2000-2016
```

Units: `year | month | day | hour`, any step (60 hourly steps resolve
conjunctions to the minute; `--unit year --step 800 --count 60` spans 48,000
years). `--tropical` disables the ayanamsa; `--koch` uses the real-obliquity
Ascendant path; `--style cosine` reproduces the heritage GRAPHDO fold.

## The 60-period drill (NU's canonical workflow)

Sixty periods for max detail; the unit is 1 to any number — day×2 = a
120-day spread, year×800 = 48,000 years. Coarse lens → find the crossing →
finer lens → locate. Each stage is one command:

```bash
# LENS 1 — 60 x 1 year, slow bodies: find the crossings of an era
uv run astgraf --year 1960 --unit year --step 1 --count 60 \
  --aspect-bodies Uranus,Neptune,Rahu,Ketu --out out/lens1

# LENS 2 — 60 x 12 hours around a found crossing, with the spot
uv run astgraf --year 2015 --month 1 --day 16 --unit hour --step 12 --count 60 \
  --aspect-bodies Uranus,Ketu --locate --out out/lens2
```

Bisection refinement makes the lenses agree to the minute (both give the
2015-01-31 08:17 UT Uranus–Ketu conjunction) and `--locate` applies the
light-time rotation — Jup 40 min, Sat 80, Ura 150, Nep 240, west from the
culmination meridian — to give the spot (here 80.55E 4.67N, off southern
Sri Lanka). One caveat: a coarse lens only resolves pairs whose relative
motion per division stays under ~90° — at yearly steps use the slow bodies;
descend the lens for the fast ones (each planet comes one by one).

## Outputs

| File | Replaces | Content |
|---|---|---|
| `positions.csv` | `ASTROC.GRF` | one row per period, 13 body longitudes |
| `positions.json` | — | full precision + params + retrograde flags + events |
| `svg/step_01_Ascendant.svg` … `step_13_Pluto.svg` | INKEY$ overlay | one-by-one cumulative reveal, GRAPHDO colors |
| `svg/combined.svg` | screen plot | all bodies + aspect markers |
| `aspects.csv` | manual matching | conjunction/square/trine/opposition crossings, bisection-refined to the minute |
| `scope/row_NN.svg`, `scope/event_NNN_*.svg` | — | scope wheels with aspect lines (`--scope`) |
| `horary.csv`, `horary_events.csv` | — | classical 27-star nakshatra/pada/navam (`--horary`); 252-grid + crossings with `--ladder 28` |
| `precession_wheel.svg` | — | 28-sector precession wheel with equinox needle (`--precession`) |

The default plot is wrapped 0–360° with line breaks at the wrap — no more
up/down dual-trace ambiguity. SVG is resolution-independent, so output is
identical on every machine.

## Band-coincidence scanner (`astgraf-bands`)

The Predict.pdf method automated: sweep the 28-band × 11-body table (the PDF's
columns — no Pluto, no Ascendant, so the scan is site-free) over any date range,
fire on **Moon + Ketu + Mars sharing a band** (escalating to *catastrophic* when
Uranus/Neptune join), merge consecutive firings into episodes, locate any giants
present, and score episodes against a disaster-catalog xlsx with a chance
baseline. 12-hour steps by default (daily sampling can skip a band — the Moon
advances 13.2° > 12.857°/day).

```bash
uv run astgraf-bands --start 2013-01-01 --days 1095 --step-hours 12 \
  --catalog "NATURAL DISASTERS.xlsx" --out out/scan-2013-2015
```

Outputs `sweep.csv`, `episodes.csv` (with giant spots), `catalog_score.csv`,
and a summary with observed hits vs expected-by-chance.

`--level` selects the PDF's refinement ladder: 0 = 28 bands (12.857°),
1 = ÷9 (1.43°, the 252 grid), 2 = ÷63 (0.204°, the "1/63rd fraction");
sweep steps default to 12h/1h/0.2h so the Moon's dwell is always resolved.

`--proximity` (NU ruling): fire on the trio's **circular spread ≤ the level
span**, grid-free — fixed cells quantize away real convergences (the tightest
1990–2020 triple, 0.758° on 2018-09-20, straddled a level-1 cell line and
never fired in grid mode). A giant escalates when within one span of the
cluster; the band is named from the Moon. The 30-year level-1 proximity
census: 1996-04-17, 2003-01-27, 2004-11-11, 2018-09-20.

## Chatur Vyuham detector (`astgraf-bands --vyuha`)

NU's fourfold array — the most dangerous stellar constraint: Sun–Saturn and
Jupiter–Neptune/Uranus oppositions crossing at 90°, with the Rahu–Ketu axis
locked into the cross as the aggravator. Daily steps suffice (slow bodies).
Writes `vyuha.csv` (per-day separations, cross angle, node alignment, Saturn
distance) and `vyuha_episodes.csv`. **Census 1900–2026: the full array with
nodes fired exactly once — 2016-06-01 → 06-06, Jupiter opp Neptune, best
cross 89.56°** — the very window NU identified from memory. Saturn's
geocentric distance that week ranked at the 26th percentile (closest days in
the sweep: the perihelic oppositions of Dec 1914 / Dec 1973).

## Event locator (`--locate`)

NU's confirmed light-time rule: a crossing acts instantly in the substratum;
the marker arrives at light speed. At each refined aspect-event instant, take
the planet's culmination meridian (where its right ascension is on the local
meridian) and rotate **west by light-time × 15°/hour**; latitude from the
planet's declination. Rule v2 (2026-08-02): the light-time is computed from
the planet's **actual distance at the instant** (engine geocentric distance,
8.3167 min/AU) — NU's fixed minutes (Jup 40, Sat 80, Ura 150, Nep 240) remain
the nearest-position anchors and the fallback. At nearest position the surface
displacement is ~1000 km (Jupiter), ~2000 (Saturn), ~4000 (Uranus); NU's
Neptune 8000 vs the physical ~6700–7200 km is a recorded tension.
`locations.csv` gives the spot for every event involving those four planets.

## Precession clock (`--precession YEAR`)

The 25,739-year cycle from Secrets of Sankhya: equinox drift at 50.352″/yr
(= 360°/25,739 — the "50.35" is the same fact), 919.25 years per nakshatra
passage. Prints where the equinox sits on the 28-sector wheel for any year,
each marker sector's occupancy epoch (Punarvasu start, Abhijit opposition,
Magha flood epoch), and the two-cycle Punarvasu zero (~30,170 BC), and
writes `precession_wheel.svg` — the 28-sector wheel with the equinox needle.
Anchor defaults to equinox-at-0° in 1996 (the book's own arithmetic: Kritika
2 sectors back ≈ 158 CE, Punarvasu 7 back ≈ 4438 BC); `--precession-zero`
moves it.

## Scope charts (`--scope`)

Conjunctions, squares, trines and oppositions are the real guides — the scope
wheel draws them. A traditional wheel (0° Aries at 9 o'clock, signs
counterclockwise, GRAPHDO body colors) with aspect lines between every pair of
bodies within orb (`--orb`, default 3°) and an exact-aspect legend. One wheel
per period row (`scope/row_NN.svg`) plus one at each refined aspect-event
moment (`scope/event_NNN_*.svg`) — the geometry at the instant of the crossing,
not the nearest sample. Event wheels cap at 100 with a printed notice; narrow
with `--aspect-bodies` for full coverage.

## Trigger rules — how the system scales (`--rules doctrine-triggers.toml`)

Every trigger pattern is DATA, not code: `doctrine-triggers.toml` holds the
taught patterns (Chatur Vyuham, the band trigger, Neptune-on-Ketu, the Nepal
double) as declarative rules built from eight primitives — conjunction, opposition,
square, trine, axis_cross, cluster, same_band, in_band, plus nodes_occupied
(the Hyderabad both-node-ends pattern, Moon excluded as the fast hand) — with `real:`
prefixes for doctrinal ahead-positions and `escalate` blocks for severity.
New inputs about what positions trigger events become a few lines in the
file; `astgraf-bands --rules FILE` sweeps and scores every rule uniformly.
The theory itself is documented in FRAMEWORK.md.

## The nakshatra layer (`--horary`)

**Default — the classical 27 stars, exactly as ASTGRAF.BAS carries them** (NU
ruling 2026-08-02: "follow exactly whats in ASTGRAF.BAS"; the Abhijit/28
question is parked for a later decision). `horary.csv` gives every body's
nakshatra, pada (1–4), and navamsam sign each period, computed with the
verbatim ASTROLOG.BAS pada-count arithmetic (lines 5680–5790) and
oracle-pinned to the QUAKE.pdf printout. Names follow the BAS DATA lines
verbatim with one ruled exception: "Magha" where the BAS prints "Makha".

**`--ladder 28` — the parked Sankhyan prediction grid**: 28 equal divisions
(star names are markers only; Abhijit inserted as the 21st, 257.14–270°,
exactly opposite Punarvasu) × 9 equal subs = **1/252** of the cycle, × 7 again
= **1/1764** (the PDF's "1/63rd fraction" — the instant; numeric only, since
the 9-lord cycle has no defined 7-fold mapping). In this mode `horary.csv`
gives division/sub/sub-sub numbers and lords, and `horary_events.csv` records
every 1/252-boundary crossing, bisection-refined, wrap- and retrograde-aware.
Conventions (stated for correction): division *n* takes Vimshottari lord
(*n*−1 mod 9); a division's first sub takes the division's own lord and cycles;
sub-subs likewise from the sub's lord. `--ayanamsa-rate 50.35` switches to NU's
50.35″/yr reckoning (`--ayanamsa-zero` sets its zero year, default 294).

## The matrix, the atlas, and the outcome logger

- **`astgraf-matrix --signatures out/signatures-m7`** — the Predict.pdf 28×11
  matrix as a library: per-cell event rates vs controls from the signature
  CSVs, rendered as a heatmap SVG with per-cell counts (`matrix.svg`,
  `matrix.csv`). Outer-planet columns are baseline-confounded (slow bands) —
  read the inner-body columns first.
- **`astgraf-atlas`** — one SVG timeline: 52 equinox-sector passages over
  48,000 years with the doctrine epochs (Punarvasu zeros, Magha flood epoch,
  Kritika 158 CE, Aswini 1996), plus the modern panel of Jup–Sat conjunction
  ticks and Ura–Nep clusters with the Krakatoa/2004/2016 returns.
- **`astgraf-outcomes --episodes .../rules_episodes.csv`** — the
  assiduous-search step automated: for every passed watch window, query the
  USGS catalog (±window, radius around the spot) and log hit/clear/pending
  to `outcomes.csv`. Future windows never touch the network. The news
  channel joins when firecrawl has credits.

## Honesty notes

- The ephemeris is the ASTROLOG.BAS/ASTGRAF.BAS canon verbatim, including its
  10-digit `PI = 3.141592654` — full-precision pi shifts the Moon ~0.01" off
  canon. The port is pinned bit-close (10 decimals, 13 bodies) to the app's JS
  engine run with its `ss2` table corrected to the BASIC DATA.
- Keplerian mean elements are calibrated near epoch 1900: minute-level timing
  near the modern era, degrees-level drift at tens of millennia. Deep-time
  plots show cycle shapes, not minute-accurate positions.
- Aspect events are only meaningful for bodies whose motion the sampling step
  resolves: at yearly steps, Moon/Ascendant/inner-planet events are aliased
  noise (the BASIC had the same limit); use day or hour steps for those, or
  `--aspect-bodies Uranus,Neptune,Ketu` to restrict detection to named bodies
  (plotting is unaffected).
- The default ayanamsa is the suite's chart formula `(year − 294) · 151 / 10800`
  (50.333″/yr, wrapping in ~25,748 years) — kept for parity with the app engine.
  The doctrinal cycle is **25,739 years = 50.352″/yr** (Secrets of Sankhya);
  the precession clock uses it natively, and `--ayanamsa-rate 50.35` applies it
  to chart longitudes too.

## Tests

```bash
uv run pytest
```

Oracles: PRATEEK.docx (the 1987 ASTROLOG.BAS printout) and a headless run of
the app's JS engine (node vm harness).
