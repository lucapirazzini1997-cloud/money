"""Versione 0.65 - Lotto 3: RIDRACOLI ridisegnata (35.51) e l'evento del GYARADOS rosso.

Prima (0.64): 35.51 era 44x34: un lago chiaro non navigabile, il muro della diga e la centrale; uscita in basso
verso la valle 35.50 (da cui si arriva da Forli' e dal Sentiero del Fumaiolo, con la 7a medaglia).

Dopo (0.65), dalla bozza 2 approvata (bozze/ridracoli.py; il disegno e' copiato qui e congelato):
  - 35.51 diventa 44x62: da sud la strada sale nella valle, devia verso la centrale (porta -> 35.52, come prima),
    arriva alla scala nel muro della diga e al coronamento; sopra c'e' il lago vero (SURF), con la baia di
    nord-est e il Rio Celluzze; sulla riva est l'accampamento del TEAM EMILIA; a nord-ovest la cascata del
    Bidente e, sopra, la sorgente (solo con CASCATA).
  - Layout nuovo (blocchi, bordo di bosco, tileset secondario fatto con tela.Unione) nello stesso posto della
    tabella dei layout (id 805, solo di 35.51).
  - Uscite: tre caselle-freccia in fondo alla strada (23-25,61) -> 35.50 (uscita 0, come prima); porta della
    centrale -> 35.52 (uscita 1, come prima, cosi' 35.52 non cambia).
  - Personaggi: custode della diga, escursionista e pescatore (allenatori), due reclute e il capo CORRADO del
    TEAM EMILIA (il capo lotta solo dopo le due reclute), il GYARADOS rosso al centro del lago (compare quando
    CORRADO e' battuto), una Poke Ball alla sorgente (ACQUA MAGICA).
  - GYARADOS: livello 40, sempre cromatico (comando nativo del progetto, gia' usato per FARFETCH'D e SHUCKLE),
    una sola cattura; dopo fuga o KO resta al suo posto e si ritenta. Sprite sulla mappa nuovo, ricavato dallo
    sprite di lotta cromatico della ROM (rimpicciolito a 32x32): prende il numero di grafica 184 (BAMBOLONE
    REGIROCK delle basi segrete, non usato da nessuna mappa) e una tavolozza nuova (tag 0x1340).
  - Incontri: l'erba prende la tabella di terra di 35.50 (stessa zona); acqua e pesca restano quelle di prima.
  - Testi di 35.50 (guida, cartello, custode) riscritti in due righe; la missione della centrale resta facoltativa.
  - Vecchi salvataggi fatti dentro 35.51: come nella 0.64, una volta sola si riparte dalla strada sotto la diga.
Differenze dalla bozza, tutte per poter giocare (collaudo/confronto_bozza_065.py): frecce d'uscita (23-25,61);
primo gradino della scala (23-25,36), che nella bozza era muro; cartello e Poke Ball della sorgente spostati da
(10,2) e (8,4), caselle di roccia irraggiungibili, alla riva sopra la cascata (9,5) e (9,8).
"""
import struct
import engine as E
from engine import H, P, B, Script
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'strumenti_rom'))
import tela

OUT = {}
MAPPA = (35, 51)
LAYOUT_VECCHIO = 0x1e1786c                    # layout di 35.51 alla 0.64 (44x34), da cui si prende la diga
W_, H_ = 44, 62
GYARADOS, LV = 130, 40
NATIVE_SHINY_WILD = 0x09730055                 # callnative dopo setwildbattle: il selvatico e' cromatico
GFX_GY, PAL_TAG = 184, 0x1340
GFX_TAB, PAL_REFS = 0x6ada3c, (0x8ea24, 0x8eab8, 0x8eb10)
FRONT_PIC, SHINY_PAL = 0x31c750, 0x3169fc      # tabelle (spostate) degli sprite di lotta e delle tavolozze cromatiche
ACQUA_MAGICA = 0xd1
TAB_ALLENATORI = 0xf21000
TERRA_3550 = 0x9e665b8                         # incontri d'erba di 35.50
INCONTRI_3551 = 0x15ccbe8                      # voce di 35.51 nella tabella degli incontri


