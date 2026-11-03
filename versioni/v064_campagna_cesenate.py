"""Versione 0.64 - Lotto 3: la CAMPAGNA CESENATE al posto di MONTE SPACCATO (35.101).

Prima (0.63): 35.101 MONTE SPACCATO, una collina in mezzo all'erba; tre rocce nella tagliata (14,16-18) verso
il casello 35.92 (Capocolle); tre allenatori; due casette (58,20 e 54,36) verso l'Ippodromo.

Dopo (0.64), dalla bozza 4 approvata (bozze/campagna_monte_spaccato.py; il disegno e' copiato qui e congelato):
  - pianura: campi, vigneti, macero, molta erba alta, il fiume che scende da una cascata del monte, il ponte
    della Via Emilia; il Monte Spaccato a nord con la galleria (25,10) verso Capocolle.
  - Stesse dimensioni (64x40) e stesso layout (0x15998b4, solo di 35.101): blocchi riscritti al loro posto,
    tileset secondario nuovo fatto con tela.Unione.
  - Uscite: casa a est (porta) -> Ippodromo (cancello ovest), come prima le due casette; galleria -> 35.92.
    Da questa mappa non si va a Cesena: Cesena -> Ippodromo -> campagna.
  - Una roccia sola davanti alla galleria (25,11), flag 0x11, script di Smeraldo (SPACCAROCCIA + 3a medaglia);
    lo script di mappa della 0.63 la nasconde se il passaggio e' gia' aperto (flag 0x22).
  - Sei allenatori: i tre di prima (ILARIO, LEONIA, PIERO: stesse flag, quindi chi li ha battuti li ritrova
    battuti) spostati e vestiti come nella bozza, e tre nuovi (numeri liberi 462, 485, 486).
  - Il luogo si chiama CAMPAGNA CESENATE; il cartello sotto il monte dice MONTE SPACCATO.
"""
import struct
import engine as E
from engine import H, P, B, Script
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'strumenti_rom'))
import tela

OUT = {}
LAYOUT = 0x15998b4
ROCCIA_SCR, ROCCIA_GFX = 0x290b6b, 86


