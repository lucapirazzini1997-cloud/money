"""0.51 - Mirabilandia e Safari separati, ingressi prima della Basilica di Classe.

- Classe (34.94): due varchi sulla piazza, prima della basilica: ovest -> Mirabilandia, est -> Safari.
- Mirabilandia (34.114): niente piu' passaggio verso il Safari; dopo ogni giostra puo' comparire un Pokemon cromatico.
- Safari: le sei aree originali della Zona Safari di Smeraldo (gruppo 26), senza modalita' Safari (niente Safari Ball,
  niente passi contati, lotte normali). Entei in una grotta nuova sulla montagna (area NE), Raikou in mezzo al prato
  (area NE), Suicune in mezzo al lago (area SE, serve Surf). Stesse flag di cattura delle versioni precedenti.
"""
from gates48 import *
import gates48 as G
import kit48
import struct, copy
import caselli48 as CS
from fixes49 import NATIVE_SHINY_WILD
import cave51 as CV

CLASSE = (34, 94)
MIRA = (34, 114)
SAFARI_S = (26, 3)
OUT = {}

# ------------------------------------------------------------------ script comuni

def legend_script(name, species, level, flag, oid, intro, caught, lost):
    """Leggendario fisso: lotta normale; se lo catturi sparisce (flag), altrimenti resta li' e puoi riprovare."""
    s = Script(name).emit(b'\x6a\x5a').msg(intro)
    s.emit(b'\xa1' + H(species) + H(2) + b'\xc5')
    s.emit(b'\xb6' + H(species) + bytes([level]) + H(0))
    s.emit(b'\x29' + H(0x8c1) + b'\xb7' + b'\x2a' + H(0x8c1))
    s.emit(b'\x26' + H(0x800d) + H(0xb7))
    s.cmp(7, 'caught')
    s.msg(lost).end()
    s.label('caught').set(flag).emit(b'\x53' + H(oid)).msg(caught).end()
    return s.save()


def sign_script(text):
    return Script('Cartello').msg(text).end().save()


# ------------------------------------------------------------------ Classe: due varchi prima della basilica

def classe_gates(cvs):
    cv = cvs[CLASSE]
    old = [(w['x'], w['y']) for w in cv.bwarps if (w['group'], w['num']) in (MIRA, (34, 115))]
    assert sorted(old) == [(29, 22), (36, 22)], old
    cv.bwarps = [w for w in cv.bwarps if (w['x'], w['y']) not in old]
    cv.bbgs = [b for b in cv.bbgs if (b['x'], b['y']) not in ((29, 23), (36, 23))]
    for (x, y) in old + [(29, 23), (36, 23)]:
        G.to_grass(cv, x, y)
    lw = [(0, y) for y in range(24, 28)]
    le = [(cv.w - 1, y) for y in range(24, 28)]
    sw = CS.autospec(cv, 'W', lw, 'MIRABILANDIA')
    se = CS.autospec(cv, 'E', le, 'SAFARI')
    gw = install_end(cv, sw, MIRA, 0)
    ge = install_end(cv, se, SAFARI_S, 0)
    # la piazza arriva fino alla porta del Safari (prima finiva una cella prima)
    for y in range(24, 28):
        cv.art[y][39] = cv.art[y][38]; cv.over[y][39] = cv.over[y][38]; cv.pathmask[y][39] = cv.pathmask[y][38]
    OUT['classe'] = dict(W=gw, E=ge)
    return gw, ge


# ------------------------------------------------------------------ Mirabilandia

RIDE_SHINY = {   # mappa giostra -> (specie, livello, nome, testi)
    (35, 46): (77, 30, 'PONYTA', "Scendi da iSpeed e un PONYTA dal manto\nche brilla ti sfreccia davanti!",
               "Hai catturato il PONYTA cromatico!\nCorreva più veloce del trenino.",
               "Il PONYTA torna a correre lungo la pista.\nFai un altro giro su iSpeed!"),
    (35, 47): (190, 30, 'AIPOM', "Fra le rovine di Katun un AIPOM\ndal pelo dorato ti ruba il cappello!",
               "Hai catturato l'AIPOM cromatico!\nIl cappello è salvo.",
               "L'AIPOM si arrampica sulle rovine.\nFai un altro giro su Katun!"),
    (35, 48): (183, 30, 'MARILL', "Lo splash di Divertical fa saltare fuori\nun MARILL dal colore insolito!",
               "Hai catturato il MARILL cromatico!\nEra fradicio quanto te.",
               "Il MARILL si tuffa nel lago.\nFai un altro giro su Divertical!"),
}


