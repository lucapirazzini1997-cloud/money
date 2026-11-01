"""In-place text fixes for the 0.21 Italian strings: apostrophes used instead of accents, missing 'è'.
Every fix keeps the string the same length or shorter (written in place, 0xFF terminated)."""
import re
from text_codec import CHAR

REV = {v: k for k, v in CHAR.items() if isinstance(v, str) and len(v) == 1}
WORDS = {"e'": 'è', "puo'": 'può', "gia'": 'già', "piu'": 'più', "la'": 'là', "se'": 'sé', "da'": 'dà', "laggiu'": 'laggiù',
         "aspettera'": 'aspetterà', "difficolta'": 'difficoltà', "spieghera'": 'spiegherà', "profondita'": 'profondità',
         "cosi'": 'così', "diventera'": 'diventerà', "citta'": 'città', "verifichera'": 'verificherà', "perche'": 'perché',
         "pero'": 'però', "sara'": 'sarà', "potra'": 'potrà', "dovra'": 'dovrà', "liberta'": 'libertà', "attivita'": 'attività',
         "universita'": 'università', "qualita'": 'qualità', "velocita'": 'velocità', "lassu'": 'lassù', "giu'": 'giù', "verra'": 'verrà'}
MISSING_E = [r"\b(Non|Questo|Questa|PALESTRA|MISSIONE|RAMPANTE|RAVENNA|Qui|Ora|Lei|Lui|Chi|Dove|Com|C|Cosa|che|ora|non|qui|tutto) e (?=(lo|la|il|di|un|una|proprio|finita|iniziata|il|a |qui|stato|stata|pronto|pronta|vero|bello|importante|aperto|aperta|chiuso|chiusa|ancora|sempre|qui))",
             r"\b(RAMPANTE|RAVENNA|PALESTRA) e (?=[\n\x0b\x0c])"]


def decode(d, p, n=400):
    out = []
    for i in range(n):
        c = d[p + i]
        if c == 0xff:
            return out, i
        out.append(c)
    return out, n


def fix_text(s):
    t = s
    for k, v in WORDS.items():
        t = re.sub(r"(?<![\w'])" + re.escape(k) + r"(?=[\s/.,!?:;\n\x0b\x0c]|$)", v, t)
        t = re.sub(r"(?<![\w'])" + re.escape(k[0].upper() + k[1:]) + r"(?=[\s/.,!?:;\n]|$)", v[0].upper() + v[1:] if v[0] != 'è' else 'È', t)
    t = t.replace("c'e'", "c'è").replace("C'e'", "C'è")
    t = re.sub(r"\bgia (?=in |stat|pront|fatt|vist|arriv)", 'già ', t)
    for pat in MISSING_E:
        t = re.sub(pat, lambda m: m.group(0).replace(' e ', ' è ', 1), t)
    return t


def apply(d, addrs):
    """Fix the strings at the given offsets in the bytearray d. Returns list of (addr, before, after)."""
    done = []
    for p in sorted(set(addrs)):
        codes, n = decode(d, p)
        # map codes to text with control codes kept as placeholders
        chars = []
        BRK = {0xfe: '\n', 0xfb: '\x0b', 0xfa: '\x0c'}
        for c in codes:
            ch = BRK.get(c) or CHAR.get(c)
            chars.append(ch if isinstance(ch, str) and len(ch) == 1 and ch not in '\x00' else '\x01%02x' % c)
        s = ''.join(ch if len(ch) == 1 else '\x02' for ch in chars)
        t = fix_text(s)
        if t == s or 'È' in t and 'È' not in REV:
            t = t.replace('È', 'è')
            if t == s:
                continue
        # rebuild bytes: walk t, re-using original codes for placeholders
        out = []; ci = 0; orig = list(codes)
        # align by re-encoding: placeholders map back to the original control bytes in order
        ph = [c for c, ch in zip(codes, chars) if len(ch) != 1]
        pi = 0
        UNBRK = {'\n': 0xfe, '\x0b': 0xfb, '\x0c': 0xfa}
        for ch in t:
            if ch == '\x02':
                out.append(ph[pi]); pi += 1
            elif ch in UNBRK:
                out.append(UNBRK[ch])
            else:
                out.append(REV[ch])
        if len(out) > n:
            continue
        d[p:p + len(out)] = bytes(out); d[p + len(out)] = 0xff
        done.append((p, s, t))
    return done
