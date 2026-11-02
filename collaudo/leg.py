"""Funzioni comuni per le prove dei leggendari (dalla 0.60; estratte da t59.py, che resta com'era).
Solo tasti, salvo le fixture dichiarate (fixture, fixture_surf, fixture_mossa, fixture_flag, fixture_posizione)."""
import os, sys, struct, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vai, pl
from pl import log, A, B
from drv import Emu, U, D, L, R, START
PLAY = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'play')
PARTE = next((a.split('=')[1] for a in sys.argv if a.startswith('--parte=')), '')

def g_da(state, sav=None):
    from drv import Emu
    if sav is None:
        sav = os.path.join(pl.P, 'leg_tmp.sav')
        with open(sav, 'wb') as f: f.write(open(os.path.join(pl.P, 'p51.sav'), 'rb').read())
    g = pl.G.__new__(pl.G); g.e = Emu(pl.ROM, sav); g.e.run(10); g.e.load(pl.P + state); g.e.run(120); g.OW = pl.OW
    g.sav = sav
    for _ in range(3): g.key(B, 2, 20)
    log('PROVA', PARTE, os.path.basename(pl.ROM), 'partenza', state, vai.stato(g), 'cb2', hex(g.cb2()))
    return g


import scr as _scr
def testo(g):
    if g.cb2() == pl.BATCB: return pl.msg(g.e)
    return _scr.text(g.e.ram(0x02021fc4, 200), 0, 200).replace(' / ', ' ')

def chiudi_testi(g, n=60, tag=None):
    """Fine lotta e testi dello script: solo B (avanza i testi, dice no al soprannome, non riparla col Pokemon)."""
    vis = []
    for i in range(n):
        t = testo(g)
        if t and (not vis or vis[-1] != t): vis.append(t)
        if vai.ow(g) and g.e.ram(0x03000e41, 1)[0] == 0:
            g.e.run(30)
            if vai.ow(g) and g.e.ram(0x03000e41, 1)[0] == 0: break
        g.key(B, 3, 40)
    return vis

def menu_lotta(g, maxi=80):
    for _ in range(maxi):
        if g.e.r('r32', 0x3005d60) == pl.ACT: return True
        if vai.ow(g) and g.e.ram(0x03000e41, 1)[0] == 0: return False
        g.key(B, 2, 20)
    return False

def fuggi(g):
    for t in range(12):
        if not menu_lotta(g): break
        g.key(D, 3, 10); g.key(R, 3, 10); g.key(A, 3, 60)
        for _ in range(30):
            if vai.ow(g) or g.e.r('r32', 0x3005d60) == pl.ACT: break
            g.key(B, 2, 20)
    g.e.run(30)

TRANSIZIONI = {0x8036f75, 0x8086035}         # entrata in lotta, ritorno al campo

def ko(g):
    """Combatte fino alla fine (mosse migliori, come pl.G.battle) ma senza mai premere A nel campo."""
    e = g.e; info = []
    for i in range(900):
        if vai.ow(g): break
        if g.cb2() in TRANSIZIONI: e.run(20); continue
        if g.cb2() == pl.BATCB and e.r('r32', 0x3005d60) == pl.ACT:
            e.key(U, 2, 4); e.key(L, 2, 4); e.key(A, 2, 20)
            if e.r('r32', 0x3005d60) == pl.MOVE:
                k, me, fo = pl.best_move(e); info.append((me['sp'], me['lv'], me['hp'], fo['sp'], fo['lv'], fo['hp']))
                e.key(U, 3, 10); e.key(L, 3, 10)
                if k & 1: e.key(R, 3, 10)
                if k & 2: e.key(D, 3, 10)
                e.key(A, 2, 30)
        elif g.cb2() != pl.BATCB:                  # menu squadra dopo un KO: manda il primo Pokemon in grado
            for k in range(6):
                if g.party()[k][1] > 0 if k < len(g.party()) else False: break
            e.run(30)
            for _ in range(k): e.key(D, 3, 20)
            e.key(A, 3, 40); e.key(A, 3, 60)
        elif 'prossimo' in testo(g).lower(): e.key(A, 2, 60)       # "Usare il prossimo POKeMON?" -> si
        else: e.key(B, 2, 18)
    return info

def parla(g, c):
    vai.guarda(g, *c['xy']); g.key(A, 3, 60)
    vis = []
    for i in range(40):
        t = testo(g)
        if t and (not vis or vis[-1] != t): vis.append(t)
        if not vai.ow(g): return vis, True
        if i > 3 and g.e.ram(0x03000e41, 1)[0] == 0: return vis, False
        g.key(A, 3, 40)
    return vis, not vai.ow(g)

def presente(g, c): return any(gf == c['gfx'] for _, gf in g.lobjs_gfx())


def fixture(g):
    """FIXTURE DICHIARATE (scritture in RAM, non prove): 5 MASTER BALL in testa alla tasca Poke Ball."""
    sb1 = g.e.r('r32', 0x3005d8c); sb2 = g.e.r('r32', 0x3005d90); key = struct.unpack('<H', g.e.ram(sb2 + 0xac, 2))[0]
    b = g.e.ram(sb1 + 0x650, 8)
    g.e.w('w16', sb1 + 0x654, struct.unpack_from('<H', b, 0)[0]); g.e.w('w16', sb1 + 0x656, struct.unpack_from('<H', b, 2)[0])
    g.e.w('w16', sb1 + 0x650, 1); g.e.w('w16', sb1 + 0x652, 5 ^ key)
    log('   FIXTURE: 5 MASTER BALL nella tasca Poke Ball')

