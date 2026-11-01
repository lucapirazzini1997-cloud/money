from pl import *
import sys
g=G(sys.argv[1]); g.mash(B,4,30)
for att in range(4):
    g.heal(); log('PROG2 curato',g.party())
    for dest in [(35,0),(35,1),(35,9)]:
        g.lost=False
        ok=g.travel(dest); log('PROG2 ->',dest,'ok',ok,'pos',g.pos(),'squadra',g.party())
        if not ok or getattr(g,'lost',False): break
    if g.pos()[2:]==(35,9): break
g.shot(sys.argv[2]); g.save(sys.argv[2]+'.ss'); g.close()
