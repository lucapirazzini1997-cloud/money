# Pokémon Romagna 0.56: blocchi della storia verificati, Cesena, nome del rivale

**Base:** ROM 0.55. Le due "Storia 1" e "Storia 2" che mi hai mandato sono identiche: SHA-256 `2bfaa8a3…4ad6`. La 0.55 non ha sorgenti, quindi la 0.56 è costruita come modifiche applicate sopra quella ROM.

**Risultato:** `Pokemon_Romagna_0_56.gba`, SHA-256 `b09eb6977ca7ceaf81be2a184d719ce6cc25229d2889e4cc3c4fa4714237495f`.
- La patch BPS 0.55→0.56 (8,8 KB) è verificata.
- Il builder, estratto in una cartella pulita con `rom055.gba` accanto, rifà lo stesso SHA.

La tua 0.44 non è stata toccata.

## 1. I sei blocchi gravi del prompt

Li ho cercati prima nella 0.44 che stai giocando, poi nella 0.55.

| # | Problema | Causa nella 0.44 | Stato | Prova |
|---|---|---|---|---|
| 1 | Bloccato a Rimini prima della medaglia di Cesena | Senza medaglia, ALDO ti spostava con un warp a sud, alla casella (28,74) davanti a Rimini. Ogni volta che risalivi ripestavi la sua riga e venivi rimandato giù. | Corretto dalla 0.47: la destinazione è (23,50), a nord. | **Riprodotto e provato nella 0.55:** dal lato di Rimini, senza medaglia, si torna verso Cesenatico. **Con la medaglia:** lotta, vittoria, ALDO sparisce (flag 0x4e9) e l'evento non si riattiva. |
| 2 | Cartello della Rocca di Forlimpopoli che manda nel vuoto | Cinque cartelli di Forlimpopoli (Rocca, città, Casa Artusi, orto, Via Emilia) puntavano a 0x01e9… invece di 0x09e9…, fuori dalla ROM. Il gioco eseguiva byte a caso e l'esito dipende dall'emulatore. | Corretto dalla 0.47. Nella 0.55 nessuna delle 477 mappe ha puntatori di script non validi. | Provato in gioco: il cartello mostra il testo e ti lascia muovere. |
| 3 | Manca il collegamento Faenza–Imola dopo Lugo | — | La 0.55 ha la strada Faenza → Ponte Santerno → Imola, chiusa fino alla sesta medaglia, e nessuna uscita da Lugo verso Imola. | **Provato giocando**, con la sesta medaglia messa da emulatore: Lugo → sentiero → Galleria dei Sigilli → sentiero → Faenza → Ponte Santerno. Il tecnico sul ponte, con la medaglia, si sposta. Poi Imola, la palestra di Rino e la cura al Centro di Imola. |
| 4 | Stazione Ravenna–Lugo | — | Nella 0.55 la vecchia stazione (35.59) è un edificio senza warp. Si va a piedi: Ravenna → casello 35.98 → Via dei Canali → Campagne di Lugo → Lugo. | **Provato:** senza la missione del Team Emilia di Ravenna conclusa (flag 0x2ac), il casello ti ferma e ti rimanda indietro. Con la missione conclusa si passa. Da Lugo verso Ravenna si torna sempre. Nessun altro warp o script porta a Lugo o Imola. |
| 5 | Si cammina sull'acqua tra Lido e Mirabilandia | Nella Pianura Romagnola (34.93) le 432 caselle di mare erano al livello 3, come la terra. | Corretto nella 0.55: livello 1. | **Solo controllo statico** di tutte le mappe raggiungibili. L'unica con acqua a livello 3 è il fondale sottomarino di Rimini (35.37), dove è normale. |
| 6 | Team Emilia alle Befane che resta dopo la sconfitta | Il primo tecnico aveva il flag di visibilità 0, quindi non spariva mai. | Corretto (dalla 0.52). | **Solo controllo statico.** Dopo la lotta ogni tecnico imposta il suo flag (0x27d, 0x27e, 0x27f), sparisce e consegna lo strumento vero: BOBINA EMILIA, REGOLATORE, PROGETTO CAVA. |

