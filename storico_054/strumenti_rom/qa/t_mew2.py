import qa21,romlib
from qa21 import Game,S,flag,walk,face
r=romlib.Rom('qa/t.gba');w=r.map(26,56)['warps'][0];print(w)
qa21.make_save('qa/t.gba',(26,56),w['x'],w['y']+1,'qa/t.sav',badges=8,flags=['0x265','0x860','0x864'])
g=Game('qa/t.gba','qa/t.sav',S);g.boot_continue();g.frames(60);g.frames(20,'up');g.frames(250);print(g.pos(),'hide mew flag',flag(0x2ce))
g.frames(60);g.shot('qa/mw_in.png',1)
