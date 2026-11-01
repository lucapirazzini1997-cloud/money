import qa21,sys,ctypes
from qa21 import Game,S,lib
import shutil;shutil.copy(sys.argv[1],'qa/t.gba')
fl=['FLAG_VISITED_%s'%n for n in 'LITTLEROOT_TOWN OLDALE_TOWN DEWFORD_TOWN LAVARIDGE_TOWN FALLARBOR_TOWN VERDANTURF_TOWN PACIFIDLOG_TOWN PETALBURG_CITY SLATEPORT_CITY MAUVILLE_CITY RUSTBORO_CITY FORTREE_CITY LILYCOVE_CITY MOSSDEEP_CITY SOOTOPOLIS_CITY EVER_GRANDE_CITY'.split()]
qa21.make_save('qa/t.gba',(34,17),40,22,'qa/t.sav',badges=int(sys.argv[2]),flags=fl+sys.argv[3:],team=[('PIDGEOT',['FLY','','',''],40)])
g=Game('qa/t.gba','qa/t.sav',S);g.boot_continue()
print([qa21.flag(0x86f+i) for i in range(16)])
g.tap('start',3,40);g.tap('down');g.tap('a',3,60);g.tap('a',3,40);g.tap('down');g.tap('a',3,90)
g.shot('qa/all.png')
