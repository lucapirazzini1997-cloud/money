# Pokémon Romagna 0.61: Regi, Deoxys, Jirachi e Mewtwo (Lotto 2, fine)

**Base:** 0.60, SHA-256 `d9ca40b361d02c0404b5d6553dc8d45252087d8bebf59e4e42c942a5786b183a`.

**Risultato:** `Pokemon_Romagna_0_61.gba`, SHA-256 `f3e7802535125bdc473bd328e4cf7f2b7aeb030f71a1fabb81675614acd63cbe`.
- Patch BPS 0.60→0.61: `rom/Pokemon_Romagna_0_60_to_0_61.bps`, (4907 byte), verificata riapplicandola.
- Modulo: `versioni/v061_regi_mitici.py`. La build da zero rifà tutti gli SHA, controlli compresi.
- Lo SHA è in `build.py` dopo il collaudo (§4).
- **Salvataggi compatibili:** il salvataggio vero della regressione carica in mGBA e VBA-M; un salvataggio fatto con la 0.60 dentro la Camera di Pietra usa lo script nuovo (provato solo per Regirock, in mGBA; §4).

## 1. Cosa c'era prima

Letto dagli script della 0.60 e poi provato a tasti dove indicato.

| | Come ci si arriva | Condizione | Problemi |
|---|---|---|---|
| **Regirock, Regice, Registeel** (Lv 40/42/45) | Faenza → Sentiero 35.73 → Galleria dei Sigilli 35.74 → scala 35.75 → camere 35.76/77/78 | 6ª medaglia (0x86C); senza, una sbarra sul Sentiero non fa passare | **FORZA non serve**: `analisi/percorso.py` arriva alle tre camere senza nessuna abilità (provato poi a tasti, §4). Dopo fuga o KO lo script finiva **senza dire nulla** |
| **Deoxys** (Lv 50) | Ravenna 34.96: SURF a est fino al bordo (x 79), passaggio a coordinate al molo 35.40, cartello del **razzo** → 35.41; rientro col razzo | Lega vinta (0x864) sul razzo e su Deoxys | righe di testo più lunghe di 30 caratteri; KO e fuga con lo stesso testo |
| **Jirachi** (Lv 50) | **portale** nel mare di Cervia (0.10, oggetto 13 a 61,22): lo script di ritorno al campo lo mostra solo dopo la Lega → 35.42 | Lega vinta | come sopra |
| **Mewtwo** (Lv 70) | Cesenatico 34.22, uscita 8 (casella 48,33) → grotta 35.43 | Lega vinta | **non si entrava**: l'uscita sta su una casella di sabbia (comportamento 0x21) e Smeraldo fa scattare le uscite solo su porte, scale e frecce. **Riprodotto** a tasti in mGBA, sulla build prima della correzione: il personaggio sta sulla casella e spinge, non succede nulla (`collaudo/risultati/061/mewtwo_ingresso_prima.txt`) |

Flag di cattura indipendenti, già prima: Regirock 0x620, Regice 0x622, Registeel 0x627, Deoxys 0x4EB, Jirachi 0x4EA, Mewtwo 0x4EF.

**Rovine dei Regi di Smeraldo** (24.6, 24.67, 24.68, flag 0x3A7–0x3A9): le loro porte (0.26, 0.20, 0.35) sono vere porte, ma dalla partenza (Lido di Savio) `analisi/percorso.py` non arriva a quelle mappe, nemmeno con tutte le abilità. La zona 0.26 → 0.2 → 0.32 esce a senso unico verso la Costa Adriatica. Il registro della build (`cammino.py`, più ottimista) le conta raggiungibili: **segnalato**, da chiarire nel Lotto 3 (raggiungibilità). Se un giorno si collegassero, sarebbero doppioni dei Regi della Galleria.

## 2. Modifiche (versioni/v061_regi_mitici.py)

