"""Fill empty lawns of the late cities with copies of their own houses and trees (no new tiles needed).
Copied houses get a locked door; every event keeps its position and all walkable areas stay connected."""
import collections, random, struct
import numpy as np
import romlib

DOOR_BEH = {0x60, 0x69}


def comps(cells):
    cells = set(cells); out = []
    while cells:
        s = cells.pop(); c = {s}; q = [s]
        while q:
            x, y = q.pop()
            for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if n in cells:
                    cells.discard(n); c.add(n); q.append(n)
        out.append(c)
    return out


def reach(walk, start):
    H, W = walk.shape
    seen = {start}; q = collections.deque([start])
    while q:
        x, y = q.popleft()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < W and 0 <= ny < H and walk[ny, nx] and (nx, ny) not in seen:
                seen.add((nx, ny)); q.append((nx, ny))
    return seen


def run(W, gn, max_houses=14, max_trees=40, seed=1, locked_script=None):
    rom = W.rom
    m = rom.map(*gn)
    a = rom.blocks(m)
    H, Wd = a.shape
    beh = lambda v: rom.attr(m, int(v) & 1023) & 0xff
    walk = (a & 0xc00) == 0
    cnt = collections.Counter(int(v) & 1023 for v in a.ravel() if not (int(v) & 0xc00))
    # ground classes: the most common walkable metatiles
    get_green = {}
    import sys
    sys.path.insert(0, '/home/claude/tools/mapkit/maps22'); sys.path.insert(0, '/home/claude/tools/mapkit')
    common = [k for k, c in cnt.most_common(6) if c > 30]
    grass, paved = set(), set()
    prim, sec = rom.tileset(m['primary']), rom.tileset(m['secondary'])
    pals = rom.palettes(prim, sec)
    mt = rom.renderer(m)
    for k in common:
        img = mt(k).astype(int)
        r, g, b = img[..., 0].mean(), img[..., 1].mean(), img[..., 2].mean()
        (grass if (g > r + 8 and g > b - 10) else paved).add(k)
    # templates: building components with a door that is a warp, up to 6x6
    warps = {(w['x'], w['y']) for w in m['warps']}
    nonbg = [(x, y) for y in range(H) for x in range(Wd) if (int(a[y, x]) & 1023) not in grass | paved]
    templates = []
    trees = []
    for c in comps(nonbg):
        xs = [p[0] for p in c]; ys = [p[1] for p in c]
        x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
        w, h = x1 - x0 + 1, y1 - y0 + 1
        doors = [p for p in c if beh(a[p[1], p[0]]) in DOOR_BEH]
        special = False
        for wv in m['warps']:
            if (wv['x'], wv['y']) == (doors[0] if doors else None):
                try:
                    im = rom.map(wv['group'], wv['num'])
                    special = any(o['gfx'] in (58, 83) for o in im['objects']) or im['width'] > 20
                except Exception:
                    special = True
        if doors and not special and 3 <= w <= 6 and 3 <= h <= 6 and len(doors) == 1 and doors[0][1] == y1:
            block = a[y0:y1 + 1, x0:x1 + 1].copy()
            mask = np.zeros((h, w), bool)
            for (x, y) in c: mask[y - y0, x - x0] = True
            templates.append((block, mask, (doors[0][0] - x0, doors[0][1] - y0)))
        elif w == 2 and h == 2 and all(not walk[y, x] for (x, y) in c) is False:
            pass
    if not templates:
        return 'no house templates'
    # anchors (events) to keep clear
    anchors = [(o['x'], o['y']) for o in m['objects']] + list(warps) + [(c['x'], c['y']) for c in m['coords']] + [(b['x'], b['y']) for b in m['bgs']]
    blocked = set()
    for (x, y) in anchors:
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                blocked.add((x + dx, y + dy))
    ground = grass or {max(paved, key=lambda k: cnt[k])}
    def is_grass(x, y):
        return 0 <= x < Wd and 0 <= y < H and (int(a[y, x]) & 1023) in ground and walk[y, x]
    pv = {(x, y) for y in range(H) for x in range(Wd) if (int(a[y, x]) & 1023) in paved and not (0x10 <= beh(a[y, x]) <= 0x15)}
    start = next(((x, y) for (x, y) in anchors if 0 <= x < Wd and 0 <= y < H and walk[y, x]), None)
    rnd = random.Random(seed)
    cand = [(x, y) for y in range(2, H - 6) for x in range(2, Wd - 7)]
    rnd.shuffle(cand)
    placed = []
    for (x, y) in cand:
        if len(placed) >= max_houses: break
        block, mask, (dx, dy) = rnd.choice(templates)
        h, w = block.shape
        ring = {(x + i, y + j) for i in range(-1, w + 1) for j in range(-1, h + 1)}
        if not all(is_grass(*c) for c in ring) or ring & blocked:
            continue
        door = (x + dx, y + dy)
        if not any((door[0] + ox, door[1] + oy) in pv for ox in (-1, 0, 1) for oy in (1, 2, 3)):
            continue
        before = walk.copy()
        prev = a[y:y + h, x:x + w].copy()
        for j in range(h):
            for i in range(w):
                if mask[j, i]:
                    a[y + j, x + i] = block[j, i]
        a[door[1], door[0]] = (int(a[door[1], door[0]]) & ~0xc00) | 0x400       # locked door: solid
        walk = (a & 0xc00) == 0
        # connectivity of all anchors must be preserved
        ok = True
        if start is not None:
            r0 = reach(before, start); r1 = reach(walk, start)
            lost = [p for p in anchors if p in r0 and p not in r1 and walk[p[1], p[0]]]
            near_lost = [p for p in anchors if p not in r1 and any((p[0] + ox, p[1] + oy) in r0 for ox, oy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                         and not any((p[0] + ox, p[1] + oy) in r1 for ox, oy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
            if lost or near_lost or len(r1) < len(r0) - w * h - 2:
                ok = False
        if not ok:
            a[y:y + h, x:x + w] = prev; walk = before
            continue
        placed.append(door)
        blocked |= ring
    # write
    border = struct.unpack_from('<4H', W.d, m['border'])
    W.set_layout(gn[0], gn[1], [int(v) for v in a.ravel()], Wd, H, border, m['primary'], m['secondary'])
    if locked_script is not None and placed:
        bgs = [dict(b) for b in m['bgs']] + [dict(x=x, y=y, elev=0, kind=0, arg=0x08000000 + locked_script) for (x, y) in placed]
        W.set_events(gn[0], gn[1], bgs=bgs)
    return 'added %d houses (templates %d)' % (len(placed), len(templates))
