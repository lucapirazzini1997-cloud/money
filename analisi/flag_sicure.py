#!/usr/bin/env python3
"""Flag 0x20-0x4FF e variabili 0x4000-0x40FF non usate dagli script: quali sono davvero sicure (Lotto 1, 0.58).

Una flag e' sicura solo se nessuna di queste fonti la usa:
  1. script della ROM (registri/flag.json, scansione flagscan52 di oggetti, script, coord, cartelli, script di mappa);
  2. oggetti nascosti delle mappe della ROM (bg di tipo 7): il codice usa la flag 0x1F4 + id
     (field_control_avatar.c, item_use.c);
  3. codice C e dati di Smeraldo (pret/pokeemerald): ogni costante FLAG_* citata in src/, include/ e data/
     (anche data/maps/: le mappe di Hoenn sono ancora nella ROM), piu' gli intervalli usati con un indice:
     allenatori registrati nel Pokenav (0x15C + REMATCH_*), FLAG_DECORATION_1..14, FLAG_HIDE_UNION_ROOM_PLAYER_1..8,
     carte del Dono Segreto (WONDER_CARD_FLAG_OFFSET, 20 flag), oggetti nascosti (0x1F4 + id);
  4. codice della ROM: ogni chiamata a FlagSet/FlagClear/FlagGet (BL diretta o puntatore in tabella di
     letterali) con il numero della flag calcolabile dalle istruzioni prima della chiamata. Le chiamate con un
     numero non calcolabile si elencano a parte.

Le variabili seguono le stesse regole (script della ROM, codice e dati di Smeraldo, chiamate a GetVarPointer,
VarGet e VarSet nel codice della ROM); in piu' si escludono 0x4000-0x400F (temporanee, azzerate a ogni cambio
di mappa) e 0x4010-0x401F (grafica degli oggetti variabili).

Uso:
  python3 analisi/flag_sicure.py --smeraldo CARTELLA_POKEEMERALD     rigenera registri/flag_smeraldo.json
  python3 analisi/flag_sicure.py ROM.gba [uscita.json]                 classifica le flag della ROM
"""
import sys, os, re, json, struct, collections
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / 'strumenti_rom'), str(ROOT / 'versioni')]

B = 0x08000000
# Funzioni del codice di Smeraldo in questa ROM (simboli di pokeemerald + 0x194, verificate decodificando i
# comandi di script setflag/clearflag/checkflag della tabella a 0x1dba9c).
FLAGSET, FLAGCLEAR, FLAGGET = 0x809d8d4, 0x809d8fc, 0x809d924
SCRIPT_CMD_TABLE = 0x1dba9c
# stesse funzioni per le variabili (setvar 0x16 -> GetVarPointer, copyvarifnotzero 0x1a -> VarGet)
GETVARPTR, VARGET, VARSET = 0x809d7dc, 0x809d828, 0x809d844
SMERALDO_JSON = ROOT / 'registri' / 'flag_smeraldo.json'
LO, HI = 0x20, 0x500
CODE_BL_END = 0x4a0000      # una BL arriva a +-4 MB: oltre, le chiamate passano da un puntatore (cercato ovunque)


# ------------------------------------------------------------------ 3. sorgente di Smeraldo
def parse_flags_h(path):
    defs = {}
    for line in open(path):
        m = re.match(r'#define\s+(\w+)\s+(.+?)\s*(//.*)?$', line)
        if m: defs[m.group(1)] = m.group(2)
    val = {}
    def ev(n, depth=0):
        if n in val: return val[n]
        if depth > 20 or n not in defs: return None
        expr = defs[n]
        for t in set(re.findall(r'\b[A-Za-z_]\w*', expr)):
            v = ev(t, depth + 1)
            if v is None: return None
            expr = re.sub(r'\b%s\b' % t, str(v), expr)
        try: val[n] = int(eval(expr, {}, {}))
        except Exception: return None
        return val[n]
    for n in defs: ev(n)
    return val


