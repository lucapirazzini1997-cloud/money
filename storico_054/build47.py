#!/usr/bin/env python3
"""Pokemon Romagna 0.47 - Volo a Forlimpopoli, oggetti concreti dell'evento Befane, (rivale rinominabile, strumento mosse).

Base: ROM 0.46 (rom046.gba). Uso: python3 build47.py [--out DIR]
"""
import sys, hashlib, argparse, struct
from kit47 import *
import kit47

OUTDIR = ROOT / 'out47'
BASE046_SHA = '4078342ecbbd4e3a0e7baa9183f88f77496f0d1e1b16de1d53a706c19c0f466b'
ITEM_TABLE = 0x72f194
CHARS = None


def enc(s):
    global CHARS
    from text_codec import CHAR
    if CHARS is None: CHARS = {v: k for k, v in CHAR.items() if len(v) == 1}
    return bytes(0xfe if c == '\n' else CHARS[c] for c in s)


def u32(p): return struct.unpack_from('<I', W.d, p)[0]
def put32(p, v): struct.pack_into('<I', W.d, p, v)


def new_key_item(iid, name, desc):
    """Riusa una voce di oggetto chiave mai ottenibile in Smeraldo (FRLG) con nome e descrizione nuovi."""
    off = ITEM_TABLE + 44 * iid
    assert struct.unpack_from('<H', W.d, off + 14)[0] == iid and W.d[off + 26] == 5, iid
    assert len(name) <= 13
    W.d[off:off + 14] = (enc(name) + b'\xff').ljust(14, b'\x00')
    put32(off + 20, B + W.alloc(enc(desc) + b'\xff', 'desc ' + name))


ITEMS = {351: ('REGISTRO MOLO', 'Registro dei carichi\ndel porto di Rimini.\nCita un corriere.'),
         359: ('FATTURA', 'Fattura del corriere.\nNomina i tecnici\ndelle Befane.'),
         354: ('BOBINA EMILIA', 'Bobina del Team\nEMILIA. Alimenta\nl\'estrattore.'),
         355: ('REGOLATORE', 'Regolatore sottratto\nal Team EMILIA.\nSpento al quarto piano.'),
         356: ('PROGETTO CAVA', 'Progetto delle\nperforazioni. Da\nportare ad Ada.')}


def give(iid):
    return b'\x1a' + H(0x8000) + H(iid) + b'\x1a' + H(0x8001) + H(1) + b'\x09\x00'


def befane_items():
    for iid, (n, dsc) in ITEMS.items(): new_key_item(iid, n, dsc)

    def patch_cont(tb, flag, item, extra=b'', keep_obj=True):
        """trainerbattle tipo 2 a `tb`: nuova continuazione = vecchia + oggetto, poi si prosegue come prima."""
        assert W.d[tb:tb + 2] == b'\x5c\x02'
        pp = tb + 14;old = u32(pp) - B
        # la vecchia continuazione e': setflag f ; [removeobject n] ; goto X   oppure   setflag f ; loadword...
        code = bytes(W.d[old:old + 3]);assert code[0] == 0x29 and struct.unpack('<H', code[1:3])[0] == flag, (hex(old), code.hex())
        q = old + 3;pre = code
        if W.d[q] == 0x53: pre += bytes(W.d[q:q + 3]);q += 3
        new = pre + give(item)
        if W.d[q] == 0x05: new += bytes(W.d[q:q + 5])           # goto bersaglio originale
        else: new += b'\x05' + P(q)                           # prosegue nello script originale
        np_ = W.alloc(new, 'befane cont %d' % flag)
        put32(pp, B + np_)
    patch_cont(0x2d2a15, 635, 351)
    patch_cont(0x2d2b38, 636, 359)
    patch_cont(0x2d2c63, 637, 354)
    patch_cont(0x2d2d69, 638, 355)
    patch_cont(0x2d2e75, 639, 356)
    # Ada: ritira il PROGETTO CAVA quando glielo porti
    gp = 0x2d2606;assert W.d[0x2d2604] == 0x06 and u32(gp) == B + 0x2d2650
    s = Script('Ada ritira progetto')
    s.emit(b'\x47' + H(356) + H(1)).cmp(0, 'skip')
    s.emit(b"\x45" + H(356) + H(1)).msg("ADA: Questo è il PROGETTO CAVA! Lo tengo io, così nessuno scava più nel buio.")
    s.label('skip').emit(b'\x05' + P(0x2d2650))
    put32(gp, B + s.save())


