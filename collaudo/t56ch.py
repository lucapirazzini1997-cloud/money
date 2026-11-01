from pl import *
from PIL import Image
import sys, struct
g=G('t56_lib_out.ss'); g.mash(B,4,30); g.travel((34,37)); ims=[]
def cnt(item):
    sb1=g.e.r('r32',0x3005d8c); sb2=g.e.r('r32',0x3005d90)
    key=struct.unpack('<H',g.e.ram(sb2+0xac,2))[0]
    b=g.e.ram(sb1+0x560,30*4)
    for i in range(30):
        it,q=struct.unpack_from('<HH',b,i*4)
        if it==item: return q^key
    return 0
def goto(adj,face,shot=False):
    for t in range(6):
        r=route(34,37,g.pos()[:2],adj,live=g.live(),objs=g.lobjs())
        for ch in (r or ''): g.step(ch)
        if g.pos()[:2]==adj: break
    g.step(face,3); g.e.run(10)
    g.key(A,3,50)
    if shot: g.shot('tmp'); ims.append(Image.open(P+'tmp.png').copy())
    for i in range(25):
        if g.e.ram(0x3000e41,1)[0]==0: break
        g.key(A,3,50)
        if shot and i==2: g.shot('tmp'); ims.append(Image.open(P+'tmp.png').copy())
    g.e.run(20)
F=(0x794,0x793,0x792,0x78a)
for adj,face,lab in (((2,2),'U','vetrata I'),((5,2),'U','vetrata II'),((12,2),'U','vetrata III'),((8,4),'U','altare prima'),
                     ((16,14),'U','candela destra per prima (errore)'),((2,4),'U','candela altare'),((1,10),'U','candela sinistra saltando (errore)'),
                     ((2,4),'U','candela altare'),((16,14),'U','candela destra'),((1,10),'U','candela sinistra'),((8,4),'U','altare premio'),((8,4),'U','altare di nuovo')):
    goto(adj,face,shot=True); log('T56C',lab,g.pos(),'C1,C2,OK,DONE',[g.flag(f) for f in F],'PIETRALUNARE',cnt(0x5e))
g.save('t56_church.ss')
W=Image.new('RGB',(240*6,160*((len(ims)+5)//6)))
for i,im in enumerate(ims): W.paste(im,((i%6)*240,(i//6)*160))
W.save(P+'t56ch.png'); g.close()
