#!/usr/bin/env python3
"""Collaudo 0.60: Kyogre e uccelli leggendari prima della Lega (Lotto 2). Solo tasti, salvo le fixture dichiarate.
Uso: python3 t60.py ROM --parte=prepara|kyogre|uccelli [--rif]"""
import os, sys, json
ROM = os.path.abspath(sys.argv[1]); os.environ['ROMF'] = os.path.relpath(ROM, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'play'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import leg, vai, pl, shutil
from leg import log, A, B, PLAY, PARTE
AB = {'taglio', 'spacca', 'surf', 'forza', 'sub'}
RIF = '--rif' in sys.argv

def prepara():
    """Da prog_imola.ss (6 medaglie, partita vera) due salvataggi in gioco con le fixture dichiarate."""
    for nome, mappa, x, y in (('bagno', (35, 19), 18, 5), ('rimini', (34, 44), 50, 21)):
        g = leg.g_da('prog_imola.ss')
        for f in (0x86d, 0x86e): leg.fixture_flag(g, f)                    # medaglie 7 e 8
        leg.fixture_mossa(g, 0, 1, 70, 15)                                  # FORZA a Blaziken
        leg.fixture_mossa(g, 1, 3, 57, 15)                                  # SURF a Breloom
        leg.fixture_mossa(g, 1, 2, 291, 10)                                 # SUB a Breloom
        leg.fixture(g)                                                      # 5 MASTER BALL
        for t in (842, 843, 844, 750, 751, 752, 753, 754, 755):             # allenatori di Via Vittoria gia' battuti
            leg.fixture_flag(g, 0x500 + t)
        leg.fixture_posizione(g, mappa, x, y)
        leg.salva(g); g.e.close()
        sav = os.path.join(PLAY, 't60_%s.sav' % nome); shutil.copy(g.sav, sav)
        prova = os.path.join(PLAY, 'leg_prova.sav'); shutil.copy(sav, prova)
        g = leg.ricarica(prova); log('  ', nome, 'dal titolo:', vai.stato(g), 'lega', pl.flag(g.e, 0x864))
        g.shot('t60_%s' % nome); g.close()

def lotta_completa(g, c, esito):
    """Parla (gia' davanti al Pokemon), fuga, nuovo tentativo, cattura con MASTER BALL."""
    vis, lotta = leg.parla(g, c); esito['parla'] = (vis, lotta); log('  parla:', vis, 'lotta', lotta)
    if RIF or not lotta: return
    leg.fuggi(g); vis = leg.chiudi_testi(g)
    esito['fuga'] = dict(testi=vis, flag=pl.flag(g.e, c['flag']), presente=leg.presente(g, c)); log('  fuga:', esito['fuga'])
    vis, lotta = leg.parla(g, c)
    if lotta:
        leg.menu_lotta(g); g.throw(); vis2 = leg.chiudi_testi(g, 20)
        esito['cattura'] = dict(testi=vis + vis2, flag=pl.flag(g.e, c['flag']), presente=leg.presente(g, c),
                                squadra=leg.specie_squadra(g)); log('  cattura:', esito['cattura'])

def dopo(g, c, esito, nome, fuori):
    """Salva in gioco, ricarica dal titolo, esce e rientra: la cattura resta."""
    leg.salva(g); g.e.close(); shutil.copy(g.sav, os.path.join(PLAY, 't60_%s_preso.sav' % nome))
    g = leg.ricarica(g.sav)
    esito['ricarica'] = dict(pos=vai.stato(g)[:3], flag=pl.flag(g.e, c['flag']), squadra=leg.specie_squadra(g))
    k, x, y = fuori; vai.vai(g, k, x, y, AB, accanto=False)
    ok = vai.vai(g, c['mappa'], *c['xy'], AB)
    esito['ricarica'].update(rientro=ok, presente_dopo_rientro=leg.presente(g, c), flag_dopo_rientro=pl.flag(g.e, c['flag']))
    log('  dopo la ricarica:', esito['ricarica']); g.close()

def kyogre():
    c = dict(mappa=(35, 37), xy=(29, 24), gfx=220, flag=0x4e1); esito = {}
    sav = os.path.join(PLAY, 'leg_tmp.sav'); shutil.copy(os.path.join(PLAY, 't60_rimini.sav'), sav); g = leg.ricarica(sav)
    log('KYOGRE', os.path.basename(ROM), vai.stato(g))
    esito['cartello'] = leg.leggi(g, (34, 44), 52, 20, AB); log('  cartello:', esito['cartello'], vai.stato(g)[:3])
    ok = vai.vai(g, (35, 37), 29, 24, AB); log('  accanto a Kyogre', ok, vai.stato(g)); g.shot('t60_kyogre_davanti')
    esito['prima_dei_piloni'] = leg.parla(g, c); log('  prima dei piloni:', esito['prima_dei_piloni'])
    esito['pilone_est_prima'] = leg.leggi(g, (35, 37), 25, 11, AB); log('  pilone est per primo:', esito['pilone_est_prima'])
    esito['pilone_ovest'] = leg.leggi(g, (35, 37), 8, 10, AB); log('  pilone ovest:', esito['pilone_ovest'])
    esito['pilone_est'] = leg.leggi(g, (35, 37), 25, 11, AB); log('  pilone est:', esito['pilone_est'])
    vai.vai(g, (35, 37), 29, 24, AB)
    lotta_completa(g, c, esito)
    if not RIF and esito.get('cattura', {}).get('flag'): dopo(g, c, esito, 'kyogre', ((35, 36), 19, 20))
    else: g.close()
    return esito

UCCELLI = dict(articuno=dict(mappa=(35, 31), xy=(13, 12), gfx=225, flag=0x4cd, rune=[(9, 17), (20, 15)]),
               zapdos=dict(mappa=(35, 32), xy=(13, 12), gfx=226, flag=0x4ce, rune=[(9, 17), (20, 15)]),
               moltres=dict(mappa=(35, 33), xy=(13, 12), gfx=228, flag=0x4cf, rune=[(9, 17), (13, 19), (20, 15)]))

def uccelli():
    esiti = {}
    sav = os.path.join(PLAY, 'leg_tmp.sav'); shutil.copy(os.path.join(PLAY, 't60_bagno.sav'), sav); g = leg.ricarica(sav)
    log('UCCELLI', os.path.basename(ROM), vai.stato(g))
    t = leg.leggi(g, (35, 27), 10, 2, AB); log('  guardia:', t, vai.stato(g)[:3])
    for nome, c in UCCELLI.items():
        e = esiti[nome] = {}
        ok = vai.vai(g, c['mappa'], *c['xy'], AB); log(nome, 'accanto', ok, vai.stato(g)[:3])
        e['senza_rune'] = leg.parla(g, c); log('  senza rune:', e['senza_rune'])
        for r in c['rune']:
            e.setdefault('rune', []).append(leg.leggi(g, c['mappa'], *r, AB))
        log('  rune:', e['rune'])
        vai.vai(g, c['mappa'], *c['xy'], AB)
        lotta_completa(g, c, e)
        vai.vai(g, (35, 28), 15, 20, AB, accanto=False)        # fuori dal santuario
    if not RIF:
        leg.salva(g); g.e.close(); shutil.copy(g.sav, os.path.join(PLAY, 't60_uccelli_presi.sav'))
        g = leg.ricarica(g.sav)
        esiti['ricarica'] = dict(pos=vai.stato(g)[:3], flag={n: pl.flag(g.e, c['flag']) for n, c in UCCELLI.items()},
                                 squadra=leg.specie_squadra(g))
        for nome in ('moltres', 'zapdos', 'articuno'):
            c = UCCELLI[nome]
            ok = vai.vai(g, c['mappa'], *c['xy'], AB)
            esiti['ricarica'][nome] = dict(arrivato=ok, presente=leg.presente(g, c) if ok else None)
            vai.vai(g, (35, 28), 15, 20, AB, accanto=False)
        log('  dopo la ricarica:', esiti['ricarica'])
    g.close()
    return esiti

def vecchio(r59):
    """Salvataggio vero fatto con la 0.59 dentro il Santuario di Articuno (oggetti in SaveBlock1 col vecchio script),
    aperto con la 0.60: parlando con Articuno deve rispondere il nuovo script (indizio delle rune, non la Lega)."""
    c = UCCELLI['articuno']; es = {}
    s = os.path.join(PLAY, 'leg_vecchio.sav'); shutil.copy(os.path.join(PLAY, 't60_bagno.sav'), s)
    g = leg.ricarica(s, r59)
    leg.leggi(g, (35, 27), 10, 2, AB); vai.vai(g, c['mappa'], *c['xy'], AB)
    es['0.59_prima'] = leg.parla(g, c); leg.salva(g); g.close()
    g = leg.ricarica(s, r59); es['0.59_dal_titolo'] = (vai.stato(g)[:3], leg.parla(g, c)); g.close()
    g = leg.ricarica(s); es['0.60_dal_titolo'] = (vai.stato(g)[:3], leg.parla(g, c)); g.close()
    log('  vecchio salvataggio:', es); return es

if PARTE == 'prepara': prepara()
elif PARTE == 'vecchio':
    es = vecchio(os.path.abspath(next(a.split('=', 1)[1] for a in sys.argv if a.startswith('--rom59='))))
    json.dump(es, open(os.path.join(PLAY, 't60_vecchio.json'), 'w'), indent=1, ensure_ascii=False, default=str)
elif PARTE in ('kyogre', 'uccelli'):
    es = kyogre() if PARTE == 'kyogre' else uccelli()
    json.dump(es, open(os.path.join(PLAY, 't60_%s_%s%s.json' % (PARTE, 'rif' if RIF else 'prova', '_vbam' if os.environ.get('VBAM') else '')), 'w'), indent=1, ensure_ascii=False, default=str)
