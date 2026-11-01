"""Costruzione dei caselli: specifiche automatiche + override per estremita'."""
from gates48 import *
import gates48 as G
from lanes48 import LANES
from plan48 import TXT

OVR = {}      # (id,'A'|'B') -> dict di override (moves, clear, ch, cw, x0, y0, ...)
PRE = {}      # (id,'A'|'B') -> funzione(cv) di pre-lavoro (rimozione oggetti, ecc.)
PRE0 = {}     # come PRE ma prima del calcolo delle geometrie
LANE_OVR = {} # (id,'A'|'B') -> corsia sostitutiva
GUARD_FLAG = {}


def autospec(cv, side, lane, name):
    xs = [p[0] for p in lane]; ys = [p[1] for p in lane]
    ch, cw = 4, 4
    if side in ('N', 'S'):
        lo, hi = min(xs), max(xs)
        cw = 4 if hi - lo < 4 else (6 if hi - lo < 6 else 8)
        x0 = lo & ~1
        if x0 + cw - 1 < hi: x0 += 2
        x0 = max(0, min(x0, cv.w - cw))
        # porta in una colonna della corsia, preferibilmente al centro del casello
        dc = 1 if cw == 4 else cw // 2 - 1
        while x0 + dc not in xs and dc < cw - 1: dc += 1
        if x0 + dc not in xs:
            dc = max(0, lo - x0)
        sp = dict(side=side, x0=x0, cw=cw, ch=3 if side == 'N' and False else ch, door_col=dc, name=name, lane=lane)
        if side == 'S':
            y0 = cv.h - 2 - ch
            sp['y0'] = y0
            sp['ring'] = (max(0, x0 - 2), y0 - 2, x0 - 1, cv.h - 1)
        return sp
    lo, hi = min(ys), max(ys)
    y0 = max(0, (hi - ch + 1) & ~1)
    while y0 + ch - 1 < hi: ch += 1
    while y0 > lo and ch < 6: y0 -= 2; ch += 2
    # resti del vecchio varco (comignoli) sopra e sotto la casa
    if side == 'W': cl = [(0, y0 - 2, 1, y0 - 1), (0, y0 + ch, 1, y0 + ch + 1)]
    else: cl = [(cv.w - 2, y0 - 2, cv.w - 1, y0 - 1), (cv.w - 2, y0 + ch, cv.w - 1, y0 + ch + 1)]
    return dict(side=side, y0=y0, ch=ch, name=name, lane=lane, clear=cl)


def build_all(maps=None, only=None, dry=False, log=print):
    """Costruisce tutti i caselli. Ritorna dict map->canvas e lista delle case. dry: nessuna emissione, solo conteggio eventi."""
    cvs = {}
    def cvf(k):
        if k not in cvs: cvs[k] = V.live_canvas(k)
        return cvs[k]
    res = []
    for (tid, mA, sA, lA, mB, sB, lB) in LANES:
        if only and tid not in only: continue
        nA, nB, text = TXT[tid]
        cA, cB = cvf(mA), cvf(mB)
        for k, c in (((tid, 'A'), cA), ((tid, 'B'), cB)):
            if k in PRE0: PRE0[k](c)          # lavori che spostano il canvas (prima di calcolare le geometrie)
        lA = LANE_OVR.get((tid, 'A'), lA); lB = LANE_OVR.get((tid, 'B'), lB)
        specA = autospec(cA, sA, lA, nA); specA.update(OVR.get((tid, 'A'), {}))
        specB = autospec(cB, sB, lB, nB); specB.update(OVR.get((tid, 'B'), {}))
        for k, c in (((tid, 'A'), cA), ((tid, 'B'), cB)):
            if k in PRE: PRE[k](c)
        res.append((tid, mA, mB, specA, specB, text))
    return cvs, res


