"""0.48 - case di passaggio ("caselli") ad ogni cambio di luogo, sul modello del Varco delle Saline di Cervia.

Ogni passaggio = una casa in ciascuna delle due mappe (sulla strada, al bordo) + una stanza interna passante.
  - strade E/O: il varco di mattoni `art22.gatehouse` (porta ad arco sul lato della strada, warp a freccia)
  - strade N/S: casello di mattoni con porta ad arco al centro in basso (porta normale, 0x60)
    sul lato sud (strada che esce verso sud) la casa chiude la strada e si gira attorno per entrare dalla porta.
"""
import collections
from kit48 import *
import cervia_int as CI
from cervia_int import side_wall, side_exit, office_counter, marble_floor, set_floor, big_plant
import art22, canvas
from art import Px, C, PAL, coppi_roof, signboard, text_width
import interior as I

GATES = []        # registro per relazione/test


# ------------------------------------------------------------------ arte
def casello_front(cw=4, ch=5, name='', door_col=1):
    """Casello di mattoni visto da sud, porta ad arco in basso alla colonna door_col."""
    Wd, Hd = cw * 16, ch * 16
    g = Px(Wd, Hd)
    b = PAL['brick']
    roof_h = 30 if ch >= 5 else (26 if ch == 4 else (22 if ch == 3 else 14))
    dh = 22 if ch >= 3 else 16
    coppi_roof(g, 0, 0, Wd, roof_h, PAL['roof'])
    top = roof_h - 2
    g.rect(2, top, Wd - 4, Hd - top, b[1])
    for y in range(top + 3, Hd, 4):
        g.hline(2, y, Wd - 4, b[2])
        o = 0 if (y // 4) % 2 else 4
        for x in range(2 + o, Wd - 2, 8):
            g.vline(x, y - 3, 3, b[2])
    g.hline(2, top, Wd - 4, b[3])
    if name:
        signboard(g, (Wd // 2 if ch >= 4 else (Wd - 3 - (text_width(name) + 6) // 2 if door_col <= cw // 2 - 1 else 3 + (text_width(name) + 6) // 2)), top + 4, name, bg=C(255, 247, 222), fg=C(66, 99, 140))
    for c in range(cw):
        if c == door_col:
            continue
        wx = c * 16 + 3
        wy = Hd - 32 if ch >= 5 else Hd - 20
        if ch >= 4 and c not in (door_col,):
            g.rect(wx, wy, 10, 10, C(239, 231, 214)); g.rect(wx + 1, wy + 1, 8, 8, C(140, 189, 214)); g.vline(wx + 5, wy + 1, 8, C(239, 231, 214))
    ax = door_col * 16
    g.rect(ax + 1, Hd - dh, 14, dh, C(239, 231, 206))
    g.rect(ax + 3, Hd - dh + 3, 10, dh - 3, C(57, 41, 41)); g.hline(ax + 4, Hd - dh + 2, 8, C(57, 41, 41))
    g.rect(ax + 3, Hd - 6, 10, 6, C(198, 173, 140))
    g.outline()
    solid = {(x, y) for x in range(cw) for y in range(ch)}
    dc = (door_col, ch - 1)
    solid.discard(dc)
    return dict(img=g.im, solid=solid, door=dc)


# ------------------------------------------------------------------ stanza interna passante
def gate_room(gn, east_warp, west_warp, guard_script, name_e, name_w, wall='ochre'):
    """Come CI.gate (12x7): porta est -> east_warp, porta ovest -> west_warp. name_*: cartelli ai lati del banco."""
    Wd, Hd = 12, 7
    r = I.Room(Wd, Hd, gn, floor='tiles', wall=wall, wall_rows=2)
    r.objs, r.bwarps, r.bcoords, r.bbgs = [], [], [], []
    set_floor(r, marble_floor)
    r.void([(x, Hd - 1) for x in range(Wd)])
    for y in range(2, Hd - 1):
        for x in (0, Wd - 1):
            r.art[y][x] = (side_wall(), None, 1, 0, False)
    ey = 4
    r.art[ey][Wd - 1] = (side_exit(marble_floor(Wd - 1, ey), True), None, 0, 0x62, False)
    r.art[ey][0] = (side_exit(marble_floor(0, ey), False), None, 0, 0x63, False)
    r.bwarps.append(dict(x=Wd - 1, y=ey, elev=0, warp=east_warp[2], num=east_warp[1], group=east_warp[0]))
    r.bwarps.append(dict(x=0, y=ey, elev=0, warp=west_warp[2], num=west_warp[1], group=west_warp[0]))
    r.furn(4, 2, office_counter(4), top_rows=1)
    for x in range(4, 8):
        a = r.art[3][x]; r.art[3][x] = (a[0], a[1], 1, 0x80, a[4])
    r.furn(5, 0, I.window_art(wall, C(57, 99, 165)))
    r.furn(1, 2, big_plant()); r.furn(10, 2, big_plant())
    # cartelli: a sinistra la direzione ovest, a destra la direzione est
    r.furn(1, 0, poster(name_w, '<')); r.furn(9, 0, poster(name_e, '>'))
    r.add_obj(6, 2, 22, guard_script, move=8)
    r.void_cell = (0, Hd - 1)
    return r


def poster(text, arrow):
    Wd = 32
    g = Px(Wd, 16)
    g.rect(0, 1, Wd, 13, C(140, 90, 57)); g.rect(1, 2, Wd - 2, 11, C(239, 222, 181))
    from art import text as drawtext, text_width
    t = text if text_width(text) <= Wd - 4 else text[:6]
    drawtext(g, 3, 5, t, C(66, 49, 49))
    g.outline()
    return dict(img=g.im, solid={(0, 0), (1, 0)}, door=None)


# ------------------------------------------------------------------ strumenti sul canvas "live"
def isgrass(cv, x, y):
    if not (0 <= x < cv.w and 0 <= y < cv.h) or cv.art[y][x] is not None: return False
    o = cv.over[y][x]
    return o is None or (o[0] == 1 and not o[1])


WATER_BEH = {0x10, 0x11, 0x12, 0x13, 0x15, 0x19}
_LAY = {}


def _over_beh(cv, key):
    k = (cv.gn, key)
    if k not in _LAY:
        import _stamps
        try:
            _LAY[k] = _stamps._layers(V.LIVE.map(*cv.gn))(key)[2]
        except Exception:
            _LAY[k] = 0
    return _LAY[k]


SURF = [False]      # True: l'acqua e' attraversabile (Surf) nei controlli di raggiungibilita'


def cell_blocked(cv, x, y):
    a = cv.art[y][x]
    if a is not None: return bool(a[2]) or (a[3] in WATER_BEH and not SURF[0])
    o = cv.over[y][x]
    if o is None: return False
    key, coll, elev = o
    if isinstance(key, int) and key < 512 and _over_beh(cv, key) in WATER_BEH and not SURF[0]: return True
    if coll is not None: return bool(coll)
    if isinstance(key, int): return bool(canvas.GBITS.get(key, 12) & 3)
    return bool(key.coll)


def blocked_cells(cv):
    return {(x, y) for y in range(cv.h) for x in range(cv.w) if cell_blocked(cv, x, y)}


def to_grass(cv, x, y):
    if 0 <= x < cv.w and 0 <= y < cv.h:
        cv.art[y][x] = None;cv.over[y][x] = None;cv.pathmask[y][x] = False


def reach(cv, start, extra_block=()):
    """Celle raggiungibili a piedi da start (collisione dell'arte + oggetti)."""
    blk = blocked_cells(cv) | {(o['x'], o['y']) for o in cv.objs} | set(extra_block)
    seen = {start};todo = [start]
    while todo:
        x, y = todo.pop()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            p = (x + dx, y + dy)
            if 0 <= p[0] < cv.w and 0 <= p[1] < cv.h and p not in seen and p not in blk:
                seen.add(p);todo.append(p)
    return seen


def varco(side, name, ch=4):
    """Varco E/O (come art22.gatehouse, ma con altezza ch in celle). side: faccia della porta ('east'|'west')."""
    cw = 4
    Wd, Hd = cw * 16, ch * 16
    g = Px(Wd, Hd)
    b = PAL['brick']
    roof_h = 30 if ch >= 5 else 26
    coppi_roof(g, 0, 0, Wd, roof_h, PAL['roof'])
    top = roof_h - 2
    g.rect(2, top, Wd - 4, Hd - top, b[1])
    for y in range(top + 3, Hd, 4):
        g.hline(2, y, Wd - 4, b[2])
        o = 0 if (y // 4) % 2 else 4
        for x in range(2 + o, Wd - 2, 8):
            g.vline(x, y - 3, 3, b[2])
    g.hline(2, top, Wd - 4, b[3])
    signboard(g, Wd // 2, top + 4, name, bg=C(255, 247, 222), fg=C(66, 99, 140))
    wx = 8 if side == 'east' else Wd - 20
    wy = Hd - 24
    g.rect(wx, wy, 10, 10, C(239, 231, 214)); g.rect(wx + 1, wy + 1, 8, 8, C(140, 189, 214)); g.vline(wx + 5, wy + 1, 8, C(239, 231, 214))
    ax = Wd - 16 if side == 'east' else 0
    g.rect(ax + 1, Hd - 22, 14, 22, C(239, 231, 206))
    g.rect(ax + 3, Hd - 19, 10, 19, C(57, 41, 41)); g.hline(ax + 4, Hd - 20, 8, C(57, 41, 41))
    g.rect(ax + 3, Hd - 6, 10, 6, C(198, 173, 140))
    g.outline()
    solid = {(x, y) for x in range(cw) for y in range(ch)}
    dc = (cw - 1 if side == 'east' else 0, ch - 1)
    solid.discard(dc)
    return dict(img=g.im, solid=solid, door=dc)


def touched_events(cv, cells):
    """Oggetti e cartelli (bg) che cadono nelle celle toccate: vanno spostati/rimossi a mano nella specifica."""
    cells = set(cells)
    objs = [(i, o['x'], o['y'], o['gfx']) for i, o in enumerate(cv.objs) if (o['x'], o['y']) in cells]
    bgs = [(i, b['x'], b['y']) for i, b in enumerate(cv.bbgs) if (b['x'], b['y']) in cells]
    return objs, bgs


def rect_cells(r):
    x0, y0, x1, y1 = r
    return {(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)}


TUNNEL = [False]     # 0.50: i lati sud sono sottopassi (si entra camminando verso sud)


def paving(x, y):
    g = Px(16, 16)
    g.rect(0, 0, 16, 16, C(198, 181, 148))
    for i in range(0, 16, 5):
        g.hline(0, (i + 3 * (x % 2)) % 16, 16, C(173, 156, 124))
    g.vline((x * 5 + y * 3) % 16, 0, 16, C(173, 156, 124))
    return g.im


def tunnel_img(cw, ch, name):
    """Portale di mattoni visto dall'alto: tetto a coppi con cartello sulla prima riga, pilastri di mattoni ai lati."""
    Wd, Hd = cw * 16, ch * 16
    g = Px(Wd, Hd)
    b = PAL['brick']
    coppi_roof(g, 0, 0, Wd, 22, PAL['roof'])
    g.rect(2, 20, Wd - 4, Hd - 20, b[1])
    for y in range(23, Hd, 4):
        g.hline(2, y, Wd - 4, b[2])
        o = 0 if (y // 4) % 2 else 4
        for x in range(2 + o, Wd - 2, 8):
            g.vline(x, y - 3, 3, b[2])
    g.hline(2, 20, Wd - 4, b[3])
    signboard(g, Wd // 2, 8, name, bg=C(255, 247, 222), fg=C(66, 99, 140))
    g.outline()
    return g.im


def vroom(gn, name_n, name_s, guard_script, wall='ochre'):
    """Stanza passante N-S: porta nel muro nord (verso il sottopasso), stuoia di uscita a sud (verso la casa)."""
    Wd, Hd = 8, 9
    r = I.Room(Wd, Hd, gn, floor='tiles', wall=wall, wall_rows=2)
    r.objs, r.bwarps, r.bcoords, r.bbgs = [], [], [], []
    set_floor(r, marble_floor)
    r.furn(0, 0, poster(name_n, '^')); r.furn(6, 0, poster(name_s, 'v'))
    r.furn(0, 3, big_plant()); r.furn(7, 3, big_plant())
    r.furn(4, 2, office_counter(3), top_rows=1)
    for x in range(4, 7):
        a = r.art[3][x]; r.art[3][x] = (a[0], a[1], 1, 0x80, a[4])
    r.add_obj(5, 2, 22, guard_script, move=8)
    return r


def install_end(cv, end, interior, idx):
    """Casello al bordo + collegamento alla stanza interna (group,num) porta idx.
    end: side N|S|E|W, lane, x0 (N/S) o y0 (E/W), cw/ch, door_col, name, clear=[(x0,y0,x1,y1)], plant=[(x,y)],
         moves={'obj':{i:(x,y)}, 'bg':{i:(x,y)|None}}, ring=(x0,y0,x1,y1) per il giro attorno (lato sud)."""
    side = end['side'];cw, ch = end.get('cw', 4), end.get('ch', 4)
    if side == 'N':
        x0, y0 = end['x0'], 0;dc = end.get('door_col', 1);door = (x0 + dc, ch - 1);appr = (door[0], ch)
    elif side == 'S' and TUNNEL[0]:
        pcols = sorted({p[0] for p in end['lane']})
        x0 = max(0, pcols[0] - 1);cw = pcols[-1] + 2 - x0 if pcols[-1] + 1 < cv.w else pcols[-1] + 1 - x0
        ch = 3;y0 = cv.h - ch;door = (pcols[0], cv.h - 1);appr = (pcols[0], y0 - 1)
    elif side == 'S':
        x0 = end['x0'];y0 = end.get('y0', cv.h - 2 - ch);dc = end.get('door_col', 1);door = (x0 + dc, y0 + ch - 1);appr = (door[0], y0 + ch)
    elif side == 'E':      # casa al bordo est della mappa, porta sulla faccia ovest
        x0, y0 = cv.w - cw, end['y0'];door = (x0, y0 + ch - 1);appr = (door[0] - 1, door[1])
    else:                  # 'W': casa al bordo ovest, porta sulla faccia est
        x0, y0 = 0, end['y0'];door = (x0 + cw - 1, y0 + ch - 1);appr = (door[0] + 1, door[1])
    foot = {(x, y) for x in range(x0, x0 + cw) for y in range(y0, y0 + ch)}
    clear = set()
    for r in end.get('clear', ()): clear |= rect_cells(r)
    ring = rect_cells(end['ring']) if end.get('ring') and not (side == 'S' and TUNNEL[0]) else set()
    touch = foot | clear | ring | {appr}
    lane = set(map(tuple, end['lane']))
    # eventi: sposta/rimuovi quello che l'utente ha indicato, segnala il resto
    mv = end.get('moves', {})
    def near(cx, cy):
        # cella pulita (erba) libera piu' vicina, fuori da casa/anello/corsia e senza eventi
        taken = {(o['x'], o['y']) for o in cv.objs} | {(b['x'], b['y']) for b in cv.bbgs} | {(w['x'], w['y']) for w in cv.bwarps} | {(c['x'], c['y']) for c in cv.bcoords}
        best = None
        for r_ in range(1, 12):
            for yy in range(cy - r_, cy + r_ + 1):
                for xx in range(cx - r_, cx + r_ + 1):
                    p = (xx, yy)
                    if 2 <= xx < cv.w - 2 and 2 <= yy < cv.h - 2 and p not in touch and p not in lane and p not in taken \
                       and isgrass(cv, xx, yy) \
                       and all(isgrass(cv, xx + a, yy + b) for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                        best = best or p
            if best: return best
        raise AssertionError(('nessuna cella libera', cv.gn, cx, cy))
    for i, pos in list(mv.get('obj', {}).items()):
        if pos == 'near': pos = mv['obj'][i] = near(cv.objs[i]['x'], cv.objs[i]['y'])
    sign_new = []
    for i, pos in list(mv.get('bg', {}).items()):
        if pos == 'near':
            pos = mv['bg'][i] = near(cv.bbgs[i]['x'], cv.bbgs[i]['y']);sign_new.append(pos)
    for i, pos in mv.get('obj', {}).items():
        if pos is None: cv.objs[i]['x'] = cv.objs[i]['y'] = -1
        else: cv.objs[i]['x'], cv.objs[i]['y'] = pos
    for i, pos in mv.get('bg', {}).items():
        ox, oy = cv.bbgs[i]['x'], cv.bbgs[i]['y']
        if 0 <= ox < cv.w and 0 <= oy < cv.h and cv.over[oy][ox] and cv.over[oy][ox][0] == 3 and cv.art[oy][ox] is None:
            to_grass(cv, ox, oy)
        if pos is None: cv.bbgs[i]['x'] = cv.bbgs[i]['y'] = -1
        else: cv.bbgs[i]['x'], cv.bbgs[i]['y'] = pos
    o_, b_ = touched_events(cv, touch - set(end.get('keep_events', ())))
    assert not o_ and not b_, ('eventi nell\'area del casello', cv.gn, side, o_, b_)
    if side == 'S' and TUNNEL[0]:
        cv.bcoords = [c for c in cv.bcoords if not (c['script'] == 0x2c926f and (c['x'], c['y']) in touch)]
    stray = [c for c in cv.bcoords if (c['x'], c['y']) in touch and (c['x'], c['y']) not in lane and (c['x'], c['y']) != appr]
    assert not stray, ('coord nell\'area del casello', cv.gn, side, [(c['x'], c['y']) for c in stray])
    stray = [w for w in cv.bwarps if (w['x'], w['y']) in touch and (w['x'], w['y']) not in lane]
    assert not stray, ('warp nell\'area del casello', cv.gn, side, [(w['x'], w['y']) for w in stray])
    cv.bcoords = [c for c in cv.bcoords if (c['x'], c['y']) not in lane]
    slots = [i for i, w in enumerate(cv.bwarps) if (w['x'], w['y']) in lane]
    for (x, y) in touch - {appr}:
        to_grass(cv, x, y)
    for (x, y) in end.get('plant', ()):
        cv.tree(x, y)
    for (x, y) in list(end.get('sign_art', ())) + sign_new:
        cv.put(x, y, 3, 1, 3)
    tun = side == 'S' and TUNNEL[0]
    if tun:
        im = tunnel_img(cw, ch, end['name'])
        for cy in range(ch):
            for cx in range(cw):
                X, Y = x0 + cx, y0 + cy
                piece = im.crop((cx * 16, cy * 16, cx * 16 + 16, cy * 16 + 16))
                if X in pcols:
                    fl = paving(X, Y)
                    if cy >= 1:
                        sh = Image.new('RGBA', (16, 16), (40, 30, 50, 70)); fl = fl.copy(); fl.alpha_composite(sh)
                    cv.art[Y][X] = (fl, piece if cy == 0 else None, 0, 0x65 if cy == ch - 1 else 0, True)
                else:
                    cv.art[Y][X] = (piece, None, 1, 0, True)
    elif side in ('N', 'S'):
        cv.place_art(x0, y0, casello_front(cw, ch, end['name'], dc))
    else:
        cv.place_art(x0, y0, varco('west' if side == 'E' else 'east', end['name'], ch))
        a = cv.art[door[1]][door[0]]
        cv.art[door[1]][door[0]] = (a[0], a[1], 0, 0x62 if side == 'E' else 0x63, a[4])
    # chiude con alberi le celle del varco originale rimaste fuori dalla casa (niente buchi che portano al nulla)
    if end.get('seal', True) and not tun:
        for (x, y) in sorted(lane - foot):
            tx, ty = x & ~1, y & ~1
            if ty + 1 < cv.h and tx + 1 < cv.w and not ({(tx, ty), (tx + 1, ty), (tx, ty + 1), (tx + 1, ty + 1)} & (foot | ring | clear | {appr})):
                cv.tree(tx, ty)
    if tun:
        cells = [(x, cv.h - 1) for x in pcols]
        for k, (x, y) in enumerate(cells):
            if k < len(slots): cv.bwarps[slots[k]].update(x=x, y=y, group=interior[0], num=interior[1], warp=idx, elev=0)
            else:
                cv.bwarps.append(dict(x=x, y=y, elev=0, warp=idx, group=interior[0], num=interior[1])); slots.append(len(cv.bwarps) - 1)
        for i in slots[len(cells):]: cv.bwarps[i].update(x=cells[-1][0], y=cells[-1][1], group=interior[0], num=interior[1], warp=idx, elev=0)
        slot = slots[0]
    elif slots:
        for i in slots:
            cv.bwarps[i].update(x=door[0], y=door[1], group=interior[0], num=interior[1], warp=idx, elev=0)
        slot = slots[0]
    else:
        cv.bwarps.append(dict(x=door[0], y=door[1], elev=0, warp=idx, group=interior[0], num=interior[1]))
        slot = len(cv.bwarps) - 1
    # l'approccio alla porta deve essere raggiungibile a piedi da un'area ampia (alberi tagliabili e NPC non contano come ostacolo)
    keep = {tuple(p) for p in end.get('keep_events', ())}
    blk = blocked_cells(cv) - keep
    seen = {appr}; todo = [appr]
    while todo:
        x, y = todo.pop()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            p = (x + dx, y + dy)
            if 0 <= p[0] < cv.w and 0 <= p[1] < cv.h and p not in seen and p not in blk:
                seen.add(p); todo.append(p)
    assert len(seen) >= end.get('reach_min', 60), ('approccio chiuso', cv.gn, side, appr, len(seen))
    return dict(x0=x0, y0=y0, cw=cw, ch=ch, door=door, appr=appr, slot=slot, side=side, reach=len(seen))
