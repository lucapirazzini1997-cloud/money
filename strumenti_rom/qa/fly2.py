import qa21,sys
from qa21 import Game,S,lib
import shutil;shutil.copy(sys.argv[1],'qa/t.gba')
fl=['FLAG_VISITED_LITTLEROOT_TOWN','FLAG_VISITED_OLDALE_TOWN','FLAG_VISITED_PETALBURG_CITY','FLAG_VISITED_PACIFIDLOG_TOWN','FLAG_VISITED_SLATEPORT_CITY']
qa21.make_save('qa/t.gba',(34,17),40,22,'qa/t.sav',badges=4,flags=fl,team=[('PIDGEOT',['FLY','','',''],40)])
g=Game('qa/t.gba','qa/t.sav',S);g.boot_continue()
st=(C:=__import__('ctypes')).create_string_buffer(lib.state_size());lib.state_save(st)
moves=eval(sys.argv[2])
for i,mv in enumerate(moves):
    lib.state_load(st)
    g.tap('start',3,40);g.tap('down');g.tap('a',3,60);g.tap('a',3,40);g.tap('down');g.tap('a',3,90)
    for k in mv: g.tap(k,3,12)
    g.shot('qa/m%d.png'%i,1)
    g.tap('a',3,30);g.frames(400)
    print(mv, g.pos());g.shot('qa/d%d.png'%i,1)
