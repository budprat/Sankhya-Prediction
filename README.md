# astgraf

Modern Python port of the family BASIC suite's transit-graph pair:
**ASTGRAF.BAS** (positions over N periods → `ASTROC.GRF`) + **GRAPHDO.BAS**
(SCREEN 12 cosine plot). Same computation core, modern I/O.

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

## Outputs

| File | Replaces | Content |
|---|---|---|
| `positions.csv` | `ASTROC.GRF` | one row per period, 13 body longitudes |
| `positions.json` | — | full precision + params + retrograde flags + events |
| `svg/step_01_Ascendant.svg` … `step_13_Pluto.svg` | INKEY$ overlay | one-by-one cumulative reveal, GRAPHDO colors |
| `svg/combined.svg` | screen plot | all bodies + aspect markers |
| `aspects.csv` | manual matching | conjunction/square/trine/opposition crossings, bisection-refined to the minute |

The default plot is wrapped 0–360° with line breaks at the wrap — no more
up/down dual-trace ambiguity. SVG is resolution-independent, so output is
identical on every machine.

## The 252-division horary grid (`--horary`)

NU's Sankhyan prediction grid: **28 equal nakshatra divisions** (star names are
markers only; Abhijit is the 22nd equal division) × 9 equal subs = **1/252** of
the cycle, × 9 again = **1/2268** ("the instant"). `horary.csv` gives every body's
division/sub/sub-sub numbers and lords each period; `horary_events.csv` records
every 1/252-boundary crossing, bisection-refined, wrap- and retrograde-aware.
Conventions (stated for correction): division *n* takes Vimshottari lord
(*n*−1 mod 9); a division's first sub takes the division's own lord and cycles;
sub-subs likewise from the sub's lord. `--ayanamsa-rate 50.35` switches to NU's
50.35″/yr reckoning (`--ayanamsa-zero` sets its zero year, default 294).

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
- The linear ayanamsa `(year − 294) · 151 / 10800` wraps a full circle in
  ~25,720 years — the precession cycle is built into the formula.

## Tests

```bash
uv run pytest
```

Oracles: PRATEEK.docx (the 1987 ASTROLOG.BAS printout) and a headless run of
the app's JS engine (node vm harness).
