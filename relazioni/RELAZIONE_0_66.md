# Pokémon Romagna 0.66: il nuovo Fumaiolo (Lotto 3)

**Base:** 0.65, SHA-256 `ad1bfa2d6eec44389edbb35a5e802dfe49fb7ede7aa3f5fc1ced63f9baa69a94`.

**Risultato:** `Pokemon_Romagna_0_66.gba`, SHA-256 `SHA_066`.
- Patch BPS 0.65→0.66: `rom/Pokemon_Romagna_0_65_to_0_66.bps` (BPS_BYTE byte), verificata riapplicandola (`consegna.sh`, log in `collaudo/risultati/066/consegna.txt`).
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
- Uscite "sospette" segnalate nella 0.61 (lezione 12): 35.16 → 35.17 era su una casella normale (si entrava solo con lo script del guardiano), 35.13 → 35.18 idem per la guida dopo GROUDON.

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
   - 35.10: guida (21,96), escursionista (9,73), masso (7,72), ALDO (27,78), missione di FORZA (5,73), strumento (8,2, sorgente del Tevere), guida per Ridracoli (17,96).
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

RISULTATI_COLLAUDO

## 6. Strumenti di analisi

- **`analisi/percorso.py` corretto:** sulle caselle a quota 0 (scale, passaggi) Smeraldo dà al giocatore quota 0, e da lì può andare a qualunque quota (`ObjectEventUpdateElevation`); il percorso invece teneva la quota di prima, e per questo non passava le scale del Sentiero (prese dal Percorso 119, dove funzionano). Ora segue il gioco. I controlli della build danno gli stessi risultati di prima (raggiungibilità: nuove 0, problemi 0).

## 7. Richieste

| Richiesta | Stato |
|---|---|
| Mappe mostrate finite e approvate prima del modulo | **fatto**: Sentiero (bozza rimescolata) e le sette stanze approvate in chat; ritocchi per poter giocare dichiarati (§3.9) |
| Il Fumaiolo: la storia va bene, la mappa va rifatta | **corretto e verificato**: storia, personaggi e script di prima, mappe nuove |
| Sentiero non più uguale al Percorso 119 | **corretto**: pezzi rimescolati, colle dell'Eremo, sorgente del Tevere; i pezzi si riconoscono ancora |
| Vecchi salvataggi | **verificato** con un salvataggio vero della 0.65 fatto dentro la vecchia grotta |
| Testi in italiano, massimo 2 righe e 30 caratteri | **corretto** per i testi nuovi (`testi.txt`); restano lunghi i testi comuni del masso di FORZA di Smeraldo, non toccati |
