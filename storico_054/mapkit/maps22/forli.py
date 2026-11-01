"""Forlì (34,68) 76x60 — the Via Emilia crosses the city east-west; north of it Piazza Aurelio Saffi, one of the
largest squares in Italy, with the monument to Saffi, the Palazzo Comunale with the civic tower, the abbey of
San Mercuriale with its campanile, the Duomo, the Musei San Domenico, arcaded houses; south of it the dense
blocks, the Caffè Saffi, PC/Mart/Gym and the Rocca di Ravaldino (Caterina Sforza) in its gardens."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import art, art22, decor, imports, r22, _stamps
from art import C
from canvas import G
from decor import rect
from _town import tree, lamp, bench, house_row, free as _tfree


def _town_free(cv, x, y):
    return 0 <= x < cv.w and 0 <= y < cv.h and _tfree(cv, [(x, y)]) and not cv.pathmask[y][x]

GN = (34, 68)
TS = 'r22_forli'
W, H = 76, 60
STARTS = [(0, 31), (75, 32)]
HEAL = 5


HOUSES = None


def terrace(cv, x0, x1, y_front, start=0):
    """Continuous row of 4-wide houses from three shared variants (keeps the tileset small)."""
    global HOUSES
    if HOUSES is None:
        HOUSES = [decor.asset('house', art.house, 4, 2, 'ochre', roof='roof', shutters='green_sh', balcony=True, seed=1),
                  decor.asset('house', art.house, 4, 2, 'pink', roof='roof_brown', shutters='brown_sh', balcony=True, seed=1),
                  decor.asset('house', art.house, 4, 2, 'cream', roof='roof', shutters='green_sh', balcony=True, seed=1)]
    out = []
    i = start
    for x in range(x0, x1 - 3, 4):
        a = HOUSES[i % 3]; i += 1
        d = cv.place_art(x, y_front - 3, a)
        if d: out.append(d)
    return out


def build():
    cv = r22.RCanvas(W, H, GN)
    fam, cob = imports.cobbles(imports.warm_stone)
    paved = rect(0, 30, W, 4)                                    # Via Emilia (corso della Repubblica / corso Mazzini)
    paved |= rect(22, 16, 40, 14)                                # Piazza Saffi
    paved |= rect(20, 2, 2, 28) | rect(62, 2, 2, 28)              # streets along the square
    paved |= rect(2, 16, 20, 2) | rect(64, 18, 10, 2)             # side streets north
    paved |= rect(33, 34, 3, 22) | rect(2, 44, 72, 2)             # corso Garibaldi south, viale south
    paved |= rect(55, 34, 2, 10) | rect(10, 34, 2, 10)
    paved |= rect(28, 49, 14, 3)                                 # forecourt of the Rocca
    cv.paint_family(fam, cob, paved)
    doors = {}
    locked = []
    # ---------------- monuments
    doors['comune'] = cv.place_art(25, 9, art.palazzo_comunale(9, 'peach', name='MUNICIPIO', tower=True), protect=True)
    doors['merc'] = cv.place_art(50, 6, art.church(6, 'brick', tower_side='right', name=None, rose=True), protect=True)
    doors['rocca'] = cv.place_art(30, 42, art22.rocca(9, 6, keep=True, towers='round'), protect=True)
    doors['musei'] = cv.place_art(3, 11, art.warehouse(7, 'MUSEI S.DOMENICO'))
    # ---------------- Piazza Saffi: the monument, flower beds, lamps, benches
    cv.place_art(41, 21, dict(img=decor.asset('statue', art.statue), solid={(0, 1)}, door=None), top_rows=1)
    fb = decor.asset('fb1', art.flowerbed, ((239, 99, 132), (255, 206, 66)))
    for (x, y) in ((39, 21), (40, 21), (42, 21), (43, 21), (39, 23), (43, 23)):
        cv.place_art(x, y, dict(img=fb, solid={(0, 0)}, door=None))
    for (x, y) in ((25, 18), (58, 18), (25, 27), (58, 27), (35, 18), (48, 18)):
        lamp(cv, x, y)
    for (x, y) in ((30, 25), (34, 25), (48, 25), (52, 25)):
        bench(cv, x, y)
    # arcaded houses around the square and along the side streets (portici)
    por = decor.asset('portici', art.portici, 6, 2, 'brick', seed=5)
    for (x, y) in ((36, 10), (42, 10), (64, 11), (67, 2)):
        locked.append(cv.place_art(x, y, por))
    locked += terrace(cv, 14, 20, 14, 2)
    locked += terrace(cv, 64, 74, 28, 0)
    locked += terrace(cv, 2, 20, 28, 1)
    # more arcaded blocks to the north (same shared houses)
    locked += terrace(cv, 22, 46, 7, 1)
    locked += terrace(cv, 2, 18, 8, 2)
    # ---------------- south of the Via Emilia
    doors['pc'] = decor.general_building(cv, 15, 36, decor.PC)
    doors['mart'] = decor.general_building(cv, 22, 36, decor.MART)
    doors['gym'] = decor.general_building(cv, 58, 35, decor.GYM)
    doors['caffe'] = cv.place_art(3, 38, art.bar(5, 'CAFFE SAFFI', 'cream', 'red'))
    doors['orologi'] = cv.place_art(66, 38, decor.asset('house', art.house, 5, 2, 'ochre', roof='roof', shutters='green_sh', balcony=True, seed=1))
    locked += terrace(cv, 40, 56, 43, 0)
    locked += terrace(cv, 2, 27, 55, 1)
    locked += terrace(cv, 46, 74, 55, 2)
    # gardens of the Rocca (Parco della Resistenza) with trees and paths
    for (x, y) in ((27, 42), (41, 42), (26, 47), (43, 47), (24, 51), (45, 51), (12, 47), (18, 47), (52, 47), (60, 47)):
        tree(cv, x, y, seed=3)
    for x in range(28, 42, 2):
        cv.place_art(x, 52, dict(img=fb, solid={(0, 0)}, door=None))
    for (x, y) in ((29, 50), (40, 50)):
        bench(cv, x, y)
    for (x, y) in ((8, 35), (30, 35), (40, 35), (50, 35), (70, 35), (6, 29), (70, 29)):
        lamp(cv, x, y)
    # gardens on the lawns: trees of one kind and flower beds (cheap tiles), never on events
    import random as _r
    rnd = _r.Random(68)
    keep = {(o['x'], o['y']) for o in cv.objs} | {(o['x'], o['y'] + 1) for o in cv.objs}
    lawns = rect(2, 18, 18, 8) | rect(64, 20, 10, 6) | rect(12, 35, 21, 2) | rect(37, 35, 16, 3) | rect(58, 40, 16, 3) | rect(2, 46, 25, 4) | rect(46, 46, 28, 4) | rect(22, 2, 26, 1)
    for (x, y) in sorted(lawns):
        if (x, y) in keep or not _town_free(cv, x, y):
            continue
        r_ = rnd.random()
        if r_ < 0.06 and _town_free(cv, x, y + 1) and (x, y + 1) not in keep:
            tree(cv, x, y, seed=3)
        elif r_ < 0.16:
            cv.put(x, y, G['flowers'])
    # borders
    border = rect(0, 0, W, 2) | rect(0, 2, 2, 28) | rect(74, 2, 2, 30) | rect(0, 34, 2, 26) | rect(74, 34, 2, 26) | rect(0, H - 2, W, 2)
    decor.woods(cv, border, seed=68, pine_ratio=0.2, gaps=0.0)
    # ---------------- events (same order as 0.21)
    cv.set_warp(2, *doors['comune']); cv.set_warp(3, *doors['merc']); cv.set_warp(4, *doors['musei'])
    cv.set_warp(5, *doors['pc']); cv.set_warp(6, *doors['mart']); cv.set_warp(7, *doors['gym'])
    cv.set_warp(8, *doors['rocca']); cv.set_warp(9, *doors['caffe']); cv.set_warp(10, *doors['orologi'])
    cv.place_objs({1: (71, 32), 2: (30, 20), 3: (45, 27), 4: (26, 32), 5: (44, 31), 6: (55, 19), 7: (6, 18),
                   8: (9, 20), 9: (57, 41), 10: (36, 50), 11: (62, 46), 12: (34, 55), 13: (17, 20), 14: (48, 47)})
    b = cv.bbgs
    b[0]['x'], b[0]['y'] = 37, 19
    b[1]['x'], b[1]['y'] = doors['gym'][0] - 3, doors['gym'][1] + 1
    b[2]['x'], b[2]['y'] = 37, 50
    b[3]['x'], b[3]['y'] = 4, 34
    for bb in b:
        cv.put(bb['x'], bb['y'], G['sign'], 1, 3)
    for d in locked:
        if d: cv.locked(d)
    cv.heal = (doors['pc'][0], doors['pc'][1] + 1)
    cv.border = [0x1D4, 0x1D5, 0x1DC, 0x1DD]
    return cv
