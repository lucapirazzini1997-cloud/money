#!/usr/bin/env python3
"""Collaudo 0.65: Ridracoli (35.51 ridisegnata) e il GYARADOS rosso. Solo tasti, salvo le fixture dichiarate.
Uso: python3 t65.py ROM --parte=prima|gyarados|sorgente|crea64|vecchio64
  prima     da prog_imola.ss (6 medaglie, Blaziken 50, Breloom 43). Fixture: 7a medaglia (0x86D, la chiede la guida
            di Forli'), posizione a Forli' vicino alla guida (34.68). Si parla con la guida -> 35.50 -> 35.51;
            GYARADOS nascosto; custode; cartello della diga; centrale (35.52) e ritorno dalla porta;
            escursionista; scala nel muro; pescatore; recluta del coronamento (vista); CORRADO rifiuta finche' manca
            una recluta; recluta della riva (vista); CORRADO -> il GYARADOS emerge; SALVA e Continua (GYARADOS
            ancora li'). Il salvataggio finale serve alla parte "gyarados".
  gyarados  dal salvataggio finale di "prima". Fixture: SURF a Breloom, 5 MASTER BALL. Coronamento -> SURF ->
            GYARADOS: fuga (resta), KO (resta), cattura con MASTER BALL: cromatico? flag, oggetto sparito, testi di
            CORRADO e del custode; SALVA e Continua; uscita a 35.50 e ritorno: il GYARADOS non c'e'.
  sorgente  da prog_imola.ss. Fixture: 7a e 8a medaglia, SURF e CASCATA a Breloom, posizione in 35.51 (24,41).
            Lago -> cascata del Bidente -> riva della sorgente: cartello, Poke Ball (ACQUA MAGICA nella borsa).
  crea64    sulla ROM 0.64: da prog_imola.ss, fixture posizione in 35.51 (35,29) (sentiero nella 0.64, lago nella
            0.65), SALVA vero -> play/t65_crea64.sav.
  vecchio64 sulla 0.65 con t65_crea64.sav: Continua; il giocatore torna una volta sola sulla strada sotto la diga
            (24,41); si cammina; SALVA e Continua: si resta li'.
"""
import os, sys, json, shutil, struct
ROM = os.path.abspath(sys.argv[1]); os.environ['ROMF'] = os.path.relpath(ROM, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'play'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'strumenti_rom'))
import leg, vai, pl, romlib
from leg import log, A, B, PLAY, PARTE
from drv import U as SU, D as SD, L as SL, R as SR
K = (35, 51)
VBAM = bool(os.environ.get('VBAM'))
OUT = os.path.join(PLAY, 't65_%s%s.json' % (PARTE, '_vbam' if VBAM else ''))
_R = romlib.Rom(ROM)
AB = {'taglio', 'spacca', 'forza'}
GY = dict(xy=(22, 27), gfx=184)
ALL = {'GIANNI': (21, 52, 31, 581), 'ERMES': (12, 34, 49, 633), 'RECLUTA_DIGA': (31, 34, 119, 634),
       'RECLUTA_RIVA': (40, 27, 119, 851), 'CORRADO': (40, 15, 196, 734)}


def numeri():
    """Flag e variabile della 0.65 lette dalla ROM (oggetto 1 = GYARADOS, oggetto 8 = Poke Ball, script d'ingresso)."""
    m = _R.map(*K); ms = dict(_R.map_scripts(m)); d = _R.data
    nascosto = m['objects'][0]['flag']; palla = m['objects'][7]['flag']
    p = ms.get(3); var = struct.unpack_from('<H', d, p + 1)[0] if p is not None and d[p] == 0x16 else None
    # nello script d'ingresso: setvar, checkflag PRESO, goto_if ...
    preso = struct.unpack_from('<H', d, p + 6)[0] if p is not None and d[p + 5] == 0x2b else None
    return nascosto, preso, palla, var


F_NASCOSTO, F_PRESO, F_ACQUA, NUOVA = numeri() if _R.map(*K)['height'] == 62 else (None, None, None, None)


