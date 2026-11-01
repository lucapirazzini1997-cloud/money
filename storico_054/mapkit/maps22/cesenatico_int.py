"""Cesenatico: the roof of the Grattacielo (34,38) as a real rooftop over the Adriatic: parapet with railings,
concrete slabs, helipad (the Skarmory platform), HVAC units, water tank, solar panels, antennas, the stairwell,
and a coin telescope pointed inland at the Rocca Malatestiana of Cesena."""
import sys, random, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import interior as I
from interior import Room
from art import Px, C, PAL
from lido_int import objs_of, warps_of, bgs_of, big_plant
from cervia_int import bench_row

SEA = C(57, 132, 206)


def slab(x, y):
    g = Px(16, 16)
    g.rect(0, 0, 16, 16, C(206, 206, 198))
    g.hline(0, 0, 16, C(173, 173, 165)); g.vline(0, 0, 16, C(173, 173, 165))
    rnd = random.Random(x * 7 + y * 13)
    for _ in range(4): g.p(rnd.randrange(1, 16), rnd.randrange(1, 16), C(189, 189, 181))
    return g.im


def parapet(side):
    """Low white parapet with a steel railing; sea seen beyond (side: n, s, w, e, nw, ne, sw, se)."""
    g = Px(16, 16)
    g.rect(0, 0, 16, 16, SEA)
    for i in range(0, 16, 5): g.hline(i % 7, i + 2, 4, C(99, 165, 222))
    w = C(247, 247, 243); sh = C(198, 198, 189); rail = C(140, 148, 156)
    if 'n' in side: g.rect(0, 9, 16, 7, w); g.hline(0, 15, 16, sh); g.hline(0, 5, 16, rail); [g.vline(x, 5, 4, rail) for x in range(1, 16, 4)]
    if 's' in side: g.rect(0, 0, 16, 7, w); g.hline(0, 6, 16, sh); g.hline(0, 10, 16, rail); [g.vline(x, 7, 4, rail) for x in range(1, 16, 4)]
    if 'w' in side: g.rect(9, 0, 7, 16, w); g.vline(15, 0, 16, sh); g.vline(5, 0, 16, rail); [g.hline(5, y, 4, rail) for y in range(1, 16, 4)]
    if 'e' in side: g.rect(0, 0, 7, 16, w); g.vline(0, 0, 16, sh); g.vline(10, 0, 16, rail); [g.hline(7, y, 4, rail) for y in range(1, 16, 4)]
    return g.im


def helipad(x, y, x0, y0):
    """5x5 helipad: yellow circle and H on dark green paint (one tile per call)."""
    g = Px(16, 16)
    g.rect(0, 0, 16, 16, C(66, 99, 82))
    for py in range(16):
        for px in range(16):
            X = (x - x0) * 16 + px - 40; Y = (y - y0) * 16 + py - 40
            r = math.hypot(X + .5, Y + .5)
            if 30 <= r <= 33: g.p(px, py, C(247, 206, 57))
            if (-12 <= X <= -7 or 6 <= X <= 11) and -14 <= Y <= 14: g.p(px, py, C(255, 255, 255))
            if -7 <= X <= 6 and -2 <= Y <= 2: g.p(px, py, C(255, 255, 255))
    return g.im


def hvac():
    g = Px(32, 32)
    g.rect(1, 6, 30, 22, C(189, 198, 206)); g.hline(1, 6, 30, C(231, 239, 247)); g.rect(1, 28, 30, 3, C(140, 148, 156))
    for cx in (9, 23):
        g.rect(cx - 6, 9, 12, 12, C(99, 107, 115))
        for a in range(0, 360, 45):
            g.p(cx + round(4 * math.cos(math.radians(a))), 15 + round(4 * math.sin(math.radians(a))), C(173, 181, 189))
        g.p(cx, 15, C(57, 66, 74))
    for x in range(4, 28, 3): g.vline(x, 22, 4, C(156, 165, 173))
    g.outline()
    return dict(img=g.im, solid={(0, 0), (1, 0), (0, 1), (1, 1)})


def water_tank():
    g = Px(32, 48)
    g.rect(4, 4, 24, 30, C(214, 214, 222)); g.rect(4, 4, 24, 4, C(239, 239, 247)); g.vline(6, 8, 26, C(239, 239, 247))
    for y in (14, 24): g.hline(4, y, 24, C(173, 173, 181))
    for x in (6, 24): g.rect(x, 34, 3, 13, C(132, 140, 148))
    g.hline(5, 40, 22, C(132, 140, 148))
    g.vline(26, 6, 30, C(99, 107, 115))                                                         # ladder
    for y in range(8, 34, 4): g.hline(25, y, 3, C(99, 107, 115))
    g.outline()
    return dict(img=g.im, solid={(0, 1), (1, 1), (0, 2), (1, 2)}, top=1)


