#!/usr/bin/env python3
"""Collaudo 0.64: Campagna Cesenate (35.101 ridisegnata). Solo tasti, salvo le fixture dichiarate.
Uso: python3 t64.py ROM --parte=prima|dopo|crea63|vecchio63|vecchio62
  prima     da s_ce3.ss (Cesena, 1 medaglia), SALVA e Continua. Nessuna fixture.
            Cesena -> casello -> Ippodromo -> porta della casa della campagna; nome del luogo; cartelli;
            la roccia davanti alla galleria non si rompe; nessun percorso verso 35.92; ritorno a Cesena
            dall'Ippodromo; SALVA e Continua.
  dopo      da prog_imola.ss (6 medaglie). Fixture: posizione all'Ippodromo (8,17); SPACCAROCCIA al Pokemon 0.
            Lotte con i tre allenatori nuovi (NICO, TONINO, OSVALDO), testo dopo la lotta; la roccia si rompe,
            si passa a 35.92 (0x22 = 1); tornando la roccia non c'e'; SALVA e Continua dentro la campagna:
            si resta dove si e' salvato; ritorno a Cesena dall'Ippodromo.
  crea63    sulla ROM 0.63: da prog_imola.ss, fixture posizione a Monte Spaccato (20,3) (calpestabile nella
            0.63, monte nella 0.64), SALVA vero -> play/t64_crea63.sav.
  vecchio63 sulla 0.64 con t64_crea63.sav: Continua; il giocatore torna una volta sola davanti alla casa (55,23);
            si cammina; SALVA e Continua: si resta li'.
  vecchio62 sulla 0.64 con t63_riproduci6.sav (SALVA vero della 0.62 a Monte Spaccato 56,21: ora la casa).
"""
import os, sys, json, shutil, struct
ROM = os.path.abspath(sys.argv[1]); os.environ['ROMF'] = os.path.relpath(ROM, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'play'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'strumenti_rom'))
import leg, vai, pl, romlib
from leg import log, A, B, PLAY, PARTE
from drv import L, U as SU
APERTO = 0x22
K = (35, 101)
OUT = os.path.join(PLAY, 't64_%s%s.json' % (PARTE, '_vbam' if os.environ.get('VBAM') else ''))
NUOVI = {'NICO': (27, 16, 7, 462), 'TONINO': (43, 13, 49, 485), 'OSVALDO': (55, 30, 33, 486)}
_R = romlib.Rom(ROM)


def var_nuova():
    """La variabile della 0.64: primo comando (setvar) dello script d'ingresso di 35.101."""
    ms = dict(_R.map_scripts(_R.map(*K)))
    p = ms.get(3); d = _R.data
    return struct.unpack_from('<H', d, p + 1)[0] if p is not None and d[p] == 0x16 else None


NUOVA = var_nuova()


def roccia(g):
    return sorted(xy for xy, gf in g.lobjs_gfx() if gf == 86) if vai.stato(g)[0] == K else None


def oggetti(g):
    return sorted(g.lobjs_gfx()) if vai.stato(g)[0] == K else None


def spingi(g, dn, n=4):
    p0 = vai.stato(g)[:3]
    for _ in range(n): g.step(dn); g.e.run(10)
    return dict(prima=p0, dopo=vai.stato(g)[:3])


def apri(state, fix):
    sav = os.path.join(PLAY, 't64_%s.sav' % PARTE)
    if not os.environ.get('VBAM'):
        g = leg.g_da(state)
        for f in fix: f(g)
        leg.salva(g); g.e.close(); shutil.copy(g.sav, sav)
    g = leg.ricarica(shutil.copy(sav, os.path.join(PLAY, 'leg_tmp.sav')))
    log('PROVA', PARTE, 'VBA-M' if os.environ.get('VBAM') else 'mGBA', os.path.basename(ROM))
    log('  dal titolo:', vai.stato(g), 'medaglie', [pl.flag(g.e, f) for f in range(0x867, 0x86f)], 'flag 0x22', pl.flag(g.e, APERTO))
    return g


def tappa(g, es, nome, mappa, x, y, ab, accanto=True):
    ok = vai.vai(g, mappa, x, y, ab, accanto=accanto)
    es[nome] = dict(ok=ok, pos=vai.stato(g)[:3], roccia=roccia(g), flag_11=pl.flag(g.e, 0x11),
                    var_nuova=g.var(NUOVA) if NUOVA else None); log('  ', nome, es[nome]); return ok


