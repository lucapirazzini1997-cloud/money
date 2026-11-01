import qa21,sys,shutil
from qa21 import Game,S,walk,face,lib
shutil.copy('out/Pokemon_Romagna_0_22.gba','qa/t.gba')
qa21.make_save('qa/t.gba',(34,32),9,3,'qa/t.sav',badges=3,flags=['0x265','0x860'])
g=Game('qa/t.gba','qa/t.sav',S);g.boot_continue();g.frames(60);g.frames(20,'up');g.frames(30);g.frames(20,'up');g.frames(200);print(g.pos())
print(walk(g,17,5,max_steps=600),g.pos());face(g,'up')
for i in range(25): g.tap('a',3,40)
g.frames(300)
E=0x02024744
pid=lib.read32(E);otid=lib.read32(E+4);lvl=lib.read8(E+84)
sh=((pid>>16)^(pid&0xffff)^(otid>>16)^(otid&0xffff))<8
print('level',lvl,'shiny',sh);g.shot('qa/tk.png',1)
