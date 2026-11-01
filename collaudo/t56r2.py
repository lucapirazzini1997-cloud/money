from pl import *
from PIL import Image
g=G('t56_rename.ss'); ims=[]
def snap(): g.shot('tmp'); ims.append(Image.open(P+'tmp.png').copy())
def name():
    sb1=g.e.r('r32',0x3005d8c); return g.e.ram(sb1+0x139c+0x1f8,8).hex()
g.step('D',3); g.e.run(10)
g.key(A,3,250); snap()        # avvia: testo col nome
g.key(A,3,300); snap()        # domanda "Vuoi cambiare..." con SI/NO
g.key(D,3,40); snap(); g.key(A,3,300); snap()   # NO -> domanda ALDO
g.key(A,3,200); snap()        # SI
for i in range(20):
    if g.e.ram(0x3000e41,1)[0]==0: break
    g.key(A,3,60)
snap(); log('T56R2 nome',name())
g.save('t56_rename2.ss')
W=Image.new('RGB',(240*6,160))
for i,im in enumerate(ims): W.paste(im,((i%6)*240,0))
W.save(P+'t56r2.png'); g.close()
