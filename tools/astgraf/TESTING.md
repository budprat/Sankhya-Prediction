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

**16 oracle tests** pin the engine against sources the implementer did not
produce:

| Oracle | What it pins |
|---|---|
| `PRATEEK.docx` | The 1987 ASTROLOG.BAS printout — all bodies, sidereal/E path |
| `QUAKE.pdf` | Tropical/Koch path: cusps, MC, sidereal time, planet table, star/pada/navam, Dasa/Bukti, the full report page |
| `Hyderaba-floods.docx` | NU's own 2016 cast: 13/13 planet rows, retrograde flags, dignities |
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
      power="plant the predicate into 10/5/2% of events")
```

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
5. **Record the verdict in `RESULTS.md`** with its numbers, whatever it says.
6. **If it survives, hold it out.** Replication is not confirmation — the
   dwell finding survived three kill attempts and two independent
   replications and was still false. Only strictly disjoint held-out data
   settled it (M6+ contains M7+; the test used M6.0–6.99).

## Where each layer's evidence lives

- **Engine fidelity** — the 16 oracle tests, and `FRAMEWORK.md`'s
  "Deliberate divergences" section.
- **Every graded claim** — `RESULTS.md`, positive and negative in one table.
- **Every ruling and its date** — `.claude/tasks/ASTGRAF_TOOL.md`.
- **Forward windows** — `WATCHLIST.md`, graded by `astgraf-outcomes`.

## Known debt in the test estate

The seven claims graded before this framework existed (`angle_grade.py`,
`asc_fingerprint.py`, `dwell_grade.py`, `loc_backtest.py`, `mine_usgs.py`,
`mirror_lifts.py`, `rotation_spectrum.py`, `spot_hypotheses.py`) carry their
designs in prose headers rather than `Claim` objects, and were not
pre-registered before running. Their results stand — each was
adversarially audited and power-checked — but they are **weaker evidence than
the four that followed the protocol**, and `RESULTS.md` should be read with
that distinction in mind. Porting them to `Claim` is open work.
