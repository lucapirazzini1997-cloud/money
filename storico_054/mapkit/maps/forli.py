"""Forlì (MAP_ROMAGNA_FORLI): Piazza Saffi, San Mercuriale, the Via Emilia and the Rocca di Ravaldino."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import canvas, art, extract, imports, mapio, check, world, decor
from canvas import Canvas, G
from decor import rect

NAME = 'Romagna_Forli'
TS = 'romagna17_forli'
W, H = world.size(NAME)


def build():
    cv = Canvas(W, H, name=NAME)
    fam, cob = imports.cobbles(imports.warm_stone)
    paved = set()
    paved |= rect(40, 18, 18, 2)                    # Corso della Repubblica (from the east)
    paved |= rect(0, 20, 18, 2)                     # Corso Garibaldi (to the west)
    paved |= rect(16, 12, 25, 14)                   # Piazza Saffi
    paved |= rect(26, 26, 2, 10)                    # corso to the Rocca
    paved |= rect(8, 15, 2, 5) | rect(4, 22, 2, 8) | rect(4, 30, 22, 2)
    paved |= rect(44, 20, 2, 12) | rect(44, 30, 10, 2)
    paved |= rect(28, 44, 2, 2)
    cv.paint_family(fam, cob, paved)
    doors = {}
    doors['municipio'] = cv.place_art(16, 6, art.palazzo_comunale(9, 'peach', name='MUNICIPIO'), protect=True)
    merc = extract.stamp_of('Romagna_Forli', 0)
    cv.stamp(30, 3, merc)
    md = extract.stamp_door(merc)
    doors['merc'] = (30 + md[0], 3 + md[1])
    doors['domenico'] = cv.place_art(3, 9, art.church(6, 'cream', tower_side='left', name='MUSEO'), protect=True)
    cv.place_art(27, 16, dict(img=art.statue(), solid={(0, 1), (1, 1), (0, 2), (1, 2)}, door=None))
    # portici on the south side of the piazza
    cv.place_art(16, 26, art.portici(4, 2, 'brick'), coll=True)
    cv.place_art(29, 26, art.portici(6, 2, 'ochre'), coll=True)
    doors['cafe'] = cv.place_art(10, 25, art.shopfront(4, 'CAFFE SAFFI', 'cream', awning='red'), protect=True)
    doors['pc'] = decor.general_building(cv, 6, 32, decor.PC)
    doors['mart'] = decor.general_building(cv, 12, 32, decor.MART)
    doors['gym'] = decor.general_building(cv, 47, 24, decor.GYM)
    doors['casa'] = cv.place_art(50, 32, art.house(4, 2, 'pink'))
    rocca = extract.stamp_of('Romagna_Forli', 17)
    cv.stamp(22, 36, rocca)
    rd = extract.stamp_door(rocca)
    doors['rocca'] = (22 + rd[0], 36 + rd[1])
    # more houses around the centre
    HO, HP = art.house(4, 2, 'ochre'), art.house(4, 2, 'pink')
    locked = []
    cv.place_art(42, 10, art.portici(5, 2, 'brick'), coll=True)
    cv.hedge(cv.hline_cells(48, 9, 9) + cv.vline_cells(48, 10, 4))
    decor.tall_grass(cv, rect(50, 11, 6, 3))
    for (x, y, h) in [(42, 4, HO), (47, 4, HP), (52, 4, HO), (10, 3, HO),
                      (34, 36, HO), (39, 36, HP), (8, 38, HO), (13, 38, HP), (46, 38, HO)]:
        locked.append(cv.place_art(x, y, h))
    # gardens and trees
    tree = decor.asset('rtree', art.round_tree, seed=9)
    for (x, y) in [(15, 12), (41, 12), (15, 22), (41, 22), (2, 16), (2, 25), (19, 36), (33, 32), (55, 26), (55, 15), (0, 30), (21, 3)]:
        cv.place_art(x, y, dict(img=tree, solid={(0, 1)}, door=None), top_rows=1)
    decor.tall_grass(cv, rect(50, 40, 6, 4) | rect(1, 40, 5, 4))
    decor.woods(cv, rect(0, 0, 3, 8) | rect(54, 0, 4, 4) | rect(0, 44, 26, 2) | rect(30, 44, 28, 2), seed=51, pine_ratio=0.2, gaps=0.2)
    for (x, y) in [(20, 14), (36, 14), (20, 23), (36, 23)]:
        cv.place_art(x, y, dict(img=decor.asset('bench', art.bench), solid={(0, 0)}, door=None))
    old = mapio.old_events(NAME)
    o = [dict(e) for e in old['object_events']]
    pos = {0: (52, 20), 1: (24, 15), 2: (19, 13), 3: (31, 24), 4: (11, 31), 5: (38, 13), 6: (3, 16), 7: (11, 17),
           8: (49, 30), 9: (29, 34), 10: (55, 42), 11: (28, 45), 12: (2, 42), 13: (33, 42)}
    for i, e in enumerate(o):
        e['x'], e['y'] = pos[i]
    cv.npcs = o
    cv.warps = []
    cv.warp(0, 0, 'MAP_ROMAGNA_FORLI', 2)      # placeholders: old edge warps 0,1
    cv.warp(1, 0, 'MAP_ROMAGNA_FORLI', 2)
    cv.warp(*doors['municipio'], 'MAP_ROMAGNA_FORLI_MUNICIPIO', 0)
    cv.warp(*doors['merc'], 'MAP_ROMAGNA_SAN_MERCURIALE', 0)
    cv.warp(*doors['domenico'], 'MAP_ROMAGNA_SAN_DOMENICO', 0)
    cv.warp(*doors['pc'], 'MAP_ROMAGNA_FORLI_CENTRO', 0)
    cv.warp(*doors['mart'], 'MAP_ROMAGNA_FORLI_MARKET', 0)
    cv.warp(*doors['gym'], 'MAP_ROMAGNA_PALESTRA_FORLI', 0)
    cv.warp(*doors['rocca'], 'MAP_ROMAGNA_RAVALDINO', 0)
    cv.warp(*doors['cafe'], 'MAP_ROMAGNA_FORLI_CAFE', 0)
    cv.warp(*doors['casa'], 'MAP_ROMAGNA_FORLI_CASA', 0)
    cv.sign(29, 19, 'Romagna12_PiazzaSign')
    cv.sign(doors['gym'][0] + 2, doors['gym'][1] + 1, 'Romagna12_GymSign')
    cv.sign(doors['rocca'][0] + 2, doors['rocca'][1] + 1, 'Romagna12_FortSign')
    cv.sign(1, 19, 'Romagna12_WestSign')
    for d in locked:
        a = cv.art[d[1]][d[0]]
        cv.art[d[1]][d[0]] = (a[0], a[1], 1, 0, a[4])
        cv.sign(d[0], d[1], 'Romagna17_LockedDoor')
    cv.border = [0x1D4, 0x1D5, 0x1DC, 0x1DD]
    return cv


STARTS = [(W - 1, 18), (0, 20)]


def main(argv):
    cv = build()
    idmap, grids = canvas.build_tileset([cv], mapio.ts_symbol(TS), TS)
    check.check(cv, grids[0], STARTS)
    sym = mapio.register_tileset(TS)
    canvas.preview(cv, grids[0], idmap, TS, argv[1] if len(argv) > 1 else '/tmp/p.png', markers='--nomarkers' not in argv)
    if '--write' in argv:
        mapio.write(NAME, cv, grids[0], idmap, sym, connections=world.connections(NAME))
        print('written')


if __name__ == '__main__':
    main(sys.argv)
