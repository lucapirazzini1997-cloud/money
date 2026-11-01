import romlib,scr,sys
r=romlib.Rom('base21.gba');d=bytes(r.data)
def first_text(p):
    if not p: return ''
    ins,_=scr.decode(d,p,300)
    out=[]
    for a,n,args in ins:
        if n=='loadword' or n=='trainerbattle':
            for x in args:
                if 0x08000000<=x<0x0a000000: out.append(scr.text(d,x-0x08000000,90).replace('\\n',' ')); 
        if n in('trainerbattle',): out.insert(0,'[TRAINER %d]'%args[1])
        if len(out)>=2: break
    return ' | '.join(out)[:170]
for a in sys.argv[1:]:
    g,n=map(int,a.split(','));m=r.map(g,n)
    print('==',a,m['width'],m['height'])
    for i,o in enumerate(m['objects']): print(' obj%d (%d,%d) g%d f%x: %s'%(i+1,o['x'],o['y'],o['gfx'],o['flag'],first_text(o['script'])))
    for b in m['bgs']: print(' bg (%d,%d): %s'%(b['x'],b['y'],first_text(b['arg']-0x08000000) if b['kind']<5 else 'hidden'))
    for i,w in enumerate(m['warps']): print(' w%d (%d,%d)->%d,%d#%d'%(i,w['x'],w['y'],w['group'],w['num'],w['warp']))
    for c in m['coords']: print(' coord (%d,%d): %s'%(c['x'],c['y'],first_text(c['script'])))
