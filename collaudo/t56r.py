from pl import *
from PIL import Image
import struct
g=G('q8_end.ss'); ims=[]
def snap(): g.shot('tmp'); ims.append(Image.open(P+'tmp.png').copy())
def name():
    sb1=g.e.r('r32',0x3005d8c); return g.e.ram(sb1+0x139c+0x1f8,8).hex()
def wait_script(maxa=25):
    for i in range(maxa):
        if g.e.ram(0x3000e41,1)[0]==0: break
        g.key(A,3,50)
g.mash(B,4,30)
g.travel((0,9)); log('T56R fuori',g.pos())
g.travel((1,4)); g.e.run(60); log('T56R dentro',g.pos(), g.lobjs_gfx())
for ch in route(1,4,g.pos()[:2],(10,9),live=g.live(),objs=g.lobjs()): g.step(ch)
log('T56R pos',g.pos(),'nome',name())
g.step('D',3); g.e.run(10)
g.key(A,3,60); snap(); g.key(A,3,60); snap()      # "si chiama ALDO" -> domanda
g.key(A,3,60); snap()                              # SI'
for i in range(4): g.key(A,3,60)                    # testo istruzioni
g.e.run(120); snap(); log('T56R schermata nome?',hex(g.cb2()))
g.key(B,3,30)                                       # cancella eventuali lettere? (B = indietro)
for k in (A,):                                      # scrive 'A'
    g.key(A,3,40)
g.key(R,3,20); g.key(A,3,40)                        # 'B'
g.key(START,3,40); g.key(A,3,80); g.e.run(150); snap()
wait_script(); snap()
log('T56R dopo nome',g.pos(),hex(g.cb2()),'nome',name())
g.save('t56_rename.ss')
# di nuovo: rifiuta il cambio e torna ad ALDO
g.step('D',3); g.e.run(10)
g.key(A,3,60); g.key(A,3,60)
g.key(B,3,60)                                       # NO al cambio
g.key(A,3,60); snap()                               # SI' a tornare ad ALDO
wait_script(); snap()
log('T56R ripristino',g.pos(),'nome',name())
W=Image.new('RGB',(240*6,160*((len(ims)+5)//6)))
for i,im in enumerate(ims): W.paste(im,((i%6)*240,(i//6)*160))
W.save(P+'t56r.png'); g.close()
