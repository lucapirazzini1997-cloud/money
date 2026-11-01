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


def _ve(n):
    out = bytearray()
    while True:
        x = n & 0x7f; n >>= 7
        if n == 0: out.append(0x80 | x); return bytes(out)
        out.append(x); n -= 1


def create(src, dst, min_run=16):
    """Patch BPS lineare: SourceRead dove i byte coincidono, TargetCopy per le file di byte uguali (es. 0xFF),
    TargetRead per il resto. Stesse dimensioni di src e dst (le ROM sono a 32 MB)."""
    assert len(src) == len(dst)
    out = bytearray(b'BPS1') + _ve(len(src)) + _ve(len(dst)) + _ve(0)
    n = len(dst); i = 0; to = 0
    def emit(action, length): out.extend(_ve(((length - 1) << 2) | action))
    while i < n:
        j = i
        while j < n and src[j] == dst[j]: j += 1
        if j > i: emit(0, j - i); i = j; continue
        j = i
        while j < n and src[j] != dst[j]: j += 1
        k = i
        while k < j:
            r = k
            while r < j and dst[r] == dst[k]: r += 1
            if r - k >= min_run:
                emit(1, 1); out.append(dst[k])
                rel = k - to                  # TargetCopy dal byte appena scritto: ripete la fila
                emit(3, r - k - 1); out.extend(_ve((abs(rel) << 1) | (1 if rel < 0 else 0))); to = k + (r - k - 1)
                k = r
            else:
                q = k
                while q < j:
                    r2 = q
                    while r2 < j and dst[r2] == dst[q]: r2 += 1
                    if r2 - q >= min_run: break
                    q = r2
                emit(1, q - k); out.extend(dst[k:q]); k = q
        i = j
    out += zlib.crc32(src).to_bytes(4, 'little') + zlib.crc32(dst).to_bytes(4, 'little')
    out += zlib.crc32(bytes(out)).to_bytes(4, 'little')
    return bytes(out)
