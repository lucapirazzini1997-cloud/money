from pl import *
from PIL import Image
import sys, struct
g=G('t56_pennelli.ss'); ims=[]
def snap():
    g.shot('tmp'); ims.append(Image.open(P+'tmp.png').copy())
def item_count(item):
    sb1=g.e.r('r32',0x3005d8c); sb2=g.e.r('r32',0x3005d90)
    key=struct.unpack('<H',g.e.ram(sb2+0xac,2))[0]
    b=g.e.ram(sb1+0x5d8,30*4)
    for i in range(30):
        it,q=struct.unpack_from('<HH',b,i*4)
        if it==item: return q^key
    return 0
g.mash(B,4,30)
if g.pos()[2:]!=(34,17): g.travel((34,17))
for t in range(6):
    r=route(34,17,g.pos()[:2],(31,24),live=g.live(),objs=[c for c in g.lobjs() if c!=(32,24)])
    for ch in (r or ''): g.step(ch)
    if g.pos()[:2]==(31,24): break
log('T56 accanto al pittore',g.pos(),'pennelli',item_count(0x15b),'squadra',g.party())
g.step('R',3); g.e.run(10)
for i in range(18):
    g.key(A,3,50)
    if i%2==0: snap()
for i in range(4): g.key(B,3,30)
pt=g.party(); log('T56 dopo pittore',pt,'flag',g.flag(0x7b0),'pennelli',item_count(0x15b))
n=g.e.ram(0x20244e9,1)[0]; b=g.e.ram(0x20244ec+(n-1)*100,100)
pid,otid=struct.unpack_from('<II',b,0)
sh=((otid&0xffff)^(otid>>16)^(pid&0xffff)^(pid>>16))
log('T56 ultimo: livello',b[84],'PID',hex(pid),'shiny value',sh,'(cromatico se <8)')
g.save('t56_smeargle.ss')
W=Image.new('RGB',(240*6,160*((len(ims)+5)//6)))
for i,im in enumerate(ims): W.paste(im,((i%6)*240,(i//6)*160))
W.save(P+'t56c.png'); g.close()
