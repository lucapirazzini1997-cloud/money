#!/usr/bin/env python3
"""Prova negativa dei controlli di build della 0.58 (registri/controlli.py): devono far fallire la build.

Su copie della ROM (non tocca out/ ne' registri/):
  1. allenatore con numero riservato: una lotta esistente in una mappa raggiungibile viene cambiata in una lotta
     con l'allenatore 682 (la sua flag 0x7aa e' presa dal pool: 'codici primo')  -> deve fallire;
  2. dono irraggiungibile: tutte le uscite che portano alla mappa 34.8 (dono di Bulbasaur, Charmander, Squirtle) vengono girate
     altrove                                                                   -> deve fallire;
  3. la ROM vera passa (controllo di partenza).
Uso: python3 collaudo/test_controlli.py ROM_0_58.gba
"""
import sys, os, json, shutil, tempfile, struct
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / 'registri'), str(ROOT / 'strumenti_rom'), str(ROOT / 'versioni'), str(ROOT / 'analisi')]
import romlib, controlli as C, raggiungibili as RG

B = 0x08000000


def run(rom_bytes, tmp, presi):
    p = Path(tmp) / 'prova.gba'; p.write_bytes(rom_bytes)
    reg = Path(tmp) / 'registri'
    if reg.exists(): shutil.rmtree(reg)
    shutil.copytree(ROOT / 'registri', reg, ignore=shutil.ignore_patterns('__pycache__', '*.py'))
    R = romlib.Rom(bytes(rom_bytes)); ev = C.eventi(R)
    esiti = {}
    for nome, f in (('allenatori', lambda: C.allenatori(R, ev, presi, reg, True)),
                    ('raggiungibilita', lambda: C.raggiungibilita(R, ev, reg, True))):
        try: f(); esiti[nome] = 'passa'
        except SystemExit as e: esiti[nome] = 'FALLISCE: %s' % e
    return esiti


def main():
    rom = Path(sys.argv[1]).read_bytes()
    presi = json.load(open(ROOT / 'out' / 'rapporto_build.json'))['flag']
    R = romlib.Rom(rom); maps, E, seen = RG.reachable(R)
    ris = {}
    with tempfile.TemporaryDirectory() as tmp:
        ris['ROM vera'] = run(rom, tmp, presi)
        # 1. una lotta in una mappa raggiungibile diventa l'allenatore 682
        ev = C.eventi(R); d = bytearray(rom); fatto = None
        for k, acc in sorted(ev.items()):
            if k not in seen or not acc['allenatori']: continue
            t = sorted(acc['allenatori'])[0]
            i = bytes(d).find(b'\x5c\x00' + struct.pack('<H', t))
            if i > 0: d[i + 2:i + 4] = struct.pack('<H', 682); fatto = (k, t, hex(i)); break
        ris['lotta con allenatore 682 (%d.%d, era %d, a %s)' % (fatto[0][0], fatto[0][1], fatto[1], fatto[2])] = run(bytes(d), tmp, presi)
        # 2. il laboratorio 34.8 diventa irraggiungibile
        d = bytearray(rom); girate = 0
        for k, m in maps.items():
            wp = R.ptr(m['events'] + 8)                       # tabella delle uscite (8 byte l'una)
            for i, w in enumerate(m['warps']):
                if (w['group'], w['num']) == (34, 8):
                    d[wp + i * 8 + 6] = 9; girate += 1       # verso 34.9 invece di 34.8
        entra = sorted('%d.%d %s' % (k[0], k[1], h) for k, es in E.items() for t, h in es.items() if t == (34, 8))
        print('  entrate in 34.8 nel grafo:', entra)
        ris['uscite verso 34.8 girate (%d)' % girate] = run(bytes(d), tmp, presi) if girate else {'raggiungibilita': 'non provato'}
    for k, v in ris.items(): print('%-60s %s' % (k, v))
    ok = (ris['ROM vera'] == {'allenatori': 'passa', 'raggiungibilita': 'passa'}
          and all('FALLISCE' in v.get('allenatori', '') for k, v in ris.items() if k.startswith('lotta'))
          and all('FALLISCE' in v.get('raggiungibilita', '') for k, v in ris.items() if k.startswith('uscite')))
    print('PROVA NEGATIVA:', 'ok' if ok else 'NON OK')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
