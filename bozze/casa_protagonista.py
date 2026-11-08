"""Bozza Lotto 4: interno della casa del protagonista (1.0 pianterreno, 1.1 camera), stesse misure di oggi
(14x10 e 12x9: i vecchi salvataggi fatti in casa restano dentro la mappa).

Romagna e mare (pezzi disegnati a mano nello strato alto, palette del primario): finestre con la vista sul mare,
tovaglia romagnola stampata a ruggine, salvagente al muro della camera, telo da mare a righe al posto del tappeto.
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


# ------------------------------------------------------------------ pezzi disegnati a mano (Romagna, mare)
# Si disegnano nello strato alto dei metatile, con le palette del primario degli interni (sempre caricate,
# non occupano posti del secondario): palette 5 = cielo, mare, sabbia; palette 1 = ruggine, bianco, salmone.
import numpy as np
P_MARE, P_RUGGINE = 5, 1


def _pal(d, ts, k):
    pp = struct.unpack_from('<I', d, ts + 8)[0] - 0x8000000
    v = struct.unpack_from('<16H', d, pp + 32 * k)
    return np.array([[(c & 31) * 8, ((c >> 5) & 31) * 8, ((c >> 10) & 31) * 8] for c in v])


def _tile_px(src_raw, idx):
    raw = src_raw[(idx - 512) * 32:(idx - 512) * 32 + 32]
    a = np.frombuffer(bytes(raw), np.uint8); px = np.empty(64, np.uint8); px[::2] = a & 15; px[1::2] = a >> 4
    return px.reshape(8, 8)


def strato_basso_rgb(U, mt):
    """16x16 RGB dello strato basso del metatile mt del secondario SEC."""
    f = U.fonte(SEC); refs = f.refs(mt); out = np.zeros((16, 16, 3), int)
    for q in range(4):
        r = refs[q]; t = _tile_px(f.raw, r & 1023)
        if r & 0x400: t = t[:, ::-1]
        if r & 0x800: t = t[::-1, :]
        out[(q // 2) * 8:(q // 2) * 8 + 8, (q % 2) * 8:(q % 2) * 8 + 8] = _pal(U.d, SEC, r >> 12)[t]
    return out


def _raw(t8):
    t = np.asarray(t8, np.uint8).reshape(64)
    return bytes(int(t[i]) | (int(t[i + 1]) << 4) for i in range(0, 64, 2))


def con_sopra(U, mt, alto16, pal):
    """Il metatile mt (strato basso com'e') con lo strato alto nuovo: alto16 = 16x16 indici della palette pal
    (0 = trasparente)."""
    base = U.metatile(SEC, mt); refs = list(U.meta[base - 512][0]) if base >= 512 else list(U.prim.refs(base))
    alto = np.asarray(alto16)
    for q in range(4):
        t = alto[(q // 2) * 8:(q // 2) * 8 + 8, (q % 2) * 8:(q % 2) * 8 + 8]
        refs[4 + q] = (U._tile(_raw(t)) | (pal << 12)) if t.any() else 0
    return U.metatile_nuovo(refs, U.fonte(SEC).attr(mt))


def vetro(rgb):
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    return (b > r + 30) & (b > 120)


def vista_mare(U, mt, riga0, vela=False):
    """Finestra (strato basso mt) con il mare dietro il vetro. riga0: riga del vetro da cui parte il metatile
    (0 per la parte alta della finestra, 16 per la bassa): l'orizzonte e' a meta' della finestra."""
    rgb = strato_basso_rgb(U, mt); m = vetro(rgb); alto = np.zeros((16, 16), int)
    ys = [y + riga0 for y in range(16) if m[y].any()]
    for y in range(16):
        for x in range(16):
            if not m[y, x]: continue
            Y = y + riga0
            if Y < 12: c = 9                                     # cielo
            elif Y < 15: c = 3                                   # foschia
            elif Y == 15: c = 4                                  # orizzonte
            else: c = 1 if ((x + Y) % 7 == 0 and Y > 17) else 10  # mare con le onde
            alto[y, x] = c
    if vela:                                                     # una vela bianca sull'orizzonte
        for y, x0, x1 in [(12 - riga0, 7, 8), (13 - riga0, 6, 8), (14 - riga0, 5, 8)]:
            if 0 <= y < 16:
                for x in range(x0, x1 + 1):
                    if m[y, x]: alto[y, x] = 1
    return con_sopra(U, mt, alto, P_MARE)


