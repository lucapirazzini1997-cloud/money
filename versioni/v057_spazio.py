"""Versione 0.57 - Lotto 1, prima parte: spazio recuperato. Non cambia il gioco.

Undici blocchi di zeri a cui non arriva nessun puntatore credibile e dentro cui non finisce nessuna struttura
nota vengono riempiti di 0xFF e aggiunti alle zone dell'engine (W.aggiungi_zone). L'elenco viene da
analisi/spazio.py lanciato sulla 0.56 (regole e margini nella sua intestazione); qui e' fissato, cosi' la
build non dipende dall'euristica, e ogni zona viene ricontrollata: deve essere ancora tutta a zero.
"""
import engine as E

# (inizio, fine) in offset di file; margine di 256 byte gia' compreso. Totale 671 KB.
ZONE_057 = [
    (0x391c14, 0x394ee6),   # 12 KB  dopo la grafica non compressa di un tileset (0x38d314)
    (0x47e5b4, 0x47fada),   # 5 KB   dopo gli attributi metatile a 0x47bfb0
    (0x502bf0, 0x5044c2),   # 6 KB   fra due strutture di tileset
    (0x55a408, 0x55bdfe),   # 6 KB   fra due strutture di tileset
    (0xb78f08, 0xba0208),   # 156 KB blocco 0xb6bcb4-0xc00000, 64 KB dopo l'ultimo bersaglio (0xb68e08)
    (0xbb09b8, 0xbbcccc),   # 48 KB  stesso blocco, 64 KB dopo 0xba08b8
    (0xbdcdcc, 0xbf59e0),   # 99 KB  stesso blocco, 64 KB dopo 0xbccccc
    (0xc98c28, 0xcbb500),   # 138 KB blocco 0xc98b26-0xd00000
    (0xccb600, 0xcdae40),   # 62 KB  stesso blocco, 64 KB dopo 0xcbb500
    (0xceaf40, 0xcf0300),   # 20 KB  stesso blocco, 64 KB dopo 0xcdae40
    (0xef3498, 0xf10000),   # 114 KB blocco 0xee4016-0xf10000, 64 KB dopo 0xee3398
]


def apply(W):
    prima = W.libere()
    for s, e in ZONE_057:
        assert not any(W.d[s:e]), 'zona %s non piu a zero: qualcuno la usa' % hex(s)
        W.d[s:e] = b'\xff' * (e - s)
    W.aggiungi_zone(ZONE_057, '0.57 blocchi di zeri')
    dopo = W.libere()
    return dict(zone=[[hex(s), hex(e), (e - s) // 1024] for s, e in ZONE_057],
                recuperati_kb=(dopo - prima) // 1024, liberi_prima_kb=prima // 1024, liberi_dopo_kb=dopo // 1024)
