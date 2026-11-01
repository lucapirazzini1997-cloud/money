"""Saline di Cervia (MAP_ROMAGNA_SALINE): salt pans with embankments, flamingos and the Casello."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import canvas, art, extract, imports, mapio, check, world, decor
from canvas import Canvas, G
from decor import rect

NAME = 'Romagna_Saline'
TS = 'romagna17_saline'
W, H = world.size(NAME)


def build():
    cv = Canvas(W, H, name=NAME)
    cv.fill(0, 0, W, H, 'sand')
    # canal arriving from the Sentiero (rows 13..15) and ending at a sluice
    cv.fill(39, 13, W - 39, 3, 'sea')
    rim_t, rim_b, face = art.quay_rim(True), art.quay_rim(False), art.quay_face()
    for x in range(39, W):
        cv.place_art(x, 12, dict(img=rim_t, solid=set(), door=None))
        cv.place_art(x, 16, dict(img=rim_b, solid=set(), door=None))
        cv.place_art(x, 13, dict(img=face, solid=set(), door=None))
    # embankments (argini) are the sand floor; basins are carved between them
    basins = [
        (rect(1, 1, 7, 5) | rect(1, 6, 4, 2), 'w'), (rect(10, 1, 6, 6), 'p'), (rect(18, 1, 9, 4), 's'), (rect(18, 6, 9, 2), 'w'),
        (rect(29, 1, 7, 7), 'p'),
        (rect(1, 10, 5, 6), 's'), (rect(7, 10, 8, 6), 'p'), (rect(17, 10, 5, 6), 'w'), (rect(23, 10, 13, 2), 's'),
        (rect(23, 13, 13, 3), 'w'),
        (rect(15, 20, 6, 8), 'w'), (rect(22, 20, 5, 3), 's'), (rect(22, 24, 5, 4), 'p'), (rect(28, 20, 8, 8), 'p'),
        (rect(1, 30, 6, 7), 'p'), (rect(8, 30, 10, 3), 's'), (rect(8, 34, 10, 3), 'w'), (rect(19, 30, 7, 7), 'w'),
        (rect(27, 30, 9, 7), 's'),
    ]
    water = set()
    for (cells, kind) in basins:
        water |= cells
        fill = {'w': art.SALTWATER, 'p': art.SALTPINK, 's': art.SALTRIM}[kind]
        rim = art.SALTRIM if kind != 's' else [art.C(255, 255, 255), art.C(214, 214, 206), art.C(156, 156, 148)]
        decor.region(cv, cells, fill, rim, coll=1, behavior=0x10 if kind != 's' else 0)
    # a raised boardwalk across the middle basins (birdwatching path)
    for x in range(7, 15):
        cv.art[12][x] = None
        cv.place_art(x, 12, dict(img=decor.asset('bw', art.boardwalk), solid=set(), door=None), walkable=True)
    # grass tufts on the embankments
    for (x, y) in [(8, 8), (16, 3), (27, 9), (12, 18), (21, 18), (31, 18), (6, 28), (13, 28), (24, 29), (17, 38), (3, 38)]:
        cv.place_art(x, y, dict(img=decor.asset('dune', art.dune_grass, (x + y) % 4), solid=set(), door=None))
    # canal mouth into basin 6 (sluice)
    for y in (13, 14, 15):
        cv.place_art(37, y, dict(img=decor.asset('bwv', art.boardwalk, True), solid=set(), door=None), walkable=True)
        cv.place_art(38, y, dict(img=decor.asset('bwv', art.boardwalk, True), solid=set(), door=None), walkable=True)
    # casello (old stamp) and its yard with salt piles
    casello = extract.stamp_of('Romagna_Saline', 0, ground=extract.ground_img(0x124))
    cv.stamp(1, 20, casello)
    cd = extract.stamp_door(casello)
    door = (1 + cd[0], 20 + cd[1])
    pile = art.salt_pile()
    for (x, y) in [(38, 20), (41, 21), (44, 19), (38, 30), (42, 33)]:
        cv.place_art(x, y, dict(img=pile, solid=rect(0, 0, 2, 2), door=None))
    # outer meadow with tall grass (encounters) east and south-east
    for (x, y) in rect(37, 24, 9, 4) | rect(37, 35, 10, 4) | rect(38, 2, 9, 9):
        cv.fill(x, y, 1, 1, 'grass')
    decor.tall_grass(cv, rect(38, 24, 7, 3) | rect(38, 36, 8, 3) | rect(39, 3, 7, 6))
    # border shrubs (tamarisks) around the whole area
    border = rect(0, H - 1, W, 1) | rect(0, 0, W, 0) | rect(W - 1, 28, 1, 7) | rect(W - 1, 0, 1, 2)
    decor.woods(cv, border, seed=8, pine_ratio=0.0, gaps=0.0)
    for (x, y) in [(12, 38), (25, 38), (36, 38), (46, 30), (46, 31)]:
        cv.place_art(x, y, dict(img=decor.asset('dune', art.dune_grass, x % 4), solid=set(), door=None))
    # events (old order)
    old = mapio.old_events(NAME)
    o = [dict(e) for e in old['object_events']]
    pos = {0: (24, 17), 1: (7, 26), 2: (44, 18), 3: (4, 3), 4: (30, 14), 5: (17, 23), 6: (31, 34)}
    for i, e in enumerate(o):
        e['x'], e['y'] = pos[i]
    o[0]['movement_type'] = 'MOVEMENT_TYPE_FACE_RIGHT'
    o[1]['movement_type'] = 'MOVEMENT_TYPE_FACE_RIGHT'
    o[2]['movement_type'] = 'MOVEMENT_TYPE_FACE_LEFT'
    cv.npcs = o
    cv.warps = []
    cv.warp(door[0], door[1], 'MAP_ROMAGNA_CASELLO_SALINE', 0)
    cv.sign(door[0] + 2, door[1] + 1, 'Romagna08_CaselloSign')
    cv.border = [0x1D4, 0x1D5, 0x1DC, 0x1DD]
    return cv, water


STARTS = [(W - 1, 17)]


def main(argv):
    cv, water = build()
    idmap, grids = canvas.build_tileset([cv], mapio.ts_symbol(TS), TS)
    check.check(cv, grids[0], STARTS)
    sym = mapio.register_tileset(TS)
    canvas.preview(cv, grids[0], idmap, TS, argv[1] if len(argv) > 1 else '/tmp/p.png', markers='--nomarkers' not in argv)
    if '--write' in argv:
        mapio.write(NAME, cv, grids[0], idmap, sym, connections=world.connections(NAME))
        print('written')


if __name__ == '__main__':
    main(sys.argv)
