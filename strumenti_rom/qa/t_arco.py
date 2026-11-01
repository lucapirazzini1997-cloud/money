import qa21
from qa21 import Game,S
qa21.make_save('qa/t.gba',(34,47),70,25,'qa/t.sav',badges=4,flags=['0x265','0x860'])
g=Game('qa/t.gba','qa/t.sav',S);g.boot_continue();g.frames(60)
for k in range(4): g.frames(16,'down');g.frames(6)
print(g.pos());g.shot('qa/arco_in.png',1)
