#!/usr/bin/env python3
"""Collaudo della consegna di SMEARGLE (pittore di Cesena, dalla 0.56) con squadra e PC entrambi pieni.
Solo tasti, salvo le fixture dichiarate, scritte in RAM prima di un SALVA vero in gioco (poi titolo -> Continua):
  - squadra a 6 copiando il Pokemon 0 negli slot 2..5 (come la prova tecnica della 0.56);
  - PC pieno: i 420 posti dei 14 box riempiti con la copia del Pokemon 0 (BoxPokemon, 80 byte);
I tre PENNELLI sono quelli raccolti a tasti nella 0.56 (savestate t56_pennelli.ss, nel labirinto della Rocca, 34.33):
da li' si va a piedi fino al pittore (32,24). (Una fixture di posizione in Cesena scritta nel labirinto lascia il
personaggio invisibile dopo Continua: non si usa.)
Uso: python3 t70.py ROM --parte=pieni|ridracoli      (mGBA: crea il salvataggio con le fixture e fa la prova)
     VBAM=1 python3 t70.py ROM --parte=pieni (VBA-M: riparte dal salvataggio fatto in mGBA)
Prova: 1) squadra e PC pieni -> il pittore tiene SMEARGLE, i pennelli restano, flag 0x7b0 a 0;
       2) al PC del Centro Pokemon di Cesena (34.26) si libera un Pokemon del box 1 (a tasti);
       3) di nuovo dal pittore -> SMEARGLE (shiny, Lv15) va nel PC, pennelli a 0, flag 0x7b0 a 1;
       4) riparlandogli non da' altro; SALVA, titolo, Continua: tutto resta.
"""
import os, sys, json, shutil, struct
ROM = os.path.abspath(sys.argv[1]); os.environ['ROMF'] = os.path.relpath(ROM, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'play'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'strumenti_rom'))
import leg, vai, pl
from leg import log, A, B, PLAY, PARTE
from drv import U, D, L, R
VBAM = bool(os.environ.get('VBAM'))
OUT = os.path.join(PLAY, 't70_%s%s.json' % (PARTE, '_vbam' if VBAM else ''))
CESENA, CENTRO = (34, 17), (34, 26)
PITTORE = (32, 24)
PENNELLO, SMEARGLE, FATTO = 0x15b, 235, 0x7b0
PARTY = 0x020244ec


def libero(g): return vai.ow(g) and g.e.ram(0x03000e41, 1)[0] == 0


def sb3(g): return g.e.r('r32', 0x3005d94)


def box(g, i):
    """(pid, otid, specie, livello? no: solo specie) del posto i (0..419) del PC; None se vuoto."""
    b = g.e.ram(sb3(g) + 4 + i * 80, 80)
    pid, otid = struct.unpack_from('<II', b, 0)
    if not pid and not otid: return None
    key = pid ^ otid; d = bytearray(b[32:80])
    for k in range(0, 48, 4): struct.pack_into('<I', d, k, struct.unpack_from('<I', d, k)[0] ^ key)
    sp = struct.unpack_from('<H', d, pl.ORDERS[pid % 24].index('G') * 12)[0]
    shiny = ((otid >> 16) ^ (otid & 0xffff) ^ (pid >> 16) ^ (pid & 0xffff)) < 8
    return dict(specie=sp, shiny=shiny)


def pc(g):
    tutti = [box(g, i) for i in range(420)]
    return dict(occupati=sum(1 for t in tutti if t), smeargle=[(i, t) for i, t in enumerate(tutti) if t and t['specie'] == SMEARGLE])


def pennelli(g):
    sb1 = g.e.r('r32', 0x3005d8c); sb2 = g.e.r('r32', 0x3005d90); key = struct.unpack('<H', g.e.ram(sb2 + 0xac, 2))[0]
    for off, n in ((0x5d8, 30), (0x560, 30)):           # tasca strumenti chiave, poi strumenti (di riserva)
        for k in range(n):
            it, q = struct.unpack('<HH', g.e.ram(sb1 + off + 4 * k, 4))
            if it == PENNELLO: return q ^ key
    return 0


def stato(g):
    return dict(pos=vai.stato(g)[:3], squadra=leg.specie_squadra(g), pennelli=pennelli(g), fatto=pl.flag(g.e, FATTO), pc=pc(g))


def fixture_pieni(g):
    src = g.e.ram(PARTY, 100)
    for i in range(len(g.party()), 6):
        for k in range(0, 100, 4): g.e.w('w32', PARTY + i * 100 + k, struct.unpack_from('<I', src, k)[0])
    g.e.w('w8', PARTY - 3, 6)
    base = sb3(g) + 4
    for i in range(420):
        for k in range(0, 80, 4): g.e.w('w32', base + i * 80 + k, struct.unpack_from('<I', src, k)[0])
    log('   FIXTURE: squadra a 6 e 420 posti del PC occupati (copie del Pokemon 0)')


def parla_pittore(g, es, nome):
    ok = vai.vai(g, CESENA, PITTORE[0] - 1, PITTORE[1], set(), accanto=False)
    vai.guarda(g, *PITTORE); g.e.run(10); g.key(A, 3, 40)
    vis = []; scatti = []
    for i in range(80):
        t = leg.testo(g)
        if t and (not vis or vis[-1] != t): vis.append(t)
        if i > 3 and libero(g):
            g.e.run(40)
            if libero(g): break
        if t and any(k in t for k in ('posto', 'PC.', 'ricevuto', 'finito')) and t not in scatti:
            scatti.append(t); g.e.run(150); g.shot('t70_%s_%d%s' % (nome, len(scatti), '_vbam' if VBAM else ''))
        g.key(B, 3, 40)                    # B: avanza i testi e dice no al soprannome
    es[nome] = dict(arrivo=ok, testi=vis, **stato(g)); log('  ', nome, json.dumps(es[nome], ensure_ascii=False))


