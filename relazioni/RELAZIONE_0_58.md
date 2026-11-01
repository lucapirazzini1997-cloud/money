# Pokémon Romagna 0.58: registri e controlli (Lotto 1, seconda parte)

**Base:** 0.57, SHA-256 `47f53668d8b5861956938cd041fb892e541b86031e4ac7b4337e8328923897c4`, rifatta da `python3 build.py` in una cartella pulita con tutti gli SHA attesi (0.54, 0.55, 0.56, 0.57).

**Risultato:** `Pokemon_Romagna_0_58.gba`, SHA-256 `47f53668d8b5861956938cd041fb892e541b86031e4ac7b4337e8328923897c4`.
- **È la stessa ROM della 0.57, byte per byte.** La 0.58 cambia gli strumenti del progetto (registri, pool, controlli di build, collaudo), non il gioco.
- Patch BPS 0.57→0.58: `rom/Pokemon_Romagna_0_57_to_0_58.bps` (29 byte, "nessuna modifica"), verificata riapplicandola.
- Lo SHA è in `SHA` dentro `build.py` dopo la regressione in mGBA e VBA-M (§6).
- Salvataggi: compatibili. La ROM è la stessa.

Con questa versione viene consegnato anche il **collaudo della 0.57**, che prima mancava: superato, vedi `RELAZIONE_0_57.md` §4.

## 1. Flag 0x20–0x4FF: 260 non usate dagli script, 41 sicure

`analisi/flag_sicure.py`. Una flag è sicura solo se nessuna di queste fonti la usa:

1. **Script della ROM.** Due scansioni insieme: `registri/flag.json` e `flagscan52`. La prima non segue gli script che partono dopo una lotta; è così che 0x4CA (impostata dopo una lotta in 35.16) sembrava libera.
2. **Oggetti nascosti delle mappe della ROM.** Il codice usa la flag 0x1F4 + numero dell'oggetto.
3. **Codice e dati di Smeraldo** (sorgente pret/pokeemerald, commit `731ad5bf`): ogni costante `FLAG_*` citata in `src/`, `include/` e `data/`. Comprese le mappe di Hoenn, che sono ancora nella ROM, e gli intervalli usati con un indice:
   - allenatori registrati nel Pokénav: 0x15C + numero di rivincita, 78 flag;
   - decorazioni;
   - giocatori della Union Room;
   - carte del Dono Segreto.

   Il risultato è salvato in `registri/flag_smeraldo.json`, così la build non ha bisogno del sorgente.
4. **Codice della ROM.** Ogni chiamata a FlagSet, FlagClear e FlagGet con il numero calcolabile dalle istruzioni precedenti.
   - Le funzioni sono a 0x809D8D4, 0x809D8FC e 0x809D924: i simboli di Smeraldo + 0x194, verificati decodificando setflag, clearflag e checkflag nella tabella dei comandi a 0x1DBA9C.
   - Le 80 chiamate con numero non calcolabile le ho guardate una per una: sono tutte funzioni di Smeraldo che usano un indice, già coperte dal punto 3 (allenatori, decorazioni, Volo, Pokénav, Dono Segreto).
   - Nessun puntatore a queste funzioni fuori dal codice.

| | Flag |
|---|---|
| Non usate dagli script (0x20–0x4FF) | 260 |
| Escluse perché usate da un **oggetto nascosto** (0x1F4–0x263) | 112 |
| Escluse perché citate dal **codice o dai dati di Smeraldo** | 78 |
| Escluse perché usate dal **codice della ROM** (chiamata con numero calcolato) | 21 |
| Escluse perché citate solo da **script di mappa di Smeraldo** (prudenza) | 8 |
| **Sicure** | **41** |

Le 41 flag: 0x22, 0x28, 0x2C, 0x34, 0x35, 0x3C, 0x3E, 0x45, 0x96, 0x1AB, 0x1DA, 0x1DE–0x1E3, 0x278, 0x296–0x29A, 0x2AE, 0x2B7–0x2BB, 0x2D9, 0x339, 0x467, 0x468, 0x470, 0x472, 0x4B4, 0x4DD–0x4DF, 0x4EC, 0x4ED. Il motivo di ogni esclusione è in `registri/risorse_libere.json`.

**Esempi di flag "libere" che non lo erano:**
- 0x15D–0x1A9: registrazioni del Pokénav;
- 0x1E5–0x1F3: Dono Segreto, azzerate dal codice a ogni nuova partita;
- 0x72, 0x80, 0x8A: chiamate di Scott e Roxanne, lette dal codice.

