"""Versione 0.69 - Lotto 3: barriere e testi lunghi.

Barriere: l'inventario (analisi/barriere.py, relazione 0.69 §2) non ha trovato requisiti impossibili; cambiano solo
i loro testi dove erano spezzati male.

Testi (solo testi degli script delle mappe; nessuna flag, variabile, mappa):
  1. RISCRITTI (testo nuovo, il vecchio resta dov'e' e non e' piu' letto): ogni istruzione loadword degli script
     di tutte le mappe che punta a un testo uguale al vecchio viene ripuntata al nuovo. Sono:
     - gli 8 testi che scorrevano una terza riga nello stesso riquadro (\\l);
     - le due direzioni sbagliate del Fumaiolo (guida del Cuore, incisione delle Sorgenti) e i due "Hai spento nodo";
     - le guide "Ingresso per ... Vuoi che ti accompagni lungo il collegamento?" e i loro "non e ancora disponibile";
     - le barriere di Lido di Savio (starter, Ravenna), spezzate a meta' frase.
  2. ACCENTI (sul posto, un byte per uno): parole senza accento (piu, gia, citta, puo, c'e, ...) e la "e" verbo
     riconosciuta dal contesto (non e, e stato, palestra e a, ...). Regole sotto; il numero di correzioni e' fissato.
I testi nuovi stanno in 2 righe da 30 caratteri per riquadro; i nomi ({GIOCATORE}, {S1}...) contano 7.
"""
import struct, textwrap, re
import romlib, scr
import engine as E
from engine import ALPHA, B

OUT = {}
SEP = {0x00, 0xfe, 0xfa, 0xfb}
SEGNAPOSTO = {'{GIOCATORE}': b'\xfd\x01', '{S1}': b'\xfd\x02', '{S2}': b'\xfd\x03', '{S3}': b'\xfd\x04', '{RIVALE}': b'\xfd\x06'}