def flags(g):
    return dict(nascosto=pl.flag(g.e, F_NASCOSTO), preso=pl.flag(g.e, F_PRESO), acqua=pl.flag(g.e, F_ACQUA),
                allenatori={n: pl.flag(g.e, 0x500 + v[3]) for n, v in ALL.items()}) if F_NASCOSTO else {}


def oggetti(g):
    return sorted(g.lobjs_gfx()) if vai.stato(g)[0] == K else None


def gyarados_presente(g):
    return vai.stato(g)[0] == K and any(gf == 184 for _, gf in g.lobjs_gfx())


def apri(start, fix, nome=None):
    """start: savestate (.ss) o salvataggio (.sav). Le fixture si scrivono in mGBA, poi SALVA vero e Continua;
    VBA-M riparte dallo stesso .sav fatto in mGBA."""
    sav = os.path.join(PLAY, 't65_%s.sav' % (nome or PARTE))
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
    """Come leg.chiudi_testi (solo B), ma a "Smettere di imparare ...?" risponde si' (A): dopo una lotta vinta un
    Pokemon puo' voler imparare una mossa, e con il solo B la domanda si ripete."""
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
    """leg.ko fino alla fine della lotta. Se dopo un KO il pilota resta nel menu della squadra (in VBA-M a volte
    apre la scheda del Pokemon invece di mandarlo in campo): B esce dalla scheda, A su "Cosa vuoi fare?" lo manda
    in campo, poi si continua a lottare."""
    info = []
    for _ in range(8):
        info += leg.ko(g)
        if vai.ow(g): break
        for _ in range(20):
            t = leg.testo(g)
            if g.cb2() == pl.BATCB and g.e.r('r32', 0x3005d60) == pl.ACT: break
            if vai.ow(g): break
            if 'Natura' in t: g.key(B, 3, 40)
            else: g.key(A, 3, 40)
    return info


def in_lotta(g):
    return not vai.ow(g)


def vai_e(g, es, nome, mappa, x, y, ab=AB, accanto=True):
    """vai.vai; se parte una lotta (allenatore che vede il giocatore) la si combatte e si riprova."""
    lotte = []
    for _ in range(4):
        ok = vai.vai(g, mappa, x, y, ab, accanto=accanto)
        if ok or vai.ow(g): break
        info = leg.ko(g); lotte.append(sorted({(i[3], i[4]) for i in info})); chiudi(g, 20)
    es[nome] = dict(ok=ok, pos=vai.stato(g)[:3], lotte=lotte, **flags(g)); log('  ', nome, es[nome]); return ok


def passo(g, dn, n=1):
    for _ in range(n): g.step(dn); g.e.run(10)


def lotta_vista(g, es, nome, dn):
    """Un passo verso la linea di vista dell'allenatore: deve partire da solo (presentazione, lotta)."""
    x, y, gfx, tid = ALL[nome]
    cura(g)
    p0 = vai.stato(g)[:3]; vis = []
    g.step(dn)
    for i in range(80):
        t = leg.testo(g)
        if t and (not vis or vis[-1] != t): vis.append(t)
        if in_lotta(g): break
        if i > 10 and vai.ow(g) and g.e.ram(0x03000e41, 1)[0] == 0 and not t: g.e.run(20)
        g.key(A, 3, 30) if t else g.e.run(20)
    lotta_ = in_lotta(g)
    info = lotta(g) if lotta_ else []
    dopo = chiudi(g, 20)
    es['vista_' + nome] = dict(da=p0, testi=vis, lotta=lotta_, squadra=sorted({(i[3], i[4]) for i in info}),
                               dopo=dopo, flag=pl.flag(g.e, 0x500 + tid), pos=vai.stato(g)[:3])
    log('  ', nome, es['vista_' + nome])


