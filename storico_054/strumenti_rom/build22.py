"""Pokémon Romagna 0.22 — binary revision on top of the 0.21 ROM.

Usage: python3 build22.py [--only fixes]  -> out/Pokemon_Romagna_0_22.gba
"""
import sys, struct, json, hashlib
from pathlib import Path
sys.path.insert(0, '/home/claude/r22')
sys.path.insert(0, '/home/claude/tools/mapkit')
import inject, romlib, asm, native, scripts22
from text_codec import CHAR

B = 0x08000000
OUT = Path('/home/claude/r22/out'); OUT.mkdir(exist_ok=True)
ALPHA = {v: k for k, v in CHAR.items() if len(v) == 1}


def P(p): return struct.pack('<I', B + p)


def enc(s, n=None):
    raw = bytes(ALPHA[c] for c in s) + b'\xff'
    if n: raw = raw.ljust(n, b'\x00')
    return raw


class Build:
    def __init__(self):
        self.W = inject.Writer()
        self.d = self.W.d
        self.L = {}
        self.maps_added = {}
        self.manifest = dict(changes=[])

    def note(self, **kw):
        self.manifest['changes'].append(kw)

    # ---------------------------------------------------------------- code + scripts
    def assemble(self, extra_src=''):
        W = self.W
        W.cursor = (W.cursor + 3) & ~3
        code, lab = asm.assemble(native.SRC, W.cursor, thumb=True)
        base = W.alloc(code, 'native')
        nat = {k: v for k, v in lab.items() if k.startswith('R22_')}
        ext = {k: B + v + 1 for k, v in nat.items()}
        ext['R22_PROF_ORIG_ADDR'] = B + self.W.rom.map(1, 4)['objects'][0]['script']
        src = scripts22.HEAD + scripts22.SRC + scripts22.aie_trainer_scripts() + extra_src
        labels = W.scripts(src, ext)
        self.L.update(labels)
        self.L.update({k: v for k, v in nat.items()})
        return labels

    # ---------------------------------------------------------------- data helpers
    def trainer(self, tid, name, cls, pic, mons, music=0, items=(), female=False):
        raw = bytearray(40)
        raw[0] = 2; raw[1] = cls; raw[2] = music | (0x80 if female else 0); raw[3] = pic
        raw[4:16] = enc(name, 12)
        for i, it in enumerate(items): struct.pack_into('<H', raw, 16 + i * 2, it)
        struct.pack_into('<I', raw, 28, 7); raw[32] = len(mons)
        party = b''.join(struct.pack('<HBxHH', iv, lvl, sp, held) for sp, lvl, held, iv in mons)
        pp = self.W.alloc(party, 'party ' + name)
        struct.pack_into('<I', raw, 36, B + pp)
        p = 0xf21000 + tid * 40
        self.d[p:p + 40] = raw

    def rename_item(self, item_name_off, new):
        self.d[item_name_off:item_name_off + 14] = enc(new, 14)

    def patch_goto(self, at, target):
        self.d[at:at + 5] = b'\x05' + P(target)

    def set_obj_script(self, g, n, idx, script):
        m = self.W.rom.map(g, n)
        p = romlib.u32(self.d, m['events'] + 4) - B + (idx - 1) * 24 + 16
        struct.pack_into('<I', self.d, p, B + script)

    # ---------------------------------------------------------------- new maps in group 35
    def add_map(self, header_src=(35, 12), name='new'):
        """Clone a header into a new slot of group 35. Returns (group, num)."""
        G = romlib.GROUPS
        gp = romlib.u32(self.d, G + 35 * 4) - B
        count = romlib.COUNTS[35]
        entries = list(struct.unpack_from('<%dI' % count, self.d, gp))
        src = self.W.rom.header(*header_src)
        hp = self.W.alloc(bytes(self.d[src:src + 28]), 'header ' + name)
        entries.append(B + hp)
        ng = self.W.alloc(struct.pack('<%dI' % len(entries), *entries) + b'\xff' * 4, 'group35 table')
        struct.pack_into('<I', self.d, G + 35 * 4, B + ng)
        romlib.COUNTS[35] = len(entries)
        # new layout id
        lid = self.new_layout_slot()
        struct.pack_into('<H', self.d, hp + 18, lid)
        return (35, len(entries) - 1)

    def new_layout_slot(self):
        W = self.W
        tbl = W.table
        # count entries: until first zero/non-pointer
        n = 0
        while True:
            v = romlib.u32(self.d, tbl + n * 4)
            if not (B <= v < B + 0x2000000): break
            n += 1
        entries = list(struct.unpack_from('<%dI' % n, self.d, tbl))
        entries.append(entries[0])
        nt = W.alloc(struct.pack('<%dI' % len(entries), *entries) + b'\x00' * 4, 'layout table')
        for ref in inject.LAYOUT_TABLE_REFS:
            struct.pack_into('<I', self.d, ref, B + nt)
        W.table = nt
        return len(entries)

    def save(self):
        out = OUT / 'Pokemon_Romagna_0_22.gba'
        sha = self.W.save(out)
        self.manifest.update(sha256=sha, allocation_end=self.W.cursor, labels={k: hex(v) for k, v in self.L.items() if not k.endswith(('_I', '_D', '_P'))})
        (OUT / 'revision_0_22.json').write_text(json.dumps(self.manifest, indent=1, ensure_ascii=False))
        return out, sha


