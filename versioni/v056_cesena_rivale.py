"""Versione 0.56 - Cesena (pittore e Smeargle, Biblioteca, chiesa) e nome del rivale per i vecchi salvataggi.
Si applica sopra la 0.55 con il motore versioni/engine.py."""
import struct
import engine as E
from engine import H, P, B, Script

ITEM_TABLE = 0x72f194
PENNELLO = 0x15b                 # voce vuota "????????" nella 0.55
TM17 = 0x131                     # MT17 PROTEZIONE: nessuno script della 0.55 la regala
MOON_STONE = 0x5e
SMEARGLE = 235
NATIVE_SHINY_GIFT = 0x09730069   # 8004=specie, 8005=livello, 8006=specie -> 0x800d: 0 squadra, 1 PC, 2 nessun posto
NATIVE_NAME = 0x19b8a2c          # schermata "NOME DEL RIVALE?" (0.52), ritorno CB2_ReturnToFieldContinueScriptPlayMapMusic
CESENA, LABIRINTO, BIBLIOTECA, CHIESA, LAB = (34, 17), (34, 33), (34, 24), (34, 37), (1, 4)
OUT = {}


def W(): return E.W


def vtext(*parts):
    """Testo con segnaposti: str normale, 'RIVALE' come oggetto speciale -> FD 06."""
    out = b''
    for p in parts:
        out += b'\xfd\x06' if p is RIVALE else W().enc(p)
    return P(W().alloc(out + b'\xff', 'vtext'))


RIVALE = object()


def msgraw(s, ptr): return s.emit(b'\x0f\x00' + ptr + b'\x09\x04')


# ------------------------------------------------------------------ strumento PENNELLO
def item_pennello():
    d = W().d; off = ITEM_TABLE + 44 * PENNELLO
    assert bytes(d[off:off + 8]) == bytes([0xac] * 8), 'la voce 0x15b non e piu libera'
    raw = bytearray(d[ITEM_TABLE + 44 * 0x15f: ITEM_TABLE + 44 * 0x15f + 44])      # REGISTRO MOLO: strumento chiave senza uso
    raw[0:14] = (W().enc('PENNELLO') + b'\xff').ljust(14, b'\x00')
    struct.pack_into('<H', raw, 14, PENNELLO)
    struct.pack_into('<H', raw, 16, 0)                                              # prezzo 0
    desc = W().alloc(W().enc('Pennello del pittore\ndi Cesena. Riportane\ntre in piazza.') + b'\xff', 'desc pennello')
    struct.pack_into('<I', raw, 20, B + desc)
    assert raw[26] == 5                                                             # tasca STRUMENTI CHIAVE
    d[off:off + 44] = raw
    return PENNELLO


# ------------------------------------------------------------------ I pennelli del pittore
def pennelli():
    pool = E.pool()
    flags = []
    for i, (x, y) in enumerate([(2, 2), (20, 8), (12, 22)]):          # vicoli ciechi lontani fra loro (BFS dall'ingresso)
        f = pool.flag('pennello %d' % (i + 1)); flags.append(f)
        s = Script('Pennello %d' % (i + 1))
        s.emit(b'\x1a' + H(0x8000) + H(PENNELLO) + b'\x1a' + H(0x8001) + H(1) + b'\x09\x01').emit(b'\x02')   # finditem
        E.add_object(LABIRINTO, x, y, 59, s.save(), flag=f)
    done = pool.flag('pittore: SMEARGLE consegnato')
    s = Script('Pittore')
    s.emit(b'\x6a\x5a')                                                  # lock, faceplayer
    s.flag(done, 'done')
    s.checkitem(PENNELLO, 3).cmp(1, 'tre')
    s.checkitem(PENNELLO, 2).cmp(1, 'due')
    s.checkitem(PENNELLO, 1).cmp(1, 'uno')
    s.msg("PITTORE: Volevo ritrarre la Fontana Masini, ma ho perso i miei tre pennelli!\n\n"
          "Il vento li ha portati nel labirinto del Parco della Rocca. Me li riporti?").end()
    s.label('uno').msg("PITTORE: Uno dei miei pennelli! Ne mancano ancora due, nel labirinto della Rocca.").end()
    s.label('due').msg("PITTORE: Due pennelli su tre! L'ultimo è ancora fra le siepi della Rocca.").end()
    s.label('tre').msg("PITTORE: Tutti e tre i miei pennelli! Grazie!\n\n"
                       "Uno SMEARGLE mi ha seguito fin qui: vuole viaggiare con chi ama i colori.")
    s.var(0x8004, SMEARGLE).var(0x8005, 15).var(0x8006, SMEARGLE)
    s.emit(b'\x23' + struct.pack('<I', NATIVE_SHINY_GIFT))
    s.cmp(2, 'pieno')
    s.cmp(1, 'pc')
    s.removeitem(PENNELLO, 3).set(done)
    s.msg("Hai ricevuto SMEARGLE! Il suo pelo brilla di colori insoliti.").end()
    s.label('pc').removeitem(PENNELLO, 3).set(done)
    s.msg("Hai ricevuto SMEARGLE! La squadra è piena: è stato mandato al PC.").end()
    s.label('pieno').msg("PITTORE: Non hai posto né in squadra né nel PC. Tengo io SMEARGLE: torna quando avrai spazio.").end()
    s.label('done').msg("PITTORE: Ho finito il ritratto della fontana. Prenditi cura di SMEARGLE!").end()
    E.add_object(CESENA, 32, 24, 48, s.save(), move=9 + 0)              # 9: guarda a sinistra (verso la fontana)
    OUT['pennelli'] = dict(flags=[hex(f) for f in flags], fatto=hex(done))


