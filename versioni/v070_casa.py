"""Versione 0.70 - Lotto 4: interno della casa del protagonista (1.0 pianterreno, 1.1 camera).

Disegno della bozza approvata (bozze/casa_protagonista.py, "Va bene cosi'"), copiato qui e congelato:
  - pezzi della casa del protagonista di Smeraldo (layout di 1.2 e 1.3, non usati), primario degli interni 0x55ea40;
  - due piante e una libreria da case generiche di Smeraldo (5.7 e 6.6);
  - Romagna e mare, disegnati a mano nello strato alto con le palette del primario: finestre sul mare, tovaglia
    romagnola stampata a ruggine, salvagente in camera, telo da mare a righe.
Misure invariate (14x10 e 12x9): i salvataggi fatti in casa restano dentro la mappa. Il layout nuovo prende il
posto del vecchio nella tabella dei layout (id 633 e 55, solo di queste mappe): Continua lo carica da li'.
Eventi: scale del pianterreno (12,2) -> (3,2), della camera (10,2) -> (1,1); la mamma (4,3) -> (11,3), davanti
alla cucina; il PC della camera (4,3),(5,3) -> (8,1), sulla scrivania: e' il metatile 0x27E del PC di Smeraldo, con
lo stesso id nel secondario nuovo (il gioco lo accende con 0x27F e lo spegne con 0x27E).
Le due TV hanno un evento con un testo italiano (prima del comportamento TV di Smeraldo, che in camera dava
"MOM might like this program..." in inglese e al pianterreno niente). La frase della cartina (comportamento 0x85,
apre la cartina della ROMAGNA) "took a closer look at the HOENN region map." e' tradotta sul posto.
Il bordo fuori dalla mappa e' un metatile nero nuovo (il metatile 0 del primario si vedeva rosa).
Niente flag e niente variabili nuove.
"""
import struct, sys
from pathlib import Path
import numpy as np
import engine as E
from engine import B, Script
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'strumenti_rom'))
import tela

PT, CAMERA = (1, 0), (1, 1)
OUT = {}

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
    T.metti(8, 1, SEC, 0x400 | 0x27e)                           # il PC di casa di Smeraldo (spento)
    return T


# ------------------------------------------------------------------ pezzi disegnati a mano (Romagna, mare)
# Si disegnano nello strato alto dei metatile, con le palette del primario degli interni (sempre caricate,
# non occupano posti del secondario): palette 5 = cielo, mare, sabbia; palette 1 = ruggine, bianco, salmone.
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


PC_SPENTO, PC_ACCESO = 0x27e, 0x27f      # Smeraldo accende e spegne il PC di casa scrivendo questi id fissi


def fissa(U, vals, posti):
    """Mette i metatile del secondario sorgente agli id che il gioco scrive da solo ({id: metatile sorgente})."""
    for src in posti.values(): U.metatile(SEC, src)
    while len(U.meta) <= max(posti) - 512: U.meta.append(U.meta[0])
    for dst, src in posti.items():
        cur = U.metatile(SEC, src)
        if cur == dst: continue
        a, b = cur - 512, dst - 512
        U.meta[a], U.meta[b] = U.meta[b], U.meta[a]
        for k, v in list(U.meta_idx.items()):
            if v == cur: U.meta_idx[k] = dst
            elif v == dst: U.meta_idx[k] = cur
        for i, v in enumerate(vals):
            if v & 1023 == cur: vals[i] = (v & 0xfc00) | dst
            elif v & 1023 == dst: vals[i] = (v & 0xfc00) | cur


def _scrivi(W, chiave, T, nome, lid, posti=None):
    d = W.d; m = W.rom.map(*chiave)
    assert m['layout_id'] == lid and (m['width'], m['height']) == (T.w, T.h), (chiave, m['layout_id'])
    U = UnioneRomagna(bytes(d)); vals = T.valori(U)
    if posti: fissa(U, vals, posti)
    nero_t = U._tile(bytes([0xff] * 32))                              # tile tutto colore 15 = nero (palette 5)
    nero = 0x400 | U.metatile_nuovo([nero_t | (P_MARE << 12)] * 4 + [0] * 4, 0)
    tp = U.scrivi(W, nome)
    lp = W.set_layout(*chiave, vals, T.w, T.h, (nero,) * 4, PRIM, tp)
    blob_attr = U.blob()[3]
    def beh(x, y):
        k = vals[y * T.w + x] & 1023
        return (U.prim.attr(k) if k < 512 else struct.unpack_from('<H', blob_attr, (k - 512) * 2)[0]) & 0xff
    OUT[nome] = dict(layout=hex(lp), tileset=hex(tp), **U.stato())
    return vals, beh


