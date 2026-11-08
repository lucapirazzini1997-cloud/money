# Pokémon Romagna 0.69: barriere e testi (Lotto 3)

**Base:** 0.68, SHA-256 `d4a65459b46f01b9c23e84c593ebda2a1669c5cdf4602ac6825af81a996bd964`.

**Risultato:** `Pokemon_Romagna_0_69.gba`, SHA-256 `e0a23d7f7c2430cf529ebb2bdf6b9b301d91e0f97340965cbaaa99a0348b3424`.
- Patch BPS 0.68→0.69: `rom/Pokemon_Romagna_0_68_to_0_69.bps` (CONSEGNA).
- Modulo: `versioni/v069_testi.py`. Strumenti nuovi: `analisi/barriere.py`, `analisi/testi_lunghi.py`.
- Lo SHA è in `build.py` dopo il collaudo (§5).
- **Salvataggi compatibili:** cambiano solo testi e i puntatori ai testi nelle istruzioni degli script; nessuna mappa, flag o variabile.

## 1. Cosa è stato chiesto

- Prompt 0.57, Lotto 3: "Progressione: ogni barriera deve avere un requisito ottenibile, un messaggio chiaro e una via di ritorno."
- Regola dei testi: "in italiano, massimo 2 righe per riquadro, controllati a schermo".
- Rimasti dalle versioni prima: i due testi del Fumaiolo con direzioni sbagliate (0.66), "non e" senza accento, il testo della guida di Forlì per Ridracoli (0.65).

## 2. Barriere (inventario)

Cercate su tutte le mappe che si raggiungono a piedi dall'inizio, con tutte le abilità (181 mappe, `analisi/percorso.py`):
eventi a coordinate (`analisi/barriere.py`) e personaggi o cartelli con testi di blocco. Elenco completo:
`collaudo/risultati/069/inventario_barriere.txt`.

| Barriera | Requisito | Chi lo dà | Messaggio | Ritorno | Prova |
|---|---|---|---|---|---|
| Lido di Savio, uscite sud (0.9, y 40) | starter (0x20) | laboratorio 1.4 | "Un momento! Non puoi lasciare il Lido senza un POKéMON." (riscritto) | si resta sul Lido | letto (nessun salvataggio senza starter) |
| Lido di Savio → Ravenna (0.9, 19–20,7) | 5ª medaglia | palestra di Faenza | "Verso RAVENNA non si passa: serve la quinta medaglia." (riscritto) | si torna a (20,9) | **a tasti** |
| Cesena → Fumaiolo (34.17, 45–48,50) | 7ª medaglia | palestra di Imola | "Il sentiero sale verso il Fumaiolo. Servono la Medaglia di Imola e un Pokémon che conosca Forza." | si resta in città | **a tasti** |
| Strada per Rimini, ALDO (34.43, 21–25,54) | 2ª medaglia | palestra di Cesena | "Prima conquista la Medaglia Collina…" | si torna a (23,50) | **a tasti** |
| Forlì, guida per Ridracoli (34.68, 39,51) e Sentiero del Savio (35.10, 17,96) | 7ª medaglia | palestra di Imola | "Il sentiero per RIDRACOLI è ancora chiuso…" (riscritto) | la guida non si sposta | **a tasti** (Forlì) |
| Faenza, VIGILE del ponte per Imola (34.85, 2,29) | 6ª medaglia (sparisce con 0x86C) | ALIDA, Lugo | "Il ponte del Santerno… Riapre dopo la vittoria sul capopalestra di Lugo." | si torna indietro | **a tasti** |
| Ravenna, VIGILE dei canali (34.96, 4,35) | chiuse riparate (0x2AB) | cartello 34.98 (4,9) | "Finché non risolvi il guaio, nessuno passa." | si torna indietro | letto |
| Rimini, guida per San Marino (34.44, 21,34) | Lega (0x864) | Lega | "La strada per SAN MARINO… Torna dopo la LEGA." (riscritto) | la guida non si sposta | letto |
| Cesenatico, osservatorio (34.6, 9,3) | rapporto del MUSEO DELLE SALINE (0x3A) | lo stesso guardiano, con lo strumento 0x10D | "I piani superiori sono riservati…" | si viene riportati giù | letto |
| Cervia, saletta del PANAMA (34.1, 0,2) | barista (0x14B) | barista 34.1 | "Di qui non si passa… Chiedi al barista." | — | letto |
| Rocce (SPACCAROCCIA), alberelli (TAGLIO) | 3ª / 1ª medaglia e la MN | MN: Rimini / Cesenatico | testi di Smeraldo tradotti | — | provati nelle versioni prima |

