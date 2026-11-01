"""Event-script disassembler for the Romagna ROM."""
import json, struct, sys
from pathlib import Path
from text_codec import CHAR

OPS = {int(k): v for k, v in json.load(open(Path(__file__).parent / 'scrops.json')).items()}
FIX = {0x16: ('setvar', [2, 2]), 0x19: ('copyvar', [2, 2]), 0x27: ('waitstate', []), 0x4f: ('applymovement', [2, 4]),
       0x50: ('applymovementat', [2, 4, 2]), 0x51: ('waitmovement', [2]), 0x52: ('waitmovementat', [2, 2]),
       0x53: ('removeobject', [2]), 0x54: ('removeobjectat', [2, 2]), 0x55: ('addobject', [2]), 0x56: ('addobjectat', [2, 2]),
       0x25: ('special', [2]), 0x26: ('specialvar', [2, 2]), 0x58: ('showobjectat', [2, 2]), 0x59: ('hideobjectat', [2, 2]),
       0x7d: ('bufferspeciesname', [1, 2]), 0x7e: ('bufferleadmonspeciesname', [1]), 0x7f: ('bufferpartymonnick', [1, 2]),
       0x80: ('bufferitemname', [1, 2]), 0x81: ('bufferdecorationname', [1, 2]), 0x82: ('buffermovename', [1, 2]),
       0x83: ('buffernumberstring', [1, 2]), 0x84: ('bufferstdstring', [1, 2]), 0x85: ('bufferstring', [1, 4]),
       0xa8: ('setobjectsubpriority', [2, 2, 1]), 0xa9: ('resetobjectsubpriority', [2, 2]), 0xbf: ('vbufferstring', [1, 4]),
       0xc6: ('bufferboxname', [1, 2]), 0xd3: ('moverotatingtileobjects', [2]), 0xd4: ('turnrotatingtileobjects', []),
       0xdd: ('buffertrainerclassname', [1, 2]), 0xde: ('buffertrainername', [1, 2]), 0xe1: ('buffercontestname', [1, 2]),
       0xe2: ('bufferitemnameplural', [1, 2, 2]), 0xe3: ('op_e3', [])}
for o in (0x39, 0x3a, 0x3b, 0x3c, 0x3d, 0x3e, 0x3f, 0x40, 0x41, 0xc4, 0xd1, 0xd7, 0xe0):
    FIX[o] = (OPS[o][0] if o in OPS else 'warpx', [1, 1, 1, 2, 2])
TB = {0: 2, 1: 3, 2: 3, 3: 1, 4: 3, 5: 2, 6: 3, 7: 3, 8: 4, 9: 2, 10: 2, 11: 2, 12: 2}
PTR_ARGS = {0x04, 0x05, 0x06, 0x07, 0x0f, 0x4f, 0x50, 0x85, 0xbf, 0x67, 0x0c, 0x0d, 0x0e, 0x23, 0x5c}
B = 0x08000000


def text(d, p, n=200):
    out = []
    for i in range(n):
        c = d[p + i]
        if c == 0xff: break
        out.append(CHAR.get(c, '\\n' if c == 0xfe else ('\\p' if c == 0xfb else ('\\l' if c == 0xfa else '{%02x}' % c))))
    return ''.join(out)


def decode(d, p, maxn=400, follow=True):
    """Linear disassembly from p; returns list of (addr, name, args) and referenced targets."""
    out, seen, todo, targets = [], set(), [p], []
    while todo:
        p = todo.pop(0)
        while p not in seen and len(out) < maxn:
            seen.add(p)
            op = d[p]
            if op in FIX: name, sizes = FIX[op]
            elif op in OPS: name, sizes = OPS[op][0], OPS[op][1]
            else:
                out.append((p, '??%02x' % op, [])); break
            q = p + 1
            if op == 0x5c:
                t = d[q]; args = [t, struct.unpack_from('<H', d, q + 1)[0], struct.unpack_from('<H', d, q + 3)[0]]; q += 5
                for _ in range(TB.get(t, 2)):
                    args.append(struct.unpack_from('<I', d, q)[0]); q += 4
                sizes2 = None
            else:
                args = []
                for s in sizes:
                    args.append(int.from_bytes(d[q:q + s], 'little')); q += s
            out.append((p, name, args))
            if op in (0x05, 0x06, 0x04, 0x07) and follow:
                tgt = args[-1] - B
                if 0 <= tgt < len(d): todo.append(tgt); targets.append(tgt)
            if op in (0x02, 0x03, 0x05, 0x08, 0x0c) : break
            p = q
    return sorted(out), targets


def show(d, p, maxn=300):
    ins, _ = decode(d, p, maxn)
    lines = []
    for a, name, args in ins:
        s = '%07x  %-22s %s' % (a, name, ', '.join(hex(x) for x in args))
        for x in args:
            if isinstance(x, int) and B <= x < B + len(d):
                t = x - B
                if name in ('loadword', 'message', 'trainerbattle', 'msgbox') or (name == 'loadword'):
                    s += '\n            "%s"' % text(d, t)
        lines.append(s)
    return '\n'.join(lines)


if __name__ == '__main__':
    d = open(sys.argv[1], 'rb').read()
    for a in sys.argv[2:]:
        print('==', a); print(show(d, int(a, 16)))
