import qa21
from qa21 import Game,S
qa21.make_save('qa/t.gba',(26,86),5,6,'qa/t.sav',badges=8,flags=['0x265','0x860','0x864'])
g=Game('qa/t.gba','qa/t.sav',S);g.boot_continue();g.frames(40)
for k in range(2): g.frames(18,'up');g.frames(8)
g.frames(200);print(g.pos())
for k in range(5): g.frames(18,'up');g.frames(8)
g.shot('qa/lugia.png',1)