def ride_shiny():
    """Alla fine del giro, prima di tornare alla stazione, il Pokemon cromatico della giostra (finche' non lo catturi)."""
    import scr
    res = {}
    for key, (sp, lv, nm, intro, caught, fled) in RIDE_SHINY.items():
        m = W.rom.map(*key)
        tab = next(q for t, q in W.rom.map_scripts(m) if t == 2)
        p = struct.unpack_from('<I', W.d, tab + 4)[0] - B
        ops, _ = scr.decode(bytes(W.d), p, 60)
        wat = next(at for at, op, args in ops if op == 'warp')
        warp = bytes(W.d[wat:wat + 8])
        assert warp[0] == 0x39 and warp[1:3] == bytes([34, 114]), warp.hex()
        flag = kit48.POOL.flag('giostra %s cromatico' % nm)
        s = Script('Giostra %s cromatico' % nm)
        s.flag(flag, 'back')
        s.msg(intro)
        s.var(0x8004, sp).var(0x8005, lv)
        s.emit(b'\xa1' + H(sp) + H(2) + b'\xc5')
        s.emit(b'\xb6' + H(sp) + bytes([lv]) + H(0))
        s.emit(b'\x23' + struct.pack('<I', NATIVE_SHINY_WILD))
        s.emit(b'\x29' + H(0x8c1) + b'\xb7' + b'\x2a' + H(0x8c1))
        s.emit(b'\x26' + H(0x800d) + H(0xb7))
        s.cmp(7, 'caught')
        s.msg(fled).jump('back')
        s.label('caught').set(flag).msg(caught)
        s.label('back').emit(warp + b'\x27\x6b\x02')
        q = s.save()
        W.d[wat:wat + 5] = b'\x05' + P(q)
        W.header_set(*key, region=27)          # prima mostrava "ROUTE 114"
        res[nm] = hex(flag)
    OUT['giostre'] = res
    return res


def mirabilandia(cvs, gw):
    cv = cvs.setdefault(MIRA, V.live_canvas(MIRA))
    south = [w for w in cv.bwarps if (w['x'], w['y']) == (43, 71)]
    assert len(south) == 1
    south[0].update(group=CLASSE[0], num=CLASSE[1], warp=gw['slot'])
    cv.bwarps = [w for w in cv.bwarps if w['x'] != 87]
    # il vecchio passaggio verso il Safari (bordo est) diventa bosco
    for y in range(33, 39):
        for x in range(78, 88):
            G.to_grass(cv, x, y)
    for (x, y) in ((84, 33), (86, 33), (84, 35), (86, 35), (84, 37), (86, 37)):
        if y + 1 < cv.h: cv.tree(x, y)
    cv.bbgs = [b for b in cv.bbgs if (b['x'], b['y']) != (81, 34)]
    G.to_grass(cv, 81, 34)
    for b in cv.bbgs:
        if (b['x'], b['y']) == (40, 65):
            b['arg'] = B + sign_script("MIRABILANDIA\nAttrazioni e ristoro. Uscita sud verso Classe.")
    for o in cv.objs:
        if (o['x'], o['y']) == (44, 64):
            o['script'] = talk("Benvenuto a MIRABILANDIA!\niSpeed a nord-ovest, Katun a nord-est.\n"
                               "Divertical è sul lago. Dopo ogni giro\nguardati intorno: qualcuno brilla!")
    return cv


# ------------------------------------------------------------------ Safari (aree originali di Smeraldo)

SAFARI_MAPS = [(26, 0), (26, 1), (26, 2), (26, 3), (26, 12), (26, 13), (26, 11)]

