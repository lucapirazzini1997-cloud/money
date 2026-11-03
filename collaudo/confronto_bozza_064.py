#!/usr/bin/env python3
"""0.64: la mappa nella ROM e' la bozza approvata?
1. Il disegno nel modulo e' la copia delle righe di disegno di bozze/campagna_monte_spaccato.py (stesse righe,
   a parte rientro e commenti di posizione).
2. I blocchi di 35.101 nella ROM 0.64 sono quelli che il disegno da' sulla ROM 0.63 (stessa Unione).
Uso: python3 collaudo/confronto_bozza_064.py ROM_063 ROM_064"""
import sys, struct, re
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / 'versioni'), str(ROOT / 'strumenti_rom')]
import romlib, tela
src = (ROOT / 'versioni' / 'v064_campagna_cesenate.py').read_text()
mod = src[src.index('def disegna(d):'):src.index('    return T')]
boz = (ROOT / 'bozze' / 'campagna_monte_spaccato.py').read_text()
boz = boz[boz.index('def lay('):boz.index('U = tela.Unione')]
norm = lambda t: [re.sub(r'\s+#.*', '', l).strip() for l in t.split('\n') if l.strip() and not l.strip().startswith('#')]
a = [l for l in norm(mod) if not l.startswith(('def disegna', '"""', 'W, H ='))]
b = [l for l in norm(boz) if not l.startswith('W, H =')]
diff = [(x, y) for x, y in zip(a, b) if x != y]
print('righe di disegno: modulo %d, bozza %d, diverse %d' % (len(a), len(b), len(diff) + abs(len(a) - len(b))))
for x, y in diff: print('  modulo:', x, '\n  bozza: ', y)
d63 = open(sys.argv[1], 'rb').read()
import importlib.util
spec = importlib.util.spec_from_file_location('m', ROOT / 'versioni' / 'v064_campagna_cesenate.py')
class _E: pass
sys.modules.setdefault('engine', __import__('engine'))
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
T = m.disegna(d63); U = tela.Unione(d63); vals = T.valori(U)
R = romlib.Rom(sys.argv[2]); mp = R.map(35, 101); blk = R.blocks(mp)
dif = sum(1 for k, v in enumerate(vals) if int(blk[k // 64, k % 64]) != v)
print('blocchi di 35.101 nella ROM uguali al disegno: %d diversi su %d' % (dif, len(vals)))
