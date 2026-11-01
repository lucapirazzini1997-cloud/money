"""Jirachi (written into gfx 238) and the Wish portal (gfx 237): 32x32 single images + 16-colour palettes."""
import math

def blank():
    return [[0] * 32 for _ in range(32)]

def px(c, x, y, v):
    if 0 <= x < 32 and 0 <= y < 32: c[y][x] = v

def ell(c, cx, cy, rx, ry, v):
    for y in range(32):
        for x in range(32):
            if ((x + .5 - cx) / rx) ** 2 + ((y + .5 - cy) / ry) ** 2 <= 1: c[y][x] = v

def outline(c, o=1):
    out = [r[:] for r in c]
    for y in range(32):
        for x in range(32):
            if c[y][x] == 0 and any(0 <= x + dx < 32 and 0 <= y + dy < 32 and c[y + dy][x + dx] not in (0, o)
                                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                out[y][x] = o
    return out

JIRACHI_PAL = [(0, 0, 0), (41, 41, 66), (248, 216, 48), (216, 168, 24), (248, 248, 248), (200, 200, 222), (88, 152, 224),
               (48, 96, 176), (16, 16, 16), (232, 96, 96), (176, 224, 248), (255, 240, 160), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0)]

def jirachi():
    c = blank()
    # star-shaped head: three points (left, up, right) around a round face
    for (dx, dy) in ((-1, 0), (0, -1), (1, 0)):
        for t in range(8):
            w = 4 - t // 2
            for k in range(-w, w + 1):
                if dx: px(c, 16 + dx * (6 + t), 11 + k, 2 if t < 6 else 3)
                else: px(c, 16 + k, 5 - t, 2 if t < 6 else 3)
    ell(c, 16, 12, 7, 6, 2)
    ell(c, 16, 13, 5, 4, 4)                         # white face
    px(c, 14, 13, 8); px(c, 18, 13, 8); px(c, 13, 13, 8); px(c, 19, 13, 8)   # closed eyes
    px(c, 16, 15, 9)
    # blue tags hanging from the three points
    for (x, y) in ((4, 12), (27, 12), (16, 1)):
        for k in range(4): px(c, x, y + k, 6); px(c, x + 1, y + k, 7)
    # body, little arms and the wispy tails
    ell(c, 16, 22, 5, 5, 4); ell(c, 16, 23, 3, 3, 5)
    for k in range(4): px(c, 10 + k, 20 + k // 2, 4); px(c, 22 - k, 20 + k // 2, 4)
    for k in range(5): px(c, 13 - k // 2, 27 + k, 5); px(c, 19 + k // 2, 27 + k, 5)
    px(c, 16, 23, 10)                               # the third eye on the belly (closed)
    for (x, y) in ((6, 4), (26, 5), (24, 25), (7, 24)): px(c, x, y, 11)  # sparkles
    return outline(c)

PORTAL_PAL = [(0, 0, 0), (56, 24, 104), (128, 64, 200), (176, 120, 240), (88, 152, 248), (200, 224, 255), (255, 255, 255),
              (248, 224, 96), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0)]

def portal():
    c = blank()
    for y in range(32):
        for x in range(32):
            dx, dy = x + .5 - 16, (y + .5 - 18) * 1.3
            r = math.hypot(dx, dy)
            if r <= 13:
                a = math.atan2(dy, dx)
                band = int((a * 3 / math.pi + r / 3)) % 4
                c[y][x] = [1, 2, 3, 4][band] if r > 4 else 5
    for (x, y) in ((16, 18), (10, 12), (22, 23), (21, 11), (9, 22), (16, 8)):
        px(c, x, y, 6)
    for (x, y) in ((16, 2), (3, 17), (29, 17)):
        px(c, x, y, 7); px(c, x - 1, y, 7); px(c, x + 1, y, 7); px(c, x, y - 1, 7); px(c, x, y + 1, 7)
    return c

def encode(fr):
    out = bytearray()
    for ty in range(4):
        for tx in range(4):
            for y in range(8):
                for x in range(0, 8, 2):
                    a = fr[ty * 8 + y][tx * 8 + x]; b = fr[ty * 8 + y][tx * 8 + x + 1]
                    out.append((a & 15) | ((b & 15) << 4))
    return bytes(out)

def pal_bytes(p):
    import struct
    return b''.join(struct.pack('<H', (r >> 3) | ((g >> 3) << 5) | ((b >> 3) << 10)) for r, g, b in p)


MEWTWO_PAL = [(0, 0, 0), (56, 40, 72), (232, 224, 240), (190, 176, 206), (160, 112, 192), (116, 76, 150), (128, 40, 168),
              (255, 255, 255), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0)]


def mewtwo():
    """Mewtwo seen from the front: large head with the blunt horns, the tube from the head to the back,
    long arms, purple belly and the thick purple tail curling on the right."""
    c = blank()
    # tail (behind, curling on the right)
    for t in range(20):
        a = t / 19 * 3.6
        x = 21 + int(6 * math.cos(a) * (1 - t / 40)); y = 26 - int(9 * math.sin(a * 0.6)) - t // 4
        ell(c, x, y, 2.4, 2.4, 4 if t < 15 else 5)
    # legs
    for x0 in (12, 18):
        for y in range(23, 31): px(c, x0, y, 3); px(c, x0 + 1, y, 2); px(c, x0 + 2, y, 3)
        px(c, x0 - 1, 30, 3); px(c, x0 + 3, 30, 3)
    # body and purple belly
    ell(c, 16, 18, 5.5, 7, 2)
    ell(c, 16, 21, 3.5, 4, 4)
    # arms
    for k in range(8): px(c, 10 - k // 3, 15 + k, 2); px(c, 22 + k // 3, 15 + k, 2)
    for k in range(3): px(c, 7 + k, 23, 3); px(c, 23 + k, 23, 3)
    # head with horns and eyes
    ell(c, 16, 8, 5.5, 4.5, 2)
    for k in range(4): px(c, 11 - k // 2, 4 - k, 2); px(c, 21 + k // 2, 4 - k, 2)
    px(c, 13, 8, 6); px(c, 14, 8, 6); px(c, 18, 8, 6); px(c, 19, 8, 6)
    px(c, 16, 10, 3)
    # tube from the back of the head to the shoulders
    for k in range(4): px(c, 20 + k // 2, 10 + k, 3)
    px(c, 12, 6, 7)
    return outline(c)