# ------------------------------------------------------------------ L'enigma dei tre codici (Biblioteca Malatestiana)
def tre_codici():
    pool = E.pool()
    L1, L2, LOK, LDONE = (pool.flag('codici %s' % k) for k in ('primo', 'secondo', 'ordine giusto', 'MT17 data'))
    codici = [  # (posizione del pluteo, ordine, testo)
        ((20, 17), 1, "Codice di Isidoro, ETYMOLOGIAE.\nCopiato nell'anno MCDXLVII."),
        ((2, 9), 2, "Codice di Agostino, DE CIVITATE DEI.\nCopiato nell'anno MCDLII."),
        ((5, 25), 3, "Codice di Plinio, NATURALIS HISTORIA.\nCopiato nell'anno MCDLIV."),
    ]
    for (x, y), k, t in codici:
        s = Script('Codice %d' % k).emit(b'\x69')                          # lockall
        s.msg(t)
        s.flag(LOK, 'gia')
        if k == 1:
            s.set(L1).clear(L2).msg("Segni il primo riferimento nel taccuino.").end()
        elif k == 2:
            s.flag(L1, 'ok', present=True).jump('no')
            s.label('ok').set(L2).msg("Segni il secondo riferimento.").end()
        else:
            s.flag(L2, 'ok', present=True).jump('no')
            s.label('ok').set(LOK).msg("Terzo riferimento: l'ordine è completo! Torna dall'archivista.").end()
        s.label('no').clear(L1).clear(L2).msg("Questo riferimento non segue il precedente. Ricomincia dal codice più antico.").end()
        s.label('gia').msg("Hai già messo in ordine i tre codici.").end()
        E.add_bg(BIBLIOTECA, x, y, s.save())
    s = Script('Archivista').emit(b'\x6a\x5a')
    s.flag(LDONE, 'done')
    s.flag(LOK, 'premio')
    s.msg("ARCHIVISTA: Il manoscritto più prezioso si apre solo a chi consulta i tre codici sui plutei.\n\n"
          "Leggili dal più antico al più recente: gli anni sono in numeri romani.").end()
    s.label('premio').msg("ARCHIVISTA: MCDXLVII, MCDLII, MCDLIV: l'ordine è giusto! Il manoscritto custodisce questa MT.")
    s.giveitem(TM17).cmp(0, 'pieno').set(LDONE)
    s.msg("ARCHIVISTA: La MT17 insegna PROTEZIONE: per un turno nessuna mossa colpisce il tuo POKéMON.").end()
    s.label('pieno').msg("ARCHIVISTA: La tua Borsa non ha posto. Torna da me: la custodisco io.").end()
    s.label('done').msg("ARCHIVISTA: I codici della Malatestiana sono incatenati ai plutei da quasi sei secoli.").end()
    E.add_object(BIBLIOTECA, 15, 3, 67, s.save(), move=8)
    OUT['codici'] = [hex(f) for f in (L1, L2, LOK, LDONE)]


