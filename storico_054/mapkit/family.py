"""Learn 8-neighbour autotiling of one tile family (e.g. Slateport cobbles) from vanilla layouts."""
import json, sys
from pathlib import Path
from collections import Counter, defaultdict
sys.path.insert(0, str(Path(__file__).parent))
import gfx

NB = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]


def learn(layout_ids, members):
    L = {l['id']: l for l in json.load(open(gfx.ROOT / 'data/layouts/layouts.json'))['layouts']}
    table = defaultdict(Counter)
    for lid in layout_ids:
        l = L[lid]
        b = gfx.u16s(gfx.ROOT / l['blockdata_filepath'])
        w, h = l['width'], l['height']
        for y in range(h):
            for x in range(w):
                v = b[y * w + x]
                if (v & 0x3FF) not in members:
                    continue
                mask = 0
                for i, (dx, dy) in enumerate(NB):
                    xx, yy = x + dx, y + dy
                    inside = not (0 <= xx < w and 0 <= yy < h) or (b[yy * w + xx] & 0x3FF) in members
                    mask |= inside << i
                table[mask][v & 0x3FF] += 1
    return table


class Family:
    def __init__(self, table, center):
        self.table, self.center = table, center

    def pick(self, mask):
        if mask in self.table:
            return self.table[mask].most_common(1)[0][0]
        # fallback: match orthogonal neighbours exactly, prefer most diagonal agreement
        ortho = [1, 3, 4, 6]
        best, bs = None, -1
        for m, c in self.table.items():
            if any(((m >> i) & 1) != ((mask >> i) & 1) for i in ortho):
                continue
            s = sum(((m >> i) & 1) == ((mask >> i) & 1) for i in range(8)) * 1000 + sum(c.values())
            if s > bs:
                best, bs = m, s
        if best is None:
            return self.center
        return self.table[best].most_common(1)[0][0]

    def paint(self, region, w, h):
        """region: set of (x,y). Returns {(x,y): id}."""
        out = {}
        for (x, y) in region:
            mask = 0
            for i, (dx, dy) in enumerate(NB):
                xx, yy = x + dx, y + dy
                inside = (xx, yy) in region or not (0 <= xx < w and 0 <= yy < h)
                mask |= inside << i
            out[(x, y)] = self.pick(mask)
        return out
