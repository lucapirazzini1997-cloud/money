#!/usr/bin/env python3
"""Regressione: la stessa partita di prova su una ROM, con tabella dei risultati (Lotto 1, dalla 0.58).

Partenze:
  - mGBA: ogni savestate di collaudo/play/ (solo mGBA li legge);
  - mGBA e VBA-M: un salvataggio vero, fatto in gioco (menu -> SALVA) sulla ROM in prova partendo dal savestate
    t56_reload, poi titolo -> Continua.
Su ogni partenza lo stesso programma di tasti: passeggiata, menu, Pokedex, squadra e riassunto, borsa e seconda
tasca, passeggiata di ritorno. Solo tasti: nessuna scrittura in RAM.

Esiti per partenza:
  gira        l'emulatore risponde fino alla fine;
  vivo        lo schermo cambia fra i punti di controllo e l'ultimo non e' di un solo colore;
  callback    la callback principale del gioco (0x030022C4) punta sempre nella ROM;
  rif         (con --rif) punti di controllo uguali alla ROM di riferimento: schermo, EWRAM, IWRAM (tolto
              l'orologio), VRAM, tavolozze, OAM. Per una versione che cambia il gioco le differenze sono attese
              dove cambia; per una che non lo cambia devono essere zero.
L'orologio: in mGBA e' fisso (./h usa un RTC finto); VBA-M usa l'ora vera, per questo sRtc e gLocalTime non
entrano nei confronti.

Uso: python3 collaudo/regressione.py ROM.gba [--rif ROM_RIF.gba] [--uscita CARTELLA] [--solo-mgba]
Scrive CARTELLA/regressione.md (tabella) e CARTELLA/regressione.json.
"""
import sys, os, json, hashlib, shutil, argparse
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path[:0] = [HERE]
import drv
from drv import A, B, START, U, D, L, R

OROLOGIO = [(0x03000dc0, 0xc), (0x03005cf8, 0x8)]           # sRtc, gLocalTime
REGIONS = [('EWRAM', 0x02000000, 0x40000), ('IWRAM', 0x03000000, 0x8000), ('VRAM', 0x06000000, 0x18000),
           ('PAL', 0x05000000, 0x400), ('OAM', 0x07000000, 0x400)]
PROGRAMMA = [('cammina', 'BBBB' + 'UUUULLLLDDDDRRRR' + '..'),
             ('menu', 'T.'),
             ('pokedex', 'A..'),
             ('squadra', 'BB.' + 'TDA..'),
             ('riassunto', 'AA..'),
             ('borsa', 'BBBB.' + 'TDDA..'),
             ('tasca2', 'R.'),
             ('ritorno', 'BBBB..' + 'RRRRDDDDLLLLUUUU' + '...')]
CONTINUA = '......' + 'T...' + 'A...' + 'A' + '.' * 6 + 'A..' + '.' * 4
SALVA = 'BBBB' + 'T.' + 'DDDD' + 'A..' + 'A' + '.' * 6 + 'A..' + '.' * 6      # menu -> SALVA -> si -> sovrascrivi


def emu(rom, sav, vbam):
    if vbam: os.environ['VBAM'] = '1'
    else: os.environ.pop('VBAM', None)
    e = drv.Emu(rom, sav); e.run(10); return e


def keys(e, seq):
    for ch in seq:
        if ch in 'UDLR': e.key(dict(U=U, D=D, L=L, R=R)[ch], 16, 3)
        elif ch == 'A': e.key(A, 3, 40)
        elif ch == 'B': e.key(B, 3, 30)
        elif ch == 'T': e.key(START, 3, 40)
        elif ch == '.': e.run(60)


def checkpoint(e, out, tag):
    e.shot(os.path.join(out, tag), 1)
    raw = open(os.path.join(out, tag + '.ppm'), 'rb').read(); os.remove(os.path.join(out, tag + '.ppm'))
    px = raw[raw.index(b'255\n') + 4:]
    h = dict(schermo=hashlib.sha1(raw).hexdigest()[:12], colori=len({px[i:i + 3] for i in range(0, len(px), 3 * 97)}),
             callback=e.r('r32', 0x030022c4))
    for name, a, n in REGIONS:
        b = bytearray(e.ram(a, n))
        if name == 'IWRAM':
            for s, l in OROLOGIO: b[s - a:s - a + l] = bytes(l)
        h[name] = hashlib.sha1(bytes(b)).hexdigest()[:12]
    return h


