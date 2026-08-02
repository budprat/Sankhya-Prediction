# ABOUTME: The full horoscope report page exactly as ASTROLOG.BAS writes it (the
# ABOUTME: QUAKE.pdf printout): header, cusp table, planet table, Dasa/Bukti, boxes.

# Verbatim port of the ASTROLOG.BAS report layer: CO920 (deg/sign/min split with
# its round-to-tenth-then-floor minutes), OWH (LUCK rulership column), the DASA
# subroutine (5840-6030), and the PRINT USING masks of 6940-7360. The RASI and
# NAVAMSAM boxes (rasi.py) close the page as the BAS HOROSCOPE subroutine does.
from .horary import LORD_CYCLE, SIGNS_12, star_position
from .models import ChartMoment, ChartResult
from .rasi import SLOT_BODIES, SLOT_NAMES, render_box_lines

# Vimshottari BR/RT pairs (ASTGRAF.BAS DATA :346): lord slot in C$, period years.
# BR order == LORD_CYCLE (Ketu..Mercury); RT are the Vimshottari year spans.
RT_YEARS = [7, 20, 6, 10, 7, 18, 16, 19, 17]
LORD_ABBREV = {"Ketu": "Ket", "Venus": "Ven", "Sun": "Sun", "Moon": "Moo",
               "Mars": "Mar", "Rahu": "Rah", "Jupiter": "Jup", "Saturn": "Sat",
               "Mercury": "Mer"}

# LUCK(12,4) rulership table (ASTGRAF.BAS DATA :352-353), rows in C$ slot order:
# columns = ruler, ruler, exalted, weak (sign numbers 1..12, 0 = none).
LUCK = [(5, 5, 1, 7), (3, 3, 6, 12), (2, 7, 12, 6), (1, 8, 10, 4),
        (9, 12, 4, 10), (10, 11, 7, 1), (11, 11, 8, 2), (12, 12, 5, 11),
        (8, 8, 0, 2), (4, 4, 2, 8), (0, 0, 2, 8), (0, 0, 8, 2)]

HOUSE_NAMES = ["Tenth", "Eleventh", "Twelth", "First", "Second", "Third",
               "Fourth", "Fifth", "Sixth", "Seventh", "EightH", "Ninth"]


def _sfield(s: str, width: int) -> str:
    return s[:width].ljust(width)


def co920(z: float) -> tuple[int, int, int]:
    """CO920: absolute degrees -> (sign 1..12, deg-in-sign, minutes).

    The ANW round-to-2dp before the final INT is load-bearing: without it,
    float residue turns 8.0 into 7 at sign boundaries.
    """
    z3 = int(z)
    q = int(z3 / 30) + 1
    wx = (z3 / 30 - int(z3 / 30)) * 30
    wx = int(wx * 100 + 0.5) / 100                     # ANW
    z1 = int(wx)
    z2 = int(int(((z - z3) * 60) * 10 + 0.5) / 10)
    return q, z1, z2


def ruler_status(slot: int, sign: int) -> str:
    """OWH (ASTROLOG.BAS 5520-5650): slot is the 1-based C$ index; 13 = Asc."""
    if slot == 13:
        return ""
    for j, val in enumerate(LUCK[slot - 1], start=1):
        if sign == val:
            return {1: "RULER", 2: "RULER", 3: "EXALTED", 4: "WEAK"}[j]
    return ""


def dasa_bukti(moon_longitude: float) -> tuple[tuple[str, int, int, int],
                                               tuple[str, int, int, int]]:
    """DASA subroutine (ASTROLOG.BAS 5840-6030) from the Moon's longitude."""
    a = moon_longitude % 360.0
    starcount = star_position(a).starcount
    bbl = ((starcount * 40) / 3 - a) / 40 * 3
    tos = starcount - int(starcount / 9) * 9
    if tos == 0:
        tos = 9
    dasa_lord = LORD_ABBREV[LORD_CYCLE[tos - 1]]
    bb = bbl * RT_YEARS[tos - 1]
    dyr = int(bb)
    dm = (bb - dyr) * 12
    dmt = int(dm)
    ddy = int((dm - dmt) * 30)
    bca = (1 - bbl) * 9
    hca = int(bca) + 1
    bukti_lord = LORD_ABBREV[LORD_CYCLE[hca - 1]]
    buk = (hca - bca) * RT_YEARS[hca - 1] * (RT_YEARS[tos - 1] / 120)
    byr = int(buk)
    bkl = (buk - byr) * 12
    bmt = int(bkl)
    bdy = int((bkl - bmt) * 30)
    return (dasa_lord, dyr, dmt, ddy), (bukti_lord, byr, bmt, bdy)


