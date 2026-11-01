import qa21,romlib
from qa21 import Game,S,walk,face
r=romlib.Rom('qa/t.gba');m=r.map(22,0);print([(o['x'],o['y'],o['gfx']) for o in m['objects']],m['warps'])
qa21.make_save('qa/t.gba',(34,21),7,7,'qa/t.sav',badges=2,flags=['0x265','0x860'])
g=Game('qa/t.gba','qa/t.sav',S);g.boot_continue();g.frames(20,'up');g.frames(200);print(g.pos())
o=[o for o in m['objects'] if o['gfx']!=85][0]
print(walk(g,o['x'],o['y']+2) or walk(g,o['x']+1,o['y']+1),g.pos())
face(g,'up');g.tap('a',3,60);g.frames(60);g.shot('qa/f_pens.png',1)
