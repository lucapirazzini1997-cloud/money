"""Versione 0.67 - Lotto 3: il TRENO REGIONALE (bozza approvata: bozze/treno.py; il disegno e' copiato qui e congelato).

Linea Rimini - Cesena - Forli' - Faenza - Imola.
- Fuori: in ogni citta' una casa chiusa diventa la STAZIONE. La casa resta com'e'; sopra la facciata c'e' un
  cartello blu con STAZIONE in bianco e la porta si apre (comportamento 0x60, come le altre porte della hack).
  Le citta' hanno i 512 tile del secondario pieni: il cartello sta in 8 tile del PRIMARIO vuoti che nessuna
  mappa, nessun metatile del primario e nessun setmetatile degli script usa. I metatile nuovi (4 del cartello e
  la porta) vanno in una copia della tabella dei metatile della citta', in posti che la citta' non usa.
- Dentro: cinque mappe nuove (24.39-24.41, 24.50, 24.51) con la sala del binario di Smeraldo (layout 118, usato
  com'e'). Il CAPOTRENO offre le citta' gia' sbloccate sulla mappa del Volo (stesse flag di visita, che seguono
  le medaglie; Imola compare dopo la 6a medaglia, quando ci si e' stati), una alla volta con si'/no. Biglietto gratis.
- La carrozza (24.74): atrio del Centro Spaziale (layout 275) con finestrini, tavolini lisci e sgabelli. Scena:
  al primo viaggio il viaggiatore chiacchiera; il CAPOTRENO arriva e annuncia la fermata; si scende sul binario
  della stazione scelta.
Vecchi salvataggi: le case sostituite erano chiuse; niente da spostare.
"""
import struct
import engine as E
from engine import H, P, B, Script
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'strumenti_rom'))
import numpy as np
import tela, scr

OUT = {}
PRIMARIO = 0x55e8c0
TILE_CARTELLO = [183, 197, 219, 235, 237, 258, 290, 306]
PAL_CARTELLO = 4
FONT = {
    'S': ['.###', '#...', '.##.', '...#', '###.'], 'T': ['###', '.#.', '.#.', '.#.', '.#.'],
    'A': ['.##.', '#..#', '####', '#..#', '#..#'], 'Z': ['####', '...#', '.##.', '#...', '####'],
    'I': ['###', '.#.', '.#.', '.#.', '###'], 'O': ['.##.', '#..#', '#..#', '#..#', '.##.'],
    'N': ['#..#', '##.#', '#.##', '#..#', '#..#'], 'E': ['####', '#...', '###.', '#...', '####'],
}


def lay(d, lid): return struct.unpack_from('<I', d, 0x627fc0 + (lid - 1) * 4)[0] - B


def cartello_pixel():
    img = np.zeros((8, 64), int)
    img[0:8, 3:61] = 0xa
    img[1:7, 4:60] = 0x7
    testo = 'STAZIONE'
    larg = sum(len(FONT[c][0]) for c in testo) + (len(testo) - 1)
    x = (64 - larg) // 2
    for c in testo:
        g = FONT[c]
        for j, riga in enumerate(g):
            for i, ch in enumerate(riga):
                if ch == '#': img[1 + j, x + i] = 0x1
        x += len(g[0]) + 1
    return img


def tile_cartello():
    img = cartello_pixel(); out = []
    for k in range(8):
        t = img[:, k * 8:k * 8 + 8].flatten()
        out.append(bytes(int(t[i]) | (int(t[i + 1]) << 4) for i in range(0, 64, 2)))
    return out


# (citta', mappa della stazione, x e y della casa, altezza, riga del cartello, meta' (0 alta, 1 bassa))
STAZIONI = [
    ('CESENA', (34, 17), (24, 39), 80, 6, 3, 7, 1),
    ('RIMINI', (34, 47), (24, 40), 52, 9, 3, 10, 1),
    ("FORLÌ", (34, 68), (24, 41), 70, 52, 4, 54, 0),
    ('FAENZA', (34, 85), (24, 50), 38, 2, 4, 4, 0),
    ('IMOLA', (35, 1), (24, 51), 55, 16, 4, 18, 0),
]
VISITA = {'CESENA': 0x876, 'RIMINI': 0x877, "FORLÌ": 0x878, 'FAENZA': 0x873, 'IMOLA': 0x872}   # flag del Volo
ORDINE = ['RIMINI', 'CESENA', "FORLÌ", 'FAENZA', 'IMOLA']                                  # lungo la linea
CARROZZA = (24, 74)
SALA_ARRIVO = (6, 4)
SALA_USCITE = [(6, 11), (7, 11)]
MUSICA = 0x168


