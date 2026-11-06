#!/usr/bin/env python3
"""Collaudo 0.66: il nuovo FUMAIOLO (Sentiero 35.10 e interno 35.12-35.18). Solo tasti, salvo le fixture dichiarate.
Uso: python3 t66.py ROM --parte=aldo|sentiero|santuario|ridracoli|crea65|vecchio65
  aldo       da prog_imola.ss. Fixture: 7a medaglia, posizione a Cesena. Ingresso: ALDO parla e la lotta parte
             all'arrivo (la squadra di prova la perde: si registra solo la partenza).
  sentiero   da prog_imola.ss (6 medaglie, Blaziken 50, Breloom 43). Fixture: 7a medaglia (0x86D), ALDO gia' affrontato (0x496), FORZA e SURF a
             Breloom, posizione a Cesena (34.17) sopra gli eventi che portano al Sentiero. Ingresso -> arrivo
             (19,97); bacheca, cartello, guide; cartello del rifugio; rifugio
             e ritorno; EREMO: escursionista, missione di FORZA, masso spinto, grotta -> 35.12 (guida, niente masso
             del vecchio rompicapo) -> scala -> 35.13 (cartello, guida); ritorno al Sentiero; cima: stele del
             TEVERE e strumento. SALVA (serve a "santuario").
  santuario  dal salvataggio di "sentiero". Fixture: 5 MASTER BALL; squadra curata prima delle lotte. 35.13 ->
             Passo (frane: si torna indietro) -> Nodo del Sale (recluta, conduttore) -> Nodo dell'Argilla -> Sala di
             BASSI (porta profonda prima e dopo, BASSI, soccorso) -> Cuore (arrivo 5,5, guida, GROUDON con MASTER
             BALL) -> uscita del Cuore (si torna alla porta e si scende) -> guida delle Sorgenti (al Passo) -> Passo a
             piedi fino a BAGNO DI ROMAGNA.
  ridracoli  da prog_imola.ss. Fixture: 7a medaglia, ALDO gia' affrontato, posizione in 35.50 vicino alla guida del sentiero orientale.
             La guida porta al Sentiero: arrivo (18,96).
  crea65     sulla ROM 0.65: da prog_imola.ss, fixture posizione in 35.13 (16,20) (grotta di oggi), SALVA vero.
  vecchio65  sulla 0.66 con t66_crea65.sav: Continua; una volta sola si riparte da (20,35) di 35.13; SALVA e
             Continua: si resta.
"""
import os, sys, json, shutil, struct
ROM = os.path.abspath(sys.argv[1]); os.environ['ROMF'] = os.path.relpath(ROM, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'play'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'strumenti_rom'))
import leg, vai, pl, romlib
from leg import log, A, B, PLAY, PARTE
VBAM = bool(os.environ.get('VBAM'))
OUT = os.path.join(PLAY, 't66_%s%s.json' % (PARTE, '_vbam' if VBAM else ''))
_R = romlib.Rom(ROM)
SENT = (35, 10)
AB = {'taglio', 'spacca', 'forza', 'surf'}
FORZA, SURF = 70, 57


def numeri():
    """Variabile dei vecchi salvataggi e flag del masso di 35.12, letti dalla ROM 0.66 (script d'ingresso di 35.12)."""
    m = _R.map(35, 12); ms = dict(_R.map_scripts(m)); d = _R.data; p = ms.get(3)
    if p is None or d[p] != 0x16: return None, None
    return struct.unpack_from('<H', d, p + 1)[0], struct.unpack_from('<H', d, p + 6)[0]


NUOVA, F_MASSO = numeri() if _R.map(*SENT)['height'] == 100 else (None, None)
STORIA = {'aldo': 0x496, 'nodo_sale': 0x4c7, 'nodo_argilla': 0x4c8, 'bassi': 0x4c9, 'groudon_fatto': 0x4cb,
          'groudon_ogg': 0x4cc, 'strumento_tevere': 0x140}


def flags(g): return {k: pl.flag(g.e, f) for k, f in STORIA.items()}


def oggetti(g): return sorted(g.lobjs_gfx())


def dove(g): return vai.stato(g)[:3]


