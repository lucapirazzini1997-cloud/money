import qa21,romlib,shutil
from qa21 import Game,S,flag,walk,face
shutil.copy('out/Pokemon_Romagna_0_22.gba','qa/t.gba')
r=romlib.Rom('qa/t.gba');w=r.map(34,17)['warps'][6];print(w)
qa21.make_save('qa/t.gba',(34,17),w['x'],w['y']+1,'qa/t.sav',badges=3,flags=['0x265','0x860'])
g=Game('qa/t.gba','qa/t.sav',S);g.boot_continue();g.frames(20,'up');g.frames(200);print('in',g.pos());g.shot('qa/ro0.png',1)
print(walk(g,9,2),g.pos());g.frames(20,'up');g.frames(200);print('maze',g.pos());g.shot('qa/ro1.png',1)
g.frames(20,'down');g.frames(200);print('back',g.pos());g.shot('qa/ro2.png',1)
