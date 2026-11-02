"""Versione 0.60 - Lotto 2, seconda parte: Kyogre e uccelli leggendari prima della Lega.

Fino alla 0.59 i quattro script controllavano per primo "Lega vinta" (flag 0x864). Tolto quel controllo,
restano le condizioni della storia:
  - KYOGRE (fondale di Rimini 35.37, si arriva dal cartello dell'Area Marina 34.44 con 8 medaglie, poi SURF e SUB):
    enigma dei piloni (variabile 0x40E9 = 2, persistente), 8a medaglia (0x86E: e' il momento in cui si ha SUB,
    consegnata in 35.26 con l'8a medaglia). Cattura: flag 0x4E1 e 0x4E0 (0x4E0 nasconde l'oggetto; lo script comune
    di ritorno al campo lo rimette solo con 0x86E e senza 0x4E1).
  - ARTICUNO 35.31, ZAPDOS 35.32, MOLTRES 35.33 (Santuari del Crinale, da Via Vittoria 35.28, prima della Lega):
    enigma delle rune (variabile temporanea 0x400D = 2, 2, 3: si azzera a ogni ingresso), 8a medaglia.
    Cattura: 0x4CD, 0x4CE, 0x4CF (le stesse di prima: chi li ha gia' presi non li ritrova).
Ogni script nuovo: cattura -> flag e oggetto rimosso; KO -> testo e nuovo tentativo; fuga -> testo e nuovo tentativo
(il Pokemon resta al suo posto, come provato per i cani nella 0.59). Corretto un difetto degli uccelli: dopo un KO
il testo "si ritira" veniva sostituito da "santuario tornato tranquillo" (mancava la callstd).
Testi in riquadri di due righe. Il vecchio script (col controllo della Lega) diventa un salto al nuovo, per i
salvataggi fatti dentro queste mappe.
"""
import struct
import engine as E
from engine import H, P, B, Script

LEGA = 0x864
OTTAVA = 0x86e
LEGG = [
    dict(nome='KYOGRE', mappa=(35, 37), oid=1, specie=404, lv=70, flags=[0x4e1, 0x4e0], var=0x40e9, valore=2,
         vecchio=0x15ca6c8,
         gia="Il santuario è tranquillo.\nHai già incontrato il suo\ncustode.",
         indizio="Il santuario è protetto da\ndue risonanze.\n\nCerca il pilone ovest e poi\nquello est: le correnti hanno\nuna via anche a nord.",
         medaglie="Il richiamo del leggendario\nresta lontano.\n\nCompleta le otto palestre\ndella Romagna.",
         intro="Tra i piloni spezzati\ndell'ISOLA DELLE ROSE dorme\nun Pokémon gigantesco...\n\nKYOGRE apre gli occhi!",
         fuga="KYOGRE si riadagia sul\nfondale.\n\nPuoi riprovare quando vuoi.",
         ko="KYOGRE crolla, poi si\nriadagia sul fondale.\n\nPuoi riprovare quando vuoi.",
         preso="Hai catturato KYOGRE!\nIl mare torna calmo."),
    dict(nome='ARTICUNO', mappa=(35, 31), oid=1, specie=144, lv=52, flags=[0x4cd], var=0x400d, valore=2,
         vecchio=0x15ca3ec,
         gia="Il custode ti ha riconosciuto.\nIl santuario è tranquillo.",
         indizio="Il sigillo protegge ARTICUNO.\n\nPrima ascolta il vento, poi\nlascia che il gelo ne\ncustodisca il soffio.",
         medaglie="Questo santuario accoglie solo\nchi ha tutte le medaglie.",
         intro="ARTICUNO reagisce alla tua\npresenza. La sfida comincia!",
         fuga="ARTICUNO si allontana, poi\ntorna sul suo trespolo.\n\nPuoi riprovare quando vuoi.",
         ko="ARTICUNO crolla, poi si\nrialza nel santuario.\n\nPuoi riprovare quando vuoi.",
         preso="ARTICUNO ha scelto di\nviaggiare con te!"),
    dict(nome='ZAPDOS', mappa=(35, 32), oid=1, specie=145, lv=52, flags=[0x4ce], var=0x400d, valore=2,
         vecchio=0x15ca4d8,
         gia="Il custode ti ha riconosciuto.\nIl santuario è tranquillo.",
         indizio="Il sigillo protegge ZAPDOS.\n\nCollega la bobina al richiamo\ndel cielo. La messa a terra\ninterrompe il circuito.",
         medaglie="Questo santuario accoglie solo\nchi ha tutte le medaglie.",
         intro="ZAPDOS reagisce alla tua\npresenza. La sfida comincia!",
         fuga="ZAPDOS si allontana, poi\ntorna sul suo trespolo.\n\nPuoi riprovare quando vuoi.",
         ko="ZAPDOS crolla, poi si\nrialza nel santuario.\n\nPuoi riprovare quando vuoi.",
         preso="ZAPDOS ha scelto di\nviaggiare con te!"),
    dict(nome='MOLTRES', mappa=(35, 33), oid=1, specie=146, lv=52, flags=[0x4cf], var=0x400d, valore=3,
         vecchio=0x15ca5d0,
         gia="Il custode ti ha riconosciuto.\nIl santuario è tranquillo.",
         indizio="Il sigillo protegge MOLTRES.\n\nDal calore più piccolo al più\ngrande: brace, fiamma e sole.",
         medaglie="Questo santuario accoglie solo\nchi ha tutte le medaglie.",
         intro="MOLTRES reagisce alla tua\npresenza. La sfida comincia!",
         fuga="MOLTRES si allontana, poi\ntorna sul suo trespolo.\n\nPuoi riprovare quando vuoi.",
         ko="MOLTRES crolla, poi si\nrialza nel santuario.\n\nPuoi riprovare quando vuoi.",
         preso="MOLTRES ha scelto di\nviaggiare con te!"),
]
OUT = {}


