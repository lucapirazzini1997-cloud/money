import qa21,sys,shutil
from qa21 import Game,S,lib,flag,walk,face
shutil.copy('out/Pokemon_Romagna_0_22.gba','qa/t.gba')
spots=[((0,9),20,20),((0,9),8,17),((0,10),30,36),((0,10),25,24),((34,20),15,12),((34,21),10,13),((34,22),20,25),((34,17),30,22),((34,47),30,25),((34,44),20,28)]
from PIL import Image
ims=[]
for i,(gn,x,y) in enumerate(spots):
    qa21.make_save('qa/t.gba',gn,x,y,'qa/t.sav',badges=3)
    g=Game('qa/t.gba','qa/t.sav',S);g.boot_continue()
    ims.append(g.shot('qa/tour%d.png'%i,1)); print(i,g.pos())
W=Image.new('RGB',(240*4,160*3))
for i,im in enumerate(ims): W.paste(im,((i%4)*240,(i//4)*160))
W.save('qa/tour.png')
