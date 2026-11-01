from pathlib import Path
import sys,struct,json,hashlib,textwrap,copy
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'strumenti_rom'),str(ROOT/'mapkit'),str(ROOT/'mapkit/maps22')]
import romlib,inject,gfx,canvas,tsbuild,r22,family,imports
B=0x08000000
romlib.COUNTS[35]=44
BASE=romlib.Rom(str(ROOT/'base31.gba'));r22.ROM=BASE
OUT=ROOT/'build';OUT.mkdir(exist_ok=True)
gfx.ROOT=ROOT/'assets';inject.TS_ROOT=gfx.ROOT/'data/tilesets/secondary'

def export_ts(ptr,name,kind):
 t=BASE.tileset(ptr);d=gfx.ROOT/'data/tilesets'/kind/gfx.folder_of(name);d.mkdir(parents=True,exist_ok=True)
 a=t['tiles'][:512];a=np.pad(a,((0,max(0,512-len(a))),(0,0),(0,0)))
 px=a.reshape(32,16,8,8).transpose(0,2,1,3).reshape(256,128)
 im=Image.fromarray(px.astype('uint8'),'P');im.putpalette([v for i in range(256) for v in (i,i,i)]);im.save(d/'tiles.png')
 for field,n,fn in [('metatiles',8192,'metatiles.bin'),('attrs',1024,'metatile_attributes.bin')]: (d/fn).write_bytes(BASE.data[t[field]:t[field]+n])
 (d/'palettes').mkdir(exist_ok=True)
 for i in range(16):
  vals=struct.unpack_from('<16H',BASE.data,t['pals']+i*32)
  gfx.write_pal(d/'palettes'/f'{i:02d}.pal',[tuple(((v>>s)&31)*255//31 for s in [0,5,10]) for v in vals])
export_ts(0x55e8c0,'gTileset_General','primary')
export_ts(BASE.map(0,0)['secondary'],'gTileset_Petalburg','secondary')
# Warm, uniform paved terrain; the family builder needs no omitted original C assets.
def cobbles(recolor=None):
 k=('paved',recolor)
 if k not in imports._fam_cache:
  m=tsbuild.meta_from(gfx.Pair('gTileset_General','gTileset_Petalburg'),0x121,coll=0,elev=3)
  if recolor:m.bottom=imports.recolor_img(m.bottom,recolor);m.top=imports.recolor_img(m.top,recolor);m.palkeys=[None]*8
  imports._fam_cache[k]=(family.Family({},0x211),{0x211:m})
 return imports._fam_cache[k]
imports.cobbles=cobbles
class Writer(inject.Writer):
 def __init__(self):
  super().__init__(str(ROOT/'base31.gba'),start=0x1a00000);self.scripts_log=[];self.changes=[]
 def text(self,t):
  from text_codec import CHAR
  alpha={v:k for k,v in CHAR.items() if len(v)==1};alpha.update({'\n':0xfe,'\r':0xfb,'È':5})
  t=t.replace('>', ' EST').replace('<', ' OVEST')
  pages=[]
  for para in t.split('\n\n'):
   lines=[]
   for line in para.split('\n'):lines+=textwrap.wrap(line,29,break_long_words=False) or ['']
   pages+=['\n'.join(lines[i:i+2]) for i in range(0,len(lines),2)]
  return self.alloc(bytes(alpha[c] for c in '\r'.join(pages))+b'\xff','text '+t[:30])
 def refresh(self):self.rom.data=self.d
 def save(self,path):
  # Publish only a fully written ROM. Some workspace-backed streams can return
  # short writes for a single 32 MiB write; Path.write_bytes alone does not
  # validate that count. This changes I/O only, not any byte of the build.
  import os
  path=Path(path);tmp=path.with_suffix(path.suffix+'.tmp');expected=hashlib.sha256(self.d).hexdigest()
  with tmp.open('wb') as f:
   for pos in range(0,len(self.d),1024*1024):
    chunk=memoryview(self.d)[pos:pos+1024*1024]
    while chunk:
     n=f.write(chunk)
     if not n:raise OSError('Incomplete ROM write')
     chunk=chunk[n:]
   f.flush();os.fsync(f.fileno())
  actual=tmp.read_bytes();assert len(actual)==len(self.d) and hashlib.sha256(actual).hexdigest()==expected
  tmp.replace(path);return expected
W=Writer()
def H(x):return struct.pack('<H',x)
def P(x):return struct.pack('<I',B+x)
class Script:
 def __init__(self,name):self.name=name;self.code=bytearray();self.labels={};self.fix=[]
 def emit(self,b):self.code+=b;return self
 def label(self,k):self.labels[k]=len(self.code);return self
 def jump(self,k,cond=None):
  self.emit(b'\x05' if cond is None else b'\x06'+bytes([cond]));self.fix.append((len(self.code),k));return self.emit(bytes(4))
 def flag(self,x,label,present=True):return self.emit(b'\x2b'+H(x)).jump(label,1 if present else 0)
 def cmp(self,v,label,cond=1,var=0x800d):return self.emit(b'\x21'+H(var)+H(v)).jump(label,cond)
 def set(self,f):return self.emit(b'\x29'+H(f))
 def var(self,v,x):return self.emit(b'\x16'+H(v)+H(x))
 def msg(self,t):return self.emit(b'\x0f\x00'+P(W.text(t))+b'\x09\x04')
 def end(self):return self.emit(b'\x6b\x02')
 def save(self):
  p=W.alloc(self.code,self.name)
  for at,label in self.fix:struct.pack_into('<I',W.d,p+at,B+p+self.labels[label])
  W.scripts_log.append(dict(name=self.name,pointer=p,size=len(self.code)));return p
 def gift(self,item,flag,text,qty=1):
  self.emit(b'\x1a'+H(0x8000)+H(item)+b'\x1a'+H(0x8001)+H(qty)+b'\x09\x00').cmp(0,'full').set(flag).msg(text).end()
  return self.label('full').msg("La Borsa è piena. Torna dopo: custodirò il premio per te.").end()
 def warp(self,g,n,x,y):return self.emit(b'\x39'+bytes([g,n,255])+H(x)+H(y)+b'\x27\x6b\x02')
def talk(t,name='Dialogo'):return Script(name).emit(b'\x6a\x5a').msg(t).end().save()
def battle(tid,flag,intro,after,remove=None):
 s=Script('Allenatore '+str(tid)).emit(b'\x6a\x5a').flag(flag,'done')
 s.emit(b'\x5c\x02'+H(tid)+H(0)+P(W.text(intro))+P(W.text('Una bella sfida!')));s.fix.append((len(s.code),'won'));s.emit(bytes(4)).end()
 s.label('won').set(flag)
 if remove is not None:s.emit(b'\x53'+H(remove))
 s.label('done').msg(after).end();return s.save()
def trainer(tid,name,mons,cls=5,pic=3):
 from text_codec import CHAR
 a={v:k for k,v in CHAR.items() if len(v)==1};raw=bytearray(40);raw[0]=2;raw[1]=cls;raw[3]=pic;raw[4:16]=(bytes(a[x] for x in name)+b'\xff').ljust(12,b'\x00');struct.pack_into('<I',raw,28,7);raw[32]=len(mons)
 p=W.alloc(b''.join(struct.pack('<HBxHH',60,lv,sp,0) for sp,lv in mons),'trainer '+name);struct.pack_into('<I',raw,36,B+p);W.d[0xf21000+tid*40:0xf21000+(tid+1)*40]=raw

def source(key):return BASE.map(*key)
def events(key,**kw):W.set_events(*key,**kw)
def blocks(key):return W.rom.blocks(W.rom.map(*key))
def writeblocks(key,a):
 m=W.rom.map(*key);W.set_layout(*key,a.ravel().tolist(),a.shape[1],a.shape[0],list(struct.unpack_from('<4H',W.d,m['border'])),m['primary'],m['secondary'])
def cv_from(key):
 from _stamps import _layers
 m=source(key);cv=r22.RCanvas(m['width'],m['height'],key);live=W.rom.map(*key)
 for dst,src in [('objs','objects'),('bwarps','warps'),('bcoords','coords'),('bbgs','bgs'),('conns','conns')]:setattr(cv,dst,copy.deepcopy(live[src]))
 get=_layers(m);a=BASE.blocks(m)
 for y in range(cv.h):
  for x in range(cv.w):
   v=int(a[y,x]);bot,top,beh,layer=get(v&1023)
   if (v&1023)<512:
    cv.put(x,y,v&1023,(v>>10)&3,v>>12)
   else:
    cv.art[y][x]=(Image.fromarray(bot,'RGBA'),Image.fromarray(top,'RGBA'),(v>>10)&3,beh,False)
 return cv

def emit(cv,name,starts=()):
 from places32 import finish_room
 finish_room(cv,name)
 # Preserve any intentional collision and behavior, with independent private tilesets.
 res=r22.build(cv,'v32_'+name,starts or [(w['x'],w['y']) for w in cv.bwarps] or [(cv.w//2,cv.h-2)],surf=getattr(cv,'test_surf',False))
 r22.emit(W,res,{})
 W.changes.append(dict(name=name,map=list(cv.gn),width=cv.w,height=cv.h,static_notes=res['problems']))
 return res

def empty_events(cv):cv.objs=[];cv.bwarps=[];cv.bcoords=[];cv.bbgs=[];cv.conns=[];return cv

def sign(cv,x,y,t):
 cv.put(x,y,3,1,3);cv.add_sign(x,y,talk(t));return len(cv.bbgs)-1

def add_map(template=(34,39),region=None,mtype=None):
 g=35;n=romlib.COUNTS[35];ptr=W.rom.ptr(romlib.GROUPS+g*4);entries=list(struct.unpack_from('<'+'I'*n,W.d,ptr));old=source(template);hp=W.alloc(W.d[old['header']:old['header']+28],'new header');entries.append(B+hp)
 gp=W.alloc(struct.pack('<'+'I'*len(entries),*entries)+b'\xff'*4,'group35');struct.pack_into('<I',W.d,romlib.GROUPS+g*4,B+gp);romlib.COUNTS[35]+=1
 lp=W.table;count=0
 while B<=romlib.u32(W.d,lp+count*4)<B+len(W.d):count+=1
 arr=list(struct.unpack_from('<'+'I'*count,W.d,lp));arr.append(B+old['layout']);np_=W.alloc(struct.pack('<'+'I'*len(arr),*arr)+bytes(4),'layouts')
 W.table=np_
 for ref in inject.LAYOUT_TABLE_REFS:struct.pack_into('<I',W.d,ref,B+np_)
 struct.pack_into('<H',W.d,hp+18,count+1)
 if region is not None:W.d[hp+20]=region
 if mtype is not None:W.d[hp+23]=mtype
 W.set_map_scripts(g,n,[]);events((g,n),objects=[],warps=[],coords=[],bgs=[]);W.set_connections(g,n,[])
 return g,n

def ow_sprite(gfx_id,species,tag):
 # Reuse the native front sprite as 32x32 overworld art, its own native palette.
 template=BASE.ptr(0x6ada3c+206*4)
 pic=BASE.lz(BASE.ptr(0x3139dc+species*8))[:2048];a=np.frombuffer(pic,dtype=np.uint8);px=np.empty(4096,dtype=np.uint8);px[::2]=a&15;px[1::2]=a>>4
 small=px.reshape(8,8,8,8).transpose(0,2,1,3).reshape(64,64)[::2,::2]
 data=bytearray()
 for y in range(0,32,8):
  for x in range(0,32,8):v=small[y:y+8,x:x+8].ravel();data+=bytes(v[::2]|(v[1::2]<<4))
 gp=W.alloc(data,'ow pixels');fr=W.alloc((P(gp)+struct.pack('<HH',512,0))*8,'ow frames');pal=W.alloc(BASE.lz(BASE.ptr(0x315c3c+species*8)),'ow palette');info=bytearray(BASE.data[template:template+36]);struct.pack_into('<H',info,2,tag);struct.pack_into('<I',info,28,B+fr);ip=W.alloc(info,'ow info');struct.pack_into('<I',W.d,0x6ada3c+gfx_id*4,B+ip)
 cur=W.rom.ptr(0x8ea24);raw=bytearray()
 while True:
  p,t=struct.unpack_from('<IH',W.d,cur)
  if p==0 and t==0x11ff:break
  raw+=W.d[cur:cur+8];cur+=8
 raw+=P(pal)+struct.pack('<HH',tag,0)+struct.pack('<IHH',0,0x11ff,0);pt=W.alloc(raw,'ow palettes')
 for ref in [0x8ea24,0x8eab8,0x8eb10]:struct.pack_into('<I',W.d,ref,B+pt)

def export_meta(path):
 meta=[]
 for key,m in romlib.all_maps(W.rom).items():
  for o in m['objects']:o.pop('raw',None)
  m['coord']=m['coords'];m['bg']=m['bgs'];meta.append(m)
 Path(path).write_text(json.dumps(dict(maps=meta)))
