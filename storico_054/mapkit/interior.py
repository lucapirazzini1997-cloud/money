"""Interior kit: procedural floors, walls and furniture drawn as art on the General primary (like 0.21 rooms)."""
import random
import art
from art import Px, PAL, C, OUT
import r22
from decor import rect

VOID = C(24, 24, 32)

FLOORS = {
    'planks': [C(214, 165, 107), C(189, 140, 90), C(156, 107, 66)],
    'terracotta': [C(222, 140, 99), C(198, 115, 82), C(165, 90, 66)],
    'tiles': [C(239, 231, 214), C(214, 206, 189), C(181, 173, 156)],
    'checker': [C(239, 239, 231), C(140, 148, 165), C(99, 107, 123)],
    'carpet': [C(198, 74, 74), C(173, 57, 57), C(132, 41, 49)],
    'blue': [C(140, 173, 214), C(115, 148, 198), C(82, 115, 165)],
}
WALLS = {
    'plaster': ([C(255, 239, 206), C(239, 222, 189), C(206, 189, 156)], PAL['wood']),
    'ochre': ([C(247, 214, 156), C(231, 189, 132), C(198, 156, 99)], PAL['wood']),
    'blue': ([C(214, 231, 247), C(189, 214, 239), C(148, 181, 214)], [C(239, 239, 239), C(206, 206, 206), C(156, 156, 156), C(99, 99, 99)]),
    'green': ([C(222, 239, 206), C(198, 222, 181), C(156, 189, 140)], PAL['wood']),
    'brick': (PAL['brick'][:3], PAL['wood']),
}


