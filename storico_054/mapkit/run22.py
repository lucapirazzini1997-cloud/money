"""Preview a maps22 module: python3 run22.py lido [--surf]"""
import sys, importlib, time
sys.path.insert(0, 'maps22')
import r22
name = sys.argv[1]
mod = importlib.import_module(name)
t = time.time()
cv = mod.build()
starts = mod.STARTS or [(w['x'], w['y']) for w in cv.bwarps if w['x'] in (0, cv.w - 1) or w['y'] in (0, cv.h - 1)]
res = r22.build(cv, mod.TS, starts, preview='/tmp/claude-0/%s.png' % name, surf='--surf' in sys.argv)
print(name, '%.1fs' % (time.time() - t), 'problems:', res['problems'])