FLY_TABLE = 0x74cfc8
HEAL_TABLE = 0x74adc0
MAPSEC_TABLE = 0x74c608
VISIT_FLAG = 0x46d


def fly_forlimpopoli():
    """Slot 5 della tabella Volo (cella (13,8) della mappa, nome 'BERTINORO', mai usato da una mappa della hack)
    diventa FORLIMPOPOLI: nome, destinazione e flag di visita 0x86F+5."""
    reg = 5
    assert tuple(W.d[FLY_TABLE + 3 * reg:FLY_TABLE + 3 * reg + 3]) == (0, 14, 18)
    nm = W.alloc(enc('FORLIMPOPOLI') + b'\xff', 'mapsec FORLIMPOPOLI')
    e = MAPSEC_TABLE + reg * 8
    assert tuple(W.d[e:e + 4]) == (13, 8, 1, 1)
    put32(e + 4, B + nm)
    W.d[FLY_TABLE + 3 * reg:FLY_TABLE + 3 * reg + 3] = bytes([35, 61, 18])
    h = HEAL_TABLE + 8 * (18 - 1)
    assert struct.unpack_from('<bbHH', W.d, h) == (0, 14, 16, 4)
    struct.pack_into('<bbHH', W.d, h, 35, 61, 3, 19)
    # entrando a Forlimpopoli si registra la visita (come le altre citta' native)
    key = (35, 61);m = W.rom.map(*key);ents = W.rom.map_scripts(m)
    old = next(p for t, p in ents if t == 3)
    # 0x874 (visita 'Verdanturf') e' riusata come flag di trama dalla hack: la visita di Forlimpopoli usa 0x46D,
    # letta dal codice del Volo nel pool di costanti a 0x124230 (caso MAPSEC 5 dello switch).
    assert u32(0x124230) == 0x874
    put32(0x124230, VISIT_FLAG)
    s = Script('Visita Forlimpopoli').emit(b'\x29' + H(VISIT_FLAG) + b'\x05' + P(old))
    W.set_map_scripts(*key, [(t, p) for t, p in ents if t != 3] + [(3, s.save())])


# ------------------------------------------------------------------ MOSSOMETRO: oggetto chiave che apre uno script
def bl_target(src):
    hi, lo = struct.unpack_from('<HH', W.d, src)
    assert hi & 0xf800 == 0xf000 and lo & 0xf800 == 0xf800, hex(src)
    off = ((hi & 0x7ff) << 11) | (lo & 0x7ff)
    if off & 0x200000: off -= 0x400000
    return src + 4 + (off << 1)


def bl_encode(src, tgt):
    off = (tgt - (src + 4)) >> 1
    return struct.pack('<HH', 0xf000 | ((off >> 11) & 0x7ff), 0xf800 | (off & 0x7ff))


