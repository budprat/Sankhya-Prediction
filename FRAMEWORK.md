# The Sankhyan Prediction Framework

How prediction works in this program, as taught by NU (2026-08-01/02) through
Secrets of Sankhya, Predict.pdf, Mathcad-QUAKE.pdf, the BASIC suite, and worked
instances. Doctrine is NU's; the structure and any errors of synthesis are the
implementer's, awaiting NU's correction.

## 1. Foundations

**Substratum.** Space is a lattice of real interacting states. A planet crossing
the Sun–Earth ecliptic "twangs" it like a bowstring, and the constraint acts
INSTANTLY — like a row of a hundred billiard balls, touch one end and the other
end acts at once. What arrives later, at light speed, is only the *image*:

- A giant's **real position runs ahead of its observed one**
  (`(NR·Rs/2Ro − 1)·500/240`: Uranus +17.856°, Neptune +29.092°) — the
  substratum acts at the real position.
- An event's **place** is the light-time made geographic: the planet's
  culmination meridian rotated west by light-minutes × 15°/h
  (Jup 40 / Sat 80 / Ura 150 / Nep 240); latitude from declination.

**Karma.** Sankhya and the theory of karma are synonymous: happenings are
predestined, hence predictable. Natal astrology reads only karmic traits —
gunas, exposed as auras — never events. **Horary is the sole correct
real-time event-prediction method.**

**The clock.** The equinox drifts 50.35″/yr — one cycle in 25,739 years
(423.52/29845.4 × 1/365.25). The ayanamsa FIXES the moving zodiac so events
can be compared across time. Zero at Punarvasu ("the return of the ray"),
~32,165 years back over two cycles; Aswini sets the zero in this epoch
(~1996); one nakshatra passage = 919.25 years. Magha marks the flood epoch.

