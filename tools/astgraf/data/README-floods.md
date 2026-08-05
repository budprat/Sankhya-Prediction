# The event corpora

Four files, one schema — so any analysis can read them together:

| file | n | span | scope |
|---|---|---|---|
| `usgs-m7-1850-2020.csv` | 1,435 declustered | 1900–2020 | Global M7+, magnitude-selected, exact instants (the pinned corpus) |
| `quakes-historical.csv` | 39 | 856 CE – 2023 | Curated majors in three tiers, incl. a **deaths-selected** tier |
| `floods-historical.csv` | 88 | ~5.3 Ma – 2021 | Global, hand-curated, deep time |
| `floods-hanze-europe.csv` | 2,724 | 1871 – 2025 | Europe, imported from HANZE v3.0.1b |

## `quakes-historical.csv` — why a curated quake file when a corpus exists

The pinned USGS corpus is **magnitude**-selected. The doctrine speaks about
catastrophe, which is not the same variable: Tangshan (Mw 7.5, ~300,000 dead)
and Haiti (Mw 7.0, ~200,000 dead) are minor by seismic moment and enormous by
consequence. This file adds a **deaths-selected** tier (12 events), a
**largest** tier (15 events, Mw ≥ 8.4), and a **pre-instrumental** tier (12
events, 856 CE onward, macroseismic locations). It also reaches past the
pinned corpus's 2020 cut-off (2023 Turkey–Syria) and back before it (1556
Shaanxi, ~830,000 deaths, the deadliest on record).

Usability: 20 rows carry minute precision, 18 day, 1 month; **32 are
chart-usable** (minute/day and ≥ 1700), 7 pre-1700 rows are disqualified by
engine drift, and 23 carry death tolls. Pre-instrumental coordinates are
macroseismic estimates (±10–100+ km) — `loc_precision` says `region` for all
of them.

# The flood corpora

Two files, same schema, different provenance:

| file | n | span | scope |
|---|---|---|---|
| `floods-historical.csv` | 88 | ~5.3 Ma – 2021 | Global, hand-curated from NU's compilation; deep time |
| `floods-hanze-europe.csv` | 2,724 | 1871 – 2025 | Europe, imported wholesale from HANZE v3.0.1b |

## `floods-hanze-europe.csv` — the imported catalogue

