import sys; sys.path.insert(0,'qa')
import qa21
from qa21 import Game,S
from PIL import Image
def tour(gn,pts,out,cols=3,badges=0,scale=2):
    ims=[]
    for (x,y) in pts:
        qa21.make_save('qa/t.gba',gn,x,y,'qa/t.sav',badges=badges)
        g=Game('qa/t.gba','qa/t.sav',S);g.boot_continue()
        for k in range(14): g.tap('b',3,40)
        g.frames(60)
        ims.append(g.shot('qa/_s.png',1)); print((x,y),g.pos())
    rows=(len(ims)+cols-1)//cols
    W=Image.new('RGB',(240*cols,160*rows))
    for i,im in enumerate(ims): W.paste(im,((i%cols)*240,(i//cols)*160))
    W.resize((W.width*scale,W.height*scale),Image.NEAREST).save(out)
if __name__=='__main__':
    g,n=int(sys.argv[1]),int(sys.argv[2]); pts=eval(sys.argv[3]); tour((g,n),pts,sys.argv[4])
