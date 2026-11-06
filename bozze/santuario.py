"""Bozza dell'interno del Fumaiolo (35.12-35.18): ogni stanza nasce da una stanza di Smeraldo, con le uscite
che non servono chiuse e personaggi, cartelli e uscite nei punti nuovi.
  35.12 Grotta dell'Eremo         <- Cascata Meteora (stanza dei gradoni viola)
  35.13 Grotta delle Sorgenti     <- Cascata Meteora (lago con l'isola): il nodo che porta alle altre stanze
  35.14 Nodo del Sale             <- Covo Magma (stanza con le colate)
  35.15 Nodo dell'Argilla         <- Covo Magma (sala dei macchinari)
  35.16 Sala di Bassi             <- Covo Magma (gradoni)
  35.17 Cuore del Fumaiolo        <- Grotta Terra (caverna con il magma)
  35.18 Passo dei Draghi          <- Passo Selvaggio (senza il bosco in fondo e senza la porta del covo)
Uso: python3 bozze/santuario.py ROM.gba cartella_uscita"""
import sys, struct
from pathlib import Path
sys.path[:0] = [str(Path(__file__).resolve().parent.parent / 'strumenti_rom')]
import tela, sprite
from PIL import Image, ImageDraw

d = open(sys.argv[1], 'rb').read()
def lay(lid): return struct.unpack_from('<I', d, 0x627fc0 + (lid - 1) * 4)[0] - 0x8000000


class Stanza:
    def __init__(self, n, nome, lid, x0=0, y0=0, w=None, h=None):
        self.n, self.nome, self.L = n, nome, lay(lid)
        a, self.S = tela.Tela.layout(d, self.L)
        self.w, self.h = w or a.shape[1] - x0, h or a.shape[0] - y0
        self.T = tela.Tela(d, self.w, self.h, self.S, 0)
        self.T.incolla(self.L, x0, y0, self.w, self.h, 0, 0)
        self.uscite, self.oggetti, self.cartelli, self.barriera = [], [], [], []
        self.lisce = False                         # True: le gobbe (0xd1, serve la Bici Cross) diventano terreno normale

    def come(self, x, y, xs, ys):                 # la casella (x,y) diventa uguale a (xs,ys)
        self.T.c[y][x] = self.T.c[ys][xs]


STANZE = []
# --- 35.12 Grotta dell'Eremo
s = Stanza(12, "Grotta dell'Eremo", 126)
s.come(7, 20, 8, 20); s.come(7, 19, 8, 19); s.come(4, 14, 4, 15); s.come(4, 13, 5, 13)                    # scale che non servono
s.uscite = [((10, 29), 'Sentiero 35.10'), ((21, 23), 'Grotta delle Sorgenti 35.13')]
s.oggetti = [(18, 27, 24, 'guida: la grotta')]
STANZE.append(s)
# --- 35.13 Grotta delle Sorgenti
s = Stanza(13, 'Grotta delle Sorgenti', 127)
s.come(5, 6, 6, 6); s.come(5, 5, 6, 5); s.come(18, 15, 18, 16); s.come(18, 14, 19, 14); s.come(3, 23, 3, 24); s.come(3, 22, 4, 22)   # scale che non servono
for x0 in (12, 19):                                            # due ingressi nuovi nella parete nord, come quello di Bassi
    for i in range(3):
        for j in (2, 3): s.come(x0 + i, j, 16 + i, j)
s.uscite = [((20, 36), 'Grotta dell\'Eremo 35.12'), ((7, 11), 'Nodo del Sale 35.14'),
            ((20, 3), "Nodo dell'Argilla 35.15"), ((17, 3), 'Sala di Bassi 35.16'),
            ((13, 3), 'Passo dei Draghi 35.18')]
