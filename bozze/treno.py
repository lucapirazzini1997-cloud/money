"""Bozza del treno regionale (Lotto 3): cinque stazioni sulla linea Rimini - Cesena - Forli' - Faenza - Imola.
  - fuori: in ogni citta' una casa chiusa diventa la STAZIONE (edificio color ocra con insegna, preso dalla porta
    di Faenza verso Ravenna, con la scritta nuova);
  - dentro: la sala del binario di Smeraldo (linee gialle, binario, tabellone, panchine), uguale in tutte le stazioni;
  - la carrozza: atrio del Centro Spaziale di Smeraldo (finestrini, tavolini e sgabelli), per la scena del viaggio.
Uso: python3 bozze/treno.py ROM.gba cartella_uscita"""
import sys, struct
from pathlib import Path
sys.path[:0] = [str(Path(__file__).resolve().parent.parent / 'strumenti_rom')]
import numpy as np
import tela, sprite, romlib
from PIL import Image, ImageDraw

d = open(sys.argv[1], 'rb').read()
R = romlib.Rom(d)
def lay(lid): return struct.unpack_from('<I', d, 0x627fc0 + (lid - 1) * 4)[0] - 0x8000000

def rgb(pal32):
    v = np.frombuffer(pal32, '<u2').astype(int)
    return np.stack([v & 31, (v >> 5) & 31, (v >> 10) & 31], -1)


# ---------------------------------------------------------------- cartello "STAZIONE"
# Le citta' hanno i 512 tile del secondario gia' pieni: il cartello sta in 8 tile del PRIMARIO che nessuna mappa,
# nessun metatile e nessun setmetatile degli script usa (vuoti in Smeraldo), e si disegna nello strato alto di
# quattro metatile della facciata, sopra il muro della casa. Palette 4 del primario: bianco e blu, come i
# cartelli veri delle stazioni.
TILE_CARTELLO = [183, 197, 219, 235, 237, 258, 290, 306]
PAL_CARTELLO = 4
FONT = {
    'S': ['.###', '#...', '.##.', '...#', '###.'], 'T': ['###', '.#.', '.#.', '.#.', '.#.'],
    'A': ['.##.', '#..#', '####', '#..#', '#..#'], 'Z': ['####', '...#', '.##.', '#...', '####'],
    'I': ['###', '.#.', '.#.', '.#.', '###'], 'O': ['.##.', '#..#', '#..#', '#..#', '.##.'],
    'N': ['#..#', '##.#', '#.##', '#..#', '#..#'], 'E': ['####', '#...', '###.', '#...', '####'],
}


def cartello_pixel():
    """64x8 indici della palette 4: bordo blu scuro, fondo blu, STAZIONE in bianco; 0 = trasparente."""
    img = np.zeros((8, 64), int)
    img[0:8, 3:61] = 0xa                     # bordo
    img[1:7, 4:60] = 0x7                     # fondo
    testo = 'STAZIONE'
    larg = sum(len(FONT[c][0]) for c in testo) + (len(testo) - 1)
    x = (64 - larg) // 2
    for c in testo:
        g = FONT[c]
        for j, riga in enumerate(g):
            for i, ch in enumerate(riga):
                if ch == '#': img[1 + j, x + i] = 0x1
        x += len(g[0]) + 1
    return img


def tile_cartello():
    img = cartello_pixel(); out = []
    for k in range(8):
        t = img[:, k * 8:k * 8 + 8].flatten()
        out.append(bytes(int(t[i]) | (int(t[i + 1]) << 4) for i in range(0, 64, 2)))
    return out


def unione_con_cartello():
    U = tela.Unione(d)
    pt = bytearray(U.prim_tiles)
    for idx, raw in zip(TILE_CARTELLO, tile_cartello()):
        assert not any(pt[idx * 32:idx * 32 + 32]), idx              # deve essere vuoto
        pt[idx * 32:idx * 32 + 32] = raw
    U.prim_tiles = bytes(pt)
    return U


def con_cartello(U, id_meta, k, meta):
    """Metatile id_meta (gia' nell'unione) con il pezzo k (0-3) del cartello nella meta' alta (meta=0) o bassa (1)
    dello strato alto; tipo di strato 'coperto' (tutto sotto i personaggi)."""
    refs, attr = (list(U.prim.refs(id_meta)), U.prim.attr(id_meta)) if id_meta < 512 else map(list, [U.meta[id_meta - 512][0], [U.meta[id_meta - 512][1]]])
    if id_meta >= 512: attr = attr[0]
    q0 = 4 + meta * 2
    refs[q0] = TILE_CARTELLO[2 * k] | (PAL_CARTELLO << 12)
    refs[q0 + 1] = TILE_CARTELLO[2 * k + 1] | (PAL_CARTELLO << 12)
    attr = (attr & ~0x3000) | 0x1000
    return U.metatile_nuovo(refs, attr)


