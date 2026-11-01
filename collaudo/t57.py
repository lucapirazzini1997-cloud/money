#!/usr/bin/env python3
"""Collaudo della 0.57 (spazio recuperato): la 0.57 deve giocare esattamente come la 0.56.

Prova a passo identico: le stesse pressioni di tasti su tre ROM
  - 0.56 (riferimento),
  - 0.57,
  - 0.57 'avvelenata': le zone recuperate riempite di byte casuali invece di 0xFF.
A ogni punto di controllo si confrontano lo schermo e la memoria (EWRAM, IWRAM, VRAM, tavolozze, OAM).
Se qualcosa nel gioco leggesse una zona recuperata, la ROM avvelenata divergerebbe.

Partenze:
  - mGBA: i savestate di collaudo/play (solo mGBA li legge);
  - mGBA e VBA-M: un salvataggio vero (.sav) fatto in gioco col menu SALVA dalla 0.56, poi Continua.
Nessuna scrittura in RAM: solo tasti. In mGBA l'orologio del gioco e' fisso (./h usa un RTC finto e ripetibile);
VBA-M usa l'ora vera, per questo i 20 byte di sRtc e gLocalTime non entrano nel confronto (OROLOGIO).

Uso: python3 collaudo/t57.py [cartella_uscita] [--parte=stati|salvataggio|tutto]
"""
import sys, os, json, hashlib, random, shutil, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path[:0] = [HERE, os.path.join(ROOT, 'versioni'), os.path.join(ROOT, 'strumenti_rom')]
os.chdir(HERE)
import drv
from drv import A, B, START, U, D, L, R
from v057_spazio import ZONE_057

ARGS = [a for a in sys.argv[1:] if not a.startswith('--')]
PARTE = ([a[8:] for a in sys.argv[1:] if a.startswith('--parte=')] or ['tutto'])[0]   # stati | salvataggio | tutto
OUT = os.path.abspath(ARGS[0] if ARGS else os.path.join(HERE, 'out57'))
os.makedirs(OUT, exist_ok=True)
ROM56 = os.path.join(ROOT, 'out', 'Pokemon_Romagna_0_56.gba')
ROM57 = os.path.join(ROOT, 'out', 'Pokemon_Romagna_0_57.gba')
POISON = os.path.join(OUT, 'Pokemon_Romagna_0_57_avvelenata.gba')
# Orologio: VBA-M legge l'ora vera del computer, quindi i secondi cambiano da una prova all'altra anche con la
# stessa ROM. Si escludono dal confronto solo sRtc e gLocalTime (simboli di pokeemerald, stessa IWRAM).
OROLOGIO = [(0x03000dc0, 0xc), (0x03005cf8, 0x8)]
REGIONS = [('EWRAM', 0x02000000, 0x40000), ('IWRAM', 0x03000000, 0x8000), ('VRAM', 0x06000000, 0x18000),
           ('PAL', 0x05000000, 0x400), ('OAM', 0x07000000, 0x400)]


def make_poison():
    d = bytearray(open(ROM57, 'rb').read()); rnd = random.Random(57)
    for s, e in ZONE_057:
        assert all(b == 0xff for b in d[s:e])
        d[s:e] = bytes(rnd.getrandbits(8) for _ in range(e - s))
    open(POISON, 'wb').write(d)


def emu(rom, sav, vbam):
    if vbam: os.environ['VBAM'] = '1'
    else: os.environ.pop('VBAM', None)
    e = drv.Emu(rom, sav); e.run(10); return e


def checkpoint(e, tag):
    e.shot(os.path.join(OUT, tag), 1)
    h = {'schermo': hashlib.sha1(open(os.path.join(OUT, tag + '.ppm'), 'rb').read()).hexdigest()[:12]}
    os.remove(os.path.join(OUT, tag + '.ppm'))
    for name, a, n in REGIONS:
        b = bytearray(e.ram(a, n))
        if name == 'IWRAM':
            for s, l in OROLOGIO: b[s - a:s - a + l] = bytes(l)
        h[name] = hashlib.sha1(bytes(b)).hexdigest()[:12]
    return h


def keys(e, seq):
    """seq: lettere U D L R (passo), A B T (start), '.' (attesa 60 frame)."""
    for ch in seq:
        if ch in 'UDLR': e.key(dict(U=U, D=D, L=L, R=R)[ch], 16, 3)
        elif ch == 'A': e.key(A, 3, 40)
        elif ch == 'B': e.key(B, 3, 30)
        elif ch == 'T': e.key(START, 3, 40)
        elif ch == '.': e.run(60)


# programma uguale per tutte le partenze: passeggiata, menu (Pokedex, squadra e riassunto, borsa), passeggiata
PROGRAMMA = [('cammina', 'BBBB' + 'UUUULLLLDDDDRRRR' + '..'),
             ('menu', 'T.'),
             ('pokedex', 'A..'),
             ('squadra', 'BB.' + 'TDA..'),
             ('riassunto', 'AA..'),
             ('borsa', 'BBBB.' + 'TDDA..'),
             ('tasca2', 'R.'),
             ('ritorno', 'BBBB..' + 'RRRRDDDDLLLLUUUU' + '...')]


