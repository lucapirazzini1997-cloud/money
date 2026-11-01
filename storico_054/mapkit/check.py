"""Static checks for a composed map: walkability, reachability of doors, NPCs, signs and items."""
import sys
from pathlib import Path
from collections import deque
sys.path.insert(0, str(Path(__file__).parent))
import gfx

WATER = {0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x19, 0x1A, 0x2A}
_gp = None


def behavior(key):
    global _gp
    if isinstance(key, int):
        if _gp is None:
            _gp = gfx.Pair('gTileset_General', 'gTileset_Petalburg')
        return _gp.attr(key) & 0xFF
    return key.behavior


def walkable_grid(cv, grid, surf=False):
    W, H = cv.w, cv.h
    ok = [[False] * W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            key, bits = grid[y][x]
            coll = (bits >> 10) & 3
            beh = behavior(key)
            if coll:
                continue
            if beh in WATER and not surf:
                continue
            ok[y][x] = True
    for o in cv.npcs:
        if 0 <= o['x'] < W and 0 <= o['y'] < H:
            ok[o['y']][o['x']] = False
    return ok


def reach(cv, grid, starts, surf=False):
    ok = walkable_grid(cv, grid, surf)
    seen = set()
    q = deque()
    for s in starts:
        if ok[s[1]][s[0]]:
            q.append(s); seen.add(s)
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < cv.w and 0 <= ny < cv.h and (nx, ny) not in seen and ok[ny][nx]:
                seen.add((nx, ny)); q.append((nx, ny))
    return seen, ok


def check(cv, grid, starts, surf=False, verbose=True):
    seen, ok = reach(cv, grid, starts, surf)
    problems = []
    def near(x, y):
        return any((x + dx, y + dy) in seen for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
    for i, o in enumerate(cv.npcs):
        x, y = o['x'], o['y']
        key, bits = grid[y][x]
        if (bits >> 10) & 3 and 'ITEM' not in o['graphics_id']:
            problems.append(('npc on blocked cell', i, o['script'], x, y))
        if not near(x, y):
            problems.append(('npc unreachable', i, o['script'], x, y))
    for i, w in enumerate(cv.warps):
        x, y = w['x'], w['y']
        if (x, y) not in seen and not near(x, y):
            problems.append(('warp unreachable', i, w['dest_map'], x, y))
    for s in cv.signs:
        if not near(s['x'], s['y']) and (s['x'], s['y']) not in seen:
            problems.append(('sign unreachable', s.get('script', s.get('item')), s['x'], s['y']))
    for t in cv.triggers:
        if (t['x'], t['y']) not in seen:
            problems.append(('trigger unreachable', t['script'], t['x'], t['y']))
    if verbose:
        for p in problems:
            print('  !', *p)
        print('  reachable cells:', len(seen))
    return problems, seen
