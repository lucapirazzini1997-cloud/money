import qa21,sys,shutil
from qa21 import Game,S
shutil.copy('out/Pokemon_Romagna_0_22.gba','qa/t.gba')
import romlib
r=romlib.Rom('qa/t.gba')
rooms=[(34,5),(34,16),(34,49),(34,63),(34,64),(34,66),(34,78),(34,103),(34,104),(34,105),(34,106),(34,107),(34,108),(34,1),(34,2),(34,4),(34,50),(34,77),(35,7),(35,23),(34,3),(34,28),(34,62),(34,46),(34,67),(34,23),(34,45),(34,8),(34,69),(35,4),(34,29),(34,11),(34,48),(34,65),(34,24),(35,35),(34,79),(34,83),(22,0)]
for gn in rooms:
    m=r.map(*gn);w=m['warps'][0]
    qa21.make_save('qa/t.gba',gn,w['x'],w['y']-1,'qa/t.sav',badges=8,flags=['0x265','0x2f0'])
    g=Game('qa/t.gba','qa/t.sav',S);g.boot_continue()
    g.frames(2,'down');g.frames(16,'down');g.frames(10);g.frames(20,'down');g.frames(200)
    p=g.pos();dest=r.map(w['group'],w['num'])['warps'][w['warp']]
    ok=p[0]==(w['group'],w['num']) and abs(p[1][0]-dest['x'])<=1 and abs(p[1][1]-dest['y'])<=1
    print(gn,'->',p,'expected',(w['group'],w['num']),(dest['x'],dest['y']),'OK' if ok else 'FAIL',flush=True)
