"""Enter/exit every door of a city map and cross its edge warps. usage: t_city.py g n"""
import qa21,romlib,sys
from qa21 import Game,S,walk
g_,n_=int(sys.argv[1]),int(sys.argv[2])
r=romlib.Rom('qa/t.gba');m=r.map(g_,n_)
bad=[]
for i,w in enumerate(m['warps']):
    edge = w['x'] in (0,m['width']-1) or w['y'] in (0,m['height']-1)
    if edge:
        dx,dy=(1,0) if w['x']==0 else (-1,0) if w['x']==m['width']-1 else (0,1) if w['y']==0 else (0,-1)
        sx,sy=w['x']+dx,w['y']+dy; key={(1,0):'left',(-1,0):'right',(0,1):'up',(0,-1):'down'}[(dx,dy)]
    else:
        sx,sy=w['x'],w['y']+1; key='up'
    qa21.make_save('qa/t.gba',(g_,n_),sx,sy,'qa/t.sav',badges=8,flags=['0x265','0x860','0x4e8'])
    G=Game('qa/t.gba','qa/t.sav',S);G.boot_continue();G.frames(40)
    for k in range(3): G.frames(18,key);G.frames(8)
    G.frames(200);p=G.pos()
    ok=p[0]==(w['group'],w['num'])
    print(i,(w['x'],w['y']),'->',p,'OK' if ok else 'FAIL')
    if not ok: bad.append(i)
print('bad',bad)
