# Pokémon Romagna 0.66: il nuovo Fumaiolo (Lotto 3)

**Base:** 0.65, SHA-256 `ad1bfa2d6eec44389edbb35a5e802dfe49fb7ede7aa3f5fc1ced63f9baa69a94`.

**Risultato:** `Pokemon_Romagna_0_66.gba`, SHA-256 `d794870a35a619553550d0913395fb5d900e122d50085bc4ec6cab5276b74f84`.
- Patch BPS 0.65→0.66: `rom/Pokemon_Romagna_0_65_to_0_66.bps` (49153 byte), verificata riapplicandola (`consegna.sh`, log in `collaudo/risultati/066/consegna.txt`).
- Modulo: `versioni/v066_fumaiolo.py`. La build da zero rifà tutti gli SHA; lo zip senza `out/` ricostruito in una cartella pulita rifà lo stesso SHA (stesso log).
- Lo SHA è in `build.py` dopo il collaudo (§5).
- **Salvataggi compatibili:** stesse mappe (35.10, 35.12–35.18) con layout nuovi, stessi oggetti con gli stessi numeri e script, stesse uscite con gli stessi indici; una variabile nuova (a 0 nei vecchi salvataggi). Un salvataggio vero della 0.65 fatto dentro la vecchia Grotta (35.13) carica nella 0.66 e prosegue, in mGBA e in VBA-M (§5).

## 1. Cosa è stato chiesto

- Nel Lotto 3 (prompt 0.57, Lotto 12): "la storia va bene, la mappa del Fumaiolo va rifatta".
- Bozza del Sentiero (prima versione, pezzi del Percorso 119): "Sì va tutto bene così mi piace molto puoi procedere". Avevo promesso di rimescolarla perché diventasse una mappa nostra.
- Bozza del Sentiero rimescolata: "Mi piace puoi proseguire".
- Bozza delle sette stanze interne: "Perfetto".

## 2. Com'era nella 0.65

- 35.10 Sentiero del Fumaiolo (56×52): prato con strade, la casa del rifugio (35.11) e la GALLERIA FORZA (35.12). Si arrivava in alto (28,3), da Cesena (eventi a coordinate in 34.17 e 33.18) e dalla guida di Ridracoli (35.50). ALDO lotta all'ingresso con la 7ª medaglia (script di frame).
- 35.12–35.18: stanze rettangolari tutte uguali, con lo stesso tileset di grotta: galleria con il rompicapo del masso, santuario con cinque uscite, i due nodi del TEAM EMILIA, la sala di BASSI, il Cuore con GROUDON, il Passo dei Draghi verso Bagno di Romagna.
- Uscite "sospette" segnalate nella 0.61 (lezione 12): 35.16 → 35.17 era su una casella normale (si entrava solo con lo script del guardiano); 35.13 → 35.18 portava al Passo, dove arriva anche la guida dopo GROUDON.

## 3. Modifiche (versioni/v066_fumaiolo.py)

1. **Le mappe.** I disegni delle bozze approvate (`bozze/fumaiolo.py`, `bozze/santuario.py`) sono copiati nel modulo e congelati. Ogni mappa ha un layout nuovo nello stesso posto della tabella dei layout (id 759 e 761–767, ognuno usato da una sola mappa) e un tileset secondario nuovo fatto con `tela.Unione`.

