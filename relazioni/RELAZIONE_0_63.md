# Pokémon Romagna 0.63: Cesena ovest, Ippodromo e Monte Spaccato (Lotto 3)

**Base:** 0.62, SHA-256 `b8ebd0918981becb7c3d77c649d78bf92e7a29d5ec8eec14def17dd772ac9080`.

**Risultato:** `Pokemon_Romagna_0_63.gba`, SHA-256 `d1fee9f903b1fb6dbc0b9568697b469080f3d356dedc63a9bbf9326b0c876187`.
- Patch BPS 0.62→0.63: `rom/Pokemon_Romagna_0_62_to_0_63.bps` (1862 byte), verificata riapplicandola.
- Modulo: `versioni/v063_cesena_ovest.py`. La build da zero rifà tutti gli SHA; lo zip senza `out/` ricostruito in una cartella pulita rifà lo stesso SHA.
- Lo SHA è in `build.py` dopo il collaudo (§5).
- **Salvataggi compatibili:** nessuna struttura nuova nel salvataggio; una sola flag nuova (0x22, a 0 nei vecchi salvataggi). Un salvataggio vero della 0.62 fatto dentro Monte Spaccato carica nella 0.63 e prosegue, in mGBA e VBA-M (§5).

## 1. Cosa chiedeva il prompt

Lotto 3, "Ippodromo e Monte Spaccato":
- l'Ippodromo è una tappa del percorso fra Cesena e Monte Spaccato, visitabile già alla prima visita di Cesena;
- il tratto da Monte Spaccato verso Capocolle e Forlimpopoli è chiuso solo da rocce fisiche da rompere con SPACCAROCCIA, non da un blocco di sistema;
- il controllo della 3ª medaglia (0x869) nel casello ovest di Cesena (35.91) va tolto;
- il blocco non si deve poter aggirare e chi l'ha già superato non deve restare chiuso fuori.

## 2. Com'era nella 0.62 (letto e riprodotto)

- Cesena 34.17 → casello 35.91 → Monte Spaccato 35.101 → casello 35.92 → Capocolle 35.60.
- Nel casello 35.91 quattro eventi a coordinate (3,2–5) controllavano 0x869: senza la 3ª medaglia "Prima conquista la terza medaglia a RIMINI…" e ritorno a Cesena. **Riprodotto a tasti** sulla 0.62 (mGBA, da `s_ce3.ss`, 1 medaglia): il giocatore resta in 35.91 con quel testo (`t63_riproduci.json`).
- L'Ippodromo 34.19 era una deviazione: ci si entrava da una casetta di Monte Spaccato (54,36), e anche il suo cancello ovest (3,17) riportava a Monte Spaccato. Davanti al cancello ovest c'erano tre rocce (oggetti 5–7, flag 0x720/0x724/0x725), resto di un vecchio progetto: chiudevano l'uscita verso Monte Spaccato, non la strada per Capocolle.
- A Monte Spaccato non c'era nessun ostacolo fisico verso ovest: oltre al sentiero nella collina, i prati a nord e a sud giravano attorno. **Riprodotto a tasti** sulla 0.62 (mGBA): con 6 medaglie, partendo da Monte Spaccato, si arriva a 35.92 senza SPACCAROCCIA (`t63_riproduci.json`; fixture: posizione).
- La MN SPACCAROCCIA la dà ADA (Rimini 34.48) dopo la missione delle Befane; AURELIO dà la 3ª medaglia dopo la stessa missione, ma **senza** chiedere la MN. Quindi un giocatore poteva avere la 3ª medaglia, essere passato dal vecchio casello e non avere la MN: per lui delle rocce sul ritorno sarebbero un muro.

## 3. Modifiche (versioni/v063_cesena_ovest.py)

1. **Casello 35.91:** tolti i quattro eventi a coordinate (lo script vecchio resta nella ROM, non è più chiamato). Nuovo testo del casellante: "A est c'è CESENA. A ovest l'IPPODROMO DEL SAVIO e poi MONTE SPACCATO, verso CAPOCOLLE e FORLIMPOPOLI."
2. **Uscite**, in modo che l'Ippodromo stia sul percorso:
   - casello 35.91, uscita ovest → Ippodromo, cancello sud (34.19 uscita 0);
   - Ippodromo, cancello sud (uscite 0, 3, 4, 5) → casello 35.91;
   - Ippodromo, cancello ovest (uscite 1, 2) → Monte Spaccato, casetta "IPPODROMO" (54,36);
   - Monte Spaccato, casetta "IPPODROMO" (54,36) e casetta "CESENA" (58,20) → Ippodromo, cancello ovest. Le due casette di Monte Spaccato portano tutte e due all'Ippodromo (prima la casetta "CESENA" portava al casello); dall'Ippodromo si torna sempre dalla casetta "IPPODROMO".
