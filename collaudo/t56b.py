from pl import *
from PIL import Image
import sys, struct
g=G(sys.argv[1]); ims=[]
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
def goadj(x,y):
    p=g.pos(); key=p[2:]
    objs=[c for c in g.lobjs() if c!=(x,y)]
    lv=g.live()
    for adj,face in (((x,y+1),'U'),((x,y-1),'D'),((x+1,y),'L'),((x-1,y),'R')):
        if (int(lv[adj[1],adj[0]])>>10)&3: continue
        r=route(key[0],key[1],p[:2],adj,live=lv,objs=objs)
        if r is not None: break
    for ch in r:
        g.step(ch)
        if g.cb2()!=OW: g.battle()
    for t in range(8):
        if g.pos()[:2]==adj: break
        r=route(key[0],key[1],g.pos()[:2],adj,live=g.live(),objs=objs)
        for ch in (r or ''): g.step(ch)
        log('  ritento',t,g.pos(),adj)
    g.step(face,3); g.e.run(10)
    return g.pos()[:2]==adj
g.mash(B,4,30)
if g.pos()[2:]!=(34,33): g.travel((34,33))
for (x,y),f in (((2,2),0x7b3),((20,8),0x7b2),((12,22),0x7b1)):
    if g.flag(f): continue
    ok=goadj(x,y)
    for i in range(6): g.key(A,3,45)
    snap(); log('T56 pennello',(x,y),'adiacente',ok,'flag',g.flag(f),'pennelli',item_count(0x15b))
g.save('t56_pennelli.ss')
g.travel((34,17)); ok=goadj(32,24)
for i in range(16):
    g.key(A,3,45)
    if i%3==0: snap()
for i in range(4): g.key(B,3,30)
pt=g.party(); log('T56 dopo pittore',pt,'flag',g.flag(0x7b0),'pennelli',item_count(0x15b))
n=g.e.ram(0x20244e9,1)[0]; b=g.e.ram(0x20244ec+(n-1)*100,100)
pid,otid=struct.unpack_from('<II',b,0)
sh=((otid&0xffff)^(otid>>16)^(pid&0xffff)^(pid>>16))
log('T56 ultimo: livello',b[84],'shiny value',sh,'(cromatico se <8)')
g.save('t56_smeargle.ss')
W=Image.new('RGB',(240*6,160*((len(ims)+5)//6)))
for i,im in enumerate(ims): W.paste(im,((i%6)*240,(i//6)*160))
W.save(P+'t56b.png'); g.close()
