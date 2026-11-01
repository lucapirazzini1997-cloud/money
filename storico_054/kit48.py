"""Strumenti comuni della 0.46: motore su ROM 0.45, pool di allenatori/flag, mappe nuove, eventi, incontri."""
import sys, re, struct, copy, random
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import engine48
sys.modules['engine32'] = engine48          # i moduli del toolkit importano engine32: usano cosi' il motore 0.46
from engine48 import *                       # noqa
import world32 as world                      # noqa
from world32 import lane, border, ground, native_warp   # noqa
import interior as I, art, art22, decor, _stamps  # noqa
from decor import rect, tall_grass            # noqa
from _town import tree, lamp, bench           # noqa
from PIL import Image, ImageDraw
import visuals33 as V                         # noqa

GROUP = 35
NEW_MAPS = []                                 # registro per relazione/test
BASE_SHA = 'f62af7e22095d85835ad9a66523ca2678d5040d34977ce5a83418f4b389f777a'   # 0.44 dell'utente

# ------------------------------------------------------------------ pool di allenatori e flag
SPECIAL_NAMES = ('MAXIE', 'WALLY', 'BRENDAN', 'MAY', 'STEVEN', 'NORMAN', 'FLANNERY', 'JUAN', 'TATE', 'WINONA', 'WATTSON',
                 'ROXANNE', 'BRAWLY', 'SIDNEY', 'PHOEBE', 'GLACIA', 'DRAKE', 'WALLACE', 'ARCHIE', 'TABITHA', 'COURTNEY',
                 'SHELLY', 'MATT', 'GRUNT', 'ADMIN', 'LEADER')


def _trainer_name(t):
    from text_codec import CHAR
    raw = W.d[0xf21000 + t * 40 + 4:0xf21000 + t * 40 + 16];s = ''
    for b in raw:
        if b == 0xff: break
        s += CHAR.get(b, '?')
    return s


def trainer_pool():
    """Id di allenatore mai citati da nessuno script della 0.45 (le loro flag 0x500+id non servono a nessuno)."""
    used = set()
    d = bytes(W.d[:0x1f00000])
    for m in re.finditer(re.escape(b'\x5c') + b'[\x00-\x09]', d):
        i = m.start()
        t, pad = struct.unpack_from('<HH', d, i + 2)
        p1 = struct.unpack_from('<I', d, i + 6)[0]
        if pad == 0 and 0x8000000 <= p1 < 0x8000000 + len(d) and t < 2000: used.add(t)
    # il motore stesso: 0xf21000 tabella da 1536 voci, flag 0x500+id valide fino a id 863
    free = [t for t in range(100, 700) if t not in used and not any(s in _trainer_name(t) for s in SPECIAL_NAMES)]
    return free


class Pool:
    def __init__(self):
        free = trainer_pool()
        self.trainers = iter(free[:60])
        self.flags = iter(0x500 + t for t in free[60:160])
        self.taken_flags = []
        self.taken_trainers = []

    def tid(self):
        t = next(self.trainers);self.taken_trainers.append(t);return t

    def flag(self, why=''):
        f = next(self.flags);self.taken_flags.append((f, why));return f


POOL = None


def init_pool():
    global POOL
    POOL = Pool();return POOL


# ------------------------------------------------------------------ mappe nuove
def new_outdoor(name, w, h, region, mtype=3, template=(34, 39)):
    key = add_map(template, region=region, mtype=mtype)
    cv = r22.RCanvas(w, h, template);empty_events(cv);cv.gn = key
    NEW_MAPS.append(dict(name=name, map=list(key), width=w, height=h, region=region))
    return cv


def mapsec_names(items):
    """items: {indice: 'NOME'}  -> scrive i nomi nella tabella aree (voce da 8 byte: x,y,w,h,ptr)."""
    from text_codec import CHAR
    a = {v: k for k, v in CHAR.items() if len(v) == 1}
    for idx, (nm, x, y) in items.items():
        p = W.alloc(bytes(a[c] for c in nm) + b'\xff', 'mapsec ' + nm)
        e = 0x74c608 + idx * 8
        W.d[e:e + 4] = bytes([x, y, 1, 1]);struct.pack_into('<I', W.d, e + 4, B + p)


# ------------------------------------------------------------------ eventi
def text_of(t): return P(W.text(t))


def sight_trainer(cv, x, y, gfx, name, mons, intro, defeat, after, rng=3, face=8, cls=5, pic=3, tid=None):
    """Allenatore che ti vede (trainerbattle 0). La flag di sconfitta e' quella nativa 0x500+id."""
    tid = tid if tid is not None else POOL.tid()
    trainer(tid, name, mons, cls=cls, pic=pic)
    s = Script('Allenatore ' + name).emit(b'\x5c\x00' + H(tid) + H(0) + text_of(intro) + text_of(defeat))
    s.emit(b'\x0f\x00' + text_of(after) + b'\x09\x02\x02')   # come i trainer nativi: loadword, callstd 2, end
    p = s.save()
    cv.add_obj(x, y, gfx, p, flag=0, move=face, ttype=1, trange=rng)
    return tid