- Nessuna barriera ha un requisito che non si ottiene: le flag richieste sono alzate da script delle mappe raggiungibili (le medaglie dai capipalestra).
- Avvertenza: la barriera del Fumaiolo controlla solo la 7ª medaglia; FORZA serve dopo, per il masso della Grotta dell'Eremo. Il testo resta com'è perché descrive il percorso, non il controllo.

## 3. Testi (versioni/v069_testi.py)

### 3.1 Testi riscritti (21, `testi.txt`)
Testo nuovo, a capo a 30 caratteri e 2 righe per riquadro; le istruzioni che leggevano il vecchio (33) ora leggono il nuovo.
- **8 testi con una terza riga che scorreva nello stesso riquadro** (`\l`): isola MIRAGGIO (Lido), pietre del laboratorio, STANZA CHEATER, tre testi della PENSIONE, OSTE della Casa delle Aie, menu del giorno.
- **Fumaiolo:**
  - guida del Cuore: "Per Bagno di Romagna prendi il PASSO DEI DRAGHI: nella Grotta delle Sorgenti è la prima porta a nord, a sinistra" (prima: "dal passo a sud-est del santuario");
  - incisione: "SALE: a ovest, oltre il lago. ARGILLA: a nord, a destra" (prima: "l'argilla a est");
  - "Hai spento nodo del sale/dell'argilla" → "Nodo del SALE/dell'ARGILLA spento!".
  - Le direzioni sono quelle del cartello del santuario (35.13: "Nord, da sinistra: PASSO DEI DRAGHI, sala di BASSI, nodo dell'ARGILLA. Ovest, oltre il lago: nodo del SALE").
- **Guide dei collegamenti:** "Ingresso per sentiero di Ridracoli. Vuoi che ti accompagni lungo il collegamento?" → "Sono la guida per la diga di RIDRACOLI. Vuoi che ti accompagni?"; lo stesso per San Marino e per l'Autodromo; i "non e ancora disponibile" → "è ancora chiuso/chiusa. Torna…".
- **Barriere di Lido di Savio:** il testo dello starter era spezzato a metà frase ("Non puoi lasciare / il Lido" da solo su una riga), quello di Ravenna anche.

### 3.2 Accenti (sul posto)
- **22 testi con l'accento scritto come apostrofo** (e', piu', gia', sara', Portero'…): parola corretta, testo più corto di un byte (`accenti.txt`).
- **110 lettere** in parole senza accento: più, già, città, può, c'è, sarà, normalità, quantità, studiò, e la "e" verbo riconosciuta dal contesto (non è, è stato, è già, è pronto, la palestra è a, il santuario è tranquillo…).
- Le regole escludono i casi in cui la "e" è congiunzione ("Ball e strumenti", "pigro e più raro", "Visita Mirabilandia e il Safari", "Riposati e salva"). Ho letto una per una tutte le 132 correzioni prima di fissarne il numero nel modulo.
- Non toccati: i testi delle lotte e quelli che non partono da un'istruzione di testo degli script.

### 3.3 Testi lunghi: cosa resta
- Nessun testo delle mappe raggiungibili ha più di 2 righe per riquadro dopo questa versione (gli 8 con lo scorrimento sono riscritti).
- Restano **611 testi** con righe di 31–42 caratteri (`testi_lunghi_069.txt`). A schermo entrano nel riquadro: la riga di 41 caratteri della mamma ("Prima di partire, riposati un po'. I tuoi") si legge intera, con margine (schermata nella prova della 0.69). Il limite di 30 caratteri è la regola dei testi nuovi; riscrivere i 611 vecchi non l'ho fatto (§6).

## 4. Budget (da `out/rapporto_build.json`)

791 KB (la 0.69 ne usa circa 2 per i 21 testi nuovi), 35 flag, 43 variabili, 67 strumenti, 10 allenatori liberi; mappe libere 24.75, 24.76.

