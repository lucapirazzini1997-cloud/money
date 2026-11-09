# Pokémon Romagna 0.72: Lido di Savio, casa di ALDO, chiesa (Lotto 4)

**Base:** 0.71, SHA-256 `17c5a9e607717a67975abefe65ed561113073725cd5d54564589bbe28dbf642a`.

**Risultato:** `Pokemon_Romagna_0_72.gba`, SHA-256 `ca69e4f17eb682780a355b2cdfd5c6072b8c838b78360e384144fba56f5080e0`.
- **Patch BPS 0.71→0.72:** `rom/Pokemon_Romagna_0_71_to_0_72.bps`, verificata riapplicandola. Il log è in `collaudo/risultati/072/consegna.txt`.
- **Zip:** lo zip senza `out/`, ricostruito in una cartella pulita, rifà lo stesso SHA.
- **Modulo:** `versioni/v072_lido.py`. Le bozze approvate sono `bozze/lido.py`, `bozze/casa_rivale.py` e `bozze/chiesa_lido.py`; le immagini sono in `bozze/immagini/` (`lido_bozza.png`, `rivale_*.png`, `chiesa_lido.png`).
- **SHA:** è in `build.py` dopo il collaudo (§5).
- **Salvataggi compatibili:** Lido (56×44) e le due stanze di ALDO (14×11, 12×10) hanno le misure di prima, con lo stesso numero di layout; le uscite di prima restano tutte. Ho provato tre salvataggi veri della 0.71 (§5).
- **Flag e variabili:** una flag nuova dal pool, 0x3E (MAREAROMA del parroco). Nessuna variabile nuova.

## 1. Cosa è stato chiesto

- **Prompt 0.57, Lotto 4:**
  - "Casa del rivale: migliorala, interno ed esterno."
  - "Chiesa di Lido di Savio: aprila, con un interno e almeno un evento."
- **In chat, sulla bozza della casa di ALDO:** "Preferisco esterno A, vorrei anche risistemare un po' tutta lido di savio, cercai di renderla più simile a quella originale ma mantenendo le strutture che ci sono già (…), vorrei anche aprire la chiesa e metterci un evento dentro".
- **Risposte alle domande:**
  - **Modello:** il paese vero.
  - **Cosa riprendere:** spiaggia con i bagni, Viale Romagna con negozi, foce del Savio, più pini e meno prato.
  - **Chiesa:** senza nome.
  - **Interno della casa di ALDO:** "Va bene così".
- **Bozza 2:**
  - "L'interno della chiesa così fa schifo".
  - Nomi: gelateria PURO & BIO, piadineria PIANETA PIADA; bagni: in basso BAGNO 340, al centro BAGNO MILANO, in alto BAGNO LIDO.
  - Uscite da sistemare: "tutte sovrapposte e fatte male".
  - Confine con il Savio: "con queste specie di canneti non mi piace molto".
- **Bozza 3:**
  - Le uscite al bordo della mappa "non sono riconoscibili"; il nord "più o meno ci siamo".
  - Coi caselli ripuliti: "Così vanno bene".

## 2. Com'era nella 0.71

- **Lido:**
  - Sulle due rive del Savio c'erano canne e sassi.
  - Sul tetto del casello PINETA era appoggiato uno striscione "PINETA CERVIA", con pini e cespugli attaccati. Anche il casello COSTIERO aveva gli ombrelloni addosso.
  - In spiaggia c'erano due file di ombrelloni e cabine sparse.
  - Molti lotti erano a prato.
  - La porta della chiesa (8,38) era "chiusa a chiave".
- **Casa di ALDO:** la casa azzurra, con l'interno fatto dalla hack nello stile della vecchia casa del protagonista.

## 3. Modifiche (`versioni/v072_lido.py`)

### Lido di Savio

Solo pezzi che la mappa ha già: nessun tile nuovo.

1. **Foce del Savio.**
   - Il capanno da pesca a metà riva nord passa vicino al mare; ora i capanni vicino alla foce sono due.
   - Alla foce ci sono due pontili.
   - Cartello nuovo (41,2): "FOCE DEL SAVIO / I capanni da pesca calano le reti quando sale la marea."