def nome_luogo(g):
    """Il nome del luogo che il gioco mostra: lo si legge dalla tabella delle sezioni con la sezione corrente."""
    sb1 = g.e.r('r32', 0x3005d8c); m = vai.stato(g)[0]
    h = _R.map(*m); reg = h['region']
    p = struct.unpack_from('<I', _R.data, 0x74cca4 - 0xd3 * 8 + reg * 8)[0] - 0x8000000
    from text_codec import CHAR
    return ''.join(CHAR.get(c, '?') for c in _R.data[p:_R.data.index(b'\xff', p)])


def cartelli(g, es, AB):
    for nome, (x, y) in dict(monte=(8, 9), casa=(53, 22), ponte=(42, 22)).items():
        es['cartello_' + nome] = leg.leggi(g, K, x, y, AB)
        log('   cartello', nome, es['cartello_' + nome])


def prima():
    g = apri('s_ce3.ss', []); es = dict(medaglie=[pl.flag(g.e, f) for f in range(0x867, 0x86f)], var_numero=hex(NUOVA))
    AB = {'taglio'}
    tappa(g, es, 'ippodromo', (34, 19), 19, 30, AB)
    tappa(g, es, 'arrivo_campagna', K, 55, 23, AB, accanto=False)          # dal cancello ovest: la porta della casa
    es['luogo'] = nome_luogo(g); es['oggetti'] = oggetti(g)
    cartelli(g, es, AB)
    tappa(g, es, 'davanti_roccia', K, 25, 12, AB, accanto=False)
    vai.guarda(g, 25, 11); g.key(A, 3, 60); es['roccia_testi'] = leg.chiudi_testi(g, 20)
    es['contro_roccia'] = spingi(g, 'U'); es['roccia_dopo'] = roccia(g)
    es['verso_35_92'] = vai.vai(g, (35, 92), 6, 4, AB, max_ricalcoli=4)    # deve fallire
    tappa(g, es, 'ritorno_ippodromo', (34, 19), 8, 17, AB)
    tappa(g, es, 'ritorno_cesena', (34, 17), 6, 43, AB)
    leg.salva(g); g.e.close(); g = leg.ricarica(g.sav)
    es['ricarica'] = dict(pos=vai.stato(g)[:3], flag_22=pl.flag(g.e, APERTO))
    g.shot('t64_prima'); g.close(); return es


def lotta_con(g, es, nome, AB):
    x, y, gfx, tid = NUOVI[nome]
    tentativi = []
    for _ in range(3):            # una lotta selvatica nell'erba alta puo' partire mentre si parla: si riprova
        ok = vai.vai(g, K, x, y, AB)
        vis, lotta = leg.parla(g, dict(xy=(x, y), gfx=gfx))
        info = leg.ko(g) if lotta else []
        dopo = leg.chiudi_testi(g, 20)
        flag = pl.flag(g.e, 0x500 + tid)
        tentativi.append(dict(testi=vis, squadra=sorted({(i[3], i[4]) for i in info}), flag=flag))
        if flag: break
    vis2, lotta2 = leg.parla(g, dict(xy=(x, y), gfx=gfx)); leg.chiudi_testi(g, 10)
    es['lotta_' + nome] = dict(arrivo=ok, testi=vis, lotta=lotta, turni=len(info), dopo=dopo, flag=flag,
                               di_nuovo=vis2, di_nuovo_lotta=lotta2, squadra_avversaria=sorted({(i[3], i[4]) for i in info}),
                               tentativi=tentativi)
    log('  ', nome, es['lotta_' + nome])


