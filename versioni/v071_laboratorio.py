"""Versione 0.71 - Lotto 4: esterno del laboratorio di Lido di Savio (0.9).

Disegno della bozza approvata (bozze/laboratorio.py, "Va bene cosi' puoi procedere"), copiato qui e congelato:
  - la vetrina "RICERCA.COSTIERA" (9-17, 22-28) diventa erba;
  - al suo posto, in (11-16, 23-28), il Museo Oceanografico di Smeraldo (Porto Alghepoli, layout 2, x 28-33,
    y 22-27), ricolorato tile per tile con la palette di Lido o del primario piu' vicina; la prima riga poggia
    sull'erba di Lido invece che sul muretto del molo;
  - il secondario di Lido (0x1fe349c, usato solo da Lido) si rifa' con l'Unione, palette 6-12 agli stessi posti.
Misure invariate (56x44); il layout nuovo prende il posto del vecchio nella tabella dei layout (id 631).
Eventi: la porta del museo e' larga due caselle: l'uscita 2 resta in (13,27) e una nuova uscita 15 in (14,27) porta
allo stesso punto del laboratorio (1.4, uscita 0). Il cartello passa da (11,28) a (10,28) con il testo riscritto a
30 caratteri. Niente flag e niente variabili nuove.
"""
import struct, sys
from pathlib import Path
import numpy as np
import engine as E
from engine import B, Script
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'strumenti_rom'))
import tela

LIDO = (0, 9)
LID = 631
SEC_LIDO = 0x1fe349c
PRIM = 0x55e8c0
LAB = (9, 20, 9, 9)                    # x, y, w, h della vetrina (si tolgono le righe da y+2)
ERBA = 0x3001
MUSEO = (28, 22, 6, 6)                 # nel layout 2 (Porto Alghepoli)
DOVE = (11, 23)
CARTELLO_VECCHIO, CARTELLO = (11, 28), (10, 28)
OUT = {}


def rgb(c): return np.array([c & 31, (c >> 5) & 31, (c >> 10) & 31], float)


def pal_rgb(raw): return [rgb(c) for c in struct.unpack('<16H', raw)]


class UnioneLido(tela.Unione):
    """Unione con le palette 6-12 di Lido agli stessi posti e i pezzi esterni ricolorati."""

    def __init__(self, d):
        super().__init__(d, PRIM)
        for k in range(6, 13): self.slot[(SEC_LIDO, k)] = k
        self.lido = self.fonte(SEC_LIDO)
        self.tavolozze = {k: pal_rgb(bytes(d[self.prim.pals + k * 32:self.prim.pals + k * 32 + 32])) for k in range(6)}
        self.tavolozze.update({k: pal_rgb(self.lido.palette(k)) for k in range(6, 13)})
        self.errori = []

    def ricolora(self, tp, mt, fondo=None):
        f = self.fonte(tp); refs = list(f.refs(mt)); new = []
        if fondo: refs[:4] = list(fondo)[:4]
        for r in refs:
            idx, pal = r & 1023, r >> 12
            if idx < 512 and pal < 6: new.append(r); continue
            raw = bytes(f.raw[(idx - 512) * 32:(idx - 512) * 32 + 32]) if idx >= 512 else \
                bytes(self.prim_tiles[idx * 32:idx * 32 + 32])
            px = np.frombuffer(raw, np.uint8); px = np.stack([px & 15, px >> 4], 1).reshape(-1)
            src = pal_rgb(f.palette(pal))
            meglio = None
            for q, tav in self.tavolozze.items():
                mappa, err = {0: 0}, 0.0
                for i in sorted(set(px.tolist()) - {0}):
                    dist = [((src[i] - tav[j]) ** 2).sum() for j in range(1, 16)]
                    j = int(np.argmin(dist)) + 1; mappa[i] = j; err += dist[j - 1] * int((px == i).sum())
                if meglio is None or err < meglio[0]: meglio = (err, q, mappa)
            err, q, mappa = meglio; self.errori.append(err / 64)
            npx = np.array([mappa[int(i)] for i in px], np.uint8).reshape(-1, 2)
            t = self._tile(bytes((npx[:, 0] | (npx[:, 1] << 4)).tolist()))
            new.append((r & 0x0c00) | t | (q << 12))
        return self.metatile_nuovo(new, f.attr(mt))


