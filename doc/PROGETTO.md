# Pokémon Romagna — documento di progetto

Stato alla **0.69** (SHA-256 `e0a23d7f…3424`, collaudata). Lotto 2 chiuso (0.59–0.61). Lotto 3 in corso: 0.62 MN e strumenti chiave (tutti si ottengono; testi di FLASH e SUB corretti); 0.63 Cesena ovest (Ippodromo sul percorso dalla prima visita, rocce di SPACCAROCCIA a Monte Spaccato al posto del controllo del casello); 0.64 la Campagna Cesenate al posto di Monte Spaccato (35.101 ridisegnata dalla bozza 4 approvata); 0.65 Ridracoli ridisegnata (35.51, bozza 2 approvata) con il TEAM EMILIA e il GYARADOS rosso; 0.66 il nuovo Fumaiolo (Sentiero 35.10 e interno 35.12–35.18 dalle bozze approvate); 0.67 il treno regionale (stazioni a Rimini, Cesena, Forlì, Faenza, Imola; sala del binario e carrozza con la scena del viaggio); 0.68 ostacoli (TV della casa del protagonista spostata, siepe aperta verso la Poké Ball della Pineta del Savio); 0.69 barriere e testi (inventario delle barriere, 21 testi riscritti fra cui le direzioni del Fumaiolo e le guide dei collegamenti, 132 accenti). **Lotto 3 chiuso** sulla 0.69 senza cambiare la ROM (`relazioni/CHIUSURA_LOTTO_3.md`): consegna di SMEARGLE con squadra e PC pieni verificata a tasti (il pittore lo tiene, poi lo manda al PC quando si libera un posto); le quattro guide di Ridracoli provate in andata e ritorno. Segnalato: frasi inglesi nella schermata dei box del PC. Prossimo: Lotto 4 (Lido di Savio, Pineta, Cervia).
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
| 3 | 0.55 | `versioni/v056_cesena_rivale.py`, `v057_spazio.py`, `v058_registri.py`, `v059_cani.py`, `v060_kyogre_uccelli.py`, `v061_regi_mitici.py`, `v062_strumenti.py`, `v063_cesena_ovest.py`, `v064_campagna_cesenate.py`, `v065_ridracoli.py`, `v066_fumaiolo.py`, `v067_treno.py`, `v068_ostacoli.py`, `v069_testi.py` | 0.56–0.69 | `b09eb697…495f`, `47f53668…97c4`, `47f53668…97c4`, `aee694c2…ec1d`, `d9ca40b3…183a`, `f3e78025…3cbe`, `b8ebd091…9080`, `d1fee9f9…6187`, `82ac35d2…7f70`, `ad1bfa2d…9a94`, `d794870a…4f84`, `aa572447…fe7b`, `d4a65459…d964`, `e0a23d7f…3424` |
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

### Regola delle mappe (richiesta dell'utente dopo la 0.63)

