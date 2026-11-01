import qa21,romlib,shutil
from qa21 import Game,S,flag,walk,face
r=romlib.Rom('qa/t.gba');L=r.map(0,9)
def enter(i,extra=None,flags=['0x265','0x860']):
    w=L['warps'][i]
    qa21.make_save('qa/t.gba',(0,9),w['x'],w['y']+1,'qa/t.sav',badges=2,flags=flags)
    g=Game('qa/t.gba','qa/t.sav',S);g.boot_continue();g.frames(20,'up');g.frames(200);return g
g=enter(4);print('bar',g.pos());g.shot('qa/l_bar.png',1)
print(walk(g,6,5),g.pos());face(g,'up');g.tap('a',3,60);g.shot('qa/l_barman.png',1)
for i in range(10): g.tap('b',3,20)
g=enter(1);print('villa',g.pos());print(walk(g,12,3),g.pos());g.frames(20,'up');g.frames(150);print('2F',g.pos());g.shot('qa/l_2f.png',1)
g.frames(30,'down');g.frames(150);print('back',g.pos())
g=enter(0);print('aldo',g.pos());print(walk(g,12,3),g.pos());g.frames(20,'up');g.frames(150);print('aldo2F',g.pos());g.shot('qa/l_a2.png',1)
