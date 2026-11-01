"""Imola (35,1) 64x48 — north the old town: Piazza Matteotti with the Palazzo Comunale and arcades, the Duomo of
San Cassiano, the Rocca Sforzesca with its round towers; the Via Emilia (east: the bridge towards Lugo; west: the
Fumaiolo path); south the Autodromo Enzo e Dino Ferrari: asphalt loop with kerbs, finish line, grandstand, with the
Steel gym and the workshop inside the loop, the circuit inn and the mountain rescue post beside it."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import art, art22, decor, imports, r22
from art import C
from canvas import G
from decor import rect
from _town import tree, lamp, bench, terrace, fill_lawns

GN = (35, 1)
TS = 'r22_imola'
W, H = 64, 48
STARTS = [(63, 21), (0, 22)]
HEAL = 16


def build():
    cv = r22.RCanvas(W, H, GN)
    fam, cob = imports.cobbles(imports.warm_stone)
    paved = rect(0, 20, 64, 4)                                   # Via Emilia
    paved |= rect(20, 10, 18, 10)                                # Piazza Matteotti
    paved |= rect(2, 9, 18, 2) | rect(40, 9, 22, 2) | rect(10, 24, 2, 4) | rect(52, 24, 2, 4)
    cv.paint_family(fam, cob, paved)
    doors, locked = {}, []
    # ---------------- old town
    doors['comune'] = cv.place_art(22, 4, art.palazzo_comunale(9, 'ochre', name='MUNICIPIO', tower=True), protect=True)
    locked.append(cv.place_art(31, 4, decor.asset('portici', art.portici, 6, 2, 'ochre', seed=2)))
    locked.append(cv.place_art(42, 2, art.church(6, 'brick', tower_side='right', rose=True), protect=True))
    locked.append(cv.place_art(2, 11, art22.rocca(8, 6, keep=True, towers='round'), protect=True))
    doors['pc'] = decor.general_building(cv, 3, 3, decor.PC)
    doors['mart'] = decor.general_building(cv, 10, 3, decor.MART)
    doors['casa'] = cv.place_art(50, 12, decor.asset('house', art.house, 4, 2, 'cream', roof='roof', shutters='green_sh', balcony=True, seed=1))
    locked += terrace(cv, 55, 63, 19, 1)
    locked += terrace(cv, 12, 20, 19, 2)
    for (x, y) in ((21, 11), (36, 11), (21, 18), (36, 18)):
        lamp(cv, x, y)
    cv.place_art(28, 14, dict(img=decor.asset('fountain', art.fountain), solid=rect(0, 0, 2, 2), door=None))
    for (x, y) in ((24, 16), (33, 16)):
        bench(cv, x, y)
    # ---------------- Autodromo Enzo e Dino Ferrari
    x0, y0, x1, y1 = 16, 28, 61, 45                              # outer rectangle of the loop (3 wide)
    loop = rect(x0, y0, x1 - x0, 3) | rect(x0, y1 - 3, x1 - x0, 3) | rect(x0, y0, 3, y1 - y0) | rect(x1 - 3, y0, 3, y1 - y0)
    for (x, y) in loop:
        e = []
        if (x, y - 1) not in loop: e.append('n')
        if (x, y + 1) not in loop: e.append('s')
        if (x - 1, y) not in loop: e.append('w')
        if (x + 1, y) not in loop: e.append('e')
        cv.place_art(x, y, dict(img=art22.track_tile(tuple(e), finish=(x == 38 and y >= y1 - 3)), solid=set(), door=None), walkable=True)
    cv.place_art(26, 25, art22.grandstand(8), protect=True)
    cv.place_art(40, 25, art22.grandstand(8), protect=True)
    doors['gym'] = decor.general_building(cv, 24, 33, decor.GYM)
    doors['officina'] = cv.place_art(42, 33, art.warehouse(7, 'OFFICINA'))
    # ---------------- west: the circuit inn, the mountain rescue, the Fumaiolo path
    doors['locanda'] = cv.place_art(2, 27, art.shopfront(5, 'LOCANDA', 'peach', awning='red', floors=2))
    doors['soccorso'] = cv.place_art(2, 36, art.shopfront(5, 'SOCCORSO ALPINO', 'cream', awning='red', floors=1))
    paved2 = rect(2, 40, 12, 2) | rect(0, 40, 2, 2)
    cv.paint_family(fam, cob, paved2)
    for (x, y) in ((6, 19), (40, 24), (58, 24), (14, 26)):
        lamp(cv, x, y)
    border = rect(0, 0, 64, 2) | rect(0, 2, 2, 18) | rect(62, 2, 2, 18) | rect(62, 24, 2, 24) | rect(0, 24, 2, 16) | rect(0, 42, 2, 6) | rect(2, 46, 62, 2)
    decor.woods(cv, border, seed=135, pine_ratio=0.5, gaps=0.0)
    # ---------------- events (same order as 0.21)
    cv.set_warp(0, 63, 21)
    order = {1: 'pc', 2: 'mart', 3: 'comune', 4: 'officina', 5: 'casa', 6: 'locanda', 7: 'soccorso', 8: 'gym'}
    for i, k in order.items():
        cv.set_warp(i, *doors[k])
    cv.set_warp(9, 0, 40)
    cv.place_objs({1: (40, 21), 2: (15, 30), 3: (30, 39), 4: (9, 42)})
    b = cv.bbgs
    b[0]['x'], b[0]['y'] = 19, 12
    b[1]['x'], b[1]['y'] = 4, 42
    for bb in b:
        cv.put(bb['x'], bb['y'], G['sign'], 1, 3)
    fill_lawns(cv, rect(20, 31, 4, 11) | rect(30, 31, 10, 11) | rect(50, 31, 8, 11) | rect(40, 12, 10, 7) | rect(2, 43, 14, 3), seed=135)
    for d in locked:
        if d: cv.locked(d)
    cv.heal = (doors['pc'][0], doors['pc'][1] + 1)
    cv.border = [0x1D4, 0x1D5, 0x1DC, 0x1DD]
    return cv
