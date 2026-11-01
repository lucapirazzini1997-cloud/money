"""Writer for the Romagna 0.22 binary revision: allocations, tilesets, layouts, events, scripts."""
import struct, hashlib
import numpy as np
from pathlib import Path
from PIL import Image
import romlib, asm

B = 0x08000000
LAYOUT_TABLE_REFS = (0x8490c, 0x1aa5b0)
TS_ROOT = Path('/home/claude/proj/sorgenti_romagna/data/tilesets/secondary')


def P(p): return struct.pack('<I', B + p)


class Writer:
    def __init__(self, base='/home/claude/r22/base21.gba', start=0x1730000):
        self.rom = romlib.Rom(base)
        self.d = self.rom.data
        self.cursor = start
        self.log = []
        self.table = romlib.u32(self.d, LAYOUT_TABLE_REFS[0]) - B
        self.nlayouts = 800

    # ---------- allocation
    def alloc(self, raw, label='', align=4):
        self.cursor = (self.cursor + align - 1) & ~(align - 1)
        p = self.cursor
        assert all(v == 0xff for v in self.d[p:p + len(raw)]), 'occupied %x %s' % (p, label)
        self.d[p:p + len(raw)] = raw
        self.cursor += len(raw)
        self.log.append((p, len(raw), label))
        return p

    def reserve(self, n, label=''):
        return self.alloc(b'\x00' * n, label)

    # ---------- tilesets
    def secondary_from_folder(self, folder, label=None):
        d = TS_ROOT / folder
        img = Image.open(d / 'tiles.png')
        w, h = img.size
        px = np.array(img, dtype=np.uint8) & 15
        tiles = px.reshape(h // 8, 8, w // 8, 8).transpose(0, 2, 1, 3).reshape(-1, 8, 8)
        raw = bytearray()
        for t in tiles:
            f = t.ravel()
            raw += bytes(f[::2] | (f[1::2] << 4))
        raw = bytes(raw).ljust(0x4000, b'\x00')
        pals = b''
        for i in range(16):
            cols = [tuple(int(v) for v in l.split()[:3]) for l in (d / 'palettes' / ('%02d.pal' % i)).read_text().split('\n')[3:19] if l.strip()]
            pals += b''.join(struct.pack('<H', (r * 31 // 255) | ((g * 31 // 255) << 5) | ((b * 31 // 255) << 10)) for r, g, b in cols[:16])
        meta = (d / 'metatiles.bin').read_bytes()
        attr = (d / 'metatile_attributes.bin').read_bytes()
        gp = self.alloc(raw, 'tiles ' + folder)
        pp = self.alloc(pals, 'pals ' + folder)
        mp = self.alloc(meta.ljust(512 * 16, b'\x00'), 'metatiles ' + folder)
        ap = self.alloc(attr.ljust(512 * 2, b'\x00'), 'attrs ' + folder)
        return self.alloc(bytes([0, 1, 0, 0]) + P(gp) + P(pp) + P(mp) + P(ap) + b'\x00' * 4, 'tileset ' + folder)

    # ---------- layouts
    def set_layout(self, g, n, vals, w, h, border, primary, secondary):
        m = self.rom.map(g, n)
        bp = self.alloc(struct.pack('<%dH' % len(vals), *vals), 'blocks %d,%d' % (g, n))
        brp = self.alloc(struct.pack('<4H', *border), 'border %d,%d' % (g, n))
        lp = self.alloc(struct.pack('<II', w, h) + P(brp) + P(bp) + P(primary) + P(secondary), 'layout %d,%d' % (g, n))
        struct.pack_into('<I', self.d, m['header'], B + lp)
        lid = m['layout_id']
        struct.pack_into('<I', self.d, self.table + (lid - 1) * 4, B + lp)
        return lp

    def use_layout_of(self, g, n, src_layout_ptr):
        """Point a map at an existing layout (by ROM offset), keeping its own layout id slot."""
        m = self.rom.map(g, n)
        struct.pack_into('<I', self.d, m['header'], B + src_layout_ptr)
        struct.pack_into('<I', self.d, self.table + (m['layout_id'] - 1) * 4, B + src_layout_ptr)

    # ---------- events
    def set_events(self, g, n, objects=None, warps=None, coords=None, bgs=None):
        m = self.rom.map(g, n)
        objects = m['objects'] if objects is None else objects
        warps = m['warps'] if warps is None else warps
        coords = m['coords'] if coords is None else coords
        bgs = m['bgs'] if bgs is None else bgs
        ob = b''
        for i, o in enumerate(objects):
            raw = bytearray(o.get('raw', bytes(24)))
            raw[0] = o.get('id', i + 1); raw[1] = o['gfx']; raw[2] = o.get('kind', 0)
            struct.pack_into('<hh', raw, 4, o['x'], o['y'])
            raw[8] = o.get('elev', 3); raw[9] = o.get('move', 8)
            raw[10] = (o.get('rx', 0) & 15) | ((o.get('ry', 0) & 15) << 4)
            struct.pack_into('<HH', raw, 12, o.get('ttype', 0), o.get('trange', 0))
            struct.pack_into('<I', raw, 16, B + o['script'] if o.get('script') else 0)
            struct.pack_into('<H', raw, 20, o.get('flag', 0))
            ob += bytes(raw)
        wb = b''.join(struct.pack('<hhBBBB', w_['x'], w_['y'], w_.get('elev', 0), w_['warp'], w_['num'], w_['group']) for w_ in warps)
        cb = b''.join(struct.pack('<hhBxHHxxI', c['x'], c['y'], c.get('elev', 3), c['var'], c['val'], B + c['script']) for c in coords)
        bb = b''.join(struct.pack('<hhBBxxI', b_['x'], b_['y'], b_.get('elev', 0), b_.get('kind', 0), b_['arg']) for b_ in bgs)
        ptrs = []
        for blob, lab in ((ob, 'obj'), (wb, 'warps'), (cb, 'coords'), (bb, 'bgs')):
            ptrs.append(P(self.alloc(blob, lab + ' %d,%d' % (g, n))) if blob else b'\x00' * 4)
        ep = self.alloc(bytes([len(objects), len(warps), len(coords), len(bgs)]) + b''.join(ptrs), 'events %d,%d' % (g, n))
        struct.pack_into('<I', self.d, m['header'] + 4, B + ep)
        return ep

    def set_map_scripts(self, g, n, entries):
        """entries: list of (kind, ptr) ; kinds 2/4 need table pointers."""
        m = self.rom.map(g, n)
        sp = self.alloc(b''.join(bytes([k]) + P(p) for k, p in entries) + b'\x00', 'mapscripts %d,%d' % (g, n))
        struct.pack_into('<I', self.d, m['header'] + 8, B + sp)

    def set_connections(self, g, n, conns):
        m = self.rom.map(g, n)
        if not conns:
            struct.pack_into('<I', self.d, m['header'] + 12, 0); return
        lst = self.alloc(b''.join(struct.pack('<IiBBxx', c['dir'], c['offset'], c['group'], c['num']) for c in conns), 'conns')
        cp = self.alloc(struct.pack('<I', len(conns)) + P(lst), 'connhdr')
        struct.pack_into('<I', self.d, m['header'] + 12, B + cp)

    def header_set(self, g, n, **kw):
        m = self.rom.map(g, n); hp = m['header']
        offs = dict(music=(16, 'H'), region=(20, 'B'), cave=(21, 'B'), weather=(22, 'B'), type=(23, 'B'), flags=(26, 'B'), battle=(27, 'B'))
        for k, v in kw.items():
            o, f = offs[k]
            struct.pack_into('<' + f, self.d, hp + o, v)

    # ---------- scripts
    def scripts(self, src, externs=None, size_hint=0x20000):
        """Assemble a script bank at the cursor; returns label dict (ROM offsets)."""
        self.cursor = (self.cursor + 3) & ~3
        base = self.cursor
        code, labels = asm.assemble(src, base, externs)
        self.alloc(code, 'scripts')
        return {k: v for k, v in labels.items() if not k.startswith('_')}

    def save(self, path):
        Path(path).write_bytes(self.d)
        return hashlib.sha256(self.d).hexdigest()
