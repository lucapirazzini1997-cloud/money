"""0.48 - campagne piu' piene: erba alta, muri di alberi con varchi presidiati da allenatori, terreni per le bacche."""
import collections, hashlib, random
from gates48 import *
import gates48 as G
import kit48

BERRY_SCRIPT = 2573989          # script vanilla dell'albero di bacche (stessa degli oggetti 'gfx 60' dei vecchi percorsi)
BERRY_IDS = iter(list(range(90, 128)) + [57])
BERRIES = []                     # registro (mappa, x, y, id)


def _h(im): return hashlib.md5(im.tobytes()).hexdigest()


class Kinds:
    """Riconosce erba pulita / erba alta sul canvas live, sia con metatile General (over) sia con arte (art)."""
    def __init__(self, cv):
        self.cv = cv
        self.art_mode = sum(1 for y in range(cv.h) for x in range(cv.w) if cv.art[y][x]) > cv.w * cv.h * 0.5
        self.g_art = self.t_art = None
        if self.art_mode:
            cg = collections.Counter(); tall = collections.Counter(); samples = {}
            for y in range(cv.h):
                for x in range(cv.w):
                    a = cv.art[y][x]
                    if not a: continue
                    k = (_h(a[0]), _h(a[1]) if a[1] is not None else None, a[2], a[3])
                    samples[k] = a
                    if a[3] == 2: tall[k] += 1
                    elif a[2] == 0 and a[3] == 0: cg[k] += 1
            self.g_art = cg.most_common(1)[0][0]; self.g_sample = samples[self.g_art]
            self.t_art = tall.most_common(1)[0][0] if tall else None
            self.t_sample = samples.get(self.t_art) if self.t_art else None

    def key(self, x, y):
        a = self.cv.art[y][x]
        return None if not a else (_h(a[0]), _h(a[1]) if a[1] is not None else None, a[2], a[3])

    def grass(self, x, y):
        cv = self.cv
        if not (0 <= x < cv.w and 0 <= y < cv.h): return False
        if self.art_mode: return self.key(x, y) == self.g_art
        return isgrass(cv, x, y)

    def tall(self, x, y):
        cv = self.cv
        if not (0 <= x < cv.w and 0 <= y < cv.h): return False
        if self.art_mode: return self.t_art is not None and self.key(x, y) == self.t_art
        o = cv.over[y][x]
        return cv.art[y][x] is None and o is not None and o[0] == 13

    def set_tall(self, x, y):
        cv = self.cv
        if self.art_mode: cv.art[y][x] = self.t_sample
        else: cv.over[y][x] = (13, 0, 3)

    def set_grass(self, x, y):
        cv = self.cv
        if self.art_mode: cv.art[y][x] = self.g_sample
        else: to_grass(cv, x, y)


def events_taken(cv):
    t = {(o['x'], o['y']) for o in cv.objs} | {(b['x'], b['y']) for b in cv.bbgs} | {(w['x'], w['y']) for w in cv.bwarps} | {(c['x'], c['y']) for c in cv.bcoords}
    return t


def tall_rect(K, rect, density=1.0, seed=0, keep_clear=()):
    """Erba alta sulle celle d'erba pulita del rettangolo (x0,y0,x1,y1) (estremi inclusi)."""
    cv = K.cv; rnd = random.Random(seed); x0, y0, x1, y1 = rect; n = 0
    taken = events_taken(cv); keep = set(keep_clear)
    for y in range(max(0, y0), min(cv.h - 1, y1) + 1):
        for x in range(max(0, x0), min(cv.w - 1, x1) + 1):
            if (x, y) in taken or (x, y) in keep or not K.grass(x, y): continue
            if density >= 1 or rnd.random() < density:
                K.set_tall(x, y); n += 1
    return n


def clear_rect(K, rect):
    x0, y0, x1, y1 = rect
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            K.set_grass(x, y)


def tree_cell_blocked(cv, x, y): return cell_blocked(cv, x, y)


def plug(K, cells):
    """Tappa celle singole rimaste libere in un muro con un cespuglio (metatile siepe)."""
    cv = K.cv
    if K.art_mode: return
    for (x, y) in cells:
        if cv.art[y][x] is None: cv.over[y][x] = (14, 1, 3)


