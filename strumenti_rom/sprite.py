"""Sprite degli oggetti sulla mappa (persone, rocce, massi...) disegnati sulle anteprime delle mappe.

Tabella delle grafiche: 0x6ada3c + gfx*4 -> ObjectEventGraphicsInfo (36 byte):
  +2 tag della tavolozza, +8 larghezza, +10 altezza, +28 puntatore ai fotogrammi (8 byte: puntatore, dimensione).
Tavolozze: il puntatore alla tabella sta nel codice a 0x8ea24; voci (puntatore, tag, 0), fine con tag 0x11ff.
Si disegna il primo fotogramma (di solito: rivolto in basso).
"""
import struct
import numpy as np
from PIL import Image

B = 0x08000000
GFX_TAB = 0x6ada3c
PAL_REF = 0x8ea24


def u32(d, p): return struct.unpack_from('<I', d, p)[0]


def _lz(d, p):
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
    return bytes(out)


def tavolozze(d):
    t = u32(d, PAL_REF) - B; out = {}
    while True:
        p, tag = struct.unpack_from('<IH', d, t)
        if p == 0 and tag == 0x11ff: break
        out[tag] = p - B; t += 8
    return out


def immagine(d, gfx, pals=None):
    """Primo fotogramma dello sprite `gfx` come immagine RGBA."""
    pals = pals or tavolozze(d)
    info = u32(d, GFX_TAB + gfx * 4) - B
    tag = struct.unpack_from('<H', d, info + 2)[0]
    w, h = struct.unpack_from('<hh', d, info + 8)
    fr = u32(d, info + 28) - B
    ip = u32(d, fr) - B
    raw = d[ip:ip + w * h // 2]
    px = np.empty(len(raw) * 2, np.uint8); a = np.frombuffer(raw, np.uint8); px[::2] = a & 15; px[1::2] = a >> 4
    tw, th = w // 8, h // 8
    img = px.reshape(th, tw, 8, 8).transpose(0, 2, 1, 3).reshape(h, w)
    pp = pals.get(tag)
    pal = np.frombuffer(d[pp:pp + 32], '<u2') if pp is not None else np.arange(16, dtype='<u2') * 0x0842
    rgb = (np.stack([pal & 31, (pal >> 5) & 31, (pal >> 10) & 31], -1) * 255 // 31).astype(np.uint8)
    rgba = np.zeros((h, w, 4), np.uint8); rgba[..., :3] = rgb[img]; rgba[..., 3] = np.where(img == 0, 0, 255)
    return Image.fromarray(rgba, 'RGBA')


def disegna(d, im, oggetti, scala=1):
    """oggetti: lista di (x, y, gfx). Lo sprite poggia sul fondo della casella ed e' centrato."""
    pals = tavolozze(d); cache = {}
    for x, y, gfx in oggetti:
        if gfx not in cache: cache[gfx] = immagine(d, gfx, pals)
        s = cache[gfx]
        if scala != 1: s = s.resize((s.width * scala, s.height * scala), Image.NEAREST)
        t = 16 * scala
        im.paste(s, (x * t + (t - s.width) // 2, y * t + t - s.height), s)
    return im


def numeri(im, etichette, scala=1):
    """Numeri di riferimento accanto agli oggetti delle bozze: etichette = [(x, y, testo)]."""
    from PIL import ImageDraw
    dr = ImageDraw.Draw(im); t = 16 * scala
    for x, y, testo in etichette:
        px, py = x * t + t, y * t - t // 2
        dr.rectangle([px - 1, py - 1, px + 7 * len(testo) + 3, py + 12], fill=(20, 20, 20))
        dr.text((px + 1, py), testo, fill=(255, 230, 0))
    return im
