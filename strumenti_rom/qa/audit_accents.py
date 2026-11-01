import romlib,scr,json,re,collections
r=romlib.Rom('out/Pokemon_Romagna_0_22.gba');d=open('out/Pokemon_Romagna_0_22.gba','rb').read()
reach=[tuple(x) for x in json.load(open('qa/reachable.json'))]
texts={}
for gn in reach:
    if gn[0]==16: continue
    m=r.map(*gn)
    ptrs=[o['script'] for o in m['objects']]+[b['arg']-0x8000000 for b in m['bgs'] if b['arg']>0x8000000]+[c['script'] for c in m['coords']]
    for p in ptrs:
        try: ins,_=scr.decode(d,p,300)
        except Exception: continue
        for a,n,ar in ins:
            for v in ar:
                if isinstance(v,int) and 0x8000000<=v<0xa000000 and n in ('loadword','msgbox','trainerbattle'):
                    texts.setdefault(v-0x8000000,(gn,scr.text(d,v-0x8000000,300)))
PAT=re.compile(r"\b(\w+)'(?=[\s/.,!?]|$)")
bad=collections.Counter();ex=[]
for addr,(gn,t) in texts.items():
    for m_ in PAT.finditer(t):
        w=m_.group(1)
        if w.lower() in ('po','un','l','d','c','dell','nell','all','sull','dall','quell','quest','com','cos','tutt','m','t','s','n','v','gl','bell','sant'): continue
        bad[w.lower()+"'"]+=1;ex.append((hex(addr),gn,w))
print(len(texts),'texts;',sum(bad.values()),'accent-apostrophes'); print(bad.most_common(30))
json.dump(ex,open('qa/accents.json','w'))
# missing accent on 'e' used as verb: ' e di tipo', 'e proprio', 'Questa e '
pat2=re.compile(r"\b(Questa|Questo|Qui|Lui|Lei|Non|che|ora|non|La [A-Z]+|Il [A-Z]+) e (?=[a-z])")
m2=[(hex(a),t[:60]) for a,(gn,t) in texts.items() if pat2.search(t)]
print('suspect missing è:',len(m2)); print(m2[:12])
