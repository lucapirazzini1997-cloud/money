"""Versione 0.68 - Lotto 3: ostacoli (bozza bozze/ostacoli.py, approvata).

Prima (0.67):
  - Casa del protagonista (1.0): si entra dalla porta sulla casella (9,9) e la TV (8-9, 7-8) sta subito sopra:
    il primo passo e' bloccato, bisogna girarle attorno.
  - Pineta del Savio (0.16): la Poke Ball (oggetto 7, 36,24) sta in una radura di sabbia chiusa da alberi e
    dalla siepe (34-36, 25): non si raggiunge, nemmeno con tutte le abilita' (analisi/percorso.py).

Dopo (0.68):
  - la TV si sposta di due caselle a sinistra (6-7, 7-8); al suo posto il pavimento (il disegno si ripete ogni
    2 caselle, resta allineato);
  - la siepe si apre in (34,25) con l'erba bassa del bosco (metatile 0x001): la radura si collega al sentiero.
Solo blocchi delle due mappe, sul posto (i due layout non sono condivisi). Niente flag, variabili, testi.
"""
import struct
import romlib

CASA, PINETA = (1, 0), (0, 16)
# (mappa, x, y, valore atteso, valore nuovo): gli stessi di bozze/ostacoli.py
MODIFICHE = [
    (CASA, 6, 7, 0x3261, 0x3663), (CASA, 7, 7, 0x3262, 0x3664),       # TV a sinistra
    (CASA, 6, 8, 0x326f, 0x3671), (CASA, 7, 8, 0x3270, 0x3672),
    (CASA, 8, 7, 0x3663, 0x3261), (CASA, 9, 7, 0x3664, 0x3262),       # pavimento dove era la TV
    (CASA, 8, 8, 0x3671, 0x326f), (CASA, 9, 8, 0x3672, 0x3270),
    (PINETA, 34, 25, 0x3616, 0x3001),                                   # siepe aperta
]


def apply(W):
    tutte = romlib.all_maps(W.rom)
    for k in (CASA, PINETA):                       # layout non condivisi: si modifica sul posto
        m = tutte[k]
        assert [o for o, mm in tutte.items() if mm['blocks'] == m['blocks'] or mm['layout_id'] == m['layout_id']] == [k], k
    for k, x, y, vecchio, nuovo in MODIFICHE:
        m = tutte[k]; p = m['blocks'] + (y * m['width'] + x) * 2
        assert struct.unpack_from('<H', W.d, p)[0] == vecchio, (k, x, y)
        struct.pack_into('<H', W.d, p, nuovo)
    return dict(modifiche=[dict(mappa='%d.%d' % k, x=x, y=y, prima=hex(a), dopo=hex(b)) for k, x, y, a, b in MODIFICHE])
