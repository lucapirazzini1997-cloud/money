#!/usr/bin/env python3
"""Percorso a piedi realistico (Lotto 2): come cammina il giocatore, con le abilita' che ha in quel momento.

Diverso da cammino.py (ottimistico): qui contano
  - quota delle caselle (elevazione): si passa solo fra quote uguali, o da/verso quota 0 e 15 (come Smeraldo);
  - acqua: serve SURF (si entra in acqua da quota 3, si scende a terra su quota 3); CASCATA per risalire;
  - sporgenze: si saltano solo nel loro verso (si atterra due caselle oltre);
  - pendii fangosi (Bici Corsa), pendii a gobbe e binari (Bici Cross): solo con la bici giusta;
  - oggetti fermi (persone, rocce, alberi, massi): bloccano, salvo rocce con SPACCAROCCIA, alberi con TAGLIO,
    massi con FORZA; chi passeggia non blocca (ottimistico); gli oggetti nascosti da una flag data come "alzata"
    non ci sono;
  - uscite (porte, scale, frecce) e connessioni ai bordi; niente Volo e niente warp degli script.
Resta un'approssimazione: ignora i blocchi degli script a coordinate (sono elencati a parte) e le correnti.
Il risultato va confermato in gioco; serve a scegliere i percorsi da provare e a trovare i tratti che chiedono
strumenti che il giocatore non ha.

Uso: python3 analisi/percorso.py ROM g.n:x,y [--abilita surf,spacca,taglio,forza,cascata,corsa,cross,flash]
                                 [--flag f1,f2] [--meta g.n:x,y ...]
Stampa, per ogni meta, se si raggiunge una casella accanto e il percorso (mappe attraversate).
"""
import sys, struct, collections, argparse
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / 'strumenti_rom')]
import romlib

SURFABILE = {0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x19, 0x1a, 0x22, 0x2a, 0x50, 0x51, 0x52, 0x53}
CASCATA = 0x13
SALTI = {0x38: (1, 0), 0x39: (-1, 0), 0x3a: (0, -1), 0x3b: (0, 1)}
FANGO, GOBBE = 0xd0, 0xd1
BINARI = {0xd3, 0xd4, 0xd5, 0xd6}
BLOCCA_DIR = {0x30: 'E', 0x31: 'W', 0x32: 'N', 0x33: 'S'}           # casella che non si attraversa verso ...
FRECCE = {0x62: 'E', 0x63: 'W', 0x64: 'N', 0x65: 'S', 0x6d: 'S', 0x6e: 'S'}   # uscite a freccia: si sta sopra e si spinge
PORTE = (set(range(0x60, 0x70)) | {0x0e, 0x0f, 0x29, 0x8d, 0x8e}) - set(FRECCE)   # caselle d'uscita calpestabili
STAZIONARI = {0, 1, 7, 8, 9, 10, 12}                                 # tipi di movimento fermi (12 = albero di bacche, dalla 0.61)
SCR_ROCCIA, SCR_ALBERO, SCR_MASSO = 0x290b6b, 0x290a67, 0x290c74     # SPACCAROCCIA (0x869), TAGLIO, FORZA (0x86d)
DIRS = {'N': (0, -1), 'S': (0, 1), 'W': (-1, 0), 'E': (1, 0)}


class Mondo:
    def __init__(self, R):
        self.R = R; self.m = {}; self.g = {}

    def mappa(self, k):
        if k not in self.m:
            m = self.R.map(*k); a = self.R.blocks(m)
            beh = {}
            for v in set(int(x) & 1023 for x in a.flat): beh[v] = self.R.attr(m, v) & 0xff
            self.m[k] = m; self.g[k] = (a, beh)
        return self.m[k]

    def casella(self, k, x, y):
        m = self.mappa(k); a, beh = self.g[k]
        if not (0 <= x < m['width'] and 0 <= y < m['height']): return None
        v = int(a[y, x]); return dict(coll=(v >> 10) & 3, z=v >> 12, b=beh[v & 1023])


def oggetti_bloccanti(R, m, ab, flag_alzate, script_tipo):
    out = {}
    for o in m['objects']:
        if o['flag'] and o['flag'] in flag_alzate: continue
        if o['move'] not in STAZIONARI: continue
        t = script_tipo.get(o['script'])
        if t == 'roccia' and 'spacca' in ab: continue
        if t == 'albero' and 'taglio' in ab: continue
        if t == 'masso' and 'forza' in ab: continue
        out[(o['x'], o['y'])] = o
    return out


