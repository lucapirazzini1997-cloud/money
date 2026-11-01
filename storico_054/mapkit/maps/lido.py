"""Lido di Savio (MAP_LITTLEROOT_TOWN) — seaside village between the pinewood and the Adriatic."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import canvas, art, extract, imports, mapio, check, decor, world
from canvas import Canvas, G

W, H = 44, 36
NAME = 'LittlerootTown'
TS = 'romagna17_lido'
OLD_BG = {0x1, 0x4, 0xD, 0x1D4, 0x1D5, 0x1DC, 0x1DD, 0x200, 0x201, 0x202, 0x203, 0x204, 0x205, 0x24, 0x170}


def old_stamp(comp_idx, mapname='LittlerootTown', protect=False):
    comps = extract.components(mapname, OLD_BG)
    c = comps[comp_idx]
    st = extract.make_stamp(mapname, c['x'], c['y'], c['w'], c['h'], OLD_BG, only=c['cells'])
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


def solid_all(img):
    return {(x, y) for x in range(img.width // 16) for y in range(img.height // 16)}


def build():
    cv = Canvas(W, H, name=NAME)
    SEA_X, SAND_X, WALL_X, PROM_X = 38, 31, 30, 27
    # ---------------- terrain
    cv.fill(WALL_X, 0, W, H, 'sand')
    cv.fill(SEA_X, 0, W - SEA_X, H, 'sea')
    cv.fill(0, 0, 6, H, 'sand')                       # pinewood floor
    fam, cob = imports.cobbles(imports.warm_stone)
    paved = {(x, y) for x in range(PROM_X, WALL_X + 1) for y in range(H - 2)}
    paved |= {(x, y) for x in range(6, PROM_X) for y in (9, 10)}            # Via Lungo Savio
    paved |= {(x, y) for x in (16, 17) for y in range(9, H)}               # street to the pinewood
    paved |= {(x, y) for x in range(15, 20) for y in range(12, 17)}         # piazzetta
    paved |= {(x, y) for x in range(18, PROM_X) for y in range(24, 27)}     # bar terrace
    paved |= {(x, y) for x in (10,) for y in (7, 8)}                         # garden path to the house
    cv.paint_family(fam, cob, paved)
    # ---------------- promenade wall with stairs to the beach
    wall = art.Px(16, 16)
    wall.rect(0, 6, 16, 6, art.PAL['stone'][1]); wall.hline(0, 6, 16, art.PAL['stone'][0])
    wall.hline(0, 11, 16, art.PAL['stone'][3]); wall.vline(7, 7, 4, art.PAL['stone'][2])
    stairs = {5, 6, 17, 18, 29, 30}
    for y in range(H - 2):
        if y not in stairs:
            cv.place_art(WALL_X, y, dict(img=wall.im, solid={(0, 0)}, door=None))
    # promenade ends in a dune bank at the south edge
    for x in range(PROM_X, WALL_X + 1):
        for y in (H - 2, H - 1):
            cv.place_art(x, y, dict(img=decor.asset('shrub', art.shrub, (x + y) % 3), solid={(0, 0)}, door=None))
    # ---------------- beach
    segs = [(range(2, 10, 2), 'blue'), (range(12, 18, 2), 'red'), (range(20, 28, 2), 'yellow'), (range(28, 34, 2), 'green')]
    for ys, color in segs:
        for y in ys:
            if y not in stairs and y + 1 not in stairs:
                cv.place_art(SAND_X, y, dict(img=art.cabina(color), solid={(0, 1)}, door=None), top_rows=1)
            for x in (33, 35):
                cv.place_art(x, y, dict(img=art.ombrellone(color), solid={(0, 1)}, door=None), top_rows=1)
    cv.place_art(36, 9, dict(img=art.lifeguard(), solid={(0, 1)}, door=None), top_rows=1)
    cv.place_art(36, 18, dict(img=art.pedalo(), solid={(0, 0), (1, 0)}, door=None))
    # ---------------- pinewood edge (staggered umbrella pines)
    pine = art.umbrella_pine()
    for y in range(0, H - 1, 2):
        xs = (0, 2, 4) if (y // 2) % 2 == 0 else (1, 3)
        for x in xs:
            if (x, y) in ((3, 14), (1, 28)):      # clearings with items
                continue
            cv.place_art(x, y, dict(img=pine, solid={(0, 1), (1, 1)}, door=None), top_rows=1)
    # ---------------- buildings
    player = art.house(5, 2, 'peach', roof='roof', shutters='green_sh', balcony=True, seed=21)
    pd = cv.place_art(8, 3, player)
    cv.hedge(cv.hline_cells(7, 2, 7) + cv.vline_cells(7, 3, 6) + cv.vline_cells(13, 3, 6) + [(8, 8), (9, 8), (11, 8), (12, 8)])
    aldo = art.house(4, 2, 'cream', roof='roof_brown', shutters='green_sh', seed=11)
    ad = cv.place_art(15, 4, aldo)
    hotel = art.hotel(6, 4, 'cream', 'HOTEL VISTAMARE', 'blue')
    hd = cv.place_art(20, 2, hotel, protect=True)
    lab = extract.stamp_of('LittlerootTown', 5, protect=True)
    lx, ly = 7, 12
    cv.stamp(lx, ly, lab)
    ld = extract.stamp_door(lab)
    # piazzetta: fountain + benches + lamps
    cv.place_art(16, 13, dict(img=art.fountain(), solid={(0, 0), (1, 0), (0, 1), (1, 1)}, door=None))
    for (x, y) in [(15, 15), (19, 13)]:
        cv.place_art(x, y, dict(img=art.bench(), solid={(0, 0)}, door=None))
    # kiosk on the promenade
    cv.place_art(24, 12, dict(img=art.kiosk(), solid={(0, 0), (1, 0), (0, 1), (1, 1)}, door=None), protect=True)
    h_ochre = art.house(4, 1, 'ochre', seed=6)
    od = cv.place_art(21, 15, h_ochre)
    # playground
    cv.place_art(8, 18, dict(img=art.swing(), solid={(0, 1), (1, 1)}, door=None), top_rows=1)
    cv.place_art(11, 18, dict(img=art.slide(), solid={(0, 1), (1, 1)}, door=None), top_rows=1)
    cv.hedge(cv.hline_cells(7, 21, 3) + cv.hline_cells(11, 21, 2))
    # bar Panama with terrace tables
    barr = art.bar(5, 'BAR PANAMA', 'peach', 'red')
    bd = cv.place_art(20, 21, barr, protect=True)
    for x in (19, 21, 25):
        cv.place_art(x, 25, dict(img=art.cafe_table('red'), solid={(0, 0)}, door=None))
    # Nora's garden: flower beds and young pines
    fb = art.flowerbed(((239, 99, 132), (255, 206, 66)))
    fb2 = art.flowerbed(((132, 99, 239), (255, 255, 255)))
    for x in range(7, 13):
        cv.place_art(x, 22, dict(img=fb, solid={(0, 0)}, door=None))
        cv.place_art(x, 25, dict(img=fb2, solid={(0, 0)}, door=None))
    tree = art.round_tree(seed=9)
    for (x, y) in [(13, 21), (13, 24), (6, 26)]:
        cv.place_art(x, y, dict(img=tree, solid={(0, 1)}, door=None), top_rows=1)
    # south houses
    h_pink = art.house(4, 2, 'pink', roof='roof_brown', balcony=True, seed=4)
    pkd = cv.place_art(8, 28, h_pink)
    h_cream = art.house(5, 1, 'cream', roof='roof', seed=8)
    cd = cv.place_art(19, 29, h_cream)
    for (x, y) in [(13, 30), (24, 28)]:
        cv.place_art(x, y, dict(img=tree, solid={(0, 1)}, door=None), top_rows=1)
    # flowers along streets
    for (x, y) in [(6, 11), (7, 11), (14, 11), (15, 11), (19, 8), (26, 8), (18, 20), (19, 20), (20, 20), (14, 33), (15, 33), (18, 33), (19, 33)]:
        cv.put(x, y, G['flowers'])
    # lamps along the promenade
    for y in (1, 8, 15, 22, 33):
        cv.place_art(PROM_X, y, dict(img=art.lamp(), solid={(0, 1)}, door=None), top_rows=1)
    # ---------------- events (old order preserved: scripts use local ids)
    old = mapio.old_events(NAME)
    o = [dict(e) for e in old['object_events']]
    pos = {0: (9, 7), 1: (14, 16), 2: (37, 12), 3: (10, 24), 4: (28, 3), 5: (36, 24), 6: (18, 19), 7: (18, 33),
           8: (21, 8), 9: (19, 27), 10: (12, 11), 11: (3, 14), 12: (13, 19), 13: (37, 34), 14: (1, 28), 15: (26, 13)}
    for i, e in enumerate(o):
        e['x'], e['y'] = pos[i]
    o[15]['movement_type'] = 'MOVEMENT_TYPE_FACE_LEFT'
    o[2]['movement_type'] = 'MOVEMENT_TYPE_FACE_RIGHT'
    cv.npcs = o
    cv.warps = []
    cv.warp(ad[0], ad[1], 'MAP_ROMAGNA_CASA_ALDO', 0)
    cv.warp(pd[0], pd[1], 'MAP_LITTLEROOT_TOWN_BRENDANS_HOUSE_1F', 1)
    cv.warp(lx + ld[0], ly + ld[1], 'MAP_LITTLEROOT_TOWN_PROFESSOR_BIRCHS_LAB', 0)
    cv.warp(hd[0], hd[1], 'MAP_ROMAGNA_VISTAMARE', 0)
    cv.warp(bd[0], bd[1], 'MAP_ROMAGNA_PANAMA', 0)
    cv.sign(SAND_X, H - 1, 'Romagna07_ShortcutSign')
    cv.sign(lx + ld[0] - 2, ly + ld[1] + 1, 'Romagna_LabSign')
    cv.sign(hd[0] - 2, hd[1] + 1, 'Romagna_VistamareSign')
    cv.sign(bd[0] - 3, bd[1] + 1, 'Romagna_PanamaSign')
    for d in (od, pkd, cd):
        cv.sign(d[0], d[1], 'Romagna17_LockedDoor')
    for x in (16, 17):
        cv.trigger(x, H - 1, 'Romagna_CheckStarter', 'VAR_TEMP_1', 0)
    cv.border = [0x170, 0x170, 0x170, 0x170]
    # locked doors are not warps: make them solid
    for d in (od, pkd, cd):
        a = cv.art[d[1]][d[0]]
        cv.art[d[1]][d[0]] = (a[0], a[1], 1, 0, a[4])
    return cv


STARTS = [(16, H - 1), (17, H - 1)]

if __name__ == '__main__':
    cv = build()
    idmap, grids = canvas.build_tileset([cv], mapio.ts_symbol(TS), TS)
    check.check(cv, grids[0], STARTS)
    sym = mapio.register_tileset(TS)
    out = sys.argv[1] if len(sys.argv) > 1 else '/tmp/lido.png'
    canvas.preview(cv, grids[0], idmap, TS, out, markers='--nomarkers' not in sys.argv)
    if '--write' in sys.argv:
        mapio.write(NAME, cv, grids[0], idmap, sym, connections=world.connections(NAME))
        print('written')