def lido_nuovo(d, rom, tabella):
    m = rom.map(*LIDO)
    assert m['secondary'] == SEC_LIDO and m['primary'] == PRIM and (m['width'], m['height']) == (56, 44)
    a = rom.blocks(m); w, h = m['width'], m['height']
    U = UnioneLido(bytes(d))
    cv = int(a[CARTELLO_VECCHIO[1], CARTELLO_VECCHIO[0]])
    x0, y0, lw, lh = LAB
    a[y0 + 2:y0 + lh, x0:x0 + lw] = ERBA
    a[CARTELLO[1], CARTELLO[0]] = cv
    vals = [(int(v) & 0xfc00) | U.metatile(SEC_LIDO, int(v) & 1023) for v in a.flat]
    lp = struct.unpack_from('<I', d, tabella + 4)[0] - B           # layout 2 (Porto Alghepoli)
    ma, msec = tela.Tela.layout(d, lp)
    mx, my, mw, mh = MUSEO
    assert [int(v) & 1023 for v in ma[my + 4, mx:mx + mw]] == [0x328, 0x329, 0x32a, 0x32a, 0x32b, 0x32c]
    for j in range(mh):
        for i in range(mw):
            v = int(ma[my + j, mx + i]); k = v & 1023
            k2 = U.ricolora(msec, k, U.prim.refs(ERBA & 1023) if j == 0 else None) if k >= 512 else U.metatile(SEC_LIDO, k)
            vals[(DOVE[1] + j) * w + DOVE[0] + i] = 0x3000 | (v & 0x0c00) | k2
    bordo = [(v & 0xfc00) | U.metatile(SEC_LIDO, v & 1023) for v in struct.unpack_from('<4H', d, m['border'])]
    return U, vals, w, h, m, bordo


def apply(W):
    import romlib
    tutte = list(romlib.all_maps(W.rom))
    n = 0
    for k in tutte:
        try: n += W.rom.map(*k)['layout_id'] == LID
        except Exception: pass
    assert n == 1
    U, vals, w, h, m, bordo = lido_nuovo(W.d, W.rom, W.table)
    ws = [dict(x) for x in m['warps']]
    assert (ws[2]['x'], ws[2]['y'], ws[2]['group'], ws[2]['num'], ws[2]['warp']) == (13, 27, 1, 4, 0) and len(ws) == 15
    bg = [dict(b) for b in m['bgs']]
    vecchio = [b for b in bg if (b['x'], b['y']) == CARTELLO_VECCHIO]
    assert len(vecchio) == 1 and vecchio[0]['arg'] == B + 0x2c9e1b
    tp = U.scrivi(W, 'Lido di Savio (0.71)')
    lp = W.set_layout(*LIDO, vals, w, h, bordo, PRIM, tp)
    blob_attr = U.blob()[3]

    def beh(x, y):
        k = vals[y * w + x] & 1023
        return (U.prim.attr(k) if k < 512 else struct.unpack_from('<H', blob_attr, (k - 512) * 2)[0]) & 0xff
    assert beh(13, 27) == beh(14, 27) == 0x60, (beh(13, 27), beh(14, 27))
    libera = lambda x, y: (vals[y * w + x] >> 10) & 3 == 0
    assert all(libera(x, 28) for x in range(11, 17)) and libera(13, 29) and not libera(*CARTELLO)
    ws.append(dict(ws[2], x=14, y=27))
    testo = W.alloc(W.enc('STAZIONE DI RICERCA ADRIATICA') + b'\xfe' + W.enc('Prof. PINO: POKéMON e ambiente') + b'\xff',
                    'testo cartello laboratorio (0.71)')
    s2 = Script('Lido: cartello del laboratorio (0.71)')
    s2.emit(b'\x0f\x00' + struct.pack('<I', B + testo) + b'\x09\x02\x02')   # loadword, callstd 2 (cartello), end
    sp = s2.save()
    vecchio[0].update(x=CARTELLO[0], y=CARTELLO[1], arg=B + sp)
    W.set_events(*LIDO, warps=ws, bgs=bg)
    OUT['lido'] = dict(layout=hex(lp), tileset=hex(tp), cartello=hex(sp), **U.stato(),
                       ricolore=dict(medio=round(float(np.mean(U.errori)), 1), max=round(float(max(U.errori)), 1)))
    OUT['eventi'] = dict(porta=[(13, 27), (14, 27)], cartello=CARTELLO)
    return OUT
