# Pokémon Romagna — documento di progetto

Stato alla **0.56** (SHA-256 `b09eb6977ca7ceaf81be2a184d719ce6cc25229d2889e4cc3c4fa4714237495f`).
Questo è il documento di riferimento: trama, mappe, eventi, indirizzi tecnici e regole di lavoro. La storia delle versioni è in `STORIA_VERSIONI.md`, le prove in emulatore in `COLLAUDO.md`.

## 1. Come è fatto il progetto

```
build.py              punto di ingresso: python3 build.py
bpslib.py             applicazione di patch BPS con controllo dei CRC
basi/                 rom047.gba (= la 0.47) e base31.gba (ROM base con le risorse originali)
storico_054/          builder storico 0.47 → 0.54 (build47.py … build54.py, engine*, assets)
pezzo_055/            patch_054_055.bps + modifiche_055.json/.md (la 0.55 non ha sorgenti)
versioni/             engine.py + un modulo per versione (v056_cesena_rivale.py, …)
registri/             flag, variabili, strumenti, mappe, spazio libero; genera.py li rigenera
strumenti_rom/        lettura di mappe, script, testi (romlib, scr, text_codec, …)
analisi/              dump.py, confronta.py, grid.py, water.py, maps.py …
collaudo/             pilota per mGBA e VBA-M, libreria di gioco, test della 0.56
doc/                  questo documento, storia delle versioni, collaudo
relazioni/            relazioni e audit delle versioni passate (archivio)
out/                  risultati del build (non va nel pacchetto)
```

### Catena di build

Ogni tappa controlla lo SHA-256 atteso e si ferma se non coincide.

| Tappa | Ingresso | Strumento | Uscita | SHA-256 |
|---|---|---|---|---|
| 1 | `basi/rom047.gba` + `basi/base31.gba` | `storico_054/build54.py` (rifà 0.48 → 0.54 in sequenza) | 0.54 | `a0653255…2906` |
| 2 | 0.54 | `pezzo_055/patch_054_055.bps` | 0.55 | `2bfaa8a3…4ad6` |
| 3 | 0.55 | `versioni/v056_cesena_rivale.py` | 0.56 | `b09eb697…495f` |
| 4 | 0.56 | `registri/genera.py` (modo rigoroso) | registri | — |

- Build completa: `python3 build.py` (circa 1 minuto).
- Solo dalla 0.55 in poi: `python3 build.py --da 055` (usa `out/Pokemon_Romagna_0_55.gba` già costruita).
- **La 0.55 resta una patch.** Non è stata fatta in questo progetto e non esistono i suoi sorgenti; `pezzo_055/modifiche_055.md` dice in chiaro cosa cambia (mappe 35.101 e 35.102, 27 mappe modificate, 21 allenatori, due tabelle spostate).

### Come si aggiunge una versione (0.57 e successive)

1. Crea `versioni/v057_<argomento>.py` con una funzione `apply(W)` che usa `engine` (vedi `v056_cesena_rivale.py`). Restituisce un dizionario con il rapporto.
2. Aggiungi `('057', 'v057_<argomento>')` a `VERSIONI` in `build.py`.
3. Lancia `python3 build.py --da 055`. Lo SHA nuovo viene stampato come "nuovo".
4. Collauda (vedi `COLLAUDO.md`). Solo dopo il collaudo copia lo SHA in `SHA` dentro `build.py`.
5. I moduli si applicano in ordine sullo stesso `Writer`: non modificare un modulo di una versione già consegnata, altrimenti cambia lo SHA di tutte quelle successive.

### Regole dell'engine