**Ogni mappa nuova o ridisegnata si mostra all'utente finita prima di metterla nel gioco**: immagine completa (`strumenti_rom/tela.py`, `anteprima`) con allenatori, cartelli, rocce, uscite e incontri al loro posto, e si aspetta il suo sì. Solo dopo si scrive il modulo e si collauda. Le correzioni chieste ripartono da una nuova immagine.

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
| 5 | Rimini (34.44, 34.47) | Le Befane (34.54–34.59) con Ing. Neri e i tre tecnici; MN SPACCAROCCIA; 3ª medaglia **AURELIO**. Starter di Johto in dono (34.48). | Ritorno a Cesena (VOLO dalla 2ª medaglia; dalla 0.67 anche il treno regionale) |
| 6 | Cesena ovest | Casello ovest (35.91, nessun controllo dalla 0.63) → Ippodromo del Savio (34.19, dal cancello sud; visitabile dalla prima visita a Cesena) → cancello ovest → Campagna Cesenate (35.101, dalla 0.64: pianura con fiume, campi, erba alta e sei allenatori; si arriva dalla porta della casa a est). A nord il Monte Spaccato: davanti alla galleria (25,10) una roccia: servono SPACCAROCCIA (ADA, Rimini 34.48) e la 3ª medaglia. Entrando nel casello 35.92 si alza la flag 0x22 e la roccia non ricompare più. | Casello 35.92 → Capocolle (35.60, Babbi) → Forlimpopoli (35.61, MOSSOMETRO) → Via Emilia Ovest |
| 7 | Forlì (34.68/34.84) | ALDO all'ingresso; 4ª medaglia **IVANO**; MN SURF. | Campagna col fiume (isolotti con 3 istruttori) |
| 8 | Faenza (34.85) | Museo della ceramica; 5ª medaglia **ADA**. | Campagna Ravennate (35.102) → Ravenna |
| 9 | Ravenna (34.94, 34.96) | Si arriva da Faenza o dal Lido (Pianura Romagnola 34.93). Arco del Team Emilia: flag **0x2ac** a missione conclusa. Mirabilandia (34.114) e Safari (gruppo 26). | Casello 35.98 (richiede 0x2ac) → Via dei Canali (35.70) → Campagne di Lugo (35.71) |
| 10 | Lugo (34.110/34.111) | Trasmettitore; 6ª medaglia **ALIDA**. | Sentiero → Galleria dei Sigilli (35.74, i tre Regi) → Faenza |
| 11 | Faenza → Imola (35.1) | Ponte Santerno (35.0) con ALDO e il tecnico, che si sposta con la 6ª medaglia; 7ª medaglia **RINO**; MN FORZA. Facoltativo, dalla 7ª medaglia: **Ridracoli** (guida di Forlì 34.68 o Sentiero del Fumaiolo 35.10 → 35.50 → 35.51, dalla 0.65): TEAM EMILIA alla diga (due reclute, poi CORRADO), il GYARADOS rosso nel lago, la CENTRALE (35.52) con la missione delle tre guardie; sopra la cascata la sorgente del Bidente (CASCATA). | Ritorno a Cesena (VOLO o treno regionale, dalla 0.67) |
| 12 | Cesena sud | Sentiero del Fumaiolo (35.10, ridisegnato nella 0.66: si risale il Savio dal basso; RIFUGIO, EREMO DI SANT'ALBERICO con il masso di FORZA, sorgente del TEVERE): ALDO all'ingresso; Grotta dell'Eremo (35.12) → Grotta delle Sorgenti (35.13, SURF) → Nodi del Sale e dell'Argilla (35.14–35.15) → Sala di BASSI (35.16) → Groudon nel Cuore del Fumaiolo (35.17) → Passo dei Draghi (35.18, frane fino a Groudon) → Bagno di Romagna (35.19), 8ª medaglia **LEDA**. | Via Vittoria |
| 13 | Finale | Via Vittoria (35.27) con ALDO → Lega Romagna (35.34). | Post-Lega |
| — | Post-Lega | San Marino (35.53–35.58). Decisioni prese: **San Marino e Bologna restano dopo la Lega**; a Bologna c'è la sede del Team Emilia, con una post-trama. | — |

- **Medaglie:** flag da 0x867 (Cervia) a 0x86e (Bagno di Romagna). 0x864 è "Lega vinta".
- **Caselli tra le aree:** mappe 35.79–35.99.
- **Elenco completo delle mappe**, con nome, dimensioni, uscite e blocchi a coordinate: `registri/mappe.json`.

## 3. Leggendari, shiny e doni

Tabella completa alla 0.61. **Regola del Lotto 2** (cani, Kyogre, uccelli, Regi, Deoxys, Jirachi, Mewtwo): **una sola cattura**; dopo fuga (anche per BOATO) o KO il Pokémon resta al suo posto e si ritenta subito; chi l'ha catturato trova la sala tranquilla. "Provato" = a tasti in mGBA e VBA-M (fixture dichiarate nelle relazioni); "letto" = solo dagli script.

| Pokémon | Lv | Dove | Come ci si arriva | Quando | Flag di cattura | Regola, esiti | Stato |
|---|---|---|---|---|---|---|---|
| Entei | 45 | Grotta Ardente 35.100 | Ravenna → Safari 26.3 → 26.12 → grotta | dalla prima visita a Ravenna (0.59) | 0x88F | sì: cattura, fuga, KO | provato (0.59) |
| Raikou | 45 | prato del Safari 26.12 | come sopra (TAGLIO, SPACCAROCCIA) | come sopra | 0x884 | sì | provato (0.59) |
| Suicune | 45 | lago del Safari 26.13 | come sopra, poi SURF | come sopra | 0x887 | sì | provato (0.59) |
| Regirock | 40 | Camera di Pietra 35.76 | Faenza → Sentiero 35.73 → Galleria dei Sigilli 35.74 → scala 35.75. **Nessuna abilità, niente FORZA** | 6ª medaglia (0x86C): prima la sbarra sul Sentiero non fa passare | 0x620 | sì (0.61): cattura, fuga, KO | provato (0.61) |
| Regice | 42 | Camera di Brina 35.77 | come sopra | come sopra | 0x622 | sì (0.61) | provato (0.61), KO solo letto |
| Registeel | 45 | Camera di Metallo 35.78 | come sopra | come sopra | 0x627 | sì (0.61) | provato (0.61), KO solo letto |
| Articuno | 52 | Santuario 35.31 | Via Vittoria (guardia con 8 medaglie, masso con FORZA) | 8ª medaglia + rune vento → gelo (0.60) | 0x4CD | sì | provato (0.60), KO solo letto |
| Zapdos | 52 | Santuario 35.32 | come sopra | 8ª medaglia + rune bobina → cielo | 0x4CE | sì | provato (0.60), KO solo letto |
| Moltres | 52 | Santuario 35.33 | come sopra | 8ª medaglia + rune brace → fiamma → sole | 0x4CF | sì | provato (0.60), KO solo letto |
| Kyogre | 70 | fondale di Rimini 35.37 | cartello dell'Area Marina 34.44 → mare 35.36, SURF e SUB | 8ª medaglia (quella che dà SUB) + piloni ovest → est (0.60) | 0x4E1 (+0x4E0) | sì | provato (0.60), KO solo letto |
| Deoxys | 50 | 35.41 (la Luna) | Ravenna 34.96: SURF verso est fino al molo 35.40, poi il **razzo ROMAGNA-1**; rientro col razzo | dopo la Lega (0x864) | 0x4EB | sì (0.61) | provato (0.61), KO solo letto |
| Jirachi | 50 | 35.42 (Mondo dei Desideri) | **portale** nel mare di Cervia (0.10, casella 61,22, con SURF): compare dopo la Lega; ritorno dal portale | dopo la Lega | 0x4EA | sì (0.61) | provato (0.61), KO solo letto |
| Mewtwo | 70 | grotta 35.43 | Cesenatico 34.22, casella 48,33 (dalla 0.61 si entra davvero) | dopo la Lega; prima lo dice il testo | 0x4EF | sì (0.61) | provato (0.61), KO solo letto |
| Rayquaza | 70 | monumento a Baracca, Lugo 34.110 | Lugo | compare con l'8ª medaglia | 0x4E3 | fuga e KO: "Puoi riprovare" (stesso testo); righe lunghe | letto |
| Groudon | 50 | Cuore del Fumaiolo 35.17 (17,25, dalla 0.66) | evento della storia (Team Emilia, dopo BASSI) | storia | 0x4CC | KO: resta e si ricattura; fuga: "potrai tornare", ma senza la flag 0x8C1 l'oggetto sparisce fino al rientro; testi di 3–4 righe | cattura con MASTER BALL provata (0.66); KO e fuga letti |
| Gyarados cromatico | 40 | lago di Ridracoli 35.51 (22,27) | guida di Forlì o Sentiero del Fumaiolo (7ª medaglia) → 35.50 → 35.51; SURF | compare quando si batte CORRADO del TEAM EMILIA (prima le due reclute) | 0x2C (oggetto: 0x28) | sì (0.65): cattura, fuga, KO; sempre cromatico (nativo 0x09730055 con 0x8004/0x8005) | provato (0.65) |
| Celebi | 50 | santuario di legno nella Pineta del Savio 0.16 (cartello a 32,5) | si posa la **GS BALL** nell'incavo (la dà il PROF. PINO, il Birch della Romagna, nel laboratorio di Lido di Savio 1.4, appena si è Campione) | dopo la Lega (0x864) e con la GS BALL | 0x4E4 | sì: se non lo catturi svanisce, la GS BALL resta e si riprova | letto; provato dall'utente nella 0.56 |
| Lugia / Ho-Oh | 70 | Monte Spaccato 26.87 / 26.75 (Isola Ombelico di Smeraldo) | MOTONAVE dal porto di Ravenna (34.96) dopo la Lega → 26.67 | dopo la Lega | 0x320 / 0x321 (di Smeraldo) | script di Smeraldo | letto, raggiungibilità da provare |
| (Regirock, Regice, Registeel di Smeraldo) | 40 | Desert Ruins 24.6, Island Cave 24.67, Ancient Tomb 24.68 | uscite in 0.26, 0.20, 0.35 | — | 0x3A7–0x3A9 | — | **non raggiungibili a piedi** dalla partenza (`analisi/percorso.py`); il registro della build, più ottimista, le conta: da chiarire nel Lotto 3 |
| (Suicune, Raikou, Entei della 0.51) | 40 | Safari della 0.51: 34.115, 35.45, 35.44 | — | — | stesse flag dei cani | — | scollegati fino al Lotto 10 |

**Regi (0.61):** la Galleria dei Sigilli si percorre a piedi senza abilità (provato a tasti, anche al ritorno sul Sentiero). Le tre camere sono indipendenti: ognuna ha la sua flag, catturarne uno non cambia gli altri. La lotta usa ancora lo special dei Regi (0x13B, con la loro musica).

**Deoxys, Jirachi, Mewtwo (0.61):** restano dopo la Lega, come da progetto. Prima della Lega: il razzo dice che il volo è riservato al CAMPIONE, il portale di Cervia non c'è, Mewtwo spiega che serve il titolo di CAMPIONE. Il bordo est di Ravenna (34.96, x 79) e il bordo ovest del molo (35.40, x 0) sono passaggi a coordinate, provati nei due versi.

**Cani leggendari (0.59):** si catturano nel Safari del gruppo 26, a cui porta Ravenna (uscita 10 → 26.3, ingresso libero, Poké Ball normali), già alla 5ª medaglia: servono TAGLIO, SPACCAROCCIA e SURF (per Suicune). Una cattura sola; dopo fuga, BOATO o KO il Pokémon resta al suo posto e si ritenta subito. Il Safari della 0.51 (34.115, 35.44, 35.45) resta scollegato fino al Lotto 10: i suoi cani hanno le stesse flag, quindi non ci sono doppioni.

**Shiny:** Gyarados 35.51 (Ridracoli, 0.65), Torkoal 34.33 (Parco della Rocca di Cesena), Skarmory 34.38 (Cesenatico), Farfetch'd 34.47 (Arco di Rimini), Shuckle 35.61 (Forlimpopoli), giostre di Mirabilandia con Ponyta, Aipom, Marill (35.46–35.48), Smeargle Lv15 dal pittore di Cesena (0.56).

**Doni:** starter a Lido 1.4, Eevee 34.0, starter di Kanto 34.8, Hitmonchan/Hitmonlee 34.25, starter di Johto 34.48, Miltank 35.63 (Capocolle), Chansey 35.66 (Forlimpopoli).

## 4. Strumenti e flag della 0.56

- **PENNELLO:** strumento 0x15b (prima vuoto). Il numero 0x15c è ancora libero; tutti i numeri liberi sono in `registri/strumenti.json`.
- **Flag nuove della 0.56:** pennelli 0x7b3, 0x7b2, 0x7b1; Smeargle consegnato 0x7b0; codici 0x7ad, 0x7ac, 0x7ab, 0x7aa; rosone 0x794, 0x793, 0x792, 0x78a.
- **Missioni del Team Emilia:** tecnici delle Befane 0x27d, 0x27e, 0x27f; Ravenna conclusa 0x2ac.

- **Conflitto latente (0.58):** 0x78A (rosone "pietralunare") è anche la flag di Danielle, allenatrice della palestra di Lavaridge di Smeraldo (4.1). Oggi la 4.1 non si raggiunge; se una versione la collega la build fallisce e Danielle va spostata su un numero libero. Le flag 0x792–0x794, 0x7AA–0x7AD e 0x7B0–0x7B3 sono di allenatori della tabella delle rivincite (servono il Pokénav, assente): rischio basso.

## 4b. Risorse rimaste (budget della 0.69)

- **Spazio nella ROM:** la ROM è a 32 MB, il massimo del GBA, e non si allarga.
  - Restano 791 KB nelle zone dell'engine (la 0.69 ne usa circa 2 per i testi riscritti) (la 0.59 ha usato 1119 byte, la 0.60 2580, la 0.61 circa 4,7 KB, la 0.62 e la 0.63 meno di 1 KB ciascuna, la 0.64 27 KB: un tileset nuovo; la 0.65 35 KB: tileset, blocchi della mappa 44×62, sprite e tavolozza del GYARADOS; la 0.66 234 KB: 8 tileset secondari e i blocchi delle 8 mappe del Fumaiolo; la 0.67 150 KB: grafica del primario con il cartello STAZIONE, per ogni città copia della tabella dei metatile e del layout, la carrozza).
  - Analisi e cose non recuperate: `relazioni/RELAZIONE_0_57.md` §3.
  - Il gruppo 0 **non** è un insieme di vecchie mappe libere: gran parte è usata dalla Romagna (0.9 Lido, 0.10 Cervia, 0.27 Mirabilandia, 0.28 Safari di Ravenna); i nomi delle zone sono riscritti, per questo 0.12 (Lavaridge) si chiama IMOLA.
  - Posti per mappe nuove: 34.10, 34.13, 34.18 (layout condiviso con altre mappe: serve un numero di layout nuovo), 24.75, 24.76. La 0.67 ha usato 24.39–24.41, 24.50, 24.51 (stazioni) e 24.74 (carrozza).
  - Tile liberi nel primario: circa 27 vuoti che nessuna mappa, nessun metatile del primario e nessun setmetatile usa (la 0.67 ne ha presi 8 per il cartello: 183, 197, 219, 235, 237, 258, 290, 306).
- **Flag:** 35 nel pool, tutte sicure 0x20–0x4FF (la 0.67 ha preso 0x3C; la 0.66 ha preso 0x35; la 0.63 ha preso 0x22, la 0.64 ha tolto dal pool le flag dei tre allenatori nuovi 462, 485, 486; la 0.65 ha preso 0x28, 0x2C, 0x34 e ha tolto dal pool le 3 flag di allenatore che vi restavano, ora dei suoi allenatori). Il motivo di ogni flag esclusa è in `registri/risorse_libere.json`.
- **Variabili:** 43 sicure (la 0.64, la 0.65, la 0.66 e la 0.67 ne hanno presa una ciascuna) (delle 90 "libere" di prima, 40 le usa il codice di Smeraldo: Repellente, giorni, lotteria…).
- **Strumenti:** 67 numeri liberi (`registri/strumenti.json`).
- **Allenatori:** 10 numeri liberi (la 0.64 ha usato 462, 485, 486; la 0.65 581, 633, 634, 734, 851); 159 citati solo dal codice di Smeraldo (rivincite), da usare solo dopo un controllo.

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
12. **Un'uscita deve stare su una casella d'uscita.** Smeraldo fa scattare un'uscita solo su porte, scale, frecce e simili: su una casella normale (sabbia, erba) non succede nulla. Era il caso della grotta di Mewtwo (34.22, corretto nella 0.61). Le altre uscite sospette fuori dalle mappe di Smeraldo (34.17 uscita 13, 35.13 → 35.18, 35.16 → 35.17) erano arrivi di script: 34.17 uscita 13 è il ritorno dal Sentiero; nella 0.66 35.13 → 35.18 è un ingresso di grotta vero, 35.16 → 35.17 resta solo l'arrivo dello script del guardiano (porta senza comportamento).
13. **Gli alberi di bacche bloccano.** Tipo di movimento 12: `analisi/percorso.py` li conta come ostacoli dalla 0.61.
14. **Numeri degli strumenti: controllarli in `registri/strumenti.json`.** Nella 0.62 avevo usato a memoria numeri sbagliati per gli ami (0x10F è CHIAVE SOTT., non SUPER AMO): gli ami sono 0x106 VECCHIO, 0x107 BUONO, 0x108 SUPER. Chi consegna cosa: `analisi/doni.py`; testi oltre le 2 righe: `analisi/righe.py`.
15. **Strumenti chiave e MN (0.62):** CASCATA Safari Ravenna 26.3 (8ª medaglia), SUB Bagno di Romagna 35.26 (8ª), FLASH Grotta Granito 24.7 (dall'Appennino 0.21), BICI CROSS Cesenatico 34.42, AMO VECCHIO Cesenatico 34.22, AMO BUONO Rimini 34.44, SUPER AMO Ravenna 34.96 (5ª).
16. **Oggetti nascosti da uno script di mappa (0.63).** Le rocce di Monte Spaccato hanno flag temporanee (0x11–0x13, azzerate a ogni cambio di mappa, come in Smeraldo); lo script d'ingresso (tipo 3) le alza se 0x22 è a 1. `analisi/percorso.py` non legge gli script di mappa: per pianificare si danno le flag come alzate (`--flag`, o `vai.FLAG_ALZATE` nel collaudo); quello che conta resta la prova a tasti.
17. **Mappa ridisegnata al suo posto (0.64).** Se il layout è usato da una sola mappa e le dimensioni restano, i blocchi si riscrivono al loro posto e il tileset secondario nuovo (tela.Unione) si aggancia al layout. Il disegno della bozza approvata si copia nel modulo (congelato). I vecchi salvataggi fatti dentro la mappa possono stare su caselle che ora sono muri: si controlla con `collaudo/vecchie_pos_064.py`, e una variabile alzata dallo script d'ingresso (tipo 3) più uno script di frame (tipo 2) riporta una volta sola il giocatore a un punto sicuro. Lo script d'ingresso gira solo entrando da un'uscita, non con Continua.
18. **Selvatico cromatico (0.65).** Il comando nativo 0x09730055 rifà il Pokémon nemico da 0x8004 (specie) e 0x8005 (livello): vanno impostati dopo `setwildbattle`. Senza, nel primo collaudo è uscito un BRELOOM di livello 0.
19. **Collaudo con allenatori che vedono e cascate (0.65).** Un allenatore che si avvicina resta nella casella nuova fino al cambio di mappa, ma il pianificatore lo crede al suo posto: si passa a lato. `vai.py` non usa CASCATA: in t65 la salita si fa a tasti (A verso la cascata in SURF, sì).
20. **Quota 0 e quota degli oggetti (0.66).** Sulle caselle a quota 0 (scale, passaggi) Smeraldo dà al giocatore quota 0, e da lì si va a qualunque quota; `analisi/percorso.py` teneva la quota di prima e non passava le scale del Percorso 119 (corretto). Un oggetto prende la quota della sua casella: GROUDON sulla lava (quota 1) non si trovava con A dalla riva (quota 3); la sua casella ora è a quota 0. Un cartello (evento di sfondo) su una casella d'acqua non si legge: A lancia SURF.
21. **Mappe rifatte con pezzi di Smeraldo (0.66).** Le stanze di Smeraldo non sono chiuse in sé: zone a quote diverse si raggiungono da scale di altre stanze. Ogni bozza va controllata con il percorso (dall'ingresso a tutte le uscite e a tutti i personaggi), con scale e ingressi che non servono chiusi; le gobbe del Passo Selvaggio vogliono la Bici Cross (qui tolte). Per le lotte che la squadra di prova non può vincere (ALDO, BASSI) il collaudo registra la partenza e, solo dopo la sconfitta, alza le flag della vittoria come fixture dichiarata, da uno stato di riserva.
22. **Treno regionale e tileset pieni (0.67).** I secondari delle città hanno 510–511 tile su 512: grafica nuova non ci sta. Il cartello STAZIONE sta in 8 tile vuoti del primario (mai usati da mappe, metatile del primario o setmetatile), nello strato alto di metatile nuovi messi in una copia della tabella dei metatile della città (posti 1019–1023). Smeraldo carica il layout dal suo numero (tabella a 0x627fc0), non dal puntatore dell'intestazione; le mappe 33.18, 33.48, 33.69, 33.86 sono la stessa intestazione di Cesena, Rimini, Forlì, Faenza. VOLO si usa dalla 2ª medaglia: la tabella delle medaglie delle MN è a 0x1600000 (8 flag, una per MN). Il treno offre le città con la flag di visita del Volo (0x872, 0x873, 0x876–0x878). Movimenti: 0x0a passo a sinistra, 0x0b a destra, 0xfe fine.
