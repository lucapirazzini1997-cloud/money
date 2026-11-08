#!/usr/bin/env python3
"""Testi troppo lunghi (Lotto 3): tutti i testi degli script delle mappe date (oggetti, cartelli, eventi a coordinate,
script di mappa), riquadro per riquadro. Regola del progetto: massimo 2 righe per riquadro e 30 caratteri per riga
(\\l, lo scorrimento, conta come riquadro nuovo, come \\p).
Uso: python3 analisi/testi_lunghi.py ROM [--mappe FILE_JSON con ["g.n", ...]] [--json USCITA]"""
import sys, struct, os, json
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
        elif c == 0xfd: cur += '{' + str(d[p]) + '}'; p += 1
        elif c == 0xfc: cur += '{c' + str(d[p]) + '}'; p += 2 if d[p] in (1, 2, 3) else 1
        else: cur += CHAR.get(c, '?')
    out.append(cur)
    box, boxes = [], []
    for l in out:
        if l.startswith('\f'): boxes.append(box); box = []; l = l[1:]
        box.append(l)
    boxes.append(box); return boxes


def lung(l):                      # {N} e' un nome (giocatore, rivale): si conta 7 caratteri
    import re
    return len(re.sub(r'\{\d+\}', 'XXXXXXX', re.sub(r'\{c\d+\}', '', l)))


def puntatori(sp):
    out, todo, visti = [], [sp], set()
    while todo:
        p = todo.pop()
        if p in visti or not (0 <= p < len(d)): continue
        visti.add(p)
        ins, _ = scr.decode(d, p, 400)
        for a, nm, args in ins:
            if nm == 'loadword' and len(args) > 1 and B <= args[1] < B + len(d): out.append(args[1] - B)
            if nm == 'trainerbattle':
                out += [x - B for x in args[3:5] if B <= x < B + len(d)]
    return list(dict.fromkeys(out))


def fonti(k):
    m = R.map(*k); out = []
    out += [('ogg %d' % o['id'], o['script']) for o in m['objects'] if o['script']]
    out += [('cart %d,%d' % (b['x'], b['y']), b['arg'] - B) for b in m['bgs'] if b['kind'] < 5 and b['arg'] >= B]
    out += [('coord %d,%d' % (c['x'], c['y']), c['script']) for c in m['coords'] if c['script']]
    for t, p in R.map_scripts(m):
        q = p - B if p >= B else p
        if t in (2, 4):
            while struct.unpack_from('<H', d, q)[0]:
                out.append(('mappa %d' % t, struct.unpack_from('<I', d, q + 4)[0] - B)); q += 8
        else: out.append(('mappa %d' % t, q))
    return out


if __name__ == '__main__':
    mappe = None
    if '--mappe' in sys.argv: mappe = [tuple(map(int, s.split('.'))) for s in json.load(open(sys.argv[sys.argv.index('--mappe') + 1]))]
    mappe = mappe or sorted(romlib.all_maps(R))
    visti = {}; res = []
    for k in mappe:
        for n, sp in fonti(k):
            for q in puntatori(sp):
                if q in visti: continue
                visti[q] = 1
                boxes = testo(q)
                bad = [b for b in boxes if len(b) > 2 or any(lung(l) > 30 for l in b)]
                if bad: res.append(dict(mappa='%d.%d' % k, fonte=n, testo=hex(q), riquadri=boxes))
    for r in res: print(r['mappa'], r['fonte'], r['testo'], ' | '.join(' / '.join(b) for b in r['riquadri'])[:230])
    print('testi con riquadri troppo lunghi:', len(res), 'su', len(visti))
    if '--json' in sys.argv: json.dump(res, open(sys.argv[sys.argv.index('--json') + 1], 'w'), indent=1, ensure_ascii=False)
