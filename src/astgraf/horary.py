# ABOUTME: The 252-division horary grid per NU's Sankhyan spec: 28 EQUAL nakshatra
# ABOUTME: divisions x 9 equal subs (1/252) x 9 sub-subs (1/2268), with lord cycling.

# NU (2026-08-01/02): the real cycle is 28 x 9 = 252 divisions (KP's 243 used 27);
# star names are MARKERS only — divisions are equal. The refinement ladder is the
# Predict.pdf one: /9 then /7 — 28 x 9 x 7 = 1764, "the 1/63rd fraction", the
# instant. Abhijit is the 21st division (257.14-270), exactly opposite Punarvasu
# (NU ruling 2026-08-02, with the Secrets-of-Sankhya opposition argument and the
# Atharvaveda 19.7 order; Predict.pdf's own table said 22nd — overridden).
from collections.abc import Callable

from pydantic import BaseModel

from .models import PeriodRow

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
    g_lo = g(lo)
    if g_lo * g(hi) > 0:
        return jd_guess
    for _ in range(60):
        mid = (lo + hi) / 2
        if g_lo * g(mid) <= 0:
            hi = mid
        else:
            lo = mid
            g_lo = g(lo)
    return (lo + hi) / 2


def find_sub_crossings(rows: list[PeriodRow], pos_at_jd: PosFn | None = None,
                       bodies: list[str] | None = None) -> list[SubCrossing]:
    """Detect 1/252-boundary crossings between samples, wrap- and retro-aware."""
    if bodies is None:
        bodies = [p.name for p in rows[0].positions]
    events: list[SubCrossing] = []
    for i in range(len(rows) - 1):
        r1, r2 = rows[i], rows[i + 1]
        for body in bodies:
            lon1, lon2 = r1.longitude_of(body), r2.longitude_of(body)
            delta = _wrap180(lon2 - lon1)
            if delta == 0:
                continue
            step = 1 if delta > 0 else -1
            sub1 = int((lon1 % 360) // SUB_SPAN) + 1
            # Walk boundaries along the motion direction until past lon2.
            k = 0
            while k < 252:
                k += 1
                if step > 0:
                    boundary = ((sub1 + k - 1) % 252) * SUB_SPAN
                    travelled = (boundary - lon1) % 360
                else:
                    boundary = ((sub1 - k) % 252) * SUB_SPAN
                    travelled = (lon1 - boundary) % 360
                if travelled == 0 or travelled > abs(delta):
                    break
                u = travelled / abs(delta)
                jd_guess = r1.jd + u * (r2.jd - r1.jd)
                jd = jd_guess if pos_at_jd is None else _refine_boundary(
                    pos_at_jd, body, boundary, r1.jd, r2.jd, jd_guess)
                from_sub = (sub1 + (k - 1) * step - 1) % 252 + 1
                to_sub = (sub1 + k * step - 1) % 252 + 1
                events.append(SubCrossing(body=body, from_sub=from_sub,
                                          to_sub=to_sub, boundary_deg=boundary, jd=jd))
    events.sort(key=lambda e: e.jd)
    return events