def apri(start, fix, nome=None):
    sav = os.path.join(PLAY, 't66_%s.sav' % (nome or PARTE))
    if not VBAM:
        if start.endswith('.ss'): g = leg.g_da(start)
        else: g = leg.ricarica(shutil.copy(os.path.join(PLAY, start), os.path.join(PLAY, 'leg_tmp.sav')))
        for f in fix: f(g)
        leg.salva(g); g.e.close(); shutil.copy(g.sav, sav)
    g = leg.ricarica(shutil.copy(sav, os.path.join(PLAY, 'leg_tmp.sav')))
    log('PROVA', PARTE, 'VBA-M' if VBAM else 'mGBA', os.path.basename(ROM))
    log('  dal titolo:', vai.stato(g), 'medaglie', [pl.flag(g.e, f) for f in range(0x867, 0x86f)], flags(g))
    return g


def chiudi(g, n=60):
    vis = []
    for i in range(n):
        t = leg.testo(g)
        if t and (not vis or vis[-1] != t): vis.append(t)
        if vai.ow(g) and g.e.ram(0x03000e41, 1)[0] == 0:
            g.e.run(30)
            if vai.ow(g) and g.e.ram(0x03000e41, 1)[0] == 0: break
        g.key(A if 'Smettere di imparare' in t else B, 3, 40)
    return vis


def lotta(g):
    info = []
    for _ in range(8):
        info += leg.ko(g)
        if vai.ow(g): break
        for _ in range(20):
            t = leg.testo(g)
            if g.cb2() == pl.BATCB and g.e.r('r32', 0x3005d60) == pl.ACT: break
            if vai.ow(g): break
            g.key(B if 'Natura' in t else A, 3, 40)
    return info


def cura(g):
    """FIXTURE DICHIARATA: squadra curata (PS al massimo, niente stato) prima di una lotta. La squadra di prova ha
    solo due Pokemon: serve a non perdere per sfinimento, non a vincere una lotta che si perderebbe da curati."""
    for k in range(len(g.party())):
        a = 0x20244ec + k * 100
        g.e.w('w32', a + 80, 0); g.e.w('w16', a + 86, g.e.r('r16', a + 88))
    log('   FIXTURE: squadra curata', g.party())


def testi_e_lotta(g, n=80, risposta=A):
    """Dopo che uno script e' partito: testi (A o la risposta data) finche' si torna liberi o parte una lotta;
    la lotta si combatte. -> (testi, squadra avversaria)."""
    vis, info = [], []
    for i in range(n):
        t = leg.testo(g)
        if t and (not vis or vis[-1] != t): vis.append(t)
        if not vai.ow(g) and g.cb2() == pl.BATCB:
            info = lotta(g); vis += chiudi(g, 40); break
        if vai.ow(g) and g.e.ram(0x03000e41, 1)[0] == 0 and i > 3:
            g.e.run(30)
            if vai.ow(g) and g.e.ram(0x03000e41, 1)[0] == 0: break
        g.key(risposta if ('?' in t) else A, 3, 40)
    return vis, sorted({(x[3], x[4]) for x in info})


def premi_a(g, x, y, risposta=B):
    vai.guarda(g, x, y); g.e.run(10)
    for _ in range(2):
        g.key(A, 3, 30)
        for _ in range(20):
            if g.e.ram(0x03000e41, 1)[0] or not vai.ow(g): break
            g.e.run(5)
        if g.e.ram(0x03000e41, 1)[0] or not vai.ow(g): break
    return testi_e_lotta(g, risposta=risposta)


def va(g, es, nome, mappa, x, y, ab=AB, accanto=True):
    ok = False
    for _ in range(4):
        ok = vai.vai(g, mappa, x, y, ab, accanto=accanto)
        if ok or vai.ow(g): break
        lotta(g); chiudi(g, 20)
    es[nome] = dict(ok=ok, pos=dove(g)); log('  ', nome, es[nome]); return ok


def parla(g, es, nome, mappa, x, y, risposta=B, cur=False, da=None):
    ok = vai.vai(g, mappa, *(da or (x, y)), AB, accanto=da is None)
    if cur: cura(g)
    vis, sq = premi_a(g, x, y, risposta) if ok else ([], [])
    es[nome] = dict(arrivo=ok, testi=vis, lotta=sq, pos=dove(g), **flags(g)); log('  ', nome, es[nome]); return vis


