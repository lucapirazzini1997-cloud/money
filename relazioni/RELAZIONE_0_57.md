# Pokémon Romagna 0.57: spazio recuperato (Lotto 1, prima parte)

**Base:** 0.56, SHA-256 `b09eb6977ca7ceaf81be2a184d719ce6cc25229d2889e4cc3c4fa4714237495f`, rifatta da `python3 build.py` con tutti gli SHA attesi.

**Risultato:** `Pokemon_Romagna_0_57.gba`, SHA-256 `47f53668d8b5861956938cd041fb892e541b86031e4ac7b4337e8328923897c4`.
- Patch BPS 0.56→0.57: `rom/Pokemon_Romagna_0_56_to_0_57.bps` (159 byte), verificata riapplicandola alla 0.56.
- **Collaudata in emulatore** (aggiornamento consegnato con la 0.58, vedi §4): lo SHA è ora in `SHA` dentro `build.py`.

**Il gioco non cambia.** Cambiano 687 400 byte, tutti dentro le undici zone recuperate: prima erano zeri, ora sono 0xFF (spazio libero). Nessun byte fuori dalle zone è diverso dalla 0.56 (controllato confrontando le due ROM).

## 1. Cosa cambia

| | Prima (0.56) | Dopo (0.57) |
|---|---|---|
| Spazio libero nelle zone dell'engine | 578 KB | **1249 KB** (+671 KB) |
| Zone dell'engine | 3 (quelle della 0.55) | 14 |

- **`versioni/v057_spazio.py`:**
  - ricontrolla che ogni zona sia ancora tutta a zero;
  - la riempie di 0xFF;
  - la aggiunge all'engine.
- **`versioni/engine.py`:**
  - `W.aggiungi_zone(zone)` accoda zone nuove con gli stessi controlli di quelle della 0.55: tutte 0xFF, allineate, senza sovrapposizioni;
  - `W.libere()` dice quanti byte restano.
- **`analisi/spazio.py`** (nuovo): ricerca delle zone, con il motivo di ogni esclusione.
- **`analisi/raggiungibili.py`** (nuovo): raggiungibilità delle mappe contando uscite, connessioni, SUB, warp degli script e Volo. Serve anche al controllo di build della 0.58.
- **`bpslib.create()`** (nuovo): crea le patch BPS; prima il progetto sapeva solo applicarle.

## 2. Come sono state scelte le zone

Le regole sono nell'intestazione di `analisi/spazio.py` e sono tutte conservative.

1. **Candidati.** Nella 0.56 ci sono 916 blocchi di zeri da almeno 4 KB, 9,4 MB in tutto. Le prime 0x200000 (codice) non si toccano.
2. **Puntatori.** Si considerano le parole allineate a 4 con valore 0x08000000–0x09FFFFFF e bersaglio allineato.
   - Si scartano come rumore quelle in mezzo a grafica o codice, cioè senza una parola vicina che sia un puntatore, un valore piccolo o 0xFFFFFFFF. Esempi controllati a mano: `0x08bbbbbb` dentro la grafica e istruzioni Thumb lette come numeri.
   - Ogni puntatore rimasto che arriva dentro un blocco esclude 64 KB dal suo bersaglio.
3. **Strutture che finiscono dentro un blocco.** Per il bersaglio credibile più vicino prima della zona si calcola dove finisce la struttura, se è nota:
   - layout, dati della mappa e bordo, per tutti gli 862 layout;
   - tileset: grafica compressa o no (0x4000 byte), tavolozze, 512 metatile e i loro attributi;
   - blob LZ77.

   Se la struttura non è nota si lasciano 64 KB di margine. Per questo, per esempio, i metatile vuoti dei tileset non sono stati presi.
4. **Margine** di 256 byte all'inizio di ogni zona e minimo 4 KB per zona.

Le zone prese sono fissate in `v057_spazio.py`, così la build non dipende dall'euristica:

