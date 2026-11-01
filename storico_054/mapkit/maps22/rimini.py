"""Rimini centro (34,47) 84x52 — Borgo San Giuliano and the Ponte di Tiberio over the Marecchia (west),
Corso d'Augusto through Piazza Tre Martiri to the Arco d'Augusto (east, towards the port),
Piazza Cavour with the Arengo and the Fontana della Pigna, Castel Sismondo, Le Befane to the south."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import art, art22, imports, decor, r22, _stamps
from canvas import G
from decor import rect
from _town import tree, lamp, bench, house_row, garden, free

GN = (34, 47)
TS = 'r22_rimini'
W, H = 84, 52
STARTS = [(83, 24), (40, 51)]
HEAL = 4


def build():
    cv = r22.RCanvas(W, H, GN)
    RX0, RX1 = 14, 21                       # Marecchia x 14..21
    cv.fill(RX0, 2, RX1 - RX0 + 1, H - 4, 'sea')
    fam, cob = imports.cobbles(imports.warm_stone)
    paved = rect(2, 24, 12, 2) | rect(22, 24, 62, 2)                 # corso d'Augusto (bridge deck in between)
    paved |= rect(2, 34, 12, 2) | rect(3, 26, 2, 8)                  # borgo streets
    paved |= rect(38, 26, 4, 26)                                     # via verso le Befane
    paved |= rect(30, 12, 20, 10) | rect(36, 11, 12, 1)               # Piazza Cavour + portico of the Arengo
    paved |= rect(52, 26, 10, 8)                                     # Piazza Tre Martiri
    paved |= rect(62, 12, 2, 12) | rect(24, 38, 14, 2) | rect(42, 38, 30, 2) | rect(70, 26, 2, 22)
    cv.paint_family(fam, cob, paved)
    # ---------------- Ponte di Tiberio (deck rows 24-25, arches 26-27)
    pt = art22.ponte_tiberio2(RX1 - RX0 + 3)
    bx = RX0 - 1
    cv.place_art(bx, 24, dict(img=pt['img'], solid=pt['solid'], door=None), walkable=False, protect=True)
    for (cx, cy) in pt['deck']:
        a = cv.art[24 + cy][bx + cx]
        if a is not None:
            cv.art[24 + cy][bx + cx] = (a[0], a[1], 0, 0x100, True)
    # river banks: parapets and trees (the Marecchia park)
    for y in list(range(3, 22, 3)) + list(range(30, 48, 3)):
        tree(cv, RX0 - 2, y, seed=y)
        tree(cv, RX1 + 2, y, seed=y + 1)
    # ---------------- Borgo San Giuliano (west): colourful houses with murals
    doors = {}
    doors['casaponte'] = cv.place_art(3, 20, decor.asset('house', art.house, 4, 2, 'pink', roof='roof_brown', shutters='brown_sh', balcony=True, seed=1))
    doors['pensione'] = cv.place_art(2, 30, art.shopfront(5, 'PENSIONE', 'yellow', awning='blue', floors=2))
    locked = []
    locked += house_row(cv, 8, 13, 23, seed=31)
    locked += house_row(cv, 2, 13, 47, seed=32)
    locked += house_row(cv, 7, 13, 33, seed=33)
    # ---------------- east bank: Bottega del Ponte, Casa Marina facing the bridge
    doors['bottega'] = cv.place_art(23, 20, art.shopfront(4, 'BOTTEGA', 'ochre', awning='green'))
    doors['marina'] = cv.place_art(28, 20, decor.asset('house', art.house, 4, 2, 'peach', roof='roof_brown', shutters='brown_sh', balcony=True, seed=1))
    # Castel Sismondo
    cs = art.church(1) if False else None
    decor.woods(cv, rect(22, 2, 8, 8), seed=44, pine_ratio=0.0, gaps=0.15)
    # ---------------- Piazza Cavour: Arengo, Fontana della Pigna, Teatro Galli
    # Palazzo dell'Arengo redrawn on the tile grid (the 0.21 stamp alone needed 250 tiles)
    doors['arengo'] = cv.place_art(36, 5, art22.arengo(), protect=True)
    cv.place_art(39, 16, dict(img=decor.asset('fountain', art.fountain), solid=rect(0, 0, 2, 2), door=None))

    for (x, y) in ((33, 18), (45, 18), (33, 14), (45, 14)):
        bench(cv, x, y)
    for (x, y) in ((30, 12), (49, 12), (30, 20), (49, 20)):
        lamp(cv, x, y)
    # ---------------- gym, PC, mart (uniform)
    doors['gym'] = decor.general_building(cv, 64, 13, decor.GYM)
    doors['pc'] = decor.general_building(cv, 43, 28, decor.PC)
    doors['mart'] = decor.general_building(cv, 47, 28, decor.MART)
    # ---------------- Piazza Tre Martiri with the tempietto and clock tower
    cv.place_art(56, 28, dict(img=decor.asset('statue', art.statue), solid={(0, 1)}, door=None), top_rows=1)
    for (x, y) in ((53, 30), (60, 30)):
        bench(cv, x, y)
    # ---------------- Arco d'Augusto at the east end of the corso (towards the port)
    ar = art22.arco_augusto()
    cv.place_art(68, 27, ar, protect=True)
    for (cx, cy) in ar['top_cells']:                    # the top of the arch is drawn over the player
        a = cv.art[27 + cy][68 + cx]
        if a is not None:
            cv.art[27 + cy][68 + cx] = (None, a[0], 0, 0, True)
    # houses along the corso and the side streets
    doors['caffe'] = cv.place_art(24, 34, art.bar(5, 'CAFFE CAVOUR', 'cream', 'green'))
    doors['mosaici'] = cv.place_art(24, 42, decor.asset('house', art.house, 4, 2, 'ochre', roof='roof', shutters='green_sh', balcony=True, seed=1))
    doors['cavour'] = cv.place_art(75, 34, decor.asset('house', art.house, 4, 2, 'pink', roof='roof_brown', shutters='brown_sh', balcony=True, seed=1))
    doors['officina'] = cv.place_art(72, 43, art22.deposito(5, 'OFFICINA'))
    locked += house_row(cv, 52, 69, 23, seed=41)
    locked += house_row(cv, 22, 37, 31, seed=42)
    locked += house_row(cv, 42, 62, 37, seed=43)
    locked += house_row(cv, 42, 69, 46, seed=44)
    locked += house_row(cv, 29, 37, 46, seed=45)
    locked += house_row(cv, 65, 76, 11, seed=46)
    locked += house_row(cv, 52, 61, 11, seed=47)
    locked += house_row(cv, 2, 13, 12, seed=48)
    locked += house_row(cv, 2, 13, 18, seed=49)
    locked += house_row(cv, 73, 82, 44 - 4, seed=50)
    garden(cv, rect(22, 2, 40, 9) | rect(64, 2, 18, 9) | rect(42, 40, 26, 6) | rect(72, 27, 10, 12), seed=5)
    # ---------------- borders and exits
    border = rect(0, 0, W, 2) | rect(0, H - 2, 38, 2) | rect(42, H - 2, 42, 2) | rect(0, 2, 2, 22) | rect(0, 26, 2, 24) | rect(82, 2, 2, 22) | rect(82, 26, 2, 24)
    decor.woods(cv, border, seed=23, pine_ratio=0.3, gaps=0.0)
    cv.place_art(37, H - 4, art22.city_gate(6, 'LE BEFANE'), top_rows=1)
    for (x, y) in ((0, 22), (0, 26)):
        cv.place_art(x, y, art22.pillar())
    # ---------------- events
    cv.place_objs({1: (23, 25), 2: (40, 19), 3: (66, 27), 4: (34, 22), 5: (40, 33), 6: (80, 24)})
    cv.objs[0]['move'] = 10   # Team Emilia grunt staring at the bridge (left)
    order = {0: (83, 24), 1: 'arengo', 2: 'pc', 3: 'mart', 4: 'gym', 5: 'casaponte', 6: 'caffe', 7: (38, 51), 8: 'bottega',
             9: 'marina', 10: 'pensione', 11: 'mosaici', 12: 'cavour', 13: 'officina', 14: (83, 25), 15: (39, 51)}
    for i, k in order.items():
        xy = doors[k] if isinstance(k, str) else k
        cv.set_warp(i, *xy)
    cv.bwarps.append(dict(x=40, y=51, elev=0, warp=0, num=54, group=34))
    cv.bwarps.append(dict(x=41, y=51, elev=0, warp=0, num=54, group=34))
    b = cv.bbgs
    b[0]['x'], b[0]['y'] = 23, 23
    b[1]['x'], b[1]['y'] = 74, 26
    b[2]['x'], b[2]['y'] = 50, 21
    b[3]['x'], b[3]['y'] = doors['gym'][0] - 2, doors['gym'][1] + 1
    for bb in b:
        cv.put(bb['x'], bb['y'], G['sign'], 1, 3)
    for dd in locked:
        cv.locked(dd)
    cv.heal = (doors['pc'][0], doors['pc'][1] + 1)
    cv.border = [0x1D4, 0x1D5, 0x1DC, 0x1DD]
    return cv
