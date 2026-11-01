from pl import *
g=G('prog_b6b.ss'); g.mash(B,4,30)
if g.pos()[:2]!=(13,8):
    for ch in (route(35,0,g.pos()[:2],(13,8),live=g.live(),objs=[c for c in g.lobjs() if c!=(12,8)]) or ''): g.step(ch)
g.step('L',3); g.e.run(10); g.key(A,3,60)
for i in range(20):
    if g.e.ram(0x3000e41,1)[0]==0: break
    g.key(A,3,60)
g.shot('ponte'); log('PROG3 tecnico flag 0x4c0',g.flag(0x4c0),'pos',g.pos())
for dest in [(35,1),(35,9)]:
    ok=g.travel(dest); log('PROG3 ->',dest,'ok',ok,'pos',g.pos(),'squadra',g.party())
g.shot('imola_gym'); g.save('prog_imola.ss')
# ritorno e cura: dal centro di Imola
ok=g.heal(); log('PROG3 cura a Imola',ok,g.pos(),g.party())
g.close()
