import qa21,sys
from qa21 import Game,S,lib,flag,walk,face,answer,yesno_open
import shutil
rom='out/Pokemon_Romagna_0_22.gba';shutil.copy(rom,'qa/t.gba')
qa21.make_save('qa/t.gba',(34,22),37,15,'qa/t.sav',badges=3)
g=Game('qa/t.gba','qa/t.sav',S);g.boot_continue();g.frames(20,'up');g.frames(150)
walk(g,6,7);face(g,'up');g.tap('a',3,30)
for i in range(8):
    g.tap('a',3,30); im=g.shot('qa/y%d.png'%i,1); px=im.load(); print(i,yesno_open(g),[sum(px[x,125]) for x in (190,205,215,222)],sum(px[210,118]))
