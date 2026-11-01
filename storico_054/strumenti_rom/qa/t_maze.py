import qa21,sys,shutil
from qa21 import Game,S,lib,flag,walk,face
shutil.copy('out/Pokemon_Romagna_0_22.gba','qa/t.gba')
qa21.make_save('qa/t.gba',(34,32),12,9,'qa/t.sav',badges=3,team=[('BLAZIKEN',['EMBER','','',''],60)])
g=Game('qa/t.gba','qa/t.sav',S);g.boot_continue();g.frames(20,'up');g.frames(150);print(g.pos())
g.shot('qa/mz0.png',1)
print(walk(g,17,5),g.pos())
face(g,'up');g.tap('a',3,40)
for i in range(12): g.tap('a',3,40)
g.frames(300);g.shot('qa/mz1.png',1)
# enemy mon
p=0x02024744
pid=lib.read32(p);ot=lib.read32(p+4)
print('enemy pid',hex(pid),'shiny value',((pid>>16)^(pid&0xffff)^(ot>>16)^(ot&0xffff)))
