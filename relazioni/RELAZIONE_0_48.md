# Pokémon Romagna 0.48: case ai cambi di luogo, campagne piene, bacche

Base: ROM 0.47 (SHA-256 `d26c0fd4…0122d`). La tua 0.44 non è stata toccata.
Risultato: `Pokemon_Romagna_0_48.gba`, SHA-256 `2246619d46cd206623b353e0e17470cee56d0f7b94ef2d1bb51449ac597978b0`.
`.bps` 0.47→0.48 generato (CRC dentro al file). Il builder estratto dal pacchetto, con `rom047.gba` e `base31.gba` accanto, rifà lo stesso SHA.
Dimensione ROM invariata (32 MB); le mappe nuove sono in aree libere.

## Cosa c'è di nuovo

**1. Casette a ogni cambio di luogo (punto 4).** Le 21 transizioni (T1–T21) non sono più warp nudi: ogni lato ha una casetta con insegna e una stanza interna con porta a est e a ovest, come quella Cervia–saline. Testo di cartello e del casellante per ognuna.

**2. Campagne più piene (punti 5, 6, 19, 21, 24).** Muri di alberi con varchi, allenatori che vedono il giocatore al varco (obbligatori), erba alta, sentieri:
- Cervia–Cesena (34.21): DANTE, VALERIA, ORESTE
- 34.20: MAURO, ROSANNA, GIORGIO
- Cesena–Cesenatico (34.43): GIANNI, CATERINA, BRUNO
- Riviera Cesenatico–Rimini (34.39): MARISA, ELVIO, ROMEO
- Via Emilia ovest (35.60): ARISTIDE, LAURA
- Monte Spaccato/Capocolle (34.19): FANTINO, SCUDERIA (facoltativi) e rocce da spaccare con Spaccaroccia ai due lati della casetta ovest
- Forlì–Faenza (34.84): mappa allungata di 40 righe (ora 56×72), fiume lungo, sentiero lastricato sulla sponda ovest con 3 allenatori obbligati (TOMMASO, FILIPPA, GENNARO), sentiero est facoltativo con LORIS e NADIA, erba alta, alberi.

**3. Terreni per bacche (punto 28).** 26 terreni (alberi di bacche vanilla a stadio vuoto) in 34.20, 34.43, 34.39, 34.19, 35.60, 34.84. Usati id 90–115 circa; restano pochi id liberi (il limite è 127).

## Test (onesto)

- Costruzione: ricostruita da zero dal pacchetto, SHA identico.
- Emulatore: tutte le 21 casette, entrambe le direzioni (interno → uscita → rientro) **OK**, sulla ROM finale.
- Controllo a grafo (non in emulatore): in ogni campagna il percorso tra le due casette passa per forza accanto ai trainer; 34.84 controllato dalla sponda ovest senza Surf.
- Render visivo controllato di 34.84 e delle campagne.

## Non verificato

- Nessuno scontro con i nuovi allenatori giocato in emulatore (solo grafo).
- Rocce di 34.19 e terreni bacche mai toccati in emulatore.
- Livelli e squadre dei nuovi allenatori scelti a occhio (≈10–33 secondo la zona), non bilanciati.
- Il cartello della scuola di canoa a 34.84 è stato tolto con l'allungamento e non è ancora rimesso.
- Salvataggi: chi era salvato su vecchie celle dei passaggi potrebbe ritrovarsi dentro l'ingombro di una casetta. Non provato con un salvataggio vero.
- La sponda ovest di 34.84 si raggiunge solo con Surf dalla est.

## Fixture dichiarate

Per i test: flag 0x12, 0x13, 32 e 1800 impostate; stato di partenza `st_free.ss`.

## Ancora da fare (non in 0.48)

Rinomina del rivale, ricostruzione di Rimini/Cesena/Forlì/Faenza, fabbrica Babbi, shiny (Smeargle, Farfetch'd, Mirabilandia, Lugo), Safari e Mirabilandia separati, riduzione di Lugo, Rocca Estense, grotta Lugo–Faenza con i tre regi, collegamento Faenza–Imola dopo la sesta medaglia.
