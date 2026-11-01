from pl import *
from PIL import Image
import sys, struct
g=G(sys.argv[1]); ims=[]
def snap():
    g.shot('tmp'); ims.append(Image.open(P+'tmp.png').copy())
def tm_count(item):
    sb1=g.e.r('r32',0x3005d8c); sb2=g.e.r('r32',0x3005d90)
    key=struct.unpack('<H',g.e.ram(sb2+0xac,2))[0]
    for base,n in ((0x640,64),(0x5d8,30),(0x560,30)):
        b=g.e.ram(sb1+base,n*4)
        for i in range(n):
            it,q=struct.unpack_from('<HH',b,i*4)
            if it==item: return q^key
    return 0
def goto(adj,face,key):
    for t in range(6):
        r=route(key[0],key[1],g.pos()[:2],adj,live=g.live(),objs=g.lobjs())
        for ch in (r or ''):
            g.step(ch)
            if g.cb2()!=OW: g.battle()
        if g.pos()[:2]==adj: break
    g.step(face,3); g.e.run(10)
def read(n=8,shots=(0,2,4)):
    for i in range(n):
        g.key(A,3,50)
        if i in shots: snap()
    for i in range(3): g.key(B,3,30)
dest=tuple(map(int,sys.argv[2].split('.')))
g.mash(B,4,30)
if g.pos()[2:]!=dest: g.travel(dest)
for step in sys.argv[3:]:
    x,y,face=step.split(',')
    goto((int(x),int(y)),face,dest); read()
    log('T56L',step,'pos',g.pos(),'flags',[g.flag(f) for f in map(lambda s:int(s,16),sys.argv[-1:][0].split('/')) ] if False else '', 'MT17',tm_count(0x131),'PIETRALUNARE',tm_count(0x5e))
g.save(sys.argv[1].replace('.ss','')+'_out.ss')
W=Image.new('RGB',(240*6,160*((len(ims)+5)//6)))
for i,im in enumerate(ims): W.paste(im,((i%6)*240,(i//6)*160))
W.save(P+'t56lib.png'); g.close()