def smeraldo(pe):
    pe = Path(pe)
    val = parse_flags_h(pe / 'include' / 'constants' / 'flags.h')
    use = collections.defaultdict(set)
    for sub in ('src', 'include', 'data'):
        for f in (pe / sub).rglob('*'):
            if f.suffix not in ('.c', '.h', '.inc', '.s', '.json', '.pory') or not f.is_file(): continue
            rel = str(f.relative_to(pe))
            if rel == 'include/constants/flags.h': continue
            for t in set(re.findall(r'\bFLAG_\w+', f.read_text(errors='ignore'))):
                if t in val and LO <= val[t] < HI: use[val[t]].add('%s (%s)' % (t, rel))
    flags_h = (pe / 'include' / 'constants' / 'flags.h').read_text()
    n_reg = len(re.findall(r'#define\s+FLAG_REGISTERED_\w+', flags_h))
    ranges = [('TRAINER_REGISTERED_FLAGS_START', n_reg, 'allenatori registrati nel Pokenav (match_call.c: inizio + REMATCH_*)'),
              ('FLAG_DECORATION_1', 14, 'decorazioni (decoration.c, secret_base.c)'),
              ('FLAG_HIDE_UNION_ROOM_PLAYER_1', 8, 'giocatori della Union Room (union_room_player_avatar.c)')]
    for name, n, why in ranges:
        for i in range(n):
            if LO <= val[name] + i < HI: use[val[name] + i].add(why)
    wc = 1000          # WONDER_CARD_FLAG_OFFSET (include/constants/mystery_gift.h? in global.h), 20 flag
    m = re.search(r'#define\s+WONDER_CARD_FLAG_OFFSET\s+(\w+)', '\n'.join(
        p.read_text(errors='ignore') for p in (pe / 'include').rglob('*.h')))
    if m:
        try: wc = int(m.group(1), 0)
        except ValueError: wc = val.get(m.group(1), wc)
    for i in range(20):
        if LO <= wc + i < HI: use[wc + i].add('carte del Dono Segreto (mystery_gift.c)')
    # definizioni non calcolabili (dipendono da costanti di altri file): si segnalano, non si ignorano
    non_calc = sorted(n for n in re.findall(r'#define\s+(FLAG_\w+)', flags_h) if n not in val)
    import subprocess
    try: rev = subprocess.run(['git', '-C', str(pe), 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
    except Exception: rev = '?'
    return dict(fonte='pret/pokeemerald ' + rev, hidden_start=val['FLAG_HIDDEN_ITEMS_START'], non_calcolabili=non_calc,
                usate={hex(f): sorted(w) for f, w in sorted(use.items())}, variabili=smeraldo_vars(pe),
                allenatori=smeraldo_trainers(pe))


def smeraldo_trainers(pe):
    """Numeri di allenatore citati dal codice C di Smeraldo (rivincite, Pokenav, Lotta Frontier...), tolte le
    tabelle che li elencano tutti (src/data/trainers.h, trainer_parties.h) e le mappe."""
    val = parse_flags_h(pe / 'include' / 'constants' / 'opponents.h')
    use = collections.defaultdict(set)
    for f in list((pe / 'src').rglob('*.c')) + list((pe / 'src' / 'data').rglob('*.h')):
        rel = str(f.relative_to(pe))
        if rel.endswith(('data/trainers.h', 'data/trainer_parties.h')): continue
        for t in set(re.findall(r'\bTRAINER_\w+', f.read_text(errors='ignore'))):
            if t in val and 0 < val[t] < 0x360 and not t.startswith('TRAINER_PIC') and not t.endswith('_COUNT'):
                use[val[t]].add('%s (%s)' % (t, rel))
    return {str(t): sorted(w) for t, w in sorted(use.items())}


def smeraldo_vars(pe):
    """Variabili 0x4000-0x40FF citate dal codice e dai dati di Smeraldo, piu' i due blocchi a indice."""
    val = parse_flags_h(pe / 'include' / 'constants' / 'vars.h')
    use = collections.defaultdict(set)
    for sub in ('src', 'include', 'data'):
        for f in (pe / sub).rglob('*'):
            if f.suffix not in ('.c', '.h', '.inc', '.s', '.json', '.pory') or not f.is_file(): continue
            rel = str(f.relative_to(pe))
            if rel == 'include/constants/vars.h': continue
            for t in set(re.findall(r'\bVAR_\w+', f.read_text(errors='ignore'))):
                if t in val and 0x4000 <= val[t] < 0x4100: use[val[t]].add('%s (%s)' % (t, rel))
    for i in range(16):
        use[0x4000 + i].add('temporanea: azzerata a ogni cambio di mappa (VAR_TEMP_*)')
        use[0x4010 + i].add('grafica di oggetto variabile (VAR_OBJ_GFX_ID_*, event_data.c)')
    return {hex(v): sorted(w) for v, w in sorted(use.items())}


# ------------------------------------------------------------------ 2. oggetti nascosti della ROM
def hidden_items(R, hidden_start):
    import flagscan52
    d = bytes(R.data); out = collections.defaultdict(list)
    for g, n in flagscan52.real_maps(d):
        try: m = R.map(g, n)
        except Exception: continue
        for b in m.get('bgs', []):
            if b['kind'] == 7:
                hid = (b['arg'] >> 16) & 0xffff
                out[hidden_start + hid].append('%d.%d oggetto nascosto %d,%d' % (g, n, b['x'], b['y']))
    return out


# ------------------------------------------------------------------ 4. codice della ROM
def _bl(h1, h2, at):
    if h1 >> 11 != 0x1e or h2 >> 11 != 0x1f: return None
    off = ((h1 & 0x7ff) << 12) | ((h2 & 0x7ff) << 1)
    if off & 0x400000: off -= 0x800000
    return B + at + 4 + off


def _r0_before(d, at):
    """Valore di r0 alla chiamata in 'at', simulando le ultime 8 istruzioni (solo costanti); None se ignoto."""
    regs = {}
    for a in range(max(0, at - 16), at, 2):
        h = struct.unpack_from('<H', d, a)[0]
        if h >> 11 == 0x04: regs[(h >> 8) & 7] = h & 0xff                       # movs rd,#imm
        elif h >> 11 == 0x09:                                                   # ldr rd,[pc,#imm]
            p = ((a + 4) & ~3) + (h & 0xff) * 4
            regs[(h >> 8) & 7] = struct.unpack_from('<I', d, p)[0] if p + 4 <= len(d) else None
        elif h >> 11 == 0x00 and (h >> 6) & 31:                                  # lsls rd,rs,#imm
            rs, rd = (h >> 3) & 7, h & 7
            regs[rd] = (regs[rs] << ((h >> 6) & 31)) & 0xffffffff if regs.get(rs) is not None else None
        elif h >> 11 == 0x01:                                                   # lsrs rd,rs,#imm
            rs, rd = (h >> 3) & 7, h & 7
            regs[rd] = regs[rs] >> ((h >> 6) & 31) if regs.get(rs) is not None else None
        elif h >> 11 == 0x06:                                                   # adds rd,#imm
            r = (h >> 8) & 7; regs[r] = regs[r] + (h & 0xff) if regs.get(r) is not None else None
        elif h >> 11 == 0x07:                                                   # subs rd,#imm
            r = (h >> 8) & 7; regs[r] = regs[r] - (h & 0xff) if regs.get(r) is not None else None
        elif h >> 9 == 0x0e:                                                    # adds rd,rs,#imm3
            rs, rd = (h >> 3) & 7, h & 7
            regs[rd] = regs[rs] + ((h >> 6) & 7) if regs.get(rs) is not None else None
        elif h >> 6 == 0x0700 >> 6 and False: pass
        elif (h & 0xffc0) == 0x1c00:                                            # movs rd,rs (adds #0)
            rs, rd = (h >> 3) & 7, h & 7; regs[rd] = regs.get(rs)
        elif (h & 0xff00) == 0x4600:                                            # mov rd,rs (alti)
            rd = (h & 7) | ((h >> 4) & 8); rs = (h >> 3) & 15
            if rd < 8: regs[rd] = regs.get(rs) if rs < 8 else None
        else:
            # qualunque altra istruzione che scrive un registro basso lo rende ignoto
            if h >> 13 in (0, 1, 2, 3) or h >> 12 in (5, 6, 8, 9, 10): regs[h & 7] = None
            if h >> 11 in (0x0f, 0x1e, 0x1f) or h >> 8 in (0xbd,) or h >> 12 == 0xd: regs = {}   # salti
    v = regs.get(0)
    return v & 0xffff if v is not None and v < 0x10000 else None


def code_calls(d, lo=0, hi=None, targets=None):
    hi = hi or len(d)
    targets = targets or {FLAGSET: 'FlagSet', FLAGCLEAR: 'FlagClear', FLAGGET: 'FlagGet'}
    const = collections.defaultdict(list); unknown = []
    for at in range(lo, min(hi, len(d)) - 4, 2):
        h1, h2 = struct.unpack_from('<HH', d, at)
        t = _bl(h1, h2, at)
        if t in targets:
            f = _r0_before(d, at)
            if f is None: unknown.append('%s a %s' % (targets[t], hex(at)))
            else: const[f].append('%s a %s' % (targets[t], hex(at)))
    # chiamate lunghe: puntatore alla funzione (|1) in un letterale
    lits = {struct.pack('<I', t | 1): n for t, n in targets.items()}
    for v, n in lits.items():
        for m in re.finditer(re.escape(v), d):
            if m.start() % 4 == 0: unknown.append('%s: puntatore a %s' % (n, hex(m.start())))
    return const, unknown


# ------------------------------------------------------------------ classificazione
def classify(rom_path):
    import romlib
    R = romlib.Rom(str(rom_path)); d = bytes(R.data)
    sm = json.load(open(SMERALDO_JSON))
    # registri/flag.json (genera.py) non segue gli script dopo le lotte; flagscan52 si': si usano tutte e due
    import flagscan52
    script = {int(k, 16) for k in json.load(open(ROOT / 'registri' / 'flag.json'))} | flagscan52.scan(d)[0]
    hid = hidden_items(R, sm['hidden_start'])
    const, unknown = code_calls(d, hi=CODE_BL_END)
    out = {}
    for f in range(LO, HI):
        if f in script: continue
        why = []
        if f in hid: why += hid[f]
        if hex(f) in sm['usate']: why += ['Smeraldo: ' + w for w in sm['usate'][hex(f)]]
        if f in const: why += ['codice ROM: ' + w for w in const[f]]
        out[hex(f)] = why
    sicure = [k for k, v in out.items() if not v]
    return dict(non_usate_dagli_script=len(out), sicure=sicure,
                escluse={k: v for k, v in out.items() if v},
                chiamate_non_calcolabili=sorted(set(unknown)), fonte_smeraldo=sm['fonte'])


def script_vars(R):
    """Variabili citate dagli script delle mappe: qualunque argomento 0x4000-0x40FF di qualunque comando (molti
    comandi accettano 'numero o variabile'), seguendo call/goto e gli script dopo le lotte."""
    import flagscan52, scr
    d = bytes(R.data); out = set()
    def walk(p, seen, depth=0):
        if p is None or p in seen or not (0 <= p < len(d)) or depth > 20: return
        seen.add(p)
        try: ins, _ = scr.decode(d, p, 600, follow=False)
        except Exception: return
        for a, nm, ar in ins:
            op = d[a]
            for x in ar:
                if isinstance(x, int) and 0x4000 <= x <= 0x40ff: out.add(x)
            if op in (4, 5, 6, 7) and ar and B <= ar[-1] < B + len(d): walk(ar[-1] - B, seen, depth + 1)
            if op == 0x5c:
                for x in ar[3:]:
                    if isinstance(x, int) and B <= x < B + len(d): walk(x - B, seen, depth + 1)
    for g, n in flagscan52.real_maps(d):
        try: m = R.map(g, n)
        except Exception: continue
        for lab, p in flagscan52.entries(R, m): walk(p, set())
    return out


def classify_vars(rom_path):
    import romlib
    R = romlib.Rom(str(rom_path)); d = bytes(R.data)
    sm = json.load(open(SMERALDO_JSON))['variabili']
    script = {int(k, 16) for k, v in json.load(open(ROOT / 'registri' / 'variabili.json')).items()
              if k.startswith('0x') and (v['mappe'] or v.get('nota'))} | script_vars(R)
    const, unknown = code_calls(d, hi=CODE_BL_END, targets={GETVARPTR: 'GetVarPointer', VARGET: 'VarGet', VARSET: 'VarSet'})
    out = {}
    for v in range(0x4000, 0x4100):
        if v in script: continue
        why = ['Smeraldo: ' + w for w in sm.get(hex(v), [])] + ['codice ROM: ' + w for w in const.get(v, [])]
        out[hex(v)] = why
    return dict(non_usate_dagli_script=len(out), sicure=[k for k, w in out.items() if not w],
                escluse={k: w for k, w in out.items() if w}, chiamate_non_calcolabili=len(set(unknown)))


def main():
    if sys.argv[1] == '--smeraldo':
        r = smeraldo(sys.argv[2]); json.dump(r, open(SMERALDO_JSON, 'w'), ensure_ascii=False, indent=1)
        print('flag di Smeraldo usate in 0x20-0x4FF: %d (%s)' % (len(r['usate']), r['fonte'])); return
    r = classify(sys.argv[1]); r['variabili'] = classify_vars(sys.argv[1])
    print('variabili non usate dagli script: %d, sicure: %d' % (r['variabili']['non_usate_dagli_script'], len(r['variabili']['sicure'])))
    print('non usate dagli script: %d, sicure: %d, escluse: %d, chiamate non calcolabili: %d' % (
        r['non_usate_dagli_script'], len(r['sicure']), len(r['escluse']), len(r['chiamate_non_calcolabili'])))
    if len(sys.argv) > 2: json.dump(r, open(sys.argv[2], 'w'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