def eat_small_art(cv, cells, maxsize=6):
    """Toglie le decorazioni piccole (alberelli, cespugli: componenti d'arte <= maxsize celle) che toccano le celle date."""
    done = set()
    for (x, y) in cells:
        if not (0 <= x < cv.w and 0 <= y < cv.h) or cv.art[y][x] is None or (x, y) in done: continue
        comp = {(x, y)}; todo = [(x, y)]
        while todo and len(comp) <= maxsize + 1:
            a, b = todo.pop()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                p = (a + dx, b + dy)
                if 0 <= p[0] < cv.w and 0 <= p[1] < cv.h and p not in comp and cv.art[p[1]][p[0]] is not None:
                    comp.add(p); todo.append(p)
        if len(comp) <= maxsize:
            for (a, b) in comp:
                cv.art[b][a] = None; cv.over[b][a] = None
        done |= comp


def _clear_art(K, x, y):
    """In modalita' arte: libera le 4 celle (erba/erba alta) perche' cv.tree possa posare l'albero."""
    if not K.art_mode: return
    cv = K.cv
    for dy in (0, 1):
        for dx in (0, 1):
            if 0 <= x + dx < cv.w and 0 <= y + dy < cv.h and (K.grass(x + dx, y + dy) or K.tall(x + dx, y + dy)):
                cv.art[y + dy][x + dx] = None; cv.over[y + dy][x + dx] = None


def wall_h(K, y, x0, x1, gaps, force=False, maxsize=6):
    """Fila di alberi 2x2 (righe y,y+1) da x0 a x1 con varchi gaps=[(gx0,gx1)] (colonne). Ritorna la lista dei varchi."""
    cv = K.cv
    for x in range(x0 & ~1, x1 + 1, 2):
        if any(gx0 <= x and x + 1 <= gx1 for gx0, gx1 in gaps): continue
        eat_small_art(cv, [(x + a, y + b) for a in (0, 1) for b in (0, 1)], maxsize)
        # alberi anche sopra erba alta: pulisco prima
        for dy in (0, 1):
            for dx in (0, 1):
                if K.tall(x + dx, y + dy): K.set_grass(x + dx, y + dy)
        _clear_art(K, x, y)
        cv.tree(x, y)
    for gx0, gx1 in gaps:
        for xx in range(gx0, gx1 + 1):
            for yy in (y, y + 1):
                if K.tall(xx, yy): K.set_grass(xx, yy)
    leaks = [(x, yy) for x in range(max(0, x0), min(cv.w - 1, x1) + 1) for yy in (y, y + 1)
             if not any(g0 <= x <= g1 for g0, g1 in gaps) and not cell_blocked(cv, x, y) and not cell_blocked(cv, x, y + 1)]
    plug(K, leaks)
    leaks = [p for p in leaks if not cell_blocked(cv, *p)]
    assert not leaks, ('muro orizzontale con buchi', cv.gn, y, leaks[:6])


def wall_v(K, x, y0, y1, gaps, maxsize=6):
    cv = K.cv
    for y in range(y0 & ~1, y1 + 1, 2):
        if any(gy0 <= y and y + 1 <= gy1 for gy0, gy1 in gaps): continue
        eat_small_art(cv, [(x + a, y + b) for a in (0, 1) for b in (0, 1)], maxsize)
        for dy in (0, 1):
            for dx in (0, 1):
                if K.tall(x + dx, y + dy): K.set_grass(x + dx, y + dy)
        _clear_art(K, x, y)
        cv.tree(x, y)
    for gy0, gy1 in gaps:
        for yy in range(gy0, gy1 + 1):
            for xx in (x, x + 1):
                if K.tall(xx, yy): K.set_grass(xx, yy)
    leaks = [(xx, y_) for y_ in range(max(0, y0), min(cv.h - 1, y1) + 1) for xx in (x, x + 1)
             if not any(g0 <= y_ <= g1 for g0, g1 in gaps) and not cell_blocked(cv, x, y_) and not cell_blocked(cv, x + 1, y_)]
    plug(K, leaks)
    leaks = [p for p in leaks if not cell_blocked(cv, *p)]
    assert not leaks, ('muro verticale con buchi', cv.gn, x, leaks[:6])


def sight_cells(cv, t):
    """Celle viste da un allenatore (x,y,face,rng) fino al primo ostacolo."""
    x, y, face, rng = t
    dx, dy = {7: (0, -1), 8: (0, 1), 9: (-1, 0), 10: (1, 0)}[face]
    out = []
    for i in range(1, rng + 1):
        p = (x + dx * i, y + dy * i)
        if not (0 <= p[0] < cv.w and 0 <= p[1] < cv.h) or cell_blocked(cv, *p): break
        out.append(p)
    return out


