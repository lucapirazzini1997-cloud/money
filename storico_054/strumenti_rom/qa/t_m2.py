import qa21
from qa21 import Game,S,lib,flag,yesno_open,walk,face
def yes(g,n=30):
    for i in range(n):
        g.frames(10)
        if yesno_open(g): g.frames(15);g.tap('a',3,15);return True
        g.tap('a',3,15)
    return False
def enemy(): return hex(lib.read32(0x02024744))
# Mewtwo cave: player surfing below the mouth (simulate: stand on water cell)
for fl in (['0x265','0x860'],['0x265','0x860','0x864']):
    qa21.make_save('qa/t.gba',(34,22),52,34,'qa/t.sav',badges=8,flags=fl,unset=['0x864'] if len(fl)==2 else [])
    g=Game('qa/t.gba','qa/t.sav',S);g.boot_continue();g.frames(60);face(g,'up');g.tap('a',3,30);r_=yes(g,15);g.frames(250);print(fl[-1],'cave?',r_,g.pos())
g.shot('qa/grotta.png',1)
print(walk(g,13,5),g.pos());face(g,'up');[g.tap('a',3,30) for _ in range(10)];g.frames(300);print('mewtwo',enemy());g.shot('qa/m2b.png',1)
qa21.make_save('qa/t.gba',(35,43),12,19,'qa/t.sav',badges=8,flags=['0x265','0x860','0x864'])
g=Game('qa/t.gba','qa/t.sav',S);g.boot_continue();g.frames(60)
for k in range(3): g.frames(18,'down');g.frames(8)
g.frames(200);print('exit',g.pos())
# motonave
r=__import__('romlib').Rom('qa/t.gba');w=r.map(34,96)['warps'][12]
qa21.make_save('qa/t.gba',(34,96),w['x'],w['y']+1,'qa/t.sav',badges=8,flags=['0x265','0x860','0x864'])
g=Game('qa/t.gba','qa/t.sav',S);g.boot_continue();g.frames(40);g.frames(16,'up');g.frames(200);g.frames(16,'down');g.frames(200);print('ravenna',g.pos())
print(walk(g,66,45,max_steps=300),g.pos());face(g,'right');g.tap('a',3,30);print('yes',yes(g));[g.tap('a',3,30) for _ in range(4)];g.frames(300);print('navel',g.pos());g.shot('qa/navel.png',1)
face(g,'down');g.tap('a',3,30);print('back yes',yes(g));[g.tap('a',3,30) for _ in range(4)];g.frames(300);print('back',g.pos())