def disegna(d):
    """La bozza 4 della Campagna Cesenate (copia congelata). Ritorna la tela."""
    W, H = 64, 40
    def lay(lid): return struct.unpack_from('<I', d, 0x627fc0 + (lid - 1) * 4)[0] - 0x8000000
    L116, L117, L119 = lay(32), lay(33), lay(35)
    _, S117 = tela.Tela.layout(d, L117); _, S119 = tela.Tela.layout(d, L119); _, S116 = tela.Tela.layout(d, L116)
    G, ALTA = 0x3001, 0x300d                                        # erba, erba alta (primario, quota 3)
    RIVA_S, ACQUA, RIVA_D = 0x1190, 0x1170, 0x1192                  # fiume (primario, quota 1, come il lago del 114)
    PONTE_A, PONTE_B = 0xf210, 0xf218                               # assi del ponte (Percorso 119, quota libera)
    T = tela.Tela(d, W, H, S117, G)
    def met(x, y, v, src=S117): T.metti(x, y, src, v)
    def blocco(src, x0, y0, w, h, x, y): T.incolla(src, x0, y0, w, h, x, y)
    def bosco(x, y, w, h, cima=True, base=True):
        for j in range(h):
            for i in range(w):
                k = i % 2
                if j % 2 == 0: v = (0x31ce + k) if (cima and j == 0) else (0x5d4 + k)
                else: v = (0x5e4 + k) if (base and j == h - 1) else (0x5dc + k)
                met(x + i, y + j, v)
    def erba_alta(x, y, w, h): T.riempi(x, y, w, h, S117, ALTA)

    # --- il Monte Spaccato a nord-ovest, con la spaccatura a V e la galleria (25,10) verso Capocolle
    blocco(L116, 41, 0, 33, 13, 1, 0)
    for (x, y) in ((7, 7), (7, 8), (16, 6), (30, 4), (31, 4)):      # via la seconda grotta e le buche
        T.c[y][x] = T.c[y][x - 1]
    # --- il monte prosegue verso est (stesso Percorso 116, stesso scarto di colonne): niente taglio netto
    blocco(L116, 74, 0, 26, 11, 34, 0)
    for x in range(39, 62): met(x, 11, 0x079, S116)                  # piede del monte
    for y in range(0, 12): met(60, y, 0x072, S116); met(61, y, 0x0a2, S116)
    for y in range(0, 12):
        for x in range(34, 61):
            if (T.c[y][x][1] & 1023) in (0x0e1, 0x1b0, 0x0af): T.c[y][x] = (S116, 0x071)   # via buche e massi
    # --- bosco ai bordi
    bosco(0, 0, 2, 40, cima=False, base=False); bosco(62, 0, 2, 40, cima=False, base=False)
    bosco(0, 36, 64, 4, base=False)
    # --- campagna ovest: frutteto, erba alta, macero, vigneto
    blocco(L117, 7, 3, 9, 5, 3, 14)
    erba_alta(13, 14, 9, 7)
    blocco(L117, 20, 1, 11, 8, 12, 27)
    T.riempi(11, 32, 4, 3, S117, G)                                # avanzo di sabbia del ritaglio
    blocco(L117, 8, 13, 10, 5, 2, 29)
    erba_alta(3, 21, 8, 6)
    # --- campagna centrale: grande prato d'erba alta, filare, vigneti
    erba_alta(28, 13, 15, 7)
    for x in (29, 33, 37, 41): bosco(x, 20, 2, 2)
    blocco(L117, 7, 3, 9, 5, 27, 28); blocco(L117, 7, 3, 9, 5, 34, 28)
    erba_alta(27, 33, 16, 3)
    # --- il fiume (da nord a sud) e il ponte della Via Emilia
    for y in range(12, 40):                                         # fino al bordo sud, sotto il bosco
        met(44, y, RIVA_S); met(49, y, RIVA_D)
        for x in range(45, 49): met(x, y, ACQUA)
    for y in range(0, 11):                                          # la sorgente: cascata giu' dal monte
        for x in range(45, 49): met(x, y, 0x10b9)
    for x, v in zip(range(45, 49), (0x102c, 0x1034, 0x1034, 0x103c)): met(x, 11, v)
    # --- campagna est: campo, erba alta
    blocco(L117, 8, 13, 10, 5, 51, 12)
    erba_alta(51, 27, 10, 9)
    # --- casa a est: ingresso dall'IPPODROMO (porta a 55,22)
    blocco(L117, 49, 1, 6, 5, 53, 18)
    # --- Via Emilia: dalla casa verso ovest, ponte sul fiume, poi a nord fino alla galleria
    def strada_h(x0, x1, y):
        for x in range(x0, x1 + 1):
            e = 0 if x == x0 else (2 if x == x1 else 1)
            met(x, y, 0x3118 + e); met(x, y + 1, 0x3120 + e); met(x, y + 2, 0x3128 + e)
    strada_h(24, 58, 23)
    for y in range(12, 25): met(24, y, 0x3120); met(25, y, 0x3121); met(26, y, 0x3122)
    met(24, 12, 0x3118); met(25, 12, 0x3119); met(26, 12, 0x311a)
    for y in (23, 24): met(25, y, 0x3121); met(26, y, 0x3121)
    for x in range(43, 51):
        met(x, 23, PONTE_A, S119); met(x, 24, PONTE_B, S119)
    met(44, 25, RIVA_S); met(49, 25, RIVA_D)
    for x in range(45, 49): met(x, 25, ACQUA)
    # cartelli: MONTE SPACCATO (8,9, gia' nel pezzo del 116), CAMPAGNA CESENATE accanto alla casa (52,22, gia' nel 117)
    met(42, 22, 0x403)                                              # cartello del ponte


    return T


# allenatori: (x, y, gfx, numero, allenatore di riferimento per classe/ritratto, donna)
VECCHI = {0xc6: (16, 17, 36, None, False),          # ILARIO: com'era (classe 5, ritratto 3)
          0xc7: (38, 26, 24, 23, True),             # LEONIA: come IRIS (donna lungo i vigneti)
          0xc8: (34, 15, 31, 216, False)}           # PIERO: come ETHAN (ragazzo di campagna)
NUOVI = [  # numero, x, y, gfx, riferimento, nome, squadra [(specie, livello)], presentazione, sconfitta, dopo
    (462, 27, 16, 7, 273, 'NICO', [(20, 25), (17, 26)],
     "Ehi! Questa strada è mia,\nci gioco da quando ero piccolo!",
     "Uffa! Hai vinto tu.",
     "La galleria del MONTE SPACCATO\nporta a CAPOCOLLE."),
    (485, 43, 13, 49, 496, 'TONINO', [(61, 26), (118, 26)],
     "Il fiume scende dal monte:\nqui i pesci abboccano sempre!",
     "Mi hai fatto scappare\ntutti i pesci...",
     "Con una canna da pesca, qui\npeschi bene tutto l'anno."),
    (486, 55, 30, 33, 392, 'OSVALDO', [(128, 27), (241, 27)],
     "Questi campi li curo io.\nVediamo se sai lottare!",
     "Forte! Come la grandine\nsul raccolto.",
     "Dall'IPPODROMO si arriva\nqui passando dalla mia casa."),
]
TAB_ALLENATORI = 0xf21000


