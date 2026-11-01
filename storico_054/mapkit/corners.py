import sys
sys.path.insert(0,'/home/claude/tools'); sys.path.insert(0,'/home/claude/tools/mapkit')
import render, vocab
from collections import Counter
mt,_=render.metatile_images('gTileset_General','gTileset_Petalburg')
def corner_cols(mid):
    im=mt(mid).load()
    out=[]
    for (x0,y0) in [(0,0),(14,0),(0,14),(14,14)]:
        c=Counter(im[x0+dx,y0+dy] for dx in range(2) for dy in range(2)).most_common(1)[0][0]
        out.append(c)
    return out
if __name__=='__main__':
    for a in sys.argv[1:]:
        mid=int(a,16); print('%03X'%mid, corner_cols(mid))
