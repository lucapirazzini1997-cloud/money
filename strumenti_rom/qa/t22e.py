import qa21,sys
from qa21 import Game,S,lib,flag,walk,face,answer,yesno_open
import shutil
shutil.copy('out/Pokemon_Romagna_0_22.gba','qa/t.gba')
import romlib
w=romlib.Rom('qa/t.gba').map(34,22)['warps'][5]
qa21.make_save('qa/t.gba',(34,22),w['x'],w['y']+1,'qa/t.sav',badges=3)
g=Game('qa/t.gba','qa/t.sav',S);g.boot_continue();g.frames(20,'up');g.frames(150)
walk(g,6,7);face(g,'up');g.tap('a',3,30)
ans=[True,True,False,True];n=0
for i in range(60):
    g.frames(10)
    if yesno_open(g):
        g.frames(20); a=ans.pop(0); g.shot('qa/yn%d.png'%n,1);n+=1
        if not a: g.tap('down',3,10)
        g.tap('a',3,10)
        while yesno_open(g): g.frames(5)
        if not ans: break
    else: g.tap('a',3,20)
for i in range(14): g.tap('a',3,40)
g.shot('qa/af0.png',1)
print('bike',flag(0x4da))
