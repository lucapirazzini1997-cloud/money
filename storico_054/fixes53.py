"""Pokemon Romagna 0.53 - interfaccia in italiano: nomi (mosse, strumenti, abilita', tipi, nature, classi),
descrizioni (mosse, strumenti, abilita'), messaggi di lotta, menu, zaino, squadra, riepilogo, PC, opzioni,
salvataggio, negozio, pesca e testi degli script comuni.
Lavora su un oggetto W con .d (bytearray) e .alloc(bytes, label). I testi inglesi restano dove sono:
cambiano solo i puntatori (i nomi a lunghezza fissa vengono riscritti sul posto)."""
import json, re, struct
from pathlib import Path
import sys
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE / 'strumenti_rom'), str(HERE)]
from text_codec import CHAR
import fitpx
import ui53_lotta, ui53_menu, ui53_mosse, ui53_strumenti, ui53_varie

B = 0x08000000
MOVE_NAMES, MOVE_DESC = 0x32c048, 0x7c76b8
ITEMS, ABIL_NAMES, ABIL_DESC = 0x72f194, 0x32dfa7, 0x32e3a0
TYPE_NAMES, NATURES, CLASSES, BATTLE = 0x32d704, 0x7c7ce4, 0x3225a0, 0x7773fc
DATA = HERE / 'ui53'

ENC = {}
for _k, _v in CHAR.items():
    if isinstance(_v, str) and len(_v) == 1 and _v not in ENC: ENC[_v] = _k
ENC.update({'À': 0x01, 'È': 0x05, 'É': 0x06, 'Ì': 0x09, 'Ò': 0x0d, 'Ù': 0x11, "'": 0xb4, '/': 0xba, ':': 0xf0,
            '“': 0xb1, '”': 0xb2, '…': 0xb0, '&': 0x2d, '+': 0x2e, '%': 0x5b})


def enc(t, term=True):
    """{xx} = FD xx, {PB} = glifo POKéBLOCK, [hhhh..] = byte grezzi, \\n \\p \\l = FE FB FA."""
    out = bytearray(); i = 0
    while i < len(t):
        c = t[i]
        if t.startswith('{PB}', i): out += bytes([0x55, 0x56, 0x57, 0x58, 0x59]); i += 4; continue
        if c == '{': out += bytes([0xfd, int(t[i + 1:i + 3], 16)]); i += 4; continue
        if c == '[':
            j = t.index(']', i); out += bytes.fromhex(t[i + 1:j]); i = j + 1; continue
        if c == '\\':
            out.append({'n': 0xfe, 'p': 0xfb, 'l': 0xfa}[t[i + 1]]); i += 2; continue
        if c == '\n': out.append(0xfe); i += 1; continue
        out.append(ENC[c]); i += 1
    return bytes(out) + (b'\xff' if term else b'')


def raw_str(d, p):
    e = d.index(b'\xff', p); return bytes(d[p:e])


# ------------------------------------------------------------------ larghezza in pixel
_GLY = {v: k for k, v in ENC.items()}


def _plain(b):
    """byte -> testo semplice per misurare (i codici FC/FD diventano segnaposto di larghezza tipica)."""
    s = []; i = 0
    while i < len(b):
        x = b[i]
        if x == 0xfd: s.append('MMMMMMMMMM'); i += 2; continue
        if x == 0xfc:
            n = {0: 1, 1: 1, 2: 1, 3: 1, 4: 3, 5: 1, 6: 1, 8: 1, 0xb: 2, 0xc: 1, 0x10: 2, 0x11: 1, 0x12: 1, 0x13: 1, 0x14: 1}.get(b[i + 1], 0)
            i += 2 + n; continue
        if x in (0xfe, 0xfb, 0xfa): s.append('\n'); i += 1; continue
        s.append(_GLY.get(x, 'M') if x < 0xf0 or x == 0xf0 else 'M'); i += 1
    return ''.join(s)


def line_widths(d, b, font=fitpx.FONTS[0]):
    return [fitpx.width(d, l, font) for l in _plain(b).split('\n')]


# ------------------------------------------------------------------ riferimenti
# Falsi positivi: parole allineate uguali all'indirizzo di un testo inglese ma dentro
# grafica compressa LZ77 (blob 0xc2e930 e 0xd82898, sprite della specie 120). Mai toccarle.
NOT_REFS = {0xc2ea0c, 0xd82974}


def refs(d, addr, scripts=True):
    pat = struct.pack('<I', B + addr); out = []
    i = d.find(pat)
    while i >= 0:
        if i in NOT_REFS: i = d.find(pat, i + 1); continue
        if i % 4 == 0 or (scripts and ((i >= 2 and d[i - 2] == 0x0f and d[i - 1] == 0x00) or d[i - 1] == 0x67)):
            out.append(i)
        i = d.find(pat, i + 1)
    return out


