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
  culmination meridian rotated west by the Mathcad quantity itself —
  `(a/2 − 1)·500/240` is ALREADY degrees of ground rotation (500 s per AU
  of travel ÷ 240 s per degree of Earth rotation), so the rotation is
  Jupiter 3.336° / Saturn 7.867° / Uranus 17.856° / Neptune 29.092°
  (rule v3, NU ruling 2026-08-05: "Mathcad version is the one"); latitude
  from declination. The superseded readings stay on record: the prose
  minutes 40/80/150/240 (= nearest-approach `a−1`, giving 10/20/37.5/60°)
  and the 2026-08-02 distance-true refinement — the Mathcad is defined on
  the ORBITAL RADIUS, so the rotation is a fixed constant per body.

**Karma.** Sankhya and the theory of karma are synonymous: happenings are
predestined, hence predictable. Natal astrology reads only karmic traits —
gunas, exposed as auras — never events. **Horary is the sole correct
real-time event-prediction method.**

**The clock.** The equinox drifts 50.35″/yr — one cycle in 25,739 years
(423.52/29845.4 × 1/365.25). The ayanamsa FIXES the moving zodiac so events
can be compared across time. NU (2026-08-04): the Earth's "wobble" is a
myth — in the Sankhya derivation of C and c the EMW frequency varies as
Rs/Ro, and the eccentricity caused by the solar/galactic velocity of
250,000 m/s is misread as a wobble; the Earth rolls smoothly, the axial
tilt balancing spin. The clock's measured drift RATE is unchanged by this —
Sankhya reinterprets the cause, not the arithmetic. Zero at Punarvasu ("the return of the ray"),
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
(<1°) — a deliberate 1/28 accuracy loss. NU ruling 2026-08-02 ("follow
exactly whats in ASTGRAF.BAS, we will decide later for Abhijit 28"): the
tool's default nakshatra layer is the classical 27-star system exactly as
the BAS carries it ("Magha" kept per the earlier ruling); the 28-equal
ladder stays implemented behind `--ladder 28`, parked until the Abhijit-28
decision. The 28-based band table and 28-sector precession clock are
untouched — their 28-ness is Predict.pdf's and the book's own. Empirical rules end at Saturn:
in the ancients' 120-year observation window Saturn completed 4 cycles,
Uranus and Neptune not even two, so no empirical calibration was possible
for them.

## 1a. THE AUTHOR'S ORBS — 2° minor / 18° major (stated 2026-08-05)

> *"Minor planet conjunctions lasts 2 degrees whereas major one lasts for 18
> degrees (**fresnel angle of simultaneous states**). All nine planets are a
> must for accuracy plus sun / moon and galactic ecliptic Aries and Asc (local
> time)."*

The orb is set by **body class**, not aspect type: **18° if either body is a
giant (Jupiter, Saturn, Uranus, Neptune, Pluto), else 2°**. Implemented as
`bands.doctrine_orb()`, read directly from his own worked example.

**HIROSHIMA — his reading, verified.** *"the first Atomic bomb on Hiroshima on
6th aug 1945 at exactly 8.16 am jap time … the exact spot where Asc / Nep / Jup
crosses, Sat con moon and Uranus conjunct Mars. Truly unique in the history of
disasters."* At 08:16 JST, 34.3853N 132.4553E, tropical (his "W = realtime"):

| His claim | Engine |
|---|---|
| Sat con Moon | Saturn 108.151° · Moon 108.017° — **0.13°** |
| Uranus conjunct Mars | 7.30° |
| Asc / Nep / Jup crosses | Jup–Nep 8.07°, Jup–Asc 8.40°, Nep–Asc 16.47° — all mutually inside 18° |

**⚠️ THE CORRECTION THIS FORCES.** This project graded **fifteen channels at a
3° orb**. Four of those five Hiroshima pairs are **invisible at 3°**. Those
tests were not measuring the author's rule — they were measuring a much
narrower one we assumed. Every "null" in `RESULTS.md` carries that caveat, and
re-runs at his orbs are recorded there.

**Other specifications in the same note, now on record:**
- **`E` / `W`**: *"E is eastern with ayanamsa deduction and W is western =
  realtime."* Tropical is the **realtime** frame — confirming the tropical
  rulings already used for angle work.
- **Body set**: *"All nine planets are a must"* — plus Sun, Moon, the galactic
  ecliptic, Aries, and the local-time Ascendant. **PLUTO IS EXCLUDED FOR NOW
  (NU ruling 2026-08-05)**, and this is a recorded TENSION with the author's
  sentence, not an agreement with it. Grounds for exclusion: Predict.pdf's own
  28×11 table has no Pluto column and `BAND_BODIES` follows it verbatim; a
  prior audit found Pluto silently leaking into min-over-bodies tests and
  treated it as a defect, restating every affected figure; and no taught
  reading — Nepal, Hyderabad, Ulsoor, the vyuham, Hiroshima — names Pluto.
  **Pluto remains COMPUTED by the frozen canon** (`ephemeris.BODY_ORDER`, the
  report page, the RASI/NAVAMSAM boxes) — the exclusion is only from doctrine
  classification (`MAJOR_BODIES`), so no canon output changes. Re-including it
  is a one-line change plus a re-run of every graded channel.
- **Grid**: HDMY unit × 2–60 periods; *"Y and 60 … if unit is 2 it is 120 yrs"*
  — exactly our `--unit/--step/--count`.
- **Controls**: *"rotate by changing asc. time — spread by changing Lat long"*,
  which is the inverse-search handle described in §2.

## 1b. The clocks — why every number in the doctrine is an Earth-rotation number

Put every motion in one unit: how long it takes to cross the author's smallest
cell, 1/81 of a degree (0.0123°). Rates are the ENGINE's own mean geocentric
apparent motion 2015–20 (which includes retrograde looping, so it exceeds the
net orbital drift — the apparent motion is what the chart plots):

| what moves | °/day | time to cross 1/81° |
|---|---|---|
| Neptune | 0.021 | 14.2 hours |
| Uranus | 0.032 | 9.3 hours |
| Saturn | 0.069 | 4.3 hours |
| Rahu / Ketu | 0.053 | 5.6 hours |
| Jupiter | 0.131 | 2.3 hours |
| Mars | 0.575 | 30.9 min |
| Sun | 0.986 | 18.0 min |
| Moon | 13.174 | 1.35 min |
| **Earth's rotation (Asc / MC)** | **360.99** | **2.95 s** |

**Nothing in the sky moves at the 3-second scale; only the ground does.** So
the author's "dwell time more than 3 seconds" cannot be a planet lingering —
it is Earth turning through a crossing zone. Every quantity in his briefing is
therefore an Earth-rotation quantity: 1° = 4 min, and 1/81° = 2.96 s.

**Dwell decoded (2026-08-05, both sessions independently).** Dwell = the
angular span of the crossing complex read at 4 min/°. Nepal: real-Uranus↔Sun
0.692° (2.77 min) + real-Neptune↔Ketu 0.342° (1.37 min) = 1.034° = **4.14
min**, against the author's stated "dwell time has been 4 minutes … because
both Uranus and Neptune crossed Ketu position one after another". The number
matches; the attribution does not.

**And the contradiction is INTERNAL to the author's own materials — it is not
our chart disagreeing with him** (verified 2026-08-05 by reading
`Mathcad-QUAKE.pdf` directly). That document, titled *"A QUICK ANALYSIS TO
SHOW THAT NEPAL QUAKE IS FROM TWO SIMULTANEOUS EVENTS"*, states both
crossings explicitly:

> "NEPTUNE in Pisces is behind KETU but is really at 29.09 deg ahead …
> 339 + 29.09 = 368.7 or 368.7−360 = 8.09 ARIES and CROSSES ecliptic at
> **8 deg Aries**" — Ketu's own degree.
>
> "URANUS in Aries 17.6 deg is really at 17.856 … 17.6 + 17.856 = 35.456 and
> is crossing the Solar ecliptic at **TAURUS 4.7 deg**" — which is where the
> **Sun** stands (34.74 = Taurus 4.74), not Ketu.

So the Mathcad says Uranus crosses the SUN and the prose says it crosses
KETU; they differ by 26.5°, and the engine reproduces the Mathcad
(real-Neptune↔Ketu 0.3423°, real-Uranus↔Sun 0.6929°, both to three decimals).
This matters beyond bookkeeping: the 4-minute dwell figure is the SUM of
those two separations, so the arithmetic the author quotes **only works under
the Mathcad reading**. The prose attribution is the error, and the dwell
number is itself evidence against it.

**Dwell GRADED AND CLOSED (2026-08-05) — both halves fail.** The construction
reproduces; the doctrine built on it does not.
- *Trigger half* ("dwell > 3 s ⇒ major shock waves"): vacuous as literally
  stated — 3 s IS 1/81°, so every crossing inside any usable orb clears it,
  at identical rates for events and controls. It selects nothing. Events also
  carry no more dwell than ordinary moments (+0.054 min at orb 3°, p = 0.42;
  sign reverses at orb 1°).
- *Magnitude half* (wider crossing → bigger event — the falsifiable and
  counterintuitive half): appeared at ρ = +0.32/+0.34 on M7+ (n = 44,
  family-wise p ≈ 0.03–0.04, independently replicated across two sessions),
  then **died on pre-registered held-out data**: 338 declustered M6.0–6.99
  events (a band disjoint from the M7+ corpus by construction) give
  **ρ = −0.040, p = 0.77**, wrong sign in every cut — pooled, single-crossing,
  both time halves, 1970+. Injection recovers a true ρ = 0.32 in 12/12 draws,
  so the instrument was not blind. Diagnosis: winner's curse — the max of
  four correlated cells at n = 44, where sampling noise on ρ is ±0.15.
- Caveat kept in the author's favour: a mechanism switching on only above M7
  would not show in the M6 band — but the M7+ result then rests on nothing
  but its own selection.

**His ground distances run ~11% optimistic.** 1° at the equator is 111.319 km,
not 100; the equator moves 465.1 m/s, not 400; the 1/81° cell is 1,374 m, not
1,234. His arithmetic is otherwise exact (240 s ÷ 81 = 2.963 s).

**The asymmetry that blocks location.** All three corrections he names —
rotation, ecliptic tilt, light travel — move LONGITUDE. Earth's spin cannot
move latitude at all. So the construction has three longitude mechanisms and
exactly one latitude mechanism, declination, which for the located set (the
four giants) caps at 23.71°N (measured achieved extreme) against Gorkha's
28.23°N. The 1/81 subdivision is a RESOLUTION, not an origin. Standing
question for the author: **what supplies the latitude?**

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
- **Both nodes occupied** (Hyderaba-floods.docx, NU's own cast of
  24-09-2016): Neptune on Ketu (1.1°) AND exalted Mercury on Rahu (3.7°),
  with Sun conjunct Jupiter (1.6°) and the Moon crossing their square —
  the nodal axis held at both ends while the fast layer fired. NU
  (2026-08-02): Hyderabad was ALSO site-specific — the local Ascendant
  crossed the Mercury-held Rahu end ~04:49 IST and the Neptune-held Ketu
  end ~17:04 IST each flood day (the evening cloudburst hour on Sep 23).
- **Giants on the Ascendant** (Ulsoor Lake fish kill, 2016-03-07, NU): the
  first SITE-SPECIFIC trigger — at Bengaluru's dawn the Ascendant swept the
  Neptune→Sun→Ketu→Uranus chain (exact crossings 06:12 and 08:20 IST,
  spanning the hours the fish were found), with the Sun 5° from Ketu two
  days before the total solar eclipse at that node. NU's mechanism, on
  record as doctrine: the Ura/Nep combo on the Asc lowers local
  micro-gravity field density toward space values and raises EM frequency,
  releasing free oxygen in water to lethal levels. Event categories thus
  extend beyond geophysics to biological/limnological effects.
- **Band coincidence** (Predict.pdf): bodies stacking in one of the 28
  bands; Moon+Ketu+Mars is the taught example, Uranus/Neptune presence
  escalates to catastrophic.

**Fast layer — the trigger.** The Moon, Sun, and Ascendant crossing the
loaded axes date the event to the day and hour (Hyderabad: Moon squares the
Sun–Jupiter conjunction (engine: exact squares 15:30–19:30 IST) on the peak
flood day; the Asc sweeps the
cross arms twice daily). The Moon is the fast hand throughout: bands are
named from it, and its dwell time sets every sweep step.

**Location layer.** At the trigger instant, the light-time rotation gives
the spot (longitude from the rotated culmination meridian, latitude from
declination). **Rule v3 (NU, 2026-08-05, "Mathcad version is the one"):**
the rotation is the Mathcad offset itself — Jupiter 3.336° / Saturn 7.867°
/ Uranus 17.856° / Neptune 29.092°, a FIXED constant per body (the Mathcad
is defined on the orbital radius), ground scale ~371 / 875 / 1,987 /
3,238 km at the equator. Two earlier readings are superseded but kept on
record: v1, the prose minutes 40/80/150/240 rotated at 15°/h; and v2
(2026-08-02), the distance-true refinement in which the displacement
followed the planet's ACTUAL distance (~1000 km Jupiter, ~2000 Saturn,
~4000 Uranus, with NU's Neptune 8000 exceeding the physical ~6700-7200 km
— that tension dissolves under v3, whose Neptune figure is ~3,238 km).

