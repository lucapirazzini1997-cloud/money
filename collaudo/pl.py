"""Libreria per la partita vera in emulatore (niente scrittura di RAM: solo tasti)."""
import sys, os, collections, struct
EMU = os.environ.get('EMU_DIR', os.path.dirname(os.path.abspath(__file__)))   # cartella con drv.py e l'eseguibile ./h
sys.path.insert(0, EMU); sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'strumenti_rom'))
os.chdir(EMU)
from drv import *
import romlib
P = os.environ.get('PLAY_DIR', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'play')) + '/'
ROM = P + os.environ.get('ROMF', '../../out/Pokemon_Romagna_0_56.gba')
RM = romlib.Rom(ROM)
LOG = open(P + 'log.txt', 'a')
def log(*a):
    s = ' '.join(str(x) for x in a); print(s); LOG.write(s + '\n'); LOG.flush()

class G:
    def __init__(self, state=None):
        self.e = Emu(ROM, P + 'p51.sav'); self.e.run(10)
        if state: self.e.load(P + state); self.e.run(120)
    def pos(self):
        sb1 = self.e.r('r32', 0x3005d8c); b = self.e.ram(sb1, 6)
        x, y = struct.unpack('<hh', b[:4]); return (x, y, b[4], b[5])
    def cb2(self): return self.e.r('r32', 0x30022c4)
    def party(self):
        n = self.e.ram(0x20244e9, 1)[0]; out = []
        for i in range(min(n, 6)):
            b = self.e.ram(0x20244ec + i * 100, 100)
            out.append((b[84], struct.unpack_from('<H', b, 86)[0], struct.unpack_from('<H', b, 88)[0]))
        return out
    def flag(self, n): return flag(self.e, n)
    def var(self, n):
        sb1 = self.e.r('r32', 0x3005d8c); return struct.unpack('<H', self.e.ram(sb1 + 0x139c + (n - 0x4000) * 2, 2))[0]
    def save(self, name): self.e.state(P + name); self.e.sync()
    def shot(self, name): self.e.shot(P + name, 1)
    def key(self, k, n=4, w=8): self.e.key(k, n, w)
    def step(self, ch, hold=16):
        if hold <= 6: self.e.run(24); self.e.key(KEY[ch], 6, 24)   # girarsi sul posto
        else: self.e.key(KEY[ch], hold, 3)
    def mash(self, k=A, n=10, w=20):
        for _ in range(n): self.e.key(k, 3, w)
    def close(self): self.e.close()
    def lobjs(self):
        b = self.e.ram(0x2037350, 0x24 * 16); out = []
        for i in range(1, 16):
            o = b[i * 0x24:(i + 1) * 0x24]
            if o[0] & 1:
                x, y = struct.unpack_from('<hh', o, 0x10); out.append((x - 7, y - 7))
                x, y = struct.unpack_from('<hh', o, 0x14); out.append((x - 7, y - 7))   # cella precedente/destinazione
        return out
    def lobjs_gfx(self):
        b = self.e.ram(0x2037350, 0x24 * 16); out = []
        for i in range(1, 16):
            o = b[i * 0x24:(i + 1) * 0x24]
            if o[0] & 1:
                x, y = struct.unpack_from('<hh', o, 0x10); out.append(((x - 7, y - 7), o[5]))
        return out
    def clear_obstacle(self, src, cands):
        obst = {c: gf for c, gf in self.lobjs_gfx() if gf in (82, 86)}
        if not obst: return False
        others = [c for c in self.lobjs() if c not in obst]
        p = self.pos()
        for c in cands:
            r = route(src[0], src[1], p[:2], c, live=self.live(), objs=others)
            if r is None: continue
            x, y = p[:2]; prev = (x, y)
            for ch in r:
                dx, dy = dict(U=(0, -1), D=(0, 1), L=(-1, 0), R=(1, 0)).get(ch, (0, 0))
                nx = (x + dx, y + dy)
                if nx in obst:
                    self.walkto(x, y); self.step(ch, 3)
                    for _ in range(6): self.key(A, 3, 45)
                    self.e.run(90)
                    if self.cb2() != OW: self.battle()
                    log('  ostacolo rimosso', nx, obst[nx]); return True
                x, y = nx
        return False
    def live(self):
        import numpy as np
        w, h, p = struct.unpack('<iiI', self.e.ram(0x3005dc0, 12))
        a = np.frombuffer(self.e.ram(p, w * h * 2), dtype='<u2').reshape(h, w)
        q = self.pos(); m = RM.map(q[2], q[3])
        return a[7:7 + m['height'], 7:7 + m['width']].copy()

