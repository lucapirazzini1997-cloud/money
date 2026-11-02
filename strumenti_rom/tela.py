"""Tela: disegno di mappe nuove a partire da pezzi di layout e tileset gia' presenti nella ROM.

Idea
----
Ogni casella della tela e' una coppia (fonte, valore_blocco).  La fonte e' il tileset
secondario da cui viene il metatile (il primario e' sempre quello generale di Smeraldo,
0x55e8c0).  Il valore_blocco e' quello dei layout: bit 0-9 metatile, bit 10-11 collisione,
bit 12-15 elevazione.

Alla fine `Unione` costruisce UN secondario nuovo che contiene tutti i metatile usati:
- un metatile del primario che usa solo le palette 0-5 resta com'e' (id < 512);
- ogni altro metatile (del secondario di origine, o del primario ma colorato con le
  palette 6-12 della fonte) viene copiato nel secondario nuovo con le palette rimappate.
Le palette del secondario nuovo sono al massimo 7 (slot 6-12): se servono piu' coppie
(fonte, palette) l'unione si ferma con un errore, non indovina.
"""
import struct
import numpy as np
from PIL import Image

B = 0x08000000
PRIMARIO = 0x55e8c0
SLOT_SEC = list(range(6, 13))


def u32(d, p): return struct.unpack_from('<I', d, p)[0]


class Tileset:
    def __init__(self, d, tp):
        self.d, self.tp = d, tp
        self.comp = d[tp]
        self.gfx, self.pals, self.meta, self.attrs = (u32(d, tp + i) - B for i in (4, 8, 12, 16))

    def tiles(self):
        if self.comp:
            return _lz(self.d, self.gfx)
        return bytes(self.d[self.gfx:self.gfx + 0x4000])

    def refs(self, i):
        return struct.unpack_from('<8H', self.d, self.meta + (i % 512) * 16)

    def attr(self, i):
        return struct.unpack_from('<H', self.d, self.attrs + (i % 512) * 2)[0]

    def palette(self, k):
        return bytes(self.d[self.pals + k * 32:self.pals + k * 32 + 32])


def _lz(d, p):
    assert d[p] == 0x10, hex(p)
    n = int.from_bytes(d[p + 1:p + 4], 'little'); p += 4; out = bytearray()
    while len(out) < n:
        f = d[p]; p += 1
        for b in range(7, -1, -1):
            if len(out) >= n: break
            if f & (1 << b):
                a, c = d[p], d[p + 1]; p += 2
                k = (a >> 4) + 3; disp = ((a & 15) << 8) + c + 1
                for _ in range(k): out.append(out[-disp])
            else:
                out.append(d[p]); p += 1
    return bytes(out[:n])


class Unione:
    """Secondario nuovo fatto con i metatile usati dalle tele."""

    def __init__(self, d, primario=PRIMARIO):
        self.d = d
        self.prim = Tileset(d, primario)
        self.prim_tiles = self.prim.tiles()
        self.fonti = {}            # tp -> Tileset
        self.slot = {}             # (tp, pal) -> slot nuovo
        self.tiles = []            # 32 byte ciascuno
        self.tile_idx = {}
        self.meta = []             # (refs8, attr)
        self.meta_idx = {}
        self.extra_pal = {}        # slot -> 32 byte (palette disegnate a mano)

    def fonte(self, tp):
        if tp not in self.fonti:
            self.fonti[tp] = Tileset(self.d, tp)
            self.fonti[tp].raw = self.fonti[tp].tiles()
        return self.fonti[tp]

    def _slot(self, tp, pal):
        if pal < 6: return pal
        k = (tp, pal)
        if k not in self.slot:
            usati = set(self.slot.values()) | set(self.extra_pal)
            liberi = [s for s in SLOT_SEC if s not in usati]
            if not liberi:
                raise ValueError('troppe palette nel secondario nuovo: %s' % sorted(self.slot))
            self.slot[k] = liberi[0]
        return self.slot[k]

    def _tile(self, raw32):
        if raw32 not in self.tile_idx:
            assert len(self.tiles) < 512, 'troppi tile nel secondario nuovo'
            self.tile_idx[raw32] = 512 + len(self.tiles)
            self.tiles.append(raw32)
        return self.tile_idx[raw32]

    def metatile(self, tp, mt):
        """Id del metatile `mt` della fonte `tp` nel risultato."""
        if mt < 512:
            refs = self.prim.refs(mt)
            if all((r >> 12) < 6 for r in refs):
                return mt
            src_raw = None; attr = self.prim.attr(mt)
        else:
            f = self.fonte(tp); refs = f.refs(mt); attr = f.attr(mt); src_raw = f.raw
        new = []
        for r in refs:
            idx = r & 1023; pal = r >> 12
            if idx >= 512:
                raw32 = bytes(src_raw[(idx - 512) * 32:(idx - 512) * 32 + 32])
                idx = self._tile(raw32)
            new.append((r & 0x0c00) | idx | (self._slot(tp, pal) << 12))
        key = (tuple(new), attr)
        if key not in self.meta_idx:
            assert len(self.meta) < 512, 'troppi metatile nel secondario nuovo'
            self.meta_idx[key] = 512 + len(self.meta)
            self.meta.append(key)
        return self.meta_idx[key]

    def metatile_nuovo(self, refs, attr):
        """Metatile disegnato a mano: refs gia' nello spazio del risultato."""
        key = (tuple(refs), attr)
        if key not in self.meta_idx:
            self.meta_idx[key] = 512 + len(self.meta); self.meta.append(key)
        return self.meta_idx[key]

    # ---- uscita
    def blob(self):
        tiles = b''.join(self.tiles).ljust(0x4000, b'\x00')
        pals = bytearray(16 * 32)
        for (tp, pal), s in self.slot.items():
            pals[s * 32:s * 32 + 32] = self.fonte(tp).palette(pal)
        for s, raw in self.extra_pal.items():
            pals[s * 32:s * 32 + 32] = raw
        meta = b''.join(struct.pack('<8H', *r) for r, _ in self.meta).ljust(512 * 16, b'\x00')
        attrs = b''.join(struct.pack('<H', a) for _, a in self.meta).ljust(512 * 2, b'\x00')
        return tiles, bytes(pals), meta, attrs

    def scrivi(self, W, etichetta):
        tiles, pals, meta, attrs = self.blob()
        gp = W.alloc(tiles, 'tiles ' + etichetta)
        pp = W.alloc(pals, 'pals ' + etichetta)
        mp = W.alloc(meta, 'metatiles ' + etichetta)
        ap = W.alloc(attrs, 'attrs ' + etichetta)
        return W.alloc(bytes([0, 1, 0, 0]) + struct.pack('<4I', B + gp, B + pp, B + mp, B + ap) + b'\x00' * 4,
                       'tileset ' + etichetta)

    def stato(self):
        return dict(metatile=len(self.meta), tile=len(self.tiles), palette=len(self.slot) + len(self.extra_pal))


