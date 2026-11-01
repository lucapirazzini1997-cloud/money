import qa21,romlib,shutil
from qa21 import Game,S,flag,walk,face
shutil.copy('out/Pokemon_Romagna_0_22.gba','qa/t.gba')
r=romlib.Rom('qa/t.gba');m=r.map(34,22)
gate=[b for b in m['bgs']];
import sys;sys.path.insert(0,'/home/claude/tools/mapkit/maps22')
for fl,un in ((['0x265','0x860'],['0x4e8']),(['0x265','0x860','0x4e8'],[])):
    # door cell = sign with R22_GrattDoor: find solid sign above the start
    import json
    L=json.load(open('out/revision_0_22.json'))
    gd=[b for b in m['bgs'] if b['arg']-0x8000000==int(L['labels']['R22_GrattDoor'],16)] if 'labels' in L else []
    bx,by=gd[0]['x'],gd[0]['y']
    qa21.make_save('qa/t.gba',(34,22),bx,by+1,'qa/t.sav',badges=2,flags=fl,unset=un)
    g=Game('qa/t.gba','qa/t.sav',S);g.boot_continue();g.frames(60);print('keys',flag(0x4e8),flag(0x1b+0x500) if False else '')
    g.frames(30,'up');g.frames(30)
    for i in range(8): g.tap('a',3,40)
    g.frames(150);print(fl[-1],g.pos())