def solar(w=3):
    g = Px(16 * w, 16)
    g.rect(1, 2, 16 * w - 2, 11, C(41, 57, 107)); g.hline(1, 2, 16 * w - 2, C(140, 156, 206))
    for x in range(1, 16 * w, 6): g.vline(x, 2, 11, C(173, 181, 206))
    g.hline(1, 7, 16 * w - 2, C(173, 181, 206)); g.rect(1, 13, 16 * w - 2, 2, C(132, 140, 148))
    g.outline()
    return dict(img=g.im, solid={(a, 0) for a in range(w)})


def antenna():
    g = Px(16, 32)
    g.vline(8, 2, 28, C(132, 140, 148)); g.rect(5, 28, 7, 3, C(99, 107, 115))
    for y, wdt in ((5, 6), (10, 8), (15, 10)): g.hline(8 - wdt // 2, y, wdt, C(156, 165, 173))
    g.p(8, 1, C(239, 57, 57))
    g.outline()
    return dict(img=g.im, solid={(0, 1)})


def telescope():
    """Coin-operated panoramic telescope, turned towards the hills inland (west)."""
    g = Px(16, 32)
    g.rect(6, 14, 4, 14, C(57, 99, 156)); g.rect(4, 27, 8, 4, C(41, 66, 115))
    g.rect(1, 6, 12, 7, C(57, 132, 206)); g.rect(0, 7, 2, 5, C(33, 41, 57)); g.hline(1, 6, 12, C(140, 189, 239))
    g.rect(12, 7, 3, 5, C(41, 66, 115)); g.p(9, 15, C(239, 206, 57))
    g.outline()
    return dict(img=g.im, solid={(0, 1)})


def stairwell_exit(x, y):
    g = Px(16, 16)
    g.rect(0, 0, 16, 16, C(140, 140, 132))
    for i in range(4): g.rect(1, i * 4, 14, 3, C(206 - i * 25, 206 - i * 25, 198 - i * 25))
    return g.im


def plaque():
    g = Px(16, 16)
    g.rect(2, 3, 12, 9, C(198, 165, 82)); g.rect(3, 4, 10, 7, C(222, 189, 99))
    for yy in (6, 8): g.hline(4, yy, 8, C(140, 107, 41))
    g.rect(7, 12, 2, 4, C(132, 140, 148))
    g.outline()
    return dict(img=g.im, solid={(0, 0)})


def roof(gn=(34, 38)):
    W, H = 24, 20
    r = Room(W, H, gn, floor='tiles', wall='plaster', wall_rows=1)
    for y in range(H):
        for x in range(W):
            r.art[y][x] = (slab(x, y), None, 0, 0, False)
    for x in range(W):
        r.art[0][x] = (parapet('n'), None, 1, 0, False)
        r.art[H - 1][x] = (parapet('s'), None, 1, 0, False)
    for y in range(H):
        r.art[y][0] = (parapet('w' + ('n' if y == 0 else 's' if y == H - 1 else '')), None, 1, 0, False)
        r.art[y][W - 1] = (parapet('e' + ('n' if y == 0 else 's' if y == H - 1 else '')), None, 1, 0, False)
    # stairwell down (the original warp position), arrival on the roof just above it
    ws = warps_of(gn)
    r.bwarps = []
    r.art[H - 1][12] = (stairwell_exit(12, H - 1), None, 0, 0x65, False)
    r.bwarps.append(dict(x=12, y=H - 1, elev=0, warp=ws[0]['warp'], num=ws[0]['num'], group=ws[0]['group']))
    # helipad in the middle (the Skarmory platform)
    for y in range(5, 10):
        for x in range(10, 15):
            r.art[y][x] = (helipad(x, y, 10, 5), None, 0, 0, False)
    # equipment
    r.furn(2, 2, hvac()); r.furn(20, 2, hvac())
    r.furn(19, 12, water_tank(), top_rows=1)
    r.furn(3, 13, solar(3)); r.furn(3, 15, solar(3)); r.furn(16, 8, solar(3)) if False else r.furn(17, 7, solar(3))
    r.furn(7, 2, antenna()); r.furn(16, 2, antenna())
    r.furn(1, 8, telescope())
    r.furn(14, 17, bench_row(2)); r.furn(8, 17, bench_row(2))
    for (x, y) in ((1, 4), (22, 15)):
        r.furn(x, y, big_plant())
    r.furn(11, 17, plaque())
    o = objs_of(gn)
    o[0]['x'], o[0]['y'] = 12, 7          # the shining feather on the helipad (Skarmory)
    o[1]['x'], o[1]['y'] = 6, 11          # the technician
    r.objs = o
    b = bgs_of(gn)
    b[0]['x'], b[0]['y'] = 11, 17         # plaque "Tetto del grattacielo"
    b.append(dict(x=1, y=9, elev=0, kind=0, arg='R22_Cannocchiale'))
    r.bbgs = b
    r.void_cell = None
    r.border = [0x170] * 4
    return r


ALL = [('roof', roof, (34, 38))]
