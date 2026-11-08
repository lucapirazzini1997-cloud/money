"""Bozza Lotto 4: esterno del laboratorio di Lido di Savio (0.9), oggi la vetrina "RICERCA.COSTIERA".

Al suo posto il Museo Oceanografico di Smeraldo (Porto Alghepoli, layout 2, x 28-33, y 22-27): un edificio di
ricerca sul mare, con il tetto verde acqua e le colonne. Sta in (11-16, 23-28): la porta resta in (13,27), dove
oggi c'e' l'uscita 2 del laboratorio; la porta del museo e' larga due caselle, quindi (14,27) diventa una seconda
uscita verso lo stesso laboratorio. Il cartello del laboratorio passa da (11,28) a (10,28).

Il secondario di Lido (0x1fe349c, solo di Lido) ha le 7 palette e i 512 tile gia' occupati: si rifa' con l'Unione,
tenendo le palette 6-12 agli stessi posti; i pezzi del museo (palette 6 e 8 di Porto Alghepoli) si ricolorano con
la palette di Lido o del primario piu' vicina, tile per tile. I tile della vetrina si liberano.
Uso: python3 bozze/laboratorio.py ROM_070 CARTELLA
"""
import sys, struct
from pathlib import Path
sys.path[:0] = [str(Path(__file__).resolve().parent.parent / 'strumenti_rom')]
import numpy as np
import tela, romlib

LIDO = (0, 9)
SEC_LIDO = 0x1fe349c
LAB = (9, 20, 9, 9)                    # x, y, w, h della vetrina da togliere (con il suo cartello)
ERBA = 0x3001
MUSEO = (28, 22, 6, 6)                 # nel layout 2 (Porto Alghepoli)
DOVE = (11, 23)
CARTELLO_VECCHIO, CARTELLO = (11, 28), (10, 28)


def rgb(c): return np.array([c & 31, (c >> 5) & 31, (c >> 10) & 31], float)


def pal_rgb(raw): return [rgb(c) for c in struct.unpack('<16H', raw)]


class UnioneLido(tela.Unione):
    """Unione con le palette 6-12 di Lido agli stessi posti e i pezzi esterni ricolorati."""

    def __init__(self, d):
        super().__init__(d)
        for k in range(6, 13): self.slot[(SEC_LIDO, k)] = k
        self.lido = self.fonte(SEC_LIDO)
        self.tavolozze = {k: pal_rgb(bytes(d[self.prim.pals + k * 32:self.prim.pals + k * 32 + 32])) for k in range(6)}
        self.tavolozze.update({k: pal_rgb(self.lido.palette(k)) for k in range(6, 13)})
        self.errori = []

    def ricolora(self, tp, mt, fondo=None):
        """Metatile `mt` della fonte `tp` con i tile ricolorati nella tavolozza piu' vicina.
        fondo: refs dello strato basso da mettere al posto di quello di origine (es. l'erba)."""
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
                for i in set(px.tolist()) - {0}:
                    dist = [((src[i] - tav[j]) ** 2).sum() for j in range(1, 16)]
                    j = int(np.argmin(dist)) + 1; mappa[i] = j; err += dist[j - 1] * int((px == i).sum())
                if meglio is None or err < meglio[0]: meglio = (err, q, mappa)
            err, q, mappa = meglio; self.errori.append(err / 64)
            npx = np.array([mappa[int(i)] for i in px], np.uint8).reshape(-1, 2)
            t = self._tile(bytes((npx[:, 0] | (npx[:, 1] << 4)).tolist()))
            new.append((r & 0x0c00) | t | (q << 12))
        return self.metatile_nuovo(new, f.attr(mt))


def lido_nuovo(d):
    rom = romlib.Rom(bytes(d)); m = rom.map(*LIDO)
    assert m['secondary'] == SEC_LIDO and (m['width'], m['height']) == (56, 44)
    a = rom.blocks(m); w, h = m['width'], m['height']
    assert int(a[27, 13]) & 1023 == int(a[27, 13]) & 1023 and (m['warps'][2]['x'], m['warps'][2]['y']) == (13, 27)
    U = UnioneLido(bytes(d))
    cv = int(a[CARTELLO_VECCHIO[1], CARTELLO_VECCHIO[0]])
    x0, y0, lw, lh = LAB
    a[y0 + 2:y0 + lh, x0:x0 + lw] = ERBA
    a[CARTELLO[1], CARTELLO[0]] = cv
    vals = [(int(v) & 0xfc00) | U.metatile(SEC_LIDO, int(v) & 1023) for v in a.flat]
    # il museo
    lp = struct.unpack_from('<I', d, 0x627fc0 + 4)[0] - 0x8000000
    ma, msec = tela.Tela.layout(d, lp)
    mx, my, mw, mh = MUSEO
    for j in range(mh):
        for i in range(mw):
            v = int(ma[my + j, mx + i]); k = v & 1023
            # la prima riga del museo poggia sul muretto bianco del molo: sotto ci va l'erba di Lido
            k2 = U.ricolora(msec, k, U.prim.refs(ERBA & 1023) if j == 0 else None) if k >= 512 else U.metatile(SEC_LIDO, k)
            vals[(DOVE[1] + j) * w + DOVE[0] + i] = 0x3000 | (v & 0x0c00) | k2
    return U, vals, w, h, m


if __name__ == '__main__':
    import sprite
    from PIL import ImageDraw
    d = open(sys.argv[1], 'rb').read(); out = Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
    U, vals, w, h, m = lido_nuovo(d)
    print(U.stato(), 'errore medio ricolore %.1f max %.1f' % (np.mean(U.errori), max(U.errori)))
    im = tela.anteprima(d, U, vals, w, h, 1)
    ogg = [(o['x'], o['y'], o['gfx']) for o in m['objects']]
    sprite.disegna(d, im, ogg, 1)
    im.save(out / 'lido_laboratorio_intera.png')
    z = im.crop((3 * 16, 18 * 16, 21 * 16, 32 * 16)); z = z.resize((z.width * 3, z.height * 3), 0)
    z.save(out / 'lido_laboratorio.png')
    rv = romlib.Rom(bytes(d)).render(m, events=False, scale=1)
    rv.crop((3 * 16, 18 * 16, 21 * 16, 32 * 16)).resize((18 * 48, 14 * 48), 0).save(out / 'lido_laboratorio_prima.png')
