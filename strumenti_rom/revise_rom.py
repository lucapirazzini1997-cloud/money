"""Revisione riproducibile della ROM Pokémon Romagna 0.16.

Non è il progetto originale: modifica solo mappe/risorse grafiche e la tabella
dei layout. Gli script, gli eventi, i Pokémon e i dati dei salvataggi restano
quelli della ROM fornita. La SHA256 della ROM di ingresso è obbligatoria.
"""
from pathlib import Path
import sys, struct, json, hashlib, collections
import numpy as np
from PIL import Image, ImageDraw
from render_rom import ROM, MAPS, ROOT

B=0x08000000
SOURCE=ROOT/'upload/Pokemon_Romagna_0_16.gba'
EXPECTED='ac2d5533329f084d27faff9b8ced1269fb078f8bf3b84a95e8ea92aef39503ae'
OUT=ROOT/'output'
OUT.mkdir(exist_ok=True)
BASE=ROM(SOURCE)
assert hashlib.sha256(BASE.data).hexdigest()==EXPECTED

THEMES={
 'LIDO DI SAVIO':('#e5d6b7','#c3ac83','#628f97','#2a6370'),
 'CERVIA':('#e7e2ca','#b7b49c','#719f9e','#396d77'),
 'CESENA':('#dfd1b3','#b5a27b','#b46649','#6b3e37'),
 'CESENATICO':('#d8d7bf','#9caa9a','#729da0','#356a79'),
 'RIMINI':('#eadbb9','#bea885','#bc865b','#756b80'),
 'FORLI':('#ded5c0','#aea291','#a8756a','#713f4e'),
 'FAENZA':('#e3e1d5','#acb7b8','#62969c','#285873'),
 'RAVENNA':('#ddd9c4','#adac92','#a7a060','#3e6d73'),
 'LUGO':('#dddcc9','#afb39f','#7098a1','#365e76'),
}

