#!/usr/bin/env python3
"""Collaudo 0.59: i tre cani (Lotto 2). Solo tasti; le fixture sono dichiarate in fixture() e nella relazione.
Uso: python3 t59.py ROM --parte=viaggio|...   (i savestate intermedi vanno in play/t59_*.ss)"""
import os, sys, struct
ROM = os.path.abspath(sys.argv[1]); os.environ['ROMF'] = os.path.relpath(ROM, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'play'))
PARTE = next((a.split('=')[1] for a in sys.argv if a.startswith('--parte=')), 'viaggio')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vai, pl
from pl import log, A, B
AB = {'taglio', 'spacca'}

def g_da(state, sav=None):
    from drv import Emu
    if sav is None:
        sav = os.path.join(pl.P, 't59_tmp.sav')
        with open(sav, 'wb') as f: f.write(open(os.path.join(pl.P, 'p51.sav'), 'rb').read())
    g = pl.G.__new__(pl.G); g.e = Emu(pl.ROM, sav); g.e.run(10); g.e.load(pl.P + state); g.e.run(120); g.OW = pl.OW
    g.sav = sav
    for _ in range(3): g.key(B, 2, 20)
    log('T59', PARTE, os.path.basename(ROM), 'partenza', state, vai.stato(g), 'cb2', hex(g.cb2()))
    return g

if PARTE == 'viaggio':
    g = g_da('gpre.ss')
    ok = vai.vai(g, (34, 94), 20, 20, AB); log('  Ravenna', ok, vai.stato(g)); g.save('t59_ravenna.ss'); g.shot('t59_ravenna')
    ok = vai.vai(g, (26, 12), 6, 23, AB); log('  accanto a Raikou', ok, vai.stato(g)); g.save('t59_raikou.ss'); g.shot('t59_raikou')
    g.close()

# ------------------------------------------------------------------ evento di un cane
import shutil
from drv import Emu, U, D, L, R, START
PLAY = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'play')
CANI = dict(raikou=dict(stato='t59_raikou.ss', mappa=(26, 12), xy=(6, 23), gfx=216, flag=0x884, specie=243,
                        fuori=((35, 100), 10, 18)),
            entei=dict(stato='t59_entei.ss', mappa=(35, 100), xy=(10, 4), gfx=217, flag=0x88f, specie=244,
                       fuori=((26, 12), 21, 6)),
            suicune=dict(stato='t59_suicune.ss', mappa=(26, 13), xy=(31, 29), gfx=230, flag=0x887, specie=245,
                         fuori=((26, 3), 38, 16)))

import scr as _scr
def testo(g):
    if g.cb2() == pl.BATCB: return pl.msg(g.e)
    return _scr.text(g.e.ram(0x02021fc4, 200), 0, 200).replace(' / ', ' ')

def chiudi_testi(g, n=60, tag=None):
    """Fine lotta e testi dello script: solo B (avanza i testi, dice no al soprannome, non riparla col Pokemon)."""
    vis = []
    for i in range(n):
        t = testo(g)
        if t and (not vis or vis[-1] != t): vis.append(t)
        if vai.ow(g) and g.e.ram(0x03000e41, 1)[0] == 0:
            g.e.run(30)
            if vai.ow(g) and g.e.ram(0x03000e41, 1)[0] == 0: break
        g.key(B, 3, 40)
    return vis

def menu_lotta(g, maxi=80):
    for _ in range(maxi):
        if g.e.r('r32', 0x3005d60) == pl.ACT: return True
        if vai.ow(g) and g.e.ram(0x03000e41, 1)[0] == 0: return False
        g.key(B, 2, 20)
    return False

def fuggi(g):
    for t in range(12):
        if not menu_lotta(g): break
        g.key(D, 3, 10); g.key(R, 3, 10); g.key(A, 3, 60)
        for _ in range(30):
            if vai.ow(g) or g.e.r('r32', 0x3005d60) == pl.ACT: break
            g.key(B, 2, 20)
    g.e.run(30)

TRANSIZIONI = {0x8036f75, 0x8086035}         # entrata in lotta, ritorno al campo

