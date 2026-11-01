"""Controlli di build del Lotto 1 (dalla 0.58): allenatori, raggiungibilita', risorse libere e budget.

Si lanciano dopo genera.py (che produce flag.json e variabili.json) e possono far fallire la build.

1. Allenatori (registri/allenatori.json). Ogni numero 1-0x35F (la flag 0x500+numero deve stare sotto le flag
   di sistema 0x860) e':
     usato       - c'e' una lotta (trainerbattle) con quel numero in uno script di una mappa;
     forse usato - solo la scansione grezza di tutta la ROM trova una sequenza simile a una lotta (spesso byte
                   di puntatori): non e' un conflitto, ma il numero non va nel pool;
     riservato   - la sua flag 0x500+numero e' presa dal pool dell'engine, o usata da script come flag normale;
     Smeraldo    - il numero e' citato dal codice C di Smeraldo (tabella delle rivincite, Lotta Frontier...);
     libero      - nessuna delle tre.
   Conflitto = un allenatore usato in lotta la cui flag e' anche presa dal pool, oppure impostata da uno script
   di una mappa dove quell'allenatore non combatte. I conflitti gia' noti sono in allenatori_ammessi.json con
   il motivo; uno nuovo fa fallire la build. Un conflitto puo' essere ammesso solo finche' certe mappe restano
   irraggiungibili anche a piedi (analisi/cammino.py): se una versione le collega, la build fallisce.

2. Raggiungibilita' (registri/raggiungibilita.json), con analisi/raggiungibili.py (uscite, connessioni, SUB,
   warp degli script, Volo). Fallisce se non si raggiunge:
     - una mappa con un dono (givemon, giveegg) o un leggendario (setwildbattle con una specie leggendaria);
     - una mappa nuova (non presente in mappe_base.json, l'elenco delle mappe della 0.57).
   Le eccezioni gia' note sono in irraggiungibili_ammesse.json con il motivo.
   Avvisi (non fanno fallire): mappe importanti raggiungibili nel grafo ma non a piedi (analisi/cammino.py).

3. Risorse libere (registri/risorse_libere.json): flag 0x20-0x4FF e variabili sicure (analisi/flag_sicure.py),
   e budget: spazio, flag del pool, variabili, strumenti, allenatori.
"""
import sys, json, re, struct, collections
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(ROOT / 'strumenti_rom'), str(ROOT / 'versioni'), str(ROOT / 'analisi')]
import romlib, scr, flagscan52

B = 0x08000000
MAX_TRAINER = 0x35f
# specie leggendarie (numeri interni di Smeraldo): uccelli, Mewtwo, Mew, cani, Lugia, Ho-Oh, Celebi,
# Regirock, Regice, Registeel, Kyogre, Groudon, Rayquaza, Latias, Latios, Jirachi, Deoxys
LEGGENDARI = {144, 145, 146, 150, 151, 243, 244, 245, 249, 250, 251,
              401, 402, 403, 404, 405, 406, 407, 408, 409, 410}


def _walk(d, p, acc, seen, depth=0):
    if p is None or p in seen or not (0 <= p < len(d)) or depth > 20: return
    seen.add(p)
    try: ins, _ = scr.decode(d, p, 600, follow=False)
    except Exception: return
    for a, nm, ar in ins:
        op = d[a]
        if op in (4, 5, 6, 7) and ar and B <= ar[-1] < B + len(d): _walk(d, ar[-1] - B, acc, seen, depth + 1)
        if op == 0x5c:
            acc['allenatori'].add(ar[1])
            for x in ar[3:]:
                if isinstance(x, int) and B <= x < B + len(d): _walk(d, x - B, acc, seen, depth + 1)
        if op == 0x79: acc['doni'].add(ar[0])
        if op == 0x7a: acc['uova'].add(ar[0])
        if op == 0xb6: acc['selvatici'].add(ar[0])


def eventi(R):
    """Per ogni mappa reale: allenatori in lotta, doni, uova, Pokemon selvatici fissi."""
    d = bytes(R.data); out = {}
    for g, n in flagscan52.real_maps(d):
        try: m = R.map(g, n)
        except Exception: continue
        acc = collections.defaultdict(set)
        for lab, p in flagscan52.entries(R, m): _walk(d, p, acc, set())
        out[(g, n)] = acc
    return out


def lotte_rom(d):
    """Tutte le trainerbattle della ROM (anche fuori dagli eventi di mappa), qualunque id locale."""
    out = set()
    for m in re.finditer(rb'\x5c[\x00-\x09]', d):
        i = m.start(); t = struct.unpack_from('<H', d, i + 2)[0]; p1 = struct.unpack_from('<I', d, i + 6)[0]
        if 0 < t <= MAX_TRAINER and B <= p1 < B + len(d) and (p1 & 0x80000000) == 0: out.add(t)
    return out


