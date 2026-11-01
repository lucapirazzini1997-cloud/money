# Pokémon Romagna 0.45 (passo A): correzioni sulla 0.44

Base: `Pokemon_Romagna_0_44.gba` dell'utente, SHA-256 `f62af7e2…777a`.
Risultato: `Pokemon_Romagna_0_45.gba`, SHA-256 `d23a091c0e0f3dd99b8971b1039871701c86ff8a037ebcfb50468e0ab5cc080e`.
549 byte cambiati. Il file `.bps` applicato alla 0.44 riproduce esattamente la 0.45 (controllato).
Solo dati di mappa e script: i salvataggi della 0.44 restano validi.

## Cosa è stato corretto (punti della tua lista)

| Punto | Causa trovata | Correzione |
|---|---|---|
| 20 Rocca di Forlimpopoli, cartello nel vuoto | 8 cartelli (5 a Forlimpopoli, 3 a Capocolle) avevano l'indirizzo dello script senza la base ROM (`0x01E92B3C` invece di `0x081E92B3C`) | Aggiunta la base ai 8 indirizzi |
| 29 Acqua camminabile | 432 celle di acqua nella pineta (34.93), 28 a Cesenatico, 27 a Rimini e 1 a Cesena avevano quota 3 (terra) | Quota 1 come le altre acque. Senza Surf si ferma al bordo |
| 9 Rivale: bloccato a Rimini | Il rimando "Prima conquista la Medaglia Collina" portava a (28,74), cioè oltre il varco, accanto all'uscita per Rimini. La riscrittura era un effetto collaterale di `seam_updates` in build32 | Rimando a (23,50), a nord del varco |
| 17 (solo la parte "non se ne vanno") Befane | I tre tecnici/ingegnere del Team Emilia restavano dopo la sconfitta | Si nascondono con la flag di avanzamento (0x27D/0x27E/0x27F) e vengono rimossi subito dopo la lotta |

## Collaudo (mGBA 0.10.x compilato qui, tasti reali)

Per arrivare ai punti di prova ho usato una copia di prova della ROM con l'uscita del Bar Panama
reindirizzata alla mappa da collaudare (fixture dichiarata). Prova sulla 0.44 e sulla 0.45 con gli stessi comandi.

- Cartello Rocca: 0.44 mostra il titolo senza testo; 0.45 mostra "La fortezza domina la piazza". Cartello di Capocolle (1 su 3) corretto.
- Rivale: 0.44 porta a (28,74); 0.45 porta a (23,50).
- Acqua pineta: in 0.44 si cammina fino a y=23 nel lago; in 0.45 ci si ferma a y=29.
- Befane (piano 3): nella copia di prova la lotta è stata saltata e si è eseguita direttamente la continuazione dello script. Il tecnico sparisce e resta assente dopo uscita e rientro nel piano. Gli altri due piani usano lo stesso schema ma non sono stati provati.

## Non verificato

- Le altre 2 insegne di Capocolle e 4 di Forlimpopoli (stesso difetto, stessa correzione).
- Befane piani 4 e 5; la lotta vera contro i tecnici.
- Superficie dell'acqua a Rimini e Cesenatico: il ritorno a quota 1 è coerente con la pineta, ma non l'ho provato a piedi.
- Volo a Forlimpopoli: NON risolto. Nella tabella del Volo esistono solo i 16 settori nativi; serve riutilizzare uno slot libero (5, 12, 13 o 14) con cella sulla mappa, destinazione e nome.

## Rimandato alle versioni seguenti

Punti 27, 33, 36 (Lugo da campagna dopo il Team Emilia, Imola solo da Faenza dopo la 6ª medaglia, cava con i tre Regi),
Volo di Forlimpopoli, oggetti consegnabili dell'evento Befane e tutti i rifacimenti grafici e gli eventi nuovi.
