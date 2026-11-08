"""Bozza Lotto 4: interno della casa del protagonista (1.0 pianterreno, 1.1 camera), stesse misure di oggi
(14x10 e 12x9: i vecchi salvataggi fatti in casa restano dentro la mappa).

Pezzi: la casa del protagonista di Smeraldo (layout di 1.2 e 1.3, che nessuna mappa usa piu'), primario degli
interni 0x55ea40 e il suo secondario 0x55ecb0. Le scale passano a sinistra, come in Smeraldo, in tutti e due i piani.
Uso: python3 bozze/casa_protagonista.py ROM_069 CARTELLA
"""
import sys, struct
from pathlib import Path
sys.path[:0] = [str(Path(__file__).resolve().parent.parent / 'strumenti_rom')]
import tela, romlib
from PIL import Image, ImageDraw

PRIM, SEC = 0x55ea40, 0x55ecb0
L12, L13 = 0x5a9dd0, 0x5a9e80             # layout di 1.2 (11x9) e 1.3 (9x8)
L57 = 0x5aa198                            # casa generica 5.7 (piante in vaso)
L66 = 0x5ab8ec                            # casa generica 6.6 (libreria, 10-11, 0-2)


def pianterreno(d):
    T = tela.Tela(d, 14, 10, SEC, 0x3201)
    a, _ = tela.Tela.layout(d, L12)
    v = lambda x, y: int(a[y, x])
    # parete: rientro con le scale (0-4), due finestre, vetrina, due finestre, lavello e fornelli, frigo
    cols = [0, 0, 1, 2, 3, 4, 5, 6, 7, 4, 5, 8, 9, 10]
    for x, c in enumerate(cols):
        for y in range(4): T.metti(x, y, SEC, v(c, y))
        for y in range(4, 10): T.metti(x, y, SEC, v(0 if x == 0 else 1, 4))
    T.metti(1, 3, SEC, v(2, 4))
    # soggiorno di Smeraldo (TV, mobile, tappeto con tavolo e sedie) a sinistra; zerbino alla porta (9-10, 9)
    T.incolla(L12, 4, 4, 6, 5, 1, 4)
    T.metti(9, 9, SEC, v(1, 8)); T.metti(10, 9, SEC, v(2, 8))
    # due piante in vaso ai lati dell'ingresso
    T.incolla(L57, 10, 6, 1, 2, 13, 7); T.incolla(L57, 10, 6, 1, 2, 7, 7)
    return T


def camera(d):
    T = tela.Tela(d, 12, 9, SEC, 0x3201)
    a, _ = tela.Tela.layout(d, L13)
    v = lambda x, y: int(a[y, x])
    T.incolla(L13, 0, 0, 9, 8, 0, 0)
    for x in range(9, 12):
        T.metti(x, 0, SEC, 0x1000 | 0x254); T.metti(x, 1, SEC, 0x1000 | 0x25c); T.metti(x, 2, SEC, v(3, 2))
        for y in range(3, 9): T.metti(x, y, SEC, v(5, 3))
    for x in range(9): T.metti(x, 8, SEC, v(x, 7))
    # libreria al muro (come nella camera di oggi) e una pianta nell'angolo
    T.incolla(L66, 10, 0, 2, 3, 10, 0)
    T.incolla(L57, 10, 6, 1, 2, 11, 7)
    return T


def immagine(d, T, eventi, scala=3):
    U = tela.Unione(d, PRIM); val = T.valori(U)
    im = tela.anteprima(d, U, val, T.w, T.h, 1).convert('RGB')
    im = im.resize((im.width * scala, im.height * scala), Image.NEAREST); dr = ImageDraw.Draw(im)
    for nome, (x, y), col in eventi:
        q = 16 * scala
        dr.rectangle((x * q, y * q, x * q + q - 1, y * q + q - 1), outline=col, width=3)
        dr.text((x * q + 4, y * q + 4), nome, fill=col)
    return U, val, im


EVENTI_PT = [('porta', (9, 9), '#0ff'), ('porta', (10, 9), '#0ff'), ('scale', (3, 2), '#0ff'), ('mamma', (11, 3), '#ff0')]
EVENTI_CAM = [('scale', (1, 1), '#0ff'), ('PC', (7, 1), '#0f0'), ('PC', (8, 1), '#0f0')]

if __name__ == '__main__':
    d = open(sys.argv[1], 'rb').read(); out = Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
    R = romlib.Rom(d)
    for k, f in [((1, 0), 'casa_pt_prima.png'), ((1, 1), 'casa_camera_prima.png')]:
        R.render(R.map(*k), events=True, scale=3).save(out / f)
    for T, ev, f in [(pianterreno(d), EVENTI_PT, 'casa_pt_dopo.png'), (camera(d), EVENTI_CAM, 'casa_camera_dopo.png')]:
        U, val, im = immagine(d, T, ev); im.save(out / f); print(f, U.stato())
