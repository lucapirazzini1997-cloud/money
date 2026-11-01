"""Strada del Mare (MAP_ROMAGNA_STRADA_MARE): flat farmland with sunflowers and drainage canals, Cesena -> Cesenatico."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import canvas, art, imports, mapio, check, world, decor
from canvas import Canvas, G
from decor import rect

NAME = 'Romagna_StradaMare'
TS = 'romagna17_stradamare'
W, H = world.size(NAME)


def build():
    cv = Canvas(W, H, name=NAME)
    fam, cob = imports.cobbles(imports.warm_stone)
    cv.paint_family(fam, cob, rect(0, 12, W, 2))
    # drainage canal crossing north-south, bridged by the road
    cv.fill(20, 0, 2, 12, 'sea'); cv.fill(20, 14, 2, H - 14, 'sea')
    for y in range(0, H):
        if y in (12, 13):
            continue
        for x in (19, 22):
            cv.place_art(x, y, dict(img=decor.asset('reeds', art.reeds, (x + y) % 3), solid={(0, 0)}, door=None) if (y % 3) else
                         dict(img=decor.asset('dune', art.dune_grass, y % 4), solid=set(), door=None))
    rail = art.white_rail()
    for x in (19, 22):
        for y in (11, 14):
            cv.place_art(x, y, dict(img=rail['EW'], solid={(0, 0)}, door=None))
    # fields: sunflowers (north-west), wheat (north-east), vines (south)
    sun, wh, vine = art.sunflower_row(), art.wheat(), art.vine_row()
    for y in range(2, 10):
        for x in range(2, 17):
            if (x, y) in rect(8, 5, 3, 3):
                continue
            cv.place_art(x, y, dict(img=sun, solid={(0, 0)}, door=None))
    for y in range(2, 10):
        for x in range(25, 41):
            cv.place_art(x, y, dict(img=wh, solid={(0, 0)}, door=None))
    for y in (17, 19, 21):
        for x in range(25, 41):
            cv.place_art(x, y, dict(img=vine, solid={(0, 0)}, door=None))
    # paths between fields, tall grass along the canal and by the farm
    for (x, y) in rect(17, 0, 2, 12) | rect(23, 0, 2, 12) | rect(8, 14, 2, 8):
        cv.path(x, y, 1, 1)
    decor.tall_grass(cv, rect(2, 15, 5, 4) | rect(11, 16, 7, 4) | rect(23, 15, 2, 9))
    farm = art.farmhouse()
    fd = cv.place_art(2, 19, farm) if False else None
    cv.place_art(28, 9, dict(img=art.kiosk(), solid=rect(0, 0, 2, 2), door=None), protect=True)
    for (x, y) in [(0, 0), (0, 2), (42, 0), (42, 2)]:
        pass
    decor.woods(cv, rect(0, 22, 19, 4) | rect(23, 23, 21, 3) | rect(41, 0, 3, 11) | rect(0, 0, 2, 11) | rect(41, 15, 3, 8),
                seed=61, pine_ratio=0.25, gaps=0.15)
    old = mapio.old_events(NAME)
    o = [dict(e) for e in old['object_events']]
    pos = {0: (14, 14), 1: (21, 15)}
    for i, e in enumerate(o):
        e['x'], e['y'] = pos[i]
    o[1]['x'], o[1]['y'] = 18, 16
    cv.npcs = o
    cv.border = [0x1D4, 0x1D5, 0x1DC, 0x1DD]
    return cv


STARTS = [(0, 12), (W - 1, 12)]


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
