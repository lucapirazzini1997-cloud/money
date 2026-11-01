"""Pokemon Romagna 0.52 - Fase 1 dell'audit: flag, testi italiani, oggetti mancanti, pesca, tutor mosse, Lugo, Forli', Saline."""
import struct, copy
from kit48 import *          # noqa  (W, Script, H, P, B, talk, events, ...)
import kit48
import flagscan52

BASE_USED = set()
REMAPPED = []


# ------------------------------------------------------------------ 1. flag
def guard_pool():
    """Il pool non deve piu' dare flag gia' usate da eventi della ROM (bug 0.49/0.51: Arco=Regice, Katun=Registeel...).
    Le allocazioni che non collidono restano identiche (stessa sequenza): cambiano solo quelle in conflitto."""
    used, _ = flagscan52.scan(W.d)
    BASE_USED.clear(); BASE_USED.update(used)
    orig_init = kit48.Pool.__init__

    def init(self):
        orig_init(self)
        free = kit48.trainer_pool()
        self.fresh = iter(f for f in (0x500 + t for t in free[160:]) if f not in BASE_USED)

    def flag(self, why=''):
        f = next(self.flags)
        if f in BASE_USED:
            g = next(self.fresh)
            while g in BASE_USED: g = next(self.fresh)
            REMAPPED.append((f, g, why)); f = g
        BASE_USED.add(f)
        self.taken_flags.append((f, why)); return f
    kit48.Pool.__init__ = init
    kit48.Pool.flag = flag
    return len(BASE_USED)


def cesena_rocks(cvs):
    """34.19: tre rocce frantumabili usavano le flag della Cava dei Sigilli (0x61d, 0x620, 0x621)."""
    cv = cvs[(34, 19)]
    n = 0
    for o in cv.objs:
        if o['flag'] in (0x61d, 0x620, 0x621):
            o['flag'] = 0; n += 1
    return n


def verify_flags():
    """Ogni flag data dal pool in questa build non deve essere usata da altri eventi gia' presenti."""
    taken = [f for f, why in kit48.POOL.taken_flags]
    assert len(taken) == len(set(taken)), 'flag del pool duplicate'
    used, owners = flagscan52.scan(W.d)
    bad = []
    for f, why in kit48.POOL.taken_flags:
        maps = {(o[1], o[2]) for o in owners.get(f, ()) if o[1] != 33}
        if len(maps) > 1: bad.append((hex(f), why, sorted(maps)))
    # controllo specifico dei casi dell'audit 0.51
    for f, reason in ((0x622, 'Regice'), (0x627, 'Registeel')):
        maps = {(o[1], o[2]) for o in owners.get(f, ()) if o[1] != 33}
        if len(maps - {(35, 77), (35, 78)}) > 0: bad.append((hex(f), reason, sorted(maps)))
    assert not bad, bad
    return dict(remapped=[(hex(a), hex(b), w) for a, b, w in REMAPPED])


def apply(cvs):
    return dict(rocce=cesena_rocks(cvs))


def post():
    out = {}
    out['testi'] = translate_dialogs()
    out['pesca'] = fishing(); out['saline'] = FISHLOG['saline']
    out['oggetti'] = missing_items(); out['cascata'] = safari_waterfall()
    out['tutor'] = move_tutors()
    out['lugo'] = lugo_gate(); out['forli'] = forli_rival_heal()
    out['rivale'] = rival_name()
    return out


# ------------------------------------------------------------------ 2. testi italiani
import re, textwrap
from text_codec import CHAR
_ALPHA = {}
for _k, _v in CHAR.items():
    if isinstance(_v, str) and len(_v) == 1 and _v not in _ALPHA: _ALPHA[_v] = _k
_ALPHA['È'] = 5


def encode_it(t, width=30):
    """¶ = pagina; a capo automatico a `width` caratteri, 2 righe per riquadro. {01}.. = segnaposto FD xx."""
    pages = []
    for para in t.split('¶'):
        words = textwrap.wrap(para.replace('\n', ' '), width, break_long_words=False)
        # i segnaposto contano come 7 caratteri: ricontrollo la larghezza reale
        lines = []
        for w_ in words:
            if len(re.sub(r'\{..\}', 'XXXXXXX', w_)) > width + 2:
                lines += textwrap.wrap(w_, width - 8, break_long_words=False)
            else: lines.append(w_)
        pages += ['\n'.join(lines[i:i + 2]) for i in range(0, len(lines), 2)]
    s = '\r'.join(pages)
    out = bytearray(); i = 0
    while i < len(s):
        c = s[i]
        if c == '{':
            out += bytes([0xfd, int(s[i + 1:i + 3], 16)]); i += 4; continue
        if c == '\n': out.append(0xfe)
        elif c == '\r': out.append(0xfb)
        else: out.append(_ALPHA[c])
        i += 1
    return bytes(out) + b'\xff'


