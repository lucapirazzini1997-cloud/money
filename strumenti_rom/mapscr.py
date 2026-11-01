import romlib,scr,struct,sys
r=romlib.Rom('base21.gba');d=bytes(r.data);B=0x08000000
def roots(m):
    out=[]
    for kind,p in r.map_scripts(m):
        if kind in (2,4):
            q=p
            while struct.unpack_from('<H',d,q)[0]:
                out.append(('ms%d var%x=%d'%(kind,struct.unpack_from('<H',d,q)[0],struct.unpack_from('<H',d,q+2)[0]),romlib.u32(d,q+4)-B));q+=8
        else: out.append(('ms%d'%kind,p))
    for i,o in enumerate(m['objects']):
        if o['script']: out.append(('obj%d'%(i+1),o['script']))
    for c in m['coords']: out.append(('coord %d,%d'%(c['x'],c['y']),c['script']))
    for b in m['bgs']:
        if b['kind']<5: out.append(('bg %d,%d'%(b['x'],b['y']),b['arg']-B))
    return out
if __name__=='__main__':
    g,n=map(int,sys.argv[1].split(','));m=r.map(g,n)
    seen=set();full='-v' in sys.argv
    for lab,p in roots(m):
        if p in seen: continue
        seen.add(p)
        ins,_=scr.decode(d,p,600)
        names=[x[1] for x in ins]
        interesting=[x for x in ins if x[1] in ('applymovement','setmetatile','warp','warpsilent','setobjectxy','setobjectxyperm','moveobjectoffscreen','trainerbattle','givemon','giveitem','special','specialvar','callnative','setflag','clearflag','setvar','checkflag','goto_if','call','goto','removeobject','addobject','copyobjectxytoperm','showobjectat','hideobjectat')]
        print('##',lab,hex(p),len(ins),'ins')
        if full: print(scr.show(d,p,600))
        else:
            for a,nm,args in interesting: print('   %x %s %s'%(a,nm,[hex(x) for x in args]))
