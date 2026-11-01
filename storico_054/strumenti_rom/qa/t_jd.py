import qa21
from qa21 import Game,S,lib,flag,yesno_open,walk,face
def yes(g,n=30):
    for i in range(n):
        g.frames(10)
        if yesno_open(g): g.frames(15);g.tap('a',3,15);return True
        g.tap('a',3,15)
    return False
def enemy(): return hex(lib.read32(0x02024744))
# --- Jirachi
qa21.make_save('qa/t.gba',(0,10),57,22,'qa/t.sav',badges=8,flags=['0x265','0x860','0x864'],team=[('WAILORD',['SURF','DIVE','',''],60)])
g=Game('qa/t.gba','qa/t.sav',S);g.boot_continue();g.frames(60);print('gates hidden?',flag(0x4ee))
g.frames(2,'right');g.frames(10);g.tap('a',3,30);print('surf',yes(g));[g.tap('a',3,20) for _ in range(4)];g.frames(200);print(g.pos())
for k in range(2): g.frames(16,'right');g.frames(10)
print('at',g.pos());face(g,'right');g.tap('a',3,30);print('portal yes',yes(g));g.frames(300);print('wish',g.pos());g.shot('qa/wish.png',1)
print(walk(g,13,4),g.pos());face(g,'right');[g.tap('a',3,30) for _ in range(10)];g.frames(300);print('jirachi enemy',enemy());g.shot('qa/jira.png',1)
# --- Deoxys
qa21.make_save('qa/t.gba',(35,40),29,16,'qa/t.sav',badges=8,flags=['0x265','0x860','0x864'])
g=Game('qa/t.gba','qa/t.sav',S);g.boot_continue();g.frames(60);face(g,'up');g.tap('a',3,30);print('rocket yes',yes(g));[g.tap('a',3,30) for _ in range(5)];g.frames(300);print('moon',g.pos());g.shot('qa/moon.png',1)
print(walk(g,19,10),g.pos());face(g,'right');[g.tap('a',3,30) for _ in range(10)];g.frames(300);print('deoxys enemy',enemy());g.shot('qa/deox.png',1)
qa21.make_save('qa/t.gba',(35,41),6,10,'qa/t.sav',badges=8,flags=['0x265','0x860','0x864'])
g=Game('qa/t.gba','qa/t.sav',S);g.boot_continue();g.frames(60);face(g,'up');g.tap('a',3,30);print('back yes',yes(g));g.frames(300);print('back',g.pos())
# before the League: rocket refuses
qa21.make_save('qa/t.gba',(35,40),29,16,'qa/t.sav',badges=8,flags=['0x265','0x860'],unset=['0x864'])
g=Game('qa/t.gba','qa/t.sav',S);g.boot_continue();g.frames(60);face(g,'up');g.tap('a',3,30);print('pre-league yesno?',yes(g,12));g.frames(100);print('pre',g.pos(),'gates hidden',flag(0x4ee))
