# ABOUTME: Faithful Python port of the ASTGRAF.BAS / ASTROLOG.BAS computation core:
# ABOUTME: Newcomb-era Keplerian planets, truncated Brown Moon, lunar nodes, Ascendant.

import math

from .models import BodyPosition, ChartMoment, ChartResult

# The suite's 10-digit pi (BASIC: PI = 3.141592654#). Kept truncated deliberately:
# full-precision pi shifts the Moon by ~0.01 arcsec against the family canon.
PI = 3.141592654


def _rad(deg: float) -> float:
    return deg * PI / 180


def _deg(rad: float) -> float:
    return rad * 180 / PI

# Export order = the DR table in the BASIC suite (GRAPHDO's A..M key order).
BODY_ORDER = ["Ascendant", "Sun", "Moon", "Mars", "Mercury", "Jupiter",
              "Venus", "Saturn", "Rahu", "Ketu", "Uranus", "Neptune", "Pluto"]

PLANET_NAMES = ["Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn",
                "Uranus", "Neptune", "Pluto"]

# Orbital element polynomials (constant, T, T^2) exactly as in the BASIC DATA blocks:
# mean anomaly, eccentricity, semi-major axis, perihelion, node, inclination.
PLANET_ELEMENTS = [
    ((358.4758445, 35999.04975, -0.000150278), (0.01675104, -0.418e-4, -0.126e-6),
     1.00000023, (101.2208333, 1.719175, 0.000452778), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)),
    ((102.2793806, 149472.5153, 0.6389e-5), (0.20561421, 0.2046e-4, -0.3e-7),
     0.3870984, (28.75375278, 0.370280556, 0.000120833),
     (47.14594444, 1.185208333, 0.173889e-3), (7.002880556, 0.001860833, -0.18333e-4)),
    ((212.6032194, 58517.80386, 0.001286056), (0.00682069, -0.4774e-4, 0.91e-7),
     0.7233316, (54.38418611, 0.508186111, -0.001386389),
     (75.77964722, 0.89985, 0.00041), (3.393630556, 0.00100583, -0.972e-6)),
    ((319.529425, 19139.8585, 0.000180806), (0.0933129, 0.92064e-4, -0.77e-7),
     1.5236915, (285.4317611, 1.069766667, 0.00013125),
     (48.78644167, 0.770991667, -0.1389e-5), (1.850333333, -0.000675, 0.12611e-4)),
    ((225.4928125, 3033.687936, 0.0), (0.04838144, -0.155e-4, 0.0),
     5.20290493, (273.3930152, 1.33834464, 0.0),
     (99.41984827, 1.05829152, 0.0), (1.3096585, -0.00515613, 0.0)),
    ((174.215296, 1223.507963, 0.0), (0.05422831, -0.00020495, 0.0),
     9.55251745, (338.911673, -0.31667941, 0.0),
     (112.8261394, 0.82587569, 0.0), (2.49080547, -0.00466035, 0.0)),
    ((74.17574887, 427.2742717, 0.0), (0.04681664, 0.00041875, 0.0),
     19.22150505, (95.68630387, 2.05082548, 0.0),
     (73.52220082, 0.52415598, 0.0), (0.77256652, 0.00012824, 0.0)),
    ((30.1329437, 240.4551595, 0.0), (0.00912805, -0.00127185, 0.0),
     30.1137593, (284.168255, -21.6328615, 0.0),
     (130.6841531, 1.10046492, 0.0), (1.77939281, -0.00975088, 0.0)),
    ((229.7810007, 145.1781092, 0.0), (0.24797376, 0.00289875, 0.0),
     39.53903455, (113.5365761, 0.208637761, 0.0),
     (108.94405, 1.37395444, 0.0), (17.15140319, -0.01611824, 0.0)),
]


def ayanamsa(year: int) -> float:
    """Linear ayanamsa of the suite; wraps a full circle in ~25,748 years."""
    return (year - 294) * 151 / 10800