**Two-channel ruling (NU, 2026-08-02): real positions TIME the crossing;
the OBSERVED image PLACES the marker.** The substratum channel is instant
and lives at the real (ahead) positions — in every taught instance the
Mathcad offsets decide which alignment is exact and when (Nepal's
real-Uranus-on-Sun / real-Neptune-on-Ketu, Hyderabad's arithmetic), never
geography. The marker channel is light: the effect manifests where the
marker lands at arrival, and light arrives from the observed direction —
so `real:`-timed rules still locate from the observed meridian with the
light-time rotation. The coherent alternative is NOT real-meridian-plus-
rotation (an instant channel does not wait 40–240 minutes) but
real-meridian-with-ZERO-rotation; the two schemes differ by ~18–29° plus
the rotation term, so the first confirmed forward hit discriminates them.
Site rules (Ascendant crossings — Ulsoor, Hyderabad) are the instant
channel's local geometry, consistent with this split.

**Location-layer status (NU-ratified 2026-08-04, after the full test
battery — ledger, same date).** On 1,435 declustered M7+ mainshocks, every
tested formulation of the world-spot channel measures at chance: the
current rule, locate-at-the-event-minute, the zero-rotation real-meridian
alternative, and the site-angle channel (family p = 0.25); per-body
longitude-gap distributions match uniform, and the latitude channel is
structurally caged by declination (median unavoidable gap 9.1°). The
implementation stays (the rule is doctrine, ported faithfully and audited
clean), but its claims are re-scoped: **earthquake windows are time-only
claims**; registered spots remain graded as a pre-registered experiment
marked "experimental: retrospectively at chance"; the **site channel is
scoped to the taught local categories** (floods, biological), where it
reproduces NU's minutes 3-for-3 and awaits its own corpus; the NR/Rs/Ro
table bears on timing, not on rescuing quake spots (a constant offset
leaves a uniform gap distribution uniform). Reinstatement criteria: a
graded forward spot hit above spatial base rate, a flood-category corpus
win, or a new NU ruling on the spot channel's role. The timing layers —
which reproduce every taught number to the minute — are the doctrine's
proven core.

**THE AUTHOR ANSWERS THE LOCATION QUESTION HIMSELF: IT IS NOT ANGULAR
(2026-08-05).** On the eclipse fortnight he wrote:

> *"when two ecliptic events occur in the same fortnight the angle between the
> moon and suns path on the ecliptic remains same for those 14 days. You can
> imagine the earths surface locations pass in the same time and location zone
> **14 times**. As seen earlier major events dont occur daily even though all
> the planetary transits occur at the same daily cycle/locations. **Only a
> select few out of them do** and our need is to learn why it happens at the
> instant and location in advance **through gravity change calculations and not
> angular position changes which are too wide to be accurate**."*

This is the most important statement received about location, and it is a
concession that changes the target:

1. **He states that angular geometry cannot locate** — "too wide to be
   accurate". Fifteen graded null channels measured exactly that.
2. **The Earth passes the same configuration ~14 times per fortnight** and at
   most one produces an event. No purely angular quantity can pick which
   passage — the angles are identical across all fourteen.
3. **The discriminator he proposes is a GRAVITY CHANGE**, with the
   Ascendant/lat-long variation used as the *search tool*, not the mechanism.

**The standing question is therefore restated.** Not "what supplies the
latitude?" but: **"what gravity quantity discriminates the one passage in
fourteen?"** Until that is specified, no angular test can settle location —
which is a statement about the target, not about the engine.

**THE AUTHOR'S OWN LOCATION METHOD IS AN INVERSE SEARCH — and it is
underdetermined (established 2026-08-05, from his SankhyaStellarPrediction.html
note).** This reframes every location result in this file, so it is stated
before them.

He does not compute a spot from a planet. He describes selecting a point on
the plotted curve and then SEARCHING the (time, latitude, longitude, GMT)
space until the crossing lands, using the Ascendant as the handle:

> "we can **select any point in the curve** and see that moment chart and get
> the time, lat long"
> "If you vary any time, lat long GMT even a little you will see **ASC shift
> FAST** and MOON would also shift but slow"
> "we can take any event … and **search for time lat long GMT precisely**"
> "converts point in curve to **ANY PLACE ON EARTH** but at a one time, long
> lat and GMT"

**The arithmetic that follows.** `Asc = f(time, latitude, longitude)` is ONE
equation in THREE unknowns. Fixing a crossing degree therefore leaves a
two-parameter family of solutions, not a place. Measured directly: requiring
`Asc = 106.0°` on 2016-10-01, **every latitude from −60° to +60° admits a
solution**, each with its own longitude and time. The author's own phrase —
"ANY PLACE ON EARTH" — states the property exactly; he offers it as a feature.

**Consequences, which are large:**
- A method that can place an event anywhere places it nowhere. This is why
  every taught instance "locates" perfectly in hindsight: the site was known
  first and the search was run to confirm it.
- It explains the fifteen graded nulls. We tested FORWARD constructions —
  "does the sky point at the epicentre?" — which he never claimed. His method
  answers the INVERSE question, "given this place, when does the crossing
  reach its Ascendant?", and that is a TIMING question, which is precisely
  the layer that does work here.
- To become predictive the method needs a second independent constraint to
  collapse the two free parameters. He is aware of this and reaches for a
  nodal correction: *"It may not be exactly on that spot because Rahu has
  shifted so there could be an angular shift in Latitude Northward."*
- **A SECOND UNRESOLVED PHRASE OF HIS: "straight line" (EXPLODE.docx note,
2026-08-05).** Of the July 2013 cluster — Bodhgaya explosions, Lac-Mégantic,
the Asiana SFO crash — he wrote: *"Saturn / Jup in straight line and Saturn /
Moon is straight line. Problem is to find an easier way to plot the straight
line in time discarding velocity of light."* Measured on his own EXPLODE chart,
no reading resolves: observed Jupiter–Saturn 122.4°, real Jupiter–Saturn 126.9°,
observed Moon–Saturn 123.7°, Moon–real-Saturn 131.6° — every one 48–58° away
from 0° or 180°. All four sit near a TRINE. So "straight line" is not an
ecliptic-longitude alignment in his usage; the most likely candidate is a line
on the PLOTTED CURVE (the cos-fold mirror, `--mirror`), which our aspect engine
could not originally see. **Unresolved; needs his clarification.**

What his sentence DOES settle is the frame: *"discarding velocity of light"*
confirms the straight-line channel is the SUBSTRATUM channel — real positions,
no light-time rotation — the same instruction the Mathcad offsets encode, and
consistent with the two-channel ruling above. What he is asking for is a tool:
plot the alignment over time in the light-discarded frame.

**What DOES hold in that chart**: Moon 91.1° and Jupiter 92.4° are **1.3°
apart, both in Punarvasu pada 4**, with Jupiter EXALTED and Moon RULER — a
tight same-cell conjunction on the exact day he names. The 6 July events sit at
Moon–Jupiter 10.3°. His June flood pair does NOT share it (82.0° and 135.2°),
so "the same combo" spans two different geometries, and Moon–Jupiter conjunct
~12 times a year: base-rate untested.

**The standing question for the author is therefore sharper than "what
  supplies the latitude?": it is "what second condition collapses the
  Ascendant solve from one equation in three unknowns to a point?"**

**His program's conventions, read from the code (canon/SankhyaStellarPrediction.html,
dated 29 Sep 2016).** Variable `l` is longitude, EAST-NEGATIVE (`l < 0` prints
"East") — the same convention as the BAS and our port. Variable `b4` is
latitude, north-positive. **The form LABELS are swapped**: the field captioned
`Lat` accepts −180…180 (a longitude range) and the one captioned `Long`
accepts −90…90 (a latitude range). Anyone reading his worked examples must
check ranges, not captions.