def dopo():
    g = apri('prog_imola.ss', [lambda g: leg.fixture_posizione(g, (34, 19), 8, 17),
                               lambda g: leg.fixture_mossa(g, 0, 3, 0xf9, 15)])
    es = dict(flag_22_inizio=pl.flag(g.e, APERTO)); AB = {'taglio', 'spacca'}
    tappa(g, es, 'arrivo_campagna', K, 55, 23, {'taglio'}, accanto=False)
    es['oggetti'] = oggetti(g)
    for nome in ('OSVALDO', 'TONINO', 'NICO'): lotta_con(g, es, nome, {'taglio'})
    tappa(g, es, 'davanti_roccia', K, 25, 12, {'taglio'}, accanto=False)
    vai.rompi(g, 'N'); leg.chiudi_testi(g, 10)
    es['dopo_rottura'] = dict(roccia=roccia(g), pos=vai.stato(g)[:3], flag_22=pl.flag(g.e, APERTO))
    tappa(g, es, 'passa', (35, 92), 6, 4, AB)
    es['flag_22_in_35_92'] = pl.flag(g.e, APERTO)
    vai.FLAG_ALZATE = {0x11}     # solo per il pianificatore: in gioco la nasconde lo script di mappa
    tappa(g, es, 'torna_galleria', K, 25, 13, {'taglio'}, accanto=False)
    tappa(g, es, 'riva_fiume', K, 43, 18, {'taglio'}, accanto=False)
    leg.salva(g); g.e.close(); g = leg.ricarica(g.sav)
    es['ricarica'] = dict(pos=vai.stato(g)[:3], flag_22=pl.flag(g.e, APERTO), var_nuova=g.var(NUOVA),
                          flag_allenatori={n: pl.flag(g.e, 0x500 + v[3]) for n, v in NUOVI.items()})
    g.e.run(120); es['ricarica_dopo_2s'] = vai.stato(g)[:3]
    tappa(g, es, 'dopo_ricarica_galleria', K, 25, 13, {'taglio'}, accanto=False)   # roccia: qui e' in vista
    x, y, gfx, tid = NUOVI['NICO']
    vai.vai(g, K, x, y, {'taglio'})
    vis, lotta = leg.parla(g, dict(xy=(x, y), gfx=gfx)); leg.chiudi_testi(g, 10)
    es['NICO_dopo_ricarica'] = dict(testi=vis, lotta=lotta, flag=pl.flag(g.e, 0x500 + tid))
    tappa(g, es, 'cesena', (34, 17), 6, 43, {'taglio'})
    g.shot('t64_dopo'); g.close(); return es


def crea63():
    """Sulla ROM 0.63: un salvataggio vero dentro Monte Spaccato in una casella che nella 0.64 e' monte."""
    sav = os.path.join(PLAY, 't64_crea63.sav')
    g = leg.g_da('prog_imola.ss'); leg.fixture_posizione(g, K, 20, 3); leg.salva(g); g.e.close(); shutil.copy(g.sav, sav)
    g = leg.ricarica(shutil.copy(sav, os.path.join(PLAY, 'leg_tmp.sav')))
    es = dict(pos_063=vai.stato(g)[:3]); log('  crea63', es); g.close(); return es


def vecchio(savname):
    log('PROVA', PARTE, 'VBA-M' if os.environ.get('VBAM') else 'mGBA', os.path.basename(ROM), savname)
    g = leg.ricarica(shutil.copy(os.path.join(PLAY, savname), os.path.join(PLAY, 'leg_tmp.sav')))
    es = dict(titolo=vai.stato(g)[:3], var_nuova=g.var(NUOVA))
    g.e.run(240); leg.chiudi_testi(g, 5)
    es['dopo_4s'] = dict(pos=vai.stato(g)[:3], var_nuova=g.var(NUOVA), oggetti=oggetti(g))
    tappa(g, es, 'cammina', K, 50, 25, {'taglio'}, accanto=False)
    leg.salva(g); g.e.close(); g = leg.ricarica(g.sav)
    es['ricarica'] = dict(pos=vai.stato(g)[:3], var_nuova=g.var(NUOVA)); g.e.run(240)
    es['ricarica_dopo_4s'] = vai.stato(g)[:3]
    vai.FLAG_ALZATE = {0x11}
    tappa(g, es, 'ippodromo', (34, 19), 8, 17, {'taglio'})
    g.shot('t64_' + PARTE); g.close(); return es


if __name__ == '__main__':
    r = dict(prima=prima, dopo=dopo, crea63=crea63, vecchio63=lambda: vecchio('t64_crea63.sav'),
             vecchio62=lambda: vecchio('t63_riproduci6.sav'))[PARTE]()
    json.dump(r, open(OUT, 'w'), indent=1, ensure_ascii=False, default=str)
    log('FINE', PARTE)
