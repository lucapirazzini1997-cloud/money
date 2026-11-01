import qa21,romlib,shutil
from qa21 import Game,S,flag,walk,face,yesno_open
shutil.copy('out/Pokemon_Romagna_0_22.gba','qa/t.gba')
qa21.make_save('qa/t.gba',(34,35),12,9,'qa/t.sav',badges=2,flags=['0x265','0x860','0x4e8'])
g=Game('qa/t.gba','qa/t.sav',S);g.boot_continue();g.frames(60);g.frames(20,'up');g.frames(200);print('roof',g.pos());g.shot('qa/rf0.png',1)
print(walk(g,2,9),g.pos());face(g,'left');g.tap('a',3,40)
for i in range(30):
    g.frames(10)
    if yesno_open(g): g.frames(10);g.tap('a',3,20);break
    g.tap('a',3,20)
g.frames(150);print('vista',g.pos());g.shot('qa/rf1.png',1)
g.frames(120);g.shot('qa/rf2.png',1)
for i in range(12): g.tap('a',3,40)
g.frames(200);print('back',g.pos())
