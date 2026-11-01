"""Generated interiors (homes, trattorie, shops, museums) keeping the events of the 0.21 rooms."""
import random, collections
import interior as I
from interior import Room
from art import C, PAL
import r22

THEMES = {}


def free_cells(r):
    return {(x, y) for y in range(r.h) for x in range(r.w) if r.art[y][x] is not None and r.art[y][x][2] == 0 and r.art[y][x][3] == 0}


def reach(r, start):
    ok = free_cells(r)
    seen = {start}; q = collections.deque([start])
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if n in ok and n not in seen:
                seen.add(n); q.append(n)
    return seen


def try_place(r, x, y, asset, keep, exit_xy):
    img = asset['img'] if isinstance(asset, dict) else asset
    cw, ch = img.width // 16, img.height // 16
    cells = {(x + a, y + b) for a in range(cw) for b in range(ch)}
    if any(not (1 <= cx < r.w - 1 and r.wall_rows <= cy < r.h - 1) for cx, cy in cells):
        return False
    if cells & keep:
        return False
    free = free_cells(r)
    if not cells <= free:
        return False
    snapshot = {c: r.art[c[1]][c[0]] for c in cells}
    r.furn(x, y, asset)
    before = len(free) - len(cells)
    if len(reach(r, (exit_xy[0], exit_xy[1] - 1))) < before - 2:
        for (cx, cy), v in snapshot.items():
            r.art[cy][cx] = v
        return False
    return True


STYLES = {
    'home': dict(floor=['planks', 'tiles', 'blue'], wall=['plaster', 'green', 'ochre', 'blue'],
                 items=[('bed', 1), ('wardrobe', 1), ('desk', 1), ('sofa', 1), ('table', 1), ('shelf_books', 1), ('plant', 2), ('rug', 1)]),
    'trattoria': dict(floor=['terracotta', 'planks', 'checker'], wall=['ochre', 'plaster', 'brick'],
                      items=[('counter', 1), ('shelf_bottles', 1), ('table', 4), ('barrels', 1), ('plant', 2), ('fireplace', 1)]),
    'shop': dict(floor=['tiles', 'checker', 'planks'], wall=['plaster', 'blue', 'green'],
                 items=[('counter', 1), ('shelf_jars', 2), ('shelf_bottles', 1), ('shelf_books', 1), ('plant', 2), ('barrels', 1)]),
    'museum': dict(floor=['checker', 'tiles'], wall=['plaster', 'ochre'],
                   items=[('shelf_books', 2), ('desk', 2), ('plant', 2), ('rug', 1), ('shelf_jars', 1)]),
    'office': dict(floor=['blue', 'tiles'], wall=['blue', 'plaster'],
                   items=[('desk', 3), ('shelf_books', 2), ('plant', 2), ('sofa', 1)]),
}


def asset(kind, rnd):
    if kind == 'bed': return I.bed(rnd.choice([C(99, 140, 206), C(206, 99, 99), C(99, 165, 99), C(214, 165, 66)]))
    if kind == 'wardrobe': return I.wardrobe()
    if kind == 'desk': return I.desk()
    if kind == 'sofa': return I.sofa(rnd.choice([C(57, 99, 165), C(165, 57, 57), C(57, 140, 90)]))
    if kind == 'table': return I.table(check=rnd.choice([C(214, 57, 57), C(57, 99, 173), C(57, 140, 74)]))
    if kind == 'shelf_books': return I.shelf('books', 2)
    if kind == 'shelf_bottles': return I.shelf('bottles', 2)
    if kind == 'shelf_jars': return I.shelf('jars', 2)
    if kind == 'plant': return I.plant()
    if kind == 'rug': return I.rug(3, 2, rnd.choice([C(165, 57, 66), C(57, 99, 165)]), C(239, 206, 132))
    if kind == 'counter': return I.counter(4)
    if kind == 'barrels': return I.barrels()
    if kind == 'fireplace': return I.fireplace()


def make(gn, theme, seed=None, size=None):
    m = r22.ROM.map(*gn)
    rnd = random.Random(seed if seed is not None else gn[0] * 1000 + gn[1])
    st = STYLES[theme]
    w, h = size or (min(m['width'], 18), min(m['height'], 14))
    w = max(w, 10); h = max(h, 9)
    r = Room(w, h, gn, floor=rnd.choice(st['floor']), wall=rnd.choice(st['wall']), wall_rows=2, keep_events=True)
    objs, bgs, warps = r.objs, r.bbgs, r.bwarps
    r.bwarps = []
    ex = w // 2
    exits = [wp for wp in warps]
    for i, wp in enumerate(exits):
        x = ex + (i if len(exits) > 1 else 0) - (1 if len(exits) > 1 else 0)
        r.exit_mat(x, h - 1, wp['group'], wp['num'], wp['warp'])
    exit_cells = {(wp['x'], wp['y']) for wp in r.bwarps}
    r.void([(x, h - 1) for x in range(w) if (x, h - 1) not in exit_cells])
    # wall decoration
    for x in range(1, w - 1, 4):
        if rnd.random() < 0.6:
            r.furn(x, 0, I.window_art(r.wall_kind, rnd.choice([C(214, 74, 74), C(57, 99, 165), C(57, 140, 74)])))
        elif rnd.random() < 0.5:
            r.furn(x, 0, I.painting(rnd.choice([C(99, 156, 206), C(214, 140, 74)])))
    keep = set()
    for x in range(ex - 2, ex + 3):
        for y in range(h - 3, h):
            keep.add((x, y))
    # npc spots: reserve a few cells with a free neighbour
    spots = []
    cand = [(x, y) for y in range(3, h - 3) for x in range(2, w - 2)]
    rnd.shuffle(cand)
    for (x, y) in cand:
        if len(spots) >= len(objs):
            break
        if all(abs(x - a) + abs(y - b) > 2 for a, b in spots):
            spots.append((x, y))
    for (x, y) in spots:
        keep |= {(x, y), (x, y + 1), (x - 1, y), (x + 1, y)}
    for i in range(len(bgs)):
        keep |= {(2 + 2 * i, 2), (2 + 2 * i, 3)}
    # furniture
    for kind, n in st['items']:
        for _ in range(n):
            a = asset(kind, rnd)
            for _try in range(40):
                img = a['img'] if isinstance(a, dict) else a
                cw, ch = img.width // 16, img.height // 16
                if kind in ('shelf_books', 'shelf_bottles', 'shelf_jars', 'wardrobe', 'fireplace', 'counter') and _try < 25:
                    x, y = rnd.randrange(1, w - cw), r.wall_rows
                else:
                    x, y = rnd.randrange(1, w - cw), rnd.randrange(r.wall_rows, h - ch - 1)
                if try_place(r, x, y, a, keep, (ex, h - 1)):
                    break
    # events
    for o, (x, y) in zip(objs, spots):
        o['x'], o['y'] = x, y
    r.objs = objs
    nb = []
    for i, b in enumerate(bgs):
        nb.append(dict(b, x=2 + 2 * i, y=1))
    r.bbgs = nb
    return r