def ow_pokemon(b, gfx_id, species, tag, shiny=True):
    """Overworld sprite (32x32) for a Pokémon from its battle front pic, like the 0.21 birds."""
    import numpy as np
    rom = b.W.rom; d = b.d
    template = rom.ptr(0x6ada3c + 206 * 4)
    pic = rom.lz(rom.ptr(0x3139dc + species * 8))[:2048]
    packed = np.frombuffer(pic, dtype=np.uint8)
    tiles = np.empty(4096, dtype=np.uint8); tiles[::2] = packed & 15; tiles[1::2] = packed >> 4
    grid = tiles.reshape(8, 8, 8, 8).transpose(0, 2, 1, 3).reshape(64, 64)
    small = grid[::2, ::2]
    def enc_tile(a):
        a = np.asarray(a, dtype=np.uint8).ravel(); return bytes(a[::2] | (a[1::2] << 4))
    data = b''.join(enc_tile(small[y:y + 8, x:x + 8]) for y in range(0, 32, 8) for x in range(0, 32, 8))
    image = b.W.alloc(data, 'ow image %d' % species)
    frames = b.W.alloc((P(image) + struct.pack('<HH', 512, 0)) * 8, 'ow frames %d' % species)
    palp = rom.ptr((0x3169fc if shiny else 0x315c3c) + species * 8)
    pal = b.W.alloc(rom.lz(palp), 'ow palette %d' % species)
    info = bytearray(d[template:template + 36]); struct.pack_into('<H', info, 2, tag); struct.pack_into('<I', info, 28, B + frames)
    infop = b.W.alloc(bytes(info), 'ow info %d' % species)
    struct.pack_into('<I', d, 0x6ada3c + gfx_id * 4, B + infop)
    # extend the object palette table (pointer used in three places)
    cur = rom.ptr(0x8ea24); entries = []
    q = cur
    while True:
        ptr, t = struct.unpack_from('<IH', d, q)
        if t == 0x11ff and ptr == 0: break
        entries.append(bytes(d[q:q + 8])); q += 8
    entries.append(P(pal) + struct.pack('<HH', tag, 0))
    entries.append(struct.pack('<IHH', 0, 0x11ff, 0))
    newt = b.W.alloc(b''.join(entries), 'object palettes')
    for ref in (0x8ea24, 0x8eab8, 0x8eb10):
        struct.pack_into('<I', d, ref, B + newt)


