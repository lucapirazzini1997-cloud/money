import romlib,scr,sys
r=romlib.Rom('out/Pokemon_Romagna_0_22.gba');d=open('out/Pokemon_Romagna_0_22.gba','rb').read()
g_,n_=int(sys.argv[1]),int(sys.argv[2])
m=r.map(g_,n_);print(m['width'],m['height'],m['conns'])
def first_text(p):
    try: ins,_=scr.decode(d,p,12)
    except Exception: return ''
    for a,n,ar in ins:
        if n=='loadword' and len(ar)>1: return scr.text(d,ar[1]-0x8000000,64)
        if n=='trainerbattle': return 'TRAINER %x'%ar[1]
    return ''
for i,w in enumerate(m['warps']):
    t=r.map(w['group'],w['num']);tt=[first_text(o['script']) for o in t['objects'][:2]]
    print('W',i,w['x'],w['y'],'->',(w['group'],w['num']),w['warp'],t['width'],t['height'],tt)
for i,o in enumerate(m['objects']): print('O',i+1,o['x'],o['y'],o['gfx'],hex(o['flag']),o['ttype'],first_text(o['script']))
for b in m['bgs']: print('B',b['x'],b['y'],first_text(b['arg']-0x8000000) if b['arg']>0x8000000 else b['arg'])
print('C',m['coords'])
r.render(m,events=True).save('qa/city_%d_%d.png'%(g_,n_))
