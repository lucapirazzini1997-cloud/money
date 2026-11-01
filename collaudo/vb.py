#!/usr/bin/env python3
"""Frontend minimo libretro (core VBA-M) con lo stesso protocollo di emu/h (stdin comandi, stderr risposte)."""
import sys, ctypes as C, os
CORE = os.environ.get('VBAM_CORE', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vbam-libretro', 'src', 'libretro', 'vbam_libretro.so'))
if not os.environ.get('VBAM_ORA_VERA'):        # orologio ripetibile (prepara_emulatori.sh applica VBAM_ORA_FISSA a RTC.cpp)
    os.environ.setdefault('VBAM_ORA_FISSA', '1767268800'); os.environ.setdefault('TZ', 'UTC')   # 1/1/2026 12:00
lib = C.CDLL(CORE)
class GameInfo(C.Structure): _fields_ = [('path', C.c_char_p), ('data', C.c_void_p), ('size', C.c_size_t), ('meta', C.c_char_p)]
class Desc(C.Structure): _fields_ = [('flags', C.c_uint64), ('ptr', C.c_void_p), ('offset', C.c_size_t), ('start', C.c_size_t), ('select', C.c_size_t), ('disconnect', C.c_size_t), ('len', C.c_size_t), ('addrspace', C.c_char_p)]
class MMap(C.Structure): _fields_ = [('descriptors', C.POINTER(Desc)), ('num', C.c_uint)]
class Var(C.Structure): _fields_ = [('key', C.c_char_p), ('value', C.c_char_p)]
REGIONS = {}
SYSDIR = C.c_char_p(os.path.dirname(os.path.abspath(__file__)).encode())
fmt = [0]
ENVF = C.CFUNCTYPE(C.c_bool, C.c_uint, C.c_void_p)
def env(cmd, data):
    c = cmd & 0xffff
    if c in (9, 31):  # system / save dir
        C.cast(data, C.POINTER(C.c_char_p))[0] = SYSDIR.value; return True
    if c == 27: C.cast(data, C.POINTER(LogIf))[0].log = logf; return True
    if c == 10: fmt[0] = C.cast(data, C.POINTER(C.c_int))[0]; return True
    if c == 15:
        v = C.cast(data, C.POINTER(Var))[0]
        return False
    if c == 36:
        m = C.cast(data, C.POINTER(MMap))[0]
        for i in range(m.num):
            d = m.descriptors[i]
            if d.ptr and d.len: REGIONS[d.start] = (d.ptr, d.len)
        return True
    return False
LOGF = C.CFUNCTYPE(None, C.c_int, C.c_char_p)
logf = LOGF(lambda lvl, f: None)
class LogIf(C.Structure): _fields_ = [('log', LOGF)]
envf = ENVF(env)
frame = [None, 0, 0, 0]
VIDF = C.CFUNCTYPE(None, C.c_void_p, C.c_uint, C.c_uint, C.c_size_t)
def vid(data, w, h, pitch):
    if data: frame[0] = C.string_at(data, pitch * h); frame[1:] = [w, h, pitch]
vidf = VIDF(vid)
AUDF = C.CFUNCTYPE(None, C.c_int16, C.c_int16); audf = AUDF(lambda l, r: None)
AUDBF = C.CFUNCTYPE(C.c_size_t, C.c_void_p, C.c_size_t); audbf = AUDBF(lambda d, n: n)
POLLF = C.CFUNCTYPE(None); pollf = POLLF(lambda: None)
keys = [0]
# libretro joypad ids: B=0 Y=1 SELECT=2 START=3 UP=4 DOWN=5 LEFT=6 RIGHT=7 A=8 X=9 L=10 R=11
MAP = {8: 1, 0: 2, 2: 4, 3: 8, 7: 16, 6: 32, 4: 64, 5: 128, 11: 256, 10: 512}
STF = C.CFUNCTYPE(C.c_int16, C.c_uint, C.c_uint, C.c_uint, C.c_uint)
def st(port, dev, idx, id_):
    if port or dev != 1: return 0
    if id_ == 256:  # bitmask
        return sum(1 << k for k, m in MAP.items() if keys[0] & m)
    m = MAP.get(id_); return 1 if (m and keys[0] & m) else 0
stf = STF(st)
lib.retro_set_environment(envf); lib.retro_set_video_refresh(vidf); lib.retro_set_audio_sample(audf)
lib.retro_set_audio_sample_batch(audbf); lib.retro_set_input_poll(pollf); lib.retro_set_input_state(stf)
lib.retro_init()
rom = open(sys.argv[1], 'rb').read(); rbuf = C.create_string_buffer(rom, len(rom))
gi = GameInfo(sys.argv[1].encode(), C.cast(rbuf, C.c_void_p), len(rom), None)
assert lib.retro_load_game(C.byref(gi))
lib.retro_set_controller_port_device(0, 1)
if len(sys.argv) > 2 and os.path.exists(sys.argv[2]):   # salvataggio di partenza (come ./h ROM SAV)
    lib.retro_get_memory_data.restype = C.c_void_p; lib.retro_get_memory_size.restype = C.c_size_t
    sv = open(sys.argv[2], 'rb').read(); n = min(len(sv), lib.retro_get_memory_size(0))
    C.memmove(lib.retro_get_memory_data(0), sv, n)
lib.retro_get_memory_data.restype = C.c_void_p; lib.retro_get_memory_size.restype = C.c_size_t
lib.retro_serialize_size.restype = C.c_size_t
def loc(a):
    for s, (p, n) in REGIONS.items():
        if s <= a < s + n: return p + (a - s)
    if 0x08000000 <= a < 0x0a000000: return C.cast(rbuf, C.c_void_p).value + (a - 0x08000000)
    raise KeyError(hex(a))
def rd(a, n): return C.string_at(loc(a), n)
def wr(a, b): C.memmove(loc(a), b, len(b))
SAV = sys.argv[2] if len(sys.argv) > 2 else None
def scrivi_sav():
    """Come un emulatore vero: la memoria di salvataggio della cartuccia finisce nel file .sav (a 'ping' e a 'quit')."""
    if not SAV: return
    n = lib.retro_get_memory_size(0)
    if n: open(SAV, 'wb').write(C.string_at(lib.retro_get_memory_data(0), n))
def runf(n):
    for _ in range(n): lib.retro_run()
out = sys.stderr
for line in sys.stdin:
    p = line.split()
    if not p: continue
    c = p[0]
    if c == 'run': runf(int(p[1]))
    elif c == 'key': keys[0] = int(p[1], 16); runf(int(p[2])); keys[0] = 0
    elif c == 'ram': out.write(rd(int(p[1], 16), int(p[2])).hex() + '\n'); out.flush()
    elif c in ('r8', 'r16', 'r32'):
        n = {'r8': 1, 'r16': 2, 'r32': 4}[c]; out.write('%0*x\n' % (2 * n, int.from_bytes(rd(int(p[1], 16), n), 'little'))); out.flush()
    elif c in ('w8', 'w16', 'w32'):
        n = {'w8': 1, 'w16': 2, 'w32': 4}[c]; wr(int(p[1], 16), int(p[2], 16).to_bytes(n, 'little'))
    elif c == 'shot':
        data, w, h, pitch = frame
        px = bytearray()
        for y in range(h):
            row = data[y * pitch:y * pitch + w * (4 if fmt[0] == 1 else 2)]
            for x in range(w):
                if fmt[0] == 1: b, g, r = row[4 * x], row[4 * x + 1], row[4 * x + 2]
                else:
                    v = row[2 * x] | row[2 * x + 1] << 8
                    if fmt[0] == 2: r, g, b = (v >> 11) << 3, ((v >> 5) & 63) << 2, (v & 31) << 3
                    else: r, g, b = ((v >> 10) & 31) << 3, ((v >> 5) & 31) << 3, (v & 31) << 3
                px += bytes((r, g, b))
        open(p[1], 'wb').write(b'P6\n%d %d\n255\n' % (w, h) + px)
    elif c == 'savestate':
        n = lib.retro_serialize_size(); b = C.create_string_buffer(n); assert lib.retro_serialize(b, n); open(p[1], 'wb').write(b.raw)
    elif c == 'loadstate':
        d = open(p[1], 'rb').read(); assert lib.retro_unserialize(d, len(d))
    elif c == 'ping': scrivi_sav(); out.write('ok\n'); out.flush()
    elif c == 'quit': scrivi_sav(); break
