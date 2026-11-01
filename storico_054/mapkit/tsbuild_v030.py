"""Build a secondary tileset (on top of an existing primary, normally General) from RGBA metatile definitions.

Every metatile is described by two 16x16 RGBA layers plus behaviour/layer type.  The builder:
  * reuses primary tiles when an 8x8 quadrant matches a primary tile+palette exactly (flips included),
  * packs the remaining tiles into the 7 secondary palettes (6..12), merging colours if needed,
  * dedupes tiles (with flips) and metatiles, and writes the pokeemerald files.
"""
import math, itertools
from pathlib import Path
from collections import Counter, defaultdict
from PIL import Image
import gfx

TRANSPARENT = None


def q5(c):
    """Snap an RGB colour to what the GBA can show (5 bits per channel) using pokeemerald's pal convention."""
    return tuple(min(255, (v >> 3) << 3) for v in c)


class Meta:
    __slots__ = ('bottom', 'top', 'behavior', 'layer', 'name', 'coll', 'elev', 'src', 'palkeys', 'protect')

    def __init__(self, bottom, top=None, behavior=0, layer=0, name=None, coll=0, elev=3, src=None, palkeys=None):
        self.bottom = bottom.convert('RGBA') if bottom is not None else Image.new('RGBA', (16, 16), (0, 0, 0, 0))
        self.top = top.convert('RGBA') if top is not None else Image.new('RGBA', (16, 16), (0, 0, 0, 0))
        self.behavior, self.layer, self.name, self.coll, self.elev, self.src = behavior, layer, name, coll, elev, src
        # one palette-group key per quadrant (8 entries: bottom TL..BR, top TL..BR); tiles sharing a key are packed together
        self.palkeys = palkeys if palkeys is not None else [palkeys] * 8
        self.protect = False


def meta_from(pair, mid, **kw):
    a = pair.attr(mid)
    keys = []
    for k in range(8):
        pal = pair.entry(mid, k) >> 12
        keys.append((pair.s.name if 6 <= pal < 13 else pair.p.name, pal))
    m = Meta(pair.layer_rgba(mid, 0), pair.layer_rgba(mid, 1), behavior=a & 0xFF, layer=(a >> 12) & 0xF, src=(pair, mid), palkeys=keys)
    for k, v in kw.items():
        setattr(m, k, v)
    return m


