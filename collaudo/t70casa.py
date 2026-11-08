#!/usr/bin/env python3
"""Collaudo 0.70: interno nuovo della casa del protagonista (1.0 pianterreno, 1.1 camera). Solo tasti, salvo le
fixture dichiarate (solo la posizione di partenza, scritta prima di un SALVA vero in gioco).
Uso: python3 t70casa.py ROM --parte=casa|crea69|vecchio69
  (Le scale si prendono andando in camera (1,2) o al pianterreno (3,3): il pilota passa dalle scale.)
  casa      da prog_imola.ss. Fixture: posizione a Lido di Savio (8,17) davanti alla porta (8,16). Su: dentro;
            mamma (11,3); TV (3,4); scale (3,2) -> camera; PC (8,1); TV (4,1) e cartina (6,1) della camera;
            telo da mare; scale (1,1) -> giu'; SALVA e Continua dentro casa; fuori dalla porta.
  crea69    sulla ROM 0.69: da prog_imola.ss, fixture posizione in 1.0 (9,8) e, in una seconda partita, in 1.1 (3,6);
            SALVA vero in entrambe.
  vecchio69 sulla 0.70 con i due salvataggi della 0.69: Continua; si guarda la stanza; in camera al PC e giu' dalle
            scale; al pianterreno su in camera e di nuovo giu' (la mamma torna al suo posto nuovo) e fuori.
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
OUT = os.path.join(PLAY, 't70casa_%s%s.json' % (PARTE, SUF))
PT, CAM, LIDO = (1, 0), (1, 1), (0, 9)
MAMMA = 215


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
        if t and not scattata and t not in vecchio_testo: g.e.run(90); g.shot('t70casa_%s%s' % (nome, SUF)); scattata = True
        if i > 3 and libero(g):
            g.e.run(40)
            if libero(g): break
        g.key(tasti_fine, 3, 40)
    es[nome] = dict(arrivo=ok, testi=vis, cb2=sorted(cb), pos=dove(g)); log('  ', nome, es[nome])


def casa():
    sav = os.path.join(PLAY, 't70casa_casa.sav')
    if not VBAM:
        g = leg.g_da('prog_imola.ss'); leg.fixture_posizione(g, LIDO, 8, 17)
        leg.salva(g); g.e.close(); shutil.copy(g.sav, sav)
    g = carica(sav); es = {}
    passo(g, U, es, 'porta'); es['oggetti_pt'] = oggetti(g)
    g.shot('t70casa_pianterreno' + SUF)
    leggi(g, es, 'mamma', PT, (11, 4), (11, 3), tasti_fine=A)
    leggi(g, es, 'tv', PT, (2, 4), (3, 4))
    es['su'] = vai.vai(g, CAM, 1, 2, set(), accanto=False); g.e.run(80); es['camera'] = dove(g)
    g.shot('t70casa_camera' + SUF)
    leggi(g, es, 'pc', CAM, (8, 2), (8, 1))
    leggi(g, es, 'tv_camera', CAM, (4, 2), (4, 1))
    leggi(g, es, 'cartina', CAM, (6, 2), (6, 1))
    es['telo'] = vai.vai(g, CAM, 2, 4, set(), accanto=False); es['sul_telo'] = dove(g)
    es['giu'] = vai.vai(g, PT, 3, 3, set(), accanto=False); g.e.run(80); es['di_nuovo_giu'] = dove(g)
    leg.salva(g); g.e.close()
    g = leg.ricarica(g.sav); es['continua'] = dict(pos=dove(g), oggetti=oggetti(g)); log('   continua', es['continua'])
    es['verso_porta'] = vai.vai(g, PT, 9, 9, set(), accanto=False)
    passo(g, D, es, 'uscita'); g.e.run(60); es['fuori'] = dove(g)
    g.close(); return es


def crea69():
    es = {}
    for nome, k, x, y in [('crea69_pt', PT, 9, 8), ('crea69_camera', CAM, 3, 6)]:
        sav = os.path.join(PLAY, 't70casa_%s.sav' % nome)
        g = leg.g_da('prog_imola.ss'); leg.fixture_posizione(g, k, x, y)
        leg.salva(g); g.e.close(); shutil.copy(g.sav, sav)
        g = carica(sav); es[nome] = dict(pos=dove(g), oggetti=oggetti(g)); g.close()
    log('  ', es); return es


def vecchio69():
    es = {}
    g = carica(os.path.join(PLAY, 't70casa_crea69_pt.sav')); g.e.run(60)
    es['pt_titolo'] = dict(pos=dove(g), oggetti=oggetti(g)); g.shot('t70casa_vecchio_pt' + SUF)
    es['pt_su'] = vai.vai(g, CAM, 1, 2, set(), accanto=False); g.e.run(80); es['pt_camera'] = dove(g)
    es['pt_giu'] = vai.vai(g, PT, 3, 3, set(), accanto=False); g.e.run(80)
    es['pt_di_nuovo'] = dict(pos=dove(g), oggetti=oggetti(g))
    es['pt_porta'] = vai.vai(g, PT, 9, 9, set(), accanto=False)
    passo(g, D, es, 'pt_uscita'); g.close()
    g = carica(os.path.join(PLAY, 't70casa_crea69_camera.sav')); g.e.run(60)
    es['cam_titolo'] = dict(pos=dove(g)); g.shot('t70casa_vecchio_camera' + SUF)
    leggi(g, es, 'cam_pc', CAM, (8, 2), (8, 1))
    es['cam_giu'] = vai.vai(g, PT, 3, 3, set(), accanto=False); g.e.run(80); es['cam_pt'] = dove(g)
    log('  ', es); g.close(); return es


if __name__ == '__main__':
    r = dict(casa=casa, crea69=crea69, vecchio69=vecchio69)[PARTE]()
    json.dump(r, open(OUT, 'w'), indent=1, ensure_ascii=False, default=str)
    log('FINE', PARTE)
