# Pokémon Romagna 0.70: la casa del protagonista (Lotto 4)

**Base:** 0.69, SHA-256 `e0a23d7f7c2430cf529ebb2bdf6b9b301d91e0f97340965cbaaa99a0348b3424`.

**Risultato:** `Pokemon_Romagna_0_70.gba`, SHA-256 `0eccfb3f9c188b984f7b111d549b8afceb36a8fc64ffc744d35f4179af22dfa3`.
- **Patch BPS 0.69→0.70:** `rom/Pokemon_Romagna_0_69_to_0_70.bps` (12.109 byte), verificata riapplicandola. Il log è in `collaudo/risultati/070/consegna.txt`.
- **Zip:** lo zip senza `out/`, ricostruito in una cartella pulita, rifà lo stesso SHA.
- **Modulo:** `versioni/v070_casa.py`. La bozza approvata è `bozze/casa_protagonista.py`; le immagini sono in `bozze/immagini/`.
- **SHA:** è in `build.py` dopo il collaudo (§5).
- **Salvataggi compatibili:** le due mappe hanno le misure di prima (14×10 e 12×9), con le stesse porte e lo stesso numero di layout. Ho provato due salvataggi veri della 0.69 fatti dentro casa (§5). Nessuna flag e nessuna variabile nuova.

## 1. Cosa è stato chiesto

- **Prompt 0.57, Lotto 4:** "Casa del protagonista: rifai l'interno."
- **Bozza 1** (pezzi della casa di Smeraldo): "Sì vorrei qualcosa che ricordi di più la Romagna, il mare va bene".
- **Bozza 2**, con il mare e i dettagli romagnoli: "Va bene così".

## 2. Com'era nella 0.69

- **Pianterreno (1.0):** un tileset fatto dalla hack, con pavimento bianco, cucina, divano, tavolo e TV sparsi. In fondo alla stanza c'è una fila nera. La scala è appoggiata al muro a destra, in (12,2).
- **Camera (1.1):** stesso stile, con letto, scrivania con PC, libreria, TV e tappeto.

## 3. Modifiche (`versioni/v070_casa.py`)

1. **Disegno.** Pezzi della casa del protagonista di Smeraldo (layout di 1.2 e 1.3, che nessuna mappa usa e non raggiungibili), con il primario degli interni 0x55ea40 e il secondario 0x55ecb0. Da altre case di Smeraldo vengono due piante in vaso (5.7) e una libreria (6.6).
   - **Pianterreno:**
     - scale a sinistra, nel rientro del muro;
     - finestre, vetrina, lavello con fornelli e frigo;
     - TV e mobile;
     - tappeto con il tavolo e quattro sedie;
     - due piante ai lati dell'ingresso.
   - **Camera:**
     - scale a sinistra;
     - orologio, TV con console, cartina, scrivania con il PC, salvagente e libreria;
     - telo da mare, letto e una pianta.
2. **Romagna e mare, disegnati a mano.** Tutto sta nello strato alto dei metatile, con le tavolozze 1 e 5 del primario degli interni. Il gioco le carica sempre, quindi non occupano posti del secondario.
   - **Finestre del pianterreno:** cielo, foschia, orizzonte e mare con le onde, e una vela bianca.
   - **Tavolo:** la tovaglia romagnola stampata a ruggine.
   - **Camera:** un salvagente bianco e rosso al muro, e il tappeto rosa diventa un telo da mare a righe bianche e azzurre.
3. **Layout.**
   - Ogni piano ha un secondario nuovo (pianterreno: 61 metatile e 130 tile; camera: 129 metatile, di cui 66 di riempimento, vedi il punto 5; 7 palette ciascuno) e un layout nuovo.
   - Il layout nuovo prende il posto del vecchio nella tabella dei layout (id 633 e 55, solo di queste mappe; il modulo lo controlla). Continua carica il layout da quella tabella.
4. **Bordo.** Fuori dalla mappa c'è un metatile nero nuovo. Con il metatile 0 del primario si vedeva rosa: l'ho visto a schermo nella prima corsa del collaudo e corretto.
5. **PC.** In (8,1) c'è il PC di casa di Smeraldo, metatile 0x27E.
   - Il gioco accende il PC scrivendo da solo l'id 0x27F; prima di spegnerlo, l'id 0x27E.
   - Nel secondario nuovo i due metatile stanno agli stessi id 0x27E e 0x27F. Per questo il secondario della camera ha 129 metatile: quelli fino a 0x27F sono riempiti con copie.
   - Senza questo, nella prima corsa il monitor diventava rosa dopo l'uso.