def text_refs(old):
    """Posizioni dei puntatori a `old`: allineate (tabelle, codice) o dentro istruzioni di script (loadword/message)."""
    pat = struct.pack('<I', B + old); d = W.d; out = []
    i = d.find(pat)
    while i >= 0:
        if i % 4 == 0 or (i >= 2 and d[i - 2] == 0x0f and d[i - 1] == 0x00) or d[i - 1] == 0x67:
            out.append(i)
        elif i >= 6 and 0x5c in d[i - 13:i - 4]:      # testi dei trainerbattle
            out.append(i)
        i = d.find(pat, i + 1)
    return out


def retext(old, new_text):
    refs = text_refs(old)
    assert refs, 'nessun riferimento a %x' % old
    p = W.alloc(encode_it(new_text), 'testo it %x' % old)
    for r in refs: struct.pack_into('<I', W.d, r, B + p)
    return len(refs)


def translate_dialogs():
    import testi52
    n = 0
    for old, t in testi52.DIALOGHI.items(): n += retext(old, t)
    for k, reg in testi52.REGIONE_MAPPE.items():
        W.d[W.rom.header(*k) + 20] = reg
    for idx, nm in testi52.ZONE.items():
        e = 0x74c608 + idx * 8; x, y = W.d[e], W.d[e + 1]
        kit48.mapsec_names({idx: (nm, x, y)})
    return n


# ------------------------------------------------------------------ 3. pesca
def species_ids():
    import scr
    d = bytes(W.d)
    return {scr.text(d, 0x32ae94 + i * 11, 11): i for i in range(1, 412)}

SEA = [(0, 9), (0, 10), (34, 9), (34, 22), (34, 43), (34, 44), (34, 47), (35, 36), (35, 37), (35, 40)]
FRESH = [(34, 17), (34, 20), (34, 39), (34, 84), (34, 93), (34, 96), (34, 114), (35, 10), (35, 49), (35, 50), (35, 51),
         (35, 70), (35, 71), (35, 72), (35, 73)]
TIER = {k: 'A' for k in [(0, 9), (0, 10), (34, 9), (34, 17), (34, 20), (34, 22), (34, 43), (34, 44), (34, 47), (35, 36), (35, 37)]}
TIER.update({k: 'B' for k in [(34, 39), (34, 84), (34, 93), (34, 96), (34, 114), (35, 40), (35, 70), (35, 71), (35, 72), (35, 73)]})
TIER.update({k: 'C' for k in [(35, 10), (35, 49), (35, 50), (35, 51)]})
LV = dict(A=((5, 10), (15, 25), (30, 40)), B=((5, 10), (20, 30), (35, 42)), C=((5, 10), (25, 35), (40, 48)))
FISH_SEA = ['MAGIKARP', 'TENTACOOL', 'TENTACOOL', 'HORSEA', 'KRABBY', 'WAILMER', 'TENTACRUEL', 'STARYU', 'CORSOLA', 'CHINCHOU']
FISH_FRESH = ['MAGIKARP', 'GOLDEEN', 'GOLDEEN', 'BARBOACH', 'CORPHISH', 'SEAKING', 'WHISCASH', 'CORPHISH', 'POLIWHIRL', 'GYARADOS']


FISHLOG = {}


def fishing():
    sp = species_ids()
    old = W.rom.ptr(kit48.WILD_REFS[0])
    assert all(W.rom.ptr(p) == old for p in kit48.WILD_REFS)
    headers, order = {}, []; p = old
    while W.d[p] != 255:
        raw = bytearray(W.d[p:p + 20]); key = (raw[0], raw[1]); p += 20
        headers[key] = raw; order.append(key)
    n = 0
    for key in SEA + FRESH:
        names = FISH_SEA if key in SEA else FISH_FRESH
        (o1, o2), (g1, g2), (s1, s2) = LV[TIER[key]]
        lv = [(o1, o2), (o1, o2), (g1, g2), (g1, g2), (g1, g2), (s1, s2), (s1, s2), (s1, s2), (s1, s2), (s1, s2)]
        mons = b''.join(struct.pack('<BBH', a, b, sp[nm]) for nm, (a, b) in zip(names, lv))
        mp = W.alloc(mons, 'pesca %d,%d' % key)
        info = W.alloc(bytes([20, 0, 0, 0]) + P(mp), 'pesca info')
        if key not in headers:
            headers[key] = bytearray(bytes(key) + bytes(18)); order.append(key)
        assert struct.unpack_from('<I', headers[key], 16)[0] == 0, key
        struct.pack_into('<I', headers[key], 16, B + info); n += 1
    FISHLOG['saline'] = saline_levels(headers)
    np_ = W.alloc(b''.join(bytes(headers[k]) for k in order) + b'\xff\xff' + bytes(18), 'wild headers 0.52')
    for ref in kit48.WILD_REFS: struct.pack_into('<I', W.d, ref, B + np_)
    return n


