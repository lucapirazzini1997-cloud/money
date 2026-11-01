import subprocess, os, sys
from PIL import Image
A,B,SEL,START,R,L,U,D,RR,LL=1,2,4,8,16,32,64,128,256,512
# keys: A=1 B=2 SELECT=4 START=8 RIGHT=16 LEFT=32 UP=64 DOWN=128 R=256 L=512
class Emu:
    def __init__(self, rom, sav=None):
        args=['./h',rom]+([sav] if sav else [])
        if os.environ.get('VBAM'): args=['python3',os.path.join(os.path.dirname(os.path.abspath(__file__)),'vb.py'),rom]
        self.p=subprocess.Popen(args,stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True,bufsize=1)
        self.n=0
    def cmd(self,s): self.p.stdin.write(s+'\n'); self.p.stdin.flush()
    def run(self,n): self.cmd(f'run {n}')
    def key(self,k,n=4,wait=8): self.cmd(f'key {k:x} {n}'); self.run(wait)
    def r(self,fmt,addr):
        self.cmd(f'{fmt} {addr:x}'); return int(self.p.stderr.readline().strip(),16)
    def ram(self,addr,ln):
        self.cmd(f'ram {addr:x} {ln}'); return bytes.fromhex(self.p.stderr.readline().strip())
    def w(self,fmt,addr,v): self.cmd(f'{fmt} {addr:x} {v:x}')
    def shot(self,name,scale=2):
        self.cmd(f'shot {name}.ppm'); self.sync()
        Image.open(name+'.ppm').resize((240*scale,160*scale),0).save(name+'.png')
    def sync(self):
        self.cmd('ping'); assert self.p.stderr.readline().strip()=='ok'
    def state(self,f): self.cmd(f'savestate {f}')
    def load(self,f): self.cmd(f'loadstate {f}')
    def close(self): self.cmd('quit')

KEY=dict(A=A,B=B,S=SEL,T=START,R=R,L=L,U=U,D=D)
def mk(rom='test_bar.gba', state=None, sav='t4.sav'):
    e=Emu(rom,sav); e.run(10)
    if state: e.load(state); e.run(5)
    def pos(): 
        sb1=e.r('r32',0x3005d8c); b=e.ram(sb1,12); return (b[0],b[2],b[4],b[5],b[6])
    e.pos=pos
    def walk(s,hold=16):
        for ch in s: e.key(KEY[ch],hold,3)
        e.run(6)
    e.walk=walk
    return e

def flag(e,n):
    sb1=e.r('r32',0x3005d8c); b=e.ram(sb1+0x1270+n//8,1)[0]; return (b>>(n%8))&1
def setflag(e,n,v=1):
    sb1=e.r('r32',0x3005d8c); a=sb1+0x1270+n//8; b=e.ram(a,1)[0]
    b=(b|(1<<(n%8))) if v else (b&~(1<<(n%8))); e.w('w8',a,b)

def setcoins(e,n):
    sb1=e.r('r32',0x3005d8c); sb2=e.r('r32',0x3005d90); key=e.r('r32',sb2+0xAC)
    e.w('w16',sb1+0x494,(n^(key&0xFFFF))&0xFFFF)
def getcoins(e):
    sb1=e.r('r32',0x3005d8c); sb2=e.r('r32',0x3005d90); key=e.r('r32',sb2+0xAC)
    return (e.r('r16',sb1+0x494)^(key&0xFFFF))&0xFFFF
def getmoney(e):
    sb1=e.r('r32',0x3005d8c); sb2=e.r('r32',0x3005d90); key=e.r('r32',sb2+0xAC)
    return e.r('r32',sb1+0x490)^key

def sheet(frames,name,cols=3,sc=1):
    from PIL import Image
    ims=[Image.open(f) for f in frames]; w,h=ims[0].size
    rows=(len(ims)+cols-1)//cols
    W=Image.new('RGB',(w*cols,h*rows))
    for i,im in enumerate(ims): W.paste(im,((i%cols)*w,(i//cols)*h))
    W.save(name)
def talk(e,seq,tag,wait=70,crop=True):
    """seq: string of keys; shot after each; returns names"""
    names=[]
    for i,ch in enumerate(seq):
        e.key(KEY[ch],3,wait); n=f'{tag}{i:02d}'; e.shot(n,1); names.append(n+'.png')
    return names

def bag(e):
    sb1=e.r('r32',0x3005d8c); sb2=e.r('r32',0x3005d90); key=e.r('r32',sb2+0xAC)&0xFFFF
    out={}
    for pocket,off,n in (('items',0x560,30),('keyitems',0x5d8,30),('balls',0x630,16),('tm',0x464,64),('berries',0x6a0,46)):
        b=e.ram(sb1+off,4*n)
        for i in range(n):
            it=b[4*i]|b[4*i+1]<<8; q=(b[4*i+2]|b[4*i+3]<<8)^key
            if it: out[(pocket,it)]=q
    return out
