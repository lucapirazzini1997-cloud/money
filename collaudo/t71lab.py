#!/usr/bin/env python3
"""Collaudo 0.71: esterno nuovo del laboratorio di Lido di Savio (0.9). Solo tasti, salvo le fixture dichiarate
(solo la posizione di partenza, scritta prima di un SALVA vero in gioco).
Uso: python3 t71lab.py ROM --parte=lab|crea70|vecchio70
  lab       da prog_imola.ss. Fixture: posizione a Lido (13,30), sul viale sotto il laboratorio. Su dalla porta (13,27):
            dentro 1.4; fuori dall'uscita (6,12): Lido (13,27); su dalla porta (14,27): dentro; fuori; cartello (10,28)
            da (10,29); SALVA e Continua dentro il laboratorio; fuori.
  crea70    sulla ROM 0.70: da prog_imola.ss, fixture posizione in 1.4 (6,10) e, in una seconda partita, a Lido (13,28);
            SALVA vero in entrambe.
  vecchio70 sulla 0.71 con i due salvataggi della 0.70: dal laboratorio fuori; da Lido (13,28) su nel laboratorio.
"""
import os, sys, json, shutil
ROM = os.path.abspath(sys.argv[1]); os.environ['ROMF'] = os.path.relpath(ROM, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'play'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'strumenti_rom'))
import leg, vai, pl
from leg import log, A, B, PLAY, PARTE
from drv import U, D
VBAM = bool(os.environ.get('VBAM'))
SUF = '_vbam' if VBAM else ''
OUT = os.path.join(PLAY, 't71lab_%s%s.json' % (PARTE, SUF))
LAB, LIDO = (1, 4), (0, 9)


def dove(g): return vai.stato(g)[:3]


def libero(g): return vai.ow(g) and g.e.ram(0x03000e41, 1)[0] == 0


def carica(sav):
    g = leg.ricarica(shutil.copy(sav, os.path.join(PLAY, 'leg_tmp.sav')))
    log('PROVA', PARTE, 'VBA-M' if VBAM else 'mGBA', os.path.basename(ROM), os.path.basename(sav), 'dal titolo:', vai.stato(g))
    return g


def oggetti(g): return [(xy, gf) for xy, gf in g.lobjs_gfx()]


def passo(g, k, es, nome):
    prima = dove(g); g.key(k, 3, 40); g.e.run(60)
    es[nome] = dict(prima=prima, dopo=dove(g)); log('  ', nome, es[nome])


def leggi(g, es, nome, mappa, da, xy, tasti_fine=B):
    """Va in `da`, guarda xy, preme A e legge i testi fino a quando il personaggio e' libero (B per chiudere)."""
    ok = vai.vai(g, mappa, *da, set(), accanto=False)
    vai.guarda(g, *xy); g.e.run(10); vecchio_testo = {leg.testo(g)}; g.key(A, 3, 60)
    vis, cb, scattata = [], set(), False
    for i in range(60):
        t = leg.testo(g); cb.add(hex(g.cb2()))
        if t and (not vis or vis[-1] != t): vis.append(t)
        if t and not scattata and t not in vecchio_testo: g.e.run(90); g.shot('t71lab_%s%s' % (nome, SUF)); scattata = True
        if i > 3 and libero(g):
            g.e.run(40)
            if libero(g): break
        g.key(tasti_fine, 3, 40)
    es[nome] = dict(arrivo=ok, testi=vis, cb2=sorted(cb), pos=dove(g)); log('  ', nome, es[nome])


def entra(g, es, nome, x):
    """Da (x,28) su verso la porta (x,27)."""
    es[nome + '_davanti'] = vai.vai(g, LIDO, x, 28, set(), accanto=False)
    for i in range(3):                       # il primo tasto puo' solo girare il personaggio
        passo(g, U, es, '%s_%d' % (nome, i)); g.e.run(60)
        if dove(g)[0] != LIDO: break
    es[nome + '_dentro'] = dove(g)


def esci(g, es, nome):
    es[nome + '_verso'] = vai.vai(g, LAB, 6, 11, set(), accanto=False)
    for i in range(3):                       # sull'uscita (6,12) si spinge ancora in basso
        passo(g, D, es, '%s_%d' % (nome, i)); g.e.run(60)
        if dove(g)[0] != LAB: break
    es[nome + '_fuori'] = dove(g)
    g.shot('t71lab_%s%s' % (nome, SUF))


def lab():
    sav = os.path.join(PLAY, 't71lab_lab.sav')
    if not VBAM:
        g = leg.g_da('prog_imola.ss'); leg.fixture_posizione(g, LIDO, 13, 30)
        leg.salva(g); g.e.close(); shutil.copy(g.sav, sav)
    g = carica(sav); es = {'partenza': dove(g)}
    g.shot('t71lab_facciata' + SUF)
    entra(g, es, 'porta13', 13)
    esci(g, es, 'uscita1')
    entra(g, es, 'porta14', 14)
    esci(g, es, 'uscita2')
    leggi(g, es, 'cartello', LIDO, (10, 29), (10, 28))
    entra(g, es, 'porta_salva', 13)
    es['dentro_salva'] = vai.vai(g, LAB, 6, 10, set(), accanto=False)
    leg.salva(g); g.e.close()
    g = leg.ricarica(g.sav); es['continua'] = dove(g); log('   continua', es['continua'])
    esci(g, es, 'uscita3')
    g.close(); return es


def crea70():
    es = {}
    for nome, k, x, y in [('crea70_lab', LAB, 6, 10), ('crea70_lido', LIDO, 13, 28)]:
        sav = os.path.join(PLAY, 't71lab_%s.sav' % nome)
        g = leg.g_da('prog_imola.ss'); leg.fixture_posizione(g, k, x, y)
        leg.salva(g); g.e.close(); shutil.copy(g.sav, sav)
        g = carica(sav); es[nome] = dove(g); g.close()
    log('  ', es); return es


def vecchio70():
    es = {}
    g = carica(os.path.join(PLAY, 't71lab_crea70_lab.sav')); g.e.run(60); es['lab_titolo'] = dove(g)
    esci(g, es, 'v_uscita'); g.close()
    g = carica(os.path.join(PLAY, 't71lab_crea70_lido.sav')); g.e.run(60); es['lido_titolo'] = dove(g)
    g.shot('t71lab_vecchio_lido' + SUF)
    entra(g, es, 'v_porta', 13)
    log('  ', es); g.close(); return es


if __name__ == '__main__':
    r = dict(lab=lab, crea70=crea70, vecchio70=vecchio70)[PARTE]()
    json.dump(r, open(OUT, 'w'), indent=1, ensure_ascii=False, default=str)
    log('FINE', PARTE)