s.oggetti = [(15, 4, 16, "incisione / escursionista"), (21, 34, 24, 'guida: Team Emilia e frane')]
s.cartelli = [(19, 33)]
STANZE.append(s)
# --- 35.14 Nodo del Sale
s = Stanza(14, 'Nodo del Sale', 339)
s.come(23, 3, 24, 3); s.come(23, 2, 24, 2); s.come(21, 9, 22, 9); s.come(21, 8, 22, 8)
s.uscite = [((7, 21), 'Grotta delle Sorgenti 35.13')]
s.oggetti = [(16, 4, 119, 'recluta del Team Emilia'), (16, 11, 24, 'conduttore del sale')]
STANZE.append(s)
# --- 35.15 Nodo dell'Argilla
s = Stanza(15, "Nodo dell'Argilla", 340)
s.uscite = [((12, 15), 'Grotta delle Sorgenti 35.13')]
s.oggetti = [(11, 12, 119, 'recluta del Team Emilia'), (10, 10, 24, "conduttore dell'argilla")]
STANZE.append(s)
# --- 35.16 Sala di Bassi
s = Stanza(16, 'Sala di Bassi', 337)
s.come(11, 23, 12, 23); s.come(11, 22, 12, 22)
s.uscite = [((17, 33), 'Grotta delle Sorgenti 35.13'), ((8, 2), 'Cuore del Fumaiolo 35.17')]
s.oggetti = [(10, 5, 196, 'BASSI'), (8, 3, 24, 'la porta profonda (dopo BASSI accompagna giù)'), (14, 31, 19, 'SOCCORSO (cura, MASTER BALL)')]
STANZE.append(s)
# --- 35.17 Cuore del Fumaiolo
s = Stanza(17, 'Cuore del Fumaiolo', 409)
s.uscite = [((5, 4), 'Sala di Bassi 35.16')]
s.oggetti = [(17, 25, 206, 'GROUDON'), (7, 22, 24, 'guida')]
STANZE.append(s)
# --- 35.18 Passo dei Draghi
s = Stanza(18, 'Passo dei Draghi', 292, 0, 0, 30, 41)
s.come(16, 18, 15, 18); s.come(16, 17, 15, 17)                                        # niente porta del covo
s.uscite = [((14, 40), 'Grotta delle Sorgenti 35.13'), ((15, 40), 'Grotta delle Sorgenti 35.13'),
            ((13, 5), 'Bagno di Romagna 35.19'), ((14, 5), 'Bagno di Romagna 35.19')]
s.oggetti = [(17, 38, 24, 'guida del passo'), (21, 9, 19, 'escursionista'), (8, 20, 59, 'strumento')]
s.lisce = True                                                 # si sale anche a piedi
s.barriera = [(14, 37), (15, 37)]                              # frane: si passa solo dopo Groudon
STANZE.append(s)


def valori(s):
    U = tela.Unione(d); v = s.T.valori(U)
    if s.lisce:
        for i, (refs, attr) in enumerate(U.meta):
            if attr & 0xff == 0xd1: U.meta[i] = (refs, attr & 0xff00)
    return U, v


def anteprima(s, scala=2):
    U, v = valori(s)
    im = tela.anteprima(d, U, v, s.w, s.h, scala)
    sprite.disegna(d, im, [(x, y, g) for x, y, g, _ in s.oggetti], scala)
    sprite.numeri(im, [(x, y, str(k + 1)) for k, (x, y, _, _) in enumerate(s.oggetti)], scala)
    dr = ImageDraw.Draw(im); q = 16 * scala
    for (x, y), _ in s.uscite: dr.rectangle((x * q, y * q, x * q + q - 1, y * q + q - 1), outline=(170, 40, 220), width=4)
    for (x, y) in s.cartelli: dr.rectangle((x * q, y * q, x * q + q - 1, y * q + q - 1), outline=(40, 170, 230), width=4)
    for (x, y) in s.barriera: dr.rectangle((x * q + 6, y * q + 6, x * q + q - 7, y * q + q - 7), outline=(230, 120, 0), width=3)
    return U, v, im


if __name__ == '__main__':
    out = Path(sys.argv[2])
    for s in STANZE:
        U, v, im = anteprima(s); im.save(out / ('stanza_35_%d.png' % s.n)); print(s.n, s.nome, s.w, s.h, U.stato())