def partita(e, out, tag, avvio=None):
    res = {}
    if avvio: keys(e, avvio); res['avvio'] = checkpoint(e, out, tag + '_avvio')
    for name, seq in PROGRAMMA:
        keys(e, seq); res[name] = checkpoint(e, out, '%s_%s' % (tag, name))
    return res


def esiti(res):
    pts = list(res.values())
    return dict(vivo=len({p['schermo'] for p in pts}) > 1 and pts[-1]['colori'] > 1,
                callback=all(0x08000000 <= p['callback'] < 0x0a000000 for p in pts))


def fai_salvataggio(rom, out):
    sav = os.path.join(out, 'partita.sav')
    with open(sav, 'wb') as f: f.write(b'\xff' * 0x20000)
    e = emu(rom, sav, False); e.load(os.path.join(HERE, 'play', 't56_reload.ss')); e.run(120)
    keys(e, SALVA); e.shot(os.path.join(out, 'salvataggio'), 1); e.sync(); e.close()
    return sav


def giro(rom, out, tag, solo_mgba):
    """Tutte le partenze su una ROM -> {partenza: {punto: hash}}"""
    ris = {}
    for st in sorted(f for f in os.listdir(os.path.join(HERE, 'play')) if f.endswith('.ss')):
        e = emu(rom, None, False); e.load(os.path.join(HERE, 'play', st)); e.run(120)
        ris['mGBA ' + st[:-3]] = partita(e, out, '%s_m_%s' % (tag, st[:-3])); e.close()
    sav = fai_salvataggio(rom, out)
    for vb, en in ((False, 'mGBA'), (True, 'VBA-M')):
        if vb and solo_mgba: continue
        s2 = os.path.join(out, 'tmp.sav'); shutil.copy(sav, s2)
        e = emu(rom, s2, vb)
        ris[en + ' salvataggio'] = partita(e, out, '%s_%s_sav' % (tag, en), avvio=CONTINUA); e.close()
    return ris


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('rom'); ap.add_argument('--rif'); ap.add_argument('--uscita', default=os.path.join(HERE, 'out_regressione'))
    ap.add_argument('--solo-mgba', action='store_true')
    a = ap.parse_args()
    out = os.path.abspath(a.uscita); os.makedirs(out, exist_ok=True)
    rom = os.path.abspath(a.rom); a.rif = os.path.abspath(a.rif) if a.rif else None
    os.chdir(HERE)                     # drv lancia ./h da qui
    prova = giro(rom, out, 'prova', a.solo_mgba)
    rif = giro(os.path.abspath(a.rif), out, 'rif', a.solo_mgba) if a.rif else None
    righe = []; tutto_ok = True
    for p, res in prova.items():
        es = esiti(res); ok = es['vivo'] and es['callback']
        conf = ''
        if rif:
            diff = ['%s.%s' % (pt, k) for pt in res for k in ('schermo',) + tuple(r[0] for r in REGIONS)
                    if res[pt][k] != rif[p][pt][k]]
            conf = 'uguale' if not diff else 'diverso: ' + ', '.join(diff[:5]) + (' ...' if len(diff) > 5 else '')
        tutto_ok &= ok
        righe.append((p, 'si', 'si' if es['vivo'] else 'NO', 'si' if es['callback'] else 'NO', conf))
    with open(os.path.join(out, 'regressione.md'), 'w') as f:
        f.write('ROM: `%s` (SHA-256 %s)\n\n' % (os.path.basename(rom), hashlib.sha256(open(rom, 'rb').read()).hexdigest()))
        if rif: f.write('Riferimento: `%s` (SHA-256 %s)\n\n' % (os.path.basename(a.rif), hashlib.sha256(open(a.rif, 'rb').read()).hexdigest()))
        f.write('| Partenza | Gira | Vivo | Callback nella ROM |%s\n|---|---|---|---|%s\n' % (' Rispetto al riferimento |' if rif else '', '---|' if rif else ''))
        for r in righe: f.write('| ' + ' | '.join(r[:4] + ((r[4],) if rif else ())) + ' |\n')
    json.dump(dict(prova=prova, rif=rif), open(os.path.join(out, 'regressione.json'), 'w'), indent=1)
    print(open(os.path.join(out, 'regressione.md')).read())
    print('REGRESSIONE:', 'ok' if tutto_ok else 'PROBLEMI')
    return 0 if tutto_ok else 1


if __name__ == '__main__':
    sys.exit(main())