def forced(cv, start, goal, trainers, extra_block=()):
    """True se, bloccando le celle viste dagli allenatori e gli allenatori stessi, goal non e' raggiungibile da start."""
    blocked = blocked_cells(cv) - {start, goal}
    blocked |= {(o['x'], o['y']) for o in cv.objs if o['gfx'] not in (59, 82, 86)}
    blocked |= set(extra_block)
    for t in trainers:
        blocked |= set(sight_cells(cv, t)) - {start}
    seen = {start}; todo = [start]
    while todo:
        x, y = todo.pop()
        if (x, y) == goal: return False
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            p = (x + dx, y + dy)
            if 0 <= p[0] < cv.w and 0 <= p[1] < cv.h and p not in seen and p not in blocked:
                seen.add(p); todo.append(p)
    return True


def connected(cv, a, b, extra_block=()):
    blocked = (blocked_cells(cv) | {(o['x'], o['y']) for o in cv.objs if o['gfx'] not in (59, 82, 86)} | set(extra_block)) - {a, b}
    seen = {a}; todo = [a]
    while todo:
        x, y = todo.pop()
        if (x, y) == b: return True
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            p = (x + dx, y + dy)
            if 0 <= p[0] < cv.w and 0 <= p[1] < cv.h and p not in seen and p not in blocked:
                seen.add(p); todo.append(p)
    return False


def berry_soil(cv, x, y):
    """Terreno morbido dove piantare le bacche (oggetto 'albero di bacche' vanilla, stadio vuoto)."""
    bid = next(BERRY_IDS)
    cv.add_obj(x, y, 60, BERRY_SCRIPT, flag=0, move=12, ttype=0, trange=bid)
    BERRIES.append((cv.gn, x, y, bid))
    return bid


def berry_patch(K, cells):
    """Aiuola di terreni per bacche su celle d'erba libere; ritorna quanti ne ha messi."""
    cv = K.cv; taken = events_taken(cv); n = 0
    for (x, y) in cells:
        if (x, y) in taken or not K.grass(x, y): continue
        # niente terreno di fronte a una porta o su un passaggio stretto: deve restare erba pulita attorno
        if not all(K.grass(x + a, y + b) or K.tall(x + a, y + b) for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1))): continue
        berry_soil(cv, x, y); n += 1
    return n


TR = {}      # registro allenatori per la relazione


def trainer_at(cv, x, y, face, rng, gfx, name, mons, intro, defeat, after, cls=5, pic=3):
    tid = kit48.sight_trainer(cv, x, y, gfx, name, mons, intro, defeat, after, rng=rng, face=face, cls=cls, pic=pic)
    TR.setdefault(cv.gn, []).append((name, x, y, face, rng, tid))
    return tid


CLUSTER_CAP = {(34, 84): 3}     # aiuole per mappa (id bacche limitati: 39 totali)
CLUSTER_USED = {}


def berry_scatter(K, rect, clusters, seed=0, size=2, avoid=()):
    """Mette 'clusters' aiuole di 'size' terreni in fila su erba pulita nel rettangolo."""
    cv = K.cv; rnd = random.Random(seed); x0, y0, x1, y1 = rect; done = 0; tries = 0
    taken = events_taken(cv)
    cap = CLUSTER_CAP.get(cv.gn, 2)
    while done < clusters and tries < 400 and CLUSTER_USED.get(cv.gn, 0) < cap:
        tries += 1
        x = rnd.randint(x0, x1 - size + 1); y = rnd.randint(y0, y1)
        cells = [(x + i, y) for i in range(size)]
        ring = {(a + dx, b + dy) for a, b in cells for dx in (-1, 0, 1) for dy in (-1, 0, 1)}
        if any(p in taken or p in avoid for p in ring): continue
        if not all(K.grass(a, b) or K.tall(a, b) for a, b in ring if 0 <= a < cv.w and 0 <= b < cv.h): continue
        if not all(0 <= a < cv.w and 0 <= b < cv.h for a, b in ring): continue
        for a, b in cells:
            if K.tall(a, b): K.set_grass(a, b)
            berry_soil(cv, a, b); taken.add((a, b))
        done += 1; CLUSTER_USED[cv.gn] = CLUSTER_USED.get(cv.gn, 0) + 1
    return done


def rock(cv, x, y):
    """Roccia rompibile (script vanilla). Flag permanente: una volta rotta non torna piu'."""
    f = kit48.POOL.flag('roccia %s %d,%d' % (cv.gn, x, y))
    cv.add_obj(x, y, 86, 2689899, flag=f, move=8)
    return f
