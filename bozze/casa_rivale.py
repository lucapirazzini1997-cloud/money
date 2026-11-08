"""Bozza Lotto 4: casa del rivale ALDO a Lido di Savio, esterno (0.9) e interno (34.40 pianterreno, 34.41 camera).

Esterno: al posto della casa azzurra (23-26, 12-15) la casa dal tetto rosso di Petalburgo (layout 1, x 19-22,
y 21-24: solo metatile del primario, niente tile nuovi) in (24-27, 12-15): la porta resta in (25,15). A sinistra un
orto romagnolo (2x3) con i fiori davanti; i due alberi passano sulla colonna 28.
Interno, stesse misure di oggi (14x11 e 12x10), primario degli interni 0x55ea40 e secondario delle case generiche
di Smeraldo 0x55ed28 (layout 313 e 314, una casa su due piani con le scale in (2,1)):
  - pianterreno: scale (2,1), cucina e tavolo sul tappeto; appunti di ALDO appesi al muro (disegnati a mano);
    l'uscita resta in (7,10), la mamma resta in (3,3);
  - camera: scale (2,1), letto sul tappeto, libreria e mobiletto con il diario (11,2); al posto del tavolo il
    tappeto d'allenamento con le impronte dei passi (disegnato a mano), accanto al personaggio in (5,6).
Uso: python3 bozze/casa_rivale.py ROM_071 CARTELLA
"""
import sys, struct
from pathlib import Path
sys.path[:0] = [str(Path(__file__).resolve().parent.parent / 'strumenti_rom')]
import numpy as np
import tela, romlib

PRIM_I, SEC_G = 0x55ea40, 0x55ed28
L313, L314 = 313, 314
LIDO = (0, 9)
P_MARE, P_RUGGINE = 5, 1


def lay(d, lid): return struct.unpack_from('<I', d, 0x627fc0 + (lid - 1) * 4)[0] - 0x8000000


# ------------------------------------------------------------------ pezzi disegnati a mano
def _raw(t8):
    t = np.asarray(t8, np.uint8).reshape(64)
    return bytes(int(t[i]) | (int(t[i + 1]) << 4) for i in range(0, 64, 2))


