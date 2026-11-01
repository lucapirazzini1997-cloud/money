import qa21,romlib
from qa21 import Game,S,lib,flag,walk,face,yesno_open
r=romlib.Rom('qa/t.gba')
# villa: up the stairs, the new bedroom, the PC, back down
w=r.map(0,9)['warps'][1]
qa21.make_save('qa/t.gba',(0,9),w['x'],w['y']+1,'qa/t.sav',badges=1,flags=['0x265','0x860'])
g=Game('qa/t.gba','qa/t.sav',S);g.boot_continue();g.frames(20,'up');g.frames(200)
print(walk(g,12,3),g.pos());g.frames(20,'up');g.frames(200);print('2F',g.pos());g.shot('qa/f_2f.png',1)
print(walk(g,4,4),g.pos());face(g,'up');g.tap('a',3,40);g.frames(90);g.shot('qa/f_pc.png',1)
for i in range(6): g.tap('b',3,30)
g.frames(60);print(walk(g,10,3),g.pos());g.frames(20,'up');g.frames(200);print('back 1F',g.pos())
# Pensione: talk to the lady
m=r.map(34,21);print([(o['x'],o['y'],o['gfx']) for o in m['objects']],[(w_['x'],w_['y'],w_['group'],w_['num']) for w_ in m['warps']])
