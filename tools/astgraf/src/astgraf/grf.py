# ABOUTME: Reader for the heritage ASTROC.GRF format (ASTGRAF.BAS's output, GRAPHDO's
# ABOUTME: input) — header (date | step count time unit) plus 13-body rows, DR order.

from pydantic import BaseModel

from .ephemeris import BODY_ORDER


class GrfFile(BaseModel):
    day: int
    month: int
    year: int
    step: float
    count: int              # the BAS's mxpr (rows written = count, pre-incremented)
    local_hours: float      # unpacked from the BAS's HH.MM TIM field
    unit: str               # Y | M | D | H
    rows: list[dict[str, float]]


def _unpack_hhmm(tim: float) -> float:
    """The BAS packs 5:30 as 5.30; ANQ unpacks to decimal hours."""
    hours = int(tim)
    return hours + round((tim - hours) * 100) / 60.0


def load_grf(path: str) -> GrfFile:
    with open(path, encoding="latin-1") as fh:
        lines = [ln.rstrip() for ln in fh if ln.strip()]
    head = lines[0].split()
    # ASTGRAF writes: dday mmon yyear | PPE mxpr TIM PPER$
    day, month, year = int(head[0]), int(head[1]), int(head[2])
    step, count, tim, unit = (float(head[3]), int(head[4]), float(head[5]),
                              head[6].upper())
    rows = []
    for line in lines[2:]:                      # skip the "Per Asc Sun ..." header
        parts = line.split()
        if len(parts) < 14:
            continue
        values = [float(v) for v in parts[1:14]]
        rows.append(dict(zip(BODY_ORDER, values)))
    return GrfFile(day=day, month=month, year=year, step=step, count=count,
                   local_hours=_unpack_hhmm(tim), unit=unit, rows=rows)
