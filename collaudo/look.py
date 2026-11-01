from pl import *
from PIL import Image
import sys
g=G(sys.argv[1]); ims=[]
def snap():
    g.shot('tmp'); ims.append(Image.open(P+'tmp.png').copy())
snap(); print(g.pos())
for ch in sys.argv[2]:
    if ch=='a': g.key(A,3,40)
    elif ch=='b': g.key(B,3,40)
    elif ch=='w': g.e.run(60)
    else: g.step(ch)
    print(ch,g.pos(),hex(g.cb2())); snap()
if len(sys.argv)>3: g.save(sys.argv[3])
W=Image.new('RGB',(240*6,160*((len(ims)+5)//6)))
for i,im in enumerate(ims): W.paste(im,((i%6)*240,(i//6)*160))
W.save(P+'look.png'); g.close()
