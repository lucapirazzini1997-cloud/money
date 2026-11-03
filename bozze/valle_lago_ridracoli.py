"""Bozza di Monte Spaccato: base Percorso 114 (colline, vigneti, lago, valle), casette di Romagna."""
import sys, struct
sys.path[:0] = ['/home/user/money/strumenti_rom']
import tela
from PIL import ImageDraw
d = open('/home/user/money/out/Pokemon_Romagna_0_63.gba', 'rb').read()
L114 = struct.unpack_from('<I', d, 0x627fc0 + 29 * 4)[0] - 0x8000000
LMS = 0x15998b4                       # Monte Spaccato attuale (casette)
a114, S114 = tela.Tela.layout(d, L114)
ams, SMS = tela.Tela.layout(d, LMS)
W, H = 40, 64
T = tela.Tela(d, W, H, S114, int(a114[0, 0]))
T.incolla(L114, 0, 0, 40, 58, 0, 0)                       # colline, vigneti, lago, ponte, valle
# fondo: bosco, corridoio d'ingresso e casetta IPPODROMO
albero = [[int(ams[0, 0]), int(ams[0, 1])], [int(ams[1, 0]), int(ams[1, 1])]]   # albero 2x2 del bordo
for y in range(58, 64, 2):
    for x in range(0, 40, 2):
        for j in range(2):
            for i in range(2): T.metti(x + i, y + j, SMS, albero[j][i])
erba = int(ams[3, 3])
T.riempi(18, 57, 6, 7, SMS, erba)                         # corridoio fino al fondo
T.incolla(L114, 25, 33, 5, 5, 22, 57)                      # casa dal tetto rosso del 114 = ingresso dall'IPPODROMO
T.riempi(18, 62, 10, 2, SMS, erba)
# via le buche delle basi segrete (casella del pianoro accanto)
for (x, y) in ((9, 47), (30, 51), (32, 57)):
    T.c[y][x] = T.c[y][x - 1]
U = tela.Unione(d)
vals = T.valori(U)
print(U.stato())
im = tela.anteprima(d, U, vals, W, H, 2)
dr = ImageDraw.Draw(im)
for x, y in ((19, 56), (20, 56), (21, 56), (22, 56)):        # rocce proposte
    dr.ellipse([x * 32 + 4, y * 32 + 4, x * 32 + 27, y * 32 + 27], outline=(255, 0, 0), width=4)
im.save('out/bozza_monte_spaccato.png')
print(im.size)
