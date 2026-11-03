#!/usr/bin/env python3
"""Testi della 0.64 letti dalla ROM, riquadro per riquadro: righe per riquadro e caratteri per riga (max 2 e 30).
Legge i testi dei trainerbattle (presentazione, sconfitta) e dei loadword degli script degli oggetti e dei cartelli
di 35.101, e i testi ripuntati del casellante 35.91 (0x1599d0a) e di ADA (0x2d2672).
Uso: python3 collaudo/testi_064.py ROM"""
import sys, struct
sys.path.insert(0, __import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), '..', 'strumenti_rom'))
import romlib
from text_codec import CHAR
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
    out = []; seg = d[sp:sp + 40]
    i = seg.find(b'\x5c')
    if i >= 0 and seg[i + 1] in (0, 2):
        out += [struct.unpack_from('<I', seg, i + 6)[0], struct.unpack_from('<I', seg, i + 10)[0]]
    j = 0
    while True:
        j = seg.find(b'\x0f\x00', j)
        if j < 0: break
        q = struct.unpack_from('<I', seg, j + 2)[0]
        if B <= q < B + len(d): out.append(q)
        j += 2
    return [q - B for q in out]
m = R.map(35, 101); ok = True
fonti = [('oggetto %d' % o['id'], o['script']) for o in m['objects'] if o['script'] != 0x290b6b]
fonti += [('cartello %d,%d' % (b['x'], b['y']), b['arg'] - B) for b in m['bgs']]
testi = [(n, q) for n, sp in fonti for q in puntatori(sp)]
testi += [('casellante 35.91', struct.unpack_from('<I', d, 0x1599d0c)[0] - B), ('ADA 34.48', struct.unpack_from('<I', d, 0x2d2674)[0] - B)]
for n, q in testi:
    for box in testo(q):
        bad = len(box) > 2 or any(len(l) > 30 for l in box)
        ok &= not bad
        print('%-16s %s %s' % (n, 'TROPPO' if bad else 'ok   ', ' / '.join('%s (%d)' % (l, len(l)) for l in box)))
print('TUTTO OK' if ok else 'CI SONO RIQUADRI TROPPO LUNGHI')
