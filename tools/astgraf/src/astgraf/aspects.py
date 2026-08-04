# ABOUTME: Aspect-event detection over a period grid: wrap-safe crossing detection on
# ABOUTME: an unwrapped sub-sampled separation series, bisection-refined per crossing.

# Audit 2026-08-02 rewrite: the old endpoint-only detector missed retrograde
# multi-crossings and its bisection converged onto the +-180 wrap (events
# reported with the OPPOSITE aspect kind). Each grid interval is now
# sub-sampled so relative motion per sub-step stays under 60 deg, the
# separation series is unwrapped (continuous), and crossings are isolated in
# sub-brackets where the wrapped refinement function has no discontinuity.
import math
from collections.abc import Callable

from .models import AspectEvent, PeriodRow

ASPECT_ANGLES = {"conjunction": 0.0, "square": 90.0, "trine": 120.0, "opposition": 180.0}

# Max geocentric rates, deg/day, with headroom — sizes the sub-sampling.
MAX_SPEED = {"Ascendant": 366.0, "Moon": 16.0, "Sun": 1.1, "Mercury": 2.3,
             "Venus": 1.4, "Mars": 0.9, "Jupiter": 0.3, "Saturn": 0.2,
             "Rahu": 0.1, "Ketu": 0.1, "Uranus": 0.1, "Neptune": 0.1,
             "Pluto": 0.1}
DEFAULT_SPEED = 20.0        # unknown (synthetic/test) bodies
MAX_MOTION = 60.0           # max relative motion per sub-step, degrees
# Known bodies follow the lens contract (README): a pair is meaningful at a
# grid only while its relative motion stays within ~one cycle per division —
# beyond that it is skipped with a note ("descend the lens"). Unknown bodies
# (synthetic tests) get a generous cost cap instead.
MAX_SUBSTEPS = 8            # known pairs: ~480 deg of relative motion/interval
MAX_SUBSTEPS_UNKNOWN = 400


def _substep_cap(body_a: str, body_b: str) -> int:
    known = body_a in MAX_SPEED and body_b in MAX_SPEED
    return MAX_SUBSTEPS if known else MAX_SUBSTEPS_UNKNOWN

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


def mirror_offset(lon_a: float, lon_b: float) -> float:
    """Miss from the cos-fold mirror: 0 when lon_a + lon_b is a multiple of 360.

    GRAPHDO.BAS (line 54) and the author's own JS both plot y = cos(longitude),
    so two traces meet not only at a conjunction but whenever
    cos(lon_a) == cos(lon_b) — the pair mirrored about the 0-180 equinox axis.
    That crossing is visible on his graph and invisible to ASPECT_ANGLES.
    """
    return _wrap180(lon_a + lon_b)


def pair_speed(body_a: str, body_b: str) -> float:
    return (MAX_SPEED.get(body_a, DEFAULT_SPEED)
            + MAX_SPEED.get(body_b, DEFAULT_SPEED))


def substeps_needed(span_days: float, speed: float) -> int:
    return max(1, math.ceil(span_days * speed / MAX_MOTION))


def unwrap(values: list[float]) -> list[float]:
    """Continuous series: each step takes the nearest representation."""
    out = [values[0]]
    for v in values[1:]:
        out.append(out[-1] + _wrap180(v - out[-1]))
    return out


Metric = Callable[[dict[str, float]], float]


def _metric(mode: str, body_a: str, body_b: str) -> Metric:
    """The scalar whose target crossings are the events of this relation."""
    if mode == "mirror":
        return lambda lons: lons[body_a] + lons[body_b]
    return lambda lons: signed_separation(lons[body_b], lons[body_a])


def _kind_targets(mode: str) -> tuple[tuple[str, float], ...]:
    if mode == "mirror":
        return (("mirror", 0.0),)
    return tuple((kind, t) for kind, angle in ASPECT_ANGLES.items()
                 for t in _targets(angle))


def _refine(pos: PosFn, metric: Metric, target: float,
            jd_lo: float, jd_hi: float, jd_guess: float) -> float:
    def g(jd: float) -> float:
        return _wrap180(metric(pos(jd)) - target)

    lo, hi = jd_lo, jd_hi
    g_lo, g_hi = g(lo), g(hi)
    # Sub-bracket motion is < MAX_MOTION, so a genuine crossing keeps |g| small
    # on at least one side; a +-180 jump bracket does not — refuse it.
    if g_lo * g_hi > 0 or min(abs(g_lo), abs(g_hi)) > 90:
        return jd_guess
    for _ in range(60):
        if hi - lo < 1e-9:                  # ~0.1 ms — beyond any output need
            break
        mid = (lo + hi) / 2
        if g_lo * g(mid) <= 0:
            hi = mid
        else:
            lo = mid
            g_lo = g(lo)
    return (lo + hi) / 2


