"""Campagna cervese (34,20) 32x40 — farmland between Cervia and Cesena, with the Casa delle Aie.

The only way south crosses the tall grass of the wheat fields (no way around)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import art, art22, imports, decor, r22
from canvas import G
from decor import rect

GN = (34, 20)
TS = 'r22_campagna'
W, H = 32, 40
STARTS = [(2, 0), (3, 0), (2, 6), (15, 39)]


def fence_row(cv, x0, x1, y, gaps=()):
    f = decor.asset('rfence', art.rustic_fence)
    xs = [x for x in range(x0, x1) if x not in gaps]
    for x in xs:
        key = ('E' if x + 1 in xs else '') + ('W' if x - 1 in xs else '')
        cv.place_art(x, y, dict(img=f[key], solid={(0, 0)}, door=None))


def build():
    cv = r22.RCanvas(W, H, GN)
    # ---------------- dirt lanes
    lane = rect(2, 0, 4, 3) | rect(2, 3, 2, 3) | rect(2, 6, 4, 5) | rect(4, 10, 12, 2) | rect(14, 10, 4, 30)
    lane |= rect(17, 12, 6, 2)
    for (x, y) in lane:
        cv.path(x, y, 1, 1)
    # ---------------- Casa delle Aie with its aia (threshing yard), pergola and tables
    aie = art22.casa_aie(11)
    door_aie = cv.place_art(19, 0, aie, protect=True)
    for (x, y) in rect(18, 6, 12, 6):           # gravel courtyard (aia)
        cv.path(x, y, 1, 1)
    cv.place_art(door_aie[0] - 1, 7, art22.entrata_sign(), top_rows=1, protect=True)
    cv.place_art(19, 7, art22.planter(3)); cv.place_art(26, 7, art22.planter(3))
    cv.place_art(19, 10, art22.rope_fence(3)); cv.place_art(26, 10, art22.rope_fence(3))
    for (x, y) in ((24, 8), (27, 8)) if False else ():
        cv.place_art(x, y, art22.aia_table())
    pine = decor.asset('pine', art.umbrella_pine)
    for (x, y) in ((16, 2), (16, 5)):
        cv.place_art(x, y, dict(img=pine, solid={(0, 1), (1, 1)}, door=None), top_rows=1)
    for (x, y) in ((18, 8), (29, 8)):
        cv.place_art(x, y, dict(img=decor.asset('lamp', art.lamp), solid={(0, 1)}, door=None), top_rows=1)
    # ---------------- Cut gate at the entrance from Cervia (story gate of 0.21)
    decor.woods(cv, rect(4, 3, 2, 3) | rect(6, 0, 12, 2) | rect(6, 2, 4, 8), seed=3, pine_ratio=0.0, gaps=0.0)
    # ---------------- fields: vineyard, sunflowers, orchard, wheat (tall grass)
    for y in range(14, 19, 2):
        for x in range(2, 13):
            cv.place_art(x, y, dict(img=decor.asset('vine', art.vine_row), solid={(0, 0)}, door=None))
    for x in range(19, 30):
        cv.place_art(x, 15, dict(img=decor.asset('sun', art.sunflower_row), solid={(0, 0)}, door=None))
        cv.place_art(x, 17, dict(img=decor.asset('sun', art.sunflower_row), solid={(0, 0)}, door=None))
    # wheat: the tall grass band that must be crossed (rows 21..26, wall to wall)
    wheat = rect(2, 21, W - 4, 6)
    decor.tall_grass(cv, wheat)
    fence_row(cv, 2, 14, 20); fence_row(cv, 18, W - 2, 20)
    fence_row(cv, 2, 14, 27); fence_row(cv, 18, W - 2, 27)
    for (x, y) in wheat:
        cv.pathmask[y][x] = False
    # meadow with tall grass and a pond south of the wheat
    decor.tall_grass(cv, rect(3, 29, 9, 4) | rect(18, 29, 5, 6))
    pond = rect(5, 34, 6, 3)
    for (x, y) in pond:
        cv.fill(x, y, 1, 1, 'pond')
    cv.place_art(22, 28, dict(img=decor.asset('hay', art.haystack), solid=rect(0, 0, 2, 2), door=None))
    farm = art.farmhouse()
    locked = [cv.place_art(24, 31, farm)]
    for (x, y) in ((2, 28), (12, 28), (18, 29), (12, 35), (29, 29)):
        cv.place_art(x, y, dict(img=decor.asset('peach', art.peach_tree, 2), solid={(0, 1)}, door=None), top_rows=1)
    # borders
    border = rect(0, 0, 2, H) | rect(W - 2, 0, 2, H) | rect(2, H - 2, 12, 2) | rect(18, H - 2, 12, 2)
    border |= rect(10, 2, 8, 6) - rect(14, 2, 0, 0)
    decor.woods(cv, border - lane, seed=6, pine_ratio=0.2, gaps=0.0)
    cv.place_art(13, H - 4, art22.city_gate(6, 'CESENA'), top_rows=1, protect=True)
    # ---------------- events
    cv.place_objs({1: (16, 19), 2: (2, 4), 3: (3, 4), 4: (5, 2)})
    cv.objs[0]['move'] = 8
    cv.bwarps = [dict(x=door_aie[0], y=door_aie[1], elev=0, warp=0, num=0, group=0)]   # dest filled by the build
    cv.add_sign(17, 10, 'R22_SignAie')
    cv.add_sign(13, 12, 'R22_SignCampagna')
    for bb in cv.bbgs:
        cv.put(bb['x'], bb['y'], G['sign'], 1, 3)
    for dd in locked:
        cv.locked(dd)
    cv.doors = dict(aie=door_aie)
    return cv