def objs(g, n):
    m = RM.map(g, n); return m

_BEH = {}
def beh(g, n):
    if (g, n) not in _BEH:
        m = RM.map(g, n); bl = RM.blocks(m); H, W = bl.shape
        bh = [[0] * W for _ in range(H)]
        cache = {}
        for y in range(H):
            for x in range(W):
                mt = int(bl[y, x]) & 1023
                if mt not in cache:
                    try: cache[mt] = RM.attr(m, mt) & 0xff
                    except Exception: cache[mt] = 0
                bh[y][x] = cache[mt]
        _BEH[(g, n)] = bh
    return _BEH[(g, n)]
WATER = {0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x19, 0x1a, 0x1b, 0x1c}
LEDGE = {0x38: 'R', 0x39: 'L', 0x3a: 'U', 0x3b: 'D'}
def route(g, n, a, b, extra_block=(), allow=(), surf=False, live=None, objs=None):
    m = RM.map(g, n); bl = RM.blocks(m) if live is None else live; bh = beh(g, n)
    ob = ({(o['x'], o['y']) for o in m['objects']} if objs is None else set(objs)) | set(extra_block)
    ob -= set(allow)
    q = collections.deque([a]); prev = {a: None}
    while q:
        c = q.popleft()
        if c == b: break
        for d, (dx, dy) in dict(U=(0, -1), D=(0, 1), L=(-1, 0), R=(1, 0)).items():
            nx = (c[0] + dx, c[1] + dy)
            if not (0 <= nx[0] < m['width'] and 0 <= nx[1] < m['height']) or nx in prev: continue
            t = bh[nx[1]][nx[0]]
            if nx != b:
                if (bl[nx[1], nx[0]] >> 10) & 3: continue
                if nx in ob: continue
                if t in WATER and not surf: continue
            if t in LEDGE:
                if LEDGE[t] != d: continue
                j = (nx[0] + dx, nx[1] + dy)      # il salto atterra oltre
                if j in prev or not (0 <= j[0] < m['width'] and 0 <= j[1] < m['height']): continue
                prev[nx] = (c, d); prev[j] = (nx, ''); q.append(j); continue
            prev[nx] = (c, d); q.append(nx)
    if b not in prev: return None
    out = ''; c = b
    while prev[c]: c, d = prev[c]; out = d + out
    return out

# ---------------------------------------------------------------- battaglie e viaggio
OW = 0x8085d9d; ACT = 0x8057445; MOVE = 0x8057ab9
D_ = open(ROM, 'rb').read()
CHART = {}
q = 0x32d5b4
while D_[q] != 0xff:
    if D_[q] != 0xfe: CHART[(D_[q], D_[q + 1])] = D_[q + 2] / 10
    q += 3
def mv(i): p = 0x32f164 + i * 12; return D_[p + 1], D_[p + 2]   # power, type
def eff(t, d1, d2):
    m = CHART.get((t, d1), 1)
    if d2 != d1: m *= CHART.get((t, d2), 1)
    return m
def bm(e, i):
    b = e.ram(0x2024084 + i * 0x58, 0x58)
    return dict(sp=struct.unpack_from('<H', b, 0)[0], moves=[struct.unpack_from('<H', b, 12 + 2 * k)[0] for k in range(4)],
                pp=list(b[0x24:0x28]), t1=b[0x21], t2=b[0x22], hp=struct.unpack_from('<H', b, 0x28)[0], lv=b[0x2a])