_A_PIEDI = {}


def a_piedi(R):
    """Mappe raggiungibili a piedi (analisi/cammino.py, ottimistico), calcolato una volta per ROM."""
    if id(R) not in _A_PIEDI:
        import cammino
        _, seen = cammino.cammina(R, [((1, 0), None), ((0, 9), None)])
        _A_PIEDI[id(R)] = {k for k, v in seen.items() if v}
    return _A_PIEDI[id(R)]


def allenatori(R, ev, pool_taken, outdir, strict):
    d = bytes(R.data)
    fl = json.load(open(outdir / 'flag.json'))
    sm = json.load(open(outdir / 'flag_smeraldo.json')).get('allenatori', {})
    dove = collections.defaultdict(set)
    for k, acc in ev.items():
        for t in acc['allenatori']: dove[t].add('%d.%d' % k)
    sparse = lotte_rom(d) - set(dove)       # lotte trovate solo dalla scansione grezza
    pool = {int(f, 16) - 0x500: why for f, why in pool_taken if 0x500 <= int(f, 16) < 0x860}
    reg = {}; conflitti = {}
    for t in range(1, MAX_TRAINER + 1):
        f = hex(0x500 + t); rec = fl.get(f, {})
        script_maps = {s.split(' ')[0] for k in ('imposta', 'azzera', 'oggetto') for s in rec.get(k, [])}
        if t in sparse and t not in dove:
            # solo la scansione grezza: spesso sono byte di puntatori (5c 09 = 0x095c....). Non e' un conflitto,
            # ma il numero resta fuori dal pool (v058_registri) per prudenza.
            stato = dict(stato='forse usato', motivo='sequenza simile a una lotta fuori dagli eventi di mappa')
        elif t in dove:
            stato = dict(stato='usato', mappe=sorted(dove[t]))
            c = []
            if t in pool: c.append('flag presa dal pool: %s' % pool[t])
            estranee = script_maps - dove.get(t, set())
            if estranee: c.append('flag usata da script di altre mappe: %s' % ', '.join(sorted(estranee)))
            if c: conflitti[str(t)] = c
        elif t in pool: stato = dict(stato='riservato', motivo='flag %s presa dal pool: %s' % (f, pool[t]))
        elif rec: stato = dict(stato='riservato', motivo='flag %s usata da script (%s)' % (f, ', '.join(sorted(script_maps))))
        elif str(t) in sm: stato = dict(stato='Smeraldo', motivo=sm[str(t)][0])
        else: stato = dict(stato='libero')
        reg[t] = stato
    amm_p = outdir / 'allenatori_ammessi.json'
    amm = json.load(open(amm_p)) if amm_p.exists() else {}
    nuovi = {t: c for t, c in conflitti.items() if t not in amm}
    # un conflitto ammesso puo' valere solo finche' certe mappe restano irraggiungibili anche a piedi
    # (analisi/cammino.py, ottimistico): se una versione le collega, il conflitto torna un errore
    cond = {t: v['finche_irraggiungibili_a_piedi'] for t, v in amm.items()
            if isinstance(v, dict) and v.get('finche_irraggiungibili_a_piedi') and t in conflitti}
    if cond:
        seen = a_piedi(R)
        for t, mappe in cond.items():
            aperte = [k for k in mappe if tuple(map(int, k.split('.'))) in seen]
            if aperte: nuovi[t] = conflitti[t] + ['la mappa %s ora si raggiunge a piedi' % ', '.join(aperte)]
            else: print('  allenatore %s: conflitto latente, %s ancora irraggiungibile a piedi' % (t, ', '.join(mappe)))
    conta = collections.Counter(v['stato'] for v in reg.values())
    json.dump(dict(conteggi=conta, conflitti=conflitti, registro={str(k): v for k, v in reg.items()}),
              open(outdir / 'allenatori.json', 'w'), ensure_ascii=False, indent=1)
    print('  allenatori: %s; conflitti %d (nuovi %d)' % (dict(conta), len(conflitti), len(nuovi)))
    if nuovi:
        for t, c in nuovi.items(): print('    NUOVO CONFLITTO allenatore %s: %s' % (t, '; '.join(c)))
        if strict: raise SystemExit('build fallita: allenatore con flag riservata (vedi registri/allenatori.json)')
    return reg, conta


