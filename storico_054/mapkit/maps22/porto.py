"""Porto di Rimini (34,44) 56x48 — porto canale with fishing boats, the Capitaneria (north bank),
the Deposito del porto (south bank), the lighthouse, the beach. Exits: Riviera (north), centro (west)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import art, art22, imports, decor, r22, _stamps
from canvas import G
from decor import rect
from _town import tree, lamp, bench, house_row, garden

GN = (34, 44)
TS = 'r22_porto'
W, H = 56, 48
STARTS = [(4, 0), (0, 32)]


def build():
    cv = r22.RCanvas(W, H, GN)
    CN, CS = 21, 25
    SAND, SEA = 40, 46
    cv.fill(SAND, 0, W, H, 'sand')
    cv.fill(SEA, 0, W - SEA, H, 'sea')
    cv.fill(10, CN + 1, SEA - 10, 3, 'sea')
    fam, cob = imports.cobbles(imports.warm_stone)
    paved = rect(3, 0, 4, 32) | rect(0, 30, 40, 4) | rect(7, CN - 2, 33, 2) | rect(10, CN, 30, 1) | rect(10, CS, 30, 1) | rect(10, CS + 1, 30, 2)
    paved |= rect(14, 10, 12, 2) | rect(20, 34, 2, 10)
    cv.paint_family(fam, cob, paved)
    rim_t, rim_b, face = art.quay_rim(True), art.quay_rim(False), art.quay_face()
    for x in range(10, SEA):
        cv.place_art(x, CN, dict(img=rim_t, solid=set(), door=None))
        cv.place_art(x, CS, dict(img=rim_b, solid=set(), door=None))
        cv.place_art(x, CN + 1, dict(img=face, solid=set(), door=None))
    for x in (12, 20, 28, 36):
        cv.place_art(x, CN, dict(img=decor.asset('bollard', art.bollard), solid={(0, 0)}, door=None))
    for i, bx in enumerate((13, 22, 31)):
        sail, hull = (('orange', (41, 99, 165)), ('red', (214, 214, 214)))[i % 2]
        cv.place_art(bx, CN + 1, dict(img=decor.asset('boat', art.boat, sail, hull), solid=rect(0, 0, 3, 3), door=None), overlay=True)
    bw = decor.asset('bw', art.boardwalk)
    for x in range(SAND, W):
        for y in (CN, CS):
            cv.place_art(x, y, dict(img=bw, solid=set(), door=None), walkable=True)
    cv.place_art(53, CN - 4, dict(img=decor.asset('lh', art.lighthouse), solid={(0, 4), (1, 4)}, door=None), top_rows=3, overlay=True)
    # canal head: a small basin with the stone quay
    for (x, y) in rect(8, CN + 1, 2, 3):
        cv.fill(x, y, 1, 1, 'sea')
    doors = {}
    doors['capit'] = cv.place_art(12, 3, art22.capitaneria(7), protect=True)
    for (x, y) in ((10, 6), (20, 6), (10, 3), (20, 3)):
        tree(cv, x, y, seed=x)
    doors['depo'] = cv.place_art(14, 36, art22.deposito(8, 'DEPOSITO DEL PORTO'), protect=True)
    for (x, y) in ((23, 39), (11, 40), (25, 42)):
        cv.place_art(x, y, art22.crates())
    for (x, y) in ((24, 34), (11, 34)):
        cv.place_art(x, y, dict(img=decor.asset('bollard', art.bollard), solid={(0, 0)}, door=None))
    # fish market stalls and seafood restaurants on the north quay
    locked = []
    locked.append(cv.place_art(24, 15, art.shopfront(4, 'PESCHERIA', 'cream', awning='blue', floors=1), protect=True))
    locked.append(cv.place_art(29, 15, art.shopfront(4, 'OSTERIA', 'ochre', awning='red', floors=1), protect=True))
    locked += house_row(cv, 24, 38, 11, seed=61)
    for (x, y) in ((34, 18), (36, 18)):
        cv.place_art(x, y, dict(img=decor.asset('ctab', art.cafe_table, 'red'), solid={(0, 0)}, door=None))
    for (x, y) in ((9, 18), (26, 18), (38, 28), (9, 28)):
        lamp(cv, x, y)
    # beach: umbrellas and cabins
    for i, y in enumerate(list(range(2, CN - 2, 3)) + list(range(CS + 3, H - 2, 3))):
        c = ['blue', 'red', 'yellow', 'green'][(i // 2) % 4]
        cv.place_art(SAND, y, dict(img=decor.asset('cab', art.cabina, c), solid={(0, 1)}, door=None), top_rows=1)
        cv.place_art(43, y, dict(img=decor.asset('omb', art.ombrellone, c), solid={(0, 1)}, door=None), top_rows=1)
    garden(cv, rect(26, 34, 13, 11) | rect(8, 2, 3, 15), seed=8)
    border = rect(0, 0, 3, 30) | rect(0, 34, 3, 14) | rect(7, 0, 33, 2) | rect(3, H - 2, 37, 2) | rect(3, 34, 7, 12)
    decor.woods(cv, border, seed=29, pine_ratio=0.5, gaps=0.0)
    cv.place_art(2, 0, art22.city_gate(6, 'RIVIERA'), top_rows=1, protect=True) if False else None
    for (x, y) in ((0, 28), (0, 34)):
        cv.place_art(x, y, art22.pillar())
    # ---------------- events
    cv.place_objs({1: (14, 19), 2: (36, 27), 3: (8, 32)})
    cv.set_warp(0, 4, 0); cv.set_warp(5, 5, 0)
    cv.set_warp(1, 0, 32); cv.set_warp(4, 0, 33)
    cv.set_warp(2, *doors['capit']); cv.set_warp(3, *doors['depo'])
    cv.bwarps.append(dict(x=3, y=0, elev=0, warp=1, num=43, group=34))
    cv.bwarps.append(dict(x=6, y=0, elev=0, warp=1, num=43, group=34))
    for yy in (30, 31):
        cv.bwarps.append(dict(x=0, y=yy, elev=0, warp=0, num=47, group=34))
    b = cv.bbgs
    b[0]['x'], b[0]['y'] = 7, 29
    cv.add_sign(2, 2, 'R22_SignRiviera')
    for bb in cv.bbgs:
        cv.put(bb['x'], bb['y'], G['sign'], 1, 3)
    for dd in locked:
        cv.locked(dd)
    cv.border = [0x1D4, 0x1D5, 0x1DC, 0x1DD]
    return cv