| Zona | KB | Cosa c'è prima |
|---|---|---|
| 0x391c14–0x394ee6 | 12 | grafica non compressa di un tileset (finisce a 0x391314) |
| 0x47e5b4–0x47fada | 5 | attributi dei metatile (0x47bfb0) |
| 0x502bf0–0x5044c2 | 6 | fine di una struttura di tileset |
| 0x55a408–0x55bdfe | 6 | fine di una struttura di tileset |
| 0xb78f08–0xba0208 | 156 | blocco 0xb6bcb4–0xc00000, margine 64 KB da 0xb68e08 |
| 0xbb09b8–0xbbcccc | 48 | stesso blocco, margine da 0xba08b8 |
| 0xbdcdcc–0xbf59e0 | 99 | stesso blocco, margine da 0xbccccc |
| 0xc98c28–0xcbb500 | 138 | blocco 0xc98b26–0xd00000 |
| 0xccb600–0xcdae40 | 62 | stesso blocco, margine da 0xcbb500 |
| 0xceaf40–0xcf0300 | 20 | stesso blocco, margine da 0xcdae40 |
| 0xef3498–0xf10000 | 114 | blocco 0xee4016–0xf10000, margine da 0xee3398 |

I tre blocchi grandi erano già a zero nella `base31.gba` e nella 0.47.

## 3. Cosa non è stato recuperato, e perché

- **Il "circa 1,4 MB" del prompt.** Con queste regole si prendono 671 KB.
  - Il resto dei blocchi grandi è vicino a puntatori che non posso escludere solo leggendo la ROM.
  - Altri 600 KB circa (0xb6bcb4–0xb78f08, 0xbf59e0–0xc00000, 0xee4016–0xef3498, i 26 KB a 0xe3ce54, 0xf295e8 e 0xf32210) sono probabilmente liberi. Il dubbio riguarda soprattutto 0xf21000, una struttura vuota di lunghezza ignota citata dal codice (0x6ef8c, 0x196ecc).
  - Li prendo solo dopo una prova in emulatore che legga davvero gli accessi alla ROM.
- **Mappa dei simboli di Smeraldo originale.** L'ho provata (`pret/pokeemerald`, branch `symbols`), ma questa ROM non ha la disposizione di Smeraldo:
  - la tabella degli strumenti è a 0x72f194 invece di 0x5839a0;
  - gli sprite dei personaggi sono a 0x6ada3c invece di 0x505620.

  Non è utilizzabile per decidere cosa c'è a un indirizzo.
- **Mappe del gruppo 0: non sono "vecchie mappe di Smeraldo" da liberare.** *(Corretto nella 0.58: la prima stesura di questo punto era sbagliata.)*
  - Il gioco ha riusato gran parte del gruppo 0 per la Romagna: 0.9 è il Lido di Savio (la partenza), 0.10 Cervia, 0.27 Mirabilandia, 0.28 il Safari di Ravenna. I nomi delle zone sono stati riscritti, per questo una mappa di Smeraldo può chiamarsi "IMOLA" (0.12 è fisicamente Lavaridge).
  - Il percorso trovato dal grafo (… → 34.74 → Safari 30.0 → 0.28 → 0.27 → 0.12) è in gran parte il gioco normale. Nella 0.58 `analisi/cammino.py` ha controllato casella per casella: anche ignorando ogni ostacolo, dalla 0.28/0.27 non si arriva a piedi alla 0.12 né alla palestra 4.1. Non è una via d'uscita dalla Romagna.
  - Il gruppo 0 non si libera: è in uso. Restano liberabili solo le singole mappe isolate (elenco sotto).
- **Doppioni 34.10, 34.13, 34.18 e mappe isolate.** Sono davvero irraggiungibili, ma i loro dati di mappa sono piccoli (3,5 KB in tutto, in pezzi sotto i 4 KB). Restano come posti per mappe nuove: l'elenco è sotto.
- **Copie vecchie delle tabelle spostate nella 0.55.**
  - Tabella dei layout a 0x1fd5634: 855 voci, 3,4 KB, nessun riferimento. È sotto i 4 KB minimi, quindi non è stata presa.
  - Nomi delle zone a 0x19b69fc: due strutture uguali (0x15cca48 e 0x19b73c4) puntano a 0x19b69f4, 8 byte prima. Senza capire cosa sono non la tocco (1,7 KB).
- **Grafica di Smeraldo mai usata.** Senza mappa dei simboli non c'è un modo affidabile di riconoscerla. Rinviata.

### Mappe non raggiungibili (70)