def ko(g):
    """Combatte fino alla fine (mosse migliori, come pl.G.battle) ma senza mai premere A nel campo."""
    e = g.e; info = []
    for i in range(900):
        if vai.ow(g): break
        if g.cb2() in TRANSIZIONI: e.run(20); continue
        if g.cb2() == pl.BATCB and e.r('r32', 0x3005d60) == pl.ACT:
            e.key(U, 2, 4); e.key(L, 2, 4); e.key(A, 2, 20)
            if e.r('r32', 0x3005d60) == pl.MOVE:
                k, me, fo = pl.best_move(e); info.append((me['sp'], me['lv'], me['hp'], fo['sp'], fo['lv'], fo['hp']))
                e.key(U, 3, 10); e.key(L, 3, 10)
                if k & 1: e.key(R, 3, 10)
                if k & 2: e.key(D, 3, 10)
                e.key(A, 2, 30)
        elif g.cb2() != pl.BATCB:                  # menu squadra dopo un KO: manda il primo Pokemon in grado
            for k in range(6):
                if g.party()[k][1] > 0 if k < len(g.party()) else False: break
            e.run(30)
            for _ in range(k): e.key(D, 3, 20)
            e.key(A, 3, 40); e.key(A, 3, 60)
        elif 'prossimo' in testo(g).lower(): e.key(A, 2, 60)       # "Usare il prossimo POKeMON?" -> si
        else: e.key(B, 2, 18)
    return info

def parla(g, c):
    vai.guarda(g, *c['xy']); g.key(A, 3, 60)
    vis = []
    for i in range(40):
        t = testo(g)
        if t and (not vis or vis[-1] != t): vis.append(t)
        if not vai.ow(g): return vis, True
        if i > 3 and g.e.ram(0x03000e41, 1)[0] == 0: return vis, False
        g.key(A, 3, 40)
    return vis, not vai.ow(g)

def presente(g, c): return any(gf == c['gfx'] for _, gf in g.lobjs_gfx())

def esci_e_torna(g, c):
    k, x, y = c['fuori']
    vai.vai(g, k, x, y, AB | {'surf'}, accanto=False); log('   uscito in', vai.stato(g)[:3])
    ok = vai.vai(g, c['mappa'], *c['xy'], AB | {'surf'}); log('   tornato', ok, vai.stato(g)[:3])

def fixture(g):
    """FIXTURE DICHIARATE (scritture in RAM, non prove): 5 MASTER BALL in testa alla tasca Poke Ball."""
    sb1 = g.e.r('r32', 0x3005d8c); sb2 = g.e.r('r32', 0x3005d90); key = struct.unpack('<H', g.e.ram(sb2 + 0xac, 2))[0]
    b = g.e.ram(sb1 + 0x650, 8)
    g.e.w('w16', sb1 + 0x654, struct.unpack_from('<H', b, 0)[0]); g.e.w('w16', sb1 + 0x656, struct.unpack_from('<H', b, 2)[0])
    g.e.w('w16', sb1 + 0x650, 1); g.e.w('w16', sb1 + 0x652, 5 ^ key)
    log('   FIXTURE: 5 MASTER BALL nella tasca Poke Ball')

def fixture_surf(g, slot=1, mossa=3):
    """FIXTURE DICHIARATA: il Pokemon in `slot` impara SURF (57) al posto della mossa `mossa` (scrittura in RAM,
    dati cifrati e checksum ricalcolati). Serve solo ad avere SURF: se si ottiene in gioco lo verifica il Lotto 3."""
    a = 0x20244ec + slot * 100; b = bytearray(g.e.ram(a, 100))
    pid, otid = struct.unpack_from('<II', b, 0); key = pid ^ otid
    data = bytearray(b[32:80])
    for k in range(0, 48, 4): struct.pack_into('<I', data, k, struct.unpack_from('<I', data, k)[0] ^ key)
    o = pl.ORDERS[pid % 24]; ia = o.index('A') * 12
    struct.pack_into('<H', data, ia + 2 * mossa, 57); data[ia + 8 + mossa] = 15
    struct.pack_into('<H', b, 28, sum(struct.unpack('<24H', bytes(data))) & 0xffff)
    for k in range(0, 48, 4): struct.pack_into('<I', data, k, struct.unpack_from('<I', data, k)[0] ^ key)
    b[32:80] = data
    for i in range(0, 100, 2): g.e.w('w16', a + i, struct.unpack_from('<H', b, i)[0])
    log('   FIXTURE: SURF al Pokemon', slot, '->', g.mon_moves(slot))

def salva(g):
    for _ in range(4): g.key(B, 3, 25)
    sb = os.path.getsize(g.sav)
    g.key(START, 3, 50)
    for _ in range(10):
        if g.e.ram(0x203760e, 1)[0] == 4: break
        g.key(D, 3, 15)
    for k in 'A..A......A......':
        if k == 'A': g.key(A, 3, 40)
        else: g.e.run(60)
        if 'Sovrascrivere' in testo(g) or 'sovrascriv' in testo(g).lower(): pass
    log('   salvataggio: testo finale', testo(g)); g.e.sync()

