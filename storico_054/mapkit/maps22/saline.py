"""Saline di Cervia (34,9) 64x48 — salt pans like the real ones: many rectangular evaporation basins of
different sizes separated by narrow earth embankments (argini), pink and grey-blue brine, the white
crystallising pans of the historic Salina Camillone with salt heaps, birdwatching huts, the visitor
centre, reed beds and tamarisks. Flamingos (elevation 1) wade inside the basins; the player walks on
the embankments only. East edge: gatehouse to Cervia (door on its west face)."""
import sys, random
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import art, art22, decor, r22
from art import Px, C, PAL
from canvas import G
from decor import rect

GN = (34, 9)
TS = 'r22_saline'
W, H = 64, 48
STARTS = [(59, 24)]

TINTS = {
    'pink': [C(239, 173, 181), C(222, 148, 165), C(198, 115, 140)],
    'grey': [C(156, 189, 206), C(132, 165, 189), C(107, 140, 165)],
    'teal': [C(140, 206, 198), C(115, 181, 181), C(90, 156, 156)],
    'salt': [C(247, 247, 239), C(231, 231, 222), C(206, 206, 198)],
}
MUD = C(156, 123, 90)
_TILES = {}


def pan_tile(tint, n, e, s, w, var):
    """One 16x16 cell of a basin: brine with ripples, a muddy rim on the sides that touch an embankment."""
    k = (tint, n, e, s, w, var)
    if k in _TILES:
        return _TILES[k]
    c = TINTS[tint]
    g = Px(16, 16)
    g.rect(0, 0, 16, 16, c[0])
    if tint == 'salt':
        rnd = random.Random(var)
        for _ in range(10):
            g.p(rnd.randrange(16), rnd.randrange(16), c[2])
        g.rect(3 + var * 3, 5, 3, 2, C(255, 255, 255))
    else:
        if var == 1:
            g.hline(3, 5, 5, c[1]); g.hline(9, 11, 4, c[1])
        elif var == 2:
            g.hline(8, 3, 5, c[1]); g.hline(2, 12, 4, c[1]); g.p(12, 8, C(255, 255, 255))
    if n: g.rect(0, 0, 16, 3, MUD); g.hline(0, 3, 16, c[2])
    if s: g.rect(0, 14, 16, 2, MUD); g.hline(0, 13, 16, c[1])
    if w: g.rect(0, 0, 2, 16, MUD); g.vline(2, 0, 16, c[2])
    if e: g.rect(14, 0, 2, 16, MUD); g.vline(13, 0, 16, c[1])
    _TILES[k] = g.im
    return g.im


def basin(cv, x0, y0, w, h, tint, heaps=False):
    cells = rect(x0, y0, w, h)
    for (x, y) in cells:
        cv.fill(x, y, 1, 1, 'pond')
        n, s = (x, y - 1) not in cells, (x, y + 1) not in cells
        we, e = (x - 1, y) not in cells, (x + 1, y) not in cells
        img = pan_tile(tint, n, e, s, we, (x * 7 + y * 3) % 3)
        cv.place_art(x, y, dict(img=img, solid=set(), door=None), behaviors={(0, 0): 0x17})
    if heaps:
        for i, x in enumerate(range(x0 + 1, x0 + w - 1, 3)):
            cv.place_art(x, y0 + 1 + (i % 2), dict(img=salt_heap(), solid={(0, 0)}, door=None))
    return cells


def salt_heap():
    g = Px(16, 16)
    for y in range(4, 15):
        half = (y - 3) * 7 // 11
        g.hline(8 - half, y, 2 * half + 1, C(255, 255, 255) if y < 10 else C(231, 231, 222))
    g.hline(2, 15, 12, C(198, 198, 189))
    g.outline()
    return g.im


def capanno():
    """Birdwatching hide: dark timber hut with an observation slit, on short stilts."""
    g = Px(32, 32)
    g.rect(2, 4, 28, 4, C(99, 74, 49)); g.hline(1, 4, 30, C(132, 99, 66))
    g.rect(3, 8, 26, 16, C(140, 107, 74))
    for x in range(3, 29, 4):
        g.vline(x, 8, 16, C(115, 82, 57))
    g.rect(6, 12, 20, 3, C(33, 24, 24))
    for x in (5, 26):
        g.rect(x, 24, 2, 7, C(99, 74, 49))
    g.outline()
    return dict(img=g.im, solid={(0, 0), (1, 0), (0, 1), (1, 1)}, door=None)


def salt_cart():
    g = Px(32, 16)
    g.rect(4, 3, 20, 8, C(140, 99, 66)); g.rect(5, 1, 18, 4, C(255, 255, 255))
    g.rect(24, 6, 7, 2, C(99, 74, 49))
    g.rect(8, 10, 5, 5, C(66, 49, 41)); g.p(10, 12, C(140, 99, 66))
    g.outline()
    return dict(img=g.im, solid={(0, 0), (1, 0)}, door=None)


