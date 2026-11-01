"""Extract buildings/monuments from the 0.12 maps as reusable stamps."""
import json, sys
from pathlib import Path
from collections import Counter, deque
from PIL import Image, ImageDraw
sys.path.insert(0, str(Path(__file__).parent))
import gfx, tsbuild

# Read-only snapshot of the 0.12 sources (we overwrite the working tree later)
SNAP = Path('/home/claude/proj/snap012')


def old_layout(mapname):
    mj = json.loads((SNAP / 'data/maps' / mapname / 'map.json').read_text())
    L = {l['id']: l for l in json.loads((SNAP / 'data/layouts/layouts.json').read_text())['layouts']}
    l = L[mj['layout']]
    vals = gfx.u16s(SNAP / l['blockdata_filepath'])
    pair = gfx.Pair(gfx.Tileset(l['primary_tileset'], 'primary', SNAP), gfx.Tileset(l['secondary_tileset'], 'secondary', SNAP))
    return mj, l, vals, pair


def components(mapname, background):
    """Connected components (8-neighbour) of cells whose metatile id is not in background."""
    mj, l, vals, pair = old_layout(mapname)
    w, h = l['width'], l['height']
    fg = [[(vals[y * w + x] & 0x3FF) not in background for x in range(w)] for y in range(h)]
    seen = set()
    comps = []
    for y in range(h):
        for x in range(w):
            if fg[y][x] and (x, y) not in seen:
                q = deque([(x, y)]); seen.add((x, y)); cells = []
                while q:
                    cx, cy = q.popleft(); cells.append((cx, cy))
                    for dx in (-1, 0, 1):
                        for dy in (-1, 0, 1):
                            nx, ny = cx + dx, cy + dy
                            if 0 <= nx < w and 0 <= ny < h and fg[ny][nx] and (nx, ny) not in seen:
                                seen.add((nx, ny)); q.append((nx, ny))
                xs = [c[0] for c in cells]; ys = [c[1] for c in cells]
                comps.append(dict(x=min(xs), y=min(ys), w=max(xs) - min(xs) + 1, h=max(ys) - min(ys) + 1, n=len(cells), cells=set(cells)))
    return comps


class BgMatcher:
    """Separates building pixels from the old ground texture inside a metatile."""
    def __init__(self, pair, bg_ids):
        self.refs = [pair.render(b).load() for b in bg_ids]

    def mask(self, im):
        px = im.load()
        best = None
        for r in self.refs:
            m = [[px[x, y][:3] == r[x, y] for x in range(16)] for y in range(16)]
            n = sum(map(sum, m))
            if best is None or n > best[0]:
                best = (n, m)
        return best[1] if best and best[0] >= 24 else [[False] * 16 for _ in range(16)]


def make_stamp(mapname, x0, y0, w, h, bg_ids, only=None, ground=None, name=None, keep_bg=False):
    """Build a Stamp from an old map region.

    Each cell becomes a Meta whose bottom layer = new ground (ground: Pair+id, default General grass) with the
    old building pixels composited on top (old ground pixels dropped), top layer kept.
    only: optional set of (x,y) absolute cells to include (others None)."""
    import canvas
    mj, l, vals, pair = old_layout(mapname)
    W = l['width']
    gm = BgMatcher(pair, bg_ids)
    if ground is None:
        gpair = gfx.Pair('gTileset_General', 'gTileset_Petalburg')
        gimg = gpair.layer_rgba(0x001, 0)
    else:
        gimg = ground
    cells = []
    for yy in range(h):
        row = []
        for xx in range(w):
            ax, ay = x0 + xx, y0 + yy
            v = vals[ay * W + ax]
            mid = v & 0x3FF
            if (only is not None and (ax, ay) not in only) or (mid in bg_ids and not keep_bg):
                row.append(None)
                continue
            bot = pair.layer_rgba(mid, 0).copy()
            top = pair.layer_rgba(mid, 1)
            full = pair.render(mid)
            if not keep_bg:
                m = gm.mask(full)
                bp = bot.load()
                for y in range(16):
                    for x in range(16):
                        if m[y][x]:
                            bp[x, y] = (0, 0, 0, 0)
                comp = gimg.copy()
                comp.alpha_composite(bot)
                bot = comp
            a = pair.attr(mid)
            meta = tsbuild.Meta(bot, top, behavior=a & 0xFF, layer=(a >> 12) & 0xF, coll=(v >> 10) & 3, elev=v >> 12,
                                src=(mapname, ax, ay))
            row.append((meta, None, None))
        cells.append(row)
    return canvas.Stamp(cells, name=name)


def inventory(mapname, bg_ids, out, min_cells=2):
    mj, l, vals, pair = old_layout(mapname)
    comps = [c for c in components(mapname, bg_ids) if c['n'] >= min_cells]
    w, h = l['width'], l['height']
    im = Image.new('RGB', (w * 16, h * 16))
    for y in range(h):
        for x in range(w):
            im.paste(pair.render(vals[y * w + x] & 0x3FF), (x * 16, y * 16))
    d = ImageDraw.Draw(im)
    for i, c in enumerate(comps):
        d.rectangle([c['x'] * 16, c['y'] * 16, (c['x'] + c['w']) * 16 - 1, (c['y'] + c['h']) * 16 - 1], outline=(255, 0, 0), width=2)
        d.rectangle([c['x'] * 16, c['y'] * 16, c['x'] * 16 + 22, c['y'] * 16 + 11], fill=(0, 0, 0))
        d.text((c['x'] * 16 + 2, c['y'] * 16), str(i), fill=(255, 255, 0))
    im.save(out)
    return comps


TREES = {0x1D4, 0x1D5, 0x1DC, 0x1DD}
BG = {
    'LittlerootTown': {0x1, 0x200, 0x201, 0x202} | TREES,
    'OldaleTown': {0x1, 0x200, 0x201, 0x202} | TREES,
    'Romagna_Cesena': {0x1, 0x200} | TREES,
    'Romagna_Cesenatico': {0x1, 0x200, 0x201, 0x202} | TREES,
    'Romagna_Forli': {0x1, 0x202, 0x4} | TREES,
    'Romagna_RiminiCentro': {0x1, 0x202, 0x203, 0x4} | TREES,
    'Romagna_RiminiPorto': {0x1, 0x202, 0x203, 0x204} | TREES,
    'Romagna_Saline': {0x1, 0x170, 0xD, 0x201, 0x200} | TREES,
    'Romagna_Befane': {0x1, 0x24, 0x4} | TREES,
    'Romagna_Ippodromo': {0x1, 0xD} | TREES,
}


def stamp_of(mapname, comp_idx, protect=False, ground=None):
    bg = BG[mapname]
    comps = components(mapname, bg)
    c = comps[comp_idx]
    st = make_stamp(mapname, c['x'], c['y'], c['w'], c['h'], bg, only=c['cells'], ground=ground)
    if protect:
        for row in st.cells:
            for cell in row:
                if cell:
                    cell[0].protect = True
    return st


def stamp_door(st):
    for y, row in enumerate(st.cells):
        for x, c in enumerate(row):
            if c and c[0].behavior in (0x60, 0x69):
                return x, y
    return None


_gpair = None


def ground_img(mid):
    """RGBA of a General metatile (flattened) to use as stamp ground."""
    global _gpair
    if _gpair is None:
        _gpair = gfx.Pair('gTileset_General', 'gTileset_Petalburg')
    return _gpair.render(mid).convert('RGBA')
