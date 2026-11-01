"""Mare di Rimini (new map, ocean route) with the Isola delle Rose. Deep water around the platform: dive spot."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import art, art22, decor, r22
from canvas import G
from decor import rect

TS = 'r22_mare'
W, H = 40, 30
STARTS = [(0, 10)]
GN = (34, 44)          # template for events; the build sets the real id


def build(gn=GN):
    cv = r22.RCanvas(W, H, (34, 44))
    cv.gn = gn
    cv.objs, cv.bwarps, cv.bcoords, cv.bbgs, cv.conns = [], [], [], [], []
    cv.fill(0, 0, W, H, 'sea')
    from PIL import Image
    # platform at the centre-east
    px, py = 24, 9
    cv.place_art(px, py, art22.isola_rose(), top_rows=2, protect=True)
    # deck rows (y+1 .. y+3) are walkable land
    for x in range(6):
        for y in (2, 3):
            a = cv.art[py + y][px + x]
            if a is not None:
                cv.art[py + y][px + x] = (a[0], a[1], 0, 0x100, True)
    # rocks / buoys
    buoy = art.Px(16, 16)
    buoy.rect(5, 4, 6, 8, (230, 57, 41)); buoy.rect(5, 7, 6, 2, (255, 255, 255)); buoy.outline()
    for (x, y) in ((8, 4), (14, 22), (34, 26), (6, 18)):
        cv.place_art(x, y, dict(img=buoy.im, solid={(0, 0)}, door=None))
    # deep water: a dark ring south of the platform where the ruins lie
    darkim = Image.new('RGBA', (16, 16), (8, 24, 82, 110))
    deep = {(x, y) for x in range(18, 36) for y in range(14, 27) if ((x - 27) / 9.0) ** 2 + ((y - 20) / 6.5) ** 2 <= 1.0}
    for (x, y) in deep:
        if cv.art[y][x] is None:
            cv.art[y][x] = (darkim, None, 0, 0x12, False)
    cv.add_obj(px + 2, py + 3, 49, 'R22_RoseGuide', move=8)
    cv.add_sign(px + 4, py + 3, 'R22_SignRose')
    cv.border = [0x170] * 4
    cv.deep = deep
    return cv
