from pathlib import Path
from functools import lru_cache
import json, struct, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parent.parent
FONT=str(ROOT/'assets/fonts/DejaVuSans.ttf')
MAPS={(m['group'],m['num']):m for m in json.loads((ROOT/'tmp/maps.json').read_text())['maps']}

class ROM:
    def __init__(self,path): self.data=Path(path).read_bytes()
    def u32(self,p): return struct.unpack_from('<I',self.data,p)[0]
    def ptr(self,p): return self.u32(p)-0x08000000
    @lru_cache(None)
    def lz(self,p):
        d=self.data
        if d[p]!=0x10: raise ValueError(f'not LZ77: {p:x}')
        length=int.from_bytes(d[p+1:p+4],'little');p+=4;out=bytearray()
        while len(out)<length:
            flags=d[p];p+=1
            for bit in range(7,-1,-1):
                if len(out)>=length: break
                if flags&(1<<bit):
                    a,b=d[p:p+2];p+=2;n=(a>>4)+3;disp=((a&15)<<8)+b+1
                    if disp>len(out):raise ValueError('invalid LZ distance')
                    for _ in range(n):
                        out.append(out[-disp])
                        if len(out)==length:break
                else:out.append(d[p]);p+=1
        return bytes(out)
    @lru_cache(None)
    def tileset(self,p):
        gfx,pals,mtiles,attrs=[self.ptr(p+i) for i in [4,8,12,16]]
        raw=self.lz(gfx) if self.data[p] else self.data[gfx:gfx+16384]
        a=np.frombuffer(raw,dtype=np.uint8)
        pixels=np.empty(len(a)*2,dtype=np.uint8);pixels[::2]=a&15;pixels[1::2]=a>>4
        return pixels.reshape(-1,8,8),pals,mtiles,attrs
    @lru_cache(None)
    def palette(self,primary,secondary):
        pp=self.tileset(primary)[1];sp=self.tileset(secondary)[1]
        # Romagna's custom graphics reference slots 13--15 as well. Their
        # palettes are present in the tileset; zeroing them blackens buildings.
        raw=self.data[pp:pp+192]+self.data[sp+192:sp+512]
        values=np.frombuffer(raw,dtype='<u2')
        rgb=np.stack([values&31,(values>>5)&31,(values>>10)&31],axis=-1)
        rgb=((rgb*255+15)//31).astype(np.uint8).reshape(16,16,3)
        return rgb
    @lru_cache(None)
    def metatile(self,primary,secondary,mt):
        ptiles,_,pmt,pattr=self.tileset(primary);stiles,_,smt,sattr=self.tileset(secondary)
        pals=self.palette(primary,secondary)
        mptr=pmt+mt*16 if mt<512 else smt+(mt-512)*16
        refs=struct.unpack_from('<8H',self.data,mptr)
        rgb=np.zeros((16,16,3),dtype=np.uint8)
        for layer in range(2):
            for quadrant in range(4):
                ref=refs[layer*4+quadrant];idx=ref&1023
                tiles=ptiles if idx<512 else stiles
                idx=idx if idx<512 else idx-512
                if idx>=len(tiles): tile=np.zeros((8,8),dtype=np.uint8)
                else:tile=tiles[idx]
                if ref&0x400:tile=tile[:,::-1]
                if ref&0x800:tile=tile[::-1,:]
                colors=pals[ref>>12][tile]
                x=(quadrant%2)*8;y=(quadrant//2)*8
                region=rgb[y:y+8,x:x+8]
                if layer==0:region[:]=colors
                else:region[tile!=0]=colors[tile!=0]
        return Image.fromarray(rgb)
    def blocks(self,key):
        m=MAPS[key];layout=self.ptr(m['header']);p=self.ptr(layout+12)
        w,h=struct.unpack_from('<II',self.data,layout)
        return np.frombuffer(self.data,dtype='<u2',count=w*h,offset=p).reshape(h,w).copy()
    def render(self,key,events=False):
        m=MAPS[key];layout=self.ptr(m['header']);primary=self.ptr(layout+16);secondary=self.ptr(layout+20)
        a=self.blocks(key);out=Image.new('RGB',(a.shape[1]*16,a.shape[0]*16))
        for y,row in enumerate(a):
            for x,block in enumerate(row):out.paste(self.metatile(primary,secondary,int(block)&1023),(x*16,y*16))
        if events:
            dr=ImageDraw.Draw(out)
            for o in m['objects']:dr.rectangle((o['x']*16,o['y']*16,o['x']*16+15,o['y']*16+15),outline='#ffda00',width=2)
            for i,w in enumerate(m['warps']):
                x=w['x']*16;y=w['y']*16
                dr.rectangle((x,y,x+15,y+15),outline='#00ffdd',width=2);dr.text((x,y),str(i),fill='#000000')
        return out
    def atlas(self,key,start=0,end=1024,scale=2):
        m=MAPS[key];layout=self.ptr(m['header']);p=self.ptr(layout+16);s=self.ptr(layout+20)
        cols=16;cell=36*scale;rows=(end-start+cols-1)//cols
        out=Image.new('RGB',(cols*cell,rows*cell),'#edf0f2');dr=ImageDraw.Draw(out)
        ft=ImageFont.truetype(FONT,9*scale)
        for n,mt in enumerate(range(start,end)):
            x=n%cols*cell;y=n//cols*cell
            out.paste(self.metatile(p,s,mt).resize((16*scale,16*scale),Image.Resampling.NEAREST),(x,y))
            ap=self.ptr((p if mt<512 else s)+16)+(mt if mt<512 else mt-512)*2
            attr=int.from_bytes(self.data[ap:ap+2],'little')
            dr.text((x,y+17*scale),f'{mt:03X} {attr&255:02X}',font=ft,fill='#17202b')
        return out

if __name__=='__main__':
    rom=ROM(sys.argv[1] if len(sys.argv)>1 else ROOT/'upload/Pokemon_Romagna_0_16.gba')
    out=ROOT/'tmp/before';out.mkdir(exist_ok=True)
    keys=[(0,9),(0,10),(34,17),(34,22),(34,47),(34,68),(34,85),(34,96),(34,110),(34,111),(34,112),(34,79),(34,80),(34,81),(34,82),(34,83),(34,45),(34,62),(34,66)]
    for key in keys:
        rom.render(key).save(out/f'{key[0]}_{key[1]}.png')
    for key in [(34,110),(34,111),(34,112),(34,79)]:
        for start,end in [(0,256),(256,512),(512,768),(768,1024)]:
            rom.atlas(key,start,end,scale=2).save(out/f'atlas_{key[0]}_{key[1]}_{start:03x}.png')
    print('Rendered',len(keys),'maps and 16 atlas pages to',out)