**Salvataggi della 0.44:** se il tuo salvataggio è nel vuoto di Forlimpopoli o bloccato a Rimini, mandami il file .sav. Il punto del vuoto dipende dai byte a caso eseguiti dal tuo emulatore. Solo con il file posso aggiungere un recupero mirato e provare che carichi sulla nuova versione senza perdere niente.

## 2. Novità della 0.56

### Cesena: "I pennelli del pittore" → SMEARGLE shiny Lv15
- **Pittore:** accanto alla Fontana Masini, in piazza (casella 32,24, rivolto verso la fontana). Spiega che il vento ha portato i suoi tre pennelli nel labirinto del Parco della Rocca. Riconosce il progresso: "Uno dei miei pennelli! Ne mancano ancora due", "Due pennelli su tre!".
- **Strumento nuovo PENNELLO** (numero 0x15b, prima vuoto): strumento chiave con descrizione. La quantità la conta il pittore. Tre Poké Ball nel labirinto, in tre vicoli ciechi lontani fra loro e dal TORKOAL dorato, che resta com'era.
- **Consegna:** con tre pennelli il pittore ti dà uno SMEARGLE Lv15 davvero shiny. I pennelli vengono tolti solo dopo che lo hai ricevuto.
  - Squadra piena: va al PC.
  - Squadra e PC pieni: non ricevi niente, i pennelli restano a te e torni dopo.
- Il dono si riceve una volta sola.

### Biblioteca Malatestiana: "L'enigma dei tre codici" → MT17 PROTEZIONE
- **Archivista:** in fondo al corridoio, sotto l'Aula del Nuti. Chiede di consultare i tre codici sui plutei dal più antico al più recente, con gli anni in numeri romani.
- **I tre plutei**, sparsi nella sala:
  - Isidoro, MCDXLVII;
  - Agostino, MCDLII;
  - Plinio, MCDLIV.
- **Gli errori:** un ordine sbagliato azzera la sequenza e si riprova.
- **Il premio:** a ordine completo l'archivista dà la MT17 PROTEZIONE, che nella 0.55 non si otteneva da nessuna parte. Con la Borsa piena la custodisce lui. È una sola copia.

### Chiesa di Cesena: "La luce del rosone" → PIETRALUNARE
- **Le tre vetrate:** dicono l'ordine delle candele e che si leggono da sinistra a destra:
  - I: la candela vicino all'altare;
  - II: la candela sulla parete destra, accanto al confessionale;
  - III: la candela sulla parete sinistra, fra le colonne.
- **Gli errori:** sbagliando, la fiamma si spegne e si ricomincia.
- **Il premio:** con l'ordine giusto la luce del rosone illumina una nicchia ai piedi dell'altare, con una PIETRALUNARE. È una sola volta; con la Borsa piena la pietra resta nella nicchia.
- **Il sacrestano** accenna all'enigma.
- **Cosa non ho toccato:** non ho rifatto la facciata e non ho identificato la chiesa reale. Il nome della chiesa non compare nella ROM.

### Nome del rivale nei salvataggi vecchi
- **Dove:** nel laboratorio di Lido di Savio, casella (10,10), c'è un personaggio che dice "Il tuo amico d'infanzia si chiama …".
- **Cambiare il nome:** se vuoi cambiarlo si apre la schermata "NOME DEL RIVALE?". Lasciandolo vuoto resta quello di prima.
- **Tornare ad ALDO:** se rispondi no, ti propone di tornare ad ALDO.
- **A chi serve:** a chi viene da un salvataggio vecchio, dove il rivale è sempre ALDO, e a chi vuole correggere il nome scelto.

### Flag nuovi
12 in tutto, da allenatori che nessuno script usa, controllati contro tutti i flag usati nella 0.55:
- **Pennelli:** 0x7b3, 0x7b2, 0x7b1;
- **Smeargle consegnato:** 0x7b0;
- **Codici:** 0x7ad, 0x7ac, 0x7ab, 0x7aa;
- **Rosone:** 0x794, 0x793, 0x792, 0x78a.

