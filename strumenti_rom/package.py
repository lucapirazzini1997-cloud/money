"""Package a release: python package.py 0_25  (ROM, RMG patch from 0.21, applica_patch.py, project, atlas from atlas list)."""
import sys, struct, hashlib, shutil, subprocess, os
from pathlib import Path
v = sys.argv[1]
out = Path('/home/claude/pkg%s' % v.replace('0_', ''))
if out.exists(): shutil.rmtree(out)
out.mkdir()
a = open('/home/claude/r22/base21.gba', 'rb').read(); b = open('/home/claude/r22/out/Pokemon_Romagna_0_22.gba', 'rb').read()
recs = []; i = 0; n = len(b); A = a + b'\xff' * (n - len(a))
while i < n:
    if A[i] != b[i]:
        j = i
        while j < n and (A[j] != b[j] or A[j:j + 16] != b[j:j + 16]): j += 1
        recs.append((i, b[i:j])); i = j
    else: i += 1
p = b'RMG1' + struct.pack('<I', n) + hashlib.sha256(a).digest() + hashlib.sha256(b).digest() + struct.pack('<I', len(recs)) + b''.join(struct.pack('<II', o, len(d)) + d for o, d in recs)
(out / ('Pokemon_Romagna_0_21_%s.rmg' % v)).write_bytes(p)
(out / ('Pokemon_Romagna_%s.gba' % v)).write_bytes(b)
s = open('/home/claude/pkg22/applica_patch.py').read().replace('0_22', v).replace('ROM 0.22', 'ROM ' + v.replace('_', '.'))
(out / 'applica_patch.py').write_text(s)
shutil.copy('/home/claude/r22/out/revision_0_22.json', out / ('revision_%s.json' % v))
shutil.copytree('/home/claude/r22', out / 'progetto/strumenti_rom', ignore=shutil.ignore_patterns('out', 'base21.gba', '*.png', '*.sav', '*.gba', '__pycache__'))
shutil.copytree('/home/claude/tools/mapkit', out / 'progetto/mapkit', ignore=shutil.ignore_patterns('__pycache__'))
r = subprocess.run([sys.executable, 'applica_patch.py', '/home/claude/r22/base21.gba', 'Pokemon_Romagna_0_21_%s.rmg' % v, '/tmp/claude-0/x.gba'], cwd=out, capture_output=True, text=True)
print(r.stdout, r.stderr)
