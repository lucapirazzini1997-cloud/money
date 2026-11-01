"""Verso Forlì (MAP_ROMAGNA_VERSO_FORLI): the Via Emilia under the Bertinoro hills, blocked by rockfalls."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import canvas, art, imports, mapio, check, world, decor
from canvas import Canvas, G
from decor import rect

NAME = 'Romagna_VersoForli'
TS = 'romagna17_versoforli'
W, H = world.size(NAME)


def build():
    cv = Canvas(W, H, name=NAME)
    fam, cob = imports.cobbles(imports.warm_stone)
    road = rect(0, 8, W, 2)
    cv.paint_family(fam, cob, road)
    # hillside vineyards north of the road, terraced by ledges
    vine = art.vine_row()
    for y in (2, 4):
        for x in range(4, 20):
            cv.place_art(x, y, dict(img=vine, solid={(0, 0)}, door=None))
        for x in range(30, 46):
            cv.place_art(x, y, dict(img=vine, solid={(0, 0)}, door=None))
    for x in range(2, 48):
        if x in (21, 22, 27, 28):
            continue
        cv.put(x, 6, G['ledge'], 0, 3)
    cv.put(2, 6, G['ledge_l'], 0, 3); cv.put(47, 6, G['ledge_r'], 0, 3)
    for (x, y) in rect(21, 0, 2, 8) | rect(27, 0, 2, 8):
        cv.path(x, y, 1, 1)
    cv.place_art(24, 1, art.farmhouse(), protect=False)
    # the Ronco south of the road with reeds and poplars
    cv.fill(0, 15, W, 4, 'sea')
    for x in range(W):
        cv.place_art(x, 14, dict(img=decor.asset('reeds', art.reeds, x % 3), solid={(0, 0)}, door=None) if x % 4 else
                     dict(img=decor.asset('dune', art.dune_grass, x % 4), solid=set(), door=None))
    decor.tall_grass(cv, rect(4, 11, 10, 3) | rect(32, 11, 12, 3))
    # rockfall narrowing the road around x=24
    for (x, y) in rect(20, 10, 3, 4) | rect(27, 10, 3, 4):
        cv.put(x, y, 0x0C5 if (x + y) % 2 else 0x18C, 1, 0) if False else None
    decor.woods(cv, rect(0, 0, 2, 8) | rect(48, 0, 2, 8) | rect(0, 19, W, 3) | rect(19, 10, 4, 4) | rect(26, 10, 4, 4),
                seed=41, pine_ratio=0.3, gaps=0.1)
    old = mapio.old_events(NAME)
    o = [dict(e) for e in old['object_events']]
    pos = {0: (23, 8), 1: (23, 9), 2: (25, 11), 3: (38, 9)}
    for i, e in enumerate(o):
        e['x'], e['y'] = pos[i]
    o[3]['movement_type'] = 'MOVEMENT_TYPE_FACE_LEFT'
    cv.npcs = o
    cv.warps = []
    cv.sign(30, 7, 'Romagna12_RoadSign')
    cv.border = [0x1D4, 0x1D5, 0x1DC, 0x1DD]
    return cv


STARTS = [(W - 1, 8)]


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
