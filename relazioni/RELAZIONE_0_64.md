# Pokémon Romagna 0.64: la Campagna Cesenate (Lotto 3)

**Base:** 0.63, SHA-256 `d1fee9f903b1fb6dbc0b9568697b469080f3d356dedc63a9bbf9326b0c876187`.

**Risultato:** `Pokemon_Romagna_0_64.gba`, SHA-256 `4eee4268983adaf4d06489aca972bd23ba6d76394aa00185cbce4bcfe152c21e`.
- Patch BPS 0.63→0.64: `rom/Pokemon_Romagna_0_63_to_0_64.bps` (6366 byte), verificata riapplicandola (`consegna.sh`, log in `collaudo/risultati/064/consegna.txt`).
- Modulo: `versioni/v064_campagna_cesenate.py`. La build da zero rifà tutti gli SHA; lo zip senza `out/` ricostruito in una cartella pulita rifà lo stesso SHA (stesso log).
- Lo SHA è in `build.py` dopo il collaudo (§5).
- **Salvataggi compatibili:** stessa mappa (35.101), stesse dimensioni, stesso layout; una variabile nuova (a 0 nei vecchi salvataggi). Un salvataggio vero della 0.63 e uno della 0.62 fatti dentro la mappa vecchia caricano nella 0.64 e proseguono, in mGBA e VBA-M (§5).

## 1. Cosa è stato chiesto

In chat, dopo la 0.63 (regola nuova: ogni mappa ridisegnata si mostra finita e si aspetta il sì):
- Monte Spaccato (35.101) non piaceva: deve diventare una **campagna pianeggiante**, perché il Monte Spaccato vero è a Capocolle. Il nome è **CAMPAGNA CESENATE**.
- L'ordine resta Cesena → Ippodromo → campagna: dalla campagna non si va direttamente a Cesena.
- Più erba alta, allenatori da affrontare, campi e un fiume.
- Bozza 3: il monte era tagliato di netto dagli alberi e in alto a destra mancava qualcosa. La **bozza 4** (il monte prosegue verso est, il fiume nasce da una cascata) è stata approvata ("Ok prosegui").

## 2. Com'era nella 0.63

- 35.101 MONTE SPACCATO, 64×40: una collina in mezzo all'erba, tre rocce nella tagliata (14,16–18), tre allenatori (ILARIO, LEONIA, PIERO, tutti con lo stesso sprite), due casette (58,20 e 54,36) che portavano all'Ippodromo, e l'uscita ovest (4,17) verso il casello 35.92.
- La mappa vecchia è in `analisi/` solo come dato (`collaudo/risultati/064/vecchie_posizioni.txt`). Il prima/dopo è quello delle bozze mandate in chat.

## 3. Modifiche (versioni/v064_campagna_cesenate.py)

1. **La mappa.** Il disegno della bozza 4 (`bozze/campagna_monte_spaccato.py`) è copiato nel modulo e congelato.
   - I pezzi vengono da layout di Smeraldo: Percorso 117 (campi, macero, casa, strada), Percorso 116 (il monte con la galleria), assi del ponte del 119, e acqua, erba ed erba alta del tileset primario.
   - Stesso layout `0x15998b4` (usato solo da 35.101), stesse dimensioni: i blocchi sono riscritti al loro posto. Il tileset secondario nuovo lo costruisce `tela.Unione`: 5 metatile, 6 tile, 2 palette nuove.
   - Il bordo fuori mappa è bosco.
2. **Uscite:**
   - la porta della casa (55,22) → Ippodromo, cancello ovest. Le uscite 0 e 2 di prima, entrambe verso l'Ippodromo, ora stanno tutte e due sulla porta;
   - la galleria del Monte Spaccato (25,10) → casello 35.92.
   - L'Ippodromo non cambia: il suo cancello ovest porta ancora all'uscita 2 di 35.101, cioè la porta della casa.
