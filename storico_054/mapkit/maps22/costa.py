"""Costa adriatica (34,21) 40x32 — road between Cesena (west) and Cesenatico (east) with the Pensione Pokémon.
The road crosses a band of tall grass (marsh meadows) that cannot be avoided."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import art, art22, imports, decor, r22
from canvas import G
from decor import rect
from campagna import fence_row

GN = (34, 21)
TS = 'r22_costa'
W, H = 40, 32
STARTS = [(0, 12), (0, 13), (39, 12), (39, 13)]


def build():
    cv = r22.RCanvas(W, H, GN)
    road = rect(0, 12, 14, 4) | rect(26, 12, 14, 4) | rect(9, 8, 2, 4)
    for (x, y) in road:
        cv.path(x, y, 1, 1)
    # tall grass band x 14..25, full height between the woods
    band = rect(14, 2, 12, H - 4)
    decor.tall_grass(cv, band)
    # Pensione Pokémon with its fenced yard
    pens = art22.pensione(8)
    door_p = cv.place_art(3, 2, pens, protect=True)
    yard = rect(3, 8, 0, 0)
    fence_row(cv, 2, 9, 11, gaps=(5,)) if False else None
    f = decor.asset('rfence', art.rustic_fence)
    fence = [(x, 7) for x in range(11, 13)] + [(12, y) for y in range(7, 11)] + [(x, 10) for x in range(2, 12) if x not in (9, 10)]
    fs = set(fence)
    for (x, y) in fence:
        key = ''.join(k for k, (dx, dy) in zip('NESW', ((0, -1), (1, 0), (0, 1), (-1, 0))) if (x + dx, y + dy) in fs)
        cv.place_art(x, y, dict(img=f[key], solid={(0, 0)}, door=None))
    for (x, y) in ((4, 8), (6, 8)):
        cv.put(x, y, G['flowers'])
    # south: pinewood and dunes towards the sea, a sandy track with benches
    for (x, y) in rect(2, 20, 12, 3):
        cv.path(x, y, 1, 1)
    pine = decor.asset('pine', art.umbrella_pine)
    for (x, y) in ((2, 23), (5, 24), (8, 23), (11, 25), (3, 27), (7, 27), (27, 20), (31, 22), (35, 20), (29, 25), (33, 26)):
        cv.place_art(x, y, dict(img=pine, solid={(0, 1), (1, 1)}, door=None), top_rows=1)
    decor.tall_grass(cv, rect(27, 2, 10, 5) | rect(2, 17, 3, 2))
    for (x, y) in ((28, 9), (34, 8), (36, 17), (30, 17)):
        cv.place_art(x, y, dict(img=decor.asset('rtree', art.round_tree, seed=4), solid={(0, 1)}, door=None), top_rows=1)
    for (x, y) in ((4, 21), (9, 21)):
        cv.place_art(x, y, dict(img=decor.asset('bench', art.bench), solid={(0, 0)}, door=None))
    # borders
    border = rect(0, 0, W, 2) | rect(0, H - 2, W, 2) | rect(0, 2, 2, 10) | rect(0, 16, 2, 14) | rect(W - 2, 2, 2, 10) | rect(W - 2, 16, 2, 14)
    decor.woods(cv, border, seed=12, pine_ratio=0.5, gaps=0.0)
    for (x, y) in ((1, 10), (1, 16), (38, 10), (38, 16)):
        cv.place_art(x, y, art22.pillar(), top_rows=0) if False else None
    # ---------------- events
    cv.place_objs({1: (20, 14), 2: (30, 13)})
    cv.add_obj(10, 9, 29, 0x291f89, move=8)          # daycare man (vanilla script)
    cv.bwarps = [dict(x=door_p[0], y=door_p[1], elev=0, warp=0, num=0, group=22)]
    cv.add_sign(7, 11, 'R22_SignPensione')
    cv.add_sign(2, 11, 'R22_SignCostaW')
    cv.add_sign(37, 11, 'R22_SignCostaE')
    for bb in cv.bbgs:
        cv.put(bb['x'], bb['y'], G['sign'], 1, 3)
    cv.doors = dict(pensione=door_p)
    return cv
