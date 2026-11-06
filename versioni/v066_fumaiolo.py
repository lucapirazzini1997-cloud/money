"""Versione 0.66 - Lotto 3: il nuovo FUMAIOLO (Sentiero 35.10 e interno 35.12-35.18), dalle bozze approvate
(bozze/fumaiolo.py e bozze/santuario.py; il disegno e' copiato qui e congelato).

Sentiero del Fumaiolo (35.10): da 56x52 a 40x100. Si entra dal basso, da Cesena, e si risale il SAVIO:
prati con l'erba alta e l'altopiano, cascata e ponte di tronchi, a ovest il colle dell'EREMO DI SANT'ALBERICO
con la grotta (ingresso del santuario, chiusa dal masso di FORZA), il RIFUGIO a est, il lago con gli scogli,
il ponte lungo e la seconda cascata; in cima, a ovest, la sorgente del TEVERE con la stele.
Pezzi del Percorso 119 rimescolati (senza pontili e istituto), colle del Percorso 120, stele = pilastro della
vetta del Monte Pira.
Interno: 35.12 Grotta dell'Eremo e 35.13 Grotta delle Sorgenti (Cascata Meteora), 35.14 Nodo del Sale,
35.15 Nodo dell'Argilla e 35.16 Sala di BASSI (Covo Magma), 35.17 Cuore del Fumaiolo (Grotta Terra),
35.18 Passo dei Draghi (Passo Selvaggio senza il bosco in fondo; le gobbe diventano terreno normale, cosi' si sale
a piedi senza la Bici Cross).
Gli oggetti di ogni mappa restano gli stessi, con lo stesso numero e gli stessi script (solo spostati); il masso
del vecchio rompicapo di 35.12 resta nella lista ma sempre nascosto (flag nuova alzata all'ingresso).
Uscite: stesse uscite e stessi indici di prima, in punti nuovi; gli script che portavano a coordinate dentro queste
mappe (ingresso da Cesena, ritorno da Ridracoli, guida delle Sorgenti, porta profonda, frane) puntano ai punti nuovi.
Vecchi salvataggi fatti dentro queste mappe: una volta sola si riparte dall'ingresso della mappa.
"""
import struct
import engine as E
from engine import H, P, B, Script
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'strumenti_rom'))
import tela

OUT = {}
L119, L120 = 0x585d30, 0x587c90
SENT = (35, 10)


def lay(d, lid): return struct.unpack_from('<I', d, 0x627fc0 + (lid - 1) * 4)[0] - 0x8000000


# ------------------------------------------------------------------ Sentiero (copia di bozze/fumaiolo.py)
SW, SH, SU = 40, 100, 40
def disegna_sentiero(d):
    a119, S119 = tela.Tela.layout(d, L119)
    T = tela.Tela(d, SW, SH, S119, 0x3001)
    def met(x, y, v): T.metti(x, y, S119, v)
    def mt(x, y): return T.c[y][x][1] & 1023
    def bosco(x, y, w, h):
        for j in range(h):
            for i in range(w): met(x + i, y + j, 0x4c7 if (y + j) % 2 else 0x4c6)
    T.incolla(L119, 0, 72, 40, SU, 0, 0)
    T.incolla(L119, 0, 0, 40, SH - SU, 0, SU)
    for y in range(SH):
        for x in range(SW):
            if 0xec <= mt(x, y) <= 0xfd or mt(x, y) == 0x206: met(x, y, 0x1170)
    bosco(0, 32, 4, 8)
    for y in range(SH):
        for x in range(1, SW):
            if mt(x, y) in (0x208, 0x1b0): T.c[y][x] = T.c[y][x - 1]
    for y in range(38, 46):
        for x in range(28, 34): met(x, y, 0x3001)
    T.incolla(L120, 0, 50, 12, 10, 0, SU + 26)
    for y in range(SU + 26, SU + 36):
        for x in range(12):
            sec, v = T.c[y][x]
            if v >> 12 == 3 and not (v >> 10) & 3: T.c[y][x] = (sec, (v & 0x0fff) | 0x4000)
            if 0xc8 <= mt(x, y) <= 0xda: met(x, y, 0x4001)
    for y in range(94, SH):
        for x in range(16, 23): met(x, y, 0x3001)
        r = 0 if y == 94 else 1
        for i in range(3): met(18 + i, y, 0x3118 + 8 * r + i)
    met(17, 98, 0x403)
    met(21, 98, 0x403)
    met(28, SU + 9, 0x3001)
    met(10, 4, 0x403)
    # in gioco la stele e' il pilastro della vetta del Monte Pira (la bozza segnava il posto con un cartello)
    T.metti(10, 4, tela.Tela.layout(d, lay(d, 303))[1], 0x72b)
    return T


