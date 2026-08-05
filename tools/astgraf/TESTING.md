# Testing — what is verified, how, and why it is trustworthy

Two entirely separate things are tested in this project, and conflating them
would be the easiest way to fool ourselves:

| Layer | Question | Answer type |
|---|---|---|
| **1. Engine fidelity** | Does the code compute what the BAS files compute? | Objective. Pass/fail against the author's own printouts. |
| **2. Claim grading** | Does a doctrine claim predict real events? | Statistical. Pre-registered, powered, refutable. |

Layer 1 must be perfect. Layer 2 is where the project's honesty lives.

---

## Layer 1 — Engine fidelity to the BAS canon

**The canon is in-tree** (`canon/`: ASTGRAF.BAS, ASTROLOG.BAS, GRAPHDO.BAS,
HORARY.BAS) so every claim of fidelity is checkable, not asserted.

**17 oracle tests** pin the engine against sources the implementer did not
produce:

| Oracle | What it pins |
|---|---|
| `PRATEEK.docx` | The 1987 ASTROLOG.BAS printout — all bodies, sidereal/E path |
| `QUAKE.pdf` | Tropical/Koch path: cusps, MC, sidereal time, planet table, star/pada/navam, Dasa/Bukti, the full report page |
| `Hyderaba-floods.docx` | NU's own 2016 cast: 13/13 planet rows, retrograde flags, dignities |
| `EXPLODE.docx` | The author's cast of **07-07-2013** (Bodhgaya explosions; Lac-Mégantic and Asiana SFO the day before) — 13/13 bodies, all cusps, sidereal time, dignities. A 2013 epoch, and the file sat unused until 2026-08-05 |
| `canon/ASTROC.GRF` | **The author's own program output** — 11 bodies × 41 daily rows, reproduced within the file's 0.12° print resolution, confirming the BAS pre-increment |
| Corrected JS engine | Bit-close parity across all bodies |

Run them:

```bash
cd tools/astgraf
uv run pytest -k "oracle or prateek or quake or docx or grf"   # 16 tests
uv run pytest                                                   # full suite
```

