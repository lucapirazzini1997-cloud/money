"""Testi con piu' di 2 righe in un riquadro, negli script indicati (seguendo call/goto).
Separatori di Smeraldo: FB = nuovo riquadro, FE = a capo, FA = a capo con scorrimento (conta come riga in piu').
Uso: python3 analisi/righe.py ROM g.n [g.n ...]   (tutti gli script della mappa)"""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parent / 'strumenti_rom'), str(HERE.parent / 'registri'), str(HERE.parent / 'versioni')]
import romlib, scr, genera
B = 0x08000000


def righe(d, p):
    out = bytearray()
    while d[p] != 0xff and len(out) < 2000: out.append(d[p]); p += 1
    pagine = bytes(out).split(b'\xfb')
    return max(pg.count(b'\xfe') + pg.count(b'\xfa') + 1 for pg in pagine)


def testi(d, p, acc, seen, depth=0):
    if p in seen or depth > 12 or not (0 <= p < len(d)): return
    seen.add(p)
    try: ops, _ = scr.decode(d, p, 400)
    except Exception: return
    for a, n, ar in ops:
        if n == 'loadword' and ar and ar[0] == 0 and B <= ar[1] < B + len(d): acc.add((a, ar[1] - B))
        if n in ('call', 'goto', 'goto_if', 'call_if') and ar and isinstance(ar[-1], int) and B <= ar[-1] < B + len(d):
            testi(d, ar[-1] - B, acc, seen, depth + 1)


if __name__ == '__main__':
    R = romlib.Rom(sys.argv[1]); d = bytes(R.data)
    for k in sys.argv[2:]:
        m = R.map(*map(int, k.split('.')))
        for lab, p in genera.entries(R, m):
            acc = set(); testi(d, p, acc, set())
            for a, t in sorted(acc):
                n = righe(d, t)
                if n > 2: print(k, lab, 'loadword a', hex(a), 'testo', hex(t), 'righe', n, '|', scr.text(d, t, 120)[:110])
