# ABOUTME: Nakshatra layers: the classical 27-star position (ASTGRAF.BAS canon, the
# ABOUTME: default) and the parked 252/1764 equal ladder (28 x 9 x 7, via --ladder 28).

# NU (2026-08-02): "follow exactly whats in ASTGRAF.BAS, we will decide later for
# Abhijit 28" — the default nakshatra layer is the classical 27-star system as the
# BASIC suite defines it (ASTGRAF.BAS DATA 348-351; position arithmetic verbatim
# from ASTROLOG.BAS 5680-5790). The 28-division ladder below stays available
# behind --ladder 28, unchanged, pending that decision.
#
# NU (2026-08-01/02, parked with the ladder): the prediction cycle is 28 x 9 =
# 252 divisions (KP's 243 used 27); star names are MARKERS only — divisions are
# equal. The refinement ladder is the Predict.pdf one: /9 then /7 — 28 x 9 x 7 =
# 1764, "the 1/63rd fraction", the instant. Abhijit is the 21st division
# (257.14-270), exactly opposite Punarvasu (with the Secrets-of-Sankhya
# opposition argument and the Atharvaveda 19.7 order; Predict.pdf's own table
# said 22nd — overridden).
from collections.abc import Callable

from pydantic import BaseModel

from .models import PeriodRow

# ASTGRAF.BAS DATA lines 348-351 verbatim: 27 names, no Abhijit. One ruled
# exception: "Magha" spelling kept (the BAS prints "Makha").
NAKSHATRAS_27 = [
    "Aswini", "Bharani", "Kritika", "Rohini", "Mirgasirsa", "Rudra", "Punarvasu",
    "Pusyam", "Ashlesha", "Magha", "Pura", "Uthra", "Hasta", "Chitra", "Swathy",
    "Visaka", "Anuradha", "Jyestha", "Moola", "Poorvashada", "Uthrashada",
    "Sravana", "Dhanishta", "Satabhisa", "P.Badra", "Uthra Badra", "Revathy",
]

# The suite's z$ sign order (DATA Sun,Ari,Tenth ... Ket,Pis,Ninth).
SIGNS_12 = ["Ari", "Tau", "Gem", "Can", "Leo", "Vir",
            "Lib", "Sco", "Sag", "Cap", "Aqu", "Pis"]

HORARY_NAKSHATRAS_28 = [
    "Aswini", "Bharani", "Kritika", "Rohini", "Mirgasirsa", "Rudra", "Punarvasu",
    "Pusyam", "Ashlesha", "Magha", "Pura", "Uthra", "Hasta", "Chitra", "Swathy",
    "Visaka", "Anuradha", "Jyestha", "Moola", "Poorvashada", "Abhijit",
    "Uthrashada", "Sravana", "Dhanishta", "Satabhisa", "P.Badra", "Uthra Badra",
    "Revathy",
]

# Vimshottari lord order (the suite's BR table). Convention, stated for NU to
# correct: division n takes lord (n-1) mod 9; the first sub of a division takes
# the division's own lord and cycles on; sub-subs likewise from the sub's lord.
LORD_CYCLE = ["Ketu", "Venus", "Sun", "Moon", "Mars",
              "Rahu", "Jupiter", "Saturn", "Mercury"]

DIVISION_SPAN = 360.0 / 28
SUB_SPAN = 360.0 / 252
SUBSUB_SPAN = 360.0 / 1764   # /9 then /7, the PDF's 1/63rd of a nakshatra


class StarPosition(BaseModel):
    longitude: float
    nakshatra: str
    starcount: int         # 1..27
    pada: int              # 1..4
    navam: str             # navamsam sign, z$ order


def star_position(longitude: float) -> StarPosition:
    """Classical 27-star position: verbatim port of ASTROLOG.BAS 5680-5790.

    y counts 3-deg-20-min padas from 0 Aries; 4 padas per star, 12 padas per
    navamsa cycle — exactly the BASIC's INT arithmetic, oracle-pinned to the
    QUAKE.pdf printout.
    """
    a = longitude % 360.0
    y = (a / 10) * 3
    count = int(y)
    pada_global = count + 1                    # PADA
    starcount = int(count / 4) + 1             # STARCOUNT
    if starcount > 27:
        starcount -= 27
    navam = pada_global - (int(y / 12) * 12)   # NAVAM
    pad = pada_global - (int(count / 4) * 4)   # PAD
    return StarPosition(longitude=a, nakshatra=NAKSHATRAS_27[starcount - 1],
                        starcount=starcount, pada=pad, navam=SIGNS_12[navam - 1])


class HoraryPosition(BaseModel):
    longitude: float
    division: int          # 1..28
    nakshatra: str
    division_lord: str
    sub: int               # 1..252 (global numbering)
    sub_lord: str
    # Numeric only: the 9-lord cycle has no defined mapping onto a 7-fold level;
    # lords for the instant level await NU's specification.
    subsub: int            # 1..1764 (global numbering)


class SubCrossing(BaseModel):
    body: str
    from_sub: int
    to_sub: int
    boundary_deg: float
    jd: float
    label: str = ""


