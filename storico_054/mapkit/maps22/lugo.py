"""Lugo (34,110) 76x60 — the Rocca Estense, the Pavaglione (the great 18th-century arcaded square of the silk
market), Piazza Baracca with the Monumento a Francesco Baracca (the stone wing), the Teatro Rossini, the Museo
Baracca with the SPAD VII; north the road to the Villa San Martino airfield, south to Ravenna, west the bridge
towards Imola."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import art, art22, decor, imports, r22
from art import C
from canvas import G
from decor import rect
from _town import tree, lamp, bench, terrace, fill_lawns

GN = (34, 110)
TS = 'r22_lugo'
W, H = 76, 60
STARTS = [(37, 59)]
HEAL = 15


def build():
    cv = r22.RCanvas(W, H, GN)
    fam, cob = imports.cobbles(imports.warm_stone)
    paved = rect(35, 0, 4, 60)                                   # corso (airfield <-> Ravenna)
    paved |= rect(0, 28, 76, 4)                                  # via Emilia-Romagna (west: Imola bridge)
    paved |= rect(40, 7, 18, 9)                                  # Pavaglione courtyard
    paved |= rect(19, 16, 15, 12)                                # Piazza Baracca
    paved |= rect(2, 16, 17, 2) | rect(39, 18, 36, 2)
    paved |= rect(20, 32, 2, 18) | rect(52, 32, 2, 18) | rect(2, 46, 72, 2)
    cv.paint_family(fam, cob, paved)
    doors, locked = {}, []
    # ---------------- Rocca Estense
    locked.append(cv.place_art(6, 9, art22.rocca(9, 6, keep=True, towers='square', merlons='ghibelline'), protect=True))
    # ---------------- Pavaglione: arcades north and south of the courtyard
    arc = art22.arcade_row(6)
    for x in (40, 46, 52):
        cv.place_art(x, 4, arc, top_rows=0, protect=True)
    for (x, y) in ((42, 9), (55, 9), (42, 14), (55, 14)):
        lamp(cv, x, y)
    for (x, y) in ((45, 12), (49, 12), (53, 12)):
        bench(cv, x, y)
    # ---------------- Piazza Baracca and the monument
    cv.place_art(25, 17, art22.baracca_monument(), protect=True)
    fb = decor.asset('fb1', art.flowerbed, ((239, 99, 132), (255, 206, 66)))
    for (x, y) in ((23, 21), (30, 21), (23, 24), (30, 24)):
        cv.place_art(x, y, dict(img=fb, solid={(0, 0)}, door=None))
    for (x, y) in ((20, 17), (33, 17), (20, 26), (33, 26)):
        lamp(cv, x, y)
    # ---------------- Teatro Rossini, Museo Baracca with the SPAD
    locked.append(cv.place_art(42, 20, art.theatre(6, 'TEATRO ROSSINI'), protect=True))
    doors['museo'] = cv.place_art(56, 20, art.warehouse(6, 'MUSEO BARACCA'))
    cv.place_art(63, 24, art22.plane_spad(), top_rows=1)
    # houses
    locked += terrace(cv, 2, 34, 7, 0)
    locked += terrace(cv, 60, 74, 15, 1)
    locked += terrace(cv, 2, 18, 27, 2)
    # ---------------- south
    doors['pc'] = decor.general_building(cv, 23, 38, decor.PC)
    doors['mart'] = decor.general_building(cv, 29, 38, decor.MART)
    doors['gym'] = decor.general_building(cv, 56, 37, decor.GYM)
    locked += terrace(cv, 40, 52, 44, 0)
    locked += terrace(cv, 2, 34, 56, 1)
    locked += terrace(cv, 40, 74, 56, 2)
    for (x, y) in ((8, 32), (30, 32), (44, 32), (66, 32), (34, 10), (39, 40)):
        lamp(cv, x, y)
    # ---------------- airfield road (north edge), Imola bridge (west edge), Ravenna (south edge)
    border = rect(0, 0, 35, 2) | rect(39, 0, 37, 2) | rect(0, 2, 2, 26) | rect(0, 32, 2, 28) | rect(74, 2, 2, 58) | rect(0, H - 2, 35, 2) | rect(39, H - 2, 37, 2)
    decor.woods(cv, border, seed=110, pine_ratio=0.2, gaps=0.0)
    # ---------------- events (same order as 0.21)
    cv.set_warp(0, 37, H - 1)
    cv.set_warp(1, *doors['museo'])
    cv.set_warp(2, *doors['gym'])
    cv.set_warp(3, 36, 0)
    cv.set_warp(4, *doors['pc'])
    cv.set_warp(5, *doors['mart'])
    cv.set_warp(6, 0, 29)
    cv.place_objs({1: (39, 27), 2: (25, 30), 3: (52, 43), 4: (39, 3), 5: (48, 12)})
    b = cv.bbgs
    pos = [(5, 16), (39, 9), (doors['museo'][0] - 2, doors['museo'][1] + 1), (24, 23), (doors['gym'][0] - 3, doors['gym'][1] + 1),
           (34, 2), (34, 56), (doors['gym'][0] + 3, doors['gym'][1] + 1)]
    for bb, (x, y) in zip(b, pos):
        bb['x'], bb['y'] = x, y
        cv.put(x, y, G['sign'], 1, 3)
    fill_lawns(cv, rect(2, 18, 17, 9) | rect(22, 33, 30, 4) | rect(40, 33, 12, 6) | rect(2, 33, 17, 16) | rect(54, 45, 20, 4) | rect(60, 3, 14, 6), seed=110)
    for d in locked:
        if d: cv.locked(d)
    cv.heal = (doors['pc'][0], doors['pc'][1] + 1)
    cv.border = [0x1D4, 0x1D5, 0x1DC, 0x1DD]
    return cv
