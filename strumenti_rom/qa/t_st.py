import qa21,romlib
from qa21 import Game,S,flag,face,walk
r=romlib.Rom('qa/t.gba');w=r.map(34,6)['warps'][1];print(w)
def run(flags):
    qa21.make_save('qa/t.gba',(34,6),w['x'],w['y']+1,'qa/t.sav',badges=2,flags=flags)
    g=Game('qa/t.gba','qa/t.sav',S);g.boot_continue();g.frames(20,'up');g.frames(200);print(g.pos())
    print(walk(g,5,5),g.pos());face(g,'up')
    for i in range(70): g.tap('a',3,30)
    return flag(0x3b),flag(0x4e7)
print('new',run(['0x265','0x860','0x3a']))
print('old save',run(['0x265','0x860','0x3a','0x3b']))