def key_item_stub(script_off):
    """Copia dei due stub Thumb di 'MAPPA ROMAGNA' (callback + funzione d'uso) con script nuovo.
    Le BL sono relative alla posizione: si ricodificano per le nuove sedi."""
    CB, CBLEN, FN, FNLEN = 0xfebf4, 0x24, 0xfec3c, 0x1c
    cb = bytearray(W.d[CB:CB + CBLEN]);fn = bytearray(W.d[FN:FN + FNLEN])
    cb_t = [(8, bl_target(CB + 8)), (14, bl_target(CB + 14)), (20, bl_target(CB + 20))]
    fn_t = [(12, bl_target(FN + 12))]
    assert struct.unpack_from('<I', W.d, CB + 0x20)[0] == 0x82c9268 and struct.unpack_from('<I', W.d, FN + 0x14)[0] == 0x203a0f4
    cb_p = W.alloc(bytes(cb), 'stub callback');fn_p = W.alloc(bytes(fn), 'stub uso')
    for o, t in cb_t: W.d[cb_p + o:cb_p + o + 4] = bl_encode(cb_p + o, t)
    for o, t in fn_t: W.d[fn_p + o:fn_p + o + 4] = bl_encode(fn_p + o, t)
    put32(cb_p + 0x20, B + script_off)
    assert struct.unpack_from('<I', W.d, fn_p + 0x18)[0] == 0x80febf5
    put32(fn_p + 0x18, B + cb_p + 1)
    return B + fn_p + 1


def vtext(*parts):
    """Testo con variabili: str = testo ('\\n' = riga, '\\r' = nuova pagina), 1/2 = {STR_VAR_1/2}."""
    out = b''
    for p in parts:
        if isinstance(p, int): out += bytes([0xfd, p + 1])      # FD 02 = STR_VAR_1, FD 03 = STR_VAR_2
        else: out += b''.join((b'\xfe' if c == '\n' else b'\xfb' if c == '\r' else enc(c)) for c in p)
    return P(W.alloc(out + b'\xff', 'vtext'))


def mossometro():
    """Oggetto chiave: ricorda (stesso meccanismo del Ricordamosse) o dimentica (stesso del Cancellamosse) qualunque mossa."""
    ITEM = 350
    s = Script('Mossometro')
    s.emit(b'\x69')                                                   # lockall
    s.emit(b'\x0f\x00' + P(W.text('MOSSOMETRO: ricorda o dimentica le mosse dei tuoi POKéMON.')) + b'\x09\x04')
    s.label('menu')
    s.emit(b'\x0f\x00' + P(W.text('Vuoi far ricordare una mossa?')) + b'\x09\x05')
    s.cmp(1, 'rec_start')
    s.emit(b'\x0f\x00' + P(W.text('Vuoi far dimenticare una mossa?')) + b'\x09\x05')
    s.cmp(1, 'dim_start')
    s.label('fine').emit(b'\x6b\x02')
    # ricorda: come il Ricordamosse di Smeraldo ma gratis
    s.label('rec_start').msg('Quale POKéMON vuoi allenare?')
    s.emit(b'\x25' + H(222) + b'\x27')
    s.emit(b'\x21' + H(0x8004) + H(255)).jump('fine', 1)
    s.emit(b'\x25' + H(330)).cmp(1, 'uovo')
    s.emit(b'\x21' + H(0x8005) + H(0)).jump('nessuna', 1)
    s.msg('Quale mossa vuoi ricordare?')
    s.emit(b'\x25' + H(227) + b'\x27')
    s.emit(b'\x21' + H(0x8004) + H(0)).jump('rec_start', 1)
    s.emit(b'\x6b\x02')
    s.label('nessuna').msg('Questo POKéMON non ha mosse da ricordare.').jump('rec_start')
    s.label('uovo').msg('Un UOVO non conosce nessuna mossa.').jump('menu')
    # dimentica: come il Cancellamosse (qualunque mossa, MN comprese)
    s.label('dim_start').msg('Quale POKéMON deve dimenticare una mossa?')
    s.emit(b'\x25' + H(162) + b'\x27')
    s.emit(b'\x21' + H(0x8004) + H(255)).jump('fine', 1)
    s.emit(b'\x25' + H(330)).cmp(1, 'uovo')
    s.emit(b'\x25' + H(226)).cmp(1, 'una_sola')
    s.msg('Quale mossa va dimenticata?')
    s.emit(b'\x97\x01\x25' + H(223) + b'\x97\x00')
    s.emit(b'\x21' + H(0x8005) + H(4)).jump('dim_start', 1)
    s.emit(b'\x25' + H(225))
    s.emit(b'\x0f\x00' + vtext(1, ': dimenticare\n', 2, '. Sei sicuro?') + b'\x09\x05')
    s.cmp(1, 'dim_ok')
    s.jump('dim_start')
    s.label('dim_ok').emit(b'\x25' + H(521)).cmp(1, 'surf')
    s.emit(b'\x25' + H(224) + b'\x31' + H(378) + b'\x32')
    s.emit(b'\x0f\x00' + vtext(1, ' ha dimenticato\n', 2, ' per sempre.') + b'\x09\x04')
    s.emit(b'\x6b\x02')
    s.label('una_sola').emit(b'\x25' + H(225))
    s.emit(b'\x0f\x00' + vtext(1, ' conosce una sola mossa:\nnon si può dimenticarla.') + b'\x09\x04').jump('menu')
    s.label('surf').emit(b'\x25' + H(225))
    s.emit(b'\x0f\x00' + vtext(1, ' non può dimenticare\nSURF: servirebbe ancora.') + b'\x09\x04').jump('menu')
    return ITEM, s.save()


