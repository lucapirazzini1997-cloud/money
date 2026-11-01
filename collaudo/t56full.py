from pl import *
import struct
g=G('t56_pennelli.ss'); e=g.e
# fixture dichiarata: squadra piena copiando lo slot 0 negli slot 2..5
src=e.ram(0x20244ec,100)
for i in range(2,6):
    for k in range(0,100,4): e.w('w32',0x20244ec+i*100+k,struct.unpack_from('<I',src,k)[0])
e.w('w8',0x20244e9,6)
sb3=e.r('r32',0x3005d94)
def box_used():
    n=0
    for i in range(30):
        pid=struct.unpack('<I',e.ram(sb3+4+i*80,4))[0]
        if pid: n+=1
    return n
before=box_used()
g.mash(B,4,30)
if g.pos()[2:]!=(34,17): g.travel((34,17))
for t in range(6):
    r=route(34,17,g.pos()[:2],(31,24),live=g.live(),objs=[c for c in g.lobjs() if c!=(32,24)])
    for ch in (r or ''): g.step(ch)
    if g.pos()[:2]==(31,24): break
g.step('R',3); g.e.run(10)
g.key(A,3,60)
for i in range(30):
    if e.ram(0x3000e41,1)[0]==0: break
    g.key(A,3,60)
g.shot('t56full')
log('T56F squadra',len(g.party()),'box usati prima/dopo',before,box_used(),'flag consegna',g.flag(0x7b0))
g.close()
