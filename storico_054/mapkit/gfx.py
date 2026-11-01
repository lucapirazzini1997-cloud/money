"""Low level helpers for pokeemerald tilesets: loading, per-layer RGBA rendering."""
import re, struct
from pathlib import Path
from PIL import Image

ROOT = Path('/home/claude/proj/sorgenti_romagna')


def u16s(p):
    b = Path(p).read_bytes()
    return list(struct.unpack('<%dH' % (len(b) // 2), b))


def folder_of(name):
    return re.sub(r'(\d)_f(?=$|_)', r'\1f', re.sub(r'(?<!^)(?=[A-Z])', '_', name[9:]).lower())


def read_pal(p):
    lines = Path(p).read_text().split('\n')[3:19]
    return [tuple(int(v) for v in l.split()[:3]) for l in lines if l.strip()]


def write_pal(p, cols):
    cols = list(cols) + [(0, 0, 0)] * (16 - len(cols))
    Path(p).write_text('JASC-PAL\n0100\n16\n' + ''.join('%d %d %d\n' % c for c in cols[:16]))


_cache = {}


class Tileset:
    def __init__(self, name, kind, root=ROOT):
        self.name, self.kind = name, kind
        d = root / 'data/tilesets' / kind / folder_of(name)
        if not d.exists():
            raise FileNotFoundError(d)
        self.dir = d
        img = Image.open(d / 'tiles.png')
        if img.mode != 'P':
            img = img.convert('P')
        w, h = img.size
        raw = img.tobytes()
        self.tiles = []
        for t in range((w // 8) * (h // 8)):
            tx, ty = (t % (w // 8)) * 8, (t // (w // 8)) * 8
            self.tiles.append(tuple(raw[(ty + y) * w + tx + x] & 15 for y in range(8) for x in range(8)))
        self.pals = []
        for i in range(16):
            pp = d / 'palettes' / ('%02d.pal' % i)
            self.pals.append(read_pal(pp) if pp.exists() else [(0, 0, 0)] * 16)
        self.metas = u16s(d / 'metatiles.bin')
        self.attrs = u16s(d / 'metatile_attributes.bin')

    @property
    def nmeta(self):
        return len(self.metas) // 8


def tileset(name, kind):
    k = (name, kind)
    if k not in _cache:
        _cache[k] = Tileset(name, kind, root=ROOT)
    return _cache[k]


class Pair:
    """A primary+secondary pair as the engine sees it."""
    def __init__(self, prim, sec):
        self.p = tileset(prim, 'primary') if isinstance(prim, str) else prim
        self.s = tileset(sec, 'secondary') if isinstance(sec, str) else sec
        self.pals = self.p.pals[:6] + self.s.pals[6:13] + self.p.pals[13:16]
        self._layer_cache = {}

    def tile_pixels(self, ti):
        if ti < 512:
            return self.p.tiles[ti] if ti < len(self.p.tiles) else (0,) * 64
        ti -= 512
        return self.s.tiles[ti] if ti < len(self.s.tiles) else (0,) * 64

    def entry(self, mid, k):
        if mid < 512:
            arr, off = self.p.metas, mid * 8
        else:
            arr, off = self.s.metas, (mid - 512) * 8
        if off + k >= len(arr):
            return 0
        return arr[off + k]

    def attr(self, mid):
        if mid < 512:
            a = self.p.attrs
            return a[mid] if mid < len(a) else 0
        a = self.s.attrs
        return a[mid - 512] if mid - 512 < len(a) else 0

    def layer_rgba(self, mid, layer):
        """16x16 RGBA image of one layer (0 bottom, 1 top); index 0 is transparent."""
        key = (mid, layer)
        if key in self._layer_cache:
            return self._layer_cache[key]
        im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
        px = im.load()
        for q in range(4):
            e = self.entry(mid, layer * 4 + q)
            ti, hf, vf, pal = e & 0x3FF, (e >> 10) & 1, (e >> 11) & 1, e >> 12
            t = self.tile_pixels(ti)
            ox, oy = (q % 2) * 8, (q // 2) * 8
            for y in range(8):
                for x in range(8):
                    c = t[(7 - y if vf else y) * 8 + (7 - x if hf else x)]
                    if c:
                        r, g, b = self.pals[pal][c] if pal < len(self.pals) else (255, 0, 255)
                        px[ox + x, oy + y] = (r, g, b, 255)
        self._layer_cache[key] = im
        return im

    def render(self, mid):
        """Composite as seen in game over the backdrop colour."""
        bg = self.pals[0][0]
        im = Image.new('RGBA', (16, 16), bg + (255,))
        im.alpha_composite(self.layer_rgba(mid, 0))
        im.alpha_composite(self.layer_rgba(mid, 1))
        return im.convert('RGB')
