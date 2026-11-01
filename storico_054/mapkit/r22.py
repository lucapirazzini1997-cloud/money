"""Bridge mapkit canvases -> Romagna 0.22 binary ROM (via /home/claude/r22/inject.py)."""
import sys, struct
from pathlib import Path
sys.path.insert(0, '/home/claude/r22')
sys.path.insert(0, str(Path(__file__).parent))
import romlib
import canvas, check
from canvas import Canvas, G, bits_for

ROM = romlib.Rom(str(Path(__file__).resolve().parents[1] / 'base31.gba'))
GENERAL = 0x55e8c0


def ev(g, n):
    m = ROM.map(g, n)
    return dict(objects=[dict(o) for o in m['objects']], warps=[dict(w) for w in m['warps']],
                coords=[dict(c) for c in m['coords']], bgs=[dict(b) for b in m['bgs']], conns=m['conns'], m=m)


class RCanvas(Canvas):
    """Canvas whose events are stored in binary form (romlib dicts)."""
    def __init__(self, w, h, gn, base='grass', name=None):
        super().__init__(w, h, base, name)
        self.gn = gn
        e = ev(*gn)
        self.old = e
        self.objs = [dict(o) for o in e['objects']]
        self.bwarps = [dict(w) for w in e['warps']]
        self.bcoords = [dict(c) for c in e['coords']]
        self.bbgs = [dict(b) for b in e['bgs']]
        self.conns = [dict(c) for c in e['conns']]
        self.script_refs = {}      # label -> list of setter callables (filled after scripts assemble)

    # positions
    def place_objs(self, pos):
        for i, (x, y) in pos.items():
            self.objs[i - 1]['x'], self.objs[i - 1]['y'] = x, y

    def set_warp(self, i, x, y):
        self.bwarps[i]['x'], self.bwarps[i]['y'] = x, y

    def add_sign(self, x, y, label_or_ptr):
        self.bbgs.append(dict(x=x, y=y, elev=0, kind=0, arg=label_or_ptr))

    def add_obj(self, x, y, gfx, script, flag=0, move=8, rx=0, ry=0, ttype=0, trange=0, elev=3):
        self.objs.append(dict(x=x, y=y, gfx=gfx, script=script, flag=flag, move=move, rx=rx, ry=ry, ttype=ttype, trange=trange, elev=elev))
        return len(self.objs)

    def add_coord(self, x, y, script, var=0x4001, val=0):
        self.bcoords.append(dict(x=x, y=y, elev=3, var=var, val=val, script=script))

    def locked(self, door, label='R22_LockedDoor'):
        """Make a door cell solid and attach the 'locked' sign."""
        x, y = door
        a = self.art[y][x]
        if a is not None:
            self.art[y][x] = (a[0], a[1], 1, 0, a[4])
        self.add_sign(x, y, label)


def vals_of(cv, grid, idmap):
    out = []
    for row in grid:
        for key, bits in row:
            mid = key if isinstance(key, int) else idmap[id(key)]
            out.append(mid | bits)
    return out


def border_of(cv, idmap):
    b = []
    for k in cv.border:
        mid = k if isinstance(k, int) else idmap[id(k)]
        b.append(mid | (bits_for(mid) if isinstance(k, int) else (1 << 10)))
    return b


def static_check(cv, grid, starts, surf=False):
    # map binary events to the json-ish structures expected by check
    cv.npcs = [dict(x=o['x'], y=o['y'], graphics_id='ITEM' if o['gfx'] == 59 else str(o['gfx']), script=str(i + 1)) for i, o in enumerate(cv.objs)]
    cv.warps = [dict(x=w['x'], y=w['y'], dest_map='%d,%d' % (w['group'], w['num'])) for w in cv.bwarps if (w['x'], w['y']) not in ((0, 0), (1, 0))]
    cv.signs = [dict(x=b['x'], y=b['y'], script=str(b['arg'])) for b in cv.bbgs]
    cv.triggers = [dict(x=c['x'], y=c['y'], script=str(c['script'])) for c in cv.bcoords]
    return check.check(cv, grid, starts, surf=surf, verbose=False)


def edge_warp_behaviours(cv):
    from PIL import Image
    clear = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    for w in cv.bwarps:
        x, y = w['x'], w['y']
        if (x, y) in ((0, 0), (1, 0)) and w.get('placeholder', True) and not (0 < x < cv.w - 1):
            pass
        beh = 0x64 if y == 0 else 0x65 if y == cv.h - 1 else 0x63 if x == 0 else 0x62 if x == cv.w - 1 else None
        if beh is None:
            continue
        a = cv.art[y][x]
        if a is None:
            cv.art[y][x] = (clear, None, 0, beh, False)
        elif a[3] == 0:
            cv.art[y][x] = (a[0], a[1], 0, beh, a[4])


def build(cv, folder, starts, preview=None, surf=False):
    if not getattr(cv, 'is_room', False):
        edge_warp_behaviours(cv)
    idmap, grids = canvas.build_tileset([cv], folder, folder)
    grid = grids[0]
    if getattr(cv, 'void_cell', None):
        vx, vy = cv.void_cell
        cv.border = [grid[vy][vx][0]] * 4
    probs, _ = static_check(cv, grid, starts, surf)
    if preview:
        canvas.preview(cv, grid, idmap, folder, preview, markers=True)
    return dict(cv=cv, folder=folder, vals=vals_of(cv, grid, idmap), border=border_of(cv, idmap), problems=probs)


def emit(W, res, labels):
    """Write a built canvas into the Writer W. labels: assembled script labels (name -> rom offset)."""
    cv = res['cv']
    g, n = cv.gn
    sec = W.secondary_from_folder(res['folder'])
    W.set_layout(g, n, res['vals'], cv.w, cv.h, res['border'], GENERAL, sec)

    def rs(v):
        return labels[v] if isinstance(v, str) else v
    objs = []
    for o in cv.objs:
        o = dict(o); o['script'] = rs(o.get('script')); objs.append(o)
    bgs = []
    for b in cv.bbgs:
        b = dict(b)
        if isinstance(b['arg'], str): b['arg'] = 0x08000000 + labels[b['arg']]
        bgs.append(b)
    coords = []
    for c in cv.bcoords:
        c = dict(c); c['script'] = rs(c['script']); coords.append(c)
    W.set_events(g, n, objs, cv.bwarps, coords, bgs)
    W.set_connections(g, n, cv.conns)
