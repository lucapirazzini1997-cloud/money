"""Casa delle Aie — interior (new map). Rustic trattoria: beams, fireplace, hams, wine shelves, five tables."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import interior as I
from interior import Room
from art import C

TS = 'r22_aie_int'
W, H = 22, 15
STARTS = [(11, 14)]
GN = (34, 20)          # template only; the build swaps in the new map id


def build(gn=GN):
    r = Room(W, H, gn, floor='terracotta', wall='ochre', wall_rows=2)
    # wall decoration
    r.furn(9, 0, I.fireplace())
    for x in (2, 15):
        r.furn(x, 0, I.hams())
    for x in (5, 19):
        r.art[0][x] = (r.art[0][x][0].copy(), None, 1, 0, False)
        r.furn(x, 0, I.window_art('ochre', C(57, 140, 74)))
    r.furn(12, 0, I.painting())
    r.furn(7, 0, I.painting(C(214, 140, 74)))
    # bar counter with wine shelves behind (right side)
    r.furn(16, 2, I.shelf('bottles', 3))
    r.furn(15, 5, I.counter(5))
    r.furn(1, 2, I.shelf('jars', 2))
    r.furn(19, 12, I.barrels())
    r.furn(1, 12, I.barrels())
    # five tables with chairs
    tables = [(3, 6), (8, 6), (3, 10), (8, 10), (13, 10)]
    for (x, y) in tables:
        r.furn(x, y, I.table())
        r.furn(x - 1, y, I.chair()); r.furn(x + 2, y, I.chair())
    for (x, y) in ((1, 5), (20, 9)):
        r.furn(x, y, I.plant())
    r.exit_mat(11, H - 1, 34, 20, 0)
    # patrons (trainers) seated next to their table, the host behind the counter's corner
    pats = [(5, 7), (10, 7), (5, 11), (10, 11), (15, 11)]
    gfx = [48, 26, 50, 25, 22]          # gentleman, woman, fisherman, pokefan, expert
    labels = ['R22_Aie1', 'R22_Aie2', 'R22_Aie3', 'R22_Aie4', 'R22_Aie5']
    moves = [10, 9, 10, 9, 10]
    for (x, y), g, lab, mv in zip(pats, gfx, labels, moves):
        r.add_obj(x, y, g, lab, move=mv)
    r.add_obj(17, 4, 27, 'R22_AieOste', move=8)      # cook / host
    r.add_sign(14, 1, 'R22_SignAieMenu')
    return r