Il grafo conta uscite, connessioni, SUB, warp degli script e Volo. Il codice nativo può portare in alcune mappe senza passare dagli script (basi segrete, Club Cavo e sale di collegamento, camion dell'introduzione, Lotta Frontier). Per queste "non raggiungibile" vuol dire solo "nessun evento della ROM ci porta".

- Davvero isolate e riusabili come posti per mappe nuove:
  - 34.10, 34.13 (Cervia) e 34.18 (Cesena);
  - 24.39–24.41 (vecchio Ponte Santerno);
  - 24.50–24.51 (Shoal Cave);
  - 24.74–24.76 (Aqua Hideout);
  - 1.2, 1.3, 2.0, 2.3, 13.8, 27.0, 27.1.
- Da non toccare:
  - 25.0–25.23 (basi segrete), 25.28–25.34 e 25.44–25.59 (Club Cavo), 25.40 (camion), 26.27 (Lotta Frontier): ci porta il codice nativo;
  - 34.115, 35.44, 35.45: il Safari della 0.51 con Suicune e Raikou, che il Lotto 2 deve collegare.

## 4. Test

| Prova | Esito | Tipo |
|---|---|---|
| `python3 build.py` dalla catena completa: 0.54 → 0.55 → 0.56 con gli SHA attesi, poi 0.57 | passa | build |
| Registri in modo rigoroso: 147 condivisioni di flag, nessuna nuova | passa | build |
| Differenze 0.56 → 0.57 solo dentro le zone | 687 400 byte, 0 fuori dalle zone | statico |
| `registri/spazio.json` vede le 11 zone nuove come 0xFF libero | sì (19 zone in tutto) | statico |
| Patch BPS 0.56→0.57 riapplicata alla 0.56 = 0.57 | sì | statico |
| mGBA, 13 savestate di `collaudo/play/`: stesso programma di tasti su 0.56, 0.57 e 0.57 "avvelenata" (zone riempite di byte casuali) | **uguale alla 0.56** in tutti gli 8 punti di controllo (schermo, EWRAM, IWRAM, VRAM, tavolozze, OAM) | emulatore, solo tasti |
| mGBA e VBA-M, salvataggio vero fatto in gioco (menu → SALVA) → titolo → Continua → stesso programma | **uguale alla 0.56**, anche la ROM avvelenata | emulatore, solo tasti |
| Ripetibilità: la 0.56 una seconda volta | uguale | emulatore |

Il collaudo è stato fatto con la consegna della 0.58 (`collaudo/t57.py`, risultati in `collaudo/risultati/057/`). Il programma di tasti: passeggiata, menu, Pokédex, squadra e riassunto, borsa e seconda tasca, passeggiata di ritorno.

- **ROM avvelenata.** Le 11 zone sono riempite di byte casuali (seme 57) invece di 0xFF. Se il gioco leggesse una zona sui percorsi provati, schermo o memoria divergerebbero: non succede.
- **Orologio.** In mGBA l'orologio è fisso. VBA-M usava l'ora vera e i secondi cambiavano anche tra due prove della stessa 0.56, quindi nel collaudo della 0.57 i 20 byte di `sRtc` e `gLocalTime` sono stati esclusi dal confronto. Dalla 0.58 anche VBA-M ha l'ora fissa (vedi la relazione 0.58).
- **Limite.** La prova copre i percorsi giocati (13 punti della partita più il salvataggio), non tutto il gioco. Una zona letta solo da un evento mai attraversato non verrebbe vista: per questo le zone vengono comunque da un'analisi conservativa (§2).

## 5. Risorse

| Risorsa | Usate | Restano |
|---|---|---|
| Spazio | 0 byte scritti dall'engine | 1249 KB nelle zone dell'engine |
| Flag | 0 | 138 nel pool |
| Variabili | 0 | 90 |
| Strumenti | 0 | 67 numeri liberi |

## 6. Stato delle richieste del Lotto 1

| Richiesta | Stato |
|---|---|
| Spazio: blocchi di zeri | **verificato**, 671 KB; collaudo in mGBA e VBA-M con la ROM avvelenata |
| Spazio: mappe del gruppo 0 e doppioni | analizzato: il gruppo 0 è in gran parte usato dalla Romagna (correzione della 0.58), i doppioni sono troppo piccoli; elenco dei posti riusabili sopra |
| Spazio: grafica mai usata, tabelle vecchie | analizzato, non recuperato (§3) |
| Zone aggiunte all'engine con lo stesso controllo | **corretto** |
| Flag, variabili, allenatori, controllo di raggiungibilità nella build, `collaudo/regressione.py`, budget | 0.58 |