- `engine.init(rom055)` crea il `Writer` e controlla che la base sia la 0.55.
- Si scrive solo nello spazio libero della 0.55, con 256 byte di margine: 0x155a9b8–0x1580000, 0x15ccd78–0x1600000, 0x19c5a6d–0x1a00000. La 0.56 ne usa una piccola parte all'inizio della prima zona; il resto è in `registri/spazio.json`.
- Flag nuove solo con `engine.pool()`: sono 0x500 + id di allenatori che nessuno script usa, escluse tutte le flag già usate (scansione `flagscan52`).
- Script con `engine.Script`, oggetti con `add_object`, cartelli con `add_bg` / `set_bg_script`.
- Dopo il build, `registri/genera.py` in modo rigoroso fa fallire il build se una flag viene usata da mappe diverse in un modo nuovo (era la causa dei bug Arco/Regice e Katun/Registeel). Le 147 condivisioni della 0.56 sono in `registri/flag_condivise_ammesse.json`; per ammetterne una nuova va aggiunta a mano, dopo averla verificata.

## 2. Trama, città per città

La trama attuale è approvata. Non va cambiata senza chiedere, salvo le richieste del prompt.

| # | Luogo (mappa) | Cosa succede | Come si prosegue |
|---|---|---|---|
| 1 | Lido di Savio (0.9, laboratorio 1.4) | Starter (Treecko, Torchic, Mudkip), nome del rivale ALDO (variabili 0x40fc–0x40ff), prima lotta. Eevee in regalo (34.0). | Pineta del Savio (0.16) |
| 2 | Cervia (0.10) | Team Emilia alle Saline; 1ª medaglia **RIVA** (Acqua); MN TAGLIO; starter di Kanto in regalo (34.8). | Campagna Cervese |
| 3 | Cesena (34.17) | 2ª medaglia **VIOLA** (Erba). Missioni della 0.56: pennelli e Smeargle, tre codici e MT17, rosone e Pietralunare. Hitmon in dono (34.25). | Est: Costa Adriatica → Cesenatico |
| 4 | Cesenatico (34.22) | Grattacielo. | Riviera Romagnola (34.43) con ALDO, serve la 2ª medaglia → Rimini |
| 5 | Rimini (34.44, 34.47) | Le Befane (34.54–34.59) con Ing. Neri e i tre tecnici; MN SPACCAROCCIA; 3ª medaglia **AURELIO**. Starter di Johto in dono (34.48). | Ritorno a Cesena |
| 6 | Cesena ovest | Ippodromo; casello ovest (35.91), oggi controlla la 3ª medaglia (0x869). | Monte Spaccato (35.101) → Capocolle (35.60, Babbi) → Forlimpopoli (35.61, MOSSOMETRO) → Via Emilia Ovest |
| 7 | Forlì (34.68/34.84) | ALDO all'ingresso; 4ª medaglia **IVANO**; MN SURF. | Campagna col fiume (isolotti con 3 istruttori) |
| 8 | Faenza (34.85) | Museo della ceramica; 5ª medaglia **ADA**. | Campagna Ravennate (35.102) → Ravenna |
| 9 | Ravenna (34.94, 34.96) | Si arriva da Faenza o dal Lido (Pianura Romagnola 34.93). Arco del Team Emilia: flag **0x2ac** a missione conclusa. Mirabilandia (34.114) e Safari (gruppo 26). | Casello 35.98 (richiede 0x2ac) → Via dei Canali (35.70) → Campagne di Lugo (35.71) |
| 10 | Lugo (34.110/34.111) | Trasmettitore; 6ª medaglia **ALIDA**. | Sentiero → Galleria dei Sigilli (35.74, i tre Regi) → Faenza |
| 11 | Faenza → Imola (35.1) | Ponte Santerno (35.0) con ALDO e il tecnico, che si sposta con la 6ª medaglia; 7ª medaglia **RINO**; MN FORZA. | Ritorno a Cesena |
| 12 | Cesena sud | Sentiero del Fumaiolo (35.10): ALDO, Team Emilia, Groudon nel Cuore del Fumaiolo (35.17) → Passo dei Draghi (35.18) → Bagno di Romagna (35.19), 8ª medaglia **LEDA**. | Via Vittoria |
| 13 | Finale | Via Vittoria (35.27) con ALDO → Lega Romagna (35.34). | Post-Lega |
| — | Post-Lega | San Marino (35.53–35.58). Decisioni prese: **San Marino e Bologna restano dopo la Lega**; a Bologna c'è la sede del Team Emilia, con una post-trama. | — |

