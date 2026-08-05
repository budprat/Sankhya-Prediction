# astgraf

**A prediction program**: event timing through transit patterns — aspect
geometry, 252-division horary crossings, and the 25,739-year precession
clock. Built on the family BASIC suite's transit-graph pair, ported verbatim:
**ASTGRAF.BAS** (positions over N periods → `ASTROC.GRF`) + **GRAPHDO.BAS**
(SCREEN 12 cosine plot). Same computation core, modern I/O. Natal chart
reading stays in the SankhyaHoroscope app; this tool predicts.

Documents: theory in `FRAMEWORK.md` · forward windows in `WATCHLIST.md` ·
evidence in `RESULTS.md` · the quake atlas in `QUAKE-ATLAS.md` · trigger rules
in `doctrine-triggers.toml` / `mined-triggers.toml` / `atlas-patterns.toml` ·
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
years). `--tropical` disables the ayanamsa; the real-obliquity (Koch)
Ascendant path is the default, as in the BAS's blank E/W answer — `--equal`
selects the equal path; `--style cosine` reproduces the heritage GRAPHDO fold.

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
light-time rotation — the Mathcad offsets (locator v3, NU ruling
2026-08-05), west from the culmination meridian — to give the spot
(here 100.17E 4.67N, the Strait of Malacca ~50 km off Perak, Malaysia;
Uranus's actual distance gave 170.4 light-minutes at this instant). The lens contract is enforced: pairs whose
relative motion exceeds ~one cycle per division are skipped with a printed
note — at yearly steps use the slow bodies; descend the lens for the fast
ones (each planet comes one by one). Within the contract, detection is
wrap-safe and finds every crossing, including retrograde multi-passes (the
2010–11 Jupiter–Saturn triple opposition resolves at a yearly lens).

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
| `rasi_navamsam.txt` | — | RASI + NAVAMSAM box charts, QUAKE.pdf layout, per period row and per aspect event (`--rasi`) |
| `horoscope.txt` | — | the full ASTROLOG report page: header, Koch cusps, planet table, Dasa/Bukti, boxes (`--report`) |
| `precession_wheel.svg` | — | 28-sector precession wheel with equinox needle (`--precession`) |
| `galactic.csv` | — | per body: separation from the Punarvasu crossover and the Magha (galactic) axis (`--galactic`; with `--scope`, both axes drawn on the wheels) |
| `mirror.csv` | — | the heritage cos-fold crossings: instants where `lon_a + lon_b = 360k` (`--mirror`; with `--scope`, drawn dashed) |

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
meridian) and rotate **west** by the light-time; latitude from the planet's
declination.

**Rule v3 (NU ruling, 2026-08-05: "Mathcad version is the one").** The
Mathcad quantity `(a/2−1)·500/240` is *already* degrees of ground rotation —
500 s per AU of light travel, 240 s per degree of Earth rotation — so the
`REAL_POSITION_OFFSETS` **are** "rotate the long to suit": Jupiter 3.336°,
Saturn 7.867°, Uranus 17.856°, Neptune 29.092° (equivalently 13.3 / 31.5 /
71.4 / 116.4 light-minutes; ~371 / 875 / 1,987 / 3,238 km at the equator).
This supersedes two earlier readings, both kept on record: the prose figures
40/80/150/240 min (= nearest-approach `a−1`, giving 10/20/37.5/60°), and the
2026-08-02 distance-true refinement — the Mathcad is defined on the orbital
radius, so the rotation is a **fixed constant** and the chart's instantaneous
distance is deliberately not consulted. Registered spots moved 21° (Uranus)
to 31° (Neptune) east when this landed; see the WATCHLIST banner.
`locations.csv` gives the spot for every event involving those four planets.

