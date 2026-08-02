# ABOUTME: RASI and NAVAMSAM box charts (South-Indian square) exactly as the
# ABOUTME: ASTROLOG.BAS HOROSCOPE subroutine prints them — the QUAKE.pdf layout.

# Verbatim port of ASTROLOG.BAS 6120-6880: the AR() square walk, the 4-char
# ZODIAC slot fields, the 15-char ASCEND field, the center label row, and the
# NVM$ slot 7-9 blanking (no Ura/Nep/Plu in the NAVAMSAM chart). ASCII "|"/"-"
# stand in for the BAS's CP437 border glyphs.
from .horary import SIGNS_12, star_position

# C$ body order = box slots 1..12 (ASTROLOG.BAS DATA 3850-3870), Asc = slot 13.
SLOT_NAMES = ["Sun", "Mer", "Ven", "Mar", "Jup", "Sat", "Ura", "Nep", "Plu",
              "Moo", "Rah", "Ket", "Asc"]
SLOT_BODIES = ["Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus",
               "Neptune", "Pluto", "Moon", "Rahu", "Ketu", "Ascendant"]
# AR(): chart order of houses in the square (DATA 12,1,2,3,11,4,10,5,9,8,7,6).
AR_ORDER = [12, 1, 2, 3, 11, 4, 10, 5, 9, 8, 7, 6]

_FULL = "+" + "-" * 67 + "+"                 # W5/W9 border


def _placements(positions: dict[str, float], navamsam: bool) -> dict[int, list[str]]:
    """Fill RAS$/NVM$: sign (1..12 = Ari..Pis) -> 13 slot fields."""
    cells = {k: [""] * 13 for k in range(1, 13)}
    for slot, body in enumerate(SLOT_BODIES):
        if body not in positions:
            continue
        if navamsam and slot in (6, 7, 8):   # ASTROLOG.BAS 6550: NVM$ 7-9 blank
            continue
        lon = positions[body] % 360.0
        if navamsam:
            sign = SIGNS_12.index(star_position(lon).navam) + 1
        else:
            sign = int(lon // 30) + 1
        cells[sign][slot] = SLOT_NAMES[slot]
    return cells


def _cell(cells: dict[int, list[str]], k: int, a: int) -> str:
    if a == 12:                              # ASCEND: USING "\             \ "
        return f"{cells[k][12]:<15.15} "
    return "".join(f"{cells[k][a + j]:<4.4}" for j in range(4))   # ZODIAC


def render_box_lines(positions: dict[str, float], navamsam: bool) -> list[str]:
    cells = _placements(positions, navamsam)
    title = "NAVAMSAM " if navamsam else "  RASI   "
    lines = [_FULL]

    def band(ks: list[int]) -> None:
        for a in (0, 4, 8, 12):
            lines.append("".join("|" + _cell(cells, k, a) for k in ks) + "|")

    def mid(left: int, right: int) -> None:
        for a in (0, 4, 8, 12):
            lines.append("|" + _cell(cells, left, a) + "|" + " " * 33
                         + "|" + _cell(cells, right, a) + "|")

    band(AR_ORDER[0:4])
    lines.append(_FULL)
    mid(AR_ORDER[4], AR_ORDER[5])
    lines.append("|" + "-" * 16 + "|" + " " * 12 + title + " " * 12
                 + "|" + "-" * 16 + "|")
    mid(AR_ORDER[6], AR_ORDER[7])
    lines.append(_FULL)
    band(AR_ORDER[8:12])
    lines.append(_FULL)
    return lines


def render_rasi_navamsam(positions: dict[str, float], label: str) -> str:
    lines = [label, ""]
    lines += render_box_lines(positions, navamsam=False)
    lines.append("")
    lines += render_box_lines(positions, navamsam=True)
    return "\n".join(lines) + "\n"
