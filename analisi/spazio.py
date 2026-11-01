#!/usr/bin/env python3
"""Ricerca di spazio recuperabile nella ROM (Lotto 1, versione 0.57).

Cerca i blocchi di zeri (>= 4 KB) a cui non arriva nessun puntatore credibile e dentro cui non finisce
nessuna struttura nota, e li restituisce come zone candidate, con il motivo di ogni esclusione.

Regole (tutte conservative):
  1. Puntatori: ogni parola a 4 byte allineata con valore 0x08000000-0x09FFFFFF e bersaglio allineato a 4.
     Si scartano come rumore solo quelli che stanno in mezzo a grafica o codice: nessuna delle due parole
     vicine e' a sua volta un puntatore, un valore piccolo (< 0x10000) o 0xFFFFFFFF.
     I puntatori non allineati (testi, script) non possono puntare dentro un blocco di soli zeri:
     un testo finirebbe solo al primo 0xFF e uno script eseguirebbe una fila di 'nop'.
  2. Un puntatore credibile dentro il blocco lo taglia: dal bersaglio si escludono 64 KB.
  3. Strutture che finiscono dentro il blocco: per il bersaglio credibile piu' vicino prima del blocco
     si calcola l'estensione se la struttura e' nota (layout, dati della mappa, bordo, tileset con grafica,
     tavolozze, metatile e attributi, blob LZ77). Se non e' nota, si lasciano 64 KB di margine dal bersaglio.
  4. 256 byte di margine all'inizio di ogni zona, allineamento a 4, minimo 4 KB per zona.
  5. Le prime 0x200000 (codice di Smeraldo) non si toccano mai.

Uso: python3 analisi/spazio.py ROM.gba [uscita.json]
"""
import sys, re, json, struct
from pathlib import Path
import numpy as np

B = 0x08000000
LAYOUT_TABLE = 0x095aa02c - B          # tabella dei layout dalla 0.55
CODE_END = 0x200000
MIN_ZONE = 4096
MARGIN = 0x100
UNKNOWN_MARGIN = 0x10000


def u32(d, p): return struct.unpack_from('<I', d, p)[0]


def pointer_index(d):
    a = np.frombuffer(d, dtype=np.uint8).astype(np.uint32)
    v = a[:-3] | (a[1:-2] << 8) | (a[2:-1] << 16) | (a[3:] << 24)
    pos = np.nonzero((v >= B) & (v < B + 0x2000000))[0]
    tgt = v[pos] - B
    k = (pos % 4 == 0) & (tgt % 4 == 0)
    return pos[k].astype(np.int64), tgt[k].astype(np.int64)


def credible(d, pos):
    def ok(p):
        if p < 0 or p > len(d) - 4: return True
        w = u32(d, p)
        return B <= w < B + 0x2000000 or w < 0x10000 or w == 0xffffffff
    return np.array([ok(int(p) - 4) or ok(int(p) + 4) for p in pos], dtype=bool)


def lz_size(d, p):
    """Lunghezza compressa di un blob LZ77 (tipo 0x10), o None se non lo e'."""
    if p + 4 > len(d) or d[p] != 0x10: return None
    n = int.from_bytes(d[p + 1:p + 4], 'little')
    if not 0 < n <= 0x40000: return None
    q = p + 4; out = 0
    try:
        while out < n:
            fl = d[q]; q += 1
            for bit in range(7, -1, -1):
                if out >= n: break
                if fl & (1 << bit):
                    a, b = d[q], d[q + 1]; q += 2
                    disp = ((a & 15) << 8) + b + 1
                    if disp > out: return None
                    out += (a >> 4) + 3
                else:
                    q += 1; out += 1
    except IndexError:
        return None
    return q - p


