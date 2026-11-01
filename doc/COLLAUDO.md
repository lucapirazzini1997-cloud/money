# Collaudo in emulatore

Le prove si fanno giocando con i soli tasti, in un emulatore senza finestra pilotato da Python. Gli strumenti sono in `collaudo/`.

## 1. Preparazione

```sh
cd collaudo
./prepara_emulatori.sh        # scarica e compila mGBA e il core VBA-M (servono git, cmake, gcc, make)
cd .. && python3 build.py      # costruisce out/Pokemon_Romagna_0_56.gba
```

- `./h` è il pilota per mGBA (sorgente `h.c`, compilato contro `libmgba`).
- `vb.py` è il pilota per il core VBA-M di libretro, con lo stesso protocollo. Lo si usa impostando `VBAM=1`. VBA-M è il motore degli emulatori per iPhone, per questo ogni versione va provata almeno una volta anche lì.
- Versioni usate per la 0.56: mGBA `fd9dc5c2cbf2`, vbam-libretro `115defb3a318` (fissate nello script).
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
| `play/` | savestate di partenza della partita di prova (vedi sotto) e `p51.sav` |

Esempio: `cd collaudo && python3 t56c.py` (consegna dei pennelli partendo da `t56_pennelli.ss`).

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
