"""Lido di Savio interiors, drawn by hand: Caffè Panama (34,1), the protagonist's villa ground floor (1,0),
Aldo's house ground floor (34,40) and upstairs (34,41). Events (NPCs, scripts, warp order) are kept from the ROM."""
import sys, random
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import interior as I
from interior import Room, floor_tile
from art import Px, C, PAL
import art22
import r22

OUT = C(41, 33, 33)


# ------------------------------------------------------------------ tiles
def tile_fill(fn):
    g = Px(16, 16); fn(g); return g.im


def diamond_floor(x, y):
    """Bar Panama floor: beige stone tiles with small dark diamond inserts."""
    g = Px(16, 16)
    g.rect(0, 0, 16, 16, C(231, 214, 181)); g.hline(0, 0, 16, C(206, 189, 156)); g.vline(0, 0, 16, C(206, 189, 156))
    for i in range(3):
        g.hline(8 - i, 6 + i, 1 + 2 * i, C(57, 49, 49)); g.hline(8 - i, 10 - i, 1 + 2 * i, C(57, 49, 49))
    g.p(3, 3, C(239, 222, 198)); g.p(12, 12, C(214, 198, 165))
    return g.im


def white_floor(x, y):
    """Villa: large light-grey porcelain slabs."""
    g = Px(16, 16)
    g.rect(0, 0, 16, 16, C(239, 239, 235))
    if x % 2 == 0: g.vline(0, 0, 16, C(206, 206, 201))
    if y % 2 == 0: g.hline(0, 0, 16, C(206, 206, 201))
    g.p(5 + (x * 3) % 7, 4 + (y * 5) % 8, C(247, 247, 247))
    return g.im


def oak_floor(x, y):
    return floor_tile('planks', x, y)


def set_floor(r, fn):
    for y in range(r.wall_rows, r.h):
        for x in range(r.w):
            a = r.art[y][x]
            if a is not None and a[2] == 0 and a[3] == 0:
                r.art[y][x] = (fn(x, y), None, 0, 0, False)
    r.floor_fn = fn


def set_walls(r, top, low):
    for x in range(r.w):
        r.art[0][x] = (top(x), None, 1, 0, False)
        r.art[1][x] = (low(x), None, 1, 0, False)