**The location board, complete (2026-08-05).** Six families built and
graded on the same 1,435 declustered M7+ mainshocks, M7+ only per NU's
ruling. Every one carries a power check proving the instrument could see
the effect it failed to find — a null without demonstrated power is only
silence:

| # | family | what it claims | verdict |
|---|---|---|---|
| 1 | Rotation spots | sub-planet point rotated by the offsets | at chance |
| 2 | Ascendant rules | cell / lord / nakshatra / horary sub | p = 0.12–0.99 |
| 3 | Site-angles | the crossing pair on the site's MC/Asc | z ≈ 0 |
| 4 | Rotation spectrum | ANY rotation 0–360°, swept per giant | flat everywhere |
| 5 | Tangent ring | epicenter at a preferred angular radius | flat, 90° bin at 0.997 of null |
| 6 | Cell→region table | the 28×11 cells prefer areas (his own design) | max R 0.699 vs null 0.662, **p = 0.166** |

Family 4 is the strongest of the six: it retires the rotation idea across
its entire parameter space rather than at one point. Family 6 was the
author's own empirical design (Predict.pdf: cells accumulate "confirmed
event synchronisation factors from areas of our interest") and the only
family that escapes the declination ceiling structurally — pre-registered,
one test, and null. Its power check plants a region preference into a real
cell: a 30% plant lifts that cell to R = 0.777, above the family null's
95th percentile of 0.742, and to p = 0.000 against a same-size null.