**The grid.** 28 equal divisions — the Sankhyan PHO-state count
((7+1/7)/2 = 3.57; 100/3.57 = 28) — with star names as markers ONLY.
Refinement ladder (NU ruling 2026-08-02: Predict.pdf's is canonical):
÷9 → 1/252 ("the real cycle"; KP's 243 forced his own ayanamsa), then
÷7 → 1/1764 — the "1/63rd fraction," the instant. Abhijit is the 21st
division, exactly opposite Punarvasu (ruling 2026-08-02; Predict.pdf's own
table said 22nd — overridden by the opposition argument and the Atharvaveda
19.7 order, and the tension is on record). Classical
practice fell back to 27 because Abhijit's observable spread collapsed
(<1°) — a deliberate 1/28 accuracy loss. Empirical rules end at Saturn:
in the ancients' 120-year observation window Saturn completed 4 cycles,
Uranus and Neptune not even two, so no empirical calibration was possible
for them.

## 2. The two-layer mechanics of an event

Every worked instance NU has given shares one structure:

**Slow layer — the loaded constraint.** Slow bodies form an exact geometric
lock, standing for weeks to months:
- **Chatur Vyuham** (the fourfold array, most dangerous): two oppositions
  crossing at 90° — Sun–Saturn × Jupiter–Neptune/Uranus — with the
  Rahu–Ketu axis locked into the cross. Once in 126 years: June 1–6, 2016.
- **Giant on a node**: Neptune on Ketu — real position at Nepal 2015
  (0.34°), observed at Hyderabad 2016 (1.15°). Two simultaneous constraints
  (real-Neptune on Ketu + real-Uranus on the Sun) = the Nepal quake.
- **Band coincidence** (Predict.pdf): bodies stacking in one of the 28
  bands; Moon+Ketu+Mars is the taught example, Uranus/Neptune presence
  escalates to catastrophic.

**Fast layer — the trigger.** The Moon, Sun, and Ascendant crossing the
loaded axes date the event to the day and hour (Hyderabad: Moon squares the
Sun–Jupiter conjunction ~14h IST on the peak flood day; the Asc sweeps the
cross arms twice daily). The Moon is the fast hand throughout: bands are
named from it, and its dwell time sets every sweep step.

**Location layer.** At the trigger instant, the light-time rotation gives
the spot (longitude from the rotated culmination meridian, latitude from
declination). Rule v2 (NU, 2026-08-02): the displacement follows the
planet's ACTUAL distance — almanacs that ignore light-delay hide the
connection; at nearest position the displacements are ~1000 km (Jupiter),
~2000 (Saturn), ~4000 (Uranus) — NU's Neptune 8000 exceeds the physical
~6700-7200 km, tension on record.

**Long-cycle families (NU, 2026-08-02).** A 1000-year record list exists
(NU to share) for the Uranus–Neptune conjunction — engine-measured period
167.6 y — as the large-flood family (2011–15 cluster: Uttarakhand, Kashmir,
China, Europe, US/Canada). The Jupiter–Saturn conjunction's ~120-year
same-region return is the Java family: 1881 Aswini conjunction → Krakatoa
1883; 2000 Kritika conjunction → 2004 Sumatra tsunami. Each 28×11 matrix
cell is to accumulate confirmed event-synchronisation factors from past
records, per category — the per-cell library the mining stages build.

## 3. Validation is part of the method

Predict.pdf: "the predicting researchers should confirm such events from
records through assiduous search and only then it can be predictable."
Retrodiction against recorded events is internal to the method, and the
system "can be made as accurate as one wants" by descending the ladder.
Scores are reported against chance baselines, pre-registered criteria,
hits and misses alike (see ledger: band trigger 0/31 vs 3.45 expected;
proximity census 4 episodes/30 yr; Chatur Vyuham 1/126 yr — on the exact
window NU named from memory).

## 4. Implementation map

| Framework element | Code | Validation |
|---|---|---|
| Ephemeris canon | `ephemeris.py` (truncated π, suite constants) | bit-parity with corrected JS engine; PRATEEK.docx (sidereal/E); QUAKE.pdf (tropical/Koch) |
| Precession clock | `precession.py`, `--precession` | book's own arithmetic (Kritika 158 CE, Punarvasu 4438 BC, 30,170 BC) |
| 252/1764 horary grid | `horary.py`, `--horary` | sample Asc → Punarvasu/Jupiter = docx C.Planet |
| Band table + triggers | `bands.py`, `astgraf-bands` (`--level`, `--proximity`) | 2013–15 + 30-yr censuses; catalog scoring |
| Chatur Vyuham | `vyuha_state`, `--vyuha` | unique June 2016 detection, 126-yr census |
| Real positions | `real_longitude` (Ura/Nep only) | Nepal chart: real-Nep→Ketu 0.34°, real-Ura→Sun 0.7° |
| Event location | `locator.py`, `--locate` | rule confirmed by NU; 12-spot archive check: 0 hits, 1 near-miss (honest negative) |
| Aspect geometry / scope | `aspects.py`, `scope.py`, `--scope` | Ura/Nep/Ketu 2000–2016 event set |

## 5. Open questions (NU's to close)

1. **NR/Rs/Ro constants table** — needed for Jupiter/Saturn real-position
   offsets (Jupiter's ≈21–22° would put real-Jupiter on Rahu at Hyderabad,
   completing both-giants-on-both-nodes).
2. Is Moon+Ketu+Mars *the* band trigger or one of a taught family?
3. Lords for the 7-fold instant level (the 9-lord cycle doesn't map onto 7).
4. Exact definition of the "Moon–Sun–Asc cross" trigger (square/conjunction
   to loaded axes? all three, or any?).
5. Sub-lord start convention; the dual ayanamsa reckoning (charts anchored
   294 CE vs epochal Aswini 1996) — implemented as coexisting, unratified.
6. Vyuha orbs (3°/5°/5° chosen by implementer from the 2016 probe).
