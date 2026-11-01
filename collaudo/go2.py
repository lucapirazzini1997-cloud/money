"""Cammina seguendo una stringa di direzioni; gestisce dialoghi e lotte (solo tasti)."""
from pl import *
from PIL import Image
import sys
g=G(sys.argv[1]); ims=[]
def snap():
    g.shot('tmp'); ims.append(Image.open(P+'tmp.png').copy())
path=sys.argv[2]; i=0; stall=0
while i<len(path):
    ch=path[i]; before=g.pos()
    if ch=='a': g.key(A,3,40); i+=1; snap(); continue
    if ch=='w': g.e.run(60); i+=1; continue
    g.step(ch)
    if g.cb2()!=OW:
        info=g.battle(); log('  lotta',info[:1],g.party(),g.pos()); snap(); continue
    after=g.pos()
    if after==before:
        stall+=1
        for _ in range(4): g.key(B,2,25)
        if g.cb2()!=OW:
            info=g.battle(); log('  lotta(b)',info[:1],g.party(),g.pos()); snap()
        if stall>6: log('bloccato a',after,'passo',i,ch); snap(); break
        continue
    stall=0; i+=1
    if after[2:]!=before[2:]: log('cambio mappa',after); g.e.run(60)
log('fine',g.pos(),g.party())
snap()
if len(sys.argv)>3: g.save(sys.argv[3])
W=Image.new('RGB',(240*6,160*((len(ims)+5)//6)))
for k,im in enumerate(ims[-36:]): W.paste(im,((k%6)*240,(k//6)*160))
W.save(P+'go2.png'); g.close()
