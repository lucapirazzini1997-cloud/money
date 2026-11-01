"""Helpers to fill town blocks densely: rows of houses on the street front, gardens and trees behind."""
import random
import art, art22, decor
from canvas import G
from decor import rect

WALLS = ['ochre', 'pink', 'blue', 'white', 'peach', 'yellow', 'cream']


def tree(cv, x, y, seed=9):
    cv.place_art(x, y, dict(img=decor.asset('rtree', art.round_tree, seed=seed % 2), solid={(0, 1)}, door=None), top_rows=1)


def lamp(cv, x, y):
    cv.place_art(x, y, dict(img=decor.asset('lamp', art.lamp), solid={(0, 1)}, door=None), top_rows=1)


def bench(cv, x, y):
    cv.place_art(x, y, dict(img=decor.asset('bench', art.bench), solid={(0, 0)}, door=None))


def free(cv, cells):
    for (x, y) in cells:
        if not (0 <= x < cv.w and 0 <= y < cv.h): return False
        if cv.art[y][x] is not None or cv.over[y][x] is not None or cv.pathmask[y][x]:
            return False
    return True


def house_row(cv, x0, x1, y_front, seed=0, floors=(1, 2), widths=(4,), gap=1, walls=('ochre', 'pink', 'peach'), shops=()):
    """Houses whose door row is y_front (doors on y_front). Returns list of door cells (locked)."""
    rnd = random.Random(seed)
    x = x0
    doors = []
    shops = list(shops)
    while x < x1:
        w = rnd.choice(widths)
        if x + w > x1:
            w = x1 - x
            if w < 3:
                break
        if shops and rnd.random() < 0.5:
            name, wall, awn = shops.pop(0)
            a = art.shopfront(w, name, wall, awning=awn, seed=rnd.randrange(99), floors=rnd.choice((1, 2)))
        else:
            f = rnd.choice(floors)
            wall = rnd.choice(walls)
            a = decor.asset('house', art.house, w, f, wall, roof='roof' if wall in ('ochre', 'cream') else 'roof_brown',
                            shutters='green_sh' if wall in ('ochre', 'pink') else 'brown_sh', balcony=(f == 2 and w >= 4), seed=1)
        h = a['img'].height // 16
        y = y_front - (h - 1)
        if free(cv, rect(x, y, w, h)):
            d = cv.place_art(x, y, a)
            if d:
                doors.append(d)
        x += w + gap
    return doors


def garden(cv, cells, seed=0, trees=0.07, flowers=0.06):
    rnd = random.Random(seed)
    cells = sorted(cells)
    for (x, y) in cells:
        if not free(cv, [(x, y), (x, y + 1)]):
            continue
        r = rnd.random()
        if r < trees and free(cv, [(x, y), (x, y + 1)]):
            tree(cv, x, y, seed=rnd.randrange(7))
        elif r < trees + flowers:
            cv.put(x, y, G['flowers'])


_TERR = {}


def terrace(cv, x0, x1, y_front, start=0, palette=('ochre', 'pink', 'cream'), floors=2, balcony=True):
    """Continuous row of 4-wide houses from three shared variants (keeps the tileset small). Returns doors."""
    import art, decor
    key = (palette, floors, balcony)
    if key not in _TERR:
        _TERR[key] = [decor.asset('house', art.house, 4, floors, c, roof='roof' if c in ('ochre', 'cream', 'peach') else 'roof_brown',
                                  shutters='green_sh' if c in ('ochre', 'cream') else 'brown_sh', balcony=balcony, seed=1) for c in palette]
    hs = _TERR[key]
    out = []
    i = start
    for x in range(x0, x1 - 3, 4):
        a = hs[i % len(hs)]; i += 1
        h = a['img'].height // 16
        d = cv.place_art(x, y_front - (h - 1), a)
        if d: out.append(d)
    return out


def fill_lawns(cv, cells, seed=1, tree_p=0.06, flower_p=0.10):
    """Trees of one kind and flower beds (primary tiles) on free lawn cells, never on or above events."""
    import random
    rnd = random.Random(seed)
    keep = {(o['x'], o['y']) for o in cv.objs} | {(o['x'], o['y'] + 1) for o in cv.objs} | {(o['x'], o['y'] - 1) for o in cv.objs}
    keep |= {(b['x'], b['y']) for b in cv.bbgs} | {(b['x'], b['y'] + 1) for b in cv.bbgs}
    def ok(x, y):
        return 0 <= x < cv.w and 0 <= y < cv.h and free(cv, [(x, y)]) and not cv.pathmask[y][x] and (x, y) not in keep
    for (x, y) in sorted(cells):
        if not ok(x, y):
            continue
        r = rnd.random()
        if r < tree_p and ok(x, y + 1):
            tree(cv, x, y, seed=3)
        elif r < tree_p + flower_p:
            cv.put(x, y, G['flowers'])
