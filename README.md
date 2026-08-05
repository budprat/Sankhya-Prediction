# Sankhya Prediction Engine

**A Sankhyan event-prediction system**: planetary transit geometry → falsifiable,
dated, located forecast windows — with the verification machinery to grade its
own predictions against real-world event catalogs.

Built as a faithful modern port of a family BASIC astrology suite
(ASTGRAF/ASTROLOG/GRAPHDO/HORARY, preserved in [`canon/`](canon/)), extended
into a full prediction pipeline from the Sankhyan doctrine of
*Secrets of Sankhya* and its worked instances. Python 3.12 · zero heavy
dependencies · 263 tests · MIT.

```
canon/                      The original BASIC suite (the computation canon, in-tree)
tools/astgraf/              The engine: CLI tools, tests, doctrine rules, documents
  ├── FRAMEWORK.md          The theory — how prediction works in this system
  ├── WATCHLIST.md          Registered forward windows + outcome protocol
  ├── AUDIT.md              Full adversarial audit: 127 findings, all resolved
  ├── RESULTS.md            The evidence ledger: every graded claim, with numbers
  ├── QUAKE-ATLAS.md        13,339 event charts across every quake catalog, graded
  ├── TESTING.md            The two test layers: canon fidelity, and claim grading
  ├── PLAN.md               Current state, open work, what is blocked
  ├── README.md             Tool-level docs: every CLI, flag, and output
  ├── doctrine-triggers.toml  Taught trigger patterns as declarative rules
  ├── mined-triggers.toml     Data-mined candidates (retired — see below)
  ├── observed-triggers.toml  Observed candidate rules in TESTING status
  ├── atlas-patterns.toml     Co-occurrence patterns mined over every M7+ quake
  │                           (loadable, labelled, and NOT SUPPORTED — see below)
  ├── charts/                 Chart wheels: 16 M8.5+ quakes, 10 deadliest
  ├── anchors.toml            The anchor library: past major events as data
  ├── families.toml           Long-cycle families (nakshatra-sector recurrence)
  └── data/                 Pinned USGS M7+ corpus 1850–2020
.claude/tasks/ASTGRAF_TOOL.md   Dated decision ledger — every ruling, every change
```

## What it does

**The engine** (`astgraf`) computes geocentric positions for 13 bodies with the
canon's own arithmetic — truncated π, 1900-epoch Keplerian elements, 20-term
Brown Moon, mean nodes, oblique-ascension Ascendant — pinned digit-for-digit
against the original suite's printouts. On top of it:

- **Period grids & graphs** — the suite's 60-period drill as one-command
  "lenses": coarse year-grids to find an era's crossings, hour-grids to refine
  an instant to the minute. SVG plots replace the VGA screen, CSV/JSON replace
  the `.GRF` files.
- **Aspect events** — wrap-safe, retrograde-aware crossing detection
  (the 2010–11 Jupiter–Saturn triple opposition resolves at a *yearly* lens),
  bisection-refined to the minute — plus the heritage **cos-fold mirror
  crossing** (`--mirror`): the suite plots `cos(longitude)`, so two traces
  also meet when `lon_a + lon_b = 360k`, a crossing visible on the author's
  own graph and invisible to ordinary aspect angles.
- **The nakshatra layer** — classical 27-star position/pada/navamsam exactly
  per the canon; the Sankhyan 28×9×7 = 1764 "instant" ladder available behind
  `--ladder 28`.
- **Band-coincidence scanner** (`astgraf-bands`) — the doctrine's 28-band ×
  11-body table swept over any date range: Moon+Ketu+Mars coincidences,
  giant-planet escalation, episode merging, catalog scoring against a
  step-honest chance baseline.
- **Declarative trigger rules** — every taught pattern is *data*, not code:
  ten geometric primitives in TOML with schema-guarded loading. New doctrine
  becomes a few lines in a file, swept and scored uniformly.
- **The event locator** — the doctrine's light-time rule: crossings act
  instantly in the substratum; the marker arrives at light speed; the spot is
  the culmination meridian rotated west, latitude from declination. Rule v3
  (2026-08-05): the rotation is the Mathcad quantity itself — a fixed
  3.336° / 7.867° / 17.856° / 29.092° for Jupiter / Saturn / Uranus /
  Neptune, superseding both the prose-minute and distance-true readings.
- **Chart angles & the site-angle layer** (`angles.py`) — Asc/Desc/MC/IC and
  the solvers that invert them. The location rule built on them fits all
  three taught anchors, was graded against leave-one-out epicenter controls,
  and is **retired as a predictor** — with a planted-signal power check
  proving the null is not blindness.
- **Galactic reference** (`--galactic`) — per body, the separation from the
  Punarvasu crossover (the galactic–ecliptic node) and the Magha axis, drawn
  on the scope wheels.
