# Pokémon Romagna: chiusura del Lotto 3 (sulla 0.69)

**ROM provata:** `Pokemon_Romagna_0_69.gba`, SHA-256 `e0a23d7f7c2430cf529ebb2bdf6b9b301d91e0f97340965cbaaa99a0348b3424`.

- Questa chiusura **non cambia la ROM**: niente versione nuova, niente modulo, niente BPS. I salvataggi non sono toccati.
- Collaudo: `collaudo/t70.py`. Risultati in `collaudo/risultati/lotto3_chiusura/`: json, log e schermate.
- Dai log ho tolto le righe "fuori percorso" del pilota, che segnalano solo una ripianificazione.

## 1. Cosa è stato chiesto

Prompt 0.57, Lotto 3: "Non verificato nella 0.56: consegna di Smeargle con squadra e PC entrambi pieni."

Rileggendo il Lotto 3 per chiuderlo ho trovato un altro punto aperto. Riguarda il collegamento fra Ridracoli e il lato di Cesena, per la richiesta "i collegamenti devono essere coerenti in entrambi i versi".
- Nella 0.65 e nella 0.66 risultavano **non provati**:
  - la guida per Ridracoli sul Sentiero del Fumaiolo (Sentiero → 35.50);
  - la guida di 35.50 per Forlì (35.50 → Forlì);
  - il ritorno a piedi dal Sentiero a Cesena.
- L'ho provato qui (§3).

## 2. SMEARGLE con squadra e PC pieni

**Lo script (0.56, `versioni/v056_cesena_rivale.py`, non toccato)**
- Il comando nativo del dono cromatico restituisce 0x800D:
  - 0 se SMEARGLE va in squadra;
  - 1 se va al PC;
  - 2 se non c'è posto.
- Con 2 il pittore tiene SMEARGLE; i PENNELLI e la flag 0x7B0 non si toccano.

**Partenza e fixture dichiarate**
- Si parte da `t56_pennelli.ss`: i tre PENNELLI sono raccolti a tasti nella 0.56, nel labirinto della Rocca (34.33). La squadra è di 2 Pokémon e il PC è vuoto.
- Fixture in RAM, scritte prima di un SALVA vero in gioco; poi titolo e Continua:
  - la squadra a 6, copiando il Pokémon 0 negli slot 2–5 (come la prova tecnica della 0.56);
  - i 420 posti dei 14 box riempiti con la copia del Pokémon 0.
- Dal labirinto al pittore (32,24) e al Centro Pokémon si va **a piedi**.
- Una fixture di posizione in Cesena, scritta stando nel labirinto, lasciava il personaggio invisibile dopo Continua. Per questo non l'ho usata (§5).

| Prova | mGBA | VBA-M |
|---|---|---|
| Squadra 6, PC 420/420, 3 PENNELLI. Parlando al pittore: "Tutti e tre i miei pennelli! Grazie! …", poi "PITTORE: Non hai posto né in squadra né nel PC. Tengo io SMEARGLE: torna quando avrai spazio." I PENNELLI restano 3, 0x7B0 resta 0, il PC resta a 420 | sì | sì |
| Centro Pokémon di Cesena (34.26), PC in (10,1), tutto a tasti: PC DI QUALCUNO → SPOSTA POKéMON → primo Pokémon del BOX 1 → LIBERA → SÌ (il cursore parte su NO). Il PC passa da 420 a 419 | sì | sì |
| Di nuovo dal pittore: "Hai ricevuto SMEARGLE! La squadra è piena: è stato mandato al PC." Il PC torna a 420, nel posto liberato c'è SMEARGLE (specie 235) **cromatico** (calcolato da PID e ID allenatore). I PENNELLI vanno a 0, 0x7B0 a 1, la squadra resta di 6 | sì | sì |
| Parlandogli ancora: "Ho finito il ritratto della fontana. Prenditi cura di SMEARGLE!", senza un altro dono | sì | sì |
| SALVA, titolo, Continua: SMEARGLE cromatico nel PC, PENNELLI 0, 0x7B0 = 1 | sì | sì |

**Schermate**
- In entrambi gli emulatori ho visto il primo riquadro di ciascuno dei tre testi: 2 righe.
- I riquadri seguenti non li ho guardati. Sono testi della 0.56, impaginati da `W.text` a 2 righe da 30 caratteri.

## 3. Ridracoli dal lato di Cesena (andata e ritorno)

**Partenza e fixture dichiarate**
- Si parte da `prog_imola.ss`, con 6 medaglie.
- Fixture, scritte prima di un SALVA vero:
  - la 7ª medaglia (0x86D), richiesta dalla guida;
  - ALDO già affrontato (0x496), come nella 0.66: la sua lotta parte entrando nel Sentiero;
  - la posizione sul Sentiero (35.10) in (17,97). Dopo Continua il personaggio è in (19,97) e va a piedi in (17,97).