def oggetto(W, mappa, oid):
    m = W.rom.map(*mappa); base = W.rom.ptr(m['events'] + 4)
    for i, o in enumerate(m['objects']):
        if o['id'] == oid: return base + i * 24, o
    raise AssertionError('oggetto %d non trovato in %s' % (oid, mappa))


def script_leggendario(c):
    s = Script('Leggendario %s (0.60)' % c['nome'])
    s.emit(b'\x6a')                                              # lock
    s.flag(c['flags'][0], 'gia')
    s.cmp(c['valore'], 'aperto', 1, var=c['var'])
    s.msg(c['indizio']).end()
    s.label('aperto').flag(OTTAVA, 'medaglie', present=False)
    s.emit(b'\x5a')                                              # faceplayer
    s.msg(c['intro'])
    s.emit(b'\xa1' + H(c['specie']) + H(2) + b'\xc5')            # playmoncry, waitmoncry
    s.emit(b'\xb6' + H(c['specie']) + bytes([c['lv']]) + H(0))   # setwildbattle
    s.set(0x8c1).emit(b'\xb7').clear(0x8c1)                      # dowildbattle
    s.emit(b'\x26' + H(0x800d) + H(0xb7))                        # esito della lotta
    s.cmp(7, 'preso').cmp(1, 'ko')
    s.msg(c['fuga']).end()
    s.label('ko').msg(c['ko']).end()
    s.label('preso')
    for f in c['flags']: s.set(f)
    s.emit(b'\x53' + H(c['oid'])).msg(c['preso']).end()
    s.label('medaglie').msg(c['medaglie']).end()
    s.label('gia').msg(c['gia']).end()
    return s.save()


def apply(W):
    d = W.d
    for c in LEGG:
        at, o = oggetto(W, c['mappa'], c['oid'])
        assert o['script'] == c['vecchio'], (c['nome'], hex(o['script']))
        v = c['vecchio']
        assert bytes(d[v:v + 4]) == b'\x6a\x2b' + H(LEGA), c['nome']
        p = script_leggendario(c)
        struct.pack_into('<I', d, at + 16, B + p)
        d[v:v + 5] = b'\x05' + P(p)                              # salvataggi fatti dentro la mappa
        OUT[c['nome']] = dict(mappa='%d.%d' % c['mappa'], flag=[hex(f) for f in c['flags']],
                              enigma='%s=%d' % (hex(c['var']), c['valore']), script=hex(p), prima=hex(v))
    return OUT
