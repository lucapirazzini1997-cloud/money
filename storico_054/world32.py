from engine32 import *
from places32 import *
from _town import tree,lamp,bench,house_row

WILD={}
WATER={}
def encounter_water(key,mons,rate=12):WATER[key]=(mons,rate)
def encounter(key,mons,rate=18):WILD[key]=(mons,rate)
def ground(cv,cells,cls='grass'):
 for x,y in cells:
  if 0<=x<cv.w and 0<=y<cv.h:cv.art[y][x]=None;cv.over[y][x]=None;cv.terrain[y][x]=cls;cv.pathmask[y][x]=False

def border(cv,gaps=(),seed=1):
 cells=rect(0,0,cv.w,2)|rect(0,cv.h-2,cv.w,2)|rect(0,2,2,cv.h-4)|rect(cv.w-2,2,2,cv.h-4)
 decor.woods(cv,cells-set(gaps),seed=seed,pine_ratio=.4,gaps=0)

def lane(cv,pts,width=3):
 for (x0,y0),(x1,y1) in zip(pts,pts[1:]):
  if x0==x1:cv.path(x0-width//2,min(y0,y1),width,abs(y1-y0)+1)
  elif y0==y1:cv.path(min(x0,x1),y0-width//2,abs(x1-x0)+1,width)

def native_warp(cv,x,y,g,n,index):cv.bwarps.append(dict(x=x,y=y,group=g,num=n,warp=index,elev=0))

def countryside():
 # Aie: move away from the edge into a landscaped forecourt, retaining all original events.
 key=(34,20);cv=r22.RCanvas(48,60,key);cv.bwarps=[];cv.bbgs=[];cv.bcoords=[];cv.conns=[]
 lane(cv,[(2,0),(2,7),(16,7),(16,59)],3);lane(cv,[(16,18),(30,18),(30,14)],3)
 door=cv.place_art(25,8,aie(),protect=True)
 cv.path(24,15,15,9)
 cv.place_art(23,17,art22.entrata_sign(),top_rows=1)
 for x,y in [(24,23),(36,23)]:cv.place_art(x,y,art22.planter(3))
 for x,y in [(24,19),(36,19)]:bench(cv,x,y)
 for x,y in [(22,8),(39,9),(23,13),(39,14)]:tree(cv,x,y)
 # Field systems around a visible north-south lane.
 for y in (13,17,21):
  for x in range(4,13):cv.place_art(x,y,asset(art.vine_row(),{(0,0)}))
 decor.tall_grass(cv,rect(2,28,44,5)|rect(21,37,12,5)|rect(4,43,9,8)|rect(34,47,10,7))
 for x in range(2,46):
  for y in range(28,33):cv.pathmask[y][x]=False
 for y in (36,40,44):
  for x in range(24,43,3):cv.place_art(x,y,asset(art.peach_tree(2),{(0,1)}),top_rows=1)
 cv.fill(25,49,6,5,'pond');cv.place_art(36,32,art.farmhouse())
 border(cv,rect(1,0,4,2)|rect(14,58,4,2),seed=32)
 # Preserve the original Cut gate and event IDs.
 cv.place_objs({1:(16,25),2:(2,4),3:(3,4),4:(5,7)})
 for o in cv.objs:o['move']=8
 native_warp(cv,*door,35,35,0)
 # The existing seam scripts expect entry/exit at these actual coordinates; rewire to explicit warps.
 cv.bwarps += [dict(x=x,y=0,elev=0,warp=0,num=10,group=0) for x in (2,3)]
 # Destination row at Cervia is supplied below using a new reciprocal exit index.
 cerv=W.rom.map(0,10);ci=len(cerv['warps']);ces=W.rom.map(34,17);si=len(ces['warps'])
 events((0,10),warps=cerv['warps']+[dict(x=18,y=51,elev=0,warp=1,group=34,num=20)])
 events((34,17),warps=ces['warps']+[dict(x=42,y=0,elev=0,warp=3,group=34,num=20)])
 for w in cv.bwarps[1:3]:w['warp']=ci
 for x in (15,16):native_warp(cv,x,59,34,17,si)
 sign(cv,20,17,'CASA DELLE AIE\nIngresso nel portico centrale. Cinque tavoli, cinque sfide e un premio dell\'oste.')
 sign(cv,13,25,'CAMPAGNA CERVESE\nA nord Cervia. A sud Cesena. Attraversa i campi di grano.')
 emit(cv,'campagna_cervese')
 # Actual arrival cells of the added seams remain walkable.
 for key,x,y in [((0,10),18,51),((34,17),42,0)]:
  a=blocks(key);a[max(0,y-1):min(a.shape[0],y+2),max(0,x-1):x+2]=0x3121;writeblocks(key,a)
 encounter((34,20),[(191,9),(179,10),(288,10),(306,11),(16,10),(37,12)])


def landmarks():
 cv=cv_from((0,10));ground(cv,rect(23,17,6,8));cv.path(23,17,7,9);cv.place_art(24,18,tower(),protect=True)
 # Clear the immediate doorway, maintain the reciprocal tower warp.
 cv.set_warp(8,26,23);ground(cv,{(26,24),(26,25)});cv.path(26,24,2,3)
 emit(cv,'torre_san_michele')
 # Ippodromo: runners only in the infield, track and grandstand preserved.
 key=(34,19);a=blocks(key)
 m=W.rom.map(*key)
 for y in range(14,24):
  for x in range(15,35):
   if (20<=x<=24 and 16<=y<=18) or (28<=x<=32 and 17<=y<=19):continue
   if not a[y,x]&0xc00:a[y,x]=0x300d
 writeblocks(key,a)
 encounter(key,[(77,16),(58,16),(84,17),(203,18),(234,18),(78,20)],rate=20)


def rival_script():
 s=Script('Rivale obbligatorio e ripresa vecchie vittorie').emit(b'\x6a')
 s.flag(0x4e9,'done')
 for tid in (622,623,624):s.emit(b'\x60'+H(tid)).jump('recover',1)
 s.flag(0x868,'early',False)
 s.msg('ALDO: Verso Rimini si passa di qui! Hai la Medaglia Collina: adesso voglio una vera sfida.')
 s.cmp(0,'b0',var=0x4023).cmp(1,'b1',var=0x4023).jump('b2')
 for name,tid in [('b0',622),('b1',623),('b2',624)]:
  s.label(name).emit(b'\x5c\x02'+H(tid)+H(0)+P(W.text('ALDO: Facciamo sul serio!'))+P(W.text('Sei cresciuto davvero!')))
  s.fix.append((len(s.code),'won'));s.emit(bytes(4)).end()
 s.label('won').set(0x4e9).emit(b'\x53'+H(3)).msg('ALDO: Hai vinto! La strada per Rimini è libera. Ci vediamo alla prossima sfida!').end()
 s.label('recover').set(0x4e9).emit(b'\x53'+H(3)).end()
 s.label('early').msg('ALDO: Prima conquista la Medaglia Collina nella palestra di Cesena. Ti aspetto qui per la nostra sfida.').warp(34,43,23,50)
 s.label('done').end();return s.save()

def riviera():
 key=(34,43);cv=r22.RCanvas(48,76,key);cv.objs=copy.deepcopy(source(key)['objects']);cv.bwarps=[];cv.bbgs=[];cv.bcoords=[];cv.conns=[]
 lane(cv,[(4,0),(4,10),(23,10),(23,75),(29,75)],4)
 cv.fill(33,3,13,67,'sand');cv.fill(41,2,6,72,'sea')
 decor.tall_grass(cv,rect(7,20,12,10)|rect(26,29,10,9)|rect(6,42,12,15)|rect(28,61,10,8))
 cv.fill(4,62,9,7,'pond');cv.path(21,38,11,3)
 for x,y in [(5,15),(17,15),(5,38),(34,44),(32,56),(16,69)]:tree(cv,x,y)
 for x,y in [(27,17),(27,41),(17,60)]:bench(cv,x,y)
 cv.place_art(32,16,art.shopfront(5,'CHIOSCO','cream',awning='blue'))
 border(cv,rect(3,0,4,2)|rect(27,74,4,2),seed=43)
 # A real narrow checkpoint spans every passable cell; no variable can disable it.
 ground(cv,rect(1,52,46,6));decor.woods(cv,rect(1,52,20,6)|rect(26,52,21,6),seed=45,pine_ratio=0,gaps=0)
 cv.path(21,52,5,6)
 rp=rival_script()
 ground(cv,{(26,54),(27,54)})
 cv.objs[0].update(x=20,y=26,move=8);cv.objs[1].update(x=27,y=51,move=8);cv.objs[2].update(x=27,y=54,move=8,script=rp)
 cv.bcoords=[dict(x=x,y=54,elev=0,var=0x400e,val=0,script=rp) for x in range(21,26)]
 for x,y,g,n,wi in [(4,0,34,22,6),(28,75,34,44,0),(5,0,34,22,6),(29,75,34,44,0)]:native_warp(cv,x,y,g,n,wi)
 # Native city and port exits retain their indices; only the route got longer.
 sign(cv,8,3,'RIVIERA ADRIATICA\nA nord Cesenatico, a sud Rimini. Segui il viale alberato fino al varco del rivale.')
 sign(cv,26,70,'RIMINI\nPorto e centro storico oltre il viale. Non occorre Surf per proseguire.')
 emit(cv,'riviera_rivale')
 add_resume(key,Script('Reset rivale').var(0x400e,0).emit(b'\x03').save())
 encounter(key,[(77,18),(58,18),(84,19),(337,18),(179,19),(309,19)])
 # Visible, broad exit from Cesenatico, with no grass/tables covering the threshold.
 cv=cv_from((34,22));gate=Script('Porta grattacielo 0.32').emit(b'\x6a').flag(0x4e8,'open').msg('La porta è chiusa a chiave. La curatrice del Museo della Marineria custodisce le chiavi.').end();gate.label('open').warp(34,34,12,20);gp=gate.save()
 for bg in cv.bbgs:
  if (bg['x'],bg['y'])==(46,15):bg['arg']=B+gp
 ground(cv,rect(41,42,8,6));cv.path(42,41,6,7)
 for x in (44,45):
  # Existing warp ordering (6 and 7) is retained.
  pass
 sign(cv,41,43,'VERSO RIMINI\nUscita sud: Riviera Adriatica. Il varco è alla fine del viale.')
 emit(cv,'uscita_cesenatico')


def verso_forli():
 key=(34,39);cv=r22.RCanvas(64,42,key);cv.bwarps=[];cv.bbgs=[];cv.bcoords=[];cv.conns=[]
 lane(cv,[(63,31),(45,31),(45,20),(23,20),(23,9),(0,9)],4)
 cv.fill(30,4,5,32,'pond');cv.path(28,18,9,4)
 decor.tall_grass(cv,rect(5,15,14,12)|rect(37,7,11,9)|rect(47,22,13,7)|rect(8,30,13,8))
 for y in (4,8):
  for x in range(4,21,3):cv.place_art(x,y,asset(art.peach_tree(2),{(0,1)}),top_rows=1)
 cv.place_art(42,3,art.farmhouse());cv.path(44,9,3,12)
 for x,y in [(6,26),(20,32),(39,30),(55,10)]:tree(cv,x,y)
 border(cv,rect(62,29,2,5)|rect(0,7,2,5),seed=39)
 for x,y,g,n,wi in [(63,31,34,19,1),(0,9,34,68,0),(0,10,34,68,0),(63,32,34,19,1)]:native_warp(cv,x,y,g,n,wi)
 for xx in range(1,63):
  if xx not in (23,24):cv.put(xx,12,0x00e,1,3)
 cv.place_objs({1:(23,12),2:(24,12),3:(26,15),4:(15,29)})
 # Keep story-blocking rock/NPC scripts, add a short reusable training quest.
 trainer(820,'ELISA',[(191,23),(192,24)]);quest=battle(820,0x4f1,'ELISA: I campi verso Forlì sono la mia palestra!','ELISA: Il sentiero per Forlì prosegue a ovest, oltre il canale.')
 cv.add_obj(22,23,13,quest)
 sign(cv,59,29,'VIA EMILIA RURALE\nA est Cesena e ippodromo. A ovest Forlì. Attraversa il ponte sul canale.')
 emit(cv,'campagna_forlivese');encounter(key,[(77,22),(58,22),(203,24),(191,22),(337,23),(234,24)])


def forli_square():
 cv=cv_from((34,68))
 # Replace lawn strips / generic clutter around the piazza with a continuous paved civic space.
 ground(cv,rect(22,16,40,14));cv.path(22,16,40,14)
 # Stone pavement bands follow the square's trapezoidal perspective.
 stone=(222,214,189)
 for y in range(17,30):
  for x in range(23,61):
   im=Image.new('RGBA',(16,16),stone+(255,));d=ImageDraw.Draw(im);d.line((0,15,15,15),fill=(189,181,156));
   if x%5==0:d.line((0,0,0,15),fill=(189,181,156))
   cv.art[y][x]=(im,None,0,0,False)
 # Monument to Aurelio Saffi, set on its own circular garden.
 im=Image.new('RGBA',(64,80),(0,0,0,0));d=ImageDraw.Draw(im);d.ellipse((1,48,62,79),fill=(99,148,90));d.ellipse((6,52,57,76),outline=(222,214,189),width=3);d.rectangle((19,40,45,65),fill=(214,206,181));d.rectangle((16,63,48,69),fill=(181,173,148));d.ellipse((28,2,38,13),fill=(239,239,231));d.polygon([(27,14),(40,14),(45,44),(22,44)],fill=(222,222,214));d.line((29,15,18,29),fill=(239,239,231),width=4)
 cv.place_art(38,21,asset(im,rect(0,0,4,5)),protect=True)
 # Porticoed fronts frame the square without obstructing civic doors.
 for x in (22,56):cv.place_art(x,17,art22.arcade_row(4))
 for x,y in [(25,27),(56,27),(31,19),(50,19)]:lamp(cv,x,y)
 sign(cv,37,27,'PIAZZA AURELIO SAFFI\nPalazzo Comunale e Torre Civica, San Mercuriale e palazzi porticati. Al centro, il monumento a Saffi.')
 # Existing NPCs move into accessible paving and remain linked to the original quests.
 cv.place_objs({2:(30,22),3:(46,27),6:(55,23),7:(6,18),8:(9,20),13:(17,20)})
 emit(cv,'piazza_saffi')


def add_resume(key,p):
 entries=W.rom.map_scripts(W.rom.map(*key));old=next((s for k,s in entries if k==5),None)
 wrap=Script('Resume '+str(key)).emit(b'\x04'+P(p))
 wrap.emit(b'\x05'+P(old) if old is not None else b'\x02')
 W.set_map_scripts(*key,[(k,s) for k,s in entries if k!=5]+[(5,wrap.save())])


def geography():
 # Imola belongs west on the Via Emilia; Bagno belongs south in the Apennines.
 for a,b in [(3,10)]:
  pa=0x74c608+a*8;pb=0x74c608+b*8;ra=bytes(W.d[pa:pa+4]);rb=bytes(W.d[pb:pb+4]);W.d[pa:pa+4]=rb;W.d[pb:pb+4]=ra
 grid=0x74baec
 for i in range(28*15):
  if W.d[grid+i]==3:W.d[grid+i]=10
  elif W.d[grid+i]==10:W.d[grid+i]=3
 for region,x,y in [(73,15,8),(74,15,9),(75,16,9),(76,14,10),(77,13,12),(78,12,12)]:
  W.d[0x74c608+region*8:0x74c608+region*8+4]=bytes([x,y,1,1]);W.d[grid+y*28+x]=region
 for x,y in [(15,7),(15,10),(14,11)]:W.d[grid+y*28+x]=73
 # Access from Cesena's southern road, with a visible locked trail until badge 7.
 key=(34,17);cv=cv_from(key);cv.bwarps=W.rom.map(*key)['warps']
 ground(cv,rect(44,46,6,6));cv.path(45,45,4,7)
 s=Script('Accesso Appennino da Cesena').emit(b'\x6a').flag(0x86d,'open')
 s.msg('Il sentiero sale verso il Fumaiolo. Servono la Medaglia di Imola e un Pokémon che conosca Forza.').end()
 s.label('open').warp(35,10,28,3);gate=s.save()
 idx=len(cv.bwarps)
 # Coordinate gate, not a warp that bypasses the check.
 cv.bcoords=[c for c in cv.bcoords if not(c['y']>=49 and 44<=c['x']<=49)]
 for x in range(45,49):cv.bcoords.append(dict(x=x,y=50,elev=0,var=0x400e,val=0,script=gate))
 # Reciprocal return uses a reserved warp placed one row above the event.
 native_warp(cv,46,49,34,17,idx)
 sign(cv,44,47,'VALLE DEL SAVIO\nA sud Appennino, Monte Fumaiolo e Bagno di Romagna. Passaggio aperto dopo la palestra di Imola.')
 # The reserved arrival is a neutral cell, not a triggered warp.
 emit(cv,'cesena_accesso_appennino')
 add_resume(key,Script('Reset sentiero').var(0x400e,0).emit(b'\x03').save())
 m=W.rom.map(*key);a=blocks(key);a[49,46]=0x3121;writeblocks(key,a)
 # Imola has no portal towards the mountains: close the old west exit.
 key=(35,1);a=blocks(key);a[38:43,0:2]=0x3ddc;writeblocks(key,a);m=W.rom.map(*key);ws=copy.deepcopy(m['warps']);ws[9]=copy.deepcopy(ws[0]);events(key,warps=ws)
 W.changes.append(dict(name='geography',Imola='west of Lugo',Appennino='south of Cesena',Bagno='after Fumaiolo',return_warp=idx))
 return idx


def mountains(return_index):
 key=(35,10);cv=r22.RCanvas(56,52,key);cv.bwarps=[];cv.bbgs=[];cv.bcoords=[];cv.conns=[]
 lane(cv,[(28,0),(28,14),(22,14),(22,27),(43,27),(43,14)],3)
 lane(cv,[(22,24),(11,24),(11,19)],3)
 cv.fill(29,19,5,30,'pond');cv.path(27,26,10,3)
 # Dark tree belts and rock ledges frame distinct climbs and glades.
 decor.woods(cv,rect(2,7,25,4)|rect(30,7,24,4)|rect(5,32,15,13)|rect(38,34,14,12),seed=10,pine_ratio=.8,gaps=.1)
 for x,y in [(3,15),(17,4),(39,4),(47,20),(17,31),(38,30)]:tree(cv,x,y)
 refuge_door=cv.place_art(7,14,art.farmhouse());cave_door=cv.place_art(40,9,art.warehouse(7,'GALLERIA FORZA'))
 cv.path(refuge_door[0],refuge_door[1]+1,2,24-refuge_door[1])
 decor.tall_grass(cv,rect(3,25,12,5)|rect(37,18,13,5)|rect(18,38,10,8))
 border(cv,rect(27,0,3,2),seed=110)
 cv.objs=copy.deepcopy(source(key)['objects']);cv.place_objs({1:(19,26),2:(38,14)})
 for xx in range(1,55):
  if xx!=28:cv.put(xx,8,0x173,1,3)
 cv.add_obj(28,8,87,0x290c74,move=1)
 native_warp(cv,28,0,34,17,return_index);native_warp(cv,*refuge_door,35,11,0);native_warp(cv,*cave_door,35,12,0)
 sign(cv,25,4,'SENTIERO DEL FUMAIOLO\nCesena a nord. Rifugio a ovest. Galleria di Forza e santuario a est.')
 emit(cv,'valle_fumaiolo');encounter(key,[(74,34),(75,35),(339,35),(358,35),(359,36)])
 # The cave network keeps its native trainer, awakening and capture scripts.
 for key in [(35,12),(35,13),(35,14),(35,15),(35,16),(35,17),(35,18)]:
  m=source(key);cv=cv_from(key)
  # Replace undifferentiated cave void with layered limestone walls and a restrained floor.
  for y in range(cv.h):
   for x in range(cv.w):
    v=int(BASE.blocks(m)[y,x]);solid=bool(v&0xc00)
    if solid:
     im=Image.new('RGBA',(16,16),(99,90,82,255));d=ImageDraw.Draw(im);d.polygon([(0,14),(2,6),(8,2),(14,5),(15,14)],fill=(148,140,115));d.line((2,6,8,2,14,5),fill=(189,181,148));cv.art[y][x]=(im,None,1,0,False)
    elif (x,y) not in {(w['x'],w['y']) for w in m['warps']}:
     im=Image.new('RGBA',(16,16),(173,156,123,255));d=ImageDraw.Draw(im);d.point((3,6),fill=(148,132,107));d.point((11,12),fill=(189,173,140));cv.art[y][x]=(im,None,0,0,False)
  # Equipment is placed against chamber walls, preserving all walk routes and native puzzle squares.
  if key[1] in (14,15,16):
   for x in (2,cv.w-6):
    cv.place_art(x,3,apparatus())
   cv.place_art(cv.w//2-2,2,labelart('TEAM EMILIA',5))
  elif key[1]==17:
   # The heart of the mountain: lava pools and basalt columns outside the scripted central arena.
   for x0 in (2,cv.w-7):
    for y in range(8,21):
     for x in range(x0,x0+4):
      if 0<=x<cv.w and not BASE.blocks(m)[y,x]&0xc00:
       im=Image.new('RGBA',(16,16),(181,57,33,255));d=ImageDraw.Draw(im);d.line((0,8,15,6),fill=(247,165,49),width=2);cv.art[y][x]=(im,None,1,0,False)
  elif key[1]==18:
   # Snow patches and alpine grass in the last ascent towards Bagno.
   for x0,y0 in [(7,7),(22,17)]:
    for y in range(y0,min(y0+5,cv.h-2)):
     for x in range(x0,min(x0+6,cv.w-2)):
      if not BASE.blocks(m)[y,x]&0xc00:cv.art[y][x]=(art22.snow_tile(x%2,y%2),None,0,0,False)
  polish_cave(cv,m,key)
  # Each native warp retains its visual and behaviour; all NPCs have a free approach.
  for w in m['warps']:
   x,y=w['x'],w['y'];cv.art[y][x]=None;cv.over[y][x]=(0x1e0,0,3)
   # Use the original metatile to preserve stair/door behaviour exactly.
   from _stamps import _layers
   bot,top,beh,lay=_layers(m)(int(BASE.blocks(m)[y,x])&1023);cv.art[y][x]=(Image.fromarray(bot,'RGBA'),Image.fromarray(top,'RGBA'),0,beh,False)
  for o in m['objects']:
   x,y=o['x'],o['y'];cv.art[y][x]=(I.floor_tile('terracotta',x,y),None,0,0,False)
   if y+1<cv.h-1 and not BASE.blocks(m)[y+1,x]&0xc00:cv.art[y+1][x]=(I.floor_tile('terracotta',x,y+1),None,0,0,False)
  if key[1]==18:
   for x0,y0 in [(7,7),(22,17)]:
    for yy in range(y0,min(y0+5,cv.h-2)):
     for xx in range(x0,min(x0+6,cv.w-2)):
      if not BASE.blocks(m)[yy,xx]&0xc00:cv.art[yy][xx]=None;cv.over[yy][xx]=(0x00d,0,3)
  emit(cv,'appennino_'+str(key[1]))
 encounter((35,18),[(147,39),(148,41),(358,39),(359,41),(395,40),(396,42)],rate=20)
 # Refuge: bunk beds, stove, walking maps; native healing remains unchanged.
 key=(35,11);r=base_room(key,24,20,'planks','brick');exits(r,key)
 for x,y in [(2,4),(2,10),(18,4),(18,10)]:r.furn(x,y,I.bed())
 r.furn(10,2,I.fireplace());r.furn(9,8,I.table(w=4));npc_at(r,1,10,13);npc_at(r,2,14,13);emit(r,'rifugio_fumaiolo')


def rose_sea():
 # Replace the inherited seam that forced Surf even without the HM with an ordinary shore.
 key=(34,44);cv=cv_from(key);cv.bcoords=[];cv.conns=[]
 # Remove every old auto-surf seam along the east edge, and make the pier end finite.
 ground(cv,rect(50,0,6,48),'sea')
 for y in range(48):
  for x in (54,55):cv.art[y][x]=(Image.new('RGBA',(16,16),(82,115,132,255)),None,1,0,False)
 # A discrete seaside gateway opens only after badge 8. Surf still uses the game's native field move.
 gate=Script('Accesso Mare delle Rose con ottava medaglia').emit(b'\x6a').flag(0x86e,'open').msg('AREA MARINA DELLE ROSE\nI fondali sono profondi. Torna con otto medaglie, Surf e la MN Sub.').end()
 gate.label('open').warp(35,36,3,20);gp=gate.save()
 # Walkable pier to a signpost; interacting does not put the player on Surf.
 cv.path(47,20,6,2);ground(cv,rect(47,20,6,2));cv.path(47,20,6,2)
 sign(cv,52,20,'MARE DELLE ROSE\nAttracco subacqueo. Accesso dal molo dopo l\'ottava medaglia.')
 cv.bbgs[-1]['arg']=B+gp
 emit(cv,'porto_accesso_mare')
 # West basin and island basin are separated by an impassable reef. Only Dive joins them.
 key=(35,36);cv=r22.RCanvas(40,32,(34,44));empty_events(cv);cv.gn=key;cv.fill(0,0,40,32,'sea')
 # Exit pier, native surface uses normal Surf from its edge.
 cv.path(0,19,7,3)
 for y in range(32):
  for x in (20,21):
   g=Px(16,16);g.rect(0,4,16,12,(132,140,123));g.rect(2,1,12,11,(173,181,156));g.hline(3,2,9,(214,222,189));cv.place_art(x,y,asset(g.im,{(0,0)}))
 cv.place_art(25,7,art22.isola_rose(),top_rows=2,protect=True)
 # Guard rocks around the platform leave a landing only from its private lagoon.
 for y in (0,31):
  for x in range(40):cv.put(x,y,0x173,1,3)
 for x0,y0 in [(10,19),(28,13)]:
  for y in range(y0,y0+4):
   for x in range(x0,x0+4):cv.art[y][x]=(Image.new('RGBA',(16,16),(8,24,82,100)),None,0,0x12,False)
 # Only the entry deck can be walked; a normal south edge drops to Surf, never auto-forces it.
 for x in range(25,31):
  for y in (9,10):
   a=cv.art[y][x]
   if a:cv.art[y][x]=(a[0],a[1],0,0x100,False)
 # A visible gangway allows disembarkation back into the lagoon after visiting the deck.
 for yy in (11,12):cv.art[yy][30]=(I.floor_tile('planks',0,yy%2),None,0,0x100,False)
 ret=Script('Ritorno dal mare al porto').emit(b'\x6a').warp(34,44,51,21).save()
 sign(cv,2,20,'RITORNO AL PORTO');cv.bbgs[-1]['arg']=B+ret
 reward=Script('Ricordo Isola delle Rose').emit(b'\x6a\x5a').flag(0x4f0,'again')
 reward.gift(219,0x4f0,'Hai raggiunto l\'Isola delle Rose attraversando i fondali! Ecco una CONCHINELLA, ricordo del mare e della tua esplorazione.')
 reward.label('again').msg('Questo era un progetto di libertà sul mare: la piattaforma dell\'Isola delle Rose. Custodisci il ricordo del tuo viaggio.').end();rp=reward.save()
 cv.add_obj(27,10,49,rp);sign(cv,29,10,'ISOLA DELLE ROSE\nPiattaforma artificiale del 1968. Repubblica Esperantista dell\'Isola delle Rose.')
 cv.conns=[dict(dir=5,offset=0,group=35,num=37)];cv.border=[0x170]*4;cv.test_surf=True;emit(cv,'mare_rose_sub')
 # Real underwater corridor; no-surfacing behaviour outside the two aligned pools.
 key=(35,37);cv=r22.RCanvas(40,32,(34,44));empty_events(cv);cv.gn=key
 for y in range(32):
  for x in range(40):
   im=Image.new('RGBA',(16,16),(49,74,115,255));d=ImageDraw.Draw(im);d.line((0,10,15,8),fill=(66,99,132));cv.art[y][x]=(im,None,1,0,False)
 corridor=rect(10,19,4,4)|rect(11,18,20,3)|rect(28,13,4,10)|rect(25,22,10,5)
 for x,y in corridor:
  im=Image.new('RGBA',(16,16),(99,148,165,255));d=ImageDraw.Draw(im);d.point((3,4),fill=(140,181,181));cv.art[y][x]=(im,None,0,0x19,False)
 for x0,y0 in [(10,19),(28,13)]:
  for y in range(y0,y0+4):
   for x in range(x0,x0+4):im=Image.new('RGBA',(16,16),(132,181,189,255));cv.art[y][x]=(im,None,0,0x100,False)
 cv.objs=copy.deepcopy(source(key)['objects']);cv.objs[0].update(x=29,y=24,move=8)
 cv.conns=[dict(dir=6,offset=0,group=35,num=36)];cv.border=[0x173]*4
 emit(cv,'fondali_rose')
 W.header_set(35,36,type=6,region=8,weather=2);W.header_set(35,37,type=5,region=8,weather=14)


def polish_cave(cv,m,key):
 import collections
 a=BASE.blocks(m);entrances=[(w['x'],w['y']) for w in m['warps']]
 nav=a.copy()
 for ax,ay in entrances:nav[ay,ax]&=0xf3ff
 # A stationary guide is an obstacle, while a native Strength boulder can move.
 for o in m['objects']:
  if o['gfx'] not in (86,87) and not o['flag']:nav[o['y'],o['x']]|=0x400
 anchors=list(entrances)
 for o in m['objects']:
  x,y=o['x'],o['y']
  anchors.extend((xx,yy) for xx,yy in [(x,y+1),(x-1,y),(x+1,y),(x,y-1)] if 0<=xx<cv.w and 0<=yy<cv.h and not nav[yy,xx]&0xc00)
 # A connected protected corridor joins every original entrance, trainer and story console.
 protect=set();start=anchors[0]
 for target in anchors:
  q=collections.deque([start]);prev={start:None}
  while q and target not in prev:
   x,y=q.popleft()
   for xx,yy in [(x+1,y),(x,y-1),(x-1,y),(x,y+1)]:
    if 0<=xx<cv.w and 0<=yy<cv.h and not nav[yy,xx]&0xc00 and (xx,yy) not in prev:prev[(xx,yy)]=(x,y);q.append((xx,yy))
  if target not in prev:continue
  pos=target
  while pos is not None:
   x,y=pos
   for dy in (-1,0,1):
    for dx in (-1,0,1):protect.add((x+dx,y+dy))
   pos=prev[pos]
 # Preserve the original Galleria choke point: Forza must still move its boulder.
 if key[1] in (13,18):
  for y in range(2,cv.h-2):
   for x in range(2,cv.w-2):
    if (x,y) in protect or a[y,x]&0xc00:continue
    # Keep a central sanctuary clearing and natural bays, rather than a perfect rectangular maze.
    if key[1]==13 and 11<=x<=21 and 7<=y<=17:continue
    if (x//3+y//3)%4==0:continue
    im=Image.new('RGBA',(16,16),(99,90,82,255));d=ImageDraw.Draw(im);d.polygon([(0,14),(2,6),(8,2),(14,5),(15,14)],fill=(148,140,115));d.line((2,6,8,2,14,5),fill=(189,181,148));cv.art[y][x]=(im,None,1,0,False)
 if key[1]==13:
  for x,y in [(10,5),(21,5),(10,19),(21,19)]:
   if (x,y+1) not in protect:cv.place_art(x,y,column(),top_rows=1)
 if key[1] in (14,15,16):
  for x,y in [(3,8),(cv.w-6,8),(3,14),(cv.w-6,14)]:
   cells=rect(x,y,3,2)
   if not(cells&protect):cv.place_art(x,y,apparatus())
  # Power conduits visually connect the installation to the central arena.
  for y in (6,17):
   for x in range(3,cv.w-3):
    if (x,y) in protect or a[y,x]&0xc00:continue
    im=I.floor_tile('tiles',x,y);d=ImageDraw.Draw(im);d.line((0,7,15,7),fill=(99,115,123),width=4);d.line((0,5,15,5),fill=(181,189,189));d.line((0,10,15,10),fill=(165,66,49));cv.art[y][x]=(im,None,0,0,False)