**Why the geometric route is exhausted, derived from the clocks (§1b).**
A slow–slow crossing cannot define a meridian: the crossing lasts days
while meridians sweep 360° per day. Geometric longitude can therefore only
come from a fast body — and every fast-body channel (families 2 and 3) is
tested and null. Meanwhile latitude has exactly one geometric source,
declination, which cannot express 44.4% of M7+ epicenters with the four
giants, or 38.5% even with lunar latitude restored (the Moon reaches
+28.58°, enough for Gorkha in principle — but its declination at the Nepal
instant was +15.94°, so even that escape hatch fails on the flagship case).

**Standing question for the author, the one that unblocks everything:**
his recipe has three longitude mechanisms (rotation, ecliptic tilt, light
travel) and one latitude mechanism (declination) capped at 23.71°, against
Nepal's 28.23°N. *What supplies the latitude?*

**Long-cycle families (NU, 2026-08-02).** A 1000-year record list exists
(NU to share) for the Uranus–Neptune flood family (2011–15 cluster:
Uttarakhand, Kashmir, China, Europe, US/Canada). The conjunction recurs at
the **~171-y synodic** (engine 171.0; next cluster ~2165); NU's quoted
"~163 years" matches Neptune's TROPICAL return (engine 163.5 y) and the
old "168-year Neptune" is the doubled-Uranus convention (engine 167.7) —
the awaited records list discriminates between these three clocks. The Jupiter–Saturn conjunction's ~120-year
same-region return is the Java family: 1881 Aswini conjunction → Krakatoa
1883; 2000 Kritika conjunction → 2004 Sumatra tsunami. Each 28×11 matrix
cell is to accumulate confirmed event-synchronisation factors from past
records, per category — the per-cell library the mining stages build.

