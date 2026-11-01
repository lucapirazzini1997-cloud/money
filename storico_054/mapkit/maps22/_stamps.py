"""Cut monuments out of the 0.21 ROM maps and paste them on new canvases as art overlays."""
import collections, struct
import numpy as np
from PIL import Image
import r22

ROM = r22.ROM
DOOR_BEH = {0x60, 0x69, 0x6d, 0x6e, 0x8d}
_cache = {}


def _layers(m):
    key = (m['group'], m['num'])
    if key in _cache:
        return _cache[key]
    prim, sec = ROM.tileset(m['primary']), ROM.tileset(m['secondary'])
    pals = ROM.palettes(prim, sec)
    d = ROM.data
    out = {}

    def get(i):
        if i in out:
            return out[i]
        base = prim['metatiles'] + i * 16 if i < 512 else sec['metatiles'] + (i - 512) * 16
        refs = struct.unpack_from('<8H', d, base)
        layers = []
        for layer in range(2):
            img = np.zeros((16, 16, 4), np.uint8)
            for q in range(4):
                r = refs[layer * 4 + q]; idx = r & 1023
                tl = prim['tiles'] if idx < 512 else sec['tiles']; idx = idx if idx < 512 else idx - 512
                t = tl[idx] if idx < len(tl) else np.zeros((8, 8), np.uint8)
                if r & 0x400: t = t[:, ::-1]
                if r & 0x800: t = t[::-1, :]
                c = pals[r >> 12][t]
                reg = img[(q // 2) * 8:(q // 2) * 8 + 8, (q % 2) * 8:(q % 2) * 8 + 8]
                if layer == 0:
                    reg[..., :3] = c; reg[..., 3] = 255
                else:
                    mask = t != 0
                    reg[mask, :3] = c[mask]; reg[mask, 3] = 255
            layers.append(img)
        attr = ROM.attr(m, i)
        out[i] = (layers[0], layers[1], attr & 0xff, (attr >> 12) & 0xf)
        return out[i]
    _cache[key] = get
    return get


def cut(gn, x0, y0, w, h, bg=None, keep_top=True):
    """Return cells[y][x] = (bottom RGBA or None, top RGBA or None, coll, behavior) for a ROM map region.
    Pixels equal to the background metatiles (most common walkable ones) become transparent."""
    m = ROM.map(*gn)
    a = ROM.blocks(m)
    get = _layers(m)
    if bg is None:
        # ground = walkable metatiles on a ring just outside the cut rectangle
        ring = set()
        for x in range(x0 - 1, x0 + w + 1):
            for y in (y0 - 1, y0 + h):
                ring.add((x, y))
        for y in range(y0 - 1, y0 + h + 1):
            for x in (x0 - 1, x0 + w):
                ring.add((x, y))
        cnt = collections.Counter(int(a[y, x]) & 1023 for (x, y) in ring
                                  if 0 <= x < a.shape[1] and 0 <= y < a.shape[0] and not (int(a[y, x]) & 0xc00))
        bg = [k for k, _ in cnt.most_common(4)]
    bgimgs = [get(b)[0] for b in bg]
    cells = []
    for y in range(y0, y0 + h):
        row = []
        for x in range(x0, x0 + w):
            v = int(a[y, x]); mid = v & 1023; coll = (v >> 10) & 3
            b, t, beh, layer = get(mid)
            b = b.copy(); t = t.copy()
            if layer == 1:      # covered: flatten top into bottom
                msk = t[..., 3] > 0
                b[msk] = t[msk]; t[:] = 0
            if mid in bg and beh not in DOOR_BEH:
                row.append(None); continue
            if beh in DOOR_BEH:
                row.append((Image.fromarray(b, 'RGBA'), None, 0, beh)); continue
            same = np.zeros((16, 16), bool)
            for bi in bgimgs:
                same |= np.all(b[..., :3] == bi[..., :3], axis=-1)
            b[same, 3] = 0
            bi = Image.fromarray(b, 'RGBA') if b[..., 3].any() else None
            ti = Image.fromarray(t, 'RGBA') if (keep_top and t[..., 3].any()) else None
            if bi is None and ti is None:
                row.append(None); continue
            row.append((bi, ti, coll, beh))
        cells.append(row)
    return cells


def paste(cv, x, y, cells, protect=False, solid_all=False):
    door = None
    for cy, row in enumerate(cells):
        for cx, c in enumerate(row):
            if c is None:
                continue
            b, t, coll, beh = c
            X, Y = x + cx, y + cy
            if not (0 <= X < cv.w and 0 <= Y < cv.h):
                continue
            if beh in DOOR_BEH:
                door = (X, Y)
                cv.art[Y][X] = (b, t, 0, 0x60, protect)
                continue
            cv.art[Y][X] = (b, t, 1 if (coll or solid_all) else 0, 0, protect)
    return door


class _St:
    pass


def cervia_torre():
    """Torre San Michele from the 0.21 Cervia map (tower only)."""
    cells = cut((0, 10), 23, 22, 5, 9)
    st = _St(); st.cells = cells; st.anchors = {}
    return st
