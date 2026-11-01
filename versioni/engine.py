"""Motore delle versioni dalla 0.56 in poi: modifiche applicate sopra la ROM 0.55 (di cui non esistono sorgenti).

Ogni modulo di versioni/ riceve il Writer W (gia inizializzato sulla 0.55 e sulle versioni precedenti)
e scrive solo nello spazio libero. La catena e in build.py.

- Base: rom055.gba (SHA-256 2bfaa8a3...4ad6), verificata all'avvio.
- Spazio: solo le tre zone di 0xFF libere nella 0.55 (con 256 byte di margine all'inizio).
- Flag nuove: 0x500+id di allenatori che nessuno script cita, escluse tutte le flag gia' usate (flagscan52).
"""
from pathlib import Path
import sys, struct, re, hashlib, textwrap, copy
ROOT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / 'strumenti_rom')]
import romlib, inject, scr
from text_codec import CHAR

B = 0x08000000
BASE055_SHA = '2bfaa8a3ada9f8bbaa1112028f85f6d1d85e00d5bc71668e1444508b45e44ad6'
FREE055 = [(0x155a9b8, 0x1580000), (0x15ccd78, 0x1600000), (0x19c5a6d, 0x1a00000)]
ALPHA = {v: k for k, v in CHAR.items() if len(v) == 1}
ALPHA.update({'\n': 0xfe, '\r': 0xfb, 'È': 5, 'À': 1, 'É': 6, 'Ì': 9, 'Ò': 0x0d, 'Ù': 0x11})


def H(x): return struct.pack('<H', x)
def P(x): return struct.pack('<I', B + x)


class Writer(inject.Writer):
    def __init__(self, base):
        raw = base if isinstance(base, (bytes, bytearray)) else Path(base).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == BASE055_SHA, 'la base non e la 0.55 attesa'
        self.rom = romlib.Rom(raw); self.d = self.rom.data; self.log = []
        self.table = romlib.u32(self.d, inject.LAYOUT_TABLE_REFS[0]) - B; self.nlayouts = 800
        self.regions = [((s + 0x100 + 3) & ~3, e) for s, e in FREE055]; self.ri = 0; self.cursor = self.regions[0][0]
        for s, e in self.regions: assert all(v == 0xff for v in self.d[s:e]), hex(s)
        self.scripts_log = []

    def alloc(self, raw, label='', align=4):
        while True:
            s, e = self.regions[self.ri]; p = (max(self.cursor, s) + align - 1) & ~(align - 1)
            if p + len(raw) <= e: break
            self.ri += 1; assert self.ri < len(self.regions), 'ROM piena'; self.cursor = self.regions[self.ri][0]
        self.cursor = p; return super().alloc(raw, label, align)

    def enc(self, t):
        return bytes(ALPHA[c] for c in t)

    def text(self, t, width=30):
        """Testo per un riquadro di 2 righe: '\\n\\n' separa i paragrafi, a capo automatico a `width` caratteri."""
        pages = []
        for para in t.split('\n\n'):
            lines = []
            for line in para.split('\n'): lines += textwrap.wrap(line, width, break_long_words=False) or ['']
            pages += ['\n'.join(lines[i:i + 2]) for i in range(0, len(lines), 2)]
        return self.alloc(self.enc('\r'.join(pages)) + b'\xff', 'testo ' + t[:30])


W = None


def init(base):
    global W
    W = Writer(base); return W


