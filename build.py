#!/usr/bin/env python3
"""Pokémon Romagna — build completa.

Catena (ogni tappa verifica lo SHA-256 atteso):
  1. basi/rom047.gba + basi/base31.gba  --builder storico (storico_054/build54.py)-->  0.54
  2. 0.54  --pezzo_055/patch_054_055.bps (la 0.55 non ha sorgenti)-->                0.55
  3. 0.55  --versioni/ (moduli Python, uno per versione)-->                            0.56, 0.57, ...
  4. registri/ rigenerati e controllo delle flag condivise.

Uso:
  python3 build.py                 build completa fino all'ultima versione in VERSIONI
  python3 build.py --da 055        salta le tappe 1-2 usando out/Pokemon_Romagna_0_55.gba gia costruita
  python3 build.py --senza-registri
"""
import sys, os, json, hashlib, argparse, subprocess, shutil, importlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'out'
SHA = {
    '047': 'd26c0fd48f75fe1db4e36865f56b7ea9c9fd7914954d72e06ccfbaf45930122d',
    '031': 'c880c7034f02c6fd9ea6ee37a4ce35f7cee57042dd5121732e84627cf8a60948',
    '054': 'a06532552a9f79744d889e948d21d713043f29a32847e78d7febae9bbdc92906',
    '055': '2bfaa8a3ada9f8bbaa1112028f85f6d1d85e00d5bc71668e1444508b45e44ad6',
    '056': 'b09eb6977ca7ceaf81be2a184d719ce6cc25229d2889e4cc3c4fa4714237495f',
}
# Versioni costruite sopra la 0.55: (numero, modulo in versioni/). Ogni nuova versione aggiunge una riga
# e il suo SHA atteso in SHA (dopo averla collaudata). Il modulo espone apply(W) -> dict (rapporto).
VERSIONI = [('056', 'v056_cesena_rivale')]


def sha(b): return hashlib.sha256(b).hexdigest()


def nome(ver): return 'Pokemon_Romagna_0_%s.gba' % ver.lstrip('0')   # '056' -> Pokemon_Romagna_0_56.gba


def check(tag, data):
    h = sha(data)
    if tag in SHA:
        assert h == SHA[tag], 'SHA della %s diverso: %s (atteso %s)' % (tag, h, SHA[tag])
        print('  ok %s  %s' % (tag, h))
    else:
        print('  %s  %s  (nuovo: aggiungilo a SHA dopo il collaudo)' % (tag, h))
    return data


def tappa_054():
    print('[1] 0.54 dal builder storico')
    for f, tag in (('rom047.gba', '047'), ('base31.gba', '031')):
        check(tag, (ROOT / 'basi' / f).read_bytes())
        dst = ROOT / 'storico_054' / f
        if not dst.exists(): shutil.copy(ROOT / 'basi' / f, dst)
    tmp = OUT / 'storico054'
    r = subprocess.run([sys.executable, 'build54.py', '--out', str(tmp)], cwd=ROOT / 'storico_054',
                       capture_output=True, text=True)
    (OUT / 'build054.log').write_text(r.stdout + r.stderr)
    assert r.returncode == 0, 'builder storico fallito: vedi out/build054.log'
    return check('054', (tmp / 'Pokemon_Romagna_0_54.gba').read_bytes())


def tappa_055(rom054):
    print('[2] 0.55 dalla patch documentata')
    sys.path.insert(0, str(ROOT))
    import bpslib
    return check('055', bpslib.apply(rom054, (ROOT / 'pezzo_055' / 'patch_054_055.bps').read_bytes()))


def tappe_versioni(rom055):
    sys.path[:0] = [str(ROOT / 'versioni'), str(ROOT / 'strumenti_rom'), str(ROOT)]
    import engine
    W = engine.init(rom055)
    rapporto = {}
    for ver, mod in VERSIONI:
        print('[3] %s con versioni/%s.py' % (ver, mod))
        m = importlib.import_module(mod)
        rapporto[ver] = m.apply(W)
        data = check(ver, bytes(W.d))
        (OUT / nome(ver)).write_bytes(data)
    json.dump(dict(rapporto=rapporto, script=W.scripts_log, flag=engine.POOL.taken if engine.POOL else []),
              open(OUT / 'rapporto_build.json', 'w'), ensure_ascii=False, indent=1, default=str)
    return bytes(W.d), VERSIONI[-1][0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--da', choices=['047', '055'], default='047')
    ap.add_argument('--senza-registri', action='store_true')
    a = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    if a.da == '047':
        r054 = tappa_054(); (OUT / 'Pokemon_Romagna_0_54.gba').write_bytes(r054)
        r055 = tappa_055(r054); (OUT / 'Pokemon_Romagna_0_55.gba').write_bytes(r055)
    else:
        r055 = check('055', (OUT / 'Pokemon_Romagna_0_55.gba').read_bytes())
    final, ver = tappe_versioni(r055)
    if not a.senza_registri:
        print('[4] registri')
        sys.path.insert(0, str(ROOT / 'registri'))
        import genera
        genera.main(OUT / nome(ver), ROOT / 'registri', strict=True)
    print('fatto: out/' + nome(ver))


if __name__ == '__main__': main()