def saline_levels(headers):
    """Saline di Cervia (34.9): selvatici fino al Lv 15 prima della prima palestra -> massimo Lv 10 (copia nuova della tabella)."""
    raw = headers[(34, 9)]
    ip = struct.unpack_from('<I', raw, 4)[0] - B
    rate = W.d[ip]; mp = struct.unpack_from('<I', W.d, ip + 4)[0] - B
    mons = []
    for i in range(12):
        lo, hi, spc = struct.unpack_from('<BBH', W.d, mp + i * 4)
        hi = min(hi, 10); lo = max(4, min(lo, hi - 2))
        mons.append((lo, hi, spc))
    nm = W.alloc(b''.join(struct.pack('<BBH', *m) for m in mons), 'saline lv')
    ni = W.alloc(bytes([rate, 0, 0, 0]) + P(nm), 'saline info')
    struct.pack_into('<I', raw, 4, B + ni)
    return [(a, b) for a, b, _ in mons]


# ------------------------------------------------------------------ 4. oggetti mancanti
ACRO_BIKE, GOOD_ROD, SUPER_ROD, HM07 = 272, 263, 264, 345
GIFTS = {}


def gift_npc(key, x, y, gfx, item, intro, after, why, need=None, need_text=None, face=None):
    f = kit48.POOL.flag(why)
    s = Script(why).emit(b'\x6a\x5a')
    s.flag(f, 'done')
    if need:
        s.flag(need, 'ok').msg(need_text).end().label('ok')
    s.msg(intro)
    s.gift(item, f, after)
    s.label('done').msg(after).end()
    p = s.save()
    m = W.rom.map(*key)
    obs = copy.deepcopy(m['objects'])
    assert all((o['x'], o['y']) != (x, y) for o in obs)
    obs.append(dict(id=max([o['id'] for o in obs] + [0]) + 1, gfx=gfx, x=x, y=y, elev=3, move=face or 8, script=p, flag=0))
    for o in obs: o.pop('raw', None) if o.get('id') == obs[-1]['id'] else None
    events(key, objects=obs)
    GIFTS[why] = (key, (x, y), hex(f))
    return f


def missing_items():
    gift_npc((34, 42), 13, 9, 22, ACRO_BIKE,
             "Ti piacciono i salti? Oltre alla BICI DA CORSA esiste la BICI CROSS: salta i binari e le rocce strette.\n\nTe la regalo: scegli tu quale usare.",
             "Con la BICI CROSS tieni premuto B per saltare. Le aree a nord del SAFARI ti aspettano!",
             'bici cross')
    gift_npc((34, 44), 11, 21, 7, GOOD_ROD,
             "Nel porto canale abboccano pesci che non vedi in mare aperto. Prova con questo!",
             "Con l'AMO BUONO peschi POKéMON più forti. Prova nel canale e in mare.",
             'amo buono rimini', face=8)
    gift_npc((34, 96), 64, 46, 7, SUPER_ROD,
             "Hai la quinta medaglia? Allora sei pronto per i pesci grossi del ravennate.",
             "Col SUPER AMO abboccano i POKéMON più rari. Anche nei canali e nei laghi!",
             'super amo ravenna', need=0x86b,
             need_text="Torna quando avrai la quinta medaglia: il SUPER AMO è per pescatori esperti.", face=8)
    return GIFTS


