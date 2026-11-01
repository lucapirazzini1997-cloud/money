"""Ippodromo del Savio (MAP_ROMAGNA_IPPODROMO): racetrack and meadows west of Cesena on the Via Emilia."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import canvas, art, imports, mapio, check, world, decor
from canvas import Canvas, G
from decor import rect

NAME = 'Romagna_Ippodromo'
TS = 'romagna17_ippodromo'
W, H = world.size(NAME)


def build():
    cv = Canvas(W, H, name=NAME)
    road = rect(0, 12, W, 2)
    fam, cob = imports.cobbles(imports.warm_stone)
    cv.paint_family(fam, cob, road)
    # racetrack: sand ring south of the road
    ring = rect(3, 15, 32, 12) - rect(7, 18, 24, 6)
    for (x, y) in ring:
        cv.fill(x, y, 1, 1, 'sand')
    rails = art.white_rail()
    def rail_line(cells):
        cs = set(cells)
        for (x, y) in cells:
            key = ''.join(k for k, (dx, dy) in zip('NESW', ((0, -1), (1, 0), (0, 1), (-1, 0))) if (x + dx, y + dy) in cs)
            cv.place_art(x, y, dict(img=rails[key], solid={(0, 0)}, door=None))
    inner = [(x, 17) for x in range(6, 32)] + [(x, 24) for x in range(6, 32)] + [(6, y) for y in range(18, 24)] + [(31, y) for y in range(18, 24)]
    rail_line([c for c in inner if c not in ((18, 24), (19, 24))])
    outer = [(x, 14) for x in range(2, 36) if x not in (17, 18, 19, 20)]
    rail_line(outer)
    # inner field: grass with tall grass where Ponyta graze
    decor.tall_grass(cv, rect(9, 19, 8, 4) | rect(22, 19, 7, 4))
    # grandstand and stables north of the road
    cv.place_art(13, 4, art.grandstand(9))
    stable = art.farmhouse()
    sd = cv.place_art(27, 3, stable)
    cv.place_art(4, 6, dict(img=art.haystack(), solid=rect(0, 0, 2, 2), door=None))
    f = art.rustic_fence()
    pad = [(x, 10) for x in range(2, 12)] + [(2, y) for y in range(3, 10)] + [(11, y) for y in range(3, 10) if y not in (8, 9)]
    ps = set(pad)
    for (x, y) in pad:
        key = ''.join(k for k, (dx, dy) in zip('NESW', ((0, -1), (1, 0), (0, 1), (-1, 0))) if (x + dx, y + dy) in ps)
        cv.place_art(x, y, dict(img=f[key], solid={(0, 0)}, door=None))
    decor.tall_grass(cv, rect(4, 3, 6, 3))
    # borders
    decor.woods(cv, rect(0, 0, W, 2) | rect(0, 26, W, 2) | rect(35, 15, 5, 11) | rect(0, 15, 2, 11) | rect(23, 2, 3, 8) | rect(35, 2, 5, 9),
                seed=31, pine_ratio=0.2, gaps=0.2)
    old = mapio.old_events(NAME)
    o = [dict(e) for e in old['object_events']]
    pos = {0: (21, 9), 1: (8, 11), 2: (25, 16), 3: (18, 16)}
    for i, e in enumerate(o):
        e['x'], e['y'] = pos[i]
    cv.npcs = o
    cv.warps = []
    cv.sign(36, 11, 'Romagna09_RaceSign')
    a = cv.art[sd[1]][sd[0]]
    cv.art[sd[1]][sd[0]] = (a[0], a[1], 1, 0, a[4])
    cv.border = [0x1D4, 0x1D5, 0x1DC, 0x1DD]
    return cv


STARTS = [(W - 1, 12), (0, 12)]


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
