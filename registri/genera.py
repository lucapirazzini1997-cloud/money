"""Genera i registri del progetto dalla ROM costruita e controlla le flag condivise.

File prodotti in registri/:
  flag.json        ogni flag usata: chi la imposta, chi la controlla, quali oggetti nasconde
  variabili.json   variabili 0x4000-0x40FF usate negli script (+ quelle note usate dal codice)
  strumenti.json   tabella strumenti: numero, nome, tasca; numeri liberi
  mappe.json       tutte le mappe: nome zona, dimensioni, uscite, connessioni, blocchi a coordinate
  spazio.json      zone di 0xFF libere (>= 4 KB) rimaste nella ROM

Controllo (strict=True): una flag usata come flag di oggetto o impostata da eventi di mappe diverse
e una "condivisione". Le condivisioni gia esistenti e verificate sono in flag_condivise_ammesse.json;
una condivisione nuova fa fallire la build (era la causa dei bug Arco/Regice e Katun/Registeel).
Uso diretto: python3 genera.py ROM.gba [--aggiorna-ammesse]
"""
import sys, json, re, struct, collections
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parent / 'strumenti_rom'), str(HERE.parent / 'versioni')]
import romlib, scr
from text_codec import CHAR

B = 0x08000000
ITEMS = 0x72f194
REGION_NAMES = 0x74c608
VAR_CODICE = {0x40fc: 'nome rivale (0x40fc-0x40ff)', 0x40fd: 'nome rivale', 0x40fe: 'nome rivale', 0x40ff: 'nome rivale'}


def name_at(d, p, n=14):
    o = ''
    for x in d[p:p + n]:
        if x == 0xff: break
        o += CHAR.get(x, '?')
    return o


def region_names(d):
    out = {}
    for i in range(213):
        p = struct.unpack_from('<I', d, REGION_NAMES + i * 8 + 4)[0]
        if B <= p < B + len(d): out[i] = name_at(d, p - B, 30)
    return out


def all_maps(R):
    """Mappe reali senza alias (flagscan52.real_maps)."""
    import flagscan52
    d = bytes(R.data); out = {}
    for g, n in flagscan52.real_maps(d):
        try:
            m = R.map(g, n)
            if 0 < m['width'] <= 300 and 0 < m['height'] <= 300: out[(g, n)] = m
        except Exception: pass
    return out


def walk(d, p, acc, seen, depth=0):
    if p is None or p in seen or not (0 <= p < len(d)) or depth > 12: return
    seen.add(p)
    try: ops, _ = scr.decode(d, p, 400)
    except Exception: return
    for a, n, ar in ops:
        if n in ('setflag', 'clearflag', 'checkflag') and ar: acc[n].add(ar[0])
        if n in ('setvar', 'addvar', 'subvar', 'copyvar', 'setorcopyvar', 'compare_var_to_value', 'compare_var_to_var'):
            for v in ar:
                if isinstance(v, int) and 0x4000 <= v <= 0x40ff: acc['var'].add(v)
        if n in ('call', 'goto', 'goto_if', 'call_if') and isinstance(ar[-1], int) and B <= ar[-1] < B + len(d):
            walk(d, ar[-1] - B, acc, seen, depth + 1)


def entries(R, m):
    d = bytes(R.data); out = []
    for o in m['objects']:
        if o['script']: out.append(('oggetto %d' % o['id'], o['script']))
    for c in m['coords']:
        if c['script']: out.append(('coord %d,%d' % (c['x'], c['y']), c['script']))
    for b in m['bgs']:
        if b['kind'] < 5 and B <= b['arg'] < B + len(d): out.append(('cartello %d,%d' % (b['x'], b['y']), b['arg'] - B))
    for k, p in R.map_scripts(m):
        if p is None: continue
        if k in (2, 4):
            q = p
            while struct.unpack_from('<H', d, q)[0]:
                t = struct.unpack_from('<I', d, q + 4)[0]
                if B <= t < B + len(d): out.append(('script mappa %d' % k, t - B))
                q += 8
        else: out.append(('script mappa %d' % k, p))
    return out


