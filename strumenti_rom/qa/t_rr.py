import qa21,romlib,shutil
from qa21 import Game,S,flag,walk,face,lib,var
shutil.copy('out/Pokemon_Romagna_0_22.gba','qa/t.gba')
for badges,fl in ((1,['0x265','0x860','0x867']),(2,['0x265','0x860','0x867','0x868'])):
    qa21.make_save('qa/t.gba',(34,43),28,23,'qa/t.sav',badges=badges,flags=fl,unset=['0x868'] if badges==1 else [])
    g=Game('qa/t.gba','qa/t.sav',S);g.boot_continue();g.frames(60)
    for k in range(3): g.frames(16,'down');g.frames(10)
    g.frames(60);print('pos',g.pos());g.shot('qa/rr_a%d.png'%badges,1)
    for i in range(14): g.tap('a',3,40)
    g.frames(400)
    E=0x02024744;print('badges',badges,'enemy pid',hex(lib.read32(E)),'species-ish',lib.read16(E+32), 'flag',flag(0x4e9))
    g.shot('qa/rr%d.png'%badges,1)
