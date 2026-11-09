"""Versione 0.72 - Lotto 4: Lido di Savio piu' simile al paese vero, casa di ALDO, chiesa aperta.

Disegno delle bozze approvate, copiato qui e congelato:
  - bozze/lido.py (bozza 3, "Cosi' vanno bene"): foce del Savio con i capanni da pesca e due pontili; argine con il
    muretto bianco sulla riva sud e prato pulito sulla riva nord; Viale Romagna con alberi, lampioni, bancarella e
    cartello; piu' pini (boschetto a sinistra del laboratorio); spiaggia con BAGNO LIDO, BAGNO MILANO e BAGNO 340
    (cabine, ombrelloni in fila, cartelli); caselli PINETA e COSTIERO ripuliti (via lo striscione sul tetto) con un
    cartello a lato; negozi con il nome: BAZAR DEL LIDO, GELATERIA PURO & BIO, PIANETA PIADA;
  - bozze/casa_rivale.py: esterno A (la casa azzurra resta, orto a destra) e interno ("Va bene cosi'"): pianterreno
    dalla casa 313 di Smeraldo con gli appunti di ALDO al muro, camera dalla 314 con il tappeto d'allenamento;
  - bozze/chiesa_lido.py (bozza 2): la porta della chiesa (8,38) si apre sulla mappa libera 24.75 (una mappa di
    Ruby rimasta in Smeraldo, che nessuna uscita raggiungeva): navata con i pezzi della chiesa di Cesena, pavimento di
    pietra chiara e tappeto blu (colori cambiati nella sua copia delle palette), quadro con la barca a vela.
    Evento: il PARROCO regala una volta un MAREAROMA (flag nuova dal pool).
Misure invariate (Lido 56x44, casa di ALDO 14x11 e 12x10): i vecchi salvataggi restano dentro le mappe.
"""
import struct, sys
from pathlib import Path
import numpy as np
import engine as E
from engine import B, P, Script
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'strumenti_rom'))
import tela, romlib

OUT = {}
LIDO, PT_R, CAM_R, CHIESA, CESENA_CHIESA = (0, 9), (34, 40), (34, 41), (24, 75), (34, 37)
PRIM_G, PRIM_I, SEC_G, SEC_C = 0x55e8c0, 0x55ea40, 0x55ed28, 0x18d89e4
MAREAROMA = 0xdc


def lay(d, lid): return struct.unpack_from('<I', d, E.W.table + (lid - 1) * 4)[0] - B


def _raw(t8):
    t = np.asarray(t8, np.uint8).reshape(64)
    return bytes(int(t[i]) | (int(t[i + 1]) << 4) for i in range(0, 64, 2))


def cartello(nome, testo):
    s = Script(nome); s.emit(b'\x0f\x00' + P(E.W.text(testo)) + b'\x09\x03\x02'); return s.save()


# ================================================================== Lido di Savio (da bozze/lido.py, bozza 3)
PINO = (0, 8, 2, 2)
ALBERO = (38, 33, 1, 2)
LAMPIONE = (39, 33, 1, 2)
OMBRELLONE = (45, 27, 1, 2)
CABINA_R, CABINA_A, CABINA_V = (42, 21, 1, 2), (42, 30, 1, 2), (42, 36, 1, 2)
CAPANNO = (9, 0, 3, 3)
PONTILE = (35, 5, 2, 2)
BANCARELLA = (26, 22, 2, 2)
CARTELLO = (38, 36, 1, 1)


class Mappa:
    def __init__(self, rom):
        self.m = rom.map(*LIDO)
        self.orig = rom.blocks(self.m); self.a = self.orig.copy()
        self.erba = int(self.orig[10, 23]); self.sabbia = int(self.orig[25, 45])
        self.cartelli = []

    def timbro(self, t, x, y):
        sx, sy, w, h = t
        self.a[y:y + h, x:x + w] = self.orig[sy:sy + h, sx:sx + w]

    def riempi(self, x, y, w, h, v): self.a[y:y + h, x:x + w] = v

    def cartello(self, x, y, testo):
        self.timbro(CARTELLO, x, y); self.cartelli.append((x, y, testo))