def disegna(d):
    """La bozza 2 di Ridracoli (copia congelata). Ritorna la tela."""
    W, H = W_, H_
    def lay(lid): return struct.unpack_from('<I', d, 0x627fc0 + (lid - 1) * 4)[0] - 0x8000000
    L114 = lay(30)
    a114, S114 = tela.Tela.layout(d, L114)
    LR = LAYOUT_VECCHIO
    T = tela.Tela(d, W, H, S114, 0x3001)
    G, ALTA = 0x3001, 0x300d
    def met(x, y, v, src=S114): T.metti(x, y, src, v)
    def mt(x, y): return T.c[y][x][1] & 1023
    def bosco(x, y, w, h, cima=True, base=True):
        for j in range(h):
            for i in range(w):
                k = (x + i) % 2
                if j % 2 == 0: v = (0x31ce + k) if (cima and j == 0) else (0x5d4 + k)
                else: v = (0x5e4 + k) if (base and j == h - 1) else (0x5dc + k)
                met(x + i, y + j, v)

    # --- 1. foresta ovunque, poi i pezzi
    bosco(0, 0, W, H, cima=False, base=False)
    T.incolla(L114, 0, 0, 20, 21, 2, 0)                                 # terrazze, cascata del Bidente, laghetto
    T.incolla(L114, 0, 21, 40, 13, 2, 21)                               # lago con l'isolotto
    T.incolla(LR, 5, 18, 34, 5, 5, 34)                                  # la diga: coronamento (34-35) e muro (36-38)
    T.incolla(L114, 0, 33, 40, 23, 2, 39)                               # valle d'accesso, con la casa (centrale)

    # --- 2. il lago: maschera dell'acqua e rive ricalcolate
    ACQUA_ID = {0x170, 0x189, 0x180, 0x181, 0x190, 0x192, 0x198, 0x19a, 0x178, 0x179, 0x2c0, 0x2c1, 0x2c8, 0x2c9, 0x28b, 0x293}
    acqua = [[False] * W for _ in range(H)]
    for y in range(21, 34):
        for x in range(W):
            acqua[y][x] = mt(x, y) in ACQUA_ID
    def a(x, y, w, h):
        for j in range(h):
            for i in range(w): acqua[y + j][x + i] = True
    a(31, 0, 4, 8)
    a(29, 8, 8, 1); a(26, 9, 12, 1); a(24, 10, 15, 11)
    a(9, 21, 30, 12); a(9, 33, 28, 1)
    for y in range(21, 34):
        for x in range(W):
            if acqua[y][x] and mt(x, y) not in ACQUA_ID and x < 9: acqua[y][x] = False
    ISOLA = {(x, y) for y in range(25, 29) for x in range(12, 16)}
    for (x, y) in ISOLA: acqua[y][x] = False
    def w(x, y): return y < 0 or (0 <= x < W and y < H and acqua[y][x])
    NE = lambda x, y: x >= 22 and y <= 33 and not (5 <= x <= 38 and y >= 34)
    for y in range(0, 34):
        for x in range(W):
            if (x, y) in ISOLA: continue
            if w(x, y):
                if y < 21 and x < 22: continue
                U, L, R = not w(x, y - 1), not w(x - 1, y), not w(x + 1, y)
                if U and L: v = 0x1180
                elif U and R: v = 0x1181
                elif U: v = 0x1189
                elif L: v = 0x1179 if w(x - 1, y - 1) else 0x1190
                elif R: v = 0x1178 if w(x + 1, y - 1) else 0x1192
                elif not w(x - 1, y - 1): v = 0x1198
                elif not w(x + 1, y - 1): v = 0x119a
                else: v = 0x1170
                met(x, y, v)
            elif NE(x, y):
                bx, by = x - x % 2, y - y % 2
                vicino = any(0 <= by + j + jj < H and w(bx + i + ii, by + j + jj)
                             for i in (0, 1) for j in (0, 1) for ii in (-1, 0, 1) for jj in (-1, 0, 1)
                             if by + j + jj >= 0)
                if vicino: met(x, y, G)
    for y in range(8, 34):
        for x in range(39, 42): met(x, y, G)
    for y in range(34, 37):
        for x in range(39, 42): met(x, y, G)
    for y in range(0, 34):
        for x in range(22, W):
            if mt(x, y) == 0x001 and w(x, y - 1): met(x, y, 0x3002)
    bosco(42, 0, 2, 40, cima=False, base=False)

    # --- 3. la valle: pulizia, strada dall'ingresso sud alla scala della diga e alla centrale
    for y in (39, 40, 41):
        for x in range(2, 42):
            if mt(x, y) in ACQUA_ID or mt(x, y) in (0x002, 0x0d3, 0x0d4): met(x, y, G)
            if mt(x, y) in (0x179, 0x178): met(x, y, G)
    BUCHE = {0x208}
    for y in range(39, H):
        for x in range(1, W):
            if mt(x, y) in BUCHE: T.c[y][x] = T.c[y][x - 1]
    def strada_v(x0, y0, y1):
        for y in range(y0, y1 + 1):
            r = 0 if y == y0 else 1
            for i in range(3): met(x0 + i, y, 0x3118 + 8 * r + i)
    def strada_h(x0, x1, y):
        for x in range(x0, x1 + 1):
            e = 0 if x == x0 else (2 if x == x1 else 1)
            met(x, y, 0x3118 + e); met(x, y + 1, 0x3120 + e); met(x, y + 2, 0x3128 + e)
    strada_v(23, 39, H - 1)
    strada_h(23, 31, 44)
    for y in (44, 45): met(23, y, 0x3120); met(24, y, 0x3121); met(25, y, 0x3121)
    for y in (37, 38):
        for x in (23, 24, 25): met(x, y, 0x00af)
    for x in (23, 24, 25): met(x, 36, 0x00af)                      # (0.65) primo gradino: nella bozza era muro
    met(22, 39, 0x403)
    met(10, 2, 0x403)
    # (0.65) la sorgente: nella bozza cartello (10,2) e Poke Ball (8,4) stavano su caselle di roccia irraggiungibili;
    # vanno sulla riva sopra la cascata (9-10, 5-9), dove si scende dal laghetto alto
    T.c[2][10] = T.c[2][9]
    met(9, 5, 0x403)
    return T


