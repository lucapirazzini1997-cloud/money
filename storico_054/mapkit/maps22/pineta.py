"""Pineta di Savio (0,16) 40x48 — umbrella-pine forest between Lido (north) and Cervia (south).
A hidden clearing holds the forest shrine (Celebi, with the GS Ball after the League)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import art, art22, decor, r22
from canvas import G
from decor import rect

GN = (0, 16)
TS = 'r22_pineta'
W, H = 40, 48
STARTS = [(19, 0), (19, H - 1)]


def build():
    cv = r22.RCanvas(W, H, GN)
    trail = set()
    trail |= rect(18, 0, 4, 6) | rect(10, 5, 12, 2) | rect(10, 5, 2, 12) | rect(10, 15, 14, 2)
    trail |= rect(22, 15, 2, 12) | rect(22, 25, 12, 2) | rect(32, 25, 2, 8) | rect(18, 31, 16, 2)
    trail |= rect(18, 31, 4, H - 31)
    trail |= rect(2, 12, 8, 2) | rect(20, 6, 12, 2) | rect(30, 6, 2, 4) | rect(13, 34, 6, 2)        # side trails
    trail |= rect(34, 22, 3, 3)
    for (x, y) in trail:
        cv.path(x, y, 1, 1)
    clearings = rect(2, 10, 5, 6) | rect(28, 2, 8, 8) | rect(13, 20, 7, 6) | rect(6, 32, 9, 7) | rect(25, 37, 10, 7)
    # tall grass on the trail and in some clearings (wild Pokémon of the pinewood)
    tall = rect(10, 8, 2, 6) | rect(22, 18, 2, 6) | rect(26, 25, 5, 2) | rect(13, 21, 6, 4) | rect(18, 36, 4, 5) | rect(26, 38, 7, 4)
    decor.tall_grass(cv, tall)
    for (x, y) in tall:
        cv.pathmask[y][x] = False
    # pond with reeds in the south-west clearing
    for (x, y) in rect(7, 34, 5, 3):
        cv.fill(x, y, 1, 1, 'pond')
    # the shrine clearing (north-east), hidden behind the pines
    cv.place_art(31, 3, art22.shrine(), protect=True)
    for (x, y) in ((29, 3), (34, 3), (29, 7), (34, 7)):
        cv.put(x, y, G['flowers'])
    cv.place_art(28, 5, dict(img=decor.asset('log', art.log), solid={(0, 0), (1, 0)}, door=None))
    # rest area near the south exit
    cv.place_art(14, 42, dict(img=decor.asset('pic', art.picnic_table), solid={(0, 0), (1, 0)}, door=None))
    for (x, y) in ((25, 44), (29, 44)):
        cv.place_art(x, y, dict(img=decor.asset('bench', art.bench), solid={(0, 0)}, door=None))
    # forest
    keep = trail | clearings | tall | rect(7, 34, 5, 3) | {(20, 4), (9, 34), (20, 44), (3, 13), (36, 24), (7, 11), (16, 17), (31, 26)}
    keep |= rect(30, 5, 3, 2)
    woods = {(x, y) for x in range(W) for y in range(H)} - keep
    decor.woods(cv, woods, seed=16, pine_ratio=0.7, gaps=0.12)
    cv.place_art(17, H - 4, art22.city_gate(6, 'CERVIA'), top_rows=1, protect=True) if False else None
    # events (same order)
    cv.place_objs({1: (11, 9), 2: (20, 4), 3: (22, 20), 4: (30, 26), 5: (9, 33), 6: (3, 13), 7: (36, 24), 8: (21, 43)})
    b = cv.bbgs
    b[0]['x'], b[0]['y'] = 22, 2
    b[1]['x'], b[1]['y'] = 22, 44
    cv.add_sign(32, 5, 'R22_CelebiShrine')
    cv.add_sign(29, 9, 'R22_SignShrine')
    for bb in (b[0], b[1], cv.bbgs[-1]):
        cv.put(bb['x'], bb['y'], G['sign'], 1, 3)
    cv.border = [0x1D4, 0x1D5, 0x1DC, 0x1DD]
    return cv
