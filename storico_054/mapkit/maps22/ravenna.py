"""Ravenna (34,96) 80x62 — city of mosaics. Piazza del Popolo with the Palazzo Comunale and the two Venetian
columns, the Tomba di Dante in the Zona del Silenzio, San Vitale and the Mausoleo di Galla Placidia, Sant'Apollinare
Nuovo with its round campanile, the Mausoleo di Teodorico in the park, the station (trains to Lugo), the mosaic
atelier, the Darsena: the canal runs east to the sea (Mare di Ravenna, with the offshore platform)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import art, art22, decor, imports, r22
from art import C
from canvas import G
from decor import rect
from _town import tree, lamp, bench, terrace, fill_lawns

GN = (34, 96)
TS = 'r22_ravenna'
W, H = 80, 62
STARTS = [(19, 61)]
HEAL = 7
CANAL = (47, 51)          # water rows of the Darsena, open to the east edge


def build():
    cv = r22.RCanvas(W, H, GN)
    fam, cob = imports.cobbles(imports.warm_stone)
    paved = rect(2, 33, 76, 4)                                   # corso
    paved |= rect(18, 37, 4, 25)                                 # road south (exit)
    paved |= rect(2, 16, 76, 2)                                  # via north
    paved |= rect(32, 2, 2, 31) | rect(52, 2, 2, 31)
    paved |= rect(8, 18, 24, 15)                                 # Piazza del Popolo
    paved |= rect(56, 44, 22, 2)                                 # quay of the Darsena (north side)
    paved |= rect(34, 38, 2, 9) | rect(52, 37, 2, 7)
    cv.paint_family(fam, cob, paved)
    c0, c1 = CANAL
    cv.fill(56, c0, 24, c1 - c0 + 1, 'sea')
    rim_t, rim_b = art.quay_rim(True), art.quay_rim(False)
    for x in range(56, W):
        cv.place_art(x, c0 - 1, dict(img=rim_t, solid=set(), door=None))
    for i, bx in enumerate((58, 74)):
        sail, hull = (('orange', (41, 99, 165)), ('red', (57, 140, 90)))[i % 2]
        cv.place_art(bx, c0, dict(img=decor.asset('boat', art.boat, sail, hull), solid=rect(0, 0, 3, 3), door=None), overlay=True)
    cv.place_art(64, c0, art22.motonave(), protect=True)          # the ferry to the legendary islands
    doors, locked = {}, []
    # ---------------- Piazza del Popolo
    doors['comune'] = cv.place_art(12, 10, art.palazzo_comunale(9, 'brick', name='COMUNE', tower=False), protect=True)
    for x in (13, 27):
        cv.place_art(x, 19, art22.venetian_column(), top_rows=3, protect=True)
    for (x, y) in ((10, 22), (29, 22), (10, 30), (29, 30)):
        lamp(cv, x, y)
    for (x, y) in ((16, 27), (20, 27), (24, 27)):
        bench(cv, x, y)
    # ---------------- Tomba di Dante, Zona del Silenzio
    doors['dante'] = cv.place_art(37, 21, art22.dante_tomb(), protect=True)
    cv.hedge(cv.hline_cells(35, 26, 3) + cv.hline_cells(39, 26, 3))
    for (x, y) in ((35, 20), (41, 20)):
        tree(cv, x, y, seed=3)
    # ---------------- San Vitale and Galla Placidia (north)
    locked.append(cv.place_art(35, 5, art22.san_vitale(), protect=True))
    locked.append(cv.place_art(44, 9, art22.galla_placidia(), protect=True))
    # ---------------- Mausoleo di Teodorico in the park (east)
    doors['teodorico'] = cv.place_art(62, 6, art22.teodorico(), protect=True)
    for (x, y) in ((57, 3), (59, 9), (70, 4), (72, 10), (57, 12), (75, 7)):
        tree(cv, x, y, seed=3)
    # ---------------- Sant'Apollinare Nuovo and the station for Lugo
    locked.append(cv.place_art(55, 24, art22.apollinare(), protect=True))
    doors['lugo'] = cv.place_art(66, 26, art.shopfront(5, 'STAZIONE', 'cream', awning='blue', floors=1))
    # houses
    doors['h10'] = cv.place_art(3, 4, decor.asset('house', art.house, 4, 2, 'pink', roof='roof_brown', shutters='brown_sh', balcony=True, seed=1))
    doors['h11'] = cv.place_art(26, 4, decor.asset('house', art.house, 4, 2, 'cream', roof='roof', shutters='green_sh', balcony=True, seed=1))
    locked += terrace(cv, 8, 24, 7, 0)
    locked += terrace(cv, 70, 78, 15, 2)
    # ---------------- south of the corso
    doors['pc'] = decor.general_building(cv, 5, 38, decor.PC)
    doors['mart'] = decor.general_building(cv, 11, 38, decor.MART)
    doors['gym'] = decor.general_building(cv, 44, 37, decor.GYM)
    doors['mosaici'] = cv.place_art(36, 39, art.shopfront(4, 'MOSAICI', 'ochre', awning='green', floors=1))
    doors['darsena'] = cv.place_art(58, 39, decor.asset('house', art.house, 4, 2, 'ochre', roof='roof', shutters='green_sh', balcony=True, seed=1))
    locked += terrace(cv, 64, 78, 42, 0)
    locked += terrace(cv, 2, 18, 57, 1)
    locked += terrace(cv, 22, 54, 57, 2)
    for (x, y) in ((8, 32), (28, 37), (40, 32), (50, 37), (60, 32), (70, 32)):
        lamp(cv, x, y)
    # borders (the canal stays open to the east edge)
    border = rect(0, 0, W, 2) | rect(0, 2, 2, 58) | rect(78, 2, 2, c0 - 3) | rect(78, c1 + 1, 2, H - c1 - 1) | rect(0, H - 2, 18, 2) | rect(22, H - 2, 58, 2)
    border |= rect(56, c1 + 1, 22, H - c1 - 3)
    decor.woods(cv, border, seed=96, pine_ratio=0.6, gaps=0.0)
    # ---------------- events (same order as 0.21)
    order = {2: 'dante', 3: 'teodorico', 4: 'comune', 5: 'pc', 6: 'mart', 7: 'mosaici', 10: 'h10', 11: 'h11', 12: 'darsena', 13: 'gym', 14: 'lugo'}
    for i, k in order.items():
        cv.set_warp(i, *doors[k])
    cv.place_objs({1: (23, 43), 2: (36, 27), 3: (60, 15), 4: (22, 21), 5: (40, 43), 6: (49, 42), 7: (30, 52), 8: (65, 31)})
    b = cv.bbgs
    b[0]['x'], b[0]['y'] = doors['dante'][0] - 2, doors['dante'][1] + 1
    b[1]['x'], b[1]['y'] = doors['teodorico'][0] - 2, doors['teodorico'][1] + 1
    b[2]['x'], b[2]['y'] = 9, 19
    b[3]['x'], b[3]['y'] = doors['gym'][0] - 3, doors['gym'][1] + 1
    b[4]['x'], b[4]['y'] = doors['lugo'][0] - 3, doors['lugo'][1] + 1
    for bb in b:
        cv.put(bb['x'], bb['y'], G['sign'], 1, 3)
    fill_lawns(cv, rect(2, 18, 6, 14) | rect(34, 28, 18, 4) | rect(2, 46, 16, 8) | rect(22, 46, 32, 8) | rect(54, 18, 22, 5) | rect(2, 2, 30, 1), seed=96)
    cv.add_obj(67, 45, 49, 'R22_Motonave', move=8)                 # the ferry's sailor on the quay
    for d in locked:
        if d: cv.locked(d)
    cv.heal = (doors['pc'][0], doors['pc'][1] + 1)
    cv.border = [0x1D4, 0x1D5, 0x1DC, 0x1DD]
    cv.doors = doors
    return cv