# ------------------------------------------------------------------ personaggi
# numero, x, y, gfx, riferimento (classe/foto), nome, donna, squadra [(specie, livello)], vista, testi
ESCURSIONISTA = (581, 21, 52, 31, 216, 'GIANNI', False, [(75, 39), (383, 40)], 0,
                 "Salgo alla diga ogni domenica.\nTi va una lotta in salita?",
                 "Che fiato che hai!",
                 "Dalla scala nel muro si sale\nin cima alla diga.")
PESCATORE = (633, 12, 34, 49, 496, 'ERMES', False, [(324, 39), (119, 40)], 0,
             "Da quando c'è il TEAM EMILIA\nil lago non dà più pesci!",
             "Almeno la lotta l'ho fatta.",
             "Il GYARADOS del lago è\nnervoso: stai attento.")
RECLUTA_DIGA = (634, 31, 34, 119, 773, 'EMILIA', False, [(287, 40), (110, 41)], 2,
                "Alt! La diga adesso è\ndel TEAM EMILIA!",
                "Uffa... il capo non sarà\ncontento.",
                "Il capo è all'accampamento,\nsulla riva est del lago.")
RECLUTA_RIVA = (851, 40, 27, 119, 773, 'EMILIA', True, [(82, 41), (338, 41)], 3,
                "Il nostro sonar fa infuriare\nil GYARADOS del lago!",
                "Il sonar... si è rotto!",
                "Senza sonar il lago dovrebbe\ncalmarsi. Forse...")
CAPO = (734, 40, 15, 196, 775, 'CORRADO', False, [(287, 42), (340, 42), (331, 43)], 0,
        "Un ragazzino alla diga?\nTi mostro chi comanda qui!",
        "Il sonar... il lago...\nCosa abbiamo fatto?",
        None)
ALLENATORI = [ESCURSIONISTA, PESCATORE, RECLUTA_DIGA, RECLUTA_RIVA, CAPO]

