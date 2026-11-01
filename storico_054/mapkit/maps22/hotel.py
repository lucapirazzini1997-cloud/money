"""Hotel Vistamare: first-floor corridor with real doors (34,15) and five different rooms (34,79..83)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import interior as I
from interior import Room
from art import C, PAL, Px

TS = 'r22_hotel'
STARTS = [(14, 2)]


def corridor():
    r = Room(24, 16, (34, 15), floor='planks', wall='blue', wall_rows=2, keep_events=True)
    old_objs, old_bgs = r.objs, r.bbgs
    r.bwarps = []
    # stairs down to the lobby (warp 0)
    st = I.stairs()
    r.art[0][14] = (r.art[0][14][0], None, 1, 0, False)
    r.furn(14, 0, st)
    r.art[1][14] = (r.art[1][14][0], None, 0, 0x60, False)
    r.bwarps.append(dict(x=14, y=1, elev=0, warp=1, num=0, group=34))
    # top row of rooms: 101, 102, 105 (cheater)
    r.wall_door(4, 34, 79, 0)
    r.wall_door(9, 34, 80, 0)
    # partition between the two corridors, open in the middle
    for x in list(range(0, 10)) + list(range(13, 24)):
        r.art[8][x] = (I.wall_tile('blue', 0, x), None, 1, 0, False)
        r.art[9][x] = (I.wall_tile('blue', 1, x), None, 1, 0, False)
    # lower rooms 103, 104 (doors in the partition, facing south)
    def lower_door(x, num):
        g = Px(16, 16)
        g.rect(0, 0, 16, 16, I.WALLS['blue'][0][1])
        g.rect(2, 0, 12, 16, PAL['wood'][2]); g.rect(3, 1, 10, 15, PAL['wood'][1]); g.vline(8, 1, 15, PAL['wood'][2])
        g.p(11, 9, C(255, 222, 99))
        r.art[9][x] = (g.im, None, 0, 0x60, False)
        r.bwarps.append(dict(x=x, y=9, elev=0, warp=0, num=num, group=34))
    lower_door(5, 81)
    lower_door(18, 82)
    r.wall_door(19, 34, 83, 0, color=[C(214, 66, 57), C(173, 49, 49), C(132, 33, 33), C(82, 24, 24)])
    # red carpet runners
    for x in range(1, 23):
        for y in (4, 12):
            r.art[y][x] = (I.floor_tile('carpet', x, y), None, 0, 0, False)
    for y in range(4, 13):
        for x in (11, 12):
            if r.art[y][x][2] == 0:
                r.art[y][x] = (I.floor_tile('carpet', x, y), None, 0, 0, False)
    # furniture
    r.furn(1, 2, I.plant()); r.furn(22, 2, I.plant())
    r.furn(1, 10, I.plant()); r.furn(22, 10, I.plant())
    r.furn(15, 13, I.sofa(C(57, 99, 165)))
    r.furn(6, 13, I.desk())
    for x in (2, 7, 16, 21):
        r.furn(x, 0, I.painting(C(99, 156, 206)))
    r.furn(13, 8, I.window_art('blue', C(57, 99, 165)))
    # events: keep order (signs = room plates next to each door)
    r.objs = [dict(old_objs[0], x=16, y=6)]
    plates = [(5, 1), (10, 1), (6, 9), (17, 9), (20, 1)]
    r.bbgs = []
    for (x, y), b in zip(plates, old_bgs):
        r.bbgs.append(dict(b, x=x, y=y))
    r.void([(x, 15) for x in range(24)])
    return r


ROOMS = [
    (79, 'planks', 'plaster', C(99, 140, 206), 'bookcase'),
    (80, 'blue', 'blue', C(206, 99, 99), 'desk'),
    (81, 'tiles', 'green', C(99, 165, 99), 'sofa'),
    (82, 'planks', 'ochre', C(214, 165, 66), 'desk'),
    (83, 'checker', 'plaster', C(140, 99, 189), 'shelf'),
]


def room(i):
    num, floor, wall, bedc, extra = ROOMS[i]
    r = Room(14, 14, (34, num), floor=floor, wall=wall, wall_rows=2, keep_events=True)
    objs, bgs = r.objs, r.bbgs
    r.bwarps = []
    r.exit_mat(7, 13, 34, 15, i + 1)
    for x in (3, 10):
        r.furn(x, 0, I.window_art(wall, C(57, 99, 165) if i % 2 else C(214, 74, 74)))
    if i % 2 == 0:
        r.furn(1, 2, I.bed(bedc)); r.furn(4, 2, I.wardrobe()); r.furn(11, 2, I.desk())
        r.furn(1, 9, I.sofa(bedc)); r.furn(11, 10, I.plant())
        r.furn(5, 6, I.rug(4, 3))
    else:
        r.furn(11, 2, I.bed(bedc)); r.furn(1, 2, I.wardrobe()); r.furn(4, 2, I.desk())
        r.furn(10, 9, I.sofa(bedc)); r.furn(1, 10, I.plant())
        r.furn(5, 6, I.rug(4, 3, C(57, 99, 165), C(239, 231, 206)))
    if extra == 'shelf':
        r.furn(9, 2, I.shelf('bottles', 2))
    r.furn(7, 0, I.painting())
    r.objs = objs
    r.bbgs = [dict(b, y=1) for b in bgs]
    r.void([(x, 13) for x in range(14) if x != 7])
    return r


def build_all():
    return [corridor()] + [room(i) for i in range(5)]
