"""Confronto strutturato tra due ROM di Pokemon Romagna: mappe, allenatori, strumenti, codice.
Uso: python3 confronta.py vecchia.gba nuova.gba uscita.json"""
import sys, json, struct, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'strumenti_rom'))
import romlib, scr
from text_codec import CHAR
B = 0x08000000


def maps_of(R):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'versioni'))
    import flagscan52
    out = {}
    for g, n in flagscan52.real_maps(bytes(R.data)):
        try:
            m = R.map(g, n)
            if 0 < m['width'] <= 300 and 0 < m['height'] <= 300: out[(g, n)] = m
        except Exception: pass
    return out


def text(d, p, n=160):
    o = ''
    while 0 <= p < len(d) and d[p] != 0xff and len(o) < n:
        x = d[p]; o += ' / ' if x in (0xfe, 0xfb, 0xfa) else CHAR.get(x, '{%02x}' % x); p += 1
    return o


def script_summary(d, p):
    try: ops, _ = scr.decode(d, p, 40)
    except Exception: return {}
    flags = sorted({hex(ar[0]) for a, n, ar in ops if n in ('checkflag', 'setflag', 'clearflag') and ar})
    texts = [text(d, ar[1] - B) for a, n, ar in ops if n == 'loadword' and len(ar) > 1 and isinstance(ar[1], int) and B <= ar[1] < B + len(d)][:2]
    warps = [list(ar[:2]) + list(ar[3:5]) for a, n, ar in ops if n in ('warp', 'warpsilent', 'warpdoor')]
    return dict(flags=flags, testi=texts, warp=warps)


def describe(R, m, key):
    d = bytes(R.data)
    ev = dict(
        dim=[m['width'], m['height']], regione=m['region'],
        warp=[[w['x'], w['y'], w['group'], w['num'], w['warp']] for w in m['warps']],
        conn=[[c['dir'], c['group'], c['num'], c['offset']] for c in m['conns']],
        oggetti=[[o['x'], o['y'], o['gfx'], hex(o['flag'])] for o in m['objects']],
        coord=sorted({(c['x'], c['y']) for c in m['coords']}),
        cartelli=[[b['x'], b['y']] for b in m['bgs']],
        blocchi=bytes(d[m['blocks']:m['blocks'] + m['width'] * m['height'] * 2]).hex() if m['blocks'] else '',
        tileset=[hex(m['primary'] or 0), hex(m['secondary'] or 0)])
    return ev


def main():
    A = romlib.Rom(sys.argv[1]); Bm = romlib.Rom(sys.argv[2])
    ma, mb = maps_of(A), maps_of(Bm); db = bytes(Bm.data); da = bytes(A.data)
    rep = dict(mappe_nuove=[], mappe_cambiate=[], allenatori=[], strumenti=[], codice=[])
    for k in sorted(mb):
        b = describe(Bm, mb[k], k)
        if k not in ma:
            rep['mappe_nuove'].append(dict(mappa='%d.%d' % k, dim=b['dim'], warp=b['warp'], oggetti=len(b['oggetti']), coord=len(b['coord']))); continue
        a = describe(A, ma[k], k); ch = {}
        for f in ('dim', 'warp', 'conn', 'oggetti', 'coord', 'cartelli', 'tileset', 'regione'):
            if a[f] != b[f]: ch[f] = dict(prima=a[f], dopo=b[f]) if f not in ('coord',) else dict(prima=len(a[f]), dopo=len(b[f]))
        if a['blocchi'] != b['blocchi']:
            if len(a['blocchi']) == len(b['blocchi']):
                n = sum(1 for i in range(0, len(a['blocchi']), 4) if a['blocchi'][i:i + 4] != b['blocchi'][i:i + 4])
                ch['caselle_cambiate'] = n
            else: ch['caselle_cambiate'] = 'tutta la mappa'
        if ch:
            m = mb[k]; gates = []
            for c in {c['script'] for c in m['coords'] if c['script']}:
                s = script_summary(db, c)
                if s.get('flags') or s.get('testi'): gates.append(s)
            ch['script_blocchi'] = gates[:4]
            rep['mappe_cambiate'].append(dict(mappa='%d.%d' % k, **ch))
    # allenatori (tabella 0xf21000, 40 byte)
    for t in range(0, 900):
        p = 0xf21000 + t * 40
        if da[p:p + 40] != db[p:p + 40]:
            nm = ''.join(CHAR.get(x, '') for x in db[p + 4:p + 16] if x not in (0xff, 0))
            rep['allenatori'].append(dict(id=t, nome=nm))
    for i in range(0, 377):
        p = 0x72f194 + 44 * i
        if da[p:p + 44] != db[p:p + 44]:
            rep['strumenti'].append(dict(id=hex(i), nome=''.join(CHAR.get(x, '') for x in db[p:p + 14] if x != 0xff)))
    i = 0
    while i < 0x200000:
        if da[i] != db[i]:
            j = i
            while j < 0x200000 and (da[j] != db[j] or (j + 1 < 0x200000 and da[j + 1] != db[j + 1])): j += 1
            rep['codice'].append(dict(da=hex(i), a=hex(j), prima=da[i:j + 1].hex(), dopo=db[i:j + 1].hex())); i = j + 1
        else: i += 1
    json.dump(rep, open(sys.argv[3], 'w'), ensure_ascii=False, indent=1, default=list)
    print('mappe nuove', len(rep['mappe_nuove']), 'cambiate', len(rep['mappe_cambiate']), 'allenatori', len(rep['allenatori']), 'strumenti', len(rep['strumenti']), 'zone di codice', len(rep['codice']))


if __name__ == '__main__': main()