Le modifiche scrivono solo nello spazio libero della 0.55, quindi i salvataggi della 0.55 restano compatibili.

## 3. Test in emulatore (onesto)
Tutti con la ROM 0.56. Dove non scrivo altro, ho usato solo i tasti.
- **Pittore:**
  - con 1 e 2 pennelli il pittore dà le frasi di progresso;
  - ho raccolto i tre pennelli nel labirinto: flag impostati, PENNELLO ×1, ×2, ×3;
  - consegna: SMEARGLE Lv15 in squadra, valore di cromaticità 0 (shiny se è sotto 8), pennelli a 0, flag 0x7b0 impostato;
  - parlandogli di nuovo non dà niente.
- **Squadra piena:** prova tecnica, con la squadra portata a 6 da emulatore copiando un Pokémon. SMEARGLE va nel box (da 0 a 1 Pokémon) e la consegna è registrata.
- **Biblioteca:**
  - II per primo: niente;
  - I e poi III saltando II: sequenza azzerata;
  - I, II, III: completata;
  - l'archivista dà la MT17 ×1, e una seconda conversazione non ne dà un'altra.
- **Chiesa:**
  - vetrate e altare letti;
  - candela destra per prima: azzerata;
  - altare e poi sinistra saltando la destra: azzerata;
  - altare, destra, sinistra: completata;
  - l'altare dà la PIETRALUNARE ×1, e la seconda volta "La nicchia è vuota".
- **Nome del rivale:**
  - cambio del nome: la variabile 0x40fc cambia e il testo lo usa;
  - ritorno ad ALDO: la variabile torna a 0 e il testo dice "si chiamerà di nuovo ALDO".
- **Salvataggio:**
  - salvo dal menu del gioco, riavvio l'emulatore da zero e scelgo "Continua";
  - risultato: stessa posizione, SMEARGLE shiny in squadra, MT17 e PIETRALUNARE in borsa, gli 8 flag delle missioni impostati;
  - **un primo tentativo è fallito:** il riavvio non era arrivato in gioco e il programma ha letto tutto vuoto. Era un problema di tempi del mio programma di prova; i due tentativi successivi sono riusciti.
- **Progressione e rivale di Rimini:** vedi la tabella al punto 1.
- **Testi:** tutti i riquadri nuovi controllati a schermo, entro 2 righe.

**Partite di prova dichiarate:**
- Sono savestate della mia partita in emulatore: Cesenatico, Cesena e Rimini dalla 0.51, laboratorio dalla 0.54.
- Senza la medaglia di Cesena per il rivale di Rimini: medaglia e flag del rivale tolti da emulatore. Per la lotta vinta la medaglia era rimessa da emulatore.
- Sesta medaglia per il percorso verso Imola: messa da emulatore. Ho provato a vincere ALIDA davvero e ho perso, perché la squadra del mio programma ha solo due Pokémon.
- Flag 0x2ac di Ravenna, nei due stati: messo da emulatore.
- Squadra piena per Smeargle: da emulatore.