2. **Argine.**
   - **Riva sud:** al posto di canne e sassi c'è un muretto bianco continuo, aperto ai piedi del ponte e al pontile.
   - **Riva nord:** solo prato. Il cartello doppione (16,2) "A nord si trova la FOCE DEL SAVIO" è tolto.
3. **Viale Romagna.**
   - Alberi e lampioni ai lati e una seconda bancarella in piazza.
   - Cartello (17,10): "VIALE ROMAGNA / Negozi, gelati e alberghi fino alla PINETA."
4. **Pini.** Undici pini nei giardini e un boschetto di quattro pini al posto delle aiuole a sinistra del laboratorio. NORA (8,27) resta raggiungibile.
5. **Casa di ALDO, esterno A:** la casa azzurra resta, con l'orto a destra e gli alberi a sinistra.
6. **Spiaggia.**
   - **Tre bagni:** BAGNO LIDO (in alto), BAGNO MILANO (al centro) e BAGNO 340 (in basso). Ognuno ha due cabine, due file di tre ombrelloni e un cartello con il nome: "Lettini e ombrelloni in fila, come in tutta la riviera."
   - **Lungomare:** lampioni regolari.
   - **Restano:** piscina, beach volley, torretta del bagnino (spostata in (51,21)), pattini e barca.
7. **Caselli PINETA e COSTIERO.**
   - Restano nello stesso posto, con le stesse uscite e lo stesso controllo "senza POKéMON". Lo striscione sul tetto è tolto e intorno c'è spazio libero.
   - Due cartelli nuovi:
     - (16,41): "PINETA DEL SAVIO / Il casello porta nella pineta, verso CERVIA."
     - (44,41): "SENTIERO COSTIERO / Il casello porta lungo la spiaggia fino a CERVIA."
8. **Negozi.** Tre porte chiuse ricevono un nome (testo nuovo al posto di "La porta è chiusa a chiave"):

   | Porta | Testo |
   |---|---|
   | (13,35) | "BAZAR DEL LIDO / Secchielli, palette e salvagenti. Chiuso per la pausa pranzo." |
   | (16,35) | "GELATERIA PURO & BIO / Gelato artigianale e biologico." |
   | (33,35) | "PIANETA PIADA / La piastra è ancora fredda: apre stasera!" |

   - Sull'insegna disegnata della gelateria resta "GELATI": "PURO & BIO" non ci sta in quei pixel.
   - **Carattere "&":** non c'era nella tabella dei caratteri dell'engine. Il modulo lo aggiunge (0x2D, il "&" del font di Smeraldo); nessun testo prima lo usava. A schermo si vede giusto (`t72_puro_bio.png`).
9. **Porta della chiesa (8,38).**
   - Il metatile della porta è copiato con il comportamento "porta" (0x60) e senza collisione, in un posto libero del secondario di Lido (0x35D). La tabella dei metatile del secondario è una copia nuova.
   - Il cartello "chiusa a chiave" è tolto. L'uscita 16 porta in chiesa.

### Casa di ALDO (34.40, 34.41)

Dalla bozza approvata. I pezzi sono della casa su due piani 313/314 di Smeraldo, con il primario degli interni e il secondario delle case generiche; il bordo fuori dalla stanza è nero.

| Cosa | Prima | Dopo |
|---|---|---|
| Pianterreno | stile della vecchia casa del protagonista | cucina con frigo e lavello, due tavoli, quattro piante, appunti di allenamento appesi al muro (disegnati a mano) |
| Scale del pianterreno | (12,2) | (2,1) |
| Uscita | (7,10) | (7,10) e la nuova (6,10): lo zerbino è largo due |
| Appunti (6,1), (7,1) | — | "Appunti di allenamento: schivare a destra, poi avvicinarsi. Mai arrendersi!" |
| Mamma di ALDO | (3,3) | (3,3) |
| Camera | letto, scrivania, libreria, tappeto blu | letto sul tappeto, libreria e mobiletto, tappeto d'allenamento azzurro con le impronte (disegnato a mano) |
| Scale della camera | (10,2) | (2,1) |
| Diario | (5,3) sulla scrivania | (11,1) sul mobiletto, stesso testo |
| Personaggio della camera | (5,6) | (5,6), accanto al tappeto delle impronte |

- **Appunti senza nome:** negli appunti non c'è il nome di ALDO, perché `W.text` non sa scrivere il segnaposto del nome del rivale.

