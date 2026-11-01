"""QA helpers for the 0.21+ binary ROM (RAM layout identical to the 0.12 build)."""
import sys, struct
sys.path.insert(0, '/home/claude/tools/qa')
import qa
from qa import Game, lib

S = qa.Sym('/home/claude/qa/syms.txt')
ROMSYM = dict(sSaveSlotLayout=0x8778d8c, gSpeciesNames=0x832ae94, gSpeciesInfo=0x8332c98,
              gExperienceTables=0x8331ff8, gBattleMoves=0x832f164)
S.S.update(ROMSYM)


def make_save(rom, gn, x, y, out, **kw):
    orig = qa.map_index
    qa.map_index = lambda dest: gn
    try:
        qa.make_save(rom, S, 'X', x, y, out, **kw)
    finally:
        qa.map_index = orig


def flag(n):
    a = lib.read32(S['gSaveBlock1Ptr'])
    return (lib.read8(a + 0x1270 + n // 8) >> (n % 8)) & 1


def var(n):
    a = lib.read32(S['gSaveBlock1Ptr'])
    return lib.read16(a + 0x139c + (n - 0x4000) * 2)


import romlib as _rl
from collections import deque as _dq


def walk(g, tx, ty, rompath='qa/t.gba', max_steps=200):
    """BFS-walk the player to (tx,ty) on the current map using collision from the ROM."""
    rom = _rl.Rom(rompath)
    for _ in range(max_steps):
        (gn, (x, y)) = g.pos()
        if (x, y) == (tx, ty): return True
        m = rom.map(*gn); a = rom.blocks(m)
        H, W = a.shape
        occ = {(o['x'], o['y']) for o in m['objects']}
        prev = {(x, y): None}; q = _dq([(x, y)])
        while q:
            c = q.popleft()
            if c == (tx, ty): break
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (c[0] + dx, c[1] + dy)
                if 0 <= n[0] < W and 0 <= n[1] < H and n not in prev and not (a[n[1], n[0]] & 0xc00) and (n not in occ or n == (tx, ty)):
                    prev[n] = c; q.append(n)
        if (tx, ty) not in prev: return False
        c = (tx, ty)
        while prev[c] != (x, y): c = prev[c]
        k = {(1, 0): 'right', (-1, 0): 'left', (0, 1): 'down', (0, -1): 'up'}[(c[0] - x, c[1] - y)]
        g.frames(2, k); g.frames(14, k); g.frames(8)
    return False


def face(g, d):
    g.frames(2, d); g.frames(10)


def yesno_open(g):
    for i in range(16):
        t = 0x03005e00 + i * 40
        if lib.read8(t + 4) and (lib.read32(t) & ~1) == 0x080e2378:
            return True
    return False


def answer(g, answers, max_presses=80):
    """Press A through dialogue; on each YES/NO menu pick the next answer (True=yes)."""
    answers = list(answers)
    for _ in range(max_presses):
        g.frames(10)
        if yesno_open(g):
            if not answers: return True
            a = answers.pop(0)
            if not a: g.tap('down', 3, 10)
            g.tap('a', 3, 40)
            continue
        if not answers: return True
        g.tap('a', 3, 20)
    return not answers