# ---------------------------------------------------------------- citta'
class Citta:
    """La casa (4 caselle di larghezza, porta nella terza colonna in basso) che diventa la stazione."""
    def __init__(self, g, n, nome, x, y, h, riga, meta):
        self.g, self.n, self.nome, self.x, self.y, self.hcasa = g, n, nome, x, y, h
        self.riga, self.meta = riga, meta                 # riga della facciata col cartello, meta' (0 alta, 1 bassa)
        self.m = R.map(g, n); self.w, self.h = self.m['width'], self.m['height']
        self.T = tela.Tela(d, self.w, self.h, self.m['secondary'], 0)
        self.T.incolla(self.m['layout'], 0, 0, self.w, self.h, 0, 0)
        self.porta = (x + 2, y + h - 1)

    def valori(self):
        U = unione_con_cartello()
        v = self.T.valori(U)
        for i in range(4):
            k = self.riga * self.w + self.x + i
            v[k] = (v[k] & 0xfc00) | con_cartello(U, v[k] & 1023, i, self.meta)
        return U, v


CITTA = [
    Citta(34, 17, 'Cesena', 80, 6, 3, 7, 1),
    Citta(34, 47, 'Rimini', 52, 9, 3, 10, 1),
    Citta(34, 68, 'Forli', 70, 52, 4, 54, 0),
    Citta(34, 85, 'Faenza', 38, 2, 4, 4, 0),
    Citta(35, 1, 'Imola', 55, 16, 4, 18, 0),
]


# ---------------------------------------------------------------- sala della stazione e carrozza
SALA_L = lay(118)                                # 13 x 12, sala del binario
class Stanza:
    def __init__(self, nome, w, h, fonte):
        self.nome, self.w, self.h = nome, w, h
        self.T = tela.Tela(d, w, h, fonte, 0)
        self.oggetti, self.cartelli, self.uscite = [], [], []


sala = Stanza('Stazione (sala del binario)', 13, 12, None)
sala.T.incolla(SALA_L, 0, 0, 13, 12, 0, 0)
sala.oggetti = [(7, 8, 115, 'CAPOTRENO: biglietti e partenze'), (1, 9, 21, 'viaggiatore in attesa'),
                (10, 2, 26, 'viaggiatrice sul binario')]
sala.cartelli = [(2, 4), (3, 4), (12, 8)]
sala.uscite = [((6, 11), 'citta'), ((7, 11), 'citta')]
sala.arrivo = (6, 4)                              # dal treno si scende qui, davanti al binario

L_CENTRO = lay(275)                               # 16 x 10, atrio del Centro Spaziale (stesso tileset della sala)
a, S = tela.Tela.layout(d, L_CENTRO)
carrozza = Stanza('Carrozza del regionale', 16, 12, S)
T = carrozza.T
for y in range(12):
    for x in range(16): T.metti(x, y, S, int(a[3, 1]))                  # pavimento
for x in range(16):
    T.metti(x, 0, S, int(a[0, 4])); T.metti(x, 1, S, int(a[1, 4]))     # parete con i finestrini
    T.metti(x, 2, S, int(a[2, 4]))                                       # ombra sotto la parete
T.incolla(L_CENTRO, 1, 0, 1, 3, 0, 0); T.incolla(L_CENTRO, 15, 0, 1, 3, 15, 0)   # porte delle due testate
for x0 in (1, 5, 9, 13):                                                 # scompartimenti con tavolino, due file
    for y0 in (3, 8):
        T.incolla(L_CENTRO, 2, 5, 2, 2, x0, y0 + 1)                     # tavolino
        for yy in (y0, y0 + 3):
            T.metti(x0, yy, S, int(a[3, 2])); T.metti(x0 + 1, yy, S, int(a[3, 2]))   # posti (sgabelli)
carrozza.oggetti = [(10, 3, 21, 'viaggiatore (prima corsa: due chiacchiere)'), (3, 7, 115, 'CAPOTRENO: "Prossima fermata..."')]
carrozza.arrivo = (8, 7)


