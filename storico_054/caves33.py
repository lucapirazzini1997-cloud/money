"""Readable Victory Road geology, preserving every collision and event cell."""
from engine32 import *
from visuals33 import live_canvas
from PIL import Image,ImageDraw

def install():
 import visuals33
 for key,theme in [((35,28),'ocra'),((35,29),'ardesia'),((35,30),'crinale')]:
  cv=live_canvas(key);m=visuals33.LIVE.map(*key);a=visuals33.LIVE.blocks(m)
  floor,light,stone,shade={'ocra':((198,181,140),(222,206,165),(140,123,90),(74,66,49)),'ardesia':((165,181,181),(198,214,206),(99,123,132),(49,66,74)),'crinale':((189,181,156),(222,214,189),(123,132,107),(57,74,57))}[theme]
  for y in range(cv.h):
   for x in range(cv.w):
    v=int(a[y,x]);coll=(v>>10)&3;beh=visuals33.LIVE.attr(m,v&1023)&255
    im=Image.new('RGBA',(16,16),stone if coll else floor);d=ImageDraw.Draw(im)
    if coll:
     d.polygon([(0,5),(4,1),(12,0),(15,5),(15,15),(0,15)],fill=stone,outline=shade)
     d.line((1,6,5,2,12,2),fill=light);d.line((1,14,14,14),fill=shade)
     if (x+y)%3==0:d.line((9,4,7,9,10,12),fill=shade)
     if y+1<cv.h and not a[y+1,x]&0xc00:
      d.rectangle((0,10,15,15),fill=shade);d.line((2,11,13,11),fill=stone)
     if (x*7+y*11)%37==0:
      d.polygon([(5,13),(3,7),(6,4),(9,9),(8,13)],fill=(148,198,198) if theme=='ardesia' else (206,189,132));d.line((6,5,6,12),fill=light)
    else:
     if y and a[y-1,x]&0xc00:d.rectangle((0,0,15,2),fill=stone)
     if x and a[y,x-1]&0xc00:d.line((0,0,0,15),fill=stone)
     for xx,yy in [(3,11),(12,5)] if (x+y)%3==0 else [(8,12)]:d.point((xx,yy),fill=light)
     if (x+y)%4==0:d.line((10,10,13,10),fill=stone)
    cv.over[y][x]=None;cv.art[y][x]=(im,None,coll,beh,False)
  # Stair mouths are visible at the exact original warp cells.
  for w in cv.bwarps:
   x,y=w['x'],w['y'];im=Image.new('RGBA',(16,16),shade);d=ImageDraw.Draw(im)
   for yy in (4,7,10,13):d.rectangle((3,yy,13,yy+1),fill=light);d.line((3,yy+2,13,yy+2),fill=stone)
   beh=visuals33.LIVE.attr(m,int(a[y,x])&1023)&255;cv.art[y][x]=(im,None,0,beh,False)
  emit(cv,'rev33_via_vittoria_'+theme)