def main(rom, outdir, strict=False, aggiorna=False):
    R = romlib.Rom(str(rom)); d = bytes(R.data); outdir = Path(outdir)
    names = region_names(d); maps = all_maps(R)
    flags = collections.defaultdict(lambda: dict(imposta=set(), azzera=set(), controlla=set(), oggetto=set()))
    vars_ = collections.defaultdict(set); mappe = {}
    for k, m in sorted(maps.items()):
        key = '%d.%d' % k
        for o in m['objects']:
            if o['flag']: flags[o['flag']]['oggetto'].add('%s oggetto %d' % (key, o['id']))
        gates = []
        for lab, p in entries(R, m):
            acc = collections.defaultdict(set); walk(d, p, acc, set())
            for f in acc['setflag']: flags[f]['imposta'].add('%s %s' % (key, lab))
            for f in acc['clearflag']: flags[f]['azzera'].add('%s %s' % (key, lab))
            for f in acc['checkflag']: flags[f]['controlla'].add('%s %s' % (key, lab))
            for v in acc['var']: vars_[v].add(key)
            if lab.startswith('coord') and acc['checkflag']: gates.append(dict(dove=lab, flag=sorted(hex(f) for f in acc['checkflag'])))
        uniq = []
        for gt in gates:
            if gt['flag'] not in [u['flag'] for u in uniq]: uniq.append(gt)
        mappe[key] = dict(nome=names.get(m['region'], '?'), dimensioni=[m['width'], m['height']], tipo=m['type'],
                          uscite=[dict(da=[w['x'], w['y']], verso='%d.%d' % (w['group'], w['num'])) for w in m['warps']],
                          connessioni=['%d.%d' % (c['group'], c['num']) for c in m['conns']],
                          blocchi=uniq, oggetti=len(m['objects']), cartelli=len(m['bgs']))
    fj = {hex(f): {k: sorted(v) for k, v in rec.items() if v} for f, rec in sorted(flags.items())}
    json.dump(fj, open(outdir / 'flag.json', 'w'), ensure_ascii=False, indent=1)
    vj = {hex(v): dict(mappe=sorted(m), nota=VAR_CODICE.get(v, '')) for v, m in sorted(vars_.items())}
    for v, nota in VAR_CODICE.items(): vj.setdefault(hex(v), dict(mappe=[], nota=nota))
    vj['_libere_negli_script'] = [hex(v) for v in range(0x4000, 0x4100) if hex(v) not in vj]
    json.dump(vj, open(outdir / 'variabili.json', 'w'), ensure_ascii=False, indent=1)
    items = []; free = []
    for i in range(377):
        p = ITEMS + 44 * i; nm = name_at(d, p)
        items.append(dict(id=hex(i), nome=nm, tasca=d[p + 26], prezzo=struct.unpack_from('<H', d, p + 16)[0]))
        if set(nm) <= {'?'}: free.append(hex(i))
    json.dump(dict(strumenti=items, liberi=free), open(outdir / 'strumenti.json', 'w'), ensure_ascii=False, indent=1)
    json.dump(mappe, open(outdir / 'mappe.json', 'w'), ensure_ascii=False, indent=1)
    zones = [dict(da=hex(m.start()), a=hex(m.end()), kb=(m.end() - m.start()) // 1024) for m in re.finditer(rb'\xff{4096,}', d)]
    json.dump(zones, open(outdir / 'spazio.json', 'w'), indent=1)
    # condivisioni: flag di oggetto/impostate in piu' mappe
    shared = {}
    for f, rec in flags.items():
        owners = {s.split(' ')[0] for s in rec['oggetto'] | rec['imposta']}
        if len(owners) > 1: shared[hex(f)] = sorted(owners)
    amm_p = outdir / 'flag_condivise_ammesse.json'
    if aggiorna or not amm_p.exists():
        json.dump(shared, open(amm_p, 'w'), indent=1); print('  ammesse aggiornate:', len(shared))
    amm = json.load(open(amm_p))
    nuove = {f: o for f, o in shared.items() if f not in amm or set(o) - set(amm[f])}
    print('  mappe %d, flag %d, variabili %d, strumenti liberi %d, zone libere %d, condivisioni %d (nuove %d)'
          % (len(mappe), len(fj), len(vj) - 1, len(free), len(zones), len(shared), len(nuove)))
    if nuove:
        print('  CONDIVISIONI NUOVE:', json.dumps(nuove, indent=1))
        if strict: raise SystemExit('flag condivise nuove: controlla registri/flag.json')
    return dict(mappe=len(mappe), flag=len(fj), nuove=nuove)


if __name__ == '__main__':
    main(sys.argv[1], HERE, strict=False, aggiorna='--aggiorna-ammesse' in sys.argv)
