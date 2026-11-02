"""Versione 0.61 - Lotto 2, terza parte: Regi, Deoxys, Jirachi e Mewtwo con la regola comune dei leggendari.

Regola del Lotto 2 per tutti: una sola cattura; dopo fuga (anche per BOATO) o KO il Pokemon resta al suo posto e si
ritenta subito; chi lo ha gia' catturato trova la sala tranquilla. Ogni esito ha il suo testo, in riquadri di due righe.

REGI - Galleria dei Sigilli (Sentiero Faenza-Lugo 35.73 -> 35.74 -> scala 35.75 -> camere 35.76/77/78).
  Dall'analisi (analisi/percorso.py) le tre camere si raggiungono a piedi senza nessuna abilita': FORZA non serve.
  Requisito: 6a medaglia (0x86C), come prima. Flag di cattura indipendenti: REGIROCK 0x620, REGICE 0x622,
  REGISTEEL 0x627. Fino alla 0.60 dopo fuga o KO lo script finiva senza dire nulla. La lotta resta quella dei Regi
  (special 0x13B, con la loro musica).
  Le rovine di Smeraldo (24.6, 24.67, 24.68, flag 0x3A7-0x3A9) restano scollegate: nessuna uscita raggiungibile vi
  porta, quindi non ci sono doppioni in gioco.
DEOXYS - 35.41, col razzo di Ravenna (34.96 bordo est -> 35.40, cartello del razzo); JIRACHI - 35.42, dal portale nel
  mare di Cervia (0.10, oggetto 13, visibile dopo la Lega); MEWTWO - 35.43, grotta di Cesenatico (34.22, uscita 8).
  Restano dopo la Lega (0x864), come da progetto. Cambiano i testi (righe troppo lunghe), il KO ha un testo suo, e
  davanti al Pokemon prima della Lega si spiega cosa serve. Razzo e portale: stessi viaggi, testi in due righe.
  Ingresso della grotta di Mewtwo: l'uscita 8 di 34.22 sta su sabbia e in gioco non scattava (provato a tasti);
  un evento a coordinate sulla stessa casella fa entrare.
I vecchi script degli oggetti diventano un salto ai nuovi (salvataggi fatti dentro le mappe).
"""
import struct
import engine as E
from engine import H, P, B, Script

SESTA, LEGA = 0x86c, 0x864
ATTENDI = "\n\nPuoi riprovare quando vuoi."
LEGG = [
    dict(nome='REGIROCK', mappa=(35, 76), oid=1, specie=401, lv=40, flag=0x620, req=SESTA, regi=True,
         vecchio=0x15c1168, inizio=b'\x6a\x5a\x2b' + H(SESTA),
         req_txt="Il custode di pietra dorme.\nSi desterà quando avrai la\nsesta medaglia, quella di LUGO.",
         intro="Il colosso di pietra non si\nmuove. Poi i suoi occhi si\naccendono, uno a uno!",
         fuga="REGIROCK torna immobile in\nfondo alla camera." + ATTENDI,
         ko="REGIROCK crolla, poi si\nrimette a guardia." + ATTENDI,
         preso="Hai catturato REGIROCK!\nLa camera di pietra tace.",
         gia="La camera di pietra è vuota.\nIl suo custode è con te."),
    dict(nome='REGICE', mappa=(35, 77), oid=1, specie=402, lv=42, flag=0x622, req=SESTA, regi=True,
         vecchio=0x15c1214, inizio=b'\x6a\x5a\x2b' + H(SESTA),
         req_txt="Il custode di brina dorme.\nSi desterà quando avrai la\nsesta medaglia, quella di LUGO.",
         intro="Una brina fitta ricopre il\ncustode. Il suo respiro\ndiventa gelo: REGICE si desta!",
         fuga="REGICE torna immobile in\nfondo alla camera." + ATTENDI,
         ko="REGICE crolla, poi si\nrimette a guardia." + ATTENDI,
         preso="Hai catturato REGICE!\nLa brina si scioglie.",
         gia="La camera di brina è vuota.\nIl suo custode è con te."),
    dict(nome='REGISTEEL', mappa=(35, 78), oid=1, specie=403, lv=45, flag=0x627, req=SESTA, regi=True,
         vecchio=0x15c12c0, inizio=b'\x6a\x5a\x2b' + H(SESTA),
         req_txt="Il custode di metallo dorme.\nSi desterà quando avrai la\nsesta medaglia, quella di LUGO.",
         intro="Il custode di metallo ti\nfissa. Il pavimento vibra:\nREGISTEEL si desta!",
         fuga="REGISTEEL torna immobile in\nfondo alla camera." + ATTENDI,
         ko="REGISTEEL crolla, poi si\nrimette a guardia." + ATTENDI,
         preso="Hai catturato REGISTEEL!\nIl pavimento smette di vibrare.",
         gia="La camera di metallo è vuota.\nIl suo custode è con te."),
    dict(nome='DEOXYS', mappa=(35, 41), oid=1, specie=410, lv=50, flag=0x4eb, req=LEGA, regi=False,
         vecchio=0x15ca7cc, inizio=b'\x6a\x2b' + H(LEGA) + b'\x06',
         req_txt="Un cristallo brilla fra i\ncrateri, ma resta spento.\n\nTorna quando sarai CAMPIONE\ndella LEGA ROMAGNOLA.",
         intro="Fra i crateri brilla un\ncristallo... DEOXYS prende\nforma davanti a te!",
         fuga="DEOXYS torna a fluttuare\nfra i crateri." + ATTENDI,
         ko="DEOXYS si dissolve, poi\nriprende forma fra i crateri." + ATTENDI,
         preso="Hai catturato DEOXYS!\nIl cristallo si spegne.",
         gia="Fra i crateri regna il\nsilenzio."),
    dict(nome='JIRACHI', mappa=(35, 42), oid=1, specie=409, lv=50, flag=0x4ea, req=LEGA, regi=False,
         vecchio=0x15ca898, inizio=b'\x6a\x2b' + H(LEGA) + b'\x06',
         req_txt="Sulla STELLA DEI DESIDERI\ndorme un piccolo Pokémon.\n\nTorna quando sarai CAMPIONE\ndella LEGA ROMAGNOLA.",
         intro="Sulla STELLA DEI DESIDERI\ndorme un piccolo Pokémon.\n\nSi sveglia e sorride:\nè JIRACHI!",
         fuga="JIRACHI torna a dormire\nsulla stella." + ATTENDI,
         ko="JIRACHI crolla, poi torna\na dormire sulla stella." + ATTENDI,
         preso="Hai catturato JIRACHI!\nLa stella brilla piano.",
         gia="La STELLA DEI DESIDERI\nbrilla, vuota."),
    dict(nome='MEWTWO', mappa=(35, 43), oid=1, specie=150, lv=70, flag=0x4ef, req=LEGA, regi=False,
         vecchio=0x15ca964, inizio=b'\x6a\x2b' + H(LEGA) + b'\x06',
         req_txt="In fondo alla grotta uno\nsguardo gelido ti osserva.\n\nTorna quando sarai CAMPIONE\ndella LEGA ROMAGNOLA.",
         intro="In fondo alla grotta, fra i\ncristalli, uno sguardo\ngelido... MEWTWO attacca!",
         fuga="MEWTWO si ritira fra i\ncristalli." + ATTENDI,
         ko="MEWTWO crolla, poi si\nrialza fra i cristalli." + ATTENDI,
         preso="Hai catturato MEWTWO!\nLa grotta torna buia.",
         gia="La grotta è silenziosa."),
]
OUT = {}


