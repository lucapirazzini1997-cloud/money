"""Prova di un blocco: viaggia verso dest e registra dove finisce, con screenshot."""
from pl import *
from PIL import Image
import sys
g=G(sys.argv[1]); g.mash(B,4,30)
dest=tuple(map(int,sys.argv[2].split('.')))
ok=g.travel(dest)
for i in range(6): g.key(A,3,40)
g.e.run(90)
log('GATE',sys.argv[1],'->',dest,'ok',ok,'pos',g.pos(),'b6',g.flag(0x86c))
g.shot(sys.argv[3]); g.save(sys.argv[3]+'.ss'); g.close()
