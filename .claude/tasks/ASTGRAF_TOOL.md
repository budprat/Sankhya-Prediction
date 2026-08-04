# ASTGRAF Tool — Modern Python Port of ASTGRAF.BAS + GRAPHDO.BAS

NU ruling (2026-08-01): focus on ASTGRAF/GRAPHDO. Platform: **Python CLI → SVG files**,
adapting all BASIC/.grf formats to modern file formats. UX Phase 2 arc is parked.

**Framing (NU, 2026-08-01): this is a PREDICTION program, not a horoscope tool** —
event timing via transit patterns (crossings, clusters, aspects, precession-cycle work).
It will move to its own folder/project later; `tools/astgraf/` is temporary housing.
The package is already portable: self-contained uv project, no app dependencies
(the JS-oracle values are baked into the tests; harness scripts live outside the repo).

## Goal
One `uv` project at `tools/astgraf/` that reproduces the ASTGRAF computation verbatim
(same algorithm, same constants — the family canon) and replaces the 1990s I/O:

| Heritage | Modern |
|---|---|
| ASTROC.GRF fixed-width text | `positions.csv` + `positions.json` (full precision, params, retro flags) |
| SCREEN 12 pixel plot | SVG (resolution-independent — NU's "pixel definition" concern) |
| cos(λ) fold (up/down dual-trace ambiguity) | wrapped 0–360° plot, line-break at wrap; `--style cosine` keeps heritage view |
| INKEY$ one-planet-at-a-time overlay | cumulative sequence SVGs (`step_01_Asc.svg` … `step_13_Plu.svg`) + `combined.svg` |
| manual number-matching for conjunctions | aspect events (0/90/120/180°) auto-detected, bisection-refined to the minute, `aspects.csv` + markers |
| east-negative / packed DD.MM inputs | modern conventions at CLI (east-positive, UTC offsets, `76:57E`), tested conversion to engine internals |

## NU requirements (from 2026-08-01 message)
1. Arbitrary period unit (Y/M/D/H) × any step × up to 60+ divisions (800y steps → deep time).
2. Ayanamsa toggle sidereal/tropical (galactic-axis / precession work; linear formula wraps in ~25,720y by construction).
3. Graph as separate portable file(s).
4. Planets drawn one by one (cumulative reveal), colors per planet (GRAPHDO palette).
5. Kill the up/down trace ambiguity.
6. Aspect chart: conjunction/square/trine/opposition are the real guides.
7. (deferred, research) "rotate longitude to locate event lat/long" — Jup 40min/Sat 80/Ura 150/Nep 240 idea; revisit after v1.

## Verification (tests before code)
- Oracle: PRATEEK.docx (28-08-1987 02:55 AM, Rohtak 76:57E 28:48N, GMT+5:30, sidereal, equal):
  10 honest bodies ±0.02°, Asc 80.1, ayanamsa 23.670648…, retro flags Jup/Ura/Nep only.
  Mer/Ven docx minutes are shim-fudged → 0.05° tolerance; Moon pinned to honest engine value
  168.66934322 (probe-derived) at 1e-6.
- Grid: month/day overflow normalizes through the JD formula (BASIC trick), hourly ΔJD = step/24.
- Aspects: synthetic crossings incl. 0/360 wrap; bisection refinement accuracy.
- CLI e2e: real run writes all artifacts, CSV row count, JSON schema, SVG well-formed.

## Honesty caveats (stated to NU)
- Keplerian mean elements are epoch-1900-calibrated: minute-level timing near modern era;
  degrees-level drift at ±30,000–48,000y (qualitative cycle shapes only). Labeled in output JSON.
- Faithful-port quirks kept deliberately for canon parity (e.g. AU scaled by π/180 — angle-invariant).

## Status
- [x] Branch `feature/astgraf-tool` off main @ 8f24ad4
- [x] Scaffold uv project
- [x] Tests written (red first; 33 green)
- [x] Ephemeris port green vs oracle — bit-identical (10 decimals, 13 bodies) to the
      canon-corrected JS engine; requires truncated PI 3.141592654
- [x] Grid/aspects/SVG/CLI green
- [x] E2E run on NU's 2000→2016 example (`tools/astgraf/out/2000-2016`, gitignored)
- [x] Commits: 04ff9bb (tool), lockfile chore

## Discoveries (2026-08-01, verified on file)
1. **JS engine pi**: `var pi = 3.1415926540000000` (line 457) = BASIC `PI = 3.141592654#`.
   Full-precision pi diverges the Moon by ~0.01 arcsec — port must use the truncated value.
2. **NEW JS ENGINE BUG (third transcription bug)**: the `ss2` T² array (line ~971) omits
   Sun's two zero rows (node, inclination — ASTROLOG.BAS lines 3920–3930), shifting all
   later T² coefficients two slots. Effect at 1987: Sun +0.018″, **Mercury +16″, Venus +21″**,
   Mars −0.28″, sub-arcsec knock-ons to outer planets via the Earth vector.
3. **Shim connection**: with ss2 corrected, the engine honestly prints Mercury 47′ and
   Venus 40′ — exactly the docx values the Prateek shim hardcodes. The shim's Mer/Ven
   fudges are symptom-patches for THIS bug. Remaining shim deltas: Moon 41′ (docx) vs
   40.16′ (canon) — plausibly single-precision drift in the original GW-BASIC run —
   and the dasha/sub-sub rows derived from it.

## The 252 system (NU spec, 2026-08-01) — BUILT (v1)
NU: horary is the ONLY correct real-time prediction method (disasters). Hierarchy
1/28 → 1/252 → 1/2268 ("the instant" ≈ reciprocal of Earth's circumference in time
divs). KP's 243 (27×9) forced his own ayanamsa; the real cycle is 252 (28×9).
28 = Sankhyan PHO-state count (100/3.57). Star names are markers only → divisions
are EQUAL. Abhijit's observed spread shrank (<1°) which is why classical practice
dropped to 27 (losing 1/28 accuracy). Ayanamsa: zero at Punarvasu ~32,165 ya;
markers rotate quadrant-wise (Punarvasu→Svati→Abhijit→Aswini); Aswini sets 0 in
this epoch; usable rate 50.35″/yr, shifts segment in ~1000 yr. Vedic natal
astrology predicts KARMIC traits (gunas/auras), NOT events; horary predicts events.
Implemented: `horary.py` (grid + lords + crossings), `--horary`, `--ayanamsa-rate/zero`.
Consistency check: sample Asc 80.1068° → division 7 Punarvasu, lord Jupiter = docx C.Planet.

## Precession clock (from NU's Secrets of Sankhya excerpt, 2026-08-01) — BUILT
Doctrine source resolves the constants: cycle **25,739 y** (423.52/29845.4 → 1/70.47 ×
1/365.25), rate 50.352″/yr (same fact), 919.25 y/sector. Anchor: book's own arithmetic
(written ~1996) puts equinox at wheel-0 then — Kritika 2 back (158 CE), Punarvasu 7 back
(4438 BC), Makha(Magha) 10 back (flood epoch ~6280-7200 BC), two-cycle Punarvasu zero
~30,170 BC ("32,165 less 1996"). Implemented `precession.py` + `--precession YEAR` +
`--precession-zero` + precession_wheel.svg. NOTE tension: NU's earlier "Aswini shifts to
next segment in ~1000 years" implies equinox near Aswini TOP now (anchor ~2915), vs the
book's equinox-at-0-in-1996; default = book, flag overrides — NU to rule. Also: book says
Abhijit "exactly 180° opposite Punarvasu" — with classical ordering (Abhijit 22nd) sector
centers are 192.9° apart; opposition is exact only if Abhijit were the 21st sector. Kept
classical ordering; flagged, NU to rule. NU RULED (2026-08-01): "Magha" is correct —
prediction program uses Magha; BASIC's "Makha" is the variant (app engine untouched).

## Event locator — BUILT (NU confirmed the light-time reading, 2026-08-01)
NU's Jup 40/Sat 80/Ura 150/Nep 240 minutes ARE the planet-to-Earth light-travel times.
Rule (confirmed): at the refined crossing instant, rotate the planet's culmination
meridian WEST by light-time × 15°/h; latitude = declination. `--locate` → locations.csv.
Engine now exposes GMST, real obliquity, and per-planet geocentric ecliptic latitude
(pure addition; canon oracle unchanged). Worked-example validation from NU still welcome.

**Atharvaveda 19.7 list (NU, 2026-08-01, deferred):** 28-asterism list starting Krittika,
with **Abhijit 21st, Sravana 22nd** in hymn order (incl. Bhanu/the Sun as 8th, Bharani
28th) — bears on the deferred Abhijit-slot question; "rest we decide later" per NU.

## Band-coincidence scanner — BUILT + FIRST VALIDATION RUN (2026-08-01)
Predict.pdf method automated (`bands.py`, `astgraf-bands`): 28×11 site-free table,
Moon+Ketu+Mars trigger, Ura/Nep escalation, 12h sweep, episode merging, catalog xlsx
parsing (messy free-text dates handled), chance-baseline scoring. **Result of the
2013–2015 run vs NU's 31-event catalog: trigger fired ONCE (2013-05-09/10, Bharani,
no giants); 0/31 catalog hits vs ~1.12 expected by chance.** As literally specified
at 28-band granularity the trigger is very rare (~1 episode/3yr) and shows no
catalog association yet. Post-hoc note (NOT a scored hit): the episode ended the day
Cyclone Mahasen's precursor formed in the Bay of Bengal. Earlier locator spot-check
(12 slow-aspect events vs USGS+best-track archives): 0 hits, 1 near-miss (Kirrily,
+3d/~1150 km), 11 misses. Knobs to explore with NU: band-specific rules (PDF's
Aswini example), ≥N-body stacking as generalized trigger, finer sub-band levels,
different trigger sets. firecrawl credits exhausted (news-archive channel blocked).