class Script:
    def __init__(self, name): self.name = name; self.code = bytearray(); self.labels = {}; self.fix = []
    def emit(self, b): self.code += b; return self
    def label(self, k): self.labels[k] = len(self.code); return self
    def jump(self, k, cond=None):
        self.emit(b'\x05' if cond is None else b'\x06' + bytes([cond])); self.fix.append((len(self.code), k)); return self.emit(bytes(4))
    def call(self, k, cond=None):
        self.emit(b'\x04' if cond is None else b'\x07' + bytes([cond])); self.fix.append((len(self.code), k)); return self.emit(bytes(4))
    def flag(self, x, label, present=True): return self.emit(b'\x2b' + H(x)).jump(label, 1 if present else 0)
    def cmp(self, v, label, cond=1, var=0x800d): return self.emit(b'\x21' + H(var) + H(v)).jump(label, cond)
    def set(self, f): return self.emit(b'\x29' + H(f))
    def clear(self, f): return self.emit(b'\x2a' + H(f))
    def var(self, v, x): return self.emit(b'\x16' + H(v) + H(x))
    def msg(self, t): return self.emit(b'\x0f\x00' + P(W.text(t)) + b'\x09\x04')
    def ask(self, t): return self.emit(b'\x0f\x00' + P(W.text(t)) + b'\x09\x05')      # MSGBOX_YESNO -> 0x800d
    def checkitem(self, item, qty=1): return self.emit(b'\x47' + H(item) + H(qty))    # 0x800d = 1 se presente
    def additem(self, item, qty=1): return self.emit(b'\x44' + H(item) + H(qty))       # 0x800d = 1 se c'era posto
    def removeitem(self, item, qty=1): return self.emit(b'\x45' + H(item) + H(qty))
    def checkspace(self, item, qty=1): return self.emit(b'\x46' + H(item) + H(qty))    # checkitemspace
    def giveitem(self, item, qty=1):       # std 0 (con fanfara e messaggio "Hai ottenuto"), 0x800d=0 se borsa piena
        return self.emit(b'\x1a' + H(0x8000) + H(item) + b'\x1a' + H(0x8001) + H(qty) + b'\x09\x00')
    def end(self): return self.emit(b'\x6b\x02')                      # release + end (come i dialoghi nativi)
    def endall(self): return self.emit(b'\x6b\x02')
    def save(self):
        p = W.alloc(bytes(self.code), self.name)
        for at, label in self.fix: struct.pack_into('<I', W.d, p + at, B + p + self.labels[label])
        W.scripts_log.append(dict(name=self.name, pointer=hex(p), size=len(self.code))); return p


# ------------------------------------------------------------------ flag libere
def used_flags():
    import flagscan52
    used, _ = flagscan52.scan(W.d); return used


def unused_trainers():
    d = bytes(W.d[:0x1f00000]); used = set()
    for m in re.finditer(re.escape(b'\x5c') + b'[\x00-\x09]', d):
        i = m.start(); t, pad = struct.unpack_from('<HH', d, i + 2); p1 = struct.unpack_from('<I', d, i + 6)[0]
        if pad == 0 and B <= p1 < B + len(d) and t < 2000: used.add(t)
    for m in re.finditer(b'[\x5d\x5e\x5f\x60]', d):          # checktrainerflag & co.
        pass
    return [t for t in range(100, 700) if t not in used]


class FlagPool:
    def __init__(self):
        self.used = used_flags(); self.taken = []
        self.it = iter(0x500 + t for t in reversed(unused_trainers()) if (0x500 + t) not in self.used)
    def flag(self, why):
        f = next(self.it); self.used.add(f); self.taken.append((hex(f), why)); return f


POOL = None


def pool():
    global POOL
    if POOL is None: POOL = FlagPool()
    return POOL


# ------------------------------------------------------------------ eventi
def live(key): return W.rom.map(*key)


def add_object(key, x, y, gfx, script, move=8, flag=0, elev=3, ttype=0, trange=0):
    m = live(key); objs = copy.deepcopy(m['objects'])
    for o in objs: o.pop('raw', None) if False else None
    o = dict(id=len(objs) + 1, gfx=gfx, kind=0, x=x, y=y, elev=elev, move=move, rx=0, ry=0, ttype=ttype, trange=trange, script=script, flag=flag)
    objs.append(o)
    W.set_events(*key, objects=objs)
    return o['id']


def add_bg(key, x, y, script, elev=0):
    m = live(key); bgs = copy.deepcopy(m['bgs'])
    bgs.append(dict(x=x, y=y, elev=elev, kind=0, arg=B + script))
    W.set_events(*key, bgs=bgs)
    return len(bgs) - 1


def set_bg_script(key, x, y, script):
    m = live(key); bgs = copy.deepcopy(m['bgs']); n = 0
    for b in bgs:
        if (b['x'], b['y']) == (x, y): b['arg'] = B + script; n += 1
    assert n == 1, (key, x, y, n)
    W.set_events(*key, bgs=bgs)
