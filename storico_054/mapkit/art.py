"""Procedural pixel art for Romagna buildings and props, in the Gen 3 overworld style.

Every asset returns an RGBA image whose size is a multiple of 16, plus metadata:
  solid  : set of (cx, cy) cells that block movement
  top    : set of cells whose pixels go to the top layer (drawn over the player)
  door   : (cx, cy) of the entrance cell, if any
"""
import random
from PIL import Image, ImageDraw

OUT = (49, 41, 49)          # outline


def C(*v):
    return tuple(v)


PAL = dict(
    roof=[C(239, 156, 115), C(214, 115, 82), C(181, 82, 66), C(132, 57, 49), C(99, 41, 41)],
    roof_brown=[C(206, 148, 107), C(173, 115, 82), C(140, 82, 66), C(107, 57, 49), C(74, 41, 41)],
    ochre=[C(255, 239, 181), C(247, 214, 140), C(222, 181, 107), C(181, 140, 82)],
    pink=[C(255, 222, 206), C(247, 189, 173), C(222, 156, 140), C(181, 115, 107)],
    brick=[C(231, 140, 107), C(206, 107, 82), C(165, 82, 66), C(123, 57, 49)],
    cream=[C(255, 247, 222), C(239, 231, 198), C(214, 198, 165), C(165, 148, 123)],
    peach=[C(255, 214, 165), C(247, 189, 132), C(222, 156, 99), C(173, 115, 74)],
    green_sh=[C(132, 206, 123), C(82, 165, 90), C(49, 115, 66), C(33, 74, 49)],
    brown_sh=[C(173, 123, 82), C(132, 90, 57), C(99, 66, 41), C(66, 41, 33)],
    glass=[C(222, 239, 255), C(156, 206, 247), C(99, 156, 222), C(66, 107, 173)],
    wood=[C(206, 156, 99), C(165, 115, 66), C(123, 82, 49), C(82, 57, 33)],
    stone=[C(231, 231, 222), C(198, 198, 189), C(156, 156, 148), C(115, 115, 115)],
    leaf=[C(156, 222, 107), C(99, 189, 82), C(57, 148, 66), C(33, 99, 57), C(24, 66, 41)],
    pine=[C(123, 189, 99), C(74, 148, 74), C(41, 107, 66), C(24, 74, 57), C(16, 49, 41)],
    bark=[C(181, 123, 82), C(140, 90, 57), C(99, 66, 41), C(66, 41, 33)],
    shadow=C(0, 0, 0, 60),
)