## Sub-band levels — BUILT + RUN (NU knob choice, 2026-08-01)
`--level 0/1/2` = band / ÷9 (1.43°) / ÷63 (0.204°, PDF's "1/63rd"), step defaults
12h/1h/0.2h. Results: L1 fired ZERO times 2013–2015 AND zero across 1990–2020
(263k samples); L2 zero. Probe (30-yr): tightest Moon+Ketu+Mars spread = 0.758°
on 2018-09-20 06:00 UT (Mars 278.54/Ketu 279.30/Moon 279.27 — STRADDLED the fixed
L1 cell boundary at 278.57 by 0.03°, hence no fire); next: 1.00° 2004-11-11,
1.11° 2003-01-27. Insight for NU: fixed-grid cells quantize away near-triples —
if the doctrine means PROXIMITY (spread ≤ 1/252 of cycle) rather than same-cell,
a --proximity trigger mode is the fix (not built; awaiting NU). Nearest notable
events to probe dates fall OUTSIDE ±3d (Palu M7.5 quake+tsunami 2018-09-28 = +8d).

## Proximity mode — BUILT + RUN (NU ruling "proximity", 2026-08-01)
Trigger = circular spread of Moon+Ketu+Mars ≤ level span, grid-free; giant escalates
within one span of the cluster; band named from the Moon. Results:
- L1 census 1990–2020: 4 episodes — 1996-04-17 (Revathy), 2003-01-27 (Jyestha),
  2004-11-11 (Swathy), 2018-09-20 (Abhijit, tightest 0.758°). None hits a famous
  natural disaster within ±3d from knowledge; 2018-09-20 sits BETWEEN Mangkhut
  landfalls (−4/−6d) and Palu quake+tsunami (+8d), both outside window.
- L0 proximity 2013–2015 @1h: 3 episodes — **2013-05-08→10 in ASWINI (the PDF's own
  example band; grid mode had called it Bharani)**, plus 2015-02-20→21 and
  2015-03-21→22 both CATASTROPHIC + Uranus (Uthra Badra). Catalog: 1/31 hits
  (March 2015 North India rain, month-window) vs 3.45 expected by chance — still
  no statistical support; stated plainly. Post-hoc checkables (not scored): Mahasen
  precursor formed 2013-05-10; Atacama floods 2015-03-24/25 within margin of ep 3.
- L2 proximity cannot fire 1990–2020 (min spread 0.758° > 0.204°; from probe, not run).

## Chatur Vyuham detector — BUILT + VALIDATED (NU doctrine, 2026-08-01)
NU: fourfold array = most dangerous constraint; instance "May end 2016": Sun opp
Saturn, Jup opp Ura/Nep, nodes in line at 90°, Saturn closest. Engine probe CONFIRMED
all axis elements to the day (Sun-Saturn 179.75° Jun 3; Jup-Nep 178°; cross exactly
90.00° Jun 4; node axis 3.2° from Jupiter arm). Detector: vyuha_state (orbs 3/5/5,
levels vyuha|vyuha+nodes, partner Nep/Ura), find_vyuha_episodes, CLI --vyuha, engine
gained geocentric distance exposure (additive; canon intact). **Census 1900–2026
(46k days): the array fired ONCE — 2016-06-01→06 vyuha+nodes, best cross 89.56°.**
Saturn-closeness element measured honestly: June 2016 = 26th percentile (engine minima
Dec 1914/Dec 1973 perihelic oppositions) — the once-in-10,000-yr closeness claim does
not hold in this engine for 2016; the array's uniqueness does. Post-hoc (unscored):
German/French flood disasters (Braunsbach/Simbach, Seine crest) fell June 1–4 2016,
dead center in the window.

**Conventions awaiting NU confirmation:**
- Sub-lord start: first sub of a division takes the division's own lord (KP-style start, equal spans).
- Ayanamsa zero year for the 50.35″/yr rate: defaulted to 294 CE — NU to confirm the Aswini-zero epoch.
- Sub-sub events not yet emitted (only 1/252 crossings); add when NU wants "the instant" level.

## Open NU decisions
- Fix `ss2` in the app engine (Resources + root HTML)? Precedent: "fix both" ruling on
  the earlier obliquity/Venus typos. Strengthens the case to remove the shim.
- Shim remove/keep (pending since the W-branch hunt) — now mostly root-caused.
- Horary 249 → 243 alignment (from HORARY.BAS analysis).
- Aspect-body filter flag for astgraf (yearly runs alias fast movers: 1130 events).
- "Rotate longitude to locate event" research idea — deferred from v1.

## Inverse-learning arc (2026-08-02) — consolidated
- Declarative trigger system: triggers.py + doctrine-triggers.toml + mined-triggers.toml,
  seven primitives + trine, real: prefixes, escalate blocks; --rules sweeps/scores any file.
- USGS M7+ 1850-2020 pinned (1,548 events, 1,472 second-precision, 0 missing coords).
- Signatures (signatures.py): all pair seps obs+real, bands, spreads, distances, spots,
  3 matched controls/event; screening miner with split-half validation; shuffled-null
  locator check (median 4,885 vs 5,159 km null). Survivors (all real-position predicates):
  rsep Ura-Sat conj 1.80/1.64, rsep Nep-Mer opp 1.76/1.41, rsep Ura-Sun tri 1.52/1.31 —
  sub-significance candidates → mined-triggers.toml (NU ruling: separate file).
- WATCHLIST.md registered: 9 mined windows w/ exact instants + spots + region names,
  6 band-trigger windows (secondary giant spots), outcome protocol. Locator v2
  (distance-true light-times per NU 2026-08-02; Neptune 8000km tension recorded);
  v2 spot amendments in WATCHLIST.
- Long-cycle doctrine rules: Ura-Nep conj (engine census 167.6y; 1649/1820/1991 clusters;
  flood family) and Jup-Sat conj (1881 Aswini → Krakatoa 1883; 2000 Kritika → 2004
  tsunami; next 2040). Rulings applied: ladder ÷9÷7 (1764 instant grid, lords undefined),
  Abhijit 21st (opposite Punarvasu exactly). QUAKE.pdf = tropical/Koch oracle in tests.
- 60-period drill documented as one-command lenses (README); demo converged both lenses
  to 2015-01-31 08:17 UT Ura-Ket conj @ 80.55E 4.67N.
- Still needed from NU: NR/Rs/Ro table, precess.mcd, 1000-year Ura-Nep records list,
  7-level lords, Moon-Sun-Asc cross definition, branch merges.

## Hyderaba-floods.docx (NU, 2026-08-02)
NU's suite-cast chart of the flood (24-09-2016 10:00 IST, 78E 16N, tropical/Koch) —
now the SECOND W/W engine oracle (arcminute parity, first-run pass). The chart itself
resolves the "Jup at Rahu" question: Rahu was held by EXALTED MERCURY (3.7°), Ketu by
Neptune (1.1°), Jupiter was conjunct the SUN (1.6°) with the Moon crossing their square
— both nodes occupied + fast-layer cross. Earlier ledger speculation (Jupiter offset
~21° closing the gap) WITHDRAWN: real-position offsets run ahead, not back. Candidate
rule for NU: "nodes doubly occupied" (any body conj Rahu AND any body conj Ketu) —
not built, awaiting word.

## Nodes-doubly-occupied rule (2026-08-02, NU "go")
New primitive nodes_occupied (require both/either); doctrine rule: planets (Moon
EXCLUDED — fast hand per FRAMEWORK §2; with Moon included the rule fires monthly
and scores at chance 6/31 vs 6.72) holding Rahu AND Ketu within 4°; giant at either
node escalates. Fires on Hyderabad (catastrophic), not Nepal, not quiet dates.
Census 1900–2026: 64 episodes. Forward: Jupiter holds Ketu Jan–Mar 2027 with
Mercury/Sun/Venus successively on Rahu — 4 windows registered in WATCHLIST.
BONUS census find: nepal-double fired 4×/126y — 1915-02, 1948-07, 1981-12,
2015-04-24→27 (Nepal quake in-window; by construction) — ~33-year spacing.

## Ulsoor Lake instance (NU, 2026-08-02)
Fish kill 2016-03-07 Bengaluru = first SITE-SPECIFIC trigger: Asc swept
Nep(06:12)→Sun(sunrise)→Ketu(07:00, eclipse 2d later)→Ura(08:20) through the
discovery hours — engine-verified. NU mechanism recorded (gravity-density drop →
EM rise → free oxygen). Built: rules CLI --site-lon/--site-lat/--utc-offset,
mentions_ascendant guard (Asc rules skipped sitelessly), doctrine rule
uranus-neptune-combo-on-ascendant (cluster Asc+Ura+Nep ≤45°; ~2.6h/day windows
in close-giant eras; era-discriminating: no fire 1960 when giants 84° apart).
Event categories extended to biological/limnological.

## Hyderabad was site-specific too (NU, 2026-08-02)
Engine-verified: local Asc crossed Mercury@Rahu ~04:49 IST and Neptune@Ketu
~17:04 IST on both flood days (evening cloudburst Sep 23 at the Ketu crossing).
New composite doctrine rule nodes-held-ascendant-cross = standing double-node
constraint + Asc within 5° of either held end (elegant reuse: nodes_occupied
with bodies=["Ascendant"], require="either"). Fires dawn+evening at Hyderabad
on the flood days, silent at noon and on unheld-node dates. WATCHLIST notes the
Jan–Mar 2027 double-occupation windows now yield per-site daily hours via this rule.

## Innovation batch (NU: "#2 then #6 and #4", 2026-08-02)
- astgraf-matrix: 28×11 per-cell event/control rates + heatmap SVG (Predict.pdf's
  library rendered; run on 1548/4644: top cells Moon@Uthra 1.50, Sat@Revathy 1.48 —
  modest, consistent with screening; outer columns baseline-confounded, flagged).
- astgraf-atlas: deep-time SVG (precession stripes 48k yrs + doctrine epochs +
  modern conjunction panel with Krakatoa/2004/2016 marks; census constants embedded
  with provenance).
- astgraf-outcomes: automated USGS grading of passed windows (hit/clear/pending,
  injected-fetch tested offline; live run 9/9 pending). WATCHLIST + README updated.

## 2026-08-02 — Follow ASTGRAF.BAS exactly: classical 27 default, Abhijit-28 parked
- NU: "follow exactly whats in ASTGRAF.BAS, we will decide later for Abhijit 28."
  Clarified via AskUserQuestion: revert scope = horary layer ONLY (bands 28×11 per
  Predict.pdf and the 28-sector precession clock stay as taught); spelling = keep
  "Magha" (earlier explicit ruling stands over the BAS's "Makha"); the 252/1764
  ladder stays available behind --ladder 28, OFF by default, nothing deleted.
- Fact base: ASTGRAF.BAS carries the 27-name STAR$ list (DIM :38, READ :49, DATA
  :348-351) and never uses it — no nakshatra arithmetic exists in the graph
  program; the position/pada/navam arithmetic lives in ASTROLOG.BAS 5680-5790.
- Implemented: horary.py NAKSHATRAS_27 (BAS DATA verbatim + Magha), SIGNS_12 (z$
  order), star_position() = verbatim ASTROLOG.BAS pada-count port, oracle-pinned
  to all 12 QUAKE.pdf planet rows (nakshatra/pada/navam). --horary now defaults
  to classical 27 columns; --ladder 28 restores the 252-grid + crossing events;
  --ladder without --horary errors. Stale "2268" ABOUTME headers corrected
  (audit Part II F5/F6). 136 tests passing.
- Audit note (2026-08-02, AUDIT.md): both audit workflows' findings documented —
  Part I all 53 flaw-hunt findings with executed repros, Part II the fidelity
  audit's 34 flags + 101 verified checks. None remediated yet; AUDIT.md is the
  work queue and its fix-order is awaiting NU's sequencing.

## 2026-08-02 — RASI/NAVAMSAM box output (--rasi)
- NU: "we need to generate RASI and NAVAMSAM as outputs for interpretations same
  as in QUAKE.pdf." Implemented rasi.py: verbatim port of the ASTROLOG.BAS
  HOROSCOPE subroutine (6120-6880) — AR() square walk (DATA 12,1,2,3,11,4,10,5,
  9,8,7,6), ZODIAC 4-char slot fields (C$ order Sun,Mer,Ven,Mar,Jup,Sat,Ura,Nep,
  Plu,Moo,Rah,Ket + Asc slot 13), ASCEND 15-char field, center label row, and
  the canon NVM$ slot 7-9 blanking (NAVAMSAM omits Ura/Nep/Plu — QUAKE.pdf p2
  confirms: Vir would hold Ura+Nep and is empty). ASCII borders for CP437.
- --rasi writes rasi_navamsam.txt: one block per period row + per refined
  aspect event. Tests: unit boxes pinned to both QUAKE.pdf pages from the PDF's
  own longitudes; end-to-end at the Nepal moment from live engine positions
  (--tropical --koch) pinning Sun/Mer/Mar Tau slots, Asc in Leo (RASI) and Gem
  (NAVAMSAM), no outers on page 2. 139 tests passing.
- Finding en route: the canon's equal/Koch flag changes the ASCENDANT itself
  (equal path Asc 121.45 vs Koch 129.0 on the QUAKE chart) and ASTGRAF.BAS
  hardcodes EQL$="KOCH" (line 45) while the CLI defaults to equal houses —
  handed to the BAS-divergence sweep for NU's ruling on the default.

## 2026-08-02 — Koch is the CLI default (NU ruling); EQL$ evidence corrected
- NU: "CLI default should flip to Koch." Implemented: astgraf CLI now defaults to
  the real-obliquity (Koch) Ascendant path; --equal opts into the equal path
  (mutually exclusive with the retained --koch); positions.json "houses" derives
  from the same switch. Horary CLI tests pin the PRATEEK equal-path oracle via
  explicit --equal; the rasi end-to-end test pins the no-flag default = koch.
- CORRECTION to the previous entry's evidence line: the BAS-divergence sweep
  proved EQL$="KOCH" (ASTGRAF.BAS:45) is DEAD CODE — assigned once, never read.
  The real switch is EE$ from the runtime "House system E or W" prompt (:643,
  :665, consumed at :100), and a BLANK answer falls through to the Koch path —
  which is the true canon basis for the Koch default. README corrected likewise.
- Scope note: bands_cli.py:16 still hardcodes equal_houses=True — the Ascendant
  doctrine retrodictions (Hyderabad, Ulsoor) were validated on the equal path.
  Flipping the rules path is a separate decision for NU (would re-derive those
  ground truths).
- Sweep documented as AUDIT.md Part III: 40 divergences (headliners: no house
  cusps/CO960, no MC, no sidereal-time output; HH.MM packed hour steps; .GRF
  one-decimal resolution; GRAPHDO tick-pitch mismatch; Z1=Z1 typo making the
  BAS's own ecliptic latitude unusable) + the checked-identical list.

## 2026-08-02 — Rules CLI to Koch (NU ruling) + full report page (--report)
- NU: "flip the rules CLI to Koch too." Done: bands_cli SITE_FREE and the site
  sweep/chart paths now equal_houses=False. Discovery en route: the Ascendant
  ground-truth unit tests (Hyderabad dawn/evening, Ulsoor) were ALREADY
  validated at tropical/Koch (compute_raw ..., False, False) — the sweep path
  was the odd one out; the flip aligns them. Ulsoor site CLI test still fires.
- NU: "port CO960 cusps + MC + sidereal time — completes the QUAKE.pdf report
  page." Done: ephemeris gains _midheaven (:106-111), _house_cusps (CO960
  verbatim incl. ANX), and the ST$ block (:134-144) on ChartResult (mc, cusps,
  sidereal_time_deg); report.py ports CO920 (incl. the load-bearing ANW
  round-to-2dp), OWH/LUCK ruler column, DASA/BUKTI (5840-6030), and the
  PRINT USING page masks; --report --name --place writes horoscope.txt ending
  in both boxes. Oracle: all 12 QUAKE.pdf cusps reproduce value-for-value
  (Tenth 3 Tau 41 33.7 ... Ninth 5 Ari 21 5.4); First cusp == AZ55 Asc to
  1e-6 deg (independent path cross-check); sidereal "2 H 6 M 47 S" reproduces
  via the canon USING quirk (SMZ float minutes rounded for display, seconds
  from the unrounded value — true time 2h 5m 47.2s). Dasa/Bukti lords/years/
  months match the PDF (Mer 4 7 / Jup 1 0); day fields are Moon-sub-arcminute
  sensitive (engine 19/11 vs PDF 14/5) — documented in tests.
- 146 tests passing.

## 2026-08-02 — Audit step 1: high-severity fidelity fixes (NU: "go")
- Neptune restored to band-trigger escalation via new near_any primitive with
  the validated scanner's exact semantics (either giant within one 28-band span
  of any trio member) — fixes audit F1 (Neptune silently dropped) AND the
  escalation-geometry mismatch in one move.
- Atlas deep-panel stripe walk corrected to retrograde (sector_for_interval_end
  counts sectors BACK from the 1996 anchor, consistent with precession.py);
  shipped out/atlas.svg regenerated — fixes audit F2 (high).
- FRAMEWORK evidence line corrected: grid 0/31 vs 1.12; proximity 1/31 (March
  2015 North India rain) vs 3.45 — fixes audit F3 (high).
- 167.6 y retired everywhere: Ura-Nep conjunction recurrence = ~171 y synodic
  (engine 171.0; next cluster ~2165, DE440 2165-01). NU's question "is 167.6
  the 168-year Neptune cycle" resolved: 167.7 = engine 2x Uranus (the
  doubled-Uranus/168 convention); Neptune sidereal = 164.5; Neptune TROPICAL
  return = 163.5 = NU's "~163 years" almost exactly. Three candidate clocks
  documented in FRAMEWORK/WATCHLIST; the 1000-year records list discriminates.
