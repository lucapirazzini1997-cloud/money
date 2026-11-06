"""0.66: le mappe del Fumaiolo nella ROM sono quelle delle bozze approvate (bozze/fumaiolo.py, bozze/santuario.py)?
Per ogni mappa (35.10, 35.12-35.18), casella per casella, confronta la bozza (calcolata sulla ROM 0.65) con la ROM 0.66:
  - immagine della casella (pixel), collisione e quota: devono coincidere, tranne i cambi dichiarati;
  - comportamento: deve coincidere, tranne i cambi dichiarati.
Cambi dichiarati: stele del Tevere (35.10, 10,4: pilastro del Monte Pira al posto del segnaposto); frecce d'uscita
(35.10, 18-20,99: solo comportamento); porta profonda (35.16, 8,2: niente comportamento di porta, si entra con lo
script); gobbe del Passo (35.18: comportamento normale, si sale senza Bici Cross).
Poi controlla posizioni di oggetti, uscite, cartelli e frane rispetto alle bozze (differenze dichiarate: guardiano
della porta profonda da 8,3 a 9,3, cosi' chi torna dal Cuore non resta chiuso sulla porta).
Uso: python3 collaudo/confronto_bozza_066.py ROM_065 ROM_066"""
import sys, runpy, struct
from pathlib import Path
import numpy as np
R = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(R / 'strumenti_rom')]
import tela, romlib
r065, r066 = sys.argv[1], sys.argv[2]
d = open(r065, 'rb').read()
sys.argv[:] = ['x', r065, '/dev/null']
fu = runpy.run_path(str(R / 'bozze/fumaiolo.py'), run_name='bozza')
sa = runpy.run_path(str(R / 'bozze/santuario.py'), run_name='bozza')
rom = romlib.Rom(r066)
ok = True


def confronta(n, T, w, h, U=None, ammessi_pixel=(), ammessi_beh=lambda x, y, a, b: False):
    global ok
    if U is None: U = tela.Unione(d)
    v = T.valori(U)
    im = np.array(tela.anteprima(d, U, v, w, h))
    m = rom.map(35, n); a = rom.blocks(m)
    assert (m['width'], m['height']) == (w, h), (n, m['width'], m['height'])
    ir = np.array(rom.render(m, events=False, scale=1))
    def beh_b(x, y):
        k = v[y * w + x] & 1023
        return (U.prim.attr(k) if k < 512 else U.meta[k - 512][1]) & 0xff
    pix, bits, beh = [], [], []
    for y in range(h):
        for x in range(w):
            if np.abs(im[y*16:y*16+16, x*16:x*16+16].astype(int) - ir[y*16:y*16+16, x*16:x*16+16].astype(int)).max() > 8: pix.append((x, y))   # le due anteprime convertono i colori in modo un po' diverso
            if (v[y * w + x] & 0xfc00) != (int(a[y, x]) & 0xfc00): bits.append((x, y))
            bb, br = beh_b(x, y), rom.attr(m, int(a[y, x]) & 1023) & 0xff
            if bb != br and not ammessi_beh(x, y, bb, br): beh.append((x, y, hex(bb), hex(br)))
    extra = [p for p in pix if p not in ammessi_pixel]
    print('35.%d: pixel diversi %s (dichiarati %s), collisione/quota diverse %s, comportamenti non dichiarati %s'
          % (n, extra, [p for p in pix if p in ammessi_pixel], bits, beh))
    ok &= not extra and not bits and not beh


# Sentiero
confronta(10, fu['T'], fu['W'], fu['H'], ammessi_pixel={(10, 4)},
          ammessi_beh=lambda x, y, a, b: (y == 99 and 18 <= x <= 20 and (a, b) == (0, 0x65)) or (x, y) == (10, 4))
m = rom.map(35, 10)
pos = [(o['x'], o['y']) for o in m['objects']]
print('   oggetti', pos == [(x, y) for x, y, _, _ in fu['OGGETTI']], pos)
usc = sorted((w['x'], w['y']) for w in m['warps']); print('   uscite', usc == sorted(p for p, _ in fu['USCITE']), usc)
bg = sorted((b['x'], b['y']) for b in m['bgs']); print('   cartelli', bg == sorted(fu['CARTELLI']), bg)
ok &= pos == [(x, y) for x, y, _, _ in fu['OGGETTI']] and usc == sorted(p for p, _ in fu['USCITE']) and bg == sorted(fu['CARTELLI'])
# interno
for s in sa['STANZE']:
    U = tela.Unione(d)
    if s.n == 18:
        amm = lambda x, y, a, b: (a, b) == (0xd1, 0)
    elif s.n == 16:
        amm = lambda x, y, a, b: (x, y) == (8, 2) and (a, b) == (0x60, 0)
    else:
        amm = lambda x, y, a, b: False
    confronta(s.n, s.T, s.w, s.h, U, ammessi_beh=amm)
    m = rom.map(35, s.n)
    pos = [(o['x'], o['y']) for o in m['objects']]
    attesi = [(x, y) for x, y, _, _ in s.oggetti]
    if s.n == 12: attesi = [pos[0]] + attesi                 # masso del vecchio rompicapo (sempre nascosto)
    if s.n == 16: attesi = [(10, 5), (9, 3), (14, 31)]      # guardiano spostato (dichiarato)
    usc = sorted(set((w['x'], w['y']) for w in m['warps'])); att_u = sorted(set(p for p, _ in s.uscite))
    co = sorted((c['x'], c['y']) for c in m['coords']); bg = sorted((b['x'], b['y']) for b in m['bgs'])
    r_ = pos == attesi and usc == att_u and co == sorted(s.barriera) and bg == sorted(s.cartelli)
    print('   oggetti %s, uscite %s, frane %s, cartelli %s' % (pos, usc, co, bg), 'ok' if r_ else 'DIVERSI')
    ok &= r_
print('TUTTO OK' if ok else 'DIFFERENZE')