### Chiesa (mappa 24.75)

- **La mappa:**
  - 24.75 è una mappa di Ruby rimasta in Smeraldo. Nessuna uscita la raggiungeva e il suo layout (317) non è usato da altre mappe: il modulo controlla tutte e due le cose.
  - L'intestazione ha la musica e le caratteristiche della chiesa di Cesena, la regione di Lido, nessuna connessione e nessuno script di mappa.
- **Interno (14×18):**
  - Pezzi della chiesa di Cesena (34.37) in una navata più corta: abside e altare al centro, organo, candelieri, balaustra, tre file di banchi fra le colonne, acquasantiera e confessionale contro il muro destro.
  - **Colori:** nella copia delle palette, i rombi rossi del pavimento diventano pietra chiara (palette 10.9, 11.7, 12.3) e il tappeto rosso diventa blu mare (11.4, 11.6). Le palette sono le stesse 7 della chiesa di Cesena.
  - **Quadro (2,1):** una barca a vela disegnata a mano sul muro.
- **Evento:** il PARROCO in (8,3).
  - **La prima volta:** "Ogni estate benediciamo il mare e le barche dei pescatori del SAVIO. / Prendi questo MAREAROMA: è l'incenso della festa. Ai POKéMON d'acqua piace!", poi il dono del MAREAROMA (strumento 0xDC) e la flag 0x3E.
  - **Con la borsa piena:** "La tua BORSA è piena. Torna quando avrai fatto spazio!" (non provato, §6).
  - **Dopo:** "Che il mare ti sia sempre calmo, ovunque tu vada!"
  - **Quadro:** "Una barca a vela dipinta: è l'ex voto dei pescatori del SAVIO, tornati a casa dopo una burrasca."
- **Uscita** in (7,17), verso la porta della chiesa a Lido.

## 4. Budget (da `out/rapporto_build.json`)

- **Spazio:** restano 588 KB, quindi la 0.72 ne usa 120.
  - Tre secondari nuovi, ognuno con lo spazio pieno di Smeraldo: le due stanze di ALDO e la chiesa, 25 KB ciascuno.
  - Una copia delle tabelle dei metatile di Lido: 9 KB.
  - I blocchi di Lido, i testi e gli script.
- **Flag:** 34 (una usata).
- **Invariati:** 43 variabili, 67 strumenti, 10 allenatori liberi.

## 5. Collaudo (solo tasti; fixture dichiarate)

**Script e risultati**
- Script: `collaudo/t72.py`; risultati in `collaudo/risultati/072/`.
- La ROM finale `ca69e4f1…80e0` è stata provata in mGBA e in VBA-M. VBA-M riparte dai salvataggi veri fatti in mGBA.

**Fixture dichiarate**
- Solo la posizione di partenza, scritta prima di un SALVA vero:
  - Lido (19,12), sul Viale Romagna;
  - per i vecchi salvataggi, sulla ROM 0.71: 34.40 (9,7), 34.41 (3,7) e Lido (8,39).
- Le partenze sono da `prog_imola.ss`.
- Borsa e flag sono solo lette.

**lido**

| Prova | mGBA | VBA-M |
|---|---|---|
| Cartello del Viale (17,10): "VIALE ROMAGNA / Negozi, gelati e alberghi fino alla PINETA." | ok | ok |
| Porta della gelateria (16,35): "GELATERIA PURO & BIO / …", con "&" a schermo | ok | ok |
| Porta (33,35): "PIANETA PIADA / La piastra è ancora fredda: apre stasera!" | ok | ok |
| Cartello (43,22): "BAGNO LIDO / Lettini e ombrelloni in fila, …" | ok | ok |
| Casa di ALDO: dentro da (25,16) in (7,10); appunti da (6,2); su per le scale fino alla camera (2,2); diario da (11,2) (testo di prima); giù e fuori dalla nuova uscita (6,10) a Lido (25,16) | ok | ok |
| Casello PINETA: da (19,43) giù nella stanza 35.81 (3,2); di nuovo su: Lido (18,43) | ok | ok |
| Casello COSTIERO: da (47,43) giù nella stanza 35.83 (3,2); di nuovo su: Lido (46,43) | ok | ok |
| Chiesa: da (8,39) su, dentro 24.75 in (7,17) | ok | ok |
| Parroco: testo, "Hai ottenuto: MAREAROMA!", "… mette MAREAROMA nella tasca STRUMENTI."; MAREAROMA da 0 a 1, flag 0x3E da 0 a 1 | ok | ok |
| Parroco di nuovo: "Che il mare ti sia sempre calmo, …"; MAREAROMA resta 1 | ok | ok |
| Quadro, da (2,2): il testo dell'ex voto | ok | ok |
| SALVA e Continua in chiesa: si resta in (7,12), MAREAROMA 1; fuori dalla porta a Lido (8,39) | ok | ok |

