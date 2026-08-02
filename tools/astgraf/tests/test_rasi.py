# ABOUTME: Tests the RASI/NAVAMSAM box-chart renderer against the QUAKE.pdf printout:
# ABOUTME: placements, fixed-slot columns, geometry, and the BAS's outer-planet omission.

from astgraf.rasi import AR_ORDER, render_box_lines, render_rasi_navamsam

# The QUAKE.pdf planet table (ayanamsa 0.000): name -> longitude.
QUAKE_POSITIONS = {
    "Ascendant": 129.0, "Sun": 34.7, "Moon": 116.4, "Mars": 48.0,
    "Mercury": 50.6, "Jupiter": 133.0, "Venus": 75.7, "Saturn": 243.6,
    "Rahu": 188.9, "Ketu": 8.9, "Uranus": 17.6, "Neptune": 339.5,
    "Pluto": 285.9,
}


def _bands(lines):
    """Split a 21-line box into cell texts keyed by AR position."""
    assert len(lines) == 21
    cells = {}
    for i in range(4):                       # top band: AR[0..3]
        cells[AR_ORDER[i]] = [lines[1 + a][1 + 17 * i:17 + 17 * i] for a in range(4)]
    cells[AR_ORDER[4]] = [lines[6 + a][1:17] for a in range(4)]    # mid1 left
    cells[AR_ORDER[5]] = [lines[6 + a][52:68] for a in range(4)]   # mid1 right
    cells[AR_ORDER[6]] = [lines[11 + a][1:17] for a in range(4)]   # mid2 left
    cells[AR_ORDER[7]] = [lines[11 + a][52:68] for a in range(4)]  # mid2 right
    for i in range(4):                       # bottom band: AR[8..11]
        cells[AR_ORDER[8 + i]] = [lines[16 + a][1 + 17 * i:17 + 17 * i]
                                  for a in range(4)]
    return {k: "\n".join(v) for k, v in cells.items()}


def test_rasi_box_matches_quake_pdf():
    lines = render_box_lines(QUAKE_POSITIONS, navamsam=False)
    assert all(len(line) == 69 for line in lines)
    cells = _bands(lines)
    # Signs 1..12 = Ari..Pis. PDF RASI: Nep in Pis, Ura+Ket in Ari,
    # Sun+Mer+Mar in Tau, Ven in Gem, Moo in Can, Jup+Asc in Leo,
    # Rah in Lib, Sat in Sag, Plu in Cap; Aqu/Vir/Sco empty.
    assert "Nep" in cells[12] and "Ura" in cells[1] and "Ket" in cells[1]
    # Fixed slot columns (BAS USING "\  \" fields): Ven's slot stays blank.
    assert cells[2].splitlines()[0] == "Sun Mer     Mar "
    assert "Ven" in cells[3]
    assert "Moo" in cells[4] and "Jup" in cells[5] and "Asc" in cells[5]
    assert "Rah" in cells[7] and "Sat" in cells[9] and "Plu" in cells[10]
    for empty_sign in (6, 8, 11):
        assert cells[empty_sign].strip() == ""
    assert "  RASI   " in lines[10]


def test_navamsam_box_matches_quake_pdf_and_omits_outers():
    lines = render_box_lines(QUAKE_POSITIONS, navamsam=True)
    cells = _bands(lines)
    text = "\n".join(lines)
    # PDF NAVAMSAM: Sat in Tau; Mar+Ket+Asc in Gem; Mer+Jup in Can;
    # Sun+Ven+Moo in Aqu; Rah in Sag.
    assert "Sat" in cells[2]
    assert "Mar" in cells[3] and "Ket" in cells[3] and "Asc" in cells[3]
    assert "Mer" in cells[4] and "Jup" in cells[4]
    assert "Sun" in cells[11] and "Ven" in cells[11] and "Moo" in cells[11]
    assert "Rah" in cells[9]
    # ASTROLOG.BAS 6550 blanks slots 7-9: no Ura/Nep/Plu in the NAVAMSAM chart
    # (QUAKE.pdf page 2 confirms — Vir would hold Ura+Nep, and stays empty).
    assert "Ura" not in text and "Nep" not in text and "Plu" not in text
    assert cells[6].strip() == ""
    assert "NAVAMSAM " in lines[10]


def test_render_handles_missing_bodies_and_sign_boundary():
    # Failure/edge case: partial position set must not crash; 30.0 deg is Tau.
    out = render_rasi_navamsam({"Sun": 30.0}, "edge")
    lines = out.splitlines()
    assert lines[0] == "edge"
    rasi_lines = lines[2:23]
    assert all(len(line) == 69 for line in rasi_lines)
    assert "Sun" in _bands(rasi_lines)[2]
