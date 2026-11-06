# Collaudo in emulatore

Le prove si fanno giocando con i soli tasti, in un emulatore senza finestra pilotato da Python. Gli strumenti sono in `collaudo/`.

## 1. Preparazione

```sh
cd collaudo
./prepara_emulatori.sh        # scarica e compila mGBA e il core VBA-M (servono git, cmake, gcc, make)
cd .. && python3 build.py      # costruisce le ROM in out/
```

- `./h` è il pilota per mGBA (sorgente `h.c`, compilato contro `libmgba`).
- `vb.py` è il pilota per il core VBA-M di libretro, con lo stesso protocollo. Lo si usa impostando `VBAM=1`. VBA-M è il motore degli emulatori per iPhone, per questo ogni versione va provata almeno una volta anche lì.
- Versioni usate dalla 0.56: mGBA `fd9dc5c2cbf2`, vbam-libretro `115defb3a318` (fissate nello script).
- `./h` va compilato con le stesse `-D` della libreria (lo script le prende da `flags.make`): senza, la struttura `mCore` non coincide e il pilota va in crash all'avvio (sistemato nella 0.58).
- **Orologio ripetibile.** `./h` usa un orologio finto che parte dall'1/1/2026 alle 12:00 (`H_WALLCLOCK=1` per l'ora vera). Per VBA-M lo script modifica una riga di `RTC.cpp` e `vb.py` imposta `VBAM_ORA_FISSA` (`VBAM_ORA_VERA=1` per l'ora vera). Senza, due prove della stessa ROM danno memoria diversa (bacche, eventi giornalieri).
- `vb.py` accetta un `.sav` come secondo argomento, come `./h`. `drv.py` scarta le righe di stderr che non sono risposte (in `e.junk`).
- Serve Pillow (`pip install pillow`) per gli screenshot.

### Variabili d'ambiente

| Variabile | Default | Uso |
|---|---|---|
| `ROMF` | `../../out/Pokemon_Romagna_0_56.gba` | ROM da provare, relativa a `PLAY_DIR` |
| `PLAY_DIR` | `collaudo/play` | savestate di partenza, screenshot, log |
| `EMU_DIR` | `collaudo` | cartella con `drv.py` e `./h` |
| `VBAM` | vuota | se impostata usa VBA-M invece di mGBA |
| `VBAM_CORE` | `collaudo/vbam-libretro/src/libretro/vbam_libretro.so` | core VBA-M |

## 2. I file

| File | Cosa fa |
|---|---|
| `drv.py` | classe `Emu`: tasti, frame, lettura e scrittura della RAM, screenshot, savestate |
| `pl.py` | libreria di gioco: posizione, squadra, flag e variabili; `route`/`walkto` (percorso sulla griglia delle collisioni), `travel` (viaggio fra mappe), `battle` (lotta automatica con la mossa migliore), `grind`, `hunt`, `throw`, `heal`, `teach_tm` |
| `go2.py`, `look.py` | camminare seguendo una stringa di direzioni; guardarsi intorno con screenshot |
| `gate.py` | prova di un blocco: va verso una destinazione e registra dove finisce |
| `fx.py` | **fixture dichiarata**: carica uno stato, imposta o azzera flag in RAM, salva un nuovo stato |
| `prog.py`, `prog2.py`, `prog3.py` | percorso Lugo → Galleria dei Sigilli → Faenza → Ponte Santerno → Imola → palestra |
| `t56a.py` | 0.56: pittore, tre pennelli nel labirinto, Smeargle shiny |
| `t56b.py`, `t56c.py`, `t56full.py` | 0.56: consegna dei pennelli, controllo della borsa e della cromaticità |
| `t56lib.py`, `t56w.py` | 0.56: Biblioteca Malatestiana, ordine giusto e sbagliato dei codici |
| `t56ch.py` | 0.56: chiesa e rosone |
| `t56r.py`, `t56r2.py` | 0.56: nome del rivale dal personaggio del laboratorio |
| `save56.py` | salvataggio dal menu del gioco, riavvio da zero, "Continua", confronto dello stato |
| `t61.py` | collaudo della 0.61: Regi a piedi senza abilità, sbarra del Sentiero senza la 6ª medaglia, razzo e portale prima e dopo la Lega, Deoxys, Jirachi, Mewtwo (fuga, KO su Regirock, cattura, ricarica), vecchio salvataggio della 0.60 |
| `t62.py` | collaudo della 0.62: i sette doni (MN e strumenti chiave) presi a tasti, controllo nella BORSA, ricarica, uscita e rientro; rifiuti del SUPER AMO senza 5ª medaglia e di SUB senza 8ª |
| `t63.py` | collaudo della 0.63: Cesena → casello → Ippodromo → Monte Spaccato dalla prima visita; rocce e corridoi chiusi senza la 3ª medaglia; rocce rotte, passaggio aperto (flag 0x22), ricarica; vecchio salvataggio a Capocolle che torna a Cesena |
| `t64.py` | collaudo della 0.64: Campagna Cesenate dalla prima visita (porta della casa, cartelli, roccia che rifiuta), lotte con i tre allenatori nuovi, roccia rotta e passaggio a 35.92, ricarica dentro la mappa; vecchi salvataggi veri della 0.63 e della 0.62 fatti dentro la mappa vecchia (`crea63` sulla ROM 0.63). `vecchie_pos_064.py`: caselle calpestabili nella mappa vecchia da cui nella nuova non si esce |
| `t65.py` | collaudo della 0.65: Ridracoli dalla guida di Forlì (35.50 → 35.51), centrale, quattro allenatori (due reclute che vedono il giocatore), CORRADO che rifiuta e poi lotta, il GYARADOS che emerge; fuga, KO e cattura del GYARADOS cromatico, ricarica e rientro; sorgente con CASCATA (salita a tasti) e ACQUA MAGICA; vecchio salvataggio vero della 0.64 dentro la mappa (`crea64` sulla ROM 0.64). `testi_065.py`, `confronto_bozza_065.py`, `vecchie_pos_065.py`: controlli statici |
| `t66.py` | collaudo della 0.66: il nuovo Fumaiolo. Ingresso da Cesena, ALDO che lotta all'arrivo, cartelli, guide, rifugio, Eremo con il masso di FORZA, grotte, stele del TEVERE; nodi del TEAM EMILIA, BASSI, porta profonda, GROUDON (MASTER BALL), uscita dal Cuore, frane prima e dopo, Passo fino a Bagno; ritorno da Ridracoli; vecchio salvataggio vero della 0.65 dentro la vecchia grotta (`crea65` sulla ROM 0.65). `testi_066.py`, `confronto_bozza_066.py`, `analisi_066.py`, `riassunto_t66.py`: controlli statici e riassunto |
| `t60.py`, `leg.py` | collaudo della 0.60 (Kyogre e uccelli) e funzioni comuni per le prove sui leggendari (fixture dichiarate: medaglie, mosse, Master Ball, posizione, allenatori) |
| `t59.py`, `vai.py` | collaudo della 0.59 (cani leggendari) e navigatore: porta il giocatore dove serve solo con i tasti, con il percorso di `analisi/percorso.py`, combattendo le lotte selvatiche |
| `regressione.py` | **regressione** (dalla 0.58): stessa partita di prova su tutte le partenze, tabella dei risultati, confronto con una ROM di riferimento |
| `t57.py` | collaudo della 0.57: confronto 0.56 / 0.57 / 0.57 con le zone recuperate riempite di byte casuali |
| `test_controlli.py` | prova negativa dei controlli di build (allenatore con flag riservata, dono irraggiungibile) |
| `risultati/` | risultati dei collaudi da tenere (tabelle e hash), una cartella per versione |
| `play/` | savestate di partenza della partita di prova (vedi sotto) e `p51.sav` (vuoto: tutto 0xFF) |

Esempio: `cd collaudo && python3 t56c.py` (consegna dei pennelli partendo da `t56_pennelli.ss`).

### Regressione

```sh
python3 collaudo/regressione.py out/Pokemon_Romagna_0_66.gba --rif out/Pokemon_Romagna_0_65.gba
```

- **Partenze:** i 13 savestate in mGBA, più un salvataggio vero fatto in gioco (menu → SALVA dal savestate `t56_reload`) e caricato con Continua in mGBA e in VBA-M.
- **Programma di tasti:** passeggiata, menu, Pokédex, squadra e riassunto, borsa e seconda tasca, ritorno.
- **Esiti per partenza:**
  - gira;
  - schermo vivo;
  - callback del gioco nella ROM;
  - con `--rif`, uguale o diverso dal riferimento (schermo, EWRAM, IWRAM, VRAM, tavolozze, OAM).
- **Risultati:** tabella in `regressione.md`, nella cartella data con `--uscita`. Circa 25 minuti con il riferimento.
- **Lettura:** per una versione che non cambia il gioco tutto deve essere uguale. Per una che lo cambia, le differenze vanno spiegate.

## 3. Savestate di partenza

Sono stati della partita giocata in emulatore (squadra di uno-tre Pokémon). Letti con `pl.G(nome).pos()`:

| File | Mappa | Dove |
|---|---|---|
| `q8_end.ss` | 1.4 | laboratorio di Lido, appena scelto lo starter (dalla 0.54) |
| `t56_rename.ss`, `t56_rename2.ss` | 1.4 | laboratorio di Lido, davanti al personaggio del nome del rivale |
| `s_ce3.ss` | 34.17 | Cesena, piazza (dalla 0.51) |
| `t56_pennelli.ss` | 34.33 | labirinto del Parco della Rocca |
| `t56_smeargle.ss`, `t56_lib2.ss` | 34.17 | Cesena, accanto al pittore |
| `t56_lib_out.ss` | 34.24 | Biblioteca Malatestiana |
| `t56_church.ss`, `t56_reload.ss` | 34.37 | chiesa di Cesena |
| `gpre.ss` | 35.71 | Campagne di Lugo, prima di una lotta |
| `prog_b6b.ss` | 35.0 | Ponte Santerno |
| `prog_imola.ss` | 35.9 | verso Imola |

Un savestate porta con sé la RAM della versione in cui è stato fatto: se una versione nuova cambia uno script già in esecuzione nello stato, riparti da un punto prima dell'evento o da un salvataggio `.sav`.

## 4. Regole

1. **Solo tasti.** Le scritture in RAM sono ammesse solo come fixture tecniche dichiarate nella relazione (per esempio "sesta medaglia messa da emulatore"), mai come prova di una vittoria o di uno sblocco.
2. **Fine dei dialoghi.** Il byte 0x03000e41 vale 0 quando nessuno script è attivo: aspetta quello invece di premere A un numero fisso di volte.
3. **Ogni evento nuovo:** si avvia; il premio arriva davvero; il flag sopravvive a salvataggio dal menu e ricarica; si esce e si rientra nella mappa.
4. **Ogni passaggio modificato:** percorribile nei due versi, senza rimbalzi e senza uscire su un ostacolo.
5. **Percorsi automatici.** Prima di scegliere una casella di arrivo, controlla la collisione della casella accanto: il percorso automatico considerava libera la casella di arrivo anche quando non lo era.
6. **Relazione onesta:** separare "provato giocando", "provato con fixture" e "solo letto nella ROM", e scrivere sempre l'elenco del non verificato.

## 5. Controlli statici

Non sostituiscono la prova in gioco, ma vanno fatti a ogni versione:

- `python3 build.py`: SHA di ogni tappa e registri in modo rigoroso (flag condivise nuove = build fallito).
- `python3 analisi/dump.py out/Pokemon_Romagna_0_56.gba 34.94`: uscite, oggetti, eventi e script di una mappa.
- `python3 analisi/confronta.py A.gba B.gba diff.json`: cosa cambia fra due ROM.
- `analisi/water.py`, `analisi/elev.py`: acqua calpestabile.
- `registri/mappe.json`: per ogni mappa nuova controlla che qualcuno ci entri (uscite o connessioni entranti).

## 6. Note dalla 0.59

- **Savestate e ROM diverse.** Un savestate conserva in SaveBlock1 la copia degli oggetti della mappa, con i puntatori agli script della ROM su cui è stato fatto. Per confrontare due ROM dallo stesso savestate bisogna prima uscire dalla mappa e rientrare (`t59.py` lo fa con `--rif`).
- **VBA-M scrive il salvataggio.** Dalla 0.59 `vb.py` riscrive il file `.sav` al `ping` e all'uscita, come mGBA: prima un salvataggio fatto in gioco su VBA-M si perdeva.
- **Regressione dal salvataggio vero:** dopo Continua, Smeraldo copia i puntatori agli script di tutti i 64 oggetti della tabella della mappa, anche oltre il numero reale. Se dopo la tabella c'è spazio usato da una versione nuova, quei byte di EWRAM cambiano: è atteso e innocuo (vedi `RELAZIONE_0_59.md` §4).
- **Fixture di posizione (dalla 0.60):** per partire da un punto della storia senza savestate si scrive la posizione in SaveBlock1 **e** nell'oggetto del giocatore (Continua ripristina anche quello), poi si salva in gioco e si continua dal titolo (`leg.fixture_posizione`).
- **SUB:** per immergersi A sull'acqua profonda; per risalire **B** sott'acqua; poi "sì".