def fixes(b):
    # 0.21 engine: hard-coded sea/shore metatiles beyond the east edges of Lido, Cervia, Cesenatico and the
    # Rimini port pointed at secondary metatiles of the old tilesets (striped garbage): use the General water
    WATER = 0x170 | 0xC00
    for a, old in ((0x87ea0, 0xe04), (0x87eb8, 0xe02), (0x87ec4, 0xdd5), (0x87edc, 0xe01)):
        assert struct.unpack_from('<I', b.d, a)[0] == old
        struct.pack_into('<I', b.d, a, WATER)
    assert bytes(b.d[0x87ee4:0x87ee8]) == bytes.fromhex('e1200001')
    struct.pack_into('<H', b.d, 0x87ee4, 0x20d7)          # mov r0,#0xd7 ; lsl r0,#4 -> 0xd70
    # flamingo overworld sprite (gfx 239): 9 frames redrawn, same palette and size
    sys.path.insert(0, '/home/claude/tools/mapkit/sprites')
    import flamingo
    for k, fr in enumerate(flamingo.frames()):
        b.W.d[0x6ac634 + k * 512:0x6ac634 + (k + 1) * 512] = flamingo.encode(fr)
    L = b.L
    d = b.d
    # 1. Fly: replace the 0.21 resume guard with a progress-based one
    b.patch_goto(0x1721ba8, L['R22_FlyGuard'])
    b.note(kind='fly_guard', detail='visited flags follow badges; Hoenn leftovers removed from the fly map')
    # 2. cheater room: warning first (both copies of the room)
    for (g, n) in ((34, 83), (33, 84)):
        m = b.W.rom.map(g, n)
        for i, o in enumerate(m['objects']):
            if o['script'] == 0x2d8126:
                b.set_obj_script(g, n, i + 1, L['R22_Cheater'])
    b.note(kind='cheater_warning')
    # 3. Mach Bike becomes the racing bike
    b.rename_item(0x731e18, 'BICI DA CORSA')
    # 3b. GS BALL (replaces the unused MYSTICTICKET), with the Ultra Ball icon
    it = 0x72f194 + 370 * 44
    b.d[it:it + 14] = enc('GS BALL', 14)
    desc = b.W.alloc(enc('Una sfera dorata\ne argentata. Vibra\nvicino ai boschi.'.replace('\\n', '\n')), 'gs ball desc') if False else None
    txt = bytes(ALPHA[c] if c != '\n' else 0xfe for c in 'Una strana sfera\ndorata. Vibra vicino\nal santuario.') + b'\xff'
    dp = b.W.alloc(txt, 'gs ball description')
    struct.pack_into('<I', b.d, it + 20, B + dp)
    struct.pack_into('<8s', b.d, 0x7bf5a4 + 370 * 8, bytes(b.d[0x7bf5a4 + 2 * 8:0x7bf5a4 + 3 * 8]))
    # 4. ferris wheel cabin: quiz
    b.set_obj_script(34, 42, 1, L['R22_RuotaQuiz'])
    b.note(kind='ruota_quiz')
    # 5. Casa delle Aie patrons
    T = scripts22.TRAINERS_AIE
    SP = dict(SNORLAX=143, MUNCHLAX=143)
    import re
    def S(name):
        txt = open('/home/claude/proj/sorgenti_romagna/include/constants/species.h').read()
        return int(re.search(r'#define SPECIES_%s\s+(\d+)' % name, txt).group(1))
    # levels for the stretch between the 1st and the 2nd badge (Riva 9, Viola 17)
    b.trainer(T[0], 'GUIDO', 0x1e, 35, [(S('ZIGZAGOON'), 15, 0, 100), (S('POOCHYENA'), 16, 0, 100)])
    b.trainer(T[1], 'TERESA', 0x14, 21, [(S('SKITTY'), 15, 0, 100), (S('MARILL'), 17, 0, 100)], female=True)
    b.trainer(T[2], 'PRIMO', 0x27, 55, [(S('BARBOACH'), 16, 0, 120), (S('WINGULL'), 16, 0, 120)])
    b.trainer(T[3], 'LORIS', 0x24, 51, [(S('ZANGOOSE'), 17, 0, 120), (S('SPINDA'), 16, 0, 120), (S('MACHOP'), 17, 0, 120)])
    b.trainer(T[4], 'NORMA', 0x0a, 24, [(S('SHROOMISH'), 17, 0, 150), (S('NUMEL'), 17, 0, 150), (S('SWABLU'), 18, 0, 150)], female=True)
    # progression of the gym leaders: Ada 40 (5th) < Alida (6th) < Rino 45 (7th) < Leda (8th) < Elite Four 49+
    def relevel(tid, levels):
        p_ = 0xf21000 + tid * 40; n_ = b.d[p_ + 32]; st = 16 if b.d[p_] & 1 else 8
        pp = struct.unpack_from('<I', b.d, p_ + 36)[0] - 0x8000000
        assert len(levels) == n_, (tid, n_)
        for k, lv in enumerate(levels):
            struct.pack_into('<H', b.d, pp + k * st + 2, lv)
    relevel(270, [38, 39, 40, 41, 43])        # ALIDA (Lugo, 6th badge)
    relevel(272, [44, 45, 45, 46, 48])        # LEDA (Bagno, 8th badge)
    relevel(747, [44, 44])                    # MILO (Bagno gym)
    relevel(25, [38, 40])                     # RENATO (Ravenna gym, after Faenza)
    relevel(856, [38, 40])                    # PILOTA (Lugo gym)
    b.note(kind='balance', alida=[38, 43], leda=[44, 48], aie=[15, 18], snorlax=20)
    b.note(kind='trainers', ids=T)


LAND_SEAMS = {(0, 9), (0, 10), (0, 16), (34, 14), (34, 17), (34, 20), (34, 21), (34, 22), (34, 44), (35, 36), (34, 96), (35, 40)}


