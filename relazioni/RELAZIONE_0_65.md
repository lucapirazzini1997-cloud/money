# Pokémon Romagna 0.65: Ridracoli e il GYARADOS rosso (Lotto 3)

**Base:** 0.64, SHA-256 `82ac35d2135894815f412ca51666f31f900e5ab778b1d8838c46bb1bbda27f70`.

**Risultato:** `Pokemon_Romagna_0_65.gba`, SHA-256 `ad1bfa2d6eec44389edbb35a5e802dfe49fb7ede7aa3f5fc1ced63f9baa69a94`.
- Patch BPS 0.64→0.65: `rom/Pokemon_Romagna_0_64_to_0_65.bps` (BPS_BYTE byte), verificata riapplicandola (`consegna.sh`, log in `collaudo/risultati/065/consegna.txt`).
- Modulo: `versioni/v065_ridracoli.py`. La build da zero rifà tutti gli SHA; lo zip senza `out/` ricostruito in una cartella pulita rifà lo stesso SHA (stesso log).
- Lo SHA è in `build.py` dopo il collaudo (§5).
- **Salvataggi compatibili:** stessa mappa (35.51) con layout nuovo e più alta (da 44×34 a 44×62), una variabile nuova (a 0 nei vecchi salvataggi). Un salvataggio vero della 0.64 fatto dentro la vecchia 35.51 carica nella 0.65 e prosegue, in mGBA e in VBA-M (§5).

## 1. Cosa è stato chiesto

In chat, dopo la bozza 1 di Ridracoli:
- Non si capiva come si sale alla diga; in alto a destra tutto era chiuso dagli alberi.
- Sopra si può salire con CASCATA, che si ottiene più avanti, con un evento o qualcosa da trovare.
- I personaggi sembravano messi a caso: ognuno deve avere un ruolo.
- La posizione del Gyarados rosso andava bene. L'evento: il TEAM EMILIA da sconfiggere, poi il Gyarados rosso arrabbiato da placare e catturare.
- La **bozza 2** è stata approvata ("Ok prosegui").

Tre scelte di storia erano rimaste aperte; senza risposta ho usato quelle annunciate in chat:
- la missione della centrale resta **facoltativa**;
- il Gyarados è al **livello 40**;
- lo strumento alla sorgente l'ho scelto io: **ACQUA MAGICA** (potenzia le mosse d'acqua). Si cambia facilmente.

## 2. Com'era nella 0.64

- 35.50 (36×38): la valle d'accesso. Ci si arriva solo con le guide: da Forlì (34.68, oggetto a 39,51) e dal Sentiero del Fumaiolo (35.10, oggetto a 23,3), tutte e due con la 7ª medaglia. Da 35.50 le due guide riportano a Forlì e al Sentiero; la freccia in alto (18,0) porta a 35.51.
- 35.51 (44×34): un lago chiaro **non navigabile**, il muro della diga, la centrale (porta 21,27 → 35.52), due personaggi con testi lunghi e un cartello. Nessuno script di mappa.
- 35.52 (centrale): le tre guardie del TEAM EMILIA e i tre comandi (missione facoltativa, MT27). **Non cambia.**
- Le caselle calpestabili di 35.51 erano 734: nella mappa nuova 608 sono lago, roccia o bosco (`collaudo/vecchie_pos_065.py`, `vecchie_posizioni.txt`).

## 3. Modifiche (versioni/v065_ridracoli.py)

1. **La mappa.** Il disegno della bozza 2 (`bozze/ridracoli.py`) è copiato nel modulo e congelato.
   - Pezzi: Percorso 114 di Smeraldo (terrazze, cascata, laghetto, isolotto, valle con la casa), la diga del layout di prima, acqua, erba e strada del tileset primario.
   - 44×62: layout nuovo (blocchi, bordo di bosco) nello stesso posto della tabella dei layout (id 805, usato solo da 35.51). Tileset secondario nuovo fatto con `tela.Unione`: 83 metatile, 68 tile, 5 palette.
   - **Differenze dalla bozza**, tutte per poter giocare (`collaudo/confronto_bozza_065.py`):
     - tre caselle-freccia d'uscita in fondo alla strada (23–25,61);
     - il primo gradino della scala nel muro (23–25,36): nella bozza era muro con collisione e la scala non portava sul coronamento;
     - il cartello e la Poké Ball della sorgente: nella bozza stavano su roccia irraggiungibile, (10,2) e (8,4); ora sono sulla riva sopra la cascata, (9,5) e (9,8).
