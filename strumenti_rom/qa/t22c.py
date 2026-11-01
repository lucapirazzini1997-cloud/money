import qa21,sys
from qa21 import Game,S,lib,flag,walk,face,answer
import shutil
rom='out/Pokemon_Romagna_0_22.gba';shutil.copy(rom,'qa/t.gba')
qa21.make_save('qa/t.gba',(34,22),37,15,'qa/t.sav',badges=3)
g=Game('qa/t.gba','qa/t.sav',S);g.boot_continue();g.frames(20,'up');g.frames(150)
walk(g,6,7);face(g,'up');g.tap('a',3,30)
print(answer(g,[True,True,False,True]));[g.tap('a',3,40) for _ in range(12)];print('bike',flag(0x4da))
g.shot('qa/q.png',1)