- **Chatur Vyuham detector** — the fourfold array (crossing oppositions +
  nodal lock); its 1900–2026 census fires exactly once: June 1–6, 2016.
- **Precession clock** — the 25,739-year equinox cycle, 919.25 years per
  sector, with the deep-time atlas SVG (48,000 years of sector passages).
- **The report layer** (`--rasi`, `--report`) — the full classical horoscope
  page: Koch house cusps, planet table with nakshatra/pada/navamsam, Vimshottari
  Dasa/Bukti, and the RASI/NAVAMSAM box charts, reproducing the canon's own
  printout value-for-value.
- **The anchor library** (`astgraf-anchors`) — the recurrence principle as
  machinery: dossiers of past major events (the taught instances + the M9
  set), every fired contact with its trigger instant refined below one
  minute and the site's Ascendant timetable — oracle-tested against the
  taught minutes (Hyderabad 04:49/17:04 IST, Ulsoor 06:12/08:20).
- **The recurrence calendar** (`astgraf-recur`) — the similarity engine over
  the anchors: scan any span for episodes where an anchor's slow pattern
  re-forms, tightest instants below one minute, the anchor's Moon triggers
  completed inside each episode. Self-check: scanning Mar–Jul 2015 for the
  Nepal configuration returns exactly one episode, April 23–25.
- **The family calendars** (`astgraf-families`) — long-cycle recurrence at
  nakshatra-sector grain: every slow-pair conjunction with its canon sector,
  taught members reproduced (1881 → Aswini/Krakatoa, 2000 → Kritika/Sumatra),
  member-sector returns flagged forward (next: 2060, Kritika).
- **Inverse learning & outcome grading** — signature extraction over the USGS
  M7+ corpus, honest mining (declustered, climatology controls, permutation
  null), and `astgraf-outcomes`: automatic grading of every passed forecast
  window against the quake catalog, each spot with its spatial base rate.
- **The event-chart atlas** (`scripts/quake_atlas.py`) — a full chart per
  event **cast at its own epicenter**, for every quake catalog in the tree:
  13,339 charts, plus 40,017 era-matched controls. Descriptive census and
  inferential grading kept strictly apart, because merging them is how a
  census becomes a false discovery. [`QUAKE-ATLAS.md`](tools/astgraf/QUAKE-ATLAS.md).
- **Co-occurrence mining** (`scripts/pattern_mine_m7.py`) — pairs and triples
  of predicates, the conjunction-of-conditions shape every taught pattern
  actually has, over a unified M7+ corpus assembled across three catalogs
  (1,635 unique events, larger than any single file).

## Quick start

```bash
cd tools/astgraf
uv sync

# A 17-year yearly lens with aspect events and plots:
uv run astgraf --year 2000 --month 1 --day 1 --time 12:00 \
  --unit year --step 1 --count 17 --out out/demo

# The classical horoscope page for the 2015 Nepal-earthquake chart
# (reproduces the canon's QUAKE printout value-for-value):
uv run astgraf --year 2015 --month 4 --day 25 --time 11:40 \
  --utc-offset +05:30 --lon 86:00E --lat 28:00N --tropical \
  --unit hour --step 6 --count 1 --report --name QUAKE --place NEPAL \
  --no-aspects --out out/quake

# Sweep the doctrine rules over a date range and score them:
uv run astgraf-bands --start 2016-05-25 --days 15 \
  --rules doctrine-triggers.toml --out out/vyuha-2016

uv run pytest   # 263 tests
```

Full CLI documentation: [`tools/astgraf/README.md`](tools/astgraf/README.md).

## The epistemic contract

This project treats prediction claims the way its own doctrine demands —
*"the predicting researchers should confirm such events from records through
assiduous search and only then it can be predictable"*:

- **Everything taught is a retrodiction** until a registered forward window
  resolves. The taught instances (Nepal 2015, Hyderabad 2016, Ulsoor 2016,
  the June 2016 vyuham, Krakatoa→2004) all reproduce under live execution —
  and are labeled as retrodictions, not evidence of forward skill.
- **Forward windows are pre-registered** in
  [`WATCHLIST.md`](tools/astgraf/WATCHLIST.md) with exact instants, located
  spots, and regeneration commands, then graded automatically by
  `astgraf-outcomes` with spatial base rates. Nearest windows:
  **Sept 30 – Oct 4 and Oct 13 – 19, 2026**.
- **The location layer is demoted to experimental** (ratified 2026-08-04):
  every tested formulation of the world-spot rule measures at chance on
  1,435 M7+ mainshocks, so earthquake windows are *time-only* claims;
  registered spots stay graded as a pre-registered experiment, and the
  site channel is scoped to the taught local categories. The timing
  layers — which reproduce the taught instances to the minute — are the
  system's proven core.
