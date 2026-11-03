"""Versione 0.63 - Lotto 3: Cesena ovest, Ippodromo e Monte Spaccato.

Prima (0.62):
  Cesena 34.17 -> casello ovest 35.91 (eventi a coordinate: senza la 3a medaglia 0x869 si torna indietro)
  -> Monte Spaccato 35.101 -> casello 35.92 -> Capocolle 35.60.
  L'Ippodromo 34.19 era una deviazione da Monte Spaccato (casetta 54,36); anche il suo cancello ovest
  (3,17) riportava a Monte Spaccato, ed era chiuso da tre rocce (oggetti 5-7, flag 0x720/0x724/0x725).
  Da Monte Spaccato, sull'erba attorno alla collina, si andava a ovest senza ostacoli fisici.

Dopo (0.63):
  Cesena -> casello 35.91 (nessun controllo) -> Ippodromo (cancello sud) -> cancello ovest -> Monte Spaccato
  -> tre rocce nella tagliata (14,16-18) -> casello 35.92 -> Capocolle.
  - L'Ippodromo e' una tappa del percorso e si visita alla prima visita di Cesena.
  - Le rocce usano lo script di Smeraldo (SPACCAROCCIA + 3a medaglia, con il suo messaggio) e flag temporanee
    0x11-0x13: come in Smeraldo ricompaiono a ogni ingresso.
  - Quattro alberi chiudono i due corridoi d'erba a nord e a sud della collina (x 11-12): a ovest si passa
    solo dalla tagliata.
  - Chi ha gia' superato il passaggio non resta chiuso fuori: entrando nel casello 35.92 si alza la flag
    nuova "passaggio aperto"; con quella, Monte Spaccato nasconde le rocce. Il casello 35.92 si raggiunge solo
    passando le rocce, o da ovest (vecchi salvataggi gia' oltre il vecchio casello).
  - Le tre rocce del cancello ovest dell'Ippodromo spariscono (le loro flag si alzano entrando nella mappa).
"""
import struct
import engine as E
from engine import H, P, B, Script

OUT = {}
ROCCIA_SCR, ROCCIA_GFX = 0x290b6b, 86
ROCCE = [(14, 16, 0x11), (14, 17, 0x12), (14, 18, 0x13)]
ALBERO = ((0x5d4, 0x5d5), (0x5dc, 0x5dd), (0x5e4, 0x5e5))     # cima, base con albero sotto, base su erba


def ripunta(W, at, testo):
    assert W.d[at] == 0x0f and W.d[at + 1] == 0x00, hex(at)
    struct.pack_into('<I', W.d, at + 2, B + W.text(testo))


def warp(W, key, i, dest, w):
    m = W.rom.map(*key); ws = [dict(x) for x in m['warps']]
    ws[i]['group'], ws[i]['num'], ws[i]['warp'] = dest[0], dest[1], w
    W.set_events(*key, warps=ws)


def blocchi(W, key, celle):
    m = W.rom.map(*key); a = W.rom.blocks(m)
    for x, y, v in celle:
        assert (int(a[y, x]) >> 10) & 3 == 0, (key, x, y, hex(int(a[y, x])))    # era erba calpestabile
        struct.pack_into('<H', W.d, m['blocks'] + (y * m['width'] + x) * 2, v)


