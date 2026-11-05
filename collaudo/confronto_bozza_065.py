"""0.65: il disegno congelato in versioni/v065_ridracoli.py e' la bozza 2 approvata (bozze/ridracoli.py)?
1) le righe di disegno della bozza compaiono identiche nel modulo;
2) tela della bozza e tela del modulo (calcolate sulla ROM 0.64) coincidono casella per casella (fonte, blocco),
   tranne i cambi voluti e dichiarati: primo gradino della scala (23-25,36: nella bozza era muro) e cartello
   della sorgente spostato da (10,2) a (9,5) (nella bozza stava su una casella irraggiungibile);
3) i blocchi di 35.51 nella ROM 0.65 sono quelli della tela del modulo, tranne le tre frecce d'uscita (23-25,61).
Uso: python3 collaudo/confronto_bozza_065.py ROM_064 ROM_065"""
import sys, re
from pathlib import Path
R = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(R / 'strumenti_rom'), str(R / 'versioni')]
import tela, romlib
b = (R / 'bozze/ridracoli.py').read_text().splitlines()
m = (R / 'versioni/v065_ridracoli.py').read_text().splitlines()
i0 = next(i for i, l in enumerate(b) if l.startswith('# --- 1.')); i1 = next(i for i, l in enumerate(b) if l.startswith('U = tela.Unione'))
norm = lambda l: re.sub(r'\s+#.*$', '', l).strip()
corpo = [norm(l) for l in m]
righe = [norm(l) for l in b[i0:i1] if norm(l) and not norm(l).startswith('#')]
mancano = [l for l in righe if l not in corpo]
print('1) righe di disegno della bozza:', len(righe), '- mancanti nel modulo:', len(mancano))
for l in mancano: print('   ', l)
d64 = open(sys.argv[1], 'rb').read()
src = (R / 'bozze/ridracoli.py').read_text().split('U = tela.Unione')[0]
g = {'__name__': 'bozza', '__file__': str(R / 'bozze/ridracoli.py')}; sys.argv[:] = ['x', sys.argv[1], '/dev/null', sys.argv[2]]
exec(compile(src, 'bozza', 'exec'), g)
Tb = g['T']
import v065_ridracoli as V
Tm = V.disegna(d64)
diff = [(x, y) for y in range(V.H_) for x in range(V.W_) if Tb.c[y][x] != Tm.c[y][x]]
VOLUTI = {(x, 36) for x in (23, 24, 25)} | {(10, 2), (9, 5)}
print('2) caselle diverse fra bozza e modulo:', len(diff), sorted(diff))
ok2 = set(diff) == VOLUTI
r = romlib.Rom(sys.argv[3]); mp = r.map(35, 51); a = r.blocks(mp)
assert (mp['width'], mp['height']) == (V.W_, V.H_)
U = tela.Unione(d64); vals = Tm.valori(U)
d3 = [(x, y) for y in range(V.H_) for x in range(V.W_) if int(a[y, x]) != vals[y * V.W_ + x]]
print('3) blocchi della ROM diversi dalla tela del modulo:', len(d3), d3)
ok3 = set(d3) == {(x, 61) for x in (23, 24, 25)}
print('TUTTO OK' if (not mancano and ok2 and ok3) else 'DIFFERENZE')
