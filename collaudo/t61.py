#!/usr/bin/env python3
"""Collaudo 0.61: Regi senza FORZA, Deoxys, Jirachi e Mewtwo (Lotto 2). Solo tasti, salvo le fixture dichiarate.
Uso: python3 t61.py ROM --parte=prepara|regi|regi5|sentiero|prima_lega|mitici|vecchio [--solo=a,b] [--rif] [--rom60=ROM]"""
import os, sys, json
ROM = os.path.abspath(sys.argv[1]); os.environ['ROMF'] = os.path.relpath(ROM, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'play'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import leg, vai, pl, shutil
from leg import log, A, B, PLAY, PARTE
from drv import R as DESTRA, L as SINISTRA
NESSUNA = set()                                    # i Regi: nessuna abilita' (la prova che FORZA non serve)
AB = {'taglio', 'spacca', 'surf', 'forza'}
RIF = '--rif' in sys.argv
OUT = os.path.join(PLAY, 't61_%s%s%s.json' % (PARTE, '_rif' if RIF else '', '_vbam' if os.environ.get('VBAM') else ''))

REGI = dict(regirock=dict(mappa=(35, 76), xy=(10, 4), gfx=200, flag=0x620),
            regice=dict(mappa=(35, 77), xy=(10, 4), gfx=201, flag=0x622),
            registeel=dict(mappa=(35, 78), xy=(10, 4), gfx=202, flag=0x627))
MITICI = dict(deoxys=dict(mappa=(35, 41), xy=(20, 10), gfx=233, flag=0x4eb),
              jirachi=dict(mappa=(35, 42), xy=(14, 4), gfx=180, flag=0x4ea),
              mewtwo=dict(mappa=(35, 43), xy=(13, 4), gfx=182, flag=0x4ef))


def nuova(nome, fixture_extra=(), mappa=(35, 73), x=22, y=25):
    """Da prog_imola.ss (6 medaglie, partita vera): fixture dichiarate, SALVA in gioco, poi Continua dal titolo."""
    g = leg.g_da('prog_imola.ss')
    for f, v in fixture_extra: leg.fixture_flag(g, f, v)
    leg.fixture_mossa(g, 1, 3, 57, 15)                                  # SURF a Breloom (per Jirachi)
    leg.fixture(g)                                                      # 5 MASTER BALL
    leg.fixture_posizione(g, mappa, x, y)
    leg.salva(g); g.e.close()
    sav = os.path.join(PLAY, 't61_%s.sav' % nome); shutil.copy(g.sav, sav)
    g = leg.ricarica(shutil.copy(sav, os.path.join(PLAY, 'leg_prova.sav')))
    log('  ', nome, 'dal titolo:', vai.stato(g), 'medaglia6', pl.flag(g.e, 0x86c), 'lega', pl.flag(g.e, 0x864))
    g.shot('t61_%s' % nome); g.close()


def prepara():
    solo = next((a.split('=', 1)[1].split(',') for a in sys.argv if a.startswith('--solo=')), None)
    if solo: return [PREP[k]() for k in solo]
    nuova('regi')                                                       # 6 medaglie, Sentiero Faenza-Lugo
    nuova('regi5', [(0x86c, 0)])                                         # senza la 6a medaglia (fixture al contrario)
    nuova('prima_lega', [(0x86d, 1), (0x86e, 1)], (34, 96), 60, 43)     # 8 medaglie, Lega non vinta, Ravenna est
    nuova('mitici', [(0x86d, 1), (0x86e, 1), (0x864, 1)], (34, 96), 60, 43)   # Lega vinta (fixture dichiarata)


PREP = dict(regi=lambda: nuova('regi'), regi5=lambda: nuova('regi5', [(0x86c, 0)]),
            prima_lega=lambda: nuova('prima_lega', [(0x86d, 1), (0x86e, 1)], (34, 96), 60, 43),
            mitici=lambda: nuova('mitici', [(0x86d, 1), (0x86e, 1), (0x864, 1)], (34, 96), 60, 43))


def apri(nome):
    sav = os.path.join(PLAY, 'leg_tmp.sav'); shutil.copy(os.path.join(PLAY, 't61_%s.sav' % nome), sav)
    g = leg.ricarica(sav); log(PARTE.upper(), os.path.basename(ROM), vai.stato(g)); return g


def tre_esiti(g, c, e, con_ko):
    """Davanti al Pokemon: fuga, (KO), cattura con MASTER BALL. Dopo fuga e KO deve restare al suo posto."""
    vis, lotta = leg.parla(g, c); e['parla'] = (vis, lotta); log('  parla:', vis, 'lotta', lotta)
    if RIF or not lotta: return
    leg.fuggi(g); vis = leg.chiudi_testi(g)
    e['fuga'] = dict(testi=vis, flag=pl.flag(g.e, c['flag']), presente=leg.presente(g, c)); log('  fuga:', e['fuga'])
    if con_ko:
        vis, lotta = leg.parla(g, c)
        if lotta:
            info = leg.ko(g); vis2 = leg.chiudi_testi(g)
            e['ko'] = dict(testi=vis + vis2, turni=len(info), pos=vai.stato(g)[:3], flag=pl.flag(g.e, c['flag']),
                           presente=leg.presente(g, c)); log('  KO:', e['ko'])
            if vai.stato(g)[0] != c['mappa']: log('  dopo il KO non sono piu\' nella camera'); return
    vis, lotta = leg.parla(g, c)
    if lotta:
        leg.menu_lotta(g); g.throw(); vis2 = leg.chiudi_testi(g, 40)
        e['cattura'] = dict(testi=vis + vis2, flag=pl.flag(g.e, c['flag']), presente=leg.presente(g, c),
                            squadra=leg.specie_squadra(g)); log('  cattura:', e['cattura'])


def regi():
    es = {}; g = apri('regi')
    for nome, c in REGI.items():
        e = es[nome] = {}
        ok = vai.vai(g, c['mappa'], *c['xy'], NESSUNA); e['arrivato_senza_abilita'] = ok
        log(nome, 'accanto senza abilita\'', ok, vai.stato(g)[:3])
        if not ok: continue
        tre_esiti(g, c, e, con_ko=(nome == 'regirock'))
        vai.vai(g, (35, 75), 14, 20, NESSUNA, accanto=False)            # fuori dalla camera
    if not RIF:
        leg.salva(g); g.e.close(); shutil.copy(g.sav, os.path.join(PLAY, 't61_regi_presi.sav'))
        g = leg.ricarica(g.sav)
        r = es['ricarica'] = dict(pos=vai.stato(g)[:3], flag={n: pl.flag(g.e, c['flag']) for n, c in REGI.items()})
        for nome in ('registeel', 'regirock'):
            c = REGI[nome]; ok = vai.vai(g, c['mappa'], *c['xy'], NESSUNA)
            r[nome] = dict(arrivato=ok, presente=leg.presente(g, c) if ok else None)
            vai.vai(g, (35, 75), 14, 20, NESSUNA, accanto=False)
        ok = vai.vai(g, (35, 73), 22, 20, NESSUNA, accanto=False)       # ritorno sul Sentiero (passaggio a ritroso)
        r['ritorno_sentiero'] = (ok, vai.stato(g)[:3]); log('  dopo la ricarica:', r)
    g.close(); return es


def regi5():
    g = apri('regi5'); c = REGI['regice']
    ok = vai.vai(g, c['mappa'], *c['xy'], NESSUNA)
    es = dict(arrivato=ok, parla=leg.parla(g, c) if ok else None, flag=pl.flag(g.e, c['flag']))
    log('  senza la 6a medaglia:', es); g.close(); return es


def a_est(g):
    """Ravenna 34.96: al bordo est (x 79) gli eventi a coordinate portano a 35.40, il molo del razzo."""
    vai.vai(g, (34, 96), 78, 49, AB, accanto=False)
    for _ in range(4):
        if vai.stato(g)[0] == (35, 40): break
        g.key(DESTRA, 3, 40)
    for _ in range(6):                                                  # via dalla colonna x 0 (riporta a 34.96)
        if vai.stato(g)[0] == (35, 40) and vai.stato(g)[1] >= 2: break
        g.key(DESTRA, 3, 40); g.e.run(30)
    return vai.stato(g)[:3]


def a_ovest(g):
    """Passaggio a ritroso: da 35.40 si torna a 34.96 spingendo a ovest sulla colonna x 0."""
    vai.vai(g, (35, 40), 1, 12, AB, accanto=False)
    for _ in range(4):
        if vai.stato(g)[0] == (34, 96): break
        g.key(SINISTRA, 3, 40)
    g.e.run(60); arrivo = vai.stato(g)[:3]
    for _ in range(6):                                                  # via dalla colonna x 79 (riporta a 35.40)
        if vai.stato(g)[0] == (34, 96) and vai.stato(g)[1] <= 77: break
        g.key(SINISTRA, 3, 40); g.e.run(30)
    return arrivo


def rispondi(g, si=True, n=40):
    """Dopo A su un cartello o un oggetto: A per avanzare e per il si', B per il no. Restituisce i testi visti."""
    vis = []
    for i in range(n):
        t = leg.testo(g)
        if t and (not vis or vis[-1] != t): vis.append(t)
        if i > 3 and vai.ow(g) and g.e.ram(0x03000e41, 1)[0] == 0:
            g.e.run(40)
            if vai.ow(g) and g.e.ram(0x03000e41, 1)[0] == 0: break
        g.key(A if si or '?' not in t else B, 3, 40)
    g.e.run(60); return vis


def tocca(g, mappa, x, y, si=True):
    if not vai.vai(g, mappa, x, y, AB): return None, vai.stato(g)[:3]
    vai.guarda(g, x, y); g.key(A, 3, 60)
    return rispondi(g, si), vai.stato(g)[:3]


def prima_lega():
    es = {}; g = apri('prima_lega')
    es['molo'] = a_est(g); log('  molo del razzo:', es['molo'])
    es['razzo'] = tocca(g, (35, 40), 29, 15); log('  razzo prima della Lega:', es['razzo'])
    es['ritorno_a_ovest'] = a_ovest(g); log('  di nuovo a Ravenna:', es['ritorno_a_ovest'])
    vai.vai(g, (0, 10), 61, 22, AB)
    es['portale_presente'] = any(gf == 183 for _, gf in g.lobjs_gfx()); log('  portale visibile:', es['portale_presente'])
    c = MITICI['mewtwo']; ok = vai.vai(g, c['mappa'], *c['xy'], AB)
    es['mewtwo'] = dict(arrivato=ok, parla=leg.parla(g, c) if ok else None, flag=pl.flag(g.e, c['flag']))
    log('  Mewtwo prima della Lega:', es['mewtwo']); g.close(); return es


def mitici():
    es = {}; g = apri('mitici')
    e = es['deoxys'] = {}; c = MITICI['deoxys']
    e['molo'] = a_est(g)
    e['razzo_no'] = tocca(g, (35, 40), 29, 15, si=False)
    e['razzo'] = tocca(g, (35, 40), 29, 15); log('  razzo:', e['razzo_no'], e['razzo'])
    if e['razzo'][1][0] == c['mappa'] and vai.vai(g, c['mappa'], *c['xy'], AB): tre_esiti(g, c, e, con_ko=False)
    e['rientro'] = tocca(g, (35, 41), 5, 9); log('  rientro:', e['rientro'])

    e = es['jirachi'] = {}; c = MITICI['jirachi']
    e['portale'] = tocca(g, (0, 10), 61, 22); log('  portale:', e['portale'])
    if e['portale'][1][0] == c['mappa'] and vai.vai(g, c['mappa'], *c['xy'], AB): tre_esiti(g, c, e, con_ko=False)
    e['ritorno'] = tocca(g, (35, 42), 14, 18); log('  ritorno:', e['ritorno'])

    e = es['mewtwo'] = {}; c = MITICI['mewtwo']
    if vai.vai(g, c['mappa'], *c['xy'], AB): tre_esiti(g, c, e, con_ko=False)
    vai.vai(g, (34, 22), 48, 35, AB, accanto=False); e['uscita'] = vai.stato(g)[:3]
    if not RIF:
        leg.salva(g); g.e.close(); shutil.copy(g.sav, os.path.join(PLAY, 't61_mitici_presi.sav'))
        g = leg.ricarica(g.sav)
        r = es['ricarica'] = dict(pos=vai.stato(g)[:3], flag={n: pl.flag(g.e, c['flag']) for n, c in MITICI.items()},
                                  squadra=leg.specie_squadra(g))
        c = MITICI['mewtwo']; ok = vai.vai(g, c['mappa'], *c['xy'], AB)
        r['mewtwo'] = dict(arrivato=ok, presente=leg.presente(g, c) if ok else None)
        log('  dopo la ricarica:', r)
    g.close(); return es


def vecchio(r60):
    """Salvataggio vero fatto con la 0.60 dentro la Camera di Pietra (oggetti in SaveBlock1 col vecchio script),
    aperto con la 0.61: deve rispondere il nuovo script (testo d'ingresso nuovo, poi fuga con il suo testo)."""
    c = REGI['regirock']; es = {}
    s = os.path.join(PLAY, 'leg_vecchio.sav'); shutil.copy(os.path.join(PLAY, 't61_regi.sav'), s)
    g = leg.ricarica(s, r60); vai.vai(g, c['mappa'], *c['xy'], NESSUNA); leg.salva(g); g.close()
    g = leg.ricarica(s); es['pos'] = vai.stato(g)[:3]
    vis, lotta = leg.parla(g, c); es['0.61_dal_titolo'] = (vis, lotta)
    if lotta: leg.fuggi(g); es['fuga'] = leg.chiudi_testi(g)
    log('  vecchio salvataggio:', es); g.close(); return es


def sentiero_senza_6a():
    """Senza la 6a medaglia: chi sbarra il Sentiero (oggetto 1 di 35.73, nascosto dalla 0x86C) cosa dice."""
    g = apri('regi5'); t = leg.leggi(g, (35, 73), 24, 9, NESSUNA); es = dict(testi=t, pos=vai.stato(g)[:3])
    log('  sbarramento del Sentiero:', es); g.close(); return es


FUN = dict(sentiero=sentiero_senza_6a, regi=regi, regi5=regi5, prima_lega=prima_lega, mitici=mitici)
if PARTE == 'prepara': prepara()
elif PARTE == 'vecchio':
    es = vecchio(os.path.abspath(next(a.split('=', 1)[1] for a in sys.argv if a.startswith('--rom60='))))
    json.dump(es, open(OUT, 'w'), indent=1, ensure_ascii=False, default=str)
elif PARTE in FUN:
    json.dump(FUN[PARTE](), open(OUT, 'w'), indent=1, ensure_ascii=False, default=str)
