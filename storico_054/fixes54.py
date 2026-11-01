"""0.54: correzione del blocco "nel nulla" dopo la lotta col rivale in laboratorio.

Nella 0.52 la schermata "NOME DEL RIVALE?" si apriva DOPO che il rivale aveva raggiunto il giocatore
(script 0x2cffc9: getplayerxy + applymovement del rivale). Al ritorno dalla schermata la mappa viene
ricaricata e, se il giocatore aveva preso la Poke Ball di destra (casella 8,9), la telecamera scorreva
da sola verso destra per 20 caselle, fuori dal laboratorio: schermo nero e nessun comando.
Con le altre due Poke Ball non succedeva (i test della 0.52/0.53 usavano quella centrale).

Causa (verificata in emulatore, mGBA e VBA-M): al ritorno dalla schermata la mappa viene ricaricata
e la Poke Ball presa non esiste piu'; gSelectedObjectEvent (0x03005df0) resta pero' l'indice di quella
Poke Ball. Con la Poke Ball di destra quell'indice, dopo la ricarica, ha uno sprite che coincide con
quello della telecamera: il "faceplayer" all'inizio della lotta lo altera e la telecamera scorre
a destra di 20 caselle, fuori dal laboratorio (il giocatore resta fermo a 8,9). Mettere
gSelectedObjectEvent sul rivale (id locale 6) elimina il problema.

Ora l'ordine e': nome del rivale (con chiusura del riquadro e dissolvenza al nero, come il gioco
originale) e SOLO DOPO il rivale cammina fino al giocatore. Se il nome e' gia' scelto, come prima.
"""
import struct
B = 0x08000000
LAB_CALL = 0x2cbbbe            # call <hook 0.52>
RIVAL_WALK = 0x2cffc9          # script originale: il rivale raggiunge il giocatore
RIVAL_VAR = 0x40fc
NATIVE_HEAD = bytes.fromhex("10b582b00020009008480190")
# gSelectedObjectEvent = indice dell'oggetto attivo con id locale 6 (il rivale)
SELECT_RIVAL = bytes.fromhex("10b5094800210278d20705d0027a062a02d1064b197003e0013124301029f2db10bc01bc004700bf50730302f05d0003")


def apply(W):
    d = W.d; out = {}
    assert d[LAB_CALL] == 0x04
    old = struct.unpack_from('<I', d, LAB_CALL + 1)[0] - B
    # vecchio hook 0.52: call RIVAL_WALK; compare 0x40fc,0; goto_if eq ask; return; ask: loadword msg; callstd 4; callnative nat; waitstate; return
    assert d[old] == 0x04 and struct.unpack_from('<I', d, old + 1)[0] == B + RIVAL_WALK, 'hook 0.52 inatteso'
    lw = bytes(d).find(b'\x0f\x00', old, old + 0x20)
    msg = struct.unpack_from('<I', d, lw + 2)[0]
    nat = bytes(d).find(NATIVE_HEAD)
    assert nat > 0 and bytes(d).find(NATIVE_HEAD, nat + 1) < 0
    assert bytes(d).find(b'\x23' + struct.pack('<I', B + nat + 1) + b'\x27', old, old + 0x40) > 0
    sel = W.alloc(SELECT_RIVAL, 'seleziona rivale 0.54')
    s = bytearray()
    s += b'\x21' + struct.pack('<HH', RIVAL_VAR, 0)                       # compare 0x40fc, 0
    j = len(s); s += b'\x06\x01' + b'\0\0\0\0'                           # goto_if eq ask
    s += b'\x04' + struct.pack('<I', B + RIVAL_WALK) + b'\x03'           # call walk; return
    ask = len(s)
    s += b'\x0f\x00' + struct.pack('<I', msg) + b'\x09\x04'              # loadword; callstd MSGBOX_DEFAULT
    s += b'\x68' + b'\x97\x01'                                          # closemessage; fadescreen FADE_TO_BLACK
    s += b'\x23' + struct.pack('<I', B + nat + 1) + b'\x27'              # callnative DoNamingScreen; waitstate
    s += b'\x23' + struct.pack('<I', B + sel + 1)                        # callnative: oggetto selezionato = rivale
    s += b'\x04' + struct.pack('<I', B + RIVAL_WALK) + b'\x03'           # call walk; return
    p = W.alloc(b'\0' * len(s), 'nome rivale 0.54')
    struct.pack_into('<I', s, j + 2, B + p + ask)
    d[p:p + len(s)] = s
    struct.pack_into('<I', d, LAB_CALL + 1, B + p)
    out['hook'] = hex(p); out['vecchio'] = hex(old)
    return out
