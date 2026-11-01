import qa21,sys,shutil
from qa21 import Game,S,lib,flag,walk,face,answer
shutil.copy('out/Pokemon_Romagna_0_22.gba','qa/t.gba')
import romlib
r=romlib.Rom('qa/t.gba')
# campagna door of the Casa delle Aie
m=r.map(34,20); w=m['warps'][0]; print('aie door',w)
qa21.make_save('qa/t.gba',(34,20),w['x'],w['y']+1,'qa/t.sav',badges=3,flags=['0x%x'%(0x500+i) for i in range(790,795)])
g=Game('qa/t.gba','qa/t.sav',S);g.boot_continue();g.frames(20,'up');g.frames(150);print(g.pos())
g.shot('qa/aie0.png',1)
walk(g,17,3) or walk(g,18,4) or walk(g,16,4)
print(g.pos())
(gn,(x,y))=g.pos()
face(g,'down' if y<4 else ('right' if x<17 else 'left'))
g.tap('a',3,30)
for i in range(30): g.tap('a',3,25)
g.shot('qa/aie1.png',1)
a=lib.read32(S['gSaveBlock1Ptr'])
print('snorlax flag',flag(0x4dc),'party count',lib.read8(a+0x234))
# party slot 2 species/personality
p=0x020244ec+100
print('pid',hex(lib.read32(p)),'otid',hex(lib.read32(p+4)))
pid=lib.read32(p);ot=lib.read32(p+4)
print('shiny value',((pid>>16)^(pid&0xffff)^(ot>>16)^(ot&0xffff)),'level',lib.read8(p+84))