# (testo vecchio come lo stampa scr.text, testo nuovo, quante istruzioni loadword devono puntarci)
RISCRITTI = [
    ("Nelle giornate limpide, al largo, / appare un'isola che sparisce subito. / La chiamano ISOLA MIRAGGIO. / Dicono che solo i CAMPIONI\\lriescano a raggiungerla...",
     "Nei giorni limpidi, al largo,\nappare un'isola che sparisce.\n\nLa chiamano ISOLA MIRAGGIO.\n\nDicono che solo i CAMPIONI riescano a raggiungerla...", 1),
    ("Prendi anche queste due pietre: / il fuoco delle saline al tramonto\\le il tuono dei temporali sul mare.",
     "Prendi anche queste due pietre: il fuoco delle saline al tramonto e il tuono dei temporali sul mare.", 1),
    ("Attenzione: la porta rossa è la / STANZA CHEATER! / Dentro c'è un venditore che regala / MASTER BALL e CARAMELLE RARE.\\lEntra solo se vuoi barare!",
     "Attenzione: la porta rossa è la STANZA CHEATER!\n\nDentro, un venditore regala MASTER BALL e CARAMELLE RARE.\n\nEntra solo se vuoi barare!", 1),
    ("Sono il SIGNORE della PENSIONE. / Mi prendo cura dei preziosi POKéMON\\ldegli ALLENATORI. / Se vuoi farne allevare uno, / parla con mia moglie.",
     "Sono il SIGNORE della PENSIONE.\n\nMi prendo cura dei POKéMON degli ALLENATORI.\n\nSe vuoi farne allevare uno, parla con mia moglie.", 1),
    ("Ah, sei tu! Stavamo allevando i tuoi / POKéMON e, che sorpresa... / {05} comparso un UOVO! / Non sappiamo come ci sia finito,\\lma era con i tuoi POKéMON. / Lo vuoi, vero?",
     "Ah, sei tu! Stavamo allevando i tuoi POKéMON e...\n\nChe sorpresa! È comparso un UOVO!\n\nNon sappiamo da dove arrivi, ma era con i tuoi POKéMON.\n\nLo vuoi, vero?", 1),
    ("A proposito, il tuo {fd}{02} / sembrava andare d'accordo con\\lil {fd}{04} di {fd}{03}. / Mi è sembrato persino che gli / portasse una LETTERA.",
     "A proposito, il tuo {S1} andava d'accordo con il {S3} di {S2}.\n\nMi è sembrato persino che gli portasse una LETTERA.", 1),
    ("OSTE: Hai battuto tutti i miei / clienti! Te lo sei meritato. / Questo SNORLAX dorme qui da anni e / mangia più piadine di tutta Cervia.\\lPortalo con te!",
     "OSTE: Hai battuto tutti i miei clienti! Te lo sei meritato.\n\nQuesto SNORLAX dorme da anni e mangia più di tutta Cervia.\n\nPortalo con te!", 1),
    ("MENU DEL GIORNO / Passatelli, strozzapreti, piadina\\lcon squacquerone e Sangiovese.",
     "MENU DEL GIORNO\nPassatelli, strozzapreti,\n\npiadina con squacquerone e Sangiovese.", 1),
    # Fumaiolo: direzioni della mappa nuova della 0.66 (cartello del santuario 35.13: "Nord, da sinistra: PASSO DEI
    # DRAGHI, sala di BASSI, nodo dell'ARGILLA. Ovest, oltre il lago: nodo del SALE.")
    ("GUIDA: Le sorgenti sono salve. / Puoi raggiungere Bagno di / Romagna dal passo a sud-est / del santuario.",
     "GUIDA: Le sorgenti sono salve.\n\nPer Bagno di Romagna prendi il PASSO DEI DRAGHI: nella Grotta delle Sorgenti è la prima porta a nord, a sinistra.", 1),
    ("L'incisione racconta: quando / la terra trema, le sorgenti / parlano. Due nodi alimentano / il cuore. Prima il sale a / ovest, poi l'argilla a est.",
     "INCISIONE: Quando la terra trema, le sorgenti parlano.\n\nDue nodi alimentano il cuore:\n\nSALE: a ovest, oltre il lago.\nARGILLA: a nord, a destra.", 1),
    ("Hai spento nodo del sale. Ora / controlla l'altro settore. Con / entrambi i nodi spenti puoi / entrare da Bassi.",
     "Nodo del SALE spento!\nOra controlla l'altro settore.\n\nCon entrambi i nodi spenti puoi entrare da BASSI.", 2),
    ("Hai spento nodo dell'argilla. / Ora controlla l'altro settore. / Con entrambi i nodi spenti / puoi entrare da Bassi.",
     "Nodo dell'ARGILLA spento!\nOra controlla l'altro settore.\n\nCon entrambi i nodi spenti puoi entrare da BASSI.", 2),
    # guide dei collegamenti (Forli' e Sentiero del Savio per Ridracoli, Rimini per San Marino, Imola per l'Autodromo)
    ("Il passaggio per sentiero di / Ridracoli non e ancora / disponibile. Prima conquista / la settima medaglia a Imola.",
     "Il sentiero per RIDRACOLI è ancora chiuso.\n\nTorna con la settima medaglia, quella di IMOLA.", 1),
    ("Il passaggio per collegamento / per Ridracoli non e ancora / disponibile. Prima conquista / la settima medaglia a Imola.",
     "Il sentiero per RIDRACOLI è ancora chiuso.\n\nTorna con la settima medaglia, quella di IMOLA.", 1),
    ("Ingresso per sentiero di / Ridracoli. Vuoi che ti / accompagni lungo il / collegamento?",
     "Sono la guida per la diga di RIDRACOLI.\n\nVuoi che ti accompagni?", 1),
    ("Ingresso per collegamento per / Ridracoli. Vuoi che ti / accompagni lungo il / collegamento?",
     "Sono la guida per la diga di RIDRACOLI.\n\nVuoi che ti accompagni?", 1),
    ("Il passaggio per San Marino e / Monte Titano non e ancora / disponibile. Torna dopo la / Lega.",
     "La strada per SAN MARINO e il MONTE TITANO è ancora chiusa.\n\nTorna dopo la LEGA.", 1),
    ("Ingresso per San Marino e / Monte Titano. Vuoi che ti / accompagni lungo il / collegamento?",
     "Sono la guida per SAN MARINO e il MONTE TITANO.\n\nVuoi che ti accompagni?", 1),
    ("Ingresso per Autodromo di / Imola. Vuoi che ti accompagni / lungo il collegamento?",
     "Sono la guida per l'AUTODROMO di IMOLA.\n\nVuoi che ti accompagni?", 1),
    # barriere di Lido di Savio (eventi a coordinate)
    ("Un momento! Non puoi lasciare / il Lido / senza un Pokémon. Passa dal / laboratorio!",
     "Un momento! Non puoi lasciare il Lido senza un POKéMON.\n\nPassa dal laboratorio!", 10),
    ("Il passaggio verso Ravenna è / chiuso. / Serve la quinta medaglia per / passare.",
     "Verso RAVENNA non si passa:\nserve la quinta medaglia.", 2),
]

