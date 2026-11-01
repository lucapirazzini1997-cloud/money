import qa21,romlib,shutil
from qa21 import Game,S,flag,walk,face
shutil.copy('out/Pokemon_Romagna_0_22.gba','qa/t.gba')
r=romlib.Rom('qa/t.gba');m=r.map(34,17)
for i,(tx,ty) in ((2,(4,5)),(8,(10,6)),(0,(5,5))):
    w=m['warps'][i]
    qa21.make_save('qa/t.gba',(34,17),w['x'],w['y']+1,'qa/t.sav',badges=3,flags=['0x265','0x860'])
    g=Game('qa/t.gba','qa/t.sav',S);g.boot_continue();g.frames(20,'up');g.frames(200);print(i,'in',g.pos(),walk(g,tx,ty),g.pos())
    g.shot('qa/cb%d.png'%i,1)
