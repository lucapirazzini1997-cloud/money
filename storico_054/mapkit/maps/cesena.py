"""Cesena (MAP_ROMAGNA_CESENA): Rocca Malatestiana on the Garampo hill, Piazza del Popolo, Malatestiana, Bonci."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import canvas, art, extract, imports, mapio, check, world, decor
from canvas import Canvas, G
from decor import rect

NAME = 'Romagna_Cesena'
TS = 'romagna17_cesena'
W, H = world.size(NAME)


def ledge_row(cv, x0, x1, y, gaps=()):
    for x in range(x0, x1):
        if x in gaps:
            continue
        cv.put(x, y, G['ledge'], 0, 3)
    cv.put(x0, y, G['ledge_l'], 0, 3)
    cv.put(x1 - 1, y, G['ledge_r'], 0, 3)


def build():
    cv = Canvas(W, H, name=NAME)
    fam, cob = imports.cobbles(imports.warm_stone)
    paved = set()
    paved |= rect(30, 0, 2, 14)                    # street from Via del Savio
    paved |= rect(15, 14, 21, 10)                  # Piazza del Popolo
    paved |= rect(35, 20, 19, 2)                   # corso east (to Strada del Mare)
    paved |= rect(0, 22, 16, 2)                    # street west (to the Ippodromo)
    paved |= rect(36, 14, 6, 2) | rect(42, 14, 9, 2)   # in front of library / duomo
    paved |= rect(17, 24, 2, 9) | rect(17, 32, 30, 2)  # south streets
    paved |= rect(44, 22, 2, 12)
    cv.paint_family(fam, cob, paved)
    # ---- Garampo hill with the Rocca: grass plateau bounded by ledges
    hill = rect(0, 0, 15, 14)
    for (x, y) in rect(9, 9, 2, 5):
        cv.path(x, y, 1, 1)
    rocca = extract.stamp_of('Romagna_Cesena', 0)
    cv.stamp(4, 2, rocca)
    rd = extract.stamp_door(rocca)
    rocca_door = (4 + rd[0], 2 + rd[1])
    ledge_row(cv, 0, 15, 14, gaps=(9, 10))
    for (x, y) in rect(9, 14, 2, 1):
        cv.path(x, y, 1, 1)
    for (x, y) in rect(9, 15, 2, 7):
        cv.path(x, y, 1, 1)
    decor.woods(cv, rect(0, 0, 3, 14) | rect(11, 0, 4, 8) | rect(12, 9, 3, 4) | rect(1, 10, 6, 3), seed=21, pine_ratio=0.1, gaps=0.25)
    decor.tall_grass(cv, rect(1, 15, 7, 5))
    # ---- piazza buildings
    doors = {}
    doors['comune'] = cv.place_art(15, 8, art.palazzo_comunale(9, 'peach', name='COMUNE'), protect=True)
    fontana = extract.stamp_of('Romagna_Cesena', 5, ground=cob[0x211].bottom)
    cv.stamp(24, 17, fontana)
    lib = extract.stamp_of('Romagna_Cesena', 3)
    cv.stamp(36, 10, lib)
    ld = extract.stamp_door(lib)
    doors['lib'] = (36 + ld[0], 10 + ld[1])
    duomo = art.church(6, 'brick', tower_side='right')
    doors['duomo'] = cv.place_art(44, 7, duomo)
    doors['bonci'] = cv.place_art(36, 26, art.theatre(6, 'TEATRO BONCI'), protect=True)
    doors['gym'] = cv.place_art(47, 25, art.greenhouse(6, 'PALESTRA'), protect=True)
    doors['pc'] = decor.general_building(cv, 20, 26, decor.PC)
    doors['mart'] = decor.general_building(cv, 25, 26, decor.MART)
    # ---- houses and gardens
    HO, HP = art.house(4, 2, 'ochre'), art.house(4, 2, 'pink')
    HO5, HP1 = art.house(5, 2, 'ochre'), art.house(4, 1, 'pink')
    HC = art.house(5, 1, 'cream', roof='roof_brown')
    houses = [(1, 25, HO), (6, 25, HP), (1, 37, HO5), (8, 38, HP1), (21, 37, HP), (27, 38, HC),
              (34, 37, HO), (41, 38, HP1), (48, 37, HO5), (43, 0, HO), (33, 1, HP), (38, 2, HC)]
    locked = []
    for (x, y, h) in houses:
        d = cv.place_art(x, y, h)
        locked.append(d)
    decor.tall_grass(cv, rect(12, 26, 4, 4))
    tree = decor.asset('rtree', art.round_tree, seed=9)
    for (x, y) in [(15, 25), (33, 25), (34, 30), (42, 24), (13, 33), (47, 17), (52, 17), (0, 33), (52, 33), (48, 0), (49, 2), (19, 1), (24, 1),
                   (6, 38), (13, 39), (26, 39), (32, 38), (39, 39), (46, 38), (51, 21), (51, 11), (36, 4)]:
        cv.place_art(x, y, dict(img=tree, solid={(0, 1)}, door=None), top_rows=1)
    for (x, y) in rect(16, 1, 13, 6):
        if (x + y) % 5 == 0:
            cv.put(x, y, G['flowers'])
    decor.woods(cv, rect(15, 0, 3, 2) | rect(26, 0, 4, 2) | rect(50, 0, 4, 6), seed=22, pine_ratio=0.2, gaps=0.2)
    for (x, y) in [(20, 16), (30, 16), (20, 22), (30, 22)]:
        cv.place_art(x, y, dict(img=decor.asset('bench', art.bench), solid={(0, 0)}, door=None))
    # ---- events
    old = mapio.old_events(NAME)
    o = [dict(e) for e in old['object_events']]
    pos = {0: (32, 6), 1: (23, 19), 2: (14, 34), 3: (50, 20), 4: (40, 15), 5: (19, 18), 6: (42, 31), 7: (46, 15)}
    for i, e in enumerate(o):
        e['x'], e['y'] = pos[i]
    cv.npcs = o
    cv.warps = []
    cv.warp(*doors['comune'], 'MAP_ROMAGNA_COMUNE_CESENA', 0)
    cv.warp(*doors['lib'], 'MAP_ROMAGNA_BIBLIOTECA', 0)
    cv.warp(*doors['bonci'], 'MAP_ROMAGNA_BONCI', 0)
    cv.warp(*doors['pc'], 'MAP_ROMAGNA_CESENA_CENTRO', 0)
    cv.warp(*doors['mart'], 'MAP_ROMAGNA_CESENA_MARKET', 0)
    cv.warp(*doors['gym'], 'MAP_ROMAGNA_GIARDINO_PALESTRA', 0)
    cv.warp(*rocca_door, 'MAP_ROMAGNA_ROCCA1_F', 0)
    cv.warp(0, 0, 'MAP_ROMAGNA_CESENA', 0)        # placeholder keeps old warp ids stable
    cv.warp(*doors['duomo'], 'MAP_ROMAGNA_DUOMO', 0)
    cv.sign(rocca_door[0] + 3, rocca_door[1] + 1, 'Romagna09_RoccaSign')
    cv.sign(1, 21, 'Romagna09_RaceSign')
    cv.sign(doors['gym'][0] - 1, doors['gym'][1] + 1, 'Romagna09_GardenSign')
    for d in locked:
        a = cv.art[d[1]][d[0]]
        cv.art[d[1]][d[0]] = (a[0], a[1], 1, 0, a[4])
        cv.sign(d[0], d[1], 'Romagna17_LockedDoor')
    return cv


STARTS = [(30, 0), (W - 1, 20), (0, 22)]


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
