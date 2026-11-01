"""Fixture dichiarata: carica uno stato, imposta/azzera flag in RAM, salva un nuovo stato."""
from pl import *
import sys, struct
g=G(sys.argv[1]); e=g.e
sb1=e.r('r32',0x3005d8c)
for a in sys.argv[3:]:
    op,n=a[0],int(a[1:],16)
    p=sb1+0x1270+(n>>3); v=e.ram(p,1)[0]
    v = v|(1<<(n&7)) if op=='+' else v&~(1<<(n&7))
    e.w('w8',p,v)
print('pos',g.pos(),[ (a, g.flag(int(a[1:],16))) for a in sys.argv[3:]])
g.save(sys.argv[2]); g.close()