def _sample_interval(r1: PeriodRow, r2: PeriodRow, n: int, pos_at_jd: PosFn,
                     bodies: list[str]) -> tuple[list[float], list[dict[str, float]]]:
    """n+1 sample points across [r1.jd, r2.jd]; ends come from the rows."""
    jds = [r1.jd + (r2.jd - r1.jd) * j / n for j in range(n + 1)]
    lons: list[dict[str, float]] = []
    for j, jd in enumerate(jds):
        if j == 0:
            lons.append({b: r1.longitude_of(b) for b in bodies})
        elif j == n:
            lons.append({b: r2.longitude_of(b) for b in bodies})
        else:
            lons.append(pos_at_jd(jd))
    return jds, lons


def _scan(rows: list[PeriodRow], pos_at_jd: PosFn | None,
          bodies: list[str] | None, skipped: list[str] | None,
          mode: str) -> list[AspectEvent]:
    if bodies is None:
        bodies = [p.name for p in rows[0].positions]
    events: list[AspectEvent] = []
    pairs = [(a, b) for i, a in enumerate(bodies) for b in bodies[i + 1:]]
    skip_set: set[str] = set()

    for i in range(len(rows) - 1):
        r1, r2 = rows[i], rows[i + 1]
        span = r2.jd - r1.jd
        live_pairs = []
        n_grid = 1
        for a, b in pairs:
            n = substeps_needed(span, pair_speed(a, b))
            if pos_at_jd is None:
                n = 1                       # no sampler: legacy single segment
            if n > _substep_cap(a, b):
                skip_set.add(f"{a}-{b}")
                continue
            live_pairs.append((a, b))
            n_grid = max(n_grid, n)
        if not live_pairs:
            continue
        if pos_at_jd is None:
            jds = [r1.jd, r2.jd]
            lons = [{p: r1.longitude_of(p) for p in bodies},
                    {p: r2.longitude_of(p) for p in bodies}]
        else:
            jds, lons = _sample_interval(r1, r2, n_grid, pos_at_jd, bodies)

        for body_a, body_b in live_pairs:
            metric = _metric(mode, body_a, body_b)
            seps = unwrap([metric(s) for s in lons])
            for kind, target in _kind_targets(mode):
                for j in range(len(jds) - 1):
                    u0, u1 = seps[j], seps[j + 1]
                    if u0 == u1:
                        continue
                    lo_v, hi_v = min(u0, u1), max(u0, u1)
                    k0 = math.ceil((lo_v - target) / 360)
                    k1 = math.floor((hi_v - target) / 360)
                    for k in range(k0, k1 + 1):
                        tgt = target + 360 * k
                        if tgt == u0 or not lo_v <= tgt <= hi_v:
                            continue   # crossings are (u0, u1]-exclusive at u0
                        u = (tgt - u0) / (u1 - u0)
                        jd_guess = jds[j] + u * (jds[j + 1] - jds[j])
                        jd = jd_guess if pos_at_jd is None else _refine(
                            pos_at_jd, metric, target,
                            jds[j], jds[j + 1], jd_guess)
                        events.append(AspectEvent(
                            body_a=body_a, body_b=body_b, kind=kind, jd=jd))
    if skipped is not None:
        skipped.extend(sorted(skip_set))
    events.sort(key=lambda e: e.jd)
    return events


def find_events(rows: list[PeriodRow], pos_at_jd: PosFn | None = None,
                bodies: list[str] | None = None,
                skipped: list[str] | None = None) -> list[AspectEvent]:
    """Classical aspect crossings: conjunction, square, trine, opposition."""
    return _scan(rows, pos_at_jd, bodies, skipped, "aspect")


def find_mirror_events(rows: list[PeriodRow], pos_at_jd: PosFn | None = None,
                       bodies: list[str] | None = None,
                       skipped: list[str] | None = None) -> list[AspectEvent]:
    """Cos-fold crossings (kind="mirror"): the instants where the pair's traces
    meet on the heritage graph because cos(lon_a) == cos(lon_b). Kept separate
    from find_events so the audited aspect stream is unchanged."""
    return _scan(rows, pos_at_jd, bodies, skipped, "mirror")