- README 60-period drill example updated to the shipped locator v2 output
  (75.46E, 170.4 light-min) replacing the stale v1 spot (80.55E).
- mined-triggers.toml header corrected: corpus 1857-2020 (not 1900-2020) +
  audit caveat that lifts are upper bounds pending batch-3 re-mining.
- 149 tests passing.

## 2026-08-02 — Audit batch 1: aspect/horary crossing engine rebuilt
- find_events: intervals sub-sampled so relative motion stays <60 deg/sub-step,
  separation series UNWRAPPED (continuous), every target crossing isolated in
  its own sub-bracket; bisection refuses +-180 jump brackets (min |g| > 90).
  Fixes audit findings 1/2/10: no more opposite-kind events at the antipode; the
  2005-2015 Jup-Sat yearly grid now finds 3 oppositions (2010-11 triple) / 8
  trines / 3 squares where it found 1/1/1; every emitted event asserts exact
  (|sep-target| < 0.01 deg at its refined instant) in tests.
- find_sub_crossings: same machinery on unwrapped body longitudes — no more
  180-deg-off boundary rows or fabricated retrograde walks (audit finding 4);
  Mars's direct year yields its ~173 true boundary crossings, each verified ON
  its boundary to <0.01 deg.
- Lens contract enforced (README's own rule, now code): pairs/bodies whose
  relative motion exceeds ~one cycle per division (8 sub-steps) are SKIPPED
  WITH A PRINTED NOTE ("descend the lens") instead of producing garbage —
  Ascendant pairs at yearly steps skip, at daily steps resolve correctly
  (audit finding 3). Synthetic/unknown bodies get a generous cost cap (400).
- Refiners break at 1e-9 day convergence. Suite runtime 4.5s. 154 tests passing.

## 2026-08-02 — Audit batch 2: sweep integrity + WATCHLIST re-derivation
- Root fix: compute_raw derives the AYANAMSA YEAR from the actual instant
  (jd_to_calendar of the jd) instead of the start-year field — hour-overflow
  sweeps no longer freeze the ayanamsa (audit HIGH data-pipeline 1); the
  signatures control charts are cured by the same path (finding 20). All
  oracles still bit-exact (dated charts unaffected).
- Tightest-instant refinement for ALL rule types: _metric_for gives every rule
  an exactness scalar (aspect gap / cluster spread / axis gap / node-holding
  gap); refine_episode_instant clamps to the window (finding 49). Acting body
  chosen AT the refined instant, ORB-GATED (a distant giant cannot publish a
  spot for a window it did not join — first run exposed exactly this: Neptune
  44 deg from a node shadowing Jupiter 0.04 deg ON Ketu; fixed + tested).
- Per-rule fine sweep steps: Ascendant rules 0.25h, Moon rules 1h, others at
  the base step — Hyderabad ground truth now resolves at the DEFAULT step
  (audit HIGH design-gaps 1); band-scan episodes.csv gains tight_instant and
  locates giants at it — 12h vs 3h step now agree within ~3 deg on the 2017-01
  Neptune episode (audit HIGH locator 1/design-gaps 2). Episodes keep band
  history across merges (finding 28).
- WATCHLIST v3 amendment: regenerated both forward sweeps with recorded
  commands (--start 2026-08-02 --days 850). MINED: byte-identical to v2 — all
  9 windows stand (aspect predicates ayanamsa-invariant). BAND-TRIGGER: edges
  sharpened up to ~9h by the 1h sweep; regenerable tightest instants; NO giant
  within a span at any instant, so the v2 "giant spots (secondary)" figures
  are retired as first-sample artifacts. NODES: four windows now carry
  regenerable instants + Jupiter (on-Ketu holder) spots — S China Sea,
  mid-Atlantic W of Cape Verde, W Atlantic E of the Antilles, Philippine Sea;
  supersede the six console-derived per-holder instants (non-regenerable).
  Primary mined tables trued to CSV-exact values. 161 tests passing.

## 2026-08-02 — Audit batch 3: honest re-mining — all three mined rules RETIRED
- signatures.py rebuilt: (1) spot/loc_km features now forward-model-consistent
  — the catalog instant is the ARRIVAL, the spot comes from the trigger chart
  light-time earlier (finding 11; ~60 deg Neptune correction, tested); (2)
  decluster() drops aftershock-like repeats (7d/500km; finding 33); (3)
  controls are a TIME-UNIFORM grid over the corpus span (finding 16); (4)
  add-one smoothed lifts, no infinite ranks (finding 53); (5)
  permutation_max_lift bitmask null, deterministic seed (finding 15).
- Methodological discovery en route: a circular-shift pilot promoted
  sep:Uranus-Neptune@opp to lift 55 (p~0) purely via the pre-1900 catalog
  completeness gradient meeting an era-locked predicate — era-locked slow
  predicates cannot be assessed against event-shifted controls at all. Final
  design adds the standard completeness cut (min_year=1900).
- VERDICT (scripts/mine_usgs.py v2 -> out/signatures-m7-v2): 1436 declustered
  post-1900 events vs 4308 uniform controls; 2-year-block split; every top
  screening lift collapses on the held-out half; family-wise max lift 1.79 vs
  permutation null median 1.73 / 95th pct 2.12, p = 0.35; locator spatial
  skill nil (4896 vs 5007 km shuffled). All three mined rules marked RETIRED
  in mined-triggers.toml (kept loadable: their 9 windows were pre-registered
  and the outcome protocol still grades them). WATCHLIST v4 amendment records
  the retirement; doctrine channel untouched.
- astgraf-outcomes writes a spatial_chance column (historical fraction of M7+
  within the grading radius of each spot) — hits read against base rate
  (findings 22/31). 165 tests passing.

## 2026-08-02 — Batch 5 ruling: real: rules locate from the OBSERVED meridian
- NU: "keep observed and go." Ratified in FRAMEWORK (two-channel scheme: real
  positions time the crossing — substratum, instant; the observed image places
  the marker — light channel, rotation west by light-time). Closes audit
  findings 40/41. The discriminable alternative (real meridian with ZERO
  rotation) is on record; the first confirmed forward hit votes.

## 2026-08-02 — Audit batch 6: hardening (all remaining silent traps closed)
- TOML schema guard (12/48): Condition/TriggerRule extra="forbid", structural
  validators per condition type, load_rules errors on empty rulesets, unknown
  body names, and real: prefixes without doctrinal offsets (23/30).
- Gregorian reform (34): julian_day_number threshold > -> >= — 1582-10-15 now
  maps to 2299161 (was 10 too big with backward JD). Deliberate one-comparison
  divergence from the BAS/JS canon, tested. Residual (35, documented): calendar
  FIELD stepping across Oct 1582 still double-covers via the phantom dates
  Oct 5-14; JD-driven paths (sweeps, make_chart_at_jd) are immune.
- Date parser (18/36/37/39): standalone month tokens (Marmara/Junction fixed),
  no year/magnitude digit tearing ("2015 October 26", "M7.8 May 12"), range
  tails kept ("July 8 and 9"), cross-year ranges upright ("Dec 28 - Jan 3"),
  month-cell fallback when the free-text cell has no month. All audit repros
  pinned as tests.
- ChartMoment rejects impossible dates (50); signatures accepts USGS
  timestamps without milliseconds (52); --utc-offset now shifts band-scan and
  vyuha sweeps (51); episode giant spots print unsigned E/W-N/S (47);
  horary_position indexes hierarchically so boundary longitudes nest across
  division/sub/sub-sub (42); scope labels stagger across the 0-Aries seam
  (43); astgraf-outcomes keeps no-spot windows as "unassessed (no spot)" (24).
- 176 tests passing. Audit batches 1-6 COMPLETE; every confirmed finding is
  fixed, ruled on, or documented as a residual with its reason.

## 2026-08-02 — README: canon-divergence section (NU: "document the two")
- New README section "Deliberate divergences from the BASIC canon": exactly two
  engine divergences (Gregorian reform-day >= fix; ayanamsa year from the
  instant), each with reason, test name, and residuals; the Magha ruled
  exception; pointer to AUDIT.md Part III SG for the pre-existing port-level
  inventory. Also trued two stale honesty bullets: series drift is
  degrees-level by the 1600s (not "tens of millennia"), and fast pairs are now
  skipped with a note under the lens contract (not emitted as aliased noise).

## 2026-08-02 — Check-again pass on the fidelity report: 8 residuals closed
- NU asked to re-verify the original fidelity-audit report item by item. All 3
  HIGHs and most mediums were already fixed in the audit batches; EIGHT
  residuals remained and are now closed: (1) locator anchor comment states
  honestly that Jup 40/Sat 80 match MEAN distance (nearest 32.9/67.0), only
  Ura/Nep are nearest-position anchors; (2) ephemeris docstring 25,720 ->
  25,748; (3) FRAMEWORK register line updated to the real 19-window census;
  (4) FRAMEWORK Moon-square hour corrected to the engine's 15:30-19:30 IST;
  (5) atlas caveat now notes the linear clock is a doctrine choice (real rate
  varies); (6) axis_cross evaluates the MIDLINE of both declared endpoints —
  order-independent (findings 19/29), tested; (7) --ayanamsa-rate without an
  explicit zero now anchors at the ruled 1996 Aswini zero (was 294), tested;
  (8) doctrine TOML: chatur-vyuham-uranus partner variant added (node-lock
  narrowing documented, --vyuha remains the validated full detector),
  jupiter-saturn restricted to the Aswini-Kritika Java-family sector via
  in_band lists (fires 2000-05 Kritika, not 2020-12 Uthrashada — tested), and
  all five previously-bare orbs carry their calibration rationale.
- The one surviving '167.6' mention is WATCHLIST's intentional historical note.
- 181 tests passing.

## 2026-08-02/03 — Full AUDIT cross-check (item-level): 3 more opens found, closed
- NU: "cross check again the AUDIT." Item-level walk of all 127 entries (Part I
  1-53, Part II F1-F34, Part III 1-40) found THREE code findings my batches had
  listed but never implemented:
  (13) refine_episode_instant now prefers the EARLIEST exact crossing within a
  1e-6 tolerance — deterministic under ephemeris noise; re-derivation moved ONE
  registered instant (2027-03-03 nodes window 01:01 -> 00:58 UT, Jupiter spot
  42.70W -> 41.95W, 0.75 deg); every other registered row byte-identical;
  WATCHLIST amended.
  (21) score_events reports catalog events outside the sweep as out_of_range
  instead of chance-weighted misses.
  (38) the chance baseline is step-honest: episode length = true extent + one
  sweep step (never a phantom full day), per-episode overlap-probability model.
  The 2013-2015 census re-scores: grid 0/31 vs 0.63 expected (was 1.12 under
  the inflated formula), proximity 1/31 vs 1.79 (was 3.45) — below-chance
  reading stands, more modestly; FRAMEWORK/WATCHLIST renumbered with the
  formula note.
- Doc residuals closed: README pre-existing-divergence list gains the grid
  start-row/count semantics and the 2000-row ceiling (Part III #13/#16); atlas
  constants carry the finding-46 span-edge caveat. Statuses everywhere else
  re-verified per item (greps/tests), incl. regenerating out/atlas.svg which
  had missed the caveat text.
- 183 tests passing.

## 2026-08-03 — Docs reconciliation sweep (NU: "check which changes need doc updates")
- Walked every session change against README/FRAMEWORK/WATCHLIST. Six gaps
  found and closed: (1) README trigger-rules section rewritten — ten
  primitives (near_any, band lists, midline axis_cross), the load guards, the
  per-rule fine steps, tightest-instant + orb-gated spots, step-honest
  scoring; (2) README outcomes bullet — spatial_chance, --corpus, unassessed
  rows, quake-channel-only scope; (3) FRAMEWORK map — nakshatra-layer row
  reflects the classical-27 default with the parked ladder, NEW report-layer
  row (rasi/report, cusps/MC/ST), aspects row notes the wrap-safe engine;
  (4) FRAMEWORK map inverse-learning row corrected — the old "real-position
  predicates replicate" claim was FALSE post-retirement; now states the v2
  no-survivor verdict; (5) FRAMEWORK section 1 records the follow-ASTGRAF.BAS
  ruling (27 default, ladder parked, bands/precession untouched); (6)
  WATCHLIST Jup-Sat line — 2040 is outside the family sector; the ~119-y
  family period puts the next Java return ~2119.

## 2026-08-03 — Migration: the engine has its own repo
- NU: separate the system/engine from the iOS app. New home:
  /Users/macbookpro/Sankhya-Prediction (tools/astgraf shape kept), fresh git
  history, import commit 439de21 (from Astro working tree @ 3db9366).
- Carried: the full engine + tests + docs + doctrine sources + AUDIT.md +
  registered out/ artifacts (on disk; out/ stays git-ignored as before), this
  ledger, and the BASIC canon into canon/ (closes audit F20 — the verbatim
  port is now verifiable in-tree). de440.bsp kept on disk, git-ignored.
  Session memory copied to the new project store and repointed.
- Verified in the new location: uv sync clean, 183/183 tests, QUAKE.pdf
  report reproduces (sidereal 2 H 6 M 47 S exact).
- The Astro repo keeps the iOS app and its history; branches
  feature/astgraf-tool and fix/engine-ss2-shim remain there unmerged.

## 2026-08-04 — NU observation: the 9/7 ladder-ratio identity
- NU: 28x9x9 = 2268 and 2268/1764 = 1.28571428... Verified: the ratio is
  exactly 9/7 (the ladders share 28x9, differing only 9-vs-7), and its cyclic
  digits are the 28-band span's own: 360/28 = 90/7 = 12.857142... deg —
  the correction factor between the superseded and ruled ladders IS one
  band-span, decimally shifted. The system's constants all sit on the 1/7
  cycle: 25/7 (PHO count), 90/7 (span), 9/7 (ladder ratio), 10/49 (instant
  cell 0.204081...). Consistency point in favor of the ruled /9/7 ladder
  (closes onto the band-span; /9/9 has no such closure); does NOT by itself
  decide the parked Abhijit-28 question.

## 2026-08-04 — Magnitude-stratified pattern search (NU) + two data fixes it caught
- NU asked whether patterns exist in M7/M8/M9 strata. Running it exposed two
  real corpus flaws, both fixed test-first:
  (1) decluster kept the FIRST event of a cluster — foreshocks silently
  displaced the 1960 Valdivia M9.5 and 2011 Tohoku M9.1 mainshocks. Now
  keep-largest greedy (time-ordered output); both restored.
  (2) The time-uniform control grid stride (span/4305 ~ 10.238 d) sat at a
  near 3:8 commensurability with the lunar cycle — control Moon phases formed
  a drifting comb whose holes landed on aspect zones after the real-offset
  fold, faking rsep:Neptune-Moon@sq at lift 165, p=0.000. Controls now use a
  golden-ratio low-discrepancy sequence (deterministic, non-resonant with any
  period); coverage test added.
- Verdicts on the corrected corpus (1435 events, mainshocks in, clean
  climatology): FULL M7+: max lift 1.71, null median 1.73, p = 0.595 — the
  no-survivors retirement stands, stronger. M>=7.5 (454): max 2.15 vs null
  median 2.31, p = 0.74. M>=8 (94): max 4.08 vs null median 4.64, p = 0.74
  (top cells rsep:Neptune-node@conj/opp — doctrine-adjacent theme, below its
  own chance bar). M>=9 (n=5): no shared doctrine signature (mkm spreads
  40-210 deg, no simultaneous vyuha components; single cells near aspects are
  chance at 6x5 looks). 184 tests passing.

## 2026-08-04 — NU standing rule: canon code is FROZEN
- NU: "never change any code that is based on the BAS files." Confirmed
  signatures.py contains no BAS-derived code (modern statistics layer; it only
  CALLS compute_raw) — the recent decluster/control-grid fixes touched no
  canon. Canon-bearing map recorded (frozen): ephemeris.py entire; horary.py
  star_position/NAKSHATRAS_27/SIGNS_12; rasi.py entire; report.py entire;
  grid.py jd_to_calendar + overflow stepping; svgplot.py GRAPHDO constants.
  Modern (changeable): aspects, bands, bands_cli, triggers, locator,
  signatures, matrix, atlas, outcomes, precession, scope, models, cli. The two
  documented divergences (Gregorian >=, instant ayanamsa year) pre-date this
  rule and stand as ruled exceptions; any future canon change requires an
  explicit NU ruling first.

## 2026-08-04 — NU ruling: the recurrence principle is the method's core
- NU: "prediction of the future events should be based on the analysis of the
  past major events, because the same positions, conjunctions and other
  patterns repeat and cause similar events." Recorded in FRAMEWORK section 2/3
  boundary as doctrine. Gap analysis against the built system delivered (see
  conversation 2026-08-04): the system has rule-sweeps and generic predicate
  mining but LACKS the event-anchored recurrence machinery — configuration-
  similarity search, anchor-event dossiers, recurrence calendars (when does an
  anchor chart's slow-layer configuration re-form), category-tagged pattern
  library per Predict.pdf's per-cell spec, and composite (multi-condition)
  pattern matching. Awaiting NU's build order.

## 2026-08-04 — Angle-localization hypothesis: tested, DOES NOT SURVIVE
- Origin: the "why spots are from Gorkha" reading found the Sun (carrying
  real-Uranus at 0.69 deg) standing 1.06 deg from the site MC in the QUAKE
  chart — suggesting the site's own angles (MC/Asc), not rotated spots, mark
  the place, matching the Hyderabad/Ulsoor Ascendant instances. NU ruled: run
  the test across the corpus; rebuild the location layer on the angle channel
  ONLY if it survives.
- Pre-registered design (scratchpad/angle_localization_test.py): declustered
  post-1900 M7+ mainshocks; per event a chart AT the epicenter at the event
  minute; 26 primary predicates = {11 band bodies + real-Ura + real-Nep} x
  {site MC, site Asc}, point conjunction, 3.0-deg orb; 5 golden-ratio control
  instants per event AT THE SAME site (matches the Asc's latitude-dependent
  sweep exactly); verdict = family max smoothed lift vs 500-run label-
  permutation null. Oracle gates passed before unblinding: QUAKE printout
  (MC 33.68 / Asc 128.97) and the in-corpus Nepal row.
- VERDICT: 1,434 events / 7,170 controls — observed max lift 1.62
  (Neptune-MC), null median 1.52, p = 0.25. Sensitivity incl. 53-predicate
  axis family: p = 0.25. Combined any-doctrine-body-on-any-angle: lift 1.13.
  Sun-MC (the Nepal cell) tops the doctrine cells at lift 1.60 (33 events
  near local culmination-noon vs 21 expected) but is exactly what a
  26-predicate family yields by chance. The location layer is NOT rebuilt;
  the observed-meridian ruling stands; honest negative on record.
- Design findings under the oracle gates (both recorded, no canon touched):
  (1) At the TRUE epicenter (84.73E) the Nepal Sun-MC separation is 2.00 deg
  — the 1.06 figure was an artifact of the canon chart's rounded 86:00E site.
  (2) The canon's sidereal mode shifts the ANGLES by ayanamsa in RA space,
  not ecliptic — body-angle separations are frame-DEPENDENT (Nepal Sun-MC:
  2.00 tropical vs 3.63 sidereal); the test ran tropical = the physical
  culmination/rising frame, matching the QUAKE oracle. (3) The equal-house
  path is Asc-90 by construction, unusable for culmination tests; the Koch
  path is domain-limited to |lat| < ~66.6 — one event excluded (Baffin Bay,
  73.15N), the canon itself cannot cast that chart.

## 2026-08-04 — Anchor library built (recurrence gap 3) + minute-refined trigger instants
- NU: build the anchor library; the rules need the trigger instant defined to
  minutes. Built test-first in the modern layer (no canon touched):
  anchors.toml (data: the 6 taught anchors incl. the vyuham configuration and
  Krakatoa, + the 5 corpus M9 events with exact catalog instants; approximate
  times flagged with time_quality) + anchors.py + astgraf-anchors CLI
  (--list / --anchor ID / --out dir, .json + .txt dossiers).
- A dossier = the anchor's configuration readout with every fired rule's
  TRIGGER INSTANT refined below one minute: contacts (55 pairs + real-Ura/Nep
  x 10, listed at 5 deg, doctrine-fired at 3 deg; degenerate Rahu-Ketu pair
  excluded) each with exact UTC minute + offset + residual; the site
  Ascendant timetable (13 positions, tropical/physical-rising frame, Koch
  path, +-12 h); band state (mkm spread, stack); vyuha state.
- ORACLES REPRODUCED (tests pin them at +-5 min): Hyderabad Asc-Rahu 04:50
  IST (taught ~04:49) and Asc-Ketu 17:06 (taught ~17:04) on 2016-09-23;
  Ulsoor Asc-Neptune 06:12 (taught 06:12) and Asc-Uranus 08:21 (taught
  08:20) with the sweep order Neptune->Sun->Ketu->Uranus; Nepal double
  signature 0.69/0.34 deg with real-Ura->Sun exactness +18.1 h after the
  quake; vyuham-2016 dossier fires the full array with each arm's exactness
  minute. 193 tests passing.
- Observation for NU (not doctrine): Nepal's own site timetable shows the
  pre-dawn Asc sweeping Neptune -> rNeptune/Ketu -> Uranus -> Sun/rUranus in
  the hours before the quake — an Ulsoor-like chain, on record as an
  observation only.

## 2026-08-04 — Location-layer variants (a) and (b): tested, BOTH AT CHANCE
- NU ran the two recorded alternatives (scratchpad/spot_variant_test.py;
  1,435 declustered mainshocks; best-of-4-bodies longitude gap; null = 20
  epicenter permutations, seed 42):
    M1 current rule (trigger-chart locate)      median 28.9 vs null 28.6, hits<=15deg 419 vs 421
    M2 variant b (locate at the event minute)   median 29.2 vs null 29.3, hits 419 vs 415
    M3 variant a (ZERO-rotation REAL-meridian)  median 29.9 vs null 28.8, hits 412 vs 417
    M4 sanity (zero-rotation observed meridian) median 28.9 — confirms M1~=M4
  Per-body medians all ~88-90 deg = the uniform-chance value. No formulation
  of the world-spot channel has corpus-level skill; the discriminating
  forward-hit question between the two ruled schemes is now moot for M7+
  quakes — both measure at chance retrospectively.
- Structural insight ON RECORD: the current forward model (locate from the
  light-time-earlier trigger chart, then rotate west) is arithmetically
  near-identical to the zero-rotation OBSERVED meridian at the arrival
  minute — the westward rotation cancels against the earlier chart's
  eastward meridian offset (Nepal: M1 Uranus 70.8E vs M4 70.6E). The
  "rotation" as implemented is self-canceling with respect to arrival.
- Nepal case study stays the tension: variant (a) real-Uranus meridian lands
  87.5E — 2.8 deg from Gorkha's longitude (1,746 km with the declination
  cage) — the formal version of the Sun-on-MC reading; but the corpus shows
  it does not generalize (M3 at/below its own null). Combined with the
  angle-channel p=0.25 verdict (same day), every location formulation tested
  for M7+ earthquakes sits at chance; the timing layers remain the doctrine's
  proven core. Location doctrine awaits NU's NR/Rs/Ro table or a new ruling.

## 2026-08-04 — NU RULING: location layer demoted to experimental (proposal ratified)
- NU: "proceed with your proposals." The four-point re-scoping is now in
  force: (1) implementation kept in full (doctrine, faithfully ported);
  (2) earthquake windows are TIME-ONLY claims — registered spots remain
  graded as a pre-registered experiment marked "experimental:
  retrospectively at chance" (WATCHLIST amendment v5); (3) the site channel
  (Asc/MC over held axes) is scoped to the taught local categories and
  interrogates named candidate sites, not the world; (4) reinstatement
  criteria: a graded forward spot hit above spatial base rate, a
  flood-category corpus win, or a new NU ruling on the spot channel's role.
  Recorded in FRAMEWORK (location-layer status), WATCHLIST v5, both READMEs.
  On record: the NR/Rs/Ro table cannot rescue quake spots (constant offsets
  leave a uniform gap distribution uniform); it bears on timing.

## 2026-08-04 — Similarity engine + recurrence calendar built (recurrence gaps 1+2)
- NU: "go-ahead with configuration-similarity engine + recurrence calendar,
  build on the anchor library." Built test-first in the modern layer:
  recurrence.py + astgraf-recur (--anchor/--all, --start/--end/--years,
  --min-match, --out -> recurrence.csv/.txt/.json, one chronological
  calendar across anchors).
- Design per the two-layer doctrine: an anchor's PATTERN = its slow layer
  (doctrine-orb contacts at the anchor instant, Moon pairs excluded);
  EPISODES = spans where >= min-match (default all) contacts stand within
  orb simultaneously (adaptive scan: 1 d when the pattern touches
  Sun/Mercury/Venus, else 5 d), each with its tightest instant refined
  below one minute; the anchor's own Moon contacts are then completed
  INSIDE each episode to the minute (the fast hand dating the window).
  Timing only — no spots (location layer experimental per the v5 ruling).
- Validation: Nepal self-recovery — scanning Mar-Jul 2015 yields exactly
  ONE episode, 2015-04-23..25 (quake Apr 25), tightest 04-22 22:51Z;
  vyuham-2016 does not re-form in 2017 (Jupiter left the Neptune
  opposition); 199 tests passing.
- FORWARD RESULT (2026-08-04 + 2 years, all 10 anchors): NO full
  re-formations; at all-but-one, a single near-episode — ALASKA-1964
  re-forms 3/4 on 2026-11-15..20, tightest 2026-11-17 13:02Z, missing only
  sep:Ketu-Uranus@tri. Selectivity is the point. NOT registered on the
  WATCHLIST — whether anchor-recurrence windows join the forecast register
  is NU's call, pending.

## 2026-08-04 — NU RULINGS: observed-rule channel (TESTING) + recurrence windows registered
- NU: "Asc-trine-real-Neptune observation deserves rule status marked as in
  Testing, also anchor-recurrence episodes join the WATCHLIST as registered
  windows."
- (1) New rules file observed-triggers.toml — the third provenance channel
  (taught / mined / observed-TESTING). First rule asc-trine-real-neptune:
  trine Ascendant x real:Neptune, orb 1.0, TROPICAL site charts only.
  Ground truth measured: 0.264 deg at the Nepal catalog minute + true
  epicenter (0.428 on the QUAKE chart's rounded 86E site); sidereal frame
  shows 3.2 deg (RA-space ayanamsa shift on angles) — frame-guard test pins
  fires-tropical/not-sidereal. Site-conditional fast hand (sweeps any site
  twice daily): no standalone forward windows; graded inside loaded windows
  at candidate sites. Exit from TESTING: NU doctrine ruling or refutation.
- (2) WATCHLIST anchor-recurrence section added: channel pre-registration
  (10 anchors, 2026-08-04 + 2 y, full and n-1 levels, time-only claims,
  regeneration command); honest empty registration of zero full
  re-formations through 2028-08; first registered window ALASKA-1964 near
  3/4, 2026-11-15..20, tightest 2026-11-17 13:02 UT, missing
  sep:Ketu-Uranus@tri, claim = M7+ worldwide in-window, base rate ~0.2
  stated (corpus 11.9 M7+/yr). Amendment v6 records the observed-rule
  channel. 200 tests passing.

## 2026-08-04 — NU input: (Rs/Ro) = 213.3266821 — Mathcad offset formula DECODED
- NU supplied Rs/Ro = 213.3266821 (Earth's orbital radius in solar radii,
  Sankhya value; astronomical ~215.03) with the doctrine context: in the
  Sankhya derivation of C and c, EMW frequency varies as Rs/Ro; the
  eccentricity caused by the solar/galactic velocity 250,000 m/s is misread
  as the Earth's "wobble" — the Earth rolls smoothly, axial tilt balancing
  spin. Recorded in FRAMEWORK (clock paragraph); the precession clock's
  measured rate is unchanged (cause reinterpreted, not arithmetic).
- DECODE (verified, round-trips both given offsets to all 10 digits):
  offset = (a/2 - 1) * 500/240, a = NR_n / 213.3266821 = orbital radius in
  Earth-orbit units. NR_19 = 6384.463 -> Neptune a 29.9281 -> 29.0917753653;
  NR_15 = 4083.496 -> Uranus a 19.1420 -> 17.8562342478.
- Jupiter/Saturn offsets are now one constant away each: the Sankhya NR
  values are NOT the canon's elements (canon Uranus 19.2215 vs Sankhya
  19.1420 — would shift the offset 0.08 deg, material at 0.34/0.69 orbs)
  and NOT astronomical axes. Candidates at standard axes: Jup ~3.34 deg,
  Sat ~7.87 deg — NOT adopted; awaiting NU's NR values for Jupiter and
  Saturn before real: offsets extend beyond Ura/Nep. No code changed.
- Same day, the repeated "why did location fail" question was answered from
  the SOURCES: Mathcad-QUAKE.pdf re-read — it is purely a timing/
  configuration proof (real-position ecliptic crossings at the node and at
  the Sun; "two simultaneous events"); it contains NO location
  construction. Predict.pdf likewise (band table + validation doctrine).
  The meridian/declination location rule exists only in the conversational
  teaching — consistent with flaw 4 (zero worked instances) and the corpus
  verdicts.

## 2026-08-04 — Real-position layer extended to all four giants (PROVISIONAL Jup/Sat)
- NU: "think and decide between [standard axes] and [canon elements], or
  test both." Decision: CANON elements — the two differ by <= 0.0025 deg
  (immaterial; testing both uninformative), and canon-derived keeps the
  single-source-of-truth principle. Adopted as PROVISIONAL data in
  bands.REAL_POSITION_OFFSETS: Jupiter 3.3363593021 (a 5.20290493),
  Saturn 7.8672056771 (a 9.55251745), via offset = (a/2 - 1)*500/240;
  Ura/Nep keep the Mathcad digits untouched. Expected Sankhya correction
  ~0.02 deg (Ura/Nep deviation trend: -0.26%/-0.47% shrinking inward).
  real:Jupiter/real:Saturn now legal in rules (guard test moved its
  offset-less example to real:Mars); anchors REAL_BODIES + site timetable
  extended (rJupiter/rSaturn). signatures.py mining space intentionally
  UNCHANGED. 202 tests passing.
- First four-giant re-reads (provisional, labeled): NEPAL gains five fired
  contacts - rsep:Jupiter-Uranus@tri 1.24, rsep:Saturn-Jupiter@tri 1.58,
  rsep:Jupiter-Mars@sq 1.63 (exact 58 h BEFORE the quake),
  rsep:Saturn-Neptune@sq 1.98, rsep:Saturn-Ketu@tri 2.54. SUMATRA gains
  rsep:Saturn-Mars@tri 2.89 (exact +91 h). HYDERABAD and KRAKATOA gain
  nothing within doctrine orb (Hyderabad's Jupiter story stays the observed
  Sun-Jup conj).
- Regeneration (completion-claims rule): Nepal self-recovery STRENGTHENS —
  still exactly one episode 2015-04-23..25, now 9/9 full match (real-Jup
  sq Mars 0.07 at the tightest instant). Forward 2026-28 under extended
  patterns: NO full and NO n-1 episodes anywhere — the registered
  alaska-1964 3/4 row does NOT reproduce under the extended engine
  (pattern 4 -> 6); row STAYS registered with a WATCHLIST annotation
  (mined-windows precedent); future rows use extended patterns. README/
  FRAMEWORK claims regenerated.

## 2026-08-04 — Candidate Jupiter/Saturn offsets: all sources on record
- Per NU ("did you document the other potential values"): the full candidate
  table is now in FRAMEWORK open question 1 — canon elements (ADOPTED
  provisional) Jup 5.20290493 -> 3.3363593 / Sat 9.55251745 -> 7.8672057;
  JPL approximate J2000 Jup 5.20288700 -> 3.3363406 / Sat 9.53667594 ->
  7.8507041; textbook mean Jup 5.2026 -> 3.3360417 / Sat 9.5549 ->
  7.8696875. Spread: Jupiter <= 0.0003 deg; Saturn <= 0.019 deg (JPL Saturn
  axis is the outlier). Purpose: when NU's exact NR values arrive, matching
  them to the nearest source diagnoses what NR physically is.

## 2026-08-04 — Do the new NR values help the location layer? Tested: NO
- NU asked; prediction registered BEFORE unblinding (a constant offset
  rotates a uniform gap distribution into a uniform one): chance expected.
  Re-ran the zero-rotation REAL-meridian corpus variant with all FOUR
  giants' real offsets live (provisional Jup/Sat included): best-of-4
  median 28.9 vs null 28.8; hits<=15deg 416 vs 418; per-body medians
  88.0/92.3/89.0/90.7 = uniform. Confirmed: the Rs/Ro decode completes the
  TIMING layer (its role per the two-channel ruling); it does not and
  cannot rescue the spot channel. Location-layer status (experimental,
  v5) unchanged; reinstatement paths unchanged (forward spot hit /
  flood-category corpus / new NU ruling).