def rgb(s): return tuple(int(s[i:i+2],16) for i in (1,3,5))
def gba_palette(colors):
    return b''.join(struct.pack('<H',sum((c[i]*31//255)<<(5*i) for i in range(3))) for c in colors)
def encode_tile(a):
    a=np.asarray(a,dtype=np.uint8).ravel()
    return bytes(a[::2] | (a[1::2]<<4))
def lz_literals(raw):
    return b'\x10'+len(raw).to_bytes(3,'little')+b''.join(b'\x00'+raw[i:i+8] for i in range(0,len(raw),8))

class Writer:
    def __init__(self):
        self.data=bytearray(BASE.data);self.cursor=0xf40000;self.allocations=[]
        self.layouts=list(struct.unpack_from('<540I',self.data,0x627fc0))
        self.assigned={};self.changes=[]
    def alloc(self,raw,label):
        self.cursor=(self.cursor+3)&~3;p=self.cursor;end=p+len(raw)
        if end>len(self.data):self.data.extend(b'\xff'*(0x2000000-len(self.data)))
        assert all(v==255 for v in self.data[p:end]),f'occupied allocation {p:x}'
        self.data[p:end]=raw;self.cursor=end
        self.allocations.append(dict(offset=p,size=len(raw),label=label));return p
    def register(self,key,layout):
        m=MAPS[key];hp=m['header']
        if hp not in self.assigned:
            self.layouts.append(B+layout);self.assigned[hp]=len(self.layouts)
        else:self.layouts[self.assigned[hp]-1]=B+layout
        struct.pack_into('<I',self.data,hp,B+layout)
        struct.pack_into('<H',self.data,hp+18,self.assigned[hp])
    def map(self,key,blocks,secondary=None):
        m=MAPS[key];raw=bytearray(BASE.data[m['layout']:m['layout']+24])
        bp=self.alloc(np.asarray(blocks,dtype='<u2').tobytes(),f'blocks {key}')
        struct.pack_into('<I',raw,12,B+bp)
        if secondary is not None:struct.pack_into('<I',raw,20,B+secondary)
        lp=self.alloc(raw,f'layout {key}');self.register(key,lp)
    def finish(self):
        table=self.alloc(struct.pack('<'+'I'*len(self.layouts),*self.layouts),'layout pointer table')
        for off in (0x8490c,0x1aa5b0):
            assert struct.unpack_from('<I',BASE.data,off)[0]==B+0x627fc0
            struct.pack_into('<I',self.data,off,B+table)
        p=OUT/'Pokemon_Romagna_0_17.gba';p.write_bytes(self.data)
        return p,table

class Secondary:
    def __init__(self,key):
        self.key=key;m=MAPS[key];sp=m['secondary'];self.sp=sp
        pixels,pp,mp,ap=BASE.tileset(sp)
        self.gfx=bytearray(b''.join(encode_tile(t) for t in pixels).ljust(16384,b'\x00'))
        self.pals=bytearray(BASE.data[pp:pp+512])
        self.meta=bytearray(BASE.data[mp:mp+8192]);self.attrs=bytearray(BASE.data[ap:ap+1024])
        protected={0}
        map_ids=set(map(int,(BASE.blocks(key)&1023).ravel()))
        border=BASE.ptr(m['layout']+8)
        map_ids.update(v&1023 for v in struct.unpack_from('<4H',BASE.data,border))
        for lp in (m['primary'],sp):
            mb=BASE.ptr(lp+12);ab=BASE.ptr(lp+16)
            is_secondary=lp==sp
            used_indices={v-512 if is_secondary else v for v in map_ids if (v>=512)==is_secondary}
            # Some custom tilesets store attributes before definitions. Never
            # infer a one-entry table from that order: protect all referenced data.
            count=min(512,max(1,(ab-mb)//16,max(used_indices,default=0)+1))
            for i in range(count):
                for ref in struct.unpack_from('<8H',BASE.data,mb+i*16):
                    if (ref&1023)>=512:protected.add((ref&1023)-512)
        self.free=[i for i in range(512) if i not in protected]
        self.newtiles={};self.next_mt=0x380
        self.assets={}
    def tile(self,raw):
        if raw in self.newtiles:return self.newtiles[raw]
        if not self.free:raise ValueError(f'not enough unused tiles: {self.key}')
        idx=self.free.pop(0);self.gfx[idx*32:idx*32+32]=raw;self.newtiles[raw]=idx
        return idx
    def palette(self,slot,colors):self.pals[slot*32:slot*32+32]=gba_palette(colors)
    def image_refs(self,im,pal):
        a=np.asarray(im,dtype=np.uint8)
        return [512+self.tile(encode_tile(a[y:y+8,x:x+8]))+(pal<<12) for y,x in [(0,0),(0,8),(8,0),(8,8)]]
    def metatile(self,bottom,top=None,attr=0):
        if top is None:top=[512+self.tile(bytes(32))]*4
        mt=self.next_mt;self.next_mt+=1
        if mt>=1024:raise ValueError('too many metatiles')
        struct.pack_into('<8H',self.meta,(mt-512)*16,*(bottom+top))
        struct.pack_into('<H',self.attrs,(mt-512)*2,attr)
        return mt
    def floor(self,im,pal,attr=0):return self.metatile(self.image_refs(im,pal),attr=attr)
    def asset(self,name,im,pal,floorrefs,attr=0x1000):
        mts=[]
        for y in range(0,im.height,16):
            row=[]
            for x in range(0,im.width,16):
                row.append(self.metatile(floorrefs,self.image_refs(im.crop((x,y,x+16,y+16)),pal),attr))
            mts.append(row)
        self.assets[name]=np.array(mts,dtype=np.uint16)
    def transplant(self,source_key,mt):
        m=MAPS[source_key];lp=m['primary'] if mt<512 else m['secondary']
        mp=BASE.ptr(lp+12)+(mt if mt<512 else mt-512)*16
        ap=BASE.ptr(lp+16)+(mt if mt<512 else mt-512)*2
        out=[]
        for ref in struct.unpack_from('<8H',BASE.data,mp):
            idx=ref&1023
            srcp=BASE.tileset(m['primary'] if idx<512 else m['secondary'])[0]
            idx=idx if idx<512 else idx-512
            data=encode_tile(srcp[idx]) if idx<len(srcp) else bytes(32)
            out.append(512+self.tile(data)+(ref&0xfc00))
        return self.metatile(out[:4],out[4:],int.from_bytes(BASE.data[ap:ap+2],'little'))
    def save(self,w):
        raw=bytearray(BASE.data[self.sp:self.sp+24]);raw[0]=1;raw[1]=1
        # A complete 512-tile stream prevents residual VRAM contents from a previous map.
        gp=w.alloc(lz_literals(bytes(self.gfx)),f'graphics {self.key}')
        pp=w.alloc(self.pals,f'palettes {self.key}')
        mp=w.alloc(self.meta,f'metatiles {self.key}')
        ap=w.alloc(self.attrs,f'attributes {self.key}')
        for off,ptr in zip((4,8,12,16),(gp,pp,mp,ap)):struct.pack_into('<I',raw,off,B+ptr)
        return w.alloc(raw,f'tileset {self.key}')

def floor_image(style):
    im=Image.new('P',(16,16),1);d=ImageDraw.Draw(im)
    if style%4==0:
        d.line((0,0,15,0),fill=2);d.line((0,0,0,15),fill=2)
        d.line((0,15,15,15),fill=3);d.line((15,0,15,15),fill=3)
        d.point((4,5),fill=4);d.point((12,10),fill=4)
    elif style%4==1:
        for y in (0,8):
            d.line((0,y,15,y),fill=3);d.line((0,y+1,15,y+1),fill=2)
        d.line((3,1,3,7),fill=3);d.line((11,9,11,15),fill=3)
        d.line((5,4,14,4),fill=4);d.line((1,12,8,12),fill=4)
    elif style%4==2:
        d.line((0,0,15,0),fill=3);d.line((0,0,0,15),fill=3)
        d.polygon([(8,4),(12,8),(8,12),(4,8)],fill=2)
        d.point((8,8),fill=5)
    else:
        for y in (0,8):d.line((0,y,15,y),fill=3)
        for x in (0,8):d.line((x,0,x,15),fill=3)
        d.rectangle((1,1,6,6),fill=2);d.rectangle((9,9,14,14),fill=2)
    return im

def asset_images():
    result={}
    im=Image.new('P',(16,16),0);d=ImageDraw.Draw(im)
    d.rectangle((5,10,11,14),fill=11);d.rectangle((6,11,10,14),fill=8)
    d.line((8,4,8,10),fill=9);d.ellipse((2,3,8,7),fill=9);d.ellipse((7,1,12,6),fill=10);d.ellipse((8,6,14,9),fill=9)
    result['plant']=im
    im=Image.new('P',(32,16),0);d=ImageDraw.Draw(im)
    d.rectangle((1,2,30,13),fill=11);d.rectangle((2,3,29,12),fill=12)
    for x in range(4,28,4):
        d.rectangle((x,5,x+2,10),fill=[5,8,13,6,9,8][(x-4)//4])
        d.point((x,5),fill=7)
    d.line((2,12,29,12),fill=11);result['shelf']=im
    im=Image.new('P',(32,32),0);d=ImageDraw.Draw(im)
    d.rectangle((3,4,28,25),fill=11);d.rectangle((4,5,27,23),fill=12);d.rectangle((6,7,25,21),fill=2)
    d.rectangle((7,8,24,9),fill=7);d.rectangle((4,24,7,28),fill=11);d.rectangle((24,24,27,28),fill=11)
    d.ellipse((13,11,18,16),fill=8);d.line((19,13,21,13),fill=11);result['table']=im
    im=Image.new('P',(32,32),0);d=ImageDraw.Draw(im)
    d.rectangle((2,3,29,27),fill=13);d.rectangle((3,4,28,25),fill=5)
    d.line((4,5,26,5),fill=7);d.line((4,6,4,23),fill=7)
    d.polygon([(16,7),(18,15),(25,18),(25,20),(18,19),(17,25),(15,25),(14,19),(7,20),(7,18),(14,15)],fill=7)
    d.line((15,13,17,13),fill=8);d.rectangle((3,26,28,29),fill=11)
    d.line((6,28,23,28),fill=12);result['plane']=im
    im=Image.new('P',(32,16),0);d=ImageDraw.Draw(im)
    d.rectangle((1,2,30,13),fill=13);d.rectangle((2,3,29,11),fill=5)
    for x in (7,16,25):
        d.ellipse((x-2,3,x+2,5),fill=7);d.polygon([(x-2,5),(x-4,9),(x+4,9),(x+2,5)],fill=6)
        d.line((x-3,8,x+3,8),fill=8)
    d.line((2,12,29,12),fill=12);result['ceramic']=im
    im=Image.new('P',(32,16),0);d=ImageDraw.Draw(im)
    d.rectangle((1,2,30,13),fill=11);d.rectangle((2,3,29,12),fill=12)
    d.rectangle((4,5,27,10),fill=2)
    d.line((16,5,16,10),fill=6)
    for y in (6,8):d.line((6,y,13,y),fill=3);d.line((19,y,25,y),fill=3)
    result['books']=im
    im=Image.new('P',(32,16),0);d=ImageDraw.Draw(im)
    d.rectangle((1,9,30,13),fill=11);d.rectangle((2,10,29,12),fill=12)
    d.line((16,1,16,9),fill=13);d.polygon([(15,1),(15,8),(6,8)],fill=7)
    d.polygon([(17,3),(17,8),(24,8)],fill=8);result['boat']=im
    im=Image.new('P',(16,16),0);d=ImageDraw.Draw(im)
    d.rectangle((2,4,13,13),fill=11);d.rectangle((3,5,12,12),fill=12)
    d.line((3,5,12,12),fill=3);d.line((3,12,12,5),fill=3);result['crate']=im
    im=Image.new('P',(32,32),0);d=ImageDraw.Draw(im)
    d.rectangle((3,2,28,29),fill=11);d.rectangle((4,3,27,28),fill=6)
    for y in range(5,27,3):
        for x in range(6,26,3):d.rectangle((x,y,x+1,y+1),fill=5 if (x+y)%2 else 7)
    d.polygon([(16,8),(23,16),(16,24),(9,16)],fill=13);d.ellipse((13,13,19,19),fill=6)
    result['mosaic']=im
    return result

def protection(m,radius=2):
    mask=np.zeros((m['height'],m['width']),dtype=bool)
    for o in m['objects']+m['warps']+m['coord']+m['bg']:
        x,y=o['x'],o['y'];mask[max(0,y-radius):y+radius+1,max(0,x-radius):x+radius+1]=True
    # Protect the main approach to the room and both sides of each exit.
    cx=m['width']//2;mask[:,max(0,cx-1):cx+2]=True
    return mask

def reachable(a,start):
    walk=(a&0xc00)==0
    if not(0<=start[0]<a.shape[1] and 0<=start[1]<a.shape[0]) or not walk[start[1],start[0]]:return set()
    q=[start];s={start}
    for x,y in q:
        for nx,ny in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
            if 0<=nx<a.shape[1] and 0<=ny<a.shape[0] and walk[ny,nx] and (nx,ny) not in s:
                s.add((nx,ny));q.append((nx,ny))
    return s

def anchor_points(m,a):
    pts=[]
    for o in m['warps']+m['objects']+m['coord']+m['bg']:
        for x,y in ((o['x'],o['y']),(o['x']-1,o['y']),(o['x']+1,o['y']),(o['x'],o['y']-1),(o['x'],o['y']+1)):
            if 0<=x<m['width'] and 0<=y<m['height'] and (a[y,x]&0xc00)==0:pts.append((x,y))
    return sorted(set(pts))

def connectivity_preserved(m,old,new):
    pts=anchor_points(m,old)
    checked=set()
    for p in pts:
        if p in checked:continue
        before=reachable(old,p);after=reachable(new,p)
        related={q for q in pts if q in before}
        if not related<=after:return False
        checked.update(related)
    return True

def place(a,old,m,mask,asset,x,y):
    h,w=asset.shape
    if x<1 or y<2 or x+w>=m['width'] or y+h>=m['height']-1:return False
    roi=a[y:y+h,x:x+w]
    if mask[y:y+h,x:x+w].any() or ((roi&0xc00)!=0).any():return False
    prev=roi.copy();a[y:y+h,x:x+w]=(roi&0xf000)|0xc00|asset
    if not connectivity_preserved(m,old,a):a[y:y+h,x:x+w]=prev;return False
    return True

def interior(w,key):
    m=MAPS[key];old=BASE.blocks(key);a=old.copy()
    walk=collections.Counter(int(v) for v in old.ravel() if (int(v)&0xc00)==0 and (int(v)&1023)>=512)
    if not walk:return
    floor,_=walk.most_common(1)[0];mt=floor&1023
    ap=BASE.ptr(m['secondary']+16)+(mt-512)*2
    attr=int.from_bytes(BASE.data[ap:ap+2],'little')
    if attr&255:return
    s=Secondary(key)
    used=set()
    for mt0 in set(map(int,(old&1023).ravel())):
        lp=m['primary'] if mt0<512 else m['secondary'];mp=BASE.ptr(lp+12)+(mt0 if mt0<512 else mt0-512)*16
        used.update(v>>12 for v in struct.unpack_from('<8H',BASE.data,mp))
    slots=[p for p in range(6,13) if p not in used]
    if len(slots)<3:return
    pf,pr,pa=slots[:3]
    city=THEMES.get(m['name'],THEMES['LIDO DI SAVIO']);n=key[1]
    c1,c2,c3,c4=map(rgb,city)
    light=tuple(min(255,v+12) for v in c1)
    floorcolors=[(0,0,0),c1,light,c2,tuple((x+y)//2 for x,y in zip(c1,c2)),c3,c4,(246,244,225)]+[(0,0,0)]*8
    rugcolors=[(0,0,0),c3,tuple(min(255,v+18) for v in c3),c4,tuple((x+y)//2 for x,y in zip(c3,c4)),c2,c1,(247,243,221)]+[(0,0,0)]*8
    artcolors=[(0,0,0),c1,(230,220,190),(166,147,116),(180,173,151),c3,(201,183,117),(245,244,228),(174,89,70),(63,113,78),(119,158,91),(84,70,54),(155,117,75),c4,(43,55,60),(183,201,196)]
    s.palette(pf,floorcolors);s.palette(pr,rugcolors);s.palette(pa,artcolors)
    baseimg=floor_image(n)
    newfloor=s.floor(baseimg,pf,attr);altfloor=s.floor(floor_image(n+1),pf,attr)
    rugimg=floor_image(2);newrug=s.floor(rugimg,pr,attr)
    base_refs=s.image_refs(baseimg,pf)
    for name,im in asset_images().items():s.asset(name,im,pa,base_refs)
    a[a==floor]=(floor&0xfc00)|newfloor
    # Every room gets its own runner or seating area, varied by its number.
    cx=m['width']//2;cy=m['height']//2
    if n%3==0:box=(cx-2,3,cx+2,m['height']-3)
    elif n%3==1:box=(max(2,cx-4),max(3,cy-2),min(m['width']-2,cx+4),min(m['height']-2,cy+2))
    else:box=(2,m['height']-6,m['width']-2,m['height']-3)
    x0,y0,x1,y1=box;roi=a[y0:y1,x0:x1];roi[(roi&1023)==newfloor]=(floor&0xfc00)|newrug
    if n in (79,80,81,82,83):
        # Five houses used exactly the same furniture coordinates.
        furniture=(a&1023)>=0x203;furniture&=(a&1023)<=0x21c
        a[furniture]=(floor&0xfc00)|newfloor
        bed=np.array([[0x203,0x204],[0x205,0x206],[0x207,0x208]],dtype=np.uint16)
        wardrobe=np.array([[0x209,0x20a],[0x20b,0x20c],[0x20d,0x20e]],dtype=np.uint16)
        sofa=np.array([[0x213,0x214,0x215],[0x216,0x217,0x218]],dtype=np.uint16)
        mask=protection(m,1)
        arrangements={79:((2,3),(10,3),(2,9)),80:((10,3),(2,3),(8,9)),81:((2,8),(10,3),(2,3)),82:((10,8),(2,3),(2,9)),83:((10,3),(2,8),(2,3))}
        for asset,(x,y) in zip((bed,wardrobe,sofa),arrangements[n]):place(a,old,m,mask,asset,x,y)
    if n==112:
        # Lugo's Flying gym inherited grass patches from Cesena's room.
        grass=(a&1023)==0x00d
        a[grass]=(a[grass]&0xfc00)|altfloor
    mask=protection(m,2)
    roles={23:'books',24:'books',25:'shelf',28:'boat',29:'crate',31:'boat',38:'boat',45:'books',46:'crate',48:'books',49:'shelf',50:'books',69:'books',70:'shelf',76:'books',86:'ceramic',87:'ceramic',88:'ceramic',89:'table',95:'shelf',97:'mosaic',98:'mosaic',99:'shelf',100:'books',103:'ceramic',104:'table',105:'shelf',106:'mosaic',107:'books',108:'shelf',109:'mosaic',111:'plane',112:'plane'}
    role=roles.get(n,['shelf','books','table','plant'][n%4])
    if m['name']=='FAENZA':role=roles.get(n,'ceramic')
    if m['name']=='RAVENNA':role=roles.get(n,'mosaic')
    placed=0
    positions=[(2,3),(m['width']-5,3),(2,m['height']-5),(m['width']-5,m['height']-5),(2,cy),(m['width']-5,cy)]
    positions=positions[n%len(positions):]+positions[:n%len(positions)]
    # Keep puzzle rooms' walkable areas unchanged apart from their graphics.
    if n not in {0,1,2,3,4,5,6,7,11,12,15,16,36,37,51,74,75,90,95}:
        for x,y in positions:
            asset=s.assets[role if placed<2 else 'plant']
            if place(a,old,m,mask,asset,x,y):placed+=1
            if placed>=3:break
    assert connectivity_preserved(m,old,a),f'connectivity {key}'
    sp=s.save(w);w.map(key,a,sp)
    w.changes.append(dict(map=list(key),city=m['name'],kind='interior',floor_style=n%4,role=role,added_furniture=placed,changed_cells=int(np.sum(a!=old))))

def outdoor(w,key):
    m=MAPS[key];old=BASE.blocks(key);a=old.copy();mask=protection(m,3)
    # Preserve the boundary tiles and connection transition strips.
    mask[:7,:]=True;mask[-7:,:]=True;mask[:,:7]=True;mask[:,-7:]=True
    s=Secondary(key);flower=s.transplant((34,68),4)
    # The source's flower palette is the shared primary palette 2.
    pp=BASE.tileset(MAPS[(34,68)]['primary'])[1];tp=BASE.tileset(m['primary'])[1]
    assert BASE.data[pp+64:pp+96]==BASE.data[tp+64:tp+96]
    count=0;flowers=0
    # Small groves have different arrangements in each city and leave broad paths.
    for y in range(8,m['height']-9,8):
        for x in range(8,m['width']-9,10):
            if (x//10+2*(y//8)+key[1])%3==0:continue
            xs=x+((y//8+key[1])%3);ys=y+((x//10+key[1])%2)
            if mask[ys-1:ys+4,xs-1:xs+4].any():continue
            if not np.all(a[ys-1:ys+4,xs-1:xs+4]==0x3001):continue
            prev=a[ys:ys+2,xs:xs+2].copy()
            a[ys:ys+2,xs:xs+2]=[[0x3dd4,0x3dd5],[0x3ddc,0x3ddd]]
            if not connectivity_preserved(m,old,a):a[ys:ys+2,xs:xs+2]=prev;continue
            count+=1
            for xx,yy in [(xs-1,ys+2),(xs+2,ys+2)]:
                if not mask[yy,xx] and a[yy,xx]==0x3001:a[yy,xx]=0x3000|flower;flowers+=1
    # Flower borders beside selected paved streets, kept entirely on grass.
    paved=(old&1023)==(0x202 if key in [(34,47),(34,68),(34,110)] else 0x200)
    for y in range(8,m['height']-8):
        for x in range(8,m['width']-8):
            if a[y,x]!=0x3001 or mask[y,x] or (x+2*y+key[1])%5:continue
            if paved[y-1:y+2,x-1:x+2].any():a[y,x]=0x3000|flower;flowers+=1
    if key==(34,22):
        # The port has narrow lawns above the quay; larger groves do not fit.
        for y in (4,7):
            for x in range(6,m['width']-6,4):
                if a[y,x]==0x3001 and not mask[y,x]:a[y,x]=0x3000|flower;flowers+=1
    assert connectivity_preserved(m,old,a)
    sp=s.save(w);w.map(key,a,sp)
    w.changes.append(dict(map=list(key),city=m['name'],kind='outdoor',groves=count,flowers=flowers,changed_cells=int(np.sum(a!=old))))

def main():
    w=Writer()
    fixes=[]
    for n in range(110,118):
        key=(34,n);m=MAPS[key];actual=w.layouts[m['layout_id']-1]-B
        assert actual!=m['layout']
        w.register(key,m['layout']);fixes.append(dict(map=list(key),city=m['name'],old_layout_id=m['layout_id'],new_layout_id=w.assigned[m['header']]))
    for n in range(118):
        m=MAPS[(34,n)]
        if m['type']==8 and m['secondary']>=0x55f000:interior(w,(34,n))
    for key in [(0,9),(0,10),(34,17),(34,22),(34,47),(34,68),(34,85),(34,96),(34,110)]:outdoor(w,key)
    p,table=w.finish()
    manifest=dict(source_sha256=EXPECTED,output_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),rom_bytes=p.stat().st_size,layout_table=table,layout_count=len(w.layouts),layout_fixes=fixes,changes=w.changes,allocations=w.allocations,validation='static; full emulator playthrough not performed')
    (OUT/'revision_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    print('ROM',p,'size',p.stat().st_size,'allocation end',hex(w.cursor))
    print('Interiors',sum(c['kind']=='interior' for c in w.changes),'cities',sum(c['kind']=='outdoor' for c in w.changes),'layout fixes',len(fixes))

if __name__=='__main__':main()