T_CUSTODE = dict(
    prima="Il TEAM EMILIA si è accampato\nsulla riva est della diga.\n\n"
          "Col loro sonar il GYARADOS\ndel lago è furioso!\n\n"
          "Dal coronamento si va a est.\nTi prego, fermali!",
    dopo="Il GYARADOS rosso è emerso al\ncentro del lago, furioso.\n\n"
         "Raggiungilo con SURF e\ncalmalo con una lotta!",
    calmo="Il lago è di nuovo calmo.\nGrazie di cuore!\n\n"
          "La CENTRALE è qui accanto:\nci sono ancora delle reclute.")
T_CAPO = dict(
    reclute="CORRADO: Prima te la vedi\ncon le mie reclute!",
    fuga="CORRADO: Il GYARADOS è fuori\ncontrollo... Ritirata!",
    emerge="Il lago ribolle...\n\nUn GYARADOS rosso emerge\ninfuriato al centro del lago!",
    dopo="CORRADO: Il GYARADOS è ancora\nfurioso. Che guaio...",
    calmo="CORRADO: L'hai calmato tu?\nIl capo non ci crederà...")
T_GY = dict(
    intro="Il GYARADOS rosso è furioso!\nCalmalo con una lotta!",
    preso="Hai calmato e catturato il\nGYARADOS rosso!\n\nIl lago torna tranquillo.",
    ko="Il GYARADOS si inabissa, poi\nriemerge, ancora furioso.\n\nPuoi riprovare quando vuoi.",
    fuga="Il GYARADOS resta al centro\ndel lago, furioso.\n\nPuoi riprovare quando vuoi.")
CARTELLI = [(22, 39, "DIGA DI RIDRACOLI\nSali la scala per il lago.\n\nLa CENTRALE è a destra."),
            (9, 5, "SORGENTE DEL BIDENTE\nQui nasce il fiume\n\nche riempie il lago.")]
# testi di 35.50 (loadword 0f 00 <ptr> negli script di oggi)
TESTI_3550 = [
    (0x1e09182, "Vuoi seguire la guida fino\na FORLÌ?"),
    (0x1e091fa, "Il sentiero orientale porta\nalla VALLE DEL SAVIO. Vieni?"),
    (0x1e092aa, "Questi sentieri portano al\nbacino del BIDENTE.\n\nPer il FUMAIOLO c'è il\nsentiero a sud di CESENA."),
    (0x1e09332, "A nord ci sono la DIGA DI\nRIDRACOLI e la CENTRALE.\n\nIl TEAM EMILIA si aggira\nda quelle parti..."),
    (0x1e0939e, "RIDRACOLI\nA nord la DIGA e il LAGO."),
]


def ripunta(W, at, testo):
    assert W.d[at] == 0x0f and W.d[at + 1] == 0x00, hex(at)
    struct.pack_into('<I', W.d, at + 2, B + W.text(testo))


def cartello(nome, testo):
    s = Script(nome)
    s.emit(b'\x0f\x00' + P(E.W.text(testo)) + b'\x09\x03\x02')        # msgbox MSGBOX_SIGN, end
    return s.save()


def allenatore(W, tid, rif, nome, squadra, donna):
    o = TAB_ALLENATORI + tid * 40
    raw = bytearray(40)
    r = TAB_ALLENATORI + rif * 40
    raw[0] = 2; raw[1] = W.d[r + 1]; raw[2] = (W.d[r + 2] & 0x7f) | (0x80 if donna else 0); raw[3] = W.d[r + 3]
    nm = W.enc(nome) + b'\xff'; raw[4:4 + len(nm)] = nm
    struct.pack_into('<I', raw, 28, 7); raw[32] = len(squadra)
    pp = W.alloc(b''.join(struct.pack('<HBxHH', 0, lv, sp, 0) for sp, lv in squadra), 'squadra ' + nome)
    struct.pack_into('<I', raw, 36, B + pp)
    W.d[o:o + 40] = raw


def lz(d, p):
    assert d[p] == 0x10, hex(p)
    n = int.from_bytes(d[p + 1:p + 4], 'little'); p += 4; out = bytearray()
    while len(out) < n:
        f = d[p]; p += 1
        for b in range(7, -1, -1):
            if len(out) >= n: break
            if f & (1 << b):
                a, c = d[p], d[p + 1]; p += 2
                k = (a >> 4) + 3; disp = ((a & 15) << 8) + c + 1
                for _ in range(k): out.append(out[-disp])
            else:
                out.append(d[p]); p += 1
    return bytes(out[:n])