def best_move(e):
    me, fo = bm(e, 0), bm(e, 1); best = (-1, 0)
    for k, (m, pp) in enumerate(zip(me['moves'], me['pp'])):
        if not m or not pp: continue
        pw, ty = mv(m)
        sc = pw * (1.5 if ty in (me['t1'], me['t2']) else 1) * eff(ty, fo['t1'], fo['t2'])
        if pw == 0: sc = 0.1
        if sc > best[0]: best = (sc, k)
    return best[1], me, fo
G.stats = collections.Counter()
import scr as _scr
MOVENAME = {_scr.text(D_, 0x32c048 + i * 13, 13): i for i in range(1, 355)}
SPNAME = {i: _scr.text(D_, 0x32ae94 + i * 11, 11) for i in range(1, 412)}
BATCB = 0x80383e9
def msg(e): return _scr.text(e.ram(0x2022e2c, 160), 0, 160).replace(' / ', ' ')
def battle(self, maxi=900):
    e = self.e; stuck = 0; info = []; m0 = self.pos()[2:]; learner = None
    for i in range(maxi):
        f = e.r('r32', 0x3005d60); cb = self.cb2()
        if cb == OW:
            e.run(20)
            if self.cb2() == OW: break
            continue
        if cb != BATCB:            # evoluzione / menu squadra: mai B (annullerebbe l'evoluzione)
            stuck += 1
            e.key([D, A, A][stuck % 3], 2, 30); continue
        t = msg(e)
        if 'is trying to' in t: learner = t.split(' is trying')[0].strip()
        if 'Delete a move' in t and '?' in t:
            new = t.split('room for ')[-1].rstrip('?').strip()
            nid = MOVENAME.get(new, 0); best = None
            for k in range(len(self.party())):
                mv4, sp = self.mon_moves(k)
                if SPNAME.get(sp, '') == learner and all(mv4):
                    pw = [mv(x)[0] if x not in HMS else 999 for x in mv4]
                    j = min(range(4), key=lambda q: pw[q])
                    if mv(nid)[0] > pw[j]: best = j
            if best is None:
                log('  non impara', new); e.key(B, 2, 40); e.key(A, 2, 40)
            else:
                log('  impara', new, 'al posto dello slot', best); e.key(A, 2, 150); e.run(60)
                for _ in range(best): e.key(D, 3, 30)
                e.key(A, 2, 90); e.key(A, 2, 40)
            continue
        if 'Stop learning' in t: e.key(A, 2, 40); continue
        if f == ACT:
            e.key(U, 2, 4); e.key(L, 2, 4); e.key(A, 2, 20)
            if e.r('r32', 0x3005d60) == MOVE:
                k, me, fo = best_move(e)
                info.append((me['sp'], me['lv'], fo['sp'], fo['lv']))
                e.key(U, 3, 10); e.key(L, 3, 10)
                if k & 1: e.key(R, 3, 10)
                if k & 2: e.key(D, 3, 10)
                e.key(A, 2, 30)
            stuck = 0
        else:
            stuck += 1
            e.key(A if stuck % 6 == 5 else B, 2, 18)
    for _ in range(4):
        if self.cb2() in (OW, BATCB): e.key(B, 2, 20)
        else: e.key(A, 2, 30)
    e.run(60)
    for _ in range(30):                      # evoluzione dopo la lotta
        if self.cb2() == OW: break
        e.key(A, 2, 40)
    if self.pos()[2:] != m0: log('  !! SCONFITTA o trasferimento dopo la lotta:', m0, '->', self.pos()); self.lost = True
    return info
