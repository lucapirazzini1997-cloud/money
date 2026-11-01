"""Map composition canvas: terrain autotiling + overlays + stamps + events -> pokeemerald map files."""
import json, pickle, struct, sys
from pathlib import Path
from PIL import Image, ImageDraw
sys.path.insert(0, str(Path(__file__).parent))
import gfx, autotile, tsbuild

GBITS = pickle.load(open(Path(__file__).parent / 'general_bits.pkl', 'rb'))

# Named General metatiles
G = dict(
    grass=0x001, tall=0x00D, flowers=0x004, sign=0x003, wsign=0x01B, bush=0x00E,
    tree_tl=0x1D4, tree_tr=0x1D5, tree_bl=0x1DC, tree_br=0x1DD, tree_bl_g=0x1E4, tree_br_g=0x1E5,
    cap_l=0x1CE, cap_r=0x1CF,
    sp_tl=0x118, sp_t=0x119, sp_tr=0x11A, sp_l=0x120, sp_c=0x121, sp_r=0x122, sp_bl=0x128, sp_b=0x129, sp_br=0x12A,
    ledge_l=0x0D5, ledge=0x087, ledge_r=0x0D6,
)


def bits_for(mid, coll=None, elev=None):
    b = GBITS.get(mid, 12)
    c, e = b & 3, b >> 2
    if coll is not None:
        c = coll
    if elev is not None:
        e = elev
    return (c << 10) | (e << 12)


class Stamp:
    """A rectangular block of cells. cells[y][x] = (key, coll, elev) or None (transparent: keep what's below)."""
    def __init__(self, cells, anchors=None, name=None):
        self.cells = cells
        self.h = len(cells)
        self.w = len(cells[0]) if cells else 0
        self.anchors = anchors or {}
        self.name = name