3. **La roccia:** una sola, davanti alla galleria (25,11).
   - Usa lo script di Smeraldo (SPACCAROCCIA + 3ª medaglia) e la flag temporanea 0x11.
   - Lo script d'ingresso della 0.63 la nasconde quando il passaggio è già aperto (0x22).
4. **Allenatori (sei):**
   - **Gli stessi tre di prima** (ILARIO 0xC6, LEONIA 0xC7, PIERO 0xC8): stesse flag e stessi script, quindi chi li ha battuti li ritrova battuti. Sono spostati e vestiti come nella bozza: LEONIA da donna, con classe e ritratto di IRIS; PIERO da ragazzo di campagna, come ETHAN.
   - **Tre nuovi**, sui numeri liberi 462, 485 e 486. Le loro flag (0x6CE, 0x6E5, 0x6E6) sono tolte dal pool dell'engine.

| Allenatore | Posizione | Squadra |
|---|---|---|
| NICO, ragazzino | sulla strada (27,16) | PIDGEOTTO 26, RATICATE 25 |
| TONINO, pescatore | sulla riva del fiume (43,13) | POLIWHIRL 26, GOLDEEN 26 |
| OSVALDO, uomo col cappello | nell'erba alta a est (55,30) | TAUROS 27, MILTANK 27 |

5. **Cartelli (tre, testi nuovi):**
   - (8,9) "MONTE SPACCATO / La galleria porta a CAPOCOLLE / poi a FORLIMPOPOLI."
   - (53,22) "CAMPAGNA CESENATE / Dalla casa si torna / all'IPPODROMO e a CESENA."
   - (42,22) "VIA EMILIA / A ovest MONTE SPACCATO, / a est l'IPPODROMO."
6. **Nome del luogo:** la sezione della mappa (0xD3) si chiama ora CAMPAGNA CESENATE. È usata solo da 35.101.
7. **Testi che parlavano di Monte Spaccato:**
   - il casellante di 35.91 ora dice "…e poi la CAMPAGNA CESENATE, verso CAPOCOLLE e FORLIMPOPOLI";
   - ADA (Rimini 34.48) ora dice "Oltre l'IPPODROMO di CESENA, una roccia chiude la galleria del MONTE SPACCATO. VOLO ti aiuterà a tornare."
8. **Vecchi salvataggi fatti dentro 35.101.** Nella mappa vecchia si poteva stare su 1164 caselle. Di queste, 263 nella mappa nuova sono monte, cascata, fiume o casa, e da lì non si arriva né alla porta né alla galleria (`collaudo/vecchie_pos_064.py`, risultato in `vecchie_posizioni.txt`).
   - **Variabile nuova** (dalle variabili sicure): la alza lo script d'ingresso di 35.101, che gira entrando da un'uscita e poi passa a quello della 0.63.
   - **Script di frame:** se la variabile è 0, il giocatore viene portato una volta sola sulla strada davanti alla casa (55,23).
   - **Quando succede:** la variabile resta a 0 solo con Continua su un salvataggio fatto dentro la mappa prima della 0.64. In quel caso si ricaricano anche gli oggetti della mappa nuova.
   - **Effetto collaterale:** succede per tutti i vecchi salvataggi fatti in quella mappa, anche quelli su caselle ancora buone.

## 4. Budget (da `out/rapporto_build.json`)

| | Stima prima | Usato | Resta |
|---|---|---|---|
| Spazio | ~30 KB (tileset) | 27 KB (tileset nuovo con i suoi 16 KB di tile, blocchi riscritti al loro posto, eventi, testi, 3 squadre) | 1212 KB |
| Flag | 0 | 0 nuove; 3 flag di allenatore tolte dal pool perché ora usate dai tre allenatori | 43 nel pool (40 sicure + 3 di allenatore) |
| Variabili | 1 | 1 (variabile della mappa nuova) | 46 |
| Allenatori | 3 | 3 (462, 485, 486) | 15 liberi |
| Strumenti | 0 | 0 | 67 |

