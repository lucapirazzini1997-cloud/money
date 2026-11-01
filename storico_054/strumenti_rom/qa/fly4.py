import qa21,sys,ctypes
from qa21 import Game,S,lib
from PIL import Image
import shutil;shutil.copy(sys.argv[1],'qa/t.gba')
fl=['FLAG_VISITED_%s'%n for n in 'LITTLEROOT_TOWN OLDALE_TOWN DEWFORD_TOWN LAVARIDGE_TOWN FALLARBOR_TOWN VERDANTURF_TOWN PACIFIDLOG_TOWN PETALBURG_CITY SLATEPORT_CITY MAUVILLE_CITY RUSTBORO_CITY FORTREE_CITY LILYCOVE_CITY MOSSDEEP_CITY SOOTOPOLIS_CITY EVER_GRANDE_CITY'.split()]
qa21.make_save('qa/t.gba',(34,17),40,22,'qa/t.sav',badges=8,flags=fl+['0x4d7','0x4d8','0x4d9','0x4cb'],team=[('PIDGEOT',['FLY','','',''],40)])
g=Game('qa/t.gba','qa/t.sav',S);g.boot_continue()
st=ctypes.create_string_buffer(lib.state_size());lib.state_save(st)
dots=[(135,71),(295,71),(72,135),(135,135),(200,135),(232,167),(264,183),(232,215),(168,247),(358,87),(358,118),(375,167),(407,215),(358,151),(375,103),(320,87),(415,119),(455,175)]
crops=[];res=[]
for (x,y) in dots:
    lib.state_load(st)
    g.tap('start',3,40);g.tap('down');g.tap('a',3,60);g.tap('a',3,40);g.tap('down');g.tap('a',3,90)
    dx=round((x-264)/16);dy=round((y-133)/16)
    for k in (['right']*dx if dx>0 else ['left']*-dx)+(['down']*dy if dy>0 else ['up']*-dy): g.tap(k,3,10)
    im=g.shot('qa/tmp.png',1);crops.append(im.crop((130,135,240,160)))
    g.tap('a',3,30);g.frames(400);res.append(g.pos())
    print((x,y),g.pos())
W=Image.new('RGB',(110,25*len(crops)))
for i,c in enumerate(crops):W.paste(c,(0,25*i))
W.resize((220,50*len(crops))).save('qa/names.png')