- **Uno script nuovo per ognuno dei sei**, come quelli della 0.60:
  1. già catturato → "la camera è vuota" / "regna il silenzio";
  2. senza la condizione (6ª medaglia per i Regi, Lega per gli altri) → testo che dice cosa serve;
  3. lotta (i Regi con lo special 0x13B, la loro musica; gli altri con `dowildbattle`), con la flag 0x8C1 perché l'oggetto resti;
  4. esito: **cattura** → flag e oggetto rimosso; **KO** → "crolla, poi si rimette a guardia… Puoi riprovare quando vuoi"; **fuga** → "torna al suo posto… Puoi riprovare quando vuoi".
- **Razzo, rientro e portale:** stessi viaggi di prima, testi in riquadri di due righe. Razzo e rientro sono cartelli (ripuntati); portale e ritorno sono oggetti, quindi anche il vecchio script diventa un salto.
- **Ingresso della grotta di Mewtwo:** un evento a coordinate sulla casella 48,33 di 34.22 (variabile temporanea 0x400F = 0, come al bordo est di Ravenna) porta in 35.43, una casella sopra l'uscita a freccia. L'uscita di ritorno (frecce) funzionava già.
- **Vecchi script degli oggetti** → salto al nuovo (5 byte, byte vecchi controllati con un `assert`), per i salvataggi fatti dentro le mappe.
- **Nessuna flag e nessuna variabile nuova.** `registri/genera.py`: condivisioni nuove 0 (riga "condivisioni 147 (nuove 0)" del log di build).

