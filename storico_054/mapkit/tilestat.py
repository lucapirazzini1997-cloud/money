"""Tile budget analysis of a canvas: which cells use unique (non-primary) 8x8 tiles."""
import sys
from collections import defaultdict
from PIL import Image, ImageDraw
import tsbuild

_P = None
def pidx():
    global _P
    if _P is None: _P = tsbuild.PrimaryIndex('gTileset_General')
    return _P

def norm(t):
    # canonical over flips
    return min((tsbuild.flip(t, h, v) for h, v in ((0,0),(1,0),(0,1),(1,1))), key=repr)

def analyse(cv, out=None, base=None):
    grid = cv.compile()
    P = pidx()
    cells = defaultdict(set)   # key -> cells
    prot = set()
    metaq = {}
    for y, row in enumerate(grid):
        for x, (key, _) in enumerate(row):
            if isinstance(key, int): continue
            if id(key) not in metaq:
                qs = []
                for im in (key.bottom, key.top):
                    for t in tsbuild.quads(im):
                        t = tuple(tsbuild.q5(c) if c else None for c in t)
                        if all(c is None for c in t) or P.find(t) is not None: continue
                        qs.append(norm(t))
                metaq[id(key)] = (qs, key.protect)
            qs, pr = metaq[id(key)]
            for q in qs:
                cells[q].add((x, y))
                if pr: prot.add(q)
    total = len(cells)
    heat = defaultdict(float)
    for q, cs in cells.items():
        for c in cs: heat[c] += 1.0 / len(cs)
    print('unique tiles %d, protected %d, unprotected %d' % (total, len(prot), total - len(prot)))
    if out:
        im = base.convert('RGB') if base is not None else Image.new('RGB', (cv.w * 16, cv.h * 16))
        ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        for (x, y), v in heat.items():
            a = min(200, int(v * 40))
            d.rectangle([x*16, y*16, x*16+15, y*16+15], fill=(255, 0, 0, a))
        im = im.convert('RGBA'); im.alpha_composite(ov); im.save(out)
    return heat, total, len(prot)

def ideal(cv, out):
    import canvas
    grid = cv.compile()
    im = Image.new('RGBA', (cv.w * 16, cv.h * 16), (0, 0, 0, 255))
    for y, row in enumerate(grid):
        for x, (key, _) in enumerate(row):
            b, t = canvas.base_layers(key)[:2]
            c = Image.new('RGBA', (16, 16), (0, 0, 0, 255)); c.alpha_composite(b.convert('RGBA')); c.alpha_composite(t.convert('RGBA'))
            im.paste(c, (x * 16, y * 16))
    im.save(out); return im

def per_asset(modname, top=25):
    """Build a map module recording every place_art call; report the tiles owned by each call site."""
    import importlib, traceback, canvas
    rec = []
    orig = canvas.Canvas.place_art
    def pa(self, x, y, asset, *a, **k):
        st = traceback.extract_stack(limit=6)
        site = next((f'{f.filename.split("/")[-1]}:{f.lineno} {f.line[:60]}' for f in reversed(st[:-1]) if 'maps22' in f.filename), str(st[-2].lineno))
        img = asset['img'] if isinstance(asset, dict) else asset
        cells = [(x + cx, y + cy) for cy in range(img.height // 16) for cx in range(img.width // 16)]
        rec.append((site, cells))
        return orig(self, x, y, asset, *a, **k)
    canvas.Canvas.place_art = pa
    try:
        m = importlib.import_module(modname); cv = m.build()
    finally:
        canvas.Canvas.place_art = orig
    grid = cv.compile(); P = pidx()
    tiles_at = {}
    for y, row in enumerate(grid):
        for x, (key, _) in enumerate(row):
            if isinstance(key, int): continue
            s = set()
            for im in (key.bottom, key.top):
                for t in tsbuild.quads(im):
                    t = tuple(tsbuild.q5(c) if c else None for c in t)
                    if all(c is None for c in t) or P.find(t) is not None: continue
                    s.add(norm(t))
            tiles_at[(x, y)] = s
    owner = {}
    for i, (site, cells) in enumerate(rec):
        for c in cells: owner[c] = site
    by_site = defaultdict(set)
    for c, s in tiles_at.items():
        by_site[owner.get(c, 'ground/other')] |= s
    users = defaultdict(set)
    for site, s in by_site.items():
        for t in s: users[t].add(site)
    rows = []
    for site, s in by_site.items():
        excl = sum(1 for t in s if len(users[t]) == 1)
        rows.append((excl, len(s), site))
    rows.sort(reverse=True)
    print(modname, 'total', len(users))
    for r in rows[:top]: print('  %4d excl %4d all  %s' % r)
    return rows