def ripunta(W, at, testo):
    assert W.d[at] == 0x0f and W.d[at + 1] == 0x00, hex(at)
    struct.pack_into('<I', W.d, at + 2, B + W.text(testo))


def cartello(nome, testo):
    s = Script(nome)
    s.emit(b'\x0f\x00' + P(E.W.text(testo)) + b'\x09\x03\x02')        # msgbox MSGBOX_SIGN, end
    return s.save()


def allenatore(W, tid, rif, nome, squadra, donna):
    o = TAB_ALLENATORI + tid * 40
    raw = bytearray(40)
    r = TAB_ALLENATORI + rif * 40
    raw[0] = 2; raw[1] = W.d[r + 1]; raw[2] = (W.d[r + 2] & 0x7f) | (0x80 if donna else 0); raw[3] = W.d[r + 3]
    nm = W.enc(nome) + b'\xff'; raw[4:4 + len(nm)] = nm
    struct.pack_into('<I', raw, 28, 7); raw[32] = len(squadra)
    pp = W.alloc(b''.join(struct.pack('<HBxHH', 0, lv, sp, 0) for sp, lv in squadra), 'squadra ' + nome)
    struct.pack_into('<I', raw, 36, B + pp)
    W.d[o:o + 40] = raw


def apply(W):
    d = W.d
    pool = E.pool()
    m = W.rom.map(35, 101)
    assert m['layout'] == LAYOUT and (m['width'], m['height']) == (64, 40)
    # ---- 1. la mappa: blocchi al loro posto e tileset secondario nuovo
    T = disegna(bytes(d))
    U = tela.Unione(bytes(d)); vals = T.valori(U)
    assert len(vals) == 64 * 40
    for k, v in enumerate(vals): struct.pack_into('<H', d, m['blocks'] + k * 2, v)
    tp = U.scrivi(W, 'campagna cesenate')
    struct.pack_into('<I', d, LAYOUT + 20, B + tp)
    for k, v in enumerate((0x5d4, 0x5d5, 0x5dc, 0x5dd)):                 # bordo: bosco
        struct.pack_into('<H', d, m['border'] + k * 2, v)
    a = W.rom.blocks(W.rom.map(35, 101))
    beh = lambda x, y: (U.prim.attr(vals[y * 64 + x] & 1023) if (vals[y * 64 + x] & 1023) < 512 else
                        struct.unpack_from('<H', U.blob()[3], ((vals[y * 64 + x] & 1023) - 512) * 2)[0]) & 0xff
    assert beh(55, 22) == 0x69 and beh(25, 10) == 0x60, (hex(beh(55, 22)), hex(beh(25, 10)))
    OUT['tileset'] = dict(puntatore=hex(tp), **U.stato())

    # ---- 2. uscite: porta della casa (55,22) -> Ippodromo; galleria (25,10) -> casello 35.92
    ws = [dict(x) for x in m['warps']]
    assert [(w['x'], w['y'], w['group'], w['num'], w['warp']) for w in ws] == \
        [(58, 20, 34, 19, 1), (4, 17, 35, 92, 0), (54, 36, 34, 19, 1)], ws
    ws[0].update(x=55, y=22); ws[1].update(x=25, y=10); ws[2].update(x=55, y=22)

    # ---- 3. allenatori
    oggetti = []
    vecchi = {}
    for o in m['objects']:
        if o['script'] == ROCCIA_SCR: continue
        k = bytes(d[o['script']:o['script'] + 16]).index(b'\x5c\x02')
        tid = struct.unpack_from('<H', d, o['script'] + k + 2)[0]
        assert tid in VECCHI, (hex(o['script']), tid)
        vecchi[tid] = o['script']
    assert sorted(vecchi) == sorted(VECCHI)
    for tid, (x, y, gfx, rif, donna) in VECCHI.items():
        if rif is not None:
            r = TAB_ALLENATORI + rif * 40; o = TAB_ALLENATORI + tid * 40
            d[o + 1] = d[r + 1]; d[o + 2] = (d[r + 2] & 0x7f) | (0x80 if donna else 0); d[o + 3] = d[r + 3]
        oggetti.append(dict(gfx=gfx, x=x, y=y, elev=3, move=8, script=vecchi[tid], flag=0))
    nuovi_flag = [0x500 + n[0] for n in NUOVI]
    assert not any(int(f, 16) in nuovi_flag for f, _ in pool.taken)
    pool.riordina([], escludi=nuovi_flag)                                 # le loro flag non vanno piu' al pool
    for tid, x, y, gfx, rif, nome, squadra, intro, perso, dopo in NUOVI:
        assert d[TAB_ALLENATORI + tid * 40 + 4] != 0xff
        allenatore(W, tid, rif, nome, squadra, False)
        s = Script('Campagna Cesenate: allenatore %s (0.64)' % nome)
        s.emit(b'\x5c\x00' + H(tid) + H(0) + P(W.text(intro)) + P(W.text(perso)))
        s.msg(dopo).end()
        oggetti.append(dict(gfx=gfx, x=x, y=y, elev=3, move=8, script=s.save(), flag=0))
    # la roccia davanti alla galleria (flag temporanea 0x11, nascosta dallo script della 0.63 se 0x22)
    oggetti.append(dict(gfx=ROCCIA_GFX, x=25, y=11, elev=(int(a[11, 25]) >> 12) & 15, move=8, script=ROCCIA_SCR, flag=0x11))
    for i, o in enumerate(oggetti): o['id'] = i + 1

    # ---- 4. cartelli
    bgs = [dict(x=8, y=9, elev=0, kind=0, arg=B + cartello('cartello Monte Spaccato (0.64)',
              "MONTE SPACCATO\nLa galleria porta a CAPOCOLLE\n\npoi a FORLIMPOPOLI.")),
           dict(x=53, y=22, elev=0, kind=0, arg=B + cartello('cartello Campagna Cesenate (0.64)',
              "CAMPAGNA CESENATE\nDalla casa si torna\n\nall'IPPODROMO e a CESENA.")),
           dict(x=42, y=22, elev=0, kind=0, arg=B + cartello('cartello del ponte (0.64)',
              "VIA EMILIA\nA ovest MONTE SPACCATO,\n\na est l'IPPODROMO."))]
    W.set_events(35, 101, objects=oggetti, warps=ws, coords=[], bgs=bgs)
    OUT['oggetti'] = [(o['id'], o['x'], o['y'], o['gfx'], hex(o['script']), hex(o['flag'])) for o in oggetti]

    # ---- 5. nome del luogo
    assert struct.unpack_from('<I', d, 0x74cca4)[0] == B + 0x15caca8
    struct.pack_into('<I', d, 0x74cca4, B + W.alloc(W.enc('CAMPAGNA CESENATE') + b'\xff', 'nome Campagna Cesenate'))

    # ---- 6. testi che parlavano di Monte Spaccato
    ripunta(W, 0x1599d0a, "CASELLANTE: A est c'è CESENA.\nA ovest l'IPPODROMO DEL SAVIO\n\n"
                          "e poi la CAMPAGNA CESENATE,\nverso CAPOCOLLE e FORLIMPOPOLI.")
    ripunta(W, 0x2d2672, "Con la terza medaglia puoi\nusare SPACCAROCCIA all'aperto.\n\n"
                         "Oltre l'IPPODROMO di CESENA,\nuna roccia chiude la galleria\n\n"
                         "del MONTE SPACCATO. VOLO\nti aiuterà a tornare.")
    OUT['allenatori_nuovi'] = [(n[0], n[5], hex(0x500 + n[0])) for n in NUOVI]

    # ---- 7. vecchi salvataggi fatti dentro 35.101: la mappa e' cambiata (263 caselle calpestabili prima sono
    # ora monte, fiume o casa). Ogni ingresso da un'uscita alza la variabile NUOVA (ON_TRANSITION); con Continua
    # in un salvataggio di prima la variabile e' 0 e lo script di frame riporta il giocatore, una volta sola,
    # sulla strada davanti alla casa (55,23), ricaricando anche gli oggetti della mappa nuova.
    NUOVA = E.variabili().var('Campagna Cesenate: entrata nella mappa nuova (vecchi salvataggi, 0.64)')
    ms = W.rom.map_scripts(W.rom.map(35, 101))
    tipi = [t for t, _ in ms]
    assert sorted(tipi) == [1, 3], ms
    vecchio3 = dict(ms)[3]
    s = Script('Campagna Cesenate: ingresso (0.64)')
    s.var(NUOVA, 1).emit(b'\x05' + P(vecchio3))                          # poi lo script della 0.63 (rocce)
    t3 = s.save()
    s = Script('Campagna Cesenate: vecchio salvataggio, si riparte dalla casa (0.64)')
    s.var(NUOVA, 1).emit(b'\x3a' + bytes([35, 101, 0xff]) + H(55) + H(23) + b'\x27\x02')
    f = s.save()
    tab = W.alloc(H(NUOVA) + H(0) + P(f) + H(0), 'frame campagna cesenate')
    W.set_map_scripts(35, 101, [(1, dict(ms)[1]), (2, tab), (3, t3)])
    OUT['vecchi_salvataggi'] = dict(variabile=hex(NUOVA), ingresso=hex(t3), frame=hex(f))
    return OUT