SENT_OGGETTI = [(21, 96), (9, 73), (7, 72), (27, 78), (5, 73), (8, 2), (17, 96)]   # oggetti 1-7, come oggi
SENT_ARRIVO_CESENA, SENT_ARRIVO_RIDRACOLI = (19, 97), (18, 96)
GROTTA_EREMO, PORTA_RIFUGIO = (7, 71), (33, 37)


# ------------------------------------------------------------------ interno (copia di bozze/santuario.py)
class Stanza:
    def __init__(self, d, n, nome, lid, x0=0, y0=0, w=None, h=None):
        self.n, self.nome, self.L = n, nome, lay(d, lid)
        a, self.S = tela.Tela.layout(d, self.L)
        self.w, self.h = w or a.shape[1] - x0, h or a.shape[0] - y0
        self.T = tela.Tela(d, self.w, self.h, self.S, 0)
        self.T.incolla(self.L, x0, y0, self.w, self.h, 0, 0)
        self.uscite, self.oggetti, self.cartelli, self.barriera, self.lisce = [], [], [], [], False
        self.porta_finta = None

    def come(self, x, y, xs, ys): self.T.c[y][x] = self.T.c[ys][xs]


def stanze(d):
    out = []
    s = Stanza(d, 12, "Grotta dell'Eremo", 126)
    s.come(7, 20, 8, 20); s.come(7, 19, 8, 19); s.come(4, 14, 4, 15); s.come(4, 13, 5, 13)
    s.uscite = [(10, 29), (21, 23)]
    s.oggetti = [None, (18, 27)]                     # 1 = masso del vecchio rompicapo (nascosto)
    s.arrivo = (10, 28); out.append(s)
    s = Stanza(d, 13, 'Grotta delle Sorgenti', 127)
    s.come(5, 6, 6, 6); s.come(5, 5, 6, 5); s.come(18, 15, 18, 16); s.come(18, 14, 19, 14); s.come(3, 23, 3, 24); s.come(3, 22, 4, 22)
    for x0 in (12, 19):
        for i in range(3):
            for j in (2, 3): s.come(x0 + i, j, 16 + i, j)
    s.uscite = [(20, 36), (7, 11), (20, 3), (17, 3), (13, 3)]
    s.oggetti = [(15, 4), (21, 34)]
    s.cartelli = [(19, 33)]
    s.arrivo = (20, 35); out.append(s)
    s = Stanza(d, 14, 'Nodo del Sale', 339)
    s.come(23, 3, 24, 3); s.come(23, 2, 24, 2); s.come(21, 9, 22, 9); s.come(21, 8, 22, 8)
    s.uscite = [(7, 21)]
    s.oggetti = [(16, 4), (16, 11)]
    s.arrivo = (7, 20); out.append(s)
    s = Stanza(d, 15, "Nodo dell'Argilla", 340)
    s.uscite = [(12, 15)]
    s.oggetti = [(11, 12), (10, 10)]
    s.arrivo = (12, 14); out.append(s)
    s = Stanza(d, 16, 'Sala di Bassi', 337)
    s.come(11, 23, 12, 23); s.come(11, 22, 12, 22)
    s.uscite = [(17, 33), (8, 2)]
    s.oggetti = [(10, 5), (9, 3), (14, 31)]
    s.porta_finta = (8, 2)                          # si entra solo con lo script della porta profonda
    s.arrivo = (17, 32); out.append(s)
    s = Stanza(d, 17, 'Cuore del Fumaiolo', 409)
    s.uscite = [(5, 4)]
    s.oggetti = [(17, 25), (7, 22)]
    s.arrivo = (5, 5); out.append(s)
    s = Stanza(d, 18, 'Passo dei Draghi', 292, 0, 0, 30, 41)
    s.come(16, 18, 15, 18); s.come(16, 17, 15, 17)
    s.uscite = [(14, 40), (13, 5)]
    s.extra = [((15, 40), 0), ((14, 5), 1)]          # caselle d'uscita in piu' (stessa destinazione)
    s.oggetti = [(17, 38), (21, 9), (8, 20)]
    s.lisce = True
    s.barriera = [(14, 37), (15, 37)]
    s.arrivo = (14, 39); out.append(s)
    return out


