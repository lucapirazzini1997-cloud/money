"""Strumenti per disegnare caverne a griglia: pareti, pavimenti, scale, porte con simboli, pedane."""
from kit48 import *
from places32 import asset

THEMES = {
    'galleria': dict(floor=(176, 160, 128), light=(206, 190, 156), stone=(122, 106, 84), shade=(63, 55, 44), deep=(40, 34, 30)),
    'sala': dict(floor=(158, 156, 170), light=(196, 194, 208), stone=(108, 104, 126), shade=(54, 50, 68), deep=(32, 30, 44)),
    'pietra': dict(floor=(190, 152, 104), light=(224, 186, 132), stone=(140, 92, 52), shade=(74, 46, 28), deep=(44, 28, 18)),
    'brina': dict(floor=(206, 228, 240), light=(240, 250, 255), stone=(110, 150, 184), shade=(52, 84, 120), deep=(28, 48, 76)),
    'metallo': dict(floor=(150, 158, 170), light=(196, 204, 214), stone=(96, 106, 120), shade=(46, 52, 64), deep=(26, 30, 40)),
}


class Grid:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.g = [['#'] * w for _ in range(h)]

    def carve(self, x0, y0, x1, y1, ch='.'):
        for y in range(max(0, y0), min(self.h, y1 + 1)):
            for x in range(max(0, x0), min(self.w, x1 + 1)):
                self.g[y][x] = ch

    def put(self, x, y, ch):
        if 0 <= x < self.w and 0 <= y < self.h: self.g[y][x] = ch

    def solid(self, x, y):
        return not (0 <= x < self.w and 0 <= y < self.h) or self.g[y][x] == '#'

    def floors(self):
        return {(x, y) for y in range(self.h) for x in range(self.w) if self.g[y][x] != '#'}


def wall_img(th, face, top, left, right, v):
    """Parete vista dall'alto: massa scura nell'interno, bordo di roccia chiara ai margini, fronte scura sopra il pavimento."""
    c = THEMES[th] if isinstance(th, str) else th
    edge = face or top or left or right
    im = Image.new('RGBA', (16, 16), c['stone'] if edge else c['deep']);d = ImageDraw.Draw(im)
    if not edge:
        if v == 1: d.line((3, 4, 7, 9, 12, 6), fill=c['shade'])
        if v == 2: d.point((5, 11), fill=c['shade']);d.point((11, 3), fill=c['shade'])
        return im
    # sommita' della roccia: luce in alto, venature
    d.rectangle((0, 0, 15, 15), fill=c['stone'])
    d.line((0, 0, 15, 0), fill=c['light']);d.line((2, 3, 9, 3), fill=c['light'])
    d.line((9, 8, 13, 6), fill=c['shade']);d.point((4, 7), fill=c['shade'])
    if face:
        d.rectangle((0, 8, 15, 15), fill=c['shade']);d.line((0, 8, 15, 8), fill=c['light'])
        for k in range(3): d.line((2 + 5 * k + v, 10, 3 + 5 * k + v, 14), fill=c['deep'])
    if top: d.rectangle((0, 0, 15, 1), fill=c['shade'])
    if left: d.line((0, 0, 0, 15), fill=c['shade'])
    if right: d.line((15, 0, 15, 15), fill=c['shade'])
    return im


