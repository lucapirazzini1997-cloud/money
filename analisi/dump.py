"""Dump di una mappa: warp, connessioni, eventi a coordinate, oggetti, cartelli, script decodificati."""
import sys, struct, json
sys.path.insert(0,str(__import__('pathlib').Path(__file__).resolve().parent.parent/'strumenti_rom'))
import romlib, scr
from text_codec import CHAR
ROM=sys.argv[1]; R=romlib.Rom(ROM); d=bytes(R.data); B=0x8000000
NAMES={int(k):v for k,v in json.load(open(str(__import__('pathlib').Path(__file__).resolve().parent/'regnames.json'))).items()}
def nm(g,n):
    try: return NAMES.get(R.map(g,n)['region'],'?')
    except Exception: return '?'
def txt(p,n=200):
    o=''
    while d[p]!=0xff and len(o)<n:
        x=d[p]; o+=(' / ' if x in (0xfe,0xfb,0xfa) else CHAR.get(x,'{%02x}'%x)); p+=1
    return o
def show(p,depth=0,seen=None,maxops=60):
    seen=seen if seen is not None else set()
    if p is None or p in seen or depth>3: return
    seen.add(p)
    try: ops,_=scr.decode(d,p,maxops)
    except Exception as e: print('   '*depth,'!!decode',hex(p),e); return
    for a,n,ar in ops:
        s=[hex(x) if isinstance(x,int) else x for x in ar]
        extra=''
        if n=='loadword' and len(ar)>1 and isinstance(ar[1],int) and B<=ar[1]<B+len(d): extra=' «'+txt(ar[1]-B,120)+'»'
        if n=='message' and isinstance(ar[0],int) and B<=ar[0]<B+len(d): extra=' «'+txt(ar[0]-B,120)+'»'
        print('   '*depth+'  ',hex(a),n,s,extra)
    for a,n,ar in ops:
        if n in ('call','goto','goto_if','call_if') and isinstance(ar[-1],int) and B<=ar[-1]<B+len(d):
            print('   '*depth+'  -> sub',hex(ar[-1]-B)); show(ar[-1]-B,depth+1,seen,maxops)
def dump(g,n,scripts=True):
    m=R.map(g,n)
    print('=== MAP',(g,n),nm(g,n),m['width'],'x',m['height'],'header',hex(m['header']),'events',hex(m['events']))
    for c in m['conns']: print(' conn dir',c['dir'],'->',(c['group'],c['num']),nm(c['group'],c['num']),'off',c['offset'])
    for i,w in enumerate(m['warps']): print(' warp',i,(w['x'],w['y']),'->',(w['group'],w['num']),nm(w['group'],w['num']),'w#',w['warp'])
    for o in m['objects']: print(' obj',o['id'],(o['x'],o['y']),'gfx',o['gfx'],'mv',o['move'],'tt',o['ttype'],'flag',hex(o['flag']),'scr',hex(o['script']) if o['script'] else 0)
    for c in m['coords']: print(' coord',(c['x'],c['y']),'var',hex(c['var']),'val',c['val'],'scr',hex(c['script']) if c['script'] else 0)
    for b in m['bgs']: print(' bg',(b['x'],b['y']),'kind',b['kind'],'arg',hex(b['arg']))
    if scripts:
        for k,p in R.map_scripts(m): print(' mapscript type',k,hex(p) if p else p)
if __name__=='__main__':
    g,n=map(int,sys.argv[2].split('.'))
    dump(g,n)
    for a in sys.argv[3:]:
        print('--- script',a); show(int(a,16))
