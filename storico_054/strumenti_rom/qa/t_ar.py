import qa21
from qa21 import Game,S
qa21.make_save('qa/t.gba',(34,47),41,13,'qa/t.sav',badges=3,flags=['0x265','0x860'])
g=Game('qa/t.gba','qa/t.sav',S);g.boot_continue();g.frames(60)
for k in range(2): g.frames(16,'up');g.frames(10)
g.frames(200);print(g.pos())