def floor_img(th, x, y, style='plain'):
    c = THEMES[th] if isinstance(th, str) else th
    im = Image.new('RGBA', (16, 16), c['floor']);d = ImageDraw.Draw(im)
    v = (x * 5 + y * 3) % 5
    if style == 'plain':
        if v == 0: d.point((3, 11), fill=c['stone']);d.point((12, 5), fill=c['light'])
        elif v == 1: d.line((9, 10, 13, 10), fill=c['stone'])
        elif v == 2: d.point((8, 12), fill=c['light'])
    elif style == 'ice':
        d.line((0, 15, 15, 15), fill=c['light']);d.line((15, 0, 15, 15), fill=c['light'])
        if v in (0, 3): d.line((3, 4, 8, 9), fill=c['light']);d.line((8, 9, 6, 13), fill=c['stone'])
    elif style == 'metal':
        d.rectangle((0, 0, 15, 15), outline=c['stone']);d.line((0, 8, 15, 8), fill=c['stone'])
        d.point((2, 2), fill=c['light']);d.point((13, 13), fill=c['light'])
    elif style == 'rock':
        d.line((0, 15, 15, 15), fill=c['stone'])
        if v < 2: d.line((2, 4, 7, 6, 12, 5), fill=c['stone'])
    elif style == 'dais':
        d.rectangle((0, 0, 15, 15), fill=c['light'], outline=c['stone']);d.point((7, 7), fill=c['stone'])
    elif style == 'carpet':
        d.rectangle((0, 0, 15, 15), fill=c['stone']);d.rectangle((2, 0, 13, 15), outline=c['light'])
    return im


def stairs_img(th):
    c = THEMES[th] if isinstance(th, str) else th
    im = Image.new('RGBA', (16, 16), c['shade']);d = ImageDraw.Draw(im)
    for yy in (3, 6, 9, 12): d.rectangle((2, yy, 13, yy + 1), fill=c['light']);d.line((2, yy + 2, 13, yy + 2), fill=c['stone'])
    return im


def paint(cv, gr, th, style='plain', wild=False, edge_cells=(), extra=None):
    """Disegna la griglia sul canvas. wild: pavimenti con incontri (comportamento 8)."""
    c = THEMES[th]
    for y in range(gr.h):
        for x in range(gr.w):
            ch = gr.g[y][x]
            if ch == '#':
                face = not gr.solid(x, y + 1)
                top = not gr.solid(x, y - 1)
                left = not gr.solid(x - 1, y);right = not gr.solid(x + 1, y)
                v = (x * 7 + y * 11) % 3
                cv.art[y][x] = (wall_img(th, face, top, left, right, v), None, 1, 0, False)
            elif ch == 'S':
                cv.art[y][x] = (stairs_img(th), None, 0, 0x60, False)
            else:
                st = {'d': 'dais', 'c': 'carpet'}.get(ch, style)
                cv.art[y][x] = (floor_img(th, x, y, st), None, 0, 8 if (wild and ch == '.') else 0, False)
            cv.over[y][x] = None
    cv.border = [0x173] * 4


def boulder(th):
    c = THEMES[th]
    im = Image.new('RGBA', (16, 16), (0, 0, 0, 0));d = ImageDraw.Draw(im)
    d.ellipse((1, 3, 14, 15), fill=c['stone'], outline=c['shade']);d.arc((3, 5, 11, 11), 180, 270, fill=c['light'])
    return im


def cave_mouth():
    """Bocca di cava 7x5 celle (112x80): parete di roccia, arco scuro; porta in (3,3); massi in (2,4) e (4,4)."""
    th = THEMES['galleria']
    im = Image.new('RGBA', (112, 80), (0, 0, 0, 0));d = ImageDraw.Draw(im)
    d.polygon([(0, 64), (0, 20), (14, 6), (40, 0), (72, 0), (98, 6), (111, 20), (111, 64)], fill=th['stone'], outline=th['shade'])
    for yy in range(8, 60, 10): d.line((4 + (yy * 3) % 20, yy, 30 + (yy * 7) % 40, yy + 3), fill=th['shade'])
    d.line((10, 10, 40, 4, 72, 4, 100, 10), fill=th['light'])
    d.pieslice((30, 14, 82, 66), 180, 360, fill=th['deep'], outline=th['shade'])
    d.rectangle((30, 40, 81, 63), fill=th['deep'])
    d.rectangle((38, 16, 73, 18), fill=th['shade'])        # architrave
    d.line((30, 40, 30, 64), fill=th['shade']);d.line((81, 40, 81, 64), fill=th['shade'])
    for x0 in (32, 80 - 14):
        d.rectangle((x0, 36, x0 + 14, 63), fill=th['deep'])
    for cx in (2, 4):
        b = boulder('galleria');im.alpha_composite(b, (cx * 16, 64))
    solid = {(x, y) for x in range(7) for y in range(4)} - {(3, 3)}
    solid |= {(2, 4), (4, 4)}
    return dict(img=im, solid=solid, door=(3, 3), w=7, h=5)


