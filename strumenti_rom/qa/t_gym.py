import qa21,romlib,shutil
from qa21 import Game,S,flag,walk,face
r=romlib.Rom('qa/t.gba');w=r.map(0,10)['warps'][1]
qa21.make_save('qa/t.gba',(0,10),w['x'],w['y']+1,'qa/t.sav',badges=1,flags=['0x265','0x860','0x24','0x25','0x23','0x26'])
g=Game('qa/t.gba','qa/t.sav',S);g.boot_continue();g.frames(20,'up');g.frames(200);print(g.pos())
print(walk(g,20,20),g.pos());face(g,'up')
for i in range(25): g.tap('a',3,30)
for i in range(5): g.tap('b',3,20)
print('flags',flag(0x26),flag(0x27))
print(walk(g,12,9),g.pos())
g.frames(80,'up');g.frames(30);print(g.pos());g.shot('qa/gy1.png',1)