def add_mossometro():
    item, sp = mossometro()
    off = ITEM_TABLE + 44 * item
    assert W.d[off + 26] == 5 and struct.unpack_from('<H', W.d, off + 14)[0] == item
    tmpl = ITEM_TABLE + 44 * 361                                # MAPPA ROMAGNA: oggetto chiave con funzione d'uso sul campo
    raw = bytearray(W.d[tmpl:tmpl + 44])
    raw[0:14] = (enc('MOSSOMETRO') + b'\xff').ljust(14, b'\x00')
    struct.pack_into('<H', raw, 14, item)
    struct.pack_into('<I', raw, 20, B + W.alloc(enc('Ricorda o dimentica\nle mosse. Usalo in\nqualunque luogo.') + b'\xff', 'desc mossometro'))
    struct.pack_into('<I', raw, 28, key_item_stub(sp))
    W.d[off:off + 44] = raw
    return item


def mossometro_npc(item):
    """Un istruttore nel Centro Pokemon di Forlimpopoli (35.65) regala il MOSSOMETRO una sola volta."""
    f = 0x479
    sc = Script('Istruttore mosse').emit(b'\x6a\x5a').flag(f, 'done')
    sc.msg('ISTRUTTORE: Ho costruito il MOSSOMETRO. Fa ricordare o dimenticare qualunque mossa ai POKéMON.\n\nÈ tuo: usalo dove vuoi.')
    sc.gift(item, f, 'Hai ricevuto il MOSSOMETRO! Lo trovi tra gli strumenti.')
    sc.label('done').msg('ISTRUTTORE: Il MOSSOMETRO ricorda le mosse imparate salendo di livello. Per dimenticarne una, scegli anche le MN.').end()
    key = (35, 65);m = W.rom.map(*key);objs = copy.deepcopy(m['objects'])
    o = copy.deepcopy(objs[-1]);o.update(id=len(objs) + 1, x=4, y=4, gfx=31, move=8, ttype=0, trange=0, flag=0, script=sc.save())
    o.pop('raw', None)
    events(key, objects=objs + [o])


def main():
    ap = argparse.ArgumentParser();ap.add_argument('--out', default=str(OUTDIR));a = ap.parse_args()
    src = (ROOT / 'rom046.gba').read_bytes()
    assert hashlib.sha256(src).hexdigest() == BASE046_SHA, 'rom046.gba non e la 0.46 attesa'
    befane_items()
    fly_forlimpopoli()
    mossometro_npc(add_mossometro())
    out = Path(a.out);out.mkdir(parents=True, exist_ok=True)
    rom = bytes(W.d)
    (out / 'Pokemon_Romagna_0_47.gba').write_bytes(rom)
    print('OK', hashlib.sha256(rom).hexdigest(), hex(W.cursor))


if __name__ == '__main__':
    main()
