"""Versione 0.59 - Lotto 2, prima parte: Entei, Raikou e Suicune catturabili dalla prima visita a Ravenna.

Decisione: i tre cani restano nel Safari di Ravenna del gruppo 26 (quello a cui porta davvero Ravenna, uscita 10
di 34.94 -> 26.3, ingresso libero e Poke Ball normali) e nei posti dove erano gia':
  - ENTEI   nella Grotta Ardente 35.100 (ingresso dal Safari 26.12), flag di cattura 0x88F;
  - RAIKOU  nel prato d'erba alta di 26.12, flag 0x884;
  - SUICUNE sul lago di 26.13 (si arriva con SURF), flag 0x887.
Fino alla 0.58 il loro script controllava "Lega vinta" (0x864) prima della lotta. Qui l'oggetto punta a uno
script nuovo senza quel controllo. Le flag di cattura non cambiano (sono le stesse del Safari della 0.51, che
resta scollegato): chi li ha gia' catturati non li ritrova, e non nascono doppioni.
Per i salvataggi fatti dentro una di queste mappe (SaveBlock1 tiene una copia degli oggetti con il vecchio
puntatore) il vecchio script diventa un salto al nuovo.
Regola del Lotto 2: una sola cattura; dopo fuga (anche per BOATO) o KO il Pokemon resta al suo posto e si ritenta
subito (provato in emulatore: l'oggetto non sparisce). I testi sono riscritti
in riquadri di due righe.
"""
import struct
import engine as E
from engine import H, P, B, Script

LEGA = 0x864
CANI = [
    # mappa, id oggetto, specie, livello, flag, script della 0.58 (col controllo della Lega), testi
    dict(nome='ENTEI', mappa=(35, 100), oid=1, specie=244, lv=45, flag=0x88f, vecchio=0x15cac40,
         intro="Il calore è insopportabile.\nENTEI si alza e ruggisce!",
         fuga="ENTEI salta fra le rocce,\npoi torna sulla pedana.\n\nPuoi riprovare quando vuoi.",
         ko="ENTEI crolla, poi si rialza\nsulla pedana.\n\nPuoi riprovare quando vuoi.",
         preso="Hai catturato ENTEI!\nLa grotta si raffredda."),
    dict(nome='RAIKOU', mappa=(26, 12), oid=10, specie=243, lv=45, flag=0x884, vecchio=0x15c9b7c,
         intro="Un tuono a ciel sereno!\nRAIKOU balza fuori dall'erba!",
         fuga="RAIKOU sparisce fra l'erba,\npoi torna in mezzo al prato.\n\nPuoi riprovare quando vuoi.",
         ko="RAIKOU crolla, poi si rialza\nfra l'erba alta.\n\nPuoi riprovare quando vuoi.",
         preso="Hai catturato RAIKOU!\nIl cielo sopra il prato\nsi rasserena."),
    dict(nome='SUICUNE', mappa=(26, 13), oid=6, specie=245, lv=45, flag=0x887, vecchio=0x15c9d28,
         intro="L'acqua del lago diventa\nlimpidissima...\n\nSUICUNE ti guarda dalla\nsuperficie!",
         fuga="SUICUNE scivola via, poi\ntorna al centro del lago.\n\nPuoi riprovare quando vuoi.",
         ko="SUICUNE crolla, poi riemerge\ndal lago.\n\nPuoi riprovare quando vuoi.",
         preso="Hai catturato SUICUNE!\nIl lago torna calmo."),
]
OUT = {}


def oggetto(W, mappa, oid):
    m = W.rom.map(*mappa); base = W.rom.ptr(m['events'] + 4)
    for i, o in enumerate(m['objects']):
        if o['id'] == oid: return base + i * 24, o
    raise AssertionError('oggetto %d non trovato in %s' % (oid, mappa))


def script_cane(c):
    s = Script('Cane %s (0.59)' % c['nome'])
    s.emit(b'\x6a')                                            # lock
    s.flag(c['flag'], 'gia')                                    # sicurezza: gia' catturato (l'oggetto e' nascosto)
    s.emit(b'\x5a')                                            # faceplayer
    s.msg(c['intro'])
    s.emit(b'\xa1' + H(c['specie']) + H(2) + b'\xc5')          # playmoncry (verso di lotta), waitmoncry
    s.emit(b'\xb6' + H(c['specie']) + bytes([c['lv']]) + H(0))   # setwildbattle
    s.set(0x8c1).emit(b'\xb7').clear(0x8c1)                      # dowildbattle (come gli script della 0.55)
    s.emit(b'\x26' + H(0x800d) + H(0xb7))                        # specialvar 0x800d = esito della lotta
    s.cmp(7, 'preso')                                            # B_OUTCOME_CAUGHT
    s.cmp(1, 'ko')                                               # B_OUTCOME_WON: KO del leggendario
    s.msg(c['fuga']).end()                                       # fuga del giocatore o del Pokemon
    s.label('ko').msg(c['ko']).end()
    s.label('preso').set(c['flag']).emit(b'\x53' + H(c['oid'])).msg(c['preso']).end()
    s.label('gia').emit(b'\x6b\x02')
    return s.save()


def apply(W):
    d = W.d
    for c in CANI:
        at, o = oggetto(W, c['mappa'], c['oid'])
        assert o['script'] == c['vecchio'], (c['nome'], hex(o['script']))
        assert o['flag'] == c['flag'], (c['nome'], hex(o['flag']))
        v = c['vecchio']                                         # lock; checkflag 0x864; goto_if 1 ...
        assert bytes(d[v:v + 4]) == b'\x6a\x2b' + H(LEGA), c['nome']
        p = script_cane(c)
        struct.pack_into('<I', d, at + 16, B + p)
        # vecchi salvataggi fatti dentro la mappa: SaveBlock1 conserva la copia degli oggetti col puntatore al vecchio
        # script, finche' non si cambia mappa. Il vecchio script diventa un salto a quello nuovo.
        d[v:v + 5] = b'\x05' + P(p)
        OUT[c['nome']] = dict(mappa='%d.%d' % c['mappa'], oggetto=c['oid'], flag=hex(c['flag']), script=hex(p),
                              prima=hex(v))
    return OUT
