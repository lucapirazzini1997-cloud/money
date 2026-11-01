import qa21,romlib
from qa21 import Game,S,flag,face,walk
r=romlib.Rom('qa/t.gba');w=r.map(35,19)['warps'][7];print(w)
qa21.make_save('qa/t.gba',(35,19),w['x'],w['y']+1,'qa/t.sav',badges=8,flags=['0x265','0x860','0x80e'])
g=Game('qa/t.gba','qa/t.sav',S);g.boot_continue();g.frames(20,'up');g.frames(200);print(g.pos())
g.frames(16,'up');g.frames(20);walk(g,11,26);face(g,'left');g.shot('qa/dv0.png',1)
for i in range(70): g.tap('a',3,30)
print('dive flag',flag(0x4e6))
# Lugo: enter from a door
L=r.map(34,110);ws=sorted(L['warps'],key=lambda w:abs(w['x']-26)+abs(w['y']-24))[0];print(ws)
qa21.make_save('qa/t.gba',(ws['group'],ws['num']),1,1,'qa/t.sav',badges=8,flags=['0x265','0x864','0x860'])