def repoint(W, addr, new_bytes, label, scripts=True):
    rs = refs(W.d, addr, scripts)
    if not rs: return 0
    p = W.alloc(new_bytes, label, align=1) if 'align' in W.alloc.__code__.co_varnames else W.alloc(new_bytes, label)
    for r in rs: W.d[r:r + 4] = struct.pack('<I', B + p)
    return len(rs)


# ------------------------------------------------------------------ nomi a lunghezza fissa
def put_fixed(W, p, size, text, what):
    b = enc(text)
    assert len(b) <= size, (what, text, len(b), size)
    W.d[p:p + size] = b + b'\xff' * (size - len(b))


def names(W):
    n = json.loads((DATA / 'names.json').read_text())
    it = json.loads((DATA / 'items_raw.json').read_text())
    cnt = dict(mosse=0, strumenti=0, abilita=0, tipi=0, classi=0)
    for k, (en, itn) in n['moves'].items():
        put_fixed(W, MOVE_NAMES + 13 * int(k), 13, itn, 'mossa %s' % k); cnt['mosse'] += 1
    fix = dict(ui53_strumenti.NOMI_FIX); fix[273] = 'PORTA{PB}'
    for k, (en, itn) in it['items'].items():
        k = int(k)
        put_fixed(W, ITEMS + 44 * k, 14, fix.get(k, itn), 'strumento %d' % k); cnt['strumenti'] += 1
    for k in fix:
        if str(k) not in it['items']:
            put_fixed(W, ITEMS + 44 * k, 14, fix[k], 'strumento %d' % k); cnt['strumenti'] += 1
    for k, (en, itn) in n['abil'].items():
        put_fixed(W, ABIL_NAMES + 13 * int(k), 13, ui53_varie.ABIL_FIX.get(int(k), itn), 'abilita %s' % k); cnt['abilita'] += 1
    for k, v in ui53_varie.ABIL_FIX.items():
        if str(k) not in n['abil']: put_fixed(W, ABIL_NAMES + 13 * k, 13, v, 'abilita %d' % k); cnt['abilita'] += 1
    for i, t in enumerate(ui53_varie.TIPI):
        put_fixed(W, TYPE_NAMES + 7 * i, 7, t, 'tipo %d' % i); cnt['tipi'] += 1
    for i in range(66):
        p = CLASSES + 13 * i
        en = _dec_name(W.d, p)
        if en in ui53_varie.CLASSI:
            put_fixed(W, p, 13, ui53_varie.CLASSI[en], 'classe %d' % i); cnt['classi'] += 1
    return cnt


def _dec_name(d, p):
    s = []; i = p
    while d[i] != 0xff:
        c = CHAR.get(d[i]); s.append(c if isinstance(c, str) and len(c) == 1 and d[i] not in (0x53, 0x54, 0xb5, 0xb6) else '{%02x}' % d[i]); i += 1
    return ''.join(s)


# ------------------------------------------------------------------ descrizioni
FONT_NORMAL = 0x7ff478
LIMITS = {'mossa': 147, 'strumento': 104, 'abilita': 148}   # px: righe inglesi piu' lunghe / larghezza delle finestre


def _wrap(d, t, lim, n):
    words = t.split(' '); L = []; cur = ''
    for w in words:
        c = (cur + ' ' + w).strip()
        if fitpx.width(d, c.replace('\x01', 'POKéBLOCK'), FONT_NORMAL) <= lim: cur = c
        else: L.append(cur); cur = w
    L.append(cur)
    ok = len(L) <= n and all(fitpx.width(d, l.replace('\x01', 'POKéBLOCK'), FONT_NORMAL) <= lim for l in L)
    return L if ok else None


def _wrap_desc(d, en_ptrs, texts, max_lines, what):
    out = {}; bad = []
    for k, t in texts.items():
        ls = _wrap(d, t.replace('{PB}', '\x01'), LIMITS[what], max_lines)
        if ls is None: bad.append((what, k, t)); continue
        out[k] = '\n'.join(ls).replace('\x01', '{PB}')
    return out, bad


