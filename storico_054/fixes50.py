"""0.50 - blocchi del Lido: primo Pokemon obbligatorio su tutte le uscite, strada nord (Pianura/Ravenna) chiusa fino alla 5a medaglia."""
from gates48 import *
import gates48 as G

STARTER = 0x20        # flag "ho il primo Pokemon"
BADGE5 = 0x86b        # 5a medaglia


def _back(name, g, n, x, y, checks):
    """checks: lista (flag, testo) in ordine: se la flag NON e' attiva mostra il testo e riporta il giocatore in (x,y)."""
    s = Script(name).emit(b'\x69')
    for i, (flag, text) in enumerate(checks):
        s.flag(flag, 'ok%d' % i, present=True)
        s.msg(text).warp(g, n, x, y)
        s.label('ok%d' % i)
    s.emit(b'\x6b\x02')
    return s.save()


def lido_guards(cvs, houses):
    cv = cvs[(0, 9)]
    out = {}
    txt1 = "Un momento! Non puoi lasciare il Lido\nsenza un Pokémon. Passa dal laboratorio!"
    txt2 = "Il passaggio verso Ravenna è chiuso.\nServe la quinta medaglia per passare."
    for tid, cols in (('T3', range(18, 22)), ('T5', range(46, 50))):
        gS = [h for h in houses if h[0] == tid][0][4]
        y = gS['y0'] - 1
        for x in cols:
            assert not any((c['x'], c['y']) == (x, y) for c in cv.bcoords), (x, y)
            p = _back('Guardia Lido %s %d' % (tid, x), 0, 9, x, y - 2, [(STARTER, txt1)])
            cv.bcoords.append(dict(x=x, y=y, elev=0, var=0x400e, val=0, script=p))
        out[tid] = (list(cols), y)
    for x in (19, 20):
        y = 7
        assert not any((c['x'], c['y']) == (x, y) for c in cv.bcoords), (x, y)
        p = _back('Guardia nord %d' % x, 0, 9, x, y + 2, [(STARTER, txt1), (BADGE5, txt2)])
        cv.bcoords.append(dict(x=x, y=y, elev=0, var=0x400e, val=0, script=p))
    out['nord'] = ([19, 20], 7)
    return out
