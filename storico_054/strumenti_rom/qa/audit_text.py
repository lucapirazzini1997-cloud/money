import romlib,scr,json,re,collections
r=romlib.Rom('out/Pokemon_Romagna_0_22.gba');d=open('out/Pokemon_Romagna_0_22.gba','rb').read()
reach=[tuple(x) for x in json.load(open('qa/reachable.json'))]
EN=re.compile(r"\b(the|you|your|you're|and|is|are|this|that|what|with|have|want|can't|don't|I'm|it's|here|there|my|for|of)\b",re.I)
hits=collections.defaultdict(list)
for gn in reach:
    if gn[0] in (16,):   # link/cable rooms
        continue
    m=r.map(*gn)
    ptrs=[('obj',o['script'],(o['x'],o['y'])) for o in m['objects']]+[('bg',b['arg']-0x8000000,(b['x'],b['y'])) for b in m['bgs'] if b['arg']>0x8000000]+[('coord',c['script'],(c['x'],c['y'])) for c in m['coords']]
    for k,p,xy in ptrs:
        try: ins,_=scr.decode(d,p,300)
        except Exception: continue
        for a,n,ar in ins:
            for v in ar:
                if isinstance(v,int) and 0x8000000<=v<0xa000000 and n in ('loadword','msgbox','trainerbattle'):
                    t=scr.text(d,v-0x8000000,200)
                    words=EN.findall(t)
                    if len(words)>=3: hits[gn].append((k,xy,t[:70]))
tot=0
for gn,h in sorted(hits.items()):
    u={x[2] for x in h};tot+=len(u)
    print(gn,len(u),list(u)[:2])
print('maps with English',len(hits),'texts',tot)
