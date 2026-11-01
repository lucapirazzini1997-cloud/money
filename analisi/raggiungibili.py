#!/usr/bin/env python3
"""Raggiungibilita' delle mappe (Lotto 1).

Grafo dalla mappa di partenza, con tutti i modi di spostarsi che si leggono nella ROM:
  - uscite (warp) delle mappe; le uscite dinamiche (0x7F) non portano a una mappa fissa;
  - connessioni ai bordi, comprese SUB (5) e risalita (6);
  - warp fatti dagli script (warp, warpsilent, warpdoor, warphole, warpteleport, setwarp, setdynamicwarp,
    setdivewarp, setholewarp, setescapewarp, warpspinenter, warpwhitefade...) in oggetti, coordinate,
    cartelli e script di mappa, seguendo call/goto e gli script degli allenatori;
  - Volo: destinazioni della tabella del Volo (0x74cfc8) con un punto di cura, quando la flag di visita della
    cella (0x86F + cella, la cella 5 usa 0x46D dalla 0.47) viene impostata da uno script di una mappa raggiungibile.
    Le flag 0x87B-0x87E vengono azzerate a ogni cambio di mappa dallo script globale: quelle celle non si volano.
  - i punti di cura (0x74adc0) non aggiungono mappe: si registrano solo visitando la mappa.
Il codice nativo di Smeraldo puo' portare in mappe fisse (Lotta Frontier, sale di collegamento...):
per questo una mappa irraggiungibile qui e' solo "candidata", non "sicuramente morta".

Uso: python3 analisi/raggiungibili.py ROM.gba [uscita.json]
"""
import sys, json, struct, collections
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / 'strumenti_rom'), str(ROOT / 'versioni')]
import romlib, scr, flagscan52

B = 0x08000000
FLY_TABLE, FLY_N = 0x74cfc8, 213
HEAL_TABLE, HEAL_N = 0x74adc0, 22
START = [(1, 0), (0, 9)]          # casa del protagonista e Lido di Savio
WARP_OPS = {0x39, 0x3a, 0x3b, 0x3c, 0x3d, 0x3e, 0x3f, 0x40, 0x41, 0xc4, 0xd1, 0xd7, 0xe0}


def script_warps(d, p, out, seen, depth=0):
    if p is None or p in seen or not (0 <= p < len(d)) or depth > 20: return
    seen.add(p)
    try: ins, _ = scr.decode(d, p, 600, follow=False)
    except Exception: return
    for a, nm, ar in ins:
        op = d[a]
        if op in WARP_OPS and len(ar) >= 2 and ar[0] != 0x7f: out.add((ar[0], ar[1]))
        if op in (0x04, 0x05, 0x06, 0x07) and ar and B <= ar[-1] < B + len(d):
            script_warps(d, ar[-1] - B, out, seen, depth + 1)
        if op == 0x5c:
            for x in ar[3:]:
                if isinstance(x, int) and B <= x < B + len(d): script_warps(d, x - B, out, seen, depth + 1)


def graph(R):
    d = bytes(R.data); maps = {}
    for g, n in flagscan52.real_maps(d):
        try:
            m = R.map(g, n)
            if 0 < m['width'] <= 512 and 0 < m['height'] <= 512: maps[(g, n)] = m
        except Exception: pass
    E = collections.defaultdict(dict)
    for k, m in maps.items():
        for w in m['warps']:
            if w['group'] != 0x7f: E[k].setdefault((w['group'], w['num']), 'uscita')
        for c in m['conns']:
            E[k].setdefault((c['group'], c['num']), 'SUB' if c['dir'] in (5, 6) else 'connessione')
        out = set()
        for lab, p in flagscan52.entries(R, m): script_warps(d, p, out, set())
        for t in out: E[k].setdefault(t, 'script')
    fly = {}
    for i in range(16):
        g, n, h = d[FLY_TABLE + 3 * i:FLY_TABLE + 3 * i + 3]
        if (g, n) in maps and h: fly[(g, n)] = 0x46d if i == 5 else 0x86f + i
    setters = collections.defaultdict(set)      # flag -> mappe con uno script che la imposta
    clears = collections.defaultdict(set)
    for k, m in maps.items():
        acc = dict(set=set(), clear=set(), check=set(), trainer=set())
        for lab, p in flagscan52.entries(R, m): flagscan52._walk(d, p, acc, set())
        for f in acc['set']: setters[f].add(k)
        for f in acc['clear']: clears[f].add(k)
    return maps, E, fly, setters, clears


def reachable(R):
    maps, E, fly, setters, clears = graph(R)
    seen = {k: 'partenza' for k in START}; todo = list(START)
    while True:
        while todo:
            k = todo.pop()
            for t, how in E[k].items():
                if t in maps and t not in seen: seen[t] = '%s da %d.%d' % (how, *k); todo.append(t)
        for t, f in fly.items():
            # flag azzerata da quasi tutte le mappe (script globale): la cella non resta mai visitata
            if t in seen or len(clears[f]) > len(maps) // 2: continue
            src = [k for k in setters[f] if k in seen]
            if src: seen[t] = 'Volo (flag %s da %d.%d)' % (hex(f), *src[0]); todo.append(t); E[src[0]].setdefault(t, 'Volo')
        if not todo: break
    return maps, E, seen


def main():
    R = romlib.Rom(sys.argv[1])
    maps, E, seen = reachable(R)
    dead = sorted(set(maps) - set(seen))
    print('mappe %d, raggiungibili %d, non raggiungibili %d' % (len(maps), len(seen), len(dead)))
    if len(sys.argv) > 2:
        incoming = collections.defaultdict(list)
        for k, es in E.items():
            for t, how in es.items(): incoming[t].append('%d.%d %s' % (k[0], k[1], how))
        json.dump(dict(raggiungibili={'%d.%d' % k: v for k, v in sorted(seen.items())},
                       non_raggiungibili={'%d.%d' % k: sorted(incoming.get(k, [])) for k in dead}),
                  open(sys.argv[2], 'w'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
