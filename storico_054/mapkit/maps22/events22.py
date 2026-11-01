"""New maps for the post-League legendaries:
- Mare di Ravenna: the sea east of the Darsena with the offshore platform and the rocket (to the Moon);
- Luna: craters, the landed rocket, the Earth in the black sky, Deoxys;
- Mondo dei Desideri: clouds and star paths in the night sky, Jirachi on the Wishing Star, the portal back."""
import sys, random, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import art, art22, decor, r22
from art import Px, C, PAL
from canvas import G
from decor import rect


def place_over(cv, x, y, asset, bgfn, top_rows=0, protect=False):
    """Place art composited cell by cell over a custom background (no grass showing through)."""
    img = asset['img']; solid = asset.get('solid', set())
    for cy in range(img.height // 16):
        for cx in range(img.width // 16):
            X, Y = x + cx, y + cy
            piece = img.crop((cx * 16, cy * 16, cx * 16 + 16, cy * 16 + 16))
            base = bgfn(X, Y).copy(); base.alpha_composite(piece.convert('RGBA'))
            cv.art[Y][X] = (base, None, 1 if (cx, cy) in solid else 0, 0x100 if (cx, cy) not in solid else 0, protect)


def _blank(cv, gn):
    cv.gn = gn
    cv.objs, cv.bwarps, cv.bcoords, cv.bbgs, cv.conns = [], [], [], [], []


# ------------------------------------------------------------------ Mare di Ravenna
def mare_ravenna(gn, ravenna_rows=(10, 14)):
    W, H = 40, 30
    cv = r22.RCanvas(W, H, (34, 44))
    _blank(cv, gn)
    cv.fill(0, 0, W, H, 'sea')
    r0, r1 = ravenna_rows
    rock = decor.asset('rock', art.boulder) if hasattr(art, 'boulder') else None
    for y in range(H):
        if r0 <= y <= r1:
            continue
        g = Px(16, 16)
        g.rect(0, 0, 16, 16, C(132, 123, 107)); g.rect(2, 2, 12, 12, C(165, 156, 140)); g.rect(4, 3, 6, 4, C(198, 189, 173))
        g.outline()
        cv.place_art(0, y, dict(img=g.im, solid={(0, 0)}, door=None))
    plat = art22.gas_platform(8, 6, rocket=True)
    cv.place_art(24, 10, plat, protect=True)
    # buoys marking the channel
    for (x, y) in ((6, 9), (6, 15), (14, 9), (14, 15)):
        g = Px(16, 16); g.rect(5, 4, 6, 8, C(214, 57, 49)); g.rect(5, 8, 6, 2, C(255, 255, 255)); g.vline(8, 1, 3, C(66, 66, 74)); g.outline()
        cv.place_art(x, y, dict(img=g.im, solid={(0, 0)}, door=None))
    cv.add_sign(29, 15, 'R22_Rocket')
    cv.add_sign(25, 15, 'R22_SignPlatform')
    cv.border = [0x170] * 4
    return cv


# ------------------------------------------------------------------ Luna
def _space(x, y):
    g = Px(16, 16)
    g.rect(0, 0, 16, 16, C(8, 8, 24))
    rnd = random.Random((x * 7 + y * 3) % 5)
    for _ in range(3):
        g.p(rnd.randrange(16), rnd.randrange(16), rnd.choice([C(255, 255, 255), C(200, 200, 255), C(255, 240, 180)]))
    return g.im


def _regolith(x, y):
    g = Px(16, 16)
    g.rect(0, 0, 16, 16, C(181, 181, 189))
    rnd = random.Random((x * 3 + y * 5) % 4)
    for _ in range(8):
        g.p(rnd.randrange(16), rnd.randrange(16), rnd.choice([C(156, 156, 165), C(206, 206, 214)]))
    return g.im


def crater(r=2):
    s = 16 * r
    g = Px(s, s)
    for y in range(s):
        for x in range(s):
            d = math.hypot(x + .5 - s / 2, (y + .5 - s / 2) * 1.4)
            if d < s / 2 - 1:
                g.p(x, y, C(132, 132, 140) if d > s / 2 - 4 else (C(148, 148, 156) if y < s / 2 else C(165, 165, 173)))
            elif d < s / 2:
                g.p(x, y, C(214, 214, 222))
    return g.im


def landed_rocket():
    g = Px(32, 64)
    g.rect(10, 8, 12, 46, C(247, 247, 247)); g.vline(10, 8, 46, C(255, 255, 255)); g.vline(21, 8, 46, C(206, 206, 214))
    for i in range(8): g.hline(16 - i, 1 + i, 2 * i if i else 1, C(214, 41, 49))
    g.rect(13, 20, 6, 6, C(57, 99, 189)); g.rect(14, 21, 4, 4, C(140, 189, 239))
    for (x0, d) in ((10, -1), (21, 1)):
        for i in range(10): g.hline(x0 + d * i if d < 0 else x0, 44 + i, i + 1 if d > 0 else 1, C(214, 41, 49))
    g.rect(4, 54, 3, 8, C(140, 140, 148)); g.rect(25, 54, 3, 8, C(140, 140, 148)); g.hline(2, 62, 28, C(99, 99, 107))
    g.rect(12, 54, 8, 4, C(99, 99, 107))
    g.outline()
    return dict(img=g.im, solid={(0, 2), (1, 2), (0, 3), (1, 3)}, door=None)


def earth():
    g = Px(48, 48)
    for y in range(48):
        for x in range(48):
            d = math.hypot(x + .5 - 24, y + .5 - 24)
            if d < 20:
                land = (math.sin(x / 5.0) + math.cos(y / 4.0 + x / 9.0)) > 0.6
                c = C(74, 156, 82) if land else C(57, 115, 206)
                if (x + y) % 11 == 0 and not land: c = C(239, 239, 247)
                if x + .5 - 24 > 10 and d > 14: c = tuple(max(0, v - 60) for v in c)
                g.p(x, y, c)
    return g.im


def luna(gn):
    W, H = 30, 22
    cv = r22.RCanvas(W, H, (34, 44))
    _blank(cv, gn)
    ground = rect(3, 6, 24, 14)
    for y in range(H):
        for x in range(W):
            if (x, y) in ground:
                cv.place_art(x, y, dict(img=_regolith(x, y), solid=set(), door=None), walkable=True)
            else:
                cv.place_art(x, y, dict(img=_space(x, y), solid={(0, 0)}, door=None))
    def bg(X, Y):
        return _regolith(X, Y) if (X, Y) in ground else _space(X, Y)
    place_over(cv, 21, 0, dict(img=earth(), solid=rect(0, 0, 3, 3)), bg, protect=True)
    for (x, y, r) in ((12, 8, 2), (18, 14, 2), (5, 16, 1), (23, 9, 1), (14, 16, 1)):
        place_over(cv, x, y, dict(img=crater(r), solid=set()), bg)
    place_over(cv, 5, 6, landed_rocket(), bg, protect=True)
    cv.add_sign(5, 9, 'R22_RocketBack')
    cv.add_sign(6, 9, 'R22_RocketBack')
    cv.add_obj(20, 10, 233, 'R22_Deoxys', flag=0x4EB, move=8)
    cv.border = [0x1D4] * 4
    cv.void_cell = (0, 0)
    return cv


# ------------------------------------------------------------------ Mondo dei Desideri
def _night(x, y):
    g = Px(16, 16)
    g.rect(0, 0, 16, 16, C(24, 24, 74))
    rnd = random.Random((x * 5 + y * 7) % 6)
    for _ in range(2):
        g.p(rnd.randrange(16), rnd.randrange(16), rnd.choice([C(255, 255, 255), C(255, 240, 160), C(200, 220, 255)]))
    return g.im


def _cloud(x, y, cells):
    g = Px(16, 16)
    g.rect(0, 0, 16, 16, C(247, 243, 255))
    for (dx, dy, side) in ((0, -1, 'n'), (0, 1, 's'), (-1, 0, 'w'), (1, 0, 'e')):
        if (x + dx, y + dy) not in cells:
            if side == 'n':
                for i in range(16): g.vline(i, 0, 2 + (i % 5 == 2), C(24, 24, 74))
            if side == 's': g.rect(0, 12, 16, 4, C(214, 206, 239)); g.hline(0, 15, 16, C(173, 165, 214))
            if side == 'w':
                for i in range(16): g.hline(0, i, 2 + (i % 5 == 2), C(24, 24, 74))
            if side == 'e':
                for i in range(16): g.hline(14 - (i % 5 == 2), i, 2 + (i % 5 == 2), C(24, 24, 74))
    g.p(5, 6, C(255, 255, 255)); g.p(11, 9, C(232, 228, 250))
    return g.im


def _starpath(x, y):
    g = Px(16, 16)
    g.rect(0, 0, 16, 16, C(24, 24, 74))
    g.rect(3, 3, 10, 10, C(248, 216, 48)); g.rect(5, 5, 6, 6, C(255, 240, 160))
    for (a, b) in ((8, 1), (8, 14), (1, 8), (14, 8)): g.p(a, b, C(248, 216, 48))
    return g.im


def wish_pedestal():
    g = Px(48, 32)
    g.rect(4, 14, 40, 16, C(206, 214, 247)); g.hline(4, 14, 40, C(255, 255, 255)); g.rect(4, 28, 40, 3, C(140, 148, 206))
    for i in range(6): g.hline(24 - 2 * i, 2 + i, 4 * i + 1, C(248, 216, 48))
    for i in range(6): g.hline(24 - 10 + i, 7 + i, 20 - 2 * i, C(248, 216, 48))
    g.outline()
    return dict(img=g.im, solid={(0, 1), (1, 1), (2, 1)}, door=None)


def mondo(gn):
    W, H = 28, 22
    cv = r22.RCanvas(W, H, (34, 44))
    _blank(cv, gn)
    clouds = rect(10, 15, 9, 5) | rect(3, 9, 6, 4) | rect(19, 9, 6, 4) | rect(10, 3, 9, 6)
    stars = {(14, y) for y in range(9, 15)} | {(x, 11) for x in range(9, 19)}
    walk = clouds | stars
    for y in range(H):
        for x in range(W):
            if (x, y) in clouds:
                cv.place_art(x, y, dict(img=_cloud(x, y, clouds), solid=set(), door=None), walkable=True)
            elif (x, y) in stars:
                cv.place_art(x, y, dict(img=_starpath(x, y), solid=set(), door=None), walkable=True)
            else:
                cv.place_art(x, y, dict(img=_night(x, y), solid={(0, 0)}, door=None))
    place_over(cv, 13, 4, wish_pedestal(), lambda X, Y: _cloud(X, Y, clouds), protect=True)
    cv.add_obj(14, 4, 180, 'R22_Jirachi', flag=0x4EA, move=8)
    cv.add_obj(14, 18, 183, 'R22_WishReturn', move=8)
    cv.border = [0x1D4] * 4
    cv.void_cell = (0, 0)
    return cv


# ------------------------------------------------------------------ Grotta di Mewtwo (off Cesenatico)
def _cave_floor(x, y):
    g = Px(16, 16)
    g.rect(0, 0, 16, 16, C(66, 57, 74))
    rnd = random.Random((x * 5 + y * 3) % 4)
    for _ in range(6): g.p(rnd.randrange(16), rnd.randrange(16), rnd.choice([C(82, 74, 90), C(57, 49, 66)]))
    return g.im


def _cave_wall(x, y, cells):
    g = Px(16, 16)
    g.rect(0, 0, 16, 16, C(41, 33, 49))
    rnd = random.Random((x * 3 + y * 7) % 5)
    for _ in range(5):
        a, b = rnd.randrange(14), rnd.randrange(14)
        g.rect(a, b, 3, 2, C(66, 57, 82))
    if (x, y + 1) in cells:                       # rock face above a floor cell
        g.rect(0, 10, 16, 6, C(90, 82, 107)); g.hline(0, 10, 16, C(115, 107, 132))
    return g.im


def _pool(x, y):
    g = Px(16, 16)
    g.rect(0, 0, 16, 16, C(41, 66, 140))
    if (x + y) % 3 == 0: g.hline(3, 6, 5, C(99, 140, 222))
    return g.im


def crystal():
    g = Px(16, 32)
    for (x0, h, c) in ((3, 18, C(173, 107, 239)), (8, 26, C(206, 156, 255)), (12, 14, C(140, 82, 206))):
        for y in range(h):
            w = max(1, 3 - y * 3 // h)
            g.hline(x0 - w // 2, 31 - y, w + 1, c)
        g.p(x0, 31 - h + 2, C(255, 255, 255))
    g.outline()
    return dict(img=g.im, solid={(0, 1)}, door=None)


def grotta(gn):
    W, H = 26, 22
    cv = r22.RCanvas(W, H, (34, 44))
    _blank(cv, gn)
    floor = rect(11, 17, 4, 4) | rect(8, 12, 10, 6) | rect(4, 6, 6, 8) | rect(16, 6, 6, 8) | rect(8, 3, 10, 4)
    pools = rect(10, 8, 6, 3)
    for y in range(H):
        for x in range(W):
            if (x, y) in pools:
                cv.place_art(x, y, dict(img=_pool(x, y), solid={(0, 0)}, door=None))
            elif (x, y) in floor:
                cv.place_art(x, y, dict(img=_cave_floor(x, y), solid=set(), door=None), walkable=True)
            else:
                cv.place_art(x, y, dict(img=_cave_wall(x, y, floor), solid={(0, 0)}, door=None))
    for (x, y) in ((5, 6), (20, 6), (9, 15), (16, 15), (8, 3), (17, 3)):
        place_over(cv, x, y, crystal(), _cave_floor)
    # exit at the bottom (back to the sea off Cesenatico)
    g = Px(16, 16); g.rect(0, 0, 16, 16, C(66, 57, 74)); g.rect(3, 6, 10, 10, C(140, 189, 222)); g.rect(5, 8, 6, 8, C(206, 231, 247))
    cv.art[H - 1][12] = (g.im, None, 0, 0x65, False)
    cv.art[H - 1][13] = (g.im, None, 0, 0x65, False)
    cv.add_obj(13, 4, 182, 'R22_Mewtwo', flag=0x4EF, move=8)
    cv.border = [0x1D4] * 4
    cv.void_cell = (0, 0)
    return cv
