"""Cervia interiors drawn by hand: MUSA - Museo del Sale (34,11) in the Magazzino Torre, and the
Palazzo Comunale (34,8). Events are kept from the ROM (same order), only moved."""
import sys, random
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import interior as I
from interior import Room
from art import Px, C, PAL
from lido_int import set_walls, set_floor, objs_of, warps_of, bgs_of, big_plant, frame
import r22


# ------------------------------------------------------------------ tiles
def brick_wall_top(x):
    """Magazzino del sale: exposed brick under the dark timber trusses."""
    g = Px(16, 16)
    g.rect(0, 0, 16, 16, PAL['brick'][1])
    for y in range(6, 16, 3):
        g.hline(0, y, 16, PAL['brick'][2])
        o = 0 if (y // 3) % 2 else 4
        for xx in range(o, 16, 8):
            g.vline(xx, y - 2, 2, PAL['brick'][2])
    g.rect(0, 0, 16, 5, C(90, 57, 41)); g.hline(0, 5, 16, C(57, 33, 24))
    if x % 4 == 0:
        g.rect(6, 0, 4, 16, C(99, 66, 49)); g.vline(6, 0, 16, C(132, 90, 66))          # truss post
    return g.im


def brick_wall_low(x):
    g = Px(16, 16)
    g.rect(0, 0, 16, 16, PAL['brick'][1])
    for y in range(2, 13, 3):
        g.hline(0, y, 16, PAL['brick'][2])
        o = 0 if (y // 3) % 2 else 4
        for xx in range(o, 16, 8):
            g.vline(xx, y - 2, 2, PAL['brick'][2])
    g.rect(0, 13, 16, 3, C(206, 198, 181)); g.hline(0, 13, 16, C(239, 231, 214))
    if x % 4 == 0:
        g.rect(6, 0, 4, 13, C(99, 66, 49)); g.vline(6, 0, 13, C(132, 90, 66))
    return g.im


def museum_floor(x, y):
    """Old warehouse floor: wide worn planks with salt dust."""
    g = Px(16, 16)
    g.rect(0, 0, 16, 16, C(181, 148, 107))
    for yy in (0, 8):
        g.hline(0, yy, 16, C(140, 107, 74))
    g.vline((x * 5 + y * 3) % 16, 1, 7, C(140, 107, 74)); g.vline((x * 5 + y * 3 + 8) % 16, 9, 7, C(140, 107, 74))
    rnd = random.Random(x * 31 + y)
    for _ in range(3):
        g.p(rnd.randrange(16), rnd.randrange(16), C(231, 222, 206))
    return g.im


def palazzo_wall_top(x):
    """Town hall: cream stucco, coffered ceiling cornice."""
    g = Px(16, 16)
    g.rect(0, 0, 16, 16, C(247, 231, 198))
    g.rect(0, 0, 16, 5, C(222, 198, 156)); g.hline(0, 5, 16, C(173, 140, 99))
    for xx in range(0, 16, 8):
        g.rect(xx + 1, 1, 6, 3, C(239, 222, 181))
    return g.im


def palazzo_wall_low(x):
    g = Px(16, 16)
    g.rect(0, 0, 16, 16, C(247, 231, 198))
    g.rect(0, 7, 16, 9, C(140, 49, 49)); g.hline(0, 7, 16, C(198, 165, 99)); g.hline(0, 15, 16, C(99, 33, 33))  # damask wainscot
    for xx in (4, 12):
        g.p(xx, 10, C(173, 74, 66)); g.p(xx, 12, C(173, 74, 66))
    return g.im


def marble_floor(x, y):
    g = Px(16, 16)
    light, dark = C(239, 235, 222), C(173, 165, 156)
    g.rect(0, 0, 16, 16, light if (x + y) % 2 == 0 else C(206, 198, 189))
    g.hline(0, 0, 16, dark); g.vline(0, 0, 16, dark)
    rnd = random.Random(x * 13 + y * 7)
    for _ in range(2):
        a, b_ = rnd.randrange(14), rnd.randrange(14)
        g.p(a, b_, C(222, 214, 206)); g.p(a + 1, b_ + 1, C(222, 214, 206))
    return g.im


def red_runner(x, y):
    g = Px(16, 16)
    g.rect(0, 0, 16, 16, C(173, 41, 49)); g.vline(1, 0, 16, C(222, 181, 82)); g.vline(14, 0, 16, C(222, 181, 82))
    g.p(7, (y * 5) % 16, C(198, 74, 74))
    return g.im


# ------------------------------------------------------------------ museum furniture
def vitrine(kind='crystals'):
    """Glass display case on a wooden plinth (2x2)."""
    g = Px(32, 32)
    g.rect(1, 18, 30, 12, C(99, 66, 49)); g.hline(1, 18, 30, C(140, 99, 66))
    g.rect(2, 3, 28, 15, C(206, 231, 239)); g.hline(2, 3, 28, C(255, 255, 255)); g.vline(2, 3, 15, C(255, 255, 255))
    if kind == 'crystals':
        for (x, y) in ((6, 10), (12, 8), (19, 11), (24, 9)):
            g.rect(x, y, 4, 5, C(255, 255, 255)); g.p(x + 1, y + 1, C(214, 222, 231)); g.p(x + 3, y + 4, C(189, 198, 206))
    elif kind == 'jars':
        for i, x in enumerate(range(5, 27, 6)):
            g.rect(x, 9, 4, 7, C(239, 239, 247)); g.rect(x, 12, 4, 4, [C(255, 255, 255), C(239, 173, 181), C(206, 198, 189), C(255, 247, 222)][i % 4])
            g.hline(x, 8, 4, C(132, 99, 66))
    else:   # documents
        g.rect(5, 8, 10, 7, C(247, 239, 206)); g.rect(17, 7, 10, 8, C(239, 222, 189))
        for yy in (10, 12): g.hline(6, yy, 8, C(140, 132, 115)); g.hline(18, yy, 8, C(140, 132, 115))
    g.outline()
    return dict(img=g.im, solid={(0, 0), (1, 0), (0, 1), (1, 1)})


def tools_rack():
    """Wall rack with the salinari's wooden tools: rakes (gaveri), shovels, the 'rodabla'."""
    g = Px(48, 32)
    g.rect(1, 4, 46, 3, C(99, 66, 49))
    for i, x in enumerate(range(5, 44, 8)):
        g.vline(x, 5, 24, C(165, 123, 82)); g.vline(x + 1, 5, 24, C(132, 99, 66))
        if i % 2 == 0:
            g.rect(x - 3, 26, 8, 3, C(165, 123, 82))                         # rake head
            for t in range(x - 3, x + 5, 2): g.p(t, 29, C(132, 99, 66))
        else:
            g.rect(x - 2, 24, 6, 6, C(140, 132, 115))                        # shovel blade
    g.outline()
    return dict(img=g.im, solid={(0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1)})


def burchiella():
    """The 'burchiella': flat wooden barge that carried the salt along the canals (4x2)."""
    g = Px(64, 32)
    g.rect(4, 10, 56, 14, C(140, 99, 66)); g.hline(4, 10, 56, C(181, 140, 99)); g.hline(4, 23, 56, C(99, 66, 49))
    for i in range(4): g.hline(2 - i // 2, 11 + i * 3, 2, C(140, 99, 66)); g.hline(60, 11 + i * 3, 2, C(140, 99, 66))
    g.rect(8, 6, 48, 6, C(255, 255, 255)); g.rect(14, 3, 36, 4, C(247, 247, 239))                # cargo of salt
    for x in range(10, 56, 9): g.p(x, 8, C(222, 222, 214))
    g.rect(2, 24, 60, 6, C(206, 198, 181))                                                         # display plinth
    g.outline()
    return dict(img=g.im, solid={(a, b) for a in range(4) for b in range(2)})


def diorama():
    """Scale model of the salt pans under glass (3x2)."""
    g = Px(48, 32)
    g.rect(1, 20, 46, 10, C(99, 66, 49))
    g.rect(2, 4, 44, 16, C(156, 123, 90))
    for (x, y, w, h, c) in ((4, 6, 12, 6, C(156, 189, 206)), (18, 6, 12, 6, C(239, 173, 181)), (32, 6, 12, 6, C(247, 247, 239)),
                            (4, 13, 19, 5, C(140, 206, 198)), (25, 13, 19, 5, C(239, 173, 181))):
        g.rect(x, y, w, h, c)
    g.rect(36, 7, 3, 3, C(255, 255, 255))
    g.hline(2, 4, 44, C(239, 247, 255)); g.vline(2, 4, 16, C(239, 247, 255))
    g.outline()
    return dict(img=g.im, solid={(a, b) for a in range(3) for b in range(2)})


def salt_sacks():
    g = Px(32, 16)
    for x in (1, 11, 21):
        g.rect(x, 3, 10, 12, C(222, 206, 173)); g.hline(x, 3, 10, C(239, 231, 206)); g.hline(x + 2, 8, 6, C(132, 99, 66))
    g.outline()
    return dict(img=g.im, solid={(0, 0), (1, 0)})


def photo(c=C(156, 148, 132)):
    g = Px(16, 16)
    g.rect(2, 2, 12, 10, C(57, 41, 33)); g.rect(3, 3, 10, 8, C(214, 206, 189))
    g.rect(4, 7, 8, 3, c); g.rect(6, 4, 2, 3, C(99, 90, 82)); g.rect(9, 5, 2, 2, C(99, 90, 82))   # sepia salinari
    g.outline()
    return g.im


def panel(title_c=C(41, 99, 140)):
    g = Px(16, 16)
    g.rect(1, 1, 14, 13, C(247, 247, 239)); g.rect(1, 1, 14, 3, title_c)
    for yy in (6, 8, 10): g.hline(3, yy, 10, C(156, 156, 148))
    g.outline()
    return g.im


def salt_mound():
    g = Px(32, 32)
    for y in range(6, 30):
        half = (y - 4) * 14 // 26
        g.hline(16 - half, y, 2 * half, C(255, 255, 255) if y < 20 else C(231, 231, 222))
    g.rect(2, 28, 28, 3, C(132, 99, 66))
    g.outline()
    return dict(img=g.im, solid={(0, 0), (1, 0), (0, 1), (1, 1)})


# ------------------------------------------------------------------ town hall furniture
def flags():
    """Italian and European flags on poles (1x2)."""
    g = Px(16, 32)
    for x, cols in ((3, (C(57, 140, 74), C(255, 255, 255), C(206, 49, 57))), (10, None)):
        g.vline(x, 2, 28, C(198, 165, 82))
        if cols:
            for i, c in enumerate(cols): g.rect(x + 1 + i * 2, 4, 2, 9, c)
        else:
            g.rect(x + 1, 4, 5, 9, C(41, 66, 173)); g.p(x + 3, 6, C(255, 222, 57)); g.p(x + 3, 10, C(255, 222, 57)); g.p(x + 2, 8, C(255, 222, 57))
    g.rect(1, 28, 14, 3, C(132, 99, 66))
    g.outline()
    return dict(img=g.im, solid={(0, 1)})


def council_desk(w=3):
    """Dark walnut desk of the Sala del Consiglio, with microphones and nameplates."""
    g = Px(16 * w, 32)
    g.rect(1, 8, 16 * w - 2, 10, C(99, 57, 41)); g.hline(1, 8, 16 * w - 2, C(140, 90, 57))
    g.rect(1, 18, 16 * w - 2, 10, C(74, 41, 33))
    for x in range(6, 16 * w - 6, 14):
        g.vline(x, 3, 6, C(66, 66, 66)); g.p(x, 3, C(41, 41, 41))                                   # microphone
        g.rect(x + 3, 6, 6, 3, C(239, 231, 206))                                                     # nameplate
    g.outline()
    return dict(img=g.im, solid={(a, b) for a in range(w) for b in range(2)})


def throne_chair():
    g = Px(16, 32)
    g.rect(3, 2, 10, 14, C(140, 41, 49)); g.rect(5, 4, 6, 10, C(173, 57, 66)); g.hline(3, 2, 10, C(222, 181, 82))
    g.rect(2, 16, 12, 6, C(140, 41, 49)); g.vline(3, 22, 8, C(99, 57, 41)); g.vline(12, 22, 8, C(99, 57, 41))
    g.outline()
    return dict(img=g.im, solid={(0, 0), (0, 1)})


def office_counter(w=4):
    """Front office counter (Ufficio Anagrafe / URP) with a glass screen, ticket display."""
    g = Px(16 * w, 32)
    W = 16 * w
    g.rect(0, 12, W, 18, C(206, 198, 181)); g.hline(0, 12, W, C(239, 231, 214)); g.hline(0, 29, W, C(156, 148, 132))
    g.rect(0, 2, W, 10, C(214, 239, 247)); g.hline(0, 2, W, C(255, 255, 255))
    for x in range(0, W, 16): g.vline(x, 2, 10, C(173, 189, 198))
    for x in range(6, W - 4, 16):
        g.rect(x, 15, 6, 4, C(255, 255, 255)); g.hline(x, 17, 6, C(156, 156, 148))           # forms
    g.outline()
    return dict(img=g.im, solid={(a, b) for a in range(w) for b in range(2)})


def ticket_display():
    g = Px(16, 16)
    g.rect(1, 3, 14, 8, C(33, 33, 41)); g.rect(3, 5, 4, 4, C(255, 66, 57)); g.rect(9, 5, 4, 4, C(255, 66, 57))
    g.outline()
    return g.im


def bench_row(w=3):
    g = Px(16 * w, 16)
    g.rect(1, 3, 16 * w - 2, 6, C(140, 99, 66)); g.hline(1, 3, 16 * w - 2, C(181, 140, 99))
    g.rect(1, 9, 16 * w - 2, 3, C(99, 66, 49))
    for x in (3, 16 * w - 5): g.vline(x, 12, 3, C(66, 49, 41))
    g.outline()
    return dict(img=g.im, solid={(a, 0) for a in range(w)})


def stemma():
    """Coat of arms of Cervia (blue and white shield under a crown)."""
    g = Px(16, 16)
    g.rect(4, 1, 8, 2, C(239, 189, 57))
    g.rect(3, 3, 10, 9, C(255, 255, 255)); g.rect(3, 3, 5, 9, C(57, 99, 173))
    for i in range(3): g.hline(5 + i, 12 + i, 6 - 2 * i, C(57, 99, 173) if i == 0 else C(255, 255, 255))
    g.outline()
    return g.im


def archive_shelf(w=2):
    g = Px(16 * w, 32)
    g.rect(1, 1, 16 * w - 2, 29, C(99, 66, 49))
    rnd = random.Random(w + 11)
    for yy in (3, 12, 21):
        g.hline(2, yy + 8, 16 * w - 4, C(140, 99, 66))
        for x in range(3, 16 * w - 4, 4):
            g.rect(x, yy, 3, 8, rnd.choice([C(57, 74, 140), C(140, 41, 49), C(206, 189, 132), C(66, 115, 74)]))
    g.outline()
    return dict(img=g.im, solid={(a, b) for a in range(w) for b in range(2)})


def grand_stairs():
    """Marble staircase to the first floor (2x2, solid: decorative)."""
    g = Px(32, 32)
    for i in range(8):
        g.rect(2 + i, 2 + i * 3, 28 - 2 * i, 3, C(239, 235, 222) if i % 2 else C(214, 206, 196))
    g.vline(1, 2, 28, C(132, 99, 66)); g.vline(30, 2, 28, C(132, 99, 66))
    g.rect(10, 14, 12, 16, C(173, 41, 49))
    g.outline()
    return dict(img=g.im, solid={(0, 0), (1, 0), (0, 1), (1, 1)})


# ------------------------------------------------------------------ rooms
def musa(gn=(34, 11)):
    W, H = 20, 14
    r = Room(W, H, gn, floor='planks', wall='brick', wall_rows=2)
    set_walls(r, brick_wall_top, brick_wall_low)
    set_floor(r, museum_floor)
    ws = warps_of(gn)
    r.void([(x, H - 1) for x in range(W) if x != 10])
    r.exit_mat(10, H - 1, ws[0]['group'], ws[0]['num'], ws[0]['warp'])
    r.art[H - 1][10] = (museum_floor(10, H - 1), None, 0, 0x65, False)
    # back wall: panels and old photographs of the salinari, the tools rack
    for x in (2, 6, 13, 17):
        r.furn(x, 0, photo())
    for x in (4, 15):
        r.furn(x, 1, panel())
    r.furn(8, 0, tools_rack())
    # the burchiella in the middle, the diorama of the pans, cases of salt crystals and jars
    r.furn(8, 4, burchiella())
    r.furn(2, 3, vitrine('crystals'))
    r.furn(15, 3, vitrine('jars'))
    r.furn(2, 7, diorama())
    r.furn(15, 7, vitrine('docs'))
    r.furn(9, 8, salt_mound())
    r.furn(13, 10, salt_sacks())
    r.furn(5, 10, salt_sacks())
    r.furn(1, 10, big_plant()) if False else None
    o = objs_of(gn)
    for oo, (x, y) in zip(o, [(6, 6), (4, 11), (12, 7), (18, 11)]):
        oo['x'], oo['y'] = x, y
    r.objs = o
    b = bgs_of(gn)
    for bb, (x, y) in zip(b, [(4, 1), (15, 1)]):
        bb['x'], bb['y'] = x, y
    r.bbgs = b
    return r


def municipio(gn=(34, 8)):
    W, H = 20, 14
    r = Room(W, H, gn, floor='tiles', wall='plaster', wall_rows=2)
    set_walls(r, palazzo_wall_top, palazzo_wall_low)
    set_floor(r, marble_floor)
    ws = warps_of(gn)
    r.void([(x, H - 1) for x in range(W) if x != 10])
    r.exit_mat(10, H - 1, ws[0]['group'], ws[0]['num'], ws[0]['warp'])
    r.art[H - 1][10] = (marble_floor(10, H - 1), None, 0, 0x65, False)
    for y in range(4, H - 1):                                   # red carpet from the door to the stairs
        for x in (10,):
            r.art[y][x] = (red_runner(x, y), None, 0, 0, False)
    # centre: grand staircase with the coat of arms and the flags
    r.furn(9, 2, grand_stairs())
    r.furn(9, 0, stemma()); r.furn(10, 0, frame(C(99, 156, 206), C(99, 165, 82)))
    r.furn(8, 2, flags()); r.furn(11, 2, flags())
    # left: Sala del Consiglio (council desks in a horseshoe, the mayor's chair, portraits)
    r.furn(3, 2, throne_chair())
    r.furn(2, 4, council_desk(3))
    r.furn(1, 7, council_desk(2)); r.furn(5, 7, council_desk(2))
    r.furn(1, 0, frame(C(140, 115, 90), C(198, 165, 132))); r.furn(5, 0, frame(C(140, 115, 90), C(198, 165, 132)))
    r.furn(1, 10, bench_row(3))
    # right: Ufficio Anagrafe / URP counter, ticket display, archives, waiting benches
    r.furn(13, 2, office_counter(4), top_rows=1)
    r.furn(14, 1, ticket_display())
    r.furn(17, 2, archive_shelf(2))
    r.furn(13, 7, bench_row(3)); r.furn(13, 9, bench_row(3))
    r.furn(18, 9, big_plant())
    r.furn(7, 11, big_plant()) if False else r.furn(6, 10, big_plant())
    r.furn(13, 0, I.window_art('plaster', C(140, 41, 49))); r.furn(17, 0, I.window_art('plaster', C(140, 41, 49)))
    o = objs_of(gn)
    for oo, (x, y) in zip(o, [(4, 3), (15, 2), (4, 9), (16, 11), (8, 6)]):
        oo['x'], oo['y'] = x, y
    r.objs = o
    b = bgs_of(gn)
    if b:
        b[0]['x'], b[0]['y'] = 12, 1          # notice board / sign
    r.bbgs = b
    for x in range(13, 17):                   # clerk behind the counter
        a = r.art[3][x]; r.art[3][x] = (a[0], a[1], 1, 0x80, a[4])
    return r


ALL = [('musa', musa, (34, 11)), ('municipio', municipio, (34, 8))]


def side_wall():
    g = Px(16, 16)
    g.rect(0, 0, 16, 16, C(239, 222, 189)); g.vline(0, 0, 16, C(206, 189, 156)); g.vline(15, 0, 16, C(206, 189, 156))
    g.rect(0, 10, 16, 6, C(181, 132, 90)); g.hline(0, 10, 16, C(214, 165, 115))
    return g.im


def side_exit(floor_img, east):
    g = floor_img.copy()
    p = Px(16, 16)
    p.rect(2, 2, 12, 12, C(165, 57, 49)); p.rect(3, 3, 10, 10, C(198, 82, 66))
    ax = 10 if east else 5
    for i in range(3):                                   # arrow pointing to the exit
        p.vline(ax + (i if east else -i), 6 + i, 5 - 2 * i, C(255, 231, 156))
    g.alpha_composite(p.im)
    return g


def flamingo_poster():
    g = Px(16, 16)
    g.rect(2, 1, 12, 14, C(206, 231, 247)); g.rect(2, 10, 12, 5, C(239, 173, 181))
    g.vline(8, 6, 7, C(198, 57, 99)); g.rect(6, 5, 5, 3, C(239, 115, 140)); g.p(6, 3, C(239, 115, 140)); g.p(6, 4, C(239, 115, 140))
    g.outline()
    return g.im


def gate(gn, cervia_warp, saline_warp, guard_script):
    """Varco delle Saline: east door -> Cervia, west door -> Saline."""
    W, H = 12, 7
    r = Room(W, H, gn, floor='tiles', wall='ochre', wall_rows=2)
    r.objs, r.bwarps, r.bcoords, r.bbgs = [], [], [], []
    set_floor(r, marble_floor)
    r.void([(x, H - 1) for x in range(W)])
    for y in range(2, H - 1):
        for x in (0, W - 1):
            r.art[y][x] = (side_wall(), None, 1, 0, False)
    ey = 4
    r.art[ey][W - 1] = (side_exit(marble_floor(W - 1, ey), True), None, 0, 0x62, False)
    r.art[ey][0] = (side_exit(marble_floor(0, ey), False), None, 0, 0x63, False)
    r.bwarps.append(dict(x=W - 1, y=ey, elev=0, warp=cervia_warp[2], num=cervia_warp[1], group=cervia_warp[0]))
    r.bwarps.append(dict(x=0, y=ey, elev=0, warp=saline_warp[2], num=saline_warp[1], group=saline_warp[0]))
    r.furn(4, 2, office_counter(4), top_rows=1)
    for x in range(4, 8):
        a = r.art[3][x]; r.art[3][x] = (a[0], a[1], 1, 0x80, a[4])
    r.furn(2, 0, flamingo_poster()); r.furn(9, 0, flamingo_poster())
    r.furn(5, 0, I.window_art('ochre', C(57, 99, 165)))
    r.furn(1, 2, big_plant()); r.furn(10, 2, big_plant())
    r.furn(2, 5, bench_row(2)) if False else None
    r.add_obj(6, 2, 22, guard_script, move=8)
    r.void_cell = (0, H - 1)
    return r


# ------------------------------------------------------------------ Cervia water gym (2,1)
def aqua_floor(x, y):
    g = Px(16, 16)
    g.rect(0, 0, 16, 16, C(222, 247, 247))
    for yy in range(0, 16, 4):
        for xx in range(0, 16, 4):
            if (xx // 4 + yy // 4 + x + y) % 5 == 0:
                g.rect(xx, yy, 4, 4, C(173, 231, 231))
    g.hline(0, 0, 16, C(189, 222, 222)); g.vline(0, 0, 16, C(189, 222, 222))
    return g.im


def teak_floor(x, y):
    g = Px(16, 16)
    g.rect(0, 0, 16, 16, C(198, 148, 99))
    for yy in (3, 7, 11, 15):
        g.hline(0, yy, 16, C(156, 107, 66))
    g.vline((x * 6 + y) % 16, 0, 16, C(173, 123, 82))
    return g.im


def gym_wall_top(x):
    g = Px(16, 16)
    g.rect(0, 0, 16, 16, C(57, 140, 189))
    for i in range(16):                                    # white wave frieze
        g.p(i, 6 + (1 if (i + x * 16) // 4 % 2 else 0), C(255, 255, 255))
        g.p(i, 9 + (0 if (i + x * 16) // 4 % 2 else 1), C(173, 222, 239))
    g.rect(0, 0, 16, 3, C(33, 99, 140))
    if x % 4 == 2:
        g.rect(4, 11, 8, 5, C(206, 239, 255)); g.vline(8, 11, 5, C(57, 140, 189))   # porthole window
    return g.im


def gym_wall_low(x):
    g = Px(16, 16)
    for yy in range(0, 16, 4):
        for xx in range(0, 16, 4):
            g.rect(xx, yy, 4, 4, C(115, 189, 222) if (xx + yy) // 4 % 2 else C(140, 206, 231))
    g.rect(0, 13, 16, 3, C(255, 255, 255))
    return g.im


def gym_side(x):
    g = Px(16, 16)
    g.rect(0, 0, 16, 16, C(57, 140, 189)); g.vline(0 if x == 0 else 15, 0, 16, C(33, 99, 140))
    for yy in range(2, 16, 4): g.hline(2, yy, 12, C(99, 173, 214))
    return g.im


def pool_tile(kind, n, e, s, w, var):
    c = {'salt': [C(99, 206, 222), C(66, 173, 206), C(41, 140, 181)], 'pink': [C(231, 165, 189), C(214, 132, 165), C(181, 99, 140)],
         'chan': [C(74, 156, 214), C(57, 132, 198), C(41, 99, 165)]}[kind]
    g = Px(16, 16)
    g.rect(0, 0, 16, 16, c[0])
    if var == 1: g.hline(3, 5, 6, c[1]); g.hline(8, 11, 5, c[1])
    if var == 2: g.hline(7, 3, 5, c[1]); g.p(4, 10, C(255, 255, 255))
    if n: g.rect(0, 0, 16, 3, C(255, 255, 255)); g.hline(0, 3, 16, c[2])
    if s: g.rect(0, 13, 16, 3, C(255, 255, 255))
    if w: g.rect(0, 0, 3, 16, C(255, 255, 255)); g.vline(3, 0, 16, c[2])
    if e: g.rect(13, 0, 3, 16, C(255, 255, 255))
    return g.im


def lane_rope(img):
    g = img.copy(); p = Px(16, 16)
    for xx in range(0, 16, 4): p.rect(xx, 7, 2, 2, C(239, 57, 57)); p.rect(xx + 2, 7, 2, 2, C(255, 255, 255))
    g.alpha_composite(p.im)
    return g


def valve_wheel():
    g = Px(16, 16)
    g.rect(6, 10, 4, 6, C(140, 140, 148))
    for a in range(16):
        import math
        x = 8 + round(5 * math.cos(a * math.pi / 8)); y = 7 + round(5 * math.sin(a * math.pi / 8))
        g.p(x, y, C(214, 41, 49))
    g.hline(3, 7, 11, C(214, 41, 49)); g.vline(8, 2, 11, C(214, 41, 49)); g.rect(7, 6, 3, 3, C(140, 140, 148))
    g.outline()
    return g.im


def lifebuoy():
    g = Px(16, 16)
    for a in range(24):
        import math
        for rr in (4, 5, 6):
            x = 8 + round(rr * math.cos(a * math.pi / 12)); y = 8 + round(rr * math.sin(a * math.pi / 12))
            g.p(x, y, C(255, 255, 255) if (a // 3) % 2 else C(239, 57, 57))
    g.outline()
    return g.im


def gym_statue():
    g = Px(16, 32)
    g.rect(3, 20, 10, 11, C(206, 206, 214)); g.hline(3, 20, 10, C(239, 239, 247))
    g.rect(4, 6, 8, 14, C(239, 189, 74)); g.rect(5, 3, 6, 4, C(239, 189, 74)); g.p(6, 4, C(41, 41, 41)); g.p(9, 4, C(41, 41, 41))
    g.rect(6, 12, 4, 4, C(57, 140, 189))                 # wave badge
    g.outline()
    return dict(img=g.im, solid={(0, 0), (0, 1)})


def bridge_open():
    g = Px(16, 16)
    g.rect(0, 0, 16, 16, C(198, 148, 99))
    for x in range(0, 16, 4): g.vline(x, 0, 16, C(156, 107, 66))
    g.hline(0, 0, 16, C(132, 90, 57)); g.hline(0, 15, 16, C(132, 90, 57))
    return g.im


def water_gym(gn=(2, 1)):
    W, H = 24, 28
    r = Room(W, H, gn, floor='tiles', wall='blue', wall_rows=2, keep_events=True)
    set_walls(r, gym_wall_top, gym_wall_low)
    set_floor(r, aqua_floor)
    for y in range(2, 8):                                   # leader's teak deck
        for x in range(1, W - 1):
            r.art[y][x] = (teak_floor(x, y), None, 0, 0, False)
    for y in range(2, H - 1):
        for x in (0, W - 1):
            r.art[y][x] = (gym_side(x), None, 1, 0, False)
    r.void([(x, H - 1) for x in range(W)])
    r.void_cell = (0, H - 1)
    ws = r.bwarps
    r.bwarps = []
    r.exit_mat(12, 26, ws[0]['group'], ws[0]['num'], ws[0]['warp'])
    r.art[26][12] = (r.art[26][12][0], None, 0, 0x65, False)
    # channel across the hall (row 8) with the sluice in the middle (bridge cells 10..13)
    for x in range(1, W - 1):
        img = pool_tile('chan', True, False, True, False, x % 3)
        r.art[8][x] = (img, None, 1, 0, False)
    # two saltwater pools with lane ropes
    for (x0, x1, kind) in ((2, 9, 'salt'), (15, 22, 'pink')):
        for y in range(10, 19):
            for x in range(x0, x1):
                img = pool_tile(kind, y == 10, x == x1 - 1, y == 18, x == x0, (x + y) % 3)
                if y in (13, 16) and x0 < x < x1 - 1:
                    img = lane_rope(img)
                r.art[y][x] = (img, None, 1, 0, False)
    # decoration
    r.furn(5, 3, gym_statue()); r.furn(18, 3, gym_statue())
    for x in (2, 21):
        r.furn(x, 2, big_plant())
    for x in (3, 20):
        r.furn(x, 0, lifebuoy())
    for (x, y) in ((1, 20), (22, 20), (2, 24), (21, 24)):
        r.furn(x, y, big_plant())
    for (x, y) in ((4, 19), (20, 19)):                       # the two valves (signs of the puzzle)
        base = r.art[y][x][0].copy(); base.alpha_composite(valve_wheel())
        r.art[y][x] = (base, None, 1, 0, False)
    r.bopen = bridge_open()
    return r
