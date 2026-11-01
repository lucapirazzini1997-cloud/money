import qa21,romlib,shutil
from qa21 import Game,S,flag,face,walk
shutil.copy('out/Pokemon_Romagna_0_22.gba','qa/t.gba')
r=romlib.Rom('qa/t.gba');c=r.map(34,15)['warps'][5];print(c)
qa21.make_save('qa/t.gba',(34,15),c['x'],c['y']+2,'qa/t.sav',flags=['0x265','0x860'])
g=Game('qa/t.gba','qa/t.sav',S);g.boot_continue();g.frames(60)
g.frames(16,'up');g.frames(80);g.shot('qa/cw.png',1);print(g.pos())