def sidereal_hms(sd_deg: float) -> tuple[int, int, int]:
    """The report's sidereal digits (ASTROLOG.BAS 1800-1830 + USING mask).

    SMZ keeps the UNROUNDED float minutes and PRINT USING "##" rounds it,
    while the seconds are cut from the same unrounded value — so the printout
    can show minutes one higher than the truncated value (QUAKE.pdf's
    "2 H 6 M 47 S" is truly 2h 5m 47.2s). Reproduced verbatim.
    """
    x = sd_deg / 15
    h = int(x)
    z = (x - h) * 60
    s = int((z - int(z)) * 60)
    return h, int(z + 0.5), s


def _dm(value: float) -> tuple[int, int]:
    v = abs(value)
    d = int(v)
    return d, int(round((v - d) * 60))


def _header(moment: ChartMoment, chart: ChartResult, name: str,
            place: str) -> list[str]:
    h24 = moment.hour
    ampm = "AM" if h24 < 12 else "PM"
    h12 = h24 % 12 or 12
    gd, gm = _dm(moment.longitude_east)
    td, tm = _dm(moment.latitude_north)
    zh, zm = _dm(moment.utc_offset_hours)
    sh, sm, ss = sidereal_hms(chart.sidereal_time_deg)
    return [
        " " * 33 + " Horoscope ",
        " " * 33 + " _________",
        "",
        f"  Full name..: {_sfield(name, 24)}"
        f"  Place of birth...: {_sfield(place, 14)} ",
        f"  Date of birth ...:  "
        f"{_sfield(f'{moment.day:02d}-{moment.month:02d}-{moment.year}', 16)} "
        f"  Time of birth ...: {h12:2d} H {moment.minute:2d} M.  "
        f"{_sfield(ampm, 5)}",
        f"  Longitude .......:  {gd:2d} d {gm:2d} M.  "
        f"{_sfield('East' if moment.longitude_east >= 0 else 'West', 5)}"
        f"  Latitude ........: {td:2d} d {tm:2d} M.  "
        f"{_sfield('North' if moment.latitude_north >= 0 else 'South', 5)}",
        f"  Time zone (GMT)..:  {zh:2d} H {zm:2d} M.  "
        f"{_sfield('East' if moment.utc_offset_hours >= 0 else 'West', 5)}"
        f"  Siderial time....: {sh:2d} H {sm:2d} M {ss:2d} S",
        f"  Ayanamsa.........:  {chart.ayanamsa:6.3f} ",
        "",
    ]


def _cusp_table(chart: ChartResult) -> list[str]:
    lines = [" " * 19 + " The house cusps  in degrees and minutes", ""]
    for i in range(6):
        row = ""
        for k in (i, i + 6):
            q, z1, z2 = co920(chart.cusps[k])
            row += (f" {_sfield(HOUSE_NAMES[k], 7)} "
                    f" {z1:2d} deg {_sfield(SIGNS_12[q - 1], 4)}{z2:2d} min  "
                    f"{chart.cusps[k]:5.1f}")
            if k == i:
                row = row.ljust(39)
        lines.append(row)
    lines.append("")
    return lines


def _planet_table(chart: ChartResult) -> list[str]:
    lines = ["    House cusps    Planets/deg  Retro  Ruler    "
             " Nakshatra        Pada Navam ", ""]
    order = ["Ascendant", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus",
             "Saturn", "Rahu", "Ketu", "Uranus", "Neptune", "Pluto"]  # DR(:345)
    for body in order:
        p = chart.positions[body]
        lon = p.longitude
        q, z1, z2 = co920(lon)
        s = star_position(lon)
        slot = SLOT_BODIES.index(body) + 1
        retro = "R " if p.retrograde else "  "
        lines.append(
            f" {z1:2d} deg {_sfield(SIGNS_12[q - 1], 3)} {z2:2d} min "
            f" {_sfield(SLOT_NAMES[slot - 1], 4)}  {lon:5.1f}   "
            f"{retro}{_sfield(ruler_status(slot, q), 10)} "
            f" {_sfield(s.nakshatra, 15)}  {s.pada:3d}  {_sfield(s.navam, 5)} ")
    lines.append("")
    return lines


def render_report(chart: ChartResult, moment: ChartMoment, name: str = "",
                  place: str = "") -> str:
    positions = {n: p.longitude for n, p in chart.positions.items()}
    moon = positions["Moon"]
    (dl, dy, dm_, dd), (bl, by, bm, bd) = dasa_bukti(moon)
    ms = star_position(moon)
    lines = _header(moment, chart, name, place)
    lines += _cusp_table(chart)
    lines += _planet_table(chart)
    lines.append(f"      Dasa at birth {dl}  {dy}  {dm_} {dd} "
                 f"       Bukti at birth {bl}  {by}  {bm}  {bd}")
    lines.append("")
    lines.append(f"      Nakshatra at birth :{ms.nakshatra}  {ms.pada}")
    lines.append("")
    lines += render_box_lines(positions, navamsam=False)
    lines.append("")
    lines += render_box_lines(positions, navamsam=True)
    return "\n".join(lines) + "\n"
