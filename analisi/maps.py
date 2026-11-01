import sys, json, struct
sys.path.insert(0,str(__import__('pathlib').Path(__file__).resolve().parent.parent/'strumenti_rom'))
import romlib
R=romlib.Rom(sys.argv[1]); names={int(k):v for k,v in json.load(open(sys.argv[2])).items()}
# discover counts per group by validity
d=bytes(R.data)
out={}
for g in range(40):
    gp=R.ptr(romlib.GROUPS+g*4)
    if gp is None or gp>len(d): break
    for n in range(256):
        try:
            hp=R.ptr(gp+n*4)
            if hp is None or hp>=len(d): break
            m=R.map(g,n)
            if not (0<m['width']<=300 and 0<m['height']<=300): break
        except Exception: break
        out[(g,n)]=m
for k,m in sorted(out.items()):
    if k[0] in (0,34,35) or len(sys.argv)>3:
        print(k, names.get(m['region'],'?%d'%m['region']), m['width'],'x',m['height'], 'w%d c%d o%d b%d'%(len(m['warps']),len(m['coords']),len(m['objects']),len(m['bgs'])), 'conn',[(c['dir'],c['group'],c['num']) for c in m['conns']])
