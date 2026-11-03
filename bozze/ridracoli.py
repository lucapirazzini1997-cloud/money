"""Bozza 2 di Ridracoli (35.51): lago grande nelle Foreste Casentinesi.
Da sud: valle d'accesso con la strada -> centrale (porta verso 35.52) -> scala nel muro -> coronamento della diga ->
lago (SURF).  A nord-ovest il Bidente scende dalla cascata (sopra: la sorgente, solo con CASCATA); a nord-est entra
il Rio Celluzze; sulla riva est l'accampamento del Team Emilia, raggiungibile a piedi dal coronamento.
Pezzi: Percorso 114 (terrazze, cascata, lago, valle, casa), layout di 35.51 (la diga), primario (acqua, erba, strada).
Uso: python3 bozze/ridracoli.py ROM.gba uscita.png"""
import sys, struct
from pathlib import Path
sys.path[:0] = [str(Path(__file__).resolve().parent.parent / 'strumenti_rom')]
import tela, sprite
from PIL import ImageDraw
d = open(sys.argv[1], 'rb').read()
def lay(lid): return struct.unpack_from('<I', d, 0x627fc0 + (lid - 1) * 4)[0] - 0x8000000
L114 = lay(30)
a114, S114 = tela.Tela.layout(d, L114)
LR = struct.unpack_from('<I', d, 0x1e06e10)[0] - 0x8000000          # layout di 35.51 (diga)
W, H = 44, 62
T = tela.Tela(d, W, H, S114, 0x3001)
G, ALTA = 0x3001, 0x300d
def met(x, y, v, src=S114): T.metti(x, y, src, v)
def mt(x, y): return T.c[y][x][1] & 1023
def bosco(x, y, w, h, cima=True, base=True):
    for j in range(h):
        for i in range(w):
            k = (x + i) % 2
            if j % 2 == 0: v = (0x31ce + k) if (cima and j == 0) else (0x5d4 + k)
            else: v = (0x5e4 + k) if (base and j == h - 1) else (0x5dc + k)
            met(x + i, y + j, v)

# --- 1. foresta ovunque, poi i pezzi
bosco(0, 0, W, H, cima=False, base=False)
T.incolla(L114, 0, 0, 20, 21, 2, 0)                                 # terrazze, cascata del Bidente, laghetto
T.incolla(L114, 0, 21, 40, 13, 2, 21)                               # lago con l'isolotto
T.incolla(LR, 5, 18, 34, 5, 5, 34)                                  # la diga: coronamento (34-35) e muro (36-38)
T.incolla(L114, 0, 33, 40, 23, 2, 39)                               # valle d'accesso, con la casa (centrale)

# --- 2. il lago: maschera dell'acqua e rive ricalcolate (acqua del primario, come nel 114)
ACQUA_ID = {0x170, 0x189, 0x180, 0x181, 0x190, 0x192, 0x198, 0x19a, 0x178, 0x179, 0x2c0, 0x2c1, 0x2c8, 0x2c9, 0x28b, 0x293}
acqua = [[False] * W for _ in range(H)]
for y in range(21, 34):
    for x in range(W):
        acqua[y][x] = mt(x, y) in ACQUA_ID                       # il ponte del 114 diventa lago
def a(x, y, w, h):
    for j in range(h):
        for i in range(w): acqua[y + j][x + i] = True
a(31, 0, 4, 8)                                                      # Rio Celluzze, da nord
a(29, 8, 8, 1); a(26, 9, 12, 1); a(24, 10, 15, 11)                  # la baia di nord-est
a(9, 21, 30, 12); a(9, 33, 28, 1)                                   # lago pieno fino al muro della diga
for y in range(21, 34):
    for x in range(W):
        if acqua[y][x] and mt(x, y) not in ACQUA_ID and x < 9: acqua[y][x] = False
