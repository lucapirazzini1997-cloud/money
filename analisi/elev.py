import sys, collections
sys.path.insert(0,str(__import__('pathlib').Path(__file__).resolve().parent.parent/'strumenti_rom'))
import romlib
SURF={0x10,0x11,0x12,0x14,0x15,0x19,0x1a,0x1b}
R=romlib.Rom(sys.argv[1])
for key in sys.argv[2:]:
    g,n=map(int,key.split('.'))
    m=R.map(g,n); bl=R.blocks(m)
    c=collections.Counter(); bad=[]
    for y in range(m['height']):
        for x in range(m['width']):
            v=int(bl[y,x]); b=R.attr(m,v&1023)&0xff
            if b in SURF:
                el=v>>12; c[(hex(b),(v>>10)&3,el)]+=1
                if el not in (0,1) and (v>>10)&3==0: bad.append((x,y))
    print(key,dict(c),'sospette',len(bad),bad[:30])