- Dopo che il pilota cammina, i primi tasti a volte non muovono il personaggio. Per le porte e i caselli ho ripetuto il tasto, fino a 4 volte, finché la mappa cambia: come nella 0.71, è il ritmo del pilota.

**Vecchi salvataggi della 0.71**

| Prova | mGBA | VBA-M |
|---|---|---|
| Salvataggio vero della 0.71 al pianterreno di ALDO (9,7): subito la stanza nuova; fuori dall'uscita (7,10) a Lido (25,16) | ok | ok |
| Salvataggio vero della 0.71 in camera (3,7): giù per le scale nuove al pianterreno (2,2) | ok | ok |
| Salvataggio vero della 0.71 a Lido (8,39): subito la Lido nuova; su: dentro la chiesa | ok | ok |

**Schermate guardate (mGBA):** la gelateria con "&", il pianterreno e la camera di ALDO, la chiesa, l'uscita dalla chiesa, il Viale con il muretto dell'argine.

**Controlli statici.**
- Build: raggiungibilità "nuove 0, problemi 0"; le mappe raggiunte passano da 675 a 676 (la chiesa).
- Il modulo controlla che nessun personaggio o Poké Ball finisca su una casella che diventa bloccata.
- L'immagine della ROM è uguale alla bozza 3.

### Regressione (`collaudo/regressione.py`, 0.72 contro 0.71)

Le 19 partenze (17 savestate in mGBA e il salvataggio vero in mGBA e VBA-M):
- girano e sono vive;
- la callback resta nella ROM;
- 17 sono **uguali** alla 0.71 in tutti i punti di controllo;
- 2 sono **diverse, come previsto**: `t56_rename` e `t56_rename2` partono nel laboratorio (1.4) e il passo "cammina" esce su Lido, che ora ha una mappa diversa. È lo stesso caso della 0.71.

## 6. Cosa non è verificato

- **Borsa piena:** la risposta del parroco con la borsa piena non è provata.
- **"Senza POKéMON":** il blocco davanti ai caselli non è riprovato. Caselle e script sono gli stessi della 0.71, non toccati.
- **Riva nord e foce:** il cartello della foce (41,2), i capanni e i pontili non sono stati raggiunti a tasti; sono solo nell'immagine della ROM.
- **Altri cartelli e porte:** i cartelli di PINETA, COSTIERO, BAGNO MILANO e BAGNO 340 e la porta del BAZAR DEL LIDO non sono letti a tasti. Usano lo stesso script dei cartelli provati.
- **VBA-M:** le schermate sono salvate ma le ho guardate solo in mGBA.

## 7. Richieste

| Richiesta | Stato |
|---|---|
| Casa del rivale, interno ed esterno | **corretto e verificato** (mGBA e VBA-M) |
| Lido più simile al paese vero, con le strutture di oggi | **corretto e verificato** nei punti del §5 |
| Nomi: PURO & BIO, PIANETA PIADA, BAGNO LIDO / MILANO / 340 | **corretto**; letti a tasti PURO & BIO, PIANETA PIADA e BAGNO LIDO |
| Uscite riconoscibili | **corretto e verificato**: caselli ripuliti, andata e ritorno a tasti |
| Confine con il Savio senza canneti | **corretto**: muretto e prato; visto nell'immagine e a schermo dal Viale |
| Chiesa aperta con un evento | **corretto e verificato** |
| Gelateria PURO & BIO visitabile con un evento | **non ancora**: per ora solo il nome sulla porta. È il prossimo punto del Lotto 4 |
| Prossimo nel Lotto 4 | interno della gelateria PURO & BIO, chiesa di Cervia, fenicotteri delle Saline |
