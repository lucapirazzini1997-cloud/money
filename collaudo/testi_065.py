#!/usr/bin/env python3
"""Testi della 0.65 letti dalla ROM, riquadro per riquadro: righe per riquadro e caratteri per riga (max 2 e 30).
Segue gli script degli oggetti e dei cartelli di 35.51 (compresi i salti e lo script di continuazione del capo)
e raccoglie i testi di loadword e trainerbattle; poi i testi ripuntati di 35.50 (oggetti 1-4 e cartello).
Uso: python3 collaudo/testi_065.py ROM"""
import sys, struct, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'strumenti_rom'))
import romlib, scr
from text_codec import CHAR
CHAR = {**CHAR, 1: 'À', 5: 'È', 6: 'É', 9: 'Ì', 0x0d: 'Ò', 0x11: 'Ù'}
R = romlib.Rom(sys.argv[1]); d = bytes(R.data); B = 0x8000000
def testo(p):
    out = []; cur = ''
    while d[p] != 0xff:
        c = d[p]; p += 1
        if c in (0xfa, 0xfb): out.append(cur); cur = '\f'
        elif c == 0xfe: out.append(cur); cur = ''
        else: cur += CHAR.get(c, '?')
    out.append(cur)
    box, boxes = [], []
    for l in out:
        if l.startswith('\f'): boxes.append(box); box = []; l = l[1:]
        box.append(l)
    boxes.append(box); return boxes
def puntatori(sp):
    out, todo, visti = [], [sp], set()
    while todo:
        p = todo.pop()
        if p in visti: continue
        visti.add(p)
        ins, _ = scr.decode(d, p, 300)
        for a, nm, args in ins:
            if nm == 'loadword' and B <= args[1] < B + len(d): out.append(args[1] - B)
            if nm == 'trainerbattle':
                out += [args[3] - B, args[4] - B]
                if args[0] == 1: todo.append(args[5] - B)            # script di continuazione
    return list(dict.fromkeys(out))
ok = True
fonti = []
for k in ((35, 51), (35, 50)):
    m = R.map(*k)
    fonti += [('%d.%d ogg %d' % (k + (o['id'],)), o['script']) for o in m['objects'] if o['script']]
    fonti += [('%d.%d cart %d,%d' % (k + (b['x'], b['y'])), b['arg'] - B) for b in m['bgs']]
for n, sp in fonti:
    for q in puntatori(sp):
        for box in testo(q):
            bad = len(box) > 2 or any(len(l) > 30 for l in box)
            ok &= not bad
            print('%-18s %s %s' % (n, 'TROPPO' if bad else 'ok   ', ' / '.join('%s (%d)' % (l, len(l)) for l in box)))
print('TUTTO OK' if ok else 'CI SONO RIQUADRI TROPPO LUNGHI')
