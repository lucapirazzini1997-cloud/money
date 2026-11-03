"""Bozza di Ridracoli (35.51): lago grande nelle Foreste Casentinesi (Percorso 114, senza ponte), la diga di oggi,
la centrale (casa del 114) e la valle d'accesso.  Uso: python3 bozze/ridracoli.py ROM.gba uscita.png"""
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
W, H = 44, 58
T = tela.Tela(d, W, H, S114, 0x3001)
def met(x, y, v, src=S114): T.metti(x, y, src, v)
def bosco(x, y, w, h, cima=True, base=True):
    for j in range(h):
        for i in range(w):
            k = i % 2
            if j % 2 == 0: v = (0x31ce + k) if (cima and j == 0) else (0x5d4 + k)
            else: v = (0x5e4 + k) if (base and j == h - 1) else (0x5dc + k)
            met(x + i, y + j, v)
bosco(0, 0, W, H, cima=False, base=False)                           # foresta ovunque, poi i pezzi
T.incolla(L114, 0, 0, 18, 21, 2, 0)                                 # terrazze, cascata, torrente che entra nel lago
T.incolla(L114, 0, 21, 40, 13, 2, 21)                               # lago, isolotto
ACQUA = int(a114[25, 15])
for y in range(21, 34):
    for x in range(19, 23): met(x + 2, y, ACQUA)                    # via il ponte: lago intero
bosco(20, 0, 22, 21, cima=False)                                    # foresta a nord-est, fino alla riva
for x in range(9, 36): met(x, 33, ACQUA)                            # il lago arriva al muro della diga
T.incolla(LR, 5, 18, 34, 5, 5, 34)                                  # la diga: coronamento e muro
T.incolla(L114, 0, 37, 40, 21, 2, 39)                               # valle d'accesso fra le rocce
T.incolla(L114, 25, 33, 5, 5, 20, 40)                               # centrale (casa del 114), sotto la diga
for y in (37, 38): met(24, y, 0x00af); met(25, y, 0x00af)          # scala nel muro: dalla valle al coronamento
for (x, y) in ((11, 47), (32, 51), (34, 57)):                       # buche delle basi segrete
    T.c[y][x] = T.c[y][x - 1]
U = tela.Unione(d); vals = T.valori(U); print(U.stato())
im = tela.anteprima(d, U, vals, W, H, 2)
sprite.disegna(d, im, [(20, 45, 55), (10, 42, 31), (30, 48, 49)], 2)  # custode, due allenatori
dr = ImageDraw.Draw(im)
gx, gy = 22, 27                                                     # Gyarados rosso, al largo dell'isolotto
dr.ellipse([gx * 32 - 6, gy * 32 - 6, gx * 32 + 38, gy * 32 + 38], outline=(230, 20, 20), width=5)
dr.text((gx * 32 - 4, gy * 32 + 40), 'GYARADOS ROSSO', fill=(255, 255, 255))
im.save(sys.argv[2]); print(im.size)