def cerca(R, partenza, ab, flag_alzate=(), script_tipo=None, z=None, surf=False, massi_vivi=None):
    """-> {stato: (stato precedente, direzione, azione)}; stato = (mappa, x, y, quota, surf).
    azione: 'passo', 'surf' (sale in acqua), 'salto', 'uscita' (porta/scala: si arriva all'uscita di destinazione)."""
    W = Mondo(R); flag_alzate = set(flag_alzate); script_tipo = script_tipo or {SCR_ROCCIA: 'roccia', SCR_ALBERO: 'albero', SCR_MASSO: 'masso'}
    blocchi = {}
    def ostacoli(k):
        if k not in blocchi:
            blocchi[k] = oggetti_bloccanti(R, W.mappa(k), ab, flag_alzate, script_tipo)
            if massi_vivi is not None and k == partenza[0]:      # massi gia' spostati (posizioni lette in RAM)
                rom = {(o['x'], o['y']) for o in W.mappa(k)['objects'] if script_tipo.get(o['script']) == 'masso'}
                for xy in massi_vivi:
                    if xy not in rom: blocchi[k][xy] = {'masso spostato': True}
        return blocchi[k]
    (k0, (x0, y0)) = partenza
    c0 = W.casella(k0, x0, y0)
    st0 = (k0, x0, y0, c0['z'] if z is None else z, surf)
    prec = {st0: None}; q = collections.deque([st0])
    mossa = ['', 'passo']
    def push(st, da):
        if st not in prec: prec[st] = (da, mossa[0], mossa[1]); q.append(st)
    def sott(k): return any(c['dir'] == 6 for c in W.mappa(k)['conns'])     # mappa sott'acqua (risalita: dir 6)
    def immersione(k, d): return next(((c['group'], c['num']) for c in W.mappa(k)['conns'] if c['dir'] == d), None)
    while q:
        st = q.popleft(); k, x, y, z, surf = st; m = W.mappa(k); cur = W.casella(k, x, y)
        if 'sub' in ab:                                          # SUB: giu' dall'acqua profonda, su dove si puo' risalire
            if surf and cur['b'] in (0x11, 0x12, 0x14) and immersione(k, 5):
                tk = immersione(k, 5); t = W.casella(tk, x, y); mossa[:] = ['', 'immersione']
                if t and t['coll'] == 0: push((tk, x, y, t['z'], False), st)
            if sott(k) and cur['b'] != 0x19:
                tk = immersione(k, 6); t = W.casella(tk, x, y) if tk else None; mossa[:] = ['', 'risalita']
                if t and t['b'] in SURFABILE: push((tk, x, y, 1, True), st)
        for dn, (dx, dy) in DIRS.items():
            if BLOCCA_DIR.get(cur['b']) == dn: continue
            mossa[:] = [dn, 'passo']
            if FRECCE.get(cur['b']) == dn:                       # uscita a freccia
                wp = [w for w in m['warps'] if (w['x'], w['y']) == (x, y)]
                if wp:
                    w = wp[0]; tk = (w['group'], w['num'])
                    try:
                        dw = W.mappa(tk)['warps'][w['warp']]; tc = W.casella(tk, dw['x'], dw['y']); mossa[1] = 'uscita'
                        push((tk, dw['x'], dw['y'], tc['z'], False), st)
                    except Exception: pass
                    continue
            nk, nx, ny = k, x + dx, y + dy
            t = W.casella(nk, nx, ny)
            if t is None:                                        # bordo: connessione
                for c in m['conns']:
                    tk = (c['group'], c['num'])
                    try: tm = W.mappa(tk)
                    except Exception: continue
                    o = c['offset']
                    if c['dir'] == 1 and dn == 'S': cand = (tk, x - o, 0)
                    elif c['dir'] == 2 and dn == 'N': cand = (tk, x - o, tm['height'] - 1)
                    elif c['dir'] == 3 and dn == 'W': cand = (tk, tm['width'] - 1, y - o)
                    elif c['dir'] == 4 and dn == 'E': cand = (tk, 0, y - o)
                    else: continue
                    t = W.casella(*cand)
                    if t is not None: nk, nx, ny = cand; break
                if t is None: continue
            opp = {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}[dn]
            if BLOCCA_DIR.get(t['b']) == opp: continue
            if (nx, ny) in ostacoli(nk): continue
            # uscita?
            wp = [w for w in W.mappa(nk)['warps'] if (w['x'], w['y']) == (nx, ny)]
            if wp and t['b'] not in FRECCE and (t['b'] in PORTE or t['coll'] == 0) and not surf:
                w = wp[0]; tk = (w['group'], w['num'])
                try:
                    tm = W.mappa(tk); dw = tm['warps'][w['warp']]
                    tc = W.casella(tk, dw['x'], dw['y']); mossa[1] = 'uscita'
                    push((tk, dw['x'], dw['y'], tc['z'], False), st)
                except Exception: pass
                if t['coll']: continue
            # salto di sporgenza
            if t['b'] in SALTI:
                if SALTI[t['b']] != (dx, dy) or surf: continue
                lx, ly = nx + dx, ny + dy; l = W.casella(nk, lx, ly); mossa[1] = 'salto'
                if l and l['coll'] == 0 and (nx, ny) not in ostacoli(nk): push((nk, lx, ly, l['z'] if l['z'] not in (0, 15) else z, False), st)
                continue
            if t['coll']: continue
            tz = t['z']
            mismatch = z not in (0, 15) and tz not in (0, 15) and tz != z
            acqua = t['b'] in SURFABILE
            if t['b'] == CASCATA:
                if not surf: continue
                if dn == 'N' and 'cascata' not in ab: continue
            if t['b'] == FANGO and dn == 'N' and 'corsa' not in ab: continue
            if (t['b'] == GOBBE or t['b'] in BINARI) and 'cross' not in ab: continue
            if sott(nk) and not surf:                            # sott'acqua si nuota come a piedi
                if not mismatch: push((nk, nx, ny, tz if tz not in (0, 15) else z, False), st)
                continue
            if surf:
                if acqua and not mismatch: push((nk, nx, ny, tz if tz not in (0, 15) else z, True), st)
                elif not acqua and tz == 3 and mismatch: push((nk, nx, ny, 3, False), st)       # scende a terra
                elif not acqua and not mismatch: push((nk, nx, ny, tz if tz not in (0, 15) else z, False), st)
                continue
            if acqua:
                mossa[1] = 'surf'
                if 'surf' in ab and z == 3 and (mismatch or tz in (0, 1)): push((nk, nx, ny, 1, True), st)
                continue
            if mismatch: continue
            push((nk, nx, ny, tz if tz not in (0, 15) else z, False), st)
    return prec