3. **Ippodromo:** le tre rocce del cancello ovest non compaiono più (uno script d'ingresso, tipo 3, alza 0x720/0x724/0x725, usate solo da quelle rocce).
4. **Monte Spaccato:**
   - tre rocce nella tagliata, a (14,16), (14,17), (14,18), con lo script delle rocce di Smeraldo (serve SPACCAROCCIA e la 3ª medaglia, altrimenti "Serve SPACCAROCCIA e la terza medaglia per rompere la roccia.") e flag temporanee 0x11–0x13: come in Smeraldo, una roccia rotta ricompare quando si rientra nella mappa;
   - quattro alberi (x 11–12, righe 2–5 e 34–37) chiudono i prati a nord e a sud della collina: a ovest si passa solo dalla tagliata;
   - nuovo testo del cartello all'ingresso est: "A ovest CAPOCOLLE, poi FORLIMPOPOLI. A est c'è l'IPPODROMO, poi CESENA."
5. **Chi è già passato non resta chiuso fuori:** entrando nel casello 35.92 (ovest delle rocce) si alza la flag nuova **0x22** ("passaggio aperto"); uno script d'ingresso di Monte Spaccato, con 0x22 a 1, alza 0x11–0x13 e le rocce non compaiono. Il casello 35.92 si raggiunge solo rompendo le rocce, oppure da ovest: è il caso dei salvataggi già oltre il vecchio casello.
6. **ADA (Rimini 34.48), testo dopo la MN:** prima diceva "Torna all'ippodromo di Cesena: le rocce verso Forlì ti aspettano"; ora "Torna a CESENA: oltre l'IPPODROMO, a MONTE SPACCATO, le rocce chiudono la strada per Forlì. VOLO ti aiuterà."
- Le flag temporanee 0x11–0x13 sono usate da molte mappe (come in Smeraldo): Monte Spaccato è aggiunta a `registri/flag_condivise_ammesse.json`.
- `collaudo/vai.py`: nuovo parametro `FLAG_ALZATE` (vuoto per default, le prove vecchie non cambiano) per dire al pianificatore che le rocce sono nascoste dallo script di mappa, che `analisi/percorso.py` non legge.

## 4. Budget

| | Stima prima | Usato | Resta |
|---|---|---|---|
| Spazio | < 1 KB | meno di 1 KB (eventi, 4 script brevi, 3 testi) | 1239 KB |
| Flag | 1 | 1 (0x22, dalle sicure 0x20–0x4FF) | 46 nel pool (40 sicure + 6 di allenatore) |
| Variabili | 0 | 0 | 47 |
| Strumenti, allenatori | 0 | 0 | 67 numeri di strumento, 18 allenatori liberi |

## 5. Collaudo (solo tasti; fixture dichiarate)

Script: `collaudo/t63.py` (con `leg.py` e `vai.py`). Risultati in `collaudo/risultati/063/`. Ogni prova parte da un salvataggio fatto con SALVA in gioco e caricato con Continua dal titolo; in VBA-M si riparte dallo stesso `.sav` fatto in mGBA.

**Fixture (scritture in RAM dichiarate, non prove):**
- `prima`: nessuna (savestate `s_ce3.ss`, Cesena, solo la 1ª medaglia: è la prima visita).
- `dopo`: posizione a Monte Spaccato (56,21), da `prog_imola.ss` (6 medaglie); SPACCAROCCIA scritta come quarta mossa del Pokémon 0 (che la MN si ottenga da ADA è solo letto negli script: vedi "Cosa non è verificato").
- `vecchio`: posizione a Capocolle (35.60, 38,17), da `prog_imola.ss`; flag 0x22 a 0. Simula un salvataggio già oltre il vecchio casello.
- `riproduci` (sulla 0.62): posizione a Monte Spaccato per la seconda metà.

| Prova | mGBA | VBA-M |
|---|---|---|
| **prima** (1 medaglia): Cesena → casello → Ippodromo, entrando dal cancello sud | sì | sì |
| Ippodromo → cancello ovest → Monte Spaccato | sì | sì |
| Davanti alle rocce: A → "Serve SPACCAROCCIA e la terza medaglia per rompere la roccia.", rocce ancora lì | sì | sì |
| Camminando contro la roccia (14,17) e contro gli alberi nuovi a nord (13,3) e a sud (13,36): la posizione non cambia | sì | sì |
| Nessun percorso a piedi verso 35.92 | sì | sì |
| Ritorno: Monte Spaccato → Ippodromo → casello → Cesena | sì | sì |
| SALVA, Continua: flag 0x22 a 0; di nuovo all'Ippodromo | sì | sì |
| **dopo** (6 medaglie, SPACCAROCCIA): A sulla roccia (14,17), "sì": la roccia sparisce, 0x22 resta a 0 | sì | sì |
| Esco all'Ippodromo e rientro: le tre rocce ci sono di nuovo | sì | sì |
| Rompo e passo fino al casello 35.92: 0x22 = 1 | sì | sì |
| Tornando a Monte Spaccato, accanto alla tagliata (12,17): nessuna roccia (0x11–0x13 alzate dallo script d'ingresso) | sì | sì |
| SALVA, Continua: 0x22 = 1; poi a Cesena, di nuovo a Monte Spaccato e fino a Capocolle senza rompere nulla | sì | sì |
| **vecchio** (a Capocolle, 0x22 = 0): verso est, nel casello 35.92 0x22 diventa 1; a Monte Spaccato nessuna roccia; si arriva a Cesena | sì | sì |
| **vecchio salvataggio vero della 0.62** (`t63_riproduci6.sav`: SALVA in gioco sulla ROM 0.62 a Monte Spaccato, 6 medaglie; fixture solo la posizione, prima di salvare) caricato con Continua nella 0.63: le tre rocce ci sono; si rompono (la squadra di `prog_imola` conosce già SPACCAROCCIA, nessuna fixture di mossa), a 35.92 0x22 = 1, tornando nessuna roccia, si arriva a Cesena | sì | sì |

I file `t63_*.json` e `t63_*_vbam.json` coincidono voce per voce (anche `t63_vecchio62`). I due "fuori percorso" nei log sono un personaggio dell'Ippodromo che cammina: il navigatore ricalcola il percorso e prosegue.

**Analisi statica** (`collaudo/risultati/063/analisi.txt`): `analisi/percorso.py` da Cesena raggiunge l'Ippodromo e Monte Spaccato con il solo TAGLIO; 35.92 e Capocolle solo con SPACCAROCCIA, anche dando tutte le altre abilità (SURF, FORZA, CASCATA, bici, SUB, FLASH). `analisi/righe.py` non trova riquadri oltre le due righe in 35.91, 35.101, 34.48, 35.92, 34.19.

### Regressione (`collaudo/regressione.py`, 0.63 contro 0.62)

Tutte le 17 partenze in mGBA e il salvataggio vero in mGBA e VBA-M girano e sono **uguali** alla 0.62 (`regressione.md`). Nessuna partenza è in Cesena ovest, quindi la regressione non tocca le mappe cambiate: le prove sono quelle sopra.

### Cosa non è verificato
- I testi nuovi del casellante 35.91, del cartello di Monte Spaccato e di ADA non sono stati letti sullo schermo: la divisione in riquadri di due righe è controllata sui byte (`analisi/righe.py`). Il testo di ADA, in particolare, non è stato raggiunto a tasti.
- Che la MN SPACCAROCCIA si ottenga da ADA è letto negli script (`analisi/doni.py`), non provato a tasti; nelle prove la mossa è una fixture.
- Il caso "3ª medaglia senza la MN, già oltre il vecchio casello" è coperto dalla flag 0x22 (prova `vecchio`, con fixture), non da una partita vera giocata così.
- Un salvataggio fatto **dentro l'Ippodromo** con una versione vecchia, davanti alle tre rocce del cancello ovest: non provato. Nella prova `vecchio62` (salvataggio dentro Monte Spaccato) dopo Continua c'erano già gli oggetti nuovi; se invece lo script d'ingresso dell'Ippodromo non girasse con Continua, le rocce resterebbero finché non si esce e si rientra. Dal cancello sud si esce comunque.
- Sulla strada dal casello 35.91 si arriva al cancello sud dell'Ippodromo, che nella grafica è sul lato opposto: è una scelta di collegamento, non un errore, ma l'aspetto non è stato curato.

## 6. Richieste del prompt

| Richiesta | Stato |
|---|---|
| Ippodromo tappa del percorso tra Cesena e Monte Spaccato, visitabile alla prima visita di Cesena | **verificato** (mGBA e VBA-M, partita con 1 medaglia) |
| Tratto Monte Spaccato → Capocolle chiuso solo da rocce fisiche di SPACCAROCCIA | **corretto e verificato**: tre rocce nella tagliata, prati chiusi da alberi; senza medaglia e MN non si passa |
| Tolto il controllo di 0x869 nel casello 35.91 | **riprodotto** sulla 0.62, **corretto e verificato** |
| SPACCAROCCIA fuori dalla lotta solo con la medaglia di Rimini | **verificato** il rifiuto con 1 medaglia; lo script delle rocce è quello di Smeraldo (controlla 0x869 e la mossa in squadra) |
| Non si può aggirare | **verificato** a tasti (roccia e alberi) e con `percorso.py` (nessun'altra strada, anche con tutte le altre abilità) |
| Chi ha già superato il passaggio non resta chiuso fuori | **corretto e verificato** con fixture (`vecchio`) e con un salvataggio vero della 0.62 caricato nella 0.63 (mGBA e VBA-M) |
| Testi in italiano, massimo 2 righe per riquadro | **corretto** per i testi toccati, controllato sui byte |
| Uscire e rientrare dalle mappe, passaggi nei due versi | **verificato** (Cesena ↔ casello ↔ Ippodromo ↔ Monte Spaccato ↔ 35.92 ↔ Capocolle) |
