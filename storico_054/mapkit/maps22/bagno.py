"""Bagno di Romagna (35,19) 48x40 — Appennine spa town under the snow, on the upper Savio (stone bridges):
the Palazzo del Capitano with the coats of arms, the Basilica di Santa Maria Assunta, the Terme with the steaming
outdoor pool, stone houses with snowy roofs, the Locanda del crinale, the research lab, the presidio of the
Via Vittoria to the north, the Dragon gym. Every piece is composited over snow (no grass under the art)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import art, art22, decor, r22
from art import C
from canvas import G
from decor import rect
from events22 import place_over

GN = (35, 19)
TS = 'r22_bagno'
W, H = 48, 40
STARTS = [(0, 17)]
HEAL = 6


def build():
    cv = r22.RCanvas(W, H, GN)
    doors, locked = {}, []
    # base-tileset buildings first (the snow goes around them)
    doors['pc'] = decor.general_building(cv, 3, 9, decor.PC)
    doors['mart'] = decor.general_building(cv, 9, 9, decor.MART)
    doors['gym'] = decor.general_building(cv, 34, 30, decor.GYM)
    occupied = {(x, y) for y in range(H) for x in range(W) if cv.over[y][x] is not None}
    river = rect(29, 0, 3, H)
    bridges = rect(29, 16, 3, 3) | rect(29, 26, 3, 2)
    streets = rect(0, 16, W, 3) | rect(14, 4, 2, 34) | rect(40, 4, 2, 33) | rect(2, 26, 44, 2) | rect(20, 13, 1, 3) | rect(4, 13, 1, 3) | rect(10, 13, 1, 3)
    streets |= rect(37, 11, 1, 5) | rect(37, 35, 1, 1)

    def ground(x, y):
        return art22.slab_tile(x, y) if (x, y) in streets else art22.snow_tile(x, y)

    for y in range(H):
        for x in range(W):
            if (x, y) in occupied:
                continue
            if (x, y) in bridges:
                e = 'n' if y in (16, 26) else ('s' if y in (18, 27) else '')
                cv.art[y][x] = (art22.stone_bridge_tile(x, y, e), None, 0, 0x100, False)
            elif (x, y) in river:
                cv.art[y][x] = (art22.river_tile(x, y, x == 29, x == 31), None, 1, 0, False)
            else:
                cv.art[y][x] = (ground(x, y), None, 0, 0x100, False)

    def put(x, y, asset, lock=False, protect=True):
        place_over(cv, x, y, asset, ground, protect=protect)
        d = asset.get('door')
        if d:
            dx, dy = x + d[0], y + d[1]
            a = cv.art[dy][dx]
            cv.art[dy][dx] = (a[0], None, 0, 0x60, a[4])
            if lock:
                locked.append((dx, dy))
            return (dx, dy)

    # ---------------- north: Palazzo del Capitano, the presidio, the Terme with the outdoor pool
    put(17, 8, art22.palazzo_capitano(7), lock=True)
    doors['presidio'] = put(16, 0, art22.stone_house(5, 2, shutters=C(165, 57, 49)))
    doors['terme'] = put(34, 6, art22.terme(7))
    place_over(cv, 42, 4, art22.thermal_pool(5, 3), ground, protect=True)
    for (x, y) in ((22, 1), (2, 1), (8, 1)):
        put(x, y, art22.stone_house(4, 2), lock=True)
    # ---------------- south of the main street
    put(2, 20, art22.stone_church(6), lock=True)
    doors['locanda'] = put(8, 21, art22.stone_house(5, 2, shutters=C(165, 57, 49)))
    doors['info'] = put(16, 22, art22.stone_house(4, 2))
    doors['lab'] = put(33, 20, art22.stone_house(5, 2, shutters=C(57, 99, 165)))
    for (x, y) in ((22, 22), (42, 21), (2, 31), (8, 31), (20, 31)):
        put(x, y, art22.stone_house(4, 2), lock=True)
    # snowy firs around the town (the Foreste Casentinesi)
    fir = art22.snowy_fir()
    edge = [(x, 38) for x in range(0, W, 2)] + [(0, y) for y in range(0, 15, 3)] + [(0, y) for y in range(20, 37, 3)] + [(46, y) for y in range(10, 37, 3)]
    edge += [(26, 3), (26, 8), (27, 12), (33, 13), (44, 13), (25, 30), (27, 34), (12, 35), (44, 27)]
    for (x, y) in edge:
        if all(cv.art[yy][x] is not None and cv.art[yy][x][3] == 0x100 for yy in (y, y + 1) if 0 <= yy < H) and (x, y) not in streets and (x, y + 1) not in streets:
            place_over(cv, x, y, fir, ground)
    # ---------------- events (same order as 0.21)
    cv.set_warp(0, 0, 17)
    for yy in (16, 17, 18):                                   # west edge of the main street: exit to the pass
        a = cv.art[yy][0]; cv.art[yy][0] = (a[0], None, 0, 0x63, a[4])
    order = {1: 'pc', 2: 'mart', 3: 'terme', 4: 'locanda', 5: 'info', 6: 'lab', 7: 'gym', 8: 'presidio'}
    for i, k in order.items():
        cv.set_warp(i, *doors[k])
    cv.place_objs({1: (22, 17), 2: (25, 27), 3: (20, 14)})
    b = cv.bbgs
    b[0]['x'], b[0]['y'] = 13, 19
    from art import Px
    sg = Px(16, 16); sg.rect(2, 2, 12, 8, C(156, 107, 66)); sg.rect(3, 3, 10, 6, C(206, 156, 99)); sg.rect(7, 10, 2, 5, C(115, 74, 41))
    sg.hline(2, 2, 12, C(255, 255, 255)); sg.outline()
    place_over(cv, 13, 19, dict(img=sg.im, solid={(0, 0)}), ground)
    for d in locked:
        cv.locked(d)
    cv.heal = (doors['pc'][0], doors['pc'][1] + 1)
    cv.border = [0x1D4, 0x1D5, 0x1DC, 0x1DD]
    return cv