Downloaded from Zenodo record **20478847** ("HANZE database of historical
flood impacts in Europe, 1870-2025", CC-BY-4.0) via the Zenodo API and
converted into the schema below. **Every row carries a full YYYY-MM-DD start
date** — 100% day precision, which per the drift table means every acting
body except the Moon is inside a 3° orb. 40 countries; 2,699 of 2,724 rows
carry a fatality count; types are flash (1,318), river (1,259), coastal
(102) and compound (45).

**Its one weakness is location.** HANZE records NUTS-3 region codes, not
coordinates, and its region file carries no centroids — so `latitude` /
`longitude` here are **country centroids** and `loc_precision` is `country`.
That is useless for a point-location test and perfectly adequate for the
tests this corpus actually unblocks (long-cycle clocks, category recurrence,
contact timing), which need dates, not places. The `place` column preserves
the original NUTS-3 list so finer geocoding can be added later.

(The Dartmouth Flood Observatory archive, which *does* publish centroids, is
no longer served — its archive URLs return HTTP 410 Gone as of 2026-08-05.)

# The curated corpus (`floods-historical.csv`)

88 flood events compiled by NU (2026-08-05) from historical documents,
paleoflood studies, and modern catalogues (DFO Global Active Archive, HANZE
Europe, Chinese river chronicles, the Wetter et al. High Rhine
reconstruction, PAGES Floods Working Group). This is the corpus the flood /
site channel has been blocked on: until now every location and long-cycle
claim in the flood family was untestable for want of a catalogue.

## Columns

| column | meaning |
|---|---|
| `id` | stable slug |
| `time` | ISO instant; **the sub-day part is padding, not data** — read `date_precision` |
| `date_precision` | `day` \| `month` \| `year` \| `century` \| `millennium` |
| `latitude`, `longitude` | degrees north / east |
| `loc_precision` | `point` \| `city` \| `region` \| `country` (HANZE) |
| `place`, `cause`, `deaths` | as recorded; `deaths` blank where not distinctive |
| `tier` | `paleo` \| `ancient` \| `medieval` \| `early-modern` \| `modern` \| `contemporary` \| `hanze` |
| `notes` | provenance and caveats, including feast-day dating |

## Which events can actually be used, and why

An event is usable for a contact test only if its date pins the acting body
inside the doctrine's 3° orb. Body drift decides that:

| body | per day | per month | per year |
|---|---|---|---|
| Neptune | 0.021° | 0.63° | 7.7° |
| Uranus | 0.032° | 0.96° | 11.7° |
| Rahu / Ketu | 0.053° | 1.59° | 19.3° |
| Saturn | 0.069° | 2.07° | 25.2° |
| Jupiter | 0.131° | 3.93° | 47.8° |
| Sun | 0.986° | 29.6° | — |
| Moon | 13.17° | — | — |

- **Day precision** — every body inside orb except the Moon, which needs the
  hour. Full contact work.
- **Month precision** — Uranus, Neptune and the nodes usable; Saturn
  marginal; Jupiter and faster, no. **Slow-layer only** — which is exactly
  the taught flood signature (the Uranus–Neptune family, Neptune on Ketu).
- **Year precision or coarser** — nothing usable at 3°. Keep for the record
  and for long-cycle family work, not for contact tests.

A second cut is the engine's own accuracy: minute-level near the modern era,
**degrees-level drift by the 1600s** (cross-checked against JPL DE440). Well
dated pre-1700 events are therefore *not* rescued by their good dates.

**The usable subset, counted:**

| set | n |
|---|---|
| Total events | 88 |
| Day precision | 40 |
| Month precision | 13 |
| **Chart-usable (day/month AND ≥ 1700)** | **39** |
| — of which full contact work (day) | 26 |
| — of which slow-layer only (month) | 13 |
| Well dated but pre-1700 (engine drift) | 14 |
| Year precision or coarser | 35 |

## Honesty notes

- **Feast-day dating is inference, not record.** Grote Mandrenke, St Lucia's,
  St Elizabeth's, All Saints', St Felix's, Magdalenenhochwasser and the
  Christmas flood are dated from the saint's day they are *named for* — a
  legitimate and standard historical method, but it is a derived date. Each
  such row says so in `notes`.
- **Julian vs Gregorian.** Pre-1582 dates are Julian as recorded; the engine
  applies the reform at 1582-10-15. No conversion has been applied to the
  medieval rows, so their absolute instants carry that offset.
- **`loc_precision` matters as much as coordinates.** A `region` row is a
  basin centroid, not an epicenter — useless for a point-location test,
  usable for a category or long-cycle test.
- **Paleoflood rows are placeholders for scale, not datable events.** Their
  `time` fields carry a nominal instant so the file parses; the dating
  uncertainty is millennia.
- **This corpus is not declustered and has no completeness model.** Reporting
  density rises steeply with time and with proximity to Europe and China —
  any test must control for that, exactly as the quake corpus required
  declustering and climatology controls.

## What it unblocks

1. The **flood-family long-cycle test** — NU's Uranus–Neptune ~163/164/171-year
   clocks, which the 2011–15 cluster members (Uttarakhand 2013, Europe 2013,
   Kashmir 2014) now sit in as data rather than anecdote.
2. The **site channel's own category** — the taught Hyderabad instance is in
   here, and the site channel has never had a corpus in the category it was
   taught in.
3. **Category-tagged recurrence** — `astgraf-recur --category flood` now has
   events to grade against.
