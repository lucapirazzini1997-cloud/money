"""0.67: il treno nella ROM e' quello della bozza approvata (bozze/treno.py)?
- citta': immagine di tutta la mappa 0.66 contro 0.67: cambiano solo le 4 caselle del cartello, e quelle sono uguali
  alla bozza; collisione e quota uguali ovunque tranne la porta (collisione 0); comportamento cambiato solo alla
  porta (0x60); uscita nuova sulla porta verso la sala; il cartello "porta chiusa" sulla porta non c'e' piu';
- sala (24.39, 24.40, 24.41, 24.50, 24.51): stessa immagine della sala del binario di Smeraldo e della bozza;
  oggetti e uscite come nella bozza; cartelli: solo la biglietteria (12,8) (differenza dichiarata: il tabellone
  (2-3,4) sta dietro la ringhiera e non si raggiunge, le fermate le dice la biglietteria);
- carrozza (24.74): immagine uguale alla bozza; oggetti come nella bozza.
Uso: python3 collaudo/confronto_bozza_067.py ROM_066 ROM_067"""
import sys, runpy
from pathlib import Path
import numpy as np
R = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(R / 'strumenti_rom')]
import tela, romlib
r066, r067 = sys.argv[1], sys.argv[2]
sys.argv[:] = ['x', r066, '/dev/null']
bz = runpy.run_path(str(R / 'bozze/treno.py'), run_name='bozza')
d = bz['d']
A, Bn = romlib.Rom(r066), romlib.Rom(r067)
ok = True


def diverse(im1, im2, w, h, tol=8):
    a = np.array(im1).astype(int); b = np.array(im2).astype(int); out = []
    for y in range(h):
        for x in range(w):
            if np.abs(a[y*16:y*16+16, x*16:x*16+16] - b[y*16:y*16+16, x*16:x*16+16]).max() > tol: out.append((x, y))
    return out


SALE = {'Cesena': (24, 39), 'Rimini': (24, 40), 'Forli': (24, 41), 'Faenza': (24, 50), 'Imola': (24, 51)}
for c in bz['CITTA']:
    k = (c.g, c.n); ma, mb = A.map(*k), Bn.map(*k); w, h = mb['width'], mb['height']
    ia, ib = A.render(ma, events=False, scale=1), Bn.render(mb, events=False, scale=1)
    dif = diverse(ia, ib, w, h)
    attese = [(c.x + i, c.riga) for i in range(4)]
    U, v = c.valori(); iz = tela.anteprima(d, U, v, w, h)
    dz = [p for p in diverse(iz, ib, w, h) if p in attese]
    aa, ab = A.blocks(ma), Bn.blocks(mb)
    bits = [(x, y) for y in range(h) for x in range(w) if (int(aa[y, x]) & 0xfc00) != (int(ab[y, x]) & 0xfc00)]
    beh = [(x, y) for y in range(h) for x in range(w)
           if A.attr(ma, int(aa[y, x]) & 1023) & 0xff != Bn.attr(mb, int(ab[y, x]) & 1023) & 0xff]
    porta = c.porta
    nuove = [(w_['x'], w_['y'], w_['group'], w_['num']) for w_ in mb['warps'][len(ma['warps']):]]
    chiusa = [b for b in mb['bgs'] if (b['x'], b['y']) == porta]
    r_ = (dif == attese and not dz and bits == [porta] and beh == [porta]
          and Bn.attr(mb, int(ab[porta[1], porta[0]]) & 1023) & 0xff == 0x60 and (int(ab[porta[1], porta[0]]) >> 10) & 3 == 0
          and nuove == [(porta[0], porta[1]) + SALE[c.nome]] and not chiusa)
    print('%-7s caselle cambiate %s (attese %s), diverse dalla bozza %s, collisione/quota %s, comportamento %s, uscite nuove %s, porta chiusa %s -> %s'
          % (c.nome, dif, attese, dz, bits, beh, nuove, bool(chiusa), 'ok' if r_ else 'DIVERSO'))
    ok &= r_

s = bz['sala']
U = tela.Unione(d); v = s.T.valori(U); iz = tela.anteprima(d, U, v, s.w, s.h)
for nome, k in SALE.items():
    m = Bn.map(*k); ib = Bn.render(m, events=False, scale=1)
    dz = diverse(iz, ib, s.w, s.h)
    og = [(o['x'], o['y'], o['gfx']) for o in m['objects']]
    bg = sorted((b['x'], b['y']) for b in m['bgs']); us = sorted((w_['x'], w_['y']) for w_ in m['warps'])
    r_ = (m['width'], m['height']) == (13, 12) and not dz and og == [(x, y, g) for x, y, g, _ in s.oggetti] \
        and bg == [(12, 8)] and us == sorted(p for p, _ in s.uscite)
    print('sala %-7s %s: diverse dalla bozza %s, oggetti %s, cartelli %s, uscite %s -> %s' % (nome, k, dz, og, bg, us, 'ok' if r_ else 'DIVERSO'))
    ok &= r_

c = bz['carrozza']
U = tela.Unione(d); v = c.T.valori(U); c.ritocco(U, v); iz = tela.anteprima(d, U, v, c.w, c.h)
m = Bn.map(24, 74); ib = Bn.render(m, events=False, scale=1)
dz = diverse(iz, ib, c.w, c.h)
og = [(o['x'], o['y'], o['gfx']) for o in m['objects']]
r_ = (m['width'], m['height']) == (16, 12) and not dz and og == [(x, y, g) for x, y, g, _ in c.oggetti]
print('carrozza 24.74: diverse dalla bozza %s, oggetti %s -> %s' % (dz, og, 'ok' if r_ else 'DIVERSO'))
ok &= r_
print('TUTTO OK' if ok else 'DIFFERENZE')