def ricarica(sav, rom=None):
    g = pl.G.__new__(pl.G); g.sav = sav; g.e = Emu(rom or pl.ROM, sav); g.e.run(10); g.OW = pl.OW
    for i, k in enumerate('......T...A...A......A......'):
        if k == 'A': g.key(A, 3, 40)
        elif k == 'T': g.key(START, 3, 40)
        else: g.e.run(60)
        if i in (6, 10, 14, 21): g.shot('t59_titolo_%d' % i)
    for _ in range(20):
        if vai.ow(g) and vai.stato(g)[0] != (0, 0): break
        g.key(A, 3, 40)
    return g

def specie_squadra(g):
    return [g.mon_moves(i)[1] for i in range(len(g.party()))]

def evento(nome, rif=False):
    c = CANI[nome]; g = g_da(c['stato']); esito = {}
    if rif: esci_e_torna(g, c)          # il savestate viene dalla 0.59: si ricarica la mappa con la ROM in prova
    vis, lotta = parla(g, c); g.shot('t59_%s_parla' % nome)
    log('  parla:', vis, 'lotta:', lotta)
    esito['parla'] = (vis, lotta)
    if rif:
        g.close(); return esito
    # 1. fuga
    fuggi(g); vis = chiudi_testi(g); g.shot('t59_%s_fuga' % nome)
    esito['fuga'] = dict(testi=vis, flag=pl.flag(g.e, c['flag']), presente=presente(g, c))
    log('  dopo la fuga:', esito['fuga'])
    esci_e_torna(g, c); esito['fuga']['presente_dopo_rientro'] = presente(g, c)
    log('  rientro dopo la fuga: presente', esito['fuga']['presente_dopo_rientro'])
    # 2. KO del leggendario (si combatte con pl.G.battle)
    vis, lotta = parla(g, c)
    if lotta:
        info = ko(g); vis2 = chiudi_testi(g); g.shot('t59_%s_ko' % nome)
        esito['ko'] = dict(lotta=info[-2:], testi=vis + vis2, flag=pl.flag(g.e, c['flag']), presente=presente(g, c),
                           pos=vai.stato(g)[:3], squadra=g.party())
        log('  dopo il KO:', esito['ko'])
        if vai.stato(g)[0] == c['mappa'] or True:
            esci_e_torna(g, c); esito['ko']['presente_dopo_rientro'] = presente(g, c)
            log('  rientro dopo il KO: presente', esito['ko']['presente_dopo_rientro'])
    g.heal() if False else None
    # 3. cattura con MASTER BALL (fixture)
    fixture(g)
    vis, lotta = parla(g, c)
    if lotta:
        menu_lotta(g); g.throw(); vis2 = chiudi_testi(g, 20); g.shot('t59_%s_preso' % nome)
        esito['cattura'] = dict(testi=vis + vis2, flag=pl.flag(g.e, c['flag']), presente=presente(g, c),
                                squadra=specie_squadra(g))
        log('  dopo la cattura:', esito['cattura'])
    # 4. salvataggio in gioco, ricarica dal titolo, uscita e rientro
    salva(g); g.shot('t59_%s_salvato' % nome); g.e.close()
    shutil.copy(g.sav, os.path.join(PLAY, 't59_%s_preso.sav' % nome))
    g = ricarica(g.sav); g.shot('t59_%s_ricaricato' % nome)
    esito['ricarica'] = dict(pos=vai.stato(g)[:3], flag=pl.flag(g.e, c['flag']), presente=presente(g, c),
                             squadra=specie_squadra(g))
    log('  dopo la ricarica:', esito['ricarica'])
    esci_e_torna(g, c); esito['ricarica']['presente_dopo_rientro'] = presente(g, c)
    esito['ricarica']['flag_dopo_rientro'] = pl.flag(g.e, c['flag'])
    log('  rientro dopo la ricarica:', esito['ricarica'])
    g.close()
    return esito


if PARTE == 'viaggio2':
    g = g_da('t59_raikou.ss')
    ok = vai.vai(g, (35, 100), 10, 4, AB); log('  accanto a Entei', ok, vai.stato(g)); g.save('t59_entei.ss'); g.shot('t59_entei')
    g.close()
    g = g_da('t59_ravenna.ss'); fixture_surf(g)
    ok = vai.vai(g, (26, 13), 31, 29, AB | {'surf'}); log('  accanto a Suicune', ok, vai.stato(g)); g.save('t59_suicune.ss'); g.shot('t59_suicune')
    g.close()

