"""Scansione di tutte le flag usate dagli eventi delle mappe (oggetti, script, coord, bg, script di mappa).
Serve al builder 0.52: il pool non deve mai dare una flag gia' usata, e alla fine non devono esserci flag condivise
fra eventi diversi (salvo un elenco di condivisioni volute)."""
import struct, collections
import romlib, scr

B = 0x08000000
GROUPS = romlib.GROUPS


def group_counts(d):
    bases = [struct.unpack_from('<I', d, GROUPS + g * 4)[0] - B for g in range(36)]
    out = {}
    for g in range(36):
        n = 0
        while True:
            p = bases[g] + n * 4
            if n > 0 and p in bases: break
            h = struct.unpack_from('<I', d, p)[0]
            if not (B <= h < B + len(d)): break
            h -= B
            if not all(B <= struct.unpack_from('<I', d, h + i)[0] < B + len(d) for i in (0, 4)): break
            if d[h + 20] >= 0xd5: break
            n += 1
        out[g] = n
    return out


def _walk(d, p, acc, seen):
    if p is None or p in seen or not (0 <= p < len(d)): return
    seen.add(p)
    try: ins, _ = scr.decode(d, p, 600)
    except Exception: return
    for a, nm, ar in ins:
        op = d[a]
        if op in (0x04, 0x05, 0x06, 0x07) and ar and B <= ar[-1] < B + len(d): _walk(d, ar[-1] - B, acc, seen)
        if op == 0x5c and ar[0] in (1, 2, 6, 8) and B <= ar[-1] < B + len(d): _walk(d, ar[-1] - B, acc, seen)
        if op == 0x29: acc['set'].add(ar[0])
        if op == 0x2a: acc['clear'].add(ar[0])
        if op == 0x2b: acc['check'].add(ar[0])
        if op == 0x5c: acc['trainer'].add(0x500 + ar[1])


def entries(R, m):
    d = R.data; out = []
    for o in m['objects']:
        if o['script']: out.append(('obj%d' % o['id'], o['script']))
    for c in m['coords']:
        if c['script']: out.append(('coord', c['script']))
    for b in m['bgs']:
        if b['kind'] < 5 and B <= b['arg'] < B + len(d): out.append(('bg', b['arg'] - B))
    for k, p in R.map_scripts(m):
        if p is None: continue
        if k in (2, 4):
            q = p
            while struct.unpack_from('<H', d, q)[0]:
                t = struct.unpack_from('<I', d, q + 4)[0]
                if B <= t < B + len(d): out.append(('ms%d' % k, t - B))
                q += 8
        else: out.append(('ms%d' % k, p))
    return out


def scan(data):
    """-> (flags usate in qualunque modo, dettaglio: flag -> set di 'proprietari' (mappa, entry) che la settano o la usano come flag oggetto)"""
    d = bytes(data); R = romlib.Rom(d)
    used = set(); owners = collections.defaultdict(set)
    for g, c in group_counts(d).items():
        for n in range(c):
            try: m = R.map(g, n)
            except Exception: continue
            for o in m['objects']:
                if o['flag']:
                    used.add(o['flag']); owners[o['flag']].add(('obj', g, n, o['id'], o['script']))
            for lab, p in entries(R, m):
                acc = dict(set=set(), clear=set(), check=set(), trainer=set())
                _walk(d, p, acc, set())
                for f in acc['set'] | acc['clear'] | acc['check']:
                    used.add(f)
                for f in acc['set']:
                    owners[f].add(('set', g, n, lab, p))
    return used, owners
