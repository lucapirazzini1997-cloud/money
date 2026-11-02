# Pokémon Romagna 0.60: Kyogre e uccelli leggendari prima della Lega (Lotto 2, seconda parte)

**Base:** 0.59, SHA-256 `aee694c2535ab1524e08e2cd4447cefc16afddd10211ba4fe0fa35b64a45ec1d`.

**Risultato:** `Pokemon_Romagna_0_60.gba`, SHA-256 `d9ca40b361d02c0404b5d6553dc8d45252087d8bebf59e4e42c942a5786b183a`.
- Patch BPS 0.59→0.60: `rom/Pokemon_Romagna_0_59_to_0_60.bps` (2686 byte), verificata riapplicandola.
- Modulo: `versioni/v060_kyogre_uccelli.py`. La build da zero rifà tutti gli SHA, controlli compresi.
- Lo SHA è in `build.py` dopo il collaudo (§4).
- **Salvataggi compatibili**, anche quelli fatti dentro le mappe dei leggendari (§4).

## 1. Causa

Gli script di Kyogre (35.37) e degli uccelli (35.31, 35.32, 35.33) controllavano **per prima cosa** "Lega vinta" (flag 0x864) e rispondevano *«Il richiamo di questo Pokémon si udirà dopo la vittoria alla LEGA ROMAGNOLA»*. Questo succedeva anche a enigma risolto e con 8 medaglie. In emulatore, sulla 0.59: **riprodotto** (§4).

Il resto delle condizioni era già quello della storia, e resta:

| | Come ci si arriva | Enigma | Condizione |
|---|---|---|---|
| **Kyogre** (Lv 70) | Cartello dell'Area Marina a Rimini (34.44, casella 52,20): con 8 medaglie porta in mare (35.36). Poi SURF e SUB fino al fondale (35.37) | Piloni: prima l'ovest, poi l'est (variabile 0x40E9 = 2, resta salvata) | 8ª medaglia (0x86E). SUB si riceve a Bagno di Romagna (35.26) proprio con l'8ª medaglia: è il momento della storia in cui si ha SUB |
| **Articuno** (Lv 52) | Via Vittoria: la guardia di 35.27 con 8 medaglie apre il passaggio (0x4D5); in 35.28 un masso da spostare con FORZA | Rune vento → gelo (0x400D = 2) | 8ª medaglia |
| **Zapdos** (Lv 52) | come sopra, poi 35.29 | Rune bobina → cielo; la "messa a terra" azzera (0x400D = 2) | 8ª medaglia |
| **Moltres** (Lv 52) | come sopra | Rune brace → fiamma → sole (0x400D = 3) | 8ª medaglia |

La variabile 0x400D è temporanea: si azzera a ogni ingresso nel santuario, quindi le rune vanno rifatte ogni volta. È il comportamento di prima.

## 2. Modifiche (versioni/v060_kyogre_uccelli.py)

- **Uno script nuovo per ognuno dei quattro** (Kyogre 211 byte, uccelli circa 160), con le condizioni nell'ordine della storia:
  1. già catturato → "Il santuario è tranquillo";
  2. enigma non risolto → indizio;
  3. senza l'8ª medaglia → testo delle medaglie;
  4. lotta;
  5. esito:
     - **cattura:** flag e oggetto rimosso;
     - **KO:** testo "crolla, poi si rialza… Puoi riprovare quando vuoi";
     - **fuga:** testo "torna al suo posto… Puoi riprovare quando vuoi".
- **Flag di cattura invariate.** Kyogre: 0x4E1 e 0x4E0; uccelli: 0x4CD, 0x4CE, 0x4CF. Chi li ha già catturati non li ritrova.
  - L'oggetto di Kyogre è mostrato dallo script comune di ritorno al campo solo con 0x86E e senza 0x4E1: non cambia.
- **Corretto un difetto degli uccelli.** Dopo un KO il testo "si ritira per recuperare" veniva caricato e poi sostituito da "santuario tornato tranquillo", perché mancava la `callstd`. Il giocatore credeva di aver chiuso l'incontro.
- **Testi riscritti in riquadri di due righe** (prima tre o quattro righe per riquadro).
- **Il vecchio script** (con il controllo della Lega) diventa un salto al nuovo, per i salvataggi fatti dentro queste mappe.
- **Registri.** La flag di sistema 0x8C1 (oggetto rimosso dopo una lotta scriptata, di Smeraldo) ora è usata anche in 35.31–35.33. Aggiunta a `registri/flag_condivise_ammesse.json`: è la flag che usano tutti gli script dei leggendari.

**Strumenti di analisi e collaudo:**
- `analisi/percorso.py` ora conosce:
  - SUB: immersione dall'acqua profonda, risalita dalle mappe sott'acqua;
  - i massi di FORZA e gli alberi di TAGLIO (script 0x290C74 e 0x290A67);
  - la posizione reale dei massi già spostati, letta in RAM.
