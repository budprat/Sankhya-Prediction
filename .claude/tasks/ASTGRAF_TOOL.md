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

## 2026-08-04 — THE 130-YEAR RECURRENCE SWEEP: every pattern is a fingerprint
- Exploratory retrodiction (not pre-registered): all 10 anchors' four-giant
  patterns scanned 1900-2030 at 0.25 d step, FULL and n-1 levels, each
  non-self episode to be graded against the declustered corpus (11.9 M7+/yr).
- SELF-RECOVERY: 9/9 in-scan anchors recover their own event inside a FULL
  episode (by construction, since patterns are extracted at the event
  instant — the non-circular content is what follows). Windows: Nepal
  Apr 22-25 (quake 25th), Sumatra Dec 26 single-day (M9.1 + same-day M7.2
  Sabang in-window), Valdivia May 22 sub-day (the window that forced the
  engine fix), Kamchatka Nov 4-7, Alaska Mar 27-30, Tohoku Mar 8-11 (window
  opens 3 days before the quake). Krakatoa's 1883 instant pre-dates the
  scan; its pattern never forms 1900-2030 — and notably did NOT re-form at
  Sumatra 2004: the Java-family link is the Jup-Sat band sector, not the
  contact fingerprint.
- HEADLINE: ZERO non-self episodes. In 130 years x 10 patterns, at BOTH
  match levels, no configuration ever re-formed away from its own event.
  Assiduous-search totals: 0 episodes, 0 days, 0 expected — nothing to
  grade, no false alarms. The channel's retrospective false-positive rate
  is zero; its predictive skill is correspondingly UNDEMONSTRATED (no
  independent trials exist yet). Honest reading: anchor patterns at 3-deg
  orb individuate their own events; a future full re-formation on the
  forward calendar will be a genuinely singular alert, roughly
  once-per-century-plus rare per anchor.

## 2026-08-04 — P1 built: the family-grain recurrence channel (astgraf-families)
- Rationale from the sweep: contact fingerprints NEVER re-form; NU's taught
  recurrence (Java family) lives at nakshatra-sector grain. Built test-first:
  families.toml (java-jupiter-saturn with NU's two members; flood-uranus-
  neptune with the engine-derived 1993 Poorvashada triple) + families.py +
  astgraf-families CLI (--family/--start/--end/--out). Conjunction series:
  20 d scan, sign-change bisection to the minute, |sep|<90 guard (opposition
  wrap excluded), retrograde triples preserved (1940-41 and 1980-81 = three
  events each); conjunction degree -> canon star_position + 28-band;
  member-sector returns flagged with anchor links.
- ORACLES REPRODUCED (tests): 1881-04-16 conjunction in Aswini (-> Krakatoa),
  2000-05-27 in Kritika (-> Sumatra), 1980-82 triple = 3, Ura-Nep 1993 + a
  return in the 2158-2172 window. 211 tests passing.
- CALENDAR FINDINGS FOR NU (engine observations, labeled): (1) the "next
  ~2040" member: 2040-10-30 falls in CHITRA - not a member sector; the next
  MEMBER-SECTOR return is 2060-04-07 in Kritika. Both dates on record; which
  carries the family claim is NU's reading. (2) The 1941 triple (Bharani,
  between the taught members) is an unexamined candidate member - records
  search open (Java arc 1940-41?). (3) The 1993 flood conjunction was itself
  a TRIPLE, all passes Poorvashada pada 4.

## 2026-08-04 — Recurrence-engine fixes surfaced by the sweep (commit 02b509b)
- Two defects found by the Valdivia self-recovery failure, both fixed
  test-first: (1) JOINT windows can be sub-day (Valdivia's five contacts
  hold days each, ~10 h together) — find_episodes gains an explicit `step`
  parameter; exhaustive scans use 0.25 d (regression test pins Valdivia at
  that step). (2) The tightest-instant refiner minimized the raw
  separation sum UNCONSTRAINED and could drift outside the episode's own
  match level (Valdivia's 4/5 sum minimum beats every 5/5 instant) — now
  penalized to stay at the episode's level; Nepal's tightest moved one
  minute (22:51 -> 22:50). WATCHLIST carries the scan-step note.

## 2026-08-04 — Documentation reconciliation pass (NU request)
- Item-level audit of every doc surface against the day's changes. Gaps
  found and closed: repo README tree lacked observed-triggers.toml and
  families.toml; FRAMEWORK section-6 document map lacked families.toml;
  the 02b509b engine fixes had no dedicated ledger entry (above);
  WATCHLIST lacked the scan-step lesson. Verified already-current: tool
  README sections for all six CLIs, FRAMEWORK implementation map rows,
  test counts (211), WATCHLIST amendments v5/v6 + annotations, candidate
  offset table, all ledger entries for verdicts and rulings.

## 2026-08-04 — P2 done: outcome-grading dry run + season protocol
- Both channels ran end-to-end at the true date: mined 9/9 pending;
  doctrine-forward-v3 4 pending + 6 unassessed-no-spot (band windows, as
  registered). No network for future windows (verified behavior); the
  hit/clear fetch path is covered by test_outcomes (injected fetch) in the
  211-test suite. Deliberately NOT simulated with --today beyond the real
  date: grading an unpassed window against live USGS would log a false
  "clear".
- Season protocol table added to WATCHLIST (run dates Oct 7 / Oct 22 /
  Nov 6 / Nov 23 with verbatim commands). Observation on record: the first
  window's spot has spatial_chance 0.0000 (equatorial Pacific, no corpus
  M7+ within radius) — a hit would be extraordinary, a clear is
  near-certain and carries almost no evidence either way.

## 2026-08-04 — P3 done: Hyderabad interpretation cross-check PASSED
- NU's own cast read from Hyderaba-floods.docx: 24-09-2016 10:00 IST,
  78:00E/16:00N, AYANAMSA 0.000 (a TROPICAL cast — the doctrine chart for
  Hyderabad is tropical, like QUAKE). Engine reproduces the printout
  value-for-value: all 13 planet rows (positions, retro, dignities
  Sun-WEAK/Mercury-EXALTED/Moon-RULER/Neptune-RULER, nakshatra/pada/navam),
  cusps to the decimal, Pusyam 3. Two sub-arcminute artifacts, root-caused:
  ST 9H56M46S vs docx 47S; Moon 11 Can 25 vs docx 26 -> dasa balance days
  Sat 7-5-22 vs docx 7-5-11 (1 arcmin of Moon ~ 10 days of Saturn balance;
  NU's 2016 print predates the ss2 corrections; the port stands on
  PRATEEK/QUAKE oracles).
- Taught numbers verified: Nep-on-Ketu 1.15 (taught 1.1), Merc-on-Rahu 3.47
  at cast (docx 3.7 at its instant), Sun-conj-Jup 1.6 at cast; Moon squares
  EXACT 15:29 IST (Sun) and 19:24 IST (Jupiter) Sep 23 — the taught
  15:30-19:30 cloudburst window bracketed to the minute; Asc crossings
  04:50/17:06 (oracle tests, taught ~04:49/~17:04).
- ENGINE OBSERVATIONS (labeled, not doctrine): the nodal axis was held by
  FOUR constraints, not two — beyond the taught Mercury-on-Rahu +
  Neptune-on-Ketu also (a) real-Uranus TRINE Rahu 0.20 deg (doctrine-exact
  Mathcad offset; the tightest contact in the chart; exactness +334 h) and
  (b) Saturn SQUARE the nodal axis 0.38 deg (exact +77 h). Saturn-Neptune
  sq 0.77 as era backdrop. Dasa context: Saturn dasa / Rahu bukti — the
  period lords are the axis-square Saturn and the held Rahu. Band trigger
  correctly silent (mkm spread 184 deg). Rule-status question for NU
  raised: do real-Ura-trine-node and Saturn-square-nodes join
  observed-triggers (TESTING)?

## 2026-08-05 — The 2016 print's lineage: SOLVED (interpreter precision)
- NU asked for the docx dasa-delta lineage. Eliminated in order: inputs
  (ST matches to 1 s), source (the Moon blocks of ASTGRAF.BAS and
  ASTROLOG.BAS are substance-identical; the port carries that one series),
  series terms (all 20 coefficients + arguments equal). Root cause CONFIRMED
  by emulation: the canon declares no DEFDBL, so the family's interpreter
  ran SINGLE precision; float32 emulation of the identical series at the
  cast instant yields Moon 101.443 = 11 Can 26 (the docx), double yields
  101.419 = 11 Can 25 (the port); delta 1.44 arcmin, and the higher
  single-precision Moon sits deeper into Pusyam -> LESS dasa balance
  (docx Sat 7-5-11 vs port 7-5-22) — direction and size both check.
- Status: documented as an ENVIRONMENT difference (third documented class,
  tool README divergences section), no code change — the port follows the
  source in double precision; period prints can differ by ~1-2 arcmin of
  Moon (~10 days of balance) when the value sits on a print-rounding
  boundary. PRATEEK/QUAKE oracles were away from boundaries. NU may rule
  single-precision fidelity if family-print parity is ever preferred.

## 2026-08-05 — P4 done: M9 shared structure — NONE, even with four giants
- The five M9 dossier contact sets (doctrine orb, four-giant rsep included;
  6-14 fired contacts each of ~376 possible keys): shared by 5/5: 0; by
  4/5: 0; by 3/5: 0. The earlier stratified-mining M9 negative
  reconfirmed at the dossier level with the extended features. The M9
  class carries no common configuration element at contact grain — each
  event is its own fingerprint, consistent with the 130-year sweep. Family
  grain (band sectors) remains the only place M9-class recurrence could
  live; awaiting the flood-records list and category records for that.

## 2026-08-05 — P5 done: re-mine on the four-giant space — NO SURVIVORS (third verdict)
- Feature space extended to all four giants' real positions (signatures.py
  REAL_BODIES; 95 pair keys x 4 aspects = 380 predicates — the space the
  mining had never seen). Same honest design: declustered post-1900 corpus
  (1,435 events), golden-ratio climatology controls (4,305), add-one
  smoothed lifts, 500-run label-permutation calibration.
