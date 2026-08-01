# ABOUTME: Aspect-event detection over a period grid: conjunction/square/trine/opposition
# ABOUTME: crossings found between samples and refined by bisection on the ephemeris.

from collections.abc import Callable

from .models import AspectEvent, PeriodRow

ASPECT_ANGLES = {"conjunction": 0.0, "square": 90.0, "trine": 120.0, "opposition": 180.0}

PosFn = Callable[[float], dict[str, float]]


def signed_separation(lon_b: float, lon_a: float) -> float:
    """Shortest signed angle from a to b, in (-180, 180]."""
    d = (lon_b - lon_a) % 360
    return d - 360 if d > 180 else d


def _targets(angle: float) -> tuple[float, ...]:
    if angle == 0:
        return (0.0,)
    if angle == 180:
        return (180.0,)  # 180 and -180 are the same crossing
    return (angle, -angle)


def _wrap180(x: float) -> float:
    d = x % 360
    return d - 360 if d > 180 else d


def _refine(pos: PosFn, body_a: str, body_b: str, target: float,
            jd_lo: float, jd_hi: float, jd_guess: float) -> float:
    def g(jd: float) -> float:
        lons = pos(jd)
        return _wrap180(signed_separation(lons[body_b], lons[body_a]) - target)

    lo, hi = jd_lo, jd_hi
    g_lo = g(lo)
    if g_lo * g(hi) > 0:
        return jd_guess  # bracket lost (multiple crossings); keep the linear estimate
    for _ in range(60):
        mid = (lo + hi) / 2
        if g_lo * g(mid) <= 0:
            hi = mid
        else:
            lo = mid
            g_lo = g(lo)
    return (lo + hi) / 2


def find_events(rows: list[PeriodRow], pos_at_jd: PosFn | None = None,
                bodies: list[str] | None = None) -> list[AspectEvent]:
    if bodies is None:
        bodies = [p.name for p in rows[0].positions]
    events: list[AspectEvent] = []
    pairs = [(a, b) for i, a in enumerate(bodies) for b in bodies[i + 1:]]
    for i in range(len(rows) - 1):
        r1, r2 = rows[i], rows[i + 1]
        for body_a, body_b in pairs:
            d1 = signed_separation(r1.longitude_of(body_b), r1.longitude_of(body_a))
            d2 = signed_separation(r2.longitude_of(body_b), r2.longitude_of(body_a))
            delta = _wrap180(d2 - d1)
            if delta == 0:
                continue
            for kind, angle in ASPECT_ANGLES.items():
                for target in _targets(angle):
                    for k in (-1, 0, 1):
                        u = (target + 360 * k - d1) / delta
                        if not 0 < u <= 1:
                            continue
                        jd_guess = r1.jd + u * (r2.jd - r1.jd)
                        jd = jd_guess if pos_at_jd is None else _refine(
                            pos_at_jd, body_a, body_b, target, r1.jd, r2.jd, jd_guess)
                        events.append(AspectEvent(
                            body_a=body_a, body_b=body_b, kind=kind, jd=jd))
    events.sort(key=lambda e: e.jd)
    return events
