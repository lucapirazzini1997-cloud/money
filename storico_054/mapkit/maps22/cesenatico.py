"""Cesenatico (34,22) 56x48 — Leonardo's porto canale with the painted-sail boats (museo galleggiante),
the Grattacielo by the sea (locked until the curator hands over the keys), the ferris wheel, the beach."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import art, art22, imports, decor, r22, _stamps
from canvas import G
from decor import rect

GN = (34, 22)
TS = 'r22_cesenatico'
W, H = 56, 48
STARTS = [(0, 34), (44, H - 1)]
HEAL = 19


def tree_at(cv, x, y, seed=9):
    cv.place_art(x, y, dict(img=decor.asset('rtree', art.round_tree, seed=seed % 2), solid={(0, 1)}, door=None), top_rows=1)


def build():
    cv = r22.RCanvas(W, H, GN)
    CN, CS = 19, 23           # rims; water 20..22
    SAND, SEA = 44, 50
    cv.fill(SAND - 1, 0, W, H, 'sand')
    cv.fill(SEA, 0, W - SEA, H, 'sea')
    cv.fill(0, CN + 1, SEA, 3, 'sea')
    fam, cob = imports.cobbles(imports.warm_stone)
    paved = rect(2, CN - 2, SAND - 3, 2) | rect(2, CN, SAND - 2, 1) | rect(2, CS, SAND - 2, 1) | rect(2, CS + 1, SAND - 3, 2)
    paved |= rect(0, 34, 44, 4)                          # viale Carducci to the west exit
    paved |= rect(12, 4, 2, 13) | rect(30, 4, 2, 13)      # north streets
    paved |= rect(2, 4, 40, 2)
    paved |= rect(20, 26, 2, 8) | rect(38, 26, 2, 22) | rect(44, 40, 2, 8)
    paved |= rect(22, 28, 9, 6)                           # piazza
    paved |= rect(2, 42, 36, 2)
    cv.paint_family(fam, cob, paved)
    rim_t, rim_b, face = art.quay_rim(True), art.quay_rim(False), art.quay_face()
    for x in range(2, SEA):
        cv.place_art(x, CN, dict(img=rim_t, solid=set(), door=None))
        cv.place_art(x, CS, dict(img=rim_b, solid=set(), door=None))
        cv.place_art(x, CN + 1, dict(img=face, solid=set(), door=None))
    for x in (5, 19, 27, 41):
        cv.place_art(x, CN, dict(img=decor.asset('bollard', art.bollard), solid={(0, 0)}, door=None))
    br = decor.asset('bridge', art.bridge_ns)
    for bx in (12, 13, 30, 31):
        for y in range(CN, CS + 1):
            cv.art[y][bx] = None
            cv.place_art(bx, y, dict(img=br, solid=set(), door=None), walkable=True)
    # the floating museum: historic boats with painted sails along the whole canal
    for i, bx in enumerate((3, 7, 15, 21, 25, 33, 37, 43)):
        sail, hull = (('orange', (41, 99, 165)), ('red', (214, 214, 214)))[i % 2]
        cv.place_art(bx, CN + 1, dict(img=decor.asset('boat', art.boat, sail, hull), solid=rect(0, 0, 3, 3), door=None), overlay=True)
    # lighthouse at the canal mouth, wooden piers into the sea
    bw = decor.asset('bw', art.boardwalk)
    for x in range(SEA - 1, W):
        for y in (CN, CS):
            cv.place_art(x, y, dict(img=bw, solid=set(), door=None), walkable=True)
    cv.place_art(53, CN - 4, dict(img=decor.asset('lh', art.lighthouse), solid={(0, 4), (1, 4)}, door=None), top_rows=3, overlay=True)
    doors = {}
    # ---------------- north bank
    doors['mercato'] = cv.place_art(4, 13, art.shopfront(5, 'MERCATO ITTICO', 'cream', awning='blue'), protect=True)
    doors['marineria'] = cv.place_art(15, 12, art.warehouse(9, 'MUSEO MARINERIA'), protect=True)
    ruota = _stamps.cut((34, 22), 34, 6, 7, 9)
    doors['ruota'] = _stamps.paste(cv, 32, 7, ruota, protect=True)
    gr = _stamps.cut((34, 22), 43, 5, 5, 12)
    doors['gratt'] = _stamps.paste(cv, 44, 4, gr, protect=True)
    # real entrances instead of the bare pale doorway tiles copied from 0.21
    for k, ov in (('ruota', art22.wheel_gate_overlay()),):
        dx, dy = doors[k]
        a = cv.art[dy][dx]
        if a is not None and a[0] is not None:
            im = a[0].copy(); im.alpha_composite(ov)
            cv.art[dy][dx] = (im, a[1], a[2], a[3], a[4])
    # paved forecourts down to the street
    fx, fy = doors['gratt']; gx, gy = doors['ruota']
    cv.paint_family(fam, cob, rect(fx - 1, fy, 3, CN - 2 - fy) | rect(gx, gy + 1, 1, CN - 2 - gy - 1))
    from PIL import Image as _Im
    cv.art[fy][fx] = (_Im.new('RGBA', (16, 16), (0, 0, 0, 0)), None, 0, 0x60, True)    # doorstep of the tower's own doorway
    locked = []
    for (x, y, c) in ((3, 7, 'pink'), (7, 7, 'ochre'), (15, 7, 'ochre'), (19, 7, 'cream'), (24, 7, 'pink')):
        locked.append(cv.place_art(x, y, decor.asset('house', art.house, 4, 2, c, seed=1)))
    for (x, y) in ((2, 0), (6, 0), (10, 0), (15, 0), (20, 0), (25, 0), (30, 0), (36, 0), (40, 0)):
        tree_at(cv, x, y, seed=x % 5)
    for (x, y) in ((28, 13), (11, 14), (29, 8)):
        tree_at(cv, x, y)
    # ---------------- south bank
    doors['pc'] = decor.general_building(cv, 4, 27, decor.PC)
    for (x, y, c) in ((9, 27, 'ochre'), (14, 27, 'pink')):
        locked.append(cv.place_art(x, y, decor.asset('house', art.house, 4, 2, c, seed=1)))
    gel = art.shopfront(4, 'PIADINERIA', 'yellow', awning='red')
    locked.append(cv.place_art(32, 27, gel, protect=True))
    # piazza with a statue (Garibaldi), benches and lamps
    cv.place_art(26, 30, dict(img=decor.asset('statue', art.statue), solid={(0, 1)}, door=None), top_rows=1)
    for (x, y) in ((23, 31), (29, 31)):
        cv.place_art(x, y, dict(img=decor.asset('bench', art.bench), solid={(0, 0)}, door=None))
    for (x, y) in ((22, 28), (30, 28)):
        cv.place_art(x, y, dict(img=decor.asset('lamp', art.lamp), solid={(0, 1)}, door=None), top_rows=1)
    for (x, y, c) in ((3, 38, 'cream'), (8, 38, 'pink'), (13, 38, 'ochre'), (24, 38, 'pink'), (29, 38, 'cream')):
        locked.append(cv.place_art(x, y, decor.asset('house', art.house, 4, 1, c, seed=1)))
    for (x, y) in ((18, 38), (34, 38), (20, 44), (2, 44), (10, 44), (30, 44)):
        tree_at(cv, x, y, seed=3)
    fb = decor.asset('fb1', art.flowerbed, ((239, 99, 132), (255, 206, 66)))
    for x in list(range(4, 10)) + list(range(23, 30)):
        cv.place_art(x, 45, dict(img=fb, solid={(0, 0)}, door=None))
    # beach: cabins, umbrellas
    for i, y in enumerate(range(26, H - 2, 3)):
        c = ['blue', 'yellow', 'red'][(i // 2) % 3]
        cv.place_art(SAND - 1, y, dict(img=decor.asset('cab', art.cabina, c), solid={(0, 1)}, door=None), top_rows=1)
        for x in (47,):
            cv.place_art(x, y, dict(img=decor.asset('omb', art.ombrellone, c), solid={(0, 1)}, door=None), top_rows=1)
    for i, y in enumerate(range(2, CN - 1, 3)):
        cv.place_art(49, y, dict(img=decor.asset('omb', art.ombrellone, 'blue'), solid={(0, 1)}, door=None), top_rows=1)
    # borders
    border = rect(0, 2, 2, CN - 2) | rect(0, CS + 1, 2, 10) | rect(0, 38, 2, 10) | rect(2, H - 2, 42, 2)
    decor.woods(cv, border, seed=31, pine_ratio=0.4, gaps=0.0)
    for (x, y) in ((1, 32), (1, 38)):
        cv.place_art(x, y, art22.pillar())
    # ---------------- events
    cv.place_objs({1: (8, 18), 2: (20, 18), 3: (42, 16), 4: (40, 18), 5: (45, 44)})
    cv.objs[3]['move'] = 9
    del cv.objs[5:6]          # the old door guard: the door itself is now locked
    cv.set_warp(0, *doors['mercato'])
    cv.set_warp(1, 1, 0)      # set below to the door cell (arrival point only)
    cv.set_warp(2, *doors['marineria'])
    cv.set_warp(3, *doors['pc'])
    cv.set_warp(4, 2, 1)      # the old 'porto' building is gone: warp parked under a tree trunk (solid, not on the edge)
    cv.set_warp(5, *doors['ruota'])
    cv.set_warp(6, 45, H - 1)
    cv.set_warp(7, 44, H - 1)
    # the skyscraper door keeps its arrival point (warp 1 of the interior leads here)
    gx, gy = doors['gratt']
    cv.gratt = (gx, gy)
    cv.set_warp(1, gx, gy)
    cv.locked((gx, gy), 'R22_GrattDoor')
    a = cv.art[gy][gx]; cv.art[gy][gx] = (a[0], a[1], 1, 0x60, a[4])   # solid from outside, a real door for the exit
    cv.add_sign(doors['pc'][0] - 2, doors['pc'][1] + 1, 'R22_SignCesenatico')
    cv.add_sign(3, 33, 'R22_SignCesenaticoW')
    cv.add_sign(43, 45, 'R22_SignRiviera')
    for bb in cv.bbgs:
        if bb['arg'] not in ('R22_GrattDoor', 'R22_LockedDoor'):
            cv.put(bb['x'], bb['y'], G['sign'], 1, 3)
    for dd in locked:
        cv.locked(dd)
    cv.heal = (doors['pc'][0], doors['pc'][1] + 1)
    cv.border = [0x1D4, 0x1D5, 0x1DC, 0x1DD]
    # Mewtwo's cave: rocky islet off the beach, mouth facing south (opens after the League)
    isl = art22.islet_cave()
    cv.place_art(51, 31, isl, protect=True)
    cv.bwarps.append(dict(x=48, y=33, elev=0, warp=0, num=0, group=0))      # beach arrival from the grotta (set by the build)
    cv.add_sign(52, 33, 'R22_CaveDoor')
    cv.add_sign(53, 33, 'R22_CaveDoor')
    return cv
