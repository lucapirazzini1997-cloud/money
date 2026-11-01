"""Sentiero delle Saline (MAP_ROMAGNA_SENTIERO_SALINE): towpath along the canal from Cervia to the salt pans."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import canvas, art, imports, mapio, check, world, decor
from canvas import Canvas, G
from decor import rect

NAME = 'Romagna_SentieroSaline'
TS = 'romagna17_sentiero'
W, H = world.size(NAME)


def build():
    cv = Canvas(W, H, name=NAME)
    # canal continues from Cervia (Cervia rows 12..16 -> here 4..8)
    cv.fill(0, 5, W, 3, 'sea')
    fam, cob = imports.cobbles(imports.warm_stone)
    # cobbled quays only near Cervia, then an earth towpath
    cv.paint_family(fam, cob, rect(16, 2, 8, 2) | rect(16, 4, 8, 1) | rect(16, 8, 8, 1) | rect(16, 9, 8, 2))
    for (x, y) in rect(0, 9, 16, 2) | rect(0, 2, 16, 2):
        cv.path(x, y, 1, 1)
    rim_t, rim_b, face = art.quay_rim(True), art.quay_rim(False), art.quay_face()
    for x in range(16, W):
        cv.place_art(x, 4, dict(img=rim_t, solid=set(), door=None))
        cv.place_art(x, 8, dict(img=rim_b, solid=set(), door=None))
        cv.place_art(x, 5, dict(img=face, solid=set(), door=None))
    # natural banks with reeds west of the quays
    for x in range(0, 16):
        cv.fill(x, 4, 1, 1, 'sand')
        cv.fill(x, 8, 1, 1, 'sand')
        if x % 3 != 1:
            cv.place_art(x, 4, dict(img=decor.asset('reeds', art.reeds, x % 3), solid={(0, 0)}, door=None))
        if x % 4 == 0:
            cv.place_art(x, 8, dict(img=decor.asset('reeds', art.reeds, (x + 1) % 3), solid={(0, 0)}, door=None))
    # marsh north of the canal: tall grass and shrubs, a dead-end with an item
    decor.tall_grass(cv, rect(3, 0, 8, 2))
    decor.woods(cv, rect(11, 0, 5, 2) | rect(0, 0, 3, 2), seed=3, pine_ratio=0.0, gaps=0.1)
    # south: meadow with tall grass pockets, tamarisks (young pines) and a wooden fence
    decor.tall_grass(cv, rect(2, 12, 6, 3) | rect(12, 13, 5, 3))
    f = art.rustic_fence()
    fence = [(x, 11) for x in range(0, 24) if x not in (9, 10, 18, 19)]
    for (x, y) in fence:
        key = ''.join(k for k, (dx, dy) in zip('NESW', ((0, -1), (1, 0), (0, 1), (-1, 0))) if (x + dx, y + dy) in set(fence))
        cv.place_art(x, y, dict(img=f[key], solid={(0, 0)}, door=None))
    decor.woods(cv, rect(0, 16, W, 2) | rect(20, 12, 4, 4) | rect(8, 15, 3, 1), seed=4, pine_ratio=0.5, gaps=0.15)
    old = mapio.old_events(NAME)
    o = [dict(e) for e in old['object_events']]
    o[0]['x'], o[0]['y'] = 12, 10
    cv.npcs = o
    cv.border = [0x1D4, 0x1D5, 0x1DC, 0x1DD]
    return cv


STARTS = [(W - 1, 9), (0, 9)]


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