def oggetto(W, mappa, oid):
    m = W.rom.map(*mappa); base = W.rom.ptr(m['events'] + 4)
    for i, o in enumerate(m['objects']):
        if o['id'] == oid: return base + i * 24, o
    raise AssertionError('oggetto %d non trovato in %s' % (oid, mappa))


def script_leggendario(c):
    s = Script('Leggendario %s (0.61)' % c['nome'])
    s.emit(b'\x6a')                                              # lock
    s.flag(c['flag'], 'gia')
    s.flag(c['req'], 'requisito', present=False)
    s.emit(b'\x5a')                                              # faceplayer
    s.msg(c['intro'])
    s.emit(b'\xa1' + H(c['specie']) + H(2) + b'\xc5')            # playmoncry, waitmoncry
    s.emit(b'\xb6' + H(c['specie']) + bytes([c['lv']]) + H(0))   # setwildbattle
    s.set(0x8c1)
    if c['regi']: s.emit(b'\x25' + H(0x13b) + b'\x27')           # special StartRegiBattle, waitstate
    else: s.emit(b'\xb7')                                        # dowildbattle
    s.clear(0x8c1)
    s.emit(b'\x26' + H(0x800d) + H(0xb7))                        # esito della lotta
    s.cmp(7, 'preso').cmp(1, 'ko')
    s.msg(c['fuga']).end()
    s.label('ko').msg(c['ko']).end()
    s.label('preso').set(c['flag'])
    s.emit(b'\x53' + H(c['oid'])).msg(c['preso']).end()
    s.label('requisito').msg(c['req_txt']).end()
    s.label('gia').msg(c['gia']).end()
    return s.save()


# Viaggi verso Deoxys e Jirachi: stessi warp di prima, testi in riquadri di due righe.
def viaggio(nome, domanda, warp, prima=None, lancio=None, suono=0x2d, lockall=False):
    s = Script('Viaggio %s (0.61)' % nome)
    s.emit(b'\x69' if lockall else b'\x6a')                     # lockall / lock
    if prima: s.flag(LEGA, 'chiuso', present=False)
    s.ask(domanda).cmp(0, 'no')
    if lancio: s.msg(lancio)
    s.emit(b'\x68' + b'\x2f' + H(suono) + b'\x97\x03')         # closemessage, playse, fadescreen 3
    s.emit(b'\x39' + warp + b'\x27')                           # warp, waitstate
    s.label('no').end()
    if prima: s.label('chiuso').msg(prima).end()
    return s.save()