def tavolini_lisci(U, v, s=None):
    """I tavolini del Centro Spaziale hanno un razzo disegnato (strato alto): metatile nuovi con il piano bianco."""
    def tile(idx):
        px = []
        for bb in U.tiles[idx - 512]: px += [bb & 15, bb >> 4]
        return np.array(px).reshape(8, 8)
    vecchi = {}
    img = np.zeros((32, 32), int)
    for j in range(2):
        for i in range(2):
            mid = U.metatile(S, int(a[5 + j, 2 + i]) & 1023); vecchi[(i, j)] = mid
            refs, _ = U.meta[mid - 512]
            for q in range(4):
                r = refs[4 + q]; t = tile(r & 1023)
                if r & 0x400: t = t[:, ::-1]
                if r & 0x800: t = t[::-1]
                y, x = j * 16 + (q // 2) * 8, i * 16 + (q % 2) * 8
                img[y:y + 8, x:x + 8] = t
    bianco = np.bincount(img[8:20, 8:24].flatten()).argmax()
    img[4:21, 5:27] = bianco
    nuovi = {}
    for (i, j), mid in vecchi.items():
        refs, attr = U.meta[mid - 512]; refs = list(refs)
        for q in range(4):
            y, x = j * 16 + (q // 2) * 8, i * 16 + (q % 2) * 8
            t = img[y:y + 8, x:x + 8].flatten()
            raw = bytes(int(t[k]) | (int(t[k + 1]) << 4) for k in range(0, 64, 2))
            refs[4 + q] = U._tile(raw) | (refs[4 + q] & 0xf000)
        nuovi[mid] = U.metatile_nuovo(refs, attr)
    for k, val in enumerate(v):
        if (val & 1023) in nuovi: v[k] = (val & 0xfc00) | nuovi[val & 1023]


carrozza.ritocco = tavolini_lisci
carrozza.uscite = []


def anteprima_stanza(s, scala=3):
    U = tela.Unione(d); v = s.T.valori(U)
    if getattr(s, 'ritocco', None): s.ritocco(U, v)
    im = tela.anteprima(d, U, v, s.w, s.h, scala)
    sprite.disegna(d, im, [(x, y, g) for x, y, g, _ in s.oggetti], scala)
    sprite.numeri(im, [(x, y, str(k + 1)) for k, (x, y, _, _) in enumerate(s.oggetti)], scala)
    dr = ImageDraw.Draw(im); q = 16 * scala
    for (x, y), _ in s.uscite: dr.rectangle((x * q, y * q, x * q + q - 1, y * q + q - 1), outline=(170, 40, 220), width=4)
    for (x, y) in s.cartelli: dr.rectangle((x * q, y * q, x * q + q - 1, y * q + q - 1), outline=(40, 170, 230), width=4)
    x, y = s.arrivo; dr.rectangle((x * q + 8, y * q + 8, x * q + q - 9, y * q + q - 9), outline=(250, 200, 0), width=4)
    return U, v, im


def anteprima_citta(c, scala=2, margine=7):
    U, v = c.valori()
    im = tela.anteprima(d, U, v, c.w, c.h, 1)
    x0, y0 = max(0, c.x - margine), max(0, c.y - margine)
    x1, y1 = min(c.w, c.x + 4 + margine), min(c.h, c.y + c.hcasa + margine)
    prima = R.render(c.m, events=False, scale=1).crop((x0 * 16, y0 * 16, x1 * 16, y1 * 16))
    dopo = im.crop((x0 * 16, y0 * 16, x1 * 16, y1 * 16))
    dr = ImageDraw.Draw(dopo); px, py = c.porta
    dr.rectangle(((px - x0) * 16, (py - y0) * 16, (px - x0) * 16 + 15, (py - y0) * 16 + 15), outline=(170, 40, 220), width=2)
    W, H = prima.width, prima.height
    out = Image.new('RGB', (W * 2 + 8, H), (30, 30, 30)); out.paste(prima, (0, 0)); out.paste(dopo, (W + 8, 0))
    return U, out.resize((out.width * scala, out.height * scala), Image.NEAREST)


if __name__ == '__main__':
    out = Path(sys.argv[2]); out.mkdir(exist_ok=True)
    for c in CITTA:
        U, im = anteprima_citta(c); im.save(out / ('stazione_%s.png' % c.nome.lower())); print(c.nome, U.stato())
    for s, f in ((sala, 'sala_stazione.png'), (carrozza, 'carrozza.png')):
        U, v, im = anteprima_stanza(s); im.save(out / f); print(s.nome, s.w, s.h, U.stato())