def lotta_parla(g, es, nome, chiave=None):
    x, y, gfx, tid = ALL[nome]
    tentativi = []
    for _ in range(3):
        ok = vai.vai(g, K, x, y, AB); cura(g)
        vis, lotta = leg.parla(g, dict(xy=(x, y), gfx=gfx))
        info = leg.ko(g) if lotta else []
        dopo = chiudi(g, 30)
        flag = pl.flag(g.e, 0x500 + tid)
        tentativi.append(dict(arrivo=ok, testi=vis, lotta=lotta, squadra=sorted({(i[3], i[4]) for i in info}),
                              dopo=dopo, flag=flag))
        if flag or not lotta: break
    vis2, lotta2 = leg.parla(g, dict(xy=(x, y), gfx=gfx)); chiudi(g, 10)
    es[chiave or 'lotta_' + nome] = dict(tentativi=tentativi, flag=flag, di_nuovo=vis2, di_nuovo_lotta=lotta2, **flags(g))
    log('  ', nome, es[chiave or 'lotta_' + nome])


def prima():
    g = apri('prog_imola.ss', [lambda g: leg.fixture_flag(g, 0x86d, 1),
                               lambda g: leg.fixture_posizione(g, (34, 68), 39, 54)])
    es = dict(medaglie=[pl.flag(g.e, f) for f in range(0x867, 0x86f)], numeri=dict(
        nascosto=hex(F_NASCOSTO), preso=hex(F_PRESO), acqua=hex(F_ACQUA), var=hex(NUOVA)))
    # la guida di Forli' (oggetto a 39,51)
    ok = vai.vai(g, (34, 68), 39, 51, AB)
    vai.guarda(g, 39, 51); g.key(A, 3, 60)
    vis = []
    for i in range(60):
        t = leg.testo(g)
        if t and (not vis or vis[-1] != t): vis.append(t)
        if vai.stato(g)[0] == (35, 50) and vai.ow(g) and g.e.ram(0x03000e41, 1)[0] == 0: break
        g.key(A, 3, 40)
    g.e.run(60)
    es['guida_forli'] = dict(arrivo=ok, testi=vis, pos=vai.stato(g)[:3]); log('  guida', es['guida_forli'])
    for nome, (x, y) in dict(cartello_3550=(16, 31)).items():
        es[nome] = leggi_testi(g, (35, 50), x, y)
    vai.vai(g, (35, 50), 25, 6, AB); vis, _ = leg.parla(g, dict(xy=(25, 6), gfx=55))
    es['custode_3550'] = vis + chiudi(g, 10); log('   custode 35.50', es['custode_3550'])
    vai_e(g, es, 'arrivo_3551', K, 24, 60, accanto=False)
    es['oggetti_arrivo'] = oggetti(g); es['gyarados_arrivo'] = gyarados_presente(g)
    es['cartello_diga'] = leggi_testi(g, K, 22, 39)
    vai.vai(g, K, 31, 45, AB); vis, _ = leg.parla(g, dict(xy=(31, 45), gfx=55)); es['custode_prima'] = vis + chiudi(g, 10)
    log('   custode', es['custode_prima'])
    vai_e(g, es, 'centrale', (35, 52), 14, 25, accanto=False)
    vai_e(g, es, 'uscita_centrale', K, 28, 44, accanto=False)
    lotta_parla(g, es, 'GIANNI')
    vai_e(g, es, 'scala', K, 24, 35, accanto=False)
    lotta_parla(g, es, 'ERMES')
    vai_e(g, es, 'prima_della_recluta', K, 30, 35, accanto=False)
    lotta_vista(g, es, 'RECLUTA_DIGA', 'R')
    vai_e(g, es, 'riva_est', K, 39, 31, accanto=False)
    # CORRADO prima della seconda recluta: rifiuta la lotta (si passa lungo x=39, fuori dalla vista della recluta,
    # che guarda in basso da 40,27 per 3 caselle)
    vai_e(g, es, 'verso_corrado', K, 39, 15, accanto=False)
    vis, lotta_p = premi_a(g, 40, 15)
    es['corrado_presto'] = dict(testi=vis, lotta=lotta_p, **flags(g)); log('  corrado presto', es['corrado_presto'])
    vai_e(g, es, 'sotto_recluta', K, 39, 31, accanto=False)
    passo(g, 'R'); es['sotto_recluta']['dopo_passo'] = vai.stato(g)[:3]
    lotta_vista(g, es, 'RECLUTA_RIVA', 'U')
    # CORRADO: lotta, poi il GYARADOS emerge
    passo(g, 'L')            # la recluta, avvicinandosi, e' rimasta a (40,29): si sale lungo x=39
    vai_e(g, es, 'da_corrado', K, 39, 15, accanto=False); cura(g)
    vai.guarda(g, 40, 15); g.key(A, 3, 60)
    vis = []
    for i in range(60):
        t = leg.testo(g)
        if t and (not vis or vis[-1] != t): vis.append(t)
        if in_lotta(g): break
        g.key(A, 3, 40)
    info = lotta(g) if in_lotta(g) else []
    dopo = chiudi(g, 40)
    es['corrado'] = dict(testi=vis, lotta=bool(info), squadra=sorted({(i[3], i[4]) for i in info}), dopo=dopo,
                         gyarados=gyarados_presente(g), oggetti=oggetti(g), **flags(g))
    log('  corrado', es['corrado'])
    vis, _ = leg.parla(g, dict(xy=(40, 15), gfx=196)); es['corrado_dopo'] = vis + chiudi(g, 10)
    vai.vai(g, K, 31, 45, AB); vis, _ = leg.parla(g, dict(xy=(31, 45), gfx=55)); es['custode_dopo'] = vis + chiudi(g, 10)
    vai_e(g, es, 'coronamento', K, 22, 34, accanto=False)
    leg.salva(g); g.e.close(); shutil.copy(g.sav, os.path.join(PLAY, 't65_prima_fine%s.sav' % ('_vbam' if VBAM else '')))
    g = leg.ricarica(g.sav)
    es['ricarica'] = dict(pos=vai.stato(g)[:3], gyarados=gyarados_presente(g), var_nuova=g.var(NUOVA), **flags(g))
    g.e.run(120); es['ricarica_dopo_2s'] = vai.stato(g)[:3]
    g.shot('t65_prima'); g.close(); return es


