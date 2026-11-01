from engine32 import *
from places32 import *
from world32 import lane,border,ground,native_warp,encounter
from _town import tree,lamp,bench


def rail_tile(kind='h',color=(198,49,49)):
 im=Image.new('RGBA',(16,16),(0,0,0,0));d=ImageDraw.Draw(im);dark=tuple(max(0,x-66) for x in color);light=tuple(min(255,x+49) for x in color)
 if kind=='h':
  for y in (5,10):d.line((0,y,15,y),fill=color,width=2)
  for x in (2,8,14):d.line((x,5,x,11),fill=dark)
  d.line((0,4,15,4),fill=light)
 elif kind=='v':
  for x in (5,10):d.line((x,0,x,15),fill=color,width=2)
  for y in (2,8,14):d.line((5,y,11,y),fill=dark)
  d.line((4,0,4,15),fill=light)
 else:
  d.arc((-11,-11,20,20),0,90,fill=color,width=2);d.arc((-5,-5,14,14),0,90,fill=color,width=2)
 return asset(im,{(0,0)})

def coaster(cv,x,y,w,h,color,theme):
 # Repeated native-sized rail pieces retain their crisp shapes within the GBA tile budget.
 for xx in range(x+1,x+w-1):
  for yy in (y,y+h-1):cv.place_art(xx,yy,rail_tile('h',color))
 for yy in range(y+1,y+h-1):
  for xx in (x,x+w-1):cv.place_art(xx,yy,rail_tile('v',color))
 c=rail_tile('c',color)
 for xx,yy,rot in [(x,y,0),(x+w-1,y,90),(x+w-1,y+h-1,180),(x,y+h-1,270)]:cv.place_art(xx,yy,asset(c['img'].rotate(rot),{(0,0)}))
 # Elevated crest/loop with visible support columns.
 iw,ih=80,96;im=Image.new('RGBA',(iw,ih),(0,0,0,0));d=ImageDraw.Draw(im)
 for xx in (16,62):d.line((xx,22,xx,94),fill=(115,132,132),width=3)
 if theme=='ispeed':
  pts=[(0,92),(10,83),(23,17),(32,7),(43,7),(54,17),(67,84),(79,92)]
  d.line(pts,fill=(90,90,90),width=5);d.line([(a,b-2) for a,b in pts],fill=color,width=3)
  d.line([(a,b+3) for a,b in pts],fill=color,width=2)
 elif theme=='katun':
  d.ellipse((12,6,67,77),outline=color,width=5);d.line((0,88,17,65),fill=color,width=4);d.line((64,63,79,88),fill=color,width=4)
  d.ellipse((17,11,62,72),outline=(148,156,156),width=1)
 else:
  d.rectangle((25,7,49,90),fill=(181,189,99));d.rectangle((30,10,44,88),fill=(99,140,156))
  for yy in range(14,89,8):d.line((26,yy,48,yy),fill=(222,222,140))
  d.line((41,9,54,15,75,84),fill=(41,99,165),width=5)
  d.rectangle((23,1,51,8),fill=(222,214,115))
 cv.place_art(x+w//2-2,y+2,asset(im,rect(0,0,5,6)),protect=True)
 # Paddock / boarding station with a clear entrance at the south edge.
 cv.place_art(x+2,y+h,art.shopfront(7,theme.upper(),'cream',awning='red' if theme=='ispeed' else 'blue'))


def ride(name,flag,description):
 s=Script('Attrazione '+name).emit(b'\x6a\x5a').msg('Benvenuto su '+name+'! '+description)
 s.emit(b'\x97\x01\x28'+H(50)+b'\x97\x00').set(flag).msg('Il giro è finito! Scendi dalla pedana e continua a esplorare il parco.').end()
 return s.save()


def mirabilandia():
 key=(34,114);cv=r22.RCanvas(88,72,key);empty_events(cv)
 # Broad continuous promenades lead to three complete, legible attraction precincts.
 cv.path(39,55,10,17);cv.path(5,52,78,5);cv.path(40,6,7,50);cv.path(5,29,78,5)
 cv.fill(53,38,24,12,'pond');cv.fill(53,38,24,12,'pond')
 coaster(cv,7,6,22,14,(206,49,49),'ispeed')
 coaster(cv,54,5,24,14,(49,57,66),'katun')
 coaster(cv,54,37,24,10,(49,115,181),'divertical')
 # Maya sanctuary and foliage around Katun, a launch straight at iSpeed, spray pool at Divertical.
 im=Image.new('RGBA',(64,64),(0,0,0,0));d=ImageDraw.Draw(im)
 for yy in range(0,56,8):d.rectangle((24-yy//3,yy,40+yy//3,yy+7),fill=(181,156,107));d.line((24-yy//3,yy,40+yy//3,yy),fill=(222,198,140))
 for yy in range(10,61,5):d.line((29,yy,35,yy),fill=(123,107,74))
 cv.place_art(72,21,asset(im),protect=True)
 # Family plaza, carousel and food court to make the spaces between rides useful.
 cv.place_art(5,38,art.shopfront(8,'RISTORO','ochre',awning='red'))
 cv.place_art(19,38,art.shopfront(6,'GELATI','pink',awning='blue'))
 for x,y in [(7,46),(13,46),(20,46),(27,46)]:cv.place_art(x,y,art22.aia_table())
 for x,y in [(34,9),(35,20),(49,22),(8,25),(31,37),(46,61),(77,62),(11,61)]:tree(cv,x,y)
 for x,y in [(35,36),(49,34),(33,61),(51,61)]:bench(cv,x,y)
 for x,y in [(36,54),(50,54),(35,31),(49,31)]:lamp(cv,x,y)
 border(cv,rect(40,70,7,2)|rect(86,33,2,5),seed=114)
 native_warp(cv,43,71,34,94,9)
 # Physically adjoining Safari: matching gate and reciprocal warp, not a distant building.
 cv.path(78,34,10,4)
 native_warp(cv,87,35,34,115,1);native_warp(cv,87,36,34,115,1)
 cv.add_obj(44,64,16,talk('MIRABILANDIA\nIl Safari Romagna è subito a est. iSpeed a nord-ovest, Katun a nord-est e Divertical sul lago.'))
 for x,y,name,flag,desc in [(20,25,'iSpeed',0x4f4,'Lancio magnetico, pista rossa e salita a cappello: tieniti forte!'),(67,24,'Katun',0x4f5,'Treno sospeso, grandi anelli e rovine Maya nella città di Sian Ka\'an!'),(65,51,'Divertical',0x4f6,'Ascensore verticale, barche offshore e uno splash nel lago!')]:
  cv.add_obj(x,y,49,ride(name,flag,desc));sign(cv,x+2,y,name.upper()+'\nPedana di accesso davanti all\'addetto.')
 sign(cv,81,34,'SAFARI ROMAGNA >\nTre ambienti: prateria, lago e terra del fuoco.')
 sign(cv,40,65,'MIRABILANDIA\nAttrazioni e ristoro. Uscita sud verso la pineta di Ravenna.')
 emit(cv,'mirabilandia')


def safari():
 # Preserve every original safari clue and capture condition, grouping them by the three beasts.
 key=(34,115);cv=r22.RCanvas(104,76,key);empty_events(cv)
 # Entrance plaza and looping trail with signs at each biome junction.
 cv.path(47,62,10,14);cv.path(4,56,96,5);cv.path(31,10,5,50);cv.path(65,10,5,50)
 cv.path(0,34,36,5);cv.path(30,28,40,4)
 # Entei's warm rocky habitat on the west, with patches of real fire encounters.
 cv.fill(3,5,27,46,'grass');decor.tall_grass(cv,rect(5,15,10,12)|rect(18,31,11,18)|rect(4,43,10,10))
 for x,y in [(5,6),(21,7),(5,29),(26,24)]:
  g=Px(32,32);g.rect(2,10,28,20,(156,115,82));g.rect(6,3,22,18,(189,148,107));g.hline(7,4,18,(222,181,132));cv.place_art(x,y,asset(g.im))
 for yy in range(5,51):
  for xx in range(3,30):
   if cv.over[yy][xx] is None and cv.art[yy][xx] is None:
    im=Image.new('RGBA',(16,16),(189,140,90,255));dd=ImageDraw.Draw(im);dd.point((3,6),fill=(165,115,74));dd.point((11,12),fill=(214,165,107));cv.art[yy][xx]=(im,None,0,0,False)
 # Central lake and island. A bridge gives access to the shrine without confusing invisible barriers.
 cv.fill(39,7,23,38,'pond');ground(cv,rect(46,22,9,7));cv.path(49,28,3,15)
 for yy in range(29,43):
  for xx in range(49,52):cv.art[yy][xx]=(I.floor_tile('planks',xx%2,yy%2),None,0,0x100,False)
 for x,y in [(42,11),(57,11),(43,36),(58,36)]:cv.put(x,y,0x173,1,3)
 # Raikou's prairie on the east: broad grass meadows, scattered trees and a rocky lookout.
 decor.tall_grass(cv,rect(73,8,26,15)|rect(73,28,10,23)|rect(87,30,12,23))
 for x,y in [(75,24),(93,24),(76,52),(97,55),(5,62),(20,63),(76,64),(92,63)]:tree(cv,x,y)
 cv.path(80,20,7,26)
 # Three fixed sanctuary pedestals are visually distinct and all beasts have actual overworld sprites.
 for x,y,col in [(18,19,(189,90,49)),(50,25,(99,173,198)),(86,17,(214,189,66))]:
  im=Image.new('RGBA',(48,32),(0,0,0,0));d=ImageDraw.Draw(im);d.ellipse((0,7,47,31),fill=col);d.ellipse((4,8,43,27),outline=(239,231,189),width=2);cv.place_art(x-1,y-1,asset(im,{(0,1),(1,1),(2,1)}))
 # Main paths keep safe walking space between grass, rather than a maze of random obstacles.
 border(cv,rect(0,34,2,5)|rect(49,74,5,2),seed=115)
 old=copy.deepcopy(source(key)['objects']);cv.objs=old
 positions={1:(51,68),2:(45,46),3:(35,47),4:(68,49),5:(31,62),6:(42,12),7:(59,34),8:(50,25),9:(69,60),10:(22,42),11:(18,19)}
 for i,(x,y) in positions.items():cv.objs[i-1].update(x=x,y=y,move=8)
 cv.objs[7].update(gfx=230,flag=0x887);cv.objs[10].update(gfx=217,flag=0x88f)
 # Raikou and both pre-existing clues migrate together from Mirabilandia to the prairie.
 raim=source((34,114))['objects']
 for idx,x,y in [(3,77,11),(4,95,44),(5,86,17)]:
  o=copy.deepcopy(raim[idx-1]);o.update(id=len(cv.objs)+1,x=x,y=y,move=8)
  if idx==5:
   o.update(gfx=216,flag=0x884)
   # Adapt only the old script's text and local removal ID, preserving the native encounter logic.
   import scr
   ops,_=scr.decode(BASE.data,o['script'],250)
   for at,op,args in ops:
    if op=='loadword':
     oldtext=scr.text(BASE.data,args[1]-B,400).upper()
     if 'ISPEED' in oldtext or 'KATUN' in oldtext:
      newtext='Il parafulmine della prateria vibra! Raikou emerge fra le scariche elettriche.' if 'RAIKOU' in oldtext else 'Prima cerca gli indizi dei due custodi della prateria. Poi torna al santuario di Raikou.'
      struct.pack_into('<I',W.d,at+2,B+W.text(newtext))
    if op=='removeobject' and args[0]==5:struct.pack_into('<H',W.d,at+1,o['id'])
  else:
   fl=0x882 if idx==3 else 0x883
   text="CUSTODE: Il parafulmine ha raccolto una scintilla dorata. Raikou è vicino. Cerca anche l'altro custode della prateria." if idx==3 else "CUSTODE: Le impronte fra l'erba brillano di elettricità. Ora il santuario della prateria ti aspetta."
   sc=Script('Indizio Raikou '+str(idx)).emit(b'\x6a\x5a').set(fl).msg(text).end();o['script']=sc.save()
  cv.objs.append(o)
 # Visible ordinary Pokémon reinforce each area's habitat; native encounters use matching species tables.
 cv.add_obj(11,37,236,talk('VULPIX si scalda fra le rocce. Nel settore di Entei vivono Pokémon di tipo Fuoco.'),move=3,rx=2,ry=1)
 cv.add_obj(90,37,231,talk('MAREEP accumula elettricità nella lana. La prateria è il territorio di Raikou.'),move=3,rx=2,ry=1)
 # Native object limit: ordinary water Pokémon is native Azumarill, placed away from the entrances.
 cv.add_obj(55,41,210,talk('AZUMARILL gioca sulla riva. Il lago al centro custodisce Suicune.'),move=3,rx=1,ry=1)
 native_warp(cv,51,75,34,94,10);native_warp(cv,0,35,34,114,1)
 sign(cv,28,54,'OVEST: TERRA DEL FUOCO\nEntei fra rocce calde e prati di Pokémon Fuoco.')
 sign(cv,47,48,'CENTRO: LAGO DI SUICUNE\nSegui il pontile per raggiungere l\'isola. Cerca gli indizi dei custodi.')
 sign(cv,70,54,'EST: PRATERIA DI RAIKOU\nErba alta, Pokémon Elettro e il santuario sulla radura.')
 # Split into real connected maps so each biome has its own encounter table.
 # (A single large map would mix Fire, Water and Electric encounters.)
 west=add_map((34,115),region=28,mtype=3);east=add_map((34,115),region=28,mtype=3)
 parts=[]
 for gn,x0,width,name in [(west,0,35,'safari_entei'),((34,115),35,35,'safari_suicune'),(east,70,34,'safari_raikou')]:
     part=r22.RCanvas(width,cv.h,(34,115));empty_events(part);part.gn=gn
     for attr in ['terrain','over','pathmask','art','fam']:
         setattr(part,attr,[row[x0:x0+width] for row in getattr(cv,attr)])
     part.objs=[dict(o,x=o['x']-x0) for o in cv.objs if x0<=o['x']<x0+width]
     # Stable local IDs preserve the original capture/quest scripts.
     for j,o in enumerate(part.objs):
         if 'id' not in o:o['id']=30+j
     part.bbgs=[dict(b,x=b['x']-x0) for b in cv.bbgs if x0<=b['x']<x0+width]
     part.bwarps=[dict(w,x=w['x']-x0) for w in cv.bwarps if x0<=w['x']<x0+width]
     for obj in part.objs:
         ox,oy=obj['x'],obj['y'];aa=part.art[oy][ox]
         if aa:part.art[oy][ox]=(aa[0],aa[1],0,aa[3],aa[4])
     part.border=[0x1d4,0x1d5,0x1dc,0x1dd]
     parts.append(part)
 westcv,centercv,eastcv=parts
 # The original direct entrance now lands on the central lake map; the park enters the west sector.
 centercv.bwarps=[dict(x=16,y=75,elev=0,warp=10,group=34,num=94)]
 westcv.bwarps=[dict(x=0,y=35,elev=0,warp=1,group=34,num=114)]
 westcv.conns=[dict(dir=4,offset=0,group=34,num=115)]
 centercv.conns=[dict(dir=3,offset=0,group=west[0],num=west[1]),dict(dir=4,offset=0,group=east[0],num=east[1])]
 eastcv.conns=[dict(dir=3,offset=0,group=34,num=115)]
 # Clear full-width crossings across both new map boundaries.
 for part in parts:
     for y in list(range(34,39))+list(range(56,61)):
         for x in [0,1,part.w-2,part.w-1]:
             if (part is westcv and x<2) or (part is eastcv and x>=part.w-2):continue
             part.art[y][x]=None;part.over[y][x]=None;part.pathmask[y][x]=True
 for part,name in zip(parts,['safari_entei','safari_suicune','safari_raikou']):emit(part,name)
 # Park's east gate is genuinely adjacent to the Safari's western entrance.
 pm=W.rom.map(34,114);ws=copy.deepcopy(pm['warps'])
 for w in ws[1:]:w.update(group=west[0],num=west[1],warp=0)
 events((34,114),warps=ws)
 encounter(west,[(37,28),(58,29),(77,30),(339,29),(218,30),(155,28)],rate=20)
 from world32 import encounter_water
 encounter_water((34,115),[(183,28),(54,29),(194,29),(184,31),(79,30)],rate=20)
 encounter((34,115),[(183,28),(54,29),(194,29),(184,31),(79,30),(311,29)],rate=16)
 encounter(east,[(179,28),(337,29),(25,30),(180,31),(100,29),(81,30)],rate=20)
 # The three legendary beasts remain fixed encounters, outside the grass tables.
