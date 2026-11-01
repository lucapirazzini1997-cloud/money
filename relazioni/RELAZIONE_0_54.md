# Pokémon Romagna 0.54: correzione del blocco dopo il rivale in laboratorio

Base: ROM 0.53 (SHA-256 `5a5f6434…f142`). La tua 0.44 (`f62af7e2…777a`) non è stata toccata.
Risultato: `Pokemon_Romagna_0_54.gba`, SHA-256 `a06532552a9f79744d889e948d21d713043f29a32847e78d7febae9bbdc92906`.
- Rispetto alla 0.53 cambiano 102 byte.
- La patch BPS 0.53→0.54 (154 byte) è verificata.
- Il builder estratto in una cartella pulita rifà lo stesso SHA.

## Il bug del video
**Cosa succedeva.** In una partita nuova, scegliendo **MUDKIP** (la Poké Ball di destra), dopo la lotta col rivale in laboratorio lo schermo restava nero e non si poteva più fare niente.

**Da quando.** È colpa mia e c'è dalla 0.52, cioè da quando ho aggiunto la schermata "NOME DEL RIVALE?". Nella 0.51 non succede.

**Perché non l'avevo visto.** Nei test della 0.52 e della 0.53 sceglievo sempre la Poké Ball centrale (TORCHIC). Con TORCHIC e TREECKO il problema non si presenta.

**Causa tecnica.**
1. Quando si chiude la schermata del nome, il gioco ricarica la mappa del laboratorio.
2. La Poké Ball che hai preso non viene più creata.
3. Il gioco però tiene a memoria `gSelectedObjectEvent`: punta ancora a lei come "oggetto con cui stai parlando".
4. All'inizio della lotta il gioco fa girare quell'oggetto verso di te ("faceplayer").
5. Con la Poké Ball di destra, quell'oggetto ormai inesistente si porta dietro il numero dello sprite che la telecamera usa per seguirti.
6. Dopo la lotta la telecamera scorre da sola per 20 caselle a destra, fuori dalla stanza.

Il giocatore resta fermo dov'è: si sposta solo la visuale, ed è il "nulla" del video.

**Correzione.**
- Il nome del rivale ora si chiede **prima** che ALDO ti raggiunga. Come nel gioco originale, il riquadro di testo si chiude e lo schermo sfuma al nero prima della schermata.
- Al ritorno, una piccola routine indica ALDO come l'oggetto con cui stai parlando. È quello che si aspetta il resto dello script.
- Se il nome è già stato scelto, la scena è identica a prima.

## Altra correzione
- Nella 0.53 la traduzione aveva modificato per sbaglio 4 byte in due immagini compresse di uno sprite Pokémon, la specie 120 nella tabella del gioco.
- Quei byte sono tornati come nella 0.52.
- Il builder ora esclude esplicitamente quei due punti.

**Salvataggi:** nessun dato del salvataggio cambia. I salvataggi della 0.52 e della 0.53 funzionano.

## Test (onesto)
Ogni prova è una partita nuova dal titolo, senza salvataggio: laboratorio, scelta dello starter, nome del rivale di una sola lettera ("A", come nel video), lotta, dialogo finale. Ho usato due emulatori diversi: **mGBA** e **VBA-M** (core libretro compilato qui). VBA-M è il motore che di solito usano gli emulatori per iPhone.

**Prima della correzione (0.53):**
- **MUDKIP:** la telecamera finisce a (28, 9) in entrambi gli emulatori. È il tuo bug, riprodotto.
- **TORCHIC e TREECKO:** nessun problema.

**Dopo la correzione (0.54):**
- **MUDKIP:** la telecamera resta a (8, 9) durante e dopo la lotta, in mGBA e in VBA-M. ALDO dice "Adesso sei pronto per la PINETA…", poi esco dal laboratorio e sono davanti a RICERCA COSTIERA.
- **TORCHIC (6, 9) e TREECKO (4, 9):** posizione corretta e lotta che parte, in entrambi gli emulatori.

**Fixture dichiarati:** le partite nuove usano il file di salvataggio p51.sav come "cartuccia". Viene sovrascritto dalla nuova partita, che parte dal titolo.

## Non verificato
- Non ho provato il tuo emulatore esatto: ho provato mGBA e VBA-M, e il bug si vedeva in entrambi.
- Se hai salvato mentre eri bloccato nel nero, quel salvataggio non l'ho provato. Il giocatore era fermo a (8, 9) e al caricamento la telecamera viene ricreata, quindi dovrebbe ripartire normale. Altrimenti conviene ricominciare: sei all'inizio.
- Tutto quello che era nella lista "non verificato" della 0.53 resta valido.

## File
- `Pokemon_Romagna_0_54.gba`
- `Pokemon_Romagna_0_53_to_0_54.bps` (da applicare alla 0.53)
- `builder_0_54.tar.gz`: richiede `rom047.gba` e `base31.gba` accanto a `build54.py`. Uso: `python3 build54.py --out out`