def ayanamsa_value(year: int, rate_arcsec: float | None, zero_year: int) -> float:
    """Suite formula by default; NU's 50.35"/yr-from-Aswini available via rate override."""
    if rate_arcsec is None:
        return ayanamsa(year)
    return (year - zero_year) * rate_arcsec / 3600


def julian_day_number(year: int, month: int, day: float) -> float:
    """The suite's Julian day (noon-based JDN); tolerates overflowed months/days."""
    im = 12 * (year + 4800) + month - 3
    j = (2 * (im - math.floor(im / 12) * 12) + 7 + 365 * im) / 12
    j = math.floor(j) + day + math.floor(im / 48) - 32083
    # >= not > (audit finding 34): the BAS/JS canon's strict test misses the
    # first Gregorian day itself — 1582-10-15 came out 10 days too big and JD
    # ran backward into 10-16. Deliberate one-comparison divergence, on record.
    if j >= 2299171:
        j += math.floor(im / 4800) - math.floor(im / 1200) + 38
    return j


def _norm360(x: float) -> float:
    return x - math.floor(x / 360) * 360


def _poly(coeffs: tuple[float, float, float], t: float) -> float:
    return coeffs[0] + coeffs[1] * t + coeffs[2] * t * t


def _anp(px: float) -> float:
    """Arcseconds to degrees, wrapped to a circle, sign-preserving (BASIC ANP)."""
    if px == 0:
        return 0.0
    a = abs(px) / 3600
    return math.copysign((a / 360 - math.floor(a / 360)) * 360, px)


def _co930(r: float, a: float) -> tuple[float, float]:
    if a == 0:
        a = 1.74533e-9
    return r * math.cos(a), r * math.sin(a)


def _co950(x: float, y: float) -> tuple[float, float]:
    if y == 0:
        y = 1.74533e-9
    if x == 0:
        x = 1.74533e-9  # BASIC would fault here; guard keeps the same limit behavior
    r = math.sqrt(x * x + y * y)
    a = math.atan(y / x)
    if a < 0:
        a += PI
    if y < 0:
        a += PI
    return r, a


def _midheaven(ra: float, ob_rad: float) -> float:
    """MC per the BASIC :106-111 block: fold RA through CO930/CO950 with cos(OB)."""
    x, y = _co930(1.0, ra)
    x *= math.cos(ob_rad)
    _, a = _co950(x, y)
    return _deg(a)


def _house_cusps(ra: float, lat_rad: float, ob_abs: float, mc: float) -> list[float]:
    """CO960 verbatim: ascensional difference + oblique-ascension chain.

    Cusps 10th..3rd from the trisected semi-arc; 4th..9th as +180 opposites.
    On the equal path (ob_abs = 0) this degenerates exactly as the BASIC does.
    """
    xx = math.sin(ra) * math.tan(ob_abs) * math.tan(lat_rad)
    ad = math.atan(xx / math.sqrt(1 - xx * xx))          # ANX
    oa = ra - ad
    ax = (PI / 2 + ad) / 3
    hc = [mc]
    for i in range(1, 6):
        ko = _rad(_norm360(_deg(oa + ax * i)))
        aa = math.atan(math.tan(lat_rad) / math.cos(ko))
        ab = aa + ob_abs
        lo = math.atan(math.tan(ko) * math.cos(aa) / math.cos(ab))
        if lo < 0:
            lo += PI
        if math.sin(ko) < 0:
            lo += PI
        hc.append(_deg(lo))
    return ([_norm360(c) for c in hc]
            + [_norm360(c + 180) for c in hc])


def _ascendant(ra: float, lat_rad: float, obliquity_rad: float) -> float:
    """Oblique-ascension Ascendant (the FLAG=2 pass of the BASIC AZ55 block)."""
    ob = -obliquity_rad
    x, y = _co930(1.0, lat_rad)              # cos(lat), sin(lat)
    q, r1 = y, x
    x, y = _co930(r1, ra)                    # cos(lat)*cos(RA), cos(lat)*sin(RA)
    g = x
    r2, a = _co950(y, q)
    a += ob
    x2, _ = _co930(r2, a)
    _, a3 = _co950(g, x2)
    if a3 < 0:
        a3 += 2 * PI
    return _norm360(_deg(a3) + 90)


