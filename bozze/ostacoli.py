"""Bozza 0.68 (Lotto 3, ostacoli): casa del protagonista (1.0) e Pineta del Savio (0.16).

- Casa 1.0: si entra dalla porta (uscita 1, casella 9,9) e la TV (8-9, 7-8) sta subito sopra: la TV si sposta di due
  caselle a sinistra (6-7, 7-8) e al suo posto torna il pavimento che c'era li' (il disegno del pavimento si ripete
  ogni 2 caselle, quindi resta allineato).
- Pineta 0.16: la Poke Ball (36,24) sta in una radura di sabbia chiusa da alberi e da una siepe (34-36, 25): si apre
  la siepe in (34,25) con l'erba bassa (metatile 0x001, come il resto del bosco), cosi' la radura si collega al
  sentiero (33,25).

Uso: python3 bozze/ostacoli.py ROM_067 CARTELLA   (scrive prima/dopo delle due mappe)
"""
import sys
from pathlib import Path
R_ = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(R_ / 'strumenti_rom')]
import struct, romlib

# (mappa, x, y, valore vecchio atteso, valore nuovo)
CASA = (1, 0)
PINETA = (0, 16)
MODIFICHE = [
    (CASA, 6, 7, 0x3261, 0x3663), (CASA, 7, 7, 0x3262, 0x3664),
    (CASA, 6, 8, 0x326f, 0x3671), (CASA, 7, 8, 0x3270, 0x3672),
    (CASA, 8, 7, 0x3663, 0x3261), (CASA, 9, 7, 0x3664, 0x3262),
    (CASA, 8, 8, 0x3671, 0x326f), (CASA, 9, 8, 0x3672, 0x3270),
    (PINETA, 34, 25, 0x3616, 0x3001),
]


def applica(d, rom):
    for k, x, y, vecchio, nuovo in MODIFICHE:
        m = rom.map(*k); p = m['blocks'] + (y * m['width'] + x) * 2
        assert struct.unpack_from('<H', d, p)[0] == vecchio, (k, x, y)
        struct.pack_into('<H', d, p, nuovo)


if __name__ == '__main__':
    rom, out = sys.argv[1], Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
    A = romlib.Rom(rom); B = romlib.Rom(rom); applica(B.data, B)
    for k, nome, box in [(CASA, 'casa', None), (PINETA, 'pineta', (26, 16, 40, 30))]:
        for R, f in [(A, 'prima'), (B, 'dopo')]:
            im = R.render(R.map(*k), events=True, scale=2)
            if box: im = im.crop(tuple(v * 32 for v in box))
            im.save(out / ('%s_%s.png' % (nome, f)))
    print('ok')
