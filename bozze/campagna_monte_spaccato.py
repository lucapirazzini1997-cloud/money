"""Bozza 3 della Campagna Cesenate (oggi 35.101 MONTE SPACCATO): pianura fra l'Ippodromo e Capocolle.
Pezzi: Percorso 117 (campi recintati, macero, casa, strada), Percorso 116 (il Monte Spaccato a nord-ovest con la
galleria verso Capocolle), Percorso 119 (assi del ponte), primario (erba, erba alta, alberi, acqua, argini).
Uso: python3 bozze/campagna_monte_spaccato.py ROM.gba uscita.png
"""
import sys, struct
from pathlib import Path
sys.path[:0] = [str(Path(__file__).resolve().parent.parent / 'strumenti_rom')]
import tela, sprite
from PIL import ImageDraw

d = open(sys.argv[1], 'rb').read()
def lay(lid): return struct.unpack_from('<I', d, 0x627fc0 + (lid - 1) * 4)[0] - 0x8000000
L116, L117, L119 = lay(32), lay(33), lay(35)
_, S117 = tela.Tela.layout(d, L117); _, S119 = tela.Tela.layout(d, L119); _, S116 = tela.Tela.layout(d, L116)
W, H = 64, 40
G, ALTA = 0x3001, 0x300d                                        # erba, erba alta (primario, quota 3)
RIVA_S, ACQUA, RIVA_D = 0x1190, 0x1170, 0x1192                  # fiume (primario, quota 1, come il lago del 114)
PONTE_A, PONTE_B = 0xf210, 0xf218                               # assi del ponte (Percorso 119, quota libera)
T = tela.Tela(d, W, H, S117, G)
def met(x, y, v, src=S117): T.metti(x, y, src, v)
def blocco(src, x0, y0, w, h, x, y): T.incolla(src, x0, y0, w, h, x, y)
def bosco(x, y, w, h, cima=True, base=True):
    for j in range(h):
        for i in range(w):
            k = i % 2
            if j % 2 == 0: v = (0x31ce + k) if (cima and j == 0) else (0x5d4 + k)
            else: v = (0x5e4 + k) if (base and j == h - 1) else (0x5dc + k)
            met(x + i, y + j, v)
def erba_alta(x, y, w, h): T.riempi(x, y, w, h, S117, ALTA)

# --- il Monte Spaccato a nord-ovest, con la spaccatura a V e la galleria (25,10) verso Capocolle
blocco(L116, 41, 0, 33, 13, 1, 0)
for (x, y) in ((7, 7), (7, 8), (16, 6), (30, 4), (31, 4)):      # via la seconda grotta e le buche
    T.c[y][x] = T.c[y][x - 1]
# --- il monte prosegue verso est (stesso Percorso 116, stesso scarto di colonne): niente taglio netto
blocco(L116, 74, 0, 26, 11, 34, 0)
for x in range(39, 62): met(x, 11, 0x079, S116)                  # piede del monte
for y in range(0, 12): met(60, y, 0x072, S116); met(61, y, 0x0a2, S116)
for y in range(0, 12):
    for x in range(34, 61):
        if (T.c[y][x][1] & 1023) in (0x0e1, 0x1b0, 0x0af): T.c[y][x] = (S116, 0x071)   # via buche e massi
# --- bosco ai bordi
bosco(0, 0, 2, 40, cima=False, base=False); bosco(62, 0, 2, 40, cima=False, base=False)
bosco(0, 36, 64, 4, base=False)
# --- campagna ovest: frutteto, erba alta, macero, vigneto
blocco(L117, 7, 3, 9, 5, 3, 14)
erba_alta(13, 14, 9, 7)
blocco(L117, 20, 1, 11, 8, 12, 27)
T.riempi(11, 32, 4, 3, S117, G)                                # avanzo di sabbia del ritaglio
blocco(L117, 8, 13, 10, 5, 2, 29)
erba_alta(3, 21, 8, 6)
# --- campagna centrale: grande prato d'erba alta, filare, vigneti
erba_alta(28, 13, 15, 7)
for x in (29, 33, 37, 41): bosco(x, 20, 2, 2)
blocco(L117, 7, 3, 9, 5, 27, 28); blocco(L117, 7, 3, 9, 5, 34, 28)
erba_alta(27, 33, 16, 3)
# --- il fiume (da nord a sud) e il ponte della Via Emilia
for y in range(12, 40):                                         # fino al bordo sud, sotto il bosco
    met(44, y, RIVA_S); met(49, y, RIVA_D)
    for x in range(45, 49): met(x, y, ACQUA)
for y in range(0, 11):                                          # la sorgente: cascata giu' dal monte
    for x in range(45, 49): met(x, y, 0x10b9)
for x, v in zip(range(45, 49), (0x102c, 0x1034, 0x1034, 0x103c)): met(x, 11, v)
# --- campagna est: campo, erba alta
blocco(L117, 8, 13, 10, 5, 51, 12)
erba_alta(51, 27, 10, 9)
# --- casa a est: ingresso dall'IPPODROMO (porta a 55,22)
blocco(L117, 49, 1, 6, 5, 53, 18)
# --- Via Emilia: dalla casa verso ovest, ponte sul fiume, poi a nord fino alla galleria
def strada_h(x0, x1, y):
    for x in range(x0, x1 + 1):
        e = 0 if x == x0 else (2 if x == x1 else 1)
        met(x, y, 0x3118 + e); met(x, y + 1, 0x3120 + e); met(x, y + 2, 0x3128 + e)
strada_h(24, 58, 23)
for y in range(12, 25): met(24, y, 0x3120); met(25, y, 0x3121); met(26, y, 0x3122)
met(24, 12, 0x3118); met(25, 12, 0x3119); met(26, 12, 0x311a)
for y in (23, 24): met(25, y, 0x3121); met(26, y, 0x3121)
for x in range(43, 51):
    met(x, 23, PONTE_A, S119); met(x, 24, PONTE_B, S119)
met(44, 25, RIVA_S); met(49, 25, RIVA_D)
for x in range(45, 49): met(x, 25, ACQUA)
# cartelli: MONTE SPACCATO (8,9, gia' nel pezzo del 116), CAMPAGNA CESENATE accanto alla casa (52,22, gia' nel 117)
met(42, 22, 0x403)                                              # cartello del ponte

U = tela.Unione(d); vals = T.valori(U); print(U.stato())
im = tela.anteprima(d, U, vals, W, H, 2)
OGGETTI = [
    (25, 11, 86),                                               # roccia di SPACCAROCCIA davanti alla galleria
    (16, 17, 36),                                               # anziano (allenatore di oggi)
    (27, 16, 7),                                                # ragazzino, accanto alla strada
    (34, 15, 31),                                               # ragazzo di campagna, nell'erba alta
    (43, 13, 49),                                               # pescatore sulla riva del fiume
    (38, 26, 24),                                               # ragazza, lungo il vigneto
    (55, 30, 33),                                               # uomo col cappello, nell'erba alta a est
]
sprite.disegna(d, im, OGGETTI, 2)
sprite.numeri(im, [(x, y, str(k)) for k, (x, y, _) in enumerate(OGGETTI)], 2)
im.save(sys.argv[2]); print(im.size)
