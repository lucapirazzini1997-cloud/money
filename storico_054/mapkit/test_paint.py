import sys
sys.path.insert(0,'.')
import autotile, gfx
from PIL import Image
W,H=30,20
g=[['grass']*W for _ in range(H)]
for y in range(H):
    for x in range(W):
        if x>=22: g[y][x]='sea'
        elif x>=17: g[y][x]='sand'
for y in range(3,8):
    for x in range(3,9): g[y][x]='pond'
for y in range(0):
    for x in range(2,17): g[y][x]='path'
for y in range(0):
    for x in range(10,12): g[y][x]='path'
flat=[c for row in g for c in row]
vals,miss=autotile.paint(flat,W,H)
print('misses',miss)
pair=gfx.Pair('gTileset_General','gTileset_Petalburg')
im=Image.new('RGB',(W*16,H*16))
for i,v in enumerate(vals):
    im.paste(pair.render(v&0x3FF),((i%W)*16,(i//W)*16))
im.resize((W*32,H*32),Image.NEAREST).save('/tmp/claude-0/-home-claude/5e717a36-63af-5454-95a7-212bf7d539cb/scratchpad/paint_test.png')
