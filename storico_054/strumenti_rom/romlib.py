"""Binary map toolkit for Pokemon Romagna 0.21+ (pokeemerald-derived ROM, no sources)."""
import struct, numpy as np
from functools import lru_cache
from PIL import Image, ImageDraw

B = 0x08000000
GROUPS = 24272696          # expanded gMapGroups (36 groups)
GROUP_SIZES = None


def u16(d, p): return struct.unpack_from('<H', d, p)[0]
def u32(d, p): return struct.unpack_from('<I', d, p)[0]


class Rom:
    def __init__(self, path_or_bytes):
        self.data = bytearray(open(path_or_bytes, 'rb').read() if isinstance(path_or_bytes, str) else path_or_bytes)

    def ptr(self, p):
        v = u32(self.data, p)
        return v - B if v >= B else None

    # ---------------- maps
    def header(self, g, n):
        return self.ptr(self.ptr(GROUPS + g * 4) + n * 4)

    def map(self, g, n):
        d = self.data
        hp = self.header(g, n)
        lp, ep, sp, cp = (self.ptr(hp + i) for i in (0, 4, 8, 12))
        m = dict(group=g, num=n, header=hp, layout=lp, events=ep, scripts=sp, connections=cp,
                 music=u16(d, hp + 16), layout_id=u16(d, hp + 18), region=d[hp + 20], cave=d[hp + 21],
                 weather=d[hp + 22], type=d[hp + 23], flags=d[hp + 26], battle=d[hp + 27])
        m['width'], m['height'] = u32(d, lp), u32(d, lp + 4)
        m['border'], m['blocks'], m['primary'], m['secondary'] = (self.ptr(lp + i) for i in (8, 12, 16, 20))
        m.update(self.events(ep))
        m['conns'] = []
        if cp:
            cnt, lst = u32(d, cp), self.ptr(cp + 4)
            for i in range(cnt):
                dirn, off, mg, mn = struct.unpack_from('<IiBB', d, lst + i * 12)
                m['conns'].append(dict(dir=dirn, offset=off, group=mg, num=mn))
        return m

    def events(self, ep):
        d = self.data
        no, nw, nc, nb = d[ep:ep + 4]
        op, wp, cp, bp = (self.ptr(ep + 4 + i * 4) for i in range(4))
        objs = []
        for i in range(no):
            p = op + i * 24
            objs.append(dict(id=d[p], gfx=d[p + 1], kind=d[p + 2], x=struct.unpack_from('<h', d, p + 4)[0],
                             y=struct.unpack_from('<h', d, p + 6)[0], elev=d[p + 8], move=d[p + 9],
                             rx=d[p + 10] & 15, ry=d[p + 10] >> 4, ttype=u16(d, p + 12), trange=u16(d, p + 14),
                             script=self.ptr(p + 16), flag=u16(d, p + 20), raw=bytes(d[p:p + 24])))
        warps = []
        for i in range(nw):
            p = wp + i * 8
            x, y = struct.unpack_from('<hh', d, p)
            warps.append(dict(x=x, y=y, elev=d[p + 4], warp=d[p + 5], num=d[p + 6], group=d[p + 7]))
        coords = []
        for i in range(nc):
            p = cp + i * 16
            x, y = struct.unpack_from('<hh', d, p)
            coords.append(dict(x=x, y=y, elev=d[p + 4], var=u16(d, p + 6), val=u16(d, p + 8), script=self.ptr(p + 12)))
        bgs = []
        for i in range(nb):
            p = bp + i * 12
            x, y = struct.unpack_from('<hh', d, p)
            bgs.append(dict(x=x, y=y, elev=d[p + 4], kind=d[p + 5], arg=u32(d, p + 8)))
        return dict(objects=objs, warps=warps, coords=coords, bgs=bgs)

    def blocks(self, m):
        return np.frombuffer(bytes(self.data[m['blocks']:m['blocks'] + m['width'] * m['height'] * 2]),
                             dtype='<u2').reshape(m['height'], m['width']).copy()

    def map_scripts(self, m):
        d = self.data; out = []; p = m['scripts']
        if p is None: return out
        while d[p]:
            out.append((d[p], self.ptr(p + 1))); p += 5
        return out

    # ---------------- graphics
    def lz(self, p):
        d = self.data
        assert d[p] == 0x10, hex(p)
        n = int.from_bytes(d[p + 1:p + 4], 'little'); p += 4; out = bytearray()
        while len(out) < n:
            fl = d[p]; p += 1
            for bit in range(7, -1, -1):
                if len(out) >= n: break
                if fl & (1 << bit):
                    a, b = d[p], d[p + 1]; p += 2
                    k = (a >> 4) + 3; disp = ((a & 15) << 8) + b + 1
                    for _ in range(k): out.append(out[-disp])
                else:
                    out.append(d[p]); p += 1
        return bytes(out[:n])

    def tileset(self, tp):
        d = self.data
        comp = d[tp]; gp, pp, mp, ap = (self.ptr(tp + i) for i in (4, 8, 12, 16))
        raw = self.lz(gp) if comp else bytes(d[gp:gp + 0x4000])
        a = np.frombuffer(raw, dtype=np.uint8)
        px = np.empty(len(a) * 2, dtype=np.uint8); px[::2] = a & 15; px[1::2] = a >> 4
        return dict(tiles=px.reshape(-1, 8, 8), pals=pp, metatiles=mp, attrs=ap, primary=d[tp + 1] == 0)

    def palettes(self, prim, sec):
        d = self.data
        raw = bytes(d[prim['pals']:prim['pals'] + 192]) + bytes(d[sec['pals'] + 192:sec['pals'] + 512])
        v = np.frombuffer(raw, dtype='<u2')
        rgb = np.stack([v & 31, (v >> 5) & 31, (v >> 10) & 31], -1)
        return ((rgb * 255 + 15) // 31).astype(np.uint8).reshape(16, 16, 3)

    def renderer(self, m):
        prim, sec = self.tileset(m['primary']), self.tileset(m['secondary'])
        pals = self.palettes(prim, sec)
        d = self.data
        cache = {}

        def mt(i):
            if i in cache: return cache[i]
            base = prim['metatiles'] + i * 16 if i < 512 else sec['metatiles'] + (i - 512) * 16
            refs = struct.unpack_from('<8H', d, base)
            img = np.zeros((16, 16, 3), np.uint8)
            for layer in range(2):
                for q in range(4):
                    r = refs[layer * 4 + q]; idx = r & 1023
                    tl = prim['tiles'] if idx < 512 else sec['tiles']; idx = idx if idx < 512 else idx - 512
                    t = tl[idx] if idx < len(tl) else np.zeros((8, 8), np.uint8)
                    if r & 0x400: t = t[:, ::-1]
                    if r & 0x800: t = t[::-1, :]
                    c = pals[r >> 12][t]
                    reg = img[(q // 2) * 8:(q // 2) * 8 + 8, (q % 2) * 8:(q % 2) * 8 + 8]
                    if layer == 0: reg[:] = c
                    else: reg[t != 0] = c[t != 0]
            cache[i] = img
            return img
        return mt

    def attr(self, m, i):
        ts = m['primary'] if i < 512 else m['secondary']
        ap = self.ptr(ts + 16)
        return u16(self.data, ap + (i if i < 512 else i - 512) * 2)

    def render(self, m, events=True, scale=1, grid=False):
        a = self.blocks(m); mt = self.renderer(m)
        H, W = a.shape
        img = np.zeros((H * 16, W * 16, 3), np.uint8)
        for y in range(H):
            for x in range(W):
                img[y * 16:y * 16 + 16, x * 16:x * 16 + 16] = mt(int(a[y, x]) & 1023)
        im = Image.fromarray(img)
        if events:
            dr = ImageDraw.Draw(im)
            for i, o in enumerate(m['objects']):
                dr.rectangle((o['x'] * 16, o['y'] * 16, o['x'] * 16 + 15, o['y'] * 16 + 15), outline='#ff0', width=2)
                dr.text((o['x'] * 16 + 2, o['y'] * 16 + 2), str(i + 1), fill='#f00')
            for i, w in enumerate(m['warps']):
                dr.rectangle((w['x'] * 16, w['y'] * 16, w['x'] * 16 + 15, w['y'] * 16 + 15), outline='#0ff', width=2)
                dr.text((w['x'] * 16 + 2, w['y'] * 16 + 2), 'w%d' % i, fill='#00f')
            for c in m['coords']:
                dr.rectangle((c['x'] * 16 + 4, c['y'] * 16 + 4, c['x'] * 16 + 11, c['y'] * 16 + 11), outline='#f0f', width=2)
            for b in m['bgs']:
                dr.rectangle((b['x'] * 16 + 2, b['y'] * 16 + 2, b['x'] * 16 + 13, b['y'] * 16 + 13), outline='#0f0', width=2)
        if grid:
            dr = ImageDraw.Draw(im)
            for x in range(0, W, 5): dr.line((x * 16, 0, x * 16, H * 16), fill=(255, 255, 255) if x % 10 == 0 else (120, 120, 120))
            for y in range(0, H, 5): dr.line((0, y * 16, W * 16, y * 16), fill=(255, 255, 255) if y % 10 == 0 else (120, 120, 120))
        if scale != 1: im = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
        return im


COUNTS = {0: 57, 1: 5, 2: 5, 3: 6, 4: 7, 5: 8, 6: 9, 7: 7, 8: 7, 9: 14, 10: 8, 11: 17, 12: 10, 13: 23, 14: 13, 15: 15, 16: 15, 17: 2, 18: 2, 19: 2, 20: 3, 21: 1, 22: 1, 23: 1, 24: 108, 25: 61, 26: 89, 27: 2, 28: 1, 29: 13, 30: 1, 31: 1, 32: 3, 33: 110, 34: 118, 35: 35}


def all_maps(rom):
    return {(g, n): rom.map(g, n) for g, c in COUNTS.items() for n in range(c)}
