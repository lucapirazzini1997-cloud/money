import sys
sys.path.insert(0,str(__import__('pathlib').Path(__file__).resolve().parent.parent/'strumenti_rom'))
import romlib
R=romlib.Rom(sys.argv[1])
for key in sys.argv[2:]:
    g,n=map(int,key.split('.')); m=R.map(g,n); bl=R.blocks(m)
    mark={}
    for o in m['objects']: mark[(o['x'],o['y'])]='O'
    for w in m['warps']: mark[(w['x'],w['y'])]='W'
    for b in m['bgs']: mark[(b['x'],b['y'])]='S'
    for c in m['coords']: mark[(c['x'],c['y'])]='C'
    print('==',key,m['width'],m['height'])
    print('   '+''.join(str(x%10) for x in range(m['width'])))
    for y in range(m['height']):
        row=''
        for x in range(m['width']):
            v=int(bl[y,x]); row+=mark.get((x,y),'#' if (v>>10)&3 else '.')
        print('%2d '%y+row)
