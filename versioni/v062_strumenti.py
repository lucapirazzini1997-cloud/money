"""Versione 0.62 - Lotto 3, prima parte: le MN e gli strumenti chiave si ottengono tutti, con testi in italiano.

Analisi (analisi/doni.py sulla 0.61: chi consegna ogni strumento, seguendo gli script di tutte le mappe):
  CASCATA     Safari Ravenna 26.3, oggetto 1, con l'8a medaglia (flag 0x630)
  SUB         Bagno di Romagna 35.26, oggetto 4, con l'8a medaglia (flag 0x4E6)
  BICI CROSS  Cesenatico 34.42, oggetto 2 (flag 0x629)
  AMO VECCHIO Cesenatico 34.22, oggetto 4 (0x26F); AMO BUONO Rimini 34.44, oggetto 5;
  SUPER AMO   Ravenna 34.96, oggetto 13, con la 5a medaglia (flag 0x62F)
  FLASH       solo il montanaro di Smeraldo nella Grotta Granito 24.7 (dall'Appennino Romagnolo 0.21), in inglese
Tutti si ottengono; cambiano solo i testi:
  - montanaro di FLASH (24.7): testi in italiano (stesso script, stessa flag 0x6D);
  - sommozzatore di SUB (35.26): i testi prima e dopo la consegna avevano riquadri di 3-4 righe
    (trovati con analisi/righe.py, che controlla anche gli altri doni: nessun altro testo oltre le 2 righe).
"""
import struct
import engine as E
from engine import H, P, B, Script

OUT = {}


def ripunta(W, at, testo):
    """loadword 0 (0f 00 <ptr>) gia' esistente: nuovo testo, stesso script."""
    assert W.d[at] == 0x0f and W.d[at + 1] == 0x00, hex(at)
    struct.pack_into('<I', W.d, at + 2, B + W.text(testo))


def apply(W):
    d = W.d
    # ---- FLASH: montanaro della Grotta Granito (24.7, oggetto 1)
    assert struct.unpack_from('<H', d, 0x22de20)[0] == 0x157
    ripunta(W, 0x22de15, "Ehi, tu! Più avanti la grotta\nè buia come la notte.\n\n"
                         "Tieni questa MN: con FLASH\nnon ti perderai nel buio.")
    dopo = "Insegna FLASH a un POKéMON e\nusala fuori dalla lotta.\n\nIlluminerà anche le grotte\npiù scure della ROMAGNA."
    ripunta(W, 0x22de2c, dopo)
    ripunta(W, 0x22de36, dopo)
    OUT['flash'] = 'testi tradotti (24.7 oggetto 1, flag 0x6D)'

    # ---- SUB: il testo dopo la consegna aveva riquadri di 3-4 righe (35.26, oggetto 4)
    assert struct.unpack_from('<H', d, 0x1731363)[0] == 0x15a
    ripunta(W, 0x173136f, "Con SUB ti immergi nelle\nacque scure del mare aperto.\n\n"
                          "Al largo di RIMINI ci sono i\nresti dell'ISOLA DELLE ROSE.\n\n"
                          "I pescatori dicono che laggiù\ndorme un POKéMON enorme.")
    ripunta(W, 0x1731379, "Sono un sommozzatore della\nriviera.\n\n"
                          "Batti LEDA e ti insegnerò a\nscendere sul fondo del mare.")
    OUT['sub'] = 'testi prima e dopo la consegna in riquadri di due righe (35.26 oggetto 4)'
    return OUT
