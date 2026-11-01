import qa21,sys,shutil,romlib
from qa21 import Game,S,lib,flag,walk,face,yesno_open
shutil.copy('out/Pokemon_Romagna_0_22.gba','qa/t.gba')
w=romlib.Rom('qa/t.gba').map(34,22)['warps'][5]
qa21.make_save('qa/t.gba',(34,22),w['x'],w['y']+1,'qa/t.sav',badges=3)
g=Game('qa/t.gba','qa/t.sav',S);g.boot_continue();g.frames(20,'up');g.frames(150)
walk(g,6,7);face(g,'up');g.tap('a',3,30)
ans=[True,True,False,True];n=0
log=[]
for i in range(200):
    g.frames(6)
    if yesno_open(g):
        g.frames(20)
        a=ans.pop(0)
        if not a:
            g.frames(2,'down');g.frames(10)
        g.frames(2,'a');g.frames(10)
        k=0
        while yesno_open(g) and k<50: g.frames(5);k+=1
        log.append(('answered',a,i))
        if not ans: break
    else:
        g.frames(2,'a');g.frames(8)
for i in range(30): g.frames(2,'a');g.frames(15)
print(log,'bike',flag(0x4da))
g.shot('qa/qz.png',1)