def symbol_door(symbol, th):
    """Porta con simbolo: 3x3 celle (48x48), porta in (1,2)."""
    c = THEMES[th]
    im = Image.new('RGBA', (48, 48), c['stone']);d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 47, 47), outline=c['shade'], fill=c['stone'])
    for yy in range(4, 24, 8): d.line((2, yy, 45, yy), fill=c['shade'])
    d.rectangle((14, 26, 33, 47), fill=c['deep'], outline=c['shade'])         # vano
    d.rectangle((16, 28, 31, 47), fill=c['deep'])
    # simbolo sopra la porta
    cx, cy = 24, 14
    if symbol == 'pietra':
        d.polygon([(cx, cy - 9), (cx + 9, cy), (cx, cy + 9), (cx - 9, cy)], fill=(224, 150, 62), outline=c['shade']);d.line((cx - 4, cy, cx + 4, cy), fill=c['shade'])
    elif symbol == 'brina':
        for a in (0, 1, 2): d.line((cx - 9 + a * 0, cy - 9 + a * 9, cx + 9, cy + 9 - a * 9), fill=(214, 240, 255), width=2)
        d.line((cx, cy - 10, cx, cy + 10), fill=(214, 240, 255), width=2);d.line((cx - 10, cy, cx + 10, cy), fill=(214, 240, 255), width=2)
    else:
        d.ellipse((cx - 9, cy - 9, cx + 9, cy + 9), fill=(150, 160, 176), outline=c['shade']);d.ellipse((cx - 3, cy - 3, cx + 3, cy + 3), fill=c['shade'])
        for a in range(0, 360, 60):
            import math
            d.line((cx + 7 * math.cos(math.radians(a)), cy + 7 * math.sin(math.radians(a)), cx + 12 * math.cos(math.radians(a)), cy + 12 * math.sin(math.radians(a))), fill=(150, 160, 176), width=2)
    return dict(img=im, solid={(x, y) for x in range(3) for y in range(3)} - {(1, 2)}, door=(1, 2), w=3, h=3)


def sigil_floor(symbol, th):
    """Simbolo inciso sul pavimento 2x2 celle."""
    c = THEMES[th]
    im = Image.new('RGBA', (32, 32), c['light']);d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 31, 31), outline=c['stone'])
    col = {'pietra': (224, 150, 62), 'brina': (96, 170, 220), 'metallo': (120, 132, 150)}[symbol]
    d.ellipse((4, 4, 27, 27), outline=col, width=2)
    if symbol == 'pietra': d.polygon([(16, 8), (24, 16), (16, 24), (8, 16)], fill=col)
    elif symbol == 'brina': d.line((16, 7, 16, 25), fill=col, width=2);d.line((7, 16, 25, 16), fill=col, width=2);d.line((9, 9, 23, 23), fill=col);d.line((23, 9, 9, 23), fill=col)
    else: d.ellipse((11, 11, 20, 20), fill=col)
    return dict(img=im, solid=set(), door=None, w=2, h=2)


def new_cave(name, w, h, region, template=(35, 12)):
    key = add_map(template, region=region, mtype=4)
    cv = r22.RCanvas(w, h, (34, 39));empty_events(cv);cv.gn = key
    NEW_MAPS.append(dict(name=name, map=list(key), width=w, height=h, region=region))
    return cv