# ------------------------------------------------------------------ testi
T_GUIDA_SENT = ("GUIDA: Il sentiero risale il SAVIO fino alla cima del FUMAIOLO.\n\n"
                "Il RIFUGIO è a nord, sulla strada di destra. L'EREMO è a ovest, oltre il ponte.\n\n"
                "Il masso davanti all'EREMO si sposta con FORZA.")
T_GUIDA_EREMO = ("GUIDA: Questa grotta scende nel cuore del FUMAIOLO.\n\n"
                 "La scala porta alla GROTTA DELLE SORGENTI.")
T_CARTELLO_SORGENTI = ("SANTUARIO DEL FUMAIOLO\n\n"
                       "Nord, da sinistra: PASSO DEI DRAGHI, sala di BASSI, nodo dell'ARGILLA.\n\n"
                       "Ovest, oltre il lago: nodo del SALE.")
CARTELLI_SENT = [(21, 98, "SENTIERO DEL FUMAIOLO\nCESENA è a sud.\n\nIl sentiero risale il SAVIO\nfino alla cima."),
                 (27, 59, "RIFUGIO DEL FUMAIOLO: a nord.\n\nEREMO DI SANT'ALBERICO: torna\nal ponte e vai a ovest."),
                 (10, 4, "Sulla stele è inciso:\nQUI NASCE IL FIUME SACRO\n\nAI DESTINI DI ROMA.\n\nÈ la sorgente del TEVERE.")]

# script che portano a coordinate dentro queste mappe: (indirizzo del comando warp, mappa, x, y vecchi, nuovi)
WARP_SCRIPT = [
    (0x1a88a48, 10, (28, 3), SENT_ARRIVO_CESENA),        # da Cesena (34.17 e 33.18, eventi a coordinate)
    (0x1e0920d, 10, (28, 3), SENT_ARRIVO_RIDRACOLI),     # guida di 35.50: ritorno al Sentiero
    (0x165f265, 18, (4, 23), (15, 39)),                  # guida delle Sorgenti: al Passo dopo Groudon
    (0x15cada1, 18, (4, 24), (14, 39)),                  # frane del Passo: si torna indietro
    (0x16755e9, 17, (15, 23), (5, 5)),                   # porta profonda: al Cuore
]


def ripunta(W, at, testo):
    assert W.d[at] == 0x0f and W.d[at + 1] == 0x00, hex(at)
    struct.pack_into('<I', W.d, at + 2, B + W.text(testo))


def cartello(nome, testo):
    s = Script(nome)
    s.emit(b'\x0f\x00' + P(E.W.text(testo)) + b'\x09\x03\x02')
    return s.save()


def freccia(U, vals, w, x, y, beh):
    v = vals[y * w + x]; mt = v & 1023
    refs, attr = (U.prim.refs(mt), U.prim.attr(mt)) if mt < 512 else U.meta[mt - 512]
    assert attr & 0xff == 0, (x, y, hex(attr))
    vals[y * w + x] = (v & 0xfc00) | U.metatile_nuovo(refs, (attr & 0xff00) | beh)


def comportamento(U, vals, w):
    def beh(x, y):
        k = vals[y * w + x] & 1023
        return (U.prim.attr(k) if k < 512 else U.meta[k - 512][1]) & 0xff
    return beh


def nuovi_oggetti(m, pos, elev):
    out = []
    for o, p in zip(m['objects'], pos):
        n = dict(o); n['raw'] = o['raw']
        n['script'] = o['script'] - B if o['script'] >= B else o['script']
        if p is not None:
            n['x'], n['y'] = p; n['elev'] = elev(*p)
        out.append(n)
    assert len(out) == len(m['objects'])
    return out


