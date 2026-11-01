"""Cesena interiors drawn by hand: the great hall of the Rocca Malatestiana (34,32).
The exit to the Parco della Rocca (hedge maze) is the big door in the back wall."""
import sys, random, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import interior as I
from interior import Room
from art import Px, C, PAL
from lido_int import set_walls, set_floor, objs_of, warps_of
from cervia_int import red_runner

STONE = [C(206, 189, 156), C(181, 165, 132), C(148, 132, 107), C(107, 90, 74)]


def stone_wall_top(x):
    g = Px(16, 16)
    g.rect(0, 0, 16, 16, STONE[1])
    g.rect(0, 0, 16, 5, C(74, 66, 66)); g.hline(0, 5, 16, STONE[3])                     # vault shadow
    for y in range(6, 16, 5):
        g.hline(0, y, 16, STONE[3])
        o = 0 if (y // 5) % 2 else 8
        g.vline(o, y + 1, 4, STONE[3]); g.p(o + 3, y + 2, STONE[0])
    return g.im


def stone_wall_low(x):
    g = Px(16, 16)
    g.rect(0, 0, 16, 16, STONE[1])
    for y in range(0, 13, 5):
        g.hline(0, y, 16, STONE[3])
        o = 8 if (y // 5) % 2 else 0
        g.vline(o, y + 1, 4, STONE[3]); g.p(o + 4, y + 2, STONE[0])
    g.rect(0, 13, 16, 3, STONE[2]); g.hline(0, 15, 16, STONE[3])
    return g.im


def flagstone(x, y):
    g = Px(16, 16)
    g.rect(0, 0, 16, 16, C(173, 165, 148))
    rnd = random.Random(x * 17 + y * 5)
    sx = rnd.choice([5, 7, 9])
    g.hline(0, 0, 16, C(132, 123, 107)); g.vline(0, 0, 8, C(132, 123, 107)); g.hline(0, 8, 16, C(132, 123, 107)); g.vline(sx, 8, 8, C(132, 123, 107))
    for _ in range(3):
        g.p(rnd.randrange(16), rnd.randrange(16), C(156, 148, 132))
    return g.im


def banner():
    """Malatesta banner: black and white chequer with the red elephant-like crest stripe."""
    g = Px(16, 32)
    g.hline(1, 1, 14, C(99, 66, 41))
    g.rect(3, 2, 10, 24, C(255, 255, 255))
    for y in range(2, 26, 3):
        for x in range(3, 13, 3):
            if ((x - 3) // 3 + (y - 2) // 3) % 2: g.rect(x, y, 3, 3, C(33, 33, 41))
    g.rect(3, 12, 10, 4, C(181, 33, 41))
    for i in range(5): g.hline(3 + i, 26 + i, 10 - 2 * i, C(33, 33, 41) if i % 2 else C(255, 255, 255))
    g.outline()
    return g.im


def torch():
    g = Px(16, 16)
    g.rect(7, 7, 3, 7, C(99, 66, 41)); g.rect(6, 6, 5, 2, C(66, 66, 74))
    g.rect(7, 2, 3, 4, C(255, 156, 49)); g.p(8, 1, C(255, 231, 115)); g.p(8, 3, C(255, 231, 115))
    g.outline()
    return g.im


def armour():
    g = Px(16, 32)
    s = [C(222, 222, 231), C(181, 181, 198), C(132, 132, 148)]
    g.rect(5, 2, 6, 6, s[1]); g.hline(6, 5, 4, C(33, 33, 41)); g.p(8, 1, C(206, 41, 49))
    g.rect(4, 8, 8, 9, s[0]); g.vline(8, 8, 9, s[2]); g.rect(2, 9, 2, 8, s[1]); g.rect(12, 9, 2, 8, s[1])
    g.vline(14, 2, 22, C(132, 99, 66)); g.rect(13, 1, 3, 3, s[0])                                     # halberd
    g.rect(5, 17, 2, 9, s[1]); g.rect(9, 17, 2, 9, s[1])
    g.rect(3, 26, 10, 5, STONE[2]); g.hline(3, 26, 10, STONE[0])
    g.outline()
    return dict(img=g.im, solid={(0, 1)})


def cannon():
    g = Px(32, 16)
    g.rect(4, 4, 22, 6, C(66, 66, 74)); g.hline(4, 4, 22, C(115, 115, 123)); g.rect(26, 3, 4, 8, C(57, 57, 66))
    for cx in (9, 20):
        for a in range(16):
            x = cx + round(4 * math.cos(a * math.pi / 8)); y = 11 + round(4 * math.sin(a * math.pi / 8))
            g.p(x, y, C(99, 66, 41))
        g.p(cx, 11, C(66, 49, 41))
    g.rect(1, 12, 4, 3, C(33, 33, 41))                                                               # cannon balls
    g.outline()
    return dict(img=g.im, solid={(0, 0), (1, 0)})


def weapon_rack():
    g = Px(32, 32)
    g.rect(2, 26, 28, 4, C(99, 66, 41)); g.rect(2, 4, 28, 3, C(99, 66, 41))
    for x in range(5, 28, 6):
        g.vline(x, 1, 26, C(140, 99, 66)); g.rect(x - 1, 0, 3, 3, C(198, 198, 214))
    g.rect(12, 9, 8, 10, C(173, 41, 49)); g.rect(14, 11, 4, 6, C(239, 206, 99))                       # shield
    g.outline()
    return dict(img=g.im, solid={(0, 0), (1, 0), (0, 1), (1, 1)})


def long_table():
    g = Px(64, 32)
    g.rect(2, 6, 60, 14, C(132, 82, 49)); g.hline(2, 6, 60, C(173, 115, 74)); g.rect(2, 20, 60, 3, C(99, 57, 33))
    for x in (5, 56): g.rect(x, 23, 3, 8, C(99, 57, 33))
    g.rect(10, 9, 6, 5, C(239, 231, 206)); g.rect(28, 8, 3, 7, C(239, 206, 99)); g.p(29, 7, C(255, 156, 49))   # parchment, candle
    g.rect(40, 9, 8, 4, C(189, 156, 107))                                                              # map of the Rocca
    g.outline()
    return dict(img=g.im, solid={(a, b) for a in range(4) for b in range(2)})


def big_door():
    """Iron-studded oak door in the back wall (lower wall row) with an arch."""
    g = Px(32, 32)
    g.rect(0, 0, 32, 32, STONE[1])
    g.rect(3, 4, 26, 28, STONE[0])
    g.rect(6, 7, 20, 25, C(115, 74, 41))
    for x in (11, 16, 21): g.vline(x, 7, 25, C(90, 57, 33))
    for y in (12, 20, 28):
        for x in range(8, 26, 4): g.p(x, y, C(57, 57, 66))
    g.hline(8, 6, 16, C(115, 74, 41))
    return g.im


def rocca(gn=(34, 32)):
    W, H = 18, 13
    r = Room(W, H, gn, floor='tiles', wall='plaster', wall_rows=2)
    set_walls(r, stone_wall_top, stone_wall_low)
    set_floor(r, flagstone)
    ws = warps_of(gn)
    r.void([(x, H - 1) for x in range(W) if x != 9])
    r.exit_mat(9, H - 1, ws[0]['group'], ws[0]['num'], ws[0]['warp'])
    r.art[H - 1][9] = (flagstone(9, H - 1), None, 0, 0x65, False)
    for y in range(3, H - 1):
        r.art[y][9] = (red_runner(9, y), None, 0, 0, False)
    # back wall: the big door to the Parco della Rocca (cells 8-9, rows 0-1; the warp is on (9,1))
    d = big_door()
    for cx in range(2):
        for cy in range(2):
            piece = d.crop((cx * 16, cy * 16, cx * 16 + 16, cy * 16 + 16))
            r.art[cy][8 + cx] = (piece, None, 1, 0, False)
    a = r.art[1][9]; r.art[1][9] = (a[0], None, 0, 0x60, False)
    a = r.art[1][8]; r.art[1][8] = (a[0], None, 0, 0x60, False)
    r.bwarps.append(dict(x=9, y=1, elev=0, warp=ws[1]['warp'], num=ws[1]['num'], group=ws[1]['group']))
    r.bwarps.append(dict(x=8, y=1, elev=0, warp=ws[1]['warp'], num=ws[1]['num'], group=ws[1]['group']))
    for x in (4, 13):
        r.furn(x, 0, banner())
    for x in (2, 7, 11, 15):
        r.furn(x, 1, torch())
    for x in (1, 16):
        r.furn(x, 2, armour())
    for x in (6, 11):
        r.furn(x, 2, armour())
    r.furn(2, 5, long_table())
    r.furn(12, 5, weapon_rack())
    r.furn(14, 5, weapon_rack())
    r.furn(2, 9, cannon()); r.furn(14, 9, cannon())
    o = objs_of(gn)
    o[0]['x'], o[0]['y'] = 7, 4                     # the castellan, beside the carpet
    o[0]['script'] = 'R22_RoccaGuide'
    r.objs = o
    return r


ALL = [('rocca', rocca, (34, 32))]


# ------------------------------------------------------------------ Duomo di Cesena (34,37)
def church_wall_top(x):
    g = Px(16, 16)
    g.rect(0, 0, 16, 16, C(239, 222, 189))
    g.rect(0, 0, 16, 4, C(173, 148, 115)); g.hline(0, 4, 16, C(140, 115, 90))
    if x % 3 == 0: g.rect(6, 4, 4, 12, C(222, 206, 173)); g.vline(6, 4, 12, C(206, 189, 156))   # pilaster
    return g.im


def church_wall_low(x):
    g = Px(16, 16)
    g.rect(0, 0, 16, 16, C(239, 222, 189))
    if x % 3 == 0: g.rect(6, 0, 4, 13, C(222, 206, 173)); g.vline(6, 0, 13, C(206, 189, 156))
    g.rect(0, 12, 16, 4, C(156, 132, 107)); g.hline(0, 12, 16, C(198, 173, 140))
    return g.im


def nave_floor(x, y):
    """Veronese red and white marble in a diamond pattern."""
    g = Px(16, 16)
    g.rect(0, 0, 16, 16, C(239, 231, 214))
    for i in range(8):
        g.hline(8 - i, i, 2 * i, C(198, 107, 90)); g.hline(8 - i, 15 - i, 2 * i, C(198, 107, 90))
    g.rect(6, 6, 4, 4, C(239, 231, 214))
    return g.im


def stained_glass(seed=0):
    g = Px(16, 32)
    g.rect(3, 2, 10, 26, C(99, 82, 66))
    rnd = random.Random(seed)
    for y in range(4, 26, 3):
        for x in range(4, 12, 3):
            g.rect(x, y, 3, 3, rnd.choice([C(57, 99, 206), C(214, 57, 57), C(239, 206, 74), C(74, 165, 99), C(165, 99, 206)]))
    g.hline(4, 2, 8, C(99, 82, 66)); g.p(5, 3, C(99, 82, 66)); g.p(10, 3, C(99, 82, 66))
    g.outline()
    return g.im


def apse_mosaic():
    """Golden apse mosaic with the Madonna (4x2 on the back wall)."""
    g = Px(64, 32)
    for y in range(32):
        half = int(30 * math.sqrt(max(0, 1 - ((32 - y) / 32) ** 2)))
        g.hline(32 - half, y, 2 * half, C(222, 181, 66) if (y // 3) % 2 else C(239, 206, 99))
    g.rect(28, 8, 8, 20, C(57, 82, 165)); g.rect(30, 4, 4, 5, C(239, 206, 173)); g.rect(29, 3, 6, 2, C(255, 239, 156))
    g.rect(31, 14, 3, 4, C(214, 57, 57))
    for x in (14, 48): g.rect(x, 14, 4, 12, C(214, 57, 57)); g.rect(x, 11, 4, 3, C(239, 206, 173))
    return g.im


def altar():
    g = Px(48, 32)
    g.rect(2, 22, 44, 9, C(206, 189, 156)); g.hline(2, 22, 44, C(239, 222, 189))                      # steps
    g.rect(6, 8, 36, 14, C(247, 243, 235)); g.hline(6, 8, 36, C(255, 255, 255))
    g.rect(14, 12, 20, 7, C(222, 189, 74)); g.rect(22, 13, 4, 5, C(255, 255, 255))                    # golden frontal
    g.vline(24, 0, 9, C(222, 181, 66)); g.hline(21, 3, 7, C(222, 181, 66))                            # crucifix
    for x in (9, 38): g.rect(x, 3, 2, 6, C(255, 255, 239)); g.p(x, 2, C(255, 173, 57))                # candles
    g.outline()
    return dict(img=g.im, solid={(a, b) for a in range(3) for b in range(2)})


def altar_rail(w=2):
    g = Px(16 * w, 16)
    g.rect(0, 4, 16 * w, 3, C(222, 206, 173)); g.rect(0, 13, 16 * w, 3, C(206, 189, 156))
    for x in range(2, 16 * w, 4): g.rect(x, 7, 2, 6, C(239, 222, 189))
    g.outline()
    return dict(img=g.im, solid={(a, 0) for a in range(w)})


def pew(w=3):
    g = Px(16 * w, 16)
    g.rect(1, 1, 16 * w - 2, 5, C(115, 66, 41)); g.hline(1, 1, 16 * w - 2, C(156, 99, 57))
    g.rect(1, 6, 16 * w - 2, 5, C(140, 82, 49)); g.rect(1, 11, 16 * w - 2, 2, C(99, 57, 33))
    for x in (1, 16 * w - 4): g.rect(x, 1, 3, 14, C(99, 57, 33))
    g.outline()
    return dict(img=g.im, solid={(a, 0) for a in range(w)})


def column():
    g = Px(16, 32)
    g.rect(4, 2, 8, 26, C(239, 231, 214)); g.vline(5, 2, 26, C(255, 255, 247)); g.vline(10, 2, 26, C(206, 198, 181))
    g.rect(2, 0, 12, 3, C(222, 206, 173)); g.rect(2, 27, 12, 4, C(206, 189, 156))
    g.outline()
    return dict(img=g.im, solid={(0, 1)})


def votive_candles():
    g = Px(16, 16)
    g.rect(1, 9, 14, 6, C(140, 99, 66)); g.hline(1, 9, 14, C(181, 140, 99))
    for x in range(2, 14, 3):
        g.rect(x, 5, 2, 4, C(255, 255, 239)); g.p(x, 4, C(255, 173, 57))
    g.outline()
    return dict(img=g.im, solid={(0, 0)})


def confessional():
    g = Px(32, 32)
    g.rect(1, 2, 30, 29, C(99, 57, 33)); g.rect(1, 2, 30, 4, C(132, 82, 49))
    g.rect(4, 8, 8, 20, C(140, 33, 41)); g.rect(20, 8, 8, 20, C(140, 33, 41)); g.rect(14, 10, 4, 6, C(57, 41, 33))
    g.outline()
    return dict(img=g.im, solid={(0, 0), (1, 0), (0, 1), (1, 1)})


def font():
    g = Px(16, 16)
    g.rect(3, 4, 10, 6, C(222, 214, 198)); g.rect(4, 5, 8, 3, C(140, 189, 222)); g.rect(6, 10, 4, 4, C(206, 198, 181)); g.rect(4, 14, 8, 2, C(181, 173, 156))
    g.outline()
    return dict(img=g.im, solid={(0, 0)})


def organ():
    g = Px(32, 32)
    g.rect(1, 18, 30, 13, C(115, 66, 41)); g.hline(1, 18, 30, C(156, 99, 57))
    for i, x in enumerate(range(3, 29, 3)):
        h = 14 - abs(i - 4) * 2
        g.rect(x, 18 - h, 2, h, C(206, 206, 214)); g.vline(x, 18 - h, h, C(239, 239, 247))
    g.outline()
    return dict(img=g.im, solid={(0, 0), (1, 0), (0, 1), (1, 1)})


def painting_saint():
    g = Px(16, 16)
    g.rect(2, 1, 12, 14, C(206, 165, 66)); g.rect(3, 2, 10, 12, C(57, 49, 66))
    g.rect(6, 4, 4, 4, C(239, 206, 173)); g.rect(5, 8, 6, 6, C(165, 41, 49)); g.p(8, 3, C(255, 231, 115))
    g.outline()
    return g.im


def duomo(gn=(34, 37)):
    W, H = 18, 22
    r = Room(W, H, gn, floor='tiles', wall='plaster', wall_rows=2)
    set_walls(r, church_wall_top, church_wall_low)
    set_floor(r, nave_floor)
    ws = warps_of(gn)
    r.void([(x, H - 1) for x in range(W) if x != 9])
    r.exit_mat(9, H - 1, ws[0]['group'], ws[0]['num'], ws[0]['warp'])
    r.art[H - 1][9] = (nave_floor(9, H - 1), None, 0, 0x65, False)
    for y in range(7, H - 1):                                       # red carpet up the nave
        for x in (8, 9):
            r.art[y][x] = (red_runner(x, y), None, 0, 0, False)
    # apse and presbytery
    r.furn(7, 0, apse_mosaic())
    r.furn(7, 2, altar())
    r.furn(2, 0, stained_glass(1)); r.furn(5, 0, stained_glass(2)); r.furn(12, 0, stained_glass(3)); r.furn(15, 0, stained_glass(4))
    r.furn(4, 5, altar_rail(4)); r.furn(10, 5, altar_rail(4))
    r.furn(14, 2, organ())
    r.furn(2, 3, votive_candles()); r.furn(3, 3, votive_candles())
    # columns between nave and aisles, pews on both sides of the aisle
    for y in (7, 11, 15):
        r.furn(3, y, column()); r.furn(14, y, column())
    for y in range(8, 18, 2):
        r.furn(4, y, pew(4)); r.furn(10, y, pew(4))
    # side chapels: paintings and votive candles, confessional, baptismal font by the door
    r.furn(1, 9, votive_candles()); r.furn(16, 13, votive_candles())
    r.furn(15, 17, confessional())
    r.furn(2, 19, font())
    o = objs_of(gn)
    for oo, (x, y) in zip(o, [(10, 4), (7, 13), (11, 19)]):
        oo['x'], oo['y'] = x, y
    r.objs = o
    return r


ALL.append(('duomo', duomo, (34, 37)))


# ------------------------------------------------------------------ Teatro Bonci (34,25)
def curtain_top(x):
    g = Px(16, 16)
    g.rect(0, 0, 16, 16, C(173, 33, 41))
    for xx in range(0, 16, 4): g.vline(xx, 0, 16, C(132, 24, 33)); g.vline(xx + 1, 0, 16, C(206, 57, 66))
    g.rect(0, 0, 16, 4, C(222, 181, 66)); g.hline(0, 4, 16, C(165, 123, 41))
    for xx in range(0, 16, 4): g.p(xx + 2, 5, C(222, 181, 66))                                  # gold fringe
    return g.im


def curtain_low(x):
    g = Px(16, 16)
    g.rect(0, 0, 16, 16, C(173, 33, 41))
    for xx in range(0, 16, 4): g.vline(xx, 0, 16, C(132, 24, 33)); g.vline(xx + 1, 0, 16, C(206, 57, 66))
    g.rect(0, 13, 16, 3, C(99, 57, 33))
    return g.im


def stage_floor(x, y):
    g = Px(16, 16)
    g.rect(0, 0, 16, 16, C(181, 123, 74))
    for yy in (0, 4, 8, 12): g.hline(0, yy, 16, C(140, 90, 49))
    g.vline((x * 5 + y * 7) % 16, 0, 16, C(156, 107, 66))
    return g.im


def stalls_floor(x, y):
    g = Px(16, 16)
    g.rect(0, 0, 16, 16, C(115, 74, 49))
    for yy in (0, 8): g.hline(0, yy, 16, C(90, 57, 41))
    for xx in range(0, 16, 4): g.vline(xx, (xx // 4 % 2) * 8, 8, C(99, 66, 41))
    if x in (11, 12): g.rect(1, 0, 14, 16, C(173, 41, 49)); g.vline(1, 0, 16, C(222, 181, 82)); g.vline(14, 0, 16, C(222, 181, 82))
    return g.im


def footlights():
    g = Px(16, 16)
    g.rect(0, 0, 16, 10, C(181, 123, 74)); g.hline(0, 0, 16, C(140, 90, 49))
    g.rect(0, 10, 16, 6, C(222, 181, 66)); g.hline(0, 10, 16, C(255, 231, 140)); g.hline(0, 15, 16, C(165, 123, 41))
    for xx in (3, 11): g.rect(xx, 6, 3, 3, C(255, 247, 189)); g.p(xx + 1, 5, C(255, 255, 255))
    return g.im


def stage_steps():
    g = Px(16, 16)
    for i in range(4):
        g.rect(0, i * 4, 16, 4, C(181 - i * 12, 123 - i * 8, 74 - i * 5)); g.hline(0, i * 4 + 3, 16, C(120, 80, 45))
    return g.im


def velvet_seats(w=4):
    g = Px(16 * w, 16)
    for i in range(w * 2):
        x = i * 8
        g.rect(x + 1, 2, 6, 6, C(198, 41, 57)); g.hline(x + 1, 2, 6, C(239, 99, 107))
        g.rect(x + 1, 8, 6, 4, C(165, 33, 49)); g.rect(x + 1, 12, 6, 2, C(99, 57, 33))
    g.outline()
    return dict(img=g.im, solid={(a, 0) for a in range(w)})


def box_wall(x, y):
    """Side walls with the gilded tiers of boxes (palchi)."""
    g = Px(16, 16)
    g.rect(0, 0, 16, 16, C(115, 24, 33))
    g.rect(0, 2, 16, 3, C(222, 181, 66)); g.hline(0, 2, 16, C(255, 231, 140))
    g.rect(2, 5, 12, 8, C(57, 16, 24)); g.rect(5, 7, 4, 5, C(239, 206, 173) if (y % 3 == 0) else C(57, 16, 24))
    g.rect(0, 13, 16, 3, C(222, 181, 66))
    return g.im


def ticket_desk():
    g = Px(32, 32)
    g.rect(1, 12, 30, 18, C(99, 57, 33)); g.hline(1, 12, 30, C(222, 181, 66))
    g.rect(1, 2, 30, 10, C(214, 239, 247)); g.rect(10, 4, 12, 4, C(255, 255, 255))
    g.outline()
    return dict(img=g.im, solid={(0, 0), (1, 0), (0, 1), (1, 1)})


def poster_opera():
    g = Px(16, 16)
    g.rect(2, 1, 12, 14, C(33, 33, 49)); g.rect(3, 2, 10, 3, C(222, 181, 66)); g.rect(5, 6, 6, 7, C(198, 41, 57)); g.p(8, 6, C(239, 206, 173))
    g.outline()
    return g.im


def bonci(gn=(34, 25)):
    W, H = 24, 20
    r = Room(W, H, gn, floor='tiles', wall='plaster', wall_rows=2, keep_events=True)
    set_walls(r, curtain_top, curtain_low)
    for y in range(2, H - 1):
        for x in range(W):
            r.art[y][x] = ((stage_floor if y <= 6 else stalls_floor)(x, y), None, 0, 0, False)
    for y in range(2, H - 1):
        for x in (0, W - 1):
            r.art[y][x] = (box_wall(x, y), None, 1, 0, False)
    for y in range(7, 16):
        for x in (1, W - 2):
            r.art[y][x] = (box_wall(x, y), None, 1, 0, False)
    # stage edge with footlights, steps in the middle and at both sides
    for x in range(1, W - 1):
        r.art[7][x] = (footlights(), None, 1, 0, False)
    for x in (2, 11, 12, 21):
        r.art[7][x] = (stage_steps(), None, 0, 0, False)
    # stalls: velvet seats in two blocks with a central aisle (rows 9, 11, 13, 15)
    for y in (9, 11, 13, 15):
        r.furn(3, y, velvet_seats(4)); r.furn(7, y, velvet_seats(2))
        r.furn(14, y, velvet_seats(2)); r.furn(16, y, velvet_seats(4))
    # foyer
    r.furn(2, 16, ticket_desk())
    for x in (21,):
        r.furn(x, 16, big_plant_local())
    r.void([(x, H - 1) for x in range(W)])
    ws = r.bwarps; r.bwarps = []
    r.exit_mat(12, H - 1, ws[0]['group'], ws[0]['num'], ws[0]['warp'])
    r.art[H - 1][12] = (stalls_floor(12, H - 1), None, 0, 0x65, False)
    r.void_cell = (0, H - 1)
    pos = [(4, 4), (8, 4), (12, 4), (16, 4), (20, 4), (6, 14), (12, 14), (19, 17)]
    for o, (x, y) in zip(r.objs, pos):
        o['x'], o['y'] = x, y
    return r


def big_plant_local():
    from lido_int import big_plant
    return big_plant()


ALL.append(('bonci', bonci, (34, 25)))