def raggiungibilita(R, ev, outdir, strict):
    import raggiungibili as RG
    maps, E, seen = RG.reachable(R)
    base_p = outdir / 'mappe_base.json'
    base = set(json.load(open(base_p))) if base_p.exists() else None
    amm_p = outdir / 'irraggiungibili_ammesse.json'
    amm = json.load(open(amm_p)) if amm_p.exists() else {}
    importanti = {}
    for k, acc in ev.items():
        legs = acc['selvatici'] & LEGGENDARI
        if acc['doni'] or acc['uova'] or legs:
            importanti['%d.%d' % k] = dict(doni=sorted(acc['doni']), uova=sorted(acc['uova']), leggendari=sorted(legs))
    keys = {'%d.%d' % k for k in maps}
    raggiunte = {'%d.%d' % k: v for k, v in seen.items()}
    nuove = sorted(keys - base) if base is not None else []
    problemi = {}
    for k in sorted(keys - set(raggiunte)):
        why = []
        if k in importanti: why.append('contiene %s' % importanti[k])
        if k in nuove: why.append('mappa nuova')
        if why and k not in amm: problemi[k] = why
    # avvisi (non fanno fallire): mappe importanti che il grafo raggiunge ma a piedi no, nemmeno in modo
    # ottimistico (il cammino non conta il Volo): il dono o il leggendario in pratica potrebbe non esserci
    piedi = {'%d.%d' % k for k in a_piedi(R)}
    avvisi = {k: importanti[k] for k in importanti if k in raggiunte and k not in piedi}
    for k, v in avvisi.items(): print('    avviso: %s %s raggiungibile nel grafo ma non a piedi' % (k, v))
    json.dump(dict(mappe=len(keys), raggiunte=len(raggiunte), a_piedi=len(piedi), importanti=importanti,
                   non_raggiunte=sorted(keys - set(raggiunte)), solo_nel_grafo=sorted(set(raggiunte) - piedi),
                   avvisi=avvisi, ammesse=amm, nuove=nuove, problemi=problemi),
              open(outdir / 'raggiungibilita.json', 'w'), ensure_ascii=False, indent=1)
    print('  raggiungibilita: %d mappe, %d raggiunte; importanti %d (non raggiunte e ammesse: %d); nuove %d; problemi %d'
          % (len(keys), len(raggiunte), len(importanti), len([k for k in importanti if k not in raggiunte]), len(nuove), len(problemi)))
    if problemi:
        for k, w in problemi.items(): print('    NON RAGGIUNGIBILE %s: %s' % (k, '; '.join(w)))
        if strict: raise SystemExit('build fallita: mappa importante o nuova non raggiungibile (registri/raggiungibilita.json)')
    if base is None: json.dump(sorted(keys, key=lambda s: tuple(map(int, s.split('.')))), open(base_p, 'w'))


def risorse(rom, W_info, reg_allenatori, outdir):
    import flag_sicure
    fs = flag_sicure.classify(rom); vs = flag_sicure.classify_vars(rom)
    usate = W_info.get('usate', {})
    flag_libere = [f for f in fs['sicure'] if f not in usate.get('flag', [])]
    var_libere = [v for v in vs['sicure'] if v not in usate.get('variabili', [])]
    strum = json.load(open(outdir / 'strumenti.json'))
    budget = dict(
        spazio_kb=W_info.get('spazio_libero', 0) // 1024,
        flag_pool=W_info.get('flag_pool_restanti'),
        flag_0x20_0x4ff_sicure=len(flag_libere),
        variabili_sicure=len(var_libere),
        strumenti_liberi=len(strum['liberi']),
        allenatori_liberi=reg_allenatori['libero'])
    json.dump(dict(budget=budget, flag_sicure=flag_libere, variabili_sicure=var_libere,
                   flag_escluse=fs['escluse'], variabili_escluse=vs['escluse'],
                   chiamate_flag_non_calcolabili=fs['chiamate_non_calcolabili'], fonte=fs['fonte_smeraldo']),
              open(outdir / 'risorse_libere.json', 'w'), ensure_ascii=False, indent=1)
    print('  budget:', budget)
    return budget


def main(rom, outdir, pool_taken=(), W_info=None, strict=True):
    outdir = Path(outdir); R = romlib.Rom(str(rom))
    ev = eventi(R)
    reg, conta = allenatori(R, ev, list(pool_taken), outdir, strict)
    raggiungibilita(R, ev, outdir, strict)
    return risorse(rom, W_info or {}, conta, outdir)


if __name__ == '__main__':
    rj = json.load(open(ROOT / 'out' / 'rapporto_build.json')) if (ROOT / 'out' / 'rapporto_build.json').exists() else {}
    main(sys.argv[1], HERE, rj.get('flag', []), rj.get('risorse', {}), strict='--rigoroso' in sys.argv)
