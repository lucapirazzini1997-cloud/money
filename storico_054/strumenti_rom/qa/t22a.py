import qa21,sys,ctypes
from qa21 import Game,S,lib,flag
import shutil
rom='out/Pokemon_Romagna_0_22.gba';shutil.copy(rom,'qa/t.gba')
# fly guard
qa21.make_save('qa/t.gba',(34,17),40,22,'qa/t.sav',badges=3,flags=[],team=[('PIDGEOT',['FLY','','',''],40)])
g=Game('qa/t.gba','qa/t.sav',S);g.boot_continue()
print('visited',[flag(0x86f+i) for i in range(16)])
