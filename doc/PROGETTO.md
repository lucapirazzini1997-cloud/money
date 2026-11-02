# Pokémon Romagna — documento di progetto

Stato alla **0.60** (SHA-256 `d9ca40b3…183a`, collaudata). Lotto 2 in corso: 0.59 cani leggendari, 0.60 Kyogre e uccelli, 0.61 Regi, Deoxys/Jirachi/Mewtwo e tabella completa.
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
analisi/              dump.py, confronta.py, grid.py, water.py, maps.py, spazio.py, raggiungibili.py,
                      cammino.py (raggiungibilità a piedi), flag_sicure.py (flag e variabili sicure) …
collaudo/             pilota per mGBA e VBA-M, libreria di gioco, regressione.py, test delle versioni, risultati/
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
| 3 | 0.55 | `versioni/v056_cesena_rivale.py`, `v057_spazio.py`, `v058_registri.py`, `v059_cani.py`, `v060_kyogre_uccelli.py` | 0.56–0.60 | `b09eb697…495f`, `47f53668…97c4`, `47f53668…97c4`, `aee694c2…ec1d`, `d9ca40b3…183a` |
| 4 | ultima | `registri/genera.py` (modo rigoroso) | registri | — |
| 5 | ultima | `registri/controlli.py` (allenatori, raggiungibilità, risorse, budget) | registri, `out/rapporto_build.json` | — |

- Build completa: `python3 build.py` (circa 3 minuti, di cui uno e mezzo per il cammino a piedi dei controlli).
- Solo dalla 0.55 in poi: `python3 build.py --da 055` (usa `out/Pokemon_Romagna_0_55.gba` già costruita).
- **La 0.55 resta una patch.** Non è stata fatta in questo progetto e non esistono i suoi sorgenti; `pezzo_055/modifiche_055.md` dice in chiaro cosa cambia (mappe 35.101 e 35.102, 27 mappe modificate, 21 allenatori, due tabelle spostate).

### Come si aggiunge una versione (0.59 e successive)

1. Crea `versioni/v059_<argomento>.py` con una funzione `apply(W)` che usa `engine` (vedi `v056_cesena_rivale.py`). Restituisce un dizionario con il rapporto.
2. Aggiungi `('059', 'v059_<argomento>')` a `VERSIONI` in `build.py`.
3. Lancia `python3 build.py --da 055`. Lo SHA nuovo viene stampato come "nuovo".
4. Collauda (vedi `COLLAUDO.md`): almeno `python3 collaudo/regressione.py out/<nuova>.gba --rif out/<precedente>.gba` più le prove delle novità. Solo dopo il collaudo copia lo SHA in `SHA` dentro `build.py`.
4b. Nella relazione copia il budget da `out/rapporto_build.json` (voce `budget`).
5. I moduli si applicano in ordine sullo stesso `Writer`: non modificare un modulo di una versione già consegnata, altrimenti cambia lo SHA di tutte quelle successive.

### Regole dell'engine

- `engine.init(rom055)` crea il `Writer` e controlla che la base sia la 0.55.
- Si scrive solo nelle zone dell'engine, con 256 byte di margine:
  - le tre zone libere della 0.55: 0x155a9b8–0x1580000, 0x15ccd78–0x1600000, 0x19c5a6d–0x1a00000;
  - dalla 0.57, undici zone recuperate da blocchi di zeri (671 KB), elencate in `versioni/v057_spazio.py` e aggiunte con `W.aggiungi_zone`.

  `W.libere()` dice quanto resta; lo spazio 0xFF della ROM è in `registri/spazio.json`. Zone nuove solo dopo un'analisi come `analisi/spazio.py` e con lo stesso controllo.
