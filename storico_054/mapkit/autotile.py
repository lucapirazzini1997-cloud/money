"""Data-driven terrain autotiling learned from vanilla Hoenn maps (General primary only).

Each General metatile gets a terrain class by pixel colour majority. From vanilla maps we learn, for every
3x3 neighbourhood of classes, which General metatile the designers placed in the centre. To paint a map we
describe terrain per cell and look the tiles up.
"""
import json, pickle, sys
from pathlib import Path
from collections import Counter, defaultdict
sys.path.insert(0, str(Path(__file__).parent))
import gfx

CACHE = Path(__file__).parent / 'autotile_cache.pkl'

# reference pure metatiles for each class (General ids)
REF = {
    'grass': [0x001],
    'sand': [0x121, 0x124],
    'sea': [0x170, 0x171],
    'shallow': [0x19E],
    'pond': [0x0A1, 0x0D1],
    'rock': [0x173, 0x17B],
    'dirt': [0x10C],
    'ash': [0x109],
}
CLASSES = list(REF)


class Classifier:
    def __init__(self):
        self.pair = gfx.Pair('gTileset_General', 'gTileset_Petalburg')
        self.colclass = {}
        for cls, ids in REF.items():
            for mid in ids:
                im = self.pair.render(mid).load()
                for y in range(16):
                    for x in range(16):
                        self.colclass.setdefault(im[x, y], cls)
        self.refcols = list(self.colclass.items())
        self.cache = {}

    def classify_rgb(self, im):
        px = im.load()
        cnt = Counter()
        for y in range(16):
            for x in range(16):
                c = px[x, y][:3]
                k = self.colclass.get(c)
                if k is None:
                    # nearest reference colour, only if close
                    best = min(self.refcols, key=lambda rc: sum((a - b) ** 2 for a, b in zip(rc[0], c)))
                    if sum((a - b) ** 2 for a, b in zip(best[0], c)) < 900:
                        k = best[1]
                    else:
                        k = 'other'
                cnt[k] += 1
        return cnt

    def classify(self, pair, mid):
        key = (pair.s.name if mid >= 512 else '', mid)
        if key not in self.cache:
            cnt = self.classify_rgb(pair.render(mid))
            top, n = cnt.most_common(1)[0]
            pure = (256 - cnt['other']) / 256.0
            self.cache[key] = (top, pure, dict(cnt))
        return self.cache[key]


def learn():
    R = gfx.ROOT
    layouts = json.load(open(R / 'data/layouts/layouts.json'))['layouts']
    clf = Classifier()
    table = defaultdict(Counter)
    for l in layouts:
        if l['primary_tileset'] != 'gTileset_General':
            continue
        if 'ROMAGNA' in l['id'] or l['id'] in ('LAYOUT_LITTLEROOT_TOWN', 'LAYOUT_OLDALE_TOWN', 'LAYOUT_ROUTE101'):
            continue
        p = R / l['blockdata_filepath']
        if not p.exists():
            continue
        try:
            pair = gfx.Pair('gTileset_General', l['secondary_tileset'])
        except FileNotFoundError:
            continue
        b = gfx.u16s(p)
        w, h = l['width'], l['height']
        cls = [clf.classify(pair, v & 0x3FF)[0] for v in b]
        for y in range(1, h - 1):
            for x in range(1, w - 1):
                v = b[y * w + x]
                mid = v & 0x3FF
                if mid >= 512:
                    continue
                c, pure, _ = clf.classify(pair, mid)
                if pure < 0.9:
                    continue
                ctx = tuple(cls[(y + dy) * w + x + dx] for dy in (-1, 0, 1) for dx in (-1, 0, 1))
                table[ctx][v] += 1
    data = {'table': dict(table), 'classes': {k: v for k, v in clf.cache.items() if k[0] == ''}}
    pickle.dump(data, open(CACHE, 'wb'))
    return data


_data = None


def data():
    global _data
    if _data is None:
        _data = pickle.load(open(CACHE, 'rb')) if CACHE.exists() else learn()
    return _data


W = [1, 2, 1, 2, 8, 2, 1, 2, 1]


def lookup(ctx, allowed=None):
    """Return the most likely map value (metatile|bits) for a 3x3 class context."""
    t = data()['table']
    if ctx in t:
        c = t[ctx]
        if allowed:
            c = Counter({k: n for k, n in c.items() if (k & 0x3FF) in allowed}) or c
        return c.most_common(1)[0][0], 0
    # relaxed: find contexts with same centre maximising weighted agreement
    best, bs = None, -1
    for k, c in t.items():
        if k[4] != ctx[4]:
            continue
        if best is None:
            best, bs = k, sum(w for w, a, b in zip(W, k, ctx) if a == b)
            continue
        s = sum(w for w, a, b in zip(W, k, ctx) if a == b)
        if s > bs or (s == bs and sum(c.values()) > sum(t[best].values())):
            best, bs = k, s
    if best is None:
        return REF[ctx[4]][0] if ctx[4] in REF else 0x001, 99
    return t[best].most_common(1)[0][0], sum(W) - bs


def paint(classes, w, h, edge='same'):
    """classes: list of class names per cell (len w*h). Returns list of map values."""
    out = []
    misses = 0
    for y in range(h):
        for x in range(w):
            ctx = []
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    xx, yy = x + dx, y + dy
                    if 0 <= xx < w and 0 <= yy < h:
                        ctx.append(classes[yy * w + xx])
                    else:
                        ctx.append(classes[y * w + x] if edge == 'same' else edge)
            v, miss = lookup(tuple(ctx))
            misses += miss > 0
            out.append(v)
    return out, misses


if __name__ == '__main__':
    d = learn()
    print(len(d['table']), 'contexts')
    cnt = Counter(v[0] for v in d['classes'].values())
    print(cnt)