# ---- accenti
PAROLE = {'piu': 'più', 'gia': 'già', 'perche': 'perché', 'poiche': 'poiché', 'citta': 'città', 'puo': 'può',
          'cosi': 'così', 'pero': 'però', 'normalita': 'normalità', 'arrivera': 'arriverà', 'sara': 'sarà',
          "c'e": "c'è", 'verita': 'verità', 'liberta': 'libertà', 'attivita': 'attività', 'qualita': 'qualità',
          'quantita': 'quantità', 'proprieta': 'proprietà', 'PIU': 'PIÙ', 'GIA': 'GIÀ', 'CITTA': 'CITTÀ'}
# accento scritto con l'apostrofo (e' piu' gia' ...): la parola si corregge e il testo si accorcia di un byte
APOSTROFO = {"e'": 'è', "piu'": 'più', "gia'": 'già', "citta'": 'città', "proprieta'": 'proprietà', "sara'": 'sarà',
             "Portero'": 'Porterò', "Avvisero'": 'Avviserò', "continuera'": 'continuerà', "c'e'": "c'è"}
DOPO_E = {'stato', 'stata', 'stati', 'gia', 'già', 'pronto', 'pronta', 'tuo', 'tua', 'tranquillo', 'tranquilla',
          'rotolata', 'fuggito', 'cronometrato', 'libero', 'libera', 'salvo', 'puro', 'pura'}
PRIMA_E = {'non', 'Non', 'palestra', 'contenitore', 'energia', 'MASINI', 'Questa'}
# coppie (parola prima, parola dopo) dove "e" e' il verbo; da sole sarebbero ambigue ("Ball e strumenti",
# "pigro e piu raro", "Visita Mirabilandia e il Safari", "Riposati e salva")
TRA_E = {('Ball', 'ancora'), ('Mirabilandia', 'al'), ('SAVIO', 'piu'), ('ritorno', 'sempre')}
PRIMA_PAROLA = {('Leonardo', 'studio'): 'studiò'}
ACCENTI_ATTESI, APOSTROFI_ATTESI = 110, 22     # letti uno per uno nella prova (relazione 0.69 §3)
_PUNT = '.,!?:;…"\'()-'


def codifica(t):
    out = bytearray()
    i = 0
    while i < len(t):
        for k, v in SEGNAPOSTO.items():
            if t.startswith(k, i): out += v; i += len(k); break
        else:
            out.append(ALPHA[t[i]]); i += 1
    return bytes(out)


def larghezza(s):
    for k in SEGNAPOSTO: s = s.replace(k, 'X' * 7)
    return len(s)


def impagina(t, width=30):
    """Come engine.W.text, ma i segnaposto contano 7 caratteri."""
    pages = []
    for para in t.split('\n\n'):
        lines = []
        for riga in para.split('\n'):
            cur = ''
            for w in riga.split(' '):
                prova = (cur + ' ' + w) if cur else w
                if cur and larghezza(prova) > width: lines.append(cur); cur = w
                else: cur = prova
            lines.append(cur)
        pages += ['\n'.join(lines[i:i + 2]) for i in range(0, len(lines), 2)]
    return '\r'.join(pages)


def riferimenti(W):
    """Istruzioni loadword (0x0f 0x00 puntatore) in tutta la ROM: indirizzo del puntatore -> testo.
    Si cerca nei byte e non seguendo gli script: il disassemblatore si ferma su alcuni comandi della hack (per
    esempio lo script dell'OSTE di Cervia 35.35). Per i testi riscritti il confronto col testo vecchio esatto
    esclude i falsi positivi; per gli accenti valgono solo i testi che contengono le parole delle regole."""
    d = bytes(W.d); out = {}
    for m in re.finditer(rb'(?=\x0f\x00(....))', d, re.S):
        v = struct.unpack('<I', m.group(1))[0]
        if B <= v < B + len(d): out[m.start() + 2] = v - B
    return out