2. **Uscite:**
   - frecce sud (23–25,61) → 35.50 (uscita 0, come prima: la freccia di 35.50 non cambia);
   - porta della centrale (29,42) → 35.52 (uscita 1, come prima: 35.52 non cambia).
3. **Percorso del giocatore:** da sud la strada sale nella valle, devia verso la centrale, arriva alla scala nel muro e al coronamento della diga. Dal coronamento:
   - a est la riva porta all'accampamento del TEAM EMILIA (a piedi);
   - a nord il lago (SURF);
   - a nord-ovest la cascata del Bidente: sopra c'è la sorgente (solo con CASCATA).
4. **Personaggi (ognuno con un ruolo):**

| N. | Chi | Dove | Ruolo |
|---|---|---|---|
| 1 | GYARADOS rosso | lago (22,27) | compare dopo CORRADO; si cattura una volta |
| 2 | custode della diga | davanti alla centrale (31,45) | spiega l'evento; tre testi (prima, dopo CORRADO, dopo la cattura) |
| 3 | GIANNI, escursionista (581) | valle (21,52) | allenatore: GRAVELER 39, LAIRON 40 |
| 4 | ERMES, pescatore (633) | coronamento (12,34) | allenatore: WHISCASH 39, SEAKING 40 |
| 5 | recluta del TEAM EMILIA (634) | coronamento (31,34), guarda giù per 2 caselle | blocca il passaggio verso est: MIGHTYENA 40, WEEZING 41 |
| 6 | recluta del TEAM EMILIA (851) | riva est (40,27), guarda giù per 3 caselle | MAGNETON 41, MANECTRIC 41 |
| 7 | CORRADO, capo del TEAM EMILIA (734) | accampamento (40,15) | lotta solo dopo le due reclute: MIGHTYENA 42, CAMERUPT 42, SHARPEDO 43 |
| 8 | Poké Ball | sorgente (9,8) | ACQUA MAGICA, solo con CASCATA |

   - Classe e ritratto: le reclute come quelle della centrale, CORRADO come ROCCO (miniboss della centrale), GIANNI come ETHAN, ERMES come DUNCAN.
   - Le flag dei cinque allenatori (0x745, 0x779, 0x77A, 0x853, 0x7DE) sono tolte dal pool dell'engine.
