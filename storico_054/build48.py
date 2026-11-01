#!/usr/bin/env python3
"""Pokemon Romagna 0.48 - caselli ad ogni cambio di luogo, campagne piu' piene, terreni per le bacche.
Base: ROM 0.47 (rom047.gba). Uso: python3 build48.py [--out DIR]"""
import sys, hashlib, argparse
from caselli48 import *
import kit48
import caselli48 as CS
import maps48 as M48

OUTDIR = ROOT / 'out48'
BASE047_SHA = 'd26c0fd48f75fe1db4e36865f56b7ea9c9fd7914954d72e06ccfbaf45930122d'
REGION = {(0, 9): 0, (34, 93): 20, (34, 94): 11, (0, 16): 16, (0, 10): 1, (34, 14): 25, (34, 20): 19, (34, 17): 7, (34, 21): 23,
          (34, 22): 6, (34, 43): 24, (34, 44): 8, (34, 19): 7, (35, 60): 88, (35, 61): 89, (34, 39): 26, (34, 68): 9,
          (34, 84): 9, (34, 85): 4, (34, 96): 11, (35, 70): 90, (35, 71): 91}
HOUSES = []


def part_caselli(only=None):
    cvs, res = build_all(only=only)
    for (tid, mA, mB, sa, sb, text) in res:
        # la mappa piu' a est tiene la porta est della stanza interna
        if sa['side'] == 'E': east, west = (mB, sb), (mA, sa)
        elif sa['side'] == 'W': east, west = (mA, sa), (mB, sb)
        else: east, west = (mA, sa), (mB, sb)
        ik = add_map(template=(34, 23), region=REGION[mA], mtype=8)
        gE = install_end(cvs[east[0]], east[1], ik, 0)
        gW = install_end(cvs[west[0]], west[1], ik, 1)
        guard = Script('Casellante ' + tid).emit(b'\x6a\x5a').msg(text).end().save()
        room = gate_room(ik, (east[0][0], east[0][1], gE['slot']), (west[0][0], west[0][1], gW['slot']), guard, east[1]['name'], west[1]['name'])
        emit(room, 'casello_' + tid.lower())
        HOUSES.append((tid, east[0], gE, west[0], gW, ik))
        for (mk, info) in ((east[0], gE), (west[0], gW)):
            M48.HOUSEINFO[(mk, info['side'] + tid)] = dict(info, key=mk)
    return cvs


def part_country(cvs):
    kit48.init_pool()
    ts = M48.c21(cvs[(34, 21)])
    print('c21 collegata/forzata', M48.check21(cvs[(34, 21)], ts))
    ts = M48.c20(cvs[(34, 20)])
    print('c20', M48.check20(cvs[(34, 20)], ts))
    ts = M48.c43(cvs[(34, 43)])
    print('c43', M48.check43(cvs[(34, 43)], ts))
    ts = M48.c39(cvs[(34, 39)])
    print('c39', M48.check39(cvs[(34, 39)], ts))
    ts = M48.c84(cvs[(34, 84)])
    print('c84', M48.check84(cvs[(34, 84)], ts))
    ts = M48.c19(cvs[(34, 19)])
    ts = M48.c60(cvs[(35, 60)])
    print('c60', M48.check60(cvs[(35, 60)], ts))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', default=str(OUTDIR)); a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    assert hashlib.sha256(open(ROOT / 'rom047.gba', 'rb').read()).hexdigest() == BASE047_SHA, 'base non e 0.47'
    V.init()
    cvs = part_caselli()
    part_country(cvs)
    for k, cv in cvs.items():
        emit(cv, 'rev48_%d_%d' % k)
    data = bytes(W.d)
    (out / 'Pokemon_Romagna_0_48.gba').write_bytes(data)
    import json
    json.dump([dict(id=t, east=list(em), eastinfo=gE, west=list(wm), westinfo=gW, ik=list(ik)) for (t, em, gE, wm, gW, ik) in HOUSES], open(out / 'houses48.json', 'w'), indent=1)
    import country48 as _C
    import json as _j; _j.dump({'trainers':{str(k):v for k,v in _C.TR.items()},'berries':_C.BERRIES},open(str(a.out)+'/trainers48.json','w'))
    print('TRAINERS',{str(k):[t[0] for t in v] for k,v in _C.TR.items()}); print('BERRIES',len(_C.BERRIES),{str(k):sum(1 for b in _C.BERRIES if b[0]==k) for k in set(b[0] for b in _C.BERRIES)})
    print('sha', hashlib.sha256(data).hexdigest(), 'cursor', hex(W.cursor), W.ri)

if __name__ == '__main__': main()