def con_sopra(U, tp, mt, alto16, pal):
    """Il metatile mt della fonte tp con lo strato alto nuovo (16x16 indici della palette pal, 0 = trasparente)."""
    base = U.metatile(tp, mt); refs = list(U.meta[base - 512][0]) if base >= 512 else list(U.prim.refs(base))
    alto = np.asarray(alto16)
    for q in range(4):
        t = alto[(q // 2) * 8:(q // 2) * 8 + 8, (q % 2) * 8:(q % 2) * 8 + 8]
        refs[4 + q] = (U._tile(_raw(t)) | (pal << 12)) if t.any() else 0
    attr = U.prim.attr(mt) if mt < 512 else U.fonte(tp).attr(mt)
    return U.metatile_nuovo(refs, attr)


def appunti(U, tp, mt, k):
    """Fogli di appunti appesi al muro (palette 1: bianco 4, scuro 1, ruggine 9)."""
    a = np.zeros((16, 16), int)
    fogli = [(2, 1, 7, 9), (9, 3, 14, 12)] if k == 0 else [(1, 2, 7, 11), (9, 1, 14, 8)]
    for x0, y0, x1, y1 in fogli:
        a[y0:y1 + 1, x0:x1 + 1] = 4
        a[y0, x0:x1 + 1] = 1; a[y1, x0:x1 + 1] = 1; a[y0:y1 + 1, x0] = 1; a[y0:y1 + 1, x1] = 1
        for y in range(y0 + 2, y1 - 1, 2): a[y, x0 + 2:x1 - 1] = 1          # righe scritte
        a[y0, (x0 + x1) // 2] = 9                                          # puntina
    return con_sopra(U, tp, mt, a, P_RUGGINE)


PIEDE = ["01110", "11111", "11111", "11111", "11111", "01110", "00000", "01110", "01110", "00100"]


def tappeto_passi(U, tp, mt, X, Y, W, H):
    """Tappeto d'allenamento azzurro (palette 5: 3 azzurro, 4 blu, 1 bianco) con le impronte dei passi.
    (X,Y) e' la casella dentro il tappeto WxH."""
    big = np.zeros((H * 16, W * 16), int)
    big[:, :] = 3
    big[0, :] = big[-1, :] = 4; big[:, 0] = big[:, -1] = 4
    big[2, 2:-2] = big[-3, 2:-2] = 1; big[2:-2, 2] = big[2:-2, -3] = 1
    # impronte: un percorso a zig-zag da sinistra a destra (schivare e avvicinarsi)
    passi = [(6, 14), (16, 6), (28, 16), (38, 6), (50, 15)]
    for i, (px, py) in enumerate(passi):
        for j, riga in enumerate(PIEDE):
            for ii, c in enumerate(riga):
                if c == '1':
                    yy, xx = py + j, px + ii + (5 if i % 2 else 0)
                    if 0 <= yy < H * 16 and 0 <= xx < W * 16: big[yy, xx] = 4
    return con_sopra(U, tp, mt, big[Y * 16:Y * 16 + 16, X * 16:X * 16 + 16], P_MARE)


class UnioneRivale(tela.Unione):
    def __init__(self, d, prim):
        super().__init__(d, prim); self.nuovi = {}

    def metatile(self, tp, mt):
        if isinstance(tp, tuple):
            if tp not in self.nuovi: self.nuovi[tp] = tp[1](self, *tp[2:])
            return self.nuovi[tp]
        return super().metatile(tp, mt)


def metti_nuovo(T, x, y, fn, *args):
    src, v = T.c[y][x]
    T.c[y][x] = (('N', fn, src, v & 1023) + args, v & 0xfc00)


# ------------------------------------------------------------------ interno
def pianterreno(d):
    T = tela.Tela(d, 14, 11, SEC_G, 0)
    L = lay(d, L313); a, _ = tela.Tela.layout(d, L)
    pav, bordo = int(a[3, 2]), int(a[3, 0])               # pavimento e colonna di sinistra in ombra
    T.incolla(L, 0, 0, 14, 6, 0, 0)                        # muro, scale, cucina, tavolini, tappeto
    for y in (6, 7, 8, 9):
        for x in range(14): T.c[y][x] = (SEC_G, bordo if x == 0 else pav)
    T.incolla(L, 8, 6, 6, 1, 8, 6)                         # bordo basso del tappeto
    T.incolla(L, 0, 6, 2, 1, 0, 9)                         # piante (parte alta)
    T.incolla(L, 0, 7, 14, 1, 0, 10)                       # piante, zerbino (uscita in 7,10)
    T.incolla(L, 0, 6, 2, 2, 12, 9)                        # altre due piante a destra
    metti_nuovo(T, 6, 1, appunti, 0); metti_nuovo(T, 7, 1, appunti, 1)
    return T


def camera(d):
    T = tela.Tela(d, 12, 10, SEC_G, 0)
    L = lay(d, L314); a, _ = tela.Tela.layout(d, L)
    pav, bordo = int(a[3, 2]), int(a[3, 0])
    T.incolla(L, 0, 0, 12, 8, 0, 0)
    for y in (8, 9):
        for x in range(12): T.c[y][x] = (SEC_G, bordo if x == 0 else pav)
    for y in range(4, 8):                                  # via il tavolo, le sedie e le piante di sinistra
        for x in range(1, 7): T.c[y][x] = (SEC_G, pav)
    T.incolla(lay(d, 96), 0, 0, 3, 3, 9, 0)               # libreria e mobiletto (casa 96) al posto del divano
    for y in range(4, 6):                                  # tappeto d'allenamento con le impronte (1-4, 4-5)
        for x in range(1, 5): metti_nuovo(T, x, y, tappeto_passi, x - 1, y - 4, 4, 2)
    T.incolla(L, 1, 6, 1, 2, 11, 8)                        # una pianta nell'angolo
    return T


# ------------------------------------------------------------------ esterno
def lido(d):
    rom = romlib.Rom(bytes(d)); m = rom.map(*LIDO); a = rom.blocks(m)
    erba = int(a[10, 23])
    a[10:18, 22:29] = erba
    p, _ = tela.Tela.layout(d, lay(d, 1))
    alto = erba & 0xf000
    for j in range(4):
        for i in range(4): a[12 + j, 24 + i] = alto | (int(p[21 + j, 19 + i]) & 0x0fff)
    orto, fiore = int(p[22, 23]), int(p[24, 23])
    for y in (12, 13, 14):
        for x in (22, 23): a[y, x] = alto | (orto & 0x0fff)
    for x in (22, 23): a[15, x] = alto | (fiore & 0x0fff)
    alb_su, alb_giu = int(rom.blocks(m)[11, 27]), int(rom.blocks(m)[12, 27])
    for y in (11, 15): a[y, 28], a[y + 1, 28] = alb_su, alb_giu
    return m, a


def lido_variante_a(d):
    """Variante: la casa azzurra resta; orto a destra (27-28, 12-14) con i fiori, alberi a sinistra."""
    rom = romlib.Rom(bytes(d)); m = rom.map(*LIDO); a = rom.blocks(m); b = rom.blocks(m)
    erba = int(a[10, 23]); alto = erba & 0xf000
    p, _ = tela.Tela.layout(d, lay(d, 1)); orto, fiore = int(p[22, 23]), int(p[24, 23])
    for y in range(10, 18):
        for x in (22, 27, 28): a[y, x] = erba
    for y in (12, 13, 14):
        for x in (27, 28): a[y, x] = alto | (orto & 0x0fff)
    for x in (27, 28): a[15, x] = alto | (fiore & 0x0fff)
    for y in (11, 15): a[y, 22], a[y + 1, 22] = int(b[11, 27]), int(b[12, 27])
    return m, a


if __name__ == '__main__':
    import sprite
    from PIL import Image, ImageDraw
    d = open(sys.argv[1], 'rb').read(); out = Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
    rom = romlib.Rom(bytes(d))
    for nome, T, k in (('pianterreno', pianterreno(d), (34, 40)), ('camera', camera(d), (34, 41))):
        U = UnioneRivale(d, PRIM_I); v = T.valori(U)
        im = tela.anteprima(d, U, v, T.w, T.h, 1)
        m = rom.map(*k)
        sprite.disegna(d, im, [(o['x'], o['y'], o['gfx']) for o in m['objects']], 1)
        im = im.resize((im.width * 3, im.height * 3), 0); im.save(out / ('rivale_%s.png' % nome))
        print(nome, U.stato())
    for nome, fn in (('rivale_esterno', lido), ('rivale_esterno_a', lido_variante_a)):
        m, a = fn(d)
        r2 = romlib.Rom(bytes(d)); dd = r2.data           # anteprima con il tileset di oggi
        struct.pack_into('<%dH' % a.size, dd, m['blocks'], *[int(x) for x in a.flat])
        im = r2.render(r2.map(*LIDO), events=False, scale=1)
        sprite.disegna(bytes(dd), im, [(o['x'], o['y'], o['gfx']) for o in m['objects']], 1)
        im.crop((17 * 16, 8 * 16, 31 * 16, 21 * 16)).resize((14 * 48, 13 * 48), 0).save(out / (nome + '.png'))
    rv = romlib.Rom(bytes(d)).render(romlib.Rom(bytes(d)).map(*LIDO), events=False, scale=1)
    rv.crop((17 * 16, 8 * 16, 31 * 16, 21 * 16)).resize((14 * 48, 13 * 48), 0).save(out / 'rivale_esterno_prima.png')