def seam_warps(b):
    """Connected maps are drawn with the tileset of the map you are in, so every seam between two of our
    towns (each with its own tileset) showed garbage. The land seams become edge warps instead: stepping on
    the last row/column of a walkable crossing warps to the matching cell of the neighbour (coord events with
    a warp-to-coordinates script); the connections are removed and the border woods close the view."""
    rom = b.W.rom
    src, todo, k = [], {}, 0
    for A in sorted(LAND_SEAMS):
        mA = rom.map(*A); aA = rom.blocks(mA); HA, WA = aA.shape
        for c in mA['conns']:
            Bm = (c['group'], c['num'])
            if Bm not in LAND_SEAMS or c['dir'] not in (1, 2, 3, 4):
                continue
            mB = rom.map(*Bm); aB = rom.blocks(mB); HB, WB = aB.shape
            o = c['offset']
            if c['dir'] in (1, 2):
                pairs = [((x, HA - 1 if c['dir'] == 1 else 0), (x - o, 0 if c['dir'] == 1 else HB - 1)) for x in range(WA)]
            else:
                pairs = [((WA - 1 if c['dir'] == 4 else 0, y), (0 if c['dir'] == 4 else WB - 1, y - o)) for y in range(HA)]
            for (ax, ay), (bx, by) in pairs:
                if not (0 <= bx < WB and 0 <= by < HB):
                    continue
                if int(aA[ay, ax]) & 0xC00 or int(aB[by, bx]) & 0xC00:
                    continue
                lab = 'R22_Seam%d' % k; k += 1
                src.append(f'''
	.set SEAM_{k}, ({Bm[0]} << 8) | {Bm[1]}
{lab}::
	lockall
	warpsilent SEAM_{k}, {bx}, {by}
	waitstate
	releaseall
	end
''')
                todo.setdefault(A, []).append((ax, ay, lab))
    labels = b.W.scripts(''.join(src), {})
    b.L.update(labels)
    for A, lst in todo.items():
        m = rom.map(*A)
        coords = [dict(c_) for c_ in m['coords']] + [dict(x=x, y=y, elev=0, var=0x400F, val=0, script=labels[l]) for (x, y, l) in lst]
        b.W.set_events(*A, coords=coords)
    for A in LAND_SEAMS:
        keep = [c for c in rom.map(*A)['conns'] if (c['group'], c['num']) not in LAND_SEAMS]
        b.W.set_connections(*A, keep)
    b.note(kind='seam_warps', cells={str(k_): len(v) for k_, v in todo.items()})
    print('seam warps', {k_: len(v) for k_, v in todo.items()})


def set_heal(b, hid, gn, xy):
    struct.pack_into('<BBhh', b.d, 0x74adc0 + (hid - 1) * 8, gn[0], gn[1], xy[0], xy[1])


MAP_MODULES = ['pineta', 'lido', 'cervia', 'saline', 'forli', 'faenza', 'ravenna', 'lugo', 'imola', 'bagno', 'ippodromo', 'campagna', 'costa', 'cesenatico', 'cesena', 'rimini', 'porto', 'maze', 'befane']
SURF = {'lido'}