def strada(prec, st):
    """-> [(stato, direzione, azione)] dalla partenza (direzione e azione portano a quello stato)"""
    out = []
    while st:
        p = prec[st]
        out.append((st,) + ((p[1], p[2]) if p else ('', ''))); st = p[0] if p else None
    return out[::-1]


def raggiunge(prec, k, x, y):
    """Stato che sta accanto a (x, y) in k (per parlare con un oggetto) o sopra la casella (x, y)."""
    best = None
    for st in prec:
        if st[0] == k and abs(st[1] - x) + abs(st[2] - y) <= 1:
            if best is None or len(strada(prec, st)) < len(strada(prec, best)): best = st
    return best


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('rom'); ap.add_argument('partenza')
    ap.add_argument('--abilita', default=''); ap.add_argument('--flag', default='')
    ap.add_argument('--meta', nargs='*', default=[])
    a = ap.parse_args()
    R = romlib.Rom(a.rom)
    def pos(s):
        k, xy = s.split(':'); return tuple(map(int, k.split('.'))), tuple(map(int, xy.split(',')))
    ab = set(x for x in a.abilita.split(',') if x)
    fl = set(int(x, 16) for x in a.flag.split(',') if x)
    prec = cerca(R, pos(a.partenza), ab, fl)
    mappe = sorted({st[0] for st in prec})
    print('abilita:', ','.join(sorted(ab)) or '-', '| mappe raggiunte:', len(mappe))
    for s in a.meta:
        (k, (x, y)) = pos(s); st = raggiunge(prec, k, x, y)
        if st is None: print('  %s NON raggiunta' % s); continue
        p = strada(prec, st); tappe = []
        for e, _, _ in p:
            if not tappe or tappe[-1] != e[0]: tappe.append(e[0])
        print('  %s raggiunta in %d passi; da %s; surf=%s; mappe: %s' % (s, len(p) - 1, st[1:3], st[4],
              ' > '.join('%d.%d' % t for t in tappe)))


if __name__ == '__main__':
    main()
