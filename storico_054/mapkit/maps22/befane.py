"""Le Befane Shopping Centre (34,54) 40x30 — Rimini south. The mall as a long low building with light cladding,
orange bands, glass barrel vaults on the roof and the tall glazed atrium of the main entrance; in front the
pedestrian plaza (planters, benches, the totem sign) and the big car park; the avenue from Rimini arrives on
the west side."""
import sys, random
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import art, art22, decor, r22, imports
from art import Px, C, PAL, text, text_width
from canvas import G
from decor import rect

GN = (34, 54)
TS = 'r22_befane'
W, H = 40, 30
STARTS = [(2, 0), (3, 0)]


def mall(cw=24):
    """The mall facade (cw x 9 cells), entrance at the bottom of the central atrium."""
    Wp, Hp = cw * 16, 144
    g = Px(Wp, Hp)
    cream = [C(247, 239, 222), C(231, 222, 198), C(206, 196, 173)]
    orange = C(239, 123, 49)
    # roof slab with three glass barrel vaults
    g.rect(0, 20, Wp, 8, C(189, 189, 181)); g.hline(0, 20, Wp, C(222, 222, 214))
    for vx in (40, Wp // 2 - 60, Wp - 120):
        for x in range(80):
            h = int(14 * (1 - ((x - 40) / 40) ** 2))
            g.vline(vx + x, 26 - h, h, C(173, 214, 239) if x % 8 else C(132, 165, 189))
    # body: cream cladding panels, orange band, ground floor shop windows
    g.rect(0, 28, Wp, Hp - 28, cream[0])
    for x in range(0, Wp, 24): g.vline(x, 28, 60, cream[2])
    for y in (48, 68): g.hline(0, y, Wp, cream[1])
    g.rect(0, 86, Wp, 6, orange); g.hline(0, 86, Wp, C(255, 173, 99))
    rnd = random.Random(4)
    for x in range(6, Wp - 6, 26):
        if Wp // 2 - 44 < x < Wp // 2 + 30: continue
        g.rect(x, 96, 20, 36, C(57, 66, 82)); g.rect(x + 1, 97, 18, 34, C(140, 189, 214))
        g.rect(x + 1, 92, 18, 4, rnd.choice([C(214, 57, 57), C(57, 99, 189), C(57, 156, 99), C(239, 189, 57), C(165, 57, 156)]))
        g.p(x + 4, 100, C(214, 239, 255)); g.p(x + 5, 101, C(214, 239, 255))
    g.rect(0, Hp - 6, Wp, 6, C(173, 165, 148))
    # big lettering on the two wings: LE BEFANE (left, red, bold) and SHOPPING CENTRE (right)
    wing = (Wp // 2 - 44) // 2
    s1 = 'LE BEFANE'; x1 = wing - text_width(s1) // 2
    g.rect(x1 - 6, 54, text_width(s1) + 12, 14, C(255, 255, 255))
    for dx in range(2):
        text(g, x1 + dx, 57, s1, C(214, 41, 49))
    s2 = 'SHOPPING CENTRE'; x2 = Wp - wing - text_width(s2) // 2
    g.rect(x2 - 6, 54, text_width(s2) + 12, 14, C(255, 255, 255))
    text(g, x2, 57, s2, C(57, 57, 66))
    # central glazed atrium rising above the roof, curved canopy over the entrance
    ax = Wp // 2 - 40
    g.rect(ax, 2, 80, Hp - 8, C(99, 132, 165))
    for x in range(ax + 2, ax + 78, 8): g.vline(x, 4, Hp - 12, C(173, 214, 239)); g.vline(x + 1, 4, Hp - 12, C(206, 231, 247))
    for y in range(10, Hp - 8, 16): g.hline(ax, y, 80, C(66, 99, 132))
    g.rect(ax - 2, 0, 84, 4, C(222, 222, 214))
    for x in range(-8, 88):
        h = int(6 * (1 - ((x - 40) / 48) ** 2))
        g.vline(ax + x, 104 - h, 3 + h, C(239, 239, 235)) if 0 <= ax + x < Wp else None
    g.hline(ax - 8, 107, 96, C(173, 173, 165))
    # entrance doors (sliding glass)
    dx = Wp // 2 - 16
    g.rect(dx, 112, 32, 26, C(41, 57, 82)); g.rect(dx + 2, 114, 13, 24, C(173, 222, 247)); g.rect(dx + 17, 114, 13, 24, C(173, 222, 247))
    g.outline()
    ch = Hp // 16
    solid = {(x, y) for x in range(cw) for y in range(ch)}
    door = (cw // 2, ch - 1)
    solid.discard(door)
    return dict(img=g.im, solid=solid, door=door)


def asphalt(x, y):
    g = Px(16, 16)
    g.rect(0, 0, 16, 16, C(115, 115, 123))
    rnd = random.Random((x * 3 + y) % 4)
    for _ in range(6): g.p(rnd.randrange(16), rnd.randrange(16), C(132, 132, 140))
    return g.im


def stall_line(x, y, row_top):
    g = Px(16, 16)
    g.rect(0, 0, 16, 16, C(115, 115, 123))
    g.vline(0, 0, 16, C(239, 239, 231))
    if row_top: g.hline(0, 0, 16, C(239, 239, 231))
    else: g.hline(0, 15, 16, C(239, 239, 231))
    return g.im


def car(color):
    """Parked car seen from above (1x2 cells), pointing up."""
    g = Px(16, 32)
    dark = tuple(max(0, v - 50) for v in color)
    g.rect(2, 3, 12, 27, color); g.hline(3, 2, 10, color); g.hline(3, 30, 10, color)
    g.rect(3, 7, 10, 5, C(57, 82, 115)); g.rect(3, 22, 10, 4, C(57, 82, 115))       # windscreens
    g.rect(3, 12, 10, 10, dark)                                                     # roof
    g.p(3, 3, C(255, 247, 189)); g.p(12, 3, C(255, 247, 189)); g.p(3, 29, C(214, 41, 41)); g.p(12, 29, C(214, 41, 41))
    g.outline()
    return dict(img=g.im, solid={(0, 0), (0, 1)}, door=None)


def totem():
    """Tall totem sign of the mall (1x3)."""
    g = Px(16, 48)
    g.rect(3, 2, 10, 42, C(239, 239, 235)); g.vline(3, 2, 42, C(255, 255, 255)); g.vline(12, 2, 42, C(198, 198, 189))
    g.rect(3, 4, 10, 10, C(214, 41, 49))
    g.rect(5, 6, 6, 1, C(255, 255, 255)); g.rect(5, 9, 6, 1, C(255, 255, 255)); g.rect(5, 12, 4, 1, C(255, 255, 255))
    for y in range(18, 40, 5): g.rect(5, y, 6, 3, random.Random(y).choice([C(57, 99, 189), C(239, 189, 57), C(57, 156, 99), C(165, 57, 156)]))
    g.rect(5, 44, 6, 4, C(140, 140, 132))
    g.outline()
    return dict(img=g.im, solid={(0, 2)}, door=None)


def bus_stop():
    g = Px(32, 32)
    g.rect(1, 6, 30, 3, C(57, 99, 156)); g.rect(2, 9, 2, 20, C(140, 148, 156)); g.rect(28, 9, 2, 20, C(140, 148, 156))
    g.rect(4, 10, 24, 14, C(206, 231, 239)); g.rect(6, 18, 20, 4, C(140, 99, 66))
    g.rect(22, 0, 8, 6, C(239, 206, 57)); g.p(25, 2, C(41, 41, 41))
    g.outline()
    return dict(img=g.im, solid={(0, 1), (1, 1)}, door=None)


def planter_tree():
    g = Px(16, 32)
    g.rect(1, 22, 14, 9, C(189, 181, 165)); g.hline(1, 22, 14, C(222, 214, 198))
    rnd = random.Random(11)
    for _ in range(90):
        x = 8 + rnd.randint(-7, 7); y = 10 + rnd.randint(-8, 10)
        g.p(x, y, rnd.choice(PAL['leaf'][:4]))
    g.vline(8, 16, 7, PAL['bark'][1])
    g.outline()
    return dict(img=g.im, solid={(0, 1)}, door=None)


def build():
    cv = r22.RCanvas(W, H, GN)
    fam, cob = imports.cobbles(imports.warm_stone)
    # avenue from Rimini (west side), the car park (south), the plaza in front of the mall
    road = rect(1, 0, 4, 28) | rect(1, 26, 38, 3)
    park = rect(5, 17, 33, 9)
    plaza = rect(5, 13, 33, 4) | rect(18, 12, 4, 1)
    cv.paint_family(fam, cob, plaza)
    for (x, y) in road | park:
        cv.place_art(x, y, dict(img=asphalt(x, y), solid=set(), door=None))
    # stall lines: two double rows of parking stalls
    for x in range(7, 37):
        if x in (19, 20, 21): continue
        for y, top in ((18, True), (19, False), (22, True), (23, False)):
            cv.place_art(x, y, dict(img=stall_line(x, y, top), solid=set(), door=None))
    colors = [C(214, 41, 49), C(57, 99, 189), C(239, 239, 235), C(41, 41, 49), C(239, 189, 57), C(140, 140, 148), C(57, 140, 99)]
    rnd = random.Random(3)
    for x in range(7, 37):
        if x in (19, 20, 21): continue
        for y in (18, 22):
            if rnd.random() < 0.55:
                cv.place_art(x, y, car(rnd.choice(colors)))
    # the mall
    doors = {}
    doors['mall'] = cv.place_art(8, 3, mall(24), protect=True)
    # plaza furniture
    for x in (7, 12, 27, 32):
        cv.place_art(x, 14, planter_tree(), top_rows=1)
    for x in (9, 14, 25, 30):
        cv.place_art(x, 15, dict(img=decor.asset('bench', art.bench), solid={(0, 0)}, door=None))
    cv.place_art(23, 13, totem(), top_rows=2)
    cv.place_art(6, 24, bus_stop(), top_rows=1)
    for (x, y) in ((6, 20), (20, 20), (37, 20)):
        cv.place_art(x, y, dict(img=decor.asset('lamp', art.lamp), solid={(0, 1)}, door=None), top_rows=1)
    # greenery around
    border = rect(0, 0, 1, H) | rect(5, 0, 35, 3) | rect(39, 0, 1, H) | rect(0, 29, 40, 1) | rect(5, 3, 3, 10) | rect(32, 3, 7, 10)
    decor.woods(cv, border, seed=31, pine_ratio=0.3, gaps=0.0)
    # events (same order): warps 0/2 from Rimini at the top of the avenue, 1 = mall entrance
    cv.set_warp(0, 2, 0); cv.set_warp(2, 3, 0)
    cv.set_warp(1, *doors['mall'])
    cv.place_objs({1: (18, 14), 2: (28, 21)})
    cv.add_sign(5, 13, 'R22_SignBefane')
    for bb in cv.bbgs:
        cv.put(bb['x'], bb['y'], G['sign'], 1, 3)
    cv.border = [0x1D4, 0x1D5, 0x1DC, 0x1DD]
    cv.doors = doors
    return cv