def vbam(nome):
    """Stesso evento su VBA-M: il salvataggio vero viene fatto in mGBA accanto al Pokemon (con le MASTER BALL
    della fixture), poi VBA-M continua dal titolo: parla, fugge, ritenta, cattura, salva, ricarica."""
    c = CANI[nome]; esito = {}
    g = g_da(c['stato']); fixture(g); salva(g); g.e.close()
    pre = os.path.join(PLAY, 't59_%s_pre.sav' % nome); shutil.copy(g.sav, pre)
    os.environ['VBAM'] = '1'
    try:
        g = ricarica(pre); log('  VBA-M dal titolo:', vai.stato(g)[:3], 'flag', pl.flag(g.e, c['flag']), 'presente', presente(g, c))
        vis, lotta = parla(g, c); esito['parla'] = (vis, lotta); log('  VBA-M parla:', vis, lotta)
        fuggi(g); vis = chiudi_testi(g); esito['fuga'] = dict(testi=vis, flag=pl.flag(g.e, c['flag']), presente=presente(g, c))
        log('  VBA-M dopo la fuga:', esito['fuga'])
        vis, lotta = parla(g, c)
        if lotta:
            menu_lotta(g); g.throw(); vis2 = chiudi_testi(g, 20); g.shot('t59_%s_vbam_preso' % nome)
            esito['cattura'] = dict(testi=vis + vis2, flag=pl.flag(g.e, c['flag']), presente=presente(g, c), squadra=specie_squadra(g))
            log('  VBA-M dopo la cattura:', esito['cattura'])
        g.sav = pre; salva(g); g.e.close()
        g = ricarica(pre)
        esito['ricarica'] = dict(pos=vai.stato(g)[:3], flag=pl.flag(g.e, c['flag']), presente=presente(g, c), squadra=specie_squadra(g))
        log('  VBA-M dopo la ricarica:', esito['ricarica'])
        esci_e_torna(g, c); esito['ricarica']['presente_dopo_rientro'] = presente(g, c)
        log('  VBA-M rientro:', esito['ricarica']); g.close()
    finally:
        os.environ.pop('VBAM', None)
    return esito

if PARTE.startswith('vbam-'):
    import json
    es = vbam(PARTE[5:])
    json.dump(es, open(os.path.join(PLAY, 't59_%s_vbam.json' % PARTE[5:]), 'w'), indent=1, ensure_ascii=False, default=str)

if PARTE == 'vecchio':
    # salvataggio vero fatto con la 0.58 dentro 26.12 (gli oggetti in SaveBlock1 puntano al vecchio script),
    # poi aperto con la 0.59: Raikou deve dare la lotta. ROM 0.58 in --rif=.
    import json
    r58 = os.path.abspath(next(a.split('=', 1)[1] for a in sys.argv if a.startswith('--rif=')))
    c = CANI['raikou']; g = g_da(c['stato']); g.e.close()
    g.e = Emu(r58, g.sav); g.e.run(10); g.e.load(pl.P + c['stato']); g.e.run(120)
    esci_e_torna(g, c); salva(g); g.e.close()
    vec = os.path.join(PLAY, 't59_vecchio_058.sav'); shutil.copy(g.sav, vec)
    g = ricarica(vec, r58); vis58, l58 = parla(g, c); g.close(); log('  0.58 dal titolo, parla:', vis58, l58)
    s59 = os.path.join(PLAY, 't59_vecchio_aperto_059.sav'); shutil.copy(vec, s59); g = ricarica(s59); log('  0.59 dal titolo:', vai.stato(g)[:3])
    vis, lotta = parla(g, c); log('  0.59 parla:', vis, 'lotta', lotta); g.close()
    json.dump(dict(r058=(vis58, l58), r059=(vis, lotta)), open(os.path.join(PLAY, 't59_vecchio.json'), 'w'), indent=1, ensure_ascii=False)

if PARTE in CANI:
    import json
    rif = '--rif' in sys.argv
    es = evento(PARTE, rif)
    out = os.path.join(PLAY, 't59_%s_%s.json' % (PARTE, 'rif' if rif else 'prova'))
    json.dump(es, open(out, 'w'), indent=1, ensure_ascii=False, default=str)