def libera_dal_pc(g, es):
    """Centro Pokemon di Cesena (34.26), PC in (10,1): PC DI QUALCUNO -> SPOSTA POKeMON -> primo Pokemon del BOX 1
    -> LIBERA -> SI' (il cursore parte su NO) -> 'Continuare con il BOX?' B -> CIAO."""
    ok = vai.vai(g, CENTRO, 10, 2, set(), accanto=False)
    vai.guarda(g, 10, 1); g.e.run(10)
    prima = pc(g)['occupati']
    for k in 'A A A A A D D A W W A D D D D A W U A W W W W B W B W B W'.split():
        if k == 'W': g.e.run(120)
        else: g.key(dict(A=A, B=B, U=U, D=D)[k], 3, 60)
        if k == 'U': g.shot('t70_libera%s' % ('_vbam' if VBAM else ''))
    for i in range(30):
        if libero(g): break
        g.key(B, 3, 60)
    es['libera'] = dict(arrivo=ok, pc_prima=prima, **stato(g)); log('   libera', json.dumps(es['libera'], ensure_ascii=False))


def apri():
    sav = os.path.join(PLAY, 't70_pieni.sav')
    if not VBAM:
        g = leg.g_da('t56_pennelli.ss')
        fixture_pieni(g)
        leg.salva(g); g.e.close(); shutil.copy(g.sav, sav)
    g = leg.ricarica(shutil.copy(sav, os.path.join(PLAY, 'leg_tmp.sav')))
    log('PROVA', PARTE, 'VBA-M' if VBAM else 'mGBA', os.path.basename(ROM), os.path.basename(sav))
    return g


def pieni():
    g = apri(); es = dict(partenza=stato(g)); log('  partenza', json.dumps(es['partenza'], ensure_ascii=False))
    parla_pittore(g, es, 'pieni')
    libera_dal_pc(g, es)
    parla_pittore(g, es, 'consegna')
    parla_pittore(g, es, 'dopo')
    leg.salva(g); g.e.close()
    g = leg.ricarica(g.sav); es['ricaricato'] = stato(g); log('   ricaricato', json.dumps(es['ricaricato'], ensure_ascii=False))
    g.close(); return es


def viaggio(g, es, nome, mappa, da, xy):
    """Parla alla guida in xy (da `da`), risponde si' (A) e aspetta l'arrivo con il personaggio libero."""
    ok = vai.vai(g, mappa, *da, AB, accanto=False)
    vai.guarda(g, *xy); g.e.run(10); g.key(A, 3, 40)
    vis = []
    for i in range(120):
        t = leg.testo(g)
        if t and (not vis or vis[-1] != t): vis.append(t)
        if i > 3 and libero(g) and vai.stato(g)[0] != mappa:
            g.e.run(60)
            if libero(g): break
        g.key(A, 3, 40)
    es[nome] = dict(arrivo=ok, testi=vis, dopo=vai.stato(g)[:3]); log('  ', nome, json.dumps(es[nome], ensure_ascii=False))


AB = {'taglio', 'spacca', 'forza', 'surf'}
SENTIERO, VALLE = (35, 10), (35, 50)


def ridracoli():
    """Guida per Ridracoli sul Sentiero del Fumaiolo (35.10, 17,96) -> valle di Ridracoli (35.50); la guida del
    sentiero in 35.50 riporta al Sentiero; prima, la guida per Forli' di 35.50 (20,34) -> Forli' e la guida di Forli'
    (39,51) -> di nuovo 35.50; poi a piedi giu' dalle frecce (18-20,99) fino a Cesena.
    Fixture (prima di un SALVA vero): 7a medaglia 0x86D, ALDO gia' affrontato 0x496 (come nella 0.66),
    posizione sul Sentiero (17,97). Partenza prog_imola.ss (6 medaglie)."""
    sav = os.path.join(PLAY, 't70_ridracoli.sav')
    if not VBAM:
        g = leg.g_da('prog_imola.ss')
        leg.fixture_flag(g, 0x86D); leg.fixture_flag(g, 0x496); leg.fixture_posizione(g, SENTIERO, 17, 97)
        leg.salva(g); g.e.close(); shutil.copy(g.sav, sav)
    g = leg.ricarica(shutil.copy(sav, os.path.join(PLAY, 'leg_tmp.sav')))
    log('PROVA', PARTE, 'VBA-M' if VBAM else 'mGBA', os.path.basename(ROM), os.path.basename(sav), vai.stato(g))
    es = {}
    viaggio(g, es, 'andata', SENTIERO, (17, 97), (17, 96))
    g.shot('t70_valle%s' % ('_vbam' if VBAM else ''))
    viaggio(g, es, 'forli', VALLE, (20, 35), (20, 34))
    g.shot('t70_forli%s' % ('_vbam' if VBAM else ''))
    viaggio(g, es, 'di_nuovo_valle', (34, 68), (39, 52), (39, 51))
    viaggio(g, es, 'ritorno', VALLE, (31, 35), (31, 34))
    ok = vai.vai(g, (34, 17), 46, 46, AB, accanto=False)
    es['cesena'] = dict(arrivo=ok, pos=vai.stato(g)[:3]); log('   cesena', es['cesena'])
    g.shot('t70_cesena%s' % ('_vbam' if VBAM else ''))
    g.close(); return es


if __name__ == '__main__':
    r = dict(pieni=pieni, ridracoli=ridracoli)[PARTE]()
    json.dump(r, open(OUT, 'w'), indent=1, ensure_ascii=False, default=str)
    log('FINE', PARTE)
