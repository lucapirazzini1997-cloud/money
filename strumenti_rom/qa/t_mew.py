import qa21,romlib,shutil
from qa21 import Game,S,flag,walk,face,yesno_open
shutil.copy('out/Pokemon_Romagna_0_22.gba','qa/t.gba')
for fl in (['0x265','0x860'],['0x265','0x860','0x864']):
    qa21.make_save('qa/t.gba',(34,1),8,10,'qa/t.sav',badges=8,flags=fl)
    g=Game('qa/t.gba','qa/t.sav',S);g.boot_continue();g.frames(60);g.frames(20,'down');g.frames(200);print('lido',g.pos())
    print(walk(g,50,34,max_steps=400),g.pos());face(g,'right')
    g.tap('a',3,40)
    for i in range(30):
        g.frames(10)
        if yesno_open(g): g.frames(10);g.tap('a',3,20);break
        g.tap('a',3,20)
    for i in range(6): g.tap('a',3,30)
    g.frames(250);print(fl[-1],'->',g.pos());g.shot('qa/mw_%s.png'%fl[-1],1)
# back from the island
w=g.pos()
if w[0]==(26,56):
    face(g,'down');g.tap('a',3,40)
    for i in range(30):
        g.frames(10)
        if yesno_open(g): g.frames(10);g.tap('a',3,20);break
        g.tap('a',3,20)
    for i in range(6): g.tap('a',3,30)
    g.frames(250);print('return ->',g.pos())
