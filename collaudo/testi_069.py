#!/usr/bin/env python3
"""Testi della 0.69 letti dalla ROM: i 21 testi riscritti (indirizzi da out/rapporto_build.json), riquadro per
riquadro (max 2 righe, 30 caratteri; i nomi contano 7); e confronto 0.68/0.69 di tutti i testi corretti sul posto
(accenti e apostrofi): fuori da quei testi e dai testi nuovi non cambia nessun byte dei testi.
Uso: python3 collaudo/testi_069.py ROM_068 ROM_069"""
import sys, os, json, re
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'strumenti_rom'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'analisi'))
a, b = open(sys.argv[1], 'rb').read(), open(sys.argv[2], 'rb').read()
sys.argv = [sys.argv[0], sys.argv[2]]
import testi_lunghi as T
rap = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'out', 'rapporto_build.json')))['rapporto']['069']
ok = True
for r in rap['riscritti']:
    q = int(r['indirizzo'], 16)
    for box in T.testo(q):
        bad = len(box) > 2 or any(T.lung(l) > 30 for l in box)
        ok &= not bad
        print('%-10s %s %s' % (r['indirizzo'], 'TROPPO' if bad else 'ok   ', ' / '.join('%s (%d)' % (l, T.lung(l)) for l in box)))
# byte cambiati fra 0.68 e 0.69
diff = [i for i in range(len(a)) if a[i] != b[i]]
testi = sorted({int(x['testo'], 16) for x in rap['accenti']} | {int(x['testo'], 16) for x in rap['apostrofi']})
def dentro(i):
    for t in testi:
        if t <= i <= a.index(b'\xff', t): return True
    return False
nuovi = [(int(r['indirizzo'], 16), int(r['indirizzo'], 16) + len(T.d[int(r['indirizzo'], 16):].split(b'\xff')[0]) + 1) for r in rap['riscritti']]
punt = sum(r['istruzioni'] for r in rap['riscritti'])
altri = [i for i in diff if not dentro(i) and not any(s <= i < e for s, e in nuovi)]
print('byte diversi 0.68/0.69:', len(diff), '; fuori dai testi corretti e dai testi nuovi:', len(altri),
      '(attesi solo i puntatori ripuntati: %d istruzioni, al massimo %d byte)' % (punt, punt * 4))
ok &= len(altri) <= punt * 4
print('TUTTO OK' if ok else 'PROBLEMI')