**Strumenti di analisi e collaudo:**
- `analisi/percorso.py`: gli alberi di bacche (tipo di movimento 12) bloccano il passaggio. Prima il navigatore cercava di attraversarli (Campagna Cervese 34.20).
- `collaudo/vai.py`: taglia gli alberi (A, sì) come spacca le rocce; `guarda` non fa un passo se il giocatore è già girato (prima, davanti a un cartello sull'acqua, lo superava).
- `collaudo/t61.py`: il collaudo di questa versione.

**Uscite su caselle sbagliate, fuori dai gruppi di Smeraldo** (scansione di tutte le uscite): oltre a Mewtwo restano 34.17 uscita 13 (in sé stessa), 35.13 → 35.18 (Passo dei Draghi), 35.16 → 35.17 (Cuore del Fumaiolo). **Segnalate**, non riprodotte: possono essere solo arrivi di script. Da controllare nel Lotto 3.

## 3. Budget

| | Stima prima | Usato | Resta |
|---|---|---|---|
| Spazio | ~4 KB | **circa 4,7 KB** (un blocco di 4716 byte nelle zone dell'engine) | 1241 KB |
| Flag | 0 | 0 | 47 nel pool |
| Variabili | 0 | 0 (0x400F è temporanea, già usata così a Ravenna) | 47 |
| Strumenti, allenatori | 0 | 0 | 67 numeri di strumento, 18 allenatori liberi |

## 4. Collaudo (solo tasti; fixture dichiarate)

Script: `collaudo/t61.py` con `leg.py` e `vai.py`. Risultati in `collaudo/risultati/061/`.

**Partenza:** il savestate `prog_imola.ss` (6 medaglie, Lega non vinta), come nella 0.60.

**Fixture (scritture in RAM dichiarate, non prove), poi SALVA in gioco e Continua dal titolo:**
- **SURF** a Breloom al posto della sua 4ª mossa (per Jirachi e il molo del razzo); TAGLIO e SPACCAROCCIA la squadra li ha già;
- **5 MASTER BALL** in testa alla tasca Poké Ball (lo strumento che c'era scala di un posto);
- **posizione:** Sentiero Faenza-Lugo (35.73) per i Regi, Ravenna (34.96, 60,43) per gli altri;
- **medaglie:** per "senza 6ª medaglia" la 0x86C è messa a 0; nei salvataggi "prima_lega" e "mitici" 7ª e 8ª medaglia (0x86D, 0x86E);
- **Lega vinta** (0x864) **solo** nel salvataggio "mitici": serve a provare gli eventi dopo la Lega, non è una prova di aver vinto la Lega.

Tutto il resto solo con i tasti: viaggio, alberi da tagliare, SURF, passaggi a coordinate, razzo, portale, lotte.

### Regi, mGBA e VBA-M (stessi risultati)

| Prova | Regirock | Regice | Registeel |
|---|---|---|---|
| Arrivo a piedi **senza nessuna abilità** dal Sentiero | sì | sì | sì |
| Lotta | sì | sì | sì |
| Fuga: testo, flag 0, Regi ancora lì | sì | sì | sì |
| KO: testo "crolla, poi si rimette a guardia", flag 0, ancora lì | sì | non provato | non provato |
| Cattura (MASTER BALL, "no" al soprannome): flag 1, sparito, in squadra | sì | sì | sì |
| SALVA in gioco, titolo → Continua: tre flag a 1 | sì | sì | sì |
| Uscita dalla camera e ritorno: Regi assente | sì | — | sì |

- Ritorno a piedi dalla scala fino al Sentiero (passaggio nell'altro verso): sì.
- Il testo finale della cattura di Registeel, in mGBA, non è stato letto (i messaggi di salita di livello sono più lunghi dell'attesa della prova); flag 1 e Regi assente sono letti. In VBA-M, con l'attesa più lunga, c'è anche il testo.
- **Senza la 6ª medaglia** (solo mGBA): il navigatore non arriva alla Galleria; la sbarra sul Sentiero dice *"Con la sesta medaglia puoi attraversarla e raggiungere le camere di Regirock, Regice e Registeel"*.

### Prima della Lega (mGBA)

- SURF verso est da Ravenna → molo del razzo 35.40; il razzo dice *"Il volo è riservato al CAMPIONE della LEGA ROMAGNOLA"*.
- Dal molo, spingendo a ovest, di nuovo a Ravenna 34.96 (passaggio nell'altro verso): sì.
- Nel mare di Cervia il portale **non c'è**.
- Si entra nella grotta di Mewtwo (con la correzione) e Mewtwo dice *"Torna quando sarai CAMPIONE della LEGA ROMAGNOLA"*; nessuna lotta, flag 0.

### Deoxys, Jirachi, Mewtwo con la Lega vinta, mGBA e VBA-M

| Prova | Deoxys | Jirachi | Mewtwo |
|---|---|---|---|
| Viaggio di andata | razzo: "no" resta, "sì" → "3… 2… 1… Lancio!" → 35.41 | portale (SURF a Cervia) → 35.42 | casella 48,33 → 35.43 |
| Lotta | sì | sì | sì |
| Fuga: testo, flag 0, ancora lì | sì | sì | sì |
| Cattura: flag 1, sparito, in squadra | sì | sì | sì |
| Ritorno | razzo → Ravenna 34.96 (62,45) | portale → Cervia 0.10 (54,22) | frecce → Cesenatico |
| SALVA, titolo → Continua: tre flag a 1, tre in squadra | sì | sì | sì |
| Di nuovo nella grotta: Mewtwo assente | — | — | sì |

- In mGBA la prova è stata fatta due volte. Nella prima il testo finale della cattura di Mewtwo non era stato letto (attesa troppo corta dopo due salite di livello), ma flag 1, Mewtwo in squadra e grotta vuota erano confermati dopo la ricarica. Nella seconda, con l'attesa più lunga, ci sono tutti e tre i testi *"Hai catturato…"*. In VBA-M anche.
- Il razzo è un cartello sull'acqua: si legge dalla casella sotto, in SURF.

### Vecchio salvataggio (solo mGBA)

Con la 0.60 si entra nella Camera di Pietra e si salva in gioco. Lo stesso file aperto con la 0.61: parlando con Regirock risponde lo script nuovo (testo d'ingresso nuovo, poi dopo la fuga *"REGIROCK torna immobile in fondo alla camera"*). Esito in `collaudo/risultati/061/t61_vecchio.json`.

### Regressione (`collaudo/regressione.py`, 0.61 contro 0.60)

**Tutte le 19 partenze uguali alla 0.60** (17 savestate in mGBA e il salvataggio vero in mGBA e in VBA-M): schermo, EWRAM, IWRAM (tolto l'orologio), VRAM, tavolozze e OAM. Tabella in `collaudo/risultati/061/regressione.md`.

**Consegna** (`.claude/skills/consegna-versione/consegna.sh`, esito a schermo, non salvato in `risultati/`): build da zero con lo SHA atteso; BPS 0.60→0.61 di 4907 byte riapplicata e identica; zip del progetto (31 MB) ricostruito in una cartella pulita con lo stesso SHA.

### Cosa non è verificato

- **Vecchi salvataggi dentro le altre mappe** (Regice, Registeel, Deoxys, Jirachi, Mewtwo, portale di Cervia e ritorno): il salto dal vecchio script è lo stesso provato con Regirock, ma non c'è un esito per ognuno. E in VBA-M non è provato nemmeno Regirock.
- **Uscita e rientro con il Pokémon catturato** per Regice, Deoxys e Jirachi (provati per Regirock, Registeel e Mewtwo).
- **Solo in mGBA:** le prove prima della Lega (razzo chiuso, ritorno a ovest dal molo, portale assente, Mewtwo prima della Lega), quelle senza la 6ª medaglia e il vecchio salvataggio.
- **Testi mai mostrati in collaudo:** i testi "già catturato" dei sei (l'oggetto sparisce con la cattura, quindi in gioco non dovrebbero comparire), i testi "serve la 6ª medaglia" dei Regi (la sbarra sul Sentiero ferma prima) e "serve la Lega" di Deoxys e Jirachi (razzo e portale chiusi prima). Sono reti di sicurezza; quello di Mewtwo invece si vede ed è provato.

- **Il KO di Regice, Registeel, Deoxys, Jirachi e Mewtwo.** Il ramo dopo la lotta è lo stesso codice provato con Regirock; per Deoxys, Jirachi e Mewtwo cambia l'avvio della lotta (`dowildbattle` invece dello special dei Regi). Non provato per non sovraccaricare la squadra di prova (Lv 50 contro Lv 50–70).
- **Ottenere SURF in gioco**, vincere davvero la Lega e la sconfitta del giocatore: fixture o fuori da questa versione (Lotto 3).
- **Lugia e Ho-Oh** (MOTONAVE dopo la Lega → Monte Spaccato 26.67, script di Smeraldo): solo letti, raggiungibilità da provare.
- **Celebi** (Pineta del Savio 0.16): *correzione dopo la consegna.* In una prima stesura avevo scritto che non c'era lotta: avevo letto solo l'oggetto 9 (lo sprite, nascosto). L'evento è il santuario di legno (cartello a 32,5): dopo la Lega, con la GS BALL (la dà il PROF. PINO, il Birch della Romagna, nel laboratorio di Lido di Savio 1.4, flag 0x4E5), compare Celebi Lv 50; se non lo catturi svanisce e la GS BALL resta, quindi segue già la regola del Lotto 2. Letto negli script; l'utente l'ha provato in gioco nella 0.56. Non riprovato in questa versione.
- **Groudon e Rayquaza** (eventi della storia): solo letti. Groudon dopo la fuga perde l'oggetto fino al rientro (manca la flag 0x8C1) e ha testi di 3–4 righe; Rayquaza ha righe troppo lunghe. Da sistemare quando si toccheranno quelle mappe.

## 5. Richieste del prompt

| Richiesta | Stato |
|---|---|
| Regi senza FORZA, con stati indipendenti di cattura, fuga e sconfitta | **verificato in parte** (mGBA e VBA-M): cattura e fuga per tutti e tre, KO solo per Regirock: FORZA non serviva già; aggiunti i testi di fuga e KO; KO provato su Regirock |
| Deoxys, Jirachi, Mewtwo: come ci si arriva e evento chiaro | **corretto e verificato**: percorsi provati a tasti; la grotta di Mewtwo prima non si apriva; testi che dicono cosa serve |
| Una sola volta, nuovo tentativo dopo fuga o sconfitta, per tutti | **verificato** per la fuga di tutti e sei e il KO di Regirock; KO degli altri solo letto (§4) |
| Tabella di tutti i leggendari in `doc/PROGETTO.md` §3 | **fatto**, con lo stato di ognuno (provato, letto, non catturabile, scollegato) |
| Lotto 2 | **chiuso** con questa versione. Restano segnalati per il Lotto 3: rovine di Smeraldo nel registro ottimista, tre uscite su caselle sospette |
