#!/usr/bin/env python3
"""Collaudo 0.68: ostacoli (TV della casa del protagonista, Poke Ball della Pineta del Savio). Solo tasti, salvo le
fixture dichiarate.
Uso: python3 t68.py ROM --parte=casa|pineta|crea67|vecchio67
  casa      da prog_imola.ss. Fixture: posizione a Lido di Savio (8,17) davanti alla porta di casa (8,16).
            Su: si entra in 1.0 sulla casella (9,9); Su: si deve salire a (9,8) (prima c'era la TV);
            si va alle scale (12,2) e si sale in camera; si torna giu' e si esce dalla porta.
  pineta    da prog_imola.ss. Fixture: posizione nella Pineta del Savio (19,5). A piedi senza abilita' fino alla
            Poke Ball (36,24) passando dalla siepe aperta (34,25); A: si raccoglie, la Ball sparisce, flag 0x2D.
  crea67    sulla ROM 0.67: da prog_imola.ss, fixture posizione nella casa 1.0 (9,9) e una seconda partita nella
            Pineta (33,25) accanto alla siepe; SALVA vero in entrambe.
  vecchio67 sulla 0.68 con i due salvataggi della 0.67: Continua; in casa Su (si deve salire a 9,8);
            nella Pineta Destra due volte (il primo tocco gira; si deve passare a 34,25) e si raccoglie la Ball.
"""
import os, sys, json, shutil
ROM = os.path.abspath(sys.argv[1]); os.environ['ROMF'] = os.path.relpath(ROM, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'play'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'strumenti_rom'))
import leg, vai, pl
from leg import log, A, B, PLAY, PARTE
from drv import U, D, R as DX
VBAM = bool(os.environ.get('VBAM'))
OUT = os.path.join(PLAY, 't68_%s%s.json' % (PARTE, '_vbam' if VBAM else ''))
CASA, LIDO, PINETA = (1, 0), (0, 9), (0, 16)
F_BALL = 0x2D


def dove(g): return vai.stato(g)[:3]


def libero(g): return vai.ow(g) and g.e.ram(0x03000e41, 1)[0] == 0


def apri(fix, nome=None):
    sav = os.path.join(PLAY, 't68_%s.sav' % (nome or PARTE))
    if not VBAM:
        g = leg.g_da('prog_imola.ss')
        for f in fix: f(g)
        leg.salva(g); g.e.close(); shutil.copy(g.sav, sav)
    return carica(sav)


def carica(sav):
    g = leg.ricarica(shutil.copy(sav, os.path.join(PLAY, 'leg_tmp.sav')))
    log('PROVA', PARTE, 'VBA-M' if VBAM else 'mGBA', os.path.basename(ROM), os.path.basename(sav))
    log('  dal titolo:', vai.stato(g), 'flag Ball', pl.flag(g.e, F_BALL))
    return g


def passo(g, k, es, nome):
    prima = dove(g); g.key(k, 3, 40); g.e.run(40)
    es[nome] = dict(prima=prima, dopo=dove(g)); log('  ', nome, es[nome])


def raccogli(g, es):
    vai.guarda(g, 36, 24); g.e.run(10); g.key(A, 3, 40)
    vis = []
    for _ in range(40):
        t = leg.testo(g)
        if t and (not vis or vis[-1] != t): vis.append(t)
        if libero(g):
            g.e.run(30)
            if libero(g): break
        g.key(B, 3, 40)
    es['ball'] = dict(testi=vis, flag=pl.flag(g.e, F_BALL), pos=dove(g),
                      ball_visibile=any(gf == 59 and (x, y) == (36, 24) for (x, y), gf in g.lobjs_gfx()))
    log('  ball', es['ball'])


def casa():
    g = apri([lambda g: leg.fixture_posizione(g, LIDO, 8, 17)])
    es = {}
    passo(g, U, es, 'porta')
    g.e.run(60); es['dentro'] = dove(g)
    passo(g, U, es, 'primo_passo')
    g.shot('t68_casa')
    es['scale'] = vai.vai(g, CASA, 12, 2, set(), accanto=False); g.e.run(80); es['camera'] = dove(g)
    es['giu'] = vai.vai(g, (1, 1), 10, 2, set(), accanto=False); g.e.run(80); es['di_nuovo_giu'] = dove(g)
    es['verso_porta'] = vai.vai(g, CASA, 9, 9, set(), accanto=False)
    passo(g, D, es, 'uscita'); g.e.run(60); es['fuori'] = dove(g)
    log('  ', es); g.close(); return es


def pineta():
    g = apri([lambda g: leg.fixture_posizione(g, PINETA, 19, 5)])
    es = {}
    es['arrivo'] = vai.vai(g, PINETA, 35, 24, set(), accanto=False); es['pos'] = dove(g)
    raccogli(g, es)
    g.shot('t68_pineta'); g.close(); return es


def crea67():
    es = {}
    for nome, k, x, y in [('crea67_casa', CASA, 9, 9), ('crea67_pineta', PINETA, 33, 25)]:
        sav = os.path.join(PLAY, 't68_%s.sav' % nome)
        g = leg.g_da('prog_imola.ss'); leg.fixture_posizione(g, k, x, y)
        leg.salva(g); g.e.close(); shutil.copy(g.sav, sav)
        g = carica(sav); es[nome] = dict(pos=dove(g), flag_ball=pl.flag(g.e, F_BALL)); g.close()
    log('  ', es); return es


def vecchio67():
    es = {}
    g = carica(os.path.join(PLAY, 't68_crea67_casa.sav')); g.e.run(60)
    es['casa_titolo'] = dove(g); g.shot('t68_vecchio67_casa_prima')
    passo(g, U, es, 'casa_su'); g.shot('t68_vecchio67_casa'); g.close()
    g = carica(os.path.join(PLAY, 't68_crea67_pineta.sav')); g.e.run(60)
    es['pineta_titolo'] = dove(g)
    passo(g, DX, es, 'pineta_gira')                  # il primo tocco gira il giocatore
    passo(g, DX, es, 'pineta_destra')
    es['arrivo'] = vai.vai(g, PINETA, 35, 24, set(), accanto=False)
    raccogli(g, es); g.shot('t68_vecchio67_pineta'); g.close(); return es


if __name__ == '__main__':
    r = dict(casa=casa, pineta=pineta, crea67=crea67, vecchio67=vecchio67)[PARTE]()
    json.dump(r, open(OUT, 'w'), indent=1, ensure_ascii=False, default=str)
    log('FINE', PARTE)