def sprite_gyarados(d):
    """Sprite 32x32 (4bpp, 16 tile) e tavolozza dal GYARADOS cromatico di lotta: ogni 2x2 diventa il colore della
    tavolozza piu' vicino alla media (trasparente se meno di 2 pixel pieni), poi un contorno nero."""
    pic = struct.unpack_from('<I', d, FRONT_PIC + GYARADOS * 8)[0] - B
    pal = struct.unpack_from('<I', d, SHINY_PAL + GYARADOS * 8)[0] - B
    raw = lz(d, pic); pr = lz(d, pal)[:32]
    px = []
    for b in raw[:2048]: px += [b & 15, b >> 4]
    img = [[0] * 64 for _ in range(64)]
    for t in range(64):
        for j in range(8):
            for i in range(8): img[(t // 8) * 8 + j][(t % 8) * 8 + i] = px[t * 64 + j * 8 + i]
    cols = [struct.unpack_from('<H', pr, k * 2)[0] for k in range(16)]
    rgb = [((c & 31), (c >> 5) & 31, (c >> 10) & 31) for c in cols]
    out = [[0] * 32 for _ in range(32)]
    for y in range(32):
        for x in range(32):
            nz = [img[2 * y + j][2 * x + i] for j in (0, 1) for i in (0, 1) if img[2 * y + j][2 * x + i]]
            if len(nz) < 2: continue
            m = [sum(rgb[k][c] for k in nz) / len(nz) for c in range(3)]
            out[y][x] = min(range(1, 16), key=lambda k: (sum((rgb[k][c] - m[c]) ** 2 for c in range(3)), k))
    pieno = [[out[y][x] != 0 for x in range(32)] for y in range(32)]
    for y in range(32):
        for x in range(32):
            if pieno[y][x] and any(not (0 <= y + dy < 32 and 0 <= x + dx < 32) or not pieno[y + dy][x + dx]
                                   for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0))):
                out[y][x] = 14                                               # nero della tavolozza
    assert cols[14] == 0, hex(cols[14])
    tiles = bytearray()
    for ty in range(4):
        for tx in range(4):
            for j in range(8):
                for i in range(0, 8, 2):
                    tiles.append(out[ty * 8 + j][tx * 8 + i] | (out[ty * 8 + j][tx * 8 + i + 1] << 4))
    return bytes(tiles), pr


def sprite_nuovo(W):
    """Grafica 184 = GYARADOS rosso: struttura copiata dalla 224 (32x32, un fotogramma), tavolozza nuova."""
    d = W.d
    tiles, pal = sprite_gyarados(bytes(d))
    ip = W.alloc(tiles, 'sprite gyarados rosso')
    pp = W.alloc(pal, 'tavolozza gyarados rosso')
    frames = W.alloc(b''.join(P(ip) + struct.pack('<I', 0x200) for _ in range(8)), 'fotogrammi gyarados rosso')
    mod = struct.unpack_from('<I', d, GFX_TAB + 224 * 4)[0] - B
    info = bytearray(d[mod:mod + 36])
    assert struct.unpack_from('<Hhh', info, 6) == (0x200, 32, 32)
    struct.pack_into('<H', info, 2, PAL_TAG)
    struct.pack_into('<I', info, 28, B + frames)
    gp = W.alloc(bytes(info), 'grafica gyarados rosso')
    vecchio = struct.unpack_from('<I', d, GFX_TAB + GFX_GY * 4)[0]
    assert vecchio == 0x86b37c0, hex(vecchio)                              # BAMBOLONE REGIROCK
    struct.pack_into('<I', d, GFX_TAB + GFX_GY * 4, B + gp)
    # tabella delle tavolozze degli oggetti: si copia con una voce in piu'
    t = struct.unpack_from('<I', d, PAL_REFS[0])[0]
    assert all(struct.unpack_from('<I', d, r)[0] == t for r in PAL_REFS)
    t -= B; voci = []
    while True:
        p, tag, z = struct.unpack_from('<IHH', d, t + len(voci) * 8)
        if p == 0 and tag == 0x11ff: break
        assert tag != PAL_TAG
        voci.append(bytes(d[t + len(voci) * 8:t + len(voci) * 8 + 8]))
    nuova = b''.join(voci) + P(pp) + H(PAL_TAG) + H(0) + struct.pack('<IHH', 0, 0x11ff, 0)
    nt = W.alloc(nuova, 'tavolozze oggetti (0.65)')
    for r in PAL_REFS: struct.pack_into('<I', d, r, B + nt)
    return dict(grafica=GFX_GY, info=hex(gp), tavolozza=hex(pp), tag=hex(PAL_TAG), tabella_tavolozze=hex(nt),
                voci=len(voci) + 1)


