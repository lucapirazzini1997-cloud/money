"""Parco della Rocca (34,33) — the 'Mega parco' inside the Rocca walls: a hedge maze with a shiny Torkoal at the end."""
import sys, random
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import art, art22, decor, r22, imports
from canvas import G
from decor import rect
from _town import tree, lamp, bench

GN = (34, 33)
TS = 'r22_maze'
W, H = 33, 33
STARTS = [(16, 32)]


def maze_cells(n, seed):
    rnd = random.Random(seed)
    seen = {(0, 0)}; stack = [(0, 0)]; links = set()
    while stack:
        c = stack[-1]
        nb = [(c[0] + dx, c[1] + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
              if 0 <= c[0] + dx < n and 0 <= c[1] + dy < n and (c[0] + dx, c[1] + dy) not in seen]
        if not nb:
            stack.pop(); continue
        nx = rnd.choice(nb); seen.add(nx); links.add(frozenset((c, nx))); stack.append(nx)
    # a few extra loops make it a park rather than a pure labyrinth
    for _ in range(n):
        a = (rnd.randrange(n - 1), rnd.randrange(n))
        links.add(frozenset((a, (a[0] + 1, a[1]))))
    return links


def build():
    cv = r22.RCanvas(W, H, GN)
    cv.conns = []
    n = 15                                  # 15x15 cells -> corridors at odd coordinates 1..29 (+1 offset)
    links = maze_cells(n, 7)
    open_ = set()
    for i in range(n):
        for j in range(n):
            open_.add((1 + 2 * i, 1 + 2 * j))
    for l in links:
        a, b = tuple(l)
        open_.add((1 + a[0] + b[0], 1 + a[1] + b[1]))
    # shift by one so the outer ring is hedge too; map is 33x33: cells at 2..30
    open_ = {(x + 1, y + 1) for (x, y) in open_}
    for (x, y) in rect(14, 31, 5, 2):
        open_.add((x, y))
    # garden at the top centre (goal) and the entrance plaza
    goal = rect(13, 1, 7, 5)
    plaza = rect(13, 28, 7, 5)
    open_ |= goal | plaza
    walls = {(x, y) for x in range(W) for y in range(H)} - open_
    for (x, y) in open_:
        cv.path(x, y, 1, 1)
    cv.hedge(walls)
    # goal garden: flowers, a fountain, benches; Torkoal sits by the fountain
    cv.place_art(16, 2, dict(img=decor.asset('fountain', art.fountain), solid=rect(0, 0, 2, 2), door=None))
    for (x, y) in ((13, 1), (19, 1), (13, 5), (19, 5)):
        cv.put(x, y, G['flowers'])
    # dead ends get flowers or a bench
    rnd = random.Random(3)
    for (x, y) in sorted(open_ - goal - plaza):
        nb = sum((x + dx, y + dy) in open_ for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        if nb == 1 and rnd.random() < 0.6:
            cv.put(x, y, G['flowers'])
    # entrance plaza
    for (x, y) in ((14, 29), (18, 29)):
        lamp(cv, x, y)
    cv.objs = cv.objs[:1]
    cv.place_objs({1: (15, 29)})
    cv.add_obj(17, 4, 235, 'R22_Torkoal', flag=0x4DB, move=8)     # gfx id patched by the build
    cv.bwarps = [dict(x=16, y=32, elev=0, warp=1, num=32, group=34)]
    cv.add_sign(17, 30, 'R22_SignMaze')
    cv.put(17, 30, G['sign'], 1, 3)
    cv.border = [0x1D4, 0x1D5, 0x1DC, 0x1DD]
    return cv
