# Forecast Watch-List — registered 2026-08-02

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
| 2026-10-02 04:45 | 138.71W 0.05S | equatorial Pacific N of the Marquesas | *pending* |
| 2027-10-04 20:15 | 11.50W 0.80N | equatorial Atlantic ~700 km S of Liberia | *pending* |
| 2027-11-12 12:00 | 73.31E 0.44N | southern Maldives (~120 km from Addu Atoll) | *pending* |
| 2028-11-06 06:15 | 167.18E 1.35N | W Pacific ~210 km from Nauru | *pending* |

## Mined: real-Uranus △ Sun (lift 1.52/1.31) — Uranus spots

| Exact instant (UT) | Spot | Region | Outcome |
|---|---|---|---|
| 2026-10-16 09:19 | 138.80W 21.01N | NE Pacific ~2,000 km E of Hawaii | *pending* |
| 2027-02-08 13:16 | 44.71E 20.37N | SW Saudi Arabia (Najran / Rub' al Khali edge) | *pending* |
| 2027-10-20 21:47 | 34.40E 21.77N | Nubian Desert, Egypt–Sudan border (Halaib) | *pending* |
| 2028-02-12 23:36 | 109.89W 21.22N | Pacific off Baja California Sur (Revillagigedo) | *pending* |
| 2028-10-24 10:43 | 159.28W 22.41N | ~45 km off Kauai, Hawaii | *pending* |

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
  1600–2030 shows triple-conjunction clusters every **167.6 years** —
  1649–52, 1820–23, 1991–94 (Abhijit/Uthrashada). Next cluster ~2159.
  No forward window in this register's span.
- **Jupiter–Saturn conjunction** (Java/tsunami-volcanic family): ~19–20 y
  rhythm; the doctrine's ~120-year episode is concrete in the census —
  **1881 conjunction in Aswini → Krakatoa 1883; 2000 conjunction in
  Kritika → 2004 Sumatra tsunami** (both conjunctions in the Aswini–Kritika
  sector, both followed by Indonesian mega-events within 2–4 years). Last:
  2020-12-21 (Uthrashada). Next: ~2040 — outside this register's span.

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