def scan(cvs, res, log=print):
    """Elenca gli eventi che cadono nelle aree toccate (senza modificare nulla)."""
    for (tid, mA, mB, sa, sb, text) in res:
        for (m, sp) in ((mA, sa), (mB, sb)):
            cv = cvs[m]
            side = sp['side']; cw, ch = sp.get('cw', 4), sp.get('ch', 4)
            if side == 'N': x0, y0 = sp['x0'], 0; dc = sp.get('door_col', 1); appr = (x0 + dc, ch)
            elif side == 'S': x0 = sp['x0']; y0 = sp.get('y0', cv.h - 2 - ch); dc = sp.get('door_col', 1); appr = (x0 + dc, y0 + ch)
            elif side == 'E': x0, y0 = cv.w - cw, sp['y0']; appr = (x0 - 1, y0 + ch - 1)
            else: x0, y0 = 0, sp['y0']; appr = (cw, y0 + ch - 1)
            foot = {(x, y) for x in range(x0, x0 + cw) for y in range(y0, y0 + ch)}
            clear = set()
            for r in sp.get('clear', ()): clear |= rect_cells(r)
            ring = rect_cells(sp['ring']) if sp.get('ring') else set()
            o, b = touched_events(cv, (foot | clear | ring | {appr}) - set(sp.get('keep_events', ())))
            log(tid, m, side, 'x0=%s y0=%s cw=%s ch=%s' % (x0, y0, cw, ch), 'OBJ', o, 'BG', b)

D = lambda **k: k
# 'near' = sposta in una cella d'erba libera vicina (e ridisegna il cartello); None = toglie (cartello di direzione, ora inutile)
OVR.update({
 ('T1', 'A'): D(reach_min=5, ch=2, cw=6, moves={'bg': {5: (16, 2)}}, sign_art=[(16, 2)]),
 ('T2', 'B'): D(moves={'bg': {2: None}}),
 ('T3', 'A'): D(clear=[(22, 38, 23, 43)]),
 ('T4', 'A'): D(moves={'obj': {7: 'near'}}),
 ('T5', 'A'): D(moves={'bg': {0: 'near'}}),
 ('T7', 'A'): D(clear=[(17, 48, 22, 50), (22, 46, 23, 47)], moves={'bg': {19: None}}),
 ('T7', 'B'): D(clear=[(4, 0, 5, 1)], x0=0, door_col=2, moves={'obj': {1: (2, 5), 2: (3, 5), 4: 'near'}}),
 ('T8', 'B'): D(moves={'bg': {59: None}}),
 ('T11', 'A'): D(moves={'bg': {3: 'near', 20: None}, 'obj': {4: 'near'}}),
 ('T12', 'A'): D(moves={'bg': {1: 'near'}}),
 ('T12', 'B'): D(moves={'bg': {7: None}}),
 ('T13', 'B'): D(ring=(16, 28, 17, 33)),
 ('T13', 'A'): D(moves={'bg': {58: None}}),
 ('T15', 'A'): D(moves={'bg': {2: None}}),
 ('T15', 'B'): D(moves={'bg': {0: None}}),
 ('T16', 'A'): D(moves={'bg': {4: None}}),
 ('T17', 'B'): D(moves={'bg': {43: None}}),
 ('T18', 'A'): D(moves={'bg': {44: None}}),
 ('T18', 'B'): D(moves={'bg': {0: None}}),   # cartello scuola di canoa: da rimettere nella fase campagna
 ('T19', 'B'): D(moves={'bg': {39: None}}),
 ('T20', 'A'): D(keep_events=[(4, 35)], moves={'obj': {11: (4, 35)}}),
 ('T20', 'B'): D(moves={'bg': {0: None}}),
 ('T21', 'B'): D(moves={'bg': {0: None}}),
})


import maps48 as _M48
PRE0[('T18', 'B')] = _M48.extend84
PRE0[('T19', 'A')] = _M48.extend84
LANE_OVR[('T18', 'B')] = [(55, y + _M48.DY84) for y in range(23, 27)]
LANE_OVR[('T19', 'A')] = [(0, 9)]
