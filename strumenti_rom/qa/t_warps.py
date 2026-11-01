import qa21,sys,shutil,json
from qa21 import Game,S,lib,flag
shutil.copy('out/Pokemon_Romagna_0_22.gba','qa/t.gba')
import romlib
r=romlib.Rom('qa/t.gba')
maps=[tuple(map(int,a.split(','))) for a in sys.argv[1:]]
def walkable(m,a,x,y):
    return 0<=x<m['width'] and 0<=y<m['height'] and not (int(a[y,x])&0xc00) and (x,y) not in {(o['x'],o['y']) for o in m['objects']}
res=[]
for gn in maps:
    m=r.map(*gn);a=r.blocks(m)
    for i,w in enumerate(m['warps']):
        x,y=w['x'],w['y']
        if (x,y) in ((0,0),(1,0)): continue
        appr=None
        order=((0,1,'up'),(1,0,'left'),(-1,0,'right'),(0,-1,'down'))
        if y==m['height']-1: order=((0,-1,'down'),)
        elif x==0: order=((1,0,'left'),)
        elif x==m['width']-1: order=((-1,0,'right'),)
        elif y==0: order=((0,1,'up'),)
        for (dx,dy,key) in order:
            if walkable(m,a,x+dx,y+dy): appr=(x+dx,y+dy,key);break
        if not appr: res.append((gn,i,'no approach'));continue
        qa21.make_save('qa/t.gba',gn,appr[0],appr[1],'qa/t.sav',badges=8,flags=['0x265','0x2f0','0x20'])
        g=Game('qa/t.gba','qa/t.sav',S);g.boot_continue()
        g.frames(2,appr[2]);g.frames(16,appr[2]);g.frames(10);g.frames(20,appr[2]);g.frames(160)
        p=g.pos()
        ok = p[0]==(w['group'],w['num'])
        res.append((gn,i,(x,y),'->',(w['group'],w['num']),'OK' if ok else 'FAIL got %s'%(p,)))
        print(res[-1],flush=True)