def apply(W):
    import romlib
    tutte = [k for k in romlib.all_maps(W.rom)]
    def condivisi(lid):
        n = 0
        for k in tutte:
            try: n += W.rom.map(*k)['layout_id'] == lid
            except Exception: pass
        return n
    assert condivisi(633) == 1 and condivisi(55) == 1
    m0, m1 = W.rom.map(*PT), W.rom.map(*CAMERA)
    assert [(w['x'], w['y'], w['group'], w['num'], w['warp']) for w in m0['warps']] == [(10, 9, 0, 9, 1), (9, 9, 0, 9, 1), (12, 2, 1, 1, 0)]
    assert [(w['x'], w['y'], w['group'], w['num'], w['warp']) for w in m1['warps']] == [(10, 2, 1, 0, 2)]
    assert [(o['x'], o['y'], o['gfx']) for o in m0['objects']] == [(4, 3, 215)]
    assert [(b['x'], b['y']) for b in m1['bgs']] == [(4, 3), (5, 3)]
    assert m0['coords'] == [] and m1['coords'] == []

    v0, beh0 = _scrivi(W, PT, romagna_pianterreno(pianterreno(bytes(W.d))), 'casa pianterreno (0.70)', 633)
    v1, beh1 = _scrivi(W, CAMERA, romagna_camera(camera(bytes(W.d))), 'casa camera (0.70)', 55,
                       {PC_SPENTO: PC_SPENTO, PC_ACCESO: PC_ACCESO})
    assert v1[1 * 12 + 8] & 1023 == PC_SPENTO
    assert beh0(9, 9) == beh0(10, 9) == 0x65 and beh0(3, 2) == 0x60 and beh1(1, 1) == 0x60, (beh0(9, 9), beh0(3, 2), beh1(1, 1))
    # caselle libere dove si arriva e dove si sta: arrivo dalle scale, mamma, davanti al PC
    libera = lambda vals, w, x, y: (vals[y * w + x] >> 10) & 3 == 0
    assert libera(v0, 14, 3, 3) and libera(v0, 14, 11, 3) and libera(v0, 14, 9, 8) and libera(v1, 12, 1, 2)
    assert libera(v1, 12, 8, 2)

    def tv(t):
        return dict(elev=0, kind=0, arg=B + Script('casa: TV (0.70)').emit(b'\x69').msg(t).end().save())
    tv_pt = tv("In TV c'è il meteo del mare: ADRIATICO calmo e bandiera bianca. Si può fare il bagno!")
    tv_cam = tv("Danno un documentario sulle SALINE di CERVIA e sui loro fenicotteri.")
    ws = [dict(w) for w in m0['warps']]; ws[2].update(x=3, y=2)
    ob = [dict(o) for o in m0['objects']]; ob[0].update(x=11, y=3)
    W.set_events(*PT, objects=ob, warps=ws, bgs=[dict(tv_pt, x=3, y=4)])
    ws = [dict(w) for w in m1['warps']]; ws[0].update(x=1, y=1)
    bg = [dict(m1['bgs'][0], x=8, y=1)]                 # il PC: una casella sola (l'effetto accende la casella guardata)
    W.set_events(*CAMERA, warps=ws, bgs=bg + [dict(tv_cam, x=4, y=1)])
    # frase della cartina (comportamento 0x85), sul posto
    d = W.d; vecchia = 0x1f8c68
    vecchio = b'\xfd\x01' + W.enc(' took a closer look at the') + b'\xfe' + W.enc('HOENN region map.') + b'\xff'
    assert bytes(d[vecchia:vecchia + len(vecchio)]) == vecchio
    nuovo = b'\xfd\x01' + W.enc(' guarda la cartina') + b'\xfe' + W.enc('della ROMAGNA.') + b'\xff'
    d[vecchia:vecchia + len(vecchio)] = nuovo.ljust(len(vecchio), b'\xff')
    OUT['testi'] = dict(cartina=hex(vecchia), tv=[hex(tv_pt['arg'] - B), hex(tv_cam['arg'] - B)])
    OUT['eventi'] = dict(scale_pianterreno=(3, 2), scale_camera=(1, 1), mamma=(11, 3), pc=(8, 1))
    return OUT