G.battle = battle
def walkto(self, x, y, allow=(), tries=25, final=None):
    for t in range(tries):
        p = self.pos()
        if p[:2] == (x, y): break
        r = route(p[2], p[3], p[:2], (x, y), allow=allow, live=self.live(), objs=self.lobjs())
        if r is None: log('nessun percorso', p, (x, y)); return False
        for ch in r:
            before = self.pos()
            self.step(ch)
            if self.cb2() != OW:
                info = self.battle(); log('  lotta', info[:1], 'squadra', self.party(), 'pos', self.pos())
                self.shot('lotta%d' % G.stats['n']); G.stats['n'] += 1
                break
            after = self.pos()
            if after[2:] != before[2:]: self.e.run(90); return True     # cambio mappa
            if after[:2] == before[:2]:
                for _ in range(3): self.key(B, 2, 20)
                if self.cb2() != OW:
                    info = self.battle(); log('  lotta(all.)', info[:1], 'squadra', self.party(), 'pos', self.pos())
                break
    if final: self.step(final); self.e.run(120)
    return self.pos()[:2] == (x, y)
G.walkto = walkto

def grass_cells(g, n):
    m = RM.map(g, n); bl = RM.blocks(m); out = []
    for y in range(m['height']):
        for x in range(m['width']):
            v = int(bl[y, x])
            if (v >> 10) & 3: continue
            try: b = RM.attr(m, v & 1023) & 0xff
            except Exception: continue
            if b in (0x02, 0x03, 0x24): out.append((x, y))   # erba alta / erba lunga
    return out
def grind(self, battles=6, minhp=0.35, until_lv=None):
    p = self.pos(); cells = set(grass_cells(p[2], p[3]))
    pair = None
    for c in sorted(cells, key=lambda c: abs(c[0] - p[0]) + abs(c[1] - p[1])):
        for dx, dy, a, b in ((1, 0, 'R', 'L'), (0, 1, 'D', 'U')):
            if (c[0] + dx, c[1] + dy) in cells: pair = (c, a, b); break
        if pair: break
    if not pair: log('niente erba qui'); return
    self.walkto(*pair[0])
    n = 0
    for i in range(400):
        pt = self.party()
        if pt and pt[0][1] < pt[0][2] * minhp: break
        if until_lv and pt[0][0] >= until_lv: break
        if n >= battles: break
        self.save('gpre.ss')
        self.step(pair[1] if i % 2 == 0 else pair[2])
        if self.cb2() != OW:
            info = self.battle(); n += 1
            if getattr(self, 'lost', False): import shutil; shutil.copy(P + 'gpre.ss', P + 'lostpre.ss')
            log('  selvatico', info[:1], self.party())
            if getattr(self, 'lost', False): return
            self.walkto(*pair[0])
    log('grind fine', n, self.party())
G.grind = grind

def hunt(self, species, maxb=40):
    p = self.pos(); cells = set(grass_cells(p[2], p[3])); pair = None
    for c in sorted(cells, key=lambda c: abs(c[0] - p[0]) + abs(c[1] - p[1])):
        for dx, dy, a, b in ((1, 0, 'R', 'L'), (0, 1, 'D', 'U')):
            if (c[0] + dx, c[1] + dy) in cells: pair = (c, a, b); break
        if pair: break
    self.walkto(*pair[0]); n = 0
    for i in range(1000):
        self.step(pair[1] if i % 2 == 0 else pair[2])
        if self.cb2() != OW:
            for k in range(60):
                if self.e.r('r32', 0x3005d60) == ACT: break
                self.key(B, 2, 20)
            fo = bm(self.e, 1); log('  incontro', fo['sp'], fo['lv'])
            if fo['sp'] in species: return fo
            self.battle(); n += 1
            if n >= maxb: return None
            self.walkto(*pair[0])
G.hunt = hunt

def throw(self):
    """Lancia la prima POKé BALL (tasca POKé BALLS = seconda tasca)."""
    e = self.e
    for k in range(60):
        if e.r('r32', 0x3005d60) == ACT: break
        e.key(B, 2, 20)
    e.key(U, 3, 8); e.key(R, 3, 10); e.key(A, 3, 60)
    for _ in range(6):
        if e.ram(0x203ce5d, 1)[0] == 1: break
        e.key(L, 3, 30)
    e.key(U, 3, 10); e.key(A, 3, 30); e.key(A, 3, 60)
    for _ in range(25):
        e.key(B, 2, 30)
        if self.cb2() == OW or e.r('r32', 0x3005d60) == ACT: break
    e.run(30)
    return self.cb2() == OW