class Canvas:
    def __init__(self, w, h, base='grass', name=None):
        self.w, self.h, self.name = w, h, name
        self.terrain = [[base] * w for _ in range(h)]
        self.over = [[None] * w for _ in range(h)]
        self.pathmask = [[False] * w for _ in range(h)]
        self.pathstyle = {}
        self.npcs, self.warps, self.signs, self.triggers = [], [], [], []
        self.border = [0x1D4, 0x1D5, 0x1DC, 0x1DD]
        self.tags = {}
        self.art = [[None] * w for _ in range(h)]   # (bottom RGBA, top RGBA, coll, behavior, layer)
        self.fam = [[None] * w for _ in range(h)]   # family painters: (Family, metas_by_id, coll, elev)
        self.famregions = []

    # --- terrain ---
    def fill(self, x, y, w, h, cls):
        for yy in range(max(0, y), min(self.h, y + h)):
            for xx in range(max(0, x), min(self.w, x + w)):
                self.terrain[yy][xx] = cls

    def fill_fn(self, fn):
        for y in range(self.h):
            for x in range(self.w):
                c = fn(x, y)
                if c:
                    self.terrain[y][x] = c

    def path(self, x, y, w, h):
        for yy in range(max(0, y), min(self.h, y + h)):
            for xx in range(max(0, x), min(self.w, x + w)):
                self.pathmask[yy][xx] = True

    # --- overlays ---
    def put(self, x, y, key, coll=None, elev=None):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.over[y][x] = (key, coll, elev)

    def rect(self, x, y, w, h, key, coll=None, elev=None):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.put(xx, yy, key, coll, elev)

    def clear(self, x, y, w=1, h=1):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                if 0 <= xx < self.w and 0 <= yy < self.h:
                    self.over[yy][xx] = None

    def stamp(self, x, y, st, name=None):
        for yy in range(st.h):
            for xx in range(st.w):
                c = st.cells[yy][xx]
                if c is not None:
                    self.put(x + xx, y + yy, *c)
        if name:
            self.tags[name] = (x, y, st)
        return {k: (x + ax, y + ay) for k, (ax, ay) in st.anchors.items()}

    def tree(self, x, y):
        """Place a 2x2 tree with its top-left at x,y (bottom tiles fixed up in finalize)."""
        if any(0 <= x + dx < self.w and 0 <= y + dy < self.h and self.art[y + dy][x + dx] is not None
               for dx in (0, 1) for dy in (0, 1)):
            return                        # never draw a tree through art already placed there
        self.put(x, y, G['tree_tl'], 1, 0)
        self.put(x + 1, y, G['tree_tr'], 1, 0)
        self.put(x, y + 1, ('treebot', 0), 1, 0)
        self.put(x + 1, y + 1, ('treebot', 1), 1, 0)

    def forest(self, x, y, w, h, keep=None):
        """Fill a rectangle with aligned 2x2 trees. keep(x,y) -> False skips that tree."""
        for yy in range(y, y + h - 1, 2):
            for xx in range(x, x + w - 1, 2):
                if keep is None or keep(xx, yy):
                    self.tree(xx, yy)

    def free(self, x, y):
        return 0 <= x < self.w and 0 <= y < self.h and self.over[y][x] is None and not self.pathmask[y][x] \
            and self.terrain[y][x] in ('grass',)

    def place_art(self, x, y, asset, behaviors=None, top_rows=0, coll=None, protect=False, walkable=False, overlay=False):
        """Overlay an art asset (dict from art.py or a bare RGBA image) with its cell grid at x,y.
        top_rows: number of upper cell rows drawn on the top layer (cover the player)."""
        if isinstance(asset, Image.Image):
            asset = dict(img=asset, solid=set(), door=None, w=asset.width // 16, h=asset.height // 16)
        img = asset['img']
        cw, ch = img.width // 16, img.height // 16
        solid = asset.get('solid', set()) if coll is None else (set((a, b) for a in range(cw) for b in range(ch)) if coll else set())
        # ---- overlaps between separately placed assets: a small decoration (tree, bench, lamp, flowerbed...)
        # never cuts into a building; a building placed later removes the small decorations under it
        if not hasattr(self, '_pl'):
            self._pl, self._own, self.overlaps = {}, {}, []
        pid = len(self._pl) + 1
        cells = []
        for cy in range(ch):
            for cx in range(cw):
                piece = img.crop((cx * 16, cy * 16, cx * 16 + 16, cy * 16 + 16))
                if piece.getbbox() is not None and 0 <= x + cx < self.w and 0 <= y + cy < self.h:
                    cells.append((x + cx, y + cy, piece))
        def hits(X, Y, piece):
            o = self._own.get((X, Y))
            if o is None or self.art[Y][X] is None:
                return None
            old = self.art[Y][X][0] or self.art[Y][X][1]
            if old is None or old.getchannel('A').getextrema()[0] == 255:
                return None                      # ground-like full tile (rims, decks): drawing over it is fine
            from PIL import ImageChops
            a1 = old.getchannel('A').point(lambda v: 255 if v > 127 else 0)
            a2 = piece.getchannel('A').point(lambda v: 255 if v > 127 else 0)
            return o if ImageChops.multiply(a1, a2).getbbox() is not None else None
        conf = {o for (X, Y, pc) in cells for o in [hits(X, Y, pc)] if o is not None}
        small = len(cells) <= 4
        if conf and not walkable and not overlay:
            if small and any(len(self._pl[o]) > len(cells) for o in conf):
                self.overlaps.append(('skipped', x, y))
                d = asset.get('door')
                return (x + d[0], y + d[1]) if d else None
            for o in conf:
                if len(self._pl[o]) <= 4 and len(self._pl[o]) < len(cells):
                    for (X, Y) in self._pl[o]:
                        if self._own.get((X, Y)) == o:
                            self.art[Y][X] = None; del self._own[(X, Y)]
                    self.overlaps.append(('removed', self._pl[o][0]))
                else:
                    self.overlaps.append(('over', x, y))
        # General 2x2 trees under the new art are removed whole (no half trees sticking out)
        if not overlay:
            for (X, Y, _) in cells:
                o = self.over[Y][X]
                if o is None:
                    continue
                k = o[0]
                if k == G['tree_tl']: ox, oy = X, Y
                elif k == G['tree_tr']: ox, oy = X - 1, Y
                elif isinstance(k, tuple) and k[0] == 'treebot': ox, oy = X - k[1], Y - 1
                else: continue
                for (tx, ty) in ((ox, oy), (ox + 1, oy), (ox, oy + 1), (ox + 1, oy + 1)):
                    if 0 <= tx < self.w and 0 <= ty < self.h:
                        self.over[ty][tx] = None
        self._pl[pid] = [(X, Y) for (X, Y, _) in cells]
        for (X, Y, _) in cells:
            self._own[(X, Y)] = pid
        for cy in range(ch):
            for cx in range(cw):
                piece = img.crop((cx * 16, cy * 16, cx * 16 + 16, cy * 16 + 16))
                if piece.getbbox() is None:
                    continue
                X, Y = x + cx, y + cy
                if not (0 <= X < self.w and 0 <= Y < self.h):
                    continue
                beh = 0
                if behaviors and (cx, cy) in behaviors:
                    beh = behaviors[(cx, cy)]
                if asset.get('door') == (cx, cy):
                    beh = 0x60
                if walkable:
                    beh = 0x100      # marker: force MB_NORMAL at land elevation
                if cy < top_rows:
                    self.art[Y][X] = (None, piece, 0, beh, protect)
                else:
                    self.art[Y][X] = (piece, None, 1 if (cx, cy) in solid else 0, beh, protect)
        d = asset.get('door')
        return (x + d[0], y + d[1]) if d else None

    def hedge(self, cells):
        import art
        if not hasattr(Canvas, '_hedge'):
            Canvas._hedge = art.hedge_tiles()
        cells = set(cells)
        for (x, y) in cells:
            key = ''.join(k for k, (dx, dy) in zip('NESW', ((0, -1), (1, 0), (0, 1), (-1, 0))) if (x + dx, y + dy) in cells)
            self.place_art(x, y, dict(img=Canvas._hedge[key], solid={(0, 0)}, door=None))

    def hline_cells(self, x, y, w):
        return [(x + i, y) for i in range(w)]

    def vline_cells(self, x, y, h):
        return [(x, y + i) for i in range(h)]

    def paint_family(self, fam, metas, region, coll=0, elev=3):
        """Paint an imported tile family (e.g. cobbles) over a set of cells."""
        ids = fam.paint(region, self.w, self.h)
        for (x, y), mid in ids.items():
            self.over[y][x] = (metas[mid], coll, elev)

    # --- events ---
    def npc(self, x, y, gfx_id, script, move='MOVEMENT_TYPE_FACE_DOWN', flag='0', rx=0, ry=0, trainer='TRAINER_TYPE_NONE', sight='0', elev=3):
        self.npcs.append(dict(graphics_id=gfx_id, x=x, y=y, elevation=elev, movement_type=move, movement_range_x=rx,
                              movement_range_y=ry, trainer_type=trainer, trainer_sight_or_berry_tree_id=str(sight),
                              script=script, flag=flag))

    def warp(self, x, y, dest, dest_warp, elev=0):
        self.warps.append(dict(x=x, y=y, elevation=elev, dest_map=dest, dest_warp_id=str(dest_warp)))
        return len(self.warps) - 1

    def sign(self, x, y, script, elev=0, kind='BG_EVENT_PLAYER_FACING_ANY'):
        self.signs.append(dict(type='sign', x=x, y=y, elevation=elev, player_facing_dir=kind, script=script))

    def hidden(self, x, y, item, flag, elev=3):
        self.signs.append(dict(type='hidden_item', x=x, y=y, elevation=elev, item=item, flag=flag))

    def trigger(self, x, y, script, var='VAR_TEMP_0', val='0', elev=3):
        self.triggers.append(dict(type='trigger', x=x, y=y, elevation=elev, var=var, var_value=str(val), script=script))

    # --- compile ---
    def _path_tile(self, x, y):
        m = self.pathmask
        def p(xx, yy):
            if not (0 <= xx < self.w and 0 <= yy < self.h):
                return True
            return m[yy][xx]
        t, b, l, r = p(x, y - 1), p(x, y + 1), p(x - 1, y), p(x + 1, y)
        if t and b and l and r:
            return G['sp_c']
        if not t and not l:
            return G['sp_tl']
        if not t and not r:
            return G['sp_tr']
        if not b and not l:
            return G['sp_bl']
        if not b and not r:
            return G['sp_br']
        if not t:
            return G['sp_t']
        if not b:
            return G['sp_b']
        if not l:
            return G['sp_l']
        if not r:
            return G['sp_r']
        return G['sp_c']

    def compile(self):
        """Return 2D grid of (key, bits) where key is int General id or a Meta object."""
        flat = [c for row in self.terrain for c in row]
        vals, _ = autotile.paint(flat, self.w, self.h)
        grid = [[(vals[y * self.w + x] & 0x3FF, vals[y * self.w + x] & 0xFC00) for x in range(self.w)] for y in range(self.h)]
        for y in range(self.h):
            for x in range(self.w):
                if self.pathmask[y][x]:
                    t = self._path_tile(x, y)
                    grid[y][x] = (t, bits_for(t, 0, 3))
        # tree bottoms
        for y in range(self.h):
            for x in range(self.w):
                o = self.over[y][x]
                if o is None:
                    continue
                key, coll, elev = o
                if isinstance(key, tuple) and key[0] == 'treebot':
                    below = self.over[y + 1][x] if y + 1 < self.h else None
                    tree_below = below is not None and below[0] in (G['tree_tl'], G['tree_tr'])
                    if y + 1 >= self.h:
                        tree_below = True
                    key = (G['tree_bl'] if tree_below else G['tree_bl_g']) if key[1] == 0 else (G['tree_br'] if tree_below else G['tree_br_g'])
                if isinstance(key, int):
                    grid[y][x] = (key, bits_for(key, coll, elev))
                else:
                    c = key.coll if coll is None else coll
                    e = key.elev if elev is None else elev
                    grid[y][x] = (key, (c << 10) | (e << 12))
        # art overlays composited over whatever ground is there
        for y in range(self.h):
            for x in range(self.w):
                a = self.art[y][x]
                if a is None:
                    continue
                bot_art, top_art, coll, beh, prot = a
                key, bits = grid[y][x]
                cm = composite(key, bot_art, top_art, coll, beh, bits)
                if prot:
                    cm.protect = True
                # acqua navigabile (stagno/oceano/profonda): elevazione 1 come in Smeraldo, altrimenti ci si cammina sopra
                eb = (1 << 12) if beh in SURF_BEH else ((3 << 12) if beh == 0x100 else (bits & 0xF000))
                grid[y][x] = (cm, (coll << 10) | eb)
        return grid

    def metas(self, grid=None):
        grid = grid or self.compile()
        out, seen = [], set()
        for row in grid:
            for key, _ in row:
                if not isinstance(key, int) and id(key) not in seen:
                    seen.add(id(key))
                    out.append(key)
        return out


SURF_BEH = {0x10, 0x11, 0x12, 0x14, 0x15}
_GPAIR = None
_COMP = {}


def base_layers(key):
    """Bottom/top images of a ground metatile normalised to NORMAL layering (top = over the player)."""
    global _GPAIR
    if isinstance(key, int):
        if _GPAIR is None:
            _GPAIR = gfx.Pair('gTileset_General', 'gTileset_Petalburg')
        b, t, a = _GPAIR.layer_rgba(key, 0), _GPAIR.layer_rgba(key, 1), _GPAIR.attr(key)
        beh, layer = a & 0xFF, (a >> 12) & 0xF
    else:
        b, t, beh, layer = key.bottom, key.top, key.behavior, key.layer
    if layer == 1:  # COVERED: both layers are under the player -> flatten
        f = b.copy(); f.alpha_composite(t)
        return f, Image.new('RGBA', (16, 16), (0, 0, 0, 0)), beh
    return b, t, beh


def composite(key, bot_art, top_art, coll, beh, bits):
    k = (key if isinstance(key, int) else id(key), bot_art.tobytes() if bot_art else None, top_art.tobytes() if top_art else None, coll, beh)
    if k in _COMP:
        return _COMP[k]
    b, t, base_beh = base_layers(key)
    b = b.copy(); t = t.copy()
    if bot_art is not None:
        b.alpha_composite(bot_art)
    if top_art is not None:
        t.alpha_composite(top_art)
    if beh == 0x100:
        m = tsbuild.Meta(b, t, behavior=0, layer=0, coll=0, elev=3)
    else:
        m = tsbuild.Meta(b, t, behavior=beh if beh else (base_beh if not coll else 0), layer=0, coll=coll, elev=(bits >> 12))
    _COMP[k] = m
    return m


def build_tileset(canvases, ts_name, folder, extra_metas=()):
    """Build one secondary tileset shared by canvases. Returns {id(meta): metatile id}."""
    metas, seen = [], set()
    grids = []
    for cv in canvases:
        g = cv.compile()
        grids.append(g)
        for m in cv.metas(g):
            if id(m) not in seen:
                seen.add(id(m))
                metas.append(m)
    for m in extra_metas:
        if id(m) not in seen:
            seen.add(id(m))
            metas.append(m)
    out = gfx.ROOT / 'data/tilesets/secondary' / folder
    ids = tsbuild.build(metas, out) if metas else tsbuild.build([tsbuild.Meta(None)], out)
    return {id(m): i for m, i in zip(metas, ids)}, grids


def write_layout(cv, grid, idmap, layout_dir):
    vals = []
    for row in grid:
        for key, bits in row:
            mid = key if isinstance(key, int) else idmap[id(key)]
            vals.append(mid | bits)
    d = gfx.ROOT / layout_dir
    d.mkdir(parents=True, exist_ok=True)
    (d / 'map.bin').write_bytes(struct.pack('<%dH' % len(vals), *vals))
    bvals = []
    for k in cv.border:
        mid = k if isinstance(k, int) else idmap[id(k)]
        bvals.append(mid | bits_for(mid) if isinstance(k, int) else mid | (1 << 10))
    (d / 'border.bin').write_bytes(struct.pack('<4H', *bvals))
    return vals


def preview(cv, grid, idmap, ts_folder, out, markers=True, scale=1):
    """Render using the freshly built tileset."""
    class T(gfx.Tileset):
        def __init__(self, d):
            img = Image.open(d / 'tiles.png'); w, h = img.size; raw = img.tobytes()
            self.name = d.name
            self.tiles = [tuple(raw[((t // (w // 8)) * 8 + y) * w + (t % (w // 8)) * 8 + x] & 15 for y in range(8) for x in range(8)) for t in range((w // 8) * (h // 8))]
            self.pals = [gfx.read_pal(d / 'palettes' / ('%02d.pal' % i)) for i in range(16)]
            self.metas = gfx.u16s(d / 'metatiles.bin'); self.attrs = gfx.u16s(d / 'metatile_attributes.bin')
    pair = gfx.Pair(gfx.tileset('gTileset_General', 'primary'), T(gfx.ROOT / 'data/tilesets/secondary' / ts_folder))
    im = Image.new('RGB', (cv.w * 16, cv.h * 16))
    for y, row in enumerate(grid):
        for x, (key, bits) in enumerate(row):
            mid = key if isinstance(key, int) else idmap[id(key)]
            im.paste(pair.render(mid), (x * 16, y * 16))
    if markers:
        d = ImageDraw.Draw(im)
        for o in cv.npcs:
            x, y = o['x'] * 16, o['y'] * 16
            d.ellipse([x + 3, y + 3, x + 12, y + 12], fill=(255, 40, 40), outline=(0, 0, 0))
        for o in cv.warps:
            x, y = o['x'] * 16, o['y'] * 16
            d.rectangle([x + 2, y + 2, x + 13, y + 13], outline=(40, 40, 255), width=2)
        for o in cv.signs:
            x, y = o['x'] * 16, o['y'] * 16
            d.rectangle([x + 5, y + 5, x + 10, y + 10], fill=(250, 220, 0))
        for o in cv.triggers:
            x, y = o['x'] * 16, o['y'] * 16
            d.line([x + 2, y + 2, x + 13, y + 13], fill=(255, 0, 255), width=2)
    if scale != 1:
        im = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
    im.save(out)
    return im