## 5. Collaudo (solo tasti; fixture dichiarate)

**Script e risultati**
- Lo script è `collaudo/t64.py`, con `leg.py` e `vai.py`. I risultati sono in `collaudo/risultati/064/`.
- Ogni prova parte da un salvataggio fatto con SALVA in gioco e caricato con Continua dal titolo.
- In VBA-M si riparte dallo stesso `.sav` fatto in mGBA.

**Fixture (scritture in RAM dichiarate, non prove):**
- `prima`: nessuna. Si parte dal savestate `s_ce3.ss`: Cesena, solo la 1ª medaglia, cioè la prima visita.
- `dopo`: si parte da `prog_imola.ss` (6 medaglie).
  - Posizione all'Ippodromo (8,17).
  - SPACCAROCCIA scritta come quarta mossa del Pokémon 0.
- `crea63` (sulla ROM 0.63): posizione a Monte Spaccato (20,3), prima di un SALVA vero. Nella 0.63 è una casella calpestabile, nella 0.64 è monte.
- `vecchio62`: nessuna fixture nuova. Usa `t63_riproduci6.sav`, il SALVA vero della 0.62 fatto per la 0.63 a Monte Spaccato (56,21); nella 0.64 quella casella è la casa.

**prima** (1 medaglia)

| Prova | mGBA | VBA-M |
|---|---|---|
| Cesena → casello → Ippodromo → cancello ovest → si arriva sulla strada davanti alla porta della casa (55,23) | sì | sì |
| Il nome della sezione della mappa, letto dalla ROM con la sezione della mappa corrente, è CAMPAGNA CESENATE. Il riquadro del nome sullo schermo non è stato letto. | sì | sì |
| I tre cartelli, letti a tasti, mostrano i testi del §3 | sì | sì |
| Davanti alla roccia (25,12): A → "Serve SPACCAROCCIA e la terza medaglia per rompere la roccia.", la roccia resta | sì | sì |
| Camminando contro la roccia la posizione non cambia | sì | sì |
| Il pianificatore, dalla posizione vera, non trova strada verso 35.92 (dato del pianificatore) | sì | sì |
| Ritorno: campagna → Ippodromo → casello → Cesena | sì | sì |
| SALVA, Continua: 0x22 a 0 | sì | sì |

**dopo** (6 medaglie, SPACCAROCCIA)

| Prova | mGBA | VBA-M |
|---|---|---|
| OSVALDO, TONINO, NICO: testo di presentazione, lotta vinta con la squadra della tabella del §3, testo di sconfitta; flag dell'allenatore a 1; riparlandogli dice il testo "dopo" e non rilancia la lotta | sì | sì (NICO al 2° tentativo, vedi sotto) |
| A sulla roccia, "sì": la roccia sparisce; 0x22 resta a 0 | sì | sì |
| Galleria → casello 35.92: 0x22 = 1 | sì | sì |
| Ritorno dalla galleria: si arriva in campagna (25,13), la roccia non c'è (0x11 alzata dallo script d'ingresso) | sì | sì |
| SALVA in campagna (43,18), Continua: si resta a (43,18) anche dopo 2 secondi; variabile nuova = 1; la roccia non c'è | sì | sì |
| Dalla campagna a Cesena, passando dall'Ippodromo | sì | sì |

**Vecchi salvataggi**

| Prova | mGBA | VBA-M |
|---|---|---|
| **vecchio63**, salvataggio vero della 0.63 a (20,3), oggi monte: Continua nella 0.64 → davanti alla casa (55,23), variabile = 1; poi si cammina (50,25); SALVA, Continua: si resta a (50,25); si arriva all'Ippodromo | sì | sì |
| **vecchio62**, salvataggio vero della 0.62 a (56,21), oggi la casa: stesso risultato | sì | — (non lanciato) |