- VERDICT: observed max lift 1.705 (sep:Moon-Neptune@conj) vs null median
  1.748, p = 0.650 — BELOW the shuffled-label typical maximum. The new
  real-Jupiter/Saturn predicates top out at 1.37-1.41 (incl. the retired
  rule's rsep:Uranus-Saturn theme at 1.362), all chance-level. The mined
  channel stays empty on the richer space: third consecutive no-survivors
  verdict (v2 2026-08-02 p=0.35; corrected-corpus 2026-08-04 p=0.595;
  four-giant 2026-08-05 p=0.65). The statistical channel is closed unless
  NU supplies a categorically different corpus; doctrine and recurrence
  channels unaffected.

## 2026-08-05 — Author's briefing re-reconciled: galactic layer + GRF oracle
- NU re-sent the author's original briefing for a missed-detail sweep: 13/15
  instructions verified implemented; TWO gaps found in one sentence ("use the
  ayanamsa to locate the galactic pole and ecliptic in major events... see how
  much Magha... Punarvasu... as of today") and closed:
  (1) galactic.py + --galactic: per-event separations from the Punarvasu
  crossover (sector-7 start, 77.143 sidereal) and the Magha axis (sector-10
  center, 122.143, folded at 180); tropical charts shift markers by the suite
  ayanamsa; with --scope both axes draw on the wheels. Frame ruling: ASTGRAF.BAS
  contains NO Abhijit/28 data (checked again — 27-name DATA only, never used),
  so the frame is the book's 28-sector precession layer.
  (2) --precession now prints the equinox's angular offset from both markers
  with the drift-time equivalent.
- NU supplied canon/ASTROC.GRF — the AUTHOR'S OWN program output (1 Jan 2015,
  41 daily rows, tropical, blank site). grf.py parses the heritage format;
  the oracle test reproduces 11 bodies x 41 rows within 0.12 deg (GRF's own
  print resolution) and CONFIRMS the BAS pre-increment (first row = start+step,
  exactly as audited). RULING (NU, 2026-08-05): ASTROC.GRF is a SAMPLE output
  only — the Moon ~0.6 deg / Asc ~13 deg gaps just reflect the sample's
  arbitrary, unrecorded site/time inputs (the GRF stores no site/GMT fields).
  No author follow-up; the fast-mover test stays as a loose regression guard.
- RULING (NU, 2026-08-05): the GRF format is NOT a pipeline stage — no writer,
  no --from-grf. It exists only as the learning/verification oracle proving the
  fused pipeline (compute in memory -> one-by-one SVGs a la GRAPHDO) is correct.
- RULING (NU, 2026-08-05): 27 stays wherever the BAS computes (reaffirmed).
- Location-layer backtest (NU: "test nepal and other events if we can pin
  point"): scripts/loc_backtest.py over out/signatures-m7-v2 (1,435 M7+ events
  1850-2020, spots from light-time-earlier charts). Result: AT CHANCE on all
  three conventions — (A) nearest-of-four at event instant: median 4,878 km vs
  5,006 null, within-1000-km 3.34% vs 3.04%; (B) doctrine-conditional acting
  giant (real-Ura/Nep vs Sun/Rahu/Ketu, orb 1): 47 contacts, 0 within 2,000 km,
  median 8,892 km; (C) Nepal taught anchor: best spot Uranus 2,846 km at the
  event instant, 8,126 km at the Uranus-Sun exactness instant, Neptune worse.
  Honest conclusion: the current sub-planet + light-time-rotation rule does not
  pinpoint retrospectively; the WATCHLIST forward windows (spots already pinned
  through 2028) are the registered live test, prior now set by this backtest
  (WATCHLIST caveat added; summary at out/loc-backtest/summary.txt).
- Addendum (NU: "Jup 40 mins" — fixed taught constants): re-graded with flat
  40/80/150/240 in place of distance-true minutes — results IDENTICAL (Nepal
  Uranus 2,847 vs 2,846 km; catalog 3.34% within 1,000 km unchanged).
  Structural finding: stepping the acting chart light-time EARLIER and rotating
  WEST by the same minutes cancel to ~0.0007 deg/min — the spot is effectively
  the sub-planet point at the event instant, so the light-time constants barely
  move the PLACE at all (they matter to timing geometry only). The v1 reading
  (arrival chart + rotation, no earlier stepping) also grades at chance (2.58%
  within 1,000 km vs 2.91% null; Nepal Uranus worsens to 5,939 km). All
  readings of "rotate the long to suit" are now tested; none pinpoints. Note
  for the author conversation: the TAUGHT site examples (Ulsoor, Hyderabad)
  pinpoint TIMES at a known site via Asc crossings — the inverse problem —
  which may be the doctrine's actual location mechanism rather than a
  time->place spot rule.
- AUTHOR BRIEFING (2026-08-05, via NU) — the scalar-pulse doctrine:
  (1) the ecliptic-crossing impulse is IMMEDIATE — a scalar pulse, not an EM
  wave; (2) sky-watch in the REAL frame: current ephemeris / tropical, "not
  astrological because panchangam deducts ayanamsa" (matches our
  observed-triggers tropical ruling); (3) plot REAL positions for ALL ecliptic
  crossings; (4) DWELL TIME gates magnitude: > 3 SECONDS can create major
  shock waves; Nepal's dwell was 4 MINUTES "because both Uranus and Neptune
  crossed Ketu position one after another"; (5) location = rotation + ecliptic
  tilt + light-travel time, months/years ahead.
  Engine checks: real-Neptune on Ketu at the quake CONFIRMED (0.342 deg,
  matches taught 0.34); but real-URANUS was on the SUN (0.692), 26.5 deg from
  Ketu — "both crossed Ketu" does not hold in the longitude frame. The 3-s /
  4-min dwell figures are EARTH-ROTATION timescales (15 arcsec/s; 1 deg per
  4 min) — giant-planet longitude conjunctions dwell for DAYS, so his crossing
  must live in the rotation frame (meridian/RA sweep); no longitude geometry
  we can compute reproduces a 4-minute Nepal dwell. Reading D (scalar spot:
  observed->REAL via ahead-offsets, immediate impulse, NO propagation
  rotation, spot = sub-real-planet point) added to loc_backtest.py: Nepal
  Uranus improves to 1,746 km (best of all readings) but catalog still at
  chance (2.51% within 1,000 km vs 3.02% null; conditional orb-1 slice median
  7,682 km, 0/47 within 1,000 km). OPEN QUESTION for the author (the crux):
  the precise dwell definition — what crosses what, in which frame, and the
  tolerance that makes Nepal 4 min while the threshold is 3 s. A rotation-
  frame crossing is inherently site-specific, so that definition likely IS
  the location mechanism. Dwell layer NOT implemented — needs his formula,
  not our invention.