def talk_npc(cv, x, y, gfx, text, face=8, name='NPC'):
    return cv.add_obj(x, y, gfx, Script(name).emit(b'\x6a\x5a').msg(text).end().save(), move=face)


def gift_npc(cv, x, y, gfx, ask, item, qty, thanks, done, why, face=8):
    f = POOL.flag(why)
    s = Script('Dono ' + why).emit(b'\x6a\x5a').flag(f, 'done').msg(ask)
    s.emit(b'\x1a' + H(0x8000) + H(item) + b'\x1a' + H(0x8001) + H(qty) + b'\x09\x00').cmp(0, 'full').set(f).msg(thanks).end()
    s.label('full').msg('La Borsa è piena. Fai spazio e torna da me.').end()
    s.label('done').msg(done).end()
    cv.add_obj(x, y, gfx, s.save(), move=face)
    return f


def item_ball(cv, x, y, item, qty=1, why='oggetto'):
    f = POOL.flag(why)
    s = Script('Oggetto ' + why).emit(b'\x6a')
    s.emit(b'\x1a' + H(0x8000) + H(item) + b'\x1a' + H(0x8001) + H(qty) + b'\x09\x00').cmp(0, 'full')
    oid = len(cv.objs) + 1
    s.emit(b'\x53' + H(oid)).end()
    s.label('full').msg('La Borsa è piena. Lo lascio qui.').end()
    cv.add_obj(x, y, 59, s.save(), flag=f, move=8)
    return f


def sign_at(cv, x, y, text):
    cv.put(x, y, 3, 1, 3)
    cv.bbgs.append(dict(x=x, y=y, elev=0, kind=0, arg=B + talk(text)))


def grass(cv, cells):
    """Erba alta solo dove non c'e' sentiero o altro."""
    tall_grass(cv, {c for c in cells if 0 <= c[0] < cv.w and 0 <= c[1] < cv.h and not cv.pathmask[c[1]][c[0]] and cv.over[c[1]][c[0]] is None and cv.art[c[1]][c[0]] is None and cv.terrain[c[1]][c[0]] == 'grass'})


def wood_planks(vertical=False):
    """Passerella di legno 16x16."""
    im = Image.new('RGBA', (16, 16), (0, 0, 0, 0));d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 15, 15), fill=(165, 115, 66))
    for i in range(0, 16, 4):
        d.line((i, 0, i, 15) if not vertical else (0, i, 15, i), fill=(110, 74, 41))
    d.line((0, 0, 15, 0) if not vertical else (0, 0, 0, 15), fill=(66, 41, 25), width=2)
    d.line((0, 15, 15, 15) if not vertical else (15, 0, 15, 15), fill=(66, 41, 25), width=2)
    return im


def bridge_ew(cv, x0, x1, y):
    for x in range(x0, x1 + 1):
        cv.pathmask[y][x] = False
        cv.art[y][x] = (wood_planks(), None, 0, 0x100, False)   # 0x100: terra camminabile a quota 3 sopra l'acqua


# ------------------------------------------------------------------ incontri selvatici (tabella viva)
WILD_REFS = [741084, 742940, 743100, 743236, 743520, 743616, 743692, 743808, 743872, 744008, 1298604, 1298664, 1667204]


def install_wild46(entries):
    """entries: {(g,n): dict(land=[(species,lvl)...]*12, rate=.., water=[...], wrate=..)}. Rilocazione completa della tabella."""
    old = W.rom.ptr(WILD_REFS[0])
    assert all(W.rom.ptr(p) == old for p in WILD_REFS), 'riferimenti tabella incontri discordi'
    headers = {};order = [];p = old
    while W.d[p] != 255:
        raw = bytearray(W.d[p:p + 20]);key = (raw[0], raw[1]);p += 20
        headers[key] = raw;order.append(key)
    for key, e in entries.items():
        if key not in headers:
            headers[key] = bytearray(bytes(key) + bytes(18));order.append(key)
        for field, (offset, slots) in dict(land=(4, 12), water=(8, 5)).items():
            if field not in e: continue
            mons = e[field];rate = e.get('rate' if field == 'land' else 'wrate', 20)
            arr = [mons[i % len(mons)] if isinstance(mons[0], tuple) else mons[i % len(mons)] for i in range(slots)]
            mp = W.alloc(b''.join(struct.pack('<BBH', max(2, lv - 1), lv, sp) for sp, lv in arr), 'wild monsters')
            info = W.alloc(bytes([rate, 0, 0, 0]) + P(mp), 'wild info');struct.pack_into('<I', headers[key], offset, B + info)
    np_ = W.alloc(b''.join(bytes(headers[k]) for k in order) + b'\xff\xff' + bytes(18), 'wild headers')
    for ref in WILD_REFS: struct.pack_into('<I', W.d, ref, B + np_)
    return np_, len(headers)
