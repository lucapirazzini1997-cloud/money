from pl import *
import sys
g=G('t56_lib2.ss'); g.mash(B,4,30); g.travel((34,24))
def goto(adj,face):
    for t in range(6):
        r=route(34,24,g.pos()[:2],adj,live=g.live(),objs=g.lobjs()); log('  rotta',t,g.pos(),adj,r, hex(g.cb2()))
        for ch in (r or ''): g.step(ch)
        if g.pos()[:2]==adj: break
    g.step(face,3); g.e.run(10)
    for i in range(12): g.key(A,3,50)
    for i in range(3): g.key(B,3,30)
F=(0x7ad,0x7ac,0x7ab)
for adj,lab in (((2,10),'II per primo'),((20,18),'I'),((5,26),'III saltando II'),((20,18),'I'),((2,10),'II'),((5,26),'III')):
    goto(adj,'U'); log('T56W',lab,g.pos(),'L1,L2,LOK',[g.flag(f) for f in F])
g.close()