def safari_waterfall():
    """L'addetto del Safari (26.3) regala la MN CASCATA dopo l'ottava medaglia (cascata dell'area Sud-est)."""
    key = (26, 3); m = W.rom.map(*key)
    obs = copy.deepcopy(m['objects'])
    o = [o for o in obs if o['id'] == 1][0]
    old = o['script']
    f = kit48.POOL.flag('mn cascata safari')
    s = Script('Safari MN Cascata').emit(b'\x6a\x5a')
    s.flag(0x86e, 'give').emit(b'\x05' + P(old))
    s.label('give').flag(f, 'old')
    s.msg("Hai otto medaglie! Nell'area Sud-est c'è una cascata che nessuno risale da anni.\n\nPrendi questa MN: con CASCATA potrai risalirla.")
    s.gift(HM07, f, "CASCATA si usa fuori dalla lotta davanti a una cascata. Serve l'ottava medaglia.")
    s.label('old').emit(b'\x05' + P(old))
    o['script'] = s.save()
    events(key, objects=obs)
    return hex(f)


# ------------------------------------------------------------------ 5. ricorda / dimentica mosse (Cervia, locanda 34.5)
def _sp(s, n): return s.emit(b'\x25' + H(n))
def _ask(s, t): return s.emit(b'\x0f\x00' + P(W.alloc(encode_it(t), 'testo')) + b'\x09\x05')
def _say(s, t): return s.emit(b'\x0f\x00' + P(W.alloc(encode_it(t), 'testo')) + b'\x09\x04')


def move_tutors():
    key = (34, 5)
    r = Script('Ricordamosse').emit(b'\x6a\x5a')
    r.msg("Sono la MAESTRA DELLE MOSSE. Faccio ricordare ai POKéMON le mosse che hanno dimenticato.\n\nPer chi viaggia in Romagna è gratis!")
    r.label('who').msg("Quale POKéMON vuole ricordare una mossa?")
    _sp(r, 0xde).emit(b'\x27').cmp(0xff, 'bye', var=0x8004)
    _sp(r, 0x14a).cmp(1, 'egg')
    r.cmp(0, 'none', var=0x8005)
    r.msg("Quale mossa vuoi ricordare?")
    _sp(r, 0xe3).emit(b'\x27').cmp(0, 'who', var=0x8004)
    r.label('bye').msg("Torna quando vuoi: le mosse non si dimenticano mai davvero.").end()
    r.label('egg').msg("Un UOVO non conosce ancora nessuna mossa!").jump('who')
    r.label('none').msg("Questo POKéMON non ha mosse da ricordare.").jump('who')
    pr = r.save()

    c = Script('Cancellamosse').emit(b'\x6a\x5a')
    _ask(c, "Sono il CANCELLAMOSSE. Posso far dimenticare una mossa a un POKéMON, anche una MN.¶Vuoi far dimenticare una mossa?")
    c.cmp(0, 'bye')
    c.label('who').msg("Quale POKéMON deve dimenticare una mossa?")
    _sp(c, 0xa2).emit(b'\x27').cmp(0xff, 'bye', var=0x8004)
    _sp(c, 0x14a).cmp(1, 'egg')
    _sp(c, 0xe2).cmp(1, 'one')
    c.msg("Quale mossa deve dimenticare?")
    c.emit(b'\x97\x01'); _sp(c, 0xdf); c.emit(b'\x97\x00')          # fadescreen
    c.cmp(4, 'who', var=0x8005)
    _sp(c, 0xe1)
    _ask(c, "{02} deve dimenticare {03}?")
    c.cmp(0, 'bye')
    _sp(c, 0x209).cmp(1, 'surf')
    _sp(c, 0xe0)
    c.emit(b'\x31' + H(0x17a) + b'\x32')                                # playfanfare, waitfanfare
    _say(c, "Fatto! {02} ha dimenticato {03}.").end()
    c.label('one'); _sp(c, 0xe1); _say(c, "{02} conosce una sola mossa: non può dimenticarla.").end()
    c.label('egg').msg("Un UOVO non conosce ancora nessuna mossa!").end()
    c.label('surf'); _sp(c, 0xe1); _say(c, "{02} non vuole dimenticare SURF in mezzo all'acqua!").end()
    c.label('bye').msg("Torna se una mossa va dimenticata.").end()
    pc = c.save()
    m = W.rom.map(*key); obs = copy.deepcopy(m['objects'])
    nid = max(o['id'] for o in obs) + 1
    obs.append(dict(id=nid, gfx=29, x=3, y=6, elev=3, move=8, script=pr, flag=0))
    obs.append(dict(id=nid + 1, gfx=46, x=5, y=6, elev=3, move=8, script=pc, flag=0))
    events(key, objects=obs)
    return dict(ricorda=hex(pr), dimentica=hex(pc))


