"""0.67: gli 8 tile del primario presi per il cartello non si vedono in nessun'altra mappa.
Disegna tutte le mappe della 0.66 e della 0.67 (senza eventi) e riporta quelle diverse.
Attese: le 5 citta' (e i loro alias nel gruppo 33, che puntano alla stessa intestazione) (solo le 4 caselle del cartello), le 5 sale e la carrozza (mappe nuove).
Uso: python3 collaudo/primario_067.py ROM_066 ROM_067"""
import sys
from pathlib import Path
sys.path[:0] = [str(Path(__file__).resolve().parent.parent / 'strumenti_rom')]
import numpy as np, romlib
A, B = romlib.Rom(sys.argv[1]), romlib.Rom(sys.argv[2])
NUOVE = {(24, 39), (24, 40), (24, 41), (24, 50), (24, 51), (24, 74)}
CITTA = {(34, 17), (34, 47), (34, 68), (34, 85), (35, 1)}
diverse, errori, n = [], [], 0
for k in romlib.all_maps(B):
    try:
        ma, mb = A.map(*k), B.map(*k)
        ia, ib = np.array(A.render(ma, events=False)), np.array(B.render(mb, events=False))
    except Exception as e:
        errori.append((k, str(e)[:60])); continue
    n += 1
    if ia.shape != ib.shape or (ia != ib).any(): diverse.append(k)
hdr = {B.map(*k)['header'] for k in NUOVE | CITTA}
alias = [k for k in diverse if k not in NUOVE | CITTA and B.map(*k)['header'] in hdr]   # stessi header (gruppo 33 = 34)
inattese = [k for k in diverse if k not in NUOVE | CITTA and k not in alias]
print('mappe disegnate', n, 'non disegnabili', len(errori))
print('diverse', sorted(diverse))
print('alias delle citta\' (stessa intestazione)', alias)
print('diverse inattese', inattese)
print('OK' if not inattese else 'DIFFERENZE')
