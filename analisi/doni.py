"""Dove si ottengono gli strumenti (MN, bici, ami...): per ogni mappa reale segue gli script
(oggetti, cartelli, coordinate, script di mappa, con call/goto) e annota setorcopyvar 0x8000 <item>
seguito da callstd 0/1 (giveitem / finditem) e additem.  Gli item ball (callstd 1) hanno la flag
nell'oggetto.  Uso: python3 analisi/doni.py ROM.gba [id_strumento ...]
Dice dove c'e' lo script, non se il giocatore ci arriva: per quello serve percorso.py.
"""
import sys, collections
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parent / 'strumenti_rom'), str(HERE.parent / 'registri'), str(HERE.parent / 'versioni')]
import romlib, scr, genera

B = 0x08000000
NOMI = {0x153: 'MN01 TAGLIO', 0x154: 'MN02 VOLO', 0x155: 'MN03 SURF', 0x156: 'MN04 FORZA', 0x157: 'MN05 FLASH',
        0x158: 'MN06 SPACCAROCCIA', 0x159: 'MN07 CASCATA', 0x15a: 'MN08 SUB', 0x103: 'BICI CORSA', 0x110: 'BICI CROSS',
        0x106: 'AMO VECCHIO', 0x107: 'AMO BUONO', 0x108: 'SUPER AMO'}


def walk(d, p, out, seen, depth=0):
    if p is None or p in seen or not (0 <= p < len(d)) or depth > 14: return
    seen.add(p)
    try: ops, _ = scr.decode(d, p, 500)
    except Exception: return
    item = None
    for a, n, ar in ops:
        if n == 'setorcopyvar' and ar and ar[0] == 0x8000: item = ar[1]
        elif n == 'callstd' and ar and ar[0] in (0, 1) and item is not None:
            out.append((item, 'giveitem' if ar[0] == 0 else 'finditem', a)); item = None
        elif n == 'additem' and ar: out.append((ar[0], 'additem', a))
        if n in ('call', 'goto', 'goto_if', 'call_if') and ar and isinstance(ar[-1], int) and B <= ar[-1] < B + len(d):
            walk(d, ar[-1] - B, out, seen, depth + 1)


def main(rom, ids):
    R = romlib.Rom(rom); d = bytes(R.data)
    res = collections.defaultdict(list)
    for k, m in sorted(genera.all_maps(R).items()):
        for lab, p in genera.entries(R, m):
            out = []; walk(d, p, out, set())
            for it, how, a in out:
                if it in ids: res[it].append(('%d.%d' % k, lab, how, hex(a)))
    for it in ids:
        print('%-18s' % NOMI.get(it, hex(it)), sorted(set(res[it])) or 'NESSUNO SCRIPT')
    return res


if __name__ == '__main__':
    ids = [int(x, 0) for x in sys.argv[2:]] or list(NOMI)
    main(sys.argv[1], ids)
