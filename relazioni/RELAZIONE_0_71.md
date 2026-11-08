# Pokémon Romagna 0.71: l'esterno del laboratorio (Lotto 4)

**Base:** 0.70, SHA-256 `0eccfb3f9c188b984f7b111d549b8afceb36a8fc64ffc744d35f4179af22dfa3`.

**Risultato:** `Pokemon_Romagna_0_71.gba`, SHA-256 `17c5a9e607717a67975abefe65ed561113073725cd5d54564589bbe28dbf642a`.
- **Patch BPS 0.70→0.71:** `rom/Pokemon_Romagna_0_70_to_0_71.bps` (27.376 byte), verificata riapplicandola. Il log è in `collaudo/risultati/071/consegna.txt`.
- **Zip:** lo zip senza `out/`, ricostruito in una cartella pulita, rifà lo stesso SHA.
- **Modulo:** `versioni/v071_laboratorio.py`. La bozza approvata è `bozze/laboratorio.py`; le immagini sono in `bozze/immagini/laboratorio_*.png`.
- **SHA:** è in `build.py` dopo il collaudo (§5).
- **Salvataggi compatibili:** Lido di Savio ha le misure di prima (56×44) e lo stesso numero di layout; la porta del laboratorio resta in (13,27). Ho provato due salvataggi veri della 0.70, uno dentro il laboratorio e uno davanti (§5). Nessuna flag e nessuna variabile nuova.

## 1. Cosa è stato chiesto

- **Prompt 0.57, Lotto 4:** "Laboratorio: rifai l'esterno, oggi è visivamente orribile."
- **Bozza** (Museo Oceanografico di Smeraldo ricolorato, cartello riscritto a 30 caratteri): "Va bene così puoi procedere".

## 2. Com'era nella 0.70

- In (9–17, 22–28) c'era una vetrina piatta 7×5: insegna "RICERCA.COSTIERA", tenda a righe ruggine e bianche, quattro vetrine e una porta grigia in (13,27). Non aveva tetto né prospettiva.
- Il cartello in (11,28) diceva "STAZIONE DI RICERCA ADRIATICA PROF. / PINO - Ambiente e POKéMON.": la prima riga ha 35 caratteri.

## 3. Modifiche (`versioni/v071_laboratorio.py`)

1. **Edificio.**
   - La vetrina diventa erba.
   - Al suo posto, in (11–16, 23–28), c'è il Museo Oceanografico di Porto Alghepoli di Smeraldo (layout 2, x 28–33, y 22–27): tetto a vetrate con le cupole, colonne, porta larga due caselle e scalinata.
   - Nella prima riga lo strato basso del museo era il muretto bianco del molo: è sostituito con l'erba di Lido.
2. **Colori.**
   - Il secondario di Lido (0x1fe349c) è usato solo da Lido. Aveva le 7 palette e 511 tile su 512 occupati.
   - Il secondario è rifatto con l'Unione, con le palette 6–12 agli stessi posti; i tile della vetrina si liberano.
   - I pezzi del museo (palette 6 e 8 di Porto Alghepoli) sono ricolorati tile per tile con la palette più vicina fra quelle di Lido e del primario. Il tetto, verde acqua in Smeraldo, viene grigio-azzurro chiaro.
   - Risultato: 349 metatile, 495 tile, 7 palette.
3. **Layout.** Il layout nuovo prende il posto del vecchio nella tabella dei layout (id 631, solo di Lido; il modulo lo controlla). Il bordo resta quello di prima.
4. **Eventi.**

   | Cosa | Prima | Dopo |
   |---|---|---|
   | porta del laboratorio (uscita 2, verso 1.4) | (13,27) | (13,27), invariata |
   | seconda porta (uscita 15, verso 1.4 uscita 0) | — | (14,27) |
   | cartello del laboratorio | (11,28) | (10,28) |
   | testo del cartello | "STAZIONE DI RICERCA ADRIATICA PROF. / PINO - Ambiente e POKéMON." | "STAZIONE DI RICERCA ADRIATICA / Prof. PINO: POKéMON e ambiente" (29 e 30 caratteri) |

   - Le due caselle della porta hanno il comportamento "porta" (0x60) del museo; la riga della scalinata (y 28) è calpestabile. Il modulo controlla tutte e due le cose.
   - Il cartello ha uno script nuovo (stesso comando "cartello" di prima); il vecchio testo resta nella ROM, non più usato.

## 4. Budget (da `out/rapporto_build.json`)

