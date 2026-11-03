"""Bozza 2 di Monte Spaccato: campagna in pianura (pezzi del Percorso 117) e il monte a nord-ovest (Percorso 116)."""
import sys, struct
sys.path[:0] = ['/home/user/money/strumenti_rom']
import tela
from PIL import ImageDraw
d = open('/home/user/money/out/Pokemon_Romagna_0_63.gba', 'rb').read()
def lay(lid): return struct.unpack_from('<I', d, 0x627fc0 + (lid - 1) * 4)[0] - 0x8000000
L116, L117 = lay(32), lay(33)
a116, S116 = tela.Tela.layout(d, L116); a117, S117 = tela.Tela.layout(d, L117)
W, H = 64, 40
G = 0x3001                                                     # erba (primario, quota 3)
T = tela.Tela(d, W, H, S117, G)
def met(x, y, v, src=S117): T.metti(x, y, src, v)
def blocco(lid, x0, y0, w, h, x, y): T.incolla({116: L116, 117: L117}[lid], x0, y0, w, h, x, y)
def bosco(x, y, w, h, cima=True, base=True):
    """Alberi 2x2 del primario: chioma su erba in cima, tronco su erba in fondo."""
    for j in range(h):
        for i in range(w):
            k = i % 2; r = j % 2
            if r == 0: v = (0x1ce + k) if (cima and j == 0) else (0x5d4 + k)
            else: v = (0x5e4 + k) if (base and j == h - 1) else (0x5dc + k)
            if r == 0 and not (cima and j == 0): v = 0x5d4 + k
            met(x + i, y + j, v | (0x3000 if v < 0x400 else 0))
# --- il monte a nord-ovest, con la spaccatura a V e la galleria verso Capocolle (25,11)
blocco(116, 41, 0, 33, 13, 1, 0)
# --- bordo: bosco
bosco(0, 0, 2, 40, cima=False, base=False); bosco(62, 0, 2, 40, cima=False, base=False)
bosco(34, 0, 28, 6, cima=False); bosco(0, 36, 64, 4, base=False)
bosco(34, 6, 2, 8, cima=False, base=True)                       # copre il taglio del monte
# --- strada (Via Emilia): dalla casa verso ovest, poi a nord fino alla galleria
def strada_h(x0, x1, y):
    for x in range(x0, x1 + 1):
        e = 0 if x == x0 else (2 if x == x1 else 1)
        met(x, y, 0x3118 + e); met(x, y + 1, 0x3120 + e); met(x, y + 2, 0x3128 + e)
def strada_v(x, y0, y1):
    for y in range(y0, y1 + 1):
        met(x, y, 0x3120); met(x + 1, y, 0x3121); met(x + 2, y, 0x3122)
strada_v(24, 12, 24); strada_h(24, 58, 23)
met(24, 12, 0x3118); met(25, 12, 0x3119); met(26, 12, 0x311a)
for y in (23, 24): met(25, y, 0x3121); met(26, y, 0x3121)
met(24, 23, 0x3120); met(24, 24, 0x3120)
# --- casa a est: ingresso dall'IPPODROMO (porta 51,5 del 117 -> 55,22)
blocco(117, 49, 1, 6, 5, 53, 18)
# --- campagna: vigneti e frutteti recintati, maceri, erba alta, filari
blocco(117, 7, 3, 9, 5, 4, 16)                                  # frutteto ovest
blocco(117, 8, 13, 10, 5, 4, 28)                                # vigneto sud-ovest
blocco(117, 8, 13, 10, 5, 46, 29)                               # vigneto sud-est
blocco(117, 7, 3, 9, 5, 36, 29)
blocco(117, 20, 1, 11, 8, 15, 27)                               # macero grande
blocco(117, 28, 13, 4, 5, 29, 15); blocco(117, 28, 13, 4, 5, 32, 16)                               # erba alta
blocco(117, 17, 13, 3, 4, 17, 17)
blocco(117, 31, 5, 18, 1, 30, 27)                               # staccionata lungo i campi
for x in (38, 44, 50):                                          # alberi isolati lungo la strada
    bosco(x, 20, 2, 2)
for (x, y) in ((7, 7), (7, 8), (16, 6), (30, 4), (31, 4)):                       # via la seconda grotta e le buche
    T.c[y][x] = T.c[y][x - 1]
T.riempi(14, 32, 4, 3, S117, G)
# angolo nord-est: frutteto, erba alta, alberi
blocco(117, 7, 3, 9, 5, 39, 7); blocco(117, 8, 13, 10, 5, 50, 7)
blocco(117, 28, 13, 4, 5, 41, 14); blocco(117, 28, 13, 4, 5, 44, 15)
for x in (37, 48): bosco(x, 13, 2, 2)
U = tela.Unione(d); vals = T.valori(U); print(U.stato())
im = tela.anteprima(d, U, vals, W, H, 2)
dr = ImageDraw.Draw(im)
dr.ellipse([25 * 32 + 4, 11 * 32 + 4, 25 * 32 + 27, 11 * 32 + 27], outline=(255, 0, 0), width=4)
im.save('out/pianura.png'); print(im.size)