ISOLA = {(x, y) for y in range(25, 29) for x in range(12, 16)}      # l'isolotto del 114 resta
for (x, y) in ISOLA: acqua[y][x] = False
def w(x, y): return y < 0 or (0 <= x < W and y < H and acqua[y][x])
NE = lambda x, y: x >= 22 and y <= 33 and not (5 <= x <= 38 and y >= 34)
for y in range(0, 34):
    for x in range(W):
        if (x, y) in ISOLA: continue
        if w(x, y):
            if y < 21 and x < 22: continue                          # le acque del 114 a nord-ovest restano
            U, L, R = not w(x, y - 1), not w(x - 1, y), not w(x + 1, y)
            if U and L: v = 0x1180
            elif U and R: v = 0x1181
            elif U: v = 0x1189
            elif L: v = 0x1179 if w(x - 1, y - 1) else 0x1190
            elif R: v = 0x1178 if w(x + 1, y - 1) else 0x1192
            elif not w(x - 1, y - 1): v = 0x1198
            elif not w(x + 1, y - 1): v = 0x119a
            else: v = 0x1170
            met(x, y, v)
        elif NE(x, y):
            # riva d'erba: si toglie l'albero intero (2x2) se una sua casella tocca l'acqua
            bx, by = x - x % 2, y - y % 2
            vicino = any(0 <= by + j + jj < H and w(bx + i + ii, by + j + jj)
                         for i in (0, 1) for j in (0, 1) for ii in (-1, 0, 1) for jj in (-1, 0, 1)
                         if by + j + jj >= 0)
            if vicino: met(x, y, G)
# rive d'erba di nord-est: la foresta lascia una fascia larga 1-2 caselle; spiaggia dell'accampamento a est
for y in range(8, 34):
    for x in range(39, 42): met(x, y, G)
for y in range(34, 37):
    for x in range(39, 42): met(x, y, G)                            # dal coronamento si scende sulla riva est
for y in range(0, 34):
    for x in range(22, W):
        if mt(x, y) == 0x001 and w(x, y - 1): met(x, y, 0x3002)    # riva sotto l'acqua
bosco(42, 0, 2, 40, cima=False, base=False)

# --- 3. la valle: pulizia, strada dall'ingresso sud alla scala della diga e alla centrale
for y in (39, 40, 41):
    for x in range(2, 42):
        if mt(x, y) in ACQUA_ID or mt(x, y) in (0x002, 0x0d3, 0x0d4): met(x, y, G)
        if mt(x, y) in (0x179, 0x178): met(x, y, G)
BUCHE = {0x208}                                                     # buche delle basi segrete
for y in range(39, H):
    for x in range(1, W):
        if mt(x, y) in BUCHE: T.c[y][x] = T.c[y][x - 1]
def strada_v(x0, y0, y1):
    for y in range(y0, y1 + 1):
        r = 0 if y == y0 else 1
        for i in range(3): met(x0 + i, y, 0x3118 + 8 * r + i)
def strada_h(x0, x1, y):
    for x in range(x0, x1 + 1):
        e = 0 if x == x0 else (2 if x == x1 else 1)
        met(x, y, 0x3118 + e); met(x, y + 1, 0x3120 + e); met(x, y + 2, 0x3128 + e)
strada_v(23, 39, H - 1)                                             # dall'ingresso sud fino al muro
strada_h(23, 31, 44)                                                # davanti alla centrale
for y in (44, 45): met(23, y, 0x3120); met(24, y, 0x3121); met(25, y, 0x3121)
for y in (37, 38):
    for x in (23, 24, 25): met(x, y, 0x00af)                        # scala nel muro: dalla valle al coronamento
met(22, 39, 0x403)                                                  # cartello: DIGA DI RIDRACOLI
met(10, 2, 0x403)                                                   # cartello: SORGENTE DEL BIDENTE

U = tela.Unione(d); vals = T.valori(U); print(U.stato())
im = tela.anteprima(d, U, vals, W, H, 2)
OGGETTI = [
    (22, 27, None),     # 0 Gyarados rosso (cerchio)
    (31, 45, 55),       # 1 custode della diga, davanti alla centrale
    (21, 52, 31),       # 2 escursionista (allenatore) sulla strada della valle
    (12, 34, 49),       # 3 pescatore (allenatore) sul coronamento
    (31, 34, 119),      # 4 recluta del Team Emilia sul coronamento
    (40, 27, 119),      # 5 recluta del Team Emilia sulla riva est
    (40, 15, 196),      # 6 capo del Team Emilia all'accampamento
    (8, 4, 59),         # 7 strumento alla sorgente (solo con CASCATA)
]
sprite.disegna(d, im, [o for o in OGGETTI if o[2] is not None], 2)
sprite.numeri(im, [(x, y, str(k)) for k, (x, y, _) in enumerate(OGGETTI)], 2)
dr = ImageDraw.Draw(im)
gx, gy = OGGETTI[0][:2]
dr.ellipse([gx * 32 - 6, gy * 32 - 6, gx * 32 + 38, gy * 32 + 38], outline=(230, 20, 20), width=5)
dr.text((gx * 32 - 4, gy * 32 + 40), 'GYARADOS ROSSO', fill=(255, 255, 255))
im.save(sys.argv[2]); print(im.size)