- **Spazio:** restano 708 KB, quindi la 0.71 ne usa 31: il secondario di Lido intero (16 KB di tile, 8 KB di metatile, 1 KB di attributi) e i blocchi della mappa 56×44.
- **Invariati:** 35 flag, 43 variabili, 67 strumenti, 10 allenatori liberi.

## 5. Collaudo (solo tasti; fixture dichiarate)

**Script e risultati**
- Script: `collaudo/t71lab.py`; risultati in `collaudo/risultati/071/`.
- La ROM finale `17c5a9e6…642a` è stata provata in mGBA e in VBA-M. VBA-M riparte dai salvataggi veri fatti in mGBA.

**Fixture dichiarate**
- Solo la posizione di partenza, scritta prima di un SALVA vero:
  - Lido di Savio (13,30), sul viale sotto il laboratorio;
  - per i vecchi salvataggi, sulla ROM 0.70: laboratorio 1.4 (6,10) e Lido (13,28).
- Le partenze sono da `prog_imola.ss`.

**lab**

| Prova | mGBA | VBA-M |
|---|---|---|
| Da (13,28) su: dentro il laboratorio 1.4, in (6,12) | ok | ok |
| Fuori dall'uscita (6,12): Lido, il personaggio esce dalla porta e si ferma in (13,28) | ok | ok |
| Da (14,28) su: dentro il laboratorio, in (6,12); di nuovo fuori in (13,28) | ok | ok |
| Cartello, da (10,29): "STAZIONE DI RICERCA ADRIATICA / Prof. PINO: POKéMON e ambiente" | ok | ok |
| Dentro, SALVA e Continua: si resta nel laboratorio (6,10); fuori in (13,28) | ok | ok |

- Dopo che il pilota ha camminato, i primi tasti Su a volte non spostano il personaggio: da (14,28) è entrato al terzo. Ho ripetuto la prova arrivando da sotto, sull'erba aperta (14,30): anche lì i primi due tasti non lo hanno mosso. È il ritmo del pilota, non la porta.

**Vecchi salvataggi della 0.70**

| Prova | mGBA | VBA-M |
|---|---|---|
| Salvataggio vero della 0.70 nel laboratorio (6,10), caricato nella 0.71: fuori dall'uscita, si arriva a Lido in (13,28) davanti al laboratorio nuovo | ok | ok |
| Salvataggio vero della 0.70 a Lido (13,28): subito la mappa nuova (schermata `t71lab_vecchio_lido.png`); su: dentro il laboratorio | ok | ok |

**Schermate guardate.** La facciata dal viale, l'uscita sulla scalinata, il riquadro del cartello su 2 righe (mGBA). I colori in gioco sono quelli della bozza.

**Controlli statici.** Build: raggiungibilità "nuove 0, problemi 0".

### Regressione (`collaudo/regressione.py`, 0.71 contro 0.70)

Le 19 partenze (17 savestate in mGBA e il salvataggio vero in mGBA e VBA-M):
- girano e sono vive;
- la callback resta nella ROM;
- 17 sono **uguali** alla 0.70 in tutti i punti di controllo;
- 2 sono **diverse, come previsto**: `t56_rename` e `t56_rename2` partono dentro il laboratorio (1.4) e il passo "cammina" esce su Lido di Savio.
  - Le ho rifatte sulla 0.70 e sulla 0.71 e ho confrontato le schermate (`regressione_t56_rename_070_071.png`).
  - Il personaggio è nello stesso punto, davanti alla porta, in tutti e due i casi.
  - Cambiano solo l'edificio e il cartello spostato in (10,28). Lo stesso vale per i punti di controllo successivi (menu, squadra, riassunto, ritorno): la mappa fa da sfondo.

## 6. Cosa non è verificato

- Le schermate di VBA-M sono state salvate ma le ho guardate solo in mGBA.
- Il resto di Lido di Savio non è stato percorso a tasti: la mappa fuori dal laboratorio ha gli stessi metatile di prima, rimessi nel secondario nuovo (controllato solo confrontando l'immagine della ROM con la bozza).

## 7. Richieste

| Richiesta | Stato |
|---|---|
| Rifai l'esterno del laboratorio | **corretto e verificato** (mGBA e VBA-M) |
| Mappa mostrata finita e approvata prima del modulo | **fatto** ("Va bene così puoi procedere"); il modulo rifà la bozza senza differenze |
| Cartello a 30 caratteri | **corretto e verificato** |
| Vecchi salvataggi | **verificato** con due salvataggi veri della 0.70 |
| Prossimo nel Lotto 4 | casa del rivale (interno ed esterno); poi gelateria "Puro & Bio", chiese di Lido e di Cervia, fenicotteri delle Saline |
