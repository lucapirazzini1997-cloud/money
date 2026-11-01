import romlib,scr,struct,collections
r=romlib.Rom('base21.gba');d=bytes(r.data);M=romlib.all_maps(r)
B=0x08000000
roots=[]
for k,m in M.items():
    for o in m['objects']:
        if o['script']: roots.append((k,o['script']))
        if o['flag']: roots.append((k,('objflag',o['flag'])))
    for c in m['coords']:
        if c['script']: roots.append((k,c['script']))
    for b in m['bgs']:
        if b['kind']<5 and B<=b['arg']<B+len(d): roots.append((k,b['arg']-B))
    for kind,p in r.map_scripts(m):
        if kind in (2,4):
            q=p
            while struct.unpack_from('<H',d,q)[0]:
                roots.append((k,romlib.u32(d,q+4)-B));q+=8
        else: roots.append((k,p))
flags=collections.defaultdict(set);vars_=collections.defaultdict(set);seen=set()
calls=collections.Counter()
todo=list(roots)
while todo:
    k,p=todo.pop()
    if isinstance(p,tuple): flags[p[1]].add(k);continue
    if p in seen or not (0<=p<len(d)): continue
    seen.add(p)
    try: ins,tg=scr.decode(d,p,2000)
    except Exception: continue
    for a,name,args in ins:
        seen.add(a)
        if name in ('setflag','clearflag','checkflag'): flags[args[0]].add(k)
        if name in ('setvar','addvar','subvar','compare_var_to_value','copyvar','compare_var_to_var'): vars_[args[0]].add(k)
        if name in ('call','goto','call_if','goto_if'):
            todo.append((k,args[-1]-B))
        if name=='trainerbattle':
            for x in args[3:]:
                pass
import pickle;pickle.dump((dict(flags),dict(vars_)),open('flags.pkl','wb'))
fl=sorted(flags)
print(len(fl));print([hex(f) for f in fl if 0x400<=f<0x900])
