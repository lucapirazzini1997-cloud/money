"""Reusable decoration helpers: woods filling, scattered props, sand trails."""
import random
import art
from canvas import G

_cache = {}


def asset(name, fn, *a, **k):
    key = (name, a, tuple(sorted(k.items())))
    if key not in _cache:
        _cache[key] = fn(*a, **k)
    return _cache[key]


def woods(cv, allowed, seed=1, pine_ratio=0.5, solid_trees=True, grid_origin=(0, 0), walk_under=False, gaps=0.3):
    """Fill the cells in `allowed` (set of (x,y)) with a mixed wood.

    2x2 General trees (solid) are placed on an aligned grid where the whole block is allowed; umbrella pines
    (walk-under canopy) are mixed in according to pine_ratio; leftovers get young pines or shrubs."""
    rnd = random.Random(seed)
    used = set()
    ox, oy = grid_origin
    pine = asset('pine', art.umbrella_pine)
    for y in range(oy % 2, cv.h - 1, 2):
        for x in range(ox % 2, cv.w - 1, 2):
            block = {(x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)}
            if not block <= allowed or block & used:
                continue
            psolid = {(0, 1), (1, 1)} if walk_under else {(0, 0), (1, 0), (0, 1), (1, 1)}
            if rnd.random() < pine_ratio or not solid_trees:
                cv.place_art(x, y, dict(img=pine, solid=psolid, door=None), top_rows=1 if walk_under else 0)
            else:
                cv.tree(x, y)
            used |= block
    rest = sorted(allowed - used)
    yp = asset('ypine', art.young_pine)
    for (x, y) in rest:
        if (x, y) in used:
            continue
        r = rnd.random()
        if r < gaps:
            if r < 0.06:
                cv.put(x, y, G['flowers'])
            used.add((x, y))
            continue
        if (x, y + 1) in allowed and (x, y + 1) not in used and r < 0.6:
            cv.place_art(x, y, dict(img=yp, solid={(0, 0), (0, 1)}, door=None))
            used |= {(x, y), (x, y + 1)}
        else:
            cv.place_art(x, y, dict(img=asset('shrub', art.shrub, 0), solid={(0, 0)}, door=None))
            used.add((x, y))
    return used


def solid_border_trees(cv, allowed, seed=2):
    """Dense impassable General trees on an aligned grid; leftovers become shrubs."""
    used = set()
    for y in range(0, cv.h - 1, 2):
        for x in range(0, cv.w - 1, 2):
            block = {(x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)}
            if block <= allowed and not block & used:
                cv.tree(x, y)
                used |= block
    rnd = random.Random(seed)
    for (x, y) in sorted(allowed - used):
        cv.place_art(x, y, dict(img=asset('shrub', art.shrub, 0), solid={(0, 0)}, door=None))
        used.add((x, y))
    return used


def rect(x, y, w, h):
    return {(xx, yy) for xx in range(x, x + w) for yy in range(y, y + h)}


def tall_grass(cv, cells):
    for (x, y) in cells:
        cv.put(x, y, G['tall'])


PC = [[0x048, 0x049, 0x04A, 0x04B], [0x050, 0x051, 0x052, 0x053], [0x058, 0x059, 0x05A, 0x05B], [0x060, 0x061, 0x062, 0x063]]
MART = [[0x028, 0x029, 0x029, 0x02B], [0x030, 0x031, 0x032, 0x033], [0x038, 0x039, 0x03A, 0x03B], [0x060, 0x041, 0x042, 0x043]]
GYM = [[0x1AA, 0x1AB, 0x1AB, 0x1AB, 0x1AB, 0x1AC], [0x1B2, 0x1B3, 0x1B3, 0x1B3, 0x1B3, 0x1B4], [0x1B8, 0x1B9, 0x1BA, 0x1B3, 0x1BB, 0x1BC],
       [0x1C0, 0x1C1, 0x1C2, 0x1C5, 0x1C3, 0x1C4], [0x1C8, 0x1C9, 0x1CA, 0x1CD, 0x1CB, 0x1CC]]
DOORS = {0x061, 0x041, 0x1CD}
_gp = None


def general_building(cv, x, y, rows, passable_rows=(0,), direct=True):
    """Place a General-tileset building whose outer cells blend over any ground. Returns door (x,y).
    direct=True puts the original General metatiles (no secondary tiles used; ground must be grass)."""
    global _gp
    if direct:
        door = None
        for ry, row in enumerate(rows):
            for rx, mid in enumerate(row):
                X, Y = x + rx, y + ry
                cv.terrain[Y][X] = 'grass'
                cv.pathmask[Y][X] = False
                cv.put(X, Y, mid)
                if mid in DOORS:
                    door = (X, Y)
        return door
    import gfx
    from PIL import Image
    if _gp is None:
        _gp = gfx.Pair('gTileset_General', 'gTileset_Petalburg')
    grass = _gp.render(0x001).convert('RGBA')
    door = None
    for ry, row in enumerate(rows):
        for rx, mid in enumerate(row):
            X, Y = x + rx, y + ry
            if mid in DOORS:
                cv.put(X, Y, mid, 1, 0)
                door = (X, Y)
                continue
            full = _gp.render(mid).convert('RGBA')
            px, gp = full.load(), grass.load()
            for yy in range(16):
                for xx in range(16):
                    if px[xx, yy] == gp[xx, yy]:
                        px[xx, yy] = (0, 0, 0, 0)
            solid = ry not in passable_rows and ry < len(rows)
            if ry in passable_rows:
                cv.art[Y][X] = (None, full, 0, 0, False)       # roof edge over the player
            else:
                cv.art[Y][X] = (full, None, 1, 0, False)
    return door


def region(cv, cells, fill, rim, coll=1, behavior=0, sparkle=None, rim_w=3):
    """Paint a rimmed region (salt basins, pools...) as opaque art tiles."""
    cells = set(cells)
    for (x, y) in cells:
        m = art.region_mask(cells, x, y)
        img = asset('region', art.region_tile, m, tuple(fill), tuple(rim), rim_w, sparkle, hash(m) % 7)
        cv.place_art(x, y, dict(img=img, solid={(0, 0)} if coll else set(), door=None),
                     behaviors={(0, 0): behavior} if behavior else None)