class Px:
    def __init__(self, w, h):
        self.im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        self.px = self.im.load()
        self.w, self.h = w, h

    def p(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h and c is not None:
            if len(c) == 4 and c[3] < 255:
                r, g, b, a = self.px[x, y]
                if a == 0:
                    return
                k = c[3] / 255.0
                self.px[x, y] = (int(r * (1 - k)), int(g * (1 - k)), int(b * (1 - k)), 255)
            else:
                self.px[x, y] = c[:3] + (255,)

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.p(xx, yy, c)

    def hline(self, x, y, w, c):
        self.rect(x, y, w, 1, c)

    def vline(self, x, y, h, c):
        self.rect(x, y, 1, h, c)

    def sprite(self, x, y, rows, cmap):
        for yy, row in enumerate(rows):
            for xx, ch in enumerate(row):
                if ch in cmap and cmap[ch] is not None:
                    self.p(x + xx, y + yy, cmap[ch])

    def outline(self, c=OUT, open_sides=''):
        """Draw an outline around opaque pixels (inside the bounds). open_sides: image borders that continue."""
        src = self.im.copy().load()
        for y in range(self.h):
            for x in range(self.w):
                if src[x, y][3] == 0:
                    continue
                edge = False
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if not (0 <= nx < self.w and 0 <= ny < self.h):
                        side = 'E' if nx >= self.w else 'W' if nx < 0 else 'S' if ny >= self.h else 'N'
                        if side not in open_sides:
                            edge = True
                    elif src[nx, ny][3] == 0:
                        edge = True
                if edge:
                    self.px[x, y] = c + (255,)


# ---------------------------------------------------------------- buildings

def window(g, x, y, wall, shutters=PAL['green_sh'], open_=False, tall=10):
    """A window with shutters, 12 px wide (3+6+3)."""
    gl = PAL['glass']
    # frame
    g.rect(x + 3, y, 6, tall, wall[0])
    g.rect(x + 4, y + 1, 4, tall - 2, gl[2])
    g.hline(x + 4, y + 1, 4, gl[3])
    g.p(x + 4, y + 2, gl[0]); g.p(x + 5, y + 2, gl[1]); g.p(x + 4, y + 3, gl[1])
    g.vline(x + 6, y + 1, tall - 2, wall[1])
    g.hline(x + 3, y + tall - 1, 6, wall[3])
    g.hline(x + 2, y + tall, 8, wall[0])  # sill
    g.hline(x + 2, y + tall + 1, 8, wall[3])
    # shutters
    if shutters:
        for sx in (x, x + 9):
            g.rect(sx, y, 3, tall, shutters[1])
            for yy in range(y + 1, y + tall, 2):
                g.hline(sx, yy, 3, shutters[2])
            g.vline(sx + (0 if sx == x else 2), y, tall, shutters[3])


def coppi_roof(g, x, y, w, h, roof, ridge=True, hip=True):
    """Terracotta hip roof at 3/4 view: a front trapezoid of curved tiles and two darker side faces."""
    r = roof
    slope = 0.9
    for yy in range(h):
        inset = int(round((h - 1 - yy) * slope)) if hip else 0
        inset = min(inset, w // 2 - 4)
        shade = yy / max(1, h - 1)
        for xx in range(w):
            band = (yy + 1) % 4
            if xx < inset or xx >= w - inset:
                # side faces: darker, diagonal courses
                d = (xx + yy) if xx < inset else (w - xx + yy)
                c = r[2] if (d // 2) % 2 == 0 else r[3]
                if band == 0:
                    c = r[3]
                g.p(x + xx, y + yy, c)
                continue
            col = ((x + xx) // 4) % 2
            if band == 0:
                c = r[3]
            elif band == 1:
                c = r[0] if col == 0 else r[1]
            else:
                c = r[1] if col == 0 else r[2]
            if (x + xx) % 4 == 3 and band != 0:
                c = r[2] if band == 1 else r[3]
            if shade > 0.75 and band != 0 and c == r[0]:
                c = r[1]
            g.p(x + xx, y + yy, c)
        if hip and 0 < inset < w // 2 - 4:
            g.p(x + inset, y + yy, r[4])
            g.p(x + w - 1 - inset, y + yy, r[4])
    if ridge:
        ins = min(int(round((h - 1) * slope)), w // 2 - 4) if hip else 0
        g.hline(x + ins, y, w - 2 * ins, r[4])
        g.hline(x + ins + 1, y + 1, w - 2 * ins - 2, r[0])
    # eaves / gutter
    g.hline(x, y + h, w, r[4])
    g.hline(x, y + h + 1, w, (74, 57, 57))


def wall_fill(g, x, y, w, h, wall, seed=0):
    g.rect(x, y, w, h, wall[1])
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            k = (xx % 8, yy % 8)
            if k in ((1, 2), (5, 6), (6, 1)):
                g.p(xx, yy, wall[2])
            elif k == (3, 5):
                g.p(xx, yy, wall[0])
    g.vline(x, y, h, wall[0])
    g.vline(x + w - 1, y, h, wall[2])


def door(g, x, y, kind='wood', w=10, h=15, arch=False):
    wd = PAL['wood']
    g.rect(x, y, w, h, wd[2])
    g.rect(x + 1, y + 1, w - 2, h - 1, wd[1])
    g.vline(x + w // 2, y + 1, h - 1, wd[3])
    for yy in (y + 3, y + 8):
        g.hline(x + 2, yy, w // 2 - 3, wd[0])
        g.hline(x + w // 2 + 2, yy, w // 2 - 3, wd[0])
    g.p(x + w // 2 - 2, y + h // 2 + 1, (247, 214, 107))
    if arch:
        g.hline(x + 1, y - 1, w - 2, OUT)
        g.p(x, y, OUT); g.p(x + w - 1, y, OUT)
    g.hline(x - 1, y + h, w + 2, PAL['stone'][2])


def house(cw=5, floors=2, wall='ochre', roof='roof', shutters='green_sh', door_cx=None, balcony=False,
          seed=1, sign=None, chimney=True, plinth=True):
    """Two-storey Romagnol house. cw = width in cells. Height = 2 (roof) + floors cells."""
    W = cw * 16
    roof_h = 24
    wall_h = floors * 16 + 8
    H = ((roof_h + wall_h + 15) // 16) * 16
    g = Px(W, H)
    wl = PAL[wall]
    rf = PAL[roof]
    top = H - wall_h - roof_h
    # chimney
    if chimney:
        cx = W - 22
        g.rect(cx, top - 2, 7, 12, PAL['brick'][1])
        g.rect(cx, top - 4, 7, 3, PAL['brick'][3])
        g.vline(cx + 6, top - 2, 12, PAL['brick'][2])
    coppi_roof(g, 1, top, W - 2, roof_h - 2, rf)
    wy = top + roof_h
    wall_fill(g, 2, wy, W - 4, wall_h, wl, seed)
    if plinth:
        g.rect(2, H - 4, W - 4, 4, PAL['stone'][2])
        g.hline(2, H - 4, W - 4, PAL['stone'][1])
    # windows
    if door_cx is None:
        door_cx = cw // 2
    # one window per cell, aligned to the 16 px grid: identical cells share their tiles (tileset budget)
    slots = [c * 16 + 2 for c in range(cw)]
    sh = PAL[shutters] if shutters else None
    for f in range(floors):
        fy = wy + 4 + f * 16
        for c, sx in enumerate(slots):
            if f == floors - 1 and c == door_cx:
                continue
            window(g, sx, fy, wl, sh)
        if balcony and f == 0 and floors > 1:
            bx = door_cx * 16 + 1
            g.rect(bx, fy + 11, 14, 2, PAL['stone'][1])
            for xx in range(bx, bx + 14, 2):
                g.vline(xx, fy + 7, 4, OUT)
            g.hline(bx, fy + 7, 14, OUT)
    # door on the ground floor
    dx = door_cx * 16 + 3
    door(g, dx, H - 17, w=10, h=13)
    if sign:
        g.rect(dx - 6, H - 22, 22, 4, PAL['cream'][0])
        g.hline(dx - 6, H - 23, 22, OUT)
    g.outline()
    cells_h = H // 16
    solid = {(x, y) for x in range(cw) for y in range(cells_h)}
    solid.discard((door_cx, cells_h - 1))
    return dict(img=g.im, solid=solid, door=(door_cx, cells_h - 1), top=set(), w=cw, h=cells_h)


def portici(cw=6, floors=2, wall='brick', roof='roof', seed=3, door_cx=None, arches=None):
    """Palazzo with an arcade (portico) on the ground floor."""
    W = cw * 16
    wall_h = floors * 16 + 4
    H = ((18 + wall_h + 15) // 16) * 16
    roof_h = H - wall_h
    g = Px(W, H)
    wl, rf = PAL[wall], PAL[roof]
    top = H - wall_h - roof_h
    coppi_roof(g, 1, top, W - 2, roof_h - 2, rf)
    wy = top + roof_h
    wall_fill(g, 1, wy, W - 2, wall_h, wl, seed)
    # upper floors windows
    for f in range(floors - 1):
        for i in range(cw):
            window(g, i * 16 + 2, wy + 3 + f * 16, wl, PAL['green_sh'], tall=9)
    # arcade
    ay = H - 18
    g.rect(1, ay, W - 2, 18, wl[2])
    for i in range(cw):
        x = i * 16
        # pillar
        g.rect(x + 1, ay, 3, 18, wl[0])
        g.vline(x + 3, ay, 18, wl[2])
        # arch opening
        g.rect(x + 4, ay + 5, 10, 13, (66, 49, 49))
        g.rect(x + 5, ay + 4, 8, 1, (66, 49, 49))
        g.rect(x + 6, ay + 3, 6, 1, (66, 49, 49))
        g.rect(x + 4, ay + 12, 10, 6, (90, 66, 57))
        g.vline(x + 4, ay + 5, 13, (49, 33, 33))
    g.outline()
    cells_h = H // 16
    if door_cx is None:
        door_cx = cw // 2
    solid = {(x, y) for x in range(cw) for y in range(cells_h)}
    solid.discard((door_cx, cells_h - 1))
    return dict(img=g.im, solid=solid, door=(door_cx, cells_h - 1), top=set(), w=cw, h=cells_h)


# ---------------------------------------------------------------- vegetation

def umbrella_pine(ground=None):
    """2x2 pine (pino domestico): flat dark canopy, thin reddish trunk. Returns 4 cells."""
    g = Px(32, 32)
    pn = PAL['pine']
    rnd = random.Random(7)
    # canopy ellipse
    cx, cy, rx, ry = 16, 9, 15, 8
    for y in range(32):
        for x in range(32):
            d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
            if d <= 1.0:
                c = pn[2]
                if y < cy - 3 and d < 0.7:
                    c = pn[1]
                if y > cy + 3:
                    c = pn[3]
                g.p(x, y, c)
    # clumps texture
    for _ in range(70):
        x, y = rnd.randrange(3, 29), rnd.randrange(2, 16)
        if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 < 0.8:
            g.p(x, y, pn[0] if y < cy else pn[2])
            g.p(x + 1, y, pn[1] if y < cy else pn[3])
    # trunk
    bk = PAL['bark']
    g.rect(14, 16, 4, 14, bk[1])
    g.vline(14, 16, 14, bk[0])
    g.vline(17, 16, 14, bk[2])
    g.rect(12, 28, 8, 2, bk[2])
    g.outline()
    # canopy underside shadow on trunk
    for x in range(14, 18):
        g.p(x, 17, (66, 41, 33))
    return g.im


def round_tree(colors='leaf', fruit=None, seed=3):
    """1x2 small tree (orchard/garden) 16x32."""
    g = Px(16, 32)
    lf = PAL[colors]
    rnd = random.Random(seed)
    for y in range(32):
        for x in range(16):
            d = ((x - 7.5) / 7.5) ** 2 + ((y - 11) / 10) ** 2
            if d <= 1:
                c = lf[2]
                if y < 8:
                    c = lf[1]
                if y < 5 and d < 0.5:
                    c = lf[0]
                if y > 16:
                    c = lf[3]
                g.p(x, y, c)
    for _ in range(25):
        x, y = rnd.randrange(2, 14), rnd.randrange(3, 19)
        if ((x - 7.5) / 7.5) ** 2 + ((y - 11) / 10) ** 2 < 0.75:
            g.p(x, y, lf[0] if y < 10 else lf[2])
    if fruit:
        for _ in range(9):
            x, y = rnd.randrange(3, 13), rnd.randrange(5, 18)
            if ((x - 7.5) / 7.5) ** 2 + ((y - 11) / 10) ** 2 < 0.6:
                g.p(x, y, fruit)
                g.p(x, y + 1, tuple(max(0, v - 50) for v in fruit))
    bk = PAL['bark']
    g.rect(6, 20, 4, 10, bk[1])
    g.vline(6, 20, 10, bk[0])
    g.vline(9, 20, 10, bk[2])
    g.outline()
    return g.im


# ---------------------------------------------------------------- beach

UMBRELLA_COLS = {
    'red': (C(239, 74, 66), C(189, 41, 49)),
    'blue': (C(74, 140, 239), C(41, 90, 189)),
    'yellow': (C(255, 214, 66), C(222, 156, 33)),
    'green': (C(99, 206, 115), C(49, 148, 74)),
    'orange': (C(255, 156, 66), C(214, 107, 33)),
}


def ombrellone(color='red'):
    """Beach umbrella with a sun lounger, 16x32 (top cell = canopy over the player)."""
    g = Px(16, 32)
    a, b = UMBRELLA_COLS[color]
    w = C(255, 255, 255)
    # canopy: octagon seen from above at an angle
    rows = [
        "....xxxxxxxx....",
        "..xxaawwaawwxx..",
        ".xaaawwwaaawwwx.",
        "xaaaawwwaaawwwax",
        "xaaaawwwaaawwwax",
        "xbbbbvvvbbbvvvbx",
        ".xbbbvvvbbbvvbx.",
        "..xxxxxxxxxxxx..",
    ]
    g.sprite(0, 4, rows, {'x': OUT, 'a': a, 'b': b, 'w': w, 'v': C(214, 214, 222)})
    # pole
    g.rect(7, 12, 2, 12, C(222, 222, 222))
    g.vline(8, 12, 12, C(156, 156, 165))
    # lounger (lettino)
    lt = [
        "..xxxxxxxxxx..",
        "..xccccccccx..",
        "..xddddddddx..",
        "..xx......xx..",
    ]
    g.sprite(1, 25, lt, {'x': OUT, 'c': C(255, 255, 255), 'd': a})
    return g.im


def cabina(color='blue'):
    """Beach hut, 16x32."""
    g = Px(16, 32)
    a, b = UMBRELLA_COLS[color]
    w = C(255, 255, 255)
    # roof
    g.rect(1, 6, 14, 5, C(239, 239, 239))
    g.hline(1, 6, 14, C(198, 198, 198))
    g.hline(0, 11, 16, C(156, 156, 165))
    # stripes body
    for x in range(1, 15):
        g.vline(x, 12, 18, a if (x // 2) % 2 == 0 else w)
    g.rect(5, 16, 6, 14, b)
    g.p(9, 23, C(255, 239, 107))
    g.outline()
    return g.im


def kiosk(text_color=(214, 66, 57)):
    """Piadina kiosk 32x32 with striped awning."""
    g = Px(32, 32)
    a = C(239, 74, 66); w = C(255, 255, 255)
    # body
    g.rect(2, 14, 28, 16, PAL['cream'][1])
    g.rect(4, 18, 24, 8, C(99, 66, 49))
    g.rect(5, 19, 22, 6, C(156, 115, 82))
    # counter
    g.rect(2, 26, 28, 4, PAL['wood'][1])
    g.hline(2, 26, 28, PAL['wood'][0])
    # awning
    for x in range(0, 32):
        c = a if (x // 4) % 2 == 0 else w
        g.vline(x, 8, 7, c)
        g.p(x, 15, c if x % 4 in (1, 2) else None)
    g.hline(0, 8, 32, C(189, 41, 49))
    # sign board
    g.rect(6, 2, 20, 6, C(255, 247, 222))
    g.hline(8, 4, 16, text_color)
    g.hline(8, 5, 12, text_color)
    g.outline()
    return g.im


def vine_row():
    """A 16x16 vineyard row tile (posts + leaves), tiles horizontally."""
    g = Px(16, 16)
    lf = PAL['leaf']
    for x in range(16):
        h = 7 + (1 if x % 5 == 0 else 0)
        for y in range(3, 3 + h):
            g.p(x, y, lf[2] if y > 6 else lf[1])
    rnd = random.Random(5)
    for _ in range(18):
        g.p(rnd.randrange(16), rnd.randrange(3, 10), lf[0])
    for _ in range(4):
        x = rnd.randrange(1, 15)
        g.p(x, 8, C(123, 57, 140)); g.p(x, 9, C(90, 41, 107))
    g.vline(1, 2, 12, PAL['wood'][2])
    g.hline(0, 4, 16, C(140, 140, 140))
    g.hline(0, 11, 16, lf[3])
    g.hline(0, 12, 16, C(0, 0, 0, 50))
    return g.im


def sheet(items, scale=4, cols=6, bg=(115, 197, 164)):
    """Preview: list of (name, image)."""
    cell = max(max(i.width, i.height) for _, i in items) * scale + 20
    rows = (len(items) + cols - 1) // cols
    out = Image.new('RGB', (cols * cell, rows * cell), (60, 60, 60))
    d = ImageDraw.Draw(out)
    for k, (n, im) in enumerate(items):
        x, y = (k % cols) * cell, (k // cols) * cell
        bgim = Image.new('RGBA', im.size, bg + (255,))
        bgim.alpha_composite(im)
        out.paste(bgim.resize((im.width * scale, im.height * scale), Image.NEAREST), (x + 4, y + 16))
        d.text((x + 4, y + 2), n, fill=(255, 255, 0))
    return out


# ---------------------------------------------------------------- tiny font (caps, 5 px tall)
FONT = {
    'A': ["010", "101", "111", "101", "101"], 'B': ["110", "101", "110", "101", "110"],
    'C': ["011", "100", "100", "100", "011"], 'D': ["110", "101", "101", "101", "110"],
    'E': ["111", "100", "110", "100", "111"], 'F': ["111", "100", "110", "100", "100"],
    'G': ["011", "100", "101", "101", "011"], 'H': ["101", "101", "111", "101", "101"],
    'I': ["111", "010", "010", "010", "111"], 'J': ["001", "001", "001", "101", "010"],
    'K': ["101", "101", "110", "101", "101"], 'L': ["100", "100", "100", "100", "111"],
    'M': ["10001", "11011", "10101", "10001", "10001"], 'N': ["1001", "1101", "1011", "1001", "1001"],
    'O': ["010", "101", "101", "101", "010"], 'P': ["110", "101", "110", "100", "100"],
    'Q': ["010", "101", "101", "110", "011"], 'R': ["110", "101", "110", "101", "101"],
    'S': ["011", "100", "010", "001", "110"], 'T': ["111", "010", "010", "010", "010"],
    'U': ["101", "101", "101", "101", "111"], 'V': ["101", "101", "101", "101", "010"],
    'W': ["10001", "10001", "10101", "11011", "10001"], 'X': ["101", "101", "010", "101", "101"],
    'Y': ["101", "101", "010", "010", "010"], 'Z': ["111", "001", "010", "100", "111"],
    ' ': ["00", "00", "00", "00", "00"], "'": ["1", "1", "0", "0", "0"], '.': ["0", "0", "0", "0", "1"],
    '0': ["111", "101", "101", "101", "111"], '1': ["010", "110", "010", "010", "111"],
    '2': ["110", "001", "010", "100", "111"], '3': ["110", "001", "010", "001", "110"],
}


def text_width(s):
    return sum(len(FONT.get(ch, FONT[' '])[0]) + 1 for ch in s) - 1


def text(g, x, y, s, col):
    for ch in s:
        gl = FONT.get(ch.upper(), FONT[' '])
        for yy, row in enumerate(gl):
            for xx, b in enumerate(row):
                if b == '1':
                    g.p(x + xx, y + yy, col)
        x += len(gl[0]) + 1


def signboard(g, cx, y, s, bg=C(255, 247, 222), fg=C(66, 49, 49), border=OUT):
    w = text_width(s) + 6
    x = cx - w // 2
    g.rect(x, y, w, 9, bg)
    g.hline(x, y, w, border); g.hline(x, y + 8, w, border)
    g.vline(x, y, 9, border); g.vline(x + w - 1, y, 9, border)
    text(g, x + 3, y + 2, s, fg)


def hotel(cw=6, floors=4, wall='cream', name='HOTEL', awning='blue', door_cx=None, seed=5):
    """Riviera hotel: flat roof with sign, balconies with railings, glass entrance."""
    W = cw * 16
    H = (floors * 16 + 8 + 15) // 16 * 16 + 16
    g = Px(W, H)
    wl = PAL[wall]
    a, b = UMBRELLA_COLS[awning]
    roof_y = H - floors * 16 - 8 - 8
    # flat roof with parapet
    g.rect(1, roof_y, W - 2, 8, PAL['stone'][1])
    g.hline(1, roof_y, W - 2, PAL['stone'][0])
    g.hline(1, roof_y + 7, W - 2, PAL['stone'][3])
    signboard(g, W // 2, roof_y - 6, name, bg=C(255, 255, 255), fg=C(41, 82, 165))
    wy = roof_y + 8
    wall_fill(g, 1, wy, W - 2, H - wy, wl)
    for f in range(floors - 1):
        fy = wy + 2 + f * 16
        for i in range(cw):
            x = i * 16
            # french window
            g.rect(x + 4, fy, 8, 11, PAL['glass'][2])
            g.hline(x + 4, fy, 8, PAL['glass'][3])
            g.p(x + 5, fy + 1, PAL['glass'][0]); g.p(x + 5, fy + 2, PAL['glass'][1])
            g.vline(x + 8, fy, 11, wl[0])
        # balcony slab + railing
        g.rect(1, fy + 11, W - 2, 2, PAL['stone'][1])
        g.hline(1, fy + 13, W - 2, PAL['stone'][3])
        g.hline(1, fy + 7, W - 2, C(90, 90, 99))
        for xx in range(2, W - 2, 3):
            g.vline(xx, fy + 7, 4, C(115, 115, 123))
    # ground floor: awning + glass doors
    gy = H - 16
    for x in range(1, W - 1):
        g.vline(x, gy - 3, 4, a if (x // 4) % 2 == 0 else C(255, 255, 255))
    g.hline(1, gy - 3, W - 2, b)
    if door_cx is None:
        door_cx = cw // 2
    for i in range(cw):
        x = i * 16
        if i == door_cx:
            g.rect(x + 2, gy + 2, 12, 14, PAL['glass'][3])
            g.rect(x + 3, gy + 3, 10, 13, PAL['glass'][2])
            g.vline(x + 8, gy + 3, 13, PAL['stone'][1])
            g.p(x + 4, gy + 4, PAL['glass'][0])
        else:
            g.rect(x + 3, gy + 3, 10, 8, PAL['glass'][2])
            g.hline(x + 3, gy + 3, 10, PAL['glass'][3])
            g.p(x + 4, gy + 4, PAL['glass'][0])
    g.rect(1, H - 3, W - 2, 3, PAL['stone'][2])
    g.outline()
    ch = H // 16
    solid = {(x, y) for x in range(cw) for y in range(ch)}
    solid.discard((door_cx, ch - 1))
    return dict(img=g.im, solid=solid, door=(door_cx, ch - 1), top=set(), w=cw, h=ch)


def bar(cw=5, name='BAR', wall='peach', awning='red', door_cx=None):
    """Seaside bar: one floor with big windows, striped awning, sign, small flat roof terrace."""
    W = cw * 16
    H = 48
    g = Px(W, H)
    wl = PAL[wall]
    a, b = UMBRELLA_COLS[awning]
    # roof terrace
    g.rect(1, 6, W - 2, 10, PAL['stone'][1])
    g.hline(1, 6, W - 2, PAL['stone'][0])
    g.hline(1, 15, W - 2, PAL['stone'][3])
    for xx in range(2, W - 2, 3):
        g.vline(xx, 3, 4, C(255, 255, 255))
    g.hline(1, 3, W - 2, C(198, 198, 198))
    wall_fill(g, 1, 16, W - 2, 32, wl)
    signboard(g, W // 2, 17, name, bg=C(41, 115, 107), fg=C(255, 247, 214), border=C(24, 57, 57))
    # awning
    for x in range(0, W):
        g.vline(x, 27, 5, a if (x // 4) % 2 == 0 else C(255, 255, 255))
        if x % 4 in (1, 2):
            g.p(x, 32, a if (x // 4) % 2 == 0 else C(255, 255, 255))
    g.hline(0, 27, W, b)
    if door_cx is None:
        door_cx = cw // 2
    for i in range(cw):
        x = i * 16
        if i == door_cx:
            g.rect(x + 3, 34, 10, 14, PAL['wood'][2])
            g.rect(x + 4, 35, 8, 13, PAL['glass'][2])
            g.vline(x + 8, 35, 13, PAL['wood'][1])
        else:
            g.rect(x + 2, 35, 12, 9, PAL['glass'][2])
            g.hline(x + 2, 35, 12, PAL['glass'][3])
            g.p(x + 3, 36, PAL['glass'][0]); g.p(x + 4, 36, PAL['glass'][1])
            g.hline(x + 1, 44, 14, wl[3])
    g.outline()
    ch = H // 16
    solid = {(x, y) for x in range(cw) for y in range(ch)}
    solid.discard((door_cx, ch - 1))
    return dict(img=g.im, solid=solid, door=(door_cx, ch - 1), top=set(), w=cw, h=ch)


def cafe_table(color='red'):
    g = Px(16, 16)
    a, b = UMBRELLA_COLS[color]
    g.sprite(1, 2, [
        "..xxxxxxxxxx..",
        ".xwwwwwwwwwwx.",
        ".xwwwwwwwwwwx.",
        "..xxxxxxxxxx..",
        ".....x..x.....",
        ".aa..x..x..aa.",
        ".aa..x..x..aa.",
        ".bb.xx..xx.bb.",
    ], {'x': OUT, 'w': C(255, 255, 255), 'a': a, 'b': b})
    return g.im


def lamp():
    g = Px(16, 32)
    g.sprite(5, 6, [
        "..xxx.",
        ".xyyyx",
        ".xyyyx",
        "..xxx.",
        "...x..",
    ], {'x': OUT, 'y': C(255, 239, 156)})
    g.rect(7, 11, 2, 17, C(66, 74, 82))
    g.rect(6, 27, 4, 2, C(49, 57, 66))
    return g.im


def bench():
    g = Px(16, 16)
    w = PAL['wood']
    g.rect(1, 5, 14, 3, w[1]); g.hline(1, 5, 14, w[0])
    g.rect(1, 9, 14, 3, w[1]); g.hline(1, 9, 14, w[0])
    g.vline(2, 12, 3, OUT); g.vline(13, 12, 3, OUT)
    g.outline()
    return g.im


def lifeguard():
    """Bagnino tower 16x32 (red/white)."""
    g = Px(16, 32)
    r = C(239, 74, 66)
    g.rect(3, 6, 10, 6, C(255, 255, 255)); g.hline(3, 6, 10, r); g.hline(3, 9, 10, r)
    g.rect(2, 4, 12, 2, r)
    g.vline(4, 12, 16, PAL['wood'][2]); g.vline(11, 12, 16, PAL['wood'][2])
    for yy in range(14, 28, 4):
        g.hline(4, yy, 8, PAL['wood'][1])
    g.outline()
    return g.im


def pedalo():
    g = Px(32, 16)
    g.sprite(2, 3, [
        "..xxxxxxxxxxxxxxxxxxxxxx..",
        ".xrrrrrrrrrrrrrrrrrrrrrrx.",
        "xrrwwwwwwrrrrrrrrwwwwwwrrx",
        "xrrwwwwwwrrxxxxrrwwwwwwrrx",
        "xrrrrrrrrrrxwwxrrrrrrrrrrx",
        ".xrrrrrrrrrrrrrrrrrrrrrrx.",
        "..xxxxxxxxxxxxxxxxxxxxxx..",
    ], {'x': OUT, 'r': C(239, 74, 66), 'w': C(255, 255, 255)})
    return g.im


def hedge_tiles():
    """Hedge line pieces keyed by connectivity 'NESW' (e.g. 'EW' horizontal). 16x16 each."""
    lf = PAL['leaf']
    out = {}
    import itertools
    for n, e, s, w in itertools.product((0, 1), repeat=4):
        g = Px(16, 16)
        x0 = 0 if w else 2
        x1 = 16 if e else 14
        y0 = 0 if n else 1
        y1 = 16 if s else 13
        # core blob
        for y in range(y0, y1):
            for x in range(x0, x1):
                g.p(x, y, lf[2])
        # horizontal hedge: top light, bottom dark face
        for x in range(x0, x1):
            if not n:
                g.p(x, y0, lf[1]); g.p(x, y0 + 1, lf[1])
            if not s:
                for y in range(y1 - 4, y1):
                    g.p(x, y, lf[3] if y < y1 - 1 else lf[4])
        # texture
        rnd = random.Random(n * 8 + e * 4 + s * 2 + w)
        for y in range(y0 + 1, y1 - 2):
            for x in range(x0 + 1, x1 - 1):
                if (x * 7 + y * 3) % 11 == 0:
                    g.p(x, y, lf[1])
                elif (x * 5 + y * 9) % 13 == 0:
                    g.p(x, y, lf[3])
        if not w:
            for y in range(y0, y1):
                g.p(x0, y, lf[3])
        if not e:
            for y in range(y0, y1):
                g.p(x1 - 1, y, lf[4])
        # rounded corners
        for (cx, cy, cond) in ((x0, y0, not n and not w), (x1 - 1, y0, not n and not e), (x0, y1 - 1, not s and not w), (x1 - 1, y1 - 1, not s and not e)):
            if cond:
                g.px[cx, cy] = (0, 0, 0, 0)
        key = ''.join(k for k, v in zip('NESW', (n, e, s, w)) if v)
        g.outline(open_sides=key)
        out[key] = g.im
    return out


def fountain():
    """Round fountain 32x32 with a basin and a jet."""
    g = Px(32, 32)
    st = PAL['stone']
    wt = [C(206, 239, 255), C(132, 197, 247), C(82, 148, 222)]
    for y in range(32):
        for x in range(32):
            dx, dy = (x - 15.5) / 15, (y - 18) / 11
            d = dx * dx + dy * dy
            if d <= 1:
                g.p(x, y, st[1] if d > 0.62 else wt[1])
                if 0.62 < d <= 0.75:
                    g.p(x, y, st[2])
                if d > 0.9 and y > 18:
                    g.p(x, y, st[3])
    for y in range(4, 18):
        g.p(15, y, wt[0]); g.p(16, y, wt[1])
    for (x, y) in ((13, 6), (18, 7), (12, 10), (19, 11), (11, 14), (20, 15)):
        g.p(x, y, wt[0])
    g.rect(13, 16, 6, 4, st[0])
    g.outline()
    return g.im


def swing():
    """Playground swing 32x32."""
    g = Px(32, 32)
    r = C(239, 74, 66)
    g.hline(3, 6, 26, r); g.hline(3, 7, 26, C(189, 41, 49))
    for x in (3, 4, 27, 28):
        g.vline(x, 6, 22, r if x in (3, 27) else C(189, 41, 49))
    for sx in (9, 19):
        g.vline(sx, 8, 12, C(140, 140, 140)); g.vline(sx + 4, 8, 12, C(140, 140, 140))
        g.rect(sx - 1, 20, 7, 2, PAL['wood'][1])
    g.outline()
    return g.im


def slide():
    g = Px(32, 32)
    y = C(255, 206, 66); b = C(74, 140, 239)
    g.rect(4, 8, 6, 20, b)
    for i in range(14):
        g.rect(10 + i, 10 + i, 4, 3, y)
    for yy in range(10, 28, 3):
        g.hline(4, yy, 6, C(41, 90, 189))
    g.outline()
    return g.im


def flowerbed(colors=((239, 99, 132), (255, 206, 66))):
    """Raised flower bed 16x16 tile (tiles horizontally)."""
    g = Px(16, 16)
    st = PAL['stone']
    g.rect(0, 9, 16, 5, st[1]); g.hline(0, 9, 16, st[0]); g.hline(0, 13, 16, st[3])
    lf = PAL['leaf']
    g.rect(0, 3, 16, 6, lf[2])
    for i, x in enumerate(range(1, 16, 3)):
        c = colors[i % len(colors)]
        g.p(x, 4, c); g.p(x + 1, 4, c); g.p(x, 5, c); g.p(x + 1, 5, tuple(max(0, v - 60) for v in c))
        g.p(x + 1, 7, lf[0])
    return g.im


def shrub(seed=1, colors='pine'):
    """Low round shrub (ginepro) 16x16."""
    g = Px(16, 16)
    lf = PAL[colors]
    for y in range(16):
        for x in range(16):
            d = ((x - 7.5) / 7.2) ** 2 + ((y - 9) / 6.2) ** 2
            if d <= 1:
                c = lf[1] if y < 7 else lf[2] if y < 12 else lf[3]
                g.p(x, y, c)
    rnd = random.Random(seed)
    for _ in range(14):
        x, y = rnd.randrange(2, 14), rnd.randrange(4, 13)
        if ((x - 7.5) / 7.2) ** 2 + ((y - 9) / 6.2) ** 2 < 0.7:
            g.p(x, y, lf[0] if y < 9 else lf[2])
    g.outline()
    return g.im


def log():
    g = Px(32, 16)
    bk = PAL['bark']
    g.rect(2, 6, 28, 7, bk[1]); g.hline(2, 6, 28, bk[0]); g.hline(2, 12, 28, bk[3])
    for x in range(5, 28, 6):
        g.vline(x, 7, 5, bk[2])
    g.rect(26, 6, 4, 7, PAL['wood'][0]); g.p(27, 9, bk[2]); g.p(28, 8, bk[2])
    g.outline()
    return g.im


def reeds(seed=2):
    """Reeds (canne) 16x16 for pond shores; transparent background."""
    g = Px(16, 16)
    rnd = random.Random(seed)
    for i in range(7):
        x = 1 + i * 2 + rnd.randrange(2)
        h = 8 + rnd.randrange(6)
        for y in range(15 - h, 15):
            g.p(x, y, PAL['leaf'][2] if y > 15 - h + 2 else PAL['leaf'][1])
        g.p(x, 15 - h - 1, C(140, 99, 57)); g.p(x, 15 - h - 2, C(140, 99, 57))
    return g.im


def picnic_table():
    g = Px(32, 16)
    w = PAL['wood']
    g.rect(2, 2, 28, 3, w[1]); g.hline(2, 2, 28, w[0])
    g.rect(4, 6, 24, 4, w[1]); g.hline(4, 6, 24, w[0]); g.hline(4, 9, 24, w[3])
    g.rect(2, 11, 28, 3, w[1]); g.hline(2, 11, 28, w[0])
    g.outline()
    return g.im


def rustic_fence():
    """Wooden post-and-rail fence pieces keyed by connectivity like hedges ('EW', 'NS', ...)."""
    import itertools
    w = PAL['wood']
    out = {}
    for n, e, s, ww in itertools.product((0, 1), repeat=4):
        g = Px(16, 16)
        # post
        g.rect(6, 4, 4, 9, w[1]); g.vline(6, 4, 9, w[0]); g.vline(9, 4, 9, w[3]); g.hline(6, 4, 4, w[0])
        if e:
            g.rect(10, 6, 6, 2, w[0]); g.rect(10, 10, 6, 2, w[1])
        if ww:
            g.rect(0, 6, 6, 2, w[0]); g.rect(0, 10, 6, 2, w[1])
        if n:
            g.rect(7, 0, 2, 4, w[1])
        if s:
            g.rect(7, 13, 2, 3, w[1])
        key = ''.join(k for k, v in zip('NESW', (n, e, s, ww)) if v)
        g.outline(open_sides=key)
        out[key] = g.im
    return out


def dune_grass(seed=3):
    """Tufts of marram grass on sand (transparent bg)."""
    g = Px(16, 16)
    rnd = random.Random(seed)
    lf = [C(165, 189, 99), C(123, 156, 74), C(90, 115, 57)]
    for t in range(3):
        cx, cy = rnd.randrange(3, 13), rnd.randrange(6, 14)
        for k in range(5):
            dx = k - 2
            for yy in range(4):
                g.p(cx + dx * (yy // 2 + 1) // 2, cy - yy, lf[min(2, yy // 2 + (k % 2))])
    return g.im


def boardwalk(vertical=False):
    g = Px(16, 16)
    w = PAL['wood']
    if vertical:
        g.rect(2, 0, 12, 16, w[1])
        for y in range(0, 16, 4):
            g.hline(2, y, 12, w[3]); g.hline(2, y + 1, 12, w[0])
        g.vline(2, 0, 16, w[3]); g.vline(13, 0, 16, w[3])
    else:
        g.rect(0, 2, 16, 12, w[1])
        for x in range(0, 16, 4):
            g.vline(x, 2, 12, w[3]); g.vline(x + 1, 2, 12, w[0])
        g.hline(0, 2, 16, w[3]); g.hline(0, 13, 16, w[3])
    return g.im


def young_pine(seed=4):
    """Small umbrella pine 16x32."""
    g = Px(16, 32)
    pn = PAL['pine']
    rnd = random.Random(seed)
    for y in range(32):
        for x in range(16):
            d = ((x - 7.5) / 7.5) ** 2 + ((y - 10) / 6) ** 2
            if d <= 1:
                g.p(x, y, pn[1] if y < 8 else pn[2] if y < 13 else pn[3])
    for _ in range(16):
        x, y = rnd.randrange(2, 14), rnd.randrange(5, 14)
        if ((x - 7.5) / 7.5) ** 2 + ((y - 10) / 6) ** 2 < 0.7:
            g.p(x, y, pn[0] if y < 10 else pn[2])
    bk = PAL['bark']
    g.rect(7, 15, 2, 14, bk[1]); g.vline(7, 15, 14, bk[0]); g.rect(6, 28, 4, 2, bk[2])
    g.outline()
    return g.im


# ---------------------------------------------------------------- canals and boats

def quay_rim(top=True):
    """Stone rim of a canal quay drawn over the ground cell (transparent above/below)."""
    g = Px(16, 16)
    st = PAL['stone']
    if top:   # bank above the water: rim at the bottom of the cell
        g.rect(0, 12, 16, 4, st[1]); g.hline(0, 12, 16, st[0]); g.hline(0, 15, 16, st[3])
        for x in (3, 11):
            g.vline(x, 13, 2, st[2])
    else:     # bank below the water: rim at the top
        g.rect(0, 0, 16, 4, st[1]); g.hline(0, 0, 16, st[2]); g.hline(0, 3, 16, st[0])
        for x in (7, 15):
            g.vline(x, 1, 2, st[2])
    return g.im


def quay_face():
    """Wall face visible at the top of the first water row (north bank)."""
    g = Px(16, 16)
    st = PAL['stone']
    g.rect(0, 0, 16, 6, st[2])
    g.hline(0, 0, 16, st[1])
    for x in range(0, 16, 8):
        g.vline(x, 0, 6, st[3])
    g.hline(0, 3, 16, st[3])
    g.hline(0, 6, 16, C(24, 57, 99, 255))
    return g.im


def bollard():
    g = Px(16, 16)
    g.sprite(5, 4, [
        ".xxxx.",
        "xddddx",
        "xddddx",
        ".xddx.",
        ".xddx.",
        "xxxxxx",
    ], {'x': OUT, 'd': C(66, 74, 90)})
    return g.im


def bridge_ns():
    """Wooden bridge planks running north-south with side rails (one cell)."""
    g = Px(16, 16)
    w = PAL['wood']
    g.rect(0, 0, 16, 16, w[1])
    for y in range(0, 16, 3):
        g.hline(0, y, 16, w[2])
        g.hline(0, y + 1, 16, w[0])
    g.rect(0, 0, 2, 16, w[3]); g.rect(14, 0, 2, 16, w[3])
    g.vline(1, 0, 16, w[2]); g.vline(14, 0, 16, w[2])
    return g.im


SAIL = {
    'orange': (C(239, 140, 57), C(198, 90, 33), C(255, 222, 99)),
    'red': (C(214, 66, 49), C(156, 41, 33), C(255, 222, 99)),
    'yellow': (C(255, 206, 74), C(214, 156, 41), C(198, 57, 49)),
}


def boat(sail='orange', hull=(41, 99, 165)):
    """Traditional Romagna fishing boat with a lug sail ('vela al terzo'), 48x48."""
    g = Px(48, 48)
    a, b, sym = SAIL[sail]
    hl = C(*hull)
    hd = tuple(max(0, v - 40) for v in hull)
    # sail (trapezoid)
    for y in range(4, 32):
        x0 = 14 + (32 - y) // 6
        x1 = 34 + (y - 4) // 5
        for x in range(x0, min(x1, 44)):
            g.p(x, y, a if (x - x0) > 1 else b)
    # yard and mast
    for i in range(22):
        g.p(13 + i, 4 + i // 6, C(99, 66, 41))
    g.vline(24, 2, 34, C(99, 66, 41))
    # painted symbol (sun)
    for y in range(13, 22):
        for x in range(27, 36):
            if (x - 31) ** 2 + (y - 17) ** 2 <= 14:
                g.p(x, y, sym)
    # hull
    for y in range(34, 44):
        inset = (y - 34) // 2
        for x in range(4 + inset, 44 - inset):
            g.p(x, y, hl if y < 39 else hd)
    g.hline(4, 34, 40, C(255, 255, 255))
    g.hline(5, 36, 38, C(239, 74, 66))
    g.outline()
    # water shadow
    for x in range(8, 40):
        g.p(x, 45, (0, 0, 0, 70))
    return g.im


def shopfront(cw=4, name='OSTERIA', wall='ochre', roof='roof', awning='green', door_cx=None, seed=3, floors=2):
    """Two-storey canal house with a shop on the ground floor (awning + sign)."""
    W = cw * 16
    roof_h = 24
    wall_h = floors * 16 + 8
    H = ((roof_h + wall_h + 15) // 16) * 16
    g = Px(W, H)
    wl, rf = PAL[wall], PAL[roof]
    a, b = UMBRELLA_COLS[awning]
    top = H - wall_h - roof_h
    coppi_roof(g, 1, top, W - 2, roof_h - 2, rf)
    wy = top + roof_h
    wall_fill(g, 2, wy, W - 4, wall_h, wl, seed)
    for f in range(floors - 1):
        for i in range(cw):
            window(g, i * 16 + 2, wy + 4 + f * 16, wl, PAL['green_sh'])
    # sign band + awning
    gy = H - 18
    signboard(g, W // 2, gy - 11, name, bg=C(255, 247, 222), fg=C(66, 49, 49))
    for x in range(1, W - 1):
        g.vline(x, gy - 1, 4, a if (x // 4) % 2 == 0 else C(255, 255, 255))
    g.hline(1, gy - 1, W - 2, b)
    if door_cx is None:
        door_cx = cw // 2
    for i in range(cw):
        x = i * 16
        if i == door_cx:
            door(g, x + 3, H - 16, w=10, h=13)
        else:
            g.rect(x + 2, gy + 4, 12, 9, PAL['glass'][2])
            g.hline(x + 2, gy + 4, 12, PAL['glass'][3])
            g.p(x + 3, gy + 5, PAL['glass'][0]); g.p(x + 4, gy + 5, PAL['glass'][1])
            g.hline(x + 1, gy + 13, 14, wl[3])
    g.rect(2, H - 3, W - 4, 3, PAL['stone'][2])
    g.outline()
    ch = H // 16
    solid = {(x, y) for x in range(cw) for y in range(ch)}
    solid.discard((door_cx, ch - 1))
    return dict(img=g.im, solid=solid, door=(door_cx, ch - 1), top=set(), w=cw, h=ch)


def warehouse(cw=8, name='MAGAZZINO', wall='brick', roof='roof', door_cx=None):
    """Long brick salt warehouse: low pitched roof, arched doorways, painted sign."""
    W = cw * 16
    H = 80
    g = Px(W, H)
    wl, rf = PAL[wall], PAL[roof]
    coppi_roof(g, 1, 4, W - 2, 26, rf, hip=False)
    wall_fill(g, 1, 32, W - 2, 48, wl)
    # pilasters
    for x in range(1, W - 1, 32):
        g.rect(x, 32, 3, 48, wl[0]); g.vline(x + 2, 32, 48, wl[2])
    g.rect(W - 4, 32, 3, 48, wl[0])
    signboard(g, W // 2, 36, name, bg=C(255, 247, 222), fg=C(123, 41, 33))
    if door_cx is None:
        door_cx = cw // 2
    for i in range(cw):
        x = i * 16
        if i % 2 == 1 and i != door_cx:
            # tall arched window
            g.rect(x + 3, 52, 10, 16, C(66, 49, 49))
            g.hline(x + 4, 51, 8, C(66, 49, 49)); g.hline(x + 5, 50, 6, C(66, 49, 49))
            g.rect(x + 4, 53, 8, 14, PAL['glass'][3])
            g.vline(x + 8, 53, 14, C(66, 49, 49))
        if i == door_cx:
            g.rect(x + 1, 58, 14, 22, C(66, 49, 49))
            g.hline(x + 2, 57, 12, C(66, 49, 49)); g.hline(x + 4, 56, 8, C(66, 49, 49))
            g.rect(x + 2, 59, 12, 21, PAL['wood'][1])
            g.vline(x + 8, 59, 21, PAL['wood'][3])
            for yy in (63, 70):
                g.hline(x + 3, yy, 10, PAL['wood'][0])
    g.rect(1, H - 3, W - 2, 3, PAL['stone'][2])
    g.outline()
    ch = H // 16
    solid = {(x, y) for x in range(cw) for y in range(ch)}
    solid.discard((door_cx, ch - 1))
    return dict(img=g.im, solid=solid, door=(door_cx, ch - 1), top=set(), w=cw, h=ch)


def palazzo_comunale(cw=9, wall='ochre', roof='roof', name='MUNICIPIO', door_cx=None, tower=True):
    """Town hall: portico on the ground floor, windows above, central clock tower."""
    W = cw * 16
    H = 96
    g = Px(W, H)
    wl, rf = PAL[wall], PAL[roof]
    # tower behind the roof
    tx = W // 2 - 10
    if tower:
        g.rect(tx, 2, 20, 40, wl[2])
        g.rect(tx + 1, 6, 18, 36, wl[1])
        g.vline(tx + 18, 6, 36, wl[3])
        coppi_roof(g, tx - 2, 0, 24, 6, rf, hip=True)
        # clock
        for y in range(12, 24):
            for x in range(tx + 4, tx + 16):
                if (x - (tx + 10)) ** 2 + (y - 18) ** 2 <= 30:
                    g.p(x, y, C(255, 255, 239))
        g.vline(tx + 10, 14, 5, OUT); g.hline(tx + 10, 18, 4, OUT)
        # bell arch
        g.rect(tx + 6, 27, 8, 9, C(66, 49, 49)); g.p(tx + 9, 31, C(214, 173, 74)); g.p(tx + 10, 31, C(214, 173, 74))
    coppi_roof(g, 1, 30, W - 2, 18, rf, hip=True)
    wy = 50
    wall_fill(g, 1, wy, W - 2, H - wy, wl)
    for i in range(cw):
        window(g, i * 16 + 2, wy + 3, wl, PAL['green_sh'], tall=9)
    signboard(g, W // 2, wy + 16, name, bg=C(255, 247, 222), fg=C(66, 49, 49))
    # portico
    ay = H - 20
    g.rect(1, ay, W - 2, 20, wl[2])
    if door_cx is None:
        door_cx = cw // 2
    for i in range(cw):
        x = i * 16
        g.rect(x + 1, ay, 3, 20, wl[0]); g.vline(x + 3, ay, 20, wl[2])
        g.rect(x + 4, ay + 6, 10, 14, C(66, 49, 49))
        g.rect(x + 5, ay + 5, 8, 1, C(66, 49, 49)); g.rect(x + 6, ay + 4, 6, 1, C(66, 49, 49))
        if i == door_cx:
            g.rect(x + 6, ay + 9, 6, 11, PAL['wood'][1]); g.vline(x + 9, ay + 9, 11, PAL['wood'][3])
        else:
            g.rect(x + 4, ay + 14, 10, 6, C(90, 66, 57))
    g.rect(W - 4, ay, 3, 20, wl[0])
    g.outline()
    ch = H // 16
    solid = {(x, y) for x in range(cw) for y in range(ch)}
    solid.discard((door_cx, ch - 1))
    # top rows (tower) don't block: the tower is behind
    return dict(img=g.im, solid=solid, door=(door_cx, ch - 1), top=set(), w=cw, h=ch)


def region_tile(mask, fill, rim, rim_w=3, sparkle=None, seed=0):
    fill, rim = list(fill), list(rim)
    """A 16x16 tile for a cell inside a region whose outside neighbours (mask chars N,E,S,W and corner
    pairs NE,SE,SW,NW meaning 'diagonal outside') get a rim. fill/rim are colour lists (light..dark)."""
    g = Px(16, 16)
    g.rect(0, 0, 16, 16, fill[1])
    rnd = random.Random(seed)
    for _ in range(6):
        x, y = rnd.randrange(16), rnd.randrange(16)
        g.p(x, y, fill[0])
        if sparkle and rnd.random() < 0.5:
            g.p(x, y, sparkle)
    # subtle ripples
    for y in (5, 11):
        for x in range(2 + (y % 3), 14, 6):
            g.hline(x, y, 3, fill[2])
    n, e, s, w = 'N' in mask, 'E' in mask, 'S' in mask, 'W' in mask
    r = rim_w
    if n:
        g.rect(0, 0, 16, r, rim[1]); g.hline(0, 0, 16, rim[0]); g.hline(0, r, 16, fill[2])
    if s:
        g.rect(0, 16 - r, 16, r, rim[1]); g.hline(0, 15, 16, rim[2]); g.hline(0, 16 - r - 1, 16, fill[0])
    if w:
        g.rect(0, 0, r, 16, rim[1]); g.vline(0, 0, 16, rim[0]); g.vline(r, 0 if not n else r, 16 - (r if n else 0) - (r if s else 0), fill[2])
    if e:
        g.rect(16 - r, 0, r, 16, rim[1]); g.vline(15, 0, 16, rim[2])
    for k, (cx, cy) in (('NE', (16 - r, 0)), ('SE', (16 - r, 16 - r)), ('SW', (0, 16 - r)), ('NW', (0, 0))):
        if k in mask:
            g.rect(cx, cy, r, r, rim[1])
    return g.im


def region_mask(cells, x, y):
    def out(dx, dy):
        return (x + dx, y + dy) not in cells
    m = []
    if out(0, -1): m.append('N')
    if out(1, 0): m.append('E')
    if out(0, 1): m.append('S')
    if out(-1, 0): m.append('W')
    if not out(0, -1) and not out(1, 0) and out(1, -1): m.append('NE')
    if not out(0, 1) and not out(1, 0) and out(1, 1): m.append('SE')
    if not out(0, 1) and not out(-1, 0) and out(-1, 1): m.append('SW')
    if not out(0, -1) and not out(-1, 0) and out(-1, -1): m.append('NW')
    return tuple(m)


SALTWATER = [C(214, 231, 239), C(173, 206, 222), C(140, 181, 206)]
SALTPINK = [C(247, 222, 222), C(231, 189, 198), C(206, 156, 173)]
SALTRIM = [C(255, 255, 247), C(231, 231, 214), C(181, 173, 156)]


def salt_pile():
    g = Px(32, 32)
    for y in range(32):
        for x in range(32):
            if y >= 8 and abs(x - 15.5) <= (y - 6) * 0.75 and y < 28:
                c = C(255, 255, 255) if x < 15 - (y - 8) * 0.2 else C(231, 231, 222)
                if y > 24:
                    c = C(206, 206, 198)
                g.p(x, y, c)
    for x in range(8, 24):
        g.p(x, 28, (0, 0, 0, 60))
    g.outline(C(140, 140, 132))
    return g.im


def farmhouse(door_cx=1):
    """Casa colonica: brick house (3 cells) + barn with a big arch (3 cells), 6x5."""
    W, H = 96, 80
    g = Px(W, H)
    br, rf = PAL['brick'], PAL['roof']
    # house part (left, taller)
    coppi_roof(g, 1, 8, 50, 22, rf, hip=True)
    wall_fill(g, 2, 32, 48, 48, br)
    for x in (4, 20, 36):
        window(g, x, 36, br, PAL['green_sh'])
    window(g, 4, 56, br, PAL['green_sh'])
    window(g, 36, 56, br, PAL['green_sh'])
    door(g, door_cx * 16 + 3, H - 17, w=10, h=13)
    # barn (right, lower)
    coppi_roof(g, 50, 24, 45, 16, PAL['roof_brown'], hip=False)
    wall_fill(g, 51, 42, 44, 38, br)
    g.rect(58, 50, 30, 30, C(74, 49, 41))
    g.hline(60, 49, 26, C(74, 49, 41)); g.hline(63, 48, 20, C(74, 49, 41))
    g.rect(60, 62, 26, 18, C(181, 148, 74))   # hay inside
    for x in range(61, 85, 3):
        g.vline(x, 63, 16, C(214, 181, 99))
    g.outline()
    solid = {(x, y) for x in range(6) for y in range(5)}
    solid.discard((door_cx, 4))
    for (x, y) in ((3, 0), (4, 0), (5, 0)):
        solid.discard((x, y))
    return dict(img=g.im, solid=solid, door=(door_cx, 4), w=6, h=5)


def haystack():
    """Traditional conical haystack (pagliaio) 32x32."""
    g = Px(32, 32)
    y0 = C(239, 206, 107); y1 = C(214, 173, 74); y2 = C(173, 132, 57)
    for y in range(4, 30):
        half = min(13, (y - 2) * 0.62)
        for x in range(32):
            if abs(x - 15.5) <= half:
                c = y0 if x < 15.5 - half / 3 else y1 if x < 15.5 + half / 2 else y2
                if (x + y) % 5 == 0:
                    c = y2 if c != y2 else y1
                g.p(x, y, c)
    g.vline(15, 0, 6, PAL['wood'][2]); g.vline(16, 0, 6, PAL['wood'][3])
    g.outline()
    return g.im


def peach_tree(seed=1):
    return round_tree(colors='leaf', fruit=(255, 156, 99), seed=seed)


def church(cw=6, wall='brick', tower_side='right', name=None, door_cx=None, rose=True):
    """Romanesque brick church: gabled facade with rose window and portal, campanile on one side."""
    W = cw * 16
    H = 112
    g = Px(W, H)
    br = PAL[wall]
    rf = PAL['roof']
    tw = 22
    tx = W - tw - 1 if tower_side == 'right' else 1
    fx0, fx1 = (1, W - tw - 2) if tower_side == 'right' else (tw + 2, W - 2)
    fw = fx1 - fx0
    # campanile
    g.rect(tx, 6, tw, H - 6, br[2])
    g.rect(tx + 1, 10, tw - 2, H - 10, br[1])
    g.vline(tx + tw - 2, 10, H - 10, br[3])
    for y in range(18, H - 20, 16):
        g.rect(tx + 6, y, 10, 8, C(66, 49, 49))
        g.hline(tx + 7, y - 1, 8, C(66, 49, 49))
        g.vline(tx + 11, y, 8, br[1])
        g.hline(tx + 1, y + 11, tw - 2, br[3])
    # pointed cap
    for y in range(0, 10):
        half = (y + 1) * (tw // 2) // 10
        g.hline(tx + tw // 2 - half, y, 2 * half, rf[2] if y < 8 else rf[3])
    # gable facade
    top = 30
    for y in range(top, top + 26):
        half = int((y - top + 1) * (fw / 2) / 26)
        cx = fx0 + fw // 2
        g.hline(cx - half, y, 2 * half, br[1])
        g.p(cx - half, y, rf[3]); g.p(cx + half - 1, y, rf[3])
    g.rect(fx0, top + 26, fw, H - top - 26, br[1])
    for yy in range((top + 26 + 3) // 4 * 4, H, 4):
        g.hline(fx0, yy, fw, br[2])
    # pilasters (lesene)
    for x in (fx0, fx0 + fw // 3, fx0 + 2 * fw // 3, fx1 - 3):
        g.rect(x, top + 24, 3, H - top - 24, br[0])
    # rose window
    cx = fx0 + fw // 2
    if rose:
        for y in range(top + 14, top + 32):
            for x in range(cx - 9, cx + 9):
                d = (x - cx + 0.5) ** 2 + (y - top - 23) ** 2
                if d <= 70:
                    g.p(x, y, PAL['glass'][2] if d > 20 else C(239, 206, 99))
                if 70 < d <= 90:
                    g.p(x, y, PAL['stone'][1])
    # portal
    g.rect(cx - 8, H - 26, 16, 26, PAL['stone'][1])
    g.rect(cx - 6, H - 22, 12, 22, PAL['wood'][2])
    g.hline(cx - 5, H - 23, 10, PAL['wood'][2])
    g.vline(cx, H - 22, 22, PAL['wood'][3])
    if name:
        signboard(g, cx, H - 36, name, bg=C(255, 247, 222), fg=C(66, 49, 49))
    g.outline()
    ch = H // 16
    if door_cx is None:
        door_cx = cx // 16
    solid = {(x, y) for x in range(cw) for y in range(ch)}
    solid.discard((door_cx, ch - 1))
    return dict(img=g.im, solid=solid, door=(door_cx, ch - 1), w=cw, h=ch)


def greenhouse(cw=6, name='PALESTRA', door_cx=None):
    """Glass greenhouse with white iron frame and a curved roof (Grass gym)."""
    W, H = cw * 16, 96
    g = Px(W, H)
    glass = [C(206, 239, 222), C(165, 222, 198), C(115, 189, 165)]
    frame = C(247, 247, 239)
    plant = PAL['leaf']
    # curved roof
    for y in range(8, 40):
        t = (y - 8) / 32
        half = int((W / 2 - 2) * min(1, (t * 2.2) ** 0.5))
        cx = W // 2
        for x in range(cx - half, cx + half):
            g.p(x, y, glass[0] if (x // 8 + y // 8) % 2 else glass[1])
    for x in range(4, W - 4, 8):
        for y in range(8, 40):
            if g.px[x, y][3]:
                g.p(x, y, frame)
    # walls
    g.rect(2, 40, W - 4, H - 40, glass[1])
    for x in range(2, W - 2, 8):
        g.vline(x, 40, H - 40, frame)
    for y in range(40, H, 12):
        g.hline(2, y, W - 4, frame)
    # plants inside
    for x in range(4, W - 4, 6):
        h = 8 + (x * 7) % 9
        for y in range(H - 6 - h, H - 6):
            g.p(x, y, plant[1]); g.p(x + 1, y, plant[2])
    g.hline(2, H - 5, W - 4, C(132, 99, 66))
    signboard(g, W // 2, 42, name, bg=C(255, 255, 255), fg=C(57, 115, 66))
    if door_cx is None:
        door_cx = cw // 2
    dx = door_cx * 16 + 3
    g.rect(dx, H - 16, 10, 16, frame); g.rect(dx + 1, H - 15, 8, 15, glass[2]); g.vline(dx + 5, H - 15, 15, frame)
    g.outline()
    ch = H // 16
    solid = {(x, y) for x in range(cw) for y in range(ch)}
    solid.discard((door_cx, ch - 1))
    return dict(img=g.im, solid=solid, door=(door_cx, ch - 1), w=cw, h=ch)


def theatre(cw=6, name='TEATRO', wall='cream', door_cx=None):
    """Neoclassical theatre: pediment, columns, three doors."""
    W, H = cw * 16, 80
    g = Px(W, H)
    wl = PAL[wall]
    st = PAL['stone']
    # roof band + pediment
    g.rect(1, 18, W - 2, 6, st[2])
    for y in range(4, 20):
        half = int((y - 3) * (W / 2 - 8) / 16)
        g.hline(W // 2 - half, y, 2 * half, wl[1])
        g.p(W // 2 - half, y, st[3]); g.p(W // 2 + half - 1, y, st[3])
    g.rect(1, 24, W - 2, H - 24, wl[1])
    signboard(g, W // 2, 26, name, bg=C(255, 247, 222), fg=C(123, 41, 33))
    # columns
    for x in range(6, W - 6, 14):
        g.rect(x, 37, 6, H - 40, st[0]); g.vline(x + 5, 37, H - 40, st[2])
        g.rect(x - 1, 36, 8, 2, st[1])
    if door_cx is None:
        door_cx = cw // 2
    for i in range(cw):
        x = i * 16
        if i == door_cx:
            g.rect(x + 3, H - 18, 10, 18, PAL['wood'][2]); g.vline(x + 8, H - 18, 18, PAL['wood'][3])
        elif i % 2 == 0:
            g.rect(x + 4, H - 30, 8, 12, PAL['glass'][3])
    g.rect(1, H - 3, W - 2, 3, st[2])
    g.outline()
    ch = H // 16
    solid = {(x, y) for x in range(cw) for y in range(ch)}
    solid.discard((door_cx, ch - 1))
    return dict(img=g.im, solid=solid, door=(door_cx, ch - 1), w=cw, h=ch)


def white_rail():
    """White racetrack rail pieces keyed by connectivity."""
    import itertools
    w0, w1, w2 = C(255, 255, 255), C(222, 222, 222), C(165, 165, 173)
    out = {}
    for n, e, s, ww in itertools.product((0, 1), repeat=4):
        g = Px(16, 16)
        g.rect(7, 5, 2, 8, w1); g.vline(7, 5, 8, w0)
        if e:
            g.rect(9, 6, 7, 2, w0); g.hline(9, 8, 7, w2)
        if ww:
            g.rect(0, 6, 7, 2, w0); g.hline(0, 8, 7, w2)
        if n:
            g.rect(7, 0, 2, 5, w0)
        if s:
            g.rect(7, 13, 2, 3, w0)
        key = ''.join(k for k, v in zip('NESW', (n, e, s, ww)) if v)
        g.outline(C(115, 115, 123), open_sides=key)
        out[key] = g.im
    return out


def grandstand(cw=8, name='IPPODROMO'):
    """Covered grandstand (tribuna) with tiered seats."""
    W, H = cw * 16, 64
    g = Px(W, H)
    # roof canopy
    g.rect(0, 6, W, 8, C(41, 115, 107)); g.hline(0, 6, W, C(74, 156, 140)); g.hline(0, 13, W, C(24, 74, 66))
    for x in range(4, W, 24):
        g.rect(x, 14, 3, 34, C(198, 198, 198))
    # tiers
    for i, y in enumerate(range(16, 48, 6)):
        g.rect(0, y, W, 6, C(222, 214, 198) if i % 2 == 0 else C(198, 189, 173))
        for x in range(2 + (i % 2) * 3, W, 7):
            g.p(x, y + 2, (C(239, 74, 66), C(74, 140, 239), C(255, 214, 66))[(x + i) % 3])
    g.rect(0, 48, W, 16, PAL['brick'][1])
    signboard(g, W // 2, 50, name, bg=C(255, 247, 222), fg=C(41, 115, 107))
    g.outline()
    solid = {(x, y) for x in range(cw) for y in range(4)}
    return dict(img=g.im, solid=solid, door=None, w=cw, h=4)


def statue(color=(156, 156, 148)):
    """Monument on a pedestal, 32x48."""
    g = Px(32, 48)
    st = PAL['stone']
    bz = [C(140, 156, 132), C(99, 123, 99), C(66, 90, 74)]
    # pedestal
    g.rect(6, 28, 20, 16, st[1]); g.hline(6, 28, 20, st[0]); g.vline(25, 28, 16, st[3])
    g.rect(4, 42, 24, 5, st[2]); g.hline(4, 42, 24, st[1])
    g.rect(10, 33, 12, 5, st[0])
    # figure
    g.rect(12, 8, 8, 20, bz[1]); g.vline(12, 8, 20, bz[0]); g.vline(19, 8, 20, bz[2])
    g.rect(13, 3, 6, 6, bz[1]); g.p(14, 4, bz[0])
    g.rect(19, 10, 6, 3, bz[1])       # raised arm
    g.rect(10, 26, 12, 3, bz[2])
    g.outline()
    return g.im


def sunflower_row():
    g = Px(16, 16)
    lf = PAL['leaf']
    for x in (2, 7, 12):
        g.vline(x + 1, 6, 9, lf[2])
        g.p(x, 9, lf[1]); g.p(x + 2, 11, lf[1])
        for (dx, dy) in ((0, 0), (1, 0), (2, 0), (0, 1), (2, 1), (0, 2), (1, 2), (2, 2), (1, -1), (-1, 1), (3, 1), (1, 3)):
            g.p(x + dx, 2 + dy, C(255, 214, 49))
        g.p(x + 1, 3, C(123, 74, 33))
    g.hline(0, 15, 16, lf[3])
    return g.im


def wheat():
    g = Px(16, 16)
    for x in range(0, 16, 2):
        for y in range(2 + (x * 3) % 4, 15):
            g.p(x, y, C(239, 206, 99) if y < 8 else C(214, 173, 74))
        g.p(x, 1 + (x * 3) % 4, C(255, 231, 140))
    return g.im


def ferris_wheel():
    """Small Ferris wheel 64x80."""
    g = Px(64, 80)
    cx, cy, r = 32, 34, 28
    import math
    for a in range(0, 360, 2):
        x = cx + r * math.cos(math.radians(a)); y = cy + r * math.sin(math.radians(a))
        g.p(int(x), int(y), C(222, 222, 222)); g.p(int(x) + 1, int(y), C(165, 165, 173))
    for a in range(0, 360, 30):
        for t in range(0, r, 1):
            x = cx + t * math.cos(math.radians(a)); y = cy + t * math.sin(math.radians(a))
            g.p(int(x), int(y), C(198, 198, 206))
        x = cx + r * math.cos(math.radians(a)); y = cy + r * math.sin(math.radians(a))
        col = (C(239, 74, 66), C(74, 140, 239), C(255, 206, 66), C(99, 206, 115))[(a // 30) % 4]
        g.rect(int(x) - 3, int(y), 7, 6, col); g.hline(int(x) - 3, int(y), 7, OUT)
    for i in range(30):
        g.p(cx - 14 + i // 2, cy + i + 4, C(156, 156, 165)); g.p(cx + 14 - i // 2, cy + i + 4, C(156, 156, 165))
    g.rect(cx - 16, 74, 32, 6, PAL['stone'][2])
    g.rect(cx - 3, cy - 3, 6, 6, C(99, 99, 107))
    return g.im


def tower_block(cw=4, floors=10, name=None):
    """Modern high-rise (Cesenatico grattacielo): glass grid, 16*cw wide."""
    W, H = cw * 16, floors * 12 + 20
    H = (H + 15) // 16 * 16
    g = Px(W, H)
    g.rect(2, 4, W - 4, H - 4, C(140, 156, 181))
    for y in range(8, H - 16, 12):
        for x in range(5, W - 6, 8):
            g.rect(x, y, 5, 8, C(99, 156, 214)); g.p(x, y, C(206, 231, 255))
    g.rect(2, 0, W - 4, 6, C(99, 107, 123))
    g.rect(W // 2 - 6, H - 14, 12, 14, PAL['glass'][3]); g.vline(W // 2, H - 14, 14, C(198, 198, 206))
    g.outline()
    ch = H // 16
    solid = {(x, y) for x in range(cw) for y in range(ch)}
    door = (cw // 2, ch - 1)
    solid.discard(door)
    return dict(img=g.im, solid=solid, door=door, w=cw, h=ch)


def lighthouse():
    """Harbour lighthouse (faro) 32x80, red and white."""
    g = Px(32, 80)
    for y in range(12, 72):
        half = 7 - (72 - y) // 20
        for x in range(16 - half, 16 + half):
            band = ((y - 12) // 10) % 2
            g.p(x, y, C(239, 74, 66) if band else C(255, 255, 255))
        g.p(16 + half - 1, y, C(181, 41, 41) if ((y - 12) // 10) % 2 else C(206, 206, 214))
    g.rect(9, 4, 14, 9, C(66, 74, 82)); g.rect(11, 6, 10, 5, C(255, 239, 140))
    g.rect(13, 0, 6, 4, C(181, 41, 41))
    g.rect(6, 72, 20, 8, PAL['stone'][1]); g.hline(6, 72, 20, PAL['stone'][0])
    g.outline()
    return g.im


def stone_bridge(cw=6):
    """Roman stone bridge (Ponte di Tiberio) deck running east-west, seen from the south: arches over water. 16*cw x 48."""
    W, H = cw * 16, 48
    g = Px(W, H)
    st = [C(231, 222, 198), C(206, 198, 173), C(173, 165, 140), C(132, 123, 107)]
    g.rect(0, 0, W, 4, st[1]); g.hline(0, 0, W, st[0])          # parapet
    g.rect(0, 4, W, 12, st[0])                                   # deck (walkable row)
    for x in range(0, W, 8):
        g.vline(x, 4, 12, st[1])
    g.rect(0, 16, W, 4, st[1]); g.hline(0, 19, W, st[3])          # south parapet
    g.rect(0, 20, W, 20, st[2])
    n = cw // 2
    for i in range(n):
        ax = i * (W // n) + 4
        aw = W // n - 8
        for y in range(24, 40):
            t = (y - 24) / 16
            half = int(aw / 2 * min(1, (t * 1.4) ** 0.5))
            g.hline(ax + aw // 2 - half, y, 2 * half, C(41, 66, 99))
    return g.im
