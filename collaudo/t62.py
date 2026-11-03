#!/usr/bin/env python3
"""Collaudo 0.62: MN e strumenti chiave (Lotto 3). Solo tasti, salvo le fixture dichiarate.
Uso: python3 t62.py ROM --parte=prepara|doni|prima|sub_prima [--solo=a,b]
Ogni prova parte da prog_imola.ss (partita vera, 6 medaglie); fixture: posizione, medaglie 7-8 dove serve,
la 5a medaglia tolta per la prova del rifiuto del SUPER AMO. Lo strumento si controlla nella BORSA (lettura della RAM)."""
import os, sys, json, struct
ROM = os.path.abspath(sys.argv[1]); os.environ['ROMF'] = os.path.relpath(ROM, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'play'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import leg, vai, pl, shutil
from leg import log, A, B, PLAY, PARTE
AB = {'taglio', 'spacca', 'surf', 'forza'}
OUT = os.path.join(PLAY, 't62_%s%s.json' % (PARTE, '_vbam' if os.environ.get('VBAM') else ''))

DONI = dict(
    amo_vecchio=dict(sav='cesenatico', mappa=(34, 22), xy=(40, 18), item=0x106, flag=0x26f),
    bici_cross=dict(sav='cesenatico', mappa=(34, 42), xy=(13, 9), item=0x110, flag=0x629),
    amo_buono=dict(sav='rimini', mappa=(34, 44), xy=(11, 21), item=0x107, flag=None),
    super_amo=dict(sav='ravenna', mappa=(34, 96), xy=(64, 46), item=0x108, flag=0x62f),
    cascata=dict(sav='safari8', mappa=(26, 3), xy=(31, 34), item=0x159, flag=0x630),
    sub=dict(sav='bagno8', mappa=(35, 26), xy=(10, 26), item=0x15a, flag=0x4e6),
    flash=dict(sav='appennino', mappa=(24, 7), xy=(36, 9), item=0x157, flag=0x6d),
)
FUORI = {(34, 22): ((34, 42), 10, 15), (34, 42): ((34, 22), 35, 17), (34, 44): ((34, 45), 8, 11),
         (34, 96): ((34, 108), 8, 11), (26, 3): ((34, 94), 40, 29), (35, 26): ((35, 19), 37, 36), (24, 7): ((0, 21), 48, 18)}
PREP = dict(cesenatico=([], (34, 22), 34, 18), rimini=([], (34, 44), 9, 20), ravenna=([], (34, 96), 62, 45),
            ravenna4=([(0x86b, 0)], (34, 96), 62, 45),
            safari8=([(0x86d, 1), (0x86e, 1)], (26, 3), 29, 35), bagno8=([(0x86d, 1), (0x86e, 1)], (35, 26), 12, 25),
            bagno6=([], (35, 26), 12, 25), appennino=([], (0, 21), 48, 18))


def borsa(g):
    """Strumenti chiave (sb1+0x5D8, 30) e MT/MN (sb1+0x690, 64): numeri degli strumenti presenti."""
    sb1 = g.e.r('r32', 0x3005d8c); out = set()
    for base, n in ((0x5d8, 30), (0x690, 64), (0x560, 30)):
        raw = g.e.ram(sb1 + base, 4 * n)
        for i in range(n):
            it = struct.unpack_from('<H', raw, 4 * i)[0]
            if it: out.add(it)
    return out


def nuova(nome):
    extra, mappa, x, y = PREP[nome]
    g = leg.g_da('prog_imola.ss')
    for f, v in extra: leg.fixture_flag(g, f, v)
    leg.fixture_posizione(g, mappa, x, y)
    leg.salva(g); g.e.close()
    sav = os.path.join(PLAY, 't62_%s.sav' % nome); shutil.copy(g.sav, sav)
    g = leg.ricarica(shutil.copy(sav, os.path.join(PLAY, 'leg_prova.sav')))
    log('  ', nome, 'dal titolo:', vai.stato(g), 'medaglie', [pl.flag(g.e, f) for f in range(0x867, 0x86f)])
    g.shot('t62_%s' % nome); g.close()


def prepara():
    solo = next((a.split('=', 1)[1].split(',') for a in sys.argv if a.startswith('--solo=')), None)
    for k in (solo or PREP): nuova(k)


def apri(nome):
    sav = os.path.join(PLAY, 'leg_tmp.sav'); shutil.copy(os.path.join(PLAY, 't62_%s.sav' % nome), sav)
    g = leg.ricarica(sav); log(PARTE.upper(), os.path.basename(ROM), nome, vai.stato(g)); return g


def prendi(g, nome, c):
    e = dict(prima=c['item'] in borsa(g))
    ok = vai.vai(g, c['mappa'], *c['xy'], AB); e['arrivato'] = ok; e['pos'] = vai.stato(g)[:3]
    if not ok: log('  ', nome, 'NON arrivato', e); return e
    vis, _ = leg.parla(g, c); vis += leg.chiudi_testi(g, 30)
    e['testi'] = vis; e['dopo'] = c['item'] in borsa(g)
    if c['flag']: e['flag'] = pl.flag(g.e, c['flag'])
    vis2, _ = leg.parla(g, c); vis2 += leg.chiudi_testi(g, 30)            # seconda volta: niente doppione
    e['seconda_volta'] = vis2
    g.shot('t62_%s' % nome); log('  ', nome, json.dumps(e, ensure_ascii=False)); return e


def doni():
    es = {}; per = {}
    for nome, c in DONI.items(): per.setdefault(c['sav'], []).append(nome)
    solo = next((a.split('=', 1)[1].split(',') for a in sys.argv if a.startswith('--solo=')), None)
    for sav, nomi in per.items():
        nomi = [n for n in nomi if not solo or n in solo]
        if not nomi: continue
        g = apri(sav)
        for n in nomi: es[n] = prendi(g, n, DONI[n])
        leg.salva(g); g.e.close(); shutil.copy(g.sav, os.path.join(PLAY, 't62_%s_dopo.sav' % sav))
        g = leg.ricarica(g.sav); b = borsa(g)
        es['ricarica_' + sav] = dict(pos=vai.stato(g)[:3], strumenti={n: DONI[n]['item'] in b for n in nomi},
                                     flag={n: pl.flag(g.e, DONI[n]['flag']) for n in nomi if DONI[n]['flag']})
        log('  ricarica', sav, es['ricarica_' + sav])
        for n in nomi:                                                   # esci dalla mappa, rientra, riparla
            c = DONI[n]; f = FUORI[c['mappa']]
            uscito = vai.vai(g, f[0], f[1], f[2], AB, accanto=False) and vai.stato(g)[0] == f[0]
            tornato = vai.vai(g, c['mappa'], *c['xy'], AB)
            vis, _ = leg.parla(g, c) if tornato else ([], None); vis += leg.chiudi_testi(g, 30)
            es['rientro_' + n] = dict(uscito=uscito, fuori=f[0], tornato=tornato, testi=vis,
                                      nuovo_dono=any('ottenuto' in t for t in vis), in_borsa=c['item'] in borsa(g))
            log('  rientro', n, es['rientro_' + n])
        g.close()
    return es


def prima():
    """Senza la 5a medaglia (fixture al contrario) il pescatore di Ravenna non da' il SUPER AMO e lo dice."""
    g = apri('ravenna4'); c = DONI['super_amo']
    ok = vai.vai(g, c['mappa'], *c['xy'], AB); vis, _ = leg.parla(g, c); vis += leg.chiudi_testi(g, 30)
    e = dict(arrivato=ok, testi=vis, super_amo=c['item'] in borsa(g)); log('  senza 5a medaglia:', e); g.close(); return e


def sub_prima():
    """Con 6 medaglie (partita vera) il sommozzatore non da' SUB: testo in due righe, nessuno strumento."""
    g = apri('bagno6'); c = DONI['sub']
    ok = vai.vai(g, c['mappa'], *c['xy'], AB); vis, _ = leg.parla(g, c); vis += leg.chiudi_testi(g, 30)
    e = dict(arrivato=ok, testi=vis, sub=c['item'] in borsa(g), flag=pl.flag(g.e, c['flag']))
    log('  SUB senza 8a medaglia:', e); g.shot('t62_sub_prima'); g.close(); return e


if __name__ == '__main__':
    r = dict(prepara=prepara, doni=doni, prima=prima, sub_prima=sub_prima)[PARTE]()
    if r is not None: json.dump(r, open(OUT, 'w'), indent=1, ensure_ascii=False, default=str)
    log('FINE', PARTE)
