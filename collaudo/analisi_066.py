"""0.66: percorsi a piedi (analisi/percorso.py) nel nuovo Fumaiolo, dall'arrivo da Cesena (35.10, 19,97).
Per ogni gruppo di abilita': caselle raggiunte per mappa e mete principali (accanto).
Il percorso non legge gli script: la porta profonda (35.16 -> 35.17) e le frane (35.18) sono script; qui la porta
risulta passabile perche' l'uscita e' su una casella calpestabile (in gioco si entra solo con il guardiano).
Uso: python3 collaudo/analisi_066.py ROM"""
import sys
from pathlib import Path
R_ = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(R_ / 'analisi'), str(R_ / 'strumenti_rom')]
import romlib, percorso as PC
R = romlib.Rom(sys.argv[1])
METE = {'rifugio 35.11': ((35, 11), None), 'grotta dell\'Eremo 35.12': ((35, 12), None),
        'Grotta delle Sorgenti 35.13': ((35, 13), None), 'Nodo del Sale (recluta 16,4)': ((35, 14), (16, 4)),
        'Nodo dell\'Argilla (recluta 11,12)': ((35, 15), (11, 12)), 'BASSI (10,5)': ((35, 16), (10, 5)),
        'guardiano della porta (9,3)': ((35, 16), (9, 3)), 'Passo dei Draghi': ((35, 18), None),
        'Bagno di Romagna 35.19': ((35, 19), None), 'stele del Tevere (10,4)': ((35, 10), (10, 4))}
for ab in ((), ('forza',), ('surf',), ('surf', 'forza')):
    st = PC.cerca(R, ((35, 10), (19, 97)), set(ab))
    per = {}
    for (k, x, y, z, s) in st: per.setdefault(k, set()).add((x, y))
    print('abilita', ab or '(nessuna)')
    print('  caselle:', {'%d.%d' % k: len(v) for k, v in sorted(per.items()) if k[0] == 35 and 10 <= k[1] <= 19})
    for nome, (k, xy) in METE.items():
        c = per.get(k, set())
        ok = bool(c) if xy is None else any((xy[0] + dx, xy[1] + dy) in c for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        print('   %-36s %s' % (nome, 'si' if ok else 'no'))