- **Medaglie:** flag da 0x867 (Cervia) a 0x86e (Bagno di Romagna). 0x864 è "Lega vinta".
- **Caselli tra le aree:** mappe 35.79–35.99.
- **Elenco completo delle mappe**, con nome, dimensioni, uscite e blocchi a coordinate: `registri/mappe.json`.

## 3. Leggendari, shiny e doni

Letti dagli script della 0.56. "Raggiungibile" vuol dire che la mappa è collegata al resto del mondo da uscite o connessioni; non vuol dire provato in gioco.

| Pokémon | Livello | Mappa | Quando | Raggiungibile |
|---|---|---|---|---|
| Celebi | 50 | Pineta del Savio 0.16 | durante la storia | sì |
| Rayquaza | 70 | Lugo 34.110 | durante la storia | sì |
| Groudon | 50 | Cuore del Fumaiolo 35.17 | evento della storia | sì |
| Articuno / Zapdos / Moltres | 52 | Santuari del Crinale 35.31 / 35.32 / 35.33 | — | sì |
| Regirock / Regice / Registeel | 40 / 42 / 45 | Galleria dei Sigilli 35.76 / 35.77 / 35.78 | con la 6ª medaglia (0x86c) | sì |
| Kyogre | 70 | fondale di Rimini 35.37 | dopo la Lega (0x864) e 8ª medaglia | sì |
| Entei | 45 | Grotta Ardente 35.100 (dal Safari, 26.12) | dopo la Lega (0x864) | sì |
| Deoxys | 50 | 35.41 (zona RAVENNA) | dopo la Lega | sì |
| Jirachi | 50 | 35.42 (zona CERVIA) | dopo la Lega | sì |
| Mewtwo | 70 | 35.43 (zona CESENATICO) | dopo la Lega | sì |
| **Suicune** | 40 | Safari 34.115 | — | **no** |
| **Raikou** | 40 | Safari 35.45 | dopo la Lega | **no** |
| Entei (seconda copia) | 40 | Safari 35.44 | dopo la Lega | **no** |

**Problema noto (Lotto 2 del prompt):** le tre mappe 34.115, 35.44 e 35.45 sono un Safari costruito nella 0.51 che non è collegato a niente: si collegano solo fra loro. Ravenna (34.94, uscita 10) porta al Safari originale di Smeraldo, gruppo 26 (26.0–26.13). Per questo Suicune e Raikou oggi non si possono catturare, e il secondo Entei non si incontra.

**Shiny:** Torkoal 34.33 (Parco della Rocca di Cesena), Skarmory 34.38 (Cesenatico), Farfetch'd 34.47 (Arco di Rimini), Shuckle 35.61 (Forlimpopoli), giostre di Mirabilandia con Ponyta, Aipom, Marill (35.46–35.48), Smeargle Lv15 dal pittore di Cesena (0.56).

**Doni:** starter a Lido 1.4, Eevee 34.0, starter di Kanto 34.8, Hitmonchan/Hitmonlee 34.25, starter di Johto 34.48, Miltank 35.63 (Capocolle), Chansey 35.66 (Forlimpopoli).

## 4. Strumenti e flag della 0.56

- **PENNELLO:** strumento 0x15b (prima vuoto). Il numero 0x15c è ancora libero; tutti i numeri liberi sono in `registri/strumenti.json`.
- **Flag nuove della 0.56:** pennelli 0x7b3, 0x7b2, 0x7b1; Smeargle consegnato 0x7b0; codici 0x7ad, 0x7ac, 0x7ab, 0x7aa; rosone 0x794, 0x793, 0x792, 0x78a.
- **Missioni del Team Emilia:** tecnici delle Befane 0x27d, 0x27e, 0x27f; Ravenna conclusa 0x2ac.

