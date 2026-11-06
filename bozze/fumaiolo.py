"""Bozza del nuovo Sentiero del Fumaiolo (35.10), 40x100.
Si entra dal basso (da Cesena) e si risale il Savio verso la cima. Dal basso:
prati con erba alta e un altopiano di roccia -> il fiume si allarga -> cascata, ponte di tronchi
e, a ovest, il colle dell'Eremo di Sant'Alberico con la grotta (ingresso del santuario, chiusa da un
masso: FORZA) -> strada a est fino al rifugio -> lago con gli scogli -> ponte lungo e seconda cascata
-> in cima, a ovest, la sorgente del Tevere con la stele.
Pezzi rimescolati del Percorso 119 (la parte bassa del 119 sta in cima, la parte alta in basso,
senza pontili e senza l'istituto) e il colle con la grotta del Percorso 120.
Uso: python3 bozze/fumaiolo.py ROM.gba uscita.png"""
import sys
from pathlib import Path
sys.path[:0] = [str(Path(__file__).resolve().parent.parent / 'strumenti_rom')]
import tela, sprite
from PIL import ImageDraw
d = open(sys.argv[1], 'rb').read()
L119, L120 = 0x585d30, 0x587c90
a119, S119 = tela.Tela.layout(d, L119)
W, H = 40, 100
SU = 40                                   # righe della parte alta (119 righe 72-111)
T = tela.Tela(d, W, H, S119, 0x3001)
def met(x, y, v): T.metti(x, y, S119, v)
def mt(x, y): return T.c[y][x][1] & 1023
def bosco(x, y, w, h):
    for j in range(h):
        for i in range(w): met(x + i, y + j, 0x4c7 if (y + j) % 2 else 0x4c6)

# --- 1. i due pezzi del 119, invertiti
T.incolla(L119, 0, 72, 40, SU, 0, 0)       # cima: seconda cascata, ponte lungo, lago con scogli, casa
T.incolla(L119, 0, 0, 40, H - SU, 0, SU)    # sotto: lago dei pontili, prima cascata, ponte, altopiano
# --- 2. niente pontili; l'acqua decorativa del 119 (0x206, non navigabile) diventa acqua normale
for y in range(H):
    for x in range(W):
        if 0xec <= mt(x, y) <= 0xfd or mt(x, y) == 0x206: met(x, y, 0x1170)
bosco(0, 32, 4, 8)                          # il lago della cima non esce dal bordo sinistro
for y in range(H):                          # buche e grotte delle basi segrete
    for x in range(1, W):
        if mt(x, y) in (0x208, 0x1b0): T.c[y][x] = T.c[y][x - 1]
for y in range(38, 46):                     # sentiero dal rifugio alla strada di destra
    for x in range(28, 34): met(x, y, 0x3001)
# --- 3. il colle dell'Eremo (Percorso 120) al posto dell'istituto, alla quota del terreno intorno (4)
T.incolla(L120, 0, 50, 12, 10, 0, SU + 26)
for y in range(SU + 26, SU + 36):
    for x in range(12):
        sec, v = T.c[y][x]
        if v >> 12 == 3 and not (v >> 10) & 3: T.c[y][x] = (sec, (v & 0x0fff) | 0x4000)
        if 0xc8 <= mt(x, y) <= 0xda: met(x, y, 0x4001)      # niente pozzanghere intorno all'Eremo
# --- 4. ingresso da Cesena in basso: stradina nel bosco fino alla scala dell'altopiano, cartello e bacheca
for y in range(94, H):
    for x in range(16, 23): met(x, y, 0x3001)
    r = 0 if y == 94 else 1
    for i in range(3): met(18 + i, y, 0x3118 + 8 * r + i)
met(17, 98, 0x403)                          # bacheca della Valle del Savio
met(21, 98, 0x403)                          # cartello: SENTIERO DEL FUMAIOLO
met(28, SU + 9, 0x3001)                     # tolgo il primo cartello del 119 (l'altro resta: RIFUGIO)
met(10, 4, 0x403)                           # stele della sorgente del Tevere (in gioco: disegno mio)

USCITE = [((18, 99), 'Cesena'), ((19, 99), 'Cesena'), ((20, 99), 'Cesena'),
          ((7, 71), 'santuario 35.12'), ((33, 37), 'rifugio 35.11')]
CARTELLI = [(17, 98), (21, 98), (27, 59), (10, 4)]
OGGETTI = [   # (x, y, gfx, cosa) - gli stessi oggetti di oggi, nei punti nuovi
    (21, 96, 24, 'guida del sentiero'),
    (9, 73, 16, 'escursionista: il santuario'),
    (7, 72, 87, 'masso (FORZA) davanti alla grotta'),
    (27, 78, 135, 'ALDO (lotta in coppia)'),
    (5, 73, 16, 'missione di FORZA'),
    (8, 2, 59, 'strumento alla sorgente del Tevere'),
    (17, 96, 24, 'guida per Ridracoli'),
]

if __name__ == '__main__':
    U = tela.Unione(d); vals = T.valori(U); print(U.stato())
    im = tela.anteprima(d, U, vals, W, H, 2)
    sprite.disegna(d, im, [(x, y, g) for x, y, g, _ in OGGETTI], 2)
    sprite.numeri(im, [(x, y, str(k + 1)) for k, (x, y, _, _) in enumerate(OGGETTI)], 2)
    dr = ImageDraw.Draw(im)
    for (x, y), _ in USCITE: dr.rectangle((x * 32, y * 32, x * 32 + 31, y * 32 + 31), outline=(170, 40, 220), width=4)
    for (x, y) in CARTELLI: dr.rectangle((x * 32, y * 32, x * 32 + 31, y * 32 + 31), outline=(40, 170, 230), width=4)
    im.save(sys.argv[2]); print(im.size)
