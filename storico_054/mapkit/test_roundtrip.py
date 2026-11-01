import sys, time
sys.path.insert(0,'.')
import gfx, tsbuild
from PIL import ImageChops
src=sys.argv[1]
pair=gfx.Pair('gTileset_General', src)
metas=[tsbuild.meta_from(pair, 512+i) for i in range(pair.s.nmeta)]
t=time.time()
out='/tmp/claude-0/-home-claude/5e717a36-63af-5454-95a7-212bf7d539cb/scratchpad/rt_'+src
ids=tsbuild.build(metas, out)
print('time %.1fs'%(time.time()-t))
# load built as tileset from directory
class T(gfx.Tileset):
    def __init__(self, d):
        from pathlib import Path
        import struct
        from PIL import Image
        d=Path(d); img=Image.open(d/'tiles.png'); w,h=img.size; raw=img.tobytes()
        self.tiles=[tuple(raw[((t//(w//8))*8+y)*w+(t%(w//8))*8+x]&15 for y in range(8) for x in range(8)) for t in range((w//8)*(h//8))]
        self.pals=[gfx.read_pal(d/'palettes'/('%02d.pal'%i)) for i in range(16)]
        self.metas=gfx.u16s(d/'metatiles.bin'); self.attrs=gfx.u16s(d/'metatile_attributes.bin')
pair2=gfx.Pair(gfx.tileset('gTileset_General','primary'), T(out))
bad=0
for i,mid in enumerate(ids):
    a=pair.render(512+i).point(lambda v:(v>>3)<<3); b=pair2.render(mid).point(lambda v:(v>>3)<<3)
    if ImageChops.difference(a,b).getbbox(): bad+=1
print('mismatching metatiles', bad, 'of', len(ids))
for i,mid in enumerate(ids):
    a=pair.render(512+i).point(lambda v:(v>>3)<<3); b=pair2.render(mid).point(lambda v:(v>>3)<<3)
    if ImageChops.difference(a,b).getbbox():
        pa=a.load(); pb=b.load()
        diffs=[(x,y,pa[x,y],pb[x,y]) for y in range(16) for x in range(16) if pa[x,y]!=pb[x,y]]
        print(hex(512+i), len(diffs), diffs[:3]); 
        print(' src entries', [hex(pair.entry(512+i,k)) for k in range(8)])
        print(' new entries', [hex(pair2.entry(mid,k)) for k in range(8)])
        break