def play(e, tag):
    res = {}
    for name, seq in PROGRAMMA:
        keys(e, seq); res[name] = checkpoint(e, '%s_%s' % (tag, name))
    return res


def make_sav():
    """Salvataggio vero dalla 0.56: savestate t56_reload, menu -> SALVA -> si (solo tasti)."""
    sav = os.path.join(OUT, 'partita57.sav')
    with open(sav, 'wb') as f: f.write(b'\xff' * 0x20000)
    e = emu(ROM56, sav, False); e.load(os.path.join(HERE, 'play', 't56_reload.ss')); e.run(120)
    keys(e, 'BBBB')
    # il cursore del menu ricorda l'ultima voce: si scende fino a SALVA guardando lo schermo, quindi si cerca
    # la voce dal testo della finestra; qui basta la sequenza fissa verificata a mano con gli screenshot.
    keys(e, 'T.' + 'DDDD' + 'A..' + 'A' + '.' * 6 + 'A..' + '.' * 6)
    e.shot(os.path.join(OUT, 'salvataggio'), 1); e.sync(); e.close()
    return sav


def main():
    if not os.path.exists(POISON): make_poison()
    roms = [('056', ROM56), ('057', ROM57), ('057avv', POISON)]
    rj = os.path.join(OUT, 'risultati.json')
    risultati = json.load(open(rj)) if os.path.exists(rj) and PARTE != 'tutto' else {}
    stati = sorted(f for f in os.listdir(os.path.join(HERE, 'play')) if f.endswith('.ss')) if PARTE in ('tutto', 'stati') else []
    for st in stati:
        for tag, rom in roms:
            e = emu(rom, None, False); e.load(os.path.join(HERE, 'play', st)); e.run(120)
            risultati['mGBA %s %s' % (st[:-3], tag)] = play(e, 'm_%s_%s' % (st[:-3], tag)); e.close()
        # ripetibilita': la 0.56 una seconda volta
        e = emu(ROM56, None, False); e.load(os.path.join(HERE, 'play', st)); e.run(120)
        risultati['mGBA %s 056bis' % st[:-3]] = play(e, 'm_%s_056bis' % st[:-3]); e.close()
        print(st, flush=True)
    sav = os.path.join(OUT, 'partita57.sav')
    if PARTE in ('tutto', 'salvataggio') and (PARTE == 'tutto' or not os.path.exists(sav)): sav = make_sav()
    for vb, en in ((False, 'mGBA'), (True, 'VBA-M')) if PARTE in ('tutto', 'salvataggio') else ():
        for tag, rom in roms + [('056bis', ROM56)]:
            s2 = os.path.join(OUT, 'tmp.sav'); shutil.copy(sav, s2)
            e = emu(rom, s2, vb)
            keys(e, '......' + 'T...' + 'A...' + 'A' + '.' * 6 + 'A..' + '.' * 4)   # titolo -> Continua
            risultati['%s salvataggio %s' % (en, tag)] = dict(avvio=checkpoint(e, '%s_sav_%s_avvio' % (en, tag)),
                                                              **play(e, '%s_sav_%s' % (en, tag)))
            if getattr(e, 'junk', None): risultati['%s salvataggio %s' % (en, tag)]['righe_scartate'] = e.junk[:5]
            e.close()
        print(en, 'salvataggio', flush=True)
    json.dump(risultati, open(os.path.join(OUT, 'risultati.json'), 'w'), indent=1)
    # confronto
    righe = []; tutto_ok = True
    partenze = sorted({k.rsplit(' ', 1)[0] for k in risultati})
    for p in partenze:
        ref = risultati[p + ' 056']
        for tag in ('056bis', '057', '057avv'):
            r = risultati[p + ' ' + tag]
            diff = ['%s.%s' % (pt, reg) for pt in ref if isinstance(ref[pt], dict) for reg in ref[pt] if ref[pt][reg] != r[pt][reg]]
            ok = not diff; tutto_ok &= ok
            righe.append((p, tag, 'uguale' if ok else 'DIVERSO: ' + ', '.join(diff[:6])))
    with open(os.path.join(OUT, 'confronto.md'), 'w') as f:
        f.write('| Partenza | ROM | Rispetto alla 0.56 |\n|---|---|---|\n')
        for p, t, s in righe: f.write('| %s | %s | %s |\n' % (p, t, s))
    print(open(os.path.join(OUT, 'confronto.md')).read())
    print('TUTTO UGUALE' if tutto_ok else 'CI SONO DIFFERENZE')
    return 0 if tutto_ok else 1


if __name__ == '__main__':
    sys.exit(main())