def apply(W):
    d = W.d
    pool = E.pool()
    APERTO = pool.flag('Monte Spaccato: passaggio verso Capocolle aperto (rocce nascoste)')
    OUT['flag'] = hex(APERTO)

    # ---- 1. Casello ovest di Cesena (35.91): niente controllo della 3a medaglia
    m = W.rom.map(35, 91)
    assert [(c['x'], c['y'], c['script']) for c in m['coords']] == [(3, y, 0x1599bd0) for y in range(2, 6)]
    assert d[0x1599bd1:0x1599bd4] == b'\x2b' + H(0x869)
    W.set_events(35, 91, coords=[])
    ripunta(W, 0x1599d0a, "CASELLANTE: A est c'è CESENA.\nA ovest l'IPPODROMO DEL SAVIO\n\n"
                          "e poi MONTE SPACCATO, verso\nCAPOCOLLE e FORLIMPOPOLI.")
    OUT['35.91'] = 'tolti i 4 eventi a coordinate (3,2-5) che controllavano 0x869'

    # ---- 2. Uscite: casello -> Ippodromo (sud) ; Ippodromo (ovest) -> Monte Spaccato
    w91 = W.rom.map(35, 91)['warps']; assert (w91[1]['x'], w91[1]['y'], w91[1]['group'], w91[1]['num']) == (0, 4, 35, 101)
    warp(W, (35, 91), 1, (34, 19), 0)
    m = W.rom.map(34, 19); ws = [dict(x) for x in m['warps']]
    assert [(w['x'], w['y']) for w in ws] == [(18, 33), (3, 17), (3, 17), (19, 33), (20, 33), (21, 33)]
    for i, w in enumerate(ws):
        if w['y'] == 33: w.update(group=35, num=91, warp=1)            # cancello sud -> casello di Cesena
        else: w.update(group=35, num=101, warp=2)                      # cancello ovest -> Monte Spaccato
    W.set_events(34, 19, warps=ws)
    m = W.rom.map(35, 101); ws = [dict(x) for x in m['warps']]
    assert [(w['x'], w['y'], w['num']) for w in ws] == [(58, 20, 91), (4, 17, 92), (54, 36, 19)]
    ws[0].update(group=34, num=19, warp=1)                             # casetta "CESENA" -> Ippodromo (cancello ovest)
    ws[2].update(group=34, num=19, warp=1)                             # casetta "IPPODROMO" -> Ippodromo (cancello ovest)
    W.set_events(35, 101, warps=ws)
    OUT['uscite'] = '35.91 w1 -> 34.19 w0; 34.19 sud -> 35.91 w1, ovest -> 35.101 w2; 35.101 w0 e w2 -> 34.19 w1'

    # ---- 3. Ippodromo: via le rocce del cancello ovest
    m = W.rom.map(34, 19)
    rocce_ipp = [(o['x'], o['y'], o['flag']) for o in m['objects'] if o['script'] == ROCCIA_SCR]
    assert rocce_ipp == [(4, 17, 0x720), (4, 16, 0x724), (4, 18, 0x725)], rocce_ipp
    s = Script('Ippodromo: rocce del cancello ovest nascoste (0.63)')
    for _, _, f in rocce_ipp: s.set(f)
    s.emit(b'\x02'); ipp = s.save()
    W.set_map_scripts(34, 19, W.rom.map_scripts(m) + [(3, ipp)])

    # ---- 4. Monte Spaccato: tre rocce nella tagliata e alberi nei corridoi d'erba
    m = W.rom.map(35, 101)
    assert not any(o['flag'] in (0x11, 0x12, 0x13) for o in m['objects'])
    a = W.rom.blocks(m)
    for x, y, _ in ROCCE:
        assert (int(a[y, x]) >> 10) & 3 == 0 and (int(a[15, x]) >> 10) & 3 and (int(a[19, x]) >> 10) & 3
    celle = []
    for x in (11, 12):
        k = x - 11
        celle += [(x, 2, ALBERO[0][k]), (x, 3, ALBERO[1][k]), (x, 4, ALBERO[0][k]), (x, 5, ALBERO[2][k]),
                  (x, 34, ALBERO[0][k]), (x, 35, ALBERO[1][k]), (x, 36, ALBERO[0][k]), (x, 37, ALBERO[1][k])]
    blocchi(W, (35, 101), celle)
    for x, y, f in ROCCE:
        E.add_object((35, 101), x, y, ROCCIA_GFX, ROCCIA_SCR, move=8, flag=f, elev=(int(a[y, x]) >> 12) & 15)
    s = Script('Monte Spaccato: rocce nascoste se il passaggio e\' aperto (0.63)')
    s.flag(APERTO, 'aperto').emit(b'\x02').label('aperto')
    for _, _, f in ROCCE: s.set(f)
    s.emit(b'\x02'); ms = s.save()
    W.set_map_scripts(35, 101, W.rom.map_scripts(W.rom.map(35, 101)) + [(3, ms)])
    # cartello all'ingresso est
    ripunta(W, 0x15951de, "MONTE SPACCATO\nA ovest CAPOCOLLE, poi\n\n"
                          "FORLIMPOPOLI. A est c'è\nl'IPPODROMO, poi CESENA.")
    OUT['35.101'] = dict(rocce=ROCCE, alberi='x 11-12, righe 2-5 e 34-37', script_ingresso=hex(ms))

    # ---- 5. Casello 35.92: entrando si alza "passaggio aperto"
    assert not W.rom.map_scripts(W.rom.map(35, 92))
    s = Script('Casello 35.92: passaggio aperto (0.63)')
    s.set(APERTO).emit(b'\x02'); c92 = s.save()
    W.set_map_scripts(35, 92, [(3, c92)])

    # ---- 6. ADA (Rimini 34.48): dopo la MN, il testo indicava le rocce nell'Ippodromo
    ripunta(W, 0x2d2672, "Con la terza medaglia puoi\nusare SPACCAROCCIA all'aperto.\n\n"
                         "Torna a CESENA: oltre\nl'IPPODROMO, a MONTE SPACCATO,\n\n"
                         "le rocce chiudono la strada\nper Forlì. VOLO ti aiuterà.")
    return OUT
