"""Cervia (MAP_OLDALE_TOWN): salt town on the porto canale, Torre San Michele and Piazza Garibaldi."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import canvas, art, extract, imports, mapio, check, world, decor
from canvas import Canvas, G
from decor import rect

NAME = 'OldaleTown'
TS = 'romagna17_cervia'
W, H = world.size(NAME)
CANAL_N, CANAL_S = 12, 16          # rim rows; water is 13..15


def build():
    cv = Canvas(W, H, name=NAME)
    # ---------------- terrain
    cv.fill(32, 17, W - 32, H - 17, 'sand')            # beach south of the canal mouth
    cv.fill(31, 0, W - 31, 12, 'sand')                 # beach north (continues from the Passaggio)
    cv.fill(38, 0, W - 38, H, 'sea')
    cv.fill(0, 13, 38, 3, 'sea')                       # canal water (animated sea tiles)
    fam, cob = imports.cobbles(imports.warm_stone)
    paved = set()
    paved |= rect(0, 10, 31, 2)                         # north quay street
    paved |= rect(0, 17, 32, 2)                         # south quay street
    paved |= rect(0, CANAL_N, 38, 1) | rect(0, CANAL_S, 38, 1)   # quay rims
    paved |= rect(12, 0, 2, 10)                         # street from the pinewood
    paved |= rect(22, 8, 9, 2)                          # little square in front of the Darsena
    paved |= rect(2, 26, 19, 8)                         # Piazza Garibaldi
    paved |= rect(18, 19, 2, 21)                        # corso to Via del Savio
    paved |= rect(20, 25, 12, 2) | rect(20, 32, 12, 2)  # streets to PC/Mart
    paved |= rect(9, 34, 2, 6)
    cv.paint_family(fam, cob, paved)
    # ---------------- canal: rims, wall face, bollards, bridges, boats
    rim_t, rim_b, face = art.quay_rim(True), art.quay_rim(False), art.quay_face()
    for x in range(0, 38):
        cv.place_art(x, CANAL_N, dict(img=rim_t, solid=set(), door=None))
        cv.place_art(x, CANAL_S, dict(img=rim_b, solid=set(), door=None))
        cv.place_art(x, CANAL_N + 1, dict(img=face, solid=set(), door=None))
    for x in (3, 9, 17, 23, 30, 35):
        cv.place_art(x, CANAL_N, dict(img=decor.asset('bollard', art.bollard), solid={(0, 0)}, door=None))
    br = art.bridge_ns()
    for bx in (12, 13, 26, 27):
        for y in range(CANAL_N, CANAL_S + 1):
            cv.art[y][bx] = None
            cv.place_art(bx, y, dict(img=br, solid=set(), door=None), walkable=True)
    # piers into the sea along the canal mouth
    bw = art.boardwalk()
    for x in range(38, 42):
        for y in (CANAL_N, CANAL_S):
            cv.place_art(x, y, dict(img=bw, solid=set(), door=None), walkable=True)
    cv.place_art(42, CANAL_N, dict(img=art.lamp().crop((0, 16, 16, 32)), solid={(0, 0)}, door=None))
    for bx, sail, hull in ((4, 'orange', (41, 99, 165)), (18, 'red', (41, 99, 165)), (31, 'orange', (41, 99, 165))):
        cv.place_art(bx, CANAL_N + 1, dict(img=art.boat(sail, hull), solid=rect(0, 0, 3, 3), door=None))
    # ---------------- north bank: Borgo Marina
    doors = {}
    doors['osteria'] = cv.place_art(1, 6, art.shopfront(4, 'OSTERIA', 'ochre', awning='green'), protect=True)
    doors['locanda'] = cv.place_art(6, 6, art.shopfront(5, 'LOCANDA', 'pink', awning='yellow'), protect=True)
    doors['pesce'] = cv.place_art(15, 6, art.shopfront(4, 'PESCHERIA', 'ochre', awning='blue', seed=5), protect=True)
    doors['trattoria'] = cv.place_art(19, 6, art.shopfront(4, 'TRATTORIA', 'pink', awning='red'), protect=True)
    doors['darsena'] = cv.place_art(23, 3, art.warehouse(8, 'MAGAZZINI DEL SALE'), protect=True)
    # pinewood edge on the north
    nb = rect(0, 0, 12, 6) | rect(14, 0, 9, 6) | rect(23, 0, 8, 2)
    decor.woods(cv, nb - rect(10, 4, 2, 2), seed=7, pine_ratio=0.8, gaps=0.2)
    # ---------------- south bank
    torre = extract.make_stamp('OldaleTown', 23, 21, 5, 10, extract.BG['OldaleTown'] | {0x203, 0x211})
    cv.stamp(13, 17, torre)
    td = extract.stamp_door(torre)
    doors['torre'] = (13 + td[0], 17 + td[1])
    doors['musa'] = cv.place_art(20, 19, art.warehouse(8, 'MUSA'), protect=True)
    doors['municipio'] = cv.place_art(2, 20, art.palazzo_comunale(9, 'ochre'), protect=True)
    # piazza: fountain, benches, trees
    cv.place_art(10, 29, dict(img=art.fountain(), solid=rect(0, 0, 2, 2), door=None))
    for (x, y) in [(6, 31), (15, 31), (6, 28), (15, 28)]:
        cv.place_art(x, y, dict(img=decor.asset('bench', art.bench), solid={(0, 0)}, door=None))
    tree = decor.asset('rtree', art.round_tree, seed=9)
    for (x, y) in [(3, 26), (19, 26), (3, 31), (13, 33)]:
        pass
    # PC, Mart, Gym (General buildings), gym house
    doors['pc'] = decor.general_building(cv, 21, 28, decor.PC)
    doors['mart'] = decor.general_building(cv, 26, 28, decor.MART)
    doors['gym'] = decor.general_building(cv, 2, 34, decor.GYM)
    h = art.house(4, 2, 'ochre', seed=13)
    hd = cv.place_art(12, 35, h)
    h2 = art.house(4, 1, 'pink', seed=14)
    h2d = cv.place_art(21, 35, h2)
    h3 = art.house(4, 2, 'ochre', seed=15)
    h3d = cv.place_art(26, 34, h3)
    # beach south of the canal
    for y in range(20, 38, 2):
        for x in (34, 36):
            cv.place_art(x, y, dict(img=decor.asset('omb', art.ombrellone, 'orange'), solid={(0, 1)}, door=None), top_rows=1)
    for y in (20, 24, 28, 32):
        cv.place_art(32, y, dict(img=decor.asset('cab', art.cabina, 'orange'), solid={(0, 1)}, door=None), top_rows=1)
    # flowers and greenery between buildings
    for (x, y) in [(29, 21), (30, 21), (29, 22), (30, 22), (0, 20), (1, 20), (0, 21), (1, 21)]:
        cv.put(x, y, G['flowers'])
    for (x, y) in [(28, 19), (0, 22), (16, 37), (31, 35), (0, 33)]:
        cv.place_art(x, y, dict(img=tree, solid={(0, 1)}, door=None), top_rows=1)
    # ---------------- events
    old = mapio.old_events(NAME)
    o = [dict(e) for e in old['object_events']]
    pos = {0: (1, 18), 1: (12, 31), 2: (35, 11), 3: (17, 30), 4: (10, 11), 5: (12, 25), 6: (25, 9),
           7: (8, 37), 8: (39, 16), 9: (4, 29), 10: (20, 11), 11: (31, 38)}
    for i, e in enumerate(o):
        e['x'], e['y'] = pos[i]
    o[2]['movement_type'] = 'MOVEMENT_TYPE_FACE_DOWN'
    cv.npcs = o
    cv.warps = []
    cv.warp(*doors['musa'], 'MAP_ROMAGNA_MUSEO_SALE', 0)
    cv.warp(*doors['gym'], 'MAP_OLDALE_TOWN_HOUSE2', 0)
    cv.warp(*doors['pc'], 'MAP_OLDALE_TOWN_POKEMON_CENTER_1F', 0)
    cv.warp(*doors['mart'], 'MAP_OLDALE_TOWN_MART', 0)
    cv.warp(*doors['osteria'], 'MAP_ROMAGNA_OSTERIA', 0)
    cv.warp(*doors['pesce'], 'MAP_ROMAGNA_PESCE', 0)
    cv.warp(*doors['trattoria'], 'MAP_ROMAGNA_TRATTORIA', 0)
    cv.warp(*doors['locanda'], 'MAP_ROMAGNA_LOCANDA', 0)
    cv.warp(*doors['torre'], 'MAP_ROMAGNA_TORRE', 0)
    cv.warp(*doors['darsena'], 'MAP_ROMAGNA_MAGAZZINI', 0)
    cv.warp(*doors['municipio'], 'MAP_ROMAGNA_MUNICIPIO', 0)
    cv.sign(doors['musa'][0] - 1, doors['musa'][1] + 1, 'Romagna08_MusaSign')
    cv.sign(doors['darsena'][0] + 2, doors['darsena'][1] + 1, 'Romagna08_DarsenaSign')
    cv.sign(0, 16, 'Romagna08_SalineSign')
    cv.sign(31, 9, 'Romagna07_ShortcutSign')
    cv.sign(doors['gym'][0] + 2, doors['gym'][1] + 1, 'Romagna_GymSign')
    for d in (hd, h2d, h3d):
        a = cv.art[d[1]][d[0]]
        cv.art[d[1]][d[0]] = (a[0], a[1], 1, 0, a[4])
        cv.sign(d[0], d[1], 'Romagna17_LockedDoor')
    cv.border = [0x170, 0x170, 0x170, 0x170]
    return cv


STARTS = [(12, 0), (19, H - 1)]


def main(argv):
    cv = build()
    idmap, grids = canvas.build_tileset([cv], mapio.ts_symbol(TS), TS)
    check.check(cv, grids[0], STARTS)
    sym = mapio.register_tileset(TS)
    canvas.preview(cv, grids[0], idmap, TS, argv[1] if len(argv) > 1 else '/tmp/p.png', markers='--nomarkers' not in argv)
    if '--write' in argv:
        mapio.write(NAME, cv, grids[0], idmap, sym, connections=world.connections(NAME))
        print('written')


if __name__ == '__main__':
    main(sys.argv)