- `collaudo/vai.py` usa FORZA sui massi e SUB per scendere e risalire (B sott'acqua). Nelle lotte selvatiche lungo la strada prova prima a fuggire.
- Nuova libreria `collaudo/leg.py` con le funzioni comuni delle prove sui leggendari (prese da `t59.py`, che resta com'era).
- `collaudo/vb.py` riscrive il `.sav` solo se il gioco ha davvero salvato.

**Percorsi** (`analisi/percorso.py`, da Bagno di Romagna con ALDO/guardia superati):

| Abilità del giocatore | Articuno | Zapdos | Moltres | Lega |
|---|---|---|---|---|
| SURF, TAGLIO, SPACCAROCCIA, FORZA | sì | sì | sì | sì |
| senza FORZA | no | no | sì | no |

Kyogre, dall'arrivo in mare (35.36): con SURF e SUB sì, senza SUB no. FORZA (Imola, 7ª medaglia) e SUB (8ª medaglia) arrivano prima della Lega; che si ottengano davvero lo verifica il Lotto 3.

## 3. Budget

| | Stima prima | Usato | Resta |
|---|---|---|---|
| Spazio | ~3 KB | **2580 byte** | 1246 KB |
| Flag | 0 | 0 | 47 nel pool |
| Variabili | 0 | 0 | 47 |
| Strumenti, allenatori | 0 | 0 | 67 numeri di strumento, 18 allenatori liberi |

## 4. Collaudo (solo tasti; fixture dichiarate)

Script: `collaudo/t60.py` con `leg.py` e `vai.py`. Risultati in `collaudo/risultati/060/`.

**Partenza:** il savestate `prog_imola.ss` di una partita precedente (6 medaglie, Lega non vinta). Non esiste una partita di prova con 8 medaglie.

**Fixture (scritture in RAM dichiarate, non prove), poi un salvataggio vero in gioco e Continua dal titolo:**
- **medaglie 7 e 8** (flag 0x86D e 0x86E): il punto della storia dopo Bagno di Romagna;
- **mosse sul campo:** FORZA a Blaziken, SURF e SUB a Breloom;
- **5 MASTER BALL;**
- **allenatori di Via Vittoria già battuti** (842–844, 750–755). Senza questa fixture la squadra di prova (Blaziken 50, Breloom 43) perde contro di loro;
- **posizione di partenza:** Bagno di Romagna (35.19) per gli uccelli, Rimini (34.44) per Kyogre. Va scritta in SaveBlock1 e nell'oggetto del giocatore, perché Continua ripristina anche quello.

Tutto il resto solo con i tasti: viaggio, guardia, masso, cartello, SURF e SUB, rune e piloni, lotte.

### 0.59 (riproduzione)

- **Kyogre:** dal cartello di Rimini si va in mare, ci si immerge e si arriva davanti a Kyogre. Si risolvono i piloni (est per primo: "Il sigillo si spegne"; poi ovest ed est: "risuona"). Kyogre risponde comunque "dopo la vittoria alla LEGA". **Riprodotto.**
- **Uccelli:** guardia, masso, poi in ogni santuario rune nell'ordine giusto ("Il sigillo si apre!"). Ognuno dei tre risponde comunque "dopo la vittoria alla LEGA". **Riprodotto.**

### 0.60, mGBA e VBA-M (stessi risultati)

| Prova | Kyogre | Articuno | Zapdos | Moltres |
|---|---|---|---|---|
| Parlando prima dell'enigma: indizio | sì | sì | sì | sì |
| Enigma nell'ordine sbagliato | "il sigillo si spegne" (pilone est per primo) | — | — | — |
| Enigma nell'ordine giusto | piloni ovest, poi est | vento, gelo | bobina, cielo | brace, fiamma, sole |
| Lotta | sì | sì | sì | sì |
| Fuga: testo, flag 0, Pokémon ancora lì | sì | sì | sì | sì |
| Cattura (MASTER BALL, "no" al soprannome): flag 1, sparito, in squadra | sì | sì | sì | sì |
| SALVA in gioco, titolo → Continua: flag 1, in squadra | sì | sì (tre uccelli in squadra) | sì | sì |
| Uscita dalla mappa e ritorno (Kyogre: risalita con SUB, poi di nuovo giù): Pokémon assente | sì | sì | sì | sì |

### Vecchio salvataggio

Con la 0.59 si entra nel Santuario di Articuno, si salva in gioco e si riapre dal titolo. Parlando con Articuno risponde "dopo la Lega". Lo **stesso file** aperto con la 0.60 dà l'indizio delle rune, cioè lo script nuovo. Esito in `collaudo/risultati/060/t60_vecchio.json`.

### Regressione (`collaudo/regressione.py`, 0.60 contro 0.59)

**Tutte le 19 partenze uguali alla 0.59** (17 savestate in mGBA e il salvataggio vero in mGBA e in VBA-M): schermo, EWRAM, IWRAM (tolto l'orologio), VRAM, tavolozze e OAM. Tabella in `collaudo/risultati/060/regressione.md`.

### Cosa non è verificato

- **Il ramo KO dei quattro.** La squadra di prova non riesce a mandarli KO. Il ramo è scritto come quello della 0.59, provato con Entei.
- **Ottenere FORZA e SUB in gioco** e la lotta con gli allenatori di Via Vittoria. Qui sono fixture; li controlla il Lotto 3.
- **La sconfitta del giocatore** (tutta la squadra KO).
- **I testi degli enigmi** (rune, piloni, cartelli dei santuari). Non sono toccati e alcuni hanno ancora tre righe per riquadro: da sistemare quando si toccheranno quelle mappe.

## 5. Richieste del prompt

| Richiesta | Stato |
|---|---|
| Kyogre catturabile prima della Lega, nel momento in cui si ha SUB | **corretto e verificato** (mGBA e VBA-M): basta l'8ª medaglia, la stessa che dà SUB |
| Uccelli leggendari catturabili prima della Lega | **corretto e verificato** (mGBA e VBA-M) |
| Una sola volta, nuovo tentativo dopo fuga o sconfitta | fuga verificata; KO non provato (§4) |
| Deoxys, Jirachi, Mewtwo, Regi, tabella riassuntiva | 0.61 |