IT = {   # (mappa, id oggetto) -> testo italiano
    ((26, 3), 1): "Benvenuto al SAFARI RAVENNA!\nQui giri quanto vuoi, senza biglietto.\n"
                  "Usa le tue Poké Ball: niente Safari Ball,\nniente passi contati.\n"
                  "Dicono che tre Pokémon leggendari\nvivano nelle zone più lontane...",
    ((26, 3), 2): "Lo sapevi? Se metti un {POKEBLOCK} nella\nmangiatoia, i Pokémon si radunano.",
    ((26, 3), 3): "Voglio andare più in fondo, ma ho\ndimenticato la bicicletta.\n"
                  "Qualcosa mi dice che i Pokémon rari\nvivono nelle zone più esterne.",
    ((26, 3), 4): "Ho messo un {POKEBLOCK} nella mangiatoia,\nma è sparito.\n"
                  "Dev'essere stato un Pokémon,\ne non me ne sono accorto!",
    ((26, 13), 1): "I Pokémon di questa zona non vengono\nda HOENN.\n"
                   "C'è chi giura di aver visto qualcosa\ndi azzurro in mezzo al lago...",
    ((26, 13), 2): "Questi Pokémon sono tutti nuovi per me!\nE posso catturarli tutti. Che forza!",
    ((26, 13), 3): "Wow! Non ho mai visto nessuno\ndi questi Pokémon!",
    ((26, 13), 5): "L'ampliamento del Safari è finito.\nGoditi le nuove aree!",
    ((26, 12), 1): "In cima alla montagna c'è una grotta\nche manda un calore strano...",
    ((26, 12), 2): "Uffa! Non riesco a catturare niente!\nEppure qui di Pokémon ce ne sono tanti.",
    ((26, 12), 4): "Ho sentito un tuono a ciel sereno,\nlà in mezzo all'erba alta del prato.",
    ((26, 2), 1): "A volte, se lancio un {POKEBLOCK},\nil Pokémon lo ignora.\n"
                  "Che anche i Pokémon abbiano\ni loro gusti?",
    ((26, 1), 1): "Cerco Pokémon d'acqua che a HOENN\nnon si vedono.\nSai dov'è il lago?",
    ((26, 1), 2): "Catturerò un sacco di Pokémon rari\ne li scambierò con i miei amici!",
    ((26, 0), 1): "Uff... uff... Ce l'ho fatta ad arrivare\nfin qui... ma sono stremato.",
    ((26, 11), 1): "Più ti avvicini al Pokémon prima\ndi lanciare la Ball, meglio è.\n"
                   "Almeno, così dicono.",
    ((26, 11), 2): "Con i {POKEBLOCK} i Pokémon selvatici\nscappano meno.",
    ((26, 11), 3): "Se metti un {POKEBLOCK} nella mangiatoia\narrivano i Pokémon.\n"
                   "Ognuno preferisce il suo gusto.",
}
POKEBLOCK = 'POKéBLOCK'


def _it(t): return t.replace('{POKEBLOCK}', POKEBLOCK)


def safari_texts(objs, key):
    for o in objs:
        t = IT.get((key, o['id']))
        if t: o['script'] = talk(_it(t))
    return objs


def safari_south(gate_slot):
    m = W.rom.map(*SAFARI_S)
    ws = copy.deepcopy(m['warps']);assert (ws[0]['x'], ws[0]['y']) == (32, 33)
    ws[0].update(group=CLASSE[0], num=CLASSE[1], warp=gate_slot)
    obs = copy.deepcopy(m['objects'])
    obs = [o for o in obs if o['id'] not in (5, 6)]           # operai del "cantiere": tutte le aree aperte
    for o in obs:
        if o['id'] == 1: o.update(x=31, y=34)                    # l'addetto non blocca piu' la porta
    safari_texts(obs, SAFARI_S)
    events(SAFARI_S, warps=ws, objects=obs)


def safari_other_texts():
    for key in [(26, 0), (26, 1), (26, 2), (26, 13), (26, 11)]:
        obs = safari_texts(copy.deepcopy(W.rom.map(*key)['objects']), key)
        events(key, objects=obs)
    m = W.rom.map(26, 2)
    bgs = copy.deepcopy(m['bgs'])
    for b in bgs:
        if (b['x'], b['y']) == (32, 7): b['arg'] = B + sign_script("CASA DI RIPOSO\nRiposa i piedi stanchi.")
    events((26, 2), bgs=bgs)
    for key in SAFARI_MAPS:
        W.header_set(*key, region=28)


