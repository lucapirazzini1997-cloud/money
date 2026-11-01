import romlib,sys
r=romlib.Rom(sys.argv[1] if sys.argv[1].endswith('.gba') else 'base21.gba')
args=[a for a in sys.argv[1:] if not a.endswith('.gba')]
for a in args:
    g,n=map(int,a.split(','));m=r.map(g,n)
    print('== %d,%d %dx%d type%d region%d music%d weather%d prim %x sec %x'%(g,n,m['width'],m['height'],m['type'],m['region'],m['music'],m['weather'],m['primary'],m['secondary']))
    for i,w in enumerate(m['warps']): print('  w%d (%d,%d) -> %d,%d #%d'%(i,w['x'],w['y'],w['group'],w['num'],w['warp']))
    for c in m['coords']: print('  coord (%d,%d) var %x=%d scr %x'%(c['x'],c['y'],c['var'],c['val'],c['script'] or 0))
    for b in m['bgs']: print('  bg (%d,%d) kind %d arg %x'%(b['x'],b['y'],b['kind'],b['arg']))
    for i,o in enumerate(m['objects']): print('  obj%d (%d,%d) gfx %d mv %d scr %x flag %x trainer %d/%d'%(i+1,o['x'],o['y'],o['gfx'],o['move'],o['script'] or 0,o['flag'],o['ttype'],o['trange']))
    print('  conns',[(c['dir'],c['offset'],c['group'],c['num']) for c in m['conns']],'scripts',[(k,hex(p)) for k,p in r.map_scripts(m)])
