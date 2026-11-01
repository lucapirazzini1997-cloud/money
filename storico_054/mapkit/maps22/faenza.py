"""Faenza (34,85) 80x58 — city of majolica. The Via Emilia crosses it; to the north the long arcaded Piazza del
Popolo with the Palazzo del Podestà and the Torre dell'Orologio, beside it Piazza della Libertà with the
Cattedrale (unfinished brick facade) and the baroque Fontana Monumentale, the pennants of the Palio del Niballo
rioni; the MIC (Museo Internazionale delle Ceramiche), ceramists' workshops with majolica racks; south the
residential blocks with PC/Mart and the Ground gym."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import art, art22, decor, imports, r22
from art import C
from canvas import G
from decor import rect
from _town import tree, lamp, bench, terrace, fill_lawns

GN = (34, 85)
TS = 'r22_faenza'
W, H = 80, 58
STARTS = [(79, 29)]
HEAL = 17


def build():
    cv = r22.RCanvas(W, H, GN)
    fam, cob = imports.cobbles(imports.warm_stone)
    paved = rect(2, 28, 78, 4)                                   # Via Emilia
    paved |= rect(14, 14, 24, 14)                                # Piazza del Popolo
    paved |= rect(40, 14, 22, 14)                                # Piazza della Libertà
    paved |= rect(38, 26, 2, 2)
    paved |= rect(2, 14, 12, 2) | rect(62, 18, 16, 2)             # side streets north
    paved |= rect(12, 32, 2, 22) | rect(32, 32, 2, 22) | rect(46, 32, 2, 22) | rect(62, 32, 2, 22)
    paved |= rect(2, 41, 76, 2)                                  # viale south
    cv.paint_family(fam, cob, paved)
    doors, locked = {}, []
    # ---------------- Piazza del Popolo
    doors['podesta'] = cv.place_art(17, 8, art.palazzo_comunale(9, 'brick', name='PODESTA', tower=False), protect=True)
    locked.append(cv.place_art(27, 10, decor.asset('portici', art.portici, 6, 2, 'ochre', seed=2)))
    cv.place_art(38, 20, art22.clock_tower(), top_rows=1, protect=True)
    for (x, y) in ((16, 17), (35, 17), (16, 25), (35, 25)):
        lamp(cv, x, y)
    for (x, y) in ((20, 22), (24, 22), (28, 22)):
        bench(cv, x, y)
    # ---------------- Piazza della Libertà: Cattedrale and Fontana Monumentale
    doors['duomo'] = cv.place_art(46, 7, art.church(6, 'brick', tower_side='left', rose=False), protect=True)
    cv.place_art(50, 20, dict(img=decor.asset('fountain', art.fountain), solid=rect(0, 0, 2, 2), door=None))
    fb = decor.asset('fb1', art.flowerbed, ((239, 99, 132), (255, 206, 66)))
    for (x, y) in ((48, 19), (53, 19), (48, 22), (53, 22)):
        cv.place_art(x, y, dict(img=fb, solid={(0, 0)}, door=None))
    for (x, y) in ((42, 17), (59, 17), (42, 25), (59, 25)):
        lamp(cv, x, y)
    # Palio del Niballo pennants over the two squares (top layer)
    pen = art22.pennants(4)
    for x0 in (14, 22, 30, 40, 48, 56):
        cv.place_art(x0, 15, dict(img=pen, solid=set(), door=None), top_rows=1)
    # ---------------- MIC and the ceramists
    doors['mic'] = cv.place_art(3, 8, art.warehouse(7, 'MIC FAENZA'), protect=True)
    doors['torniante'] = cv.place_art(64, 13, art.shopfront(4, 'CERAMICHE', 'cream', awning='blue', floors=1))
    rack = art22.majolica_rack()
    for (x, y) in ((68, 16), (70, 16), (2, 16), (4, 40)):
        cv.place_art(x, y, rack)
    # houses north
    locked += terrace(cv, 2, 46, 5, 0)
    locked += terrace(cv, 54, 78, 6, 1)
    locked += terrace(cv, 64, 78, 27, 2)
    # ---------------- south of the Via Emilia
    doors['pc'] = decor.general_building(cv, 15, 34, decor.PC)
    doors['mart'] = decor.general_building(cv, 22, 34, decor.MART)
    doors['gym'] = decor.general_building(cv, 51, 35, decor.GYM)
    doors['bottega'] = cv.place_art(3, 36, art.shopfront(5, 'BOTTEGA CERAMICA', 'ochre', awning='green', floors=1))
    doors['rioni'] = cv.place_art(3, 47, decor.asset('house', art.house, 4, 2, 'pink', roof='roof_brown', shutters='brown_sh', balcony=True, seed=1))
    doors['smalti'] = cv.place_art(66, 46, decor.asset('house', art.house, 4, 2, 'ochre', roof='roof', shutters='green_sh', balcony=True, seed=1))
    locked += terrace(cv, 34, 46, 40, 1)
    locked += terrace(cv, 14, 31, 53, 2)
    locked += terrace(cv, 34, 46, 53, 0)
    locked += terrace(cv, 48, 62, 53, 1)
    locked += terrace(cv, 70, 78, 53, 2)
    for (x, y) in ((8, 33), (28, 33), (40, 33), (58, 33), (72, 33), (6, 27), (60, 27)):
        lamp(cv, x, y)
    # borders
    border = rect(0, 0, W, 2) | rect(0, 2, 2, 54) | rect(78, 2, 2, 26) | rect(78, 32, 2, 24) | rect(0, H - 2, W, 2)
    decor.woods(cv, border, seed=85, pine_ratio=0.2, gaps=0.0)
    # ---------------- events (same order as 0.21)
    order = {2: 'podesta', 3: 'duomo', 4: 'mic', 5: 'pc', 6: 'mart', 7: 'gym', 8: 'bottega', 11: 'torniante', 12: 'rioni', 13: 'smalti'}
    for i, k in order.items():
        cv.set_warp(i, *doors[k])
    cv.place_objs({1: (72, 30), 2: (30, 20), 3: (56, 24), 4: (30, 39), 5: (66, 23), 6: (42, 36), 7: (57, 44), 8: (10, 47)})
    b = cv.bbgs
    b[0]['x'], b[0]['y'] = doors['mic'][0] + 2, doors['mic'][1] + 1
    b[1]['x'], b[1]['y'] = doors['podesta'][0] - 2, doors['podesta'][1] + 1
    b[2]['x'], b[2]['y'] = doors['gym'][0] - 3, doors['gym'][1] + 1
    for bb in b:
        cv.put(bb['x'], bb['y'], G['sign'], 1, 3)
    fill_lawns(cv, rect(2, 17, 11, 10) | rect(62, 20, 16, 4) | rect(14, 43, 17, 6) | rect(34, 43, 12, 6) | rect(48, 43, 14, 6) | rect(64, 34, 14, 6) | rect(2, 33, 9, 2), seed=85)
    for d in locked:
        if d: cv.locked(d)
    cv.heal = (doors['pc'][0], doors['pc'][1] + 1)
    cv.border = [0x1D4, 0x1D5, 0x1DC, 0x1DD]
    return cv