# --- Suicune: in mezzo al lago dell'area SE (serve Surf)
def suicune():
    key = (26, 13)
    obs = copy.deepcopy(W.rom.map(*key)['objects'])
    safari_texts(obs, key)
    oid = len(obs) + 1
    p = legend_script('SUICUNE Safari', 245, 45, 0x887, oid,
                      "L'acqua del lago diventa limpidissima...\nSUICUNE ti guarda dalla superficie!",
                      "Hai catturato SUICUNE!\nIl lago torna calmo.",
                      "SUICUNE scivola via sull'acqua.\nTornerà al centro del lago.")
    obs.append(dict(id=oid, gfx=230, x=31, y=29, elev=1, move=8, rx=0, ry=0, ttype=0, trange=0, script=p, flag=0x887))
    events(key, objects=obs)
    OUT['suicune'] = (key, 31, 29)


# --- area NE: grotta di Entei sulla montagna, Raikou in mezzo al prato
CV.THEMES['fuoco'] = dict(floor=(196, 132, 92), light=(232, 172, 120), stone=(128, 60, 40), shade=(66, 30, 22), deep=(38, 16, 12))
CAVE_DOOR = (21, 4)


def entei_cave(ne_slot):
    cv = CV.new_cave('Grotta Ardente', 22, 20, 97)
    g = CV.Grid(22, 20)
    g.carve(9, 15, 12, 18);g.carve(10, 19, 11, 19)          # ingresso
    g.carve(3, 11, 12, 14);g.carve(3, 6, 6, 11)              # corridoio a zig-zag
    g.carve(3, 6, 18, 9);g.carve(15, 9, 18, 13)
    g.carve(7, 3, 14, 5, 'd')                                # pedana di Entei
    g.carve(9, 5, 12, 6)
    for p in [(8, 13), (16, 11), (5, 8), (13, 7)]: g.put(*p, '#')
    CV.paint(cv, g, 'fuoco', style='rock', wild=False)
    cv.void_cell = (0, 0)
    native_warp(cv, 10, 19, 26, 12, ne_slot);native_warp(cv, 11, 19, 26, 12, ne_slot)
    oid = len(cv.objs) + 1
    p = legend_script('ENTEI Safari', 244, 45, 0x88f, oid,
                      "Il calore è insopportabile.\nENTEI si alza e ruggisce!",
                      "Hai catturato ENTEI!\nLa grotta si raffredda di colpo.",
                      "ENTEI torna ad accucciarsi sulla pedana.\nPuoi riprovare quando vuoi.")
    cv.add_obj(10, 4, 217, p, flag=0x88f, move=8)
    emit(cv, 'rev51_grotta_entei')
    OUT['entei'] = (cv.gn, 10, 4)
    return cv.gn


def safari_ne():
    key = (26, 12)
    cv = V.live_canvas(key)
    safari_texts(cv.objs, key)
    # bocca della grotta: porta in CAVE_DOOR, si entra da sud
    x0, y0 = CAVE_DOOR[0] - 3, CAVE_DOOR[1] - 3
    taken = {(o['x'], o['y']) for o in cv.objs}
    foot = {(x0 + x, y0 + y) for x in range(7) for y in range(5)}
    assert not (taken & foot), taken & foot
    door = cv.place_art(x0, y0, CV.cave_mouth(), protect=True)
    assert door == CAVE_DOOR, door
    cv.bwarps.append(dict(x=door[0], y=door[1], elev=0, group=0, num=0, warp=0))
    slot = len(cv.bwarps) - 1
    # Raikou fra l'erba alta del prato
    oid = len(cv.objs) + 1
    p = legend_script('RAIKOU Safari', 243, 45, 0x884, oid,
                      "Un tuono a ciel sereno!\nRAIKOU balza fuori dall'erba alta!",
                      "Hai catturato RAIKOU!\nIl cielo sopra il prato si rasserena.",
                      "RAIKOU sparisce fra l'erba con un lampo.\nTornerà in mezzo al prato.")
    cv.add_obj(6, 23, 216, p, flag=0x884, move=8)
    OUT['raikou'] = (key, 6, 23)
    return cv, slot


def safari(cvs, ge):
    safari_south(ge['slot'])
    safari_other_texts()
    suicune()
    cv, slot = safari_ne()
    cave = entei_cave(slot)
    cv.bwarps[slot].update(group=cave[0], num=cave[1], warp=0)
    cvs[(26, 12)] = cv
    kit48.mapsec_names({97: ('GROTTA ARDENTE', 3, 9)})
    return OUT


def apply(cvs):
    gw, ge = classe_gates(cvs)
    mirabilandia(cvs, gw)
    ride_shiny()
    safari(cvs, ge)
    return OUT