def lido_disegno(d, rom):
    M = Mappa(rom); o = M.orig
    # foce del Savio
    for x in (33, 37):
        M.riempi(x, 0, 3, 3, M.erba); M.timbro(CAPANNO, x, 0)
    M.riempi(28, 0, 3, 3, M.erba)
    for x in (44, 48): M.timbro(PONTILE, x, 5)
    M.cartello(41, 2, "FOCE DEL SAVIO\nI capanni da pesca calano le reti quando sale la marea.")
    # argine
    for x in range(56):
        if (int(o[2, x]) & 1023) in {0x20f, 0x210, 0x211, 0x212}: M.a[2, x] = M.erba
    M.a[2, 16] = M.erba
    for x in range(42):
        if x in (19, 20, 35, 36, 22): continue
        M.a[7, x] = 0x3000 | 0x0400 | 0x3e
    for x in (19, 20, 35, 36): M.a[7, x] = int(o[7, 17])
    # caselli ripuliti
    M.a[40, 17:22] = o[40, 12]
    M.a[41:44, 14:16] = M.erba; M.a[41:44, 23:25] = M.erba
    M.timbro(PINO, 12, 42)
    M.cartello(16, 41, "PINETA DEL SAVIO\nIl casello porta nella pineta, verso CERVIA.")
    M.cartello(44, 41, "SENTIERO COSTIERO\nIl casello porta lungo la spiaggia fino a CERVIA.")
    # Viale Romagna
    for y in (11, 15, 24, 33):
        for x in (17, 21):
            if (M.a[y:y + 2, x] == M.erba).all(): M.timbro(ALBERO, x, y)
    for y in (13, 26, 36):
        for x in (17, 21):
            if (M.a[y:y + 2, x] == M.erba).all(): M.timbro(LAMPIONE, x, y)
    M.timbro(BANCARELLA, 22, 26)
    M.cartello(17, 10, "VIALE ROMAGNA\nNegozi, gelati e alberghi fino alla PINETA.")
    # pini
    for x, y in [(1, 17), (4, 17), (9, 17), (12, 17), (31, 10), (31, 16), (31, 37), (36, 37), (26, 37),
                 (10, 37), (15, 22)]:
        if (M.a[y:y + 2, x:x + 2] == M.erba).all(): M.timbro(PINO, x, y)
    M.riempi(4, 22, 5, 7, M.erba)
    for x, y in [(4, 22), (7, 22), (4, 25), (6, 27)]: M.timbro(PINO, x, y)
    # casa di ALDO, esterno A: orto a destra (27-28, 12-14) con i fiori, alberi a sinistra
    p, _ = tela.Tela.layout(d, lay(d, 1)); orto, fiore = int(p[22, 23]), int(p[24, 23])
    alto = M.erba & 0xf000
    for y in range(10, 18):
        for x in (22, 27, 28): M.a[y, x] = M.erba
    for y in (12, 13, 14):
        for x in (27, 28): M.a[y, x] = alto | (orto & 0x0fff)
    for x in (27, 28): M.a[15, x] = alto | (fiore & 0x0fff)
    for y in (11, 15): M.a[y, 22], M.a[y + 1, 22] = int(o[11, 27]), int(o[12, 27])
    # spiaggia: tre bagni
    M.riempi(42, 21, 10, 20, M.sabbia)
    for y0, cab, nome in ((22, CABINA_R, 'BAGNO LIDO'), (28, CABINA_A, 'BAGNO MILANO'), (34, CABINA_V, 'BAGNO 340')):
        for y in (y0, y0 + 3): M.timbro(cab, 42, y)
        M.cartello(43, y0, "%s\nLettini e ombrelloni in fila, come in tutta la riviera." % nome)
        for y in (y0, y0 + 3):
            for x in (45, 47, 49): M.timbro(OMBRELLONE, x, y)
    for y in (22, 28, 34): M.a[y + 2, 42] = o[23, 42]
    M.a[31, 50:52] = o[31, 50:52]
    M.timbro((50, 22, 1, 2), 51, 21)
    for y in (24, 30, 36):
        if (M.a[y:y + 2, 39] == M.erba).all(): M.timbro(LAMPIONE, 39, y)
    M.porte = {(13, 35): "BAZAR DEL LIDO\nSecchielli, palette e salvagenti. Chiuso per la pausa pranzo.",
               (16, 35): "GELATERIA PURO & BIO\nGelato artigianale e biologico.",
               (33, 35): "PIANETA PIADA\nLa piastra è ancora fredda: apre stasera!"}
    return M