def aldo():
    """Ingresso con la 7a medaglia: ALDO parla e la lotta parte da sola (script di mappa di oggi, non toccato).
    La squadra di prova (2 Pokemon) contro i 5 di ALDO perde: si registra solo che la lotta parte all'arrivo."""
    g = apri('prog_imola.ss', [lambda g: leg.fixture_flag(g, 0x86d, 1), lambda g: leg.fixture_posizione(g, (34, 17), 46, 48)])
    es = {}
    for _ in range(2): g.step('D'); g.e.run(20)
    g.e.run(200); es['arrivo'] = dict(pos=dove(g), oggetti=oggetti(g))
    vis = []
    for i in range(60):
        t = leg.testo(g)
        if t and (not vis or vis[-1] != t): vis.append(t)
        if g.cb2() == pl.BATCB and g.e.r('r32', 0x3005d60) == pl.ACT: break
        g.key(A, 3, 40)
    es['lotta_partita'] = dict(testi=vis, in_lotta=g.cb2() == pl.BATCB); log('  ALDO', es)
    g.shot('t66_aldo'); g.close(); return es


def sentiero():
    g = apri('prog_imola.ss', [lambda g: leg.fixture_flag(g, 0x86d, 1),
                               lambda g: leg.fixture_flag(g, 0x496, 1),       # ALDO gia' affrontato (vedi parte aldo)
                               lambda g: leg.fixture_mossa(g, 1, 2, FORZA, 15),
                               lambda g: leg.fixture_mossa(g, 1, 3, SURF, 15),
                               lambda g: leg.fixture_posizione(g, (34, 17), 46, 48)])
    es = dict(numeri=dict(nuova=hex(NUOVA or 0), masso=hex(F_MASSO or 0)))
    # ingresso dal sud di Cesena: due passi verso sud sugli eventi (46,50)
    cura(g)
    for _ in range(2): g.step('D'); g.e.run(20)
    g.e.run(200)
    es['arrivo'] = dict(pos=dove(g)); log('  arrivo', es['arrivo'])
    g.e.run(60); es['oggetti_arrivo'] = oggetti(g)       # ALDO (oggetto 4) tolto dallo script di mappa
    parla(g, es, 'bacheca', SENT, 17, 98)
    parla(g, es, 'cartello_ingresso', SENT, 21, 98)
    parla(g, es, 'guida', SENT, 21, 96)
    parla(g, es, 'guida_ridracoli', SENT, 17, 96)
    parla(g, es, 'cartello_rifugio', SENT, 27, 59)
    va(g, es, 'rifugio', (35, 11), 12, 18, accanto=False)
    va(g, es, 'fuori_dal_rifugio', SENT, 33, 39, accanto=False)
    parla(g, es, 'escursionista_eremo', SENT, 9, 73)
    parla(g, es, 'missione_forza', SENT, 5, 73, risposta=A)
    es['massi_prima'] = [xy for xy, gf in g.lobjs_gfx() if gf == 87]
    va(g, es, 'grotta_eremo', (35, 12), 10, 29, accanto=False)
    es['oggetti_3512'] = oggetti(g)
    parla(g, es, 'guida_3512', (35, 12), 18, 27)
    va(g, es, 'sorgenti', (35, 13), 20, 36, accanto=False)
    parla(g, es, 'cartello_sorgenti', (35, 13), 23, 35, da=(22, 35))
    parla(g, es, 'guida_sorgenti', (35, 13), 21, 34, da=(20, 34))
    va(g, es, 'torna_eremo', (35, 12), 21, 23, accanto=False)
    va(g, es, 'torna_sentiero', SENT, 7, 71, accanto=False)
    es['massi_dopo'] = [xy for xy, gf in g.lobjs_gfx() if gf == 87]
    parla(g, es, 'stele', SENT, 10, 4)
    parla(g, es, 'strumento', SENT, 8, 2, risposta=A)
    leg.salva(g); g.e.close(); shutil.copy(g.sav, os.path.join(PLAY, 't66_sentiero_fine%s.sav' % ('_vbam' if VBAM else '')))
    g = leg.ricarica(g.sav)
    es['ricarica'] = dict(pos=dove(g), var_nuova=g.var(NUOVA) if NUOVA else None, **flags(g)); g.e.run(120)
    es['ricarica_dopo_2s'] = dove(g)
    g.shot('t66_sentiero'); g.close(); return es


