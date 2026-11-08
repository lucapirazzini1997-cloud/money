"""Bozza Lotto 4: interno della chiesa di Lido di Savio (mappa libera 24.75, nessuna uscita la raggiunge oggi).

Stesso tileset della chiesa di Cesena (34.37, layout 670): la navata e' piu' corta (righe 0-8 e 13-21 di Cesena,
18x18): altare, organo, balaustra, quattro file di banchi, acquasantiera e confessionale; uscita in (9,17) verso
la porta della chiesa a Lido (8,38).
Evento: il PARROCO (in 10,4) racconta la benedizione del mare e la prima volta regala un MAREAROMA (flag nuova);
alla finestra (5,1) l'ex voto dei pescatori del Savio.
Uso: python3 bozze/chiesa_lido.py ROM_071 CARTELLA
"""
import sys, struct
from pathlib import Path
sys.path[:0] = [str(Path(__file__).resolve().parent.parent / 'strumenti_rom')]
import numpy as np
import romlib

CESENA_CHIESA = (34, 37)
RIGHE = list(range(0, 9)) + list(range(13, 22))
PARROCO = (10, 4, 29)
USCITA = (9, 17)
EX_VOTO = (5, 1)
TESTI = dict(
    parroco="PARROCO: Ogni estate benediciamo il mare e le barche dei pescatori del SAVIO.\n\n"
            "Prendi questo MAREAROMA: è l'incenso della festa. Ai POKéMON d'acqua piace!",
    parroco_dopo="PARROCO: Che il mare ti sia sempre calmo, ovunque tu vada!",
    ex_voto="Una barca dipinta: è l'ex voto dei pescatori del SAVIO, tornati a casa dopo una burrasca.")


def chiesa(d):
    rom = romlib.Rom(bytes(d)); m = rom.map(*CESENA_CHIESA); a = rom.blocks(m)
    b = a[RIGHE, :].copy()
    return m, b


if __name__ == '__main__':
    import sprite
    from PIL import ImageDraw
    d = open(sys.argv[1], 'rb').read(); out = Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
    m, b = chiesa(d)
    r2 = romlib.Rom(bytes(d)); mm = dict(r2.map(*CESENA_CHIESA))
    mt = r2.renderer(mm); H, W = b.shape
    img = np.zeros((H * 16, W * 16, 3), np.uint8)
    for y in range(H):
        for x in range(W): img[y * 16:y * 16 + 16, x * 16:x * 16 + 16] = mt(int(b[y, x]) & 1023)
    from PIL import Image
    im = Image.fromarray(img)
    sprite.disegna(d, im, [PARROCO], 1)
    im = im.resize((W * 48, H * 48), 0); dr = ImageDraw.Draw(im)
    for (x, y), c in ((USCITA, (0, 255, 220)), (EX_VOTO, (255, 220, 0))):
        dr.rectangle((x * 48, y * 48, x * 48 + 47, y * 48 + 47), outline=c, width=3)
    im.save(out / 'chiesa_lido.png'); print(W, H)
    for k, t in TESTI.items(): print(k, t)