def descriptions(W):
    d = W.d; cnt = {}; bads = []
    # mosse
    mp = [struct.unpack_from('<I', d, MOVE_DESC + 4 * (m - 1))[0] - B for m in range(1, 355)]
    md, bad = _wrap_desc(d, mp, ui53_mosse.DESC, 2, 'mossa'); bads += bad
    for m, t in md.items():
        p = W.alloc(enc(t), 'desc mossa %d' % m)
        W.d[MOVE_DESC + 4 * (m - 1):MOVE_DESC + 4 * m] = struct.pack('<I', B + p)
    cnt['mosse'] = len(md)
    # strumenti (puntatore a +20)
    ip = {k: struct.unpack_from('<I', d, ITEMS + 44 * k + 20)[0] - B for k in ui53_strumenti.DESC}
    idd, bad = _wrap_desc(d, list(ip.values()), ui53_strumenti.DESC, 3, 'strumento'); bads += bad
    cache = {}
    for k, t in idd.items():
        if t not in cache: cache[t] = W.alloc(enc(t), 'desc strumento %d' % k)
        W.d[ITEMS + 44 * k + 20:ITEMS + 44 * k + 24] = struct.pack('<I', B + cache[t])
    cnt['strumenti'] = len(idd)
    # descrizioni gia' italiane della hack (strumenti nuovi) che escono dal riquadro: solo a capo
    rew = 0
    for k in range(1, 377):
        if k in ui53_strumenti.DESC: continue
        p = struct.unpack_from('<I', d, ITEMS + 44 * k + 20)[0] - B
        if not (0 <= p < len(d)): continue
        raw = raw_str(d, p)
        if any(x in raw for x in (0xfc, 0xfd, 0xfb, 0xfa)): continue
        t = _plain(raw)
        if all(fitpx.width(d, l, FONT_NORMAL) <= LIMITS['strumento'] for l in t.split('\n')): continue
        ls = _wrap(d, ' '.join(t.split()), LIMITS['strumento'], 3)
        if ls is None: bads.append(('strumento hack', k, t)); continue
        q = W.alloc(enc('\n'.join(ls)), 'desc strumento %d a capo' % k)
        W.d[ITEMS + 44 * k + 20:ITEMS + 44 * k + 24] = struct.pack('<I', B + q); rew += 1
    cnt['strumenti_hack_a_capo'] = rew
    # abilita' (una riga)
    ap = [struct.unpack_from('<I', d, ABIL_DESC + 4 * a)[0] - B for a in range(78)]
    ad, bad = _wrap_desc(d, ap, ui53_varie.ABIL_DESC, 1, 'abilita'); bads += bad
    for a, t in ad.items():
        p = W.alloc(enc(t), 'desc abilita %d' % a)
        W.d[ABIL_DESC + 4 * a:ABIL_DESC + 4 * a + 4] = struct.pack('<I', B + p)
    cnt['abilita'] = len(ad)
    # nature (tabella di puntatori)
    for i, nm in enumerate(ui53_varie.NATURE):
        p = W.alloc(enc(nm), 'natura %d' % i)
        W.d[NATURES + 4 * i:NATURES + 4 * i + 4] = struct.pack('<I', B + p)
    cnt['nature'] = len(ui53_varie.NATURE)
    assert not bads, bads
    return cnt


# ------------------------------------------------------------------ lotta e menu
def battle(W):
    d = W.d; n = 0; wide = []
    # limite: la riga inglese piu' larga della tabella, misurata allo stesso modo
    en_max = max(max(line_widths(d, raw_str(d, struct.unpack_from('<I', d, BATTLE + 4 * i)[0] - B))) for i in range(363))
    for i, t in ui53_lotta.T.items():
        b = enc(t)
        w = max(line_widths(d, b))
        if w > en_max: wide.append((i, w, en_max, t))
        p = W.alloc(b, 'lotta %d' % i)
        W.d[BATTLE + 4 * i:BATTLE + 4 * i + 4] = struct.pack('<I', B + p); n += 1
    return n, wide


def menus(W):
    d = W.d; done = 0; norefs = []; wide = []
    for a, t in sorted(ui53_menu.M.items()):
        old = raw_str(d, a)
        b = enc(t)
        ow = max(line_widths(d, old + b'\xff')); nw = max(line_widths(d, b))
        if nw > max(ow, 1) and nw > ow * 1.0 and len(_plain(b)) > 3: wide.append((hex(a), ow, nw, t))
        k = repoint(W, a, b, 'menu %x' % a)
        if k: done += 1
        else: norefs.append(hex(a))
    return done, norefs, wide


def apply(W):
    out = {}
    out['nomi'] = names(W)
    out['descrizioni'] = descriptions(W)
    out['lotta'], wide_b = battle(W)
    out['menu'], out['menu_senza_rif'], wide_m = menus(W)
    out['lotta_larghi'] = len(wide_b); out['menu_larghi'] = len(wide_m)
    return out, wide_b, wide_m
