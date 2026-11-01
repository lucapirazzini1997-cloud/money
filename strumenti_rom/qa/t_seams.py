import sys; sys.path.insert(0,'qa')
import qa21, romlib, scr
from qa21 import Game,S
r=romlib.Rom('qa/t.gba'); d=open('qa/t.gba','rb').read()
MAPS=[(0,9),(0,10),(0,16),(34,14),(34,17),(34,20),(34,21),(34,22),(34,44),(35,36),(34,96),(35,40)]
bad=[]
for gn in MAPS:
    m=r.map(*gn); W,H=m['width'],m['height']; seen=set()
    for c in m['coords']:
        ins,_=scr.decode(d,c['script'],4)
        w=[i for i in ins if i[1]=='warpsilent']
        if not w: continue
        tgt=(w[0][2][0],w[0][2][1])
        if tgt in seen: continue
        seen.add(tgt)
        x,y=c['x'],c['y']
        if y==H-1: sx,sy,k=x,y-1,'down'
        elif y==0: sx,sy,k=x,y+1,'up'
        elif x==W-1: sx,sy,k=x-1,y,'right'
        else: sx,sy,k=x+1,y,'left'
        qa21.make_save('qa/t.gba',gn,sx,sy,'qa/t.sav',badges=8,flags=['0x20'])
        g=Game('qa/t.gba','qa/t.sav',S);g.boot_continue()
        for i in range(16): g.tap('b',3,30)
        g.frames(2,k);g.frames(14,k);g.frames(160)
        p=g.pos(); ok=p[0]==tgt
        print(gn,(x,y),'->',tgt,'got',p,'OK' if ok else 'BAD')
        if not ok: bad.append((gn,x,y))
print('bad',bad)
