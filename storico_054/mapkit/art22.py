"""Extra procedural art for Romagna 0.22: gates, Ponte di Tiberio, harbour buildings, Casa delle Aie, Pensione."""
import random
from art import Px, PAL, C, OUT, coppi_roof, wall_fill, window, door, signboard, text, text_width

PAL.setdefault('blue', [C(206, 231, 247), C(165, 206, 231), C(123, 173, 206), C(82, 132, 173)])
PAL.setdefault('white', [C(255, 255, 255), C(239, 239, 231), C(214, 214, 206), C(165, 165, 156)])
PAL.setdefault('yellow', [C(255, 247, 173), C(247, 231, 123), C(222, 198, 82), C(173, 148, 57)])
PAL.setdefault('terracotta', [C(239, 173, 132), C(222, 140, 99), C(189, 107, 74), C(140, 74, 57)])
PAL.setdefault('istria', [C(247, 243, 231), C(226, 221, 206), C(196, 190, 173), C(156, 150, 135), C(115, 110, 99)])

WATER = [C(115, 181, 222), C(82, 148, 206), C(57, 115, 173), C(41, 82, 140)]


def city_gate(cw=4, name='CERVIA', brick='brick'):
    """Welcome arch over a road: two pillars and a signboard. Top row is drawn over the player."""
    W, H = cw * 16, 48
    g = Px(W, H)
    b = PAL[brick]
    for px in (0, W - 12):
        g.rect(px + 1, 8, 10, 40, b[1])
        for y in range(10, 48, 6):
            g.hline(px + 1, y, 10, b[2])
            off = 0 if (y // 6) % 2 else 5
            g.vline(px + 1 + off, y - 5, 5, b[2])
        g.vline(px + 10, 8, 40, b[3])
        g.rect(px, 6, 12, 3, PAL['stone'][1]); g.hline(px, 6, 12, PAL['stone'][0])
        g.rect(px, 44, 12, 4, PAL['stone'][2])
    g.rect(4, 2, W - 8, 13, PAL['wood'][1])
    g.hline(4, 2, W - 8, PAL['wood'][0]); g.hline(4, 14, W - 8, PAL['wood'][3])
    signboard(g, W // 2, 4, name, bg=C(255, 247, 222))
    g.outline()
    solid = {(0, 1), (0, 2), (cw - 1, 1), (cw - 1, 2)}
    return dict(img=g.im, solid=solid, door=None, top_rows=1)


def road_sign(text_lines=('CESENA',), arrow='>'):
    """Small brown tourist sign on a post (1x2 cells)."""
    g = Px(16, 32)
    g.rect(7, 14, 2, 18, PAL['wood'][2])
    g.rect(1, 2, 14, 13, C(140, 90, 57)); g.rect(2, 3, 12, 11, C(173, 115, 74))
    for i in range(3):
        g.hline(4, 5 + i * 3, 8, C(255, 247, 222))
    g.outline()
    return dict(img=g.im, solid={(0, 1)}, door=None)


def ponte_tiberio():
    """Ponte di Tiberio seen from the south: 5 arches in Istrian stone, piers with tabernacles.
    Deck (2 walkable rows) on top, arch face below. 10 cells x 4 cells (160 x 64)."""
    W, H = 160, 64
    g = Px(W, H)
    st = PAL['istria']
    rnd = random.Random(7)
    # deck: north parapet, roman paving, south parapet
    g.rect(0, 0, W, 5, st[1]); g.hline(0, 0, W, st[0]); g.hline(0, 4, W, st[3])
    for x in range(0, W, 12):
        g.vline(x, 1, 3, st[2])
    g.rect(0, 5, W, 22, C(156, 150, 140))
    for y in range(5, 27, 6):
        off = rnd.randrange(8)
        for x in range(-off, W, 10 + (y % 3)):
            w = 7 + rnd.randrange(4)
            g.rect(max(0, x + 1), y + 1, w, 4, C(178, 172, 160) if (x + y) % 3 else C(166, 160, 148))
    g.rect(0, 27, W, 5, st[1]); g.hline(0, 27, W, st[0]); g.hline(0, 31, W, st[3])
    # face of the bridge
    g.rect(0, 32, W, 32, st[2])
    for y in range(34, 64, 5):
        off = 0 if (y // 5) % 2 else 6
        g.hline(0, y, W, st[3])
        for x in range(off, W, 12):
            g.vline(x, y - 4, 4, st[3])
    g.rect(0, 32, W, 3, st[1]); g.hline(0, 32, W, st[0])        # string course
    spans = [(6, 26), (38, 26), (68, 26), (98, 26), (128, 26)]
    for (ax, aw) in spans:
        cx = ax + aw / 2
        for y in range(40, 64):
            t = (y - 40) / 13.0
            half = int(aw / 2 * min(1.0, (min(t, 1.0) * (2 - min(t, 1.0))) ** 0.5)) if y < 53 else aw // 2
            if half <= 0:
                continue
            for x in range(int(cx - half), int(cx + half)):
                d = (y - 40) / 24.0
                col = WATER[1] if d > 0.6 else (WATER[2] if d > 0.3 else WATER[3])
                g.p(x, y, col)
            g.p(int(cx - half) - 1, y, st[4]); g.p(int(cx + half), y, st[4])
        # voussoirs (radial stones)
        for k in range(9):
            import math
            a = math.pi * (k + 0.5) / 9
            for r in (aw / 2 + 1, aw / 2 + 2):
                x = cx - math.cos(a) * r; y = 53 - math.sin(a) * r * 1.0
                g.p(int(x), int(y), st[0])
        # water highlights
        for y in (58, 61):
            g.hline(int(cx - 6), y, 5, WATER[0])
    # tabernacles (aedicules) on the piers
    for px in (33, 63, 93, 123):
        g.rect(px, 38, 6, 12, st[1])
        g.rect(px + 1, 41, 4, 8, st[3])
        g.p(px + 2, 37, st[0]); g.p(px + 3, 37, st[0]); g.hline(px - 1, 38, 8, st[0])
    g.outline(open_sides='EW')
    deck = {(x, y) for x in range(10) for y in (0, 1)}
    solid = {(x, y) for x in range(10) for y in (2, 3)}
    return dict(img=g.im, solid=solid, door=None, deck=deck)


def capitaneria(cw=7):
    """Port authority: white building, blue band, flag pole, anchor emblem."""
    W, H = cw * 16, 80
    g = Px(W, H)
    wl = PAL['white']
    # flat roof with parapet
    g.rect(2, 12, W - 4, 6, PAL['stone'][2]); g.hline(2, 12, W - 4, PAL['stone'][1])
    wall_fill(g, 3, 18, W - 6, 62, wl, 3)
    g.rect(3, 34, W - 6, 4, C(57, 99, 173)); g.hline(3, 34, W - 6, C(99, 140, 206))
    for f, fy in enumerate((20, 42, 58)):
        for i in range(cw - 1):
            sx = 10 + i * ((W - 20) // (cw - 1))
            if f == 2 and abs(sx + 6 - W // 2) < 14:
                continue
            g.rect(sx, fy, 10, 10, PAL['glass'][1]); g.rect(sx + 1, fy + 1, 8, 3, PAL['glass'][0])
            g.hline(sx, fy, 10, OUT); g.hline(sx, fy + 9, 10, OUT); g.vline(sx, fy, 10, OUT); g.vline(sx + 9, fy, 10, OUT)
    # flag pole and Italian flag
    g.vline(W // 2, 0, 13, C(140, 140, 140))
    g.rect(W // 2 + 1, 1, 4, 6, C(57, 165, 82)); g.rect(W // 2 + 5, 1, 4, 6, C(255, 255, 255)); g.rect(W // 2 + 9, 1, 4, 6, C(214, 57, 57))
    signboard(g, W // 2, 24, 'CAPITANERIA', bg=C(57, 99, 173), fg=C(255, 255, 255))
    # anchor emblem
    ax = W // 2
    g.vline(ax, 44, 9, C(57, 99, 173)); g.hline(ax - 3, 46, 7, C(57, 99, 173))
    g.hline(ax - 4, 52, 9, C(57, 99, 173)); g.p(ax - 4, 51, C(57, 99, 173)); g.p(ax + 4, 51, C(57, 99, 173))
    dx = W // 2 - 8
    g.rect(dx, 60, 16, 20, C(66, 99, 140)); g.rect(dx + 2, 62, 12, 18, PAL['glass'][2])
    g.vline(dx + 8, 62, 18, OUT)
    g.rect(dx - 4, 77, 24, 3, PAL['stone'][1])
    g.outline()
    ch = H // 16
    solid = {(x, y) for x in range(cw) for y in range(ch)}
    dcell = (W // 2) // 16
    solid.discard((dcell, ch - 1))
    return dict(img=g.im, solid=solid, door=(dcell, ch - 1))


def deposito(cw=8, name='DEPOSITO'):
    """Harbour warehouse: corrugated pitched roof, brick, big sliding doors, crates."""
    W, H = cw * 16, 64
    g = Px(W, H)
    roof = [C(189, 198, 206), C(156, 165, 173), C(115, 123, 132), C(82, 90, 99)]
    for y in range(4, 24):
        g.hline(2, y, W - 4, roof[1] if y % 3 else roof[2])
    for x in range(4, W - 4, 6):
        g.vline(x, 4, 20, roof[0])
    g.hline(2, 4, W - 4, roof[0]); g.hline(2, 23, W - 4, roof[3])
    wall_fill(g, 3, 24, W - 6, 40, PAL['brick'], 9)
    # two big doors
    for dx in (14, W - 46):
        g.rect(dx, 34, 32, 30, C(99, 115, 132))
        for x in range(dx + 2, dx + 32, 4):
            g.vline(x, 35, 29, C(82, 99, 115))
        g.hline(dx, 34, 32, OUT); g.vline(dx, 34, 30, OUT); g.vline(dx + 31, 34, 30, OUT)
        g.vline(dx + 16, 34, 30, OUT)
    signboard(g, W // 2, 26, name)
    # small door in the middle
    mx = W // 2 - 6
    door(g, mx, H - 17, w=12, h=15)
    g.outline()
    ch = H // 16
    solid = {(x, y) for x in range(cw) for y in range(ch)}
    dc = (W // 2) // 16
    solid.discard((dc, ch - 1))
    return dict(img=g.im, solid=solid, door=(dc, ch - 1))


def crates():
    g = Px(32, 32)
    for (x, y) in ((2, 12), (16, 14), (8, 2)):
        g.rect(x, y, 14, 14, C(189, 140, 82)); g.rect(x + 1, y + 1, 12, 12, C(214, 165, 99))
        g.hline(x + 1, y + 6, 12, C(165, 115, 66)); g.vline(x + 6, y + 1, 12, C(165, 115, 66))
    g.outline()
    return dict(img=g.im, solid={(0, 1), (1, 1), (0, 0), (1, 0)}, door=None)


def casa_aie(cw=11):
    """Casa delle Aie (Cervia), from the photo: cream/pale-yellow plaster, dark grey low hip roofs with
    deep eaves and brick chimneys; two-storey wings left and right, central body with two tall round
    arches over the glazed entrance; barred windows."""
    W, H = cw * 16, 96
    g = Px(W, H)
    wall = [C(255, 239, 196), C(247, 222, 165), C(226, 196, 140), C(181, 148, 99)]
    roofc = [C(115, 115, 115), C(90, 90, 90), C(66, 66, 66), C(49, 49, 49), C(33, 33, 33)]
    lw, rw = 3 * 16, 4 * 16
    cx0, cx1 = lw, W - rw
    # roofs (left wing lower, central lowest, right wing tallest)
    coppi_roof(g, 0, 18, lw + 4, 18, roofc)
    coppi_roof(g, cx0 - 2, 24, cx1 - cx0 + 4, 14, roofc, hip=False)
    coppi_roof(g, cx1 - 4, 8, rw + 4, 22, roofc)
    for x0, y0 in ((18, 8), (W - 30, 0)):
        g.rect(x0, y0, 9, 12, PAL['brick'][1]); g.rect(x0 - 1, y0, 11, 3, PAL['brick'][3])
        g.hline(x0, y0 + 5, 9, PAL['brick'][2])
    # walls
    wall_fill(g, 2, 38, lw - 2, 58, wall, 1)
    wall_fill(g, cx0, 40, cx1 - cx0, 56, wall, 2)
    wall_fill(g, cx1, 32, rw - 2, 64, wall, 3)
    # central arches: tall round arches framing the upper windows, glazed doors below
    n = 2
    aw = (cx1 - cx0 - 12) // n
    for i in range(n):
        ax = cx0 + 6 + i * (aw + 0)
        g.rect(ax + 3, 52, aw - 6, 40, C(140, 99, 66))
        for y in range(44, 52):
            t = (52 - y) / 8.0
            half = int((aw - 6) / 2 * max(0.0, 1 - t * t) ** 0.5)
            g.hline(ax + aw // 2 - half, y, 2 * half, C(140, 99, 66))
        g.rect(ax + 6, 50, aw - 12, 10, PAL['glass'][1]); g.vline(ax + aw // 2, 50, 10, OUT)
        g.rect(ax + 5, 66, aw - 10, 26, C(99, 74, 57))
        g.rect(ax + 7, 68, aw - 14, 22, C(255, 214, 140))          # warm light inside
        g.vline(ax + aw // 2, 68, 22, C(99, 74, 57))
    # barred windows on the wings
    def barred(x, y):
        g.rect(x, y, 12, 12, C(66, 82, 99)); g.rect(x + 1, y + 1, 10, 10, PAL['glass'][2])
        for xx in range(x + 2, x + 11, 3):
            g.vline(xx, y + 1, 10, C(49, 49, 49))
        g.hline(x - 1, y + 12, 14, wall[3])
    for (x, y) in ((12, 46), (30, 46), (12, 70), (cx1 + 10, 40), (cx1 + 36, 40), (cx1 + 10, 66), (cx1 + 36, 66)):
        barred(x, y)
    g.rect(28, 78, 14, 18, C(99, 74, 57))                         # side door left wing
    # wooden sign ENTRATA on two posts, in front of the left arch
    g.rect(2, 92, W - 4, 4, PAL['stone'][2])
    g.outline()
    ch = H // 16
    solid = {(x, y) for x in range(cw) for y in range(ch)}
    door_cx = (cx0 + 6 + (aw // 2)) // 16
    solid.discard((door_cx, ch - 1))
    return dict(img=g.im, solid=solid, door=(door_cx, ch - 1))


def entrata_sign():
    g = Px(32, 32)
    g.rect(2, 6, 3, 26, PAL['wood'][3]); g.rect(27, 6, 3, 26, PAL['wood'][3])
    g.rect(0, 2, 32, 12, C(214, 214, 206)); g.hline(0, 2, 32, C(255, 255, 255))
    text(g, 3, 5, 'ENTRATA', C(49, 49, 66))
    g.outline()
    return dict(img=g.im, solid={(0, 1), (1, 1)}, door=None, top_rows=1)


def planter(w=3):
    g = Px(16 * w, 16)
    g.rect(0, 8, 16 * w, 8, C(90, 57, 41)); g.hline(0, 8, 16 * w, C(132, 90, 57))
    rnd = random.Random(w)
    g.rect(1, 1, 16 * w - 2, 8, PAL['leaf'][2])
    for _ in range(18 * w):
        x = rnd.randrange(1, 16 * w - 1); y = rnd.randrange(0, 9)
        g.p(x, y, rnd.choice(PAL['leaf'][0:3]))
    g.outline()
    return dict(img=g.im, solid={(i, 0) for i in range(w)}, door=None)


def rope_fence(n=4):
    g = Px(16 * n, 16)
    for i in range(n):
        g.rect(i * 16 + 6, 4, 4, 11, C(239, 239, 231)); g.hline(i * 16 + 6, 4, 4, C(255, 255, 255))
    for x in range(16 * n):
        y = 7 + int(2 * abs(((x % 16) - 8) / 8.0))
        g.p(x, y, C(214, 206, 189))
    return dict(img=g.im, solid={(i, 0) for i in range(n)}, door=None)


def pergola(cw=4):
    """Wooden pergola with vines, walk-under (top layer)."""
    W, H = cw * 16, 32
    g = Px(W, H)
    rnd = random.Random(5)
    for x in (2, W - 5):
        g.rect(x, 6, 3, 26, PAL['wood'][2])
    g.rect(0, 2, W, 5, PAL['wood'][1]); g.hline(0, 2, W, PAL['wood'][0])
    for _ in range(W * 3):
        x = rnd.randrange(W); y = rnd.randrange(0, 12)
        g.p(x, y, rnd.choice(PAL['leaf'][:4]))
    for _ in range(10):
        x = rnd.randrange(2, W - 2); y = rnd.randrange(4, 12)
        g.p(x, y, C(132, 57, 132)); g.p(x + 1, y + 1, C(99, 41, 99))
    g.outline()
    return dict(img=g.im, solid={(0, 1), (cw - 1, 1)}, door=None, top_rows=1)


def aia_table():
    """Long rustic table with benches (2x2)."""
    g = Px(32, 32)
    g.rect(1, 4, 30, 4, PAL['wood'][2])
    g.rect(0, 10, 32, 12, PAL['wood'][1]); g.hline(0, 10, 32, PAL['wood'][0])
    for x in (4, 12, 20, 26):
        g.rect(x, 12, 4, 3, C(255, 255, 255)); g.p(x + 1, 13, C(214, 57, 57))
    g.rect(1, 24, 30, 4, PAL['wood'][2])
    for x in (2, 28):
        g.vline(x, 22, 6, PAL['wood'][3])
    g.outline()
    return dict(img=g.im, solid={(0, 0), (1, 0), (0, 1), (1, 1)}, door=None)


def pensione(cw=8):
    """Pensione Pokémon: a farmhouse with a red roof and a big sign."""
    W, H = cw * 16, 80
    g = Px(W, H)
    coppi_roof(g, 1, 6, W - 2, 30, PAL['roof'])
    wall_fill(g, 2, 36, W - 4, 44, PAL['cream'], 2)
    g.rect(2, 36, W - 4, 3, PAL['wood'][2])
    for i in range(cw - 2):
        sx = 8 + i * ((W - 16) // (cw - 2))
        if abs(sx + 6 - W // 2) < 14:
            continue
        window(g, sx, 50, PAL['cream'], PAL['brown_sh'])
    signboard(g, W // 2, 40, 'PENSIONE POKEMON', bg=C(255, 239, 214), fg=C(165, 57, 41))
    dx = W // 2 - 6
    door(g, dx, H - 17, w=12, h=15)
    g.rect(2, H - 4, W - 4, 4, PAL['stone'][2])
    g.outline()
    ch = H // 16
    solid = {(x, y) for x in range(cw) for y in range(ch)}
    dc = (W // 2) // 16
    solid.discard((dc, ch - 1))
    return dict(img=g.im, solid=solid, door=(dc, ch - 1))


def beach_volley():
    g = Px(64, 32)
    g.vline(3, 4, 26, PAL['wood'][3]); g.vline(60, 4, 26, PAL['wood'][3])
    for y in range(6, 14, 2):
        g.hline(4, y, 56, C(255, 255, 255))
    for x in range(4, 60, 3):
        g.vline(x, 6, 8, C(214, 214, 214))
    g.hline(4, 6, 56, C(57, 99, 173))
    g.outline()
    return dict(img=g.im, solid={(0, 1), (3, 1)}, door=None, top_rows=1)


def fishing_hut():
    """Padellone/capanno da pesca on stilts with the square net (bilancia)."""
    g = Px(48, 48)
    for x in (6, 38):
        g.vline(x, 26, 22, PAL['wood'][3])
    g.rect(4, 14, 40, 14, PAL['wood'][1]); g.hline(4, 14, 40, PAL['wood'][0])
    for x in range(6, 44, 4):
        g.vline(x, 15, 12, PAL['wood'][2])
    g.rect(2, 8, 44, 7, PAL['roof'][2]); g.hline(2, 8, 44, PAL['roof'][1])
    g.rect(18, 18, 10, 9, PAL['wood'][3])
    # net poles
    for i in range(12):
        g.p(30 + i, 6 - i // 2, PAL['wood'][3])
    g.outline()
    return dict(img=g.im, solid={(x, y) for x in range(3) for y in (1, 2)}, door=None, top_rows=1)


def pillar(brick='brick'):
    """Stone/brick gate pillar with a lantern (1x2), marks side exits."""
    g = Px(16, 32)
    b = PAL[brick]
    g.rect(3, 8, 10, 24, b[1])
    for y in range(10, 32, 5):
        g.hline(3, y, 10, b[2])
    g.vline(12, 8, 24, b[3])
    g.rect(2, 5, 12, 4, PAL['stone'][1]); g.hline(2, 5, 12, PAL['stone'][0])
    g.rect(6, 0, 4, 5, C(255, 231, 140)); g.hline(5, 0, 6, OUT)
    g.outline()
    return dict(img=g.im, solid={(0, 1)}, door=None)


def isola_rose():
    """Isola delle Rose (1967-69): square steel platform on pylons ~11 km off Rimini, with a white
    multi-storey block, railings, a flag (orange field, white shield with three red roses). 6x6 cells."""
    W, H = 96, 96
    g = Px(W, H)
    steel = [C(206, 206, 214), C(173, 173, 181), C(132, 132, 140), C(90, 90, 99)]
    # deck seen from above (4 rows), front face and pylons into the sea
    g.rect(0, 16, W, 48, steel[1])
    for x in range(0, W, 8):
        g.vline(x, 16, 48, steel[2])
    for y in range(16, 64, 8):
        g.hline(0, y, W, steel[2])
    for x in range(0, W, 4):                            # railings
        g.vline(x, 14, 3, steel[3])
    g.hline(0, 14, W, steel[0]); g.hline(0, 62, W, steel[0])
    g.rect(0, 64, W, 8, steel[2]); g.hline(0, 64, W, steel[3])
    for px in (6, 30, 54, 78):
        g.rect(px, 72, 10, 24, steel[3]); g.vline(px + 1, 72, 24, steel[2])
    # building on the deck (white, two storeys, flat roof), upper part covers the player
    g.rect(28, 0, 40, 34, C(247, 247, 239)); g.rect(28, 0, 40, 4, C(214, 214, 206))
    for wx in (32, 44, 56):
        for wy in (8, 22):
            g.rect(wx, wy, 8, 7, PAL['glass'][1]); g.hline(wx, wy, 8, OUT)
    g.rect(44, 36, 8, 12, C(99, 74, 57))             # door on the deck (decorative)
    # flag
    g.vline(78, 0, 22, C(140, 140, 140))
    g.rect(79, 1, 14, 9, C(247, 140, 41))
    g.rect(83, 2, 6, 7, C(255, 255, 255))
    for (x, y) in ((84, 4), (86, 4), (85, 6)):
        g.p(x, y, C(214, 41, 57))
    g.outline(open_sides='')
    solid = {(x, y) for x in range(6) for y in (4, 5)} | {(x, 0) for x in range(2, 4)} | {(x, y) for x in range(2, 4) for y in (1, 2)}
    return dict(img=g.im, solid=solid, door=None, top_rows=1)


def shrine():
    """Small wooden forest shrine on a stone base (2x2), with a round hollow for the GS Ball."""
    g = Px(32, 32)
    st = PAL['stone']
    g.rect(4, 22, 24, 10, st[2]); g.hline(4, 22, 24, st[1]); g.hline(4, 31, 24, st[3])
    g.rect(7, 8, 18, 14, PAL['wood'][1]); g.rect(9, 10, 14, 11, PAL['wood'][3])
    g.rect(13, 13, 6, 6, C(206, 189, 99)); g.rect(14, 14, 4, 4, C(255, 239, 156))
    # roof
    for i in range(7):
        g.hline(4 + i, 7 - i, 24 - 2 * i, PAL['roof_brown'][1] if i % 2 else PAL['roof_brown'][2])
    g.hline(3, 8, 26, PAL['roof_brown'][3])
    # rope with paper streamers
    g.hline(7, 10, 18, C(239, 222, 173))
    for x in (10, 16, 22):
        g.vline(x, 11, 3, C(255, 255, 255))
    g.outline()
    return dict(img=g.im, solid={(0, 0), (1, 0), (0, 1), (1, 1)}, door=None)


def vistamare(cw=7):
    """Vistamare Suite Hotel (Lido di Savio): white modern block, seven floors of long cantilevered
    balconies with glass railings, flat roof, glazed ground floor with the restaurant."""
    W, H = cw * 16, 128
    g = Px(W, H)
    white = [C(255, 255, 255), C(239, 239, 235), C(214, 214, 206), C(173, 173, 165)]
    g.rect(4, 6, W - 8, H - 10, C(247, 239, 214))                 # cream core
    g.rect(2, 2, W - 4, 5, white[1]); g.hline(2, 2, W - 4, white[0])   # roof slab
    g.rect(W // 2 - 10, 0, 20, 3, white[2])
    floors = 6
    fh = 16                                   # floors and windows on the 8 px grid: identical tiles repeat
    for f in range(floors):
        y = 8 + f * fh
        # windows / glass doors behind the balcony
        for x in range(8, W - 8, 8):
            g.rect(x, y + 2, 6, fh - 6, C(156, 189, 214)); g.p(x + 1, y + 3, C(222, 239, 255))
        # cantilevered balcony slab + glass railing
        g.rect(0, y + fh - 4, W, 3, white[0]); g.hline(0, y + fh - 1, W, white[3])
        g.rect(1, y + fh - 8, W - 2, 4, C(206, 231, 239))
        g.hline(1, y + fh - 8, W - 2, white[2])
        for x in range(4, W - 1, 4):
            g.vline(x, y + fh - 8, 4, white[2])
    # ground floor: glazed restaurant with white curtains and the entrance
    gy = 8 + floors * fh
    g.rect(4, gy, W - 8, H - gy - 2, C(99, 140, 156))
    for x in range(6, W - 6, 8):
        g.rect(x, gy + 2, 6, H - gy - 6, C(206, 231, 239)); g.rect(x, gy + 2, 2, H - gy - 6, C(255, 255, 255))
    signboard(g, W // 2, gy - 9, 'VISTAMARE', bg=C(255, 255, 255), fg=C(57, 99, 140))
    dx = W // 2 - 7
    g.rect(dx, H - 16, 14, 14, C(57, 99, 140)); g.rect(dx + 2, H - 14, 10, 12, C(173, 214, 231))
    g.rect(0, H - 2, W, 2, white[3])
    g.outline()
    ch = H // 16
    solid = {(x, y) for x in range(cw) for y in range(ch)}
    dc = (W // 2) // 16
    solid.discard((dc, ch - 1))
    return dict(img=g.im, solid=solid, door=(dc, ch - 1))


def pool(w=6, h=4):
    """Hotel pool with a teak deck rim (walk around it; water not swimmable)."""
    g = Px(16 * w, 16 * h)
    g.rect(0, 0, 16 * w, 16 * h, C(198, 156, 107))
    for y in range(0, 16 * h, 4):
        g.hline(0, y, 16 * w, C(173, 132, 90))
    g.rect(6, 6, 16 * w - 12, 16 * h - 12, C(99, 206, 231))
    g.rect(6, 6, 16 * w - 12, 3, C(57, 165, 206))
    for x in range(14, 16 * w - 14, 12):
        g.hline(x, 16 + (x % 3) * 6, 6, C(206, 247, 255))
    g.rect(6, 6, 16 * w - 12, 16 * h - 12, C(99, 206, 231)) if False else None
    return dict(img=g.im, solid={(x, y) for x in range(1, w - 1) for y in range(1, h - 1)}, door=None)


def daybed():
    g = Px(32, 16)
    g.rect(1, 3, 30, 11, C(255, 255, 255)); g.rect(1, 12, 30, 3, C(206, 206, 206))
    g.rect(2, 4, 8, 4, C(239, 239, 239))
    g.outline()
    return dict(img=g.im, solid={(0, 0), (1, 0)}, door=None)


def white_umbrella():
    g = Px(16, 32)
    g.vline(8, 10, 21, C(132, 99, 66))
    for y in range(2, 11):
        half = min(7, (y - 1))
        g.hline(8 - half, y, 2 * half + 1, C(255, 255, 255) if y < 9 else C(214, 214, 206))
    g.outline()
    return dict(img=g.im, solid={(0, 1)}, door=None, top_rows=1)


def palm():
    g = Px(32, 48)
    g.rect(14, 18, 4, 30, PAL['bark'][1]); g.vline(15, 18, 30, PAL['bark'][0])
    for (dx, dy) in ((-12, 4), (12, 4), (-10, -2), (10, -2), (0, -6), (-14, 10), (14, 10)):
        for t in range(12):
            x = 16 + int(dx * t / 12); y = 16 + int(dy * t / 12) + (t * t) // 18
            g.rect(x - 1, y - 1, 3, 2, PAL['leaf'][1 + (t % 3)])
    g.outline()
    return dict(img=g.im, solid={(0, 2), (1, 2)}, door=None, top_rows=2)


def bar_panama(cw=9):
    """Caffè Panama (Lido di Savio): ground floor of a 1960s apartment block (tan brick bands,
    white balcony column), a deep flat grey canopy on thin columns all along the front, the dark
    'Caffè Panama' sign with a palm and the 'MOKADOR' board, glazed bar with dark frames behind."""
    W, H = cw * 16, 80
    g = Px(W, H)
    brick = [C(239, 198, 156), C(222, 173, 132), C(198, 148, 107), C(165, 115, 82)]
    bw = W - 20                                  # block narrower than the canopy
    bx = 10
    # apartment block (3 floors visible above the canopy)
    g.rect(bx, 2, bw, 46, brick[1])
    for y in range(4, 48, 4):
        g.hline(bx, y, bw, brick[2])
        o = 0 if (y // 4) % 2 else 4
        for x in range(bx + o, bx + bw, 8):
            g.vline(x, y - 3, 3, brick[2])
    g.rect(bx - 1, 0, bw + 2, 3, C(140, 115, 99))                # roof edge
    # white stucco column with balconies (left third), like the photo
    cx0, cw0 = bx + 6, 40
    g.rect(cx0, 3, cw0, 45, C(247, 243, 235))
    for fy in (4, 19, 34):
        g.rect(cx0 + 3, fy + 1, cw0 - 6, 8, C(99, 115, 132))         # glass doors in shadow
        g.rect(cx0 + 5, fy + 2, 6, 6, C(173, 189, 206)); g.rect(cx0 + 22, fy + 2, 8, 6, C(173, 189, 206))
        g.rect(cx0 - 2, fy + 9, cw0 + 4, 2, C(255, 255, 255))     # slab
        g.hline(cx0 - 2, fy + 11, cw0 + 4, C(181, 181, 173))
        for x in range(cx0 - 1, cx0 + cw0 + 2, 3):                  # white railing
            g.vline(x, fy + 4, 5, C(255, 255, 255))
        g.hline(cx0 - 2, fy + 4, cw0 + 4, C(255, 255, 255))
        g.rect(cx0 + 26, fy, 12, 3, C(239, 222, 189))              # rolled awning
    # brick windows with roller shutters (right part)
    for fy in (6, 21, 36):
        for x in range(cx0 + cw0 + 10, bx + bw - 10, 22):
            g.rect(x, fy, 10, 9, C(239, 231, 214)); g.rect(x + 1, fy + 1, 8, 4, C(214, 206, 189))
            g.rect(x + 1, fy + 5, 8, 4, C(99, 115, 140)); g.hline(x, fy + 9, 10, C(255, 255, 255))
    # ---- canopy: long flat grey slab with a dark fascia
    g.rect(0, 48, W, 3, C(156, 156, 148)); g.rect(0, 51, W, 3, C(99, 99, 99))
    g.hline(0, 48, W, C(198, 198, 189))
    # sign boards hanging on the fascia (centre): Caffè Panama (dark, palm) + MOKADOR
    sx = W // 2 - 26
    g.rect(sx, 38, 52, 11, C(24, 33, 49)); g.hline(sx, 38, 52, C(57, 66, 90)); g.hline(sx, 48, 52, C(8, 8, 16))
    text(g, sx + 3, 40, 'PANAMA', C(247, 239, 214))
    g.vline(sx + 46, 40, 7, C(239, 206, 57)); g.vline(sx + 47, 41, 6, C(214, 173, 41))
    for (dx, dy) in ((-3, 0), (3, 0), (-2, -1), (2, -1), (0, -2)):
        g.p(sx + 46 + dx, 40 + dy, C(57, 165, 74)); g.p(sx + 46 + dx // 2, 40 + dy // 2, C(57, 140, 66))
    g.rect(sx + 10, 54, 32, 6, C(41, 33, 33)); text(g, sx + 11, 54, 'MOKA', C(255, 255, 255)) if False else None
    g.hline(sx + 12, 56, 28, C(214, 206, 189))
    # ---- under the canopy: shadowed glazed bar, thin columns
    g.rect(0, 54, W, 26, C(115, 115, 115))
    g.rect(4, 56, W - 8, 22, C(57, 66, 74))
    for x in range(6, W - 6, 10):
        g.rect(x, 58, 8, 18, C(90, 115, 132)); g.p(x + 1, 59, C(156, 189, 206)); g.p(x + 2, 60, C(156, 189, 206))
    g.rect(0, 78, W, 2, C(173, 165, 156))
    for x in range(2, W, 32):
        g.rect(x, 51, 2, 29, C(140, 140, 140)); g.vline(x, 51, 29, C(189, 189, 181))
    # entrance: glass door with the bar light inside
    dc = cw // 2
    dx = dc * 16
    g.rect(dx + 2, 62, 12, 18, C(41, 41, 49)); g.rect(dx + 3, 63, 10, 17, C(239, 189, 107))
    g.vline(dx + 8, 63, 17, C(41, 41, 49)); g.rect(dx + 4, 66, 3, 4, C(255, 231, 156))
    g.outline()
    ch = H // 16
    solid = {(x, y) for x in range(cw) for y in range(ch)}
    solid.discard((dc, ch - 1))
    return dict(img=g.im, solid=solid, door=(dc, ch - 1))


def panama_table(cloth=C(239, 132, 49)):
    """Square table with an orange cloth and two white plastic chairs."""
    g = Px(32, 16)
    for x in (1, 23):
        g.rect(x, 3, 8, 6, C(255, 255, 255)); g.rect(x, 9, 8, 3, C(231, 231, 223))
        g.vline(x + 1, 12, 3, C(206, 206, 198)); g.vline(x + 6, 12, 3, C(206, 206, 198))
    g.rect(10, 4, 12, 9, cloth); g.hline(10, 12, 12, C(198, 99, 33)); g.p(14, 6, C(255, 255, 255)); g.p(16, 7, C(255, 255, 255))
    g.outline()
    return dict(img=g.im, solid={(0, 0), (1, 0)}, door=None)


def white_planter(w=2):
    """Long white planter box with dark green shrubs (Caffè Panama front)."""
    g = Px(16 * w, 16)
    g.rect(0, 9, 16 * w, 7, C(247, 247, 243)); g.hline(0, 9, 16 * w, C(255, 255, 255)); g.hline(0, 15, 16 * w, C(198, 198, 189))
    rnd = random.Random(7 + w)
    for _ in range(30 * w):
        x = rnd.randrange(1, 16 * w - 1); y = rnd.randrange(0, 10)
        g.p(x, y, rnd.choice([C(41, 99, 49), C(57, 123, 57), C(82, 148, 74)]))
    g.outline()
    return dict(img=g.im, solid={(i, 0) for i in range(w)}, door=None)


def blue_lamp():
    g = Px(16, 32)
    g.rect(7, 6, 2, 25, C(41, 90, 189)); g.vline(7, 6, 25, C(99, 140, 222))
    g.rect(4, 2, 8, 4, C(231, 231, 223)); g.hline(4, 5, 8, C(173, 173, 165))
    g.outline()
    return dict(img=g.im, solid={(0, 1)}, door=None)


def torre_san_michele(cw=4):
    """Torre San Michele (Cervia, 1691): square brick tower with a battered base and a stone
    string-course, small windows, the city arms over an arched door, corbels and battlements on top."""
    W, H = cw * 16, 96
    g = Px(W, H)
    b = [C(222, 140, 99), C(198, 115, 82), C(173, 90, 66), C(132, 66, 49)]
    stone = [C(239, 231, 206), C(214, 206, 181), C(173, 165, 140)]
    inset = 6
    g.rect(inset, 12, W - 2 * inset, H - 12, b[1])
    for y in range(14, H, 3):                                   # brick courses
        g.hline(inset, y, W - 2 * inset, b[2])
        o = 0 if (y // 3) % 2 else 3
        for x in range(inset + o, W - inset, 6):
            g.p(x, y + 1, b[2])
    g.vline(inset, 12, H - 12, b[0]); g.vline(W - inset - 1, 12, H - 12, b[3])
    # battered base (scarpa) + cordone
    for i in range(14):
        y = H - 14 + i
        g.hline(inset - i // 3, y, W - 2 * inset + 2 * (i // 3), b[2] if i % 3 else b[3])
    g.rect(inset - 1, H - 16, W - 2 * inset + 2, 2, stone[0]); g.hline(inset - 1, H - 15, W - 2 * inset + 2, stone[2])
    # corbels (beccatelli) and the projecting battlemented parapet
    g.rect(2, 8, W - 4, 4, b[2])
    for x in range(3, W - 3, 5):
        g.rect(x, 12, 3, 4, b[3]); g.p(x + 1, 15, b[2])
    g.rect(2, 2, W - 4, 7, b[1]); g.hline(2, 8, W - 4, b[3])
    for x in range(2, W - 2, 8):
        g.rect(x, 0, 5, 3, b[1]); g.hline(x, 0, 5, b[0])
    # windows (slits and a small square one), clock-like coat of arms
    for (x, y) in ((W // 2 - 1, 24), (W // 2 - 1, 44)):
        g.rect(x, y, 3, 8, C(57, 41, 41)); g.hline(x - 1, y - 1, 5, stone[1])
    g.rect(W // 2 - 4, 58, 9, 10, stone[0]); g.rect(W // 2 - 3, 59, 7, 4, C(57, 99, 173)); g.rect(W // 2 - 3, 63, 7, 4, C(239, 239, 239))
    g.rect(W // 2 - 2, 60, 5, 2, C(255, 222, 99))
    # arched door with stone frame
    dx = (cw // 2) * 16 - 8 + 2
    g.rect(dx, H - 16, 12, 16, stone[1]); g.rect(dx + 2, H - 13, 8, 13, C(99, 57, 41))
    g.hline(dx + 3, H - 14, 6, C(99, 57, 41)); g.vline(dx + 6, H - 12, 12, C(66, 41, 33))
    g.outline()
    ch = H // 16
    solid = {(x, y) for x in range(cw) for y in range(ch)}
    dc = (dx + 6) // 16
    solid.discard((dc, ch - 1))
    return dict(img=g.im, solid=solid, door=(dc, ch - 1))


def gatehouse(side='east', name='SALINE'):
    """Varco: small brick gatehouse straddling the road, with a pass-through arch on one side
    (door on the east face for Cervia, on the west face for the Saline)."""
    cw, ch = 4, 5
    W, H = cw * 16, ch * 16
    g = Px(W, H)
    b = PAL['brick']
    coppi_roof(g, 0, 0, W, 30, PAL['roof'])
    g.rect(2, 28, W - 4, H - 28, b[1])
    for y in range(31, H, 4):
        g.hline(2, y, W - 4, b[2])
        o = 0 if (y // 4) % 2 else 4
        for x in range(2 + o, W - 2, 8):
            g.vline(x, y - 3, 3, b[2])
    g.hline(2, 28, W - 4, b[3])
    signboard(g, W // 2 - (6 if side == 'east' else -6), 34, name, bg=C(255, 247, 222), fg=C(66, 99, 140))
    # windows
    wx = 8 if side == 'east' else W - 20
    g.rect(wx, 48, 10, 10, C(239, 231, 214)); g.rect(wx + 1, 49, 8, 8, C(140, 189, 214)); g.vline(wx + 5, 49, 8, C(239, 231, 214))
    # pass-through arch on the door side (bottom cell of that column)
    ax = W - 16 if side == 'east' else 0
    g.rect(ax + 1, H - 22, 14, 22, C(239, 231, 206))
    g.rect(ax + 3, H - 19, 10, 19, C(57, 41, 41)); g.hline(ax + 4, H - 20, 8, C(57, 41, 41))
    g.rect(ax + 3, H - 6, 10, 6, C(198, 173, 140))
    g.outline()
    solid = {(x, y) for x in range(cw) for y in range(ch)}
    dc = (cw - 1 if side == 'east' else 0, ch - 1)
    solid.discard(dc)
    return dict(img=g.im, solid=solid, door=dc)


def door_overlay(frame=C(222, 206, 173), wood=C(115, 66, 41)):
    """A proper wooden door for buildings pasted from the 0.21 maps (replaces the bare pale doorway)."""
    g = Px(16, 16)
    g.rect(1, 0, 14, 16, frame); g.vline(1, 0, 16, C(173, 156, 123)); g.vline(14, 0, 16, C(173, 156, 123))
    g.rect(3, 2, 10, 14, wood); g.hline(4, 1, 8, wood)
    g.vline(8, 2, 14, C(74, 41, 24)); g.p(6, 9, C(239, 206, 99)); g.p(10, 9, C(239, 206, 99))
    for y in (5, 11): g.hline(4, y, 3, C(140, 90, 57)); g.hline(9, y, 3, C(140, 90, 57))
    g.hline(0, 15, 16, C(156, 140, 115))
    return g.im


def glass_door_overlay():
    """Modern glazed entrance with a steel canopy (Grattacielo)."""
    g = Px(16, 16)
    g.rect(0, 0, 16, 16, C(173, 181, 189))
    g.rect(0, 0, 16, 3, C(99, 107, 115)); g.hline(0, 3, 16, C(57, 66, 74))
    g.rect(2, 4, 12, 12, C(57, 74, 99)); g.rect(3, 5, 5, 11, C(140, 189, 222)); g.rect(8, 5, 5, 11, C(140, 189, 222))
    g.vline(8, 5, 11, C(57, 74, 99)); g.p(4, 6, C(222, 239, 255)); g.p(9, 6, C(222, 239, 255))
    g.p(7, 11, C(206, 206, 214)); g.p(9, 11, C(206, 206, 214))
    return g.im


def wheel_gate_overlay():
    """Boarding gate of the ferris wheel: small wooden platform with a little red-white awning."""
    g = Px(16, 16)
    g.rect(0, 0, 16, 16, C(198, 148, 99))
    for y in (4, 8, 12): g.hline(0, y, 16, C(156, 107, 66))
    for x in range(0, 16, 4):
        g.rect(x, 0, 2, 4, C(222, 57, 57)); g.rect(x + 2, 0, 2, 4, C(255, 255, 255))
    g.vline(1, 4, 12, C(132, 140, 148)); g.vline(14, 4, 12, C(132, 140, 148))
    g.rect(5, 7, 6, 2, C(239, 206, 57))
    return g.im


def ponte_tiberio2(cells=10):
    """Ponte di Tiberio (AD 14-21) seen from the south, larger: deck with Roman paving and massive parapets
    (rows 0-1, walkable), then three rows of face in warm Istrian stone: cornice with dentils, five round
    arches with voussoirs and keystones, aedicules with pediments on the four piers, cutwaters in the water.
    Textures repeat every 16 px so the tiles are shared."""
    import math
    W, H = cells * 16, 80
    g = Px(W, H)
    st = [C(239, 231, 214), C(222, 212, 192), C(198, 188, 166), C(165, 156, 136), C(123, 115, 99)]
    # deck: north parapet (blocks + coping), paving tile pattern (period 16), south parapet
    g.rect(0, 0, W, 6, st[1]); g.hline(0, 0, W, st[0]); g.hline(0, 5, W, st[4])
    for x in range(0, W, 16): g.vline(x, 1, 4, st[3])
    pav = [(1, 7, 7, 3), (9, 7, 6, 3), (1, 11, 5, 4), (7, 11, 8, 4), (1, 16, 8, 4), (10, 16, 5, 4), (1, 21, 6, 4), (8, 21, 7, 4)]
    g.rect(0, 6, W, 20, C(140, 134, 124))
    for x0 in range(0, W, 16):
        for (x, y, w, h) in pav:
            g.rect(x0 + x, y, w, h, C(166, 160, 148) if (x + y) % 3 else C(156, 150, 138))
    g.rect(0, 26, W, 6, st[1]); g.hline(0, 26, W, st[0]); g.hline(0, 31, W, st[3])
    for x in range(0, W, 16): g.vline(x, 27, 4, st[3])
    # face: ashlar courses (period 16)
    g.rect(0, 32, W, 48, st[2])
    for y in range(38, 80, 5):
        g.hline(0, y, W, st[3])
        off = 0 if (y // 5) % 2 else 8
        for x in range(off, W, 16): g.vline(x, y - 4, 4, st[3])
    # cornice with dentils under the parapet
    g.rect(0, 32, W, 5, st[0]); g.hline(0, 36, W, st[4])
    for x in range(1, W, 4): g.rect(x, 37, 2, 2, st[1])
    # five arches (the middle three a little wider)
    spans = [(4, 24), (34, 28), (66, 28), (98, 28), (132, 24)]
    for ax, aw in spans:
        cx = ax + aw / 2.0; r = aw / 2.0; spring = 58
        for y in range(int(spring - r), 80):
            if y < spring:
                half = math.sqrt(max(0.0, r * r - (spring - y) ** 2))
            else:
                half = r
            for x in range(int(cx - half), int(cx + half) + 1):
                if 0 <= x < W:
                    depth = (y - (spring - r)) / (80 - (spring - r))
                    g.p(x, y, C(41, 49, 57) if y < spring + 6 else (WATER[2] if depth < 0.85 else WATER[1]))
        for k in range(11):                                      # voussoirs
            a = math.pi * k / 10
            for rr in (r + 1, r + 2, r + 3):
                x = cx - math.cos(a) * rr; y = spring - math.sin(a) * rr
                g.p(int(round(x)), int(round(y)), st[0] if k % 2 else st[1])
        g.rect(int(cx) - 1, int(spring - r) - 4, 3, 4, st[0])     # keystone
        for y in (68, 73, 77): g.hline(int(cx - 6), y, 5, WATER[0]); g.hline(int(cx + 2), y + 2, 4, WATER[0])
    # piers: aedicules (niche + pilasters + pediment) and cutwaters
    for px in (30, 63, 95, 129):
        g.rect(px - 1, 44, 2, 12, st[0]); g.rect(px + 5, 44, 2, 12, st[0])
        g.rect(px + 1, 46, 4, 10, st[4]); g.hline(px - 2, 43, 10, st[0])
        for i in range(4): g.hline(px - 1 + i, 42 - i, 8 - 2 * i, st[0])
        g.hline(px - 2, 56, 10, st[1])
        for i in range(8):                                       # cutwater (triangular breakwater)
            g.hline(px + 3 - (8 - i) // 2, 72 + i, (8 - i), st[1] if i < 3 else st[3])
    g.rect(0, 78, W, 2, WATER[3])
    g.outline(open_sides='EW')
    deck = {(x, y) for x in range(cells) for y in (0, 1)}
    solid = {(x, y) for x in range(cells) for y in (2, 3, 4)}
    return dict(img=g.im, solid=solid, door=None, deck=deck)


def arco_augusto():
    """Arco d'Augusto (27 BC), Rimini: single round arch in Istrian stone, two pairs of engaged Corinthian
    columns, round clipei with the gods, entablature with the inscription, central pediment and the
    medieval brick swallowtail merlons on top. 6x7 cells; the road passes through columns 2-3 (upper part drawn over the player)."""
    import math
    W, H = 96, 112
    g = Px(W, H)
    st = [C(247, 239, 222), C(231, 220, 198), C(206, 194, 170), C(173, 160, 136), C(123, 112, 94)]
    # medieval merlons (brick)
    br = [C(214, 132, 99), C(181, 107, 74), C(140, 82, 57)]
    g.rect(6, 6, W - 12, 6, br[1]); g.hline(6, 6, W - 12, br[0])
    for x in range(6, W - 10, 12):
        g.rect(x, 0, 8, 6, br[1]); g.rect(x + 3, 0, 2, 3, (0, 0, 0, 0))            # swallowtail notch
        g.hline(x, 0, 3, br[0]); g.hline(x + 5, 0, 3, br[0])
    # body
    g.rect(2, 12, W - 4, 100, st[1])
    for y in range(16, 112, 6):
        g.hline(2, y, W - 4, st[2])
    # entablature + inscription band
    g.rect(0, 12, W, 12, st[0]); g.hline(0, 23, W, st[3])
    g.rect(14, 15, W - 28, 6, st[1])
    for x in range(16, W - 16, 3): g.p(x, 17, st[4]); g.p(x + 1, 18, st[4])
    # pediment (triangular, over the arch)
    for i in range(10):
        g.hline(W // 2 - 4 - 2 * i, 26 + i, 8 + 4 * i, st[0] if i < 9 else st[3])
    g.rect(W // 2 - 26, 35, 52, 2, st[3])
    # columns (two pairs) with capitals and plinths
    for cx in (8, 22, W - 24, W - 10):
        g.rect(cx - 3, 40, 7, 54, st[0]); g.vline(cx - 3, 40, 54, C(255, 251, 239)); g.vline(cx + 3, 40, 54, st[3])
        for x in (cx - 1, cx + 1): g.vline(x, 44, 48, st[2])
        g.rect(cx - 5, 36, 11, 5, st[1]); g.p(cx - 4, 37, st[3]); g.p(cx + 4, 37, st[3]); g.p(cx, 38, st[3])   # capital
        g.rect(cx - 5, 94, 11, 18, st[2]); g.hline(cx - 5, 94, 11, st[0])                                  # plinth
    # clipei (round medallions with the gods' heads) between the columns
    for cx in (15, W - 17):
        for a in range(32):
            x = cx + round(5 * math.cos(a * math.pi / 16)); y = 30 + round(5 * math.sin(a * math.pi / 16))
            g.p(x, y, st[3])
        g.rect(cx - 2, 28, 4, 5, st[2]); g.p(cx - 1, 29, st[4])
    # the arch: opening with dark intrados at the top, voussoirs, keystone
    cx, r, spring = W // 2, 16, 64
    for y in range(spring - r, H):
        half = math.sqrt(max(0.0, r * r - (spring - y) ** 2)) if y < spring else r
        for x in range(int(cx - half), int(cx + half)):
            g.p(x, y, C(90, 82, 74) if y < spring else (0, 0, 0, 0))
    for k in range(13):
        a = math.pi * k / 12
        for rr in (r + 1, r + 2, r + 3):
            g.p(int(round(cx - math.cos(a) * rr)), int(round(spring - math.sin(a) * rr)), st[0] if k % 2 else st[2])
    g.rect(cx - 2, spring - r - 5, 4, 5, st[0])
    g.outline()
    for y in range(spring, H):                                    # open passage (the road shows through)
        for x in range(cx - r, cx + r):
            g.im.putpixel((x, y), (0, 0, 0, 0))
        g.im.putpixel((cx - r - 1, y), st[3] + (255,)); g.im.putpixel((cx + r, y), st[3] + (255,))
    passage = {(x, y) for x in (2, 3) for y in range(7)}
    solid = {(x, y) for x in range(6) for y in range(7)} - passage
    return dict(img=g.im, solid=solid, door=None, top_cells={(x, y) for x in (2, 3) for y in range(4)})


def rocca(cw=8, ch=6, keep=True, towers='round', wall=None, merlons='guelph'):
    """A Romagna fortress (Ravaldino, Sforzesca, Estense): brick curtain wall with corbels and merlons,
    corner towers (round or square), central keep, gate with the portcullis at the bottom centre.
    Brick texture repeats every 8 px so the tiles are shared."""
    import math
    Wp, Hp = cw * 16, ch * 16
    g = Px(Wp, Hp)
    b = wall or [C(214, 140, 99), C(189, 115, 82), C(156, 90, 66), C(115, 66, 49)]
    def bricks(x0, y0, w, h):
        g.rect(x0, y0, w, h, b[1])
        for y in range(y0, y0 + h, 4):
            g.hline(x0, y, w, b[2])
            off = 0 if (y // 4) % 2 else 4
            for x in range(x0 + ((off - x0) % 8), x0 + w, 8):
                g.vline(x, y + 1, 3, b[2])
    def merl(x0, y0, w):
        g.rect(x0, y0 + 4, w, 3, b[2])
        for x in range(x0, x0 + w - 3, 6):
            if merlons == 'ghibelline':
                g.rect(x, y0, 4, 5, b[1]); g.p(x + 1, y0, (0, 0, 0, 0)); g.p(x + 2, y0, (0, 0, 0, 0))
            else:
                g.rect(x, y0, 4, 5, b[1]); g.hline(x, y0, 4, b[0])
        for x in range(x0, x0 + w, 4):
            g.rect(x + 1, y0 + 7, 2, 3, b[3])                          # corbels
    # curtain wall
    wy = 26
    bricks(12, wy + 8, Wp - 24, Hp - wy - 8)
    merl(12, wy, Wp - 24)
    g.rect(12, Hp - 10, Wp - 24, 10, b[2])                            # battered base (scarpa)
    for y in range(Hp - 10, Hp, 2): g.hline(12, y, Wp - 24, b[3] if y % 4 == 0 else b[2])
    # keep (mastio)
    if keep:
        kx, kw = Wp // 2 - 14, 28
        bricks(kx, 8, kw, wy)
        merl(kx - 2, 0, kw + 4)
        g.rect(kx + 11, 16, 6, 9, C(57, 41, 41)); g.hline(kx + 11, 15, 6, b[0])
    # corner towers
    for tx in (0, Wp - 24):
        if towers == 'round':
            for y in range(14, Hp):
                for x in range(24):
                    dx = (x - 11.5) / 12
                    if abs(dx) <= 1:
                        shade = b[0] if dx < -0.5 else (b[1] if dx < 0.4 else b[2])
                        if (y // 4) % 2 == 0 and int(x + (y // 4) * 4) % 8 == 0: shade = b[2]
                        if y % 4 == 0: shade = b[2]
                        g.p(tx + x, y, shade)
            merl(tx, 8, 24)
        else:
            bricks(tx + 2, 14, 20, Hp - 14); merl(tx, 8, 24)
        g.rect(tx + 10, 30, 4, 7, C(57, 41, 41))                       # arrow slit
    # gate with portcullis and the drawbridge
    gx = Wp // 2 - 8
    g.rect(gx - 2, Hp - 30, 20, 30, C(222, 206, 173))
    g.rect(gx, Hp - 26, 16, 26, C(41, 33, 33)); g.hline(gx + 2, Hp - 27, 12, C(41, 33, 33))
    for x in range(gx + 2, gx + 16, 3): g.vline(x, Hp - 26, 18, C(115, 107, 99))
    for y in range(Hp - 24, Hp - 8, 4): g.hline(gx, y, 16, C(115, 107, 99))
    g.outline()
    solid = {(x, y) for x in range(cw) for y in range(ch)}
    door = (cw // 2, ch - 1)
    solid.discard(door)
    return dict(img=g.im, solid=solid, door=door)


def clock_tower(name=None):
    """Torre dell'Orologio (Faenza style): slender brick tower with a stone clock face and a small lantern (2x6)."""
    g = Px(32, 96)
    b = [C(214, 140, 99), C(189, 115, 82), C(156, 90, 66), C(115, 66, 49)]
    g.rect(6, 20, 20, 76, b[1])
    for y in range(20, 96, 4):
        g.hline(6, y, 20, b[2])
        for x in range(6 + (0 if (y // 4) % 2 else 4), 26, 8): g.vline(x, y + 1, 3, b[2])
    g.rect(4, 18, 24, 3, C(239, 222, 189)); g.rect(4, 56, 24, 2, C(239, 222, 189))
    g.rect(9, 0, 14, 4, b[3]); g.rect(11, 4, 10, 14, C(239, 222, 189)); g.rect(13, 7, 6, 9, C(57, 49, 49))   # lantern
    g.rect(15, 0, 2, 2, C(239, 189, 57))
    for a in range(32):
        import math
        x = 16 + round(7 * math.cos(a * math.pi / 16)); y = 33 + round(7 * math.sin(a * math.pi / 16))
        g.p(x, y, C(57, 49, 49))
    g.rect(11, 28, 10, 10, C(255, 251, 239)); g.rect(10, 29, 12, 8, C(255, 251, 239))
    g.vline(16, 28, 5, C(41, 41, 41)); g.hline(16, 33, 4, C(41, 41, 41))
    g.rect(12, 66, 8, 12, C(57, 41, 41)); g.hline(12, 65, 8, C(239, 222, 189))
    g.rect(10, 84, 12, 12, C(222, 206, 173)); g.rect(12, 86, 8, 10, C(99, 57, 41))
    g.outline()
    return dict(img=g.im, solid={(0, y) for y in range(6)} | {(1, y) for y in range(6)}, door=None)


def majolica_rack():
    """Rack of hand-painted Faenza majolica plates and jugs outside a workshop (2x1)."""
    g = Px(32, 16)
    g.rect(1, 12, 30, 3, C(140, 99, 66)); g.vline(2, 2, 12, C(140, 99, 66)); g.vline(29, 2, 12, C(140, 99, 66))
    cols = [(C(57, 99, 189), C(255, 255, 255)), (C(239, 189, 57), C(57, 140, 99)), (C(214, 57, 57), C(255, 239, 189)), (C(57, 140, 189), C(239, 189, 57))]
    for i, x in enumerate((7, 16, 25)):
        c1, c2 = cols[i % 4]
        for a in range(16):
            import math
            g.p(x + round(4 * math.cos(a * math.pi / 8)), 7 + round(4 * math.sin(a * math.pi / 8)), c1)
        g.rect(x - 2, 5, 5, 5, c2); g.p(x, 7, c1)
    g.outline()
    return dict(img=g.im, solid={(0, 0), (1, 0)}, door=None)


def pennants(n=4):
    """String of Palio del Niballo pennants (the five rioni colours), drawn over the street (top layer)."""
    g = Px(16 * n, 16)
    cols = [C(214, 41, 49), C(239, 206, 57), C(57, 140, 74), C(57, 99, 189), C(33, 33, 41)]
    for x in range(16 * n):
        y = 2 + int(2 * ((x % 32) / 16 - 1) ** 2)
        g.p(x, y, C(99, 82, 66))
    for i, x in enumerate(range(2, 16 * n - 4, 6)):
        c = cols[i % 5]
        for k in range(5):
            g.hline(x + k // 2, 4 + k, 4 - k // 1 if 4 - k > 0 else 1, c)
    return g.im


def _bricks(g, x0, y0, w, h, b, period=8):
    g.rect(x0, y0, w, h, b[1])
    for y in range(y0, y0 + h, 4):
        g.hline(x0, y, w, b[2])
        off = 0 if (y // 4) % 2 else period // 2
        for x in range(x0 + ((off - x0) % period), x0 + w, period):
            g.vline(x, y + 1, 3, b[2])


def _roof(g, x0, y0, w, h, r=None):
    """Simple tiled pitched roof seen from the front (trapezoid)."""
    r = r or [C(206, 107, 74), C(181, 90, 66), C(140, 66, 49)]
    for i in range(h):
        inset = (h - 1 - i) * w // (2 * h + 2)
        g.hline(x0 + inset, y0 + i, w - 2 * inset, r[0] if i % 3 else r[1])
    g.hline(x0, y0 + h - 1, w, r[2])


BRICK = [C(214, 140, 99), C(189, 115, 82), C(156, 90, 66), C(115, 66, 49)]


def san_vitale():
    """Basilica di San Vitale (VI c.): brick octagon with tiered tiled roofs and the drum, narthex front. 7x6."""
    W, H = 112, 96
    g = Px(W, H)
    _bricks(g, 24, 10, 64, 26, BRICK)                       # drum (upper octagon)
    _roof(g, 20, 0, 72, 12)
    for x in range(30, 84, 10): g.rect(x, 18, 4, 12, C(57, 49, 57)); g.hline(x, 17, 4, BRICK[0])   # drum windows
    _bricks(g, 6, 40, 100, 44, BRICK)                       # lower octagon
    _roof(g, 2, 32, 108, 10)
    for x in range(14, 100, 14): g.rect(x, 50, 5, 14, C(57, 49, 57)); g.hline(x, 49, 5, BRICK[0])  # arched windows
    for x in (6, 104): g.vline(x, 40, 44, BRICK[3])          # octagon edges
    for x in (34, 76): g.vline(x, 42, 42, BRICK[2])
    g.rect(40, 70, 32, 26, C(222, 206, 173)); _bricks(g, 42, 72, 28, 24, BRICK)  # narthex
    g.rect(50, 80, 12, 16, C(57, 41, 41)); g.hline(51, 79, 10, BRICK[0])
    g.outline()
    return dict(img=g.im, solid={(x, y) for x in range(7) for y in range(6)} - {(3, 5)}, door=(3, 5))


def galla_placidia():
    """Mausoleo di Galla Placidia: small Latin-cross brick building with a square central tower. 4x4."""
    W, H = 64, 64
    g = Px(W, H)
    _bricks(g, 22, 6, 20, 22, BRICK); _roof(g, 20, 0, 24, 8)
    _bricks(g, 4, 26, 56, 26, BRICK); _roof(g, 2, 20, 60, 8)
    _bricks(g, 18, 34, 28, 30, BRICK)
    for x in (8, 50): g.rect(x, 34, 4, 8, C(57, 49, 57))
    g.rect(28, 46, 8, 18, C(57, 41, 41)); g.hline(29, 45, 6, BRICK[0])
    g.outline()
    return dict(img=g.im, solid={(x, y) for x in range(4) for y in range(4)} - {(2, 3)}, door=(2, 3))


def apollinare():
    """Sant'Apollinare Nuovo: basilica facade with marble portico and the round (cylindrical) campanile. 7x6."""
    W, H = 112, 96
    g = Px(W, H)
    # round campanile on the left
    for y in range(0, 96):
        for x in range(22):
            dx = (x - 10.5) / 11
            col = BRICK[0] if dx < -0.4 else (BRICK[1] if dx < 0.5 else BRICK[2])
            if y % 4 == 0: col = BRICK[2]
            g.p(2 + x, y, col)
    for y in (12, 30, 48): g.rect(8, y, 3, 8, C(57, 49, 57)); g.rect(14, y, 3, 8, C(57, 49, 57))
    g.rect(1, 0, 24, 3, C(156, 90, 66))
    # nave facade
    _roof(g, 30, 20, 80, 18)
    _bricks(g, 32, 36, 76, 60, BRICK)
    g.rect(60, 44, 20, 6, C(57, 49, 57))                        # mullioned window
    g.rect(30, 66, 80, 30, C(239, 231, 214))                    # marble portico
    for x in range(34, 108, 12): g.rect(x, 70, 7, 26, C(206, 196, 173)); g.rect(x + 1, 70, 5, 26, C(222, 214, 196))
    g.hline(30, 66, 80, C(255, 251, 239)); g.rect(64, 76, 12, 20, C(57, 41, 41))
    g.outline()
    return dict(img=g.im, solid={(x, y) for x in range(7) for y in range(6)} - {(4, 5)}, door=(4, 5))


def dante_tomb():
    """Tomba di Dante: small neoclassical temple with a pediment and a little dome (1780). 3x4."""
    import math
    W, H = 48, 64
    g = Px(W, H)
    st = [C(247, 239, 222), C(231, 220, 198), C(206, 194, 170), C(165, 150, 126)]
    for i in range(8):                                                                               # low dome
        half = int(9 * math.sqrt(max(0, 1 - ((8 - i) / 8.0) ** 2))) + 2
        g.hline(24 - half, 2 + i, 2 * half, st[1] if i < 7 else st[3])
    g.rect(14, 0, 4, 2, st[2]) if False else None
    g.rect(6, 10, 36, 4, st[0])
    for i in range(10): g.hline(24 - 2 - 2 * i, 14 + i, 4 + 4 * i, st[0] if i < 9 else st[3])       # pediment
    g.rect(4, 24, 40, 40, st[1])
    for x in (6, 38): g.rect(x, 26, 4, 36, st[0]); g.vline(x + 3, 26, 36, st[3])
    g.rect(16, 36, 16, 28, st[2]); g.rect(18, 40, 12, 24, C(99, 66, 41))
    g.rect(20, 28, 8, 4, st[3])                                  # inscription
    g.outline()
    return dict(img=g.im, solid={(x, y) for x in range(3) for y in range(4)} - {(1, 3)}, door=(1, 3))


def teodorico():
    """Mausoleo di Teodorico: two-storey decagon in Istrian stone, deep arches below, monolithic dome with
    the ring of handles on top. 6x6."""
    W, H = 96, 96
    g = Px(W, H)
    st = [C(239, 231, 214), C(222, 212, 192), C(198, 188, 166), C(156, 146, 126), C(115, 106, 90)]
    # monolithic dome (flat) with the 12 handles
    import math
    for y in range(4, 19):                                     # shallow monolithic dome (lens)
        half = int(34 * math.sqrt(max(0, 1 - ((18 - y) / 14.0) ** 2)))
        g.hline(48 - half, y, 2 * half, st[0] if y < 9 else (st[1] if y < 15 else st[2]))
    for x in range(18, 80, 7): g.rect(x, 14, 3, 3, st[3]); g.p(x + 1, 13, st[2])   # the handles (small knobs)
    # upper storey
    g.rect(18, 18, 60, 26, st[1])
    for x in range(22, 76, 10): g.vline(x, 18, 26, st[2])
    g.rect(42, 24, 12, 18, C(57, 49, 49))
    g.rect(14, 44, 68, 4, st[0])
    # lower decagon with deep arches
    g.rect(6, 48, 84, 48, st[1])
    for x in range(10, 86, 16):
        g.rect(x, 58, 12, 38, st[3]); g.rect(x + 2, 60, 8, 36, C(66, 57, 49))
        for i in range(4): g.hline(x + 2 + i, 58 - i + 2, 8 - 2 * i, st[0])
    for x in range(6, 90, 16): g.vline(x, 48, 48, st[2])
    g.outline()
    return dict(img=g.im, solid={(x, y) for x in range(6) for y in range(6)} - {(3, 5)}, door=(3, 5))


def venetian_column(statue=C(214, 206, 189)):
    """One of the two Venetian columns of Piazza del Popolo (1483), statue on top. 1x4."""
    g = Px(16, 64)
    g.rect(5, 12, 6, 42, C(239, 231, 214)); g.vline(5, 12, 42, C(255, 251, 239)); g.vline(10, 12, 42, C(198, 188, 166))
    g.rect(3, 9, 10, 4, C(222, 212, 192))
    g.rect(6, 1, 4, 8, statue); g.rect(7, 0, 2, 2, statue)
    g.rect(2, 54, 12, 10, C(206, 196, 173)); g.hline(2, 54, 12, C(239, 231, 214))
    g.outline()
    return dict(img=g.im, solid={(0, 3)}, door=None)


def gas_platform(cw=8, ch=6, rocket=False):
    """Offshore platform off Ravenna (like the Adriatic gas rigs): steel deck on legs, crane, helipad;
    a launch tower with a white rocket on it (rocket=True) or the empty launch tower."""
    W, H = cw * 16, ch * 16
    g = Px(W, H)
    steel = [C(206, 214, 222), C(173, 181, 189), C(132, 140, 148), C(90, 99, 107)]
    for x in (8, W - 14, W // 2 - 3):
        g.rect(x, 56, 6, 40, steel[3]); g.vline(x, 56, 40, steel[2])
        for y in range(60, 96, 8): g.hline(x - 4, y, 14, steel[2])
    g.rect(0, 40, W, 18, steel[1]); g.hline(0, 40, W, steel[0]); g.rect(0, 54, W, 4, C(214, 173, 57))
    for x in range(0, W, 6): g.vline(x, 36, 4, steel[2])
    g.hline(0, 36, W, steel[2])
    # launch tower (red lattice) on the right
    tx = W - 40
    g.rect(tx, 0, 6, 40, C(198, 57, 49)); g.rect(tx + 18, 0, 6, 40, C(198, 57, 49))
    for y in range(2, 40, 6): g.hline(tx, y, 24, C(198, 57, 49))
    if rocket:
        g.rect(tx + 8, 4, 8, 34, C(247, 247, 247)); g.vline(tx + 8, 4, 34, C(255, 255, 255)); g.vline(tx + 15, 4, 34, C(206, 206, 214))
        for i in range(5): g.hline(tx + 12 - i, i, 2 * i if i else 1, C(214, 41, 49))
        g.rect(tx + 5, 30, 3, 8, C(214, 41, 49)); g.rect(tx + 16, 30, 3, 8, C(214, 41, 49))
        g.rect(tx + 9, 14, 6, 2, C(57, 99, 189))
    # crane and the control cabin
    g.rect(10, 18, 22, 22, C(239, 239, 235)); g.rect(13, 22, 16, 6, C(140, 189, 214))
    g.vline(40, 6, 34, C(239, 189, 57)); g.hline(40, 6, 30, C(239, 189, 57)); g.vline(69, 6, 8, steel[3])
    g.outline()
    return dict(img=g.im, solid={(x, y) for x in range(cw) for y in range(ch)}, door=None)


def motonave():
    """Ferry (motonave) moored in the Darsena: white hull with a blue band, two decks of windows, red funnel. 6x3."""
    W, H = 96, 48
    g = Px(W, H)
    for y in range(26, 44):
        inset = max(0, (y - 38)) * 2
        g.hline(4 + inset, y, W - 8 - inset - (y - 26) // 3, C(247, 247, 247))
    g.rect(4, 30, W - 12, 4, C(41, 82, 165)); g.rect(6, 40, W - 20, 4, C(173, 41, 49))
    g.rect(16, 14, 60, 12, C(239, 239, 235)); g.hline(16, 14, 60, C(255, 255, 255))
    for x in range(19, 74, 6): g.rect(x, 17, 4, 4, C(57, 99, 156))
    g.rect(28, 6, 34, 8, C(239, 239, 235))
    for x in range(31, 60, 6): g.rect(x, 8, 4, 3, C(57, 99, 156))
    g.rect(66, 0, 8, 14, C(214, 57, 49)); g.rect(66, 0, 8, 3, C(41, 41, 49))
    g.outline()
    return dict(img=g.im, solid={(x, y) for x in range(6) for y in range(3)}, door=None)


def islet_cave():
    """Rocky islet off Cesenatico with a dark cave mouth facing south (4x3); the mouth is cell (1..2, 2)."""
    W, H = 64, 48
    g = Px(W, H)
    import random
    rnd = random.Random(5)
    for y in range(H):
        for x in range(W):
            d = ((x - 32) / 31.0) ** 2 + ((y - 30) / 22.0) ** 2
            if d < 1:
                g.p(x, y, rnd.choice([C(132, 123, 107), C(148, 140, 123), C(115, 107, 94)]) if d > 0.25 or y < 22 else C(156, 148, 132))
    for y in range(26, 48):
        half = int(10 * min(1, (y - 25) / 8.0))
        g.hline(32 - half, y, 2 * half, C(24, 20, 24))
    for x in range(10, 54, 9): g.rect(x, 4 + (x % 4), 5, 3, C(99, 148, 82))
    g.outline()
    return dict(img=g.im, solid={(x, y) for x in range(4) for y in range(3)}, door=None)


def baracca_monument():
    """Monumento a Francesco Baracca (Lugo, 1936): a huge white stone wing rising behind the bronze statue
    of the pilot on a stepped base. 4x5."""
    W, H = 64, 80
    g = Px(W, H)
    st = [C(247, 243, 235), C(231, 225, 214), C(206, 198, 186), C(165, 156, 140)]
    for y in range(4, 66):                                      # the wing: tall, curved, tapering upwards
        t = (66 - y) / 62.0
        x0 = 14 + int(10 * t * t); x1 = 52 - int(4 * t)
        g.hline(x0, y, x1 - x0, st[1])
        g.p(x0, y, st[0]); g.p(x1 - 1, y, st[3])
        for k in range(x0 + 6, x1 - 2, 8): g.p(k, y, st[2]) if y % 6 == 0 else None
    for y in range(8, 64, 6):                                    # feathers
        g.hline(28, y, 20, st[2])
    g.rect(20, 66, 36, 14, st[2]); g.rect(16, 72, 44, 8, st[3]); g.hline(20, 66, 36, st[0])
    g.rect(32, 46, 8, 20, C(115, 90, 57)); g.rect(33, 40, 6, 7, C(140, 107, 66))      # bronze statue
    g.rect(31, 48, 10, 3, C(99, 74, 49))
    g.outline()
    return dict(img=g.im, solid={(x, y) for x in range(4) for y in range(5)}, door=None)


def arcade_row(cw=6, wall=None):
    """One side of the Pavaglione: a long Tuscan arcade with the tiled roof seen from the square (cw x 3)."""
    W, H = cw * 16, 48
    g = Px(W, H)
    wall = wall or [C(239, 206, 156), C(222, 181, 132), C(189, 148, 99), C(140, 107, 74)]
    r = [C(206, 107, 74), C(181, 90, 66), C(140, 66, 49)]
    for y in range(0, 14):
        g.hline(0, y, W, r[0] if y % 3 else r[1])
    g.hline(0, 13, W, r[2])
    g.rect(0, 14, W, 34, wall[1]); g.hline(0, 14, W, wall[0])
    for x in range(0, W, 16):
        g.rect(x + 3, 24, 10, 24, C(90, 66, 49))
        for i in range(4): g.hline(x + 3 + i, 23 - i // 2, 10 - 2 * i, C(90, 66, 49))
        g.rect(x, 22, 3, 26, wall[0]); g.rect(x + 13, 22, 3, 26, wall[0])
    for x in range(4, W, 16): g.rect(x, 16, 8, 4, C(140, 189, 214))
    g.outline()
    return dict(img=g.im, solid={(x, y) for x in range(cw) for y in (0, 1)}, door=None, top=1)


def plane_spad():
    """The SPAD VII with the cavallino rampante, as a museum sign/statue (2x2)."""
    g = Px(32, 32)
    g.rect(2, 12, 28, 4, C(156, 165, 115)); g.rect(2, 20, 28, 3, C(156, 165, 115))           # wings
    g.rect(13, 6, 6, 22, C(181, 189, 140)); g.rect(14, 2, 4, 4, C(99, 99, 107))              # fuselage, prop
    g.rect(15, 14, 3, 4, C(41, 41, 41))                                                       # cavallino
    g.rect(10, 26, 12, 3, C(132, 140, 99))
    g.outline()
    return dict(img=g.im, solid={(0, 1), (1, 1)}, door=None)


def grandstand(cw=8):
    """Grandstand of the Autodromo (cw x 3): tiers of coloured seats under a white cantilever roof."""
    W, H = cw * 16, 48
    g = Px(W, H)
    g.rect(0, 0, W, 6, C(239, 239, 235)); g.hline(0, 5, W, C(173, 173, 165))
    for x in range(4, W, 24): g.rect(x, 6, 3, 40, C(140, 148, 156))
    cols = [C(214, 41, 49), C(239, 206, 57), C(57, 99, 189)]
    for i, y in enumerate(range(10, 42, 6)):
        g.rect(0, y, W, 5, C(156, 156, 148))
        for x in range(1, W - 1, 4):
            g.rect(x, y + 1, 3, 3, cols[(i + x // 16) % 3])
    g.rect(0, 42, W, 6, C(132, 132, 124))
    g.outline()
    return dict(img=g.im, solid={(x, y) for x in range(cw) for y in range(3)}, door=None)


def track_tile(edges, finish=False):
    """Asphalt of the racetrack; red/white kerbs on the given edges ('n','s','w','e'), chequered finish line."""
    g = Px(16, 16)
    g.rect(0, 0, 16, 16, C(99, 99, 107))
    g.p(4, 7, C(115, 115, 123)); g.p(11, 3, C(115, 115, 123))
    for e in edges:
        for i in range(0, 16, 4):
            c1, c2 = C(214, 41, 49), C(247, 247, 247)
            if e == 'n': g.rect(i, 0, 2, 3, c1); g.rect(i + 2, 0, 2, 3, c2)
            if e == 's': g.rect(i, 13, 2, 3, c1); g.rect(i + 2, 13, 2, 3, c2)
            if e == 'w': g.rect(0, i, 3, 2, c1); g.rect(0, i + 2, 3, 2, c2)
            if e == 'e': g.rect(13, i, 3, 2, c1); g.rect(13, i + 2, 3, 2, c2)
    if finish:
        for y in range(0, 16, 4):
            for x in range(6, 10, 2):
                g.rect(x, y + (2 if (x // 2) % 2 else 0), 2, 2, C(247, 247, 247)); g.rect(x, y + (0 if (x // 2) % 2 else 2), 2, 2, C(24, 24, 24))
    return g.im


def snow_tile(x, y):
    g = Px(16, 16)
    g.rect(0, 0, 16, 16, C(239, 243, 251))
    rnd = random.Random((x * 3 + y * 5) % 4)
    for _ in range(5): g.p(rnd.randrange(16), rnd.randrange(16), rnd.choice([C(214, 222, 239), C(255, 255, 255)]))
    return g.im


def slab_tile(x, y):
    """Cleared street: grey sandstone slabs with snow in the joints."""
    g = Px(16, 16)
    g.rect(0, 0, 16, 16, C(165, 160, 156))
    g.hline(0, 0, 16, C(222, 226, 235)); g.vline(0 if (y % 2) else 8, 0, 16, C(222, 226, 235))
    g.p(4, 6, C(181, 176, 172)); g.p(11, 11, C(148, 143, 140))
    return g.im


def river_tile(x, y, w_edge, e_edge):
    g = Px(16, 16)
    g.rect(0, 0, 16, 16, C(66, 123, 189))
    if (x + y) % 3 == 0: g.hline(4, 5 + (y % 2) * 5, 6, C(140, 189, 239))
    if w_edge: g.rect(0, 0, 3, 16, C(239, 243, 251)); g.vline(3, 0, 16, C(115, 107, 99))
    if e_edge: g.rect(13, 0, 3, 16, C(239, 243, 251)); g.vline(12, 0, 16, C(115, 107, 99))
    return g.im


def stone_bridge_tile(x, y, edge):
    g = Px(16, 16)
    g.rect(0, 0, 16, 16, C(181, 173, 165)); g.hline(0, 4, 16, C(156, 148, 140)); g.hline(0, 10, 16, C(156, 148, 140))
    if edge == 'n': g.rect(0, 0, 16, 3, C(132, 123, 115)); g.hline(0, 0, 16, C(239, 243, 251))
    if edge == 's': g.rect(0, 13, 16, 3, C(132, 123, 115))
    return g.im


def snowy_fir():
    g = Px(16, 32)
    g.rect(7, 26, 2, 6, C(99, 66, 41))
    for i, (y, w) in enumerate(((2, 2), (6, 4), (10, 6), (14, 6), (18, 7), (22, 7))):
        g.rect(8 - w, y, 2 * w, 4, C(41, 99, 66) if i % 2 else C(57, 123, 82))
        g.rect(8 - w + 1, y, 2 * w - 2, 1, C(247, 251, 255))
    g.outline()
    return dict(img=g.im, solid={(0, 1)}, door=None)


def stone_house(cw=4, floors=2, door_cx=None, shutters=C(99, 140, 74)):
    """Appennine stone house: rough sandstone walls, snow-covered roof, wooden shutters, small balcony."""
    W = cw * 16; H = 16 + floors * 16 + 8
    H = (H + 15) // 16 * 16
    g = Px(W, H)
    roof_h = 14
    for i in range(roof_h):
        inset = (roof_h - 1 - i) // 2
        g.hline(inset, i, W - 2 * inset, C(247, 251, 255) if i < roof_h - 4 else C(214, 222, 239))
    g.hline(0, roof_h - 1, W, C(140, 132, 123))
    wy = roof_h
    g.rect(1, wy, W - 2, H - wy, C(189, 176, 156))
    rnd = random.Random(cw * 7 + floors)
    for y in range(wy + 2, H, 5):
        for x in range(2 + (y % 2) * 4, W - 4, 8):
            g.rect(x, y, 6, 3, rnd.choice([C(173, 160, 140), C(206, 194, 173), C(181, 168, 148)]))
    if door_cx is None: door_cx = cw // 2
    for f in range(floors):
        y = wy + 4 + f * 16
        for i in range(cw):
            if f == floors - 1 and i == door_cx: continue
            x = i * 16 + 4
            g.rect(x, y, 8, 9, C(57, 66, 82)); g.rect(x - 2, y, 2, 9, shutters); g.rect(x + 8, y, 2, 9, shutters)
            g.hline(x - 1, y + 9, 10, C(247, 251, 255))
    dx = door_cx * 16 + 3
    g.rect(dx, H - 14, 10, 14, C(115, 74, 41)); g.vline(dx + 5, H - 13, 13, C(90, 57, 33)); g.p(dx + 7, H - 7, C(239, 206, 99))
    g.outline()
    ch = H // 16
    solid = {(x, y) for x in range(cw) for y in range(ch)}; solid.discard((door_cx, ch - 1))
    return dict(img=g.im, solid=solid, door=(door_cx, ch - 1))


def palazzo_capitano(cw=7):
    """Palazzo del Capitano (Bagno di Romagna, XV c.): Florentine stone facade full of coats of arms,
    arched portal, small loggia windows, snow on the roof ledge."""
    W, H = cw * 16, 80
    g = Px(W, H)
    g.rect(0, 0, W, 8, C(247, 251, 255)); g.hline(0, 8, W, C(140, 132, 123))
    g.rect(2, 9, W - 4, H - 9, C(214, 200, 173))
    for y in range(12, H, 6): g.hline(2, y, W - 4, C(198, 184, 156))
    for x in range(8, W - 8, 14):
        g.rect(x, 14, 8, 12, C(57, 66, 82)); g.hline(x - 1, 13, 10, C(239, 231, 214))
    for i, x in enumerate(range(6, W - 10, 11)):                         # coats of arms of the captains
        cols = [(C(214, 41, 49), C(239, 206, 57)), (C(57, 99, 189), C(255, 255, 255)), (C(57, 140, 74), C(239, 206, 57))][i % 3]
        g.rect(x, 34, 7, 8, cols[0]); g.rect(x + 2, 36, 3, 4, cols[1]); g.hline(x + 1, 42, 5, cols[0]); g.p(x + 3, 43, cols[0])
    dx = W // 2 - 8
    g.rect(dx, 52, 16, 28, C(239, 231, 214)); g.rect(dx + 2, 56, 12, 24, C(90, 57, 33))
    for i in range(4): g.hline(dx + 2 + i, 55 - i, 12 - 2 * i, C(90, 57, 33))
    g.outline()
    return dict(img=g.im, solid={(x, y) for x in range(cw) for y in range(5)} - {(cw // 2, 4)}, door=(cw // 2, 4))


def terme(cw=7):
    """Terme di Bagno di Romagna: long warm-coloured spa building with a glazed hall and steam rising."""
    W, H = cw * 16, 80
    g = Px(W, H)
    for y in range(0, 14):
        inset = (13 - y) // 2
        g.hline(inset, y, W - 2 * inset, C(247, 251, 255) if y < 10 else C(214, 222, 239))
    g.rect(1, 14, W - 2, H - 14, C(239, 206, 156)); g.hline(1, 14, W - 2, C(255, 231, 189))
    for x in range(6, W - 6, 14): g.rect(x, 20, 9, 12, C(57, 82, 115)); g.rect(x + 1, 21, 3, 4, C(173, 214, 239))
    g.rect(W // 2 - 26, 40, 52, 40, C(115, 156, 189))
    for x in range(W // 2 - 24, W // 2 + 26, 6): g.vline(x, 42, 38, C(206, 231, 247))
    signboard(g, W // 2, 34, 'TERME', bg=C(255, 255, 255), fg=C(57, 99, 156))
    g.rect(W // 2 - 7, 64, 14, 16, C(41, 66, 99))
    for (x, y) in ((10, 2), (W - 16, 4), (W // 2 + 30, 0)):                        # steam
        for k in range(4): g.rect(x + (k % 2) * 2, y + k * 3, 5, 3, C(255, 255, 255))
    g.outline()
    return dict(img=g.im, solid={(x, y) for x in range(cw) for y in range(5)} - {(cw // 2, 4)}, door=(cw // 2, 4))


def thermal_pool(w=5, h=3):
    """Outdoor thermal pool with warm turquoise water and steam (solid)."""
    g = Px(16 * w, 16 * h)
    g.rect(0, 0, 16 * w, 16 * h, C(165, 160, 156))
    g.rect(4, 4, 16 * w - 8, 16 * h - 8, C(99, 189, 189)); g.rect(4, 4, 16 * w - 8, 3, C(57, 156, 165))
    for x in range(10, 16 * w - 10, 14):
        for k in range(3): g.rect(x + k % 2, 6 + k * 4, 6, 3, C(239, 247, 251))
    return dict(img=g.im, solid={(x, y) for x in range(w) for y in range(h)}, door=None)


def stone_church(cw=6):
    """Basilica di Santa Maria Assunta: sandstone church with a bell tower, snow on the roofs."""
    W, H = cw * 16, 96
    g = Px(W, H)
    tx = W - 22
    g.rect(tx, 8, 18, 88, C(189, 176, 156)); g.rect(tx, 4, 18, 5, C(247, 251, 255))
    g.rect(tx + 5, 16, 8, 10, C(57, 49, 49)); g.rect(tx + 7, 40, 4, 8, C(57, 49, 49))
    for i in range(20):
        inset = (19 - i) * (W - 26) // 44
        g.hline(inset, 24 + i, W - 24 - 2 * inset, C(247, 251, 255) if i < 16 else C(214, 222, 239))
    g.rect(2, 44, W - 26, 52, C(206, 194, 173))
    for y in range(48, 96, 6): g.hline(2, y, W - 26, C(189, 176, 156))
    cx = (W - 22) // 2
    for a in range(24):
        import math
        g.p(cx + round(6 * math.cos(a * math.pi / 12)), 54 + round(6 * math.sin(a * math.pi / 12)), C(123, 107, 90))
    g.rect(cx - 6, 72, 12, 24, C(90, 57, 33))
    g.outline()
    ch = H // 16
    door = (cx // 16, ch - 1)
    return dict(img=g.im, solid={(x, y) for x in range(cw) for y in range(ch)} - {door}, door=door)


def tribuna(cw=14):
    """Main grandstand of the Ippodromo del Savio: white cantilever roof, tiers with spectators, glazed base. cw x 5."""
    W, H = cw * 16, 80
    g = Px(W, H)
    for y in range(0, 14):
        g.hline(0, y, W, C(247, 247, 243) if y < 10 else C(206, 206, 198))
    for x in range(0, W, 32): g.vline(x + 2, 0, 14, C(214, 214, 206))
    for x in range(8, W, 40): g.rect(x, 14, 4, 50, C(156, 156, 148))
    rnd = random.Random(19)
    for i, y in enumerate(range(16, 56, 5)):
        g.rect(0, y, W, 4, C(181, 181, 173)); g.hline(0, y + 4, W, C(140, 140, 132))
        for x in range(2, W - 2, 3):
            if rnd.random() < 0.55:
                g.rect(x, y + 1, 2, 2, rnd.choice([C(214, 57, 57), C(57, 99, 189), C(239, 206, 57), C(255, 255, 255), C(57, 140, 74)]))
    g.rect(0, 56, W, 24, C(206, 214, 222))
    for x in range(4, W - 4, 12): g.rect(x, 60, 9, 18, C(115, 156, 189)); g.p(x + 1, 61, C(222, 239, 255))
    signboard(g, W // 2, 64, 'IPPODROMO DEL SAVIO', bg=C(255, 255, 255), fg=C(41, 82, 140))
    g.outline()
    return dict(img=g.im, solid={(x, y) for x in range(cw) for y in range(5)}, door=None)


def judges_tower():
    g = Px(32, 64)
    g.rect(6, 20, 20, 44, C(239, 239, 235)); g.vline(6, 20, 44, C(255, 255, 255)); g.vline(25, 20, 44, C(198, 198, 189))
    g.rect(2, 4, 28, 18, C(57, 82, 115)); g.rect(4, 7, 24, 10, C(173, 214, 239)); g.rect(0, 2, 32, 4, C(214, 57, 49))
    g.rect(12, 50, 8, 14, C(99, 66, 41))
    g.outline()
    return dict(img=g.im, solid={(x, y) for x in range(2) for y in range(4)}, door=None)


def totalizzatore(cw=4):
    """Totalisator board in the infield: black board with lit numbers and the odds."""
    W, H = cw * 16, 32
    g = Px(W, H)
    g.rect(2, 2, W - 4, 20, C(24, 24, 33)); g.rect(2, 2, W - 4, 3, C(57, 99, 156))
    rnd = random.Random(7)
    for y in (7, 12, 17):
        for x in range(5, W - 6, 6):
            g.rect(x, y, 4, 3, rnd.choice([C(255, 206, 57), C(255, 255, 255), C(255, 107, 49)]))
    for x in (8, W - 10): g.rect(x, 22, 3, 10, C(132, 140, 148))
    g.outline()
    return dict(img=g.im, solid={(x, 1) for x in range(cw)} | {(x, 0) for x in range(cw)}, door=None)


def scuderie(cw=8):
    """Stables: long low building with horse boxes, green split doors, a horse looking out."""
    W, H = cw * 16, 48
    g = Px(W, H)
    for y in range(0, 14):
        g.hline(0, y, W, C(181, 90, 66) if y % 3 else C(156, 74, 57))
    g.hline(0, 13, W, C(115, 57, 41))
    g.rect(0, 14, W, 34, C(239, 222, 189))
    for i, x in enumerate(range(4, W - 10, 14)):
        g.rect(x, 22, 11, 26, C(57, 115, 74)); g.rect(x, 22, 11, 10, C(41, 41, 41)); g.hline(x, 32, 11, C(41, 82, 57))
        if i % 3 == 1:
            g.rect(x + 3, 23, 5, 8, C(140, 90, 57)); g.rect(x + 4, 22, 3, 2, C(99, 57, 33))   # horse head
    g.outline()
    return dict(img=g.im, solid={(x, y) for x in range(cw) for y in range(3)}, door=None)


def panama21():
    """Caffè Panama as in 0.21: a three-storey 1960s block (cream walls, terracotta pilasters, long
    balconies), the white canopy with the black PANAMA sign, the terrace with chairs and potted palms.
    Drawn on the 8/16 px grid so the repeated bays share their tiles."""
    cw, chh = 9, 8
    W, H = cw * 16, chh * 16
    g = Px(W, H)
    cream = [C(255, 247, 222), C(239, 222, 189), C(214, 189, 148), C(173, 148, 107)]
    terra = [C(214, 115, 74), C(189, 90, 57), C(148, 66, 41)]
    grey = [C(222, 222, 214), C(189, 189, 181), C(140, 140, 132), C(90, 90, 90)]
    x0, x1 = 8, W - 8                        # front face; side faces in perspective
    top = 24
    # roof slab and the rooftop box
    g.rect(96, 12, 24, 12, cream[1]); g.rect(100, 15, 8, 6, grey[2]); g.hline(96, 12, 24, cream[0])
    g.rect(x0 - 4, top, x1 - x0 + 8, 8, grey[0]); g.hline(x0 - 4, top, x1 - x0 + 8, C(255, 255, 255))
    g.hline(x0 - 4, top + 7, x1 - x0 + 8, grey[2])
    # side faces
    for sx in (x0 - 6, x1):
        g.rect(sx, top + 8, 6, 64, cream[2])
        g.rect(sx + 1, top + 12, 4, 56, terra[2])
    # two floors of 32 px: terracotta pilasters every 32 px, windows between, a long balcony slab
    for f in range(2):
        fy = top + 8 + f * 32
        g.rect(x0, fy, x1 - x0, 32, cream[1])
        for bx in range(x0, x1, 32):
            g.rect(bx, fy, 8, 32, terra[1]); g.vline(bx + 7, fy, 32, terra[2])
            # window with dark frame
            g.rect(bx + 12, fy + 4, 16, 12, grey[3]); g.rect(bx + 13, fy + 5, 14, 10, C(82, 99, 115))
            g.vline(bx + 20, fy + 5, 10, grey[3]); g.p(bx + 14, fy + 6, C(173, 189, 206))
            g.rect(bx + 3, fy + 7, 2, 2, C(255, 255, 255))         # round vent on the pilaster
            g.hline(bx + 8, fy, 24, cream[2])                         # shadow under the slab above
        # balcony: cream slab with a shadow and a parapet
        g.rect(x0 - 4, fy + 18, x1 - x0 + 8, 10, cream[0])
        g.hline(x0 - 4, fy + 18, x1 - x0 + 8, C(255, 255, 255))
        for xx in range(x0 - 4, x1 + 4, 4):
            g.p(xx, fy + 21, cream[1])
        g.hline(x0 - 4, fy + 24, x1 - x0 + 8, cream[2])
        g.rect(x0 - 4, fy + 28, x1 - x0 + 8, 4, cream[3])
    # canopy: white sloping awning over the whole terrace
    cy = top + 72
    g.rect(0, cy - 2, W, 12, C(247, 247, 239))
    g.hline(0, cy - 2, W, C(255, 255, 255)); g.hline(0, cy + 8, W, grey[1]); g.hline(0, cy + 9, W, grey[2])
    for xx in range(0, W, 16):
        g.vline(xx, cy - 1, 9, grey[0])
    g.rect(32, cy - 2, 80, 11, C(16, 16, 16))
    text(g, 72 - text_width('PANAMA') // 2, cy, 'PANAMA', C(255, 255, 255))
    # terrace: glazed bar behind, columns, chairs and tables, potted palms at the ends
    ty = cy + 10
    g.rect(4, ty, W - 8, H - ty - 2, C(66, 82, 99))
    for gx in range(8, W - 8, 16):
        g.rect(gx, ty + 2, 12, 10, C(115, 140, 165)); g.p(gx + 2, ty + 3, C(189, 206, 222))
    g.rect(64, ty, 16, H - ty - 2, C(57, 66, 74)); g.rect(66, ty + 2, 12, H - ty - 4, C(140, 165, 189))
    g.vline(72, ty + 2, H - ty - 4, C(57, 66, 74))
    for px_ in range(0, W, 48):
        g.vline(px_ + 2, cy + 10, H - cy - 12, grey[0])
    for tx in (16, 32, 96, 112):
        g.rect(tx + 4, H - 9, 8, 2, C(239, 239, 239)); g.vline(tx + 7, H - 7, 4, grey[2])
        for chx in (tx + 1, tx + 12):
            g.rect(chx, H - 8, 3, 5, C(165, 99, 57)); g.hline(chx, H - 9, 3, C(115, 66, 41))
    for ppx in (2, W - 14):
        g.rect(ppx + 3, H - 8, 6, 6, C(140, 74, 49))
        for k in range(5):
            g.hline(ppx + k, H - 13 + k // 2 - (k % 2) * 2, 12 - 2 * k if k < 3 else 4, C(66, 115, 57))
        g.rect(ppx + 2, H - 16, 8, 6, C(82, 140, 66))
    g.rect(0, H - 2, W, 2, grey[1])
    g.outline()
    solid = {(x, y) for x in range(cw) for y in range(chh)}
    solid.discard((4, chh - 1))
    return dict(img=g.im, solid=solid, door=(4, chh - 1))


def arengo():
    """Palazzo dell'Arengo (Rimini, 1204): red-brick communal palace with a ghibelline crown of merlons,
    gothic three-light windows on the upper floor and the great pointed arches of the portico below.
    Bays on a 48 px period so the four bays share their tiles; door under the second arch."""
    cw, chh = 12, 7
    W, H = cw * 16, chh * 16
    g = Px(W, H)
    br = [C(222, 132, 99), C(198, 107, 74), C(165, 82, 57), C(123, 57, 41)]
    stone = PAL['stone']
    top = 12
    # merlons (swallow-tail) on a 16 px period
    for x in range(0, W, 16):
        g.rect(x + 2, top - 10, 12, 10, br[1])
        g.rect(x + 6, top - 10, 4, 4, (0, 0, 0, 0)) if False else None
        g.rect(x + 7, top - 10, 2, 4, None) if False else None
    for x in range(0, W, 16):
        for yy in range(4):
            g.hline(x + 7 - yy // 2, top - 10 + yy, 2 + yy, None) if False else None
    img = g.im; px = img.load()
    for x in range(0, W, 16):                     # cut the swallow tail notch
        for yy in range(5):
            for xx in range(x + 6 + yy // 2, x + 10 - yy // 2):
                px[xx, top - 10 + yy] = (0, 0, 0, 0)
        for yy in range(10):
            px[x + 13, top - 10 + yy] = br[3] + (255,) if isinstance(br[3], tuple) and len(br[3]) == 3 else px[x + 13, top - 10 + yy]
    g.rect(0, top, W, 4, br[2]); g.hline(0, top + 3, W, br[3])       # corbel band
    # brick wall with 4 px courses
    g.rect(0, top + 4, W, H - top - 4, br[1])
    for yy in range(top + 8, H, 4):
        g.hline(0, yy, W, br[2])
    for yy in range(top + 6, H, 8):
        for xx in range(0, W, 8):
            g.p(xx + (4 if (yy // 4) % 2 else 0), yy, br[0])
    centers = [24 + 48 * k for k in range(4)]
    # upper floor: gothic three-light windows (trifore) with white stone frames
    wy = top + 14
    for cx in centers:
        g.rect(cx - 13, wy - 2, 26, 22, stone[1])
        for k in (-8, 0, 8):
            g.rect(cx + k - 3, wy + 2, 6, 15, C(57, 49, 57))
            g.p(cx + k - 3, wy + 2, stone[1]); g.p(cx + k + 2, wy + 2, stone[1])
            g.hline(cx + k - 2, wy + 1, 4, C(57, 49, 57))
        g.hline(cx - 13, wy + 18, 26, stone[0]); g.hline(cx - 13, wy + 19, 26, stone[2])
        g.rect(cx - 2, wy - 6, 4, 4, stone[0])       # small oculus above
    # string course between the floors
    g.rect(0, top + 40, W, 3, stone[1]); g.hline(0, top + 42, W, stone[2])
    # portico: great pointed arches with the shaded loggia behind
    ay = top + 46
    for cx in centers:
        half = 19
        for yy in range(ay, H - 2):
            d = yy - ay
            hw = half if d >= 14 else int(half * (0.35 + 0.65 * (d / 14) ** 0.5))
            g.hline(cx - hw, yy, 2 * hw, C(82, 57, 49))
            if d < 14:
                g.p(cx - hw - 1, yy, stone[1]); g.p(cx + hw, yy, stone[1])
        g.rect(cx - half, H - 14, 2 * half, 12, C(66, 49, 41))
        for xx in range(cx - half + 4, cx + half - 4, 8):
            g.vline(xx, H - 14, 12, C(90, 66, 57))
    # door at the back of the second arch
    dcx = centers[1]
    g.rect(dcx - 6, H - 18, 12, 16, PAL['wood'][2]); g.rect(dcx - 5, H - 17, 10, 15, PAL['wood'][1])
    g.vline(dcx, H - 17, 15, PAL['wood'][3])
    g.rect(0, H - 2, W, 2, stone[2])
    g.outline()
    solid = {(x, y) for x in range(cw) for y in range(chh)}
    door = (dcx // 16, chh - 1)
    solid.discard(door)
    return dict(img=g.im, solid=solid, door=door)