| Prova | mGBA | VBA-M |
|---|---|---|
| Guida (17,96): "Sono la guida per la diga di RIDRACOLI. Vuoi che ti accompagni?" (il testo della 0.69), "sì" → valle di Ridracoli 35.50 (18,34) | sì | sì |
| Guida per Forlì in 35.50 (20,34): "Vuoi seguire la guida fino a FORLÌ?", "sì" → Forlì 34.68 (39,52) | sì | sì |
| Guida di Forlì (39,51): stesso testo della guida del Sentiero, "sì" → di nuovo 35.50 (18,34) | sì | sì |
| Guida del sentiero in 35.50 (31,34): "Il sentiero orientale porta alla VALLE DEL SAVIO. Vieni?", "sì" → Sentiero (18,96) | sì | sì |
| Dal Sentiero a piedi fino a Cesena (34.17, 46,46). L'uscita usata non è registrata | sì | sì |

Forlì → 35.50 era già provato nella 0.65. Ora le quattro guide sono provate a tasti: Ridracoli si raggiunge e si lascia in entrambi i versi, sia dal lato di Cesena sia da quello di Forlì.

## 4. Il Lotto 3, punto per punto

| Richiesta | Versione | Stato |
|---|---|---|
| SUB, CASCATA, FLASH, Bici Cross, Super Amo si ottengono | 0.62 | **verificato** (mGBA e VBA-M) |
| Ippodromo sul percorso dalla prima visita; rocce di SPACCAROCCIA al posto del controllo del casello 35.91; nessun aggiramento; chi è già passato non resta fuori | 0.63, 0.64 | **corretto e verificato** |
| Ridracoli coerente nei due versi | 0.65, qui | **verificato**: Forlì → 35.50 nella 0.65; le altre tre guide e il ritorno a Cesena qui (§3) |
| Ritorni a Cesena meno pesanti | 0.67 | **corretto e verificato** (treno regionale; che VOLO serva solo la 2ª medaglia è letto nella ROM) |
| TV in casa del protagonista; Poké Ball della Pineta | 0.68 | **corretto e verificato** |
| Ogni barriera con requisito ottenibile, messaggio chiaro, via di ritorno | 0.69 | **verificato**: inventario e 5 barriere provate a tasti; le altre lette |
| Consegna di SMEARGLE con squadra e PC pieni | qui | **verificato** (mGBA e VBA-M): non era un difetto, lo script era già giusto |

Il Lotto 3 è chiuso.

## 5. Segnalato, non corretto

- **PC in inglese.** Nella schermata dei box del PC restano frasi inglesi di Smeraldo:
  - le etichette "CLOSE BOX" e "PARTY POKéMON";
  - i messaggi "COMBUSKEN is selected.", "COMBUSKEN was released." e "Bye-bye, COMBUSKEN!".
  
  Visto a schermo in mGBA e VBA-M (`t70_libera.png`). I menu ("SPOSTA", "LIBERA", "Liberare questo POKéMON?") sono in italiano. È da sistemare insieme all'interfaccia, perché la traduzione della 0.53 non li copre.
- **Fixture di posizione.** Scritta mentre il personaggio è nel labirinto della Rocca (34.33) per farlo comparire a Cesena, dopo Continua lo lascia invisibile, a (26,15). Riguarda solo gli strumenti di collaudo, non il gioco. Qui ho evitato la fixture camminando.

## 6. Cosa non è verificato

- I riquadri successivi al primo dei tre testi del pittore: non li ho guardati a schermo.
- Il livello 15 di SMEARGLE nel PC: non l'ho letto, perché nel PC il livello non è salvato a parte. La specie e il cromatismo sono letti dai dati del box.
- Quale uscita del Sentiero ha usato il pilota per tornare a Cesena.

## 7. I 611 testi vecchi con righe di 31–42 caratteri: non riscritti

Su richiesta ("se è una cosa utile") ho provato a rimpaginarli tutti a 30 caratteri con `analisi/rifluisci.py`.
- **Come funziona:** cambia solo gli spazi, gli a capo e i cambi di riquadro, quindi si potrebbe riscrivere sul posto senza spazio nuovo.
- **Esito sulle 181 mappe raggiungibili:**
  - 611 testi rimpaginabili;
  - i riquadri salgono da 1055 a 1362 (+29%), e 264 testi ne avrebbero uno in più;
  - i riquadri con una sola riga di 10 caratteri o meno passano da 23 a 160 ("squadra!", "clienti.", "TAGLIO.").
- **Esempio:** "INFERMIERA: Benvenuto al Centro / Pokémon di CESENA. | Mi occupo subito della tua squadra!" diventerebbe "INFERMIERA: Benvenuto al / Centro Pokémon di CESENA. | Mi occupo subito della tua / squadra!".

**Decisione: non li riscrivo.**
- A schermo i testi di oggi entrano nel riquadro: una riga di 41 caratteri è stata vista intera nella 0.69.
- La rimpaginazione automatica li renderebbe più lunghi e più spezzati.
- Il limite di 30 caratteri resta la regola per i testi nuovi e riscritti.
- Un testo vecchio si riscrive a mano quando si lavora sulla sua mappa: per esempio nei lotti città per città.