def combatti(g, es, nome, k, x, y, vittoria, risposta=B):
    """Lotta con un allenatore della storia. Prima uno stato di riserva: se la squadra di prova (2 Pokemon) perde,
    si torna allo stato di riserva e le flag della vittoria si alzano come FIXTURE DICHIARATA (non e' una prova
    della vittoria: serve a provare le stanze che vengono dopo)."""
    vai.vai(g, k, x, y, AB); cura(g); g.save('t66_riserva.ss')
    vis, sq = premi_a(g, x, y, risposta)
    vinta = all(pl.flag(g.e, f) for f in vittoria) and vai.stato(g)[0] == k
    es[nome] = dict(testi=vis, lotta=sq, vinta=vinta, pos=dove(g), **flags(g))
    if not vinta:
        g.e.load(pl.P + 't66_riserva.ss'); g.e.run(120)
        for f in vittoria: leg.fixture_flag(g, f, 1)
        es[nome]['fixture_dopo_sconfitta'] = [hex(f) for f in vittoria]; es[nome]['pos_dopo'] = dove(g)
    log('  ', nome, es[nome])


def frane(g, es, nome):
    """Dal Passo in basso (14,38) un passo sulla scala (14,37): prima di GROUDON il testo e si torna a (14,39)."""
    va(g, es, nome + '_partenza', (35, 18), 14, 38, accanto=False)
    g.step('U'); vis = []; pos = []
    for i in range(80):
        t = leg.testo(g) if g.e.ram(0x03000e41, 1)[0] else ''
        if t and (not vis or vis[-1] != t): vis.append(t)
        p = dove(g)
        if not pos or pos[-1] != p: pos.append(p)
        if t: g.key(A, 3, 30)
        else: g.e.run(15)
    es[nome] = dict(testi=vis, posizioni=pos, **flags(g)); log('  ', nome, es[nome])


def santuario():
    g = apri('t66_sentiero_fine.sav', [leg.fixture])
    es = dict(inizio=dict(pos=dove(g), **flags(g)))
    frane(g, es, 'frane_prima')
    # Nodo del Sale e Nodo dell'Argilla
    for nome, k, rec, con in (('sale', (35, 14), (16, 4), (16, 11)), ('argilla', (35, 15), (11, 12), (10, 10))):
        combatti(g, es, 'recluta_' + nome, k, *rec, [0x500 + (0x2e9 if nome == 'sale' else 0x2ea), 0x4c7 if nome == 'sale' else 0x4c8])
        parla(g, es, 'conduttore_' + nome, k, *con)
        parla(g, es, 'recluta_%s_dopo' % nome, k, *rec)
    # Sala di BASSI
    parla(g, es, 'soccorso', (35, 16), 14, 31, risposta=A)
    parla(g, es, 'porta_prima', (35, 16), 9, 3)
    combatti(g, es, 'bassi', (35, 16), 10, 5, [0x500 + 0x259, 0x4c9, 0x4ca])
    vai.vai(g, (35, 16), 9, 3, AB); vis, _ = premi_a(g, 9, 3); g.e.run(150)
    es['porta_dopo'] = dict(testi=vis, pos=dove(g), **flags(g)); log('  porta dopo', es['porta_dopo'])
    # Cuore
    parla(g, es, 'guida_cuore', (35, 17), 7, 22)
    vai.vai(g, (35, 17), 17, 26, AB, accanto=False); cura(g)
    vis, sq = [], []
    vai.guarda(g, 17, 25); g.key(A, 3, 60)
    for i in range(60):
        t = leg.testo(g)
        if t and (not vis or vis[-1] != t): vis.append(t)
        if not vai.ow(g) and g.cb2() == pl.BATCB: break
        g.key(A, 3, 40)
    n0 = len(g.party()); cattura = None
    if g.cb2() == pl.BATCB:
        leg.menu_lotta(g); g.throw(); vis += chiudi(g, 60)
        if len(g.party()) > n0: cattura = dict(specie=leg.specie_squadra(g)[-1], livello=g.party()[-1])
    es['groudon'] = dict(testi=vis, cattura=cattura, oggetti=oggetti(g), pos=dove(g), **flags(g)); log('  GROUDON', es['groudon'])
    # uscita del Cuore: si torna sulla porta profonda e si scende
    va(g, es, 'uscita_cuore', (35, 16), 8, 2, accanto=False)
    g.step('D'); g.e.run(20); es['sceso_dalla_porta'] = dove(g)
    # guida delle Sorgenti: al Passo
    vai.vai(g, (35, 13), 20, 34, AB, accanto=False); vis, _ = premi_a(g, 21, 34, risposta=A); g.e.run(150)
    es['guida_al_passo'] = dict(testi=vis, pos=dove(g)); log('  guida al passo', es['guida_al_passo'])
    frane(g, es, 'frane_dopo')
    parla(g, es, 'guida_passo', (35, 18), 17, 38)
    parla(g, es, 'escursionista_passo', (35, 18), 21, 9)
    parla(g, es, 'strumento_passo', (35, 18), 8, 20, risposta=A)
    va(g, es, 'bagno', (35, 19), 1, 17, accanto=True)
    leg.salva(g); g.e.close(); g = leg.ricarica(g.sav)
    es['ricarica'] = dict(pos=dove(g), **flags(g))
    g.shot('t66_santuario'); g.close(); return es


