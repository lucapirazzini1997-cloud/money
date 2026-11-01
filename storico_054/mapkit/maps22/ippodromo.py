"""Ippodromo del Savio (34,19) 48x34 — Cesena's trotting track: light sand oval with white rails, the finish line,
the covered grandstand and the judges' tower on the north straight, the infield lawn with the totalisator and a
small lake, the stables, the entrance from Cesena (south) and the path to the west."""
import sys, math, random
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import art, art22, decor, imports, r22
from art import Px, C
from canvas import G
from decor import rect
from _town import tree, lamp, bench, fill_lawns

GN = (34, 19)
TS = 'r22_ippodromo'
W, H = 48, 34
STARTS = [(19, 33), (0, 16)]

# stadium-shaped track in pixels: outer rounded rectangle, inner rounded rectangle
OX0, OY0, OX1, OY1, OR = 5 * 16, 9 * 16, 43 * 16, 28 * 16, 64
TW = 40                                                       # track width in pixels


def _rr_dist(px, py, x0, y0, x1, y1, r):
    """Signed distance-ish: <0 inside the rounded rectangle."""
    cx = min(max(px, x0 + r), x1 - r); cy = min(max(py, y0 + r), y1 - r)
    return math.hypot(px - cx, py - cy) - r


def _cell(x, y):
    g = Px(16, 16)
    kinds = set()
    for py in range(16):
        for px in range(16):
            X, Y = x * 16 + px + .5, y * 16 + py + .5
            d = _rr_dist(X, Y, OX0, OY0, OX1, OY1, OR)
            if d > 0:
                c = C(115, 189, 107) if (px + py) % 7 else C(99, 173, 90); k = 'out'
            elif d > -3:
                c = C(255, 255, 255); k = 'rail'
            elif d > -TW + 3:
                c = C(222, 196, 148) if (px * 3 + py * 5 + x + y) % 11 else C(198, 173, 132); k = 'track'
                if 22 * 16 <= X < 22 * 16 + 4 and Y < OY0 + TW + 16:          # finish line (north straight)
                    c = C(255, 255, 255)
            elif d > -TW:
                c = C(255, 255, 255); k = 'rail'
            else:
                c = C(132, 206, 115) if (px + py) % 7 else C(115, 189, 99); k = 'in'
            if k == 'out':
                g.im.putpixel((px, py), (0, 0, 0, 0))
            else:
                g.p(px, py, c)
            kinds.add(k)
    return g.im, kinds


def build():
    cv = r22.RCanvas(W, H, GN)
    fam, cob = imports.cobbles(imports.warm_stone)
    cv.paint_family(fam, cob, rect(17, 29, 6, 5) | rect(0, 15, 5, 3) | rect(2, 2, 44, 1))
    track_cells = set()
    for y in range(H):
        for x in range(W):
            X0, Y0 = x * 16, y * 16
            if X0 + 16 < OX0 - 2 or X0 > OX1 + 2 or Y0 + 16 < OY0 - 2 or Y0 > OY1 + 2:
                continue
            im, kinds = _cell(x, y)
            if kinds == {'out'}:
                continue
            cv.place_art(x, y, dict(img=im, solid=set(), door=None), walkable=True)
            track_cells.add((x, y))
    # north: the grandstand and the judges' tower, facing the home straight
    cv.place_art(8, 3, art22.tribuna(14), protect=True)
    cv.place_art(23, 4, art22.judges_tower(), top_rows=2, protect=True)
    # infield: totalisator, a small lake, flower beds and benches for the trainers
    cv.place_art(20, 16, art22.totalizzatore(5), protect=True)
    for (x, y) in rect(28, 17, 5, 3):
        cv.fill(x, y, 1, 1, 'pond')
        cv.art[y][x] = None
    fb = decor.asset('fb1', art.flowerbed, ((239, 99, 132), (255, 206, 66)))
    for (x, y) in ((14, 16), (15, 16), (14, 21), (15, 21), (35, 21), (36, 21)):
        cv.place_art(x, y, dict(img=fb, solid={(0, 0)}, door=None))
    # stables south-east, ticket gate south, poplars all around
    cv.place_art(31, 29, art22.scuderie(8), protect=True)
    cv.place_art(8, 29, dict(img=decor.asset('kiosk', art.kiosk), solid=rect(0, 0, 2, 2), door=None), protect=True)
    for (x, y) in ((16, 30), (23, 30)):
        lamp(cv, x, y)
    border = rect(0, 0, W, 2) | rect(0, 2, 2, 13) | rect(0, 18, 2, 16) | rect(46, 2, 2, 32) | rect(2, 32, 15, 2) | rect(23, 32, 8, 2)
    decor.woods(cv, border, seed=19, pine_ratio=0.1, gaps=0.0)
    # ---------------- events (same order as 0.21)
    for i, x in ((0, 20), (3, 18), (4, 19), (5, 21)):
        cv.set_warp(i, x, H - 1)
    cv.set_warp(1, 0, 16); cv.set_warp(2, 0, 17)
    cv.place_objs({1: (21, 26), 2: (10, 11), 3: (38, 18), 4: (12, 25)})
    cv.border = [0x1D4, 0x1D5, 0x1DC, 0x1DD]
    return cv