def lido(W):
    d = W.d; rom = W.rom
    m0 = rom.map(*LIDO)
    assert (m0['width'], m0['height']) == (56, 44) and len(m0['warps']) == 16
    assert [(w['x'], w['y'], w['group'], w['num']) for w in m0['warps'][7:15]] == \
        [(x, 43, 35, 81) for x in range(18, 22)] + [(x, 43, 35, 83) for x in range(46, 50)]
    M = lido_disegno(bytes(d), rom)
    # oggetti e Poke Ball non devono finire sotto un pezzo nuovo che non c'era
    for o in m0['objects']:
        x, y = o['x'], o['y']
        if 0 <= x < 56 and 0 <= y < 44 and M.a[y, x] != M.orig[y, x]:
            assert (int(M.a[y, x]) >> 10) & 3 == 0, ('oggetto su una casella bloccata', o['x'], o['y'])
    # porta della chiesa: copia del metatile con il comportamento porta (0x60) e senza collisione
    sec = m0['secondary']; St = tela.Tileset(bytes(d), sec)
    meta_t = bytearray(d[St.meta:St.meta + 512 * 16]); attr_t = bytearray(d[St.attrs:St.attrs + 512 * 2])
    usati = {int(v) & 1023 for v in M.a.flat} | {v & 1023 for v in struct.unpack_from('<4H', d, m0['border'])}
    liberi = [i for i in range(512, 1024) if i not in usati and not any(struct.unpack_from('<8H', meta_t, (i - 512) * 16))]
    porta_old = int(M.a[38, 8]); k_old = porta_old & 1023
    assert k_old >= 512 and struct.unpack_from('<H', attr_t, (k_old - 512) * 2)[0] & 0xff == 0
    nuovo = liberi[0]
    meta_t[(nuovo - 512) * 16:(nuovo - 512) * 16 + 16] = meta_t[(k_old - 512) * 16:(k_old - 512) * 16 + 16]
    a_old = struct.unpack_from('<H', attr_t, (k_old - 512) * 2)[0]
    struct.pack_into('<H', attr_t, (nuovo - 512) * 2, (a_old & 0xff00) | 0x60)
    M.a[38, 8] = (porta_old & 0xf000) | nuovo
    mp = W.alloc(bytes(meta_t), 'metatile Lido (0.72)'); ap = W.alloc(bytes(attr_t), 'attributi Lido (0.72)')
    ts = bytearray(d[sec:sec + 24]); struct.pack_into('<II', ts, 12, B + mp, B + ap)
    tsp = W.alloc(bytes(ts), 'tileset Lido con la porta della chiesa (0.72)')
    border = list(struct.unpack_from('<4H', d, m0['border']))
    lp = W.set_layout(*LIDO, [int(v) for v in M.a.flat], 56, 44, border, m0['primary'], tsp)
    # eventi
    ws = [dict(w) for w in m0['warps']]
    ws.append(dict(x=8, y=38, elev=0, warp=0, num=CHIESA[1], group=CHIESA[0]))
    bgs = [dict(b) for b in m0['bgs']]
    via = [(16, 2), (8, 38)]
    assert all(len([b for b in bgs if (b['x'], b['y']) == xy]) == 1 for xy in via)
    bgs = [b for b in bgs if (b['x'], b['y']) not in via]
    for (x, y), t in M.porte.items():
        bb = [b for b in bgs if (b['x'], b['y']) == (x, y)]; assert len(bb) == 1, (x, y)
        bb[0]['arg'] = B + cartello('Lido: %s (0.72)' % t.split('\n')[0], t)
    for x, y, t in M.cartelli:
        assert not [b for b in bgs if (b['x'], b['y']) == (x, y)], (x, y)
        bgs.append(dict(x=x, y=y, elev=0, kind=0, arg=B + cartello('Lido: %s (0.72)' % t.split('\n')[0], t)))
    W.set_events(*LIDO, warps=ws, bgs=bgs)
    OUT['lido'] = dict(layout=hex(lp), tileset=hex(tsp), porta_chiesa=hex(nuovo), cartelli=len(M.cartelli),
                       uscita_chiesa=len(ws) - 1)
    return len(ws) - 1


# ================================================================== casa di ALDO (da bozze/casa_rivale.py)
P_MARE, P_RUGGINE = 5, 1