**Altre note sulle prove**
- La posizione del salvataggio della 0.63 è confermata con la ROM 0.63 (`t64_crea63.json`: (20,3)).
- **NICO in VBA-M:** al primo tentativo, mentre il pilota parlava con NICO, è partita una lotta selvatica nell'erba alta (MACHOP 25) e il pilota ha battuto quella. La prova ora riprova se la flag dell'allenatore resta a 0: al secondo tentativo la lotta con NICO è stata vinta.
- **Log:** nei log ci sono "fuori percorso", che sono incontri selvatici (fuga). Tutto in `collaudo/risultati/064/log_t64.txt`.

**Analisi statica** (`collaudo/risultati/064/analisi.txt`, `analisi/percorso.py`):
- **Con il solo TAGLIO**, da Cesena si arriva alla casa e davanti alla roccia, ma non a 35.92 né a Capocolle.
- **Con tutte le abilità tranne SPACCAROCCIA** (SURF, FORZA, CASCATA, bici, SUB, FLASH) non ci si arriva comunque.
- **Con SPACCAROCCIA** sì.
- **Dalla campagna a Cesena** si passa sempre dall'Ippodromo: 35.101 → 34.19 → 35.91 → 34.17.
- **Testi:** `analisi/righe.py` non trova riquadri oltre le due righe in 35.101, 35.91 e 34.48.

### Regressione (`collaudo/regressione.py`, 0.64 contro 0.63)

Vedi `collaudo/risultati/064/regressione.md`.

### Cosa non è verificato
- Il riquadro con il nome del luogo che compare entrando non è stato letto sullo schermo: il nome è letto dalla ROM, nella sezione della mappa corrente.
- I testi nuovi di ADA e del casellante non sono stati raggiunti a tasti: la divisione in due righe è controllata sui byte.
- I tre allenatori di prima (ILARIO, LEONIA, PIERO) non sono stati sfidati in questa versione. Le loro flag sono quelle di prima, e prima di cambiarne classe e ritratto il modulo controlla nei loro script il numero di ogni allenatore.
- Il nuovo vestito di LEONIA e PIERO (classe e ritratto in lotta) non è stato visto in lotta.
- Il fiume (SURF), la cascata e gli incontri selvatici nell'erba alta non sono stati provati a parte: le lotte selvatiche viste durante le prove sono partite nell'erba alta della campagna. La tabella degli incontri è la stessa di prima.
- Con un vecchio salvataggio, il ritorno davanti alla casa è stato visto per due posizioni (20,3) e (56,21). Che valga per tutte le 263 caselle segue dallo script, che non guarda la posizione: letto, non provato.
- `vecchio62` non è stato lanciato in VBA-M; lo è `vecchio63`, che usa lo stesso meccanismo.
- Il caso "SPACCAROCCIA senza la 3ª medaglia" resta letto nello script di Smeraldo, come nella 0.63.

## 6. Richieste

| Richiesta | Stato |
|---|---|
| Mappa mostrata finita e approvata prima del modulo | **fatto**: bozza 4 approvata in chat |
| Campagna pianeggiante, nome CAMPAGNA CESENATE | **corretto e verificato** (mappa dalla ROM uguale alla bozza; nome letto dalla ROM) |
| Ordine Cesena → Ippodromo → campagna, niente collegamento diretto con Cesena | **verificato** a tasti nei due versi e con `percorso.py` |
| Più erba alta, allenatori, campi, fiume | **corretto**; i tre allenatori nuovi **verificati** a tasti (mGBA e VBA-M) |
| Monte Spaccato a nord, con la galleria verso Capocolle e la roccia davanti | **corretto e verificato** (rifiuto senza medaglia e MN, rottura, passaggio, ritorno) |
| Il monte non tagliato dagli alberi, qualcosa in alto a destra | **corretto**: il monte prosegue a est, cascata del fiume (bozza 4) |
| Vecchi salvataggi | **verificato** con salvataggi veri della 0.63 e della 0.62 fatti dentro la mappa |
| Testi in italiano, massimo 2 righe | **corretto**, controllato sui byte |
