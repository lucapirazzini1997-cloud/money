import sys, os, struct, pl
from pl import *
SAV = P + 't56.sav'
if os.path.exists(SAV): os.remove(SAV)
open(SAV, 'wb').write(b'\xff' * 131072)
class G2(G):
    def __init__(self, state=None):
        self.e = Emu(pl.ROM, SAV); self.e.run(10)
        if state: self.e.load(P + state); self.e.run(120)
def snapshot(g):
    sb1=g.e.r('r32',0x3005d8c); sb2=g.e.r('r32',0x3005d90)
    key=struct.unpack('<H',g.e.ram(sb2+0xac,2))[0]
    items={}
    for base,n in ((0x560,30),(0x5d8,30),(0x640,64)):
        b=g.e.ram(sb1+base,n*4)
        for i in range(n):
            it,q=struct.unpack_from('<HH',b,i*4)
            if it in (0x15b,0x131,0x5e): items[hex(it)]=q^key
    n=g.e.ram(0x20244e9,1)[0]; mons=[]
    for i in range(n):
        b=g.e.ram(0x20244ec+i*100,100); pid,otid=struct.unpack_from('<II',b,0)
        mons.append((b[84], ((otid&0xffff)^(otid>>16)^(pid&0xffff)^(pid>>16))<8))
    flags=[g.flag(f) for f in (0x7b0,0x7b1,0x7b2,0x7b3,0x7aa,0x7ab,0x78a,0x792)]
    return dict(pos=g.pos(),mons=mons,items=items,flags=flags)
g = G2(sys.argv[1]); e = g.e
before = snapshot(g)
e.key(START, 3, 40)
for _ in range(10):
    if e.ram(0x203760e, 1)[0] == 4: break
    e.key(D, 3, 15)
e.key(A, 3, 90); g.shot('sv1'); e.key(A, 3, 90); g.shot('sv2'); e.key(A, 3, 90); g.shot('sv3')
for i in range(12): e.run(60)
g.shot('sv4')
for _ in range(3): e.key(B, 3, 30)
g.close()
g = G2(None); e = g.e
for i in range(60):
    e.key(A, 3, 40)
    if g.cb2() == OW: break
e.run(200); g.shot('sv5')
after = snapshot(g)
print('prima', before); print('dopo ', after); print('UGUALE', before == after)
g.save('t56_reload.ss'); g.close()