- RETRACTION + canon/SankhyaStellarPrediction.html read (NU challenge, "you
  sure interpreting the dwell time meaning correctly"). My "the crossing must
  live in the rotation frame" was ONE hypothesis stated as a conclusion —
  withdrawn as a conclusion, kept as a candidate. The author's 2016 JS
  (81 KB, 6 script blocks, read in full) is his own port of the same engine:
  * CONFIRMS: 27 stars ("Makha"), truncated PI, mxpr+1 pre-increment,
    eqls="Koch" HARDCODED (no E/W branch at all — our Koch default is right),
    ayanamsa only when zodtype=="E" (tropical = 0), same ss/ss1/ss2/aus
    elements, same ANU/ADX/ANX/ANQ/ANR/ANS/ANW/ANP helpers, same 20-term Moon.
  * GRAPH: y = cos(lon)*200+240, IDENTICAL to GRAPHDO.BAS line 54; axes
    labelled 0/360 bottom, 180 top, 90/270 middle. Our svgplot cosine_y
    reproduces this fold exactly (verified at 0/90/180/270/360).
  * The 14 colours from the briefing are here (Peru/Orange/SaddleBrown/Blue/
    Red/Cyan/Gold/RoyalBlue/Indigo/DarkGray/Green/LawnGreen/Magenta + black).
  * DEFAULT-VISIBLE TRACES: Asc, Moon, Uranus, Neptune (s5 line 4) — the
    author's own working set; everything else starts hidden.
  * CONTAINS NO dwell, crossing-detection, aspect, or location code at all
    ("RemoveRule" is a CSS call). The dwell doctrine exists in NO software he
    has given us — it is post-software teaching, so it cannot be recovered by
    reading code; only he can state it.
  * REAL GAP FOUND: the cos fold means two traces also cross when
    cos(l1)=cos(l2) with l1 = -l2 (MIRROR about the 0-180 equinox axis).
    Our aspect engine detects only conj/opp/square/trine and never the mirror.
    At Nepal three mirror pairs stood: Moon x Saturn 0.067 deg (very tight),
    Venus x Pluto 1.686, Uranus x Neptune 2.971. NOT implemented pending NU.
- Dwell candidate (arithmetic, NOT adopted): using the author's own two taught
  separations, real-Nep x Ketu 0.342 + real-Ura x Sun 0.692 = 1.034 deg swept
  at Earth's rotation 15.041 deg/h = 4.13 min — his stated "4 minutes", and it
  explains "BOTH crossed one after another" as two dwells ADDING. 3 s then =
  45 arcsec. Tested for generalisation over the 1,435-event catalog: corr
  (dwell, magnitude) = +0.238 at orb 1 (n=43) but -0.082 at orb 3 (n=147) —
  the sign flips with an arbitrary knob, so the Nepal fit does not replicate.
  Recorded as a candidate to put to the author, not a rule.
  NU ruling 2026-08-05: "yes i think this is what he meant" — the dwell
  candidate stands as the working reading (still unimplemented pending his
  exact formula; the non-replication above stays on record).
- MIRROR CROSSING IMPLEMENTED (NU: "do checkable gap you said in #1"), TDD,
  8 new tests, suite 221 -> 229 green. The cos-fold means traces also meet
  when lon_a + lon_b = 360k. aspects.py: mirror_offset() (signed miss) and
  find_mirror_events() (kind="mirror"); the audited scan loop was generalised
  over a metric so BOTH relations share one wrap-safe/sub-sampled/bisecting
  path — find_events behaviour is unchanged (test pins it). triggers.py: new
  "mirror" primitive (orb-gated, 2 bodies) with its own _metric_for exactness
  scalar so mirror rules refine to the instant like any other. scope.py:
  mirrors_in_orb() + dashed lines with data-mirror + legend. cli.py: --mirror
  writes mirror.csv (label, jd, bodies, lons, signed offset) and feeds the
  scope wheels. Nepal oracle: Moon x Saturn 0.067 deg from the mirror while
  127 deg apart classically — a crossing the author sees and we could not.
- GALACTIC-ECLIPTIC GEOMETRY COMPUTED (NU question). The two planes stand
  60.1886 deg apart and cross the ecliptic at 90.0232 / 270.0232 deg — the
  SOLSTICE points (0.02 deg off), from the IAU J2000 galactic pole
  (RA 192.85948, Dec +27.12825). Consequences: (1) the Sun crosses the
  galactic plane at the solstices — last 2026-06-21 08:51 UT northward,
  2025-12-21 15:29 UT southward; (2) as planes they never stop crossing, so
  the datable event is the EQUINOX reaching a node, every 12,886 y.
  *** VALIDATION OF THE AUTHOR'S FRAME ***: the equinox last stood on that
  galactic node in the MID-5th MILLENNIUM BC, and the book's own 28-sector
  clock puts the equinox ENTERING Punarvasu at 4439 BC. Honest error bar
  (self-corrected before reporting): the epoch depends on the precession
  model — linear 50.2879"/yr gives 4445 BC, the IAU2006 quadratic gives
  4539 BC, the book's constant 25,739-y cycle gives 4439 BC; spread 94 y.
  So the claim is "all three land within ~100 y of each other out of 6,500",
  NOT a 5-year match. The structural point is exact and model-free: the true
  node sits at ecliptic 90.02 deg and the book's Punarvasu sector boundary
  sits at 90.00 deg — 0.02 deg apart. His crossover marker IS the real
  galactic-ecliptic node, landing on a sector boundary of his own wheel, and
  the previous cycle back is his "30,000 years zero ascension in Punarvasu".
  NU RULING 2026-08-05: "crossover" MEANS the galactic-ecliptic node. Applied
  (TDD, 2 new tests, suite 229 -> 231 green):
  * galactic.py PUNARVASU_CROSSOVER_SIDEREAL 77.142857 -> 66.170810, derived
    from the measured ASCENDING node (tropical 90.02322 at J2000, minus the
    suite ayanamsa). Verified stable to 0.002 deg over 1900-2100, i.e. it
    behaves like the fixed inertial direction it is. CROSSOVER_TROPICAL_J2000
    kept alongside so the derivation is visible.
  * FRAME BUG FOUND AND FIXED while applying it: precession.report_lines was
    comparing the equinox's WHEEL longitude against markers labelled SIDEREAL
    — two frames an ayanamsa (~23.8 deg) apart. New precession.marker_on_wheel()
    converts a sidereal direction onto the wheel (S + ayanamsa(zero_year)), and
    equinox_offsets() returns both offsets. Oracle test: the equinox's offset
    from the crossover is 0.050 deg at year -4440 and 90.387 deg today — i.e.
    the machinery independently reproduces the crossing epoch.
  * Structural result, model-free: the node lands at wheel 89.967 against the
    Punarvasu sector boundary at 90.000 — 0.033 deg.
  * MAGHA NOT TOUCHED (unruled): its 122.142857 is 9.5 sectors OF THIS WHEEL by
    construction, so it is a wheel value despite the _SIDEREAL name, and it is
    now used as-is rather than converted (behaviour unchanged, label honest).
    OPEN QUESTION for NU: is the Magha axis meant to be the galactic CENTRE?
    Sgr A* (RA 266.41684, Dec -29.00781) is ecliptic 266.852 -> suite-sidereal
    243.00, folded 63.00 — 59 deg from the present constant. Until NU rules,
    galactic.py still treats Magha as a sidereal direction in chart work,
    which is the same frame mismatch the crossover just had.
- SELF-AUDIT of the three commits (NU: "check every change... useful and
  intentional"). Reviewed hunk by hunk; 3 real defects found in MY OWN work
  and fixed, suite 231 -> 232 green, no new lint:
  (1) DEAD CODE: CROSSOVER_TROPICAL_J2000 was defined and never referenced,
      while PUNARVASU_CROSSOVER_SIDEREAL carried a hand-computed 66.170810.
      Now the sidereal value is DERIVED from it (node - ayanamsa(2000)), so
      the two cannot drift apart; the redundant lazy ayanamsa import in
      marker_longitudes went with it. No import cycle (ephemeris <- models).
  (2) INCOMPLETE FEATURE: mirror rules refined to an instant but named no
      acting body, so their episodes carried NO SPOT while every other pair
      primitive published one. acting_body_at now handles mirror, measuring
      the gap on the condition's OWN specs so a `real:` prefix is honoured.
      Two wrong test premises were caught by the red phase on the way:
      real-Nep x Ketu at Nepal is a CONJUNCTION not a mirror (17.43 deg off),
      and Saturn IS a light-time body — the corrected test pins Uranus (the
      genuine 2.971 mirror), Saturn (the tight 0.067 pair) and two negatives.
  (3) CONTRADICTORY COMMENT: galactic.py claimed "Both markers are FIXED
      SIDEREAL directions" and then documented Magha as a wheel value; the
      wheel-vs-boundary figure also said 0.02 where the computed value is
      0.033. Both corrected.
  Cosmetic: mirror_offset had been defined above the _wrap180 it calls (moved
  below). Accepted as-is: mirrors_in_orb evaluates mirror_offset twice per
  pair (78 pairs, negligible) — not worth the churn.
  Process note: commit 93b760c bundled NU's new canon files with an unrelated
  epoch correction; disclosed in the message but they should have been split.
- MAGHA FORK DOCUMENTED (NU: "document well"). FRAMEWORK open question 9 now
  carries the whole thing: the two readings side by side (sector-10 centre
  122.143 in force vs the galactic CENTRE, Sgr A* ecliptic 266.852 =
  suite-sidereal 243.00, folded 63.00), the 59 deg gap that no orb hides,
  the two consequences (every galactic.csv Magha separation and --scope spoke
  moves; and the wheel-vs-sidereal frame defect rides along, since 122.143 is
  9.5 sectors OF THE WHEEL), and what would settle it. galactic.py points at
  it. Nothing changed in behaviour — the fork is NU's/the author's to close.
- canon/HORARYaura.docx READ: it is the HORARY.BAS listing verbatim (243
  cusps = 27 x 9, sub and sub-sub from the Vimshottari RT years, BR lord
  order from Ketu). No new code, but NU's covering note supplies the
  RESOLUTION BUDGET, now FRAMEWORK section 3a:
  * the horary divides by 9 and again by 9 -> one cell = 1/81;
  * per degree: 240 s / 81 = 2.963 s ("about 3 sec"), 60' / 81 = 0.741'
    ("about a min"), 111.32 km / 81 = 1374 m (his 100 km -> 1234 m);
    equator speed 465 m/s (his 400); his headline "1200 m and 3 secs" is
    internally consistent (3 s x 400 m/s), ~10% off the exact figures only
    because of the 100-vs-111.32 km rounding. One more 9 (1/729) -> ~1 s,
    ~460 m, his stated ideal ("divide these results by 3").
  * ARITHMETIC DISCREPANCY, flagged not silently resolved: his words say
    "1/81 of a house of 30 deg" (= 0.370 deg) but every figure he computes
    divides ONE degree by 81 (= 0.0123 deg). The per-degree reading is the
    operative one — it is the only one consistent with "about a min apart"
    and with 1234 m / 3 s.
  * *** THE 3-SECOND DWELL THRESHOLD IS NOT ARBITRARY ***: 240 s / 81 =
    2.963 s IS one horary cell of time. His "dwell more than 3 seconds ->
    MAJOR SHOCK WAVES" reads as "longer than one resolution cell". And the
    Nepal dwell of 4 min = 240 s = 81 cells = exactly ONE DEGREE of rotation,
    which is also what the taught separations sum to (0.342 + 0.692 = 1.034
    deg). Three separate statements of his land on the same quantum — the
    strongest support the dwell reading has, and it arrived independently of
    the fit that produced it.
  * NOT IMPLEMENTED, per NU: keep as a sub-program "only to improve accuracy
    WHEN we can predict spot on". Refining a spot to 1.2 km while the
    location layer grades at chance would be false precision on a marker
    that is not yet in the right place. Recorded as a finishing step.
- ASCENDANT LOCATION MECHANISM RULED OUT (NU: "are they useful for the
  location-layer"). I had proposed the Asc as the likely real mechanism
  (2026-08-05, "the taught site examples pinpoint TIMES at a known site —
  the inverse problem — which may be the doctrine's actual location
  mechanism"), and NU's 1/81 budget states its cell in lat/long terms, so it
  was the strongest surviving candidate. TESTED instead of assumed:
  scripts/asc_fingerprint.py computes the Asc AT the true epicenter AT the
  true instant and compares it with a null that keeps the same sites and the
  same instants but breaks their pairing — which rules out the whole family
  without having to guess the specific rule (cell, lord or aspect).
  Result, stable across seeds: Asc round the zodiac p = 0.12/0.23, within a
  nakshatra p = 0.59/0.88, within a horary sub p = 0.85/0.36; Asc-to-nearest-
  real-giant within 3 deg 6.3% (chance ~6%); and in the doctrinally faithful
  slice where a taught crossing is actually in force, p = 0.35-0.99 at both
  orb 3 (n=148) and orb 1 (n=44). NOTHING anywhere.
  Method notes kept honest: (a) an early version compared chi2 across
  different sample sizes, which is invalid since chi2 scales with N — fixed
  by drawing same-N null subsamples for an empirical p; (b) with only 3
  nulls per event the null median swung 13.6-22.1 between runs and the
  p-value with it (0.06 vs 0.45), so the pool went to 12 per event and the
  numbers stabilised; (c) high-latitude events where the canon's Koch cusps
  are undefined are skipped and COUNTED (0 of 600 in the main sample).
  CONSEQUENCE: two whole families are now closed — no rotation-based spot
  construction (4 variants, loc_backtest.py) and no Ascendant-based rule
  places these events. What remains is either a dwell/crossing definition
  unlike every reading tested, or a piece of the doctrine we do not have.
- MIRROR CROSSING GRADED — NO MINED SIGNAL (NU: "go"). scripts/mirror_lifts.py
  reuses the v2 corpus and protocol EXACTLY (the same 1,435 declustered
  post-1900 events and 4,305 time-uniform controls whose jd columns the
  audited mining used; add-one smoothed lifts; 200-permutation max-lift bar),
  swapping only the predicate family: 95 mirror predicates (55 observed pairs
  + real-giant pairs), hit = |lon_a + lon_b| within orb of 0.
  orb 3 deg: an event chart carries 1.577 mirror hits on average vs 1.553 for
  controls — no aggregate difference. Best predicate mir:Jupiter-Saturn lift
  1.719, and the permutation null's MEDIAN is 1.720 (95th pct 2.057), so
  p = 0.505 — the best of 95 lands precisely where chance puts it.
  orb 1 deg: nothing clears the 2% event-rate floor (0.511 vs 0.512 hits).
  Reads exactly like the retired aspect mining (max lift 1.79 vs null 1.73,
  p = 0.35). VERDICT: the mirror layer faithfully reproduces what the
  author's graph shows and lets a taught rule be EXPRESSED, but it is not a
  miner — no mirror predicate predicts M7+ timing. Scope of the negative:
  this is the quake corpus only, and single predicates only; it does not test
  the mirror inside a compound taught rule, nor for floods/biological events.
  Recorded in README (mirror section) and FRAMEWORK (implementation map).
- SPOT BRAINSTORM, EVIDENCE FIRST (NU: "brainstorm how the spot should be
  located"). scripts/spot_hypotheses.py, four diagnostics:
  (1) *** FEASIBILITY, the structural finding ***: a giant's sub-planet point
      can never leave |lat| <= 23.71 deg (its declination bound), but 44.4%
      of M7+ epicenters (637/1435) lie OUTSIDE that band — median |lat| 20.7.
      So a declination->latitude rule cannot locate nearly half of all major
      quakes NO MATTER what longitude rule accompanies it. This is geometry,
      not statistics, and it condemns the point-at-the-sub-planet family
      independently of every lift measured so far. Alaska, Chile, Japan,
      Kamchatka are unreachable in principle.
  (2) LOCI instead of points — a pulse along the planet-Earth axis also marks
      the antipode, the 90-deg "max shear" great circle and the 45/135-deg
      small circles; circles reach EVERY latitude, so they escape (1).
      Result: the circle loci track their nulls exactly (shear 0.256 vs
      0.239; 45/135 0.390 vs 0.409 within 5 deg). The escape route is
      geometrically available and empirically empty.
  (3) The plain sub-point (observed positions, no light-time, no rotation —
      simpler than our locator) is the ONLY construction that separates from
      its null, and only in the tightest bin: 23/1435 within 5 deg (557 km)
      vs a null mean of 16.9, lift 1.77, stratified-permutation p = 0.054
      (0.016 on an earlier control draw — it moves with the draw, which is
      itself a sign it sits at the edge of detectability). NOT a discovery:
      ~8 geometric variants were tried, so corrected p ~0.13, and this
      project's own mining null puts the best-of-many lift at 1.72 BY CHANCE
      against this 1.77.
  (4) Split-half over 2-year blocks: same direction in both (lift 1.43 p=0.115
      and 1.66 p=0.050), significant in neither. Weak-and-consistent, or a
      small-number artifact — only fresh data separates those.
  STANDING: nothing is adopted, no constant or default changed. The one
  pre-registerable candidate is the plain sub-point at 5 deg; the honest test
  is out-of-sample (the M6.5-7.0 band, or the WATCHLIST windows as they
  mature), NOT more variants on this corpus.
- FULL RE-READ OF THE AUTHOR'S CONTEXT (NU: "brainstorm, deep research and
  interpret yourself"). Two sections added to spot_hypotheses.py:
  (5) THE LONGITUDE CHANNEL ALONE — he says "rotate the LONG to suit", and
      unlike latitude, longitude has no tropical bound, so this is the
      geometric construction's last hope. All three conventions tested (west
      = our locator, east = the "observer rotated away" reading, none): every
      one tracks its null (within 10 deg: 0.183/0.219, 0.191/0.189,
      0.209/0.200). BOTH halves of the geometry are now empty — latitude by
      impossibility, longitude by measurement.
  (6) THE MATRIX AS MEMORY — his OTHER stated mechanism, and the one I had
      been ignoring: "each of these matrix points would contain confirmed
      event synchronisation factors from past records... an algorithm to
      pinpoint areas on Earth that would be affected". Tested whether events
      sharing a 28x11 cell cluster geographically MORE than random catalog
      events (null respects the Ring of Fire): 21 of 296 cells beat p<0.05
      where 14.8 are expected — 1.4x, not significant. Caveat that matters:
      his memory half is indexed on a multi-category 1000-year record (open
      question 7, never supplied), not on M7+ quakes.
  *** THE INTERPRETIVE FINDING ***: the author never claims a WORKING
  location algorithm. "Computerisation and development of algorithm to
  pinpoint areas on Earth that would be affected in each category WOULD BE
  NECESSARY" — future tense, in his own text. We have been reverse-
  engineering a finished method from a description of an intended one. His
  location theory has two halves: geometry (light-time x rotation, "rotate
  the long to suit") which we implemented and which measures flat, and
  memory (the matrix cells learned from records) which HE leaves unbuilt.
  LIGHT-TIME DISCREPANCY BETWEEN HIS OWN TWO SOURCES, now quantified:
  the Mathcad offsets decode to (a/2-1) AU = 13.3/31.5/71.4/116.4 min for
  Jup/Sat/Ura/Nep, while the prose gives 40/80/150/240 min = exactly the
  NEAREST-approach distance (a-1) AU, which his own sentence confirms
  ("these figures are for the nearest position"). Ratio 3.00/2.54/2.10/2.06.
  We use BOTH — Mathcad offsets for real-position timing (validated by the
  taught Nepal 0.34 deg signature) and prose minutes for the spot rotation —
  which may be correct (two quantities, two roles) but must be put to him.
  His km series (1000/2000/4000/8000) is a clean doubling that matches the
  physics for Jup/Sat/Ura (1116/2232/4186) and BREAKS for Neptune (6697),
  another sign the spot figures were reasoned by pattern, not computed.
- *** NU RULING 2026-08-05: "Mathcad version is the one", and "dont
  underestimate his statements 'rotate the long to suit'" *** — a correction
  of my dismissal of the rotation as a rule of thumb. APPLIED to the code:
  * KEY DECODE: the Mathcad quantity (a/2-1)*500/240 is ALREADY degrees of
    ground rotation (500 s per AU of light travel, 240 s per degree of Earth
    rotation). So REAL_POSITION_OFFSETS *is* "rotate the long to suit", and
    the light-time is offset x 4 minutes: Jup 13.35, Sat 31.47, Ura 71.42,
    Nep 116.37 min.
  * locator.py now rotates by ROTATION_DEGREES = the Mathcad offsets
    (3.336/7.867/17.856/29.092 deg). SUPERSEDES BOTH the prose figures
    40/80/150/240 min (= 10/20/37.5/60 deg) AND the 2026-08-02 distance-true
    refinement — the Mathcad is defined on the orbital radius, so the
    rotation is a FIXED constant; light_minutes_for no longer consults the
    chart's distance. Both supersessions are stated in the module header and
    pinned by tests so neither can be re-introduced silently.
  * BLAST RADIUS, all reported not hidden: 232 tests green after updating 4
    that pinned the old rotation (now asserting the RULE — delta ==
    ROTATION_DEGREES[body] — rather than re-baselined magic numbers). EVERY
    REGISTERED WATCHLIST SPOT MOVED EAST: Uranus rows +21 deg, Neptune rows
    +31 deg, i.e. 2,000-3,500 km into different regions (2026-10-16 was
    140.33W E of Hawaii, now 119.24W off Baja; 2027-11-12 was the mid-Indian
    Ocean, now central SUMATRA). Band-window giant spots and the three
    nodes-cluster Jupiter spots recomputed too. WATCHLIST carries a REVISED
    banner with the supersession and a worked example; old values remain in
    git history. Latitudes unchanged (declination), instants unchanged.
  * MEASUREMENT, on record and NOT a veto of the ruling: tested all six
    readings of the Mathcad rotation (observed/real position x west/east/none)
    against the audited controls — every one tracks its null on the M7+
    catalog (longitude within 10 deg: 0.221/0.207 best case). The ruling is
    doctrinal and the corpus is quake-only; both statements stand.
  * STILL OPEN, flagged for NU: signatures.py steps the chart light-time
    EARLIER and then locate() rotates west, and these cancel EXACTLY (the
    minutes and the degrees are now the same quantity). The author's scalar
    pulse is IMMEDIATE, which argues the earlier-chart step should not exist
    at all — but that is an audited behaviour (finding 11), so it is left in
    place pending a ruling. Until then the ruling changes CLI/bands spots but
    not signature-corpus spots.
- SELF-AUDIT of the two ruling commits (NU: "check every change... useful and
  intentional"). Code verified clean: the deleted ENGINE_UNITS_PER_AU /
  LIGHT_MINUTES_PER_AU are referenced nowhere; BodyPosition.distance is still
  consumed by bands (Saturn closeness) and signatures (dist: features) so no
  orphan; light_minutes_for's now-unused `result` parameter is deliberate and
  documented (callers unchanged). THREE DEFECTS FOUND AND FIXED:
  (1) ROTATION_DEGREES was public but production code never used it — locate()
      round-tripped through minutes x 0.25. locate() now applies
      ROTATION_DEGREES directly so the rule is visible where it acts (same
      value; x4 then x0.25 is exact in binary).
  (2)+(3) THREE PLACE NAMES WERE WRONG. I generated the region wording from
      coordinates by reasoning, with no geocoder, and did not verify:
        * 1.9E 13.3N called "Burkina Faso / Benin border" — it is SW NIGER,
          31 km from Niamey (Benin's northern tip is ~12.4N, so 13.3N cannot
          be Benin at all);
        * 49.7E 15.6N called "Gulf of Aden off Somaliland" — it is INLAND
          YEMEN, ~140 km north of Mukalla (the Gulf lies south of that coast);
        * README's worked example 100.17E 4.67N called "the Malay peninsula
          near the Thai-Malaysian border" — it is the Strait of Malacca ~50 km
          off Perak, ~200 km south of that border.
      All three corrected, several others loosened (Andhra->Vijayawada,
      Darfur->N Kordofan, Tak->Kanchanaburi, Makran->"~530 km S of the coast"),
      and WATCHLIST now carries an explicit caveat that lat/long are
      authoritative while the region wording is a hand-derived reading aid.
      LESSON: coordinates computed by the engine are trustworthy; prose
      geography written from them is not, and must be checked against
      landmarks before it enters a register.
- NEPAL RE-TESTED UNDER THE MATHCAD RULING (NU: "did you test it using nepal
  example") — I had adopted the ruling WITHOUT re-running the anchor. Done now,
  and the honest result is that IT IS WORSE:
  | convention | old rule | Mathcad ruling |
  | Nepal best-of-four (event instant) | 2,846 km (Uranus) | 4,151 km (Uranus) |
  | Nepal Uranus x Sun at exactness | 8,126 km | 8,120 km |
  | catalog within 1,000 km | 3.34% vs 3.04% null | 3.83% vs 3.00% null |
  So the catalog lift edges up (1.10 -> 1.28, still inside the 1.72 chance bar
  this project's own mining null established) while the taught anchor gets
  1,300 km worse. Neither is a pinpoint; the ruling is doctrinal and stands,
  and this measurement sits beside it rather than overturning it.
  HARD CEILING restated: Gorkha is at 28.23 N and no sub-planet point exceeds
  23.71 N, so latitude alone costs >= 503 km before longitude is considered.
- STALE-ARTIFACT BUG CAUGHT (the completion-claims lesson repeating):
  loc_backtest.py sections A/B/C read the spot_lat/spot_lon/loc_km columns
  STORED in signatures.csv, which were computed under the OLD rotation — so
  after the ruling the script silently reported superseded numbers (it printed
  the pre-ruling 3.34% while the live figure is 3.83%). All three sections now
  recompute from locate() live; section D was already live. Anything that
  caches a spot must be regenerated or recomputed when the rotation changes.
- EXHAUSTIVE NEPAL SEARCH (NU pressed hard for a pinpoint; this is the full
  space actually tested, not a sketch):
  1. SUB-POINT OF EVERY BODY, not just the four giants — I had only ever
     located the giants because LIGHT_MINUTES holds only those, while the
     author's own default plot is Asc+Moon+Ura+Nep. At the Gorkha instant the
     ranking is Sun 1,694 km, Mars 1,950, Mercury 1,984, Uranus 2,852,
     Ketu 3,627 ... Saturn 16,650. NOTHING is near.
  2. ALL ROTATION CONVENTIONS (Mathcad/prose/distance-true x west/east/none,
     observed and real positions): none brings any body onto Gorkha.
  3. ASCENDANT CONDITIONS at Nepal's longitude and instant: the latitude that
     puts the Asc exactly on Jupiter is 40.29 N (1,342 km off), on
     real-Jupiter 47.66 N, on the Moon -5.6 N. None gives 28.23 N.
  4. CULMINATION/MC: the MC at Gorkha is 32.74 with the Sun at 34.74 and
     real-Uranus at 35.43 — the taught crossing pair IS nearly culminating,
     and the Sun's culmination meridian is 86.66 E against Gorkha's 84.73 E,
     only 193 km. THIS LOOKED LIKE THE MECHANISM AND IS NOT: tested on the
     other taught anchors it fails outright — Hyderabad 7,405 km, Ulsoor
     9,480 km. Caught as overfitting before it was proposed.
  5. THREE-ANCHOR CONSISTENCY (the discipline that killed 4): for Nepal,
     Hyderabad and Ulsoor together, NO body's sub-point is near all three.
  6. CATALOG, longitude channel, ALL 11 bodies (not giants alone as before):
     at chance — within 5 deg 0.2599 observed vs 0.2697 null. Sun-only shows
     0.0369 vs 0.0251 (lift 1.47), but that is a LOCAL-TIME excess, a classic
     catalog-artifact class, one of four tests, and Nepal-only per (4).
  *** THE STRUCTURAL RESULT, stated once and for all ***: across all three
  taught anchors and every body, the spot latitude minus the site latitude is
  ALWAYS NEGATIVE. Every ecliptic body's sub-point is capped at |lat| 23.44
  (the obliquity — that IS the definition of the tropics) while Gorkha is at
  28.23 N, Tohoku 38.3, Kamchatka 52.6, Alaska 60.9. The sky, in this frame,
  cannot express the latitude of 44% of M7+ events, Nepal included. No
  rotation, constant, instant or body choice can lift that ceiling; only a
  different latitude source can. That is why no pinpoint has been produced,
  and it is a geometric fact rather than a failure of search effort.
  WHAT WOULD CLOSE IT (in order of value): (a) the author's own answer to
  "has your method ever placed an event beyond 23.5 deg latitude, and how" —
  Nepal itself is beyond it, so he must have a latitude source we have not
  been told; (b) his 1000-year multi-category record, which is the training
  corpus for the 28x11 memory half he explicitly leaves unbuilt.
- Location-layer interpretation re-confirmed for NU (see FRAMEWORK two-channel
  ruling): spot = sub-planet point (culmination meridian + declination
  latitude) rotated WEST by light-time x 15 deg/h; v2 distance-true; per-planet
  one-by-one. 221 tests passing (incl. NU's new anchors/families/recurrence
  suites).
- *** THE SITE-ANGLE LAYER — a location mechanism that fits all three taught
  anchors, built as src/astgraf/angles.py (6 tests, suite 232 -> 238) ***
  Found by asking what the three taught sites have in common instead of what
  formula moves a sub-planet point. Answer: at each one the CROSSING PAIR
  stands on an ANGLE of the site's own chart —
    Nepal      Sun 2.00 deg and real-Uranus 2.69 deg from the MC
               (his taught pair IS "real-Uranus on the Sun" — it culminates)
    Hyderabad  Neptune 0.56 and Ketu 0.59 from the Asc, Rahu 0.59 from Desc
               (his "Jup and Nep are at the ket and Rahu nodes")
    Ulsoor     Neptune 0.09 from the Asc, Saturn 1.51 from the MC
               (his "the Asc swept Neptune -> Sun -> Ketu -> Uranus")
  This is the author's own language, and it escapes the tropical ceiling that
  kills the sub-planet spot: the MC fixes a MERIDIAN (longitude, sharply) and
  the Ascendant fixes a CURVE that reaches every latitude.
  SELECTIVITY CONTROL (run before believing it): "some body within 3 deg of
  some angle" is nearly vacuous — 66% of random site/instant pairs satisfy it,
  median tightest 1.11 deg. Nepal's 2.00 is unremarkable (53% of random sites
  do better), Hyderabad's 0.56 is top-22%, Ulsoor's 0.09 top-3.7%. So the rule
  has content ONLY in its specified form — the pair NAMED BY THE CROSSING on
  the angle, a ~1.3% coincidence per body — which holds at Hyderabad and
  Ulsoor. The unspecified version must never be quoted as evidence.
  CONDITIONING, the real limit on pinpointing: dAsc/dlat is only ~0.35 deg per
  degree, so latitude is the soft axis — a 1 deg Asc residual becomes ~3 deg
  (~330 km) of latitude, and solving both angles at once for the anchors gives
  938-3,820 km. Longitude is sharp, latitude is not. This is ALSO why the
  author's 3-second quantum matters: 3 s is 0.0125 deg of Asc ~ 4 km of
  latitude, so his claimed precision is reachable ONLY if the crossing instant
  and the angle condition are both exact.
  STATUS: mechanism implemented and pinned to the anchors; NOT yet a validated
  predictor — it needs the same catalog grading the other channels got.
- *** SITE-ANGLE LAYER GRADED AND RETIRED AS A PREDICTOR (same day) ***
  scripts/angle_grade.py + scripts/angle_power.py, suite 238 -> 239.
  The grading had to change shape: every other channel claims an INSTANT and
  was graded against time-uniform controls, but this one claims a PLACE, so
  the instant is held fixed and the PLACE is varied. Control places are the
  other events' own epicenters (leave-one-out), which matches the geography of
  seismicity exactly, so the test asks the only question a location layer must
  answer: given a quake happened in the belt, does the rule say WHICH place?
  At a fixed instant the true epicenter and its 49 controls are exchangeable
  under the null, so the RANK of the true place is exactly uniform — no
  calibration needed, which is why rank is the primary statistic here.
  RESULT over 1434 declustered post-1900 M7+ events:
    T1 per-body      best of 15 is Mars z = -2.27 (bar is z = -3.0). Nothing.
    T3 specified     acting taught contact only, 314 instances: z = -0.35.
    T6 doctrinal     same 314 at the CROSSING EXACTNESS instant — the instant
                     a forward run actually has — z = +1.20. Nothing.
    T4 unspecified   lift 1.050 at orb 3 deg, exactly as vacuous as warned.
    T5 Nepal         specified bodies rank 5/50 (top-10%, ~1 event in 10 does
                     this); unspecified tightest body ranks 25/50, dead median.
  POWER FIRST, then the null: a null from a blind instrument is worthless, so
  angle_power.py plants epicenters where the body sits exactly on an angle and
  re-runs the identical statistic. Detection at z = -41.6 exact, and still
  z = -17.9 after +-25 deg of jitter. BOTH angles are planted — the first pass
  only tested the MC and then generalised to "any angle rule", which was an
  overclaim, because the taught Hyderabad and Ulsoor readings are ASCENDANT
  ones and the Asc is the weakly-conditioned axis. Adding the Asc arm confirms
  the same power (z = -17.1 at +-25 deg), so the verdict now covers the axis
  the anchors actually used. Enforced in tests/test_angles.py so it cannot rot.
  SCOPE LIMIT discovered while running it: the BAS cusp chain takes
  sqrt(1 - xx*xx) with xx = sin(RA)*tan(ob)*tan(lat), so it is undefined once
  tan(lat) >= 1/tan(23.44) — i.e. beyond the polar circle at 66.56 deg. The
  angles literally do not exist up there. 1 of 1435 events excluded, from both
  arms. Any future location work inherits this ceiling.
  WHAT THIS MEANS: the three-anchor fit was a fit. Three sites hand-picked
  from the author's teaching is exactly the selection process that manufactures
  such agreements, and the catalog says the pattern does not generalise.
  angles.py stays as a way to READ a chart's angles; it must not be used to
  claim a location. Third location family retired by test, after the
  rotation-based spots and the Ascendant-based rules.
- *** THE DWELL CLAIM: TRIGGER HALF FAILS, MAGNITUDE HALF SURVIVES ***
  scripts/dwell_grade.py. The construction comes from his two numbers: dwell =
  SUM of active crossing separations x 4 min/deg. At Gorkha the two taught
  contacts are real-Uranus/Sun 0.692 and real-Neptune/Ketu 0.342, summing to
  1.034 deg = 4.14 min, which reproduces his "4 minutes" AND his "one after
  another". CAVEAT ON THE RECORD: one confirming instance, and his prose puts
  BOTH crossings on Ketu whereas the chart puts real-Uranus on the Sun, 26.5
  deg from Ketu. The number fits; the attribution does not.
  TRIGGER HALF — FAILS. Events carry no more dwell than time-uniform controls
  (+0.054 min at orb 3, p = 0.42; at orb 1 it runs the WRONG way, events 0.062
  vs controls 0.079). His 3-second threshold is vacuous as literally stated:
  3 s IS 1/81 deg, so any crossing inside orb clears it, at the same rate for
  events and controls.
  MAGNITUDE HALF — SURVIVES. Four cells of dwell-vs-magnitude:
    taught/orb1  rho +0.3223 (n= 44)   <- the hit
    all4/orb1    rho +0.1923 (n= 95)
    taught/orb3  rho -0.0646 (n=148)
    all4/orb3    rho +0.0085 (n=268)
  Shuffling magnitudes across ALL events and recomputing every cell (which
  preserves the nesting between cells) gives family-wise p = 0.042, null
  median 0.137, 95th pct 0.310. This is the FIRST thing in this project to
  clear a multiplicity-corrected bar, so it was attacked three ways:
    1. COUNT CONFOUND? No. count-vs-magnitude is only rho +0.100, and within
       events having exactly ONE active crossing (n=41) rho stays +0.3145. It
       is the WIDTH of a single crossing — which is his claim, not a restated
       stack count.
    2. SPLIT-HALF? Holds. earlier n=22 rho +0.455, later n=22 rho +0.333.
    3. IS THE TEST HONEST? An injected rank correlation of 0.30 is recovered
       at 0.306, detected in 8/12 draws — underpowered but unbiased. NOTE the
       first version of this power arm was BROKEN (injected on raw dwell,
       which is skewed, so 0.25 scored below 0.10); it was rebuilt on ranks
       and averaged over seeds before any of this was believed.
  STATUS AT THE TIME: the project's one live lead, NOT a result — n=44,
  p=0.042 marginal, construction fitted to a single anchor.
- *** AND IT DID NOT REPLICATE — the dwell lead is dead ***
  scripts/dwell_holdout.py, data/usgs-m6-1900-2020.csv (12,212 events fetched
  from USGS FDSN, minmag 6.0 maxmag 6.99 — disjoint from the M7+ corpus by
  construction, verified in-script by asserting max mag < 7.0). Declustered
  with the identical 7 d / 500 km keep-largest rule to 10,324; 338 carry an
  active taught crossing at orb 1.
  PRE-REGISTERED before running: one cell (taught giants, orb 1), one
  statistic (Spearman dwell vs magnitude), one-sided because the direction was
  predicted, expected rho > 0 of order +0.3. No re-tuning permitted.
  RESULT: rho = -0.0399, one-sided p = 0.768. Wrong sign. Every secondary cut
  agrees: count -0.033, within-single-crossing -0.019, halves -0.048/-0.045,
  1970+ -0.041, and pooled M6+M7 over the full 6.0-8.5 range (n=382)
  rho = -0.0528, p = 0.298 — which also kills the range-restriction excuse.
  POWER: injecting a true rho of 0.32 into these same 338 events recovers it
  in 12/12 draws, rho 0.20 in 11/12, rho 0.10 in 6/12. The test could not have
  missed the claimed effect.
  VERDICT: the dwell doctrine is unsupported. Trigger half vacuous, magnitude
  half a winner's curse — an underpowered cell taken as the max of four, on a
  construction fitted to one anchor. FAIR CAVEAT ON THE RECORD: his claim is
  about MAJOR events, and a mechanism switching on only above M7 would not
  appear in the M6 band; but the M7+ result now rests on nothing except its
  own selection.
  METHOD NOTE WORTH KEEPING: pre-registering the cell and direction BEFORE
  running is what made this a clean kill rather than another argument. Do it
  for every future lead.
- *** THE ROTATION SPECTRUM: NO GROUND ROTATION CARRIES LOCATION SIGNAL ***
  scripts/rotation_spectrum.py. NU's reading of the author's briefing found
  that his PROSE light-times (Jup 40, Sat 80, Ura 150, Nep 240 min ->
  10/20/37.5/60 deg) reproduce his own stated displacements (1000/2000/4000/
  8000 km) while the Mathcad offsets we implemented (3.34/7.87/17.86/29.09,
  from (a/2-1)*500/240) are about a third of that. Rather than test two
  candidates, the rotation was SCANNED right round the circle at 5 deg steps
  for each giant, using the same leave-one-out epicenter rank statistic the
  angle layer was graded with.
  THE SPECTRUM IS FLAT. Deepest dip anywhere is Neptune at 25 deg, z = -2.32,
  against a z = -3.7 bar for 4 bodies x 72 angles. The per-body minima sit at
  Jup 270, Sat 170, Ura 60, Nep 25 deg — NOT clustered near the physical
  light-time values, which is what a real propagation effect would produce.
  BY CONVENTION (nearest-of-four, within 1000 km / rank z):
    mathcad (current)   0.0383  z -1.67
    prose 40/80/150/240 0.0258  z -1.04   <- WORSE, not better
    no rotation at all  0.0328  z -1.15
  At Gorkha itself, NO rotation is best (Uranus 2852 km) vs mathcad 4151 and
  prose 5939. Adding any rotation moves the spot AWAY from the taught anchor.
  POWER FIRST: planting synthetic epicenters at a known 100 deg rotation, the
  scan recovers it in the exact 5 deg bin at z = -64, and still exactly at
  z = -60 with +-30 deg of jitter. The instrument finds rotations that exist.
  CONSEQUENCE: the Mathcad-vs-prose question is settled for PREDICTION — the
  3x discrepancy was never what was costing us accuracy, because no value
  works. It is NOT settled as doctrine: the evidence says neither predicts,
  not which one the author meant. NU's Mathcad ruling can stand on doctrinal
  grounds; it simply has no predictive consequence. Fourth location family
  retired by test, and the first one retired across its ENTIRE parameter
  space rather than at a single point.
- *** THE CANON HAS NO LUNAR LATITUDE — the tropical ceiling is HIS ceiling ***
  Chasing NU's question "what is 23.5", the per-body bound was measured rather
  than assumed, and it is NOT a flat 23.44: a sub-point's latitude is the
  body's declination, bounded by obliquity PLUS the body's own ecliptic
  latitude. Sun 23.44, Uranus 24.06, Neptune 24.20, Jupiter 24.37, Saturn
  25.62. Beyond even Saturn's bound lies 41.8% of the M7+ catalog (600/1435);
  the old "44%" used the flat 23.44 and was slightly overstated.
  The Moon is the interesting case. In the real sky it reaches +-28.6 deg at a
  major standstill — PAST Gorkha's 28.23 N — because its orbit is inclined
  5.15 deg. But ASTGRAF.BAS cannot express that: its 20-term Brown series
  accumulates ML, a LONGITUDE correction only (PX = LL + ML), with no sin(F)
  latitude terms anywhere in the block. Our port reproduces this faithfully
  (ecliptic_latitude is computed only in the planet loop from the geocentric
  vector; the Moon defaults to 0.0) — verified against canon/ASTGRAF.BAS
  lines 253-320, so it is a canon limitation, NOT a port bug.
  WHY IT MATTERS: the author's own program cannot place a sub-planet point at
  Gorkha's latitude by ANY body, the Moon included. That sharpens the standing
  question to him from "how do you exceed 23.5" to something much more precise:
  his latitude source cannot be a sub-planet point computed by ASTGRAF at all,
  so it must come from somewhere the program does not compute.
  STILL OPEN, and the honest next lead: every location family tried so far
  derives the place from the sky ALONE. The author's own claim couples a
  crossing to a 1/81 horary subdivision, which needs a reference longitude to
  subdivide FROM — and we have never been told what his zero is. Until that
  arrives (or the 1000-year record), there is no location layer to grade.

## 2026-08-05 — Cross-session reconciliation: five documentation gaps closed
- Reviewed all 22 commits made after 0d5f9dd by the parallel session
  (locator v3 Mathcad ruling, angles.py site-angle layer graded + retired,
  mirror crossings, galactic layer, GRF oracle; 239 tests green). Work is
  sound; five gaps found where the new ruling did not reach:
  (1) CONSEQUENTIAL — locator v3 sets ROTATION_DEGREES =
  dict(REAL_POSITION_OFFSETS), so the PROVISIONAL canon-axis Jupiter
  (3.3363593) and Saturn (7.8672057) offsets now set SPOT LONGITUDES and
  derived light-minutes, not just real positions. Documented at both ends:
  a caution block in locator.py and a "scope of the provisionals widened"
  paragraph in FRAMEWORK open question 1, with the regeneration duty when
  NU's exact NR values land (expected shift <= 0.02 deg of longitude,
  ~2 km; Ura/Nep unaffected — their offsets are the Mathcad's own digits).
  (2) FRAMEWORK section 1 still carried the v1 prose reading (Jup 40 / Sat
  80 / Ura 150 / Nep 240 at 15 deg/h) -> rewritten to v3 with v1/v2 kept on
  record. (3) FRAMEWORK section 2 still carried "Rule v2 distance-true" ->
  rewritten to v3; NU's Neptune-8000-km tension noted as DISSOLVED under
  v3 (Neptune ground scale ~3,238 km). (4) Repo README still said
  "Distance-true light-times" -> v3. (5) Repo README stale otherwise: test
  count 211 -> 239, and the capability list gained the mirror crossing, the
  angles/site-angle layer (with its retirement), the galactic reference,
  the ASTROC.GRF oracle, and the single-precision environment note.
- No code behavior changed (comment-only in locator.py); 239 tests green.

## 2026-08-05 — Tropical-ceiling figures corrected (second pass, independent re-measurement)
- The 01ea85e per-body table quoted ANALYTIC BOUNDS (obliquity + max|beta|),
  which are only spent when a body's peak latitude falls at a solstitial
  longitude — usually it does not. Achieved extremes, engine-measured
  1900-2030 at 2-day steps: Jupiter +23.52/-23.53 (quoted 24.37), Saturn
  +22.84/-22.82 (quoted 25.62 — Saturn actually stays BELOW the flat
  obliquity this era: near lon 90 it sits short of its ~113 node with
  negative latitude), Uranus +23.71/-23.71 (quoted 24.06), Neptune
  +22.39/-22.36 (quoted 24.20).
- Operative ceiling is the LOCATED SET (four giants, the only bodies with
  light-times): 23.71 deg, beyond which lies 44.4% of the declustered
  post-1900 corpus (637/1435). The "41.8% beyond Saturn's bound" used a
  bound no giant reaches; the original "44%" was right for the right reason.
- MY OWN ERROR, retracted in the same pass: I first reported that Mars
  (28.90) clears Gorkha and that the no-body claim was false. That used
  |dec| — Mars's 28.90 extreme is SOUTHERN. Signed northern maxima: Venus
  +27.82, Mars +27.23, Mercury +25.66. NO body reaches +28.23. The author's
  no-sub-point-at-Gorkha conclusion HOLDS — on a 0.4 deg margin, not the
  4.8 deg a flat-23.44 story implies, and only because Mars's deep extreme
  falls south. Recorded in angles.py so the argument is made on the giants'
  23.71 ceiling rather than on a claim that nothing gets near 28.
- Independently re-verified and CONFIRMED: the canon has no lunar latitude
  series (ASTGRAF.BAS ends the 20-term block at PX = LL + ML, line 311; no
  sin(F) latitude accumulation), and the port is faithful
  (ecliptic_latitude assigned only in the planet loop, Moon defaults 0.0).

## 2026-08-05 — Author's briefing decoded: DWELL TIME solved; the ring reading refuted
- DWELL TIME DECODED (the standing "what is dwell?" question). His numbers are
  all EARTH-ROTATION quantities, not planetary motion: 1 deg = 4 min = 100 km;
  1/81 deg = 1,234 m = 2.96 s (his "3 seconds"). Reading: dwell = the ANGULAR
  SPAN OF THE CROSSING COMPLEX converted at 4 min/deg. Verified at Nepal:
  real-Ura->Sun 0.692 deg (2.77 min) + real-Nep->Ketu 0.342 deg (1.37 min) =
  1.034 deg = 4.14 MINUTES against his stated "dwell time has been 4 minutes -
  because both Uranus and Neptune crossed Ketu position one after another".
  Implication: dwell is a SEVERITY criterion ("above 3 seconds MAJOR SHOCK
  WAVES"), longer span = more crossings in sequence = bigger event — a
  magnitude-correlated, timing-layer claim, testable on the corpus and
  independent of the blocked location layer. NOT yet implemented; proposed as
  the next test (dwell vs magnitude, declustered corpus).
- RING HYPOTHESIS TESTED AND REFUTED. His "scalar pulse, IMMEDIATE, straight
  line to the surface" suggested the affected locus might be the TANGENT RING
  (edge-on incidence = maximum shear) rather than the sub-point (normal
  incidence = compression) — which would also escape the declination cage,
  since a ring at 90 deg from a sub-point reaches +-83 deg latitude. Measured:
  angular distance sub-point -> epicenter, four giants, 1,435 declustered
  events, 18 x 10-deg bins vs 20 shuffled-epicenter nulls. FLAT — every bin
  within ~10% of null; the 90-100 deg tangent bin is 0.997 of null; the only
  bin above 1.05 is 0-10 deg (1.104), the sub-point excess already known at
  ~1.8 sigma. No preferred radius exists. Fourth location family refuted.
- ANALYTICAL POINT ON RECORD: all three corrections the author names
  (rotation, ecliptic tilt, light travel) are LONGITUDE mechanisms; Earth's
  rotation cannot move latitude at all. His construction therefore has three
  longitude sources and exactly one latitude source — declination — which for
  the located set (four giants) caps at 23.71 deg against Nepal's 28.23 N.
  The 1/81 subdivision is a RESOLUTION, not an ORIGIN: it presupposes a zero
  to subdivide from. Both gaps (latitude source, zero-longitude convention)
  remain the blocking inputs.

## 2026-08-05 — Cross-session check: dwell-magnitude finding REPLICATED independently
- Reconstructed the parallel session's dwell-magnitude test from its prose
  description only (not its code), same corpus (1,435 declustered post-1900),
  dwell = sum of real-giant-to-(Sun/Rahu/Ketu) separations x 4 min/deg:
    taught giants orb 1.0: rho +0.342, n 44   (theirs +0.322, n 44)
    taught giants orb 3.0: rho -0.064, n 148  (theirs -0.065, n 148)
    all four      orb 1.0: rho +0.202, n 95   (theirs +0.192, n 95)
    all four      orb 3.0: rho +0.007, n 268  (theirs +0.009, n 268)
    family-wise permutation p = 0.028 (theirs 0.042); single-crossing subset
    n 41 rho +0.344 (theirs +0.315).
  INDEPENDENT REPLICATION CONFIRMED within noise. The computation is real;
  whether the EFFECT is real remains open.
- ADDED CAUTION (not in their report): the surviving cell is the smallest
  (n=44) and the correlation REVERSES at orb 3 (-0.064). An effect present
  only in the tightest cell and sign-flipped when loosened is either
  genuinely threshold-dependent or the classic small-n fluctuation shape.
- DESIGN NOTE for the proposed M6+ held-out test: M6+ CONTAINS M7+, so the
  fit would leak. The held-out set must be strictly M6.0-6.9 (disjoint from
  the M7+ corpus the hypothesis was formed on).
- ARITHMETIC: their rounding catch is right and this session had repeated
  the author's figure uncritically — 1 deg at the equator is 111.319 km, not
  100; equatorial speed 465.1 m/s, not 400; the 1/81 cell is 1,374 m, not
  1,234. All his ground-distance claims run ~11% optimistic.
- STRUCTURAL POINT for FRAMEWORK: (a-1)*500/240 reproduces his PROSE
  rotations (Uranus 37.80 vs 37.5, Neptune 60.27 vs 60 — and (a-1) IS the
  nearest-approach distance he explicitly names), while (a/2-1)*500/240 is
  the Mathcad form validated by the NEPAL CHART as the REAL-POSITION offset.
  These are two different quantities sharing a formula shape; the v3 ruling
  set them equal. The 0-360 rotation sweep shows the choice has no
  predictive consequence, so the ruling stands untouched — but the two
  should be recorded as distinct, not identified.

## 2026-08-05 — FRAMEWORK section 1b added: the clocks (merged cross-session model)
- The synthesized mental model both sessions converged on is now doctrine
  documentation rather than chat: every motion expressed as time-to-cross the
  author's 1/81-degree cell, using the ENGINE's own mean geocentric apparent
  motion 2015-20 (Neptune 14.2 h ... Moon 1.35 min ... Earth rotation 2.95 s).
  Note recorded: geocentric apparent motion INCLUDES retrograde looping, so it
  exceeds net orbital drift (Neptune 0.021 vs 0.006 deg/day) — the apparent
  motion is what the chart plots and what a crossing test sees.
- Section carries: the dwell decode with the Nepal 4.14-min match AND the
  attribution mismatch (his prose says both giants crossed Ketu; the chart
  puts real-Ura on the Sun, 26.5 deg away); dwell as a SEVERITY quantity;
  the 3-second threshold shown vacuous as literally stated; the ~11%
  optimistic ground distances (111.319 km/deg, 465.1 m/s, 1,374 m cell); and
  the three-longitude-mechanisms / one-latitude-mechanism asymmetry with the
  23.71 vs 28.23 gap as the standing question for the author.

## 2026-08-05 — DWELL CLOSED on held-out data; the location/doctrine board is now 5/5 null
- The parallel session ran the decisive test with the disjointness fix this
  session flagged (M6.0-6.99 STRICTLY, not M6+, so the M7+ discovery set
  cannot leak): 12,212 USGS FDSN events -> 10,324 declustered by the same
  7d/500km rule -> 338 with an active taught crossing at orb 1 (7.7x the
  discovery sample). Cell, direction and statistic PRE-REGISTERED.
  RESULT: rho -0.040, p 0.77 — wrong sign in EVERY cut (pooled 6.0-8.5
  -0.053; single-crossing -0.019; halves -0.048/-0.045; 1970+ -0.041).
  Power: injected rho 0.32 recovered 12/12, rho 0.20 in 11/12 — not blind.
  Diagnosis: winner's curse (max of four correlated cells at n=44, sampling
  noise +-0.15). The p=0.042 was real arithmetic on a fake effect — and the
  caution this session filed when replicating it (smallest cell, sign
  reverses at orb 3) is exactly what it turned out to be.
- FRAMEWORK section 1b updated in place: dwell's construction still
  reproduces (Nepal 4.14 min) but BOTH doctrine halves are recorded closed —
  trigger half vacuous (3 s = 1/81 deg, selects nothing; events carry no
  excess dwell, p 0.42), magnitude half dead on held-out data. Author's
  caveat kept: an above-M7-only mechanism would not show in the M6 band, but
  then the M7+ result rests on nothing but its own selection.
- BOARD: five location/doctrine families built and graded — rotation spots,
  Ascendant rules, site-angles, the full 0-360 rotation spectrum, dwell —
  ALL NULL under honest testing, each with a power check proving the
  instrument could see the effect it failed to find. The timing channels
  (anchor dossiers, recurrence fingerprints, family calendars, taught-minute
  reproduction) stand untouched; nothing in the location doctrine survives.
- METHOD RULING (adopt as standing practice): pre-register cell, direction
  and statistic BEFORE running any future lead. It converted this one from
  an argument into a single clean kill.

## 2026-08-05 — PRE-REGISTRATION: the cell-region test (author's own location design)
- COMMITTED BEFORE RUNNING (per the standing method ruling). Script:
  scripts/cell_region.py, whose header carries the full pre-registration.
- WHY THIS FAMILY. Five geometric families are dead (rotation spots,
  Ascendant rules, site-angles, the full 0-360 rotation spectrum, dwell).
  Re-reading the author's briefing against the clocks model shows we were
  building the wrong KIND of thing: Predict.pdf says each matrix point
  "would contain confirmed event synchronisation factors from areas of our
  interest" and calls for an "algorithm to pinpoint areas on Earth ... in
  each category" — a LEARNED TABLE, not a geometric construction. A learned
  region also escapes the declination ceiling structurally, which no
  geometric family can: measured this session, sub-point constructions
  cannot express 44.4% of M7+ latitudes with the four giants, and still
  38.5% even if lunar latitude were restored (the Moon reaches +28.58,
  enough for Gorkha in principle — but its declination at the Nepal instant
  was only +15.94, so even that escape hatch fails on the flagship case).
- Also derived from the clocks model and recorded: a slow-slow crossing
  CANNOT define a meridian (the crossing lasts days; meridians sweep 360
  deg/day), so geometric longitude can only come from a fast body — and
  every fast-body channel is already tested and null. The geometric route
  is exhausted; the empirical one is untouched.
- DESIGN (fixed in advance): corpus = the same 1,435 declustered post-1900
  M7+ mainshocks, M7+ ONLY per NU's ruling; cell = (body, band) at level 0
  (Predict.pdf's own 28 divisions), 11 bodies x 28 bands, each event firing
  11 cells; statistic = spherical resultant length R of a cell's epicenters
  (higher = more concentrated); qualifying cells n >= 15 fixed in advance;
  family statistic = max R over qualifying cells; null = shuffle EPICENTERS
  across events holding band-vectors fixed (preserves the catalog's real
  geography and all cell sizes, destroys only the sky-to-place pairing),
  500 shuffles, seed 42; direction predicted = real R HIGHER than null;
  verdict p < 0.05. A power check plants a known region preference so a
  null cannot be mistaken for blindness.
- PRIOR STATED IN ADVANCE: low. Same corpus that has refused five families
  and three mining passes. What justifies one clean shot: it is the
  author's own stated design, it escapes the latitude cage structurally,
  and a hit would be operationally useful (a ranked region shortlist is
  what his stated purpose — logistics planning — actually needs).

## 2026-08-05 — Cell-region test RESULT: null (p = 0.166), instrument verified
- Ran the pre-registered test (design committed first at ac88628, untouched).
  1,435 declustered M7+ mainshocks; 302 cells reached the n>=15 bar.
  Observed max R 0.6993 (Mars band 22, n=38); null max median 0.6624, 95th
  0.7424; p = 0.166 over 500 epicenter shuffles. NULL — the author's
  empirical cell-region design does not beat chance on M7+.
- POWER: the first arm as written was BROKEN (it reported the family max,
  which a planted cell never became — identical 0.7392 at both 50% and 30%
  plants gave it away). Rebuilt to measure the planted cell directly
  against a same-size null: a 30% plant lifts the cell to R 0.777
  (p = 0.000, and above the family null's 95th of 0.742), 50% to 0.878,
  100% to 0.998. The instrument CAN see a region preference of the size
  claimed; it is not blind. Verdict therefore stands as a refutation, not
  an inconclusive.
- Worth recording: Mars band 22 alone would read p = 0.002 against a
  same-size null — and is exactly what the family-wise correction exists to
  discount at 302 cells. Same shape as the dwell winner's curse; caught by
  design this time rather than after a held-out test.
- LOCATION BOARD NOW SIX FAMILIES, ALL NULL: rotation spots, Ascendant
  rules, site-angles, the full 0-360 rotation spectrum, the tangent ring,
  and the cell-region table. Recorded as a table in FRAMEWORK with the
  derivation of why the geometric route is exhausted (slow-slow crossings
  cannot define a meridian; latitude has one source and it is capped).

## 2026-08-05 — Documentation pass: PLAN.md created, FRAMEWORK completed
- NU: "document well your visualization and other updates from this
  session, also the plan, and framework."
- FRAMEWORK.md now carries the full picture: section 1b (the clocks model —
  every motion as time-to-cross the 1/81 cell, measured from the engine's
  own mean geocentric apparent motion; the dwell decode AND its closure;
  the ~11% optimistic ground distances; the three-longitude/one-latitude
  asymmetry) and the completed six-family location board with power-check
  notes and the exhaustion argument.
- PLAN.md CREATED (new document, referenced from the doc map): the one-line
  state, what works with the reproduced-instant table, what is closed
  (location / mining / dwell), the five standing METHOD RULINGS
  (pre-register before running; every null needs a power check; replication
  is not confirmation; held-out sets must be strictly disjoint; honest
  negatives stay on record), the three next actions buildable without new
  input, the ranked list of what is blocked on NU, and the standing
  latitude question.

## 2026-08-05 — Recurrence gaps CLOSED: category tagging + composite matching
- NU directed both remaining recurrence gaps. Built test-first in the modern
  layer (no canon touched); 245 tests passing.
- CATEGORY (Predict.pdf's design is explicitly per category): astgraf-recur
  gains --category (earthquake | flood | biological | volcanic |
  configuration) with a guarded unknown-category exit listing the known set;
  every calendar row (csv/json) now carries the anchor's category.
- COMPOSITE (the last unbuilt recurrence gap): composite_conditions() reads
  the anchor's OTHER layers at its instant — Moon/Ketu/Mars spread, band
  stack_max, vyuha level — and composite_match_at() requires them to stand
  again: vyuha level EXACT (categorical), spread at least as tight, stack at
  least as high. find_episodes(anchor=...) applies it, so a composite episode
  set is always a subset of the contact-only set. Demonstrated: the June 2016
  vyuham window narrows from June 3-4 to June 3 alone.
- BUG FOUND AND FIXED BY THE SELF-MATCH TEST: composite_conditions stored a
  ROUNDED mkm_spread, so every anchor failed its OWN composite test by
  ~0.00025 deg (rounded threshold below the live value). Now stored
  unrounded, rounded at display only; regression test asserts self-match for
  four anchors. A second failure was the TEST's fault, not the code's — the
  subset assertion did not allow the tightest instant to sit one scan step
  outside the sampled bounds (the documented sub-day-window tolerance).
- The recurrence principle is now fully built: anchor dossiers -> similarity
  engine -> recurrence calendars -> family calendars -> category tagging ->
  composite matching. All of it timing-only, on the proven core.

## 2026-08-05 — FLOOD CORPUS created (NU input) + NR ruling
- NU RULING: exact Sankhya NR for Jupiter/Saturn is NOT needed for now — the
  current provisional canon-axis values (3.3363593021 / 7.8672056771) are
  good enough and stand. Open question 1 is parked, not blocking.
- NU supplied the compiled flood record. Built data/floods-historical.csv:
  88 events, columns id/time/date_precision/latitude/longitude/loc_precision/
  place/cause/deaths/tier/notes, spanning paleo (Zanclean, Missoula, Altai,
  Agassiz) through ancient/medieval/early-modern/modern/contemporary.
  data/README-floods.md documents it.
- THE USABILITY ANALYSIS IS THE POINT (measured, not assumed): an event is
  usable for a 3-deg contact test only if its date pins the acting body
  inside the orb. Body drift: Neptune 0.63 deg/month, Uranus 0.96, nodes
  1.59, Saturn 2.07, Jupiter 3.93, Sun 29.6, Moon 395. So DAY precision =
  every body but the Moon; MONTH precision = Uranus/Neptune/nodes only
  (which IS the taught flood signature); YEAR or coarser = nothing at 3 deg.
  Second cut: the engine drifts to degrees-level by the 1600s, so
  well-dated pre-1700 events are NOT rescued by their dates.
  COUNTS: 88 total; 40 day, 13 month, 35 year-or-coarser; CHART-USABLE
  (day/month AND >= 1700) = 39, of which 26 full-contact and 13
  slow-layer-only; 14 well-dated but pre-1700.
- HONESTY RECORDED IN THE README: feast-day dating is inference (Grote
  Mandrenke, St Lucia's, St Elizabeth's, All Saints', St Felix's,
  Magdalenen, Christmas flood are dated from the saint's day they are NAMED
  for — standard historical method, but derived); pre-1582 rows are Julian
  as recorded with no conversion applied; loc_precision region = basin
  centroid, NOT an epicenter; paleo rows carry nominal instants only; the
  corpus is NOT declustered and has NO completeness model (reporting density
  rises steeply with time and toward Europe/China) — any test must control
  for that as the quake corpus needed declustering + climatology controls.
- Invariant test added (246 passing): ids unique, precision/loc enums valid,
  coordinates in range, the taught Hyderabad row agrees with anchors.toml,
  and the chart-usable subset stays >= 30.
- UNBLOCKS: the Uranus-Neptune long-cycle clock test (163.5/164.5/171.0),
  the site channel's OWN category (never corpus-tested), and
  astgraf-recur --category flood.

## 2026-08-05 — HANZE Europe imported: the flood corpus goes from 88 to 2,812
- NU: "can you scrape more using the sources i gave". firecrawl is EXHAUSTED
  (-1/1,000 credits), but the Zenodo REST API answers curl directly.
- SOURCE: Zenodo record 20478847, "HANZE database of historical flood
  impacts in Europe, 1870-2025", CC-BY-4.0, file HANZE_events_v3_0_1b.csv.
  Downloaded and converted into the project schema as
  data/floods-hanze-europe.csv — 2,724 events, 1871-2025, 40 countries,
  **100% full YYYY-MM-DD start dates** (so every acting body except the Moon
  sits inside a 3-deg orb), 2,699 rows carrying fatality counts, types flash
  1,318 / river 1,259 / coastal 102 / compound 45.
- LOCATION LIMIT RECORDED HONESTLY: HANZE stores NUTS-3 region codes and its
  region file (S2) carries NO centroids — only Code,Name. So latitude/
  longitude are COUNTRY CENTROIDS and loc_precision is "country": useless
  for a point-location test, adequate for the tests this corpus actually
  unblocks (long-cycle clocks, category recurrence, contact timing), which
  need dates not places. The original NUTS-3 list is preserved in `place`
  so finer geocoding can be added later.
- DFO Global Active Archive NOT obtained: its archive URLs
  (floodobservatory.colorado.edu/Archives/...) return HTTP 410 Gone as of
  2026-08-05. Recorded in the README so nobody re-tries it blind. DFO is
  the source that DOES publish centroids, so if a mirror is found the
  location weakness above is fixable.
- Schema interoperability enforced by test (247 passing): identical column
  order to floods-historical.csv, unique ids, all-day precision, all-country
  loc_precision, year range 1870-2026.

## 2026-08-05 — PLAN.md rewritten as the authoritative open-work document
- NU: "document well what still needs to be done." PLAN.md had gone stale
  within hours (its P2/P3 next-actions were built; its top two blocked
  inputs were resolved). Rewritten from measurements, not intentions:
  * Section 2 CLOSED — the seven graded channels in one table with verdicts,
    plus the derivation that the geometric location route is EXHAUSTED
    rather than merely untested.
  * Section 3 RUNNABLE NOW (what the flood corpora opened): four
    pre-registration candidates with available n MEASURED —
    (3.1) long-cycle clock test: 2,757 dated events since 1871, 326 in the
    1988-98 conjunction window, with the honest limit stated up front that a
    155-year record is LESS THAN ONE CYCLE of any candidate clock, so the
    test can rule one OUT but cannot confirm one; and the warning that the
    null must be built first because flood reporting density rises steeply
    with time and toward Europe. (3.2) the taught Neptune-on-Ketu signature
    tested in its OWN category for the first time, n=2,750 day-precision —
    every prior grading used the quake corpus. (3.3) category-tagged
    recurrence grading. (3.4) site channel in its own category, flagged
    UNDERPOWERED at n=13 (only 13 events are day-precision AND modern AND
    point/city located).
  * Section 4 ENGINEERING DEBTS, seven, each with impact and fix — including
    one measured today: 21 TESTS FAIL WHEN RUN FROM THE REPO ROOT because
    trigger/CLI tests open doctrine-triggers.toml relative to cwd (the suite
    is only green from tools/astgraf); HANZE's country-centroid limit; the
    undeclustered flood corpora with no completeness model; the canon's
    missing lunar latitude; the parked provisional Jup/Sat offsets;
    unconverted pre-1582 Julian dates; exhausted firecrawl credits.
  * Section 5 BLOCKED ON NU, re-ranked now that the flood records and the NR
    values are resolved — THE LATITUDE QUESTION TO THE AUTHOR IS NOW #1.
  * Sections 6-7: the autumn season table with its base-rate warning, and
    the six standing method rulings.

## 2026-08-05 — Engineering debt 1 CLOSED: rule files resolve from any cwd
- 21 tests failed when the suite ran from the repo root: 18 from rule TOMLs
  opened by BARE NAME (doctrine/mined/observed-triggers.toml) and 3 from a
  cwd-relative "../../canon/ASTROC.GRF" in test_grf.py.
- FIX (test-first): triggers._resolve_rules_path falls back to the package
  root for a bare filename, leaving explicit and absolute paths untouched so
  typos still raise FileNotFoundError loudly (asserted). test_grf.py now
  resolves the canon path from __file__ instead of cwd. Bonus: astgraf-bands
  --rules doctrine-triggers.toml now works from any directory too, which is
  what a user would expect.
- VERIFIED BOTH WAYS: 248 passed from tools/astgraf AND 248 passed from the
  repo root (exit 0 each). The debt is closed, not merely mitigated.

## 2026-08-05 — PRE-REGISTRATION: the taught flood signature in its own category
- COMMITTED BEFORE RUNNING. Script scripts/flood_signature.py carries the
  full design in its header.
- WHY: every doctrine grading to date used the QUAKE corpus. "Giant on a
  node — Neptune on Ketu" is taught as a FLOOD constraint (Hyderabad 1.15
  observed, Nepal 0.34 real). The flood corpora built today make it testable
  in the category it was TAUGHT IN for the first time.
- HYPOTHESIS: flood dates carry Neptune-on-Ketu more often than era-matched
  instants. DIRECTION: lift > 1.
- CORPUS: both flood files, date_precision == day AND year >= 1700 (day
  precision puts every body but the Moon inside 3 deg; the engine drifts to
  degrees by ~1600). n = 2,750 raw -> 1,886 after 3-DAY TEMPORAL
  declustering (temporal only: HANZE locations are country centroids, so
  spatial declustering is meaningless and one European episode otherwise
  appears as several country rows on adjacent days).
- CONTROLS — the load-bearing choice, measured first: flood reporting
  density rises ~12x across the span (36 events/decade in the 1870s to 447
  in the 2000s), so UNIFORM controls would hand any era-locked slow-body
  predicate a trivial win (this is exactly the artifact that once promoted
  sep:Uranus-Neptune@opp to lift 55). Controls are ERA-MATCHED: 5 instants
  per event drawn uniformly from +-365 d, excluding +-7 d. Era, reporting
  regime and slow-body epoch are all held fixed while the Neptune-Ketu
  separation still sweeps ~27 deg/year against a 3 deg orb.
- PRIMARY: real:Neptune conj Ketu, orb 3.0, one predicate. STATISTIC:
  add-one smoothed lift. VERDICT: within-block permutation (which of the
  1 event + 5 controls is labelled the event), 2,000 shuffles, p < 0.05 AND
  lift > 1 supports the doctrine.
- SECONDARY (reported, NOT the verdict, with their own family-wise p):
  observed Neptune-Ketu; real-Neptune-Rahu; real-Uranus-Ketu/Rahu; and the
  primary at orb 1.0.
- POWER CHECK in the same script: plant the predicate into 10/5/2% of events
  and confirm recovery, so a null cannot be mistaken for blindness.

## 2026-08-05 — FLOOD SIGNATURE RESULT: null (lift 1.012, p = 0.57)
- Ran the pre-registered test (design committed first at 997484d, untouched).
  1,886 declustered day-precision flood events >= 1700, 9,430 era-matched
  controls (+-1 y, excluding +-7 d).
- PRIMARY real-Neptune conj Ketu @ 3 deg: events 30/1886 = 0.0159, controls
  152/9430 = 0.0161, LIFT 1.012 — null median 1.012, 95th 1.344, p = 0.5685.
  Dead on the null median. The taught flood constraint does not distinguish
  flood dates from ordinary instants in the same era.
- SECONDARY (reported, not the verdict): observed Neptune-Ketu 1.186;
  real-Nep-Rahu 0.859; real-Ura-Ketu 0.915; real-Ura-Rahu 1.353;
  real-Nep-Ketu @ orb 1 = 1.303. Family max 1.353, family-wise p = 0.382 —
  nothing survives multiplicity.
- POWER: planting the predicate into just 2% of events yields lift 2.220 at
  p = 0.0000 (5% -> 4.08, 10% -> 7.15). The instrument would detect an
  effect a fraction of the claimed size; it is not blind. Verdict is a
  refutation, not an inconclusive.
- SIGNIFICANCE: this was the FIRST test of a taught doctrine rule in the
  category it was TAUGHT IN — every prior grading used the quake corpus, so
  "wrong catalogue" was a live excuse. It is now spent. The Hyderabad
  reading remains exact as a retrodiction (Neptune on Ketu 1.15 deg), but
  the rule generalises to 1,886 flood events at exactly chance.
- Running count: SEVEN graded channels, seven nulls, each power-checked.

## 2026-08-05 — PRE-REGISTRATION: Predict.pdf's headline band rule, properly powered
- COMMITTED BEFORE RUNNING. Script scripts/band_trigger_grade.py.
- WHY: this is the AUTHOR'S OWN primary predictive claim ("if Moon, Knode and
  Mars ... is in Aswin 0-12.8 deg band we can anticipate a disruptive event.
  If Uranus and Neptune too is present there can be catastrophic events").
  It has been scored exactly ONCE, against a 31-episode disaster spreadsheet
  (grid 0/31 vs 0.63 expected; proximity 1/31 vs 1.79) — far too small to
  detect anything short of an enormous effect. We now hold ~3,300 events.
- PRIMARY CORPUS = QUAKES, and the reason is registered: the rule contains
  the MOON, which moves 13.2 deg/day = ONE FULL BAND SPAN per day, so only
  exact instants can test it. 1,435 declustered M7+ with catalog instants.
- SECONDARY = FLOODS (1,886), reported but NOT the verdict: their times are
  nominal 12:00 UTC, leaving the Moon +-6.6 deg uncertain (half a band).
  That caveat is IN the registration, not added afterwards.
- PREDICATES: P1 PRIMARY proximity (trio circular spread <= 12.857 deg,
  grid-free per NU's ruling that fixed cells quantize away real
  convergences); P2 grid (all three in one division); P3 escalated (P1 plus a
  giant within one band span of any trio member — the "catastrophic" form).
  Only P1 carries the verdict.
- CONTROLS: era-matched, 5 per event, +-365 d excluding +-7 d — the design
  validated on the flood-signature test. Holds catalogue completeness fixed
  (quake detection improves sharply post-1960; flood reporting rises ~12x)
  while the Moon sweeps the zodiac many times inside the window.
- STATISTIC add-one smoothed lift; VERDICT within-block permutation, 2,000
  shuffles, p < 0.05 AND lift > 1. Power check plants into 10/5/2%.

## 2026-08-05 — BAND-TRIGGER RESULT: does NOT clear the pre-registered bar (p = 0.069)
- Ran the pre-registered grading (design committed first, untouched).
- PRIMARY, quakes, exact instants, 1,435 events / 7,175 era-matched controls:
    P1 proximity  ev 12/1435 = 0.0084, ctl 0.0049, LIFT 1.804,
                  null median 1.124, p = 0.0690  -> FAILS the p<0.05 rule
    P2 grid       ev 3/1435, lift 2.220, p = 0.259
    P3 escalated  ev 3/1435, lift 2.220, p = 0.264
- SECONDARY, floods (indicative only, Moon +-6.6 deg): P1 lift 0.937,
  p = 0.741 — pointing the OTHER way. P2 0.666. P3 2.997 at p = 0.262 on 2
  events (noise).
- POWER: planting 2% of events gives lift 5.69 at p = 0.0000, so the
  instrument is not blind — but note that a 2% plant is ~29 events on top of
  12, far larger than anything observed.
- WHY THIS IS NOT A NEAR-MISS TO GET EXCITED ABOUT (measured, not asserted):
  the whole result rests on TWELVE firings against ~7.0 expected. The excess
  is 5 events = 1.4 Poisson sd. The predicate is simply RARE (fires on 0.84%
  of events), which is why n=1,435 still yields single digits. Projected:
  if the 1.80 lift were real, n=3,000 gives ~2.3 sd, n=6,000 ~3.2 sd,
  n=12,000 ~4.6 sd. So this is decidable — but only with a corpus 4-8x
  larger, e.g. M6+ quakes (which we already know how to fetch: 12,212 rows
  came down from USGS FDSN for the dwell test).
- VERDICT AS REGISTERED: null. Recorded honestly as the closest any primary
  predicate has come in this project, and as the FIRST properly powered test
  of Predict.pdf's own headline claim (previous scoring: 31 episodes).
  Ninth graded channel; ninth failure to clear its bar.

## 2026-08-05 — RESULTS.md created: the evidence ledger
- NU: "document well." The gap: the chronological ledger is 1,500+ lines,
  FRAMEWORK is theory, PLAN is forward-looking — nothing recorded EVERY test
  and what it found in one place, so positive and negative could be quoted
  separately. RESULTS.md fixes that in five parts:
  * Part 1 WHAT REPRODUCES — the 12-row retrodiction table (Hyderabad
    04:50/17:06 and the 15:29-19:24 Moon squares, Ulsoor 06:12/08:21 with the
    sweep order, Nepal 0.692/0.342, the QUAKE page, the docx 13/13, the Java
    members, the vyuha census) plus the 130-year sweep's zero false
    positives — and the matching statement that zero trials means skill is
    UNDEMONSTRATED, not demonstrated.
  * Part 2 WHAT FAILED — all ten graded channels in one table with design,
    result and POWER CHECK per row; and the note that channels 8/9/10 each
    closed a standing excuse (never held-out; wrong catalogue; only 31
    episodes). #10 flagged as the only one merely UNDERPOWERED rather than
    refuted, with its sigma projections.
  * Part 3 STRUCTURAL RESULTS — the declination ceiling with measured
    achieved extremes, the canon's missing lunar latitude, the
    slow-slow-cannot-define-a-meridian derivation, three-longitude/
    one-latitude, 1/81 is a resolution not an origin, the ~11% optimistic
    ground distances.
  * Part 4 REGISTERED NOT YET RESOLVED — the autumn season with its base-rate
    warning.
  * Part 5 HOW THESE WERE PRODUCED — the six method rulings, each tied to the
    specific mistake that earned it, including the git-verifiable
    pre-registration timestamps.
- Wired in: FRAMEWORK section 3 now points at RESULTS.md and its stale
  31-episode band scoring is marked SUPERSEDED by the 2026-08-05 regrade;
  FRAMEWORK document map, PLAN header, and the repo README tree all list it;
  repo README's epistemic contract gained the ten-channel summary; test
  counts trued to 248.

## 2026-08-05 — Historical QUAKE corpus created + pre-registered deaths-selected test
- NU supplied a curated earthquake compilation (NCEI/WDS, ISC-GEM, USGS,
  GEM GHEA). Saved as data/quakes-historical.csv in the SAME schema as the
  two flood corpora: 39 events, three tiers — pre-instrumental 12 (856 CE
  Damghan through 1833 Sumatra), largest 15 (Mw >= 8.4, 1906-2012),
  deadliest 12 (1908 Messina through 2023 Turkey-Syria).
- USABILITY (measured): 20 minute-precision, 18 day, 1 month; 32 chart-usable
  (minute/day AND >= 1700); 7 pre-1700 disqualified by engine drift; 23 carry
  death tolls. Includes the 1556 Shaanxi event (~830,000 deaths, deadliest on
  record) and 2023 Turkey-Syria, both outside the pinned USGS corpus which
  ends 2020.
- WHAT IT ADDS that the pinned corpus cannot: a DEATHS-SELECTED tier. USGS
  M7+ is MAGNITUDE-selected, so Tangshan (Mw 7.5, ~300,000 dead) and Haiti
  (Mw 7.0, ~200,000 dead) are minor by its criterion and enormous by
  consequence. The M9 shared-structure test could not see them.
- PRE-REGISTERED TEST (committed before running): scripts/deadliest_structure.py
  — do deaths-selected events share fired-contact structure more than
  same-size samples of magnitude-selected ones? Statistic: mean pairwise
  Jaccard similarity of contact sets, Moon pairs EXCLUDED throughout (day
  rows cannot place the Moon), registered in advance. Null: 2,000 random
  12-event samples from the 1,435 declustered M7+ corpus, seed 42.
  POWER WARNING REGISTERED IN ADVANCE: n = 12 gives 66 pairs; a null means
  "no effect large enough for 12 events to reveal", never "no effect", and a
  positive would need replication on NCEI's >5,700 deaths-selected events
  before meaning anything — the dwell finding died exactly this way at n=44.

## 2026-08-05 — DEATHS-SELECTED STRUCTURE RESULT: null (p = 0.34), and honestly underpowered
- Ran the pre-registered test (design committed first, untouched).
  12 deaths-selected events, 66 pairs: mean pairwise Jaccard similarity of
  fired-contact sets = 0.0159. Null (2,000 random 12-event samples from the
  1,435 magnitude-selected declustered corpus): median 0.0139, 95th 0.0229.
  p = 0.3435 — NULL. The deadliest earthquakes do not share configuration
  structure more than magnitude-selected ones.
- POWER, as registered: the statistic works — the tightest 12-event window in
  the corpus (95 days, so the slow bodies are near-identical by construction)
  scores 0.1514 at p = 0.0000, roughly TEN TIMES the observed value. So the
  instrument sees structure when structure exists.
- BUT THE REGISTERED POWER WARNING STANDS AND IS THE HEADLINE: n = 12. This
  null means "no effect large enough for 12 events to reveal", NOT "no
  effect". Recorded as UNDERPOWERED-NULL, not as a refutation — the honest
  distinction the dwell episode taught. NCEI/WDS holds >5,700 deaths/damage
  -selected events; importing it would make this a real test.
- Corpus documented in data/README-floods.md (retitled "The event corpora",
  now covering all four files and why a curated quake file exists alongside
  the pinned magnitude-selected one). Invariant test added: schema identical
  to the flood files, unique ids, tier enum, coordinate ranges, and agreement
  with anchors.toml coordinates where the same event appears in both.
  249 tests passing.

## 2026-08-05 — NCEI/WDS imported: the deaths-selected test becomes POWERED, and is null
- Firecrawl is exhausted, but NOAA's hazard-service REST API answers curl:
  https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/earthquakes
  Paging capped at itemsPerPage=200 (500/1000 return HTTP 400). The payload
  omits deaths, BUT minDeaths filters SERVER-SIDE — so graded queries at
  1/10/100/1000/10000/100000 reconstruct death BRACKETS by set difference.
  Counts 1700-2025: 1,999 / 1,098 / 563 / 250 / 72 / 5.
- data/quakes-ncei-deaths.csv: 1,981 rows in the shared schema, span
  1702-2025, 1,688 minute-precision + 293 day, brackets >=1 (898), >=10
  (532), >=100 (307), >=1,000 (175), >=10,000 (64), >=100,000 (5).
- THE TEST IS NOW POWERED. Same statistic, same null, same seed as the n=12
  pre-registration — only n changes:
    >=100,000 deaths  n=5    similarity 0.0071  null median 0.0121  p = 0.68
    >= 10,000 deaths  n=63   similarity 0.0130  null median 0.0142  p = 0.86
    >=  1,000 deaths  n=175  similarity 0.0138  null median 0.0142  p = 0.80
  Every bracket sits AT OR BELOW its null. Deaths-selected earthquakes share
  no more configuration structure than magnitude-selected ones — and at
  n=175 this is a real verdict, not the n=12 gesture. The underpowered-null
  from earlier today is now UPGRADED TO A REFUTATION for the >=1,000 bracket.
- Note the direction: all three observed values are BELOW their null medians,
  the same pattern the held-out dwell test showed. Nothing to salvage.
- ELEVENTH graded channel; eleventh failure. Invariant test added (250
  passing): schema identical to the curated files, unique ids, precision and
  bracket formats, year range.
