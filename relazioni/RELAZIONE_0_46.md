# Pokémon Romagna 0.46: progressione Ravenna → Lugo → Faenza, Cava dei Tre Sigilli

Base: ROM 0.45 (SHA-256 `d23a091c…c080e`), derivata dalla tua 0.44 (`f62af7e2…777a`). La 0.44 originale non è stata toccata.
Risultato: `Pokemon_Romagna_0_46.gba`, SHA-256 `4078342ecbbd4e3a0e7baa9183f88f77496f0d1e1b16de1d53a706c19c0f466b`.
`.bps` 0.45→0.46 controllato: applicato alla 0.45 dà esattamente la 0.46. Il builder rifatto da zero dà lo stesso SHA (due volte).
Salvataggi della 0.45 e 0.44: solo mappe/script/tabelle nuove, nessuna flag nativa riusata (vedi sotto). Dovrebbero restare validi, ma non ho provato a caricare un salvataggio reale.

## Cosa c'è di nuovo

**Ravenna → Lugo a piedi.** Il varco ovest di Ravenna (riga 35) è chiuso da un vigile finché non finisci la missione Team Emilia (flag 0x2AB). La porta della stazione di Ravenna non porta più a Lugo: ha un cartello. Percorso: Via dei Canali (35.70, ponte sul canale, 3 allenatori, 3 oggetti, Franco che dà 5 Mega Ball) → Campagne di Lugo (35.71, 3 allenatori, 2 oggetti, guardaboschi con 3 Superrepellenti, mugnaio con indizio) → Lugo. Erba alta con tabelle d'incontro vere (Liv 30–33).
Anche la stazione di Lugo porta ora alle Campagne a piedi.

**Cava dei Tre Sigilli** (7 mappe nuove, 35.72–35.78). Lugo ovest e Faenza nord portano al Colle della Cava; un custode (vigile) chiude l'ingresso su entrambi i lati finché non hai la 6ª medaglia (flag 0x86C), poi resta aperta per sempre. Galleria centrale lunga con 4 allenatori, 4 oggetti, un eremita, cartelli, incontri in grotta (Liv 33–37). Scala verso la Sala dei Sigilli con 3 porte-simbolo. Tre camere separate, ognuna con ritorno alla sala:
- Camera di Pietra: Regirock Liv 40
- Camera di Brina: Regice Liv 42
- Camera di Metallo: Registeel Liv 45
Sprite visibili, flag indipendenti, non cromatici. Si può attraversare la cava senza catturarli.

**Faenza → Imola.** Faenza ha ora uscita nord (cava, sempre aperta dopo la 6ª medaglia) e uscita ovest verso il ponte del Santerno (35.0), con vigile che blocca fino alla medaglia 0x86C. Il ponte porta a Imola a ovest; il lato est ora ritorna a Faenza, non più a Lugo. Il varco Lugo→Imola è stato sostituito dalla cava.

Nuovi nomi d'area: indici 90–96 (Via dei Canali, Campagne di Lugo, Colle della Cava, Cava dei Sigilli, Camera di Pietra/Brina/Metallo).

## Risorse usate (per evitare conflitti)
Allenatori nuovi: id 101–104, 110–113, 117, 120–123, 132 (mai citati da nessuno script della 0.45; flag di sconfitta 0x500+id). Flag di oggetti/doni/Regi: 21+ flag prese da `0x500+id` di id liberi ≥ 160 (`0x5fb…`), tutte < 0x860. Wild: tabella incontri rilocata, 13 riferimenti aggiornati.

## Collaudo (mGBA con tasti reali; fixture dichiarate)
Fixture: copia di prova con l'uscita del Bar Panama reindirizzata, incontri casuali azzerati nelle mappe nuove, flag di prova impostate (0x86C e gli allenatori già battuti), e negli script dei Regi un Tyranitar Liv 60 + 5 Master Ball dati all'inizio. Niente di tutto questo è nella ROM consegnata.

Verificato:
- Ravenna: senza 0x2AB il vigile ferma al varco ovest con dialogo; con 0x2AB si passa.
- Ravenna → Via dei Canali → Campagne → Lugo (37,59): allenatori ti sfidano a vista, il ponte si attraversa.
- Lugo ovest → Colle della Cava: il custode parla all'ingresso (senza 0x86C).
- Con 0x86C: Lugo → Colle → Galleria → scala → Sala → Camera di Brina, Pietra e Metallo: sprite del Regi visibile, testo d'ingresso, lotta selvatica parte (Regice 42, Regirock, Registeel).
- Regice: dopo fuga resta al suo posto; dopo KO resta e si può riaffrontare.
- Pietra e Metallo: fuga, il Regi resta al suo posto.
- Percorso inverso: Galleria ovest → Colle (Faenza) → Faenza (50,0), poi Faenza (0,29) → Ponte del Santerno (29,8) con vigile nascosto da 0x86C.

NON verificato (dillo se vuoi che lo faccia nella prossima passata):
- **Cattura dei Regi e flag di nascondimento dopo la cattura**: usa lo schema nativo (flag e rimozione solo se catturato, specialvar = 7), ma il test via menu era instabile e non l'ho chiuso. Persistenza dopo salvataggio non provata.
- KO/cattura per Regirock e Registeel (provata solo la fuga); persistenza dopo salvataggio per tutti.
- Vigile di Faenza (ovest) senza 0x86C: stesso schema di Ravenna, non provato a mano.
- Vigili del Colle: provato il lato Lugo; lato Faenza non provato con la flag spenta.
- Le lotte vere con i 14 allenatori nuovi (nei test erano già battuti); scambio di oggetti/regali (Franco, guardaboschi); trovare gli oggetti. Gli ID degli oggetti (Mega Ball 3, Pozione 22, Iperpozione 21, Revive 24, Guaritutto 23, Elisir 36, Superrepellente 83) li ho assunti dalla tabella di pokeemerald: controlla i nomi in gioco.
- Incontri nell'erba delle mappe nuove (rate azzerato nei test). In una prova la grotta ha dato un Graveler, quindi le tabelle funzionano.
- Ravenna e Faenza sono state ri-disegnate (tileset secondario a 512 tile, quantizzato): ho visto solo gli scorci dei test, non il confronto completo con la 0.45.
- Le vecchie porte delle mappe toccate (34.96 warp 15 ecc.) non ricontrollate una per una.

## Ancora da fare (fasi seguenti)
0.47: Volo Forlimpopoli, oggetti Befane, nome rivale, tutor mosse. 0.48: case con warp, campagna, terra bacche. 0.49+: città, cromatici, Safari/Mirabilandia, Lugo ridotta, Rocca Estense.

## File
- `Pokemon_Romagna_0_46.gba`
- `Pokemon_Romagna_0_45_to_0_46.bps` (da applicare alla 0.45)
- `builder_0_46.tar.gz` (richiede `rom045.gba` e `base31.gba` accanto a `build46.py`; `python3 build46.py --out out`)