def con_sopra(U, tp, mt, alto16, pal):
    base = U.metatile(tp, mt); refs = list(U.meta[base - 512][0]) if base >= 512 else list(U.prim.refs(base))
    alto = np.asarray(alto16)
    for q in range(4):
        t = alto[(q // 2) * 8:(q // 2) * 8 + 8, (q % 2) * 8:(q % 2) * 8 + 8]
        refs[4 + q] = (U._tile(_raw(t)) | (pal << 12)) if t.any() else 0
    attr = U.prim.attr(mt) if mt < 512 else U.fonte(tp).attr(mt)
    return U.metatile_nuovo(refs, attr)


def appunti(U, tp, mt, k):
    a = np.zeros((16, 16), int)
    fogli = [(2, 1, 7, 9), (9, 3, 14, 12)] if k == 0 else [(1, 2, 7, 11), (9, 1, 14, 8)]
    for x0, y0, x1, y1 in fogli:
        a[y0:y1 + 1, x0:x1 + 1] = 4
        a[y0, x0:x1 + 1] = 1; a[y1, x0:x1 + 1] = 1; a[y0:y1 + 1, x0] = 1; a[y0:y1 + 1, x1] = 1
        for y in range(y0 + 2, y1 - 1, 2): a[y, x0 + 2:x1 - 1] = 1
        a[y0, (x0 + x1) // 2] = 9
    return con_sopra(U, tp, mt, a, P_RUGGINE)


PIEDE = ["01110", "11111", "11111", "11111", "11111", "01110", "00000", "01110", "01110", "00100"]


def tappeto_passi(U, tp, mt, X, Y, W_, H_):
    big = np.zeros((H_ * 16, W_ * 16), int)
    big[:, :] = 3
    big[0, :] = big[-1, :] = 4; big[:, 0] = big[:, -1] = 4
    big[2, 2:-2] = big[-3, 2:-2] = 1; big[2:-2, 2] = big[2:-2, -3] = 1
    passi = [(6, 14), (16, 6), (28, 16), (38, 6), (50, 15)]
    for i, (px, py) in enumerate(passi):
        for j, riga in enumerate(PIEDE):
            for ii, c in enumerate(riga):
                if c == '1':
                    yy, xx = py + j, px + ii + (5 if i % 2 else 0)
                    if 0 <= yy < H_ * 16 and 0 <= xx < W_ * 16: big[yy, xx] = 4
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


def pianterreno(d):
    T = tela.Tela(d, 14, 11, SEC_G, 0)
    L = lay(d, 313); a, _ = tela.Tela.layout(d, L)
    pav, bordo = int(a[3, 2]), int(a[3, 0])
    T.incolla(L, 0, 0, 14, 6, 0, 0)
    for y in (6, 7, 8, 9):
        for x in range(14): T.c[y][x] = (SEC_G, bordo if x == 0 else pav)
    T.incolla(L, 8, 6, 6, 1, 8, 6)
    T.incolla(L, 0, 6, 2, 1, 0, 9)
    T.incolla(L, 0, 7, 14, 1, 0, 10)
    T.incolla(L, 0, 6, 2, 2, 12, 9)
    metti_nuovo(T, 6, 1, appunti, 0); metti_nuovo(T, 7, 1, appunti, 1)
    return T


def camera(d):
    T = tela.Tela(d, 12, 10, SEC_G, 0)
    L = lay(d, 314); a, _ = tela.Tela.layout(d, L)
    pav, bordo = int(a[3, 2]), int(a[3, 0])
    T.incolla(L, 0, 0, 12, 8, 0, 0)
    for y in (8, 9):
        for x in range(12): T.c[y][x] = (SEC_G, bordo if x == 0 else pav)
    for y in range(4, 8):
        for x in range(1, 7): T.c[y][x] = (SEC_G, pav)
    T.incolla(lay(d, 96), 0, 0, 3, 3, 9, 0)
    for y in range(4, 6):
        for x in range(1, 5): metti_nuovo(T, x, y, tappeto_passi, x - 1, y - 4, 4, 2)
    T.incolla(L, 1, 6, 1, 2, 11, 8)
    return T


def scrivi_interno(W, chiave, T, nome):
    m = W.rom.map(*chiave)
    assert (m['width'], m['height']) == (T.w, T.h)
    U = UnioneRivale(bytes(W.d), PRIM_I); vals = T.valori(U)
    nero_t = U._tile(bytes([0xff] * 32))
    nero = 0x400 | U.metatile_nuovo([nero_t | (P_MARE << 12)] * 4 + [0] * 4, 0)
    tp = U.scrivi(W, nome)
    lp = W.set_layout(*chiave, vals, T.w, T.h, (nero,) * 4, PRIM_I, tp)
    blob_attr = U.blob()[3]

    def beh(x, y):
        k = vals[y * T.w + x] & 1023
        return (U.prim.attr(k) if k < 512 else struct.unpack_from('<H', blob_attr, (k - 512) * 2)[0]) & 0xff

    def libera(x, y): return (vals[y * T.w + x] >> 10) & 3 == 0
    OUT[nome] = dict(layout=hex(lp), tileset=hex(tp), **U.stato())
    return beh, libera


def casa_aldo(W):
    m0, m1 = W.rom.map(*PT_R), W.rom.map(*CAM_R)
    assert [(w['x'], w['y'], w['group'], w['num'], w['warp']) for w in m0['warps']] == [(7, 10, 0, 9, 0), (12, 2, 34, 41, 0)]
    assert [(w['x'], w['y'], w['group'], w['num'], w['warp']) for w in m1['warps']] == [(10, 2, 34, 40, 1)]
    assert [(o['x'], o['y'], o['gfx']) for o in m0['objects']] == [(3, 3, 215)]
    assert [(o['x'], o['y'], o['gfx']) for o in m1['objects']] == [(5, 6, 9)]
    assert [(b['x'], b['y']) for b in m1['bgs']] == [(5, 3)] and m0['bgs'] == []
    beh0, lib0 = scrivi_interno(W, PT_R, pianterreno(bytes(W.d)), 'casa di ALDO pianterreno (0.72)')
    beh1, lib1 = scrivi_interno(W, CAM_R, camera(bytes(W.d)), 'casa di ALDO camera (0.72)')
    assert beh0(6, 10) == beh0(7, 10) == 0x65 and beh0(2, 1) == 0x60 and beh1(2, 1) == 0x60
    assert lib0(3, 3) and lib0(7, 9) and lib0(2, 2) and lib1(5, 6) and lib1(2, 2)
    # il diario sul mobiletto verde (11,1-2): si legge dalla casella libera sotto
    dy = 2 if not lib1(11, 2) else 1
    assert not lib1(11, dy) and lib1(11, dy + 1)
    ws = [dict(w) for w in m0['warps']]; ws[1].update(x=2, y=1); ws.append(dict(ws[0], x=6, y=10))
    p_app = cartello('casa di ALDO: appunti (0.72)',
                     "Appunti di allenamento: schivare a destra, poi avvicinarsi. Mai arrendersi!")
    W.set_events(*PT_R, warps=ws, bgs=[dict(x=6, y=1, elev=0, kind=0, arg=B + p_app),
                                        dict(x=7, y=1, elev=0, kind=0, arg=B + p_app)])
    ws = [dict(w) for w in m1['warps']]; ws[0].update(x=2, y=1)
    W.set_events(*CAM_R, warps=ws, bgs=[dict(m1['bgs'][0], x=11, y=dy)])
    OUT['casa_aldo'] = dict(scale=(2, 1), uscite=[(7, 10), (6, 10)], diario=(11, dy), appunti=[(6, 1), (7, 1)])


# ================================================================== chiesa (da bozze/chiesa_lido.py, bozza 2)
COLONNE = list(range(2, 16))
RIGHE = list(range(0, 13)) + list(range(17, 22))


def c15(r, g, b): return (r >> 3) | ((g >> 3) << 5) | ((b >> 3) << 10)


COLORI = {(10, 9): c15(200, 192, 176), (11, 7): c15(200, 192, 176), (12, 3): c15(200, 192, 176),
          (11, 4): c15(48, 96, 176), (11, 6): c15(88, 136, 208)}


class UnioneChiesa(tela.Unione):
    def __init__(self, d):
        super().__init__(d, PRIM_G)
        for k in range(6, 13): self.slot[(SEC_C, k)] = k

    def blob(self):
        tiles, pals, meta, attrs = super().blob()
        pals = bytearray(pals)
        for (k, i), c in COLORI.items(): struct.pack_into('<H', pals, k * 32 + i * 2, c)
        return tiles, bytes(pals), meta, attrs

    def quadro(self):
        a = np.zeros((16, 16), int)
        a[1:15, 2:14] = 4
        a[2:14, 3:13] = 10
        a[9:14, 3:13] = 2
        for y in range(3, 9):
            for x in range(8 - (y - 3) // 2, 8): a[y, x] = 9
        a[3:10, 8] = 1
        a[9, 5:11] = 1; a[10, 6:10] = 1
        return a


def chiesa(W, uscita_lido):
    d = bytes(W.d); rom = W.rom
    mc = rom.map(*CESENA_CHIESA); a = rom.blocks(mc)
    assert mc['secondary'] == SEC_C and mc['primary'] == PRIM_G and (mc['width'], mc['height']) == (18, 22)
    b = a[np.ix_(RIGHE, COLONNE)].copy()
    b[13:15, 13] = a[13, 14]
    b[13:15, 11:13] = a[17:19, 15:17]
    U = UnioneChiesa(d)
    vals = [(int(v) & 0xfc00) | U.metatile(SEC_C, int(v) & 1023) for v in b.flat]
    Wd, Hd = b.shape[1], b.shape[0]
    k = 1 * Wd + 2
    base = vals[k] & 1023; refs = list(U.meta[base - 512][0]); al = U.quadro()
    for q in range(4):
        t = al[(q // 2) * 8:(q // 2) * 8 + 8, (q % 2) * 8:(q % 2) * 8 + 8]
        refs[4 + q] = (U._tile(_raw(t)) | (9 << 12)) if t.any() else 0
    vals[k] = (vals[k] & 0xfc00) | U.metatile_nuovo(refs, U.meta[base - 512][1])
    bordo = [(v & 0xfc00) | U.metatile(SEC_C, v & 1023) for v in struct.unpack_from('<4H', d, mc['border'])]
    # mappa libera 24.75: nessuna uscita la raggiunge, layout 317 solo suo
    for kk in romlib.all_maps(rom):
        try:
            mm = rom.map(*kk)
        except Exception:
            continue
        if mm['header'] != rom.header(*LIDO):
            assert not [w for w in mm['warps'] if (w['group'], w['num']) == CHIESA], kk
        if mm['header'] != rom.header(*CHIESA): assert mm['layout_id'] != rom.map(*CHIESA)['layout_id'], kk
    tp = U.scrivi(W, 'chiesa di Lido (0.72)')
    lp = W.set_layout(*CHIESA, vals, Wd, Hd, bordo, PRIM_G, tp)
    blob_attr = U.blob()[3]
    kk = vals[17 * Wd + 7] & 1023
    assert struct.unpack_from('<H', blob_attr, (kk - 512) * 2)[0] & 0xff == 0x65
    lido_m = rom.map(*LIDO)
    W.header_set(*CHIESA, music=mc['music'], region=lido_m['region'], cave=0, weather=0, type=8,
                 flags=mc['flags'], battle=0)
    W.set_connections(*CHIESA, [])
    W.set_map_scripts(*CHIESA, [])
    flag = E.pool().flag('chiesa di Lido: MAREAROMA dal parroco (0.72)')
    s = Script('chiesa di Lido: parroco (0.72)')
    s.emit(b'\x6a\x5a').flag(flag, 'dopo')
    s.msg("PARROCO: Ogni estate benediciamo il mare e le barche dei pescatori del SAVIO.\n\n"
          "Prendi questo MAREAROMA: è l'incenso della festa. Ai POKéMON d'acqua piace!")
    s.giveitem(MAREAROMA).cmp(0, 'pieno').set(flag).end()
    s.label('pieno').msg("PARROCO: La tua BORSA è piena. Torna quando avrai fatto spazio!").end()
    s.label('dopo').msg("PARROCO: Che il mare ti sia sempre calmo, ovunque tu vada!").end()
    p_par = s.save()
    p_quadro = cartello('chiesa di Lido: quadro (0.72)',
                        "Una barca a vela dipinta: è l'ex voto dei pescatori del SAVIO, tornati a casa dopo "
                        "una burrasca.")
    W.set_events(*CHIESA, objects=[dict(id=1, gfx=29, x=8, y=3, elev=3, move=8, script=p_par)],
                 warps=[dict(x=7, y=17, elev=0, warp=uscita_lido, num=LIDO[1], group=LIDO[0])],
                 coords=[], bgs=[dict(x=2, y=1, elev=0, kind=0, arg=B + p_quadro)])
    OUT['chiesa'] = dict(mappa='24.75', layout=hex(lp), tileset=hex(tp), flag=hex(flag), parroco=hex(p_par),
                         **U.stato())


def apply(W):
    E.ALPHA.setdefault('&', 0x2d)          # '&' del font di Smeraldo (per PURO & BIO); nessun testo prima lo usava
    uscita = lido(W)
    casa_aldo(W)
    chiesa(W, uscita)
    return OUT