## 5. Collaudo (solo tasti; fixture dichiarate)

**Script e risultati:** `collaudo/t69.py`; risultati in `collaudo/risultati/069/`. ROM finale `e0a23d7f…3424` in mGBA e VBA-M.

**Fixture dichiarate:** solo la posizione di partenza, scritta prima di un SALVA vero:
- Lido di Savio (20,9), da `q8_end.ss` (0 medaglie);
- Cesena (46,47) e strada per Rimini 34.43 (23,51), da `s_ce3.ss` (1 medaglia; a piedi il pilota si fermava nel casello 35.89);
- Forlì (39,53) e Faenza (2,31), da `t59_ravenna.ss` (5 medaglie; `gpre.ss` parte in lotta e non si può salvare).

| Prova | mGBA | VBA-M |
|---|---|---|
| Lido → Ravenna senza la 5ª medaglia: "Verso RAVENNA non si passa: serve la quinta medaglia."; di nuovo in (20,9); si cammina via fino a (20,12) | ok | ok |
| Cesena → Fumaiolo con 1 medaglia: messaggio; si resta in (46,50); si torna a (46,45) | ok | ok |
| Strada per Rimini con 1 medaglia: ALDO "Prima conquista la Medaglia Collina…"; riportati a (23,50); si torna a (23,47) | ok | ok |
| Forlì, guida per Ridracoli con 5 medaglie: "Il sentiero per RIDRACOLI è ancora chiuso. Torna con la settima medaglia, quella di IMOLA." | ok | ok |
| Faenza, VIGILE del ponte con 5 medaglie: "Il ponte del Santerno, verso Imola, è chiuso…" | ok | ok |
| A schermo (mGBA): riquadri della guida di Forlì e della barriera di Ravenna, con "è" e gli a capo giusti (`t69_schermo_*.png`, non nel pacchetto) | ok | — |

**Controlli statici**
- `testi.txt` (`collaudo/testi_069.py`): i 21 testi riscritti, riquadro per riquadro, entro 2 righe da 30 caratteri. Fra 0.68 e 0.69 cambiano 3409 byte: i testi nuovi, i testi corretti sul posto e 99 byte di puntatori (33 istruzioni ripuntate). TUTTO OK.
- Build: raggiungibilità "nuove 0, problemi 0".

### Regressione (`collaudo/regressione.py`, 0.69 contro 0.68)
Le 19 partenze (17 savestate in mGBA e il salvataggio vero in mGBA e VBA-M) girano, sono vive, la callback resta nella ROM e sono **uguali** alla 0.68 in tutti i punti di controllo: nessuna mostra un testo cambiato (`regressione.md`).

### Cosa non è verificato
- A tasti non ho letto in gioco i testi del Fumaiolo, della PENSIONE, dell'OSTE, della STANZA CHEATER e la maggior parte dei 132 accenti: sono controllati sulla ROM (`testi.txt`, `accenti.txt`).
- Le barriere segnate "letto" in §2.
- Le guide con la domanda "Vuoi che ti accompagni?" dopo la 7ª medaglia (il viaggio): lo script non cambia, cambia solo il testo.

## 6. Richieste

| Richiesta | Stato |
|---|---|
| Ogni barriera: requisito ottenibile, messaggio chiaro, via di ritorno | **verificato**: 5 a tasti in mGBA e VBA-M, le altre lette (§2); messaggi spezzati riscritti |
| Testi con più di 2 righe per riquadro | **corretto e verificato** sulla ROM (gli 8 con lo scorrimento) |
| Due testi del Fumaiolo con direzioni sbagliate | **corretto** (letto sulla ROM, non in gioco) |
| "non e" senza accento e accenti mancanti | **corretto**: 22 testi con l'apostrofo, 110 lettere |
| Guida di Forlì per Ridracoli | **corretto e verificato** a tasti |
| Righe di 31–42 caratteri nei 611 testi vecchi | **non fatto, da decidere**: entrano nel riquadro; riscriverle tutte a 30 caratteri allungherebbe i dialoghi di circa un terzo |
| Prossimo | consegna di Smeargle con squadra e PC pieni (non verificata dalla 0.56), poi chiusura del Lotto 3 |