def premi_a(g, x, y):
    """Girato verso (x, y), A; aspetta che lo script parta (al massimo due tentativi). Poi i testi fino alla fine."""
    vai.guarda(g, x, y); g.e.run(10)
    for _ in range(2):
        g.key(A, 3, 30)
        for _ in range(20):
            if g.e.ram(0x03000e41, 1)[0] or not vai.ow(g): break
            g.e.run(5)
        if g.e.ram(0x03000e41, 1)[0] or not vai.ow(g): break
    vis = []
    for i in range(40):
        t = leg.testo(g)
        if t and (not vis or vis[-1] != t): vis.append(t)
        if not vai.ow(g): return vis, True
        if g.e.ram(0x03000e41, 1)[0] == 0:
            g.e.run(20)
            if g.e.ram(0x03000e41, 1)[0] == 0: return vis, False
        g.key(B, 3, 40)
    return vis, not vai.ow(g)


def leggi_testi(g, mappa, x, y, ab=AB):
    if not vai.vai(g, mappa, x, y, ab): log('   non arrivo accanto a', (x, y)); return None
    t, _ = premi_a(g, x, y); log('   cartello', (x, y), t); return t


def cura(g):
    """FIXTURE DICHIARATA: squadra curata (PS al massimo, niente stato) prima di una lotta. La squadra di prova ha
    solo due Pokemon e a Ridracoli non c'e' un Centro: serve a non perdere per sfinimento, non a vincere una lotta
    che si perderebbe da curati."""
    for k in range(len(g.party())):
        a = 0x20244ec + k * 100
        g.e.w('w32', a + 80, 0); g.e.w('w16', a + 86, g.e.r('r16', a + 88))
    log('   FIXTURE: squadra curata', g.party())


def shiny(g, slot):
    b = g.e.ram(0x20244ec + slot * 100, 8); pid, otid = struct.unpack('<II', b)
    return ((otid >> 16) ^ (otid & 0xffff) ^ (pid >> 16) ^ (pid & 0xffff)) < 8