def fixture_surf(g, slot=1, mossa=3):
    """FIXTURE DICHIARATA: il Pokemon in `slot` impara SURF (57) al posto della mossa `mossa` (scrittura in RAM,
    dati cifrati e checksum ricalcolati). Serve solo ad avere SURF: se si ottiene in gioco lo verifica il Lotto 3."""
    a = 0x20244ec + slot * 100; b = bytearray(g.e.ram(a, 100))
    pid, otid = struct.unpack_from('<II', b, 0); key = pid ^ otid
    data = bytearray(b[32:80])
    for k in range(0, 48, 4): struct.pack_into('<I', data, k, struct.unpack_from('<I', data, k)[0] ^ key)
    o = pl.ORDERS[pid % 24]; ia = o.index('A') * 12
    struct.pack_into('<H', data, ia + 2 * mossa, 57); data[ia + 8 + mossa] = 15
    struct.pack_into('<H', b, 28, sum(struct.unpack('<24H', bytes(data))) & 0xffff)
    for k in range(0, 48, 4): struct.pack_into('<I', data, k, struct.unpack_from('<I', data, k)[0] ^ key)
    b[32:80] = data
    for i in range(0, 100, 2): g.e.w('w16', a + i, struct.unpack_from('<H', b, i)[0])
    log('   FIXTURE: SURF al Pokemon', slot, '->', g.mon_moves(slot))

def salva(g):
    for _ in range(4): g.key(B, 3, 25)
    sb = os.path.getsize(g.sav)
    g.key(START, 3, 50)
    for _ in range(10):
        if g.e.ram(0x203760e, 1)[0] == 4: break
        g.key(D, 3, 15)
    for k in 'A..A......A......':
        if k == 'A': g.key(A, 3, 40)
        else: g.e.run(60)
        if 'Sovrascrivere' in testo(g) or 'sovrascriv' in testo(g).lower(): pass
    log('   salvataggio: testo finale', testo(g)); g.e.sync()

def ricarica(sav, rom=None):
    g = pl.G.__new__(pl.G); g.sav = sav; g.e = Emu(rom or pl.ROM, sav); g.e.run(10); g.OW = pl.OW
    for i, k in enumerate('......T...A...A......A......'):
        if k == 'A': g.key(A, 3, 40)
        elif k == 'T': g.key(START, 3, 40)
        else: g.e.run(60)
        if i in (6, 10, 14, 21): g.shot('t59_titolo_%d' % i)
    for _ in range(20):
        if vai.ow(g) and vai.stato(g)[0] != (0, 0): break
        g.key(A, 3, 40)
    return g

def specie_squadra(g):
    return [g.mon_moves(i)[1] for i in range(len(g.party()))]


def fixture_mossa(g, slot, mossa, nuova, pp):
    """FIXTURE DICHIARATA: il Pokemon `slot` impara la mossa `nuova` al posto della mossa `mossa` (dati cifrati e
    checksum ricalcolati). Serve solo a usare la MN sul campo; ottenerla in gioco e' verificato a parte."""
    a = 0x20244ec + slot * 100; b = bytearray(g.e.ram(a, 100))
    pid, otid = struct.unpack_from('<II', b, 0); key = pid ^ otid
    data = bytearray(b[32:80])
    for k in range(0, 48, 4): struct.pack_into('<I', data, k, struct.unpack_from('<I', data, k)[0] ^ key)
    ia = pl.ORDERS[pid % 24].index('A') * 12
    struct.pack_into('<H', data, ia + 2 * mossa, nuova); data[ia + 8 + mossa] = pp
    struct.pack_into('<H', b, 28, sum(struct.unpack('<24H', bytes(data))) & 0xffff)
    for k in range(0, 48, 4): struct.pack_into('<I', data, k, struct.unpack_from('<I', data, k)[0] ^ key)
    b[32:80] = data
    for i in range(0, 100, 2): g.e.w('w16', a + i, struct.unpack_from('<H', b, i)[0])
    log('   FIXTURE: mossa', nuova, 'al Pokemon', slot, '->', g.mon_moves(slot))

def fixture_flag(g, f, v=1):
    """FIXTURE DICHIARATA: flag di partenza (per esempio medaglie)."""
    pl.setflag(g.e, f, v); log('   FIXTURE: flag', hex(f), '=', v)

def fixture_posizione(g, mappa, x, y):
    """FIXTURE DICHIARATA: posizione di partenza scritta in SaveBlock1 (si usa prima di un salvataggio in gioco:
    Continua carica la mappa da li')."""
    sb1 = g.e.r('r32', 0x3005d8c)
    g.e.w('w16', sb1, x); g.e.w('w16', sb1 + 2, y)
    g.e.w('w8', sb1 + 4, mappa[0]); g.e.w('w8', sb1 + 5, mappa[1]); g.e.w('w8', sb1 + 6, 0xff)
    g.e.w('w16', sb1 + 8, x); g.e.w('w16', sb1 + 10, y)
    pa = g.e.ram(0x02037590, 8); ob = 0x02037350 + 0x24 * pa[5]       # oggetto del giocatore (salvato con la partita)
    g.e.w('w8', ob + 9, mappa[1]); g.e.w('w8', ob + 10, mappa[0])
    for off in (0x0c, 0x10, 0x14): g.e.w('w16', ob + off, x + 7); g.e.w('w16', ob + off + 2, y + 7)
    log('   FIXTURE: posizione', mappa, (x, y))

def leggi(g, mappa, x, y, ab, n=12):
    """Va accanto alla casella (x, y) (cartello, runa, Pokemon), si gira e preme A; restituisce i testi visti."""
    ok = vai.vai(g, mappa, x, y, ab)
    if not ok: log('   non arrivo accanto a', mappa, (x, y)); return None
    vai.guarda(g, x, y); g.key(A, 3, 60)
    return chiudi_testi(g, n)
