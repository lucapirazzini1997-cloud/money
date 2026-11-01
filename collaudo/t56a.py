"""0.56: pittore, tre pennelli nel labirinto, SMEARGLE cromatico. Solo tasti (nessuna scrittura in RAM)."""
from pl import *
from PIL import Image
import sys, struct
g=G('s_ce3.ss'); ims=[]
def snap(n=None):
    g.shot('tmp'); ims.append(Image.open(P+'tmp.png').copy())
def talk_at(x,y,face):
    g.walkto(x,y); g.step(face,3); g.e.run(10)
    for i in range(14):
        g.key(A,3,45)
        if i in (0,3,6,9): snap()
    for i in range(4): g.key(B,3,30)
def item_count(item):
    sb1=g.e.r('r32',0x3005d8c); sb2=g.e.r('r32',0x3005d90)
    key=struct.unpack('<H',g.e.ram(sb2+0xac,2))[0]
    # tasca chiave: sb1+0x5d8, 30 voci (id, qta^key)
    b=g.e.ram(sb1+0x5d8,30*4)
    for i in range(30):
        it,q=struct.unpack_from('<HH',b,i*4)
        if it==item: return q^key
    return 0
g.mash(B,4,30)
g.travel((34,17)); log('T56 a Cesena',g.pos())
talk_at(33,24,'L'); log('T56 pittore 1',g.flag(0x7b0),'pennelli',item_count(0x15b))
g.travel((34,33)); log('T56 labirinto',g.pos())
for (x,y),f in (((2,2),0x7b3),((20,8),0x7b2),((12,22),0x7b1)):
    r=route(34,33,g.pos()[:2],(x,y))
    # vai accanto e guarda il pennello
    for adj,face in (((x,y+1),'U'),((x,y-1),'D'),((x+1,y),'L'),((x-1,y),'R')):
        if route(34,33,g.pos()[:2],adj) is not None: break
    g.walkto(*adj); g.step(face,3); g.e.run(10)
    for i in range(6): g.key(A,3,45)
    snap(); log('T56 pennello',(x,y),'flag',g.flag(f),'pennelli',item_count(0x15b))
g.save('t56_pennelli.ss')
g.travel((34,17)); talk_at(33,24,'L')
pt=g.party(); log('T56 dopo pittore',pt,'flag',g.flag(0x7b0),'pennelli',item_count(0x15b))
# controllo cromatico dell'ultimo della squadra
n=g.e.ram(0x20244e9,1)[0]; b=g.e.ram(0x20244ec+(n-1)*100,100)
pid,otid=struct.unpack_from('<II',b,0)
sh=((otid&0xffff)^(otid>>16)^(pid&0xffff)^(pid>>16))
log('T56 ultimo: livello',b[84],'shiny value',sh,'(cromatico se <8)')
g.save('t56_smeargle.ss')
W=Image.new('RGB',(240*6,160*((len(ims)+5)//6)))
for i,im in enumerate(ims): W.paste(im,((i%6)*240,(i//6)*160))
W.save(P+'t56a.png'); g.close()