def compute_raw(year: int, month: int, day: float, local_hours: float,
                engine_gmt: float, engine_longitude: float, latitude_north: float,
                sidereal: bool, equal_houses: bool,
                ayanamsa_rate: float | None = None,
                ayanamsa_zero: int = 294) -> ChartResult:
    f = (local_hours + engine_gmt) / 24          # UT fraction of day
    lat_rad = _rad(latitude_north)
    j = julian_day_number(year, month, day)
    # The ayanamsa year follows the ACTUAL instant: sweeps advance time by
    # field overflow, and the BASIC's YR is always the current calendar year
    # (audit batch 2 — frozen-ayanamsa fix). Identical for normally-dated
    # charts, so oracle parity is untouched.
    if sidereal:
        from .grid import jd_to_calendar
        year_eff = jd_to_calendar(math.floor(j + f))[0]
        nam = ayanamsa_value(year_eff, ayanamsa_rate, ayanamsa_zero)
    else:
        nam = 0.0
    t = ((j - 2415020) + f - 0.5) / 36525

    # Local sidereal time -> RA of the east point, less the ayanamsa.
    rg = (23925.836 + 8640184.542 * t + 0.0929 * t * t) / 3600
    rg = (rg + f * 24) / 24
    gmst = (rg - math.floor(rg)) * 360
    ux = ((rg - math.floor(rg)) * 24) * 15 - engine_longitude
    ra = _rad(_norm360(ux - nam))
    obliquity_real = 23.45229444 - 0.0130125 * t

    # Equal houses run the Ascendant with OB=0, exactly as the BASIC E-path does.
    ob_house = 0.0 if equal_houses else _rad(23.45229444 - 0.0130125 * t)
    asc = _ascendant(ra, lat_rad, ob_house)
    mc = _midheaven(ra, ob_house)
    cusps = _house_cusps(ra, lat_rad, abs(ob_house), mc)
    # ST$ block (:134-144): RA back to degrees, southern-hemisphere 180 flip,
    # ayanamsa restored — the sidereal time the suite prints.
    st_deg = _deg(ra)
    if latitude_north < 0:
        st_deg = _norm360(st_deg + 180)
    sidereal_time_deg = st_deg + nam

    positions: dict[str, BodyPosition] = {}
    m1 = c1_rad = x1 = y1 = z1 = 0.0
    for index, (name, el) in enumerate(zip(PLANET_NAMES, PLANET_ELEMENTS), start=1):
        m = _rad(_norm360(_poly(el[0], t)))
        e = _poly(el[1], t)
        ea = m
        for _ in range(5):
            ea = m + e * math.sin(ea)
        au = _rad(el[2])   # BASIC quirk: AU pushed through ANR; angle-invariant
        rv = au * (1 - e * math.cos(ea))
        x = au * (math.cos(ea) - e)
        y = au * math.sin(ea) * math.sqrt(1 - e * e)
        _, a = _co950(x, y)
        a_deg = _deg(a) + _poly(el[3], t)
        s_node = _poly(el[4], t)
        v = _norm360(a_deg + s_node)
        m_node = _rad(s_node)
        b = _rad(v)
        inc = _rad(_poly(el[5], t))
        a2 = math.atan(math.cos(inc) * math.tan(b - m_node))
        if a2 < 0:
            a2 += PI
        c = _deg(a2 + m_node)
        if abs(v - c) > 10:
            c -= 180
        c = _norm360(c)
        c_rad = _rad(c)
        d = math.atan(math.sin(c_rad - m_node) * math.tan(inc))
        retro = False
        if index > 1:
            xx = ((rv ** 0.5 + m1 ** 0.5) * (m1 ** 0.5 * rv ** 0.5)) / (rv ** 1.5 + m1 ** 1.5)
            retro = (xx - math.cos(c1_rad - c_rad)) < 0
        x = rv * math.cos(d) * math.cos(c_rad)
        y = rv * math.cos(d) * math.sin(c_rad)
        z = rv * math.sin(d)
        if index == 1:
            m1, c1_rad = rv, c_rad
            x1, y1, z1 = x, y, z
            sun = _norm360(_deg(c1_rad) + 180 - nam)
            positions["Sun"] = BodyPosition(name="Sun", longitude=sun, retrograde=False,
                                            distance=rv)
        else:
            xg, yg, zg = x - x1, y - y1, z - z1
            _, geo = _co950(xg, yg)
            c_geo = _norm360(_deg(geo) - nam)
            beta = _deg(math.atan(zg / math.sqrt(xg * xg + yg * yg)))
            positions[name] = BodyPosition(name=name, longitude=c_geo, retrograde=retro,
                                           ecliptic_latitude=beta,
                                           distance=math.sqrt(xg * xg + yg * yg + zg * zg))

    # Truncated Brown lunar theory (arcseconds), then node and Ketu.
    ll = 973563 + 1732564379 * t - 4 * t * t
    g = 1012395 + 6189 * t + 1.6 * t * t
    g1 = 1203586 + 14648523 * t - 37 * t * t
    nn = 933060 - 6962911 * t + 7.5 * t * t
    dd = 1262655 + 1602961611 * t - 5 * t * t
    lm = (ll - g1) / 3600
    l1 = ((ll - dd) - g) / 3600
    ff = (ll - nn) / 3600
    d2 = dd / 3600
    x2 = 2 * d2

    def s(deg: float) -> float:
        return math.sin(_rad(deg))

    ml = (22639.6 * s(lm) - 4568.4 * s(lm - x2) + 2369.89 * s(x2) + 769 * s(2 * lm)
          - 668.9 * s(l1) - 411.6 * s(2 * ff) - 211.7 * s(2 * lm - x2)
          - 206.2 * s(lm + l1 - 2 * d2)
          + 191.9 * s(lm + x2) - 165.4 * s(l1 - x2) + 147.9 * s(lm - l1) - 124.8 * s(d2)
          - 109.8 * s(lm + l1) - 55.2 * s(2 * ff - x2) - 45.1 * s(lm + 2 * ff)
          + 39.5 * s(lm - 2 * ff)
          - 38.4 * s(lm - 4 * d2) + 36.1 * s(3 * lm) - 30.8 * s(2 * lm - 4 * d2)
          - 28.5 * s(lm - l1 - 2 * d2))

    moon = _norm360(_anp(ll + ml) - nam)
    rahu = _norm360(_norm360(_anp(nn)) - nam)
    ketu = _norm360(rahu + 180)

    positions["Moon"] = BodyPosition(name="Moon", longitude=moon, retrograde=False)
    positions["Rahu"] = BodyPosition(name="Rahu", longitude=rahu, retrograde=False)
    positions["Ketu"] = BodyPosition(name="Ketu", longitude=ketu, retrograde=False)
    positions["Ascendant"] = BodyPosition(name="Ascendant", longitude=asc, retrograde=False)

    ordered = {name: positions[name] for name in BODY_ORDER}
    return ChartResult(positions=ordered, ayanamsa=nam, jd=j + f - 0.5,
                       gmst=gmst, obliquity=obliquity_real, mc=mc, cusps=cusps,
                       sidereal_time_deg=sidereal_time_deg)


def compute_chart(moment: ChartMoment, hour_offset: float = 0.0) -> ChartResult:
    return compute_raw(moment.year, moment.month, moment.day,
                       moment.local_decimal_hours + hour_offset,
                       moment.engine_gmt_hours, moment.engine_longitude,
                       moment.latitude_north, moment.sidereal, moment.equal_houses,
                       moment.ayanamsa_rate_arcsec, moment.ayanamsa_zero_year)
