import qa21,sys
from qa21 import Game,S
rom=sys.argv[1] if len(sys.argv)>1 else 'base21.gba'
import shutil;shutil.copy(rom,'qa/t.gba')
fl=['FLAG_VISITED_LITTLEROOT_TOWN','FLAG_VISITED_OLDALE_TOWN','FLAG_VISITED_PETALBURG_CITY','FLAG_VISITED_PACIFIDLOG_TOWN','FLAG_VISITED_SLATEPORT_CITY']
qa21.make_save('qa/t.gba',(34,17),40,22,'qa/t.sav',badges=4,flags=fl,team=[('PIDGEOT',['FLY','',None,None][:1]+['','',''],40)])
g=Game('qa/t.gba','qa/t.sav',S);g.boot_continue()
print([qa21.flag(0x86f+i) for i in range(16)])
g.tap('start',3,40);g.shot('qa/f0.png')
g.tap('down');g.tap('a',3,60);g.shot('qa/f1.png')
g.tap('a',3,40);g.shot('qa/f2.png')
g.tap('down');g.tap('a',3,90);g.shot('qa/f3.png')
for k in ['left','left','down','right','up','up']:
    g.tap(k,3,20)
g.shot('qa/f4.png')
