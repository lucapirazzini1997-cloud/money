#!/usr/bin/env python3
"""Raggiungibilita' a piedi, ottimistica (Lotto 1): casella per casella, su tutte le mappe.

Il grafo di raggiungibili.py collega due mappe se esiste un'uscita o una connessione, senza guardare se ci si
arriva camminando. Qui invece si visita la griglia: una casella e' percorribile se il suo bit di collisione e' 0;
dal bordo di una mappa si passa alla mappa connessa (con lo spostamento della connessione); da una casella di
uscita (o accanto a una porta) si arriva all'uscita di destinazione. Script e Volo come in raggiungibili.py
(il punto d'arrivo e' l'uscita indicata dallo script o, se manca, tutte le caselle libere della mappa).

E' ottimistica: ignora salti, acqua (Surf), rocce, alberi da tagliare, persone e blocchi degli script.
Quindi "non raggiungibile qui" vuol dire "non raggiungibile nemmeno con tutte le MN e senza blocchi":
un risultato forte. "Raggiungibile qui" invece va confermato in gioco.

Uso: python3 analisi/cammino.py ROM.gba [g.n ...]   (stampa se le mappe indicate si raggiungono a piedi)
"""
import sys, struct, collections
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / 'strumenti_rom'), str(ROOT / 'versioni'), str(ROOT / 'analisi')]
import romlib, raggiungibili as RG

START = ((0, 9), None)      # Lido di Savio: tutte le caselle libere collegate al punto di partenza (vedi sotto)
START_XY = {(1, 0): None}


def grids(R, maps):
    d = R.data; G = {}
    for k, m in maps.items():
        w, h, b = m['width'], m['height'], m['blocks']
        G[k] = (w, h, [struct.unpack_from('<H', d, b + 2 * i)[0] for i in range(w * h)])
    return G


def cammina(R, partenze):
    """partenze: [(mappa, (x, y) o None)] -> {mappa: insieme di caselle raggiunte}"""
    maps, E, fly, setters, clears = RG.graph(R)
    G = grids(R, maps)
    def libera(k, x, y):
        w, h, a = G[k]; return 0 <= x < w and 0 <= y < h and (a[y * w + x] >> 10) & 3 == 0
    seen = collections.defaultdict(set); q = collections.deque()
    def push(k, x, y, forza=False):
        if k not in G: return
        w, h, a = G[k]
        if not (0 <= x < w and 0 <= y < h) or (x, y) in seen[k]: return
        if not forza and not libera(k, x, y): return
        seen[k].add((x, y)); q.append((k, x, y))
    def tutta(k):
        w, h, a = G[k]
        for y in range(h):
            for x in range(w): push(k, x, y)
    for k, xy in partenze:
        if xy: push(k, *xy, forza=True)
        else: tutta(k)
    warps = {k: m['warps'] for k, m in maps.items()}
    script_done = set()
    while q:
        k, x, y = q.popleft(); w, h, a = G[k]
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)): push(k, x + dx, y + dy)
        # uscite: sulla casella o accanto (porte, scale sul bordo)
        for i, wp in enumerate(warps[k]):
            if abs(wp['x'] - x) + abs(wp['y'] - y) <= 1 and wp['group'] != 0x7f:
                t = (wp['group'], wp['num'])
                if t in warps and wp['warp'] < len(warps[t]):
                    dw = warps[t][wp['warp']]; push(t, dw['x'], dw['y'], forza=True)
                elif t in G: tutta(t)
        # connessioni ai bordi
        for c in maps[k]['conns']:
            t = (c['group'], c['num']); o = c['offset']
            if t not in G: continue
            wt, ht, _ = G[t]
            if c['dir'] == 1 and y == h - 1: push(t, x - o, 0)
            elif c['dir'] == 2 and y == 0: push(t, x - o, ht - 1)
            elif c['dir'] == 3 and x == 0: push(t, wt - 1, y - o)
            elif c['dir'] == 4 and x == w - 1: push(t, 0, y - o)
            elif c['dir'] in (5, 6): tutta(t)
        # warp degli script (una volta per mappa: si arriva in tutta la mappa di destinazione)
        if k not in script_done:
            script_done.add(k)
            for t, how in E[k].items():
                if how == 'script' and t in G: tutta(t)
    return maps, seen


def main():
    R = romlib.Rom(sys.argv[1])
    maps, seen = cammina(R, [((1, 0), None), ((0, 9), None)])
    print('mappe raggiunte a piedi (ottimistico): %d su %d' % (len([k for k in seen if seen[k]]), len(maps)))
    for a in sys.argv[2:]:
        k = tuple(map(int, a.split('.')))
        print(a, 'raggiungibile' if seen.get(k) else 'NON raggiungibile', len(seen.get(k, ())))


if __name__ == '__main__':
    main()
