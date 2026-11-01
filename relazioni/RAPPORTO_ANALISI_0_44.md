# Pokémon Romagna 0.44 — rapporto di analisi (fase 3)

ROM letta: `Pokemon_Romagna_0_44.gba` (caricata dall'utente), SHA-256
`f62af7e22095d85835ad9a66523ca2678d5040d34977ce5a83418f4b389f777a`.

Questa ROM NON è stata costruita da me. Rispetto alla mia 0.43 (casinò) cambiano:
2 mappe esistenti (34.19, 34.39) e 10 mappe nuove (35.60–35.69). Sorgenti e builder
della 0.44 non sono disponibili: tutto ciò che segue è letto dalla ROM.

## 1. Grafo reale (letto da warp e connessioni)

Le città sono unite da warp di bordo, non da connessioni native (nessuna mappa ha connessioni
tranne il Safari). Gruppo 34 = Romagna, gruppo 35 = estensioni.

    Cesena 34.17 → 34.19 → Capocolle 35.60 → Forlimpopoli 35.61 → 34.39 → Forlì 34.68
    Forlì 34.68 → 34.84 (argine, 56x32, acqua con Surf) → Faenza 34.85   [Faenza: nessun'altra uscita]
    Lido di Savio 0.9 → 34.93 pineta → Ravenna 34.94 → Ravenna 34.96
    Ravenna 34.96 (porta STAZIONE, warp 14 a (68,28)) → Lugo 34.110 (warp 0 a (37,59))   [salto diretto]
    Lugo 34.110 → 34.113 (nord) ; Lugo 34.110 (0,29) → 35.0 → Imola 35.1

## 2. I quattro tratti

| Tratto | Stato nella 0.44 | Problema | Priorità |
|---|---|---|---|
| Cesena–Forlì | Esiste: 34.19, Capocolle 35.60 (con Babbi e interni 35.62–63), Forlimpopoli 35.61 (interni 35.64–69), 34.39 | Da collaudare. Babbi ha 2 interni (spec: 3). Forlimpopoli senza tabella incontri (città: ok). | media |
| Forlì–Faenza | Solo 34.84, una mappa 56x32 con acqua e incontri lv 28–32 | Nessun separatore a filari, nessun bivio, una sola mappa | alta |
| Faenza–Lugo | NON esiste. Faenza è un vicolo cieco; Lugo si raggiunge solo da Ravenna e va verso Imola | Serve cava, due ingressi, blocco fino alla 6ª medaglia | alta |
| Ravenna–Lugo | Un unico warp "STAZIONE": zero cammino | Va sostituito da sentiero a piedi con erba alta | altissima (primo da costruire) |

## 3. Progressione (flag letti dagli script)

- 5ª medaglia: flag 0x86B. Impostata in uno script condiviso della mappa 0.105.
- 6ª medaglia (Lugo): flag 0x86C, impostata in 34.112 (palestra di Lugo). È il flag giusto per aprire la cava.
- 7ª medaglia (Imola): flag 0x86D, impostata in 35.9.
- Ravenna è raggiungibile prima di Lugo (da Lido di Savio, 0.9 → 34.93 → 34.94 → 34.96), senza cava e senza Lugo: nessuna dipendenza circolare.
- La stazione di Ravenna oggi non controlla nessuna medaglia: chi entra a Ravenna può andare subito a Lugo.

## 4. Eventi di Forlimpopoli trovati nella ROM (da verificare giocando)

- Shuckle lv 24 (35.61, oggetto 5, flag evento 0x170). Cromatico: NON verificato.
- Miltank lv 25 (35.63, fabbrica Babbi, oggetto 1). Dono.
- Chansey lv 20 (35.66, Casa Artusi, oggetto 1). Dono.
- Eevee cromatico nel cortile: non trovato dalla scansione. Da verificare.

## 5. Cosa non è stato verificato

Collisioni di Capocolle, tagliata sigillata, ritorno nei due sensi, cromaticità reale, duplicazioni
dopo salvataggio/riavvio, salvataggi della 0.43 su 0.44. Nessun collaudo emulato ancora eseguito sulla 0.44.
