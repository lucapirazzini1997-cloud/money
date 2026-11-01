"""Passaggio costiero (MAP_ROMAGNA_PASSAGGIO_COSTIERO): dunes and beach between Lido di Savio and Cervia."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import canvas, art, imports, mapio, check, world, decor
from canvas import Canvas, G
from decor import rect

NAME = 'Romagna_PassaggioCostiero'
TS = 'romagna17_passaggio'
W, H = world.size(NAME)


def build():
    cv = Canvas(W, H, name=NAME)
    cv.fill(0, 0, W, H, 'sand')
    # coastline wiggles a little
    shore = [8, 8, 8, 9, 9, 9, 8, 8, 7, 7, 8, 8, 9, 9, 8, 8, 8, 8, 9, 9, 9, 8, 8, 8, 7, 7, 8, 8, 9, 9, 9, 8, 8, 8, 8, 8, 8, 8, 8, 8]
    for y in range(H):
        cv.fill(shore[y], y, W - shore[y], 1, 'sea')
    # dune belt (west): grass tufts, shrubs and tall grass pockets
    dunes = set()
    for y in range(H):
        for x in range(0, 3 if y % 7 < 4 else 2):
            dunes.add((x, y))
    for (x, y) in dunes:
        cv.place_art(x, y, dict(img=decor.asset('shrub', art.shrub, (x * 3 + y) % 3), solid={(0, 0)}, door=None))
    # dune grass decoration (walkable) and tall grass for encounters
    for (x, y) in [(3, 4), (4, 9), (3, 15), (5, 21), (3, 27), (4, 33), (6, 6), (6, 17), (6, 29)]:
        cv.place_art(x, y, dict(img=decor.asset('dune', art.dune_grass, (x + y) % 4), solid=set(), door=None))
    for (x, y) in rect(3, 18, 3, 5) | rect(3, 30, 3, 4):
        cv.fill(x, y, 1, 1, 'grass')
        cv.put(x, y, G['tall'])
    # a narrow neck closed by two small trees (Cut)
    for x in range(3, 8):
        if x not in (4, 5):
            cv.place_art(x, 12, dict(img=decor.asset('shrub', art.shrub, x % 3), solid={(0, 0)}, door=None))
    for y in (11, 13):
        for x in range(3, 8):
            if x not in (4, 5):
                cv.place_art(x, y, dict(img=decor.asset('shrub', art.shrub, (x + y) % 3), solid={(0, 0)}, door=None))
    # fishing hut on the beach and boats on the shore
    cv.place_art(5, 24, dict(img=art.cabina('green'), solid={(0, 1)}, door=None), top_rows=1)
    cv.place_art(6, 36, dict(img=art.pedalo(), solid={(0, 0), (1, 0)}, door=None))
    old = mapio.old_events(NAME)
    o = [dict(e) for e in old['object_events']]
    o[0]['x'], o[0]['y'] = 4, 12
    o[1]['x'], o[1]['y'] = 5, 12
    cv.npcs = o
    cv.sign(6, 3, 'Romagna07_ShortcutSign')
    cv.border = [0x170, 0x170, 0x170, 0x170]
    return cv


STARTS = [(4, 0), (4, H - 1)]


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