# ------------------------------------------------------------------ La luce del rosone (chiesa di Cesena)
def rosone():
    pool = E.pool()
    C1, C2, COK, CDONE = (pool.flag('rosone %s' % k) for k in ('prima', 'seconda', 'ordine giusto', 'pietralunare'))
    vetrate = [
        ((2, 1), "VETRATA: un angelo regge una candela vicino all'altare. In basso: I.\n\nLe vetrate si leggono da sinistra a destra."),
        ((5, 1), "VETRATA: una candela sulla parete di destra, accanto al confessionale. In basso: II."),
        ((12, 1), "VETRATA: una candela sulla parete di sinistra, fra le colonne. In basso: III."),
    ]
    for (x, y), t in vetrate:
        s = Script('Vetrata').emit(b'\x69').msg(t).end()
        E.add_bg(CHIESA, x, y, s.save())
    candele = [([(2, 3), (3, 3)], 1), ([(16, 13)], 2), ([(1, 9)], 3)]
    for cells, k in candele:
        s = Script('Candela %d' % k).emit(b'\x69')
        s.flag(COK, 'gia')
        if k == 1:
            s.set(C1).clear(C2).msg("Accendi la candela vicina all'altare.").end()
        elif k == 2:
            s.flag(C1, 'ok', present=True).jump('no')
            s.label('ok').set(C2).msg("Accendi la candela sulla parete di destra.").end()
        else:
            s.flag(C2, 'ok', present=True).jump('no')
            s.label('ok').set(COK).msg("Accendi la terza candela.\n\nLa luce del rosone scende sull'altare!").end()
        s.label('no').clear(C1).clear(C2).msg("La fiamma si spegne subito. Le candele vanno accese nell'ordine delle vetrate.").end()
        s.label('gia').msg("La candela brucia tranquilla.").end()
        p = s.save()
        for (x, y) in cells: E.add_bg(CHIESA, x, y, p)
    s = Script('Altare').emit(b'\x69')
    s.flag(CDONE, 'vuota')
    s.flag(COK, 'nicchia')
    s.msg("Sopra l'altare il rosone dorato raccoglie la luce. Forse le candele hanno un ordine.").end()
    s.label('nicchia').msg("La luce del rosone illumina una piccola nicchia ai piedi dell'altare. Dentro c'è una pietra.")
    s.giveitem(MOON_STONE).cmp(0, 'pieno').set(CDONE).end()
    s.label('pieno').msg("La Borsa è piena: la pietra resta nella nicchia.").end()
    s.label('vuota').msg("La nicchia ai piedi dell'altare è vuota. La luce del rosone resta bellissima.").end()
    p = s.save()
    for x in (7, 8, 9): E.add_bg(CHIESA, x, 3, p)
    s = Script('Sacrestano').emit(b'\x6a\x5a')
    s.msg("SACRESTANO: Le vetrate di questa chiesa raccontano un ordine. Chi lo rispetta vede la luce del rosone.").end()
    E.add_object(CHIESA, 13, 6, 29, s.save(), move=8)
    OUT['rosone'] = [hex(f) for f in (C1, C2, COK, CDONE)]


# ------------------------------------------------------------------ nome del rivale anche nei salvataggi vecchi
def anagrafe():
    s = Script('Anagrafe rivale').emit(b'\x6a\x5a')
    msgraw(s, vtext("Il tuo amico d'infanzia si chiama ", RIVALE, '.'))
    s.ask("Vuoi cambiare il nome con cui lo chiami?").cmp(0, 'no')
    s.msg("Scrivi il nuovo nome. Se lo lasci vuoto, resta quello di prima.")
    s.emit(b'\x68\x97\x01')                                              # closemessage; fadescreen al nero
    s.emit(b'\x23' + struct.pack('<I', B + NATIVE_NAME + 1) + b'\x27')    # DoNamingScreen; waitstate
    msgraw(s, vtext("D'ora in poi si chiamerà ", RIVALE, '.'))
    s.end()
    s.label('no').ask("Vuoi tornare al nome ALDO?").cmp(0, 'fine')
    for v in range(0x40fc, 0x4100): s.var(v, 0)
    s.msg("Va bene: si chiamerà di nuovo ALDO.").end()
    s.label('fine').end()
    E.add_object(LAB, 10, 10, 126, s.save(), move=8)


def apply(W):
    assert E.W is W
    item_pennello()
    pennelli()
    tre_codici()
    rosone()
    anagrafe()
    OUT['flag'] = E.POOL.taken
    return OUT