def gyarados():
    g = apri('t65_prima_fine.sav', [lambda g: leg.fixture_mossa(g, 1, 3, 57, 15), leg.fixture])
    es = dict(inizio=dict(gyarados=gyarados_presente(g), **flags(g)))
    AB2 = AB | {'surf'}
    vai_e(g, es, 'al_gyarados', K, 22, 27, AB2)
    es['in_surf'] = bool(g.e.ram(0x02037590, 1)[0] & 8)
    cura(g); vis, lotta = leg.parla(g, GY); es['parla'] = dict(testi=vis, lotta=lotta)
    leg.fuggi(g); vis = chiudi(g)
    es['fuga'] = dict(testi=vis, presente=gyarados_presente(g), pos=vai.stato(g)[:3], **flags(g)); log('  fuga', es['fuga'])
    cura(g); vis, lotta = leg.parla(g, GY)
    info = leg.ko(g) if lotta else []; vis2 = chiudi(g, 40)
    es['ko'] = dict(testi=vis + vis2, lotta=lotta, turni=len(info), avversario=sorted({(i[3], i[4]) for i in info}),
                    presente=gyarados_presente(g), pos=vai.stato(g)[:3], **flags(g)); log('  KO', es['ko'])
    if vai.stato(g)[0] != K: vai_e(g, es, 'torna', K, 22, 27, AB2)
    cura(g); vis, lotta = leg.parla(g, GY)
    n0 = len(g.party())
    if lotta:
        leg.menu_lotta(g); g.throw(); vis2 = chiudi(g, 40)
    else: vis2 = []
    sq = leg.specie_squadra(g)
    es['cattura'] = dict(testi=vis + vis2, lotta=lotta, squadra=sq, livello=g.party()[-1] if len(g.party()) > n0 else None,
                         cromatico=shiny(g, len(g.party()) - 1) if len(g.party()) > n0 else None,
                         presente=gyarados_presente(g), oggetti=oggetti(g), **flags(g)); log('  cattura', es['cattura'])
    try: vis, _ = leg.parla(g, GY); es['parla_dopo'] = vis + chiudi(g, 10)
    except KeyError: es['parla_dopo'] = 'non accanto: %s' % (vai.stato(g)[:3],)
    vai_e(g, es, 'verso_corrado', K, 39, 15, AB2, accanto=False)
    vis, _ = leg.parla(g, dict(xy=(40, 15), gfx=196)); es['corrado_calmo'] = vis + chiudi(g, 10)
    vai.vai(g, K, 31, 45, AB2); vis, _ = leg.parla(g, dict(xy=(31, 45), gfx=55)); es['custode_calmo'] = vis + chiudi(g, 10)
    log('  testi dopo', es['corrado_calmo'], es['custode_calmo'])
    leg.salva(g); g.e.close(); g = leg.ricarica(g.sav)
    es['ricarica'] = dict(pos=vai.stato(g)[:3], gyarados=gyarados_presente(g), squadra=leg.specie_squadra(g), **flags(g))
    vai_e(g, es, 'esce_3550', (35, 50), 18, 3, AB2, accanto=False)
    vai_e(g, es, 'rientra', K, 24, 58, AB2, accanto=False)
    es['rientro'] = dict(gyarados=gyarados_presente(g), oggetti=oggetti(g))
    g.shot('t65_gyarados'); g.close(); return es


def borsa(g):
    sb1 = g.e.r('r32', 0x3005d8c); sb2 = g.e.r('r32', 0x3005d90); key = struct.unpack('<H', g.e.ram(sb2 + 0xac, 2))[0]
    raw = g.e.ram(sb1 + 0x560, 120)
    return [(i, q ^ key) for i, q in struct.iter_unpack('<HH', raw) if i]