def panama_wall_top(x):
    """Orange-red ceiling with the wavy turquoise band and black soffit with spotlights."""
    g = Px(16, 16)
    g.rect(0, 0, 16, 16, C(214, 82, 57))
    wave = [0, 1, 2, 2, 1, 0, -1, -1]
    for i in range(16):
        off = wave[(x * 16 + i) // 4 % 8]
        g.vline(i, 6 + off, 4, C(57, 173, 181)); g.p(i, 6 + off, C(115, 206, 206))
    g.rect(0, 12, 16, 4, C(33, 33, 41))
    if x % 2 == 0: g.rect(7, 13, 2, 2, C(255, 247, 206))
    return g.im


def panama_wall_low(x):
    """Mosaic of small yellow-green glass tiles with blue specks, turquoise skirting."""
    g = Px(16, 16)
    rnd = random.Random(x)
    for yy in range(0, 13, 2):
        for xx in range(0, 16, 2):
            c = rnd.choice([C(222, 231, 140), C(206, 222, 123), C(231, 239, 165), C(206, 222, 123), C(57, 82, 165)])
            g.rect(xx, yy, 2, 2, c)
    g.rect(0, 13, 16, 3, C(57, 156, 165)); g.hline(0, 13, 16, C(115, 206, 206))
    return g.im


def villa_wall_top(x):
    g = Px(16, 16); g.rect(0, 0, 16, 16, C(247, 247, 243)); g.rect(0, 0, 16, 3, C(214, 214, 206)); g.hline(0, 3, 16, C(189, 189, 181))
    if x % 3 == 1: g.rect(6, 6, 4, 2, C(255, 255, 230))                      # recessed light
    return g.im


def villa_wall_low(x):
    g = Px(16, 16); g.rect(0, 0, 16, 16, C(243, 243, 239)); g.rect(0, 13, 16, 3, C(140, 140, 132)); g.hline(0, 13, 16, C(189, 189, 181))
    return g.im


def home_wall_top(x):
    g = Px(16, 16); g.rect(0, 0, 16, 16, C(247, 231, 198)); g.rect(0, 0, 16, 4, C(156, 107, 66)); g.hline(0, 4, 16, C(115, 74, 49))
    for xx in range(2, 16, 5): g.vline(xx, 6, 8, C(239, 214, 181))   # striped wallpaper
    return g.im


def home_wall_low(x):
    g = Px(16, 16); g.rect(0, 0, 16, 16, C(247, 231, 198))
    for xx in range(2, 16, 5): g.vline(xx, 0, 6, C(239, 214, 181))
    g.rect(0, 6, 16, 10, C(181, 132, 90)); g.hline(0, 6, 16, C(214, 165, 115)); g.hline(0, 15, 16, C(115, 74, 49))
    for xx in (3, 11): g.vline(xx, 8, 6, C(156, 107, 66))
    return g.im


def kid_wall_top(x):
    g = Px(16, 16); g.rect(0, 0, 16, 16, C(198, 222, 247)); g.rect(0, 0, 16, 4, C(239, 239, 239)); g.hline(0, 4, 16, C(173, 173, 173))
    if x % 4 == 2: g.rect(5, 8, 6, 4, C(255, 255, 255))                          # little cloud
    return g.im


def kid_wall_low(x):
    g = Px(16, 16); g.rect(0, 0, 16, 16, C(198, 222, 247)); g.rect(0, 9, 16, 7, C(99, 140, 206)); g.hline(0, 9, 16, C(255, 255, 255)); g.hline(0, 15, 16, C(57, 90, 156))
    return g.im


# ------------------------------------------------------------------ furniture
def asset(w, h, solid=None):
    g = Px(16 * w, 16 * h)
    return g, (lambda: dict(img=(g.outline(), g.im)[1], solid=solid if solid is not None else {(a, b) for a in range(w) for b in range(h)}))


def panama_counter(w=7):
    """Curved bar counter: turquoise leather front with an embossed sun, light oak base, marble top."""
    g = Px(16 * w, 32)
    W = 16 * w
    for x in range(W):
        bend = int(4 * (1 - ((x - W / 2) / (W / 2)) ** 2))          # bulges toward the room
        g.vline(x, 4 + bend, 4, C(222, 206, 173))                     # marble top
        g.p(x, 4 + bend, C(247, 239, 222))
        g.vline(x, 8 + bend, 12, C(57, 156, 165))                     # turquoise front
        g.p(x, 8 + bend, C(41, 115, 123))
        g.vline(x, 20 + bend, 7, C(214, 165, 99))                     # oak base
        g.p(x, 26 + bend, C(156, 107, 66))
    cx = W // 3
    for (dx, dy) in ((0, 0), (2, 0), (-2, 0), (0, 2), (0, -2), (1, 1), (-1, -1), (1, -1), (-1, 1)):
        g.p(cx + dx, 15 + dy, C(99, 189, 189))
    # espresso machine, cups and the big Mokador cup on the counter
    g.rect(W // 2 - 6, 0, 12, 6, C(189, 189, 198)); g.hline(W // 2 - 6, 0, 12, C(239, 239, 247)); g.p(W // 2 - 3, 3, C(57, 57, 66))
    g.rect(14, 1, 7, 5, C(255, 255, 255)); g.rect(15, 2, 5, 2, C(99, 57, 41))
    g.rect(W - 26, 3, 4, 3, C(255, 255, 255)); g.rect(W - 18, 3, 4, 3, C(255, 255, 255))
    g.outline()
    return dict(img=g.im, solid={(a, b) for a in range(w) for b in range(2)})


def red_stool():
    g = Px(16, 16)
    g.rect(3, 3, 10, 5, C(214, 41, 49)); g.hline(3, 3, 10, C(247, 99, 99))
    g.rect(4, 8, 2, 7, C(66, 49, 49)); g.rect(10, 8, 2, 7, C(66, 49, 49)); g.hline(4, 12, 8, C(99, 74, 66))
    g.outline()
    return dict(img=g.im, solid={(0, 0)})


def bottle_ring(w=5):
    """Round hanging shelf with bottles, orange rim (on the back wall)."""
    g = Px(16 * w, 32)
    W = 16 * w
    g.rect(2, 2, W - 4, 3, C(222, 99, 49)); g.hline(2, 2, W - 4, C(247, 156, 99))
    g.rect(2, 22, W - 4, 3, C(222, 99, 49)); g.hline(2, 24, W - 4, C(165, 66, 33))
    for x in range(6, W - 6, 10):
        g.vline(x, 5, 17, C(206, 206, 214))
    rnd = random.Random(5)
    for x in range(4, W - 4, 3):
        c = rnd.choice([C(140, 41, 66), C(57, 115, 74), C(214, 189, 99), C(239, 239, 239), C(99, 66, 41)])
        h = rnd.choice([8, 10, 12])
        g.rect(x, 21 - h, 2, h, c); g.p(x, 20 - h, C(41, 41, 41))
    g.outline()
    return dict(img=g.im, solid={(a, b) for a in range(w) for b in range(2)})


def mosaic_cabinet():
    """Back-wall niche with red-orange frame, glass shelves on the yellow-green mosaic."""
    g = Px(32, 32)
    g.rect(0, 0, 32, 32, C(214, 82, 57)); g.rect(2, 2, 28, 28, C(57, 156, 165))
    rnd = random.Random(3)
    for yy in range(4, 28, 2):
        for xx in range(4, 28, 2):
            g.rect(xx, yy, 2, 2, rnd.choice([C(222, 231, 140), C(206, 222, 123), C(57, 82, 165)]))
    for yy in (10, 18, 26):
        g.hline(4, yy, 24, C(239, 247, 255))
        for xx in range(6, 26, 5):
            g.rect(xx, yy - 4, 3, 4, rnd.choice([C(214, 41, 49), C(239, 239, 239), C(57, 140, 74)]))
    g.outline()
    return dict(img=g.im, solid={(0, 0), (1, 0), (0, 1), (1, 1)})


def pastry_case(w=2):
    g = Px(16 * w, 32)
    W = 16 * w
    g.rect(1, 6, W - 2, 14, C(206, 239, 247)); g.hline(1, 6, W - 2, C(255, 255, 255))
    rnd = random.Random(w)
    for x in range(3, W - 4, 5):
        for yy in (10, 15):
            g.rect(x, yy, 4, 3, rnd.choice([C(239, 189, 99), C(214, 140, 66), C(247, 222, 173), C(165, 99, 57)]))
    g.rect(1, 20, W - 2, 10, C(214, 165, 99)); g.hline(1, 20, W - 2, C(156, 107, 66))
    g.outline()
    return dict(img=g.im, solid={(a, b) for a in range(w) for b in range(2)})


def gelato_case(w=2):
    g = Px(16 * w, 32)
    W = 16 * w
    g.rect(1, 4, W - 2, 16, C(206, 239, 247)); g.hline(1, 4, W - 2, C(255, 255, 255))
    cols = [C(255, 239, 214), C(99, 57, 41), C(247, 156, 173), C(156, 214, 115), C(255, 222, 99), C(214, 66, 66)]
    for i, x in enumerate(range(3, W - 5, 6)):
        g.rect(x, 9, 5, 7, cols[i % len(cols)]); g.hline(x, 9, 5, C(255, 255, 255))
    g.rect(1, 20, W - 2, 10, C(57, 156, 165)); g.hline(1, 20, W - 2, C(115, 206, 206))
    g.outline()
    return dict(img=g.im, solid={(a, b) for a in range(w) for b in range(2)})


def white_table_orange(w=2):
    """Table with an orange cloth and white plastic chairs above/below (2x2)."""
    g = Px(32, 32)
    g.rect(9, 1, 14, 6, C(255, 255, 255)); g.hline(9, 6, 14, C(214, 214, 206))         # chair behind
    g.rect(4, 8, 24, 14, C(239, 132, 49)); g.hline(4, 21, 24, C(198, 99, 33)); g.hline(4, 8, 24, C(255, 173, 99))
    g.rect(13, 12, 6, 4, C(255, 255, 255)); g.rect(14, 13, 4, 2, C(99, 57, 41))         # cappuccino
    g.rect(9, 24, 14, 7, C(255, 255, 255)); g.hline(9, 30, 14, C(214, 214, 206))        # chair in front
    g.outline()
    return dict(img=g.im, solid={(0, 0), (1, 0), (0, 1), (1, 1)})


def big_plant():
    g = Px(16, 32)
    g.rect(3, 22, 10, 9, C(247, 247, 243)); g.hline(3, 22, 10, C(255, 255, 255)); g.hline(3, 30, 10, C(198, 198, 189))
    rnd = random.Random(8)
    for _ in range(70):
        x = 8 + rnd.randint(-7, 7); y = 4 + rnd.randint(0, 18)
        g.p(x, y, rnd.choice([C(41, 115, 57), C(74, 156, 66), C(115, 189, 82)]))
    g.outline()
    return dict(img=g.im, solid={(0, 1)})


def kitchen(w=4, modern=False):
    """Kitchen run on the back wall: cabinets, sink, hob, (fridge at the right end)."""
    g = Px(16 * w, 32)
    W = 16 * w
    body = C(247, 247, 243) if modern else C(214, 165, 107)
    edge = C(189, 189, 181) if modern else C(156, 107, 66)
    top = C(99, 99, 107) if modern else C(239, 231, 214)
    g.rect(0, 8, W - 16, 22, body); g.rect(0, 6, W - 16, 4, top)
    for x in range(2, W - 18, 12):
        g.rect(x, 13, 10, 15, edge); g.rect(x + 1, 14, 8, 13, body); g.p(x + 5, 17, C(66, 66, 66))
    g.rect(6, 6, 12, 3, C(173, 189, 206)); g.vline(10, 2, 5, C(173, 173, 181))                  # sink + tap
    g.rect(24, 6, 14, 3, C(41, 41, 41)); g.p(28, 7, C(214, 66, 49)); g.p(34, 7, C(214, 66, 49))  # hob
    g.rect(W - 15, 0, 14, 30, C(239, 239, 239) if not modern else C(189, 189, 198))             # fridge
    g.hline(W - 15, 12, 14, C(173, 173, 173)); g.vline(W - 4, 4, 6, C(140, 140, 140)); g.vline(W - 4, 15, 8, C(140, 140, 140))
    g.outline()
    return dict(img=g.im, solid={(a, b) for a in range(w) for b in range(2)})


def tv(modern=False):
    g = Px(32, 32)
    g.rect(2, 18, 28, 12, C(156, 107, 66) if not modern else C(66, 66, 74))
    g.hline(2, 18, 28, C(198, 148, 99) if not modern else C(115, 115, 123))
    if modern:
        g.rect(1, 2, 30, 16, C(24, 24, 33)); g.rect(3, 4, 26, 12, C(57, 115, 173)); g.rect(5, 10, 10, 5, C(90, 173, 90))
    else:
        g.rect(5, 4, 22, 14, C(66, 66, 74)); g.rect(7, 6, 15, 10, C(99, 156, 206)); g.p(24, 8, C(214, 66, 49))
    g.rect(8, 22, 6, 5, C(41, 41, 41))                                                   # console
    g.outline()
    return dict(img=g.im, solid={(0, 0), (1, 0), (0, 1), (1, 1)})


def modern_sofa():
    g = Px(48, 32)
    g.rect(1, 4, 46, 10, C(140, 148, 156)); g.rect(1, 14, 46, 12, C(165, 173, 181))
    for x in (16, 32): g.vline(x, 14, 12, C(140, 148, 156))
    g.rect(6, 8, 8, 6, C(57, 156, 165)); g.rect(34, 8, 8, 6, C(239, 189, 74))           # cushions
    g.rect(1, 26, 46, 4, C(99, 99, 107))
    g.outline()
    return dict(img=g.im, solid={(a, b) for a in range(3) for b in range(2)})


def glass_table():
    g = Px(48, 32)
    for x in (4, 20, 36):
        g.rect(x + 2, 0, 8, 6, C(255, 255, 255)); g.rect(x + 2, 26, 8, 6, C(255, 255, 255))   # white chairs
    g.rect(2, 7, 44, 18, C(206, 231, 239)); g.hline(2, 7, 44, C(255, 255, 255)); g.hline(2, 24, 44, C(156, 189, 206))
    g.rect(20, 12, 8, 6, C(239, 239, 239)); g.rect(22, 10, 4, 4, C(57, 140, 74))          # vase
    g.outline()
    return dict(img=g.im, solid={(a, b) for a in range(3) for b in range(2)})


def big_window(w=2):
    """Floor-to-ceiling glazing on the back wall (villa): shows the pine trees outside."""
    g = Px(16 * w, 32)
    g.rect(0, 2, 16 * w, 28, C(140, 140, 132))
    g.rect(2, 4, 16 * w - 4, 24, C(173, 214, 239))
    for x in range(4, 16 * w - 4, 7):
        g.rect(x, 14, 5, 12, C(57, 123, 74)); g.rect(x + 1, 11, 3, 4, C(74, 148, 82))
    for x in range(16, 16 * w, 16): g.vline(x, 4, 24, C(140, 140, 132))
    return g.im


def stairs_up(wood=True):
    """Stair flight on the back wall going up (16x32: wall row + floor row with the warp)."""
    g = Px(16, 32)
    c = [C(214, 165, 107), C(189, 140, 90), C(132, 90, 57)] if wood else [C(239, 239, 235), C(214, 214, 206), C(156, 156, 148)]
    g.rect(0, 0, 16, 32, c[2])
    for i in range(7):
        y = 2 + i * 4
        g.rect(1, y, 14, 4, c[i % 2]); g.hline(1, y + 3, 14, c[2])
    g.vline(0, 0, 32, C(99, 66, 41)); g.vline(15, 0, 32, C(99, 66, 41))
    return g.im


def stairs_down():
    g = Px(16, 16)
    g.rect(0, 0, 16, 16, C(66, 49, 41))
    for i in range(4):
        g.rect(1, 1 + i * 4, 14, 3, C(214 - i * 30, 165 - i * 25, 107 - i * 15))
    return g.im


def put_stairs(r, x, y, img, dest, beh=0x61):
    """Stairs: art covering (x, y-1) and the warp cell (x, y)."""
    h = img.height // 16
    for j in range(h):
        cy = y - (h - 1) + j
        piece = img.crop((0, j * 16, 16, j * 16 + 16))
        if cy == y:
            r.art[cy][x] = (piece, None, 0, beh, False)
        else:
            r.art[cy][x] = (piece, None, 1, 0, False)
    g, n, w = dest
    r.bwarps.append(dict(x=x, y=y, elev=0, warp=w, num=n, group=g))


def frame(c1, c2, w=1):
    g = Px(16 * w, 16)
    g.rect(1, 2, 16 * w - 2, 11, C(99, 66, 41)); g.rect(2, 3, 16 * w - 4, 9, c1); g.rect(2, 8, 16 * w - 4, 4, c2)
    g.outline()
    return g.im


def poster_bici():
    """Poster of a racing cyclist (Romagna, Pantani country)."""
    g = Px(16, 16)
    g.rect(2, 1, 12, 14, C(255, 222, 66)); g.rect(3, 2, 10, 12, C(255, 239, 156))
    for cx in (5, 11):
        g.rect(cx - 2, 9, 4, 4, C(41, 41, 41)); g.p(cx - 1, 10, C(255, 239, 156)); g.p(cx, 11, C(255, 239, 156))
    g.hline(5, 8, 6, C(214, 41, 49)); g.rect(7, 4, 3, 4, C(214, 41, 49)); g.p(8, 3, C(239, 189, 156))
    g.outline()
    return g.im


def clock():
    g = Px(16, 16)
    g.rect(4, 3, 9, 9, C(255, 255, 255)); g.hline(5, 2, 7, C(66, 66, 74)); g.hline(5, 12, 7, C(66, 66, 74))
    g.vline(3, 4, 7, C(66, 66, 74)); g.vline(13, 4, 7, C(66, 66, 74)); g.vline(8, 5, 3, C(41, 41, 41)); g.hline(8, 7, 3, C(41, 41, 41))
    return g.im


# ------------------------------------------------------------------ rooms
def objs_of(gn):
    return [dict(o) for o in r22.ROM.map(*gn)['objects']]


def warps_of(gn):
    return [dict(w) for w in r22.ROM.map(*gn)['warps']]


def bgs_of(gn):
    return [dict(b) for b in r22.ROM.map(*gn)['bgs']]


def bar_panama(gn=(34, 1)):
    W, H = 16, 12
    r = Room(W, H, gn, floor='tiles', wall='plaster', wall_rows=2)
    set_walls(r, panama_wall_top, panama_wall_low)
    set_floor(r, diamond_floor)
    r.floor_kind = 'tiles'
    ws = warps_of(gn)
    r.void([(x, H - 1) for x in range(W) if x != 8])
    r.exit_mat(8, H - 1, ws[0]['group'], ws[0]['num'], ws[0]['warp'])
    r.art[H - 1][8] = (diamond_floor(8, H - 1), None, 0, 0x65, False)
    # back wall: bottle ring over the counter, the two mosaic niches, glass cabinet
    r.furn(4, 0, bottle_ring(5))
    r.furn(11, 0, mosaic_cabinet())
    r.furn(13, 0, mosaic_cabinet())
    r.furn(1, 0, mosaic_cabinet())
    # the curved counter, with the barman behind it, red stools in front
    r.furn(3, 3, panama_counter(7), top_rows=1)
    for x in range(3, 10):                      # talk to the barman across the counter
        a = r.art[4][x]; r.art[4][x] = (a[0], a[1], 1, 0x80, a[4])
    for x in (3, 5, 7, 9):
        r.furn(x, 5, red_stool())
    r.furn(11, 2, pastry_case(2))
    r.furn(13, 2, gelato_case(2))
    r.furn(1, 2, big_plant())
    # tables with orange cloths (the terrace look of the photo, inside)
    for (x, y) in ((1, 7), (4, 8), (11, 6), (13, 8)):
        r.furn(x, y, white_table_orange())
    r.furn(14, 4, big_plant())
    r.furn(1, 10, big_plant()) if False else None
    o = objs_of(gn)
    pos = [(6, 3), (11, 5), (8, 6), (13, 7), (15, 10)]        # barman behind the counter, customers, item
    for oo, (x, y) in zip(o, pos):
        oo['x'], oo['y'] = x, y
    o[0]['move'] = 10 if False else o[0]['move']
    r.objs = o
    return r


def villa(gn=(1, 0)):
    """Ground floor of the protagonist's modern villa: open space, kitchen, glass table, sofa, glazing."""
    W, H = 14, 10
    r = Room(W, H, gn, floor='tiles', wall='plaster', wall_rows=2)
    set_walls(r, villa_wall_top, villa_wall_low)
    set_floor(r, white_floor)
    ws = warps_of(gn)
    r.void([(x, H - 1) for x in range(W) if x not in (9, 10)])
    # warp order kept: 0 and 1 = front door mats, 2 = stairs (2F arrives on warp 2)
    for i, x in enumerate((10, 9)):
        r.exit_mat(x, H - 1, ws[i]['group'], ws[i]['num'], ws[i]['warp'])
        r.art[H - 1][x] = (white_floor(x, H - 1), None, 0, 0x65, False)
    r.furn(1, 0, kitchen(5, modern=True))
    r.furn(6, 0, big_window(3))
    r.furn(10, 0, frame(C(57, 156, 189), C(239, 206, 99)))
    put_stairs(r, 12, 2, stairs_up(wood=False), (1, 1, 0))
    r.furn(2, 4, glass_table())
    r.furn(8, 5, I.rug(4, 2, C(189, 189, 181), C(222, 222, 214)))
    r.furn(8, 4, modern_sofa())
    r.furn(8, 7, tv(modern=True))
    r.furn(10, 2, I.shelf('books', 2))
    r.furn(12, 6, big_plant())
    r.furn(1, 7, big_plant())
    o = objs_of(gn)
    o[0]['x'], o[0]['y'] = 4, 3           # mamma in the kitchen
    r.objs = o
    return r


def aldo_1f(gn=(34, 40)):
    W, H = 14, 11
    r = Room(W, H, gn, floor='planks', wall='plaster', wall_rows=2)
    set_walls(r, home_wall_top, home_wall_low)
    ws = warps_of(gn)
    r.void([(x, H - 1) for x in range(W) if x != 7])
    r.exit_mat(7, H - 1, ws[0]['group'], ws[0]['num'], ws[0]['warp'])
    r.furn(1, 0, kitchen(4))
    r.furn(5, 0, I.window_art('plaster', C(57, 140, 74)))
    r.furn(7, 0, clock())
    r.furn(8, 0, I.window_art('plaster', C(57, 140, 74)))
    put_stairs(r, 12, 2, stairs_up(), (ws[1]['group'], ws[1]['num'], ws[1]['warp']))
    r.furn(10, 0, I.shelf('books', 1)) if False else None
    r.furn(9, 2, I.shelf('books', 2))
    t = I.table(C(255, 255, 255), C(57, 99, 173), 2)
    r.furn(2, 5, t)
    r.furn(1, 5, I.chair()); r.furn(4, 5, I.chair())
    r.furn(8, 7, I.rug(4, 2, C(165, 57, 66), C(239, 206, 132)))
    r.furn(8, 5, I.sofa(C(165, 57, 57)))
    r.furn(12, 7, tv())
    r.furn(1, 8, I.plant())
    r.furn(12, 4, I.plant())
    o = objs_of(gn)
    o[0]['x'], o[0]['y'] = 3, 3           # Aldo's mother at the cooker
    r.objs = o
    return r


def aldo_2f(gn=(34, 41)):
    W, H = 12, 10
    r = Room(W, H, gn, floor='blue', wall='blue', wall_rows=2)
    set_walls(r, kid_wall_top, kid_wall_low)
    set_floor(r, oak_floor)
    r.void([(x, H - 1) for x in range(W)])
    ws = warps_of(gn)
    put_stairs(r, 10, 2, stairs_down().resize((16, 16)) if False else stairs_up(), (ws[0]['group'], ws[0]['num'], ws[0]['warp']))
    r.furn(1, 2, I.bed(C(57, 99, 173)))
    r.furn(1, 0, poster_bici())
    r.furn(4, 0, I.window_art('blue', C(57, 99, 165)))
    r.furn(7, 0, frame(C(99, 189, 239), C(239, 222, 156)))
    r.furn(5, 2, I.desk())
    r.furn(8, 2, I.shelf('books', 2))
    r.furn(1, 6, I.rug(3, 2, C(57, 99, 165), C(239, 206, 132)))
    r.furn(8, 6, tv())
    r.furn(10, 7, I.plant())
    r.furn(1, 7, I.wardrobe()) if False else None
    o = objs_of(gn)
    o[0]['x'], o[0]['y'] = 5, 6
    r.objs = o
    b = bgs_of(gn)
    if b:
        b[0]['x'], b[0]['y'] = 5, 3        # the desk / PC sign
    r.bbgs = b
    r.void_cell = (0, H - 1)
    return r


ALL = [('bar', bar_panama, (34, 1)), ('villa', villa, (1, 0)), ('aldo1', aldo_1f, (34, 40)), ('aldo2', aldo_2f, (34, 41))]


def villa_2f(gn=(1, 1)):
    """The protagonist's bedroom upstairs in the villa (replaces Emerald's rival bedroom and its intro scripts)."""
    W, H = 12, 9
    r = Room(W, H, gn, floor='planks', wall='plaster', wall_rows=2)
    r.objs, r.bwarps, r.bcoords, r.bbgs = [], [], [], []
    set_walls(r, villa_wall_top, villa_wall_low)
    set_floor(r, oak_floor)
    r.void([(x, H - 1) for x in range(W)])
    put_stairs(r, 10, 2, stairs_up(wood=False), (1, 0, 2))
    r.furn(1, 2, I.bed(C(57, 156, 165)))
    r.furn(1, 0, poster_bici())
    r.furn(4, 0, big_window(2))
    r.furn(7, 0, frame(C(57, 156, 189), C(239, 206, 99)))
    r.furn(4, 2, I.desk())                         # desk with the PC
    r.furn(7, 2, I.shelf('books', 2))
    r.furn(5, 5, I.rug(3, 2, C(57, 156, 165), C(239, 239, 235)))
    r.furn(8, 5, tv(modern=True))
    r.furn(1, 5, big_plant())
    r.add_sign(4, 3, 'R22_HomePC')
    r.add_sign(5, 3, 'R22_HomePC')
    r.void_cell = (0, H - 1)
    return r


ALL.append(('villa2', villa_2f, (1, 1)))
