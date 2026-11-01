# Pokémon Romagna 0.51: Mirabilandia e Safari separati, cani leggendari, giostre con i cromatici

Base: ROM 0.50 (SHA-256 `e3461825…5b04`), derivata dalla tua 0.44 (`f62af7e2…777a`), che non è stata toccata.
Risultato: `Pokemon_Romagna_0_51.gba`, SHA-256 `58e13a7bb40eaefb0564dc49d991116eb03a576066377e41dd0501bf8e523859`.
Il builder estratto dal pacchetto (con `rom047.gba` e `base31.gba` accanto) rifà lo stesso SHA. La 0.51 include tutto quello della 0.50.

## Cosa c'è di nuovo

**1. Ingressi prima della Basilica di Classe (punto 30).** Le due frecce accanto alla basilica non ci sono più. Arrivando da sud (Pianura), sulla piazza *prima* della basilica ci sono due varchi di mattoni: a **ovest MIRABILANDIA**, a **est SAFARI**. Sono due aree separate: non c'è più nessun passaggio tra Mirabilandia e il Safari (il vecchio sentiero a est del parco ora è bosco), e niente eventi in comune. Dal parco non si parla più del Safari.

**2. Safari = la Zona Safari di Smeraldo (punto 32).** Le sei aree originali (Sud, Sud-ovest, Nord-ovest, Nord, Nord-est, Sud-est) con la Casa di riposo, identiche a Smeraldo. Sono collegate al varco est di Classe. Ci giri liberamente: niente biglietto, niente Safari Ball e niente passi contati. Le lotte sono normali e catturi con le tue Poké Ball. Gli operai del "cantiere" non ci sono più: Nord-est e Sud-est sono aperte da subito. I dialoghi, che erano rimasti in inglese, ora sono in italiano. Il nome sulla mappa è "SAFARI RAVENNA".

**3. I tre cani, nelle zone più lontane** (stesse flag di cattura di prima: chi li aveva già presi non li ritrova):
- **ENTEI (Lv 45) in una grotta**: la Grotta Ardente, nuova, si apre in cima alla montagna dell'area Nord-est. È il punto più lontano a piedi dall'ingresso. Dentro, un corridoio porta a Entei sulla sua pedana.
- **RAIKOU (Lv 45) in mezzo al prato**: nell'erba alta dell'area Nord-est, il punto di prato più lontano dall'ingresso.
- **SUICUNE (Lv 45) in un lago**: in mezzo al grande lago dell'area Sud-est. Serve Surf.
- Basta parlarci: niente indizi o custodi. Se lo catturi sparisce. Se lo sconfiggi o scappi resta lì e puoi riprovare.
- Alcuni NPC del Safari danno un indizio (grotta calda sulla montagna, tuono sul prato, qualcosa di azzurro nel lago).

**4. Mirabilandia: giostre con i cromatici (punto 31).** Alla fine di ogni giro in trenino compare un Pokémon cromatico legato alla giostra:
- iSpeed: **PONYTA** Lv 30 (flag 0x623)
- Katun: **AIPOM** Lv 30 (flag 0x627)
- Divertical: **MARILL** Lv 30 (flag 0x628)

Ricompare a ogni giro finché non lo catturi. Uso la stessa funzione cromatica della tua ROM (SHUCKLE di Forlimpopoli, Farfetch'd dell'Arco). Corretto anche il nome delle mappe delle giostre, che mostravano "ROUTE 114".

## Test (onesto)
- Emulatore, Classe: dal varco ovest entro a Mirabilandia (43,71) e torno indietro; dal varco est entro nel Safari Sud (32,34) e torno indietro. Tutto OK.
- Emulatore, Safari: dall'ingresso arrivo **a piedi** fino alla grotta in cima alla montagna (cammino calcolato sulle collisioni reali ed eseguito passo passo). Entro nella Grotta Ardente, raggiungo Entei e parte la lotta: ENTEI Lv 45, non cromatico.
- Emulatore: a piedi fino a Raikou nell'erba alta; parte la lotta, RAIKOU Lv 45.
- Emulatore, giostre: alla fine di ciascuno dei tre giri parte la lotta. Dalla RAM il Pokémon nemico è cromatico (PONYTA blu, AIPOM rosa, MARILL verde). Con la flag di cattura già attiva non compare nulla e torno alla stazione giusta.
- Emulatore: l'addetto del Safari parla in italiano. Il vecchio passaggio a est di Mirabilandia è chiuso.
- Emulatore, regressione 0.50: tutti i passaggi N/S ed E/O, i blocchi del Lido (primo Pokémon, 5ª medaglia): OK.
- Grafo: ogni porta raggiungibile a piedi in tutte le mappe; nel Safari sono raggiungibili a piedi le aree Sud, Sud-ovest, Nord-est e Sud-est.

**Fixture dichiarati:** per i test a piedi nel Safari ho azzerato gli incontri selvatici nella copia di prova. Ho usato uno stato con i flag impostati a mano e senza squadra: le lotte iniziano, ma poi finiscono in "sconfitta".

## Non verificato
- **Suicune**: non provato in emulatore perché serve Surf con una squadra vera. Ho controllato solo a grafo che la cella sia raggiungibile surfando. Lo script è lo stesso di Entei e Raikou.
- La cattura vera dei tre cani e dei tre cromatici (e quindi la sparizione e il salvataggio della flag): ho provato solo l'inizio delle lotte.
- Le aree Nord e Nord-ovest restano come in Smeraldo: servono le bici (Bici Corsa/Cross) per arrivarci. Nella tua ROM ho trovato la consegna della Bici Corsa, ma non quella della Bici Cross. I leggendari però non sono lì.
- Il vecchio Safari fatto a mano (mappe 34.115, 35.44, 35.45) resta nella ROM ma non è più raggiungibile.
- Salvataggi vecchi: se avevi salvato dentro il vecchio Safari, ricarica e esci da un'altra parte.

## File
- `Pokemon_Romagna_0_51.gba`
- `Pokemon_Romagna_0_50_to_0_51.bps` (da applicare alla 0.50)
- `builder_0_51.tar.gz` (richiede `rom047.gba` e `base31.gba` accanto a `build51.py`; `python3 build51.py --out out`)