**The recurrence principle (NU, 2026-08-04, stated as the method's core):**
prediction of future events is BASED ON the analysis of past major events —
the same positions, conjunctions, and patterns repeat and cause similar
events. Past-event charts are therefore not merely validation material: they
are the anchor library from which forward windows are generated. The taught
rules and charts (Nepal, Hyderabad, Ulsoor, the 2016 vyuham, Krakatoa→2004)
are instances of this principle; the per-cell matrix library and the
long-cycle families are its aggregate form.

## 2b. Engine accuracy vs the orbs we test at (measured 2026-08-05)

Cross-checked against JPL **DE440** (in-tree, `de440.bsp`) at 2026-07-19:
Jupiter **0.273°**, Neptune **0.703°**, Saturn 0.465°, Uranus 0.353° from the
port's tropical longitudes. This is the CANON's accuracy — a 1900-epoch
Keplerian model reproduced faithfully — not a porting error. But it is the
same order as a 1° orb.

**Standing rule, correctly scoped (NU, 2026-08-05: "we rely on our program").**
The program IS the authority for doctrine geometry — the offsets, crossings,
bands and sectors are defined in its own frame, and disagreement with JPL does
not make a doctrine claim wrong. DE440 matters in ONE case only: when a claim
ties the program's clock to a REAL-WORLD event clock (a quake at a recorded
instant, a flood on a recorded day). There the sky is the arbiter, and the
0.3–0.7° offset becomes a real matching constraint — e.g. ~4.1 days of timing
spread on a Uranus–Ketu crossing, whose relative motion is only 0.0863°/day.
For anything internal to the doctrine, the program stands alone.** The doctrine's own 3° orbs are
unaffected, and aggregate statistics are robust (the Jupiter–Neptune episode
scan gives 18 episodes and ratio 1.03 on both ephemerides). What is *not*
robust is a quoted sub-degree separation, or an episode boundary: the 2026
Assam window is 18–22 July on the port and 15–19 July on DE440.

## 3. Validation is part of the method

Predict.pdf: "the predicting researchers should confirm such events from
records through assiduous search and only then it can be predictable."
Retrodiction against recorded events is internal to the method, and the
system "can be made as accurate as one wants" by descending the ladder.
Scores are reported against chance baselines, pre-registered criteria,
hits and misses alike. **The full scoreboard is `RESULTS.md`** — every
graded claim with its numbers, positive and negative in one place.

Superseded here for the record: the band trigger's first scoring used the
31-episode `NATURAL DISASTERS.xlsx` (grid mode 0/31 vs 0.63 expected;
proximity mode 1/31 — March 2015 North India rain — vs 1.79; baselines
step-honest per the 2026-08-02 audit fix, earlier quotes of 1.12/3.45 used
the inflated formula). At n = 31 that carried essentially no power. It was
regraded 2026-08-05 against 1,435 exact-instant quakes and 1,886 floods with
era-matched controls: **lift 1.804, p = 0.069 — short of its pre-registered
bar, and resting on 12 firings against 7.0 expected (1.4 sigma)**. The
proximity census (4 episodes/30 yr) and the Chatur Vyuham census (1 firing
in 126 years, on the exact window NU named from memory) stand.

