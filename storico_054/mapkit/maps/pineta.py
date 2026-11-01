"""Pineta del Savio (MAP_ROUTE101): pinewood between Lido di Savio and Cervia."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import canvas, art, imports, mapio, check, world, decor
from canvas import Canvas, G
from decor import rect

NAME = 'Route101'
TS = 'romagna17_pineta'
W, H = world.size(NAME)


def build():
    cv = Canvas(W, H, name=NAME)
    trails = set()
    trails |= rect(16, 0, 2, 8)
    trails |= rect(6, 6, 12, 2)
    trails |= rect(6, 6, 2, 15)
    trails |= rect(6, 19, 18, 2)
    trails |= rect(22, 19, 2, 13)
    trails |= rect(12, 30, 12, 2)
    trails |= rect(12, 30, 2, 10)
    trails |= rect(2, 19, 5, 2)            # spur to the western clearing (Nora's seeds)
    trails |= rect(18, 6, 8, 2) | rect(24, 6, 2, 4)   # spur to the eastern nook
    for (x, y) in trails:
        cv.path(x, y, 1, 1)
    clear1 = rect(9, 9, 7, 7)               # northern clearing
    clear2 = rect(12, 23, 9, 6)             # southern clearing
    west = rect(2, 18, 4, 7)                # western clearing
    nook = rect(24, 7, 4, 4)
    rest = rect(24, 31, 5, 5)
    pond = rect(17, 11, 7, 5) | rect(19, 16, 4, 1) | rect(16, 13, 1, 2)
    for (x, y) in pond:
        cv.fill(x, y, 1, 1, 'pond')
    tall = rect(10, 10, 5, 5) | rect(13, 24, 7, 4) | rect(2, 22, 4, 3)
    decor.tall_grass(cv, tall)
    # reeds and a little boardwalk pier into the pond
    for (x, y) in [(16, 11), (16, 12), (24, 13), (24, 14), (16, 15), (18, 16)]:
        cv.place_art(x, y, dict(img=decor.asset('reeds', art.reeds, (x + y) % 3), solid={(0, 0)}, door=None))
    for y in (17, 18):
        cv.place_art(20, y, dict(img=decor.asset('bwv', art.boardwalk, True), solid=set(), door=None))
    # rest area
    cv.place_art(25, 32, dict(img=art.picnic_table(), solid={(0, 0), (1, 0)}, door=None))
    cv.place_art(9, 34, dict(img=art.log(), solid={(0, 0), (1, 0)}, door=None))
    # woods everywhere else
    open_ = trails | clear1 | clear2 | west | nook | rest | pond | rect(16, 10, 1, 8) | rect(24, 12, 1, 4) | rect(20, 17, 1, 2) \
        | rect(8, 33, 4, 3) | rect(18, 1, 3, 4)
    border = rect(0, 0, 2, H) | rect(W - 2, 0, 2, H)
    border -= trails
    pos = {0: (8, 12), 1: (19, 3), 2: (21, 25), 3: (21, 21), 4: (10, 33), 5: (3, 21), 6: (26, 9), 7: (26, 34)}
    reserved = set(pos.values()) | {(x + 1, y) for x, y in pos.values()} | {(x - 1, y) for x, y in pos.values()}
    inner = {(x, y) for x in range(W) for y in range(H)} - open_ - border - reserved
    decor.solid_border_trees(cv, border)
    decor.woods(cv, inner, seed=5, pine_ratio=0.65, gaps=0.45)
    # events
    old = mapio.old_events(NAME)
    o = [dict(e) for e in old['object_events']]
    face = {0: 'MOVEMENT_TYPE_FACE_RIGHT', 2: 'MOVEMENT_TYPE_FACE_LEFT', 3: 'MOVEMENT_TYPE_FACE_DOWN'}
    for i, e in enumerate(o):
        e['x'], e['y'] = pos[i]
        if i in face:
            e['movement_type'] = face[i]
    cv.npcs = o
    cv.sign(18, 4, 'Romagna_ForestSign')
    cv.sign(14, 36, 'Romagna_ForestSign')
    cv.border = [0x1D4, 0x1D5, 0x1DC, 0x1DD]
    return cv


STARTS = [(16, 0), (17, 0)]


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
