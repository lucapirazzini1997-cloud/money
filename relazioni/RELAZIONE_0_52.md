# Pokémon Romagna 0.52: correzioni dell'audit (Fase 1)

Base: ROM 0.51 (SHA-256 `58e13a7b…3859`), derivata dalla tua 0.44 (`f62af7e2…777a`), che non è stata toccata.
Risultato: `Pokemon_Romagna_0_52.gba`, SHA-256 `d2412f7c250dd6568dce1a99ad7fc9236e9702ef188557eb269b88b9413aed4b`.
Il builder estratto dal pacchetto, con `rom047.gba` e `base31.gba` accanto, rifà lo stesso SHA. La patch BPS 0.51→0.52 è verificata.

## Cosa cambia

**1. Flag doppie (audit, punti 1–4).**
- Farfetch'd dell'Arco, PONYTA, AIPOM e MARILL delle giostre e le 3 rocce di Cesena hanno ora flag proprie (0x726, 0x727, 0x72b, 0x72c, 0x720, 0x724, 0x725). Regice, Registeel e gli strumenti delle Camere tengono le loro.
- Il builder ora rifiuta qualsiasi flag già usata da un evento della ROM e controlla le collisioni a fine build.
- *Vecchi salvataggi:* chi aveva già preso Farfetch'd o AIPOM nella 0.49/0.51 li ritrova una volta. Chi li aveva presi aveva anche nascosto per errore Regice o Registeel, e quelli restano nascosti finché non li catturi: la flag è la loro.

**2. Dialoghi e nomi di zona in italiano.**
- Tradotti i 61 testi rimasti in inglese: Centro Pokémon e Club Cavo della Lega, alberi di bacche, pensione, sale del Club.
- Nomi di zona: la pensione ora è in "COSTA ADRIATICA", le isole sono "ISOLA MIRAGGIO" e "ISOLA OMBELICO", la zona senza nome è "CLUB CAVO".
- Nelle mappe raggiungibili restano 0 dialoghi in inglese. L'interfaccia (lotta, menu, zaino) arriva con la 0.53.

**3. Oggetti mancanti e pesca.**
- **BICI CROSS**: un secondo NPC nel negozio di bici di Cesenatico, accanto a chi regala la Bici da Corsa.
- **AMO BUONO**: un pescatore sul porto canale di Rimini.
- **SUPER AMO**: un pescatore a Ravenna, che lo dà dopo la 5ª medaglia.
- **MN CASCATA**: la dà l'addetto del Safari dopo l'8ª medaglia, per la cascata dell'area Sud-est.
- **Pesca:** prima si pescava solo nel Safari, quindi anche l'Amo Vecchio era inutile. Ora si pesca in 25 mappe:
  - mare: Magikarp, Tentacool, Horsea, Krabby, Wailmer, Tentacruel, Staryu, Corsola, Chinchou;
  - fiumi, canali e laghi: Magikarp, Goldeen, Barboach, Corphish, Seaking, Whiscash, Poliwhirl, Gyarados raro;
  - livelli per area: Amo Vecchio 5–10, Amo Buono 15–35, Super Amo 30–48.
- La MN Flash non l'ho messa: non c'è nessuna grotta buia in cui serva.

**4. Maestra delle mosse e Cancellamosse** a Cervia, nella locanda (34.5). Sono gratis: niente Squama Cuore. La prima fa ricordare le mosse, il secondo le fa dimenticare, MN comprese.

**5. Lugo dopo Ravenna.** Il casello tra Ravenna e Via dei Canali (35.98) lascia passare solo dopo l'ultima tappa della missione contro il Team Emilia a Ravenna (flag 0x2ac).

**6. Rivale a Forlì.** Prima della lotta ALDO cura la tua squadra: "Aspetta, la tua squadra è stanca…".

**7. Saline di Cervia.** Selvatici portati da Lv 5–15 a Lv 5–10: in emulatore ho visto incontri Lv 5–8.

**8. Rivale rinominabile.**
- In laboratorio, dopo la scelta dello starter, si apre la schermata "NOME DEL RIVALE?".
- Il nome scelto compare in tutti i dialoghi (40 testi aggiornati) e in lotta ("ALLENATORE … would like to battle!").
- Se il nome non è mai stato scelto, come nei salvataggi vecchi, resta "ALDO".
- Tecnica: il nome sta nelle variabili 0x40FC–0x40FF, che nessuno script usa. Il segnaposto {RIVALE} del gioco ora le legge.

## Test (onesto)
- **Rivale:** in emulatore, nuova partita dal titolo. Dopo lo starter si apre la schermata con il titolo, scrivo "GNNO". Il rivale parla come "GNNO" e in lotta compare "PKMN TRAINER GNNO". Da un salvataggio vecchio a Forlì il rivale si chiama ancora "ALDO".
- **Lugo:** con 5 medaglie e senza missione a Ravenna, entrando nel casello compare "Il passaggio verso LUGO è chiuso…" e torno indietro. Ho giocato la missione di Ravenna (7 tappe, 2 lotte), il blocco si apre e arrivo in Via dei Canali.
- **Oggetti:** in emulatore ho ricevuto Super Amo (Ravenna), Amo Buono (Rimini), Amo Vecchio (Cesenatico) e Bici Cross: compaiono negli strumenti chiave. MN Cascata nel Safari: ricevuta, ma con la flag dell'8ª medaglia attivata a mano (fixture).
- **Pesca reale:**
  - Cesenatico (mare): Amo Vecchio TENTACOOL Lv 9 e MAGIKARP Lv 5; Amo Buono TENTACOOL Lv 15–24; Super Amo STARYU Lv 38 e WAILMER Lv 31;
  - Cesena (fiume): MAGIKARP Lv 7, CORPHISH Lv 15, GOLDEEN Lv 22, WHISCASH Lv 33;
  - Via dei Canali: SEAKING Lv 36–37 col Super Amo.
- **Maestra delle mosse:** BRELOOM mostra le mosse da ricordare (Absorb, Tackle, Stun Spore, Mega Drain, Headbutt, Mach Punch…) e si arriva alla scelta della mossa da sostituire. **Cancellamosse:** chiede "BRELOOM deve dimenticare ROCK SMASH?". Ho risposto No, quindi non ho provato fino in fondo la cancellazione.
- **Forlì:** arrivo con la squadra a 68/90, il rivale dice la frase nuova e la lotta parte a 90/90.
- **Saline:** 8 incontri tra Lv 5 e 8.
- **Flag:** riesaminate tutte le mappe raggiungibili. Le 5 flag in conflitto non sono più condivise; le 28 condivise rimaste sono volute (rivale, sistema, eventi a più mappe).
- **Testi:** riesaminati 2295 testi, 0 in inglese.

**Fixture dichiarati:**
- per riprendere da dove ero arrivato ho caricato i savestate della partita 0.51 nella ROM 0.52;
- la flag dell'8ª medaglia l'ho attivata a mano, solo per il test della MN Cascata.

## Non verificato
- Le catture vere dei Pokémon pescati: ho solo fatto partire le lotte.
- La cancellazione completa di una mossa (ho risposto No).
- I testi tradotti del Centro e del Club Cavo della Lega: li ho controllati solo nella ROM, non in emulatore, perché la Lega non l'ho raggiunta.
- Il salvataggio dal menu del gioco con un nome del rivale scelto.

## File
- `Pokemon_Romagna_0_52.gba`
- `Pokemon_Romagna_0_51_to_0_52.bps` (da applicare alla 0.51)
- `builder_0_52.tar.gz` (richiede `rom047.gba` e `base31.gba` accanto a `build52.py`; `python3 build52.py --out out`)
