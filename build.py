#!/usr/bin/env python3
"""Pokémon Romagna — build completa.

Catena (ogni tappa verifica lo SHA-256 atteso):
  1. basi/rom047.gba + basi/base31.gba  --builder storico (storico_054/build54.py)-->  0.54
  2. 0.54  --pezzo_055/patch_054_055.bps (la 0.55 non ha sorgenti)-->                0.55
  3. 0.55  --versioni/ (moduli Python, uno per versione)-->                            0.56, 0.57, ...
  4. registri/ rigenerati e controllo delle flag condivise.
  5. controlli del Lotto 1 (registri/controlli.py): allenatori con flag riservata, mappe importanti o nuove
     non raggiungibili (la build fallisce), risorse libere e budget (out/rapporto_build.json).

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
    '057': '47f53668d8b5861956938cd041fb892e541b86031e4ac7b4337e8328923897c4',   # collaudo: collaudo/risultati/057
    '058': '47f53668d8b5861956938cd041fb892e541b86031e4ac7b4337e8328923897c4',   # = 0.57 (solo registri e controlli)
    '059': 'aee694c2535ab1524e08e2cd4447cefc16afddd10211ba4fe0fa35b64a45ec1d',   # collaudo: collaudo/risultati/059
    '060': 'd9ca40b361d02c0404b5d6553dc8d45252087d8bebf59e4e42c942a5786b183a',   # collaudo: collaudo/risultati/060
    '061': 'f3e7802535125bdc473bd328e4cf7f2b7aeb030f71a1fabb81675614acd63cbe',   # collaudo: collaudo/risultati/061
    '062': 'b8ebd0918981becb7c3d77c649d78bf92e7a29d5ec8eec14def17dd772ac9080',   # collaudo: collaudo/risultati/062
    '063': 'd1fee9f903b1fb6dbc0b9568697b469080f3d356dedc63a9bbf9326b0c876187',   # collaudo: collaudo/risultati/063
    '064': '82ac35d2135894815f412ca51666f31f900e5ab778b1d8838c46bb1bbda27f70',   # collaudo: collaudo/risultati/064
    '065': 'ad1bfa2d6eec44389edbb35a5e802dfe49fb7ede7aa3f5fc1ced63f9baa69a94',   # collaudo: collaudo/risultati/065
    '066': 'd794870a35a619553550d0913395fb5d900e122d50085bc4ec6cab5276b74f84',   # collaudo: collaudo/risultati/066
}
# Versioni costruite sopra la 0.55: (numero, modulo in versioni/). Ogni nuova versione aggiunge una riga
# e il suo SHA atteso in SHA (dopo averla collaudata). Il modulo espone apply(W) -> dict (rapporto).
VERSIONI = [('056', 'v056_cesena_rivale'), ('057', 'v057_spazio'), ('058', 'v058_registri'), ('059', 'v059_cani'), ('060', 'v060_kyogre_uccelli'), ('061', 'v061_regi_mitici'), ('062', 'v062_strumenti'), ('063', 'v063_cesena_ovest'), ('064', 'v064_campagna_cesenate'), ('065', 'v065_ridracoli'), ('066', 'v066_fumaiolo'), ('067', 'v067_treno')]


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
    risorse = dict(spazio_libero=W.libere(),
                   flag_pool_restanti=len(engine.POOL.restanti()) if engine.POOL else None,
                   variabili_restanti=len(engine.VARS.rest) if engine.VARS else None,
                   usate=dict(flag=[f for f, _ in engine.POOL.taken] if engine.POOL else [],
                              variabili=[v for v, _ in engine.VARS.taken] if engine.VARS else []))
    json.dump(dict(rapporto=rapporto, script=W.scripts_log, flag=engine.POOL.taken if engine.POOL else [],
                   variabili=engine.VARS.taken if engine.VARS else [], risorse=risorse),
              open(OUT / 'rapporto_build.json', 'w'), ensure_ascii=False, indent=1, default=str)
    return bytes(W.d), VERSIONI[-1][0], risorse, (engine.POOL.taken if engine.POOL else [])


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
    final, ver, risorse, presi = tappe_versioni(r055)
    if not a.senza_registri:
        print('[4] registri')
        sys.path.insert(0, str(ROOT / 'registri'))
        import genera
        genera.main(OUT / nome(ver), ROOT / 'registri', strict=True)
        print('[5] controlli: allenatori, raggiungibilita, risorse e budget')
        import controlli
        budget = controlli.main(OUT / nome(ver), ROOT / 'registri', presi, risorse, strict=True)
        rj = json.load(open(OUT / 'rapporto_build.json')); rj['budget'] = budget
        json.dump(rj, open(OUT / 'rapporto_build.json', 'w'), ensure_ascii=False, indent=1, default=str)
    print('fatto: out/' + nome(ver))


if __name__ == '__main__': main()
