# Pokémon Romagna 0.47: Volo a Forlimpopoli, oggetti Befane, Mossometro

Base: ROM 0.46 (SHA-256 `4078342e…466b`). La tua 0.44 non è stata toccata.
Risultato: `Pokemon_Romagna_0_47.gba`, SHA-256 `d26c0fd48f75fe1db4e36865f56b7ea9c9fd7914954d72e06ccfbaf45930122d`.
2089 byte cambiati rispetto alla 0.46. `.bps` 0.46→0.47 controllato (applicato alla 0.46 dà esattamente la 0.47). Il builder rifatto da zero dà lo stesso SHA (tre volte, anche dal pacchetto estratto).
Cambiano solo tabelle, script e testi: i salvataggi della 0.46 dovrebbero restare validi (non ho caricato un salvataggio reale).

## Cosa c'è di nuovo

**1. Volo a Forlimpopoli.** Nella mappa del Volo la cella (13,8) esisteva già (ex "Bertinoro", mai usata da nessuna mappa della hack). Ora si chiama FORLIMPOPOLI e porta a (3,19), accanto al Centro Pokémon. La città si sblocca entrando a Forlimpopoli.
Trovato un conflitto: la flag nativa di visita di quella cella (0x874) la usa già la trama della hack. Ho cambiato la costante nel codice del Volo e uso la flag 0x46D, che nessuno script usa. Chi era già a Forlimpopoli deve rientrarci una volta.

**2. Oggetti Befane concreti.** Cinque oggetti chiave veri, visibili nella Borsa (tasca Strumenti), riusando slot di oggetti FRLG che Smeraldo non dà mai:
- REGISTRO MOLO: dopo il tecnico al deposito della banchina sud.
- FATTURA: dopo il corriere del Ponte di Tiberio.
- BOBINA EMILIA, REGOLATORE, PROGETTO CAVA: dai tre tecnici ai piani 3, 4 e 5.
Quando consegni il PROGETTO CAVA ad Ada, lei lo prende ("lo tengo io") e poi ti dà la MN come prima. Gli altri restano come ricordo. Chi aveva già finito l'evento non riceve nulla in più.

**3. MOSSOMETRO.** Oggetto chiave usabile dal campo, dalla Borsa. Menù a due domande: far ricordare una mossa (stesso meccanismo del Ricordamosse di Smeraldo, gratis) o far dimenticare una mossa (stesso del Cancellamosse, anche le MN). Resta una protezione: non si può dimenticare SURF se è l'ultimo POKéMON che lo conosce. Lo regala un istruttore nel Centro Pokémon di Forlimpopoli (flag 0x479, una volta sola).
Il Mossometro ricorda le mosse imparate salendo di livello, non le MT né le mosse uovo: è il comportamento del Ricordamosse nativo.

## Collaudo (mGBA con tasti reali; fixture dichiarate)
Fixture: copie di prova con l'uscita del Bar Panama reindirizzata alla mappa da provare; dove serviva un POKéMON, un Pidgeot Liv 50 dato da un NPC di prova con le mosse scritte nella RAM; flag di prova (0x860, medaglie, Faenza visitata); per la lotta ai tecnici un Tyranitar Liv 60. Niente di questo è nella ROM consegnata.

Verificato:
- Volo: da Forlimpopoli compare "FLY to where?" con la cella FORLIMPOPOLI, la scelta atterra a Forlimpopoli (3,19). La flag 0x46D si imposta entrando in città.
- Befane piano 5: vera lotta contro ING. NERI, a fine lotta PROGETTO CAVA in Borsa, flag 639 e tecnico sparito. Ada: dà il testo nuovo, ritira l'oggetto (sparisce dalla Borsa).
- Mossometro: oggetto in Borsa con nome e descrizione giusti. Si apre lo script. Ramo "ricorda": scelta POKéMON, elenco mosse, "Teach TACKLE?" nativo. Ramo "dimentica": scelta POKéMON, schermo mosse, conferma "PIDGEOT: dimenticare FLY. Sei sicuro?", poi "PIDGEOT ha dimenticato FLY per sempre." (mossa davvero cancellata dal messaggio finale).
- Istruttore nel Centro: dà il Mossometro una volta (flag 0x479).

NON verificato:
- Gli altri quattro oggetti Befane (registro, fattura, bobina, regolatore): stesso codice del piano 5 con controllo automatico delle flag, ma non ho giocato quelle lotte.
- Cosa succede nel Mossometro con UOVO, POKéMON con una sola mossa, SURF protetto, annullamento a metà.
- Volo da altre città verso Forlimpopoli: provato solo da Forlimpopoli stessa. Il colore del nodo sulla mappa del Volo non l'ho confrontato (la scelta funziona).
- Borsa piena: se la tasca Strumenti è piena i cinque oggetti Befane andrebbero persi (la lotta non si rifà). Improbabile (30 posti), ma non gestito.
- L'effetto sui salvataggi reali.

## Non fatto: rivale rinominabile
Non è risolvibile con soli script. Il nome del rivale (ALDO) sta nella tabella allenatori e nei testi: la battaglia lo legge direttamente da lì, non da una variabile salvata. Servirebbe codice nuovo nella ROM (schermata di nome, salvataggio del nome, modifica dei punti dove la battaglia legge il nome). È fattibile, ma richiede un lavoro mirato sul codice: lo propongo come passo separato prima della 0.50.
Alternativa meno ambiziosa: scegliere il nome da un elenco fisso (6-8 nomi), con copie della tabella allenatori. Dimmi tu quale preferisci.

## Ancora da fare
0.48: case al posto dei warp nudi, campagna più ricca, terra per le bacche. 0.49+: città, cromatici, Safari/Mirabilandia, Lugo ridotta, Rocca Estense, rivale rinominabile.

## File
- `Pokemon_Romagna_0_47.gba`
- `Pokemon_Romagna_0_46_to_0_47.bps` (da applicare alla 0.46)
- `builder_0_47.tar.gz` (richiede `rom046.gba` e `base31.gba` accanto a `build47.py`; `python3 build47.py --out out`)