def apply(W):
    d = W.d
    for c in LEGG:
        at, o = oggetto(W, c['mappa'], c['oid'])
        assert o['script'] == c['vecchio'], (c['nome'], hex(o['script']))
        v = c['vecchio']
        assert bytes(d[v:v + len(c['inizio'])]) == c['inizio'], c['nome']
        p = script_leggendario(c)
        struct.pack_into('<I', d, at + 16, B + p)
        d[v:v + 5] = b'\x05' + P(p)                              # salvataggi fatti dentro la mappa
        OUT[c['nome']] = dict(mappa='%d.%d' % c['mappa'], flag=hex(c['flag']), requisito=hex(c['req']),
                              script=hex(p), prima=hex(v))

    # Razzo di Ravenna (cartello in 35.40) e rientro (due cartelli in 35.41): sono cartelli, basta ripuntarli.
    W_DEOXYS = bytes([35, 41, 0xff]) + H(6) + H(10)
    assert bytes(d[0x1730d3f:0x1730d47]) == b'\x39' + W_DEOXYS
    razzo = viaggio('razzo', "RAZZO ROMAGNA-1: tutto pronto!\nVuoi partire per la LUNA?", W_DEOXYS,
                    prima="RAZZO ROMAGNA-1. Il volo è\nriservato al CAMPIONE della\nLEGA ROMAGNOLA.",
                    lancio="3... 2... 1... Lancio!", suono=0xb2, lockall=True)
    E.set_bg_script((35, 40), 29, 15, razzo)
    W_RIENTRO = bytes([34, 96, 0xff]) + H(62) + H(45)
    assert bytes(d[0x1730d6e:0x1730d76]) == b'\x39' + W_RIENTRO
    rientro = viaggio('rientro dalla Luna', "Il razzo è pronto per il\nrientro. Vuoi tornare a RAVENNA?",
                      W_RIENTRO, suono=0xb2, lockall=True)
    E.set_bg_script((35, 41), 5, 9, rientro)
    E.set_bg_script((35, 41), 6, 9, rientro)

    # Portale di Jirachi (oggetto 13 in 0.10) e ritorno (oggetto 2 in 35.42): oggetti, quindi anche il salto.
    W_JIRACHI = bytes([35, 42, 0xff]) + H(14) + H(17)
    W_CERVIA = bytes([0, 10, 0xff]) + H(54) + H(22)
    for mappa, oid, vecchio, warp, domanda, suono in (
            ((0, 10), 13, 0x1730cca, W_JIRACHI,
             "Sull'acqua gira un vortice di\nstelle: è un portale per il\nMONDO DEI DESIDERI!\n\nVuoi attraversarlo?", 0x2d),
            ((35, 42), 2, 0x1730cef, W_CERVIA,
             "Il portale riporta al mare\ndi CERVIA. Vuoi tornare?", 0x2e)):
        at, o = oggetto(W, mappa, oid)
        assert o['script'] == vecchio and d[vecchio] == 0x6a, (mappa, hex(o['script']))
        assert d.find(b'\x39' + warp, vecchio, vecchio + 0x30) > 0, mappa
        p = viaggio('portale %d.%d' % mappa, domanda, warp, suono=suono)
        struct.pack_into('<I', d, at + 16, B + p)
        d[vecchio:vecchio + 5] = b'\x05' + P(p)
        OUT['portale %d.%d' % mappa] = dict(script=hex(p), prima=hex(vecchio))
    OUT['razzo'] = dict(andata=hex(razzo), rientro=hex(rientro))

    # Ingresso della grotta di Mewtwo (34.22, uscita 8 a 48,33): l'uscita sta su una casella di sabbia (comportamento
    # 0x21) e Smeraldo fa scattare le uscite solo su porte, scale e frecce: in gioco non si entrava (provato a tasti).
    # Un evento a coordinate sulla stessa casella porta dentro; la variabile temporanea 0x400F vale 0 a ogni ingresso
    # nella mappa (come al bordo est di Ravenna). Si atterra una casella sopra l'uscita a freccia di 35.43.
    m = W.rom.map(34, 22); w8 = m['warps'][8]
    assert (w8['x'], w8['y'], w8['group'], w8['num']) == (48, 33, 35, 43), w8
    assert not any((c['x'], c['y']) == (48, 33) for c in m['coords'])
    s = Script('Ingresso grotta di Mewtwo (0.61)')
    s.emit(b'\x69' + b'\x2f' + H(9) + b'\x97\x01')             # lockall, playse SE_EXIT, fadescreen 1 (al nero)
    s.emit(b'\x3a' + bytes([35, 43, 0xff]) + H(12) + H(20) + b'\x27')    # warpsilent 35.43 (12,20), waitstate
    s.end()
    entra = s.save()
    coords = list(m['coords']) + [dict(x=48, y=33, elev=0, var=0x400f, val=0, script=entra)]
    W.set_events(34, 22, coords=coords)
    OUT['ingresso Mewtwo'] = dict(mappa='34.22', casella=(48, 33), script=hex(entra))
    return OUT