| Mappa | Prima | Dopo | Modello |
|---|---|---|---|
| 35.10 Sentiero del Fumaiolo | 56×52 | 40×100 | Percorso 119 rimescolato (parte bassa in cima, senza pontili e istituto), colle del Percorso 120, stele = pilastro della vetta del Monte Pira |
| 35.12 Grotta dell'Eremo | 28×20 | 30×32 | Cascata Meteora (sala dei gradoni viola) |
| 35.13 Grotta delle Sorgenti | 32×28 | 29×38 | Cascata Meteora (lago con l'isola), due ingressi nuovi nella parete nord |
| 35.14 Nodo del Sale | 22×20 | 28×24 | Covo Magma (colate di lava) |
| 35.15 Nodo dell'Argilla | 22×20 | 24×17 | Covo Magma (sala dei macchinari) |
| 35.16 Sala di BASSI | 24×22 | 33×39 | Covo Magma (gradoni) |
| 35.17 Cuore del Fumaiolo | 32×28 | 27×30 | Grotta Terra (caverna con il magma) |
| 35.18 Passo dei Draghi | 36×30 | 30×41 | Passo Selvaggio senza il bosco in fondo e senza la porta del covo |

2. **Il Sentiero.** Si entra dal basso, da Cesena, e si risale il SAVIO: prati con l'erba alta, altopiano, cascata e ponte di tronchi; a ovest il colle dell'EREMO DI SANT'ALBERICO con la grotta, chiusa dal masso di FORZA; a est la strada fino al RIFUGIO; il lago con gli scogli, il ponte lungo e la seconda cascata; in cima la sorgente del TEVERE con la stele. Il rompicapo del masso della vecchia 35.12 non c'è più: il masso è davanti alla grotta.
3. **Personaggi e oggetti:** gli stessi di prima, con lo stesso numero e lo stesso script, in punti nuovi (le posizioni sono quelle delle bozze).
   - 35.10: guida (21,96), escursionista (9,73), masso (7,72), ALDO (20,95, accanto all'ingresso), missione di FORZA (5,73), strumento (8,2, sorgente del Tevere), guida per Ridracoli (17,96).
   - 35.12: il masso del vecchio rompicapo resta nella lista ma sempre nascosto (flag nuova 0x35, alzata dallo script d'ingresso); guida (18,27).
   - 35.13: escursionista dell'incisione (15,4), guida (21,34). 35.14 e 35.15: recluta e conduttore. 35.16: BASSI (10,5), guardiano della porta profonda (9,3), soccorso (14,31). 35.17: GROUDON (17,25), guida (7,22). 35.18: guida (17,38), escursionista (21,9), strumento (8,20).
4. **Uscite:** stesse destinazioni e stessi indici di prima, in caselle d'uscita vere (frecce, scale, ingressi di grotta, porta del rifugio); al Sentiero tre frecce in fondo verso Cesena (34.17, uscita 13 come prima), al Passo due frecce in fondo e due in cima.
5. **Script che portano dentro queste mappe** (comando `warp` verificato byte per byte prima di cambiarlo):

| Script | Prima | Dopo |
|---|---|---|
| eventi a coordinate di Cesena (34.17, 33.18) → Sentiero | (28,3) | (19,97) |
| guida di 35.50 → Sentiero | (28,3) | (18,96) |
| guida delle Sorgenti, dopo GROUDON → Passo | (4,23) | (15,39) |
| frane del Passo → indietro | (4,24) | (14,39) |
| guardiano della porta profonda → Cuore | (15,23) | (5,5) |

6. **Testi nuovi** (2 righe, 30 caratteri): guida del Sentiero, cartello d'ingresso, cartello del rifugio, stele del Tevere, guida della Grotta dell'Eremo, incisione della Grotta delle Sorgenti (le direzioni nuove). La bacheca della Valle del Savio è la stessa di prima.
7. **Passo dei Draghi senza Bici Cross.** Nel Passo Selvaggio per salire servono le gobbe con la Bici Cross; qui le gobbe hanno comportamento normale (stessa grafica), così la strada della storia per Bagno non dipende dalla bici.
8. **Vecchi salvataggi fatti dentro queste mappe:** variabile nuova **0x4052**, alzata dallo script d'ingresso (tipo 3) di ogni mappa; uno script di frame (tipo 2, messo prima di quello di ALDO nel Sentiero) riporta una volta sola all'ingresso della mappa: Sentiero (19,97), Grotta dell'Eremo (10,28), Grotta delle Sorgenti (20,35), Nodi (7,20) e (12,14), Sala di BASSI (17,32), Cuore (5,5), Passo (14,39).
9. **Differenze dalle bozze**, tutte per poter giocare (`collaudo/confronto_bozza_066.py`, `confronto_bozza.txt`):
   - stele del Tevere: nella bozza il posto era segnato con un cartello; in gioco è il pilastro del Monte Pira;
   - frecce d'uscita del Sentiero (18–20,99): solo il comportamento;
   - incisione della Grotta delle Sorgenti da (19,33) a (23,35): (19,33) è acqua e A faceva partire SURF (trovato nel collaudo);
   - guardiano della porta profonda da (8,3) a (9,3), e la porta (8,2) senza comportamento di porta: chi torna dal Cuore arriva sulla porta e deve poter scendere; si entra solo con lo script del guardiano, come prima;
   - ALDO da (27,78) a (20,95), accanto all'ingresso: parla e lotta appena si arriva (script di frame), e lontano non si vedeva (trovato nel collaudo);
   - casella di GROUDON (17,25) a quota 0 invece di 1 (lava): Smeraldo dà all'oggetto la quota della sua casella, e con quota 1 A dalla riva (quota 3) non trovava GROUDON (trovato nel collaudo);
   - gobbe del Passo: comportamento normale (punto 7).

## 4. Budget (da `out/rapporto_build.json`)

| | Stima prima | Usato | Resta |
|---|---|---|---|
| Spazio | ~200 KB | 234 KB (8 tileset secondari nuovi, i blocchi delle 8 mappe, eventi, script, testi) | 943 KB |
| Flag | 1 | 1 (0x35, masso del vecchio rompicapo sempre nascosto) | 36 nel pool, tutte sicure |
| Variabili | 1 | 1 (0x4052, vecchi salvataggi) | 44 |
| Allenatori | 0 | 0 | 10 liberi |
| Strumenti | 0 | 0 | 67 |

## 5. Collaudo (solo tasti; fixture dichiarate)

**Script e risultati**
- Lo script è `collaudo/t66.py`, con `leg.py` e `vai.py`. I risultati sono in `collaudo/risultati/066/` (json di ogni parte, `log_t66.txt`; riassunto con `collaudo/riassunto_t66.py`).
- Ogni prova parte da un salvataggio fatto con SALVA in gioco e caricato con Continua dal titolo. In VBA-M si riparte dallo stesso `.sav` fatto in mGBA.
- Tutte le corse sono sulla ROM finale `d794870a…4f84` (lo SHA è in `regressione.md`; i log riportano il nome del file, rifatto dalla build con questo SHA). Le parti in VBA-M sono state fatte dopo tutte quelle in mGBA, ognuna dal suo `.sav` fatto in mGBA; nel log l'ordine delle parti VBA-M non è quello delle tabelle.

**Fixture (scritture in RAM dichiarate, non prove):**
- `aldo`: da `prog_imola.ss` (6 medaglie, BLAZIKEN 50 e BRELOOM 43). **7ª medaglia** (0x86D) e posizione a Cesena (34.17, 46,48), sopra gli eventi che portano al Sentiero.
- `sentiero`: come sopra, più **ALDO già affrontato** (0x496: la sua lotta è nella parte `aldo`), **FORZA e SURF** a BRELOOM; **squadra curata** all'inizio.
- `santuario`: dal salvataggio finale di `sentiero` (fatto in gioco). **5 MASTER BALL**; **squadra curata** prima di ogni lotta (la squadra di prova ha due Pokémon).
- **BASSI** (5 Pokémon, Lv 47–50, letti dalla ROM; nella lotta registrata se ne vedono 3): la squadra di prova perde. Il collaudo torna a uno stato fatto subito prima della lotta e alza le flag della vittoria (0x759 allenatore, 0x4C9, 0x4CA) come **fixture**: serve a provare il Cuore e il Passo, **la vittoria su BASSI non è provata**.
- `ridracoli`: 7ª medaglia, ALDO già affrontato, posizione in 35.50 vicino alla guida del sentiero orientale.
- `crea65` (sulla ROM 0.65): 7ª medaglia e posizione nella vecchia 35.13 (16,20), prima di un SALVA vero.

**aldo**

| Prova | mGBA | VBA-M |
|---|---|---|
| Dagli eventi di Cesena (due passi a sud) si arriva al Sentiero in (19,97) | sì | sì |
| ALDO è sulla mappa accanto all'ingresso (20,95); parla ("Il Team Emilia si muove verso il Fumaiolo…") e la lotta parte da sola (SWELLOW…) | sì | sì |
| La lotta: persa dalla squadra di prova contro 5 Pokémon (prima corsa, `corse_scartate/`); non rifatta | — | — |

**sentiero**

| Prova | mGBA | VBA-M |
|---|---|---|
| Arrivo (19,97); ALDO (0x496 a 1) non c'è | sì | sì |
| Bacheca (17,98): la bacheca di prima; cartello (21,98), guida (21,96), guida per Ridracoli (17,96, "no": testo di prima), cartello del rifugio (27,59): testi nuovi del §3 | sì | sì |
| Porta del rifugio (33,37) → 35.11 e ritorno (33,39) | sì | sì |
| Eremo: escursionista (9,73); missione di FORZA (5,73): "Una dimostrazione perfetta!", POZIONE MAX | sì | sì |
| Masso (7,72) spinto con FORZA (prova: si entra nella grotta), grotta (7,71) → 35.12 (10,29); il masso del vecchio rompicapo non c'è; guida (18,27) | sì | sì |
| Scala (21,23) → 35.13 (20,36); incisione (23,35) e guida (21,34): testi | sì | sì |
| Ritorno: scala → 35.12 (sì); freccia (10,29) → Sentiero: `torna_sentiero` è falso, il pilota resta sulla freccia; l'arrivo sul Sentiero è registrato dal passo dopo (`stele`), senza che il log dica da quale uscita | sì, al secondo comando | sì, al secondo comando |
| Cima: stele del TEVERE (10,4): "Sulla stele è inciso…"; strumento (8,2): IPERPOZIONE, flag 0x140 | sì | sì |
| SALVA e Continua: si resta (9,2), variabile 0x4052 = 1 | sì | sì |

**santuario**

| Prova | mGBA | VBA-M |
|---|---|---|
| Grotta delle Sorgenti → Passo (il pilota arriva in 14,38; l'arrivo in 14,40 e l'ingresso usato non sono registrati); un passo sulla scala (14,37): "Il passo verso BAGNO DI ROMAGNA è chiuso…", si torna a (14,39) | sì | sì |
| Nodo del Sale: recluta battuta a tasti (tre Pokémon, Lv 44–45), "Hai spento nodo del sale…", 0x4C7; conduttore spento | sì | sì |
| Nodo dell'Argilla: recluta battuta a tasti (tre Pokémon tra cui CLAYDOL, Lv 44–45), 0x4C8; conduttore spento | sì | sì |
| Sala di BASSI: soccorso (cura); porta profonda prima di BASSI: "bloccata dall'impianto" | sì | sì |
| BASSI: presentazione e lotta (persa, vedi fixture) | sì | sì |
| Porta profonda dopo BASSI: "La rete è spenta…", si arriva al Cuore (5,5) | sì | sì |
| Cuore: guida (7,22); GROUDON (17,25): "Groudon reagisce alla tua presenza…", lotta, MASTER BALL: GROUDON Lv 50 in squadra, "Groudon è al sicuro…", 0x4CB e 0x4CC | sì | sì |
| Uscita del Cuore (5,4) → Sala di BASSI sulla porta (8,2); un passo in giù: (8,3) | sì | sì |
| Guida delle Sorgenti dopo GROUDON: "Le sorgenti sono tornate calme…", si arriva al Passo (15,39) | sì | sì |
| Passo: la scala (14,37) non rimanda più indietro; guida (17,38), escursionista (21,9), strumento (8,20): ULTRA BALL | sì | sì |
| A piedi su per il Passo fino a Bagno di Romagna (35.19); SALVA e Continua: si resta | sì | sì |

**ridracoli e vecchi salvataggi**

| Prova | mGBA | VBA-M |
|---|---|---|
| Guida di 35.50 (31,34), "sì": si arriva al Sentiero in (18,96) | sì | sì |
| **vecchio65**, salvataggio vero della 0.65 nella vecchia 35.13 (16,20): dopo Continua nella 0.66 il giocatore è in (20,35), variabile 1; si cammina; SALVA, Continua: si resta; si arriva alla Grotta dell'Eremo | sì | sì |

**Note sulle prove**
- Nel primo giro GROUDON non rispondeva ad A e l'incisione lanciava SURF (§3.9): corretti nel modulo prima dello SHA; poi tutte le parti rifatte. Dopo aver spostato ALDO, tutte le parti sono state rifatte ancora sulla ROM finale.
- `torna_sentiero` risulta "no" nel json: il pilota arriva sulla freccia (10,29) della Grotta dell'Eremo ma non la usa al primo tentativo; la prova dopo (la stele) passa proprio da lì e arriva al Sentiero. L'uscita funziona; è il pilota.
- Nei log ci sono "fuori percorso": passi interrotti da incontri o da testi, il pilota ricalcola.
- Il testo di BASSI dopo la vittoria e la sua lotta vinta non sono provati (fixture).

**Analisi statica** (`collaudo/risultati/066/`):
- **Le mappe sono le bozze** (`confronto_bozza.txt`): per le 8 mappe immagine, collisione, quota e comportamento di ogni casella coincidono con la bozza, tranne i cambi dichiarati del §3.9; oggetti, uscite, frane e cartelli nei punti delle bozze (con le differenze dichiarate).
- **Testi** (`testi.txt`): tutti i testi degli script di 35.10–35.18 stanno in 2 righe da 30 caratteri, tranne i 3 testi comuni del masso di FORZA di Smeraldo (35 caratteri), già così prima e non toccati.
- **Percorsi** (`analisi.txt`, `collaudo/analisi_066.py` dall'arrivo da Cesena): senza abilità si arriva al rifugio e alla stele; con FORZA anche alle grotte (35.12, 35.13 solo in basso); con SURF e FORZA a tutte le stanze, a BASSI, al guardiano, al Passo e a Bagno.

### Regressione (`collaudo/regressione.py`, 0.66 contro 0.65)

Tutte le 17 partenze in mGBA e il salvataggio vero in mGBA e VBA-M girano e sono **uguali** alla 0.65 (`regressione.md`, 19 righe "uguale"). Nessuna partenza è al Fumaiolo: le prove delle mappe sono quelle sopra.

### Cosa non è verificato
- Le vittorie su **ALDO** e **BASSI** con una squadra vera (la squadra di prova perde; script non toccati).
- **GROUDON** dopo KO e dopo fuga (script non toccato; provata la cattura).
- Gli **incontri** selvatici delle mappe nuove: le tabelle sono quelle di prima, non provate a parte.
- Il ritorno all'ingresso dei vecchi salvataggi è provato per la Grotta delle Sorgenti; per le altre 7 mappe è lo stesso script con un altro punto d'arrivo (letto).
- Da Bagno giù per il Passo verso il santuario: letto (percorso), non provato a tasti.
- L'ingresso al Sentiero dagli eventi di **33.18** (stesso script di 34.17, provato da 34.17); il ritorno dal Sentiero a **Cesena** dalle frecce (18–20,99); il viaggio con la **guida per Ridracoli** (Sentiero → 35.50).
- **Testi vecchi con direzioni sbagliate** (trovati nella revisione, non corretti in questa versione per non cambiare la ROM collaudata; vanno nella 0.67): la guida del Cuore dopo GROUDON dice che il passo è "a sud-est del santuario" (ora è l'ingresso nord di sinistra); l'escursionista dell'incisione dice "l'argilla a est" (ora è a nord, a destra). Anche "non e ancora disponibile" della guida per Ridracoli è senza accento (testo di prima).
- Screenshot prima e dopo delle mappe in emulatore: non ci sono; le immagini delle mappe sono quelle fatte dalla ROM (bozze approvate e immagine finale inviata in chat).

## 6. Strumenti di analisi

- **`analisi/percorso.py` corretto:** sulle caselle a quota 0 (scale, passaggi) Smeraldo dà al giocatore quota 0, e da lì può andare a qualunque quota (`ObjectEventUpdateElevation`); il percorso invece teneva la quota di prima, e per questo non passava le scale del Sentiero (prese dal Percorso 119, dove funzionano). Ora segue il gioco. I controlli della build danno gli stessi risultati di prima (raggiungibilità: nuove 0, problemi 0).

## 7. Richieste

| Richiesta | Stato |
|---|---|
| Mappe mostrate finite e approvate prima del modulo | **fatto**: Sentiero (bozza rimescolata) e le sette stanze approvate in chat; ritocchi per poter giocare dichiarati (§3.9) |
| Il Fumaiolo: la storia va bene, la mappa va rifatta | **corretto e verificato**: storia, personaggi e script di prima, mappe nuove; due testi vecchi con direzioni da aggiornare (0.67) |
| Sentiero non più uguale al Percorso 119 | **corretto**: pezzi rimescolati, colle dell'Eremo, sorgente del Tevere; i pezzi si riconoscono ancora |
| Vecchi salvataggi | **verificato** con un salvataggio vero della 0.65 fatto dentro la vecchia grotta |
| Testi in italiano, massimo 2 righe e 30 caratteri | **corretto** per i testi nuovi (`testi.txt`); restano lunghi i testi comuni del masso di FORZA di Smeraldo, non toccati |