**Status (NU-ratified 2026-08-04): experimental.** Every tested formulation
of this channel — the rule above, locate-at-the-event-minute, and the
zero-rotation real-meridian alternative — measures at chance on 1,435
declustered M7+ mainshocks (per-body longitude gaps match uniform), and the
rotation as implemented self-cancels against the trigger-chart offset.
Earthquake windows are therefore **time-only claims**; registered spots
stay graded (WATCHLIST amendment v5) as a pre-registered experiment.

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
taught patterns (both Chatur Vyuham variants, the band trigger, Neptune-on-Ketu,
the Nepal double, the node/site rules) as declarative rules built from eleven
primitives — conjunction, opposition, square, trine, axis_cross (evaluated on
the order-independent midline of both axis endpoints), cluster, same_band,
in_band (single band or a band list, e.g. the Jupiter–Saturn Java-family
sector), near_any (the scanner's giant-escalation geometry),
nodes_occupied (the Hyderabad both-node-ends pattern, Moon excluded as the
fast hand), and mirror (the heritage cos-fold crossing, below) — with
`real:` prefixes for doctrinal ahead-positions and
`escalate` blocks for severity. Loading is guarded: unknown keys, unknown
body names, structurally incomplete conditions, offset-less `real:` prefixes,
and empty rulesets all fail the load instead of no-oping silently.

Rules carry their provenance in their file: `doctrine-triggers.toml` (NU's
taught patterns), `mined-triggers.toml` (data-mined candidates — retired),
and `observed-triggers.toml` (**TESTING** status, NU ruling 2026-08-04:
single-chart observations promoted for testing — currently
`asc-trine-real-neptune`, Nepal 0.26°, orb 1.0, tropical site charts only;
the frame matters because the canon's sidereal mode shifts angles by
ayanamsa in RA space).

`astgraf-bands --rules FILE` sweeps every rule uniformly, with fast-body
rules on their own fine steps automatically (Ascendant 0.25 h, Moon 1 h);
each episode gets its tightest instant (refined per the rule's own exactness
metric, earliest-exact deterministic) and an acting-body spot only when a
locatable body is genuinely within its condition's orb at that instant.
Catalog scoring uses the step-honest chance baseline and reports
out-of-range events separately. The theory itself is in FRAMEWORK.md.

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
50.35″/yr reckoning, anchored at the ruled 1996 Aswini zero by default
(`--ayanamsa-zero` overrides; the suite formula keeps its 294 CE zero).

## RASI and NAVAMSAM boxes (`--rasi`)

`--rasi` writes `rasi_navamsam.txt`: the South-Indian square charts exactly as
the ASTROLOG.BAS HOROSCOPE subroutine prints them (lines 6120–6880) — the AR()
house-square walk, fixed 4-character body slots (which produce the staggered
look of the printout), the 15-character Ascendant line, and the canon's
deliberate omission of Ura/Nep/Plu from the NAVAMSAM chart. One block per
period row plus one per refined aspect event. ASCII `|`/`-` stand in for the
BAS's CP437 border glyphs. To reproduce QUAKE.pdf itself:
`--year 2015 --month 4 --day 25 --time 11:40 --utc-offset +05:30 --lon 86:00E
--lat 28:00N --tropical --rasi` (the PDF chart is the Koch path — the canon's
E/W house answer changes the Ascendant itself. ASTGRAF.BAS asks "House system
E or W" at run time and a blank answer takes the Koch path, which is why Koch
is this CLI's default; `--equal` selects the equal path, the PRATEEK oracle
setting. The oft-quoted `EQL$ = "KOCH"` at ASTGRAF.BAS:45 is a dead
assignment — never read.)

## The full report page (`--report`)

`--report --name X --place Y` writes `horoscope.txt` for the start moment —
the complete ASTROLOG.BAS printout as in QUAKE.pdf: the header block
(including the sidereal time with the canon's rounded-minute display quirk),
the 12 Koch house cusps (CO960 ported verbatim: ascensional difference +
oblique-ascension chain; the First cusp reproduces the AZ55 Ascendant to
1e-6°), the planet table with Retro/Ruler (the LUCK rulership table) and
Nakshatra/Pada/Navam columns, Dasa/Bukti at birth (Vimshottari from the
Moon), Nakshatra at birth, and both box charts. The QUAKE.pdf cusp table
reproduces value-for-value; Dasa/Bukti day fields are sensitive to the
engine-vs-BAS sub-arcminute Moon difference (±few days) — lords, years, and
months match the printout.

## The galactic reference (`--galactic`)

The author's reading of the ayanamsa's purpose: "locate the galactic pole and
ecliptic in major events." Two fixed directions are exposed per chart — the
**Punarvasu crossover** and the **Magha axis** (sector-10 center, 122.143°,
folded at 180°).

The crossover is the **galactic-ecliptic node** (NU ruling, 2026-08-05): the
point where the galactic plane actually cuts the ecliptic, measured from the
IAU J2000 galactic pole — tropical **90.023°** at J2000, **suite-sidereal
66.171°**. Its name records where the *equinox* stood on the 28-sector wheel
when it last crossed that node (mid-5th millennium BC — "zero ascension in
Punarvasu"), not where the node sits on today's zodiac; on the wheel the node
reads 89.967° against the Punarvasu sector boundary at 90.0°, 0.03° apart.
These markers are exposed per chart:
`galactic.csv` gives every body's separation from each, and with `--scope`
both axes are drawn on the wheels (dashed). Sidereal charts use the markers
directly; tropical charts shift them by the suite ayanamsa for the chart's
year. `--precession YEAR` now also prints the equinox's offset from both
markers with the drift-time equivalent ("how much Magha… Punarvasu… as of
today"). Frame note: ASTGRAF.BAS carries no Abhijit/28 data (its 27-name
list is read and never used), so these directions come from Secrets of
Sankhya's own clock — recorded in the ledger.

Why this validates the frame: the galactic plane crosses the ecliptic at
90.02°/270.02° — the solstice points, the planes standing 60.19° apart — and
the equinox last stood on the ascending node in the **mid-5th millennium BC**
(4445 BC on a linear 50.2879″/yr, 4539 BC on the IAU-2006 quadratic; the
book's own constant 25,739-year cycle says 4439 BC, all within ~100 y of each
other out of 6,500). One cycle earlier is the author's "30,000 years zero
ascension in Punarvasu". The Sun itself crosses the galactic plane at the
solstices — last on 2026-06-21 08:51 UT northward. Note the two frames in
play: the precession wheel's zero is the 1996 equinox while the suite's
sidereal zero is an ayanamsa away, so a sidereal direction is converted with
`precession.marker_on_wheel()` before being compared with the equinox.

## The mirror crossing (`--mirror`)

GRAPHDO.BAS (line 54) and the author's own 2016 JS both plot
`y = cos(longitude)`, folding the circle so 0/360 sits at the bottom, 180 at
the top and 90/270 in the middle. On that graph two traces meet not only at a
conjunction but whenever `cos(lon_a) == cos(lon_b)` — the pair mirrored about
the 0–180 equinox axis, i.e. `lon_a + lon_b = 360k`. Those crossings are
visible on his screen and invisible to the four aspect angles, so they are
detected separately: `--mirror` writes `mirror.csv` (each crossing refined to
the instant, with the signed offset), `--scope` draws them dashed, and rules
can use the `mirror` primitive with an `orb`. Example — at the Gorkha quake
the Moon and Saturn stood 0.067° from the mirror while being 127° apart in the
classical frame. `find_events` is untouched: the audited aspect stream still
reports only conjunction/square/trine/opposition.

**Graded, and it carries no mined signal** (`scripts/mirror_lifts.py`, same
corpus and protocol as the v2 mining that retired the mined aspect rules —
1,435 declustered post-1900 events vs 4,305 time-uniform controls). At orb 3°
an event chart holds 1.577 mirror hits on average against 1.553 for controls,
and the best of 95 predicates (`mir:Jupiter-Saturn`, lift 1.72) sits **exactly
on the permutation null's median of 1.72** (95th pct 2.06, p = 0.505). At orb
1° nothing clears the 2% event-rate floor. So the layer is a faithful redraw
of what the author's graph shows — it lets a taught rule be *expressed* — but
as a miner for M7+ timing it finds nothing, exactly like the aspect
predicates before it.

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
  to `outcomes.csv`, each spot with its `spatial_chance` (the historical
  fraction of M7+ events within the grading radius — the base rate behind
  any hit; `--corpus` sets the reference catalog). Windows without a spot
  stay on the ledger as `unassessed (no spot)`. Future windows never touch
  the network. Only the quake channel is graded — the flood/volcanic
  families need the news search (firecrawl credits pending).

## The event-chart atlas and the pattern miner

Two grading pipelines that run over the event catalogs rather than over a
date range. Both keep the DESCRIPTIVE census and the INFERENTIAL grading
strictly apart — a census of thousands of charts always produces
striking-looking regularities, and only an event-vs-control contrast can tell
a sky base rate from an effect.

```bash
uv run python scripts/quake_atlas.py --corpus all      # 13,339 charts, ~11 min
uv run python scripts/quake_atlas.py --corpus m7 --no-wheels
uv run python scripts/pattern_mine_m7.py               # co-occurrence, ~10 s
```

**`quake_atlas.py`** casts a full chart per event **at its own epicenter** —
13 body longitudes, retrograde flags, nakshatra/pada, 28-band occupancy, the
four giants' real positions, band stack, Moon–Ketu–Mars spread, vyuha state,
doctrine rules fired, every doctrine-orb contact — for all four quake
catalogs, then screens the doctrine's full predicate vocabulary against
era-matched controls with a family-wise maximum-lift null. Writes
`charts.csv`, one SVG wheel per event, `census.txt`, `lifts.csv` and
`patterns.txt` per corpus. Tracked digests: `data/quake-charts-*.csv`;
tracked wheels: `charts/great-quakes/` (16 M8.5+) and `charts/deadliest/` (10).

**`pattern_mine_m7.py`** searches **co-occurring** configurations — pairs and
triples, the conjunction-of-conditions shape every taught pattern has — over
a unified M7+ corpus assembled across all three catalogs that carry M7+
events and deduplicated at 3 d / 300 km (1,635 unique, larger than any single
file). It carries three guards earned by a false positive it actually
produced:

- a **testability filter** — a predicate whose value never varies across a
  block's slots cannot be tested by permutation (it contributes zero null
  variance while still driving the observed lift). Drops exactly
  `band:Neptune` and `band:Uranus`, which a ±365 d control cannot decorrelate.
- a **distinct-epoch count** — for a slow-body predicate the unit of
  independence is the epoch, not the event.
- a **mandatory split-half** — both 2-year-block halves must agree.

Output goes to `atlas-patterns.toml` in the project's own rule schema, so the
patterns load with `triggers.load_rules()` and sweep with
`astgraf-bands --rules atlas-patterns.toml`. Every rule carries its lift,
support, epoch count, split-half lifts and a `SURVIVOR` / `FAILS REPLICATION`
tag, and the file header states the whole-file status. **The file is labelled
NOT SUPPORTED** — nothing is dropped for looking bad, because
`mined-triggers.toml` was retired for exactly that.

## The long-cycle flood clock (`scripts/flood_clock.py`)

`PLAN.md` §3.1, pre-registered and closed 2026-08-05. Asks which
Uranus–Neptune clock (163.5 / 164.5 / 171.0 y) the flood records support, and
finds the question splits in two:

**Part 1 — which clock? Not answerable, and that is arithmetic rather than a
null.** Across the systematic record (HANZE 1871–2025, 154 y) the candidates
separate by at most **14.9° of phase**, over a span covering **0.90–0.94 of
one cycle**, while reporting density rises **~12×**. Periods that close cannot
be told apart from less than a cycle.

**Part 2 — is incidence elevated near the conjunction at all?** Detrended
against a centred 51-year moving average, ±8 y on the 1993 triple,
circular-shift null over 122 non-overlapping windows: **0.9815, p = 0.393,
rank 49 of 123.**

**The binding limit is n = 1.** The systematic record holds exactly one
conjunction epoch; 1821 and 1650 carry zero usable events within ±10 y in
either corpus. The 670 HANZE events near 1993 are 670 observations of *one
epoch*, not of a clock — so the doctrine verdict is **UNTESTED**, and the
script's honest output is that power statement rather than its p-value.
Unblocking it needs a systematic flood catalogue reaching ~1780–1860 at day
precision (FRAMEWORK open question 7).

## The anchor library (`astgraf-anchors`)

The recurrence principle (NU, 2026-08-04) as machinery: past major events are
the anchors prediction works from. `anchors.toml` holds the library — the
taught instances (Nepal, Hyderabad, Ulsoor, the 2016 vyuham, Krakatoa, 2004
Sumatra) plus the corpus M9 set — and `astgraf-anchors` builds each anchor's
dossier:

```bash
uv run astgraf-anchors --list                  # the library
uv run astgraf-anchors --anchor nepal-2015     # one dossier to stdout
uv run astgraf-anchors --out out/anchors       # all dossiers as .json/.txt
```

A dossier is the event's full configuration readout, **every fired rule with
its trigger instant refined below one minute**:

- **Contacts** — all pairs (11 bodies + the four giants' real positions;
  Jupiter/Saturn offsets provisional since the Rs/Ro decode) within 5° of an
  aspect angle, doctrine-orb (3°) hits starred; each starred contact carries
  the exact instant the aspect perfects (UTC minute), its offset from the
  event, and the residual if it never perfects (Nepal: real-Uranus reaches
  the Sun exactly 18.1 h after the quake; real-Neptune reaches Ketu +107 h).
- **The site timetable** — for located anchors, every Ascendant conjunction
  (observed and real positions) within ±12 h, minute-refined in the tropical
  (physical rising) frame. Oracle-tested against NU's taught minutes:
  Hyderabad Asc–Rahu 04:50 vs taught ~04:49 IST, Asc–Ketu 17:06 vs ~17:04;
  Ulsoor Asc–Neptune 06:12 exact, Asc–Uranus 08:21 vs 08:20, sweep order
  Neptune → Sun → Ketu → Uranus reproduced.
- **Band state and vyuha** — Moon/Ketu/Mars spread, band stack, and the
  Chatur Vyuham state at the instant.

Anchors with `time_quality = "approximate"` (Krakatoa's paroxysm, the
Hyderabad cloudburst hour) keep valid slow-layer exactness instants — those
are found by geometry near the date — while the fast-layer readouts inherit
the time uncertainty.

## The recurrence calendar (`astgraf-recur`)

The similarity engine over the anchor library — the recurrence principle
run forward. An anchor's **pattern** is its slow layer: the doctrine-orb
contacts at its instant, Moon pairs excluded (the Moon is the fast hand,
not the configuration). The engine scans any span for **episodes** where
the whole pattern (or `--min-match` of it) stands within orb
simultaneously, refines each episode's tightest instant below one minute,
and then completes the anchor's own Moon contacts inside the episode — the
fast hand dating the window, exactly as in the taught instances. Timing
only: no spots (the location layer is experimental, WATCHLIST v5).

```bash
# When does the Nepal configuration re-form?
uv run astgraf-recur --anchor nepal-2015 --start 2015-03-01 --end 2015-07-01
# -> exactly one episode: 2015-04-23 .. 2015-04-25 (the quake was Apr 25)

# The forward calendar over every anchor:
uv run astgraf-recur --start 2026-08-04 --years 2 --out out/recur
# -> with the four-giant real-position patterns: no full and no all-but-one
#    re-formations anywhere through 2028-08 - the selectivity is the point.
#    (Nepal's own 2015 window still recovers as exactly one episode, now at
#    9/9 with the real-Jupiter/Saturn contacts included.)
```

**Per category** (`--category earthquake | flood | biological | volcanic |
configuration`) — Predict.pdf's design is explicitly per category, so the
scan is too; every calendar row carries its anchor's category.

**Composite matching** (`--composite`) — a contact pattern says which pairs
are locked; it cannot say what the band table and the fourfold array were
doing meanwhile. With `--composite` an episode must ALSO reproduce the
anchor's other layers: the same vyuha level (categorical, exact), a
Moon–Ketu–Mars spread at least as tight, and a band stack at least as high.
A composite episode set is therefore always a subset of the contact-only
one — the June 2016 vyuham window narrows from June 3–4 to June 3.

Outputs: `recurrence.csv` / `.txt` / `.json` — one chronological calendar
across anchors, each row with its category, the episode span, match level,
tightest instant, per-contact separations, and fast-hand trigger minutes.

## The family calendars (`astgraf-families`)

Recurrence at the grain where it actually repeats. The 130-year sweep showed
contact-fingerprint patterns never re-form; NU's taught recurrence lives at
the **nakshatra-sector** grain — the Java family: the 1881 Jupiter–Saturn
conjunction in Aswini → Krakatoa 1883; the 2000 conjunction in Kritika →
the 2004 Sumatra tsunami. `families.toml` holds the families as data;
`astgraf-families` computes each pair's full conjunction series
(minute-refined, wrap-safe — the 1940–41 and 1980–81 triples stay three
events each), the canon star/pada/band of every conjunction degree, and
flags **member-sector returns**:

```bash
uv run astgraf-families --start 1850 --end 2100 --out out/families
```

Both taught members reproduce under the engine's own arithmetic
(1881-04-16 → Aswini, 2000-05-27 → Kritika), and the forward calendar
sharpens the doctrine's "next ~2040": the 2040-10-30 conjunction falls in
**Chitra** (not a member sector); the next **member-sector return is
2060-04-07 in Kritika**. The 1941 triple in Bharani sits between the taught
members as an unexamined candidate (records search open). The Uranus–Neptune
flood family's 1993 conjunction was itself a triple, all three passes in
Poorvashada pada 4 — the 1,000-year records list (awaited) populates its
historical members. Timing only — no spots.

## The dwell claim (`scripts/dwell_grade.py`) — half of it survives

The author gives two numbers: a threshold (*"dwell time more than 3 seconds,
for above that MAJOR SHOCK WAVES can be created"*) and one worked case
(*"In Nepal the dwell time has been 4 minutes"*). At Gorkha exactly two taught
contacts are in force — real-Uranus on the Sun at 0.692° and real-Neptune on
Ketu at 0.342° — and their sum, 1.034°, is **4.14 minutes** at his own 4 min per
degree. So dwell is read as `Σ(active crossing separations) × 4 min/deg`. Note
this makes a *wider* pair give a *longer* dwell, so the doctrine predicts looser
configurations drive bigger events.

His claim has two separable halves, and they do not fare alike.

**The trigger half fails.** Events do not carry more dwell than time-uniform
controls — the difference is +0.054 min at orb 3° (p = 0.42), and at orb 1° it
runs the *wrong way* (events 0.062 min vs controls 0.079). His 3-second
threshold is also vacuous as literally stated: 3 s is 1/81°, so any crossing
inside orb clears it, and the rates are the same for events and controls.

**The magnitude half survives three attempts to kill it.** Over the four
correlation cells inspected, dwell vs magnitude gives:

| cell | ρ | n |
|---|---|---|
| **taught giants, orb 1°** | **+0.322** | 44 |
| all four giants, orb 1° | +0.192 | 95 |
| taught giants, orb 3° | −0.065 | 148 |
| all four giants, orb 3° | +0.009 | 268 |

Shuffling magnitudes across all events and recomputing every cell gives a
**family-wise permutation p = 0.042** (null median 0.137, 95th pct 0.310).

- *Is it just the crossing count?* No — count vs magnitude is only ρ = +0.100,
  and restricting to events with exactly **one** active crossing (n = 41) leaves
  ρ = **+0.315**. It is the width of a single crossing, which is his claim.
- *Does it split?* Both halves in time hold: earlier n = 22, ρ = +0.455; later
  n = 22, ρ = +0.333.
- *Is the test honest?* Injecting a known rank correlation into the same
  44-event cell recovers ρ = 0.306 for a 0.30 target, detected in 8/12 draws —
  underpowered, but unbiased.

### …and then it failed to replicate (`scripts/dwell_holdout.py`)

The M7+ result was flagged as a lead, not a result, precisely because n = 44 and
the cell was the largest of four. It was tested against genuinely held-out data:
**12,212 M6.0–6.99 events** from USGS FDSN (a band disjoint from the M7+ corpus
by construction), declustered by the identical 7 d / 500 km rule to 10,324, of
which **338** carry an active taught crossing at orb 1°.

The cell, direction and statistic were **pre-registered before running** — one
test, no re-tuning, predicted ρ > 0 of order +0.3.

| test | n | ρ | p |
|---|---|---|---|
| **held-out M6.0–6.99** | 338 | **−0.040** | 0.77 (one-sided) |
| pooled M6 + M7+, full 6.0–8.5 range | 382 | −0.053 | 0.30 |
| within single-crossing events | 329 | −0.019 | — |
| earlier / later halves | 169 / 169 | −0.048 / −0.045 | — |
| 1970+ only (M6 completeness) | 170 | −0.041 | — |

**Wrong sign, every cut.** And the test was not blind: injecting a true ρ of
0.32 into the same 338 events recovers it in **12/12 draws**, and even ρ = 0.20
in 11/12. The pooled row also removes the range-restriction excuse — full
6.0–8.5 dynamic range, still nothing.

**Verdict: the dwell doctrine is unsupported.** Its trigger half was vacuous,
and its magnitude half was a winner's curse — an underpowered cell selected as
the max of four, on a construction fitted to one anchor. The one caveat worth
stating: the author's claim concerns *major* events, and a mechanism that
switches on only above M7 would not show in the M6 band — but the M7+ result
now rests on nothing except its own selection.

## The rotation spectrum (`scripts/rotation_spectrum.py`) — no rotation works

The locator rotates a body's sub-point west by the Earth-rotation angle
corresponding to its light time. Two candidate offset sets exist: the Mathcad
`(a/2−1)·500/240` values (3.34/7.87/17.86/29.09°) and the author's prose light
times (40/80/150/240 min → 10/20/37.5/60°, which reproduce his own stated
1000/2000/4000/8000 km displacements).

Rather than test two points, the rotation is **scanned round the whole circle**
at 5° steps per giant, using the same leave-one-out epicenter rank statistic
that graded the angle layer. **The spectrum is flat** — deepest dip anywhere is
Neptune at 25°, z = −2.32, against a z = −3.7 bar for 288 tests. The per-body
minima (Jup 270°, Sat 170°, Ura 60°, Nep 25°) are scattered, not clustered near
the physical light-time values, which is what a real propagation effect would
produce.

| convention | within 1000 km | rank z |
|---|---|---|
| Mathcad (current) | 0.0383 | −1.67 |
| prose 40/80/150/240 min | 0.0258 | −1.04 |
| no rotation at all | 0.0328 | −1.15 |

At Gorkha, **no rotation is best** (Uranus 2,852 km) against Mathcad 4,151 km
and prose 5,939 km — every rotation moves the spot away from the taught anchor.

Power check in the same script: planting synthetic epicenters at a known 100°
rotation, the scan recovers it in the exact 5° bin at z = −64, and still exactly
at z = −60 with ±30° of jitter. It finds rotations that exist.

This settles the Mathcad-vs-prose question **for prediction only** — the 3×
discrepancy was never what cost us accuracy, because no value works. It does not
settle which the author meant.

## The site-angle layer (`astgraf.angles`) — graded, and retired as a predictor

The idea: an event stands where the crossing pair sits on an **angle** of the
site's own chart. It fits all three of NU's taught anchors in the author's own
language (Nepal's Sun/real-Uranus 2.00°/2.69° from the MC, Hyderabad's
Neptune/Ketu 0.56°/0.59° on the Asc, Ulsoor's Neptune 0.09° on the Asc), and it
escapes the tropical ceiling that kills the sub-planet spot — the MC fixes a
meridian, the Ascendant fixes a curve reaching every latitude.

**It does not survive the catalog** (`scripts/angle_grade.py`). Because this
layer claims a *place* rather than an *instant*, the controls are places, not
times: 49 leave-one-out epicenters per event at the same instant, which matches
the geography of seismicity exactly. Over 1434 declustered post-1900 M7+ events
the true epicenter is not preferred — best of 15 bodies is Mars at z = −2.27
against a z = −3.0 multiplicity bar; the specified form (acting taught contact
only, 314 instances) gives z = −0.35, and **z = +1.20 at the crossing exactness
instant**, which is the only instant a forward run actually has.

**The null is not blindness** (`scripts/angle_power.py`). Planting epicenters
where the body sits exactly on an angle, the identical statistic recovers the
signal at z = −41.6 exact and still ≈ z = −17.5 after ±25° of jitter. Both
angles are planted — **MC and Ascendant** — because the taught Hyderabad and
Ulsoor readings are Ascendant ones, and the Ascendant is the weakly-conditioned
axis; testing only the MC would have left the anchors' own axis unchecked. A
rule of this shape, that loose, on either angle, would have been found. The
power claim is enforced in the suite, not just written down.

Scope limit found while running it, and corrected on 2026-08-05 after being
measured rather than assumed: the BAS cusp chain evaluates `sqrt(1 − xx²)`
with `xx = sin(RA)·tan(ε)·tan(lat)`, so it is undefined once `|xx| ≥ 1`.

Two things the original note got wrong. **The limit is not a fixed latitude** —
66.56° assumes `sin(RA) = 1`, but RA moves with sidereal time, so the real
threshold depends on the instant as well as the place (at RA 120° the chain
computes at 67°N and fails at 70°). 66.56° is the *worst case*: the latitude
below which the chain is defined at every RA, exposed as
`angles.POLAR_SAFE_LIMIT`, with `angles.angles_defined_at()` asking the
arithmetic rather than a constant. And **the angles do exist up there** — the
Ascendant and MC both compute at 85°N; only the twelve cusps do not.
`compute_raw` fails as a unit because it builds cusps unconditionally, so
`angles.py` raises `PolarChartError` and its helpers degrade to `None`/`[]`.
*Open for a ruling:* a cusp-less chart would make the site channel available
at polar latitudes, and the Asc-based rules are the ones that matter there.

`angles.py` remains a correct way to read a chart's angles. It must not be used
to claim a location.

## Honesty notes

- The ephemeris is the ASTROLOG.BAS/ASTGRAF.BAS canon verbatim, including its
  10-digit `PI = 3.141592654` — full-precision pi shifts the Moon ~0.01" off
  canon. The port is pinned bit-close (10 decimals, 13 bodies) to the app's JS
  engine run with its `ss2` table corrected to the BASIC DATA.
- Keplerian mean elements are calibrated near epoch 1900: minute-level timing
  near the modern era, but drift is already **degrees-level by the 1600s**
  (Jupiter–Saturn conjunction timing −16 d at 1603, −31 d at 1623, vs DE440)
  and grows beyond. Census years near the 1600s are trustworthy to ~a year,
  not a day; deep-time plots show cycle shapes, not positions.
- Aspect events are only emitted within the lens contract (relative motion up
  to ~one cycle per division — wrap-safe and complete inside it, including
  retrograde multi-passes). Pairs faster than the lens are **skipped with a
  printed note**, never emitted as aliased noise; use day or hour steps for
  Moon/Ascendant/inner-planet events, or `--aspect-bodies` to restrict.
- The default ayanamsa is the suite's chart formula `(year − 294) · 151 / 10800`
  (50.333″/yr, wrapping in ~25,748 years) — kept for parity with the app engine.
  The doctrinal cycle is **25,739 years = 50.352″/yr** (Secrets of Sankhya);
  the precession clock uses it natively, and `--ayanamsa-rate 50.35` applies it
  to chart longitudes too.

## Deliberate divergences from the BASIC canon

The computation core is the BAS verbatim (oracle-pinned to the PRATEEK and
QUAKE.pdf printouts and bit-close to the corrected JS engine). Exactly **two**
engine behaviors deliberately diverge from the canon, both bug fixes, both
tested, both ledger-recorded — plus one documented **environment** difference
(not a source divergence): the canon declares no `DEFDBL`, so the family's
interpreter ran the series in *single precision*; the port computes the same
series in double. Effect: the Moon can differ by ~1–2 arcminutes from a
period print (the Hyderabad 2016 docx prints Moon 11°26′ where the port
prints 25′ — float32 emulation of the canon series reproduces the docx value
exactly), which the Vimshottari balance amplifies to ~10 days. Print oracles
match when the Moon sits away from a rounding boundary; the port follows the
SOURCE (the series as written), not the 1980s float hardware.

1. **The Gregorian reform day** (`ephemeris.py`, `julian_day_number`). The
   BAS/JS canon's strict `IF J > 2299171` misses the first Gregorian day
   itself: 1582-10-15 mapped to a JDN ten days too big and JD ran *backward*
   into 10-16. The port uses `>=` — one comparison changed. Pinned by
   `test_gregorian_reform_day_maps_correctly` (1582-10-04 → 2299160,
   1582-10-15 → 2299161). Residual on record: stepping calendar *fields*
   across October 1582 still double-covers the ten phantom dates (Oct 5–14
   don't exist); JD-driven paths (sweeps, `make_chart_at_jd`) are immune.

2. **The ayanamsa year follows the instant** (`ephemeris.py`,
   `compute_raw`). The canon takes the year from the input field; the port
   derives it from the actual JD. For every run the BASIC could perform this
   is **identical** — the BAS steps its year field so its `YR` was always
   current, and its hour grids capped at 63 periods. It differs only on
   multi-year hour-overflow sweeps (impossible in the BAS), which previously
   froze the ayanamsa at the start year and corrupted every long census; plus
   one sub-print-resolution edge (a 63-hour BAS grid crossing New Year holds
   the old year's ayanamsa a few hours longer — ~50″, under the printout's
   0.1° resolution). Pinned by
   `test_ayanamsa_follows_the_instant_not_the_start_field`.

One **ruled exception** (not a silent divergence): the nakshatra name
**"Magha"** where the BAS DATA prints "Makha" — NU's explicit ruling,
2026-08-02. Pre-existing port-level differences (double precision vs QBasic
singles, ASTGRAF's `+7` where ASTROLOG has `+6`, the corrected `Z1 = Z1`
typo, CSV/SVG in place of `.GRF`/VGA output, six decimals vs the `.GRF`'s
one, real date labels vs the broken `YR` column, decimal hours vs packed
`HH.MM` steps, the grid computing exactly `--count` rows from the start
moment where the BAS computed count+1 from start+step, and the count
ceiling of 2000 vs the BAS's 63) are inventoried in `AUDIT.md` Part III §G
and the decision ledger — none is silent.

## Tests

```bash
uv run pytest
```

Oracles: PRATEEK.docx (the 1987 ASTROLOG.BAS printout) and a headless run of
the app's JS engine (node vm harness).
