"""Cesenatico (MAP_ROMAGNA_CESENATICO): Leonardo's porto canale with the painted-sail boats, Grattacielo and wheel."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import canvas, art, extract, imports, mapio, check, world, decor
from canvas import Canvas, G
from decor import rect

NAME = 'Romagna_Cesenatico'
TS = 'romagna17_cesenatico'
W, H = world.size(NAME)
CN, CS = 15, 19        # canal rims (water 16..18)


def build():
    cv = Canvas(W, H, name=NAME)
    cv.fill(38, 0, W - 38, H, 'sand')
    cv.fill(42, 0, W - 42, H, 'sea')
    cv.fill(0, CN + 1, 42, 3, 'sea')
    fam, cob = imports.cobbles(imports.warm_stone)
    paved = rect(0, 13, 38, 2) | rect(0, 20, 38, 2) | rect(0, CN, 38, 1) | rect(0, CS, 38, 1)
    paved |= rect(0, 24, 30, 2) | rect(28, 22, 2, 22) | rect(30, 40, 4, 4) | rect(10, 22, 2, 3)
    paved |= rect(20, 2, 2, 11) | rect(14, 26, 2, 10)
    cv.paint_family(fam, cob, paved)
    rim_t, rim_b, face = art.quay_rim(True), art.quay_rim(False), art.quay_face()
    for x in range(0, 38):
        cv.place_art(x, CN, dict(img=rim_t, solid=set(), door=None))
        cv.place_art(x, CS, dict(img=rim_b, solid=set(), door=None))
        cv.place_art(x, CN + 1, dict(img=face, solid=set(), door=None))
    for x in (4, 13, 24, 33):
        cv.place_art(x, CN, dict(img=decor.asset('bollard', art.bollard), solid={(0, 0)}, door=None))
    br = art.bridge_ns()
    for bx in (8, 9, 26, 27):
        for y in range(CN, CS + 1):
            cv.art[y][bx] = None
            cv.place_art(bx, y, dict(img=br, solid=set(), door=None), walkable=True)
    # the floating museum: boats with painted sails moored along the canal
    for bx, sail, hull in ((1, 'orange', (41, 99, 165)), (11, 'red', (57, 140, 90)), (15, 'yellow', (214, 214, 214)),
                           (20, 'orange', (214, 214, 214)), (29, 'red', (41, 99, 165)), (34, 'yellow', (57, 140, 90))):
        cv.place_art(bx, CN + 1, dict(img=art.boat(sail, hull), solid=rect(0, 0, 3, 3), door=None))
    bw = art.boardwalk()
    for x in range(38, 44):
        for y in (CN, CS):
            cv.place_art(x, y, dict(img=bw, solid=set(), door=None), walkable=True)
    doors = {}
    # north bank
    doors['mercato'] = cv.place_art(2, 9, art.shopfront(5, 'MERCATO ITTICO', 'cream', awning='blue'), protect=True)
    doors['marineria'] = cv.place_art(9, 9, art.warehouse(8, 'MARINERIA'), protect=True)
    ruota = extract.stamp_of('Romagna_Cesenatico', 0)
    cv.stamp(22, 4, ruota)
    rd = extract.stamp_door(ruota)
    doors['ruota'] = (22 + rd[0], 4 + rd[1]) if rd else (25, 12)
    gr = extract.stamp_of('Romagna_Cesenatico', 1)
    cv.stamp(31, 2, gr)
    gd = extract.stamp_door(gr)
    doors['gratt'] = (31 + gd[0], 2 + gd[1])
    # south bank
    doors['pc'] = decor.general_building(cv, 2, 26, decor.PC)
    doors['mart'] = decor.general_building(cv, 7, 26, decor.MART)
    doors['rist'] = cv.place_art(17, 21, art.shopfront(5, 'RISTORANTE', 'pink', awning='red'), protect=True)
    HO, HP = art.house(4, 2, 'ochre'), art.house(4, 2, 'pink')
    locked = [cv.place_art(x, y, h) for (x, y, h) in [(1, 33, HO), (6, 33, HP), (17, 28, HO), (22, 28, HP), (17, 34, HP), (22, 34, HO), (1, 2, HP), (12, 2, HO)]]
    # beach and pier
    for y in range(22, 42, 2):
        cv.place_art(39, y, dict(img=decor.asset('omb', art.ombrellone, 'blue'), solid={(0, 1)}, door=None), top_rows=1)
    for y in (24, 30, 36):
        cv.place_art(38, y, dict(img=decor.asset('cab', art.cabina, 'blue'), solid={(0, 1)}, door=None), top_rows=1)
    cv.place_art(43, CN - 4, dict(img=art.lighthouse(), solid={(0, 4), (1, 4)}, door=None), top_rows=3)
    tree = decor.asset('rtree', art.round_tree, seed=9)
    for (x, y) in [(12, 30), (12, 36), (26, 28), (26, 34), (5, 23), (16, 2), (30, 13 - 2)]:
        cv.place_art(x, y, dict(img=tree, solid={(0, 1)}, door=None), top_rows=1)
    decor.woods(cv, rect(0, 40, 28, 4) | rect(34, 40, 4, 4) | rect(5, 0, 7, 2), seed=71, pine_ratio=0.5, gaps=0.2)
    # events
    old = mapio.old_events(NAME)
    o = [dict(e) for e in old['object_events']]
    pos = {0: (7, 14), 1: (24, 20), 2: (33, 14), 3: (41, CS), 4: (32, 40)}
    for i, e in enumerate(o):
        e['x'], e['y'] = pos[i]
    cv.npcs = o
    cv.warps = []
    cv.warp(*doors['mercato'], 'MAP_ROMAGNA_MERCATO_ITTICO', 0)
    cv.warp(*doors['gratt'], 'MAP_ROMAGNA_GRATTACIELO1_F', 0)
    cv.warp(*doors['marineria'], 'MAP_ROMAGNA_MARINERIA', 0)
    cv.warp(*doors['pc'], 'MAP_ROMAGNA_CESENATICO_CENTRO', 0)
    cv.warp(*doors['rist'], 'MAP_ROMAGNA_RISTORANTE_PORTO', 0)
    cv.warp(*doors['ruota'], 'MAP_ROMAGNA_CABINA_RUOTA', 0)
    cv.warp(0, 0, 'MAP_ROMAGNA_CESENATICO', 0)
    cv.warp(1, 0, 'MAP_ROMAGNA_CESENATICO', 0)
    for x in range(28, 34):
        cv.trigger(x, H - 2, 'Romagna17_RivieraGate', 'VAR_TEMP_0', 0)
    for d in locked:
        a = cv.art[d[1]][d[0]]
        cv.art[d[1]][d[0]] = (a[0], a[1], 1, 0, a[4])
        cv.sign(d[0], d[1], 'Romagna17_LockedDoor')
    cv.border = [0x170, 0x170, 0x170, 0x170]
    return cv, doors


STARTS = [(0, 24), (30, H - 1)]


def build_cv():
    return build()[0]


def main(argv):
    cv, doors = build()
    idmap, grids = canvas.build_tileset([cv], mapio.ts_symbol(TS), TS)
    check.check(cv, grids[0], STARTS)
    sym = mapio.register_tileset(TS)
    canvas.preview(cv, grids[0], idmap, TS, argv[1] if len(argv) > 1 else '/tmp/p.png', markers='--nomarkers' not in argv)
    if '--write' in argv:
        mapio.write(NAME, cv, grids[0], idmap, sym, connections=world.connections(NAME))
        print('written')


if __name__ == '__main__':
    main(sys.argv)
