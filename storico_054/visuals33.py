"""Hand-selected room upgrades and legible exits, retaining live 0.32 events."""
from engine32 import *
import places32 as A,interior as I,art,art22,decor,_stamps,collections,random
from PIL import Image,ImageDraw
LIVE=None

def init():
 global LIVE
 LIVE=romlib.Rom(bytes(W.d));r22.ROM=LIVE;_stamps.ROM=LIVE;_stamps._cache.clear()

def live_canvas(key):
 m=LIVE.map(*key);cv=r22.RCanvas(m['width'],m['height'],key);cur=W.rom.map(*key)
 for dst,src in [('objs','objects'),('bwarps','warps'),('bcoords','coords'),('bbgs','bgs'),('conns','conns')]:setattr(cv,dst,copy.deepcopy(cur[src]))
 a=LIVE.blocks(m);get=_stamps._layers(m)
 for y in range(cv.h):
  for x in range(cv.w):
   v=int(a[y,x]);b,t,beh,layer=get(v&1023)
   if m['primary']==0x55e8c0 and v&1023<512:cv.put(x,y,v&1023,(v>>10)&3,v>>12)
   else:cv.art[y][x]=(Image.fromarray(b,'RGBA'),Image.fromarray(t,'RGBA'),(v>>10)&3,beh,bool(layer))
 if m['type'] in (4,8):cv.void_cell=(0,0)
 return cv

def room(key,floor,wall):
 m=W.rom.map(*key);r=I.Room(m['width'],m['height'],key,floor=floor,wall=wall);r.objs=copy.deepcopy(m['objects']);r.bbgs=copy.deepcopy(m['bgs']);r.bcoords=copy.deepcopy(m['coords']);r.bwarps=copy.deepcopy(m['warps'])
 exits={(w['x'],w['y']) for w in r.bwarps};r.void([(x,r.h-1) for x in range(r.w) if (x,r.h-1) not in exits]+[(0,y) for y in range(2,r.h)]+[(r.w-1,y) for y in range(2,r.h)])
 for w in r.bwarps:
  x,y=w['x'],w['y'];v=int(LIVE.blocks(LIVE.map(*key))[y,x]);b,t,beh,lay=_stamps._layers(LIVE.map(*key))(v&1023);r.art[y][x]=(Image.fromarray(b,'RGBA'),Image.fromarray(t,'RGBA'),0,beh,False)
 return r

def keep_events(cv,radius=1):
 keep=set()
 for o in cv.objs+cv.bcoords+cv.bwarps:
  for dx in range(-radius,radius+1):
   for dy in range(-radius,radius+1):keep.add((o['x']+dx,o['y']+dy))
 for o in cv.bbgs:keep.add((o['x'],o['y']))
 return keep

def clear_approaches(r):
 for o in r.objs:
  for x,y in [(o['x'],o['y']),(o['x'],o['y']+1)]:
   if 0<x<r.w-1 and 1<y<r.h-1:r.art[y][x]=(I.floor_tile(r.floor_kind,x,y),None,0,0,False)