The suite passes **from any working directory** (the rule files resolve from
the package, not the shell's cwd).

### The frozen boundary

Canon-derived code is **frozen** (NU ruling): `ephemeris.py` entire,
`rasi.py` entire, `report.py` entire, `horary.py`'s `star_position` /
`NAKSHATRAS_27` / `SIGNS_12`, `grid.py`'s calendar arithmetic, `svgplot.py`'s
GRAPHDO constants. Modern layers (aspects, bands, triggers, locator,
signatures, anchors, recurrence, families, validation) are freely
changeable. If a line traces to a BAS line, it does not change without an
explicit ruling.

**Three deliberate divergences, all documented, all tested:** the Gregorian
reform-day comparison, the instant-derived ayanamsa year, and — an
*environment* difference rather than a source one — the canon ran in single
precision, so a period print can differ from ours by 1–2 arcminutes of Moon.

---

## Layer 2 — Claim grading

### The problem this framework solves

Eleven claims were graded before `validation.py` existed. Each script
invented its own controls, statistic and null. The variation was *partly*
principled — location claims genuinely need different controls from timing
claims — but the principle lived in prose, and seven of the eleven were never
formally pre-registered. That is how a project talks itself into a finding.

`src/astgraf/validation.py` makes three things **structural rather than
conventional**.

### 1. Pre-registration is a type, not a comment

A `Claim` cannot be constructed without every element of its design:
hypothesis, direction, statistic, control kind, corpus, verdict rule, and
power plan. Leave one blank and it raises. **You cannot run a test here
without first stating what would refute it.**

```python
Claim(name="flood-neptune-ketu",
      hypothesis="flood dates carry real-Neptune on Ketu more than era-matched instants",
      direction="higher",
      statistic="add-one smoothed lift",
      control="era-matched, 5 per event, ±365 d excluding ±7 d",
      corpus="1,886 declustered day-precision flood events ≥1700",
      verdict="p < 0.05 and lift > 1",
      power="plant the predicate into 10/5/2% of events",
      preregistered=True)
```

**`preregistered` has no default and must be stated.** A design written down
after its result is known is a legitimate record, but it is not evidence of
the same weight — and a retrospective declaration that silently reads like a
pre-registration is the precise failure this framework exists to prevent.
`True` is honest only when the design was committed to version control
*before* the run, where the git timestamp can be checked. `banner()` prints
the status on every run, and `report()` appends an explicit
**"this is a LEAD, not a finding"** caution to any *positive* result carrying
`preregistered=False`.

The design is then committed to git **before the script is run**, so the
timestamps are auditable. (Verifiable example: the cell-region design was
committed 13:55:27 and its result 14:00:45, with an empty diff between.)

### 2. Controls are chosen by the claim's kind, not by taste

| Claim kind | Control | Why |
|---|---|---|
| **Timing** — "this configuration accompanies events" | `era_matched_controls` — instants near each event | Holds the catalogue's completeness regime and the slow bodies' epoch fixed. Uniform controls once promoted an era-locked predicate to **lift 55** on nothing but a reporting gradient. |
| **Location** — "this points at a place" | `place_controls` — other *real* epicentres at the same instant | Random points on a sphere are not a null for seismicity, which lives on belts. |
| **Structure** — "these events resemble each other" | same-size samples from the reference population | Compares like with like. |

The null itself is `block_permutation_p`: re-label *within* each block —
which of the (1 event + k controls) was the event? Every block keeps its own
composition, so era, geography and seasonality cannot leak into the null.
A calibration test asserts the false-positive rate stays near α under pure
noise.

### 3. A null without power is silence, not evidence

`power_curve()` plants a known effect at 10/5/2% and reports recovery.
`report()` prints it with every result and **emits a WARNING that downgrades
the finding to UNDERPOWERED** if the instrument failed to recover a planted
effect. This is not optional politeness — it is the difference between
"we found nothing" and "we could not have found anything", and this project
has published both.

`poisson_sigma()` guards the opposite error: a large ratio on a tiny count.
The band trigger's lift of 1.804 rests on 12 firings against 7.0 expected —
**1.4 σ**, which the ratio alone hides.

---

## The protocol, per test

1. **Write the `Claim`** — hypothesis, direction, statistic, control, corpus,
   verdict, power. If you cannot state what would refute it, stop.
2. **Commit it before running.** Push it. The timestamp is the evidence.
3. **Run once.** No re-tuning, no second look at a different orb.
4. **Report through `report()`** so results cannot be shaped to flatter.
5. **If — and only if — the claim ties the program's clock to a REAL-WORLD
   event clock, confirm it on JPL DE440** (`de440.bsp`, in-tree). The program
   is the authority for doctrine geometry; DE440 is not a higher court for
   what the doctrine asserts. It matters when matching records: the engine
   sits 0.3–0.7° from DE440 in the modern era (the canon's own accuracy,
   faithfully reproduced), which is ~4 days of timing spread on a slow-pair
   crossing. Aggregate counts survive; individual sub-degree readings and
   episode boundaries do not.
6. **Record the verdict in `RESULTS.md`** with its numbers, whatever it says.
7. **If it survives, hold it out.** Replication is not confirmation — the
   dwell finding survived three kill attempts and two independent
   replications and was still false. Only strictly disjoint held-out data
   settled it (M6+ contains M7+; the test used M6.0–6.99).

## Where each layer's evidence lives

- **Engine fidelity** — the 16 oracle tests, and `FRAMEWORK.md`'s
  "Deliberate divergences" section.
- **Every graded claim** — `RESULTS.md`, positive and negative in one table.
- **Every ruling and its date** — `.claude/tasks/ASTGRAF_TOOL.md`.
- **Forward windows** — `WATCHLIST.md`, graded by `astgraf-outcomes`.

## The test estate — all twelve graded claims now run through the framework

**Closed 2026-08-05.** Every grading script in the project constructs a
`Claim` and prints its banner when it runs. There is no longer a script whose
design lives only in prose. Sixteen scripts, six of them pre-registered.

| Script | Claim | Pre-registered |
|---|---|---|
| `band_trigger_grade.py` | `band-trigger-m7` | ✅ |
| `band_trigger_m6.py` | `band-trigger-m6` | ✅ |
| `cell_region.py` | `cell-region-table` | ✅ |
| `flood_signature.py` | `flood-neptune-ketu` | ✅ |
| `deadliest_structure.py` | `deadliest-shared-structure` | ✅ |
| `flood_clock.py` | `flood-uranus-neptune-clock` | ✅ |
| `angle_grade.py` | `site-angle-location` | ❌ retrospective |
| `asc_fingerprint.py` | `ascendant-location-family` | ❌ retrospective |
| `dwell_grade.py` | `dwell-doctrine` | ❌ retrospective |
| `loc_backtest.py` | `rotation-spot-location` | ❌ retrospective |
| `mine_usgs.py` | `inverse-mining-v2` | ❌ retrospective |
| `mirror_lifts.py` | `cos-fold-mirror-mining` | ❌ retrospective |
| `rotation_spectrum.py` | `rotation-spectrum` | ❌ retrospective |
| `spot_hypotheses.py` | `spot-shape-diagnostics` | ❌ retrospective |
| `quake_atlas.py` | `quake-atlas-screen` | ❌ exploratory |
| `pattern_mine_m7.py` | `m7-pattern-mine` | ❌ exploratory |

**The port changed no result.** Every one of the eight retrospective scripts
was run before and after and its output diffed line by line: all eight are
byte-identical apart from the added banner. Their `Claim` transcribes the
design from the script's own prose header — it does not idealise it — and each
carries its result in `notes` so the record is self-describing.

**One implementation of the statistic.** The add-one smoothed lift had been
copy-pasted into six places with identical arithmetic. All now call
`validation.smoothed_lift`, including `signatures.mine_lifts`. Identical
formula, so no number moved; the point is that there is now one place to
audit.

The honest residue: the eight retrospective claims are still **weaker evidence
than the pre-registered five**, exactly as before. Declaring a design after
the fact does not make it a pre-registration, and the `preregistered` flag
exists so that distinction survives in the code rather than in a footnote
someone has to remember.
