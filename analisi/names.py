import sys, struct
sys.path.insert(0,str(__import__('pathlib').Path(__file__).resolve().parent.parent/'strumenti_rom'))
import romlib
from text_codec import CHAR
ROM=sys.argv[1]
R=romlib.Rom(ROM); d=bytes(R.data)
def s(p):
    o=''
    while d[p]!=0xff and len(o)<40: o+=CHAR.get(d[p],'?'); p+=1
    return o
# region map entries table: search code literal used by GetMapName: try default
T=int(sys.argv[3],16)
names={}
for i in range(213):
    p=struct.unpack_from('<I',d,T+i*8+4)[0]
    if 0x8000000<=p<0xa000000: names[i]=s(p-0x8000000)
import json
json.dump(names,open(sys.argv[2],'w'),ensure_ascii=False,indent=0)
print(len(names), [names.get(i) for i in range(0,10)])
