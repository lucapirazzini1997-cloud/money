import qa21,romlib
from qa21 import Game,S,walk
r=romlib.Rom('qa/t.gba');w=r.map(34,47)['warps'][7];print(w)
qa21.make_save('qa/t.gba',(34,47),w['x'],w['y']-1,'qa/t.sav',badges=4,flags=['0x265','0x860'])
g=Game('qa/t.gba','qa/t.sav',S);g.boot_continue();g.frames(60)
g.frames(20,'down');g.frames(20,'down');g.frames(200);print('befane',g.pos())
for k in range(2): g.frames(16,'down');g.frames(10)
print(walk(g,20,12,max_steps=600),g.pos());g.frames(20,'up');g.frames(200);print('mall',g.pos())
g.frames(20,'down');g.frames(200);print('out',g.pos())
qa21.make_save('qa/t.gba',(34,47),70,25,'qa/t.sav',badges=4,flags=['0x265','0x860'])
g=Game('qa/t.gba','qa/t.sav',S);g.boot_continue();g.frames(60)
for k in range(10): g.frames(16,'down');g.frames(6)
print('arco',g.pos())
