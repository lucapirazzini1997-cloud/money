import qa21
from qa21 import Game,S
qa21.make_save('qa/t.gba',(34,34),8,12,'qa/t.sav',badges=2,flags=['0x265','0x860','0x4e8'])
g=Game('qa/t.gba','qa/t.sav',S);g.boot_continue();g.frames(40)
for k in range(2): g.frames(18,'down');g.frames(8)
g.frames(200);print('exit gratt',g.pos())
