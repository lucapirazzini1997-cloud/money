#!/usr/bin/env python3
"""Collaudo 0.72: Lido di Savio nuova, casa di ALDO, chiesa aperta (24.75). Solo tasti, salvo le fixture dichiarate
(solo la posizione di partenza, scritta prima di un SALVA vero in gioco).
Uso: python3 t72.py ROM --parte=lido|crea71|vecchio71
  lido      da prog_imola.ss. Fixture: posizione a Lido (19,12) sul Viale Romagna. Cartelli (viale, BAGNO LIDO) e porte
            con il nome (PURO & BIO, PIANETA PIADA); casa di ALDO: appunti, scale, diario, uscita nuova (6,10); caselli
            PINETA e COSTIERO andata e ritorno; chiesa: parroco (MAREAROMA una volta), quadro; SALVA e Continua in chiesa;
            fuori.
  crea71    sulla ROM 0.71: da prog_imola.ss, fixture posizione in 34.40 (9,7), 34.41 (3,7), Lido (8,39); SALVA vero.
  vecchio71 sulla 0.72 con i tre salvataggi della 0.71: fuori dalla casa di ALDO dai due piani; in chiesa da Lido.
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
OUT = os.path.join(PLAY, 't72_%s%s.json' % (PARTE, SUF))
LIDO, PT, CAM, CHIESA = (0, 9), (34, 40), (34, 41), (24, 75)
PINETA, COSTA = (35, 81), (35, 83)
FLAG, MAREAROMA = 0x3e, 0xdc


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
        if t and not scattata and t not in vecchio_testo: g.e.run(90); g.shot('t72_%s%s' % (nome, SUF)); scattata = True
        if i > 3 and libero(g):
            g.e.run(40)
            if libero(g): break
        g.key(tasti_fine, 3, 40)
    es[nome] = dict(arrivo=ok, testi=vis, cb2=sorted(cb), pos=dove(g)); log('  ', nome, es[nome])


def premi(g, es, nome, k, da_mappa, n=4):
    """Preme k finche' la mappa cambia (il primo tasto puo' solo girare il personaggio)."""
    for i in range(n):
        passo(g, k, es, '%s_%d' % (nome, i)); g.e.run(60)
        if dove(g)[0] != da_mappa: break
    es[nome] = dove(g)


def borsa(g): return __import__('drv').bag(g.e).get(('items', MAREAROMA), 0)


def flag(g): return __import__('drv').flag(g.e, FLAG)


def lido():
    sav = os.path.join(PLAY, 't72_lido.sav')
    if not VBAM:
        g = leg.g_da('prog_imola.ss'); leg.fixture_posizione(g, LIDO, 19, 12)
        leg.salva(g); g.e.close(); shutil.copy(g.sav, sav)
    g = carica(sav); es = {'partenza': dove(g)}
    g.shot('t72_viale' + SUF)
    leggi(g, es, 'viale', LIDO, (18, 10), (17, 10))
    leggi(g, es, 'puro_bio', LIDO, (16, 36), (16, 35))
    leggi(g, es, 'piadina', LIDO, (33, 36), (33, 35))
    leggi(g, es, 'bagno_lido', LIDO, (44, 22), (43, 22))
    # casa di ALDO
    es['aldo_davanti'] = vai.vai(g, LIDO, 25, 16, set(), accanto=False)
    premi(g, es, 'aldo_dentro', U, LIDO); g.shot('t72_aldo_pt' + SUF)
    leggi(g, es, 'appunti', PT, (6, 2), (6, 1))
    es['aldo_su'] = vai.vai(g, CAM, 2, 2, set(), accanto=False); g.e.run(60); es['aldo_camera'] = dove(g)
    g.shot('t72_aldo_camera' + SUF)
    leggi(g, es, 'diario', CAM, (11, 2), (11, 1))
    es['aldo_giu'] = vai.vai(g, PT, 2, 2, set(), accanto=False)
    es['aldo_zerbino'] = vai.vai(g, PT, 6, 9, set(), accanto=False)
    premi(g, es, 'aldo_fuori', D, PT)
    # caselli
    es['pineta_davanti'] = vai.vai(g, LIDO, 19, 42, set(), accanto=False)
    premi(g, es, 'pineta_dentro', D, LIDO)
    premi(g, es, 'pineta_ritorno', U, PINETA, n=6)
    es['costa_davanti'] = vai.vai(g, LIDO, 47, 42, set(), accanto=False)
    premi(g, es, 'costa_dentro', D, LIDO)
    premi(g, es, 'costa_ritorno', U, COSTA, n=6)
    # chiesa
    es['chiesa_davanti'] = vai.vai(g, LIDO, 8, 39, set(), accanto=False)
    premi(g, es, 'chiesa_dentro', U, LIDO); g.shot('t72_chiesa' + SUF)
    es['borsa_prima'], es['flag_prima'] = borsa(g), flag(g)
    leggi(g, es, 'parroco', CHIESA, (8, 4), (8, 3))
    es['borsa_dopo'], es['flag_dopo'] = borsa(g), flag(g)
    leggi(g, es, 'parroco_2', CHIESA, (8, 4), (8, 3))
    es['borsa_dopo2'] = borsa(g)
    leggi(g, es, 'quadro', CHIESA, (2, 2), (2, 1))
    es['in_chiesa'] = vai.vai(g, CHIESA, 7, 12, set(), accanto=False)
    leg.salva(g); g.e.close()
    g = leg.ricarica(g.sav); es['continua'] = dove(g); es['borsa_continua'] = borsa(g); log('   continua', es['continua'])
    es['chiesa_uscita'] = vai.vai(g, CHIESA, 7, 16, set(), accanto=False)
    premi(g, es, 'chiesa_fuori', D, CHIESA); g.e.run(60); es['chiesa_fuori_pos'] = dove(g)
    g.shot('t72_fuori_chiesa' + SUF)
    g.close(); return es


def crea71():
    es = {}
    for nome, k, x, y in [('crea71_pt', PT, 9, 7), ('crea71_cam', CAM, 3, 7), ('crea71_lido', LIDO, 8, 39)]:
        sav = os.path.join(PLAY, 't72_%s.sav' % nome)
        g = leg.g_da('prog_imola.ss'); leg.fixture_posizione(g, k, x, y)
        leg.salva(g); g.e.close(); shutil.copy(g.sav, sav)
        g = carica(sav); es[nome] = dove(g); g.close()
    log('  ', es); return es


def vecchio71():
    es = {}
    g = carica(os.path.join(PLAY, 't72_crea71_pt.sav')); g.e.run(60); es['pt_titolo'] = dove(g)
    g.shot('t72_vecchio_pt' + SUF)
    es['pt_zerbino'] = vai.vai(g, PT, 7, 9, set(), accanto=False)
    premi(g, es, 'pt_fuori', D, PT); g.close()
    g = carica(os.path.join(PLAY, 't72_crea71_cam.sav')); g.e.run(60); es['cam_titolo'] = dove(g)
    es['cam_giu'] = vai.vai(g, PT, 2, 2, set(), accanto=False); es['cam_pt'] = dove(g); g.close()
    g = carica(os.path.join(PLAY, 't72_crea71_lido.sav')); g.e.run(60); es['lido_titolo'] = dove(g)
    g.shot('t72_vecchio_lido' + SUF)
    premi(g, es, 'lido_chiesa', U, LIDO)
    log('  ', es); g.close(); return es


if __name__ == '__main__':
    r = dict(lido=lido, crea71=crea71, vecchio71=vecchio71)[PARTE]()
    json.dump(r, open(OUT, 'w'), indent=1, ensure_ascii=False, default=str)
    log('FINE', PARTE)
