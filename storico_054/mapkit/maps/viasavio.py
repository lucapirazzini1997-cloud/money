"""Via del Savio (MAP_ROMAGNA_VIA_SAVIO): countryside road from Cervia to Cesena, orchards, vines and the river."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import canvas, art, imports, mapio, check, world, decor
from canvas import Canvas, G
from decor import rect

NAME = 'Romagna_ViaSavio'
TS = 'romagna17_viasavio'
W, H = world.size(NAME)


def build():
    cv = Canvas(W, H, name=NAME)
    # the Savio along the west edge
    cv.fill(0, 0, 3, H, 'sea')
    for y in range(H):
        cv.place_art(3, y, dict(img=decor.asset('reeds', art.reeds, y % 3), solid={(0, 0)}, door=None))
    road = rect(14, 0, 2, 9) | rect(14, 8, 8, 2) | rect(20, 8, 2, 17) | rect(14, 23, 8, 2) | rect(14, 23, 2, 17)
    road |= rect(6, 31, 8, 2)                 # lane to the farm
    road |= rect(22, 3, 5, 2)                 # side lane into the orchard (closed by small trees)
    for (x, y) in road:
        cv.path(x, y, 1, 1)
    # vineyard (west of the road)
    vine = art.vine_row()
    for y in range(12, 22, 2):
        for x in range(5, 13):
            cv.place_art(x, y, dict(img=vine, solid={(0, 0)}, door=None))
    # peach orchard (east)
    peach = art.peach_tree()
    for y in range(1, 19, 3):
        for x in range(24, 29, 2):
            if (x, y) in ((24, 1),):
                continue
            cv.place_art(x, y, dict(img=peach, solid={(0, 1)}, door=None), top_rows=1)
    # farmhouse, haystacks, fenced yard
    farm = art.farmhouse()
    fd = cv.place_art(4, 26, farm)
    hay = art.haystack()
    cv.place_art(11, 27, dict(img=hay, solid=rect(0, 0, 2, 2), door=None))
    cv.place_art(4, 33, dict(img=hay, solid=rect(0, 0, 2, 2), door=None))
    f = art.rustic_fence()
    fence = [(x, 35) for x in range(4, 14)] + [(13, y) for y in range(26, 35) if y not in (31, 32)]
    fs = set(fence)
    for (x, y) in fence:
        key = ''.join(k for k, (dx, dy) in zip('NESW', ((0, -1), (1, 0), (0, 1), (-1, 0))) if (x + dx, y + dy) in fs)
        cv.place_art(x, y, dict(img=f[key], solid={(0, 0)}, door=None))
    # tall grass along the road (encounters)
    decor.tall_grass(cv, rect(16, 11, 4, 6) | rect(22, 26, 6, 5) | rect(16, 33, 6, 4) | rect(5, 4, 7, 4))
    # hedgerows / poplar-like trees at the field borders
    decor.woods(cv, rect(4, 0, 9, 3) | rect(4, 8, 9, 2) | rect(23, 21, 7, 4) | rect(17, 0, 3, 7) | rect(22, 32, 8, 8)
                | rect(4, 37, 9, 3) | rect(28, 0, 2, 21), seed=11, pine_ratio=0.15, gaps=0.2)
    old = mapio.old_events(NAME)
    o = [dict(e) for e in old['object_events']]
    pos = {0: (19, 18), 1: (22, 3), 2: (22, 4), 3: (17, 9)}
    for i, e in enumerate(o):
        e['x'], e['y'] = pos[i]
    o[0]['movement_type'] = 'MOVEMENT_TYPE_FACE_RIGHT'
    cv.npcs = o
    # a hidden item at the end of the orchard lane
    cv.border = [0x1D4, 0x1D5, 0x1DC, 0x1DD]
    # locked farmhouse door (no interior)
    a = cv.art[fd[1]][fd[0]]
    cv.art[fd[1]][fd[0]] = (a[0], a[1], 1, 0, a[4])
    cv.sign(fd[0], fd[1], 'Romagna17_LockedDoor')
    return cv


STARTS = [(14, 0), (14, H - 1)]


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