G.throw = throw

ORDERS = ['GAEM','GAME','GEAM','GEMA','GMAE','GMEA','AGEM','AGME','AEGM','AEMG','AMGE','AMEG',
          'EGAM','EGMA','EAGM','EAMG','EMGA','EMAG','MGAE','MGEA','MAGE','MAEG','MEGA','MEAG']
def mon_moves(self, i):
    b = self.e.ram(0x20244ec + i * 100, 100)
    pid, otid = struct.unpack_from('<II', b, 0); key = pid ^ otid
    data = bytearray(b[32:80])
    for k in range(0, 48, 4):
        struct.pack_into('<I', data, k, struct.unpack_from('<I', data, k)[0] ^ key)
    o = ORDERS[pid % 24]; a = o.index('A')
    sub = data[a * 12:(a + 1) * 12]
    g_ = data[o.index('G') * 12:(o.index('G') + 1) * 12]
    return struct.unpack_from('<HHHH', sub, 0), struct.unpack_from('<H', g_, 0)[0]
G.mon_moves = mon_moves

def swap01(self):
    e = self.e
    for _ in range(3): e.key(B, 3, 30)
    e.key(START, 3, 50)
    for _ in range(8):
        if e.ram(0x203760e, 1)[0] == 1: break
        e.key(U, 3, 12)
    e.key(A, 3, 60); e.run(90)
    e.key(L, 3, 30)
    FIELD = {15, 19, 57, 70, 148, 249, 127, 291, 100, 91, 230, 135, 208, 290}
    nf = len([m for m in self.mon_moves(0)[0] if m in FIELD])
    e.key(A, 3, 50)
    for _ in range(1 + nf): e.key(D, 3, 25)
    e.key(A, 3, 50); e.key(R, 3, 35); e.key(A, 3, 120)
    for _ in range(4): e.key(B, 3, 40)
    log('swap ->', self.party())
G.swap01 = swap01

ARROW = {0x62: 'R', 0x63: 'L', 0x64: 'U', 0x65: 'D'}
_ME = {}
def map_edges(k):
    if k in _ME: return _ME[k]
    try: m = RM.map(*k)
    except Exception: _ME[k] = []; return []
    out = []
    for w in m['warps']:
        if w['group'] > 40: continue
        try: RM.map(w['group'], w['num'])
        except Exception: continue
        out.append(((w['group'], w['num']), (w['x'], w['y'])))
    _ME[k] = out
    return out
def map_path(a, b, avoid=()):
    q = collections.deque([a]); prev = {a: None}
    while q:
        c = q.popleft()
        if c == b: break
        for d, cell in map_edges(c):
            if d not in prev and d not in avoid:
                prev[d] = (c, cell); q.append(d)
    if b not in prev: return None
    out = []; c = b
    while prev[c]: p, cell = prev[c]; out.append((p, cell, c)); c = p
    return out[::-1]
