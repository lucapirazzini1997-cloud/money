#!/usr/bin/env python3
"""Collaudo 0.69: barriere (requisito, messaggio, ritorno) e testi riscritti. Solo tasti, salvo le fixture dichiarate
(solo la posizione di partenza, scritta prima di un SALVA vero).
Uso: python3 t69.py ROM --parte=lido|cesena|guide
  lido    da q8_end.ss (0 medaglie, starter preso). Fixture: posizione a Lido di Savio (20,9). Su fino a (20,7):
          barriera verso Ravenna (serve la 5a medaglia): testo, si torna indietro; poi si cammina via (ritorno).
  cesena  da s_ce3.ss (1 medaglia). Fixture: posizione a Cesena (46,47). Giu' a (46,50): barriera del Fumaiolo
          (7a medaglia): testo; via verso nord. Poi a piedi sulla strada per Rimini (34.43): giu' da (23,53) a
          (23,54): ALDO, barriera della 2a medaglia: testo, si torna a (23,50); via. (Seconda partita dallo stesso
          savestate con la fixture di posizione in 34.43 (23,51): a piedi il pilota si ferma nel casello 35.89.)
  guide   da t59_ravenna.ss (5 medaglie; gpre.ss parte in lotta e non si puo' salvare). Fixture: posizione a Forli' (39,53): si parla alla guida (39,51) per Ridracoli
          (7a medaglia): testo riscritto. Poi fixture posizione a Faenza (2,31): VIGILE (2,29) del ponte per Imola.
"""
import os, sys, json, shutil
ROM = os.path.abspath(sys.argv[1]); os.environ['ROMF'] = os.path.relpath(ROM, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'play'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'strumenti_rom'))
import leg, vai, pl
from leg import log, A, B, PLAY, PARTE
from drv import U, D
VBAM = bool(os.environ.get('VBAM'))
OUT = os.path.join(PLAY, 't69_%s%s.json' % (PARTE, '_vbam' if VBAM else ''))
AB = {'taglio', 'spacca', 'forza', 'surf'}


def dove(g): return vai.stato(g)[:3]


def libero(g): return vai.ow(g) and g.e.ram(0x03000e41, 1)[0] == 0


def apri(stato, mappa, x, y, nome=None):
    sav = os.path.join(PLAY, 't69_%s.sav' % (nome or PARTE))
    if not VBAM:
        g = leg.g_da(stato); leg.fixture_posizione(g, mappa, x, y)
        leg.salva(g); g.e.close(); shutil.copy(g.sav, sav)
    g = leg.ricarica(shutil.copy(sav, os.path.join(PLAY, 'leg_tmp.sav')))
    log('PROVA', PARTE, 'VBA-M' if VBAM else 'mGBA', os.path.basename(ROM), os.path.basename(sav))
    log('  dal titolo:', vai.stato(g), 'medaglie', ''.join(str(pl.flag(g.e, f)) for f in range(0x867, 0x86f)))
    return g


def testi_fino_a_libero(g, n=60):
    vis = []
    for i in range(n):
        t = leg.testo(g)
        if t and (not vis or vis[-1] != t): vis.append(t)
        if i > 2 and libero(g):
            g.e.run(40)
            if libero(g): break
        g.key(B, 3, 40)
    return vis


def barriera(g, es, nome, mappa, da, verso, via):
    """Si va in `da`, si preme `verso` (un passo nella barriera), si leggono i testi; poi si va in `via`."""
    ok = vai.vai(g, mappa, *da, AB, accanto=False)
    g.key(verso, 3, 20); g.key(verso, 3, 20)
    vis = testi_fino_a_libero(g)
    dopo = dove(g)
    rit = vai.vai(g, mappa, *via, AB, accanto=False)
    es[nome] = dict(arrivo=ok, testi=vis, dopo=dopo, ritorno=rit, pos_ritorno=dove(g)); log('  ', nome, es[nome])


def parla(g, es, nome, mappa, da, xy):
    ok = vai.vai(g, mappa, *da, AB, accanto=False)
    vai.guarda(g, *xy); g.e.run(10); g.key(A, 3, 40)
    vis = []
    for i in range(60):
        t = leg.testo(g)
        if t and (not vis or vis[-1] != t): vis.append(t)
        if i > 2 and libero(g):
            g.e.run(40)
            if libero(g): break
        g.key(B if 'accompagni' in t else A, 3, 40)          # alla domanda della guida si risponde no
    es[nome] = dict(arrivo=ok, testi=vis, dopo=dove(g)); log('  ', nome, es[nome])


def lido():
    g = apri('q8_end.ss', (0, 9), 20, 9)
    es = {}
    barriera(g, es, 'ravenna', (0, 9), (20, 8), U, (20, 12))
    g.shot('t69_lido'); g.close(); return es


def cesena():
    g = apri('s_ce3.ss', (34, 17), 46, 47)
    es = {}
    barriera(g, es, 'fumaiolo', (34, 17), (46, 49), D, (46, 45))
    g.shot('t69_cesena'); g.close()
    g = apri('s_ce3.ss', (34, 43), 23, 51, nome='cesena_rimini')
    barriera(g, es, 'rimini', (34, 43), (23, 53), D, (23, 47))
    g.shot('t69_rimini'); g.close(); return es


def guide():
    g = apri('t59_ravenna.ss', (34, 68), 39, 53)
    es = {}
    parla(g, es, 'guida_ridracoli', (34, 68), (39, 52), (39, 51))
    g.shot('t69_guida'); g.close()
    g = apri('t59_ravenna.ss', (34, 85), 2, 31, nome='guide_faenza')
    parla(g, es, 'vigile_faenza', (34, 85), (2, 30), (2, 29))
    g.shot('t69_vigile'); g.close(); return es


if __name__ == '__main__':
    r = dict(lido=lido, cesena=cesena, guide=guide)[PARTE]()
    json.dump(r, open(OUT, 'w'), indent=1, ensure_ascii=False, default=str)
    log('FINE', PARTE)