## 3a. The resolution budget — what "accurate" can mean

The author (NU, 2026-08-05, with `canon/HORARYaura.docx` = HORARY.BAS) fixes
the system's grain from the horary ladder itself: the horary "divides by 9
and again by nine", so one cell is **1/81**. Applied to one degree, and
because one degree is simultaneously an angle, a duration and a distance:

| quantity | 1 degree | ÷ 81 (one cell) | author's figure |
|---|---|---|---|
| time (Earth's rotation) | 4 min = 240 s | 2.963 s | "about 3 sec" |
| arc | 60′ | 0.741′ | "lat long about a min apart" |
| ground at the equator | 111.32 km (his 100) | 1374 m (his 1234) | "1234 meters" |
| equatorial speed | — | — | 465 m/s (his "400 m/s") |

His conclusion: **"accuracy of prediction now is 1200 m and 3 secs"** — the
two are one statement, since 3 s × 400 m/s = 1200 m. Recomputed without his
round numbers it is ~1374 m and ~2.96 s; the 10% spread comes from 100 vs
111.32 km per degree. Descending one more 9 (1/729) would give ~1 s and
~460 m — "just divide these results by 3", his stated ideal.

**This retires the arbitrariness of the 3-second dwell threshold.** The
author's earlier rule — "plot ALL ecliptic crossings with dwell time more
than 3 seconds, for above that MAJOR SHOCK WAVES can be created" — is not a
free parameter: 240 s ÷ 81 = 2.963 s is *one horary cell of time*. A crossing
must persist for at least one cell to be resolvable at all. And the Nepal
figure lands on the same ladder: its 4-minute dwell is 240 s = **81 cells =
exactly one degree of rotation**, which is also what the taught separations
sum to (0.342° + 0.692° = 1.034°). Three independent statements of his
converge on the same quantum, which is the strongest support the dwell
reading has.

Status: **documented, not implemented.** NU's instruction is to keep it as a
sub-program "only to improve accuracy WHEN we can predict spot on" — the
location layer currently grades at chance (see `scripts/loc_backtest.py`), so
refining a spot to 1.2 km would be false precision on a marker that is not
yet in the right place. It is a finishing step, not a fix.

## 4. Implementation map

| Framework element | Code | Validation |
|---|---|---|
| Ephemeris canon | `ephemeris.py` (truncated π, suite constants) | bit-parity with corrected JS engine; PRATEEK.docx (sidereal/E); QUAKE.pdf (tropical/Koch) |
| Precession clock | `precession.py`, `--precession` | book's own arithmetic (Kritika 158 CE, Punarvasu 4438 BC, 30,170 BC) |
| Nakshatra layer | `horary.py`, `--horary` (classical 27 default; 252/1764 ladder behind `--ladder 28`) | QUAKE.pdf star/pada/navam rows; sample Asc → Punarvasu/Jupiter = docx C.Planet |
| Report layer | `rasi.py`, `report.py`, `--rasi`, `--report` (boxes, Koch cusps, MC, sidereal time, Dasa/Bukti) | QUAKE.pdf page reproduced value-for-value |
| Band table + triggers | `bands.py`, `astgraf-bands` (`--level`, `--proximity`) | 2013–15 + 30-yr censuses; catalog scoring |
| Chatur Vyuham | `vyuha_state`, `--vyuha` | unique June 2016 detection, 126-yr census |
| Real positions | `real_longitude` — all four giants since the 2026-08-04 Rs/Ro decode (Jupiter 3.3364°/Saturn 7.8672° PROVISIONAL from canon axes; Ura/Nep the Mathcad digits) | Nepal chart: real-Nep→Ketu 0.34°, real-Ura→Sun 0.7°; extended re-read adds real-Jup□Mars exact 58 h pre-quake |
| Event location | `locator.py`, `--locate` | rule confirmed by NU; 12-spot archive check: 0 hits, 1 near-miss (honest negative) |
| Aspect geometry / scope | `aspects.py`, `scope.py`, `--scope` (wrap-safe multi-crossing, lens contract) | 2010–11 Jup–Sat triple opposition at a yearly lens; every event exact at its instant |
| Trigger rules as data | `triggers.py`, `doctrine-triggers.toml`, `mined-triggers.toml`, `observed-triggers.toml` (TESTING channel, NU 2026-08-04: asc-trine-real-neptune, tropical site charts), `--rules` | all doctrine rules fire on their ground-truth charts; observed rule fires on Nepal tropical, frame-guarded |
| Inverse learning (signatures/mining) | `signatures.py`, `scripts/mine_usgs.py` (v2: declustered, climatology controls, permutation null) | NO survivors — max lift 1.79 vs null median 1.73, p = 0.35; mined rules RETIRED 2026-08-02 |
| Anchor library (recurrence principle) | `anchors.py`, `anchors.toml`, `astgraf-anchors` (dossiers: fired contacts with minute-refined trigger instants, site Asc timetable, band/vyuha state) | taught minutes reproduced: Hyderabad Asc-Rahu 04:50/Asc-Ketu 17:06 IST (taught ~04:49/~17:04), Ulsoor 06:12/08:21 (taught 06:12/08:20), Nepal real-Ura→Sun exact +18.1 h |
| Similarity engine + recurrence calendar | `recurrence.py`, `astgraf-recur` (slow pattern = non-Moon doctrine contacts; episodes with minute-refined tightest instants; Moon triggers completed inside episodes; `--category` per Predict.pdf's per-category design; `--composite` also requires the anchor's band/vyuha layers; timing only) | self-recovery: Nepal scan Mar–Jul 2015 → one episode Apr 23–25, 9/9 with the four-giant patterns; vyuham does not re-form in 2017; 2026–28 forward under extended patterns: NO full and NO n−1 episodes (the pre-extension alaska-1964 3/4 row stays registered on the WATCHLIST, annotated) |
| Forecast register | `WATCHLIST.md` | 19 windows (9 mined: instants+spots; 6 band: instants; 4 nodes: instants+Jupiter spots), outcome protocol |
| Event-chart atlas (all quake catalogs) | `scripts/quake_atlas.py`, `data/quake-charts-*.csv`, `charts/` | 13,339 charts cast at their epicentres; 4 corpora screened, all null (family-wise p 0.30 / 0.08 / 0.16); deaths-selected and magnitude-selected populations indistinguishable |
| Long-cycle flood clock | `scripts/flood_clock.py` (pre-registered) | Part 1 NOT ANSWERABLE — 3 clocks separate by ≤14.9° of phase over 0.9 of one cycle; Part 2 p = 0.393 on n = 1 conjunction epoch. Verdict: untested. Needs a systematic catalogue reaching ~1780–1860 (open question 7) |
| Co-occurrence mining (pairs + triples) | `scripts/pattern_mine_m7.py`, `atlas-patterns.toml` | 1,506 unified M7+ across 3 catalogs, 805 patterns; winner fails independence + split-half, best replicating 1.960 vs null-max median 1.957 |
| Cos-fold mirror crossing | `aspects.mirror_offset` / `find_mirror_events`, `mirror` rule primitive, `--mirror` | detection verified against GRAPHDO's own fold (Nepal Moon×Saturn 0.067° while 127° apart classically); MINED SIGNAL: none — best of 95 predicates lift 1.72 = the permutation null's median, p = 0.505 (`scripts/mirror_lifts.py`) |
| Location layer, families ruled out | `scripts/loc_backtest.py`, `scripts/asc_fingerprint.py` | rotation-based spots (4 readings) at chance; Ascendant-based rules excluded, p = 0.12–0.99 conditional and not |
| Long-cycle families | `families.py`, `families.toml`, `astgraf-families` (conjunction series with canon sectors, member-return flags) + conjunction rules in `doctrine-triggers.toml` | taught members reproduce: 1881→Aswini, 2000→Kritika; forward: 2040 conj in Chitra (NOT a member sector), next member-sector return 2060 Kritika; 1941 Bharani triple = unexamined candidate; Ura-Nep 1993 triple all in Poorvashada (next ~2165) |

## 5. Open questions (NU's to close)

1. **NR/Rs/Ro constants table — PARTIALLY CLOSED (NU, 2026-08-04): Rs/Ro
   = 213.3266821.** With it the Mathcad formula decodes completely:
   offset = (a/2 − 1)·500/240 where a = NR_n/213.3266821 is the planet's
   orbital radius in Earth-orbit units — NR₁₉ = 6384.463 (Neptune,
   a 29.9281), NR₁₅ = 4083.496 (Uranus, a 19.1420), both round-tripping
   the given offsets to all ten digits. STILL NEEDED: the Sankhya NR
   values for Jupiter and Saturn — the canon's own elements do NOT match
   the Sankhya radii (canon Uranus 19.2215 vs Sankhya 19.1420, a 0.08°
   offset difference — significant at doctrine orbs), so astronomical or
   canon axes cannot substitute exactly. NU ruled (2026-08-04, "decide
   between canon and standard, or test both"): the two differ by
   ≤ 0.0025° — immaterial — so the CANON's own axes were adopted as
   PROVISIONAL (Jupiter 3.3363593021°, Saturn 7.8672056771°, in
   `REAL_POSITION_OFFSETS`), expected within ~0.02° of the Sankhya truth
   by the Ura/Nep deviation trend; NU's exact NR values replace them as
   data when supplied. All candidate values ON RECORD (offset =
   (a/2 − 1)·500/240), so the arriving Sankhya NR values can be matched
   against their nearest source:
   | a source | Jupiter a → offset | Saturn a → offset |
   |---|---|---|
   | canon elements (ADOPTED provisional) | 5.20290493 → 3.3363593° | 9.55251745 → 7.8672057° |
   | JPL approximate J2000 | 5.20288700 → 3.3363406° | 9.53667594 → 7.8507041° |
   | textbook mean axes | 5.2026 → 3.3360417° | 9.5549 → 7.8696875° |
   Spread: Jupiter ≤ 0.0003°; Saturn ≤ 0.019° (the JPL Saturn axis is the
   outlier). Sankhya-trend expectation (Ura −0.26%, Nep −0.47%, shrinking
   inward): corrections within ~0.02°. (Earlier note stands: offsets run
   AHEAD; Hyderabad reads as Jupiter-on-Sun + Mercury-on-Rahu.)
   **SCOPE OF THE PROVISIONALS WIDENED 2026-08-05:** under locator rule v3
   the same `REAL_POSITION_OFFSETS` are also the ground rotation
   (`locator.ROTATION_DEGREES = dict(REAL_POSITION_OFFSETS)`), so these two
   provisional numbers now set **spot longitudes and derived light-minutes
   as well as real positions**. When NU's exact NR values land, Jupiter and
   Saturn spots move with them, and every published Jupiter/Saturn
   longitude (WATCHLIST rows, dossiers, signature `spot_lon:` features)
   must be regenerated — expected shift ≲ 0.02° of longitude (~2 km), so
   the correction is real but small. Uranus and Neptune are unaffected
   (their offsets are the Mathcad's own digits).
2. Is Moon+Ketu+Mars *the* band trigger or one of a taught family?
3. Lords for the 7-fold instant level (the 9-lord cycle doesn't map onto 7).
4. Exact definition of the "Moon–Sun–Asc cross" trigger (square/conjunction
   to loaded axes? all three, or any?).
5. Sub-lord start convention; the dual ayanamsa reckoning (charts anchored
   294 CE vs epochal Aswini 1996) — implemented as coexisting, unratified.
6. Vyuha orbs (3°/5°/5° chosen by implementer from the 2016 probe).
7. The 1000-year Uranus–Neptune records list (NU to share) — the per-cell
   matrix library's training corpus.
8. `precess.mcd` (referenced by Secrets of Sankhya; not yet shared).
9. **The Magha axis: sector-10 centre, or the galactic CENTRE?** The
   crossover was closed on 2026-08-05 (NU: "crossover means the
   galactic-ecliptic node"), and that ruling left its twin marker exposed.
   `MAGHA_AXIS_SIDEREAL = 9.5 × 360/28 = 122.142857°` was taken as the
   centre of the wheel's tenth sector. The author calls Magha the
   **galactic axis**, and the natural astronomical reading of that is the
   direction of the galactic centre — Sgr A* (RA 266.41684°,
   Dec −29.00781°) sits at ecliptic longitude **266.852°**, which is
   **suite-sidereal 243.00°**, folded at 180° to **63.00°**.

   | reading | sidereal | folded axis | source |
   |---|---|---|---|
   | sector-10 centre (in force) | 122.143° | 122.143° | 9.5 × 360/28 on the wheel |
   | galactic centre (Sgr A*) | 243.00° | 63.00° | IAU position, measured |

   The gap is **59°** — a fork, not a rounding difference, so the two
   cannot both be right and no orb hides the choice. Two consequences
   ride on it:
   - **Every Magha separation in `galactic.csv`** and every Magha spoke
     drawn by `--scope` moves by 59° if the reading changes.
   - **A frame defect rides along.** 122.142857° is 9.5 sectors *of the
     precession wheel*, so it is a WHEEL value despite the `_SIDEREAL`
     name — the wheel's zero is the 1996 equinox, an ayanamsa (~23.8°)
     from the suite's sidereal zero. `precession.equinox_offsets()`
     therefore uses it as-is (correct for a wheel value), while
     `galactic.marker_longitudes()` still treats it as sidereal and adds
     the ayanamsa for tropical charts. That is exactly the mismatch the
     crossover carried until 2026-08-05, and it is left in place
     deliberately: fixing it means choosing a frame, which is NU's call.
     Note the galactic-centre reading is a genuine sidereal direction and
     would resolve the defect as a side effect, the way the node did.

   What would settle it: the author's own words on whether "Magha
   galactic axis" names the flood-epoch sector of his wheel or the
   direction of the galaxy's core. If the latter, the constant becomes
   243.00° (or 63.00° as the folded axis) and `galactic.py` needs no
   other change — `galactic_separations` already folds Magha at 180°.

## 6. Document map

- `FRAMEWORK.md` — this file: the theory and its implementation status.
- `README.md` — tool-by-tool usage, the 60-period drill, honesty notes.
- `WATCHLIST.md` — registered forward windows, spots, outcome protocol.
- `PLAN.md` — current state, method rulings, next actions, what is blocked on NU.
- `RESULTS.md` — the evidence ledger: every graded claim with its numbers.
- `TESTING.md` — the two test layers: engine fidelity to the BAS canon, and the claim-grading framework (`validation.py`).
- `QUAKE-ATLAS.md` — 13,339 event charts across every quake catalog, and every pattern they surface, graded.
- `doctrine-triggers.toml` / `mined-triggers.toml` / `observed-triggers.toml` — rules as data by provenance: NU's taught rules; mined candidates (the three RETIRED 2026-08-02, windows stay graded); observed single-chart promotions in TESTING status (NU ruling 2026-08-04).
- `anchors.toml` — the anchor library (recurrence principle); `astgraf-recur` episodes register on the WATCHLIST.
- `families.toml` — the long-cycle families (nakshatra-sector recurrence); `astgraf-families` computes the conjunction calendars.
- `data/usgs-m7-1850-2020.csv` — pinned training corpus.
- `scripts/loc_backtest.py` — the location layer graded against a shuffled null (all readings at chance; the honest prior behind every spot).
- `../../canon/` — the author's own sources: `ASTGRAF.BAS`, `ASTROLOG.BAS`, `GRAPHDO.BAS`, `HORARY.BAS`; `ASTROC.GRF` (a SAMPLE output, the port's oracle at its print resolution); `SankhyaStellarPrediction.html` (his 2016 JS port — cos-fold graph, Koch hardcoded, 27 stars); `HORARYaura.docx` (the HORARY.BAS listing, source of the 1/81 resolution budget in §3a); `EQINAFG.pdf` (unread).
- `.claude/tasks/ASTGRAF_TOOL.md` (repo) — decision ledger, every ruling dated.
