#!/usr/bin/env python3
"""Collaudo 0.67: il TRENO REGIONALE. Solo tasti, salvo le fixture dichiarate.
Uso: python3 t67.py ROM --parte=rimini|imola|salva
  rimini  da prog_imola.ss (6 medaglie: sulla mappa del Volo ci sono Cesena, Rimini, Forli', Faenza; Imola no).
          Fixture: posizione a Rimini davanti alla stazione. Porta -> sala; tabellone, biglietteria, viaggiatore;
          CAPOTRENO: domande (attese CESENA, FORLI', FAENZA; non IMOLA), si' a CESENA -> carrozza (primo viaggio:
          il viaggiatore parla) -> binario di Cesena (6,4) -> uscita in citta' davanti alla porta (82,8).
          Cesena -> si' a FORLI' (secondo viaggio: niente chiacchiere) -> Forli' -> fuori. Di nuovo dentro: si
          rifiuta tutto (domande attese RIMINI, CESENA, FAENZA), si esce.
  imola   da prog_imola.ss. Fixture: 7a medaglia (0x86D), posizione a Imola davanti alla stazione. Domande attese
          RIMINI, CESENA, FORLI', FAENZA; si' a CESENA -> Cesena.
  crea66  sulla ROM 0.66: da prog_imola.ss, fixture posizione a Cesena (82,10) davanti alla casa che diventa la
          stazione, SALVA vero.
  vecchio66 sulla 0.67 con t67_crea66.sav: Continua. Si prova a entrare dalla porta; poi si esce dalla citta' (casello
          est, 35.87) e si rientra, e si riprova.
  salva   da prog_imola.ss. Fixture: posizione a Rimini. Dentro la sala: SALVA vero, titolo, Continua: si e' nella
          sala; si esce a Rimini.
"""
import os, sys, json, shutil, struct
ROM = os.path.abspath(sys.argv[1]); os.environ['ROMF'] = os.path.relpath(ROM, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'play'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'strumenti_rom'))
import leg, vai, pl, romlib
from leg import log, A, B, PLAY, PARTE
from drv import U, D
VBAM = bool(os.environ.get('VBAM'))
OUT = os.path.join(PLAY, 't67_%s%s.json' % (PARTE, '_vbam' if VBAM else ''))
_R = romlib.Rom(ROM)
AB = {'taglio', 'spacca', 'forza', 'surf'}
CARROZZA = (24, 74)
SALE = {'CESENA': (24, 39), 'RIMINI': (24, 40), 'FORLI': (24, 41), 'FAENZA': (24, 50), 'IMOLA': (24, 51)}
CITTA = {'CESENA': ((34, 17), (82, 8)), 'RIMINI': ((34, 47), (54, 11)), 'FORLI': ((34, 68), (72, 55)),
         'FAENZA': ((34, 85), (40, 5)), 'IMOLA': ((35, 1), (57, 19))}


def numeri():
    """Variabile del viaggio e flag del primo viaggio, letti dagli script della carrozza."""
    m = _R.map(*CARROZZA); ms = dict(_R.map_scripts(m)); d = _R.data
    tab = ms[2]; var = struct.unpack_from('<H', d, tab)[0]
    p = struct.unpack_from('<I', d, tab + 4)[0] - 0x8000000
    assert d[p] == 0x69 and d[p + 4] == 0x2b
    return var, struct.unpack_from('<H', d, p + 5)[0]


TRENO, F_PRIMO = numeri()


def dove(g): return vai.stato(g)[:3]


def apri(fix, nome=None):
    sav = os.path.join(PLAY, 't67_%s.sav' % (nome or PARTE))
    if not VBAM:
        g = leg.g_da('prog_imola.ss')
        for f in fix: f(g)
        leg.salva(g); g.e.close(); shutil.copy(g.sav, sav)
    g = leg.ricarica(shutil.copy(sav, os.path.join(PLAY, 'leg_tmp.sav')))
    log('PROVA', PARTE, 'VBA-M' if VBAM else 'mGBA', os.path.basename(ROM))
    log('  dal titolo:', vai.stato(g), 'medaglie', [pl.flag(g.e, f) for f in range(0x867, 0x86f)],
        'visita', {c: pl.flag(g.e, f) for c, f in [('CES', 0x876), ('RIM', 0x877), ('FOR', 0x878), ('FAE', 0x873), ('IMO', 0x872)]})
    return g


def libero(g): return vai.ow(g) and g.e.ram(0x03000e41, 1)[0] == 0


def chiudi(g, n=40):
    vis = []
    for _ in range(n):
        t = leg.testo(g)
        if t and (not vis or vis[-1] != t): vis.append(t)
        if libero(g):
            g.e.run(30)
            if libero(g): break
        g.key(B, 3, 40)
    return vis


def a_capotreno(g, es, nome, sala, meta=None):
    """Si parla al CAPOTRENO (7,8) da sotto (7,9). Alle domande "Un biglietto per X?" si risponde si' solo a meta.
    Si seguono i testi (anche quelli della carrozza) finche' si e' liberi fuori dalla carrozza."""
    ok = vai.vai(g, sala, 7, 9, AB, accanto=False)
    vai.guarda(g, 7, 8); g.e.run(10); g.key(A, 3, 40)
    vis, domande, mappe = [], [], []
    for i in range(400):
        t = leg.testo(g)
        if t and (not vis or vis[-1] != t):
            vis.append(t)
            if 'biglietto per' in t and t.startswith('Un'): domande.append(t.split('per ')[1].rstrip('?').strip().replace('{09}', 'Ì'))
        m = dove(g)[0]
        if not mappe or mappe[-1] != m: mappe.append(m)
        if i > 5 and libero(g) and m != CARROZZA:
            g.e.run(40)
            if libero(g) and dove(g)[0] != CARROZZA: break
        k = A
        if t.startswith('Un biglietto per') and (meta is None or meta not in t.upper().replace('Ì', 'I').replace('{09}', 'I')): k = B
        g.key(k, 3, 30)
    es[nome] = dict(arrivo_capotreno=ok, testi=vis, domande=domande, mappe=[str(x) for x in mappe], pos=dove(g),
                    var_treno=g.var(TRENO), primo_viaggio=pl.flag(g.e, F_PRIMO))
    log('  ', nome, es[nome])


