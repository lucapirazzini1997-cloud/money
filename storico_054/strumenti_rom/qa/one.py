import qa21,sys,shutil
from qa21 import Game,S
shutil.copy('out/Pokemon_Romagna_0_22.gba','qa/t.gba')
gn=tuple(map(int,sys.argv[1].split(',')));x,y=int(sys.argv[2]),int(sys.argv[3])
qa21.make_save('qa/t.gba',gn,x,y,'qa/t.sav',badges=int(sys.argv[5]) if len(sys.argv)>5 else 3)
g=Game('qa/t.gba','qa/t.sav',S);g.boot_continue();g.shot(sys.argv[4],2);print(g.pos())