class Tela:
    """Griglia di (fonte, blocco)."""

    def __init__(self, d, w, h, fonte, blocco):
        self.d, self.w, self.h = d, w, h
        self.c = [[(fonte, blocco)] * w for _ in range(h)]

    @staticmethod
    def layout(d, lp):
        w, h = struct.unpack_from('<II', d, lp)
        bp, sec = u32(d, lp + 12) - B, u32(d, lp + 20) - B
        a = np.frombuffer(bytes(d[bp:bp + w * h * 2]), dtype='<u2').reshape(h, w)
        return a, sec

    def incolla(self, lp, x0, y0, w, h, x, y, salta=None):
        """Copia il rettangolo (x0,y0,w,h) del layout lp nella tela a (x,y)."""
        a, sec = self.layout(self.d, lp)
        for j in range(h):
            for i in range(w):
                v = int(a[y0 + j, x0 + i])
                if salta and (v & 1023) in salta: continue
                if 0 <= y + j < self.h and 0 <= x + i < self.w:
                    self.c[y + j][x + i] = (sec, v)

    def metti(self, x, y, fonte, blocco):
        if 0 <= y < self.h and 0 <= x < self.w:
            self.c[y][x] = (fonte, blocco)

    def riempi(self, x, y, w, h, fonte, blocco):
        for j in range(h):
            for i in range(w): self.metti(x + i, y + j, fonte, blocco)

    def valori(self, unione):
        out = []
        for riga in self.c:
            for tp, v in riga:
                out.append((v & 0xfc00) | unione.metatile(tp, v & 1023))
        return out


def anteprima(d, unione, valori, w, h, scala=1):
    """Immagine della mappa come la vedrebbe il gioco con il secondario nuovo."""
    prim = unione.prim
    ptiles = np.frombuffer(unione.prim_tiles, dtype=np.uint8)
    pt = np.empty(len(ptiles) * 2, np.uint8); pt[::2] = ptiles & 15; pt[1::2] = ptiles >> 4
    pt = pt.reshape(-1, 8, 8)
    tiles, pals, meta, attrs = unione.blob()
    st = np.frombuffer(tiles, dtype=np.uint8)
    s2 = np.empty(len(st) * 2, np.uint8); s2[::2] = st & 15; s2[1::2] = st >> 4
    s2 = s2.reshape(-1, 8, 8)
    raw = bytes(d[prim.pals:prim.pals + 192]) + pals[192:]
    v = np.frombuffer(raw, dtype='<u2')
    rgb = (np.stack([v & 31, (v >> 5) & 31, (v >> 10) & 31], -1) * 255 // 31).astype(np.uint8).reshape(16, 16, 3)
    cache = {}

    def mt(i):
        if i in cache: return cache[i]
        refs = prim.refs(i) if i < 512 else struct.unpack_from('<8H', meta, (i - 512) * 16)
        img = np.zeros((16, 16, 3), np.uint8)
        for layer in range(2):
            for q in range(4):
                r = refs[layer * 4 + q]; idx = r & 1023
                t = pt[idx] if idx < 512 else s2[idx - 512]
                if r & 0x400: t = t[:, ::-1]
                if r & 0x800: t = t[::-1, :]
                c = rgb[r >> 12][t]
                reg = img[(q // 2) * 8:(q // 2) * 8 + 8, (q % 2) * 8:(q % 2) * 8 + 8]
                if layer == 0: reg[:] = c
                else: reg[t != 0] = c[t != 0]
        cache[i] = img
        return img
    img = np.zeros((h * 16, w * 16, 3), np.uint8)
    for k, val in enumerate(valori):
        y, x = divmod(k, w)
        img[y * 16:y * 16 + 16, x * 16:x * 16 + 16] = mt(val & 1023)
    im = Image.fromarray(img)
    if scala != 1: im = im.resize((im.width * scala, im.height * scala), Image.NEAREST)
    return im
