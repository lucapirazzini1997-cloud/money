"""Lido di Savio (0,9) 56x44 — village between the Savio mouth (north), the pinewood (west) and the Adriatic (east).

The Savio river crosses the whole north edge: Ravenna is reachable only with SURF (as the story says)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import art, art22, extract, imports, decor, r22
from canvas import G
from decor import rect

GN = (0, 9)
TS = 'r22_lido'
W, H = 56, 44
STARTS = [(19, H - 1), (47, H - 1)]
HEAL = 1


def tree_at(cv, x, y, seed=9, kind='round'):
    img = decor.asset('rtree', art.round_tree, seed=seed % 2) if kind == 'round' else decor.asset('ypine', art.young_pine)
    cv.place_art(x, y, dict(img=img, solid={(0, 1)}, door=None), top_rows=1)


def build():
    cv = r22.RCanvas(W, H, GN)
    PROM = 40          # lungomare x 40..41
    SAND = 42          # beach x 42..51
    SEA = 52
    RIV0, RIV1 = 3, 6  # river rows
    # ---------------- terrain
    cv.fill(SAND, 0, W, H, 'sand')
    cv.fill(SEA, 0, W - SEA, H, 'sea')
    cv.fill(0, RIV0, W, RIV1 - RIV0 + 1, 'sea')               # Savio river into the sea
    cv.fill(0, RIV1 + 1, W, 1, 'sand')                        # south bank
    cv.fill(0, 0, W, 1, 'grass')
    cv.fill(SAND, 0, SEA - SAND, RIV0, 'sand')
    fam, cob = imports.cobbles(imports.warm_stone)
    paved = rect(PROM, 8, 2, H - 8)                           # lungomare
    paved |= rect(4, 8, PROM - 4, 2)                          # via Lungo Savio
    paved |= rect(18, 10, 4, H - 10)                          # viale della Pineta (south exit)
    paved |= rect(29, 10, 2, 30)                              # via dei Gabbiani
    paved |= rect(4, 20, 36, 2)                               # via Romea
    paved |= rect(4, 30, 36, 2)
    paved |= rect(22, 22, 7, 7)                               # piazzetta
    paved |= rect(4, 39, 36, 2)
    paved |= rect(42, H - 3, 0, 0)
    cv.paint_family(fam, cob, paved)
    # path on the north bank to Ravenna's road
    for (x, y) in rect(19, 0, 2, 3):
        cv.path(x, y, 1, 1)
    # ---------------- river banks: reeds, fishing huts, a boardwalk pier for fishing
    for x in list(range(0, 17)) + list(range(23, 40)):
        if x % 3 != 1:
            cv.place_art(x, RIV1 + 1, dict(img=decor.asset('reeds', art.reeds, x % 3), solid={(0, 0)}, door=None))
        if x % 4 == 0:
            cv.place_art(x, 2, dict(img=decor.asset('reeds', art.reeds, (x + 1) % 3), solid={(0, 0)}, door=None))
    for x in (34, 35):
        for y in (RIV1, RIV1 - 1):
            cv.place_art(x, y, dict(img=decor.asset('bwv', art.boardwalk, True), solid=set(), door=None), walkable=True)
    cv.place_art(9, 0, art22.fishing_hut(), top_rows=1)
    cv.place_art(28, 0, art22.fishing_hut(), top_rows=1)
    # ---------------- pinewood (west) and border trees
    pine = decor.asset('pine', art.umbrella_pine)
    for y in range(8, H - 1, 2):
        for x in ((0, 2) if (y // 2) % 2 == 0 else (1,)):
            if (x, y) in ((2, 26),):
                continue
            cv.place_art(x, y, dict(img=pine, solid={(0, 1), (1, 1)}, door=None), top_rows=1)
    # south border: hedges/trees except the two exits
    south = rect(4, H - 2, 13, 2) | rect(23, H - 2, 19, 2)
    decor.woods(cv, south, seed=4, pine_ratio=0.6, gaps=0.0)
    cv.place_art(17, H - 4, art22.city_gate(6, 'PINETA - CERVIA'), top_rows=1, protect=True)
    # ---------------- buildings
    doors = {}
    import _stamps
    # the original villa of the protagonist (0.21), kept exactly as it was
    doors['player'] = _stamps.paste(cv, 5, 10, _stamps.cut((0, 9), 4, 3, 7, 7), protect=True)
    for (x, y) in rect(8, 17, 1, 3):
        cv.path(x, y, 1, 1)
    aldo = art.house(4, 2, 'blue', roof='roof_brown', shutters='brown_sh', seed=11)
    doors['aldo'] = cv.place_art(23, 12, aldo)
    cv.hedge(cv.hline_cells(22, 18, 2) + cv.hline_cells(25, 18, 2))
    hotel = art22.vistamare(7)
    doors['hotel'] = cv.place_art(32, 10, hotel, protect=True)
    lab = extract.stamp_of('LittlerootTown', 5, protect=True)
    cv.stamp(10, 23, lab)
    ld = extract.stamp_door(lab)
    doors['lab'] = (10 + ld[0], 23 + ld[1])
    # Caffè Panama: ground floor of a brick apartment block with the long flat canopy
    # the Caffè Panama as it was in 0.21 (the user's favourite): apartment block, PANAMA sign, canopy
    doors['bar'] = cv.place_art(31, 22, art22.panama21(), protect=True)
    church = art.church(5, 'cream', tower_side='left', rose=False)
    locked = [cv.place_art(5, 32, church)]
    HO, HP, HC = decor.asset('house', art.house, 4, 2, 'ochre', seed=1), decor.asset('house', art.house, 4, 2, 'pink', roof='roof_brown', seed=1), decor.asset('house', art.house, 5, 1, 'cream', seed=1)
    HY = decor.asset('house', art.house, 4, 1, 'ochre', seed=1)
    HW = decor.asset('house', art.house, 3, 1, 'pink', roof='roof_brown', seed=1)
    for (x, y, h) in ((12, 12, HO), (31, 32, HP), (35, 33, HW), (11, 33, HY)):
        locked.append(cv.place_art(x, y, h))
    # gelateria next to the church
    gel = art.shopfront(3, 'GELATI', 'pink', awning='blue', floors=1)
    locked.append(cv.place_art(15, 33, gel, protect=True))
    # ---------------- piazzetta: fountain, benches, kiosk (Poké Ball seller), lamps
    cv.place_art(24, 24, dict(img=decor.asset('fountain', art.fountain), solid=rect(0, 0, 2, 2), door=None))
    for (x, y) in ((22, 23), (27, 23), (22, 27), (27, 27)):
        cv.place_art(x, y, dict(img=decor.asset('bench', art.bench), solid={(0, 0)}, door=None))
    cv.place_art(26, 22, dict(img=decor.asset('kiosk', art.kiosk), solid=rect(0, 0, 2, 2), door=None), protect=True)
    for (x, y) in ((21, 22), (21, 28), (28, 29)):
        cv.place_art(x, y, dict(img=decor.asset('lamp', art.lamp), solid={(0, 1)}, door=None), top_rows=1)
    # ---------------- playground + Nora's garden (young pines nursery)
    cv.place_art(22, 33, dict(img=decor.asset('swing', art.swing), solid={(0, 1), (1, 1)}, door=None), top_rows=1)
    cv.place_art(25, 33, dict(img=decor.asset('slide', art.slide), solid={(0, 1), (1, 1)}, door=None), top_rows=1)
    cv.place_art(23, 36, dict(img=decor.asset('pic', art.picnic_table), solid={(0, 0), (1, 0)}, door=None))
    cv.hedge(cv.hline_cells(22, 38, 2) + cv.hline_cells(26, 38, 2))
    fb = decor.asset('fb1', art.flowerbed, ((239, 99, 132), (255, 206, 66)))
    fb2 = decor.asset('fb2', art.flowerbed, ((132, 99, 239), (255, 255, 255)))
    for x in range(4, 9):
        cv.place_art(x, 23, dict(img=fb, solid={(0, 0)}, door=None))
        cv.place_art(x, 28, dict(img=fb2, solid={(0, 0)}, door=None))
    for (x, y) in ((4, 24), (6, 24), (8, 25), (5, 26)):
        tree_at(cv, x, y, kind='ypine')
    # ---------------- trees along the streets
    for (x, y) in ((16, 11), (16, 15), (27, 11), (27, 15), (31, 11), (38, 18), (38, 33)):
        tree_at(cv, x, y, seed=9)
    for (x, y) in ((4, 11), (4, 19), (13, 19), (13, 29), (24, 19), (36, 30), (12, 38), (35, 38), (20, 12), (28, 12)):
        cv.put(x, y, G['flowers'])
    # ---------------- beach: cabins, umbrellas, lifeguard, volley, pedalos
    colors = ['blue', 'red', 'yellow', 'green']
    # Vistamare beach club: teak deck with the pool, white daybeds, white umbrellas and palms
    club = rect(SAND, 9, 10, 10)
    for (x, y) in club:
        cv.path(x, y, 1, 1)
    cv.place_art(44, 11, art22.pool(6, 4), protect=True)
    for (x, y) in ((43, 16), (46, 16), (49, 16), (43, 9), (49, 9)):
        cv.place_art(x, y, art22.daybed())
    for (x, y) in ((42, 12), (51, 12)):
        cv.place_art(x, y, art22.white_umbrella(), top_rows=1)
    for (x, y) in ((42, 15), (50, 15)) if False else ():
        pass
    cv.place_art(46, 6, art22.palm(), top_rows=2) if False else None
    for i, y in enumerate(range(9, H - 4, 3)):
        c = colors[(i // 3) % 4]
        if y < 20:
            continue
        if y not in (18, 27):
            cv.place_art(SAND, y, dict(img=decor.asset('cab', art.cabina, c), solid={(0, 1)}, door=None), top_rows=1)
        for x in (45, 48):
            if (x, y) in ((45, 21), (48, 21), (45, 24), (48, 24)):
                continue
            cv.place_art(x, y, dict(img=decor.asset('omb', art.ombrellone, c), solid={(0, 1)}, door=None), top_rows=1)
    cv.place_art(44, 21, art22.beach_volley(), top_rows=1)
    cv.place_art(50, 22, dict(img=decor.asset('life', art.lifeguard), solid={(0, 1)}, door=None), top_rows=1)
    cv.place_art(50, 31, dict(img=decor.asset('ped', art.pedalo), solid={(0, 0), (1, 0)}, door=None))
    # boatman to the Isola Miraggio (after the League) with his boat moored at the shore
    cv.place_art(52, 33, dict(img=decor.asset('boat', art.boat, 'red', (57, 140, 90)), solid=rect(0, 0, 3, 3), door=None))
    for y in (9, 16, 33, 37):
        cv.place_art(PROM - 1, y, dict(img=decor.asset('lamp', art.lamp), solid={(0, 1)}, door=None), top_rows=1)
    # ---------------- events
    cv.place_objs({1: (7, 17), 2: (25, 19), 3: (35, 5), 4: (8, 27), 5: (41, 9), 6: (41, 34), 7: (26, 36),
                   8: (24, 29), 9: (37, 19), 10: (38, 31), 11: (22, 17), 12: (2, 26), 13: (15, 37), 14: (50, 40),
                   15: (39, 12), 16: (26, 21)})
    cv.objs[2]['move'] = 9    # fisherman faces up (towards the river)
    cv.objs[15]['move'] = 8
    del cv.objs[16:18]        # the two guards: the river itself now blocks the way north
    cv.set_warp(0, *doors['aldo'])
    cv.set_warp(1, *doors['player'])
    cv.set_warp(2, *doors['lab'])
    cv.set_warp(3, *doors['hotel'])
    cv.set_warp(4, *doors['bar'])
    # signs: passaggio, lab, hotel, bar, Ravenna (south bank), foce (north bank)
    b = cv.bbgs
    b[0]['x'], b[0]['y'] = 46, H - 3
    b[1]['x'], b[1]['y'] = doors['lab'][0] - 2, doors['lab'][1] + 1
    b[2]['x'], b[2]['y'] = doors['hotel'][0] - 2, doors['hotel'][1] + 1
    b[3]['x'], b[3]['y'] = doors['bar'][0] - 1, doors['bar'][1] + 1
    b[4]['x'], b[4]['y'] = 22, 7
    b[5]['x'], b[5]['y'] = 18, 1
    for bb in b:
        cv.put(bb['x'], bb['y'], G['sign'], 1, 3)
    for dd in locked:
        cv.locked(dd)
    cv.add_obj(51, 34, 49, 'R22_MiraggioBoat', move=9)
    cv.heal = (doors['player'][0], doors['player'][1] + 1)
    cv.border = [0x1D4, 0x1D5, 0x1DC, 0x1DD]      # woods beyond the west edge (the engine draws the sea east)
    return cv