def quads(im):
    px = im.load()
    out = []
    for q in range(4):
        ox, oy = (q % 2) * 8, (q // 2) * 8
        out.append(tuple((px[ox + x, oy + y][:3] if px[ox + x, oy + y][3] >= 128 else None) for y in range(8) for x in range(8)))
    return out


def flip(t, h, v):
    return tuple(t[(7 - y if v else y) * 8 + (7 - x if h else x)] for y in range(8) for x in range(8))


class PrimaryIndex:
    """Exact lookup of 8x8 RGB(+transparency) tiles in a primary tileset under its palettes 0..5."""
    def __init__(self, prim_name):
        self.p = gfx.tileset(prim_name, 'primary')
        self.lut = {}
        for ti, t in enumerate(self.p.tiles[:512]):
            if not any(t):
                continue
            for pal in range(6):
                cols = self.p.pals[pal]
                rgb = tuple(q5(cols[c]) if c else None for c in t)
                for h, v in ((0, 0), (1, 0), (0, 1), (1, 1)):
                    k = flip(rgb, h, v)
                    if k not in self.lut:
                        self.lut[k] = (ti, h, v, pal)

    def find(self, rgbtile):
        return self.lut.get(rgbtile)


def cdist(a, b):
    # perceptual-ish weighted distance
    rm = (a[0] + b[0]) / 2
    dr, dg, db = a[0] - b[0], a[1] - b[1], a[2] - b[2]
    return math.sqrt((2 + rm / 256) * dr * dr + 4 * dg * dg + (2 + (255 - rm) / 256) * db * db)


def pack_palettes(colorsets, npal=7, size=15):
    """Greedy bin packing of colour sets into palettes. Returns list of palettes (sets) and assignment list, or None."""
    uniq = sorted(set(colorsets), key=lambda s: (-len(s), sorted(s)))
    # drop sets that are subsets of others handled later naturally
    pals = []
    for s in uniq:
        best, bestcost = None, None
        for i, p in enumerate(pals):
            u = p | s
            if len(u) <= size:
                cost = len(u) - len(p)
                if bestcost is None or cost < bestcost:
                    best, bestcost = i, cost
        if best is None:
            if len(pals) >= npal:
                return None
            pals.append(set(s))
        else:
            pals[best] |= s
    assign = {}
    for s in set(colorsets):
        cands = [i for i, p in enumerate(pals) if s <= p]
        assign[s] = min(cands, key=lambda i: len(pals[i]))
    return pals, assign


def reduce_colors(tiles, target):
    """Merge closest colours (weighted by usage) until the number of distinct colours <= target."""
    usage = Counter(c for t in tiles for c in t if c is not None)
    cols = list(usage)
    mapping = {c: c for c in cols}
    while len(cols) > target:
        best = None
        for i in range(len(cols)):
            for j in range(i + 1, len(cols)):
                d = cdist(cols[i], cols[j])
                if best is None or d < best[0]:
                    best = (d, i, j)
        _, i, j = best
        a, b = cols[i], cols[j]
        keep, drop = (a, b) if usage[a] >= usage[b] else (b, a)
        usage[keep] += usage[drop]
        for k, v in mapping.items():
            if v == drop:
                mapping[k] = keep
        cols.remove(drop)
    return mapping


def tile_reduce_colors(t, maxc=15):
    cs = set(c for c in t if c is not None)
    if len(cs) <= maxc:
        return t
    m = reduce_colors([t], maxc)
    return tuple(m[c] if c is not None else None for c in t)


class BuildError(Exception):
    pass


def enc(tile, h, v, pal):
    """Internal wide metatile entry (tile index is not limited to 10 bits until the final pack)."""
    return tile | (h << 16) | (v << 17) | (pal << 18)


def dec(e):
    return e & 0xFFFF, (e >> 16) & 1, (e >> 17) & 1, e >> 18


def pack16(e):
    t, h, v, p = dec(e)
    if t >= 1024:
        raise BuildError('tile index overflow %d' % t)
    return t | (h << 10) | (v << 11) | (p << 12)


def reduce_tiles(tiles_out, meta_entries, palcols, max_tiles, verbose=True, protected=()):
    """Lossy: merge the most similar secondary tiles until the budget fits. Mutates tiles_out."""
    import numpy as np
    n = len(tiles_out)
    # palette + usage of each tile from its first use
    first_pal = {}
    usage = Counter()
    for ents, _ in meta_entries:
        for e in ents:
            ti, _h, _v, pal = dec(e)
            if ti >= 512:
                usage[ti - 512] += 1
                first_pal.setdefault(ti - 512, pal)
    def rgb(i, h=0, v=0):
        pal = first_pal.get(i, 6) - 6
        cols = [(0, 0, 0)] + list(palcols[pal]) if 0 <= pal < len(palcols) else [(0, 0, 0)] * 16
        t = flip(tiles_out[i], h, v)
        out = []
        for c in t:
            out.extend(cols[c] if c < len(cols) else (0, 0, 0))
            out.append(255 if c else 0)  # transparency as a channel
        return out
    idx = list(range(1, n))  # tile 0 (blank) is fixed
    A = np.array([rgb(i) for i in idx], dtype=np.float32)
    flips = [(0, 0), (1, 0), (0, 1), (1, 1)]
    B = [np.array([rgb(i, h, v) for i in idx], dtype=np.float32) for h, v in flips]
    na = (A ** 2).sum(1)
    D = np.full((len(idx), len(idx)), np.inf, dtype=np.float32)
    F = np.zeros((len(idx), len(idx)), dtype=np.int8)
    for k, Bk in enumerate(B):
        nb = (Bk ** 2).sum(1)
        d = na[:, None] + nb[None, :] - 2 * A @ Bk.T
        better = d < D
        D[better] = d[better]
        F[better] = k
    np.fill_diagonal(D, np.inf)
    for k, t in enumerate(idx):
        if t in protected:
            D[k, :] = np.inf
    w = np.array([max(1, usage[i]) for i in idx], dtype=np.float32)
    D = D * w[:, None]          # removing a heavily used tile costs more
    alive = np.ones(len(idx), bool)
    redirect = {}
    excess = n - max_tiles
    for _ in range(excess):
        i, j = np.unravel_index(np.argmin(D), D.shape)
        if not np.isfinite(D[i, j]):
            raise RuntimeError('tileset over budget even after merging (too many protected tiles)')
        # i (row) is replaced by j's flipped variant: rgb(i) ~ flip(rgb(j))
        redirect[idx[i]] = (idx[j], flips[F[i, j]])
        alive[i] = False
        D[i, :] = np.inf
        D[:, i] = np.inf
    def resolve(t, h, v):
        while t in redirect:
            t2, (fh, fv) = redirect[t]
            t, h, v = t2, h ^ fh, v ^ fv
        return t, h, v
    keep = [0] + [idx[k] for k in range(len(idx)) if alive[k]]
    newpos = {t: i for i, t in enumerate(keep)}
    new_entries = []
    for ents, attr in meta_entries:
        ne = []
        for e in ents:
            ti, h0, v0, p0 = dec(e)
            if ti >= 512:
                t, h, v = resolve(ti - 512, h0, v0)
                pal = p0 if t == ti - 512 else first_pal.get(t, p0)
                e = enc(512 + newpos[t], h, v, pal)
            ne.append(e)
        new_entries.append((tuple(ne), attr))
    kept = [tiles_out[t] for t in keep]
    tiles_out[:] = kept
    if verbose:
        print('  tile reduction: merged %d similar tiles' % excess)
    return new_entries


def build(metas, out_dir, prim_name='gTileset_General', max_tiles=512, max_metas=512, verbose=True):
    """Encode metas into a secondary tileset at out_dir. Returns list of metatile ids (512+) parallel to metas."""
    out_dir = Path(out_dir)
    pidx = PrimaryIndex(prim_name)
    prim = gfx.tileset(prim_name, 'primary')

    # 1. collect quadrant tiles
    layer_tiles = []  # per meta: 8 tiles (rgb tuples)
    for m in metas:
        b = quads(m.bottom)
        t = quads(m.top)
        layer_tiles.append([tuple(q5(c) if c else None for c in x) for x in b + t])

    new_tiles, new_keys = [], []
    for m, lt in zip(metas, layer_tiles):
        for k, t in enumerate(lt):
            if all(c is None for c in t) or pidx.find(t) is not None:
                continue
            new_tiles.append(t)
            key = m.palkeys[k]
            new_keys.append(key if key is not None else ('tile', t))
    # 2. palette assignment: agglomerative clustering of tile colour groups into 7 palettes,
    #    then per-palette weighted k-means when a palette needs more than 15 colours.
    groups = {}          # gid -> Counter(colour -> pixels)
    tile_gid = []
    keymap = {}
    for t, key in zip(new_tiles, new_keys):
        if key is None or key[0] == 'tile':
            key = ('set', frozenset(c for c in t if c is not None))
        if key not in keymap:
            keymap[key] = len(keymap)
            groups[keymap[key]] = Counter()
        g = keymap[key]
        groups[g].update(c for c in t if c is not None)
        tile_gid.append(g)
    parent = {g: g for g in groups}

    def find(g):
        while parent[g] != g:
            parent[g] = parent[parent[g]]
            g = parent[g]
        return g

    def cost(a, b):
        A, B = groups[a], groups[b]
        U = set(A) | set(B)
        if len(U) <= 15:
            return len(U) - max(len(A), len(B))
        w = A + B
        cols = sorted(U, key=lambda c: w[c])
        extra = len(U) - 15
        err = 0.0
        for c in cols[:extra]:
            d = min(cdist(c, o) for o in U if o != c)
            err += w[c] * d
        return 1000 + err

    import heapq
    live = set(groups)
    heap = []
    ids = sorted(live)
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            heapq.heappush(heap, (cost(a, b), a, b))
    nextg = max(groups) + 1 if groups else 0
    while len(live) > 7 or (heap and heap[0][0] <= 0 and len(live) > 1):
        if not heap:
            break
        c, a, b = heapq.heappop(heap)
        if a not in live or b not in live:
            continue
        if len(live) <= 7 and c > 0:
            break
        g = nextg; nextg += 1
        groups[g] = groups[a] + groups[b]
        parent[g] = g
        parent[a] = g; parent[b] = g
        live.discard(a); live.discard(b)
        for o in live:
            heapq.heappush(heap, (cost(g, o), g, o))
        live.add(g)
    final = sorted(live)
    if len(final) > 7:
        raise BuildError('palette clustering failed')
    # quantise each palette to <= 15 colours (weighted k-means, deterministic init)
    pal_map = {}     # final gid -> {colour: palette colour}
    palcols = []
    for g in final:
        w = groups[g]
        cols = list(w)
        if len(cols) <= 15:
            centers = cols
            mapping = {c: c for c in cols}
        else:
            centers = sorted(cols, key=lambda c: -w[c])[:15]
            for _ in range(12):
                buckets = defaultdict(list)
                for c in cols:
                    k = min(range(len(centers)), key=lambda i: cdist(c, centers[i]))
                    buckets[k].append(c)
                newc = []
                for i, cen in enumerate(centers):
                    bl = buckets.get(i)
                    if not bl:
                        newc.append(cen); continue
                    tw = sum(w[c] for c in bl)
                    avg = tuple(int(sum(c[j] * w[c] for c in bl) / tw) for j in range(3))
                    # snap to the nearest real member colour to keep the art crisp
                    newc.append(min(bl, key=lambda c: cdist(c, avg)))
                if newc == centers:
                    break
                centers = newc
            mapping = {c: min(centers, key=lambda k: cdist(c, k)) for c in cols}
            if verbose:
                print('  palette quantised: %d -> 15 colours' % len(cols))
        pal_map[g] = mapping
        palcols.append(sorted(set(mapping.values())))
    palidx = [{c: i + 1 for i, c in enumerate(pc)} for pc in palcols]
    final_index = {g: i for i, g in enumerate(final)}
    tile_pal = {}
    for t, g0 in zip(new_tiles, tile_gid):
        tile_pal[t] = find(g0)

    # 3. encode tiles
    tiles_out = [(0,) * 64]  # secondary tile 0 = blank
    tile_lut = {}

    def add_tile(idx, pal):
        # tiles are deduped per palette so that a lossy merge never recolours another use
        for h, v in ((0, 0), (1, 0), (0, 1), (1, 1)):
            k = (flip(idx, h, v), pal)
            if k in tile_lut:
                ti, h0, v0 = tile_lut[k]
                return ti, h ^ h0, v ^ v0
        tiles_out.append(idx)
        ti = len(tiles_out) - 1
        tile_lut[(idx, pal)] = (ti, 0, 0)
        return ti, 0, 0

    meta_entries = []
    for m, lt in zip(metas, layer_tiles):
        ents = []
        for t in lt:
            if all(c is None for c in t):
                ents.append(0)
                continue
            f = pidx.find(t)
            if f is not None:
                ti, h, v, pal = f
                ents.append(enc(ti, h, v, pal))
                continue
            g = tile_pal[t]
            pi = final_index[g]
            mp = pal_map[g]
            idx = tuple(palidx[pi][mp[c]] if c is not None else 0 for c in t)
            ti, h, v = add_tile(idx, pi)
            ents.append(enc(512 + ti, h, v, 6 + pi))
        meta_entries.append((tuple(ents), (m.behavior & 0xFF) | ((m.layer & 0xF) << 12)))
    if len(tiles_out) > max_tiles:
        prot = set()
        for m, (ents, _) in zip(metas, meta_entries):
            if getattr(m, 'protect', False):
                prot.update(dec(e)[0] - 512 for e in ents if dec(e)[0] >= 512)
        if verbose: print('  tiles before reduction: %d, protected: %d' % (len(tiles_out), len(prot)))
        meta_entries = reduce_tiles(tiles_out, meta_entries, palcols, max_tiles, verbose, prot)

    # 4. dedupe metatiles
    ids = []
    uniq = {}
    order = []
    for e in meta_entries:
        if e not in uniq:
            uniq[e] = 512 + len(order)
            order.append(e)
        ids.append(uniq[e])
    if len(order) > max_metas:
        raise BuildError('too many metatiles: %d > %d' % (len(order), max_metas))

    # 5. write
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / 'palettes').mkdir(exist_ok=True)
    n = len(tiles_out)
    rows = (n + 15) // 16
    img = Image.new('P', (128, rows * 8), 0)
    img.putpalette(sum(([i * 16, i * 16, i * 16] for i in range(16)), []) + [0] * (240 * 3))
    px = img.load()
    for i, t in enumerate(tiles_out):
        tx, ty = (i % 16) * 8, (i // 16) * 8
        for y in range(8):
            for x in range(8):
                px[tx + x, ty + y] = t[y * 8 + x]
    img.save(out_dir / 'tiles.png')
    for i in range(16):
        if 6 <= i < 6 + len(palcols):
            cols = [(0, 0, 0)] + palcols[i - 6]
            # colour 0: use a neutral transparent key
            cols[0] = (255, 0, 255)
        elif i < 6 or i >= 13:
            cols = prim.pals[i]
        else:
            cols = [(0, 0, 0)] * 16
        gfx.write_pal(out_dir / 'palettes' / ('%02d.pal' % i), cols)
    import struct
    (out_dir / 'metatiles.bin').write_bytes(b''.join(struct.pack('<8H', *[pack16(x) for x in e[0]]) for e in order))
    (out_dir / 'metatile_attributes.bin').write_bytes(b''.join(struct.pack('<H', e[1]) for e in order))
    if verbose:
        print('  %s: %d tiles, %d metatiles, %d palettes' % (out_dir.name, n, len(order), len(palcols)))
    return ids