# ------------------------------------------------------------------ 6. Lugo dopo Ravenna, cura prima del rivale a Forli'
RAVENNA_DONE = 0x2ac      # 34.100: ultimo passo della missione del Team Emilia a Ravenna


def lugo_gate():
    """Casello Ravenna -> Via dei Canali (35.98): si passa solo dopo gli eventi del Team Emilia a Ravenna."""
    key = (35, 98); m = W.rom.map(*key)
    bl = W.rom.blocks(m)
    s = Script('Blocco Lugo').emit(b'\x69')
    s.flag(RAVENNA_DONE, 'ok')
    s.msg("Il passaggio verso LUGO è chiuso.\nPrima aiuta Ravenna contro il TEAM EMILIA!")
    s.emit(b'\x39' + bytes([35, 98, 255]) + H(8) + H(4) + b'\x27')
    s.label('ok').emit(b'\x6b\x02')
    p = s.save()
    cs = copy.deepcopy(m['coords'])
    for y in range(m['height']):
        if not (int(bl[y, 2]) >> 10) & 3:
            cs.append(dict(x=2, y=y, elev=0, var=0x400e, val=0, script=p))
    events(key, coords=cs)
    return [(c['x'], c['y']) for c in cs]


def forli_rival_heal():
    """Il rivale a Forli' ferma il giocatore appena entra: prima della lotta cura la squadra."""
    import scr
    m = W.rom.map(34, 68)
    o = [o for o in m['objects'] if o['id'] == 15][0]
    ins, _ = scr.decode(bytes(W.d), o['script'], 80)
    at = [i for i, (a, nm, ar) in enumerate(ins) if nm == 'lock']
    assert at, 'lock non trovato'
    a_lock = ins[at[0]][0]; a_lw, nm, ar = ins[at[0] + 1]; a_std = ins[at[0] + 2][0]
    assert nm == 'loadword' and W.d[a_std] == 0x09, (nm, hex(a_std))
    after = a_std + 2
    s = Script('Rivale Forli cura')
    s.emit(b'\x6a').emit(b'\x0f\x00' + struct.pack('<I', ar[1]) + b'\x09\x04')
    s.msg("ALDO: Aspetta, la tua squadra è stanca. Prima la curo io: voglio una lotta vera!")
    s.emit(b'\x25' + H(0))                                   # special HealPlayerParty
    s.emit(b'\x05' + P(after))
    p = s.save()
    W.d[a_lock:a_lock + 5] = b'\x05' + P(p)
    for i in range(a_lock + 5, after): W.d[i] = 0x00        # nop
    return hex(p)


# ------------------------------------------------------------------ 7. rivale rinominabile
RIVAL_VAR = 0x40fc            # 0x40fc-0x40ff: 8 byte = nome del rivale (7 lettere + fine). Vuoto/0 -> "ALDO"
TPL_ARRAY_LIT = 0xe31a8       # letterale di sNamingScreenTemplates in NamingScreen_Init
TPL_ARRAY = 0x73785c
TPL_PLAYER = 0x73782c


def _enc(s): return bytes(_ALPHA[c] for c in s)


