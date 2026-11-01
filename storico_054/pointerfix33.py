"""Repair raw offset arguments emitted by the inherited sign helper.

Object/coordinate scripts are offsets in romlib, but background script arguments
are already absolute GBA addresses. Normalise only facing-script event kinds;
hidden items and secret-base packed arguments must remain untouched.
"""
from engine32 import *

def install():
 repaired=[]
 for g,count in romlib.COUNTS.items():
  for n in range(count):
   key=(g,n);m=W.rom.map(*key);bgs=copy.deepcopy(m['bgs']);changes=[]
   for b in bgs:
    p=b['arg']
    if b['kind'] in (0,1,2,3,4) and 0<p<len(W.d):
     assert W.d[p] in (0x6a,0x6b,0x05,0x0f,0x02,0x03,0x2b,0x16), (key,b,hex(W.d[p]))
     b['arg']=B+p;changes.append(dict(x=b['x'],y=b['y'],offset=p))
   if changes:
    events(key,bgs=bgs);repaired.append(dict(map=list(key),events=changes))
    W.changes.append(dict(name='rev33_puntatori_cartelli',map=list(key),repaired=len(changes)))
 W.changes.append(dict(name='puntatori_cartelli_riparati',maps=repaired,total=sum(len(m['events']) for m in repaired)))