def floor_tile(kind, x, y):
    c = FLOORS[kind]
    g = Px(16, 16)
    g.rect(0, 0, 16, 16, c[0])
    if kind == 'planks':
        for yy in (0, 5, 10, 15):
            g.hline(0, yy, 16, c[2])
        off = (x * 7 + y * 3) % 16
        for yy, o in ((0, off), (5, off + 6), (10, off + 11)):
            g.vline(o % 16, yy + 1, 4, c[2])
        for yy in (2, 7, 12):
            g.hline(1, yy, 14, c[1]) if (x + y + yy) % 3 == 0 else None
    elif kind in ('terracotta', 'tiles', 'blue'):
        g.hline(0, 0, 16, c[2]); g.vline(0, 0, 16, c[2]); g.hline(0, 8, 16, c[2]); g.vline(8, 0, 16, c[2])
        g.p(3, 3, c[1]); g.p(12, 11, c[1]); g.p(11, 4, c[1])
    elif kind == 'checker':
        for yy in range(16):
            for xx in range(16):
                if ((xx // 8) + (yy // 8)) % 2:
                    g.p(xx, yy, c[1])
    elif kind == 'carpet':
        g.rect(0, 0, 16, 16, c[1])
        for yy in range(1, 16, 4):
            for xx in range((yy // 4) % 2 * 2, 16, 4):
                g.p(xx, yy, c[0])
    return g.im


def wall_tile(kind, row, x):
    """row 0 = upper wall (with a beam on top), row 1 = lower wall with wainscot."""
    w, trim = WALLS[kind]
    g = Px(16, 16)
    if row == 0:
        g.rect(0, 0, 16, 16, w[1])
        g.rect(0, 0, 16, 4, trim[2]); g.hline(0, 4, 16, trim[3])
        if kind == 'brick':
            for yy in range(6, 16, 4):
                g.hline(0, yy, 16, w[2])
                o = 0 if (yy // 4) % 2 else 4
                for xx in range(o, 16, 8):
                    g.vline(xx, yy - 3, 3, w[2])
    else:
        g.rect(0, 0, 16, 16, w[1])
        g.rect(0, 6, 16, 10, trim[1]); g.hline(0, 6, 16, trim[0]); g.hline(0, 15, 16, trim[3])
        for xx in (3, 11):
            g.vline(xx, 8, 6, trim[2])
    return g.im


def window_art(kind='plaster', curtain=C(214, 74, 74)):
    g = Px(16, 16)
    g.rect(2, 3, 12, 11, PAL['wood'][2])
    g.rect(3, 4, 10, 9, C(156, 214, 247)); g.rect(3, 4, 10, 3, C(206, 239, 255))
    g.vline(8, 4, 9, PAL['wood'][2])
    g.rect(2, 3, 3, 11, curtain); g.rect(11, 3, 3, 11, curtain)
    return g.im


class Room(r22.RCanvas):
    def __init__(self, w, h, gn, floor='planks', wall='plaster', exit_x=None, keep_events=False, wall_rows=2):
        super().__init__(w, h, (34, 23) if gn[0] == 35 and gn[1] >= 35 else gn)
        self.gn = gn
        self.is_room = True
        self.floor_kind, self.wall_kind = floor, wall
        if not keep_events:
            self.objs, self.bwarps, self.bcoords, self.bbgs = [], [], [], []
        self.conns = []
        self.wall_rows = wall_rows
        for y in range(h):
            for x in range(w):
                if y < wall_rows:
                    img = wall_tile(wall, 0 if y < wall_rows - 1 else 1, x)
                    self.art[y][x] = (img, None, 1, 0, False)
                else:
                    self.art[y][x] = (floor_tile(floor, x, y), None, 0, 0, False)
        self.exit_x = exit_x if exit_x is not None else w // 2
        self.border = [0x0, 0x0, 0x0, 0x0]
        self.void([(0, h - 1)])
        self.void_cell = (0, h - 1)

    def void(self, cells):
        g = Px(16, 16); g.rect(0, 0, 16, 16, VOID)
        for (x, y) in cells:
            self.art[y][x] = (g.im, None, 1, 0, False)

    def walls_box(self, x0, y0, w, h):
        """Interior partition: wall block with its two rows drawn as wall."""
        for x in range(x0, x0 + w):
            for y in range(y0, y0 + h):
                row = 0 if y < y0 + h - 1 else 1
                self.art[y][x] = (wall_tile(self.wall_kind, row, x), None, 1, 0, False)

    def exit_mat(self, x, y, dest_group, dest_num, dest_warp):
        g = Px(16, 16)
        g.rect(1, 3, 14, 12, C(165, 57, 49)); g.rect(2, 4, 12, 10, C(198, 82, 66))
        for xx in range(3, 13, 3):
            g.vline(xx, 5, 8, C(165, 57, 49))
        base = floor_tile(self.floor_kind, x, y)
        base.alpha_composite(g.im)
        self.art[y][x] = (base, None, 0, 0x65, False)
        self.bwarps.append(dict(x=x, y=y, elev=0, warp=dest_warp, num=dest_num, group=dest_group))
        return len(self.bwarps) - 1

    def wall_door(self, x, dest_group, dest_num, dest_warp, color=PAL['wood']):
        """A door in the north wall (lower wall row)."""
        y = self.wall_rows - 1
        g = Px(16, 16)
        g.rect(0, 0, 16, 16, WALLS[self.wall_kind][0][1])
        g.rect(2, 0, 12, 16, color[2]); g.rect(3, 1, 10, 15, color[1])
        g.vline(8, 1, 15, color[2]); g.p(11, 9, C(255, 222, 99))
        g.rect(4, 3, 3, 4, color[0]); g.rect(9, 3, 3, 4, color[0])
        self.art[y][x] = (g.im, None, 0, 0x60, False)
        # the upper row above the door gets a lintel
        if y - 1 >= 0:
            up = wall_tile(self.wall_kind, 0, x)
            gg = Px(16, 16); gg.rect(1, 12, 14, 4, color[3])
            up = up.copy(); up.alpha_composite(gg.im)
            self.art[y - 1][x] = (up, None, 1, 0, False)
        self.bwarps.append(dict(x=x, y=y, elev=0, warp=dest_warp, num=dest_num, group=dest_group))
        return len(self.bwarps) - 1

    def furn(self, x, y, asset, top_rows=0):
        if isinstance(asset, dict):
            img = asset['img']; solid = asset.get('solid')
            if solid is None:
                solid = {(a, b) for a in range(img.width // 16) for b in range(img.height // 16)}
        else:
            img = asset; solid = {(a, b) for a in range(img.width // 16) for b in range(img.height // 16)}
        for cy in range(img.height // 16):
            for cx in range(img.width // 16):
                piece = img.crop((cx * 16, cy * 16, cx * 16 + 16, cy * 16 + 16))
                if piece.getbbox() is None:
                    continue
                X, Y = x + cx, y + cy
                base = self.art[Y][X][0].copy() if self.art[Y][X] else floor_tile(self.floor_kind, X, Y)
                if cy < top_rows:
                    self.art[Y][X] = (base, piece, self.art[Y][X][2] if self.art[Y][X] else 0, 0, False)
                else:
                    base.alpha_composite(piece)
                    self.art[Y][X] = (base, None, 1 if (cx, cy) in solid else 0, 0, False)


# ---------------------------------------------------------------- furniture

def table(cloth=C(255, 255, 255), check=C(214, 57, 57), w=2):
    g = Px(16 * w, 32)
    g.rect(2, 6, 16 * w - 4, 16, cloth)
    for xx in range(2, 16 * w - 2, 4):
        for yy in range(6, 22, 4):
            if (xx // 4 + yy // 4) % 2:
                g.rect(xx, yy, 2, 2, check)
    g.rect(2, 22, 16 * w - 4, 3, C(206, 206, 206))
    g.rect(4, 25, 2, 6, PAL['wood'][3]); g.rect(16 * w - 6, 25, 2, 6, PAL['wood'][3])
    # plates and a carafe of wine
    for px in range(6, 16 * w - 6, 10):
        g.rect(px, 10, 6, 4, C(255, 255, 255)); g.hline(px, 14, 6, C(181, 181, 181))
    g.rect(16 * w // 2 - 1, 7, 3, 6, C(140, 41, 66))
    g.outline()
    return dict(img=g.im, solid={(a, b) for a in range(w) for b in range(2)})


def chair():
    g = Px(16, 16)
    g.rect(4, 1, 8, 6, PAL['wood'][1]); g.rect(4, 7, 8, 4, PAL['wood'][0])
    g.vline(4, 11, 4, PAL['wood'][3]); g.vline(11, 11, 4, PAL['wood'][3])
    g.outline()
    return dict(img=g.im, solid={(0, 0)})


def counter(w=4):
    g = Px(16 * w, 32)
    g.rect(0, 6, 16 * w, 8, PAL['wood'][0]); g.hline(0, 6, 16 * w, C(255, 239, 206))
    g.rect(0, 14, 16 * w, 16, PAL['wood'][2])
    for xx in range(4, 16 * w, 12):
        g.rect(xx, 17, 8, 10, PAL['wood'][1])
    g.rect(6, 1, 4, 6, C(99, 140, 74)); g.rect(18, 2, 3, 5, C(140, 41, 66)); g.rect(30, 3, 8, 4, C(239, 214, 156))
    g.outline()
    return dict(img=g.im, solid={(a, b) for a in range(w) for b in range(2)})


def shelf(items='bottles', w=2):
    g = Px(16 * w, 32)
    g.rect(1, 2, 16 * w - 2, 28, PAL['wood'][2]); g.rect(2, 3, 16 * w - 4, 26, PAL['wood'][3])
    rnd = random.Random(len(items) * w)
    for yy in (4, 13, 22):
        g.hline(2, yy + 7, 16 * w - 4, PAL['wood'][1])
        for xx in range(3, 16 * w - 4, 4):
            if items == 'bottles':
                c = rnd.choice([C(140, 41, 66), C(57, 115, 74), C(214, 189, 99)])
                g.rect(xx, yy + 1, 3, 6, c); g.p(xx + 1, yy, c)
            elif items == 'jars':
                g.rect(xx, yy + 3, 3, 4, rnd.choice([C(239, 140, 66), C(214, 57, 57), C(140, 189, 74)]))
                g.hline(xx, yy + 2, 3, C(255, 255, 255))
            else:
                g.rect(xx, yy + 1, 3, 6, rnd.choice([C(57, 99, 173), C(165, 57, 41), C(57, 140, 90), C(214, 181, 74)]))
    g.outline()
    return dict(img=g.im, solid={(a, 1) for a in range(w)} | {(a, 0) for a in range(w)})


def fireplace():
    g = Px(32, 32)
    g.rect(0, 0, 32, 32, PAL['stone'][2]); g.rect(1, 1, 30, 4, PAL['stone'][1])
    g.rect(5, 10, 22, 20, C(41, 33, 33))
    g.rect(9, 22, 14, 6, C(132, 82, 49))
    for (x, c) in ((11, C(255, 140, 49)), (15, C(255, 206, 82)), (19, C(255, 107, 49))):
        g.rect(x, 16, 3, 7, c)
    g.outline()
    return dict(img=g.im, solid={(0, 0), (1, 0), (0, 1), (1, 1)})


def barrels():
    g = Px(32, 16)
    for x in (1, 16):
        g.rect(x, 2, 14, 13, PAL['wood'][1])
        for yy in (4, 8, 12):
            g.hline(x, yy, 14, PAL['wood'][3])
        g.vline(x + 3, 2, 13, PAL['wood'][0])
    g.outline()
    return dict(img=g.im, solid={(0, 0), (1, 0)})


def hams():
    """Salami and hams hanging from the beam (wall decoration, upper wall row)."""
    g = Px(32, 16)
    g.hline(0, 1, 32, PAL['wood'][3])
    for x, c in ((3, C(165, 74, 66)), (11, C(198, 107, 82)), (19, C(165, 74, 66)), (26, C(214, 173, 140))):
        g.vline(x + 2, 1, 3, C(206, 189, 156))
        g.rect(x, 4, 5, 9, c); g.p(x + 1, 6, C(239, 214, 206)); g.p(x + 3, 9, C(239, 214, 206))
    g.outline()
    return g.im


def plant():
    g = Px(16, 32)
    g.rect(4, 22, 8, 9, C(189, 99, 66)); g.hline(3, 22, 10, C(214, 123, 82))
    rnd = random.Random(2)
    for _ in range(60):
        x = 8 + rnd.randint(-6, 6); y = 6 + rnd.randint(-5, 15)
        g.p(x, y, rnd.choice(PAL['leaf'][:4]))
    g.outline()
    return dict(img=g.im, solid={(0, 1)})


def bed(color=C(99, 140, 206)):
    g = Px(32, 32)
    g.rect(2, 1, 28, 6, PAL['wood'][2])
    g.rect(3, 6, 26, 24, C(255, 255, 255)); g.rect(5, 7, 22, 5, C(239, 239, 247))
    g.rect(3, 13, 26, 17, color); g.hline(3, 13, 26, C(255, 255, 255))
    g.outline()
    return dict(img=g.im, solid={(0, 0), (1, 0), (0, 1), (1, 1)})


def wardrobe():
    g = Px(32, 32)
    g.rect(1, 0, 30, 31, PAL['wood'][1]); g.rect(3, 2, 12, 26, PAL['wood'][0]); g.rect(17, 2, 12, 26, PAL['wood'][0])
    g.p(14, 15, C(255, 222, 99)); g.p(17, 15, C(255, 222, 99))
    g.outline()
    return dict(img=g.im, solid={(0, 0), (1, 0), (0, 1), (1, 1)})


def desk():
    g = Px(32, 32)
    g.rect(1, 6, 30, 10, PAL['wood'][0]); g.rect(1, 16, 30, 12, PAL['wood'][2])
    g.rect(4, 2, 10, 6, C(255, 255, 255)); g.rect(20, 1, 6, 6, C(99, 140, 74))
    g.rect(3, 19, 10, 8, PAL['wood'][1])
    g.outline()
    return dict(img=g.im, solid={(0, 0), (1, 0), (0, 1), (1, 1)})


def rug(w=3, h=2, c1=C(165, 57, 66), c2=C(239, 206, 132)):
    g = Px(16 * w, 16 * h)
    g.rect(1, 1, 16 * w - 2, 16 * h - 2, c1)
    g.rect(4, 4, 16 * w - 8, 16 * h - 8, c2); g.rect(6, 6, 16 * w - 12, 16 * h - 12, c1)
    return dict(img=g.im, solid=set())


def sofa(color=C(57, 99, 165)):
    g = Px(48, 32)
    g.rect(1, 4, 46, 12, color); g.rect(1, 16, 46, 10, color)
    g.rect(4, 14, 40, 8, tuple(min(255, v + 40) for v in color))
    g.rect(1, 26, 4, 5, PAL['wood'][3]); g.rect(43, 26, 4, 5, PAL['wood'][3])
    g.outline()
    return dict(img=g.im, solid={(0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1)})


def painting(c=C(99, 156, 206)):
    g = Px(16, 16)
    g.rect(2, 2, 12, 10, PAL['wood'][0]); g.rect(3, 3, 10, 8, c)
    g.rect(3, 8, 10, 3, C(99, 165, 82)); g.p(9, 5, C(255, 231, 115))
    g.outline()
    return g.im


def stairs():
    g = Px(32, 32)
    for i in range(6):
        g.rect(2 + i * 2, 2 + i * 5, 28 - i * 4, 5, PAL['wood'][i % 2])
        g.hline(2 + i * 2, 6 + i * 5, 28 - i * 4, PAL['wood'][3])
    g.outline()
    return g.im