def accenti(d, p):
    """Correzioni sul posto nel testo che inizia a p: -> lista (offset, vecchio, nuovo, parola)."""
    e = d.index(0xff, p); raw = d[p:e]
    parole, cur, ini, i = [], bytearray(), 0, 0
    while i <= len(raw):
        b = raw[i] if i < len(raw) else 0
        if b in SEP or b in (0xfc, 0xfd):
            if cur: parole.append((ini, bytes(cur)))
            salto = 2 if b in (0xfc, 0xfd) else 1
            cur = bytearray(); i += salto; ini = i
        else:
            cur.append(b); i += 1
    CH = {v: k for k, v in ALPHA.items()}
    txt = [(o, ''.join(CH.get(b, '?') for b in w)) for o, w in parole]
    nuc = [w.strip(_PUNT) for _, w in txt]
    cambi = []
    for j, (o, w) in enumerate(txt):
        n = nuc[j]; lead = len(w) - len(w.lstrip(_PUNT))
        nuovo = None
        if n in PAROLE: nuovo = PAROLE[n]
        elif n == 'e' and w == 'e' and ((j + 1 < len(nuc) and nuc[j + 1] in DOPO_E) or (j > 0 and nuc[j - 1] in PRIMA_E)
                                        or (0 < j < len(nuc) - 1 and (nuc[j - 1], nuc[j + 1]) in TRA_E)): nuovo = 'è'
        elif j > 0 and (nuc[j - 1], n) in PRIMA_PAROLA: nuovo = PRIMA_PAROLA[(nuc[j - 1], n)]
        if nuovo:
            assert len(nuovo) == len(n)
            for i, (a, b) in enumerate(zip(n, nuovo)):
                if a != b: cambi.append((p + o + lead + i, ALPHA[a], ALPHA[b], n + '->' + nuovo, p))
    return cambi


def apply(W):
    d = W.d
    rif = riferimenti(W)
    # 1. riscritti
    fatti = []
    db = bytes(d); testi = {}
    for t in set(rif.values()):
        if db[t - 1] == 0xff or db[t - 1] == 0x00 or True:
            e = db.find(b'\xff', t, t + 600)
            if e > 0: testi[t] = db[t:e]
    cache = {}
    def come_testo(t):
        if t not in cache: cache[t] = scr.text(db, t, 600).replace('\\n', ' / ')
        return cache[t]
    for vecchio, nuovo, quanti in RISCRITTI:
        dove = [a for a, t in rif.items() if t in testi and len(testi[t]) >= len(vecchio) // 2 and come_testo(t) == vecchio]
        assert len(dove) == quanti, (vecchio[:40], len(dove), quanti)
        nt = W.alloc(codifica(impagina(nuovo)) + b'\xff', 'testo ' + nuovo[:30])
        for a in dove:
            struct.pack_into('<I', d, a, B + nt); rif[a] = nt
        fatti.append(dict(vecchio=vecchio, nuovo=nuovo, istruzioni=len(dove), indirizzo=hex(nt)))
    OUT['riscritti'] = fatti
    # 2. accenti, nei testi ancora letti dagli script (solo puntatori a un testo vero: niente {..} di comandi)
    validi = []; db = bytes(d)
    for t in sorted(set(rif.values())):
        v = re.sub(r'\{fd\}\{..\}|\{0[1569d]\}|\{11\}', '', scr.text(db, t, 600))
        if '{' not in v and d.find(b'\xff', t, t + 600) > 0: validi.append(t)
    apo = []
    for t in validi:
        e = d.index(0xff, t); raw = bytes(d[t:e]); nuovo = raw
        for k, v in APOSTROFO.items():
            vk, vv = codifica(k), codifica(v)
            nuovo = re.sub(rb'(?<![^\x00\xfe\xfa\xfb])' + re.escape(vk) + rb'(?=[\x00\xfe\xfa\xfb]|$)', vv, nuovo)
        if nuovo != raw:
            d[t:e + 1] = nuovo + b'\xff' * (e + 1 - t - len(nuovo))
            apo.append(dict(testo=hex(t), prima=scr.text(raw + b'\xff', 0, 600), dopo=scr.text(nuovo + b'\xff', 0, 600)))
    OUT['apostrofi'] = apo
    assert len(apo) == APOSTROFI_ATTESI, len(apo)
    cambi = []; db = bytes(d)
    for t in validi:
        cambi += accenti(db, t)
    cambi = sorted(set(cambi))
    for off, a, b, _, _ in cambi:
        assert d[off] == a
        d[off] = b
    OUT['accenti'] = [dict(indirizzo=hex(o), parola=w, testo=hex(t)) for o, _, _, w, t in cambi]
    assert len(cambi) == ACCENTI_ATTESI, len(cambi)
    return OUT
