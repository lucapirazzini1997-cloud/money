# Pokémon Romagna 0.49: acqua non camminabile, ponti veri, Arco di Augusto, Centri Pokémon originali

Base: ROM 0.48 (SHA-256 `2246619d…78b0`), derivata dalla tua 0.44 (`f62af7e2…777a`), che non è stata toccata.
Risultato: `Pokemon_Romagna_0_49.gba`, SHA-256 `cefab56d0f5ff0641f1c2a22c6af5c70d1ea42029a11aea6b116562df1d8afcc`.
138 797 byte diversi dalla 0.48. Il builder estratto dal pacchetto (con `rom047.gba` e `base31.gba` accanto) rifà lo stesso SHA. La 0.49 include tutto quello della 0.48.

## Cosa c'è di nuovo

**1. Acqua camminabile (punto 29 della tua lista).** Causa trovata: nelle mappe ridisegnate a "arte" l'acqua perdeva la quota (elevazione 1 di Smeraldo, che la rende invalicabile a piedi) e restava a quota 3, quindi ci si camminava sopra. Riguardava Lido di Savio–Pianura (34.93), il fiume Forlì–Faenza (34.84) e altre mappe già rifatte. Ora l'acqua navigabile esce sempre a quota 1. Scansione di tutte le mappe del gioco: zero celle d'acqua camminabili nelle mappe della hack (restano solo alcune celle nelle mappe originali di Hoenn, che non uso).

**2. Ponti veri.** Con l'acqua chiusa, tre passaggi della storia restavano tagliati: il canale di Lido di Savio verso la casetta Pianura (0.9), il fiume della campagna di Pianura (34.93, ponte lungo 12 celle) e il fiume Forlì–Faenza (34.84). Ho messo un ponte in legno in ognuno. Controllo a grafo su tutte le mappe: ogni porta/casetta è raggiungibile a piedi dalle altre.

**3. Arco di Augusto (Rimini).** Camminando sotto l'arcata ti piomba addosso un FARFETCH'D cromatico Lv 26. Ripetibile finché non lo catturi (flag 0x622). Riuso la funzione nativa cromatica già presente nella tua ROM (la stessa dello SHUCKLE di Forlimpopoli).

**4. Centri Pokémon originali (punto 14).** Le 11 mappe dei Centri (1F) usavano un layout con pavimento modificato; ora puntano di nuovo al layout di Smeraldo.

**5. Casa delle Aie (punto 7).** Targa chiara con testo scuro, leggibile (prima beige su marrone, minuscolo).

**6. Rimini (punto 16).** Il lampione e un riquadro di selciato che "bucavano" il tetto di una casa sono spariti: tetto e finestra ripristinati.

## Cose della tua lista che sono già fatte nelle versioni precedenti
Il punto 33 (Lugo a piedi da una campagna dopo il Team Emilia a Ravenna), il 27 e 36 (Faenza → Imola solo dopo la 6ª medaglia, e la Cava dei Tre Sigilli tra Lugo e Faenza con le tre stanze dei Regi) sono nella 0.46. La tua lista era stata scritta sulla 0.44. Il 20 (Forlimpopoli) e il Volo sono nella 0.47.

## Test (onesto)

- Emulatore: tutte le 21 casette in entrambe le direzioni **OK** sulla ROM finale.
- Emulatore, acqua e ponte: dalla casetta nord di 34.93 si scende sul ponte (19,24); a sinistra e oltre il bordo destro del ponte il movimento è bloccato.
- Emulatore, Arco: sotto l'arco parte il FARFETCH'D selvatico Lv 26. Dalla RAM il mostro nemico risulta cromatico rispetto al tuo ID allenatore (formula TID^SID^PID).
- Emulatore, trainer: sul riviera (34.43) il primo allenatore ti ferma e parte lo scontro. Nella 0.48 gli allenatori nuovi erano controllati solo a grafo; questa è la prima prova in emulatore.
- Emulatore, Rimini: senza medaglia 0x868 il rivale ti rimanda indietro e il giocatore si muove; con la medaglia parte lo scontro.
- Emulatore, Centri: da dentro si esce correttamente a Forlì, Forlimpopoli e al Centro del gruppo 2.
- Grafi: scansione dell'acqua (zero celle camminabili) e componenti delle mappe, tutte coerenti.
- Confronto visivo prima/dopo per le mappe toccate: cambiano solo le celle previste; c'è un po' di rumore di quantizzazione dei tile nelle mappe ri-emesse (insegne e dettagli minuscoli).

## Non verificato

- **Il bug del rivale a Rimini (punto 9)**: non sono riuscito a riprodurlo sulla 0.48/0.49. Il controllo funziona e non ci sono scorciatoie a piedi attorno al varco; l'ipotesi più probabile è che nella 0.44 si aggirasse camminando sull'acqua (ora chiusa). Se ti ricapita, dimmi mappa e cella.
- La cattura vera del Farfetch'd e il salvataggio del flag 0x622 (ho provato solo l'inizio dello scontro).
- Scontri completi con i nuovi allenatori delle campagne (verificato solo l'inizio con GIANNI), rocce di Capocolle e terreni per le bacche (mai toccati in emulatore).
- Il fatto che i Centri sembrino identici agli originali: guardato solo con screenshot di tre Centri.
- Salvataggi reali non provati. Una nuova flag (0x622) e il layout dei Centri; le coordinate del giocatore salvate sull'acqua o sulle vecchie celle potrebbero finire in un punto non valido.

## Ancora da fare
Rivale rinominabile, ricostruzione di Cesena (fontana Masini, Rocca, chiesa, biblioteca, Smeargle cromatico del pittore), Cesenatico (grattacielo), Rimini (porto, barche, eventi), Forlì (Piazza Saffi, Rocca di Ravaldino), Faenza (eventi del Team Emilia, piazza), fabbrica Babbi, Safari/Mirabilandia separati con eventi cromatici, Lugo ridotta e Rocca Estense.

## File
- `Pokemon_Romagna_0_49.gba`
- `Pokemon_Romagna_0_48_to_0_49.bps` (da applicare alla 0.48)
- `builder_0_49.tar.gz` (richiede `rom047.gba` e `base31.gba` accanto a `build49.py`; `python3 build49.py --out out`)