# ------------------------------------------------------------------ carrozza (copia di bozze/treno.py)
def disegna_carrozza(d):
    L = lay(d, 275)
    a, S = tela.Tela.layout(d, L)
    T = tela.Tela(d, 16, 12, S, 0)
    for y in range(12):
        for x in range(16): T.metti(x, y, S, int(a[3, 1]))
    for x in range(16):
        T.metti(x, 0, S, int(a[0, 4])); T.metti(x, 1, S, int(a[1, 4])); T.metti(x, 2, S, int(a[2, 4]))
    T.incolla(L, 1, 0, 1, 3, 0, 0); T.incolla(L, 15, 0, 1, 3, 15, 0)
    for x0 in (1, 5, 9, 13):
        for y0 in (3, 8):
            T.incolla(L, 2, 5, 2, 2, x0, y0 + 1)
            for yy in (y0, y0 + 3):
                T.metti(x0, yy, S, int(a[3, 2])); T.metti(x0 + 1, yy, S, int(a[3, 2]))
    return T, a, S, L


def tavolini_lisci(U, v, a, S):
    def tile(idx):
        px = []
        for bb in U.tiles[idx - 512]: px += [bb & 15, bb >> 4]
        return np.array(px).reshape(8, 8)
    vecchi = {}
    img = np.zeros((32, 32), int)
    for j in range(2):
        for i in range(2):
            mid = U.metatile(S, int(a[5 + j, 2 + i]) & 1023); vecchi[(i, j)] = mid
            refs, _ = U.meta[mid - 512]
            for q in range(4):
                r = refs[4 + q]; t = tile(r & 1023)
                if r & 0x400: t = t[:, ::-1]
                if r & 0x800: t = t[::-1]
                y, x = j * 16 + (q // 2) * 8, i * 16 + (q % 2) * 8
                img[y:y + 8, x:x + 8] = t
    bianco = np.bincount(img[8:20, 8:24].flatten()).argmax()
    img[4:21, 5:27] = bianco
    nuovi = {}
    for (i, j), mid in vecchi.items():
        refs, attr = U.meta[mid - 512]; refs = list(refs)
        for q in range(4):
            y, x = j * 16 + (q // 2) * 8, i * 16 + (q % 2) * 8
            t = img[y:y + 8, x:x + 8].flatten()
            raw = bytes(int(t[k]) | (int(t[k + 1]) << 4) for k in range(0, 64, 2))
            refs[4 + q] = U._tile(raw) | (refs[4 + q] & 0xf000)
        nuovi[mid] = U.metatile_nuovo(refs, attr)
    for k, val in enumerate(v):
        if (val & 1023) in nuovi: v[k] = (val & 0xfc00) | nuovi[val & 1023]


# ------------------------------------------------------------------ testi
def T_SALUTO(c): return "CAPOTRENO: Stazione di %s!\nDove vuoi andare?" % c
def T_DOMANDA(c): return "Un biglietto per %s?" % c
def T_PARTENZA(c): return ("CAPOTRENO: Ecco il biglietto per %s.\nPer chi allena Pokémon è gratis!\n\n"
                           "Il regionale è in partenza.\nSali pure!" % c)
T_NESSUNA = ("CAPOTRENO: Il regionale ferma solo nelle città che vedi sulla mappa del VOLO.\n\n"
             "Per ora non ce n'è nessuna. Torna più avanti!")
T_NO = "CAPOTRENO: Va bene. Il regionale passa spesso, torna quando vuoi!"
T_ATTESA = ("Aspetto il regionale. Fa sempre un po' di ritardo...\n\n"
            "Però arriva, e in un attimo sei dall'altra parte della Romagna!")
T_BINARIO = "Il treno sta arrivando... non vedo l'ora di vedere il mare!"
T_BIGLIETTERIA = ("BIGLIETTERIA AUTOMATICA\nFuori servizio.\n\n"
                  "Fermate del regionale: IMOLA, FAENZA, FORLÌ, CESENA, RIMINI.\n\nChiedi al CAPOTRENO.")
T_VIAGGIATORE = ("VIAGGIATORE: Hai visto dal finestrino? Il treno corre lungo la VIA EMILIA.\n\n"
                 "Una volta da Rimini a Imola si andava a piedi. Adesso ci vuole un attimo!\n\n"
                 "Io scendo alla prossima: mia sorella fa la piadina migliore della Romagna!")
T_VIAGGIATORE_DOPO = "VIAGGIATORE: Il regionale è comodo, ma la piadina si mangia a casa!"
T_CAPO_CARROZZA = "CAPOTRENO: Buon viaggio sul regionale della Romagna!"
def T_ANNUNCIO(c): return "CAPOTRENO: Prossima fermata: %s.\nScendete dal lato del binario." % c


def cartello(nome, testo):
    s = Script(nome)
    s.emit(b'\x0f\x00' + P(E.W.text(testo)) + b'\x09\x03\x02')
    return s.save()


def parla(nome, testo):
    s = Script(nome); s.emit(b'\x6a\x5a'); s.msg(testo); s.end(); return s.save()


def setmetatile_ids(W, key):
    """Metatile che gli script della mappa mettono con setmetatile (da non sovrascrivere)."""
    import genera
    d = bytes(W.d); out = set()
    def walk(p, seen, depth=0):
        if p is None or p in seen or not (0 <= p < len(d)) or depth > 20: return
        seen.add(p)
        try: ops, _ = scr.decode(d, p, 500)
        except Exception: return
        for a_, n, ar in ops:
            if n == 'setmetatile': out.add(ar[2] & 1023)
            if n in ('call', 'goto', 'goto_if', 'call_if') and ar and isinstance(ar[-1], int) and B <= ar[-1] < B + len(d):
                walk(ar[-1] - B, seen, depth + 1)
    m = W.rom.map(*key); seen = set()
    for lab, p in genera.entries(W.rom, m): walk(p, seen)
    return out


def apply(W):
    d = W.d
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'registri'))
    pool = E.pool()
    F_PRIMO = pool.flag('Treno: primo viaggio fatto, il viaggiatore ha gia\' chiacchierato (0.67)')
    TRENO = E.variabili().var('Treno: stazione di arrivo del viaggio in corso, 0 = nessuno (0.67)')
    OUT['flag'] = dict(primo_viaggio=hex(F_PRIMO)); OUT['variabile'] = hex(TRENO)

    # ---------------- 1. cartello nel primario
    gp = struct.unpack_from('<I', d, PRIMARIO + 4)[0] - B
    assert d[PRIMARIO] == 1 and d[gp] == 0x10
    raw = bytearray(tela._lz(bytes(d), gp)); assert len(raw) == 0x4000
    for idx, t in zip(TILE_CARTELLO, tile_cartello()):
        assert not any(raw[idx * 32:idx * 32 + 32]), idx
        raw[idx * 32:idx * 32 + 32] = t
    lz = b'\x10' + len(raw).to_bytes(3, 'little') + b''.join(b'\x00' + bytes(raw[i:i + 8]) for i in range(0, len(raw), 8))
    np_ = W.alloc(lz, 'tile del primario con il cartello STAZIONE')
    assert d.count(struct.pack('<I', B + gp)) == 1
    struct.pack_into('<I', d, PRIMARIO + 4, B + np_)
    OUT['primario'] = dict(tile=TILE_CARTELLO, grafica=hex(np_), vecchia=hex(gp))

    # ---------------- 2. sala (layout 118 com'e') e carrozza
    L118 = lay(bytes(d), 118)
    a118, _ = tela.Tela.layout(bytes(d), L118)
    assert a118.shape == (12, 13) and [(int(a118[11, x]) & 1023) for x in (6, 7)] == [0x206, 0x207]
    m19 = W.rom.map(19, 0)
    T, a275, S275, L275 = disegna_carrozza(bytes(d))
    U = tela.Unione(bytes(d)); vals = T.valori(U); tavolini_lisci(U, vals, a275, S275)
    tp = U.scrivi(W, 'carrozza del regionale')
    brd = [struct.unpack_from('<H', d, struct.unpack_from('<I', d, L275 + 8)[0] - B + 2 * i)[0] for i in range(4)]
    brd = [(v & 0xfc00) | U.metatile(S275, v & 1023) for v in brd]
    mc = W.rom.map(*CARROZZA)
    lpc = W.set_layout(*CARROZZA, vals, 16, 12, brd, PRIMARIO, tp)
    OUT['carrozza'] = dict(mappa='24.74', layout=hex(lpc), **U.stato())

    # ---------------- 3. citta'
    stazioni = {}
    for nome, citta, sala, x, y, h, riga, meta in STAZIONI:
        m = W.rom.map(*citta); w = m['width']
        assert m['primary'] == PRIMARIO
        a = W.rom.blocks(m).astype(int).flatten().tolist()
        porta = (x + 2, y + h - 1)
        bgs = [dict(b) for b in m['bgs']]
        chiusa = [b for b in bgs if (b['x'], b['y']) == porta]
        assert len(chiusa) == 1 and not [w_ for w_ in m['warps'] if (w_['x'], w_['y']) == porta], nome
        sec = m['secondary']; St = tela.Tileset(bytes(d), sec); Pt = tela.Tileset(bytes(d), PRIMARIO)
        usati = {v & 1023 for v in a} | setmetatile_ids(W, citta)
        lp_old = struct.unpack_from('<I', d, m['header'])[0] - B
        border = list(struct.unpack_from('<4H', d, struct.unpack_from('<I', d, lp_old + 8)[0] - B))
        usati |= {v & 1023 for v in border}
        liberi = [i for i in range(1023, 511, -1) if i not in usati][:5]
        meta_t = bytearray(d[St.meta:St.meta + 512 * 16]); attr_t = bytearray(d[St.attrs:St.attrs + 512 * 2])
        def leggi(mt):
            if mt < 512: return list(Pt.refs(mt)), Pt.attr(mt)
            return list(struct.unpack_from('<8H', meta_t, (mt - 512) * 16)), struct.unpack_from('<H', attr_t, (mt - 512) * 2)[0]
        def scrivi_mt(i, refs, attr):
            struct.pack_into('<8H', meta_t, (i - 512) * 16, *refs); struct.pack_into('<H', attr_t, (i - 512) * 2, attr)
        for i in range(4):
            k = riga * w + x + i; v = a[k]
            refs, attr = leggi(v & 1023)
            q0 = 4 + meta * 2
            refs[q0] = TILE_CARTELLO[2 * i] | (PAL_CARTELLO << 12)
            refs[q0 + 1] = TILE_CARTELLO[2 * i + 1] | (PAL_CARTELLO << 12)
            scrivi_mt(liberi[i], refs, (attr & 0x0fff) | 0x1000)
            a[k] = (v & 0xfc00) | liberi[i]
        k = porta[1] * w + porta[0]; v = a[k]
        refs, attr = leggi(v & 1023)
        assert attr & 0xff == 0, (nome, hex(attr))
        scrivi_mt(liberi[4], refs, (attr & 0xff00) | 0x60)
        a[k] = (v & 0xf000) | liberi[4]                                   # collisione 0: ci si entra
        mp = W.alloc(bytes(meta_t), 'metatile %s (0.67)' % nome); ap = W.alloc(bytes(attr_t), 'attributi %s (0.67)' % nome)
        ts = bytearray(d[sec:sec + 24]); struct.pack_into('<II', ts, 12, B + mp, B + ap)
        tsp = W.alloc(bytes(ts), 'tileset %s con la stazione (0.67)' % nome)
        lp = W.set_layout(*citta, a, w, m['height'], border, PRIMARIO, tsp)
        bgs.remove(chiusa[0])
        ws = [dict(w_) for w_ in m['warps']]
        ws.append(dict(x=porta[0], y=porta[1], elev=0, warp=0, num=sala[1], group=sala[0]))
        W.set_events(*citta, bgs=bgs, warps=ws)
        stazioni[nome] = dict(citta=citta, sala=sala, porta=porta, uscita_citta=len(ws) - 1, regione=m['region'])
        OUT.setdefault('citta', {})[nome] = dict(mappa='%d.%d' % citta, layout=hex(lp), porta=porta, metatile=liberi,
                                                 stazione='%d.%d' % sala)

    # ---------------- 4. sale delle stazioni
    nomi = [s[0] for s in STAZIONI]
    for nome, citta, sala, *_ in STAZIONI:
        st = stazioni[nome]
        W.use_layout_of(*sala, L118)
        W.header_set(*sala, music=MUSICA, region=st['regione'], cave=0, weather=0, type=8, flags=4, battle=0)
        W.set_connections(*sala, [])
        # capotreno
        s = Script('Treno: capotreno di %s (0.67)' % nome)
        s.emit(b'\x6a\x5a')
        altre = [c for c in ORDINE if c != nome]
        for c in altre: s.flag(VISITA[c], 'qualcuna')
        s.msg(T_NESSUNA).end()
        s.label('qualcuna').msg(T_SALUTO(nome))
        for c in altre:
            s.flag(VISITA[c], 'salta_' + str(nomi.index(c)), present=False)
            s.ask(T_DOMANDA(c)).cmp(1, 'va_' + str(nomi.index(c)))
            s.label('salta_' + str(nomi.index(c)))
        s.msg(T_NO).end()
        for c in altre:
            j = nomi.index(c)
            s.label('va_%d' % j).msg(T_PARTENZA(c)).var(TRENO, j + 1)
            s.emit(b'\x39' + bytes([CARROZZA[0], CARROZZA[1], 0xff]) + H(8) + H(7) + b'\x27').end()
        p_cap = s.save()
        ogg = [dict(gfx=115, x=7, y=8, elev=3, move=8, script=p_cap),
               dict(gfx=21, x=1, y=9, elev=3, move=10, script=parla('Treno: viaggiatore in attesa (0.67)', T_ATTESA)),
               dict(gfx=26, x=10, y=2, elev=3, move=8, script=parla('Treno: viaggiatrice sul binario (0.67)', T_BINARIO))]
        for i, o in enumerate(ogg): o['id'] = i + 1
        ws = [dict(x=x_, y=y_, elev=0, warp=st['uscita_citta'], num=citta[1], group=citta[0]) for x_, y_ in SALA_USCITE]
        # il tabellone (2-3,4) sta dietro la ringhiera: nessuna casella lo raggiunge, le fermate le dice la biglietteria
        p_big = cartello('Treno: biglietteria (0.67)', T_BIGLIETTERIA) if nome == 'CESENA' else OUT['_big']
        OUT['_big'] = p_big
        bgs = [dict(x=12, y=8, elev=0, kind=0, arg=B + p_big)]
        W.set_events(*sala, objects=ogg, warps=ws, coords=[], bgs=bgs)
        W.set_map_scripts(*sala, [])
    OUT.pop('_big')

    # ---------------- 5. carrozza: eventi e scena
    W.header_set(*CARROZZA, music=MUSICA, region=stazioni['CESENA']['regione'], cave=0, weather=0, type=8, flags=0, battle=0)
    W.set_connections(*CARROZZA, [])
    mov = W.alloc(bytes([0x0b] * 4 + [0xfe]), 'capotreno: quattro passi a destra (0.67)')
    p_viagg = parla('Treno: viaggiatore in carrozza (0.67)', T_VIAGGIATORE_DOPO)
    voci = b''
    for j, (nome, citta, sala, *_) in enumerate(STAZIONI):
        s = Script('Treno: viaggio verso %s (0.67)' % nome)
        s.emit(b'\x69' + b'\x28' + H(30))                                  # lockall, delay
        s.flag(F_PRIMO, 'annuncio')
        s.msg(T_VIAGGIATORE).set(F_PRIMO)
        s.label('annuncio')
        s.emit(b'\x4f' + H(2) + P(mov) + b'\x51' + H(2))                  # il capotreno arriva
        s.emit(b'\x5b' + H(0xff) + bytes([3]))                            # il giocatore si gira verso di lui
        s.msg(T_ANNUNCIO(nome))
        s.var(TRENO, 0)
        s.emit(b'\x39' + bytes([sala[0], sala[1], 0xff]) + H(SALA_ARRIVO[0]) + H(SALA_ARRIVO[1]) + b'\x27')
        s.end()
        voci += H(TRENO) + H(j + 1) + P(s.save())
    tab = W.alloc(voci + H(0), 'frame carrozza (0.67)')
    W.set_map_scripts(*CARROZZA, [(2, tab)])
    ogg = [dict(id=1, gfx=21, x=10, y=3, elev=3, move=8, script=p_viagg),
           dict(id=2, gfx=115, x=3, y=7, elev=3, move=10, script=parla('Treno: capotreno in carrozza (0.67)', T_CAPO_CARROZZA))]
    W.set_events(*CARROZZA, objects=ogg, warps=[], coords=[], bgs=[])
    OUT['stazioni'] = {n: dict(citta='%d.%d' % s['citta'], sala='%d.%d' % s['sala'], porta=s['porta'])
                       for n, s in stazioni.items()}
    return OUT
