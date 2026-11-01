"""Cesena (34,17) 96x52 — Rocca Malatestiana on the Garampo hill, Piazza del Popolo with the Fontana Masini,
Malatestiana library, Duomo, Teatro Bonci; the Savio with the Ponte Vecchio on the road to the Ippodromo (west)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from art import C
import art, art22, imports, decor, r22, _stamps, _town
from canvas import G
from decor import rect
from _town import tree, lamp, bench, house_row, garden

GN = (34, 17)
TS = 'r22_cesena'
W, H = 96, 52
STARTS = [(41, 0), (95, 41), (0, 41)]
HEAL = 3


def build():
    cv = r22.RCanvas(W, H, GN)
    # ---------------- the Savio (west) with the Ponte Vecchio
    cv.fill(3, 2, 4, H - 4, 'sea')
    fam, cob = imports.cobbles(imports.warm_stone)
    paved = rect(0, 40, W, 4)                         # corso: Ippodromo <-> Costa
    paved |= rect(40, 0, 4, 40)                       # via verso la campagna (north)
    paved |= rect(8, 17, 86, 2)                       # corso Mazzini
    paved |= rect(21, 19, 17, 10)                     # Piazza del Popolo
    paved |= rect(60, 19, 2, 21) | rect(76, 19, 2, 21) | rect(24, 29, 2, 11)
    paved |= rect(44, 9, 46, 2)                       # via del Duomo / Malatestiana
    paved |= rect(14, 14, 2, 3)                       # ramp to the Rocca
    paved |= rect(26, 16, 1, 1)                       # step in front of the Palazzo comunale
    for (x, y) in rect(3, 40, 4, 4):
        cv.terrain[y][x] = 'grass'
    cv.paint_family(fam, cob, paved)
    par = art.Px(16, 16) if hasattr(art, 'Px') else None
    pw = art.Px(16, 16)
    pw.rect(0, 4, 16, 8, art.PAL['stone'][1]); pw.hline(0, 4, 16, art.PAL['stone'][0]); pw.hline(0, 11, 16, art.PAL['stone'][3])
    for x in (2, 8, 14):
        pw.vline(x, 5, 6, art.PAL['stone'][2])
    for x in range(3, 7):
        cv.place_art(x, 39, dict(img=pw.im, solid={(0, 0)}, door=None))
        cv.place_art(x, 44, dict(img=pw.im, solid={(0, 0)}, door=None))
    # ---------------- Garampo hill and the Rocca Malatestiana
    rocca = _stamps.cut((34, 17), 8, 5, 8, 8)
    doors = {}
    doors['rocca'] = _stamps.paste(cv, 9, 4, rocca, protect=True)
    for y in (2, 4, 6, 8, 10):
        tree(cv, 8, y, seed=y)
    for (x, y) in ((17, 3), (19, 6), (18, 10), (12, 13), (16, 13)):
        tree(cv, x, y, seed=x)
    cv.place_art(13, 14, art22.city_gate(4, 'ROCCA'), top_rows=1, protect=True)
    # ---------------- Piazza del Popolo: Palazzo comunale, Fontana Masini, portici
    doors['comune'] = cv.place_art(22, 10, art.palazzo_comunale(9, 'brick', name='COMUNE', tower=False))
    doors['fontana'] = _stamps.paste(cv, 28, 22, _stamps.cut((34, 17), 26, 22, 3, 3))
    for (x, y) in ((24, 21), (34, 21), (24, 26), (34, 26)):
        bench(cv, x, y)
    for (x, y) in ((21, 19), (37, 19), (21, 28), (37, 28)):
        lamp(cv, x, y)
    portici = art.portici(6, 2, 'brick', seed=5)
    house_doors = [cv.place_art(31, 13, portici)]
    # ---------------- monuments on via del Duomo
    doors['duomo'] = _stamps.paste(cv, 45, 2, _stamps.cut((34, 17), 44, 10, 6, 7), protect=True)
    doors['biblio'] = cv.place_art(55, 4, art.warehouse(8, 'MALATESTIANA', wall='brick'))
    doors['bonci'] = _stamps.paste(cv, 66, 5, _stamps.cut((34, 17), 72, 12, 7, 5), protect=True)   # the 0.21 theatre
    # real doors on the buildings pasted from 0.21 (no more bare pale doorway tiles)
    for k, fr in (('duomo', C(198, 115, 82)), ('bonci', C(239, 231, 206))):
        dx, dy = doors[k]
        a = cv.art[dy][dx]
        if a is not None and a[0] is not None:
            im = a[0].copy(); im.alpha_composite(art22.door_overlay(fr))
            cv.art[dy][dx] = (im, a[1], a[2], a[3], a[4])
    for (x, y) in ((52, 6), (64, 7), (73, 7), (51, 3)):
        tree(cv, x, y, seed=x)
    house_doors += house_row(cv, 75, 92, 8, seed=3)
    house_doors += house_row(cv, 22, 39, 7, seed=4)
    house_doors += house_row(cv, 44, 92, 16, seed=5, floors=(1,))
    # ---------------- south of corso Mazzini
    doors['pc'] = decor.general_building(cv, 46, 33, decor.PC)
    doors['mart'] = decor.general_building(cv, 52, 33, decor.MART)
    doors['gym'] = decor.general_building(cv, 82, 32, decor.GYM)
    house_doors += house_row(cv, 8, 20, 22, seed=6)
    house_doors += house_row(cv, 8, 23, 38, seed=7)
    house_doors += house_row(cv, 27, 40, 38, seed=8)
    house_doors += house_row(cv, 44, 59, 26, seed=9, shops=[('PIADINA', 'yellow', 'red'), ('FORNO', 'cream', 'green')])
    house_doors += house_row(cv, 62, 76, 26, seed=10, shops=[('CAFFE', 'pink', 'blue')])
    house_doors += house_row(cv, 62, 75, 38, seed=11)
    house_doors += house_row(cv, 78, 93, 26, seed=12)
    house_doors += house_row(cv, 8, 40, 49 - 1, seed=13, floors=(1,))
    house_doors += house_row(cv, 44, 92, 49 - 1, seed=14, floors=(1,))
    # Giardini pubblici: pond, fountain, hedges (south-west block)
    for (x, y) in rect(10, 27, 6, 4):
        cv.fill(x, y, 1, 1, 'pond')
    cv.hedge(cv.hline_cells(9, 25, 8) + cv.hline_cells(9, 32, 3) + cv.hline_cells(14, 32, 3))
    for (x, y) in ((17, 27), (8, 27)):
        bench(cv, x, y)
    # market stalls in Piazza del Popolo
    for (x, y) in ((22, 23), (35, 23)):
        cv.place_art(x, y, dict(img=decor.asset('kiosk', art.kiosk), solid=rect(0, 0, 2, 2), door=None), protect=True)
    # avenue trees
    for x in range(46, 92, 6):
        tree(cv, x, 19, seed=x)
    for y in range(22, 38, 5):
        tree(cv, 39, y, seed=y); tree(cv, 44, y, seed=y + 1)
    # gym square: hedges, flowers; park between PC and gym
    cv.hedge(cv.hline_cells(79, 37, 3) + cv.hline_cells(89, 37, 3))
    garden(cv, rect(8, 23, 13, 12) | rect(27, 30, 12, 4) | rect(44, 27, 15, 5) | rect(62, 27, 13, 6) | rect(78, 27, 15, 4) | rect(58, 33, 1, 5), seed=21)
    for (x0, y0) in ((10, 30), (64, 30), (48, 28), (80, 28)):
        fb = decor.asset('fb1', art.flowerbed, ((239, 99, 132), (255, 206, 66)))
        for x in range(x0, x0 + 4):
            if _town.free(cv, [(x, y0)]): cv.place_art(x, y0, dict(img=fb, solid={(0, 0)}, door=None))
    for (x, y) in ((57, 36), (70, 31), (33, 31)):
        bench(cv, x, y)
    # ---------------- borders
    border = rect(0, 0, 40, 2) | rect(44, 0, 52, 2) | rect(0, 2, 3, 38) | rect(0, 44, 3, 8) | rect(94, 2, 2, 38) | rect(94, 44, 2, 6) | rect(7, H - 2, 87, 2)
    decor.woods(cv, border, seed=17, pine_ratio=0.2, gaps=0.0)
    cv.place_art(39, 0, art22.city_gate(6, 'CERVIA'), top_rows=1, protect=True)
    for (x, y) in ((0, 38), (0, 44), (94, 38), (94, 44)):
        cv.place_art(x, y, art22.pillar())
    # ---------------- events
    cv.place_objs({1: (38, 20), 2: (27, 25), 3: (70, 41), 4: (91, 41), 5: (58, 11), 6: (31, 21), 7: (80, 19), 8: (51, 13), 9: (9, 41)})
    order = ['comune', 'biblio', 'bonci', 'pc', 'mart', 'gym', 'rocca', None, 'duomo']
    for i, k in enumerate(order):
        if k:
            cv.set_warp(i, *doors[k])
    cv.set_warp(7, 0, 41)
    for yy in (40, 42, 43):
        cv.bwarps.append(dict(x=0, y=yy, elev=0, warp=0, num=19, group=34))
    b = cv.bbgs
    b[0]['x'], b[0]['y'] = doors['rocca'][0] + 2, doors['rocca'][1] + 1
    b[1]['x'], b[1]['y'] = 10, 44
    b[2]['x'], b[2]['y'] = doors['gym'][0] - 2, doors['gym'][1] + 1
    b[3]['x'], b[3]['y'] = 8, 39
    for bb in b:
        cv.put(bb['x'], bb['y'], G['sign'], 1, 3)
    for dd in house_doors:
        cv.locked(dd)
    cv.heal = (doors['pc'][0], doors['pc'][1] + 1)
    cv.border = [0x1D4, 0x1D5, 0x1DC, 0x1DD]
    return cv
