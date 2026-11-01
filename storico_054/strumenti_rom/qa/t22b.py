import qa21,sys
from qa21 import Game,S,lib,flag,walk,face
import shutil
rom='out/Pokemon_Romagna_0_22.gba';shutil.copy(rom,'qa/t.gba')
def boot(gn,x,y,**kw):
    qa21.make_save('qa/t.gba',gn,x,y,'qa/t.sav',**kw)
    g=Game('qa/t.gba','qa/t.sav',S);g.boot_continue();return g
def seq(g,keys,tag):
    n=0
    for k in keys:
        if k=='shot': g.shot('qa/%s%d.png'%(tag,n),1);n+=1;continue
        g.tap(k,3,40)
g=boot((34,15),21,6,badges=3); g.frames(20,'up'); g.frames(150); print(g.pos())
walk(g,7,6); face(g,'up'); seq(g,['a','shot','a','a','shot','b','b','b','b','b'],'ch')
g=boot((34,22),37,15,badges=3); g.frames(20,'up'); g.frames(150); print(g.pos())
walk(g,6,7); face(g,'up'); seq(g,['a','shot','a','a','a','a','shot','a','a','a','a','a','shot','b','a','a','a','a','shot','a','a','a','a','a','shot','a','a','a','a','a','a','shot','a','a','a','a','a','shot'],'q')
print('bike flag',flag(0x4da))