- Patch BPS: `bpslib.apply` e `bpslib.create`.
- Flag nuove solo con `engine.pool()`. Dalla 0.58 il pool dà prima le 41 flag 0x20–0x4FF verificate sicure (`analisi/flag_sicure.py`: script, oggetti nascosti, codice e dati di Smeraldo, chiamate nel codice della ROM), poi 6 flag di allenatori che non combattono da nessuna parte e che il codice di Smeraldo non cita. Fino alla 0.57 dava 0x500 + id di allenatori non usati (vedi §4 per le conseguenze).
- Variabili nuove solo con `engine.variabili().var('motivo')` (47 sicure dalla 0.58). **Missioni a più passi: una variabile come contatore**, non una flag per passo.
- Allenatori nuovi: solo numeri "libero" di `registri/allenatori.json`. La build fallisce se un allenatore che combatte ha la flag presa dal pool o usata da script di un'altra mappa.
- Mappe nuove, doni e leggendari: la build fallisce se non si raggiungono (grafo di `analisi/raggiungibili.py`). Le eccezioni stanno in `registri/irraggiungibili_ammesse.json`, con il motivo; una mappa nuova va comunque collegata.
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
| Articuno / Zapdos / Moltres | 52 | Santuari del Crinale 35.31 / 35.32 / 35.33 (Via Vittoria, FORZA per il masso) | **dalla 0.60: prima della Lega**, con 8 medaglie e le rune del santuario (flag 0x4CD/0x4CE/0x4CF) | sì, provato in gioco |
| Regirock / Regice / Registeel | 40 / 42 / 45 | Galleria dei Sigilli 35.76 / 35.77 / 35.78 | con la 6ª medaglia (0x86c) | sì |
| Kyogre | 70 | fondale di Rimini 35.37 (cartello dell'Area Marina 34.44, SURF e SUB) | **dalla 0.60: prima della Lega**, con l'8ª medaglia (quella che dà SUB) e i piloni ovest → est (flag 0x4E1) | sì, provato in gioco |
| Entei | 45 | Grotta Ardente 35.100 (dal Safari, 26.12) | **dalla 0.59: dalla prima visita a Ravenna** (flag 0x88F) | sì, provato in gioco |
| Raikou | 45 | prato del Safari 26.12 | **dalla 0.59: dalla prima visita a Ravenna** (flag 0x884) | sì, provato in gioco |
| Suicune | 45 | lago del Safari 26.13 (con SURF) | **dalla 0.59: dalla prima visita a Ravenna** (flag 0x887) | sì, provato in gioco |
| Deoxys | 50 | 35.41 (zona RAVENNA) | dopo la Lega | sì |
| Jirachi | 50 | 35.42 (zona CERVIA) | dopo la Lega | sì |
| Mewtwo | 70 | 35.43 (zona CESENATICO) | dopo la Lega | sì |
| (Suicune) | 40 | Safari della 0.51, 34.115 | stessa flag 0x887 | no, scollegato |
| (Raikou) | 40 | Safari della 0.51, 35.45 | stessa flag 0x884 | no, scollegato |
| (Entei) | 40 | Safari della 0.51, 35.44 | stessa flag 0x88F | no, scollegato |

**Cani leggendari (0.59):** si catturano nel Safari del gruppo 26, a cui porta Ravenna (uscita 10 → 26.3, ingresso libero, Poké Ball normali), già alla 5ª medaglia: servono TAGLIO, SPACCAROCCIA e SURF (per Suicune). Una cattura sola; dopo fuga, BOATO o KO il Pokémon resta al suo posto e si ritenta subito. Il Safari della 0.51 (34.115, 35.44, 35.45) resta scollegato fino al Lotto 10: i suoi cani hanno le stesse flag, quindi non ci sono doppioni.

**Shiny:** Torkoal 34.33 (Parco della Rocca di Cesena), Skarmory 34.38 (Cesenatico), Farfetch'd 34.47 (Arco di Rimini), Shuckle 35.61 (Forlimpopoli), giostre di Mirabilandia con Ponyta, Aipom, Marill (35.46–35.48), Smeargle Lv15 dal pittore di Cesena (0.56).

**Doni:** starter a Lido 1.4, Eevee 34.0, starter di Kanto 34.8, Hitmonchan/Hitmonlee 34.25, starter di Johto 34.48, Miltank 35.63 (Capocolle), Chansey 35.66 (Forlimpopoli).

## 4. Strumenti e flag della 0.56

- **PENNELLO:** strumento 0x15b (prima vuoto). Il numero 0x15c è ancora libero; tutti i numeri liberi sono in `registri/strumenti.json`.
- **Flag nuove della 0.56:** pennelli 0x7b3, 0x7b2, 0x7b1; Smeargle consegnato 0x7b0; codici 0x7ad, 0x7ac, 0x7ab, 0x7aa; rosone 0x794, 0x793, 0x792, 0x78a.
- **Missioni del Team Emilia:** tecnici delle Befane 0x27d, 0x27e, 0x27f; Ravenna conclusa 0x2ac.

- **Conflitto latente (0.58):** 0x78A (rosone "pietralunare") è anche la flag di Danielle, allenatrice della palestra di Lavaridge di Smeraldo (4.1). Oggi la 4.1 non si raggiunge; se una versione la collega la build fallisce e Danielle va spostata su un numero libero. Le flag 0x792–0x794, 0x7AA–0x7AD e 0x7B0–0x7B3 sono di allenatori della tabella delle rivincite (servono il Pokénav, assente): rischio basso.

## 4b. Risorse rimaste (budget della 0.60)

- **Spazio nella ROM:** la ROM è a 32 MB, il massimo del GBA, e non si allarga.
  - Restano 1246 KB nelle zone dell'engine (la 0.59 ha usato 1119 byte, la 0.60 2580).
  - Analisi e cose non recuperate: `relazioni/RELAZIONE_0_57.md` §3.
  - Il gruppo 0 **non** è un insieme di vecchie mappe libere: gran parte è usata dalla Romagna (0.9 Lido, 0.10 Cervia, 0.27 Mirabilandia, 0.28 Safari di Ravenna); i nomi delle zone sono riscritti, per questo 0.12 (Lavaridge) si chiama IMOLA.
  - Posti per mappe nuove: 34.10, 34.13, 34.18, 24.39–24.41, 24.50–24.51, 24.74–24.76.
- **Flag:** 47 nel pool (41 sicure 0x20–0x4FF + 6 di allenatore). Il motivo di ogni flag esclusa è in `registri/risorse_libere.json`.
- **Variabili:** 47 sicure (delle 90 "libere" di prima, 40 le usa il codice di Smeraldo: Repellente, giorni, lotteria…).
- **Strumenti:** 67 numeri liberi (`registri/strumenti.json`).
- **Allenatori:** 18 numeri liberi; 159 citati solo dal codice di Smeraldo (rivincite), da usare solo dopo un controllo.

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
9. **Mappe raggiungibili.** Una mappa che esiste non è per forza raggiungibile: il Safari della 0.51 ne è l'esempio. Dalla 0.58 lo controlla la build; `analisi/cammino.py` dice anche se ci si arriva a piedi (il grafo da solo collega mappe separate da un muro di alberi). Dalla 0.59 `analisi/percorso.py` calcola il percorso realistico con le abilità del giocatore (quote, SURF, CASCATA, sporgenze, bici, rocce, alberi): serve per dire quali strumenti chiede un tratto.
10. **"Libero" negli script non vuol dire libero.** Flag e variabili che nessuno script usa possono essere usate dal codice di Smeraldo (oggetti nascosti 0x1F4+, Pokénav 0x15C+, Repellente 0x4021, giorni 0x4040). Si prendono solo dai pool.
11. **Scansioni di script.** Seguire anche gli script dopo una lotta (trainerbattle) e le lotte con id locale diverso da 0: la scansione della 0.56 non le vedeva.