def leggi(g, es, nome, mappa, x, y, da):
    ok = vai.vai(g, mappa, *da, AB, accanto=False)
    vai.guarda(g, x, y); g.e.run(10); g.key(A, 3, 40)
    vis = chiudi(g)
    es[nome] = dict(arrivo=ok, testi=vis, pos=dove(g)); log('  ', nome, es[nome])


def entra(g, es, nome, citta):
    mappa, (x, y) = CITTA[citta]
    ok = vai.vai(g, mappa, x, y + 1, AB, accanto=False)
    vai.guarda(g, x, y); g.e.run(5)
    for _ in range(3):
        g.key(U, 3, 60)
        if dove(g)[0] == SALE[citta]: break
    g.e.run(60)
    es[nome] = dict(arrivo=ok, pos=dove(g)); log('  ', nome, es[nome])


def esci(g, es, nome, citta):
    """Dalla sala si scende all'uscita (6,11): si deve tornare in citta' davanti alla porta."""
    vai.vai(g, SALE[citta], 6, 10, AB, accanto=False)
    for _ in range(3):
        g.key(D, 3, 60)
        if dove(g)[0] != SALE[citta]: break
    g.e.run(60)
    es[nome] = dict(pos=dove(g), porta=CITTA[citta]); log('  ', nome, es[nome])


def rimini():
    g = apri([lambda g: leg.fixture_posizione(g, (34, 47), 54, 13)])
    es = {}
    entra(g, es, 'ingresso_rimini', 'RIMINI')
    leggi(g, es, 'biglietteria', SALE['RIMINI'], 12, 8, (11, 8))
    leggi(g, es, 'viaggiatore', SALE['RIMINI'], 1, 9, (2, 9))
    a_capotreno(g, es, 'rimini_cesena', SALE['RIMINI'], 'CESENA')
    g.shot('t67_arrivo_cesena')
    esci(g, es, 'uscita_cesena', 'CESENA')
    entra(g, es, 'ingresso_cesena', 'CESENA')
    a_capotreno(g, es, 'cesena_forli', SALE['CESENA'], 'FORLI')
    esci(g, es, 'uscita_forli', 'FORLI')
    entra(g, es, 'ingresso_forli', 'FORLI')
    a_capotreno(g, es, 'forli_rifiuto', SALE['FORLI'], None)
    esci(g, es, 'uscita_forli_2', 'FORLI')
    g.shot('t67_' + PARTE); g.close(); return es


def imola():
    g = apri([lambda g: leg.fixture_flag(g, 0x86d, 1), lambda g: leg.fixture_posizione(g, (35, 1), 57, 21)])
    es = {}
    entra(g, es, 'ingresso_imola', 'IMOLA')
    a_capotreno(g, es, 'imola_cesena', SALE['IMOLA'], 'CESENA')
    esci(g, es, 'uscita_cesena', 'CESENA')
    g.shot('t67_' + PARTE); g.close(); return es


def salva():
    g = apri([lambda g: leg.fixture_posizione(g, (34, 47), 54, 13)])
    es = {}
    entra(g, es, 'ingresso_rimini', 'RIMINI')
    vai.vai(g, SALE['RIMINI'], 4, 9, AB, accanto=False)
    leg.salva(g); g.e.close(); g = leg.ricarica(g.sav)
    es['dopo_continua'] = dove(g); log('  ', es)
    g.e.run(120); es['dopo_2s'] = dove(g)
    esci(g, es, 'uscita_rimini', 'RIMINI')
    g.shot('t67_' + PARTE); g.close(); return es


def crea66():
    sav = os.path.join(PLAY, 't67_crea66.sav')
    g = leg.g_da('prog_imola.ss'); leg.fixture_posizione(g, (34, 17), 82, 10)
    leg.salva(g); g.e.close(); shutil.copy(g.sav, sav)
    g = leg.ricarica(shutil.copy(sav, os.path.join(PLAY, 'leg_tmp.sav')))
    es = dict(pos_066=dove(g)); log('  crea66', es); g.close(); return es


def vecchio66():
    log('PROVA', PARTE, 'VBA-M' if VBAM else 'mGBA', os.path.basename(ROM))
    g = leg.ricarica(shutil.copy(os.path.join(PLAY, 't67_crea66.sav'), os.path.join(PLAY, 'leg_tmp.sav')))
    es = dict(titolo=dove(g)); g.e.run(120)
    g.shot('t67_vecchio66_titolo')
    entra(g, es, 'porta_subito', 'CESENA')
    if dove(g)[0] == SALE['CESENA']: esci(g, es, 'fuori_1', 'CESENA')
    es['uscita_citta'] = vai.vai(g, (35, 87), 5, 4, AB, accanto=True)
    es['dopo_uscita'] = dove(g); log('  ', es)
    entra(g, es, 'porta_dopo_rientro', 'CESENA')
    g.shot('t67_' + PARTE); g.close(); return es


if __name__ == '__main__':
    r = dict(rimini=rimini, imola=imola, salva=salva, crea66=crea66, vecchio66=vecchio66)[PARTE]()
    json.dump(r, open(OUT, 'w'), indent=1, ensure_ascii=False, default=str)
    log('FINE', PARTE)