def sorgente():
    g = apri('prog_imola.ss', [lambda g: leg.fixture_flag(g, 0x86d, 1), lambda g: leg.fixture_flag(g, 0x86e, 1),
                               lambda g: leg.fixture_mossa(g, 1, 3, 57, 15), lambda g: leg.fixture_mossa(g, 1, 2, 127, 15),
                               lambda g: leg.fixture_posizione(g, K, 24, 41)])
    es = dict(inizio=dict(borsa_d1=[x for x in borsa(g) if x[0] == 0xd1], **flags(g)))
    AB3 = AB | {'surf', 'cascata'}
    vai_e(g, es, 'senza_cascata', K, 10, 8, AB | {'surf'}, accanto=False)          # deve fallire
    # ai piedi della cascata del Bidente (12,13) in SURF; A verso la cascata, "si'": si risale fino al laghetto alto
    vai_e(g, es, 'piede_cascata', K, 12, 13, AB | {'surf'}, accanto=False)
    vai.guarda(g, 12, 12); g.key(A, 3, 60); vis = []
    for i in range(80):
        t = leg.testo(g)
        if t and (not vis or vis[-1] != t): vis.append(t)
        if i > 5 and vai.ow(g) and g.e.ram(0x03000e41, 1)[0] == 0 and vai.stato(g)[2] < 10: break
        g.key(A, 3, 40) if '?' in t or i < 4 else g.e.run(30)
    g.e.run(60)
    es['cascata'] = dict(testi=vis, pos=vai.stato(g)[:3], surf=bool(g.e.ram(0x02037590, 1)[0] & 8)); log('  cascata', es['cascata'])
    vai_e(g, es, 'riva_sorgente', K, 10, 8, AB | {'surf'}, accanto=False)
    es['cartello'] = leggi_testi(g, K, 9, 5)
    vai.vai(g, K, 9, 8, AB3); vai.guarda(g, 9, 8); g.key(A, 3, 60); vis = chiudi(g, 30)
    es['palla'] = dict(testi=vis, borsa_d1=[x for x in borsa(g) if x[0] == 0xd1], oggetti=oggetti(g), **flags(g))
    log('  palla', es['palla'])
    leg.salva(g); g.e.close(); g = leg.ricarica(g.sav)
    es['ricarica'] = dict(pos=vai.stato(g)[:3], oggetti=oggetti(g), borsa_d1=[x for x in borsa(g) if x[0] == 0xd1], **flags(g))
    g.shot('t65_sorgente'); g.close(); return es


def crea64():
    """Sulla ROM 0.64: un salvataggio vero dentro 35.51 in una casella che nella 0.65 e' lago."""
    sav = os.path.join(PLAY, 't65_crea64.sav')
    g = leg.g_da('prog_imola.ss'); leg.fixture_flag(g, 0x86d, 1); leg.fixture_posizione(g, K, 35, 29)
    leg.salva(g); g.e.close(); shutil.copy(g.sav, sav)
    g = leg.ricarica(shutil.copy(sav, os.path.join(PLAY, 'leg_tmp.sav')))
    es = dict(pos_064=vai.stato(g)[:3]); log('  crea64', es); g.shot('t65_crea64'); g.close(); return es


def vecchio(savname):
    log('PROVA', PARTE, 'VBA-M' if VBAM else 'mGBA', os.path.basename(ROM), savname)
    g = leg.ricarica(shutil.copy(os.path.join(PLAY, savname), os.path.join(PLAY, 'leg_tmp.sav')))
    es = dict(titolo=vai.stato(g)[:3], var_nuova=g.var(NUOVA))
    g.e.run(240); chiudi(g, 5)
    es['dopo_4s'] = dict(pos=vai.stato(g)[:3], var_nuova=g.var(NUOVA), oggetti=oggetti(g), **flags(g))
    log('  ', es)
    vai_e(g, es, 'cammina', K, 24, 45, accanto=False)
    leg.salva(g); g.e.close(); g = leg.ricarica(g.sav)
    es['ricarica'] = dict(pos=vai.stato(g)[:3], var_nuova=g.var(NUOVA)); g.e.run(240)
    es['ricarica_dopo_4s'] = vai.stato(g)[:3]
    vai_e(g, es, 'verso_3550', (35, 50), 18, 3, accanto=False)
    g.shot('t65_' + PARTE); g.close(); return es


if __name__ == '__main__':
    r = dict(prima=prima, gyarados=gyarados, sorgente=sorgente, crea64=crea64,
             vecchio64=lambda: vecchio('t65_crea64.sav'))[PARTE]()
    json.dump(r, open(OUT, 'w'), indent=1, ensure_ascii=False, default=str)
    log('FINE', PARTE)
