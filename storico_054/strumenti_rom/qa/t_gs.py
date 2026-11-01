import qa21,sys,shutil,romlib
from qa21 import Game,S,lib,flag,walk,face
import inject
W=inject.Writer('out/Pokemon_Romagna_0_22.gba',start=0x1f00000);W.set_events(1,4,coords=[]);W.save('qa/t.gba')
w=romlib.Rom('qa/t.gba').map(0,9)['warps'][2]
qa21.make_save('qa/t.gba',(0,9),w['x'],w['y']+1,'qa/t.sav',badges=8,flags=['0x265','0x864','0x20','0x860'])
g=Game('qa/t.gba','qa/t.sav',S);g.boot_continue();g.frames(20,'up');g.frames(200);print(g.pos())
for k in range(4):
    ok=walk(g,6,5)
    if ok: break
    for i in range(10): g.tap('a',3,30)
    g.frames(200)
print(ok,g.pos());g.shot('qa/lab.png',1);face(g,'up')
for i in range(70): g.tap('a',3,35)
print('gs flag',flag(0x4e5))
# now go to the shrine in the pineta
qa21.make_save('qa/t.gba',(0,16),32,6,'qa/t.sav',badges=8,flags=['0x265','0x864','0x4e5'],items=[('MYSTIC_TICKET',0x5d8,30)])
g=Game('qa/t.gba','qa/t.sav',S);g.boot_continue()
face(g,'up');g.tap('a',3,40)
from qa21 import yesno_open
for i in range(30):
    g.frames(10)
    if yesno_open(g): g.frames(15);g.tap('a',3,20);break
    g.tap('a',3,20)
for i in range(8): g.tap('a',3,40)
g.frames(300);g.shot('qa/celebi.png',1)
