import qa21,romlib,shutil
from qa21 import Game,S,flag,walk,face
shutil.copy('out/Pokemon_Romagna_0_22.gba','qa/t.gba')
qa21.make_save('qa/t.gba',(0,10),6,43,'qa/t.sav',badges=2,flags=['0x265','0x860'])
g=Game('qa/t.gba','qa/t.sav',S);g.boot_continue();g.frames(60)
print('start',g.pos())
g.frames(60,'left');g.frames(120);print('gate?',g.pos());g.shot('qa/gt0.png',1)
g.frames(200,'left');g.frames(150);print('saline?',g.pos());g.shot('qa/gt1.png',1)
g.frames(16,'right');g.frames(30,'right');g.frames(150);print('gate back?',g.pos())
g.frames(200,'right');g.frames(150);print('cervia?',g.pos());g.shot('qa/gt2.png',1)