def horary_position(longitude: float) -> HoraryPosition:
    lon = longitude % 360.0
    division = int(lon // DIVISION_SPAN) + 1
    sub = int(lon // SUB_SPAN) + 1
    subsub = int(lon // SUBSUB_SPAN) + 1
    division_index = division - 1
    sub_in_division = sub - division_index * 9 - 1        # 0..8
    sub_lord_index = (division_index + sub_in_division) % 9
    return HoraryPosition(
        longitude=lon,
        division=division,
        nakshatra=HORARY_NAKSHATRAS_28[division_index],
        division_lord=LORD_CYCLE[division_index % 9],
        sub=sub,
        sub_lord=LORD_CYCLE[sub_lord_index],
        subsub=subsub,
    )


def _wrap180(x: float) -> float:
    d = x % 360
    return d - 360 if d > 180 else d


PosFn = Callable[[float], dict[str, float]]


def _refine_boundary(pos: PosFn, body: str, boundary: float,
                     jd_lo: float, jd_hi: float, jd_guess: float) -> float:
    def g(jd: float) -> float:
        return _wrap180(pos(jd)[body] - boundary)

    lo, hi = jd_lo, jd_hi
    g_lo, g_hi = g(lo), g(hi)
    # A +-180 jump bracket has |g| large on both sides; a real crossing does
    # not (sub-bracket motion < 60 deg) — refuse the jump.
    if g_lo * g_hi > 0 or min(abs(g_lo), abs(g_hi)) > 90:
        return jd_guess
    for _ in range(60):
        if hi - lo < 1e-9:
            break
        mid = (lo + hi) / 2
        if g_lo * g(mid) <= 0:
            hi = mid
        else:
            lo = mid
            g_lo = g(lo)
    return (lo + hi) / 2


def find_sub_crossings(rows: list[PeriodRow], pos_at_jd: PosFn | None = None,
                       bodies: list[str] | None = None,
                       skipped: list[str] | None = None) -> list[SubCrossing]:
    """Detect 1/252-boundary crossings, wrap- and retro-aware.

    Audit 2026-08-02 rewrite: each interval is sub-sampled so a body moves
    under 60 deg per sub-step (fast movers at too-coarse grids are skipped
    with a note), the longitude series is unwrapped, and every boundary
    multiple crossed on the continuous axis becomes one event, refined in a
    sub-bracket free of the +-180 discontinuity.
    """
    from math import ceil, floor

    from .aspects import (DEFAULT_SPEED, MAX_MOTION, MAX_SPEED, MAX_SUBSTEPS,
                          MAX_SUBSTEPS_UNKNOWN, unwrap)
    if bodies is None:
        bodies = [p.name for p in rows[0].positions]
    events: list[SubCrossing] = []
    skip_set: set[str] = set()
    for i in range(len(rows) - 1):
        r1, r2 = rows[i], rows[i + 1]
        span = r2.jd - r1.jd
        live = []
        n_grid = 1
        for body in bodies:
            n = max(1, ceil(span * MAX_SPEED.get(body, DEFAULT_SPEED) / MAX_MOTION))
            if pos_at_jd is None:
                n = 1
            cap = MAX_SUBSTEPS if body in MAX_SPEED else MAX_SUBSTEPS_UNKNOWN
            if n > cap:
                skip_set.add(body)
                continue
            live.append(body)
            n_grid = max(n_grid, n)
        if not live:
            continue
        jds = [r1.jd + span * j / n_grid for j in range(n_grid + 1)]
        samples = []
        for j, jd in enumerate(jds):
            if j == 0:
                samples.append({b: r1.longitude_of(b) for b in live})
            elif j == n_grid:
                samples.append({b: r2.longitude_of(b) for b in live})
            else:
                samples.append(pos_at_jd(jd))
        for body in live:
            lons = unwrap([s[body] for s in samples])
            for j in range(n_grid):
                l0, l1 = lons[j], lons[j + 1]
                if l0 == l1:
                    continue
                lo_v, hi_v = min(l0, l1), max(l0, l1)
                direction = 1 if l1 > l0 else -1
                for k in range(ceil(lo_v / SUB_SPAN), floor(hi_v / SUB_SPAN) + 1):
                    v = k * SUB_SPAN
                    if v == l0 or not lo_v <= v <= hi_v:
                        continue           # crossings are (l0, l1]-exclusive at l0
                    boundary = v % 360.0
                    kb = round(boundary / SUB_SPAN) % 252   # boundary index 0..251
                    if direction > 0:
                        from_sub, to_sub = (kb - 1) % 252 + 1, kb % 252 + 1
                    else:
                        from_sub, to_sub = kb % 252 + 1, (kb - 1) % 252 + 1
                    u = (v - l0) / (l1 - l0)
                    jd_guess = jds[j] + u * (jds[j + 1] - jds[j])
                    jd = jd_guess if pos_at_jd is None else _refine_boundary(
                        pos_at_jd, body, boundary, jds[j], jds[j + 1], jd_guess)
                    events.append(SubCrossing(body=body, from_sub=from_sub,
                                              to_sub=to_sub, boundary_deg=boundary,
                                              jd=jd))
    if skipped is not None:
        skipped.extend(sorted(skip_set))
    events.sort(key=lambda e: e.jd)
    return events