def ridracoli():
    g = apri('prog_imola.ss', [lambda g: leg.fixture_flag(g, 0x86d, 1), lambda g: leg.fixture_flag(g, 0x496, 1),
                               lambda g: leg.fixture_posizione(g, (35, 50), 31, 36)])
    es = {}
    vai.vai(g, (35, 50), 31, 34, AB); vis, _ = premi_a(g, 31, 34, risposta=A); g.e.run(200)
    es['guida'] = dict(testi=vis, pos=dove(g)); log('  guida', es['guida'])
    vis, sq = testi_e_lotta(g, 120); es['aldo'] = dict(testi=vis, lotta=sq, pos=dove(g))
    g.shot('t66_ridracoli'); g.close(); return es


def crea65():
    sav = os.path.join(PLAY, 't66_crea65.sav')
    g = leg.g_da('prog_imola.ss'); leg.fixture_flag(g, 0x86d, 1); leg.fixture_posizione(g, (35, 13), 16, 20)
    leg.salva(g); g.e.close(); shutil.copy(g.sav, sav)
    g = leg.ricarica(shutil.copy(sav, os.path.join(PLAY, 'leg_tmp.sav')))
    es = dict(pos_065=dove(g)); log('  crea65', es); g.shot('t66_crea65'); g.close(); return es


def vecchio(savname):
    log('PROVA', PARTE, 'VBA-M' if VBAM else 'mGBA', os.path.basename(ROM), savname)
    g = leg.ricarica(shutil.copy(os.path.join(PLAY, savname), os.path.join(PLAY, 'leg_tmp.sav')))
    es = dict(titolo=dove(g), var_nuova=g.var(NUOVA))
    g.e.run(240); chiudi(g, 5)
    es['dopo_4s'] = dict(pos=dove(g), var_nuova=g.var(NUOVA)); log('  ', es)
    va(g, es, 'cammina', (35, 13), 17, 34, accanto=False)
    leg.salva(g); g.e.close(); g = leg.ricarica(g.sav)
    es['ricarica'] = dict(pos=dove(g), var_nuova=g.var(NUOVA)); g.e.run(240)
    es['ricarica_dopo_4s'] = dove(g)
    va(g, es, 'verso_eremo', (35, 12), 10, 28, accanto=False)
    g.shot('t66_' + PARTE); g.close(); return es


if __name__ == '__main__':
    r = dict(aldo=aldo, sentiero=sentiero, santuario=santuario, ridracoli=ridracoli, crea65=crea65,
             vecchio65=lambda: vecchio('t66_crea65.sav'))[PARTE]()
    json.dump(r, open(OUT, 'w'), indent=1, ensure_ascii=False, default=str)
    log('FINE', PARTE)