## 4b. Risorse rimaste dopo la 0.56

- **Spazio nella ROM:** la ROM è a 32 MB, il massimo del GBA, e non si allarga. Restano circa 590 KB sicuri nelle tre zone dell'engine. Candidati da verificare (Lotto 1): circa 1,4 MB di blocchi di zeri senza puntatori, le vecchie mappe di Smeraldo nel gruppo 0, i doppioni 34.10, 34.13, 34.18, la grafica mai usata e le tabelle copiate dalla 0.55.
- **Flag:** 138 nel pool di `engine.pool()`; altre 260 tra 0x20 e 0x4ff non usate da script, da controllare contro il codice di Smeraldo.
- **Variabili:** 90 libere (`registri/variabili.json`).
- **Strumenti:** 67 numeri liberi (`registri/strumenti.json`).

## 5. Indirizzi tecnici

| Cosa | Indirizzo |
|---|---|
| Tabella dei nomi delle zone | 0x74c608 (voci da 8 byte, puntatore al nome a +4) |
| Tabella degli sprite dei personaggi | 0x6ada3c (numeri come in Smeraldo; 59 = Poké Ball) |
| Tavolozze degli sprite | 0x6b4054 |
| Tabella degli strumenti | 0x72f194 (44 byte per voce) |
| Nomi delle specie | 0x32b8ad − 235·11 (11 byte per nome) |
| Tabella dei layout (dalla 0.55) | 0x095aa02c |
| Nomi delle zone per la mappa regionale (dalla 0.55) | 0x095cc080 |
| Routine nativa per il nome del rivale | 0x19b8a2c |
| Comando nativo per il dono shiny | NATIVE_SHINY_GIFT = 0x09730069 |
| gSelectedObjectEvent | 0x03005df0 |
| gSpecialVar_LastTalked | 0x020375f2 |
| Stato dello script attivo (collaudo) | byte 0x03000e41 (0 = nessuno script) |
| Mappe | il gruppo 33 contiene una vecchia copia della tabella del gruppo 34: usare `flagscan52.real_maps`, non contare 33.1–33.110 |

## 6. Lezioni imparate

1. **`faceplayer` e `gSelectedObjectEvent`.** Nei cartelli, o dopo una ricarica della mappa (schermata del nome, borsa…), `faceplayer` usa un indice rimasto da prima. Riporta l'oggetto selezionato su quello giusto. È stata la causa del "nel nulla" dopo il rivale nella 0.53.
2. **Schermate a tutto schermo.** Prima di aprirne una: `closemessage` e `fadescreen`, come il gioco originale.
3. **Acqua al livello 1.** Se l'acqua sta allo stesso livello della terra ci si cammina sopra (Pianura Romagnola fino alla 0.54).
4. **Puntatori di script con prefisso 0x08/0x09.** Un puntatore 0x01… porta a eseguire byte a caso, con esiti diversi a seconda dell'emulatore (cartelli di Forlimpopoli fino alla 0.46).
5. **Testi dentro dati compressi.** Quando ripunti testi, escludi le parole che stanno dentro blob LZ77 o grafica (0.53).
6. **Flag condivise.** Una flag usata da due mappe per scopi diversi fa sparire o ricomparire cose a caso: per questo c'è il controllo rigoroso nei registri.
7. **Callback e menu.** Sostituire una callback con un indirizzo "vicino" può aprire altre schermate (0x080860d5 apre il menu START): si usa la callback originale, 0x0808610d.
8. **Collaudo onesto.** Le scritture in RAM sono solo fixture dichiarate, mai una prova di vittoria o di sblocco. Si aspetta la fine dei dialoghi leggendo 0x03000e41, non premendo A alla cieca.
9. **Mappe raggiungibili.** Una mappa che esiste non è per forza raggiungibile: il Safari della 0.51 ne è l'esempio. Controlla le uscite entranti in `registri/mappe.json`.