def apply(W):
    d = W.d
    pool = E.pool()
    NUOVA = E.variabili().var('Fumaiolo: entrata nelle mappe nuove (vecchi salvataggi, 0.66)')
    F_MASSO = pool.flag('Fumaiolo: masso del vecchio rompicapo di 35.12 sempre nascosto (0.66)')
    OUT['flag'] = dict(masso_35_12=hex(F_MASSO)); OUT['variabile'] = hex(NUOVA)
    mappe = {}

    # ---------------- 1. Sentiero
    m = W.rom.map(*SENT)
    assert (m['width'], m['height']) == (56, 52)
    assert [(w['x'], w['y'], w['group'], w['num'], w['warp']) for w in m['warps']] == \
        [(28, 0, 34, 17, 13), (8, 18, 35, 11, 0), (43, 13, 35, 12, 0)], m['warps']
    T = disegna_sentiero(bytes(d))
    U = tela.Unione(bytes(d)); vals = T.valori(U)
    for x in (18, 19, 20): freccia(U, vals, SW, x, 99, 0x65)
    beh = comportamento(U, vals, SW)
    assert beh(*GROTTA_EREMO) == 0x60 and beh(*PORTA_RIFUGIO) == 0x69, (hex(beh(*GROTTA_EREMO)), hex(beh(*PORTA_RIFUGIO)))
    tp = U.scrivi(W, 'sentiero fumaiolo')
    lp = W.set_layout(*SENT, vals, SW, SH, (0x4c6, 0x4c6, 0x4c7, 0x4c7), m['primary'], tp)
    mappe['35.10'] = dict(layout=hex(lp), dimensioni=[SW, SH], **U.stato())
    elev = lambda x, y: (lambda z: 3 if z in (0, 15) else z)((vals[y * SW + x] >> 12) & 15)
    ogg = nuovi_oggetti(m, SENT_OGGETTI, elev)
    ws = [dict(w) for w in m['warps']]
    ws[0].update(x=19, y=99); ws[1].update(x=PORTA_RIFUGIO[0], y=PORTA_RIFUGIO[1]); ws[2].update(x=GROTTA_EREMO[0], y=GROTTA_EREMO[1])
    ws += [dict(ws[0], x=18), dict(ws[0], x=20)]
    bg_old = {(b['x'], b['y']): b for b in m['bgs']}
    assert set(bg_old) == {(25, 4), (26, 6)}
    bgs = [dict(x=17, y=98, elev=0, kind=0, arg=bg_old[(26, 6)]['arg'])]        # la bacheca di oggi
    for x, y, t in CARTELLI_SENT:
        bgs.append(dict(x=x, y=y, elev=0, kind=0, arg=B + cartello('Fumaiolo: cartello %d,%d (0.66)' % (x, y), t)))
    W.set_events(*SENT, objects=ogg, warps=ws, coords=[], bgs=bgs)
    ripunta(W, 0x16501ce, T_GUIDA_SENT)
    mappe['35.10'].update(oggetti=[(o['id'], o['x'], o['y']) for o in ogg],
                          uscite=[(w['x'], w['y'], '%d.%d' % (w['group'], w['num']), w['warp']) for w in ws])

    # ---------------- 2. interno
    attese = {12: [(3, 15, 10, 2), (24, 4, 13, 0)],
              13: [(4, 24, 12, 1), (4, 7, 14, 0), (27, 8, 15, 0), (16, 4, 16, 0), (25, 24, 18, 0)],
              14: [(11, 19, 13, 1)], 15: [(11, 19, 13, 2)], 16: [(12, 21, 13, 3), (12, 4, 17, 0)],
              17: [(15, 24, 16, 1)], 18: [(3, 24, 13, 4), (33, 6, 19, 0)]}
    arrivi = {10: SENT_ARRIVO_CESENA}
    for s in stanze(bytes(d)):
        k = (35, s.n); m = W.rom.map(*k)
        assert [(w['x'], w['y'], w['num'], w['warp']) for w in m['warps']] == attese[s.n], (s.n, m['warps'])
        assert all(w['group'] == 35 for w in m['warps'])
        U = tela.Unione(bytes(d)); vals = s.T.valori(U)
        if s.lisce:
            n = 0
            for i, (refs, attr) in enumerate(U.meta):
                if attr & 0xff == 0xd1: U.meta[i] = (refs, attr & 0xff00); n += 1
            assert n > 0
        beh = comportamento(U, vals, s.w)
        if s.porta_finta:
            x, y = s.porta_finta; v = vals[y * s.w + x]; k_ = v & 1023
            assert beh(x, y) == 0x60
            refs, attr = (U.prim.refs(k_), U.prim.attr(k_)) if k_ < 512 else U.meta[k_ - 512]
            vals[y * s.w + x] = (v & 0xfc00) | U.metatile_nuovo(refs, attr & 0xff00)
        for (x, y) in [u for u in s.uscite if u != s.porta_finta] + [p for p, _ in getattr(s, 'extra', [])]:
            assert beh(x, y) in (0x60, 0x61, 0x64, 0x65), (s.n, x, y, hex(beh(x, y)))
        a_src = s.L
        brd = [struct.unpack_from('<H', d, struct.unpack_from('<I', d, a_src + 8)[0] - B + 2 * i)[0] for i in range(4)]
        brd = [(v & 0xfc00) | U.metatile(s.S, v & 1023) for v in brd]
        tp = U.scrivi(W, 'fumaiolo %d' % s.n)
        lp = W.set_layout(*k, vals, s.w, s.h, brd, m['primary'], tp)
        elev = lambda x, y, v=vals, w=s.w: (lambda z: 3 if z in (0, 15) else z)((v[y * w + x] >> 12) & 15)
        ogg = nuovi_oggetti(m, s.oggetti, elev)
        if s.n == 12:
            assert ogg[0]['gfx'] == 87 and ogg[0]['flag'] == 0
            ogg[0]['flag'] = F_MASSO
        ws = [dict(w) for w in m['warps']]
        for w, (x, y) in zip(ws, s.uscite): w.update(x=x, y=y)
        for (x, y), i in getattr(s, 'extra', []): ws.append(dict(ws[i], x=x, y=y))
        coords = []
        if s.barriera:
            vecchie = m['coords']; assert len(vecchie) == 14 and len({(c['var'], c['val'], c['script']) for c in vecchie}) == 1
            c0 = vecchie[0]
            coords = [dict(x=x, y=y, elev=c0['elev'], var=c0['var'], val=c0['val'],
                           script=c0['script'] - B if c0['script'] >= B else c0['script']) for x, y in s.barriera]
        bgs = [dict(b) for b in m['bgs']]
        if s.cartelli:
            assert len(bgs) == 1; bgs[0].update(x=s.cartelli[0][0], y=s.cartelli[0][1])
            p = bgs[0]['arg'] - B; ripunta(W, p + 2, T_CARTELLO_SORGENTI)
        W.set_events(*k, objects=ogg, warps=ws, coords=coords, bgs=bgs)
        arrivi[s.n] = s.arrivo
        mappe['35.%d' % s.n] = dict(nome=s.nome, layout=hex(lp), dimensioni=[s.w, s.h], **U.stato(),
                                    oggetti=[(o['id'], o['x'], o['y']) for o in ogg],
                                    uscite=[(w['x'], w['y'], '%d.%d' % (w['group'], w['num']), w['warp']) for w in ws],
                                    frane=s.barriera)
    ripunta(W, 0x165ec82, T_GUIDA_EREMO)

    # ---------------- 3. script che portano dentro queste mappe
    for at, n, vecchio, nuovo in WARP_SCRIPT:
        assert d[at:at + 4] == bytes([0x39, 35, n, 0xff]) and struct.unpack_from('<HH', d, at + 4) == vecchio, hex(at)
        struct.pack_into('<HH', d, at + 4, *nuovo)
    OUT['warp_script'] = [(hex(a), '35.%d' % n, v, nu) for a, n, v, nu in WARP_SCRIPT]

    # ---------------- 4. script di mappa: vecchi salvataggi (una volta sola si riparte dall'ingresso)
    for n, (x, y) in sorted(arrivi.items()):
        k = (35, n); m = W.rom.map(*k)
        vecchi = W.rom.map_scripts(m)
        s = Script('Fumaiolo %d: ingresso (0.66)' % n)
        s.var(NUOVA, 1)
        if n == 12: s.set(F_MASSO)
        s.emit(b'\x02'); t3 = s.save()
        s = Script('Fumaiolo %d: vecchio salvataggio, si riparte da %d,%d (0.66)' % (n, x, y))
        s.var(NUOVA, 1).emit(b'\x3a' + bytes([35, n, 0xff]) + H(x) + H(y) + b'\x27\x02')
        f = s.save()
        voci = H(NUOVA) + H(0) + P(f)
        nuovi = []
        for t, p in vecchi:
            assert t in (1, 2, 5), (n, t)
            if t == 2:                                       # tabella del frame di oggi (ALDO): la mia voce prima
                q = p - B if p >= B else p; resto = b''
                while struct.unpack_from('<H', d, q)[0]: resto += d[q:q + 8]; q += 8
                voci += resto
            else: nuovi.append((t, p - B if p >= B else p))
        tab = W.alloc(voci + H(0), 'frame fumaiolo %d' % n)
        W.set_map_scripts(*k, nuovi + [(2, tab), (3, t3)])
    OUT['vecchi_salvataggi'] = {'35.%d' % n: list(p) for n, p in sorted(arrivi.items())}
    OUT['mappe'] = mappe
    return OUT
