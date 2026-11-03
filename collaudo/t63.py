#!/usr/bin/env python3
"""Collaudo 0.63: Cesena ovest, Ippodromo, rocce di Monte Spaccato. Solo tasti, salvo le fixture dichiarate.
Uso: python3 t63.py ROM --parte=prima|dopo|vecchio|riproduci|vecchio62 (riproduci: sulla ROM 0.62; vecchio62: sulla 0.63 col .sav fatto da riproduci)
  prima   da s_ce3.ss (Cesena, 1 medaglia: prima visita), SALVA e Continua. Nessuna fixture.
          Cesena -> casello -> Ippodromo -> Monte Spaccato; le rocce non si rompono; i corridoi d'erba sono
          chiusi; ritorno a Cesena; SALVA e Continua: flag 0x22 ancora a 0.
  dopo    da prog_imola.ss (6 medaglie). Fixture: posizione a Monte Spaccato (56,21); SPACCAROCCIA al Pokemon 0.
          Una roccia rotta ricompare rientrando; poi si rompe e si passa a 35.92 (flag 0x22 = 1); tornando,
          le rocce non ci sono; SALVA e Continua; si va a Cesena e si torna a Capocolle.
  vecchio da prog_imola.ss. Fixture: posizione a Capocolle (35.60, 38,17), flag 0x22 a 0 (salvataggio gia' oltre
          il vecchio casello). Verso est: le rocce non ci sono e si arriva a Cesena.
"""
import os, sys, json, shutil
ROM = os.path.abspath(sys.argv[1]); os.environ['ROMF'] = os.path.relpath(ROM, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'play'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import leg, vai, pl
from leg import log, A, B, PLAY, PARTE
from drv import L
APERTO = 0x22
ROCCE = [(14, 16), (14, 17), (14, 18)]
OUT = os.path.join(PLAY, 't63_%s%s.json' % (PARTE, '_vbam' if os.environ.get('VBAM') else ''))


def rocce(g):
    return sorted(xy for xy, gf in g.lobjs_gfx() if gf == 86 and xy in ROCCE) if vai.stato(g)[0] == (35, 101) else None


def spingi(g, dn, n=4):
    """Prova a camminare contro un ostacolo: posizione prima e dopo."""
    p0 = vai.stato(g)[:3]
    for _ in range(n): g.step(dn); g.e.run(10)
    return dict(prima=p0, dopo=vai.stato(g)[:3])


def apri(state, fix):
    """In mGBA: savestate, fixture, SALVA in gioco -> play/t63_<parte>.sav. In VBA-M (che non legge i savestate
    di mGBA) si riparte da quel .sav. In tutti e due i casi la prova comincia con Continua dal titolo."""
    sav = os.path.join(PLAY, 't63_%s.sav' % PARTE)
    if not os.environ.get('VBAM'):
        g = leg.g_da(state)
        for f in fix: f(g)
        leg.salva(g); g.e.close(); shutil.copy(g.sav, sav)
    g = leg.ricarica(shutil.copy(sav, os.path.join(PLAY, 'leg_tmp.sav')))
    log('  dal titolo:', vai.stato(g), 'medaglie', [pl.flag(g.e, f) for f in range(0x867, 0x86f)], 'flag 0x22', pl.flag(g.e, APERTO))
    return g


def tappa(g, es, nome, mappa, x, y, ab, accanto=True):
    ok = vai.vai(g, mappa, x, y, ab, accanto=accanto)
    es[nome] = dict(ok=ok, pos=vai.stato(g)[:3], rocce=rocce(g), flag_11_13=[pl.flag(g.e, f) for f in (0x11, 0x12, 0x13)]); log('  ', nome, es[nome]); return ok


def prima():
    g = apri('s_ce3.ss', []); es = dict(medaglie=[pl.flag(g.e, f) for f in range(0x867, 0x86f)])
    AB = {'taglio'}
    tappa(g, es, 'ippodromo', (34, 19), 19, 30, AB)                        # dal casello si entra dal cancello sud
    es['percorso_ippodromo'] = vai.stato(g)[0]
    tappa(g, es, 'monte_spaccato', (35, 101), 56, 21, AB)                 # dal cancello ovest
    tappa(g, es, 'davanti_rocce', (35, 101), 15, 17, AB, accanto=False)
    vai.guarda(g, 14, 17); g.key(A, 3, 60); es['roccia_testi'] = leg.chiudi_testi(g, 20)
    es['contro_roccia'] = spingi(g, 'L'); es['rocce_dopo'] = rocce(g)
    tappa(g, es, 'corridoio_nord', (35, 101), 13, 3, AB, accanto=False); es['contro_alberi_nord'] = spingi(g, 'L')
    tappa(g, es, 'corridoio_sud', (35, 101), 13, 36, AB, accanto=False); es['contro_alberi_sud'] = spingi(g, 'L')
    es['verso_35_92'] = vai.vai(g, (35, 92), 6, 4, AB)                    # deve fallire: nessun percorso
    tappa(g, es, 'ritorno_ippodromo', (34, 19), 8, 17, AB)
    tappa(g, es, 'ritorno_cesena', (34, 17), 6, 43, AB)
    leg.salva(g); g.e.close(); g = leg.ricarica(g.sav)
    es['ricarica'] = dict(pos=vai.stato(g)[:3], flag_22=pl.flag(g.e, APERTO), medaglia3=pl.flag(g.e, 0x869))
    tappa(g, es, 'di_nuovo_ippodromo', (34, 19), 19, 30, AB)
    g.shot('t63_prima'); g.close(); return es


def dopo():
    g = apri('prog_imola.ss', [lambda g: leg.fixture_posizione(g, (35, 101), 56, 21),
                               lambda g: leg.fixture_mossa(g, 0, 3, 0xf9, 15)])
    es = dict(flag_22_inizio=pl.flag(g.e, APERTO), rocce_inizio=rocce(g)); AB = {'taglio', 'spacca'}
    tappa(g, es, 'davanti_rocce', (35, 101), 15, 17, AB, accanto=False)
    vai.rompi(g, 'W'); leg.chiudi_testi(g, 10)
    es['dopo_rottura'] = dict(rocce=rocce(g), pos=vai.stato(g)[:3], flag_22=pl.flag(g.e, APERTO))
    tappa(g, es, 'esce_ippodromo', (34, 19), 8, 17, {'taglio'})
    tappa(g, es, 'rientra', (35, 101), 16, 17, {'taglio'}, accanto=False)   # la roccia rotta e' tornata
    tappa(g, es, 'passa', (35, 92), 6, 4, AB)
    es['flag_22_in_35_92'] = pl.flag(g.e, APERTO)
    tappa(g, es, 'torna_monte', (35, 101), 8, 17, {'taglio'})             # rocce nascoste
    tappa(g, es, 'accanto_rocce_ovest', (35, 101), 12, 17, {'taglio'}, accanto=False)
    leg.salva(g); g.e.close(); g = leg.ricarica(g.sav)
    es['ricarica'] = dict(pos=vai.stato(g)[:3], flag_22=pl.flag(g.e, APERTO), rocce=rocce(g))
    vai.FLAG_ALZATE = {0x11, 0x12, 0x13}     # solo per il pianificatore: in gioco le nasconde lo script di mappa
    tappa(g, es, 'cesena', (34, 17), 6, 43, {'taglio'})
    tappa(g, es, 'di_nuovo_monte', (35, 101), 56, 21, {'taglio'})
    tappa(g, es, 'capocolle', (35, 60), 38, 17, {'taglio'})               # senza SPACCAROCCIA: rocce nascoste
    g.shot('t63_dopo'); g.close(); return es


def vecchio():
    g = apri('prog_imola.ss', [lambda g: leg.fixture_posizione(g, (35, 60), 38, 17),
                               lambda g: leg.fixture_flag(g, APERTO, 0)])
    es = dict(flag_22_inizio=pl.flag(g.e, APERTO)); AB = {'taglio'}
    tappa(g, es, 'casello_92', (35, 92), 6, 4, AB)
    es['flag_22_in_35_92'] = pl.flag(g.e, APERTO)
    tappa(g, es, 'monte', (35, 101), 12, 17, AB, accanto=False)
    vai.FLAG_ALZATE = {0x11, 0x12, 0x13}     # solo per il pianificatore: in gioco le nasconde lo script di mappa
    tappa(g, es, 'oltre_rocce', (35, 101), 20, 17, AB, accanto=False)
    tappa(g, es, 'cesena', (34, 17), 6, 43, AB)
    g.shot('t63_vecchio'); g.close(); return es


def riproduci():
    """Sulla 0.62 (per la relazione): con 1 medaglia il casello 35.91 rimanda a Cesena; con 6 medaglie, da Monte
    Spaccato a 35.92 si passa senza SPACCAROCCIA e senza rocce (nessun ostacolo fisico)."""
    es = {}
    g = apri('s_ce3.ss', []); AB = {'taglio'}
    es['una_medaglia_verso_monte'] = vai.vai(g, (35, 101), 56, 21, AB, max_ricalcoli=4)
    es['una_medaglia_pos'] = vai.stato(g)[:3]; es['testi'] = leg.chiudi_testi(g, 10); g.close()
    PARTE2 = 'riproduci6'
    sav = os.path.join(PLAY, 't63_%s.sav' % PARTE2)
    if not os.environ.get('VBAM'):
        g = leg.g_da('prog_imola.ss'); leg.fixture_posizione(g, (35, 101), 56, 21); leg.salva(g); g.e.close(); shutil.copy(g.sav, sav)
    g = leg.ricarica(shutil.copy(sav, os.path.join(PLAY, 'leg_tmp.sav')))
    es['sei_medaglie_35_92'] = vai.vai(g, (35, 92), 6, 4, AB); es['sei_medaglie_pos'] = vai.stato(g)[:3]
    log('  riproduci', es); g.close(); return es


def vecchio62():
    """Salvataggio vero della 0.62 (t63_riproduci6.sav: SALVA in gioco sulla ROM 0.62 a Monte Spaccato, 6 medaglie)
    caricato con la 0.63: Continua, poi a 35.92 e ritorno a Cesena."""
    g = leg.ricarica(shutil.copy(os.path.join(PLAY, 't63_riproduci6.sav'), os.path.join(PLAY, 'leg_tmp.sav')))
    es = dict(titolo=vai.stato(g)[:3], flag_22=pl.flag(g.e, APERTO)); AB = {'taglio', 'spacca'}
    tappa(g, es, 'davanti_rocce', (35, 101), 16, 17, {'taglio'}, accanto=False)
    tappa(g, es, 'passa', (35, 92), 6, 4, AB)
    es['flag_22_in_35_92'] = pl.flag(g.e, APERTO)
    tappa(g, es, 'monte', (35, 101), 12, 17, {'taglio'}, accanto=False)
    vai.FLAG_ALZATE = {0x11, 0x12, 0x13}
    tappa(g, es, 'cesena', (34, 17), 6, 43, {'taglio'})
    g.close(); return es


if __name__ == '__main__':
    r = dict(prima=prima, dopo=dopo, vecchio=vecchio, riproduci=riproduci, vecchio62=vecchio62)[PARTE]()
    json.dump(r, open(OUT, 'w'), indent=1, ensure_ascii=False, default=str)
    log('FINE', PARTE)
