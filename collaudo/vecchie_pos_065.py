# 0.65: caselle calpestabili di 35.51 nella 0.64 da cui, nella 0.65, non si arriva a piedi alle uscite (frecce sud, porta).
import sys, collections
sys.path[:0]=['analisi','strumenti_rom']
import romlib, percorso as PC
K=(35,51)
def raggiunte(rom, part, ab, flag=()):
    R=romlib.Rom(rom); st=PC.cerca(R, (K,part), ab, flag_alzate=flag)
    return {(x,y,z) for (k,x,y,z,s) in st if k==K and not s}
old=set()
for p in ((20,32),(21,28)):
    try: old|=raggiunte('out/Pokemon_Romagna_0_64.gba', p, {'surf','spacca','taglio','forza','cascata'})
    except Exception as e: print('err',p,e)
print('vecchie posizioni', len(old))
# nuova mappa: chi arriva alle frecce sud (23-25,61) o alla porta della centrale senza abilita'
R=romlib.Rom('out/Pokemon_Romagna_0_65.gba'); Wm=PC.Mondo(R); m=Wm.mappa(K)
ogg={(o['x'],o['y']) for o in m['objects']}
def vicini(x,y,z):
    for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
        t=Wm.casella(K,x+dx,y+dy)
        if t is None or t['coll'] or (x+dx,y+dy) in ogg: continue
        if t['b'] in PC.SURFABILE: continue
        if not (t['z']==z or t['z'] in (0,15) or z in (0,15)): continue
        yield x+dx,y+dy,(z if t['z'] in (0,15) else t['z'])
mete={(23,61),(24,61),(25,61),(29,42)}
bloccati=[]
for (x,y,z) in sorted(old):
    c=Wm.casella(K,x,y)
    z0=z
    seen={(x,y,z0)}; q=collections.deque([(x,y,z0)]); ok=False
    while q:
        s=q.popleft()
        if (s[0],s[1]) in mete or any((nx,ny) in mete for nx,ny in ((s[0]+1,s[1]),(s[0]-1,s[1]),(s[0],s[1]+1),(s[0],s[1]-1))): ok=True; break
        for n in vicini(*s):
            if n not in seen: seen.add(n); q.append(n)
    if not ok: bloccati.append((x,y,z,c['coll'],c['z'],hex(c['b'])))
print('bloccati', len(bloccati))
for b in bloccati: print(b)
