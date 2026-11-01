"""Static audit: reachable maps from Lido, warp targets, reciprocity, landing cells, connections."""
import romlib, collections, json, sys
r = romlib.Rom('out/Pokemon_Romagna_0_22.gba')
def M(g, n):
    try: return r.map(g, n)
    except Exception: return None
start = (0, 9)
seen = {start}; q = collections.deque([start]); edges = []
while q:
    gn = q.popleft(); m = M(*gn)
    if m is None: continue
    nb = [((w['group'], w['num']), 'warp') for w in m['warps']] + [((c['group'], c['num']), 'conn') for c in m['conns'] if c['dir'] in (1, 2, 3, 4)]
    for t, k in nb:
        if t == (127, 127): continue
        if t not in seen:
            seen.add(t); q.append(t)
print('reachable maps (warps+connections from Lido):', len(seen))
issues = []
WALKBEH_WARP = {0x60, 0x61, 0x62, 0x63, 0x64, 0x65, 0x69, 0x6a, 0x6b, 0x6c, 0x6d, 0x6e, 0x6f, 0x8d, 0x67, 0x68}
for gn in sorted(seen):
    m = M(*gn)
    if m is None: issues.append(('missing map', gn)); continue
    a = r.blocks(m)
    for i, w in enumerate(m['warps']):
        t = (w['group'], w['num'])
        if t == (127, 127): continue
        tm = M(*t)
        if tm is None: issues.append(('warp to missing map', gn, i, (w['x'], w['y']), t)); continue
        if w['warp'] >= len(tm['warps']):
            issues.append(('warp to missing warp index', gn, i, (w['x'], w['y']), t, w['warp'])); continue
        tw = tm['warps'][w['warp']]
        ta = r.blocks(tm)
        if not (0 <= tw['x'] < tm['width'] and 0 <= tw['y'] < tm['height']):
            issues.append(('landing outside map', gn, i, t, (tw['x'], tw['y']))); continue
        v = int(ta[tw['y'], tw['x']]); beh = r.attr(tm, v & 1023) & 0xff
        # back-link: some warp of target leads back to this map
        if not any((x['group'], x['num']) == gn for x in tm['warps']) and not any((c['group'], c['num']) == gn for c in tm['conns']):
            issues.append(('no way back', gn, i, (w['x'], w['y']), t))
        if (v >> 10) & 3 and beh not in WALKBEH_WARP:
            issues.append(('landing on solid cell', gn, i, t, (tw['x'], tw['y']), hex(beh)))
    for c in m['conns']:
        t = (c['group'], c['num']); tm = M(*t)
        if tm is None: issues.append(('conn to missing', gn, t)); continue
        opp = {1: 2, 2: 1, 3: 4, 4: 3, 5: 6, 6: 5}[c['dir']]
        if not any((x['group'], x['num']) == gn and x['dir'] == opp and x['offset'] == -c['offset'] for x in tm['conns']):
            issues.append(('connection not reciprocal', gn, c, t, tm['conns']))
for i in issues: print(i)
json.dump(sorted(seen), open('qa/reachable.json', 'w'))
