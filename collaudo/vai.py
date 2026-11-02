"""Navigatore per le prove in emulatore (Lotto 2): porta il giocatore accanto a una casella, solo con i tasti.

Il percorso viene da analisi/percorso.py (quote, acqua, sporgenze, rocce, uscite, connessioni), calcolato dalla
posizione letta in RAM (lettura, non scrittura). A ogni passo si controlla dove si e' davvero arrivati; se una
lotta selvatica interrompe, la si combatte con pl.G.battle; se qualcosa blocca, si ricalcola il percorso.
SURF: davanti all'acqua A e "si". Rocce (gfx 86): A e "si" (SPACCAROCCIA).
"""
import os, sys, struct
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(HERE, '..', 'analisi')]
import pl
from pl import G, log, A, B
import percorso as PC

DIRCH = {'N': 'U', 'S': 'D', 'W': 'L', 'E': 'R'}
DXY = {'N': (0, -1), 'S': (0, 1), 'W': (-1, 0), 'E': (1, 0)}


def stato(g):
    sb1 = g.e.r('r32', 0x3005d8c); b = g.e.ram(sb1, 6)
    x, y = struct.unpack('<hh', b[:4])
    pa = g.e.ram(0x02037590, 8); ob = g.e.ram(0x02037350 + 0x24 * pa[5], 0x24)
    return (b[4], b[5]), x, y, ob[0xb] & 15, bool(pa[0] & 8)


CAMPO = {0x8085d9d, 0x8085d91}              # CB2 del campo (con o senza script/messaggio)


def ow(g): return g.cb2() in CAMPO


FUGA = True          # nelle lotte selvatiche lungo la strada si prova prima a fuggire


def lotta(g):
    from drv import D, R
    if FUGA:
        for t in range(10):
            for _ in range(80):                                   # fino al menu della lotta
                if ow(g) or g.e.r('r32', 0x3005d60) == pl.ACT: break
                g.key(B, 2, 20)
            if ow(g): break
            g.key(D, 3, 10); g.key(R, 3, 10); g.key(A, 3, 60)
            for _ in range(30):
                if ow(g) or g.e.r('r32', 0x3005d60) == pl.ACT: break
                g.key(B, 2, 20)
            if ow(g): break
        g.e.run(30)
        if ow(g): log('  lotta selvatica: fuga', 'squadra', g.party(), 'pos', stato(g)[:3]); return
    info = g.battle(); log('  lotta', info[:1], 'squadra', g.party(), 'pos', stato(g)[:3])


def rompi(g, dn):
    """Davanti a una roccia o a un albero: A, si (SPACCAROCCIA o TAGLIO; albero dalla 0.61)."""
    g.step(DIRCH[dn], 3)
    for _ in range(4): g.key(A, 3, 45)
    g.e.run(120)
    if not ow(g): lotta(g)


def vai(g, mappa, x, y, ab, accanto=True, max_ricalcoli=30, quota_fissa=None):
    R = pl.RM
    for giro in range(max_ricalcoli):
        k, px, py, z, surf = stato(g)
        if k == mappa and abs(px - x) + abs(py - y) <= (1 if accanto else 0): return True
        massi = [xy for xy, gf in g.lobjs_gfx() if gf == 87]
        prec = PC.cerca(R, (k, (px, py)), ab, z=z, surf=surf, massi_vivi=massi)
        st = PC.raggiunge(prec, mappa, x, y) if accanto else next((s for s in prec if s[:3] == (mappa, x, y)), None)
        if st is None: log('  nessun percorso da', (k, px, py, z, surf), 'a', mappa, (x, y)); return False
        passi = PC.strada(prec, st)[1:]
        ok = True
        for (nst, dn, az) in passi:
            k0, x0, y0, _, _ = stato(g)
            vivi = dict(g.lobjs_gfx()) if az == 'passo' else {}
            dx, dy = DXY.get(dn, (0, 0))
            if vivi.get((x0 + dx, y0 + dy)) in (86, 82) and k0 == nst[0]:      # roccia o albero: A, si
                rompi(g, dn)
            if vivi.get((x0 + dx, y0 + dy)) == 87 and k0 == nst[0]:       # masso: FORZA (A, si), poi spinta
                g.step(DIRCH[dn], 3)
                for _ in range(4): g.key(A, 3, 45)
                g.e.run(60)
            if az == 'surf':
                g.step(DIRCH[dn], 3)
                for _ in range(3): g.key(A, 3, 50)
                g.e.run(150)
            elif az in ('immersione', 'risalita'):        # SUB: A sull'acqua profonda, B sott'acqua per risalire; poi "si"
                if az == 'risalita': g.key(B, 3, 60)
                for _ in range(3): g.key(A, 3, 50)
                g.e.run(240); ok = False; break
            elif az == 'uscita':
                g.step(DIRCH[dn]); g.e.run(150)
            else:
                g.step(DIRCH[dn])
                if az == 'salto': g.e.run(20)
            if not ow(g):
                g.e.run(30)
                if not ow(g): lotta(g); ok = False; break
            k1, x1, y1, _, s1 = stato(g)
            if (k1, x1, y1) != nst[:3]:
                if az == 'uscita' and k1 != k0: g.e.run(60); ok = False; break
                g.e.run(30); k1, x1, y1, _, s1 = stato(g)
                if (k1, x1, y1) != nst[:3]:
                    log('  fuori percorso: atteso', nst[:3], 'sono', (k1, x1, y1), 'azione', az, dn)
                    for _ in range(2): g.key(B, 2, 20)
                    g.e.run(40); ok = False; break
        if ok:
            k, px, py, _, _ = stato(g)
            if k == mappa and abs(px - x) + abs(py - y) <= (1 if accanto else 0): return True
    return False


def guarda(g, x, y):
    """Si gira verso la casella (x, y) accanto."""
    _, px, py, _, _ = stato(g)
    dn = {(1, 0): 'R', (-1, 0): 'L', (0, 1): 'D', (0, -1): 'U'}[(x - px, y - py)]
    ob = 0x02037350 + 0x24 * g.e.ram(0x02037590, 8)[5]                  # oggetto del giocatore
    if g.e.ram(ob + 0x18, 1)[0] & 0x0f == {'D': 1, 'U': 2, 'L': 3, 'R': 4}[dn]: return   # gia' girato: niente passo
    g.step(dn, 3); g.e.run(10)


def nuovo(state, rom):
    os.environ['ROMF'] = rom
    g = G(state); g.OW = g.cb2(); return g
