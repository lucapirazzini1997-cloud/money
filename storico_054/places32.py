from engine32 import *
import interior as I,art,art22,decor,random,math
from art import Px,C,PAL
from decor import rect
from lido_int import big_plant
from cervia_int import bench_row,burchiella,vitrine,photo,archive_shelf,stemma

# Deliberately limited palettes and repeated details preserve crisp native pixels.
STONE=(214,206,181);SHADOW=(140,132,115);WOOD=(140,99,57);DARK=(57,49,41)
def asset(im,solid=None,door=None):return dict(img=im,solid=solid if solid is not None else rect(0,0,im.width//16,im.height//16),door=door)
def txt(im,xy,text,fill):
 d=ImageDraw.Draw(im);font=ImageFont.truetype(str(ROOT/'fonts/DejaVuSans.ttf'),7);d.text(xy,text,font=font,fill=fill,stroke_width=0)

def tower():
 g=Px(64,96);d=ImageDraw.Draw(g.im)
 # Stocky square tower, sloping foot, pale brick and covered rooftop loggia.
 d.polygon([(7,26),(56,26),(61,94),(2,94)],fill=(165,132,90));d.rectangle((8,24,55,76),fill=(198,165,115))
 d.polygon([(42,24),(55,27),(55,78),(61,94),(43,94)],fill=(156,123,82))
 for y in range(28,91,4):
  d.line((7,y,55,y),fill=(181,148,99))
  for x in range(9+(y//4%2)*4,54,8):d.line((x,y,x,y+3),fill=(173,140,90))
 for yy in (37,53):
  d.rectangle((24,yy,32,yy+11),fill=(231,222,198));d.rectangle((26,yy+2,30,yy+9),fill=(57,57,49))
  d.rectangle((44,yy+3,49,yy+10),fill=(206,189,156));d.rectangle((46,yy+4,48,yy+9),fill=(57,57,49))
 for x,y in [(15,31),(38,41),(18,57),(39,62),(14,67),(47,70)]:d.rectangle((x,y,x+1,y+2),fill=DARK)
 d.rectangle((7,74,56,77),fill=(222,206,173));d.rectangle((7,77,56,79),fill=(148,115,74))
 d.rectangle((5,16,58,26),fill=(206,173,123))
 for x in (10,21,32,43,52):d.rectangle((x,10,x+5,20),fill=(49,49,41))
 d.rectangle((5,20,58,23),fill=(222,198,156))
 d.polygon([(0,11),(9,4),(54,4),(63,11),(61,14),(3,14)],fill=(99,90,66));d.line((3,12,60,12),fill=DARK)
 # Real raised doorway and a clearly readable modern entrance ramp.
 d.rectangle((27,66,36,74),fill=(239,222,181));d.rectangle((29,67,34,74),fill=DARK)
 d.rectangle((28,80,39,94),fill=(49,49,41));d.rectangle((30,82,37,94),fill=(115,90,57));d.rectangle((29,79,38,80),fill=STONE)
 d.rectangle((24,94,45,95),fill=(231,222,198));d.rectangle((42,89,60,92),fill=STONE)
 return asset(g.im,rect(0,0,4,6)-{(2,5)},(2,5))

def aie():
 g=Px(176,112);d=ImageDraw.Draw(g.im);wall=(231,189,107);light=(247,214,140);shade=(181,140,74);roof=(140,123,90)
 # One continuous hipped roof, two symmetrical wings and the central three-arch porch.
 d.polygon([(3,24),(22,10),(154,10),(173,24),(173,32),(3,32)],fill=roof)
 for y in range(14,31,4):
  d.line((9,y,166,y),fill=(173,156,115))
  for x in range(12+(y//4%2)*3,165,6):d.line((x,y,x+2,y+3),fill=(107,99,74))
 d.rectangle((8,32,167,108),fill=wall);d.rectangle((8,32,43,108),fill=light);d.rectangle((133,32,167,108),fill=(214,173,99))
 d.rectangle((7,30,168,34),fill=(99,99,66));d.rectangle((8,69,167,72),fill=(206,206,173))
 for x in [23,145]:
  d.rectangle((x,4,x+9,20),fill=wall);d.rectangle((x-2,2,x+11,5),fill=(99,90,66))
  for dx in (1,5):d.rectangle((x+dx,7,x+dx+2,12),fill=DARK)
 # Tall round arches; recessed dark porch below, grilled upper windows above.
 for x in [48,76,104]:
  d.ellipse((x,42,x+23,74),fill=shade);d.rectangle((x,58,x+23,108),fill=shade)
  d.ellipse((x+3,45,x+20,72),fill=(74,74,49));d.rectangle((x+3,59,x+20,104),fill=(74,74,49))
  d.rectangle((x+7,49,x+15,63),fill=(41,49,41))
  for dx in [9,12,15]:d.line((x+dx,49,x+dx,63),fill=(148,140,115))
  d.rectangle((x,68,x+23,72),fill=(206,206,173))
 for x in [20,145]:
  d.rectangle((x,45,x+12,60),fill=shade);d.rectangle((x+2,46,x+10,59),fill=(49,57,41))
  for dx in [4,8]:d.line((x+dx,46,x+dx,59),fill=(115,115,90))
  d.rectangle((x+1,83,x+11,105),fill=(214,173,90));d.rectangle((x+3,85,x+9,105),fill=shade)
 # Main door in the middle arch, warm light and a visible paved threshold.
 d.rectangle((80,79,95,111),fill=(49,57,41));d.rectangle((82,81,93,108),fill=(99,132,107));d.line((88,81,88,108),fill=(41,66,49));d.rectangle((85,96,86,98),fill=(247,222,123))
 d.rectangle((78,109,97,111),fill=(239,231,198));d.rectangle((63,34,116,42),fill=(99,82,49));txt(g.im,(65,34),'CASA DELLE AIE',(247,231,181))
 return asset(g.im,rect(0,1,11,6)-{(5,6)},(5,6))

def column():
 g=Px(16,32);d=ImageDraw.Draw(g.im);d.rectangle((3,2,12,5),fill=(239,231,206));d.rectangle((5,6,10,27),fill=STONE);d.line((5,6,5,27),fill=(247,239,222));d.line((10,6,10,27),fill=SHADOW);d.rectangle((3,28,12,31),fill=(181,173,148));return asset(g.im,{(0,1)})
def pluteo():
 g=Px(32,16);d=ImageDraw.Draw(g.im);d.polygon([(1,4),(26,4),(31,10),(1,10)],fill=(165,115,66));d.rectangle((2,10,29,13),fill=(107,66,33));d.rectangle((3,13,5,15),fill=DARK);d.rectangle((25,13,27,15),fill=DARK)
 d.polygon([(8,4),(14,3),(18,6),(12,8)],fill=(247,231,189));d.polygon([(14,3),(21,3),(24,6),(18,6)],fill=(222,206,165));d.line((19,7,27,9),fill=(90,90,82));return asset(g.im)
def altar():
 g=Px(64,48);d=ImageDraw.Draw(g.im);d.rectangle((6,30,57,43),fill=(214,206,181));d.rectangle((4,28,59,31),fill=(247,239,214));d.rectangle((12,17,51,27),fill=(239,231,206));d.rectangle((29,1,33,24),fill=(140,99,49));d.rectangle((21,8,41,11),fill=(140,99,49));d.rectangle((6,43,57,47),fill=(156,148,132));return asset(g.im)
def labelart(text,w=4):
 im=Image.new('RGBA',(w*16,16),(82,66,49,255));ImageDraw.Draw(im).rectangle((1,1,w*16-2,14),outline=(206,181,123));txt(im,(4,3),text,(247,231,189));return asset(im)

def base_room(key,w,h,floor='tiles',wall='plaster'):
 r=I.Room(w,h,key,floor=floor,wall=wall);r.objs=copy.deepcopy(source(key)['objects']);r.bbgs=[];r.bcoords=[];r.bwarps=[]
 # Finite rooms, a central aisle, with an explicit visible perimeter.
 r.void([(x,h-1) for x in range(w)]+[(0,y) for y in range(2,h)]+[(w-1,y) for y in range(2,h)])
 return r

def exits(r,key,positions=None):
 ws=source(key)['warps'];positions=positions or [(r.w//2,r.h-1)]+[(r.w-3,4+i*3) for i in range(len(ws)-1)]
 for w,(x,y) in zip(ws,positions):
  base=I.floor_tile(r.floor_kind,x,y);im=base.copy();d=ImageDraw.Draw(im);d.rectangle((1,2,14,14),fill=(165,66,49));d.polygon([(5,6),(11,6),(8,11)],fill=(247,231,189))
  r.art[y][x]=(im,None,0,0x65 if y==r.h-1 else 0x61,False);r.bwarps.append(dict(w,x=x,y=y))

def npc_at(r,idx,x,y):
 o=r.objs[idx-1];o.update(x=x,y=y,move=8);r.art[y][x]=(I.floor_tile(r.floor_kind,x,y),None,0,0,False)

def shelves(r,x,y,w=2,kind='books'):
 r.furn(x,y,I.shelf('books' if kind=='books' else kind,w))

def library():
 key=(34,24);r=base_room(key,24,40,'terracotta','plaster');exits(r,key)
 # Three aisles with twenty columns and 58 chained reading desks.
 for y in range(5,34,2):
  for x in (2,5,17,20):r.furn(x,y,pluteo())
 # 15 rows * 4 = 60, remove the last two to create the entry alcove (58).
 for x in (2,20):
  for xx in range(x,x+2):r.art[33][xx]=(I.floor_tile('terracotta',xx,33),None,0,0,False)
 for y in range(4,34,3):
  for x in (8,15):r.furn(x,y,column(),top_rows=1)
 for y in range(4,34,4):
  for x in (1,22):r.furn(x,y,I.window_art(curtain=(181,173,148)))
 # Oculus / rose window and Malatesta memorial at the end of the central nave.
 im=Image.new('RGBA',(48,32),(239,231,206,255));d=ImageDraw.Draw(im);d.ellipse((10,1,37,28),fill=(173,148,99));d.ellipse((13,4,34,25),fill=(156,198,206));d.line((24,4,24,25),fill=STONE);d.line((13,14,34,14),fill=STONE)
 r.furn(10,0,asset(im));r.furn(10,3,labelart('AULA DEL NUTI',4));r.furn(2,36,I.desk());r.furn(19,36,I.shelf('books',3))
 npc_at(r,1,11,35);npc_at(r,2,5,35)
 r.bbgs.append(dict(x=12,y=3,elev=0,kind=0,arg=B+talk('AULA DEL NUTI: tre navate, venti colonne e 58 plutei. I codici sono ancora custoditi da catene.')))
 emit(r,'malatestiana')

def marineria():
 key=(34,29);r=base_room(key,26,26,'planks','brick');exits(r,key)
 r.furn(10,0,labelart('MUSEO MARINERIA',6))
 r.furn(2,5,burchiella());r.furn(17,5,burchiella())
 # Central full-size historical sail, ropes, sea charts and shipbuilding tools.
 im=Image.new('RGBA',(64,80),(0,0,0,0));d=ImageDraw.Draw(im);d.rectangle((30,2,33,73),fill=(132,90,49));d.polygon([(28,5),(4,51),(28,51)],fill=(239,189,99));d.polygon([(36,10),(58,49),(36,49)],fill=(181,74,49));d.polygon([(5,60),(58,60),(47,75),(17,75)],fill=(132,82,41));d.line((6,63,56,63),fill=(222,173,99),width=3)
 r.furn(11,7,asset(im));r.furn(3,13,vitrine('crystals'));r.furn(20,13,vitrine('crystals'))
 for x in (3,8,18,22):r.furn(x,2,photo((99,140,165)))
 r.furn(2,19,bench_row(4));r.furn(19,19,bench_row(4));r.furn(16,21,I.counter(6))
 npc_at(r,1,15,20);npc_at(r,2,7,16)
 emit(r,'marineria')

def ruota():
 key=(34,42);r=base_room(key,20,18,'blue','blue');exits(r,key)
 # Panoramic cabin: glass on three sides, perimeter benches, central controls.
 for x in range(2,18,2):r.furn(x,0,asset(I.window_art(curtain=(206,222,231))))
 for y in (4,7,10):
  for x in (1,18):r.furn(x,y,I.window_art(curtain=(206,222,231)))
 r.furn(3,4,bench_row(4));r.furn(13,4,bench_row(4));r.furn(3,11,bench_row(4));r.furn(13,11,bench_row(4));r.furn(8,2,labelart('RUOTA',4));r.furn(8,7,I.desk())
 npc_at(r,1,10,9);emit(r,'ruota_panoramica')

def grattacielo():
 for key,w,h in [((34,34),24,22),((34,35),24,24)]:
  r=base_room(key,w,h,'tiles','blue');exits(r,key,[(12,h-1),(20,4)])
  if key[1]==34:
   r.furn(3,4,I.counter(7));r.furn(3,8,I.sofa());r.furn(3,12,I.sofa());r.furn(15,12,I.sofa());r.furn(15,16,I.table(w=3));r.furn(17,6,labelart('SCALE >',4));npc_at(r,1,8,5)
  else:
   for x,y in [(3,5),(3,11),(15,11),(15,17)]:r.furn(x,y,I.desk());r.furn(x+3,y,I.shelf('books',2))
   r.furn(2,18,I.counter(6));r.furn(15,2,labelart('TETTO >',4));npc_at(r,1,12,8)
  for x,y in [(1,2),(21,17),(7,h-3)]:r.furn(x,y,I.plant())
  emit(r,'grattacielo_'+str(key[1]))

def gyms():
 for key,name,floor,wall in [((34,36),'cesena','tiles','green'),((34,51),'rimini','tiles','brick'),((34,74),'forli','planks','brick')]:
  m=source(key);r=base_room(key,m['width'],m['height'],floor,wall);exits(r,key)
  # Keep original trainer locations and the complete badge / quest logic.
  r.objs=copy.deepcopy(m['objects'])
  if name=='cesena':
   for x in (2,15):
    for y in (6,12):
     for yy in range(y,y+3):
      for xx in range(x,x+3):r.art[yy][xx]=(Image.new('RGBA',(16,16),(99,165,99,255)),None,1,0,False)
   for x,y in [(2,4),(16,4),(2,17),(16,17)]:r.furn(x,y,I.plant())
   r.furn(7,2,labelart('VIOLA',5))
   for y in range(5,19):
    for x in (9,10):r.art[y][x]=(I.floor_tile('terracotta',x,y),None,0,0,False)
  elif name=='rimini':
   # Rock terraces and excavation galleries, not a generic empty sports hall.
   for x,y in [(2,6),(17,6),(2,13),(17,13),(2,20),(17,20)]:
    r.furn(x,y,asset(Image.new('RGBA',(64,32),(156,148,123,255))))
    for xx in range(x,x+4):
     for yy in range(y,y+2):
      d=ImageDraw.Draw(r.art[yy][xx][0]);d.line((0,7,15,7),fill=(115,107,90));d.line((7,0,7,15),fill=(181,173,148))
   r.furn(8,2,labelart('AURELIO',5));r.furn(4,2,column(),1);r.furn(19,2,column(),1)
   for y in range(6,24):
    for x in (11,12,13):r.art[y][x]=(I.floor_tile('tiles',x,y),None,0,0,False)
  else:
   for x,y in [(3,17),(15,12),(3,7)]:
    r.furn(x,y,I.rug(6,4,(189,115,74),(239,214,165)))
    # Tatami is walkable and trainers remain on its surface.
    for yy in range(y,y+4):
     for xx in range(x,x+6):a=r.art[yy][xx];r.art[yy][xx]=(a[0],a[1],0,0,a[4])
   r.furn(9,2,labelart('IVANO',5))
   for x in (2,21):r.furn(x,3,I.shelf('books',1))
  for o in r.objs:
   x,y=o['x'],o['y'];r.art[y][x]=(I.floor_tile(floor,x,y),None,0,0,False)
   if r.art[y+1][x][2]:r.art[y+1][x]=(I.floor_tile(floor,x,y+1),None,0,0,False)
  emit(r,'palestra_'+name)

def forli_rooms():
 # San Mercuriale: an abbey nave with organ, colonnades, presbytery and cloister windows.
 key=(34,70);r=base_room(key,24,32,'tiles','brick');exits(r,key);r.furn(10,2,altar())
 for x in (2,19):
  for y in (10,15,20,25):r.furn(x,y,bench_row(3))
 for x in (7,16):
  for y in (8,14,20,26):r.furn(x,y,column(),1)
 r.furn(2,3,I.shelf('books',4));r.furn(18,4,I.fireplace());npc_at(r,1,12,8);npc_at(r,2,6,28);emit(r,'san_mercuriale')
 # San Domenico: two gallery wings around a cloister, art and white statue.
 key=(34,71);r=base_room(key,32,28,'tiles','plaster');exits(r,key)
 for x in (3,8,22,27):
  for y in (3,10,17):r.furn(x,y,I.painting((107,140,165)))
 for x in (10,20):
  for y in (5,11,17):r.furn(x,y,column(),1)
 for y in range(7,18):
  for x in range(12,20):r.art[y][x]=(Image.new('RGBA',(16,16),(140,181,115,255)),None,1,0,False)
 # Ebe-inspired marble figure on a plinth.
 im=Image.new('RGBA',(32,48),(0,0,0,0));d=ImageDraw.Draw(im);d.ellipse((12,0,21,9),fill=(247,239,222));d.polygon([(13,10),(21,10),(25,34),(7,34)],fill=(239,231,214));d.line((13,13,5,23),fill=STONE,width=3);d.line((21,13,28,8),fill=STONE,width=3);d.rectangle((5,35,27,46),fill=(189,181,156))
 r.furn(14,11,asset(im));r.furn(2,22,bench_row(5));r.furn(24,22,bench_row(5))
 for i,(x,y) in enumerate([(16,22),(6,20),(26,20),(7,7),(25,7)],1):npc_at(r,i,x,y)
 emit(r,'san_domenico')
 # Ravaldino: fortified courtyard, armory exhibits and a separate upper hall.
 for key,w,h in [((34,75),32,30),((34,76),24,20)]:
  r=base_room(key,w,h,'tiles','brick');exits(r,key,[(w//2,h-1),(w//2,3)] if key[1]==75 else None)
  if key[1]==75:
   for x,y in [(2,5),(24,5),(2,18),(24,18)]:r.furn(x,y,I.shelf('books',5));r.furn(x,y+2,I.barrels())
   for x in (8,23):
    for y in (6,12,18):r.furn(x,y,column(),1)
   r.furn(12,10,stemma());r.furn(12,17,I.table(w=4));r.furn(2,25,bench_row(5));r.furn(25,25,bench_row(5))
   for i,(x,y) in enumerate([(16,24),(15,6),(24,23)],1):npc_at(r,i,x,y)
  else:
   r.furn(8,2,labelart('CATERINA SFORZA',7));r.furn(8,5,I.desk());r.furn(2,7,I.shelf('books',4));r.furn(17,7,I.shelf('books',4));r.furn(8,11,I.table(w=4));npc_at(r,1,11,9);npc_at(r,2,5,15)
  emit(r,'ravaldino_'+str(key[1]))

# Additional furniture families for the specifically requested venues.
def apparatus():
 im=Image.new('RGBA',(48,32),(0,0,0,0));d=ImageDraw.Draw(im);d.rectangle((1,3,46,27),fill=(90,99,107));d.rectangle((2,4,45,7),fill=(165,173,181));d.rectangle((5,9,22,22),fill=(33,49,57));d.rectangle((7,11,20,19),fill=(74,165,181));d.line((8,16,12,13,15,17,19,12),fill=(173,231,198));d.rectangle((28,10,42,17),fill=(49,57,66));
 for x,col in [(29,(214,66,49)),(35,(99,198,107)),(41,(239,206,82))]:d.ellipse((x-2,20,x+1,23),fill=col)
 d.rectangle((4,28,8,31),fill=DARK);d.rectangle((39,28,43,31),fill=DARK);return asset(im)

def weaponrack():
 im=Image.new('RGBA',(48,32),(0,0,0,0));d=ImageDraw.Draw(im);d.rectangle((2,2,45,25),fill=(115,74,41));d.rectangle((4,4,43,22),fill=(165,115,66));d.rectangle((1,24,46,28),fill=(90,57,33))
 for x in [9,23,37]:d.line((x,4,x,23),fill=(198,206,206),width=2);d.line((x-4,15,x+4,15),fill=(222,181,82),width=2);d.rectangle((x-1,21,x+1,28),fill=DARK)
 return asset(im)

def sandbag():
 im=Image.new('RGBA',(16,32),(0,0,0,0));d=ImageDraw.Draw(im);d.line((8,0,8,5),fill=(99,99,99));d.rounded_rectangle((3,4,13,27),radius=3,fill=(181,66,49));d.line((4,7,12,7),fill=(222,123,74));d.line((6,5,6,25),fill=(206,90,66));d.rectangle((4,27,12,30),fill=(99,57,49));return asset(im,{(0,1)})

def map_table():
 im=Image.new('RGBA',(64,32),(0,0,0,0));d=ImageDraw.Draw(im);d.rectangle((1,5,62,24),fill=(140,90,49));d.rectangle((6,7,56,21),fill=(222,198,148));d.line((9,17,21,12,34,15,49,9),fill=(99,140,132),width=2);d.line((28,8,36,20),fill=(165,115,66));d.rectangle((5,25,8,30),fill=DARK);d.rectangle((55,25,58,30),fill=DARK);return asset(im)

def finish_room(r,name):
 if not getattr(r,'is_room',False):return
 # Side-wall details and controlled furniture density: clear central and perimeter circulation.
 if name.startswith('grattacielo'):
  for x,y in [(3,r.h-4),(16,8)]:r.furn(x,y,apparatus())
  for x in (4,10,16):r.furn(x,0,I.window_art(curtain=(156,189,206)))
 elif name=='marineria':
  r.furn(2,7,weaponrack());r.furn(20,7,weaponrack());r.furn(4,16,map_table());r.furn(17,16,map_table())
 elif name=='palestra_cesena':
  for x0,y0 in [(2,6),(15,6),(2,12),(15,12)]:
   for y in range(y0,y0+3):
    for x in range(x0,x0+3):r.art[y][x]=None;r.over[y][x]=(0x00e if y in (y0,y0+2) else 0x004,1,3)
  for x,y in [(3,2),(14,2),(3,18),(14,18)]:r.furn(x,y,bench_row(3))
 elif name=='palestra_rimini':
  # Geological exhibits and warm torch sconces break up the excavation galleries.
  for x,y in [(3,3),(18,3),(3,16),(18,16)]:r.furn(x,y,apparatus())
  for x in (2,20):r.furn(x,21,weaponrack())
 elif name=='palestra_forli':
  for x,y in [(2,4),(20,4),(10,10),(21,21),(3,23)]:r.furn(x,y,sandbag(),1)
  for x,y in [(4,2),(16,2)]:r.furn(x,y,weaponrack())
  r.furn(14,22,bench_row(6))
 elif name=='san_domenico':
  for x,y in [(3,5),(24,5),(3,12),(24,12),(3,19),(24,19)]:r.furn(x,y,asset(photo((181,140,99))))
  for y in range(7,18):
   for x in range(12,20):
    # Render greenery as planted beds around the statue, rather than a flat rectangle.
    if x in (12,19) or y in (7,17):r.art[y][x]=None;r.over[y][x]=(0x00e,1,3)
  r.furn(14,2,labelart('SAN DOMENICO',6))
 elif name=='san_mercuriale':
  for x,y in [(2,12),(19,12),(2,23),(19,23)]:r.furn(x,y,I.painting((181,140,82)))
  r.furn(9,0,labelart('SAN MERCURIALE',7))
 elif name.startswith('ravaldino'):
  for x,y in [(2,5),(r.w-7,5),(2,r.h-9),(r.w-7,r.h-9)]:r.furn(x,y,weaponrack())
  if name.endswith('75'):r.furn(12,17,map_table());r.furn(3,11,apparatus());r.furn(25,11,apparatus())
  else:r.furn(8,11,map_table())
 # Furniture never occupies a trainer/NPC or the one-cell approach below them.
 for o in r.objs:
  for x,y in [(o['x'],o['y']),(o['x'],o['y']+1)]:
   if 0<=y<r.h-1 and 0<x<r.w-1 and r.art[y][x] is not None and r.art[y][x][2]:r.art[y][x]=(I.floor_tile(r.floor_kind,x,y),None,0,0,False)