def rival_name():
    import asm52, scr
    out = {}
    aldo = W.alloc(_enc('ALDO') + b'\xff', 'ALDO')
    # 1) segnaposto {RIVALE} (FD 06): nome scelto dal giocatore, altrimenti ALDO
    exp = bytearray(asm52.RIVAL_EXPAND); struct.pack_into('<I', exp, 32, B + aldo)
    assert struct.unpack_from('<I', W.d, 0x9090)[0] == B + 0x7933e4     # sito atteso (BRENDAN)
    W.d[0x907c:0x907c + len(exp)] = exp
    # 2) nome in lotta: gli allenatori che si chiamano "ALDO" mostrano il nome scelto
    for site, lit, code in ((0x14f642, 0x14f650, asm52.HOOK_TRAINER1), (0x14f924, 0x14f938, asm52.HOOK_TRAINER2)):
        assert struct.unpack_from('<I', W.d, lit)[0] == 0x08f21004, hex(lit)
        h = W.alloc(code, 'hook nome rivale')
        off = lit - ((site + 4) & ~3)
        W.d[site:site + 4] = struct.pack('<HH', 0x4800 | (off // 4), 0x4700)     # ldr r0,[pc,#off]; bx r0
        struct.pack_into('<I', W.d, lit, B + h + 1)
    # 3) schermata del nome: nuovo modello "NOME DEL RIVALE?" (indice 5), senza icona
    title = W.alloc(_enc('NOME DEL RIVALE?') + b'\xff', 'titolo rivale')
    tpl = bytearray(W.d[TPL_PLAYER:TPL_PLAYER + 12]); tpl[2] = 0; struct.pack_into('<I', tpl, 8, B + title)
    tp = W.alloc(bytes(tpl), 'modello nome rivale')
    arr = bytearray(W.d[TPL_ARRAY:TPL_ARRAY + 20]) + struct.pack('<I', B + tp)
    ap = W.alloc(bytes(arr), 'modelli nome')
    assert struct.unpack_from('<I', W.d, TPL_ARRAY_LIT)[0] == B + TPL_ARRAY
    struct.pack_into('<I', W.d, TPL_ARRAY_LIT, B + ap)
    # tabella delle funzioni del titolo (indicizzata dal numero del modello): voce 5 = titolo senza Pokemon
    TITLE_TAB_LIT = 0xe4b9c
    assert struct.unpack_from('<I', W.d, TITLE_TAB_LIT)[0] == B + 0x7377dc
    tt = bytearray(W.d[0x7377dc:0x7377dc + 20]) + struct.pack('<I', 0x080e4ab1)
    tp2 = W.alloc(bytes(tt), 'titoli nome')
    struct.pack_into('<I', W.d, TITLE_TAB_LIT, B + tp2)
    nat = W.alloc(asm52.NATIVE_NAME, 'nativo nome rivale')
    # 4) in laboratorio, prima della prima frase del rivale
    lab = 0x2cbbbe
    assert W.d[lab] == 0x04, hex(W.d[lab])
    old_call = struct.unpack_from('<I', W.d, lab + 1)[0]
    s = Script('Nome rivale')
    s.emit(b'\x04' + struct.pack('<I', old_call))
    s.cmp(0, 'ask', var=RIVAL_VAR).emit(b'\x03')                         # gia' scelto: return
    s.label('ask')
    _say(s, "Il tuo vicino di casa è arrivato di corsa al laboratorio.¶Come si chiama il tuo amico?")
    s.emit(b'\x23' + struct.pack('<I', B + nat + 1) + b'\x27')            # callnative; waitstate
    s.emit(b'\x03')
    p = s.save()
    struct.pack_into('<I', W.d, lab + 1, B + p)
    out['lab'] = hex(p)
    # 5) "ALDO" nei testi -> {RIVALE}
    out['testi'] = rival_texts()
    return out


def rival_texts():
    import romlib, scr
    d = bytes(W.d); R = romlib.Rom(d)
    texts = set()
    def walk(p, seen):
        if p in seen or not (0 <= p < len(d)): return
        seen.add(p)
        try: ins, _ = scr.decode(d, p, 600)
        except Exception: return
        for a, nm, ar in ins:
            op = d[a]
            if op in (0x04, 0x05, 0x06, 0x07) and ar and B <= ar[-1] < B + len(d): walk(ar[-1] - B, seen)
            if op == 0x0f and ar and B <= ar[-1] < B + len(d): texts.add(ar[-1] - B)
            if op == 0x67 and B <= ar[0] < B + len(d): texts.add(ar[0] - B)
            if op == 0x5c:
                for v in ar[3:]:
                    if B <= v < B + len(d):
                        if ar[0] in (1, 2, 6, 8) and v == ar[-1]: walk(v - B, seen)
                        else: texts.add(v - B)
    for g, c in flagscan52.group_counts(d).items():
        if g not in (0, 1, 2, 16, 22, 26, 34, 35): continue
        for n in range(c):
            try: m = R.map(g, n)
            except Exception: continue
            seen = set()
            for lab, p in flagscan52.entries(R, m): walk(p, seen)
    word = _enc('ALDO'); letters = set(_ALPHA[c] for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzàèéìòù')
    n = 0
    for t in texts:
        end = W.d.find(b'\xff', t, t + 2000)
        if end < 0: continue
        s = bytearray(W.d[t:end]); i = 0; changed = False
        while True:
            i = s.find(word, i)
            if i < 0: break
            before = s[i - 1] if i > 0 else 0x00
            after = s[i + 4] if i + 4 < len(s) else 0xff
            if (i > 0 and before in letters and not (i > 1 and s[i - 2] == 0xfd)) or after in letters:
                i += 4; continue
            s[i:i + 4] = b'\xfd\x06'; changed = True; n += 1
        if changed:
            W.d[t:end + 1] = bytes(s) + b'\xff' + b'\xff' * (end - t - len(s))
    return n
