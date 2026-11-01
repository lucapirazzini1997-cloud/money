import qa21,sys,shutil
from qa21 import Game,S,lib,flag,yesno_open
shutil.copy('out/Pokemon_Romagna_0_22.gba','qa/t.gba')
qa21.make_save('qa/t.gba',(35,36),24,12,'qa/t.sav',badges=8,flags=['0x265'],team=[('WAILORD',['SURF','DIVE','',''],60)])
g=Game('qa/t.gba','qa/t.sav',S);g.boot_continue()
def press_until_yesno(n=30):
    for i in range(n):
        g.frames(10)
        if yesno_open(g): g.frames(15); return True
        g.tap('a',3,15)
    return False
def step(d,n=1):
    for _ in range(n): g.frames(2,d);g.frames(14,d);g.frames(10)
g.frames(2,'left');g.frames(10);g.tap('a',3,30)
print('surf prompt',press_until_yesno());g.shot('qa/k0.png',1);g.tap('a',3,10);g.frames(200);print(g.pos());g.shot('qa/k1.png',1)
step('left',1);step('down',1);print(g.pos())
g.shot('qa/k2.png',1);g.tap('a',3,30);print('dive prompt',press_until_yesno());g.shot('qa/k3.png',1);g.tap('a',3,10);[g.tap('a',3,30) for _ in range(6)];g.frames(400);print('after dive',g.pos())
g.shot('qa/uw.png',2)
from qa21 import walk,face
print(walk(g,23,14),g.pos());face(g,'down');g.tap('a',3,30)
for i in range(10): g.tap('a',3,30)
g.frames(300);g.shot('qa/kyb.png',1)
print('enemy species',lib.read16(0x02024744+32) if False else hex(lib.read32(0x02024744)))