- **Fourteen channels have been graded and every one failed its bar**, each
  with a power check proving the instrument could see the effect it did not
  find — three mining passes, six location families, the dwell doctrine, the
  taught flood signature in its own category, Predict.pdf's headline band
  rule at M7+ *and* on held-out M6, a full-vocabulary screen over epicenter
  charts, and a co-occurrence mine over pairs and triples. The full
  scoreboard, positive and negative together, is
  [`RESULTS.md`](tools/astgraf/RESULTS.md).
- **The band trigger is settled.** Its M7+ near-miss (lift 1.804, p = 0.069)
  rested on 12 firings against 7.0 expected. Pre-registered and re-run on
  10,324 held-out M6.0–6.99 events it gives **lift 0.915, p = 0.76 — the
  wrong direction**. The atlas shows why: the trigger fires at 0.41% of
  ordinary instants, so the M7+ figure of 0.84% was a 2× fluctuation on
  twelve events.
- **A screen can only see what it is powered for.** The taught patterns fire
  at ~0.1% of events — `nepal-double` at 1 event in 1,506, Chatur Vyuham at
  0. No mining pass over any existing M7+ catalog can validate or refute
  them; settling a rule that rare needs ~10⁵ events. That is a structural
  limit, not a result.
- **Some questions are not answerable at all, and saying so beats answering
  them badly.** The flood long-cycle clock (163.5 / 164.5 / 171.0 y) is one:
  its three candidates separate by at most **14.9° of phase** over a record
  covering 0.9 of a single cycle, and the systematic corpus contains
  **exactly one** conjunction epoch. Its verdict is *untested* — neither
  supported nor refuted — and the useful output is the power statement, not
  the p-value.
- **Negative results stay on the record.** The three data-mined candidate
  rules were *retired* when honest re-mining (declustered corpus, time-uniform
  climatology controls, 2-year-block split, 200-run permutation calibration)
  showed their lifts were artifacts — max lift 1.79 vs a null median of 1.73,
  p = 0.35. Their pre-registered windows remain graded as a falsifiable
  experiment. The doctrine channel is untouched by this verdict.
- **The whole system was adversarially audited**: two multi-agent audit
  passes (135 fidelity checks + 53 executed-repro flaw hunts), every finding
  fixed, ruled on, or recorded as a residual with its reason —
  [`AUDIT.md`](tools/astgraf/AUDIT.md) is the complete ledger.

## Provenance & fidelity

- **The canon is in-tree** ([`canon/`](canon/)) and the port is verifiable
  against it: all 144 planetary coefficients digit-for-digit, the truncated
  `PI = 3.141592654`, the epoch arithmetic, the Ascendant chain — pinned by
  oracle tests against the suite's own printouts (PRATEEK, QUAKE), the
  author's own program output (`canon/ASTROC.GRF` — 11 bodies × 41 daily
  rows reproduced within the file's 0.12° print resolution, confirming the
  BAS pre-increment; a sample output, not a pipeline stage), and bit-close
  parity with the corrected JS descendant of the suite.
- **One environment difference, not a source divergence**: the canon
  declares no `DEFDBL`, so the family's interpreter ran the series in
  single precision. The port computes in double, which can move the Moon
  1–2 arcminutes from a period print (and ~10 days of Vimshottari balance).
  The port follows the source, not the 1980s float hardware.
- **Exactly two engine behaviors deliberately diverge from the canon** (the
  Gregorian reform-day comparison and the instant-derived ayanamsa year), both
  bug fixes, both tested, both documented — see
  ["Deliberate divergences"](tools/astgraf/README.md#deliberate-divergences-from-the-basic-canon).
- **Accuracy honestly stated**: minute-level near the modern era,
  degrees-level drift by the 1600s (cross-checked against JPL DE440);
  deep-time plots show cycle shapes, not positions.

## History

`main` begins at the migration snapshot (the engine was developed inside the
local Astro app repository). The complete 45-commit
development history — every audit batch, ruling, and fix with its message —
is preserved on the [`astro-history`](../../tree/astro-history) branch, and
narratively in the [decision ledger](.claude/tasks/ASTGRAF_TOOL.md).

## Status & roadmap

Open doctrine inputs awaited: the NR/Rs/Ro constants table (Jupiter/Saturn
real-position offsets), `precess.mcd`, the Vimshottari lords for the 7-fold
instant level, and the 1,000-year flood-records list — which will
discriminate between the three candidate long-cycle clocks (Neptune tropical
163.5 y / Neptune sidereal 164.5 y / Uranus–Neptune synodic 171.0 y). The
Abhijit-28 ladder decision is parked; the news-archive outcome channel joins
when crawling credits allow.

## License

[MIT](LICENSE).