## 4. Non verificato
- Squadra e PC entrambi pieni alla consegna di SMEARGLE (lo script lo gestisce, ma non l'ho provato).
- La sesta medaglia vinta davvero contro ALIDA.
- L'acqua tra Lido e Mirabilandia e le Befane: solo lettura della ROM, nessuna prova in gioco.
- Il recupero di un salvataggio 0.44 nel vuoto: serve il tuo file.
- Emulatori diversi da mGBA per le novità della 0.56. La 0.54 l'avevo provata anche con VBA-M.

## 5. Inventario delle richieste del prompt

Legenda:
- **fatto**: presente e provato;
- **presente**: c'è nella ROM, ma in questa revisione non l'ho riprovato;
- **da fare**: manca.

| § | Richiesta | Stato |
|---|---|---|
| 5.1 | Nome del rivale | fatto: a inizio partita (0.52, corretto nella 0.54) e per i salvataggi vecchi (0.56). Telefonate: nella hack non esistono. |
| 5.2 | Rivale a Rimini | fatto (0.47), verificato ora |
| 6 | Strumento per le mosse | presente: il MOSSOMETRO (0.47), che te lo dà l'istruttore nel Centro Pokémon di Forlimpopoli. Ricorda le mosse di livello e fa dimenticare qualunque mossa, MN comprese, con un controllo per SURF. Non tiene lo storico di MT e MN. |
| 7 | Caselli tra le aree | presente in molti passaggi (0.48 e successive). Manca l'inventario completo di quelli che restano. |
| 8 | Erba e allenatori nelle campagne | presente (0.48: campagne, Riviera, Via Emilia Ovest); bilanciamento non rivisto |
| 9.1 | Insegna della Casa delle Aie | da fare |
| 9.2 | Grattacielo di Cesenatico | da fare |
| 9.3 | Esterno della Rocca di Cesena, mezzo tavolo | da fare |
| 9.4 | Fontana Masini e pittore | missione fatta (0.56); grafica della fontana da fare |
| 9.5 | Chiesa | evento fatto (0.56); facciata da fare |
| 9.6 | Biblioteca, enigma dei codici | fatto (0.56) |
| 10 | Centri Pokémon originali | presente (0.49) |
| 11.1 | Porto di Rimini, locali, Amo Buono | Amo Buono presente (0.52); porto e locali da fare |
| 11.2 | Casa con il lampione a Rimini | da fare |
| 11.3 | Befane | fatto (0.52), verificato sulla ROM |
| 11.4 | Farfetch'd shiny all'Arco | presente (0.49) |
| 12.1 | Fabbrica Babbi in alto e colori | da fare |
| 12.2 | Rocce dell'ippodromo e Monte Spaccato | Monte Spaccato c'è (0.55); le rocce sono da verificare |
| 12.3 | Cartello di Forlimpopoli | fatto (0.47); recupero dei salvataggi: serve il tuo file |
| 12.4 | Volo e mappa per Forlimpopoli | presente (0.47) |
| 12.5 | Via Emilia Ovest | presente (0.48), da rivedere |
| 13 | Piazza Saffi, Ravaldino ("Caterina Sforza quadro"), fiume Forlì–Faenza | fiume ampliato nella 0.55; piazza e Ravaldino da fare |
| 14.1, 14.2 | Piazza di Faenza, "Le ceramiche trafugate" | da fare |
| 14.3 | Faenza–Imola | fatto (0.55), provato ora |
| 15 | Terreni per bacche | presente (0.48: 26 terreni) |
| 16.1 | Acqua tra Lido e Mirabilandia | fatto (0.55) |
| 16.2, 16.3 | Aree separate prima di Classe; Voltorb e Bagon | da fare |
| 17 | Safari stile Smeraldo con i tre leggendari | da fare. Oggi Entei è nelle rovine, Raikou a Mirabilandia e Suicune in un lago. |
| 18 | Ravenna–Lugo a piedi | fatto (0.55), provato ora |
| 19 | Lugo: dimensioni, aeroporto, uccelli della Rocca Estense | da fare |
| 20 | Galleria Lugo–Faenza e tre Regi | presente (0.55). Ho provato in gioco i blocchi della sesta medaglia (lato Lugo e passaggio con la medaglia); enigmi e Regi non provati. |

**Prossimo lotto proposto (0.57):** Rimini, cioè il porto con osterie e pescheria e la casa col lampione, insieme alla grafica di Cesena: fontana, Rocca, Casa delle Aie, grattacielo.

## File
- `Pokemon_Romagna_0_56.gba`
- `Pokemon_Romagna_0_55_to_0_56.bps`: da applicare alla 0.55 (Storia 1 o 2).
- `builder_0_56.tar.gz`: metti `rom055.gba` (la 0.55) accanto a `build56.py` e lancia `python3 build56.py --out out`.

**Salvataggi:** un salvataggio della 0.55 si carica sulla 0.56 così com'è. Le missioni nuove compaiono entrando nelle mappe di Cesena e del laboratorio.