5. **L'evento:**
   - prima di battere CORRADO il GYARADOS non c'è (flag 0x28, alzata dallo script d'ingresso);
   - CORRADO, se manca una recluta: "Prima te la vedi con le mie reclute!";
   - lotta con CORRADO (trainerbattle di tipo 1): vinto, dice "Il GYARADOS è fuori controllo... Ritirata!", il GYARADOS compare (addobject), verso, "Il lago ribolle... Un GYARADOS rosso emerge infuriato al centro del lago!";
   - il GYARADOS: livello 40, **sempre cromatico** (comando nativo del progetto 0x09730055, lo stesso del FARFETCH'D e dello SHUCKLE, con specie e livello in 0x8004/0x8005). Con la flag 0x8C1 attorno alla lotta l'oggetto resta dopo fuga e KO e si riprova. Cattura: flag 0x2C, l'oggetto sparisce e non torna.
6. **Lo sprite del GYARADOS sulla mappa.** Smeraldo non ha uno sprite di GYARADOS da campo. Il modulo lo ricava dallo sprite di lotta cromatico della ROM (64×64 → 32×32: ogni 2×2 diventa il colore della tavolozza più vicino alla media, poi un contorno nero), con una tavolozza nuova (tag 0x1340).
   - Prende il numero di grafica 184, il BAMBOLONE REGIROCK delle basi segrete, che nessuna mappa usa: chi mettesse quel bambolone in una base segreta vedrebbe il GYARADOS rosso. I numeri oltre 239 non sono usabili (sono grafiche a variabile).
   - La tabella delle tavolozze degli oggetti è copiata con una voce in più; i 3 riferimenti nel codice puntano alla copia.
7. **Cartelli:** (22,39) "DIGA DI RIDRACOLI / Sali la scala per il lago. / La CENTRALE è a destra."; (9,5) "SORGENTE DEL BIDENTE / Qui nasce il fiume / che riempie il lago."
8. **Incontri:** l'erba di 35.51 prende la tabella di terra di 35.50 (stessa zona); acqua e pesca restano quelle di prima.
9. **Testi di 35.50** riscritti in riquadri di 2 righe (guida per Forlì con l'accento su FORLÌ, guida per la Valle del Savio, escursionista, custode, cartello). Cosa fanno le guide non cambia.
10. **Vecchi salvataggi fatti dentro 35.51:** come nella 0.64.
    - **Variabile nuova 0x404E**: la alza lo script d'ingresso di 35.51 (tipo 3), che decide anche se il GYARADOS si vede.
    - **Script di frame:** se la variabile è 0 (Continua su un salvataggio fatto dentro la mappa prima della 0.65), il giocatore viene portato una volta sola sulla strada sotto la diga (24,41), con un'uscita vera: la mappa si ricarica con gli oggetti nuovi.

## 4. Budget (da `out/rapporto_build.json`)

| | Stima prima | Usato | Resta |
|---|---|---|---|
| Spazio | ~40 KB | 35 KB (tileset secondario 25 KB, blocchi 44×62, sprite e tavolozza del GYARADOS, tabella delle tavolozze, eventi, testi, 5 squadre) | 1177 KB |
| Flag | 3 | 3 (0x28 GYARADOS nascosto, 0x2C GYARADOS catturato, 0x34 ACQUA MAGICA); in più tolte dal pool le 3 flag di allenatore che vi erano | 37 nel pool, tutte sicure |
| Variabili | 1 | 1 (0x404E, vecchi salvataggi) | 45 |
| Allenatori | 5 | 5 (581, 633, 634, 734, 851) | 10 liberi |
| Strumenti | 0 | 0 | 67 |
| Grafiche oggetto | 1 | 1 (la 184, prima BAMBOLONE REGIROCK) | — |

## 5. Collaudo (solo tasti; fixture dichiarate)

**Script e risultati**
- Lo script è `collaudo/t65.py`, con `leg.py` e `vai.py`. I risultati sono in `collaudo/risultati/065/`.
- Ogni prova parte da un salvataggio fatto con SALVA in gioco e caricato con Continua dal titolo. In VBA-M si riparte dallo stesso `.sav` fatto in mGBA.

**Fixture (scritture in RAM dichiarate, non prove):**
- `prima`: da `prog_imola.ss` (6 medaglie, BLAZIKEN 50 e BRELOOM 43). La **7ª medaglia** (0x86D: la chiede la guida di Forlì) e la posizione a Forlì (39,54), vicino alla guida.
- `gyarados`: dal salvataggio finale di `prima` (fatto in gioco dopo CORRADO). **SURF** a BRELOOM, **5 MASTER BALL**.
- `sorgente`: da `prog_imola.ss`. 7ª e **8ª medaglia** (CASCATA la chiede), **SURF e CASCATA** a BRELOOM, posizione in 35.51 (24,41).
- In `prima` e `gyarados`, **squadra curata** (PS al massimo, niente stato) prima di ogni lotta: la squadra di prova ha due Pokémon e a Ridracoli non c'è un Centro. Le lotte si combattono comunque a tasti fino alla fine.
- `crea64` (sulla ROM 0.64): 7ª medaglia e posizione in 35.51 (35,29), prima di un SALVA vero. Nella 0.64 è erba calpestabile, nella 0.65 è lago.

**prima**

| Prova | mGBA | VBA-M |
|---|---|---|
| Guida di Forlì, "sì": si arriva a 35.50 (18,34) | sì | sì |
| Cartello e custode di 35.50: testi nuovi di 2 righe | sì | sì |
| 35.50 → freccia → 35.51: il pilota arriva in fondo alla strada (24,60); GYARADOS nascosto (0x28 = 1) | sì | sì |
| Cartello della diga e custode: testi "prima" del §3 | sì | sì |
| Porta della centrale → 35.52 (14,25) e ritorno in 35.51 (28,44) | sì | sì |
| GIANNI: presentazione, lotta (GRAVELER 39, LAIRON 40), sconfitta, flag a 1, poi solo il testo "dopo" | sì | sì |
| Scala nel muro: il pilota arriva sul coronamento (24,35) | sì | sì |
| ERMES: come GIANNI (WHISCASH 39, SEAKING 40) | sì | sì |
| Un passo da (30,35) a (31,35): la recluta del coronamento vede il giocatore, parla e lotta da sola (MIGHTYENA 40, WEEZING 41); flag a 1 | sì | sì |
| CORRADO prima della seconda recluta: "Prima te la vedi con le mie reclute!", nessuna lotta | sì | sì |
| Un passo in (40,30): la recluta della riva vede il giocatore e lotta (MAGNETON 41, MANECTRIC 41); flag a 1 | sì | sì |
| CORRADO: lotta (MIGHTYENA 42, CAMERUPT 42, SHARPEDO 43), poi "Ritirata!", "Il lago ribolle... Un GYARADOS rosso emerge…"; il GYARADOS è sulla mappa (22,27), 0x28 = 0 | sì | VBAM_CORRADO |
| Custode dopo CORRADO: "Il GYARADOS rosso è emerso…"; CORRADO: "è ancora furioso" | sì | sì |
| SALVA sul coronamento, Continua: si resta lì, il GYARADOS c'è, variabile 0x404E = 1 | sì | sì |

**gyarados** (SURF e MASTER BALL sono fixture)

| Prova | mGBA | VBA-M |
|---|---|---|
| Dal coronamento in SURF fino a (22,28), sotto il GYARADOS | sì | sì |
| A: "Il GYARADOS rosso è furioso! Calmalo con una lotta!", lotta | sì | sì |
| Fuga: "Il GYARADOS resta al centro del lago…", il GYARADOS c'è ancora, 0x2C = 0 | sì | sì |
| KO (avversario GYARADOS 40): "Il GYARADOS si inabissa, poi riemerge…", c'è ancora | sì | sì |
| Cattura con MASTER BALL: in squadra un GYARADOS di livello 40, **cromatico** (letto da PID e ID allenatore), 0x2C = 1, l'oggetto sparisce | sì | sì |
| CORRADO: "L'hai calmato tu?…"; custode: "Il lago è di nuovo calmo…" | sì | sì |
| SALVA, Continua: il GYARADOS non c'è; uscita a 35.50 e ritorno: non c'è | sì | sì |

**sorgente** (8ª medaglia, SURF e CASCATA sono fixture)

| Prova | mGBA | VBA-M |
|---|---|---|
| Senza CASCATA il pilota non trova strada per la riva della sorgente | sì | sì |
| In SURF ai piedi della cascata (12,13), A: "È una grande cascata. Vuoi usare CASCATA?", sì: si risale fino a (12,9) | sì | sì |
| Riva della sorgente (10,8); cartello (9,5): testo del §3 | sì | sì |
| Poké Ball: "trova: ACQUA MAGICA!", nella tasca STRUMENTI (da 1 a 2: il giocatore di prova ne aveva già una), 0x34 = 1, la Poké Ball sparisce; dopo SALVA e Continua non torna | sì | sì |

**Vecchi salvataggi**

| Prova | mGBA | VBA-M |
|---|---|---|
| **vecchio64**, salvataggio vero della 0.64 in 35.51 (35,29), oggi lago: dopo Continua nella 0.65 il giocatore è sulla strada sotto la diga (24,41), variabile 1; si cammina fino a (24,45); SALVA, Continua: si resta lì; si arriva a 35.50 | sì | sì |

**Altre note sulle prove**
- Nella prima corsa di `gyarados` il Pokémon catturato era un **BRELOOM di livello 0**, cromatico: il comando nativo rifà il Pokémon da 0x8004/0x8005, che non avevo impostato. Corretto nel modulo (prima dello SHA), poi `prima` e `gyarados` rifatte sulla ROM corretta.
- Dopo il KO del GYARADOS il BRELOOM di prova vuole imparare una mossa: il collaudo risponde "sì" a "Smettere di imparare…?" (solo B la faceva ripetere).
- **CORRADO in VBA-M:** VBAM_NOTA
- Il pianificatore (`vai.py`) non usa CASCATA: la salita è fatta a tasti nella prova. Un allenatore che si avvicina resta nella casella nuova fino al cambio di mappa: le prove passano a lato.
- Nei log ci sono "fuori percorso" e "lotta selvatica: fuga": incontri nell'erba e in acqua. Testi rimasti nel buffer (per esempio "Natura INGENUA…" dopo una lotta, "MEDAGLIE") vengono da menu aperti dal pilota, non dagli script.
- Log: `collaudo/risultati/065/log_t65.txt`; ogni corsa comincia con una riga "PROVA <parte> <emulatore>".

**Analisi statica** (`collaudo/risultati/065/`):
- **La mappa è la bozza** (`confronto_bozza.txt`): le 75 righe di disegno della bozza sono nel modulo; la tela della bozza e quella del modulo differiscono solo nelle 5 caselle dichiarate (gradino, cartello); i 2728 blocchi di 35.51 nella ROM sono quelli della tela del modulo, tranne le 3 frecce.
- **Testi** (`testi.txt`): `collaudo/testi_065.py` segue tutti gli script degli oggetti e dei cartelli di 35.51 e 35.50 (anche la lotta di CORRADO e il suo seguito): tutti i riquadri hanno al massimo 2 righe e 30 caratteri.
- **Percorsi** (`analisi.txt`, `analisi/percorso.py` da 35.50):
  - senza abilità: valle, centrale, coronamento, riva est e accampamento sì; GYARADOS e sorgente no;
  - con SURF: anche il GYARADOS; la sorgente no;
  - con SURF e CASCATA: anche la sorgente;
  - con tutte le abilità tranne CASCATA: la sorgente no;
  - da 35.51 si torna a piedi alle due guide di 35.50.
- **Vecchie posizioni** (`vecchie_posizioni.txt`): 608 delle 734 caselle calpestabili della vecchia 35.51 nella mappa nuova non portano a un'uscita senza abilità; il ritorno sotto la diga le copre tutte (lo script non guarda la posizione).

### Regressione (`collaudo/regressione.py`, 0.65 contro 0.64)

Tutte le 17 partenze in mGBA e il salvataggio vero in mGBA e VBA-M girano e sono **uguali** alla 0.64 (`collaudo/risultati/065/regressione.md`, 19 righe "uguale"). Nessuna partenza è a Ridracoli: le prove della mappa sono quelle sopra.

### Cosa non è verificato
- Il **BAMBOLONE REGIROCK** delle basi segrete ora mostrerebbe il GYARADOS: non provato (letto).
- Gli **incontri** dell'erba di 35.51 (tabella di 35.50) non sono stati provati a parte; le lotte selvatiche viste nelle prove sono partite camminando e in SURF.
- La **guida del Sentiero del Fumaiolo** (35.10 → 35.50) non è stata usata in questa versione; non cambia.
- La **missione della centrale** (35.52) non è stata rifatta: la mappa non cambia e la porta porta ancora lì (provato andata e ritorno).
- Il testo della guida di Forlì (34.68: "Ingresso per sentiero di Ridracoli…") è ancora lungo: Forlì non è toccata da questa versione; va con le barriere e i testi lunghi.
- Lo sprite del GYARADOS è stato visto nelle anteprime fatte dalla ROM (`sprite.py`), non in una schermata dell'emulatore; in gioco l'oggetto c'è (letto dalla RAM degli oggetti).
- Il ritorno sotto la diga è stato visto per una posizione, (35,29); per le altre segue dallo script.

## 6. Richieste

| Richiesta | Stato |
|---|---|
| Mappa mostrata finita e approvata prima del modulo | **fatto**: bozza 2 approvata in chat; 3 ritocchi per poter giocare, dichiarati (§3.1) |
| Si capisce come si sale alla diga | **corretto e verificato**: strada dalla valle, scala nel muro, coronamento |
| In alto a destra non tutto chiuso | **corretto**: baia di nord-est, Rio Celluzze, riva est con l'accampamento |
| Sopra con CASCATA, qualcosa da trovare | **corretto e verificato**: sorgente con cartello e ACQUA MAGICA, solo con CASCATA |
| Personaggi con un ruolo | **corretto**: tabella del §3.4; tutti provati a tasti |
| TEAM EMILIA da sconfiggere, poi il GYARADOS rosso da placare e catturare | **corretto e verificato** in mGBA e VBA-M: reclute, CORRADO, GYARADOS cromatico Lv 40, fuga e KO con nuovo tentativo, una sola cattura |
| Vecchi salvataggi | **verificato** con un salvataggio vero della 0.64 fatto dentro la mappa |
| Testi in italiano, massimo 2 righe e 30 caratteri | **corretto**, controllato sui byte per tutti i testi di 35.50 e 35.51 (`testi.txt`) |
