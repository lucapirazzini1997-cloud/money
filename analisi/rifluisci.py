#!/usr/bin/env python3
"""Rimpaginazione dei testi vecchi a 30 caratteri e 2 righe per riquadro (proposta per la 0.70).

Si lavora sui byte: le parole restano le stesse, cambiano solo i separatori (spazio 0x00, a capo 0xFE,
riquadro nuovo 0xFB, scorrimento 0xFA). Ogni separatore e' un byte, quindi il testo nuovo non e' mai piu' lungo
del vecchio: si riscrive sul posto (i byte avanzati diventano 0xFF dopo il terminatore), senza puntatori nuovi.
Regole:
  - un cambio di riquadro dopo una frase finita (. ! ? ...) resta un cambio di riquadro (nuovo paragrafo);
    gli altri a capo e cambi di riquadro diventano spazi e il paragrafo si rimpagina;
  - cartelli: un titolo iniziale tutto in maiuscolo (almeno due parole, seguito da una parola minuscola) va su
    una riga da solo;
  - i segnaposto dei nomi ({N}) contano 7 caratteri, i codici colore 0;
  - si saltano i testi con spazi doppi, spazi accanto a un a capo o codici colore (impaginazione voluta).
Uso: python3 analisi/rifluisci.py ROM MAPPE.json USCITA.json   (MAPPE: ["g.n", ...], le mappe raggiungibili)
"""
import sys, os, json, re
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'strumenti_rom'))
sys.argv, _args = sys.argv[:2], sys.argv[2:]
import testi_lunghi as TL                     # carica la ROM di sys.argv[1]
d = TL.d
SEP = {0x00, 0xFE, 0xFB, 0xFA}
FINE = set('.!?') | {'…'}


def gettoni(p):
    """Parole (liste di byte) e separatori del testo in p; None se l'impaginazione sembra voluta."""
    parole, seps, cur, q = [], [], bytearray(), p
    while d[q] != 0xFF:
        c = d[q]
        if c in SEP:
            if not cur: return None                       # separatori di fila o in testa
            parole.append(bytes(cur)); seps.append(c); cur = bytearray(); q += 1
        elif c == 0xFD: cur += d[q:q + 2]; q += 2
        elif c == 0xFC: return None
        else: cur.append(c); q += 1
    if not cur: return None
    parole.append(bytes(cur)); return parole, seps, q - p


def larg(w):
    n, i = 0, 0
    while i < len(w):
        if w[i] == 0xFD: n += 7; i += 2
        else: n += 1; i += 1
    return n


def car(w): return ''.join('{%d}' % w[i + 1] if w[i] == 0xFD else TL.CHAR.get(w[i], '?') for i in range(len(w)) if i == 0 or w[i - 1] != 0xFD)


def titolo(parole):
    """Numero di parole del titolo iniziale tutto maiuscolo (0 se non c'e')."""
    n = 0
    for w in parole:
        s = car(w)
        if re.search(r'[a-zàèéìòù]', s): break
        n += 1
    if n >= 2 and n < len(parole) and re.match(r'[A-ZÀÈÉÌÒÙ][a-zàèéìòù]', car(parole[n])): return n
    return 0


def righe(parole, width=30):
    out, cur, lc = [], [], 0
    for w in parole:
        lw = larg(w)
        if cur and lc + 1 + lw > width: out.append(cur); cur, lc = [w], lw
        else: lc = lc + 1 + lw if cur else lw; cur.append(w)
    out.append(cur); return out


def rifluisci(p, cartello):
    g = gettoni(p)
    if not g: return None
    parole, seps, n = g
    paragrafi, cur = [], [parole[0]]
    for w, s in zip(parole[1:], seps):
        if s in (0xFB, 0xFA) and car(cur[-1])[-1:] in FINE: paragrafi.append(cur); cur = [w]
        else: cur.append(w)
    paragrafi.append(cur)
    out = bytearray(); box = 0
    for i, para in enumerate(paragrafi):
        t = titolo(para) if (cartello and i == 0) else 0
        rr = (righe(para[:t]) + righe(para[t:])) if t else righe(para)
        for j, r in enumerate(rr):
            if out: out.append(0xFB if (j == 0 or j % 2 == 0) else 0xFE)
            out += b'\x00'.join(r)
    out.append(0xFF)
    assert len(out) <= n + 1
    return bytes(out), n + 1


def riquadri(b):
    s = []; cur = []; w = bytearray()
    for c in b:
        if c in SEP or c == 0xFF:
            cur.append(bytes(w)) if c != 0x00 else None
            if c == 0x00: w.append(0); continue
            w = bytearray()
            if c in (0xFB, 0xFA, 0xFF): s.append(cur); cur = []
        else: w.append(c)
    return s


def mostra(b):
    out, box, line, i = [], [], '', 0
    while b[i] != 0xFF:
        c = b[i]
        if c == 0xFD: line += '{%d}' % b[i + 1]; i += 2; continue
        if c == 0xFE: box.append(line); line = ''
        elif c in (0xFB, 0xFA): box.append(line); out.append(box); box, line = [], ''
        else: line += TL.CHAR.get(c, '?') if c else ' '
        i += 1
    box.append(line); out.append(box); return out


if __name__ == '__main__':
    mappe = [tuple(map(int, s.split('.'))) for s in json.load(open(_args[0]))]
    visti, res, saltati = {}, [], []
    for k in mappe:
        for fonte, sp in TL.fonti(k):
            for q in TL.puntatori(sp):
                if q in visti: continue
                visti[q] = 1
                vecchio = TL.testo(q)
                if not any(len(b) > 2 or any(TL.lung(l) > 30 for l in b) for b in vecchio): continue
                r = rifluisci(q, fonte.startswith('cart'))
                if not r: saltati.append(dict(mappa='%d.%d' % k, fonte=fonte, testo=hex(q), riquadri=vecchio)); continue
                nuovo, n = r
                nb = mostra(nuovo)
                assert all(len(b) <= 2 and all(TL.lung(l) <= 30 for l in b) for b in nb), (hex(q), nb)
                res.append(dict(mappa='%d.%d' % k, fonte=fonte, testo=hex(q), lunghezza=n,
                                vecchio_hex=d[q:q + n].hex(), nuovo_hex=nuovo.hex(), prima=vecchio, dopo=nb))
    rv = sum(len(r['prima']) for r in res); rn = sum(len(r['dopo']) for r in res)
    orfani = [r for r in res if len(r['dopo']) > 1 and len(r['dopo'][-1]) == 1 and len(r['dopo'][-1][0]) <= 10]
    print('testi lunghi:', len(res) + len(saltati), 'rimpaginati:', len(res), 'saltati:', len(saltati))
    print('riquadri prima:', rv, 'dopo:', rn, '(+%.0f%%)' % (100 * (rn - rv) / max(rv, 1)))
    print('ultimo riquadro con una sola parola corta:', len(orfani))
    json.dump(dict(testi=res, saltati=saltati), open(_args[1], 'w'), indent=1, ensure_ascii=False)
