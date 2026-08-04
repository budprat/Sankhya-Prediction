# Forecast Watch-List — registered 2026-08-02

Outcome grading is automated: `uv run astgraf-outcomes --episodes
out/mined-forward/rules_episodes.csv` fills the quake channel objectively
after each window passes (run 2026-08-02: 9/9 pending).

Falsifiable forward windows from the trigger rules, each with its exact-aspect
instant (refined to the minute) and located spot. Protocol per Predict.pdf:
after each window passes, do the assiduous search of event records, log the
outcome here, and update the rule's standing. Mined rules are candidates
(split-half replicated, below formal significance); doctrine rules are NU's.
A ±1 h timing uncertainty moves a spot ±15° in longitude — names mark the
center of a watch region. Regenerate any row:
`uv run astgraf-bands --start ... --rules mined-triggers.toml` (spots are in
`rules_episodes.csv`).

## Mined: real-Neptune ☍ Mercury (lift 1.76/1.41) — Neptune spots

| Exact instant (UT) | Spot | Region | Outcome |
|---|---|---|---|
| 2026-10-02 04:43 | 138.32W 0.05S | equatorial Pacific N of the Marquesas | *pending* |
| 2027-10-04 20:15 | 11.61W 0.80N | equatorial Atlantic ~700 km S of Liberia | *pending* |
| 2027-11-12 12:07 | 70.84E 0.44N | central Indian Ocean W of the Maldives | *pending* |
| 2028-11-06 06:09 | 168.16E 1.35N | W Pacific ~120 km E of Nauru | *pending* |

## Mined: real-Uranus △ Sun (lift 1.52/1.31) — Uranus spots

| Exact instant (UT) | Spot | Region | Outcome |
|---|---|---|---|
| 2026-10-16 09:19 | 140.33W 21.01N | NE Pacific ~1,900 km E of Hawaii | *pending* |
| 2027-02-08 13:16 | 42.20E 20.37N | SW Saudi Arabia (Asir, toward the Red Sea) | *pending* |
| 2027-10-20 21:47 | 33.07E 21.77N | Nubian Desert, Egypt–Sudan border (Lake Nasser E) | *pending* |
| 2028-02-12 23:36 | 112.35W 21.22N | Pacific off Baja California Sur (Revillagigedo) | *pending* |
| 2028-10-24 10:43 | 160.46W 22.41N | ~170 km SW of Kauai, Hawaii | *pending* |

## Mined: real-Uranus ☌ Saturn (strongest, lift 1.80/1.64)

No windows through 2028 — the conjunction does not form in this span.

## Doctrine: band trigger (Moon+Ketu+Mars) — tightest instants

No doctrinal light-time exists for the trigger trio, so no acting spot is
derivable; giant spots at the tightest instant are secondary information only.

| Tightest instant (UT) | Spread | Named giant spots | Outcome |
|---|---|---|---|
| 2026-11-03 01:00 | 6.3° | Jup: Andhra coast nr Nellore, India; Sat: upper Rio Negro, Colombia–Brazil | *pending* |
| 2026-11-30 05:00 | 7.1° | Jup: central Mali (Ségou) | *pending* |
| 2027-02-20 20:00 | 10.2° | Jup: western Yemen; Ura: NE of Punta Cana, Dom. Rep. | *pending* |
| 2027-03-19 16:00 | 3.2° | Jup: Konkan coast nr Ratnagiri, India; Sat: Gran Sabana, Venezuela | *pending* |
| 2027-04-15 15:00 | 4.8° | Jup: Arabian Sea off Dhofar, Oman; Sat: Colombian Llanos | *pending* |
| 2028-08-17 23:00 | 2.7° | Ura: Chhattisgarh nr Korba, India; Nep: Gulf of Guinea S of Ghana | *pending* |

## Doctrine: Chatur Vyuham, Neptune-on-Ketu, Nepal-double

