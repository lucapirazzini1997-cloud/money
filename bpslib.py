"""Applicazione e verifica di patch BPS (formato standard, CRC32 controllati)."""
import zlib


def _vi(b, i):
    d, s = 0, 1
    while True:
        x = b[i]; i += 1; d += (x & 0x7f) * s
        if x & 0x80: return d, i
        s <<= 7; d += s


def apply(src, bps):
    assert bps[:4] == b'BPS1', 'non e una patch BPS'
    assert zlib.crc32(bps[:-4]) == int.from_bytes(bps[-4:], 'little'), 'patch corrotta'
    assert zlib.crc32(src) == int.from_bytes(bps[-12:-8], 'little'), 'la ROM di partenza non e quella attesa dalla patch'
    ss, i = _vi(bps, 4); ts, i = _vi(bps, i); ms, i = _vi(bps, i); i += ms
    res = bytearray(); end = len(bps) - 12; so = to = 0
    while i < end:
        v, i = _vi(bps, i); a = v & 3; n = (v >> 2) + 1
        if a == 0: res += src[len(res):len(res) + n]
        elif a == 1: res += bps[i:i + n]; i += n
        elif a == 2:
            o, i = _vi(bps, i); so += (-1 if o & 1 else 1) * (o >> 1); res += src[so:so + n]; so += n
        else:
            o, i = _vi(bps, i); to += (-1 if o & 1 else 1) * (o >> 1)
            for _ in range(n): res.append(res[to]); to += 1
    out = bytes(res)
    assert zlib.crc32(out) == int.from_bytes(bps[-8:-4], 'little'), 'risultato diverso da quello atteso'
    return out
