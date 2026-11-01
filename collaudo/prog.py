"""Percorso giocato: Lugo -> sentiero -> galleria -> sentiero -> Faenza -> Ponte Santerno -> Imola -> palestra."""
from pl import *
import sys
g=G(sys.argv[1]); g.mash(B,4,30)
log('PROG start',g.pos(),'b6',g.flag(0x86c),'squadra',g.party())
for dest in [(35,72),(35,74),(35,73),(34,85),(35,0),(35,1),(35,9)]:
    ok=g.travel(dest)
    log('PROG ->',dest,'ok',ok,'pos',g.pos(),'squadra',g.party())
    if not ok: break
g.shot(sys.argv[2]); g.save(sys.argv[2]+'.ss'); g.close()
