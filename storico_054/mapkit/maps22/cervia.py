"""Cervia (0,10) 64x52 — porto canale with the Magazzini del Sale and Torre San Michele (north),
the 'città quadrata' around Piazza Garibaldi (south), the Adriatic to the east."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import art, art22, extract, imports, decor, r22
from canvas import G
from decor import rect

GN = (0, 10)
TS = 'r22_cervia'
W, H = 64, 52
STARTS = [(19, 0), (47, 0), (5, 42), (19, H - 1)]
HEAL = 14


def tree_at(cv, x, y, seed=9):
    cv.place_art(x, y, dict(img=decor.asset('rtree', art.round_tree, seed=seed % 2), solid={(0, 1)}, door=None), top_rows=1)


def build():
    cv = r22.RCanvas(W, H, GN)
    CN, CS = 12, 16          # canal rims; water rows 13..15
    SAND, SEA = 53, 58
    cv.fill(SAND, 0, W, H, 'sand')
    cv.fill(SEA, 0, W - SEA, H, 'sea')
    cv.fill(0, CN + 1, SEA, 3, 'sea')
    fam, cob = imports.cobbles(imports.warm_stone)
    paved = set()
    paved |= rect(18, 0, 4, 12) | rect(46, 0, 4, 12)                     # roads from the north
    paved |= rect(2, 10, SAND - 2, 2) | rect(2, CN, SAND - 2, 1)          # north quay
    paved |= rect(2, CS, SAND - 2, 1) | rect(2, 17, SAND - 2, 2)          # south quay
    paved |= rect(18, 19, 4, 33) | rect(46, 19, 4, 26)                    # north-south streets
    paved |= rect(0, 40, 22, 4)                                           # road west to the saline
    paved |= rect(22, 29, 15, 10)                                         # Piazza Garibaldi
    paved |= rect(4, 26, 46, 2) | rect(4, 45, 46, 2)                      # streets of the città quadrata
    paved |= rect(37, 33, 9, 2)
    cv.paint_family(fam, cob, paved)
    # ---------------- canal: quay rims, bollards, boats, two wooden bridges
    rim_t, rim_b, face = art.quay_rim(True), art.quay_rim(False), art.quay_face()
    for x in range(2, SEA):
        cv.place_art(x, CN, dict(img=rim_t, solid=set(), door=None))
        cv.place_art(x, CS, dict(img=rim_b, solid=set(), door=None))
        cv.place_art(x, CN + 1, dict(img=face, solid=set(), door=None))
    for x in (6, 14, 28, 38, 52):
        cv.place_art(x, CN, dict(img=decor.asset('bollard', art.bollard), solid={(0, 0)}, door=None))
    br = decor.asset('bridge', art.bridge_ns)
    for bx in (19, 20, 47, 48):
        for y in range(CN, CS + 1):
            cv.art[y][bx] = None
            cv.place_art(bx, y, dict(img=br, solid=set(), door=None), walkable=True)
    for i, bx in enumerate((4, 11, 24, 33, 41, 52)):
        sail, hull = (('orange', (41, 99, 165)), ('red', (57, 140, 90)))[i % 2]
        cv.place_art(bx, CN + 1, dict(img=decor.asset('boat', art.boat, sail, hull), solid=rect(0, 0, 3, 3), door=None), overlay=True)
    # ---------------- north bank: borgo marinaro (osteria, pescheria, trattoria, magazzino darsena, locanda)
    doors = {}
    doors['osteria'] = cv.place_art(3, 5, art.shopfront(4, 'OSTERIA', 'ochre', awning='green'))
    doors['pesce'] = cv.place_art(9, 5, art.shopfront(4, 'PESCE', 'cream', awning='blue'))
    doors['tratt'] = cv.place_art(23, 5, art.shopfront(4, 'TRATTORIA', 'pink', awning='red'))
    doors['darsena'] = cv.place_art(30, 3, art.warehouse(9, 'MAGAZZINO DARSENA'))
    doors['locanda'] = cv.place_art(51, 3, art.shopfront(5, 'LOCANDA', 'peach', awning='green', floors=2))
    HO = decor.asset('house', art.house, 4, 2, 'ochre', seed=1)
    locked = [cv.place_art(13, 4, decor.asset('house', art.house, 4, 2, 'pink', roof='roof_brown', seed=1)), cv.place_art(40, 4, HO)]
    for (x, y) in ((2, 2), (2, 7), (16, 2), (28, 2), (39, 2), (45, 2)):
        tree_at(cv, x, y)
    for (x, y) in ((8, 9), (22, 9), (29, 9), (44, 9), (50, 9)):
        cv.place_art(x, y, dict(img=decor.asset('lamp', art.lamp), solid={(0, 1)}, door=None), top_rows=1)
    # ---------------- south bank: Torre San Michele on its lawn, MUSA in the Magazzino Torre
    import _stamps
    doors['torre'] = cv.place_art(24, 18, art22.torre_san_michele(4), protect=True)
    doors['musa'] = cv.place_art(31, 19, art.warehouse(9, 'MUSA MUSEO DEL SALE'), protect=True)
    decor.tall_grass(cv, set())
    for (x, y) in ((23, 20), (23, 23), (41, 20), (41, 23)):
        tree_at(cv, x, y, seed=5)
    for x in (24, 30):
        cv.put(x, 25, G['flowers'])
    # salt pile and benches in front of the museum
    cv.place_art(42, 18, dict(img=decor.asset('salt', art.salt_pile), solid=rect(0, 0, 2, 2), door=None))
    # ---------------- città quadrata: rows of salt-workers' houses around Piazza Garibaldi
    # continuous terraces of low salt-workers' houses (the 'quadrilatero'), each house a different colour
    V = [decor.asset('house', art.house, 4, 2, 'ochre', roof='roof', shutters='green_sh', seed=1),
         decor.asset('house', art.house, 3, 2, 'pink', roof='roof_brown', shutters='brown_sh', seed=1),
         decor.asset('house', art.house, 4, 2, 'pink', roof='roof_brown', shutters='brown_sh', seed=1),
         decor.asset('house', art.house, 3, 2, 'ochre', roof='roof', shutters='green_sh', seed=1)]
    terr = [(4, 20, 0), (8, 20, 1), (11, 20, 2), (15, 20, 3),
            (4, 32, 3), (7, 32, 2), (11, 32, 1), (14, 32, 0),
            (23, 41, 0), (27, 41, 1), (30, 41, 2), (34, 41, 3)]
    for (x, y, k) in terr:
        locked.append(cv.place_art(x, y, V[k]))
    # Cattedrale di Santa Maria Assunta, facing the Municipio across Piazza Garibaldi
    locked.append(cv.place_art(31, 25, art.church(5, 'brick', tower_side='right', rose=True), protect=True))
    # Palazzo comunale on the west side of the square, Duomo on the east side
    doors['comune'] = cv.place_art(22, 28, art.palazzo_comunale(7, 'peach', name='MUNICIPIO'), protect=True)
    # Pokémon center, mart, gym (uniform General buildings)
    doors['pc'] = decor.general_building(cv, 5, 37, decor.PC)
    doors['mart'] = decor.general_building(cv, 10, 37, decor.MART)
    doors['gym'] = decor.general_building(cv, 39, 36, decor.GYM)
    # piazza: fountain, benches, lamps, flower beds (nothing covers the monuments)
    cv.place_art(28, 35, dict(img=decor.asset('fountain', art.fountain), solid=rect(0, 0, 2, 2), door=None))
    for (x, y) in ((24, 37), (33, 37), (26, 37), (31, 37)):
        cv.place_art(x, y, dict(img=decor.asset('bench', art.bench), solid={(0, 0)}, door=None))
    for (x, y) in ((22, 37), (36, 37)):
        cv.place_art(x, y, dict(img=decor.asset('lamp', art.lamp), solid={(0, 1)}, door=None), top_rows=1)
    for (x, y) in ((38, 41), (44, 41), (44, 28), (4, 47), (12, 47), (26, 48), (36, 48), (42, 48), (50, 48)):
        tree_at(cv, x, y, seed=(x + y) % 7)
    # park east of the piazza: playground, hedges, picnic
    cv.place_art(39, 29, dict(img=decor.asset('swing', art.swing), solid={(0, 1), (1, 1)}, door=None), top_rows=1)
    cv.place_art(42, 29, dict(img=decor.asset('slide', art.slide), solid={(0, 1), (1, 1)}, door=None), top_rows=1)
    cv.hedge(cv.hline_cells(38, 32, 8))
    # gardens with flower beds and hedges south of the città quadrata
    fb = decor.asset('fb1', art.flowerbed, ((239, 99, 132), (255, 206, 66)))
    for x in list(range(5, 11)) + list(range(28, 34)) + list(range(39, 45)):
        cv.place_art(x, 48, dict(img=fb, solid={(0, 0)}, door=None))
    for (x, y) in ((16, 48), (23, 48), (46, 48)):
        cv.place_art(x, y, dict(img=decor.asset('bench', art.bench), solid={(0, 0)}, door=None))
    # beach east of the town
    for i, y in enumerate(range(20, H - 2, 3)):
        c = ['blue', 'red', 'yellow', 'green'][(i // 3) % 4]
        cv.place_art(SAND, y, dict(img=decor.asset('cab', art.cabina, c), solid={(0, 1)}, door=None), top_rows=1)
        cv.place_art(55, y, dict(img=decor.asset('omb', art.ombrellone, c), solid={(0, 1)}, door=None), top_rows=1)
    # borders
    border = rect(0, 0, 2, 39) | rect(0, 44, 2, 8) | rect(2, H - 2, 16, 2) | rect(22, H - 2, 31, 2) | rect(0, 0, 18, 1) - rect(18, 0, 4, 2)
    border |= rect(22, 0, 24, 1) | rect(50, 0, 3, 1)
    decor.woods(cv, border, seed=8, pine_ratio=0.5, gaps=0.0)
    # exits: welcome gates
    cv.place_art(17, H - 4, art22.city_gate(6, 'CAMPAGNA - CESENA'), top_rows=1)
    # Varco delle Saline: gatehouse at the west end of the road (door on its east face)
    doors['gate'] = cv.place_art(0, 39, art22.gatehouse('east', 'SALINE'))
    gx, gy = doors['gate']
    a = cv.art[gy][gx]; cv.art[gy][gx] = (a[0], a[1], 0, 0x63, a[4])     # side passage: west arrow warp
    cv.conns = [c for c in cv.conns if c['dir'] != 3]
    # ---------------- events
    cv.place_objs({1: (7, 42), 2: (30, 36), 3: (36, 11), 4: (55, 11), 5: (10, 11), 6: (23, 22), 7: (37, 26),
                   8: (41, 42), 9: (50, 17), 10: (29, 34), 11: (52, 9), 12: (14, 24)})
    cv.objs[2]['move'] = 9
    order = ['musa', 'gym', 'pc', 'mart', 'osteria', 'pesce', 'tratt', 'locanda', 'torre', 'darsena', 'comune']
    for i, k in enumerate(order):
        cv.set_warp(i, *doors[k])
    cv.add_obj(61, 22, 183, 'R22_WishPortal', flag=0x4EE, move=8, elev=0)      # Jirachi portal (after the League)
    cv.bwarps.append(dict(x=doors['gate'][0], y=doors['gate'][1], elev=0, warp=0, num=0, group=0))   # -> gatehouse (set by the build)
    b = cv.bbgs
    b[0]['x'], b[0]['y'] = doors['musa'][0] + 2, doors['musa'][1] + 1
    b[1]['x'], b[1]['y'] = doors['darsena'][0] + 2, doors['darsena'][1] + 1
    b[2]['x'], b[2]['y'] = 4, 44
    b[3]['x'], b[3]['y'] = 45, 2
    for bb in b:
        cv.put(bb['x'], bb['y'], G['sign'], 1, 3)
    for dd in locked:
        cv.locked(dd)
    cv.heal = (doors['pc'][0], doors['pc'][1] + 1)
    cv.border = [0x1D4, 0x1D5, 0x1DC, 0x1DD]
    return cv
