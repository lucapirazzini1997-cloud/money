import re,sys
A=open('base21.gba','rb').read();Bd=open('/home/claude/proj/sorgenti_romagna/pokemon_romagna_alpha_12.gba','rb').read()
syms={}
for l in open('/home/claude/qa/syms.txt'):
    p=l.split()
    if len(p)==3: syms[p[2]]=int(p[0],16)
def mask_pattern(b):
    # mask thumb BL pairs
    out=b''
    i=0
    while i<len(b)-1:
        hw=b[i]|b[i+1]<<8
        if (hw&0xf800)==0xf000 and i+3<len(b):
            out+=b'..'+b'..';i+=4;continue
        out+=re.escape(b[i:i+2]);i+=2
    return out
def find(name,n=40):
    a=syms[name]&~1;off=a-0x08000000
    if off<0 or off>=len(Bd): return None
    if A[off:off+n]==Bd[off:off+n]: return a
    pat=mask_pattern(Bd[off:off+n])
    hits=[m.start() for m in re.finditer(pat,A,re.S)]
    return [hex(h+0x08000000) for h in hits[:5]]
if __name__=='__main__':
    for s in sys.argv[1:]: print(s, find(s) if isinstance(find(s),list) else hex(find(s)))