def add(r,x,y,prop,keep=None):
 im=prop['img'] if isinstance(prop,dict) else prop;cells={(x+dx,y+dy) for dx in range(im.width//16) for dy in range(im.height//16)}
 if any(not (1<=xx<r.w-1 and 2<=yy<r.h-1) for xx,yy in cells):return False
 if cells & (keep or set()):return False
 r.furn(x,y,prop)
 return True

def crate():
 im=Image.new('RGBA',(32,32),(0,0,0,0));d=ImageDraw.Draw(im);d.rectangle((1,7,29,29),fill=(140,90,49),outline=(74,49,33));d.polygon([(1,7),(8,2),(31,2),(29,7)],fill=(198,148,90));d.rectangle((3,10,27,26),fill=(181,123,66));d.line((3,10,27,26),fill=(115,74,41),width=3);d.line((27,10,3,26),fill=(214,165,99),width=3);d.rectangle((6,11,14,17),fill=(231,214,165));return A.asset(im)

def ceramics():
 im=Image.new('RGBA',(48,32),(0,0,0,0));d=ImageDraw.Draw(im);d.rectangle((1,17,46,24),fill=(148,99,57));d.rectangle((4,24,7,31),fill=(82,57,33));d.rectangle((40,24,43,31),fill=(82,57,33))
 for x,c in [(8,(49,99,165)),(23,(189,99,49)),(37,(74,132,90))]:
  d.ellipse((x-5,7,x+5,20),fill=(239,222,181),outline=c);d.rectangle((x-2,5,x+2,9),fill=c);d.line((x-4,13,x+4,13),fill=c)
 return A.asset(im)

def ropes():
 im=Image.new('RGBA',(32,16),(0,0,0,0));d=ImageDraw.Draw(im)
 for dx in [0,16]:
  for pad in [0,3,6]:d.ellipse((dx+pad,3+pad//2,dx+15-pad,14-pad//2),outline=(189,148,82),width=2)
 return A.asset(im)

def toolrack():
 im=Image.new('RGBA',(48,32),(0,0,0,0));d=ImageDraw.Draw(im)
 d.rectangle((1,3,46,27),fill=(140,99,57),outline=(82,57,33));d.rectangle((3,5,44,25),fill=(173,132,82))
 for x in (10,24,37):
  d.line((x,12,x,23),fill=(82,74,66),width=3)
 d.arc((6,6,14,14),0,180,fill=(214,222,222),width=3);d.rectangle((19,8,29,12),fill=(181,189,198));d.line((34,8,40,14),fill=(214,214,206),width=3)
 d.rectangle((2,28,45,30),fill=(99,66,41));return A.asset(im)

def firstaid():
 im=Image.new('RGBA',(32,32),(0,0,0,0));d=ImageDraw.Draw(im)
 d.rectangle((2,7,29,29),fill=(222,222,206),outline=(99,115,107));d.rectangle((10,3,21,7),outline=(99,115,107),width=2);d.rectangle((13,12,18,25),fill=(206,66,66));d.rectangle((9,16,22,21),fill=(206,66,66));return A.asset(im)

def rooms():
 # Theme, dimensions and original object positions define each room's arrangement.
 specs={
 (34,23):('archive','tiles','ochre'),(34,28):('warehouse','planks','blue'),(34,31):('dining','terracotta','ochre'),
 (34,45):('harbor','planks','blue'),(34,46):('warehouse','planks','brick'),(34,48):('archive','tiles','ochre'),
 (34,49):('home','planks','plaster'),(34,50):('dining','terracotta','ochre'),(34,62):('workshop','planks','brick'),(34,63):('home','blue','blue'),(34,64):('inn','planks','ochre'),(34,65):('ceramic','tiles','ochre'),(34,66):('garden','tiles','green'),(34,67):('harbor','planks','brick'),
 (34,69):('archive','tiles','ochre'),(34,77):('dining','terracotta','ochre'),(34,78):('workshop','planks','plaster'),
 (34,86):('archive','tiles','ochre'),(34,88):('ceramic','tiles','plaster'),(34,89):('workshop','terracotta','brick'),
 (34,98):('mausoleum','tiles','plaster'),(34,99):('archive','tiles','ochre'),(34,100):('mosaic','tiles','blue'),
 (34,103):('ceramic','terracotta','ochre'),(34,104):('archive','planks','plaster'),(34,105):('workshop','terracotta','brick'),(34,106):('gallery','planks','blue'),(34,107):('archive','tiles','plaster'),(34,108):('harbor','planks','blue'),
 (35,4):('archive','tiles','ochre'),(35,5):('workshop','checker','brick'),(35,6):('home','terracotta','brick'),(35,7):('inn','planks','ochre'),(35,8):('ranger','planks','green'),(35,23):('inn','planks','brick'),(35,24):('ranger','planks','blue'),(35,25):('lab','tiles','green')}
 for key,(theme,floor,wall) in specs.items():
  r=room(key,floor,wall);keep=keep_events(r);w,h=r.w,r.h;left,right=2,w-5;back,front=3,h-5
  # Furniture is grouped by use, with the main doorway and NPC approaches preserved.
  if theme in ('archive','gallery'):
   for x,y in [(left,back),(right,back),(left,front),(right,front)]:add(r,x,y,I.shelf('books',3) if theme=='archive' else A.vitrine('crystals'),keep)
   add(r,left,7,I.desk(),keep);add(r,max(2,w//2-3),max(3,h//2),A.map_table(),keep);add(r,right,7,I.sofa(),keep)
   if theme=='gallery':add(r,w//2-1,3,A.stemma(),keep)
  elif theme in ('warehouse','workshop','ceramic','harbor','ranger','lab','mosaic'):
   sets={'warehouse':[crate(),I.barrels(),crate(),ropes(),crate()], 'workshop':[toolrack(),A.apparatus(),A.map_table(),crate(),I.shelf('jars',3)],'ceramic':[ceramics(),I.shelf('jars',3),ceramics(),I.desk(),I.barrels()],'harbor':[A.map_table(),ropes(),I.shelf('bottles',3),I.desk(),I.barrels()],'ranger':[A.map_table(),firstaid(),I.shelf('books',3),I.fireplace(),I.bed()],'lab':[A.apparatus(),I.shelf('jars',3),A.map_table(),A.apparatus(),I.desk()],'mosaic':[ceramics(),toolrack(),A.map_table(),I.shelf('jars',3),A.vitrine('crystals')]}
   for (x,y),p in zip([(left,back),(right,back),(left,front),(right,front),(max(2,w//2-2),3)],sets[theme]):add(r,x,y,p,keep)
   if w>=20:add(r,left,9,crate() if theme in ('warehouse','workshop') else I.sofa(),keep)
  elif theme=='mausoleum':
   # Central porphyry basin and a restrained pale stone chamber.
   for x,y in [(3,3),(w-5,3),(3,h-6),(w-5,h-6)]:add(r,x,y,A.column(),keep)
   im=Image.new('RGBA',(64,48),(0,0,0,0));d=ImageDraw.Draw(im);d.ellipse((4,16,59,41),fill=(90,57,66),outline=(57,41,49),width=2);d.rectangle((4,14,59,28),fill=(123,74,82));d.ellipse((4,4,59,28),fill=(156,99,107),outline=(82,49,57),width=3);d.ellipse((9,8,54,23),fill=(74,49,57),outline=(181,123,123),width=2)
   add(r,w//2-2,4,A.asset(im),keep);add(r,3,9,A.bench_row(3),keep);add(r,w-6,12,A.bench_row(3),keep)
  elif theme in ('home','inn'):
   add(r,left,back,I.bed((99,140,181)),keep);add(r,right,back,I.wardrobe(),keep);add(r,left,front,I.sofa(),keep);add(r,right,front,I.table(),keep);add(r,w//2-2,back,I.shelf('books',2),keep)
   if theme=='inn':add(r,right-1,back+3,I.bed((165,90,74)),keep);add(r,left,7,I.fireplace(),keep)
   else:add(r,w//2-2,front,I.desk(),keep)
  elif theme=='dining':
   add(r,left,back,I.counter(4),keep);add(r,right,back,I.shelf('bottles',3),keep);add(r,left,front,I.table(),keep);add(r,right,front,I.table(check=(57,140,74)),keep);add(r,w//2-2,6,I.table(),keep)
  elif theme=='garden':
   for x,y in [(left,back),(right,back),(left,front),(right,front)]:add(r,x,y,I.plant(),keep)
   add(r,left,7,I.shelf('jars',2),keep);add(r,right-1,7,I.desk(),keep);add(r,w//2-2,3,A.map_table(),keep)
  for x in range(2,w-1,5):r.furn(x,0,I.window_art(wall,curtain=(99,140,173) if theme in ('harbor','ranger') else (173,123,82)))
  clear_approaches(r);emit(r,'rev33_'+theme+'_'+str(key[0])+'_'+str(key[1]))
 # A real dining hall: five groups of tables, an innkeeper, kitchen and service cupboard.
 key=(35,35);r=room(key,'terracotta','ochre');keep=keep_events(r,0)
 for o in r.objs[:5]:add(r,o['x']-1,o['y']-2,I.table(check=(173,66,49)),keep)
 add(r,2,2,I.fireplace(),keep);add(r,7,2,I.hams(),keep);add(r,14,2,I.shelf('bottles',5),keep);add(r,18,6,I.counter(3),keep);add(r,18,9,I.barrels(),keep)
 for x in [3,9,15]:r.furn(x,0,I.window_art('ochre',curtain=(173,66,49)))
 clear_approaches(r);emit(r,'rev33_casa_aie_sala')
 # Enrich the existing themed venues, while preserving their carefully placed exits and quest NPCs.
 additions={(34,29):[(2,16,ropes()),(21,17,ropes())],(34,42):[(3,7,A.map_table()),(14,7,I.plant())],(34,34):[(15,4,I.sofa()),(3,16,I.shelf('books',3))],(34,35):[(8,15,I.counter(4)),(9,4,A.map_table())],(34,70):[(2,6,A.column()),(19,6,A.column())],(34,71):[(9,22,A.bench_row(4)),(20,22,A.bench_row(4))],(34,75):[(7,24,A.weaponrack()),(20,24,A.weaponrack())],(35,11):[(2,15,I.shelf('books',3)),(18,15,I.wardrobe())],(35,22):[(2,3,I.shelf('bottles',3)),(19,3,I.wardrobe()),(3,12,A.bench_row(4))]}
 for key,props in additions.items():
  cv=live_canvas(key);keep=keep_events(cv)
  for x,y,prop in props:
   im=prop['img'] if isinstance(prop,dict) else prop;cells={(x+dx,y+dy) for dx in range(im.width//16) for dy in range(im.height//16)};a=LIVE.blocks(LIVE.map(*key))
   if cells&keep or any(not(1<=xx<cv.w-1 and 2<=yy<cv.h-1) or a[yy,xx]&0xc00 for xx,yy in cells):continue
   cv.place_art(x,y,prop)
  emit(cv,'rev33_dettagli_'+str(key[0])+'_'+str(key[1]))


def guide_text(region):
 return {0:'Lido di Savio',1:'Cervia',2:'Lugo',3:'Imola',4:'Faenza',6:'Cesenatico',7:'Cesena',8:'Rimini',9:'Forli',10:'Bagno di Romagna',11:'Ravenna',15:'Lega Romagna',28:'Safari Romagna',29:'Mirabilandia',73:'Sentiero del Fumaiolo',74:'Santuario del Fumaiolo',76:'Passo dei Draghi',77:'Via Vittoria'}.get(region,'Sentiero della Romagna')

def exits_and_services():
 citykeys=[(0,9),(0,10),(34,17),(34,22),(34,44),(34,47),(34,68),(34,85),(34,94),(34,96),(34,110),(35,1),(35,19),(35,34)]
 gyms={(2,1),(34,36),(34,51),(34,74),(34,90),(34,112),(35,9),(35,26)}
 for key in citykeys:
  cv=live_canvas(key);m=LIVE.map(*key);a=LIVE.blocks(m);used=keep_events(cv,0);added=0;destinations=set()
  for w in list(cv.bwarps):
   dest=(w['group'],w['num'])
   if dest==key:continue
   dm=W.rom.map(*dest);x,y=w['x'],w['y']
   if dest in gyms:
    # Consistent Gym plaque beside the native facade, with a bright Poké Ball crest.
    xx,yy=x+1,y-1
    if 0<=xx<cv.w and 0<=yy<cv.h and (xx,yy) not in used:
     im=Image.new('RGBA',(16,16),(206,82,49,255));d=ImageDraw.Draw(im);d.rectangle((1,1,14,14),outline=(247,222,165));A.txt(im,(1,4),'GYM',(247,239,214));cv.art[yy][xx]=(im,None,1,0,False)
   if dm['type'] not in (1,2,3) or not(x in (0,1,cv.w-2,cv.w-1) or y in (0,1,cv.h-2,cv.h-1)):continue
   if added>=4 or dest in destinations:continue
   for xx,yy in [(x-2,min(cv.h-3,max(2,y+1))),(x+2,min(cv.h-3,max(2,y+1))),(min(cv.w-3,max(2,x+1)),y-2)]:
    if not(1<=xx<cv.w-1 and 2<=yy<cv.h-1) or (xx,yy) in used or a[yy,xx]&0xc00:continue
    if any(abs(xx-o['x'])+abs(yy-o['y'])<=1 for o in cv.objs+cv.bcoords+cv.bwarps):continue
    sign(cv,xx,yy,'DIREZIONE '+guide_text(dm['region'])+'\nSegui il sentiero fino al varco.');used.add((xx,yy));destinations.add(dest);added+=1;break
  if key==(0,9):
   # The river is named before crossing the northern footbridge.
   for x,y in [(21,10),(23,4)]:
    if 0<=x<cv.w and 0<=y<cv.h and (x,y) not in used and not a[y,x]&0xc00:sign(cv,x,y,'FIUME SAVIO\nLa corrente attraversa la pineta e sfocia nell\'Adriatico. Il percorso sulla riva conduce verso Ravenna.');break
  emit(cv,'rev33_servizi_uscite_'+str(key[0])+'_'+str(key[1]))
