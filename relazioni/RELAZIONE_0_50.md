# Pokémon Romagna 0.50: passaggi allineati alla direzione di marcia, blocchi del Lido

Base: ROM 0.49 (SHA-256 `cefab56d…8afcc`), derivata dalla tua 0.44 (`f62af7e2…777a`), che non è stata toccata.
Risultato: `Pokemon_Romagna_0_50.gba`, SHA-256 `e346182555162637e65f0998295d3922bda5955ce5ccc95c0b453cb0c26b5b04`.
Il builder estratto dal pacchetto (con `rom047.gba` e `base31.gba` accanto) rifà lo stesso SHA. La 0.50 include tutto quello della 0.49.

## Cosa c'è di nuovo

**1. Passaggi N/S in linea con l'ingresso.** Prima ogni uscita a sud era una casetta con la porta rivolta a sud: per andare a sud dovevi girarle intorno e entrare camminando verso nord. Ora:
- **Uscita a sud** = un portale di mattoni sul bordo basso della mappa (tetto con cartello col nome del luogo, pilastri ai lati, passaggio in ombra). Ci entri camminando verso sud e l'ultima cella ti porta dentro.
- **Uscita a nord** = la casetta come in Pineta (porta in basso, ci entri camminando verso nord), invariata.
- **Stanza interna** nuova e verticale (8x9): si entra dal portale da nord e si esce a sud (stuoia) nella casetta dell'altra mappa, e viceversa. C'è il casellante col suo banco e due cartelli coi nomi dei luoghi.
- Esempio richiesto: Lido di Savio → Pineta = verso sud; Pineta → Lido = verso nord.
- Riguarda i 10 passaggi N/S (T1–T8, T11, T12). I 10 passaggi E/O non sono cambiati. T13 (Monte Spaccato → Cesena, unico passaggio misto E/O con S) ha il portale a sud e la stanza orizzontale di prima.

**2. Primo Pokémon obbligatorio su tutte le uscite del Lido.** Il bug era la strada costiera (T5): non aveva il controllo, e da lì si arrivava a Cervia e alla Pineta da sud. Ora c'è un controllo davanti a entrambi i portali sud del Lido (Pineta e Costiera) e davanti al ponte nord. Se non hai il primo Pokémon: messaggio e vieni riportato indietro.

**3. Strada nord chiusa fino alla 5ª medaglia.** Davanti al ponte del Lido (0.9, cella y=7): senza primo Pokémon il messaggio del laboratorio; con primo Pokémon ma senza la 5ª medaglia (flag 0x86b) "Il passaggio verso Ravenna è chiuso. Serve la quinta medaglia per passare."; con la medaglia si passa. L'unica strada verso Pianura/Ravenna passa da lì (i controlli di raggiungibilità non mostrano altre vie dal Lido).

## Test (onesto)
- Emulatore, 10 passaggi N/S: dalla stanza esco nel portale giusto, risalgo fuori, ridiscendo e rientro nella stanza, poi esco a sud nella casetta dell'altra mappa: **tutti OK**.
- Emulatore, T13: uscita nel portale (18,33), risalgo, rientro nella stanza: OK.
- Emulatore, passaggi E/O (T9, T10, T14–T21): invariati e **OK** nei due versi.
- Emulatore, Lido senza primo Pokémon (flag 32 spenta): ai due portali sud compare il messaggio e il giocatore viene riportato su (19..21→y=38); con il flag acceso si entra nella stanza.
- Emulatore, ponte nord: senza 5ª medaglia messaggio e ritorno a y=9; con la 5ª medaglia attraverso il ponte ed entro nella casetta Pianura (34.93 arrivo (18,43)).
- Grafo: ogni porta e casetta raggiungibile a piedi (zero componenti isolate).
- Screenshot dei portali a Lido, Cervia, Pineta, Pianura, Cesena e altri: nessun errore visivo evidente.

## Non verificato
- Prova con una partita reale dall'inizio (ho usato stati di test con i flag impostati a mano).
- La direzione in cui si guarda appena usciti dal portale (cammino sempre verso nord, ma non ho controllato lo sprite uscendo).
- Salvataggi vecchi: se salvi dentro una vecchia casetta sud (0.49) e carichi la 0.50, la stanza ha dimensioni diverse: **ricomincia da un punto fuori dai caselli**.
- Il cartello di direzione già presente sopra il portale di Lido (PINETA/CERVIA) si sovrappone un po' al bordo del tetto: estetico, non sistemato.
- Non è stato toccato il resto (rivale, Cesena, ecc.).

## Safari e Mirabilandia: NON fatti in questa versione
Hai ragione, sono ancora quelli di prima. È un lavoro grosso (aree separate, ingressi prima della Basilica di Classe, Safari libero senza limite palle, Entei/Raikou/Suicune in prato/grotta/lago, eventi cromatici nelle attrazioni): lo faccio nella 0.51 in modo dedicato, senza mischiarlo ai passaggi.

## File
- `Pokemon_Romagna_0_50.gba`
- `Pokemon_Romagna_0_49_to_0_50.bps` (da applicare alla 0.49)
- `builder_0_50.tar.gz` (richiede `rom047.gba` e `base31.gba` accanto a `build50.py`; `python3 build50.py --out out`)
