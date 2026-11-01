"""Build and write every redesigned map, then report problems. Usage: build_all.py [names...] [--preview DIR]"""
import importlib, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / 'maps'))
import canvas, mapio, check, world

MODULES = ['lido', 'pineta', 'passaggio', 'cervia', 'sentiero', 'saline', 'viasavio', 'cesena']


def run(name, preview_dir=None, write=True):
    mod = importlib.import_module(name)
    t = time.time()
    res = mod.build()
    cv = res[0] if isinstance(res, tuple) else res
    idmap, grids = canvas.build_tileset([cv], mapio.ts_symbol(mod.TS), mod.TS)
    probs, _ = check.check(cv, grids[0], mod.STARTS, verbose=False)
    probs = [p for p in probs if 'Flamigo' not in str(p) and not (p[0] == 'warp unreachable' and p[3] == 0 and p[4] == 0)]
    sym = mapio.register_tileset(mod.TS)
    if preview_dir:
        canvas.preview(cv, grids[0], idmap, mod.TS, str(Path(preview_dir) / (mod.NAME + '.png')), markers=False)
    if write:
        mapio.write(mod.NAME, cv, grids[0], idmap, sym, connections=world.connections(mod.NAME))
    print('%-28s %5.1fs  problems: %s' % (mod.NAME, time.time() - t, probs if probs else 'none'))
    return probs


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    pdir = None
    if '--preview' in sys.argv:
        pdir = sys.argv[sys.argv.index('--preview') + 1]
        args = [a for a in args if a != pdir]
        Path(pdir).mkdir(parents=True, exist_ok=True)
    for m in (args or MODULES):
        run(m, pdir, write='--nowrite' not in sys.argv)
