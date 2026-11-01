"""Analyse metatile vocabulary: pixel terrain classification and vanilla usage statistics."""
import sys, json, struct
from pathlib import Path
from collections import Counter, defaultdict
sys.path.insert(0, '/home/claude/tools')
import render
R = Path('/home/claude/proj/sorgenti_romagna'); render.R = R
LAYOUTS = {l['id']: l for l in json.load(open(R/'data/layouts/layouts.json'))['layouts']}

def metatile_rgb(prim, sec, mid):
    mt, behav = render.metatile_images(prim, sec)
    return mt(mid)

def vanilla_usage(primary='gTileset_General'):
    """Return Counter of (metatile id -> count) and Counter of (id -> upper bits) over vanilla layouts using primary."""
    use = Counter(); bits = defaultdict(Counter); lay = []
    for l in LAYOUTS.values():
        if l['primary_tileset'] != primary: continue
        if 'Romagna' in l['id'] or l['id'] in ('LAYOUT_LITTLEROOT_TOWN','LAYOUT_OLDALE_TOWN','LAYOUT_ROUTE101'): continue
        p = R/l['blockdata_filepath']
        if not p.exists(): continue
        b = render.u16(p)
        lay.append((l, b))
        for v in b:
            use[(l['secondary_tileset'] if (v & 0x3FF) >= 512 else '', v & 0x3FF)] += 1
            bits[(l['secondary_tileset'] if (v & 0x3FF) >= 512 else '', v & 0x3FF)][v >> 10] += 1
    return use, bits, lay

if __name__ == '__main__':
    use, bits, lay = vanilla_usage()
    print(len(lay), 'layouts')
    prim = [(k[1], c) for k, c in use.items() if k[0] == '']
    prim.sort(key=lambda t: -t[1])
    for mid, c in prim[:80]:
        print('%03X %6d  bits %s' % (mid, c, dict(bits[('', mid)].most_common(3))))