## 2. Variabili: 87 non usate dagli script, 47 sicure

`registri/variabili.json` ne contava 90 libere. Ne restano 87 con una scansione che conta qualunque argomento 0x4000–0x40FF di qualunque comando e segue gli script dopo le lotte. Di queste, **40 le usa il codice di Smeraldo**. Usarle avrebbe rotto il gioco in modo difficile da capire, per esempio:

| Variabile | Uso nel codice di Smeraldo |
|---|---|
| 0x4021 | passi rimasti del Repellente |
| 0x402A, 0x402B | contapassi dell'amicizia e del veleno |
| 0x4040 | giorni trascorsi (eventi giornalieri) |
| 0x4046 | Pokédex nazionale |
| 0x404B, 0x404C | numeri della lotteria |
| 0x40EA–0x40F1 | contatori giornalieri, basi segrete, TV |

Restano **47 variabili sicure** (`versioni/v058_registri.py`, `VAR_SICURE_058`). Le variabili 0x4000–0x400F (temporanee, azzerate a ogni cambio di mappa) e 0x4010–0x401F (grafica degli oggetti) sono escluse.

**Regola per le missioni a più passi:** si usa una variabile come contatore, presa con `engine.variabili().var('motivo')`, invece di una flag per ogni passo. Un contatore da 0 a N occupa una variabile al posto di N flag.

## 3. Pool delle flag (engine.pool)

`v058_registri.apply(W)` ricontrolla le 41 flag e le 47 variabili sulla ROM che sta costruendo. Una sola che risultasse usata fa fallire la build. Poi riordina il pool:

1. prima le **41 flag sicure** 0x20–0x4FF;
2. poi le **flag di allenatore** rimaste (0x500 + numero), tolte quelle degli allenatori che:
   - combattono in qualunque script, anche con id locale diverso da 0 (la scansione della 0.56 vedeva solo l'id 0);
   - sono citati dal codice di Smeraldo (tabella delle rivincite, Pokénav, Lotta Frontier).

| | Prima (0.57) | Dopo (0.58) |
|---|---|---|
| Flag nel pool | 138 (tutte di allenatore) | **47** (41 sicure + 6 di allenatore) |

Il pool è più piccolo ma pulito. Le flag già prese dalla 0.56 restano dove sono: l'ordine nuovo vale solo per le flag date d'ora in poi, quindi gli SHA della 0.56 e della 0.57 non cambiano.

## 4. Registro degli allenatori (registri/allenatori.json)

Ogni numero da 1 a 0x35F ha uno stato:

| Stato | Numeri | Cosa vuol dire |
|---|---|---|
| usato | 634 | combatte in uno script di una mappa |
| Smeraldo | 159 | non combatte, ma il codice di Smeraldo cita il numero (rivincite, Pokénav...) |
| riservato | 41 | la sua flag è presa dal pool o usata da uno script come flag normale |
| forse usato | 11 | solo la scansione grezza di tutta la ROM vede una sequenza simile a una lotta (spesso byte di puntatori): fuori dal pool per prudenza |
| **libero** | **18** | usabile per un allenatore nuovo |

**Controllo di build** (`registri/controlli.py`). La build fallisce se un allenatore che combatte ha la flag presa dal pool, oppure impostata da uno script di un'altra mappa. I conflitti già noti sono in `registri/allenatori_ammessi.json`, con il motivo.

**Trovato con il registro (segnalato, non corretto):**
- **Allenatrice 650 (Danielle) e flag 0x78A del rosone.**
  - La 0.56 ha preso dal pool la flag 0x78A per il rosone della chiesa di Cesena (34.37). È anche la flag di Danielle, allenatrice della palestra di Lavaridge di Smeraldo (mappa 4.1, lotta con id locale 5).
  - Se Danielle venisse battuta, il cartello del rosone (che come prima cosa controlla 0x78A) si comporterebbe come "già risolto".
  - **Oggi non succede.** La 4.1 e la 0.12 non si raggiungono: nemmeno a piedi in modo ottimistico (§5) e non sono destinazioni del Volo.
  - Il conflitto è quindi latente ed è ammesso solo a una condizione: se una versione futura rende raggiungibili 4.1 o 0.12, la build fallisce. La correzione giusta, se servirà, è spostare Danielle su un numero libero: chi ha già salvato non perde nulla.
- **Flag della 0.56 su numeri della tabella delle rivincite.**
  - Le flag 0x792–0x794 (rosone), 0x7AA–0x7AD (codici) e 0x7B0–0x7B3 (pennelli e Smeargle) sono di allenatori che il codice di Smeraldo legge per le rivincite: Wally VR 3–5, John & Jay 2–5, Lila & Roy 2–5.
  - Le rivincite partono solo con il Pokénav, che nel menu di questo gioco non c'è. Rischio basso, segnalato.
  - Dalla 0.58 il pool non dà più flag di questo tipo.

## 5. Controllo di raggiungibilità nella build

`registri/controlli.py` usa `analisi/raggiungibili.py`, che conta uscite, connessioni, SUB e risalita, warp degli script e Volo. Il risultato è in `registri/raggiungibilita.json`.

**La build fallisce se non si raggiunge:**
- una mappa con un dono (givemon o giveegg);
- una mappa con un leggendario (setwildbattle con una specie leggendaria);
- una mappa nuova, cioè assente da `registri/mappe_base.json` (le 739 mappe della 0.57).

| | |
|---|---|
| Mappe | 739, raggiunte 669 |
| Mappe con doni o leggendari | 36 |
| Non raggiunte, ammesse | 3: Safari della 0.51, cioè 34.115 (Suicune), 35.44 (Raikou), 35.45 (Entei). Vanno collegate nel Lotto 2 (`irraggiungibili_ammesse.json`) |

**Nuovo: `analisi/cammino.py`, raggiungibilità a piedi.**
- Il grafo collega due mappe anche se il bordo è un muro di alberi. Il cammino invece visita le caselle senza collisione, passando dai bordi e dalle uscite.
- È ottimistico: ignora salti, acqua, rocce e persone, quindi "non raggiungibile a piedi" è un risultato forte.
- 644 mappe si raggiungono a piedi. 25 sono raggiungibili nel grafo ma non a piedi: Lavaridge 0.12 e la sua palestra, la Torre dei Cieli 24.84–24.93 e poche altre. Il Volo non è contato nel cammino.

**Avvisi (non fanno fallire la build):**
- uovo di Wynaut (Lavaridge 0.12);
- Rayquaza della Torre dei Cieli (24.85).

Sono mappe di Smeraldo rimaste senza accesso a piedi. Rayquaza si trova comunque nella 34.110.

## 6. collaudo/regressione.py

La stessa partita di prova su una ROM, con una tabella dei risultati.

**Partenze:**
- mGBA: i 13 savestate di `collaudo/play/`;
- mGBA e VBA-M: un salvataggio vero fatto in gioco (menu → SALVA), poi titolo → Continua.

**Programma di tasti:** passeggiata, menu, Pokédex, squadra e riassunto, borsa e seconda tasca, ritorno.

**Esiti:**
- l'emulatore risponde fino alla fine;
- lo schermo cambia e l'ultimo non è di un solo colore;
- la callback principale del gioco punta sempre nella ROM;
- con `--rif`, confronto con una ROM di riferimento su schermo, EWRAM, IWRAM, VRAM, tavolozze e OAM.

Uso: `python3 collaudo/regressione.py ROM.gba --rif ROM_RIF.gba`

**Risultato sulla 0.58 contro la 0.56** (`collaudo/risultati/058/regressione.md`):

| Partenza | Gira | Vivo | Callback nella ROM | Rispetto alla 0.56 |
|---|---|---|---|---|
| mGBA, 13 savestate | sì | sì | sì | uguale (13 su 13) |
| mGBA, salvataggio → Continua | sì | sì | sì | uguale |
| VBA-M, salvataggio → Continua | sì | sì | sì | uguale |

## 7. Strumenti di collaudo sistemati

Senza questi interventi il collaudo non partiva o non era ripetibile.

- **`./h` (mGBA) andava in crash all'avvio.** Era compilato senza le stesse `-D` della libreria (`ENABLE_DIRECTORIES` cambia la struttura `mCore`). `prepara_emulatori.sh` ora le prende da `flags.make`.
- **Log di mGBA spento.** Usciva su stderr, lo stesso canale delle risposte.
- **Orologio ripetibile in mGBA:** RTC finto che parte dall'1/1/2026 alle 12:00. Con `H_WALLCLOCK=1` si usa l'ora vera.
- **Orologio ripetibile in VBA-M.**
  - VBA-M leggeva l'ora vera. Due prove della stessa ROM a dieci minuti di distanza davano memoria diversa (bacche ed eventi a tempo).
  - `prepara_emulatori.sh` applica una modifica di una riga a `RTC.cpp` (variabile `VBAM_ORA_FISSA`), che `vb.py` imposta sempre.
  - Verificato: due prove a un minuto di distanza danno lo stesso risultato.
- **`vb.py` carica un `.sav`**, come `./h`. Così VBA-M può provare un salvataggio vero.
- **`drv.py`** scarta le righe di stderr che non sono risposte e le tiene in `e.junk`, invece di desincronizzarsi.
- Il vecchio `play/p51.sav` è vuoto (tutto 0xFF). Il salvataggio per VBA-M ora si fa in gioco dal savestate `t56_reload`.

## 8. Test

| Prova | Esito | Tipo |
|---|---|---|
| `python3 build.py` in una cartella pulita: 0.54 → 0.55 → 0.56 → 0.57 → 0.58, tutti gli SHA attesi | passa | build |
| Registri rigorosi: 147 condivisioni di flag, nessuna nuova | passa | build |
| Ricontrollo delle 41 flag e 47 variabili sulla ROM in costruzione | passa (aveva trovato 0x4CA, tolta) | build |
| Controlli: allenatori (1 conflitto, ammesso e latente), raggiungibilità (0 problemi) | passa | build |
| **Prova negativa** (`collaudo/test_controlli.py`): una lotta cambiata in allenatore 682 (flag del pool) | la build **fallisce** come deve | statico, su copia della ROM |
| **Prova negativa:** l'uscita verso 34.8 (dono di Bulbasaur, Charmander, Squirtle) girata altrove | la build **fallisce** come deve | statico, su copia della ROM |
| Regressione 0.58 contro 0.56, mGBA (14 partenze) e VBA-M (1 partenza) | 15 su 15 uguali | emulatore, solo tasti |
| Patch BPS 0.57→0.58 riapplicata | sì | statico |

**Fixture dichiarate:** nessuna scrittura in RAM. Solo tasti.

**Non verificato:**
- Il conflitto Danielle/rosone non è stato provato in gioco. La 4.1 non si raggiunge, quindi in gioco non si può far succedere; il cartello che legge 0x78A l'ho letto nel codice dello script.
- Le esclusioni delle flag vengono dal sorgente di Smeraldo e da una lettura del codice della ROM, non da una prova.
  - Il codice aggiunto dal gioco che scrive direttamente nella memoria delle flag, senza passare da FlagSet, non sarebbe visto.
  - Nelle chiamate lette non ce n'è traccia.
- Il cammino a piedi non conta il Volo e non vede i blocchi degli script. Per questo i suoi risultati sono avvisi, non errori.
- La regressione copre i 13 punti della partita di prova e un salvataggio, non tutto il gioco.

## 9. Budget (risorse usate e rimaste)

| Risorsa | Usate nella 0.58 | Restano |
|---|---|---|
| Spazio nelle zone dell'engine | 0 byte | 1249 KB |
| Flag del pool | 0 | 47 (41 sicure 0x20–0x4FF + 6 di allenatore) |
| Variabili | 0 | 47 |
| Strumenti (numeri) | 0 | 67 |
| Allenatori (numeri liberi) | 0 | 18 (più 159 "Smeraldo", da usare solo dopo aver controllato le rivincite) |

Il budget viene calcolato a ogni build (`out/rapporto_build.json`, voce `budget`) e va copiato in ogni relazione.

## 10. Stato delle richieste del Lotto 1

| Richiesta | Stato |
|---|---|
| Spazio: blocchi di zeri, zone nell'engine con lo stesso controllo | **verificato** (0.57, collaudo in mGBA e VBA-M con ROM avvelenata) |
| Spazio: gruppo 0, doppioni 34.10/34.13/34.18, grafica, tabelle vecchie | analizzato (0.57; il gruppo 0 è in uso dalla Romagna, correzione in questa versione) |
| Flag 0x20–0x4FF controllate contro il codice di Smeraldo, solo le sicure nel pool | **corretto e verificato in build**: 41 su 260 |
| Variabili: 90 libere, contatori per le missioni | **corretto**: 47 sicure, `engine.variabili()` |
| Registro allenatori, build che fallisce su numero riservato | **corretto, verificato con prova negativa** |
| Controllo di raggiungibilità nella build (warp di script, SUB, Volo) | **corretto, verificato con prova negativa**; in più il cammino a piedi |
| `collaudo/regressione.py` con tabella | **fatto**, usato su questa versione |
| Budget in ogni relazione | **fatto** (§9, calcolato dalla build) |
| Danielle/rosone 0x78A | **segnalato**, latente, bloccato dalla build se diventa raggiungibile |