No windows through 2028 (consistent with the vyuha's once-in-126-years census).

## Doctrine: nodes-doubly-occupied (added 2026-08-02)

The Hyderabad pattern (Mercury on Rahu + Neptune on Ketu): both node ends
held by planets (Moon excluded — it is the fast hand). Census 1900–2026:
64 episodes (~one cluster every two years). Forward: an unusually
persistent cluster — **Jupiter holds Ketu through Jan–Mar 2027** while
Mercury, the Sun, then Venus successively hold Rahu:

| Window (UT) | Rahu held by | Ketu held by | Outcome |
|---|---|---|---|
| 2027-01-24 → 01-28 | Mercury (0.6°) | Jupiter (2.6°) | *pending* |
| 2027-02-06 → 02-13 | Sun (0.2°) | Jupiter (1.5°) | *pending* |
| 2027-02-24 → 03-10 | Mercury (1.3°) | Jupiter (0.07°) | *pending* |
| 2027-03-14 → 03-20 | Venus (0.5°) | Jupiter + Mars | *pending* |

Dated trigger instants of the cluster (fast-layer crossings of the held
axis), with the acting holder Jupiter located at each — all spots fall in
Jupiter's 15–16.5°N declination band:

| Instant (UT) | Trigger | Jupiter spot | Region | Outcome |
|---|---|---|---|---|
| 2027-02-06 22:28 | **Moon on Rahu, Sun 3° away — the annular solar eclipse at the held node** | 22.44E 14.96N | eastern Chad (Ouaddaï, toward Sudan border) | *pending* |
| 2027-02-09 17:31 | Sun exact on Rahu | 93.58E 15.08N | Andaman Sea off Myanmar's Irrawaddy delta | *pending* |
| 2027-02-20 04:03 | Moon on the Ketu–Jupiter end | 76.08W 15.54N | Caribbean S of Haiti / N of Guajira | *pending* |
| 2027-03-02 07:31 | **Jupiter exactly on Ketu — constraint peak** | 139.39W 15.94N | NE Pacific ~1,700 km ESE of Hawaii | *pending* |
| 2027-03-06 02:35 | Moon on the Rahu end | 69.60W 16.08N | Caribbean N of Curaçao (Beata Ridge) | *pending* |
| 2027-03-19 10:54 | Moon on the Ketu–Jupiter end | 151.03E 16.45N | W Pacific NE of Guam (Marianas) | *pending* |

Note the February corridor: this table's Chad spot (22E 15N), the
band-trigger's western-Yemen spot (43E 15.6N, Feb 20), and the
real-Uranus△Sun SW-Saudi spot (42E 20.4N, Feb 8) place three independent
February instants in the Sahel–Red Sea–Arabia belt at 15–20°N.

During these windows the site-specific companion rule
`nodes-held-ascendant-cross` gives DAILY local trigger hours at any chosen
site (the Asc crossing each held axis end, ~40 min per end per day):
`astgraf-bands --rules doctrine-triggers.toml --site-lon ... --site-lat ...
--step-hours 0.25 --start 2027-01-24 --days 56`.

## Doctrine: nepal-double census note (added 2026-08-02)

The real-Neptune-on-Ketu + real-Uranus-on-Sun signature fired **four times
in 126 years — 1915-02, 1948-07, 1981-12, and 2015-04-24→27, the window
containing the Nepal earthquake** (the rule was derived from that chart, so
the 2015 firing is by construction; the ~33-year spacing 1915/1948/1981/2015
is the discovery). Next occurrence beyond 2028.

## Doctrine: uranus-neptune-combo-on-ascendant (added 2026-08-02)

Site-specific daily trigger, not a calendar window: at any chosen site the
Ascendant crosses the Uranus–Neptune arc for ~2.6 h every day while the
giants stay within 45° of each other (true through the 2010s–2030s).
Meaningful in combination with standing constraints (eclipse-loaded nodes
at Ulsoor). Sweep any site with
`astgraf-bands --rules doctrine-triggers.toml --site-lon ... --site-lat ...
--step-hours 0.5`. No rows registered here — the rule selects hours at a
place, not dates on a calendar.

## Doctrine: long-cycle families (added 2026-08-02)

- **Uranus–Neptune conjunction** (flood-catastrophe family): engine census
  1600–2030 shows conjunction clusters every **~171 years** (the Ura–Nep
  synodic; engine 171.0, modern 171.4) — 1649–52, 1820–23, 1991–94
  (Abhijit/Uthrashada). Next cluster **~2165** (DE440: 2165-01). The 167.6
  figure previously here was the doubled-Uranus/"168-year Neptune" convention
  (engine 2×83.85 = 167.7), not the conjunction recurrence. Candidate clocks
  for NU's ~163-y flood records (list awaited): Neptune TROPICAL return
  163.5 y, Neptune sidereal return 164.5 y, Ura–Nep conjunction 171.0 y.
  No forward window in this register's span on any of the three.
- **Jupiter–Saturn conjunction** (Java/tsunami-volcanic family): ~19–20 y
  rhythm; the doctrine's ~120-year episode is concrete in the census —
  **1881 conjunction in Aswini → Krakatoa 1883; 2000 conjunction in
  Kritika → 2004 Sumatra tsunami** (both conjunctions in the Aswini–Kritika
  sector, both followed by Indonesian mega-events within 2–4 years). Last:
  2020-12-21 (Uthrashada — outside the family sector, as is 2040's). The
  family period is ~119 y (1881 → 2000), so the next Java-family return is
  ~2119 — far outside this register's span.

## Amendment 2026-08-02 — locator rule v2 (distance-true light-times)

The location rule now uses the planet's actual distance at the instant
(NU: "these figures are for the nearest position"), replacing fixed minutes.
Registered spots shift ≤ ~1.6° longitude; v2 values (authoritative,
regenerable from `rules_episodes.csv`):

| Instant (UT) | v2 spot | v1 spot |
|---|---|---|
| 2026-10-02 04:43 | 138.32W 0.05S | 138.71W |
| 2027-10-04 20:15 | 11.61W 0.80N | 11.50W |
| 2027-11-12 12:07 | 70.84E 0.44N | 73.31E |
| 2028-11-06 06:09 | 168.16E 1.35N | 167.18E |
| 2026-10-16 09:19 | 140.33W 21.01N | 138.80W |
| 2027-02-08 13:16 | 42.20E 20.37N | 44.71E |
| 2027-10-20 21:47 | 33.07E 21.77N | 34.40E |
| 2028-02-12 23:36 | 112.35W 21.22N | 109.89W |
| 2028-10-24 10:43 | 160.46W 22.41N | 159.28W |

Region names hold at this scale except: 2027-02-08 moves ~260 km west
(SW Saudi Arabia toward the Asir highlands); 2027-11-12 moves ~275 km west
(still the central Indian Ocean west of the Maldives chain); 2028-10-24
moves ~120 km further west of Kauai.

## Amendment 2026-08-02 (v3) — engine fixes; re-derivation of every window

The audit batch-1/2 fixes landed (wrap-safe crossing engine; per-instant
ayanamsa in sweeps; tightest-instant refinement for ALL rule types with the
acting body chosen, orb-gated, at the refined instant; per-rule fine sweep
steps). Both forward sweeps were regenerated with the fixed engine and these
exact commands (recorded for reproducibility):

```
uv run astgraf-bands --start 2026-08-02 --days 850 --rules mined-triggers.toml   --out out/mined-forward-v3
uv run astgraf-bands --start 2026-08-02 --days 850 --rules doctrine-triggers.toml --out out/doctrine-forward-v3
```

**Mined windows: CONFIRMED unchanged.** The regenerated CSV is byte-identical
to the registered v2 (aspect predicates are ayanamsa-invariant) — all 9 mined
windows, instants, and spots stand exactly as registered above.

**Band-trigger windows: sharpened and completed.** The 1-hour fine sweep
(Moon rule) moves window edges by up to ~9 h, and each window now carries a
regenerable tightest instant. No giant sits within one span at any of these
instants, so NO giant spots exist for these windows — the v2 "giant spots
(secondary information)" figures are RETIRED as artifacts of the old
first-sample location:

| Window (UT) | Tightest instant (UT) |
|---|---|
| 2026-11-02 03:00 → 11-03 13:00 | 2026-11-03 01:18 |
| 2026-11-29 19:00 → 12-01 03:00 | 2026-11-30 04:42 |
| 2027-02-20 01:00 → 02-21 00:00 | 2027-02-20 20:26 |
| 2027-03-18 20:00 → 03-20 08:00 | 2027-03-19 16:16 |
| 2027-04-15 02:00 → 04-16 12:00 | 2027-04-15 15:01 |
| 2028-08-17 02:00 → 08-18 17:00 | 2028-08-17 23:26 |

**Nodes-doubly-occupied windows: instants + Jupiter spots, now regenerable.**
The tightest instant minimizes the both-ends holding gap; the acting body is
the holder ON the node at that instant — Jupiter (on Ketu) in all four
windows, confirming the Jan–Mar 2027 Jupiter-on-Ketu reading. These
supersede the six per-holder console-derived instants in the section above
(audit: non-regenerable); the Feb-06 eclipse-on-Rahu context stays as
commentary only.

| Window (UT) | Tightest instant (UT) | Jupiter spot | Watch-region center |
|---|---|---|---|
| 2027-01-24 → 01-28 | 2027-01-27 17:15 | 111.98E 14.50N | South China Sea, west of Luzon |
| 2027-02-06 → 02-13 | 2027-02-11 01:30 | 27.65W 15.14N | mid-Atlantic, west of Cape Verde |
| 2027-02-24 → 03-10 | 2027-03-03 00:58 | 41.95W 15.97N | western Atlantic, east of the Antilles |
| 2027-03-14 → 03-20 | 2027-03-16 12:54 | 124.19E 16.38N | Philippine Sea, off Luzon |

The canonical artifacts `out/mined-forward/rules_episodes.csv` and
`out/doctrine-forward/rules_episodes.csv` now hold the v3 rows; the outcome
protocol (astgraf-outcomes) grades these. Tie-break note (finding 13, fixed
2026-08-02): when several equally-exact crossings exist, the EARLIEST now wins
deterministically — re-derivation moved one registered instant (2027-03-03
nodes window: 01:01 → 00:58 UT, Jupiter spot 42.70W → 41.95W); all other rows
byte-identical. Chance baselines were also made step-honest (findings 21/38):
the 2013-2015 census re-scores as grid 0/31 vs 0.63 expected, proximity 1/31
vs 1.79 expected — the below-chance reading stands, more modestly. Spot caveat unchanged: ±1 h of
timing moves a spot ±15° of longitude; names mark watch-region centers.

## Amendment 2026-08-02 (v4) — mined rules retired; windows stay as the experiment

The batch-3 honest re-mining (declustered post-1900 corpus, time-uniform
climatology controls, 2-year-block split, add-one smoothed lifts, 200-run
permutation calibration; `scripts/mine_usgs.py` v2 → `out/signatures-m7-v2`)
retires all three mined rules: observed family-wise max lift **1.79** vs a
permutation null median of 1.73 (95th percentile 2.12), **p = 0.35**; every
top screening lift collapses on the held-out block-half; locator spatial
skill is nil (median nearest-spot 4,896 km vs 5,007 km shuffled). The v1
lifts (1.80/1.76/1.52) are attributed to aliased event-shifted controls and
a leaky even/odd split. A methodological note for the record: a circular-
shift pilot design promoted `sep:Uranus-Neptune@opp` to lift 55 purely
through the catalog's pre-1900 completeness gradient meeting an era-locked
predicate — era-locked slow-planet predicates cannot be assessed against
event-shifted controls at all.

**The 9 mined windows above REMAIN registered**: they were pre-registered
before the re-mining, and the outcome protocol grades them regardless — as
a falsifiable experiment now carrying no statistical support. The doctrine
channel (band trigger, nodes, vyuham, site rules) is untouched by this
verdict. `astgraf-outcomes` now also writes a `spatial_chance` column — the
historical fraction of M7+ events within the grading radius of each spot —
so any future "hit" is read against its base rate.

## Amendment 2026-08-04 (v5) — spots demoted to experimental; quake windows are time-only claims

NU ratified the location-layer re-scoping after the 2026-08-04 test battery
(ledger, same date): the world-spot channel measures at chance on 1,435
declustered M7+ mainshocks in EVERY tested formulation — the current rule
(median longitude gap 28.9° vs 28.6° shuffled), locate-at-the-event-minute
(29.2° vs 29.3°), the zero-rotation real-meridian alternative (29.9° vs
28.8°), and the site-angle channel (family p = 0.25); per-body gap
distributions match uniform. The rotation as implemented is self-canceling
against the trigger-chart offset (the current rule ≈ the observed
culmination meridian at arrival).

Consequences for this register:

- **Every spot above and in `rules_episodes.csv` REMAINS registered and
  will be graded** by `astgraf-outcomes` with its `spatial_chance` base
  rate — but all spots now carry the status **experimental: retrospectively
  at chance**. A graded forward hit above base rate is the reinstatement
  criterion.
- **The claims of this watch-list are the INSTANTS.** For earthquake
  windows the located names mark grading regions for the experiment, not
  point-predictions of the system.
- **The site channel (Ascendant/MC over held axes) is scoped to the taught
  local categories** (Hyderabad-type floods, Ulsoor-type local events):
  it interrogates a named candidate site; it is not a world-search. Its
  corpus test awaits the flood-records list and the news outcome channel.
- The awaited NR/Rs/Ro table cannot rescue the quake-spot channel (a
  constant longitude offset leaves a uniform gap distribution uniform); its
  bearing is on TIMING — which alignments are exact and when.

## Anchor recurrence (added 2026-08-04, NU ruling) — registered windows

NU ruled that recurrence-calendar episodes join this register. Channel
pre-registration: anchors = the 10 in `anchors.toml`; engine =
`astgraf-recur` (pattern = the anchor's non-Moon doctrine-orb contacts,
daily scan, tightest instant refined below one minute); scan span
2026-08-04 + 2 years at full match (n/n) and near match (n−1/n). All claims
are TIME-ONLY per amendment v5 — no spots. Regenerate:
`uv run astgraf-recur --start 2026-08-04 --years 2 --out out/recur`
(near level: add `--min-match <n-1>` per anchor).

**Full re-formations through 2028-08: NONE across all 10 anchors** — an
honest empty registration; the channel's first full window enters here when
a scan produces one.

| Anchor | Level | Window (UT) | Tightest (UT) | Missing contact | Registered claim | Base rate | Outcome |
|---|---|---|---|---|---|---|---|
| alaska-1964 (M9.2) | near 3/4 | 2026-11-15 → 2026-11-20 | 2026-11-17 13:02 | sep:Ketu-Uranus@tri | M7+ earthquake worldwide inside the window (time-only) | ~0.2 expected M7+ in the window (corpus 11.9/yr) | *pending* |

Grading note: with a ~0.2 base expectation, a single in-window M7+ is weak
evidence by itself; the channel accumulates standing across windows, hits
AND clears logged alike.

## Amendment 2026-08-04 (v6) — observed-rule channel opened, status TESTING

Per NU's same-day ruling, the Nepal observation **site Ascendant trine
real-Neptune** (0.26° at the catalog minute and true epicenter; 0.43° on
the QUAKE chart's rounded site) is promoted to a rule in **TESTING**
status: `observed-triggers.toml`, orb 1.0°, tropical site charts only (the
canon's sidereal mode shifts angles by ayanamsa in RA space — frame-guard
test pinned). It is a site-conditional fast hand — it sweeps any given
site twice daily, so it carries no standalone forward windows; its testing
record is its behavior inside loaded windows at candidate sites, graded
with the site channel.
