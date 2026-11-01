"""Import metatiles from vanilla secondaries (optionally recoloured) as Meta objects."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import gfx, tsbuild, family

_pairs = {}


def pair(sec):
    if sec not in _pairs:
        _pairs[sec] = gfx.Pair('gTileset_General', sec)
    return _pairs[sec]


def recolor_img(im, fn):
    im = im.copy()
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a:
                px[x, y] = fn((r, g, b)) + (a,)
    return im


def meta(sec, mid, recolor=None, **kw):
    m = tsbuild.meta_from(pair(sec), mid, **kw)
    if recolor:
        m.bottom = recolor_img(m.bottom, recolor)
        m.top = recolor_img(m.top, recolor)
        m.palkeys = [None] * 8
    return m


def metas(sec, ids, recolor=None, **kw):
    return {i: meta(sec, i, recolor, **kw) for i in ids}


def warm_stone(c):
    """Grey cobbles -> warm sandstone."""
    r, g, b = c
    if abs(r - g) < 24 and abs(g - b) < 30:  # greyish
        l = (r + g + b) / 3
        return (min(255, int(l * 1.06 + 10)), min(255, int(l * 0.98 + 4)), min(255, int(l * 0.84)))
    return c


_fam_cache = {}


def cobbles(recolor=None):
    key = ('cobbles', recolor)
    if key in _fam_cache:
        return _fam_cache[key]
    mem = [0x208, 0x209, 0x20A, 0x210, 0x211, 0x212, 0x218, 0x219, 0x21A, 0x232, 0x233, 0x23A, 0x23B]
    t = family.learn(['LAYOUT_SLATEPORT_CITY'], set(mem))
    fam = family.Family(t, 0x211)
    ms = metas('gTileset_Slateport', mem, recolor)
    _fam_cache[key] = (fam, ms)
    return fam, ms
