import qa21,romlib,shutil
from qa21 import Game,S,flag,walk,face,yesno_open
shutil.copy('out/Pokemon_Romagna_0_22.gba','qa/t.gba')
r=romlib.Rom('qa/t.gba');m=r.map(34,110);o=m['objects'][-1];print('rq',o['x'],o['y'])
qa21.make_save('qa/t.gba',(34,110),o['x'],o['y']+2,'qa/t.sav',badges=8,flags=['0x265','0x864','0x860'])
g=Game('qa/t.gba','qa/t.sav',S);g.boot_continue();g.frames(60);g.shot('qa/rq0.png',1)
g.frames(10,'up');g.frames(30);face(g,'up')
for i in range(40):
    g.tap('a',3,30)
    if yesno_open(g): g.frames(10);g.tap('a',3,20)
g.frames(200);g.shot('qa/rq1.png',1)
# dive giver
m=r.map(35,26);o=m['objects'][-1];print('dv',o['x'],o['y'])
qa21.make_save('qa/t.gba',(35,26),o['x'],o['y']+1,'qa/t.sav',badges=8,flags=['0x265','0x860'])
g=Game('qa/t.gba','qa/t.sav',S);g.boot_continue();g.frames(60);face(g,'up')
for i in range(60): g.tap('a',3,30)
print('dive flag',flag(0x4e6))