def travel(self, dest, avoid=(), tries=3):
    for t in range(40):
        here = self.pos()[2:]
        if here == dest: return True
        path = map_path(here, dest, avoid)
        if not path: log('nessun cammino mappe', here, dest); return False
        src, cell, nxt = path[0]
        m = RM.map(*src)
        # tra i warp che portano a nxt scegli quello raggiungibile
        cands = [(w['x'], w['y']) for w in m['warps'] if (w['group'], w['num']) == nxt]
        live = self.live(); p = self.pos(); best = None
        for c in cands:
            r = route(src[0], src[1], p[:2], c, live=live, objs=self.lobjs())
            if r is not None and (best is None or len(r) < len(best[1])): best = (c, r)
        if not best and self.clear_obstacle(src, cands):
            continue
        if not best: log('warp irraggiungibile', src, '->', nxt, cands); return False
        c = best[0]; b = beh(*src)[c[1]][c[0]]
        fin = ARROW.get(b)
        if fin is None:
            if c[1] == m['height'] - 1: fin = 'D'
            elif c[1] == 0: fin = 'U'
            elif c[0] == 0: fin = 'L'
            elif c[0] == m['width'] - 1: fin = 'R'
            else: fin = 'U'
        self.walkto(c[0], c[1], final=fin)
        if self.pos()[2:] == src:
            self.step(fin); self.e.run(120)
        if self.pos()[2:] == src:                    # porta-script (bg): parla verso la porta
            q = self.pos()
            if abs(q[0] - c[0]) + abs(q[1] - c[1]) <= 1:
                for _ in range(6):
                    self.key(A, 3, 40)
                    if self.pos()[2:] != src: break
                self.e.run(120)
            else:
                ok = self.walkto(c[0], c[1] + 1)
                self.step('U', 3)
                for _ in range(6):
                    self.key(A, 3, 40)
                    if self.pos()[2:] != src: break
                self.e.run(120)
        log('  ->', self.pos())
    return self.pos()[2:] == dest
G.travel = travel
PCS = {}
for g_, c_ in [(0, 57), (1, 5), (2, 5), (16, 15), (34, 118), (35, 101)]:
    for n_ in range(c_):
        try: m_ = RM.map(g_, n_)
        except Exception: continue
        for o_ in m_['objects']:
            if o_['gfx'] == 58: PCS[(g_, n_)] = (o_['x'], o_['y'])
def heal(self):
    here = self.pos()[2:]
    best = None
    for k in PCS:
        pth = map_path(here, k) if k != here else []
        if pth is not None and (best is None or len(pth) < len(best[1])): best = (k, pth)
    if not best: log('nessun centro'); return False
    k = best[0]; outside = best[1][-1][0] if best[1] else None
    self.travel(k)
    x, y = PCS[k]; self.walkto(x, y + 2); self.step('U', 3); self.e.run(10)
    for _ in range(14): self.key(A, 3, 45)
    for _ in range(4): self.key(B, 3, 30)
    log('cura', k, self.party())
    if outside: self.travel(outside)
    return True
G.heal = heal

def open_pocket(self, pocket):
    e = self.e
    for _ in range(4): e.key(B, 3, 25)
    e.key(START, 3, 50)
    for _ in range(10):
        if e.ram(0x203760e, 1)[0] == 2: break
        e.key(D, 3, 15)
    e.key(A, 3, 90); e.run(60)
    for _ in range(6):
        if e.ram(0x203ce5d, 1)[0] == pocket: break
        e.key(R, 3, 30)
    for _ in range(12): e.key(U, 3, 12)
G.open_pocket = open_pocket
def teach_tm(self, index, slot_mon, forget_slot):
    """index: posizione nella tasca MT/MN; slot_mon: 0/1 nella squadra; forget_slot: mossa da dimenticare (0-3) o None."""
    e = self.e
    self.open_pocket(2)
    for _ in range(index): e.key(D, 3, 20)
    e.key(A, 3, 40); e.key(A, 3, 60)          # USE
    for _ in range(3): e.key(A, 3, 45)        # testi + YES
    e.run(60)
    for _ in range(slot_mon): e.key(R if slot_mon == 1 else D, 3, 25)
    e.key(A, 3, 60)
    if forget_slot is not None:
        for _ in range(3): e.key(A, 3, 45)
        e.run(120)
        for _ in range(forget_slot): e.key(D, 3, 30)
        e.key(A, 3, 90)
    for _ in range(6): e.key(A, 3, 40)
    for _ in range(4): e.key(B, 3, 30)
    log('MT insegnata', [self.mon_moves(i) for i in range(len(self.party()))])
G.teach_tm = teach_tm
HMS = {15, 19, 57, 70, 148, 249, 127, 291}
