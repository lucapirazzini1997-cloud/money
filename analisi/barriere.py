#!/usr/bin/env python3
"""Inventario delle barriere a coordinate (Lotto 3, "Progressione"): per ogni evento a coordinate il cui script
sposta il giocatore (applymovement 0xFF) senza cambiare la propria variabile, cioe' un blocco che si ripete,
stampa: mappa, caselle, condizioni lette (checkflag/compare), testi, se cambia mappa.
Uso: python3 analisi/barriere.py ROM [--json FILE]"""
import sys, json, struct, collections
from pathlib import Path
R_ = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(R_ / 'strumenti_rom')]
import romlib, scr

rom = romlib.Rom(sys.argv[1]); d = bytes(rom.data)
gruppi = collections.OrderedDict()
for k, m in romlib.all_maps(rom).items():
    for c in m['coords']:
        if not c['script']: continue
        ins, _ = scr.decode(d, c['script'], 300)
        nomi = [n for _, n, _ in ins]
        muove = any(n == 'applymovement' and a[0] in (0xff, 0x7f) for _, n, a in ins)
        if not muove: continue
        cambia_var = any(n == 'setvar' and a[0] == c['var'] for _, n, a in ins) if c['var'] else False
        warp = any(n.startswith('warp') for n in nomi)
        cond = sorted({'%s %s' % (n, ' '.join(hex(x) for x in a[:2])) for _, n, a in ins if n in ('checkflag', 'compare', 'checkitem', 'checkpartymove', 'goto_if_set', 'goto_if_unset')})
        testi = []
        for a_, n, a in ins:
            if n == 'loadword' and len(a) > 1 and a[1] >= scr.B: testi.append(scr.text(d, a[1] - scr.B, 400))
        key = (k, c['script'])
        g = gruppi.setdefault(key, dict(mappa='%d.%d' % k, script=hex(c['script']), caselle=[], var=hex(c['var']), val=c['val'],
                                         cambia_var=cambia_var, warp=warp, condizioni=cond, testi=testi))
        g['caselle'].append((c['x'], c['y']))
out = list(gruppi.values())
for g in out:
    tipo = 'scena (una volta)' if g['cambia_var'] else 'BLOCCO'
    print('%-6s %-18s %s var %s=%d %s caselle %s' % (g['mappa'], tipo, g['script'], g['var'], g['val'], 'warp' if g['warp'] else '', g['caselle']))
    for c in g['condizioni']: print('        ', c)
    for t in g['testi']: print('         "%s"' % t[:160])
if '--json' in sys.argv: json.dump(out, open(sys.argv[sys.argv.index('--json') + 1], 'w'), indent=1, ensure_ascii=False)
