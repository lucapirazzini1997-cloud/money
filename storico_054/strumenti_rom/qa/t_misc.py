import qa21,sys,shutil
from qa21 import Game,S,lib,flag,walk,face
shutil.copy('out/Pokemon_Romagna_0_22.gba','qa/t.gba')
import romlib
r=romlib.Rom('qa/t.gba')
def boot(gn,x,y,**kw):
    qa21.make_save('qa/t.gba',gn,x,y,'qa/t.sav',**kw)
    g=Game('qa/t.gba','qa/t.sav',S);g.boot_continue();return g
def step(g,d,n=1):
    for _ in range(n): g.frames(2,d);g.frames(14,d);g.frames(8)
out=[]
# 1 daycare: costa door
m=r.map(34,21);w=m['warps'][0]
g=boot((34,21),w['x'],w['y']+1,badges=3);step(g,'up');g.frames(150);p1=g.pos()
step(g,'down',3);g.frames(150);out.append(('pensione in/out',p1,g.pos()))
# 2 grattacielo locked, then with keys
m=r.map(34,22);w=m['warps'][1]
g=boot((34,22),w['x'],w['y']+1,badges=3);face(g,'up');g.tap('a',3,40);g.shot('qa/gr0.png',1);[g.tap('a',3,30) for _ in range(6)];out.append(('gratt locked',g.pos()))
g=boot((34,22),w['x'],w['y']+1,badges=3,flags=['0x2f0']);face(g,'up');g.tap('a',3,40);[g.tap('a',3,30) for _ in range(5)];g.frames(200);p1=g.pos()
walk(g,8,13);g.frames(10);step(g,'down');g.frames(200);out.append(('gratt with keys',p1,g.pos()))
# 3 hotel: lobby stairs -> corridor -> room 104
m=r.map(34,0);w=m['warps'][1]
g=boot((34,0),w['x'],w['y']+1,badges=3);step(g,'up');g.frames(150);p1=g.pos();g.shot('qa/ho0.png',1)
walk(g,18,10);step(g,'up');g.frames(150);p2=g.pos();g.shot('qa/ho1.png',1)
step(g,'down',2);g.frames(150);out.append(('hotel',p1,p2,g.pos()))
# 4 lido: river blocks north
g=boot((0,9),19,9,badges=0,flags=['0x265']);step(g,'up',4);out.append(('lido north (expect y>=8)',g.pos()));g.shot('qa/li0.png',1)
# 5 lido south to pineta
g=boot((0,9),19,40,badges=1,flags=['0x20','0x265']);step(g,'down',5);g.frames(60);out.append(('lido->pineta',g.pos()))
for o in out: print(o)