def build():
    cv = r22.RCanvas(W, H, GN)
    cv.conns = [c for c in cv.conns if not (c['dir'] == 4)]       # east: gatehouse instead of the old path
    # ---------------- embankments everywhere, basins cut into them
    dirt = rect(2, 2, 58, 44)
    for (x, y) in dirt:
        cv.path(x, y, 1, 1)
    water = set()
    # western evaporation basins (big, brine getting pinker towards the crystallisers)
    for (x, y, w, h, t) in ((3, 3, 11, 7, 'grey'), (15, 3, 9, 7, 'grey'), (25, 3, 12, 7, 'teal'),
                            (3, 11, 7, 11, 'grey'), (11, 11, 13, 5, 'teal'), (11, 17, 13, 5, 'pink'), (25, 11, 12, 11, 'grey'),
                            (3, 28, 9, 8, 'teal'), (13, 28, 12, 8, 'pink'), (26, 28, 11, 8, 'pink'),
                            (3, 37, 15, 8, 'grey'), (19, 37, 8, 8, 'teal'), (28, 37, 9, 8, 'pink')):
        water |= basin(cv, x, y, w, h, t)
    # Salina Camillone: small crystallising pans with salt heaps (east, south of the road)
    for (x, y, w, h) in ((40, 29, 5, 4), (46, 29, 5, 4), (40, 34, 5, 4), (46, 34, 5, 4)):
        water |= basin(cv, x, y, w, h, 'salt', heaps=True)
    # canal feeding the basins (north of the main embankment)
    for (x, y, w, h, t) in ((38, 3, 4, 19, 'teal'),):
        water |= basin(cv, x, y, w, h, t)
    # main embankment (2 wide) from the gatehouse west across the pans: rows 24-25
    for (x, y) in rect(2, 23, 58, 4):
        cv.path(x, y, 1, 1)
    fam, cob = __import__('imports').cobbles(__import__('imports').warm_stone)
    cv.paint_family(fam, cob, rect(40, 24, 20, 2))                 # gravel road to the visitor centre
    # ---------------- borders: tamarisks and pines, reed beds along the basins
    border = (rect(0, 0, W, 2) | rect(0, H - 2, W, 2) | rect(0, 0, 2, H) | rect(60, 0, 4, 20) | rect(60, 25, 4, H - 25))
    decor.woods(cv, border, seed=21, pine_ratio=0.4, gaps=0.0)
    for x in list(range(3, 37, 3)):
        cv.place_art(x, 2, dict(img=decor.asset('reeds', art.reeds, x % 3), solid={(0, 0)}, door=None))
    for y in range(28, 45, 3):
        cv.place_art(2, y, dict(img=decor.asset('reeds', art.reeds, y % 3), solid={(0, 0)}, door=None))
    # tall grass: salicornia meadows (wild Pokémon), east of the canal and south-east corner
    tall = rect(43, 3, 4, 7) | rect(53, 39, 6, 6) | rect(3, 22, 8, 1) | rect(20, 26, 10, 1)
    decor.tall_grass(cv, tall)
    for (x, y) in tall:
        cv.pathmask[y][x] = False
    # ---------------- buildings
    doors = {}
    doors['gate'] = cv.place_art(60, 20, art22.gatehouse('west', 'CERVIA'), protect=True)
    gx, gy = doors['gate']
    a = cv.art[gy][gx]; cv.art[gy][gx] = (a[0], a[1], 0, 0x62, a[4])     # side passage: east arrow warp
    doors['centro'] = cv.place_art(48, 12, art.warehouse(6, 'CENTRO VISITE'), protect=True)
    locked = [cv.place_art(53, 29, art.house(4, 1, 'cream', roof='roof', shutters='green_sh', seed=7))]   # casa del salinaro
    # birdwatching huts on the embankments
    for (x, y) in ((6, 26), (31, 26)):
        cv.place_art(x, y, capanno())
    cv.place_art(55, 33, salt_cart())
    for (x, y) in ((44, 22), (52, 22), (56, 20)):
        cv.place_art(x, y, dict(img=decor.asset('rtree', art.round_tree, seed=4), solid={(0, 1)}, door=None), top_rows=1)
    for (x, y) in ((47, 27), (57, 27)):
        cv.place_art(x, y, dict(img=decor.asset('bench', art.bench), solid={(0, 0)}, door=None))
    # ---------------- events (same order as 0.21)
    o = cv.objs
    pos = {1: (45, 25), 2: (52, 20), 3: (56, 25), 4: (8, 6), 5: (30, 6), 6: (16, 14), 7: (30, 32)}
    cv.place_objs(pos)
    for i in (3, 4, 5, 6):                       # flamingos wade inside the basins
        o[i]['elev'] = 1; o[i]['move'] = 2; o[i]['rx'] = 3; o[i]['ry'] = 2
    cv.set_warp(0, *doors['centro'])
    cv.bwarps.append(dict(x=doors['gate'][0], y=doors['gate'][1], elev=0, warp=1, num=0, group=0))   # fixed by the build
    b = cv.bbgs
    b[0]['x'], b[0]['y'] = doors['centro'][0] - 2, doors['centro'][1] + 1
    cv.add_sign(58, 26, 'R22_SignSaline')
    for bb in cv.bbgs:
        cv.put(bb['x'], bb['y'], G['sign'], 1, 3)
    for dd in locked:
        cv.locked(dd)
    cv.doors = doors
    cv.border = [0x1D4, 0x1D5, 0x1DC, 0x1DD]
    return cv