def maps(b, only=None):
    import importlib
    sys.path.insert(0, '/home/claude/tools/mapkit/maps22')
    import r22
    probs = {}
    # new map: Casa delle Aie (interior)
    aie_gn = b.add_map((34, 23), 'casa delle aie')
    b.W.set_map_scripts(*aie_gn, [])
    b.W.header_set(*aie_gn, region=b.W.rom.map(34, 20)['region'], type=8, weather=0)
    import aie_int
    room = aie_int.build(aie_gn)
    res = r22.build(room, aie_int.TS, aie_int.STARTS)
    probs['aie_int'] = res['problems']
    r22.emit(b.W, res, b.L)
    # new map: Varco delle Saline (gatehouse between Cervia and the Saline)
    sea_gn = b.add_map((0, 47), 'mare di rimini')
    uw_gn = b.add_map((0, 54), 'fondale isola delle rose')
    gate_gn = b.add_map((34, 23), 'varco saline')
    vista_gn = b.add_map((34, 38), 'vista cannocchiale')
    assert vista_gn == (35, 39), vista_gn
    ravsea_gn = b.add_map((0, 47), 'mare di ravenna')
    moon_gn = b.add_map((34, 38), 'luna')
    wish_gn = b.add_map((34, 38), 'mondo dei desideri')
    grotta_gn = b.add_map((34, 38), 'grotta di mewtwo')
    assert (ravsea_gn, moon_gn, wish_gn, grotta_gn) == ((35, 40), (35, 41), (35, 42), (35, 43))
    b.W.set_map_scripts(*gate_gn, [])
    b.W.header_set(*gate_gn, region=b.W.rom.map(0, 10)['region'], type=8, weather=0)
    for name in (only or MAP_MODULES):
        mod = importlib.import_module(name)
        cv = mod.build()
        if name == 'campagna':
            cv.bwarps[0].update(group=aie_gn[0], num=aie_gn[1], warp=0)
        if name == 'cervia':
            cv.bwarps[-1].update(group=gate_gn[0], num=gate_gn[1], warp=0)
            cervia_gate_warp = len(cv.bwarps) - 1
        if name == 'ravenna':
            cv.conns = [dict(dir=4, offset=37, group=ravsea_gn[0], num=ravsea_gn[1])]
        if name == 'cesenatico':
            cv.bwarps[-1].update(group=grotta_gn[0], num=grotta_gn[1], warp=0)
            cesenatico_cave_warp = len(cv.bwarps) - 1
        if name == 'saline':
            cv.bwarps[-1].update(group=gate_gn[0], num=gate_gn[1], warp=1)
            saline_gate_warp = len(cv.bwarps) - 1
        res = r22.build(cv, mod.TS, mod.STARTS, surf=name in SURF)
        probs[name] = res['problems']
        r22.emit(b.W, res, b.L)
        if getattr(mod, 'HEAL', None) and getattr(cv, 'heal', None):
            set_heal(b, mod.HEAL, cv.gn, cv.heal)
        if name == 'costa':
            d = cv.doors['pensione']
            m = b.W.rom.map(22, 0)
            ws = [dict(w) for w in m['warps']]
            for w_ in ws: w_.update(group=34, num=21, warp=0)
            b.W.set_events(22, 0, warps=ws)
        if name == 'cesenatico':
            b.W.set_events(34, 22, warps=None)    # no-op placeholder (warps already emitted)
        if name == 'maze':
            b.W.header_set(34, 33, type=3, weather=0)
    # hotel: corridor + five rooms share one tileset
    import hotel, canvas
    cvs = hotel.build_all()
    idmap, grids = canvas.build_tileset(cvs, hotel.TS, hotel.TS)
    sec = b.W.secondary_from_folder(hotel.TS)
    for cv, grid in zip(cvs, grids):
        vx, vy = cv.void_cell
        cv.border = [grid[vy][vx][0]] * 4
        vals = r22.vals_of(cv, grid, idmap)
        b.W.set_layout(cv.gn[0], cv.gn[1], vals, cv.w, cv.h, r22.border_of(cv, idmap), r22.GENERAL, sec)
        def rs(v):
            return b.L[v] if isinstance(v, str) else v
        objs = [dict(o, script=rs(o.get('script'))) for o in cv.objs]
        bgs = [dict(x, arg=(0x08000000 + b.L[x['arg']]) if isinstance(x['arg'], str) else x['arg']) for x in cv.bbgs]
        b.W.set_events(cv.gn[0], cv.gn[1], objs, cv.bwarps, [], bgs)
    # regenerated generic interiors (fuller and all different)
    import rooms
    ROOMS = {'home': [(34, 5), (34, 16), (34, 49), (34, 63), (34, 64), (34, 66), (34, 78), (34, 103), (34, 104), (34, 105), (34, 106), (34, 107), (34, 108)],
             'trattoria': [(34, 2), (34, 4), (34, 50), (34, 77), (35, 7), (35, 23)],
             'shop': [(34, 3), (34, 28), (34, 62), (34, 46), (34, 67)],
             'office': [(34, 23), (34, 45), (34, 69), (35, 4)],
             }
    for theme, gns in ROOMS.items():
        for gn in gns:
            rm = rooms.make(gn, theme)
            res = r22.build(rm, 'r22_room_%d_%d' % gn, [(rm.w // 2, rm.h - 2)])
            if res['problems']:
                probs['room %d,%d' % gn] = res['problems']
            r22.emit(b.W, res, b.L)
    # Cervia interiors drawn by hand (MUSA, Municipio) and the gatehouse to the Saline
    import cervia_int
    rooms_c = [(n, f(gn)) for n, f, gn in cervia_int.ALL]
    rooms_c.append(('gate', cervia_int.gate(gate_gn, (0, 10, cervia_gate_warp), (34, 9, saline_gate_warp), 0x2cbd63)))
    for name, rm in rooms_c:
        st = [(w['x'], w['y'] - 1) for w in rm.bwarps if w['y'] == rm.h - 1] or [(rm.bwarps[0]['x'] - 1, rm.bwarps[0]['y'])]
        res = r22.build(rm, 'r22_cervia_%s' % name, st)
        if res['problems']:
            probs['cervia_int %s' % name] = res['problems']
        r22.emit(b.W, res, b.L)
    b.set_obj_script(34, 12, 2, b.L['R22_TorreStones'])
    # post-League legendaries: Jirachi (Wish World, portal off Cervia) and Deoxys (rocket off Ravenna -> Moon)
    import events22
    sys.path.insert(0, '/home/claude/tools/mapkit/sprites')
    import wish
    # sprites in the slots of three unused big dolls, each with a new palette tag (table extended)
    pt_ptrs = (0x8ea24, 0x8eab8, 0x8eb10)
    old = struct.unpack_from('<I', b.W.d, pt_ptrs[0])[0] - 0x8000000
    entries = []
    k = 0
    while True:
        pp, tg = struct.unpack_from('<IH', b.W.d, old + k * 8)
        entries.append((pp, tg)); k += 1
        if tg == 0x11ff: break
    newpals = {}
    for gfx, tag, img, pal in ((180, 0x1140, wish.jirachi(), wish.JIRACHI_PAL), (183, 0x1141, wish.portal(), wish.PORTAL_PAL), (182, 0x1142, wish.mewtwo(), wish.MEWTWO_PAL)):
        palp = b.W.alloc(wish.pal_bytes(pal), 'pal %x' % tag)
        entries.insert(len(entries) - 1, (0x8000000 + palp, tag))
        ip = struct.unpack_from('<I', b.W.d, 0x6ada3c + gfx * 4)[0] - 0x8000000
        struct.pack_into('<H', b.W.d, ip + 2, tag)
        b.W.d[ip + 12] = (b.W.d[ip + 12] & 0xF0) | 10
        imgs = struct.unpack_from('<I', b.W.d, ip + 28)[0] - 0x8000000
        enc = wish.encode(img)
        for f in range(20):
            dp, sz = struct.unpack_from('<IH', b.W.d, imgs + f * 8)
            if not (0x8000000 <= dp < 0xa000000) or sz != 512: break
            b.W.d[dp - 0x8000000:dp - 0x8000000 + 512] = enc
    tbl = b.W.alloc(b''.join(struct.pack('<IHxx', pp, tg) for pp, tg in entries), 'object palette table')
    for q in pt_ptrs:
        struct.pack_into('<I', b.W.d, q, 0x8000000 + tbl)
    rav = b.W.rom.map(34, 96)
    for gn_, fn, ts, st, surf, hdr in ((ravsea_gn, events22.mare_ravenna, 'r22_ravsea', [(0, 12)], True, dict(region=rav['region'], type=6, weather=2, music=rav['music'])),
                                       (moon_gn, events22.luna, 'r22_luna', [(6, 10)], False, dict(region=rav['region'], type=8, weather=0)),
                                       (wish_gn, events22.mondo, 'r22_wish', [(14, 17)], False, dict(region=b.W.rom.map(0, 10)['region'], type=8, weather=0)),
                                       (grotta_gn, events22.grotta, 'r22_grotta', [(12, 20)], False, dict(region=b.W.rom.map(34, 22)['region'], type=4, weather=0))):
        cv_ = fn(gn_)
        if gn_ == ravsea_gn:
            cv_.conns = [dict(dir=3, offset=-37, group=34, num=96)]
        if gn_ == grotta_gn:
            cv_.bwarps = [dict(x=x, y=21, elev=0, warp=cesenatico_cave_warp, num=22, group=34) for x in (12, 13)]
        b.W.set_map_scripts(*gn_, [])
        b.W.header_set(*gn_, **hdr)
        res = r22.build(cv_, ts, st, surf=surf)
        if res['problems']:
            probs[ts] = res['problems']
        r22.emit(b.W, res, b.L)
    # Grattacielo roof (real rooftop + telescope) and the telescope view of the Rocca di Cesena
    import cesenatico_int
    for name, fn, gn in cesenatico_int.ALL:
        rm = fn(gn)
        res = r22.build(rm, 'r22_cesenatico_%s' % name, [(12, rm.h - 2)])
        if res['problems']:
            probs['cesenatico_int %s' % name] = res['problems']
        r22.emit(b.W, res, b.L)
    import numpy as np
    ces = b.W.rom.map(34, 17)
    blk = b.W.rom.blocks(ces)[0:20, 2:26].copy()
    border = struct.unpack_from('<4H', b.W.d, ces['border'])
    b.W.set_layout(*vista_gn, [int(v) for v in blk.ravel()], 24, 20, border, ces['primary'], ces['secondary'])
    b.W.set_events(*vista_gn, objects=[], warps=[], coords=[], bgs=[])
    roofm = b.W.rom.map(34, 38)
    b.W.header_set(*vista_gn, region=roofm['region'], type=ces['type'], weather=0, music=roofm['music'])
    tbl = b.W.alloc(struct.pack('<HHI', 0x4000, 0, 0x08000000 + b.L['R22_VistaFrame']) + b'\x00' * 8, 'vista frame table')
    b.W.set_map_scripts(*vista_gn, [(2, tbl)])
    b.W.set_connections(*vista_gn, [])
    b.set_obj_script(26, 56, 1, b.L['R22_MiraggioReturn'])
    # Italian texts for the English Emerald strings still reachable: repoint every reference
    import json as _json
    for k in _json.load(open('/home/claude/r22/translations22.json')):
        old = struct.pack('<I', 0x8000000 + int(k, 16)); new = struct.pack('<I', 0x8000000 + b.L['R22_TT_' + k[2:]])
        n_ = 0; pos = 0
        while True:
            pos = b.W.d.find(old, pos)
            if pos < 0 or pos >= 0x1730000: break
            b.W.d[pos:pos + 4] = new; n_ += 1; pos += 4
        assert n_ > 0, k
    # accents: apostrophes used as accents and missing 'è' in the 0.21 texts (fixed in place)
    import accents22, scr as _scr
    addrs = set()
    for g_, cnt in romlib.COUNTS.items():
        if g_ not in (0, 1, 2, 22, 25, 26, 34, 35):
            continue
        for n_ in range(cnt):
            try: mm = b.W.rom.map(g_, n_)
            except Exception: continue
            ptrs = [o['script'] for o in mm['objects']] + [x['arg'] - 0x8000000 for x in mm['bgs'] if x['arg'] > 0x8000000] + [c['script'] for c in mm['coords']]
            for p_ in ptrs:
                try: ins, _ = _scr.decode(bytes(b.W.d), p_, 300)
                except Exception: continue
                for a_, nm, ar in ins:
                    for v in ar:
                        if isinstance(v, int) and 0x8000000 <= v < 0xa000000 and nm in ('loadword', 'msgbox', 'trainerbattle'):
                            addrs.add(v - 0x8000000)
    fixed = accents22.apply(b.W.d, addrs)
    b.note(kind='accents', fixed=len(fixed))
    b.set_obj_script(26, 67, 1, b.L['R22_MotonaveBack'])       # Navel Rock harbour: sailor back to Ravenna
    # mandatory rival battle on the Riviera (Cesenatico -> Rimini) after the Cesena gym
    for tid, mons in ((622, [(304, 17), (183, 18), (281, 20)]), (623, [(304, 17), (337, 18), (284, 20)]), (624, [(304, 17), (339, 18), (278, 20)])):
        b.trainer(tid, 'ALDO', 50, 70, [(sp, lv, 0, 40) for sp, lv in mons])
    riv = b.W.rom.map(34, 43)
    objs = [dict(o) for o in riv['objects']]
    assert len(objs) == 2
    objs.append(dict(x=30, y=26, gfx=135, script=b.L['R22_RivalTalk'], flag=0x4E9, move=9))
    coords = [dict(c) for c in riv['coords']] + [dict(x=x, y=26, elev=0, var=0x4001, val=0, script=b.L['R22_RivalRiviera']) for x in (28, 29)]
    b.W.set_events(34, 43, objects=objs, coords=coords)
    # Grattacielo keys: 0x2F0 is FLAG_HIDE_LITTLEROOT_TOWN_MOM_OUTSIDE (set at new game) -> free flag 0x4E8
    assert b.W.d[0xf10595] == 0x2b and b.W.d[0xf105a8] == 0x29
    struct.pack_into('<H', b.W.d, 0xf10596, 0x4E8)
    struct.pack_into('<H', b.W.d, 0xf105a9, 0x4E8)     # Isola Miraggio (Faraway Island): sailor back to Lido
    import cesena_int
    for name, fn, gn in cesena_int.ALL:
        rm = fn(gn)
        res = r22.build(rm, 'r22_cesena_%s' % name, [(9, rm.h - 2)])
        if res['problems']:
            probs['cesena_int %s' % name] = res['problems']
        r22.emit(b.W, res, b.L)
    # Cervia water gym: new look, same events; the opened bridge metatile is added to the tileset
    import canvas, tsbuild
    from PIL import Image
    gym = cervia_int.water_gym((2, 1))
    bm = tsbuild.Meta(gym.bopen, Image.new('RGBA', (16, 16), (0, 0, 0, 0)), behavior=0, layer=0, coll=0, elev=3)
    idmap, grids = canvas.build_tileset([gym], 'r22_cervia_gym', 'r22_cervia_gym', extra_metas=[bm])
    vx, vy = gym.void_cell
    gym.border = [grids[0][vy][vx][0]] * 4
    probs['gym cervia'], _ = r22.static_check(gym, grids[0], [(12, 25)])
    res = dict(cv=gym, folder='r22_cervia_gym', vals=r22.vals_of(gym, grids[0], idmap), border=r22.border_of(gym, idmap), problems=[])
    r22.emit(b.W, res, b.L)
    bid = idmap[id(bm)]
    for k in range(4):
        struct.pack_into('<H', b.W.d, 0x2cd6f2 + k * 9 + 5, bid)
    b.note(kind='cervia_gym', bridge_metatile=hex(bid))
    # Lido di Savio interiors drawn by hand (Caffè Panama, villa, Aldo's house)
    import lido_int
    for name, fn, gn in lido_int.ALL:
        rm = fn(gn)
        res = r22.build(rm, 'r22_lido_%s' % name, [(w['x'], w['y'] - 1) for w in rm.bwarps if w['y'] == rm.h - 1] or [(rm.bwarps[0]['x'], rm.bwarps[0]['y'] + 1)])
        if gn == (1, 1):
            b.W.set_map_scripts(1, 1, [(5, 0x172216c)])          # only the fly guard: no Emerald intro scripts
        if res['problems']:
            probs['lido_int %s' % name] = res['problems']
        r22.emit(b.W, res, b.L)
    # ---------------- Mare di Rimini, Isola delle Rose, fondale (Kyogre)
    import mare, numpy as np
    rom = b.W.rom
    porto = rom.map(34, 44)
    b.W.set_map_scripts(*sea_gn, []); b.W.set_map_scripts(*uw_gn, [])
    b.W.header_set(*sea_gn, region=porto['region'], type=6, weather=2, music=porto['music'])
    b.W.header_set(*uw_gn, region=porto['region'], type=5, weather=14, music=411)
    src = rom.map(0, 54); a = rom.blocks(src)
    crop = a[5:35, 20:60].copy()
    cv = mare.build(sea_gn)
    walk_uw = {(x, y) for y in range(30) for x in range(40) if not (int(crop[y, x]) & 0xc00)}
    kx, ky = 23, 15
    cv.deep_override = {(x, y) for (x, y) in walk_uw if abs(x - kx) <= 6 and abs(y - ky) <= 5}
    # deep water exactly over the reachable trench around Kyogre
    from PIL import Image
    darkim = Image.new('RGBA', (16, 16), (8, 24, 82, 110))
    for (x, y) in cv.deep:
        if cv.art[y][x] is not None and cv.art[y][x][3] == 0x12:
            cv.art[y][x] = None
    for (x, y) in cv.deep_override:
        if cv.art[y][x] is None:
            cv.art[y][x] = (darkim, None, 0, 0x12, False)
    cv.conns = [dict(dir=3, offset=-10, group=34, num=44), dict(dir=5, offset=0, group=uw_gn[0], num=uw_gn[1])]
    res = r22.build(cv, mare.TS, [(0, 10)], surf=True)
    probs['mare'] = res['problems']
    r22.emit(b.W, res, b.L)
    border = struct.unpack_from('<4H', b.d, src['border'])
    b.W.set_layout(uw_gn[0], uw_gn[1], [int(v) for v in crop.ravel()], 40, 30, border, src['primary'], src['secondary'])
    kyo = dict(x=kx, y=ky, gfx=197, script=b.L['R22_Kyogre'], flag=0x4E0, move=8, elev=1)
    b.W.set_events(*uw_gn, objects=[kyo], warps=[], coords=[], bgs=[])
    b.W.set_connections(*uw_gn, [dict(dir=6, offset=0, group=sea_gn[0], num=sea_gn[1])])
    pc = [dict(c) for c in rom.map(34, 44)['conns']] + [dict(dir=4, offset=10, group=sea_gn[0], num=sea_gn[1])]
    b.W.set_connections(34, 44, pc)
    b.note(kind='kyogre', sea=list(sea_gn), underwater=list(uw_gn))
    # ---------------- Rayquaza at Lugo (monument to Baracca), after the League
    lugo = rom.map(34, 110); la = rom.blocks(lugo)
    occ = {(o['x'], o['y']) for o in lugo['objects']}
    best = None
    for r_ in range(1, 6):
        for dx in range(-r_, r_ + 1):
            for dy in range(-r_, r_ + 1):
                x, y = 27 + dx, 25 + dy
                if not (int(la[y, x]) & 0xc00) and (x, y) not in occ and best is None:
                    best = (x, y)
        if best: break
    objs = [dict(o) for o in lugo['objects']] + [dict(x=best[0], y=best[1], gfx=41, script=b.L['R22_Rayquaza'], flag=0x4E2, move=8)]
    b.W.set_events(34, 110, objects=objs)
    # ---------------- Dive giver at the Bagno gym door, GS Ball from Prof. Pino
    gym = rom.map(35, 26); ga = rom.blocks(gym)
    w0 = gym['warps'][0]
    spot = next((x, y) for (x, y) in ((w0['x'] - 2, w0['y'] - 1), (w0['x'] + 2, w0['y'] - 1), (w0['x'] - 2, w0['y'] - 2), (w0['x'] + 3, w0['y'] - 2))
                if not (int(ga[y, x]) & 0xc00))
    objs = [dict(o) for o in gym['objects']] + [dict(x=spot[0], y=spot[1], gfx=42, script=b.L['R22_DiveGiver'], move=8)]
    b.W.set_events(35, 26, objects=objs)
    b.set_obj_script(1, 4, 1, b.L['R22_ProfPino'])
    # ---------------- cheater room: warning in front of the red door
    corr = rom.map(34, 15)
    cw = corr['warps'][5]
    coords = [dict(x=cw['x'], y=cw['y'] + 1, elev=0, var=0x4001, val=0, script=b.L['R22_CheaterDoorWarn'])]
    b.W.set_events(34, 15, coords=coords)
    # uniform PC / Mart / Gym in the later cities
    import uniform
    rep = {}
    b.note(kind='uniform_buildings', report={str(k): v for k, v in rep.items()})
    print(rep)
    seam_warps(b)
    b.note(kind='maps', problems={k: [list(map(str, p)) for p in v] for k, v in probs.items()}, aie=list(aie_gn))
    return probs


if __name__ == '__main__':
    b = Build()
    b.assemble(scripts22.signs_src() + scripts22.translations_src())
    fixes(b)
    ow_pokemon(b, 235, 321, 0x1133, shiny=True)
    print(maps(b))
    out, sha = b.save()
    print(out, sha, hex(b.W.cursor))
