"""Convert a 0.21 city onto the General primary keeping its street plan and every event position:
monuments are cut from the ROM, PC/Mart/Gym become the uniform General buildings, empty lawns get houses."""
import collections, random
import numpy as np
import art, art22, decor, imports, r22, _stamps, _town
from canvas import G
from decor import rect

ROM = r22.ROM
GRID = {'PC': (decor.PC, (1, 3)), 'MART': (decor.MART, (1, 3)), 'GYM': (decor.GYM, (3, 4))}


def classify_bg(m, a, get, k=8):
    cnt = collections.Counter(int(v) & 1023 for v in a.ravel() if not (int(v) & 0xc00))
    tot = sum(cnt.values())
    grass, paved = set(), set()
    for mid, c in cnt.most_common(k):
        if c < tot * 0.01:
            continue
        img = get(mid)[0][..., :3].astype(int)
        r, g, b = img[..., 0].mean(), img[..., 1].mean(), img[..., 2].mean()
        if g > r + 8 and g > b - 10:
            grass.add(mid)
        else:
            paved.add(mid)
    return grass, paved


def components(cells):
    cells = set(cells); out = []
    while cells:
        s = cells.pop(); comp = {s}; q = [s]
        while q:
            x, y = q.pop()
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    n = (x + dx, y + dy)
                    if n in cells:
                        cells.discard(n); comp.add(n); q.append(n)
        out.append(comp)
    return out


def convert(gn, swaps, keep_ground=False, fill=True, seed=1, protect_min=12, cobble=True):
    m = ROM.map(*gn)
    a = ROM.blocks(m)
    H, W = a.shape
    get = _stamps._layers(m)
    grass, paved = classify_bg(m, a, get)
    cv = r22.RCanvas(W, H, gn)
    bgcells = {(x, y) for y in range(H) for x in range(W) if (int(a[y, x]) & 1023) in grass | paved}
    if keep_ground:
        # paste the original ground everywhere (snow towns), objects on top
        for y in range(H):
            for x in range(W):
                b, t, beh, layer = get(int(a[y, x]) & 1023)
        cells = _stamps.cut(gn, 0, 0, W, H, bg=[])
        _stamps.paste(cv, 0, 0, cells)
    else:
        pv = {(x, y) for (x, y) in bgcells if (int(a[y, x]) & 1023) in paved}
        if cobble:
            fam, cob = imports.cobbles(imports.warm_stone)
            cv.paint_family(fam, cob, pv)
        else:
            for (x, y) in pv:
                cv.path(x, y, 1, 1)
    # door positions of the buildings to swap
    swap_xy = {}
    for wi, kind in swaps.items():
        w = m['warps'][wi]
        swap_xy[(w['x'], w['y'])] = (wi, kind)
    others = [(x, y) for y in range(H) for x in range(W) if (x, y) not in bgcells]
    comps = components(others)
    doors = {}
    for comp in comps:
        hit = [xy for xy in comp if xy in swap_xy]
        if hit:
            continue            # replaced by a General building
        if keep_ground:
            continue
        xs = [c[0] for c in comp]; ys = [c[1] for c in comp]
        x0, y0 = min(xs), min(ys)
        cells = _stamps.cut(gn, x0, y0, max(xs) - x0 + 1, max(ys) - y0 + 1, bg=sorted(grass | paved))
        # only this component
        for yy, row in enumerate(cells):
            for xx in range(len(row)):
                if (x0 + xx, y0 + yy) not in comp:
                    row[xx] = None
        _stamps.paste(cv, x0, y0, cells, protect=len(comp) >= protect_min)
    if keep_ground:
        # clear the swapped components back to the ground used around them
        pass
    for (wx, wy), (wi, kind) in swap_xy.items():
        grid, (dc, dr) = GRID[kind]
        bx, by = wx - dc, wy - dr
        for ry, row in enumerate(grid):
            for rx, mid in enumerate(row):
                X, Y = bx + rx, by + ry
                cv.art[Y][X] = None
        decor.general_building(cv, bx, by, grid)
        doors[wi] = (wx, wy)
    cv.convert_info = dict(grass=grass, paved=paved, bgcells=bgcells, a=a)
    return cv


def anchors(cv):
    pts = []
    for o in cv.objs:
        pts.append((o['x'], o['y']))
    for w in cv.bwarps:
        pts.append((w['x'], w['y']))
    for c in cv.bcoords:
        pts.append((c['x'], c['y']))
    for b in cv.bbgs:
        pts.append((b['x'], b['y']))
    return pts


def fill_houses(cv, seed=1, max_houses=30, margin=1, walls=('ochre', 'pink', 'peach'), protect_rect=()):
    """Place houses on empty lawns, door facing a walkable cell, never near events and keeping every
    walkable area connected."""
    rnd = random.Random(seed)
    W, H = cv.w, cv.h
    blocked = set()
    for (x, y) in anchors(cv):
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                blocked.add((x + dx, y + dy))
    for r in protect_rect:
        blocked |= rect(*r)

    def is_lawn(x, y):
        return (0 <= x < W and 0 <= y < H and cv.art[y][x] is None and cv.over[y][x] is None
                and not cv.pathmask[y][x] and cv.fam[y][x] is None and cv.terrain[y][x] == 'grass')
    paved = {(x, y) for y in range(H) for x in range(W) if cv.fam[y][x] is not None or cv.pathmask[y][x]}
    placed = []
    cands = [(x, y) for y in range(3, H - 3) for x in range(2, W - 6)]
    rnd.shuffle(cands)
    for (x, y) in cands:
        if len(placed) >= max_houses:
            break
        w_, f = 4, rnd.choice((1, 2))
        h_ = 3 if f == 1 else 4
        foot = rect(x, y, w_, h_)
        ring = rect(x - margin, y - margin, w_ + 2 * margin, h_ + 2 * margin)
        if not all(is_lawn(*c) for c in ring) or foot & blocked:
            continue
        door = (x + 2, y + h_ - 1)
        front = (door[0], door[1] + 1)
        # the house must face a street within two cells
        if not any((front[0] + dx, front[1] + dy) in paved for dx in (-1, 0, 1) for dy in (0, 1, 2)):
            continue
        wall = rnd.choice(walls)
        asset = decor.asset('house', art.house, w_, f, wall, seed=1)
        d = cv.place_art(x, y, asset)
        placed.append(d)
        blocked |= ring
    return placed


def fill_garden(cv, seed=2, density=0.06):
    rnd = random.Random(seed)
    blocked = set()
    for (x, y) in anchors(cv):
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                blocked.add((x + dx, y + dy))
    for y in range(2, cv.h - 3):
        for x in range(2, cv.w - 2):
            if (x, y) in blocked or (x, y + 1) in blocked:
                continue
            if all(cv.art[yy][x] is None and cv.over[yy][x] is None and not cv.pathmask[yy][x] and cv.fam[yy][x] is None
                   and cv.terrain[yy][x] == 'grass' for yy in (y, y + 1)):
                r = rnd.random()
                if r < density:
                    _town.tree(cv, x, y, seed=rnd.randrange(7))
                elif r < density * 1.6:
                    cv.put(x, y, G['flowers'])