def apply(W):
    d = W.d
    pool = E.pool()
    m = W.rom.map(*MAPPA)
    assert m['layout'] == LAYOUT_VECCHIO and (m['width'], m['height']) == (44, 34)
    assert W.rom.map_scripts(m) == []
    # ---- 1. la mappa nuova: layout nuovo (blocchi, bordo, secondario)
    T = disegna(bytes(d))
    U = tela.Unione(bytes(d)); vals = T.valori(U)
    assert len(vals) == W_ * H_
    # frecce d'uscita in fondo alla strada (verso sud, comportamento 0x65)
    for x in (23, 24, 25):
        v = vals[61 * W_ + x]; mt = v & 1023
        assert mt < 512 and (U.prim.attr(mt) & 0xff) == 0, (x, hex(v))
        nuovo = U.metatile_nuovo(U.prim.refs(mt), (U.prim.attr(mt) & 0xff00) | 0x65)
        vals[61 * W_ + x] = (v & 0xfc00) | nuovo
    blob_attr = U.blob()[3]
    def beh(x, y):
        k = vals[y * W_ + x] & 1023
        return (U.prim.attr(k) if k < 512 else struct.unpack_from('<H', blob_attr, (k - 512) * 2)[0]) & 0xff
    porte = [(x, y) for y in range(H_) for x in range(W_) if beh(x, y) in (0x69, 0x60)]
    assert len(porte) == 1, porte
    porta = porte[0]
    assert [beh(x, 61) for x in (23, 24, 25)] == [0x65] * 3
    tp = U.scrivi(W, 'ridracoli')
    lp = W.set_layout(*MAPPA, vals, W_, H_, (0x5d4, 0x5d5, 0x5dc, 0x5dd), m['primary'], tp)
    OUT['layout'] = dict(puntatore=hex(lp), dimensioni=[W_, H_], porta_centrale=porta, **U.stato())

    # ---- 2. uscite: 0 = freccia sud (verso 35.50, come prima), 1 = porta della centrale (35.52 punta qui)
    ws = [dict(x) for x in m['warps']]
    assert [(w['x'], w['y'], w['group'], w['num'], w['warp']) for w in ws] == [(20, 33, 35, 50, 0), (21, 27, 35, 52, 0)], ws
    ws[0].update(x=24, y=61); ws[1].update(x=porta[0], y=porta[1])
    ws += [dict(ws[0], x=23), dict(ws[0], x=25)]
    m50 = W.rom.map(35, 50)
    assert [(w['x'], w['y'], w['group'], w['num'], w['warp']) for w in m50['warps']] == [(18, 0, 35, 51, 0)]
    m52 = W.rom.map(35, 52)
    assert [(w['group'], w['num'], w['warp']) for w in m52['warps']] == [(35, 51, 1)]

    # ---- 3. flag, variabili, sprite
    F_NASCOSTO = pool.flag('Ridracoli: GYARADOS rosso nascosto (oggetto) (0.65)')
    F_PRESO = pool.flag('Ridracoli: GYARADOS rosso catturato (0.65)')
    F_ACQUA = pool.flag('Ridracoli: ACQUA MAGICA alla sorgente (0.65)')
    nuovi_flag = [0x500 + a[0] for a in ALLENATORI]
    assert not any(int(f, 16) in nuovi_flag for f, _ in pool.taken)
    pool.riordina([], escludi=nuovi_flag)
    NUOVA = E.variabili().var('Ridracoli: entrata nella mappa nuova (vecchi salvataggi, 0.65)')
    OUT['sprite'] = sprite_nuovo(W)

    # ---- 4. allenatori
    for a in ALLENATORI:
        tid, rif, nome, donna, squadra = a[0], a[4], a[5], a[6], a[7]
        assert d[TAB_ALLENATORI + tid * 40 + 4] != 0xff, tid
        allenatore(W, tid, rif, nome, squadra, donna)
    def semplice(a):
        s = Script('Ridracoli: allenatore %s (0.65)' % a[5])
        s.emit(b'\x5c\x00' + H(a[0]) + H(0) + P(W.text(a[9])) + P(W.text(a[10])))
        s.msg(a[11]).end()
        return s.save()
    CAPO_F = 0x500 + CAPO[0]
    # vinto il capo (script di continuazione della lotta di tipo 1): il GYARADOS emerge
    s = Script('Ridracoli: CORRADO battuto, il GYARADOS emerge (0.65)')
    s.emit(b'\x6a').msg(T_CAPO['fuga'])
    s.clear(F_NASCOSTO).emit(b'\x55' + H(1))                            # addobject 1 (il GYARADOS)
    s.emit(b'\xa1' + H(GYARADOS) + H(2) + b'\xc5')                      # playmoncry, waitmoncry
    s.msg(T_CAPO['emerge']).end()
    vinto = s.save()
    # il capo: lotta solo dopo le due reclute
    s = Script('Ridracoli: capo CORRADO (0.65)')
    s.emit(b'\x6a\x5a')                                                 # lock, faceplayer
    s.flag(CAPO_F, 'battuto')
    s.flag(0x500 + RECLUTA_DIGA[0], 'r1')
    s.label('mancano').msg(T_CAPO['reclute']).end()
    s.label('r1').flag(0x500 + RECLUTA_RIVA[0], 'lotta')
    s.jump('mancano')
    s.label('lotta')
    s.emit(b'\x5c\x01' + H(CAPO[0]) + H(0) + P(W.text(CAPO[9])) + P(W.text(CAPO[10])) + P(vinto))
    s.label('battuto').flag(F_PRESO, 'calmo')
    s.msg(T_CAPO['dopo']).end()
    s.label('calmo').msg(T_CAPO['calmo']).end()
    capo_scr = s.save()

    # ---- 5. il GYARADOS rosso
    s = Script('Ridracoli: GYARADOS rosso (0.65)')
    s.emit(b'\x6a')                                                     # lock
    s.flag(F_PRESO, 'fine')
    s.msg(T_GY['intro'])
    s.emit(b'\xa1' + H(GYARADOS) + H(2) + b'\xc5')                      # playmoncry, waitmoncry
    s.emit(b'\xb6' + H(GYARADOS) + bytes([LV]) + H(0))                   # setwildbattle
    s.var(0x8004, GYARADOS).var(0x8005, LV)                              # il nativo rifa' il Pokemon da 8004/8005
    s.emit(b'\x23' + struct.pack('<I', NATIVE_SHINY_WILD))               # callnative: cromatico
    s.set(0x8c1).emit(b'\xb7').clear(0x8c1)                              # dowildbattle (l'oggetto resta)
    s.emit(b'\x26' + H(0x800d) + H(0xb7))                                # esito
    s.cmp(7, 'preso').cmp(1, 'ko')
    s.msg(T_GY['fuga']).end()
    s.label('ko').msg(T_GY['ko']).end()
    s.label('preso').set(F_PRESO).set(F_NASCOSTO).emit(b'\x53' + H(1))   # removeobject 1
    s.msg(T_GY['preso']).end()
    s.label('fine').end()
    gy_scr = s.save()

    # ---- 6. custode, Poke Ball, oggetti
    s = Script('Ridracoli: custode della diga (0.65)')
    s.emit(b'\x6a\x5a')
    s.flag(F_PRESO, 'calmo').flag(CAPO_F, 'dopo')
    s.msg(T_CUSTODE['prima']).end()
    s.label('dopo').msg(T_CUSTODE['dopo']).end()
    s.label('calmo').msg(T_CUSTODE['calmo']).end()
    custode = s.save()
    s = Script('Ridracoli: ACQUA MAGICA alla sorgente (0.65)')
    s.emit(b'\x1a' + H(0x8000) + H(ACQUA_MAGICA) + b'\x1a' + H(0x8001) + H(1) + b'\x09\x01\x02')
    palla = s.save()
    elev = lambda x, y: (vals[y * W_ + x] >> 12) & 15
    oggetti = [dict(gfx=GFX_GY, x=22, y=27, elev=1, move=8, script=gy_scr, flag=F_NASCOSTO),
               dict(gfx=55, x=31, y=45, elev=3, move=8, script=custode, flag=0)]
    for a in (ESCURSIONISTA, PESCATORE, RECLUTA_DIGA, RECLUTA_RIVA):
        oggetti.append(dict(gfx=a[3], x=a[1], y=a[2], elev=3, move=8, script=semplice(a), flag=0,
                            ttype=1 if a[8] else 0, trange=a[8]))
    oggetti.append(dict(gfx=CAPO[3], x=CAPO[1], y=CAPO[2], elev=3, move=8, script=capo_scr, flag=0))
    oggetti.append(dict(gfx=59, x=9, y=8, elev=elev(9, 8), move=8, script=palla, flag=F_ACQUA))
    for i, o in enumerate(oggetti): o['id'] = i + 1
    for o in oggetti:
        if o['gfx'] != GFX_GY: assert elev(o['x'], o['y']) in (0, 3), (o, elev(o['x'], o['y']))
    assert elev(22, 27) == 1 and beh(22, 27) != 0
    bgs = [dict(x=x, y=y, elev=0, kind=0, arg=B + cartello('Ridracoli: cartello %d,%d (0.65)' % (x, y), t))
           for x, y, t in CARTELLI]
    for x, y, _ in CARTELLI: assert T.c[y][x][1] == 0x403
    W.set_events(*MAPPA, objects=oggetti, warps=ws, coords=[], bgs=bgs)
    OUT['oggetti'] = [(o['id'], o['x'], o['y'], o['gfx'], hex(o['script']), hex(o['flag'])) for o in oggetti]
    OUT['allenatori_nuovi'] = [(a[0], a[5], hex(0x500 + a[0])) for a in ALLENATORI]
    OUT['flag'] = dict(nascosto=hex(F_NASCOSTO), preso=hex(F_PRESO), acqua_magica=hex(F_ACQUA))
    OUT['uscite'] = [(w['x'], w['y'], '%d.%d' % (w['group'], w['num']), w['warp']) for w in ws]

    # ---- 7. incontri: l'erba nuova prende la tabella di terra di 35.50
    assert d[INCONTRI_3551:INCONTRI_3551 + 2] == bytes([35, 51])
    assert struct.unpack_from('<I', d, INCONTRI_3551 + 4)[0] == 0
    assert struct.unpack_from('<I', d, 0x15ccbac + 4)[0] == TERRA_3550 and d[0x15ccbac:0x15ccbae] == bytes([35, 50])
    struct.pack_into('<I', d, INCONTRI_3551 + 4, TERRA_3550)

    # ---- 8. testi di 35.50
    for at, t in TESTI_3550: ripunta(W, at, t)

    # ---- 9. script di mappa: ingresso (GYARADOS visibile solo tra la vittoria su CORRADO e la cattura;
    # variabile NUOVA per i vecchi salvataggi) e frame (vecchio salvataggio -> strada sotto la diga, una volta)
    s = Script('Ridracoli: ingresso (0.65)')
    s.var(NUOVA, 1)
    s.flag(F_PRESO, 'nascondi').flag(CAPO_F, 'mostra', present=True)
    s.label('nascondi').set(F_NASCOSTO).emit(b'\x02')
    s.label('mostra').clear(F_NASCOSTO).emit(b'\x02')
    t3 = s.save()
    s = Script('Ridracoli: vecchio salvataggio, si riparte sotto la diga (0.65)')
    s.var(NUOVA, 1).emit(b'\x3a' + bytes([35, 51, 0xff]) + H(24) + H(41) + b'\x27\x02')
    f = s.save()
    tab = W.alloc(H(NUOVA) + H(0) + P(f) + H(0), 'frame ridracoli')
    W.set_map_scripts(*MAPPA, [(2, tab), (3, t3)])
    OUT['vecchi_salvataggi'] = dict(variabile=hex(NUOVA), ingresso=hex(t3), frame=hex(f), arrivo=[24, 41])
    return OUT
