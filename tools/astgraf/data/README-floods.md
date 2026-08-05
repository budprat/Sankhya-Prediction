# The flood corpus (`floods-historical.csv`)

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
| `loc_precision` | `point` \| `city` \| `region` |
| `place`, `cause`, `deaths` | as recorded; `deaths` blank where not distinctive |
| `tier` | `paleo` \| `ancient` \| `medieval` \| `early-modern` \| `modern` \| `contemporary` |
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
