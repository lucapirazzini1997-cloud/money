"""Flamingo overworld sprite (32x32, 9 frames: down, up, left, down walk x2, up walk x2, left walk x2).
Drawn with palette indices of the existing flamingo palette (tag 0x1124)."""
import math

K, OUT, PK_D, PK, PK_L, PK_H, WH, GR = 1, 3, 9, 12, 13, 13, 14, 4
LEG = 5


def blank():
    return [[0] * 32 for _ in range(32)]


def ell(c, cx, cy, rx, ry, col):
    for y in range(32):
        for x in range(32):
            if ((x + .5 - cx) / rx) ** 2 + ((y + .5 - cy) / ry) ** 2 <= 1:
                c[y][x] = col


def px(c, x, y, col):
    if 0 <= x < 32 and 0 <= y < 32:
        c[y][x] = col


def line(c, x0, y0, x1, y1, col, w=1):
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    for i in range(n + 1):
        x = round(x0 + (x1 - x0) * i / n); y = round(y0 + (y1 - y0) * i / n)
        for dx in range(w):
            px(c, x + dx, y, col)


def outline(c):
    o = [r[:] for r in c]
    for y in range(32):
        for x in range(32):
            if c[y][x] == 0 and any(0 <= x + dx < 32 and 0 <= y + dy < 32 and c[y + dy][x + dx] not in (0, OUT, LEG, K)
                                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                o[y][x] = OUT
    return o


def legs(c, xs, phase, side=False):
    """Thin legs from the body to the feet at y=31; phase bends one knee."""
    for i, x in enumerate(xs):
        bent = (phase == 1 and i == 0) or (phase == 2 and i == 1)
        if bent:
            line(c, x, 20, x - 2 if side else x, 25, LEG); line(c, x - 2 if side else x, 25, x, 29, LEG)
            px(c, x - 1, 29, LEG); px(c, x + 1, 29, LEG)
        else:
            line(c, x, 20, x, 30, LEG)
            px(c, x - 1, 31, LEG); px(c, x, 31, LEG); px(c, x + 1, 31, LEG)
        px(c, x, 25, PK_D)               # knee


def side(phase=0):
    c = blank()
    legs(c, (16, 19), phase, side=True)
    ell(c, 19, 16, 6.5, 4, PK)                       # body
    ell(c, 20, 15, 4.5, 2.2, PK_L)                   # wing highlight
    for x in range(22, 27):                          # black flight feathers at the tail
        px(c, x, 16 + (x - 22) // 3, K); px(c, x, 17 + (x - 22) // 3, K)
    for y in range(17, 19):
        for x in range(13, 24):
            if c[y][x] == PK: c[y][x] = PK_D
    # S-shaped neck: from the chest (12,13) up to the head (8,3)
    pts = [(14, 14), (11, 13), (9, 11), (9, 9), (11, 7), (12, 5), (11, 3)]
    for (a, b), (d, e) in zip(pts, pts[1:]):
        line(c, a, b, d, e, PK, 2)
    ell(c, 11, 2.5, 2.4, 2.1, PK)                    # head
    px(c, 11, 2, K)                                  # eye
    # bent bill: pale then black tip, hooked down
    for (x, y, col) in ((9, 2, PK_L), (8, 3, PK_L), (7, 3, PK_L), (7, 4, K), (6, 4, K), (6, 5, K), (8, 4, PK_L)):
        px(c, x, y, col)
    return outline(c)


def front(phase=0, back=False):
    c = blank()
    legs(c, (14, 18), phase)
    ell(c, 16, 16, 5, 4.5, PK)
    if back:
        ell(c, 16, 15, 3.5, 2.5, PK_L)
        for x in range(13, 20):
            px(c, x, 19, K); px(c, x, 18, K if x % 2 else PK_D)
    else:
        ell(c, 16, 17, 3, 2.5, PK_L)
        for x in (11, 21):
            line(c, x, 14, x, 18, PK_D)
    line(c, 15, 4, 15, 12, PK, 2)                    # long thin neck
    px(c, 16, 8, PK_L)
    ell(c, 16, 3.5, 2.4, 2.2, PK)
    if not back:
        px(c, 14, 3, K); px(c, 18, 3, K)             # eyes
        for (x, y, col) in ((15, 5, PK_L), (16, 5, PK_L), (15, 6, K), (16, 6, K), (16, 7, K)):
            px(c, x, y, col)
    return outline(c)


def frames():
    return [front(0), front(0, True), side(0), front(1), front(2), front(1, True), front(2, True), side(1), side(2)]


def encode(fr):
    """32x32 index grid -> 512 bytes of 4bpp tiles (4x4 tiles, row-major)."""
    out = bytearray()
    for ty in range(4):
        for tx in range(4):
            for y in range(8):
                for x in range(0, 8, 2):
                    a = fr[ty * 8 + y][tx * 8 + x]; b = fr[ty * 8 + y][tx * 8 + x + 1]
                    out.append((a & 15) | ((b & 15) << 4))
    return bytes(out)