def known_structures(d):
    """Estensioni note: {inizio: (fine, descrizione)}."""
    S = {}
    def add(p, n, what):
        if p is None or not (0 <= p < len(d)): return
        e = p + n
        if p not in S or S[p][0] < e: S[p] = (e, what)
    def ptr(p):
        v = u32(d, p); return v - B if B <= v < B + len(d) else None
    seen_ts = set()
    for i in range(1000):
        lp = ptr(LAYOUT_TABLE + i * 4)
        if lp is None:
            if u32(d, LAYOUT_TABLE + i * 4) == 0: continue
            break
        w, h = u32(d, lp), u32(d, lp + 4)
        if not (0 < w <= 512 and 0 < h <= 512): continue
        add(lp, 0x18, 'layout %d' % i)
        add(ptr(lp + 12), w * h * 2, 'dati mappa layout %d' % i)
        add(ptr(lp + 8), 8, 'bordo layout %d' % i)
        for tp in (ptr(lp + 16), ptr(lp + 20)):
            if tp is None or tp in seen_ts: continue
            seen_ts.add(tp); add(tp, 0x18, 'tileset')
            tiles = ptr(tp + 4)
            if tiles is not None:
                n = lz_size(d, tiles) if d[tp] else 0x4000
                add(tiles, n or 0x4000, 'grafica tileset %s' % ('compressa' if d[tp] else 'non compressa'))
            add(ptr(tp + 8), 0x200, 'tavolozze tileset')
            add(ptr(tp + 12), 0x2000, 'metatile')
            add(ptr(tp + 16), 0x400, 'attributi metatile')
    return S


def analyse(d):
    pos, tgt = pointer_index(d)
    cr = credible(d, pos)
    P, T = pos[cr], tgt[cr]
    o = np.argsort(T, kind='stable'); P, T = P[o], T[o]
    S = known_structures(d)
    ivals = sorted((st, en) for st, (en, _) in S.items())
    zones, detail = [], []
    for m in re.finditer(rb'\x00{%d,}' % MIN_ZONE, d):
        s, e = m.start(), m.end()
        if s < CODE_END:
            continue
        info = dict(blocco=[hex(s), hex(e)], kb=(e - s) // 1024)
        detail.append(info)
        # 2. bersagli credibili dentro il blocco: da ognuno si escludono 64 KB (struttura di lunghezza ignota)
        i, j = np.searchsorted(T, s), np.searchsorted(T, e)
        cuts = [(int(t), int(t) + UNKNOWN_MARGIN) for t in T[i:j]]
        if cuts: info['bersagli_dentro'] = sorted(set(hex(c[0]) for c in cuts))
        # 3a. si tolgono tutte le strutture note che toccano il blocco
        pieces = [(s, e)]
        for st, en in ivals + cuts:
            if en <= s or st >= e: continue
            nxt = []
            for a, b in pieces:
                if en <= a or st >= b: nxt.append((a, b)); continue
                if a < st: nxt.append((a, st))
                if en < b: nxt.append((en, b))
            pieces = nxt
        info['zone'] = []
        for a, b in pieces:
            # 3b. il bersaglio credibile piu' vicino prima del pezzo: dove finisce la sua struttura?
            k = np.searchsorted(T, a) - 1
            prev = int(T[k]) if k >= 0 else 0
            if prev in S: fine = S[prev][0]; why = '%s a %s' % (S[prev][1], hex(prev))
            elif any(st <= prev < en for st, en in ivals if st <= prev): fine = a; why = 'dentro una struttura nota'
            else:
                n = lz_size(d, prev)
                if n: fine = prev + n; why = 'LZ77 a %s' % hex(prev)
                else: fine = prev + UNKNOWN_MARGIN; why = 'struttura ignota a %s, margine 64 KB' % hex(prev)
            zs = (max(a, fine) + MARGIN + 3) & ~3
            if b - zs >= MIN_ZONE:
                zones.append((zs, b)); info['zone'].append(dict(zona=[hex(zs), hex(b)], kb=(b - zs) // 1024, prima=why))
    return zones, detail


def main():
    rom = Path(sys.argv[1]); d = rom.read_bytes()
    zones, info = analyse(d)
    tot = sum(e - s for s, e in zones)
    print('zone candidate: %d, %d KB' % (len(zones), tot // 1024))
    if len(sys.argv) > 2:
        json.dump(dict(zone=[[hex(s), hex(e)] for s, e in zones], dettaglio=info), open(sys.argv[2], 'w'), indent=1)


if __name__ == '__main__':
    main()