6. **Eventi.**

   | Cosa | Prima | Dopo |
   |---|---|---|
   | scale del pianterreno (uscita 2) | (12,2) | (3,2) |
   | scale della camera | (10,2) | (1,1) |
   | la mamma | (4,3) | (11,3), davanti alla cucina |
   | PC della camera | (4,3), (5,3) | (8,1) (un evento solo: l'effetto accende la casella guardata) |
   | TV del pianterreno (3,4) | — | evento: "In TV c'è il meteo del mare: ADRIATICO calmo e bandiera bianca. Si può fare il bagno!" |
   | TV della camera (4,1) | — | evento: "Danno un documentario sulle SALINE di CERVIA e sui loro fenicotteri." |

   - Le due TV di Smeraldo hanno il comportamento "televisione". In camera davano "MOM might like this program. … Better get going!" in inglese; al pianterreno, nella prima corsa, non hanno dato nessun testo nuovo.
   - Gli eventi delle TV hanno la precedenza sul comportamento.
7. **Cartina della camera.** Il comportamento 0x85 apre già la cartina della ROMAGNA. La frase prima della cartina, "{giocatore} took a closer look at the HOENN region map.", è tradotta sul posto: "{giocatore} guarda la cartina della ROMAGNA.".
   - È una frase comune di Smeraldo, usata da ogni casella con quel comportamento.

## 4. Budget (da `out/rapporto_build.json`)

- **Spazio:** restano 739 KB, quindi la 0.70 ne usa 52. I due secondari occupano lo spazio pieno di Smeraldo: 16 KB di tile, 8 KB di metatile e 1 KB di attributi ciascuno.
- **Invariati:** 35 flag, 43 variabili, 67 strumenti, 10 allenatori liberi.

## 5. Collaudo (solo tasti; fixture dichiarate)

**Script e risultati**
- Script: `collaudo/t70casa.py`; risultati in `collaudo/risultati/070/`.
- La ROM finale `0eccfb3f…dfa3` è stata provata in mGBA e in VBA-M. VBA-M riparte dai salvataggi veri fatti in mGBA.

**Fixture dichiarate**
- Solo la posizione di partenza, scritta prima di un SALVA vero:
  - Lido di Savio (8,17) davanti alla porta;
  - per i vecchi salvataggi, 1.0 (9,8) e 1.1 (3,6) sulla ROM 0.69.
- Le partenze sono da `prog_imola.ss`.
- Le scale si prendono facendo camminare il pilota da un piano all'altro.

**casa**

| Prova | mGBA | VBA-M |
|---|---|---|
| Su dalla strada: dentro, in (9,9); la mamma è in (11,3) | ok | ok |
| Mamma: "Prima di partire, riposati un po'. I tuoi POKéMON sono di nuovo in forma!" | ok | ok |
| TV del pianterreno, da (2,4): il testo del meteo del mare | ok | ok |
| Su per le scale: camera, (1,2) | ok | ok |
| PC, da (8,2): "… accende il PC.", "Cosa vuoi fare?"; si chiude con B | ok | ok |
| TV della camera, da (4,2): il documentario sulle SALINE | ok | ok |
| Cartina, da (6,2): "… guarda la cartina della ROMAGNA.", poi si apre la cartina della ROMAGNA | ok | ok |
| Sul telo da mare (2,4); giù per le scale: pianterreno (3,3) | ok | ok |
| SALVA e Continua: si resta in (3,3), la mamma in (11,3); fuori dalla porta a Lido di Savio (8,17) | ok | ok |

**Vecchi salvataggi della 0.69**

| Prova | mGBA | VBA-M |
|---|---|---|
| Salvataggio vero della 0.69 al pianterreno (9,8), caricato nella 0.70: subito la stanza nuova (schermata `t70casa_vecchio_pt.png`); su in camera, di nuovo giù, la mamma è in (11,3); fuori dalla porta | ok | ok |
| Salvataggio vero della 0.69 in camera (3,6): subito la camera nuova; PC da (8,2); giù al pianterreno (3,3) | ok | ok |

**Schermate guardate.** Pianterreno e camera nel gioco; i riquadri delle due TV e della cartina, su 2 righe; il bordo nero; il PC dopo l'uso.

**Controlli statici.** `analisi/percorso.py` sulla 0.70, senza abilità, da Lido di Savio: si raggiungono le scale, la mamma e il PC. Build: raggiungibilità "nuove 0, problemi 0".

### Regressione (`collaudo/regressione.py`, 0.70 contro 0.69)

Le 19 partenze (17 savestate in mGBA e il salvataggio vero in mGBA e VBA-M):
- girano e sono vive;
- la callback resta nella ROM;
- sono **uguali** alla 0.69 in tutti i punti di controllo. Nessuna parte dalla casa.

### Cosa non è verificato

- **La mamma nei vecchi salvataggi.** Nelle due partite di prova costruite per i vecchi salvataggi, subito dopo Continua la mamma non c'era: la lista degli oggetti della partita viene dal savestate di partenza (35.9). In un salvataggio vero fatto in casa nella 0.69, dopo Continua la mamma dovrebbe stare al suo posto vecchio (4,3) finché non si esce dalla stanza: l'ho solo letto nel codice di Smeraldo, non provato. (4,3) è pavimento anche nella casa nuova.
- **Il PC dopo la chiusura** resta col monitor acceso (0x27F) fino a quando si esce dalla stanza; non ho visto lo spegnimento.
- **Il secondo riquadro delle TV** non l'ho guardato a schermo. I testi sono impaginati a 2 righe da 30 caratteri.

## 6. Richieste

| Richiesta | Stato |
|---|---|
| Rifai l'interno della casa del protagonista | **corretto e verificato** (mGBA e VBA-M) |
| Qualcosa che ricordi di più la Romagna, il mare | **corretto**: finestre sul mare, tovaglia a ruggine, salvagente, telo, TV con il mare e le SALINE |
| Mappe mostrate finite e approvate prima del modulo | **fatto** ("Va bene così"). Differenze dalla bozza: bordo nero, PC 0x27E, eventi delle TV, frase della cartina (§3) |
| Vecchi salvataggi | **verificato** con due salvataggi veri della 0.69 fatti in casa |
| Prossimo nel Lotto 4 | laboratorio (esterno); poi casa del rivale, gelateria "Puro & Bio", chiese di Lido e di Cervia, fenicotteri delle Saline |