def tovaglia(U, mt):
    """Il tavolo (strato alto, palette 9 del secondario) con la tovaglia romagnola stampata a ruggine."""
    f = U.fonte(SEC); refs = list(f.refs(mt)); pal9 = _pal(U.d, SEC, 9)
    base = U.metatile(SEC, mt); nuovi = list(U.meta[base - 512][0])
    for q in range(4):
        r = refs[4 + q]; t = _tile_px(f.raw, r & 1023)
        rgb = pal9[t]; lum = rgb.sum(-1); out = np.zeros((8, 8), int)
        X0, Y0 = (q % 2) * 8, (q // 2) * 8
        for y in range(8):
            for x in range(8):
                if t[y, x] == 0: continue
                X = X0 + (7 - x if r & 0x400 else x); Y = Y0 + y
                if lum[y, x] > 560:                              # piano chiaro del tavolo -> tela con il motivo
                    out[y, x] = 9 if ((X + Y) % 6 == 0 or (X - Y) % 6 == 0) and 2 < Y < 13 else 4
                elif lum[y, x] > 380: out[y, x] = 10             # bordo -> ruggine chiaro
                else: out[y, x] = 1                              # contorni e gambe
        nuovi[4 + q] = (U._tile(_raw(out)) | (P_RUGGINE << 12) | (r & 0x0c00))
    return U.metatile_nuovo(nuovi, f.attr(mt))


def salvagente(U, mt):
    """Salvagente bianco e rosso appeso al muro (strato alto, palette 1)."""
    alto = np.zeros((16, 16), int); c = 7.5
    for y in range(16):
        for x in range(16):
            r = ((x - c) ** 2 + (y - c - 0.5) ** 2) ** 0.5
            if 3.2 <= r <= 7.2:
                if r > 6.4 or r < 3.9: alto[y, x] = 1
                else:
                    ang = np.degrees(np.arctan2(y - c - 0.5, x - c)) % 360
                    alto[y, x] = 10 if int(ang // 45) % 2 == 0 else 4
    return con_sopra(U, mt, alto, P_RUGGINE)


def telo(U, mt, riga0):
    """Il tappeto rosa diventa un telo da mare a righe bianche e blu (solo sul rosa pieno)."""
    rgb = strato_basso_rgb(U, mt); rosa = (rgb[..., 0] > 150) & (rgb[..., 1] < 150) & (rgb[..., 2] > 100)
    alto = np.zeros((16, 16), int)
    for y in range(16):
        for x in range(16):
            if rosa[y, x]: alto[y, x] = 10 if ((y + riga0) // 4) % 2 == 0 else 1
    return con_sopra(U, mt, alto, P_MARE)


class UnioneRomagna(tela.Unione):
    """Unione che capisce anche le caselle ('N', nome, argomenti) dei pezzi disegnati a mano."""
    def __init__(self, d):
        super().__init__(d, PRIM); self.nuovi = {}

    def metatile(self, tp, mt):
        if isinstance(tp, tuple):
            if tp not in self.nuovi: self.nuovi[tp] = tp[1](self, *tp[2:])
            return self.nuovi[tp]
        return super().metatile(tp, mt)


def metti_nuovo(T, x, y, fn, *args):
    vecchio = T.c[y][x][1]
    T.c[y][x] = (('N', fn) + args, vecchio & 0xfc00)


def romagna_pianterreno(T):
    metti_nuovo(T, 12, 0, vista_mare, 0x21e, 0, False)
    for x in (5, 6, 9, 10):                                     # finestre con vista sul mare
        metti_nuovo(T, x, 0, vista_mare, 0x21e, 0, x == 6)
        metti_nuovo(T, x, 1, vista_mare, 0x226, 16, x == 6)
    for (x, y), mt in {(3, 6): 0x2b9, (4, 6): 0x2ba, (3, 7): 0x2c1, (4, 7): 0x2c2}.items():
        metti_nuovo(T, x, y, tovaglia, mt)
    return T


def romagna_camera(T):
    metti_nuovo(T, 9, 1, salvagente, 0x25c)
    for y in range(3, 7):
        for x in range(1, 5):
            mt = T.c[y][x][1] & 1023
            metti_nuovo(T, x, y, telo, mt, (y - 3) * 16)
    return T


def immagine(d, T, eventi, scala=3):
    U = UnioneRomagna(d); val = T.valori(U)
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
    for T, ev, f in [(romagna_pianterreno(pianterreno(d)), EVENTI_PT, 'casa_pt_dopo.png'), (romagna_camera(camera(d)), EVENTI_CAM, 'casa_camera_dopo.png')]:
        U, val, im = immagine(d, T, ev); im.save(out / f); print(f, U.stato())
