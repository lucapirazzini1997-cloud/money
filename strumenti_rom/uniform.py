"""Swap custom PC/Mart/Gym buildings of the late cities for the uniform General ones, in place.
General building tiles are copied into free slots of the city's secondary tileset (palettes 0-5 are General's)."""
import struct, collections
import numpy as np
import romlib, pickle
GBITS = pickle.load(open('/home/claude/tools/mapkit/general_bits.pkl', 'rb'))
B = 0x08000000
GEN = 0x55e8c0
PC = [[0x048, 0x049, 0x04A, 0x04B], [0x050, 0x051, 0x052, 0x053], [0x058, 0x059, 0x05A, 0x05B], [0x060, 0x061, 0x062, 0x063]]
MART = [[0x028, 0x029, 0x029, 0x02B], [0x030, 0x031, 0x032, 0x033], [0x038, 0x039, 0x03A, 0x03B], [0x060, 0x041, 0x042, 0x043]]
GYM = [[0x1AA, 0x1AB, 0x1AB, 0x1AB, 0x1AB, 0x1AC], [0x1B2, 0x1B3, 0x1B3, 0x1B3, 0x1B3, 0x1B4], [0x1B8, 0x1B9, 0x1BA, 0x1B3, 0x1BB, 0x1BC],
       [0x1C0, 0x1C1, 0x1C2, 0x1C5, 0x1C3, 0x1C4], [0x1C8, 0x1C9, 0x1CA, 0x1CD, 0x1CB, 0x1CC]]
GRID = {'PC': (PC, (1, 3)), 'MART': (MART, (1, 3)), 'GYM': (GYM, (3, 4))}


def encode(t):
    f = np.asarray(t, dtype=np.uint8).ravel()
    return bytes(f[::2] | (f[1::2] << 4))


def run(W, jobs):
    """jobs: {(g,n): {warp_index: kind}}. Returns report."""
    rom = W.rom; d = W.d
    gen = rom.tileset(GEN)
    gmeta = gen['metatiles']; gattr = gen['attrs']
    report = {}
    for gn, swaps in jobs.items():
        m = rom.map(*gn)
        a = rom.blocks(m)
        H, Wd = a.shape
        sec = m['secondary']
        ts = rom.tileset(sec)
        tiles = [t.copy() for t in ts['tiles']] + [np.zeros((8, 8), np.uint8)] * (512 - len(ts['tiles']))
        pals = bytes(d[ts['pals']:ts['pals'] + 512])
        meta = bytearray(d[ts['metatiles']:ts['metatiles'] + 512 * 16])
        attrs = bytearray(d[ts['attrs']:ts['attrs'] + 1024])
        users = [k for k, mm in romlib.all_maps(rom).items() if mm['secondary'] == sec and k[0] != 33]
        used_mt = set()
        for k in users:
            used_mt |= set(int(v) & 1023 for v in rom.blocks(rom.map(*k)).ravel())
        # ground used around the old building
        cnt = collections.Counter(int(v) & 1023 for v in a.ravel() if not (int(v) & 0xc00))
        for wi, kind in swaps.items():
            w = m['warps'][wi]
            grid, (dc, dr) = GRID[kind]
            bx, by = w['x'] - dc, w['y'] - dr
            # clear the old building: connected non-walkable/door cells around the door
            seen = {(w['x'], w['y'])}; q = [(w['x'], w['y'] - 1)]
            while q:
                x, y = q.pop()
                if (x, y) in seen or not (0 <= x < Wd and 0 <= y < H): continue
                if not (int(a[y, x]) & 0xc00) and abs(x - w['x']) > 1: continue
                if abs(x - w['x']) > 5 or abs(y - w['y']) > 6: continue
                seen.add((x, y))
                if int(a[y, x]) & 0xc00:
                    q += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
            ring = collections.Counter(int(a[y, x]) & 1023 for (x, y) in
                                       [(bx - 1, yy) for yy in range(by, by + len(grid))] + [(bx + len(grid[0]), yy) for yy in range(by, by + len(grid))]
                                       if 0 <= x < Wd and 0 <= y < H and not (int(a[y, x]) & 0xc00))
            ground = (ring.most_common(1) or cnt.most_common(1))[0][0]
            for (x, y) in seen:
                if (x, y) != (w['x'], w['y']):
                    a[y, x] = ground | 0x3000
        used_mt = set(int(v) & 1023 for v in a.ravel())
        for k in users:
            if k != tuple(gn): used_mt |= set(int(v) & 1023 for v in rom.blocks(rom.map(*k)).ravel())
        used_t = {0}
        for mt in range(512):
            refs = struct.unpack_from('<8H', meta, mt * 16)
            if (mt + 512) in used_mt:
                for r in refs:
                    if (r & 1023) >= 512: used_t.add((r & 1023) - 512)
        free_t = [i for i in range(511, 0, -1) if i not in used_t]
        n_free_t0 = len(free_t)
        free_mt = [mt for mt in range(511, -1, -1) if (mt + 512) not in used_mt]
        tmap = {}
        mtmap = {}
        ok = True
        def gtile(idx):
            return gen['tiles'][idx]
        need = []
        for wi, kind in swaps.items():
            need += [mid for row in GRID[kind][0] for mid in row]
        for mid in dict.fromkeys(need):
            refs = struct.unpack_from('<8H', d, gmeta + mid * 16)
            new = []
            for r in refs:
                t = r & 1023
                key = encode(gtile(t))
                if key not in tmap:
                    if not free_t:
                        ok = False; break
                    slot = free_t.pop(0); tiles[slot] = gtile(t).copy(); tmap[key] = slot
                new.append((512 + tmap[key]) | (r & 0xFC00))
            if not ok or not free_mt:
                ok = False; break
            mt = free_mt.pop(0)
            struct.pack_into('<8H', meta, mt * 16, *new)
            struct.pack_into('<H', attrs, mt * 2, struct.unpack_from('<H', d, gattr + mid * 2)[0])
            mtmap[mid] = mt + 512
        if not ok:
            report[gn] = 'not enough free tiles/metatiles (free tiles %d, free metatiles %d, need %d metatiles)' % (len(free_t), len(free_mt), len(set(need)))
            continue
        for wi, kind in swaps.items():
            w = m['warps'][wi]
            grid, (dc, dr) = GRID[kind]
            bx, by = w['x'] - dc, w['y'] - dr
            for ry, row in enumerate(grid):
                for rx, mid in enumerate(row):
                    bits = GBITS.get(mid, 12)
                    a[by + ry, bx + rx] = mtmap[mid] | ((bits & 3) << 10) | ((bits >> 2) << 12)
        # write new tileset + layout
        raw = b''.join(encode(t) for t in tiles)
        gp = W.alloc(raw.ljust(0x4000, b'\x00'), 'uniform tiles')
        pp = W.alloc(pals, 'uniform pals')
        mp = W.alloc(bytes(meta), 'uniform metatiles')
        ap = W.alloc(bytes(attrs), 'uniform attrs')
        hdr = bytearray(d[sec:sec + 24]); hdr[0] = 0
        for off, p in zip((4, 8, 12, 16), (gp, pp, mp, ap)):
            struct.pack_into('<I', hdr, off, B + p)
        nsec = W.alloc(bytes(hdr), 'uniform tileset')
        border = struct.unpack_from('<4H', d, m['border'])
        W.set_layout(gn[0], gn[1], [int(v) for v in a.ravel()], Wd, H, border, m['primary'], nsec)
        report[gn] = 'ok (%d tiles, %d metatiles)' % (len(tmap), len(mtmap))
    return report
