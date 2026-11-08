"""Bozza Lotto 4 (2): interno della chiesa di Lido di Savio (mappa libera 24.75, nessuna uscita la raggiunge oggi).

Pezzi della chiesa di Cesena (34.37), ma un'altra chiesa: navata raccolta 14x18 con l'abside al centro, pavimento di
pietra chiara (disegnato al posto dei rombi rossi), tappeto blu mare con il bordo d'oro (ricolorato), tre file di
banchi fra le colonne, organo, acquasantiera, confessionale; al muro un quadro con una barca a vela (ex voto dei
pescatori, disegnato a mano). Stesse palette della chiesa di Cesena: nessuna palette nuova.
Evento: il PARROCO (in 8,3) racconta la benedizione del mare e la prima volta regala un MAREAROMA (flag nuova);
il quadro (2,1) si legge. Uscita in (7,17) verso la porta della chiesa a Lido.
Uso: python3 bozze/chiesa_lido.py ROM_071 CARTELLA
"""
import sys, struct
from pathlib import Path
sys.path[:0] = [str(Path(__file__).resolve().parent.parent / 'strumenti_rom')]
import numpy as np
import tela, romlib

CESENA_CHIESA = (34, 37)
SEC_C = 0x18d89e4
PRIM = 0x55e8c0
COLONNE = list(range(2, 16))                                  # 14 colonne, navata centrata (tappeto in 6-7)
RIGHE = list(range(0, 13)) + list(range(17, 22))              # 18 righe
PARROCO = (8, 3, 29)
USCITA = (7, 17)
QUADRO = (2, 1)
PAVIMENTO = 0x214
TESTI = dict(
    parroco="PARROCO: Ogni estate benediciamo il mare e le barche dei pescatori del SAVIO.\n\n"
            "Prendi questo MAREAROMA: è l'incenso della festa. Ai POKéMON d'acqua piace!",
    parroco_dopo="PARROCO: Che il mare ti sia sempre calmo, ovunque tu vada!",
    quadro="Una barca a vela dipinta: è l'ex voto dei pescatori del SAVIO, tornati a casa dopo una burrasca.")


def _px(raw, idx):
    a = np.frombuffer(bytes(raw[idx * 32:idx * 32 + 32]), np.uint8)
    p = np.empty(64, np.uint8); p[::2] = a & 15; p[1::2] = a >> 4
    return p.reshape(8, 8)


def _raw(t):
    t = np.asarray(t, np.uint8).reshape(64)
    return bytes(int(t[i]) | (int(t[i + 1]) << 4) for i in range(0, 64, 2))


def pal(d, k):
    v = struct.unpack('<16H', tela.Tileset(d, SEC_C).palette(k))
    return np.array([[(c & 31) * 8, ((c >> 5) & 31) * 8, ((c >> 10) & 31) * 8] for c in v], float)


def c15(r, g, b): return (r >> 3) | ((g >> 3) << 5) | ((b >> 3) << 10)


# colori nuovi: pavimento (rombi rossi della palette 10 -> pietra chiara), tappeto (palette 11, rosso -> blu mare)
COLORI = {(10, 9): c15(200, 192, 176), (11, 7): c15(200, 192, 176), (12, 3): c15(200, 192, 176),   # rombi
          (11, 4): c15(48, 96, 176), (11, 6): c15(88, 136, 208)}                                     # tappeto blu


class UnioneChiesa(tela.Unione):
    """Unione dalla chiesa di Cesena, stesse palette agli stessi posti, con i colori di pavimento e tappeto cambiati."""

    def __init__(self, d):
        super().__init__(d, PRIM)
        for k in range(6, 13): self.slot[(SEC_C, k)] = k

    def blob(self):
        tiles, pals, meta, attrs = super().blob()
        pals = bytearray(pals)
        for (k, i), c in COLORI.items(): struct.pack_into('<H', pals, k * 32 + i * 2, c)
        return tiles, bytes(pals), meta, attrs

    def quadro(self):
        """Quadro con la barca a vela (palette 9: 1 scuro, 2 blu, 4 oro scuro, 9 legno, 10 chiaro)."""
        a = np.zeros((16, 16), int)
        a[1:15, 2:14] = 4
        a[2:14, 3:13] = 10
        a[9:14, 3:13] = 2
        for y in range(3, 9):
            for x in range(8 - (y - 3) // 2, 8): a[y, x] = 10 if False else 9
        a[3:10, 8] = 1
        a[9, 5:11] = 1; a[10, 6:10] = 1
        return a


def chiesa(d):
    rom = romlib.Rom(bytes(d)); m = rom.map(*CESENA_CHIESA); a = rom.blocks(m)
    b = a[np.ix_(RIGHE, COLONNE)].copy()
    b[13:15, 13] = a[13, 14]                                   # via la meta' del confessionale tagliata
    b[13:15, 11:13] = a[17:19, 15:17]                          # confessionale intero, contro il muro destro
    return b


def costruisci(d):
    b = chiesa(d); U = UnioneChiesa(d)
    vals = [(int(v) & 0xfc00) | U.metatile(SEC_C, int(v) & 1023) for v in b.flat]
    # quadro: strato alto disegnato sul muro (palette 9)
    W = b.shape[1]; k = QUADRO[1] * W + QUADRO[0]
    base = vals[k] & 1023; refs = list(U.meta[base - 512][0])
    al = U.quadro()
    for q in range(4):
        t = al[(q // 2) * 8:(q // 2) * 8 + 8, (q % 2) * 8:(q % 2) * 8 + 8]
        refs[4 + q] = (U._tile(_raw(t)) | (9 << 12)) if t.any() else 0
    vals[k] = (vals[k] & 0xfc00) | U.metatile_nuovo(refs, U.meta[base - 512][1])
    return U, vals, b.shape[1], b.shape[0]


if __name__ == '__main__':
    import sprite
    from PIL import ImageDraw
    d = open(sys.argv[1], 'rb').read(); out = Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
    U, vals, W, H = costruisci(d)
    im = tela.anteprima(d, U, vals, W, H, 1)
    sprite.disegna(d, im, [PARROCO], 1)
    im = im.resize((W * 48, H * 48), 0); dr = ImageDraw.Draw(im)
    for (x, y), c in ((USCITA, (0, 255, 220)), (QUADRO, (255, 220, 0))):
        dr.rectangle((x * 48, y * 48, x * 48 + 47, y * 48 + 47), outline=c, width=3)
    im.save(out / 'chiesa_lido.png'); print(W, H, U.stato())
