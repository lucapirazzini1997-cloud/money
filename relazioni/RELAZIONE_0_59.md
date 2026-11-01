# Pokémon Romagna 0.59: Entei, Raikou e Suicune dalla prima visita a Ravenna (Lotto 2, prima parte)

**Base:** 0.58, SHA-256 `47f53668d8b5861956938cd041fb892e541b86031e4ac7b4337e8328923897c4` (uguale alla 0.57).

**Risultato:** `Pokemon_Romagna_0_59.gba`, SHA-256 `aee694c2535ab1524e08e2cd4447cefc16afddd10211ba4fe0fa35b64a45ec1d`.
- Patch BPS 0.58→0.59: `rom/Pokemon_Romagna_0_58_to_0_59.bps` (1204 byte), verificata riapplicandola.
- Modulo: `versioni/v059_cani.py`. La build da zero (`python3 build.py`) rifà tutti gli SHA, controlli compresi.
- Lo SHA è in `SHA` dentro `build.py` dopo il collaudo (§4).
- **Salvataggi compatibili**, anche quelli fatti dentro le mappe dei cani (§2).

## Piano del Lotto 2 (3 versioni)

| Versione | Contenuto |
|---|---|
| **0.59** | Entei, Raikou e Suicune catturabili dalla prima visita a Ravenna (questa relazione) |
| 0.60 | Kyogre al largo di Rimini quando si ha SUB; uccelli leggendari prima della Lega |
| 0.61 | Regi senza FORZA, con stati di cattura, fuga e sconfitta separati; evento chiaro per Deoxys, Jirachi e Mewtwo; regola del nuovo tentativo per tutti; tabella dei leggendari in `doc/PROGETTO.md` §3 |

**Come ho capito il compito dei cani** (scritto prima di iniziare): dalla prima visita a Ravenna il giocatore deve poter catturare Entei, Raikou e Suicune, una sola volta ciascuno e con un nuovo tentativo dopo fuga o sconfitta. Nessun tratto deve chiedere strumenti che a quel punto non ha, e chi li ha già catturati in un vecchio salvataggio non deve ritrovarli.

## 1. Causa e decisione

**Causa (riprodotta in emulatore, §4).** Ravenna (34.94, uscita 10) porta al Safari originale di Smeraldo, gruppo 26 (si entra in 26.3). Il Safari ha ingresso libero e si usano le Poké Ball normali. I tre cani c'erano già, ma il loro script controllava "Lega vinta" (flag 0x864) e rispondeva *«Il richiamo di questo Pokémon si udirà dopo la vittoria alla LEGA ROMAGNOLA»*:

| Cane | Dove | Flag di cattura |
|---|---|---|
| Entei | Grotta Ardente 35.100, ingresso da 26.12 | 0x88F |
| Raikou | prato d'erba alta in 26.12 | 0x884 |
| Suicune | lago di 26.13, si arriva con SURF | 0x887 |

Il Safari costruito nella 0.51 (34.115, 35.44, 35.45) ha i suoi cani con **le stesse flag**, ma nessuna uscita ci porta.

**Decisione: i cani restano nel Safari del gruppo 26**, dove già erano, e non si collega quello della 0.51. I motivi:
- è il Safari a cui porta davvero Ravenna, ed è la base del Lotto 10;
- i posti sono già quelli della proposta: Entei in una grotta, Raikou in un prato, Suicune su un lago;
- collegare il Safari della 0.51 vorrebbe dire rimettere in funzione anche le sue missioni (impianti, custodi, braciere), senza guadagno.

Il Safari della 0.51 resta scollegato. In `registri/irraggiungibili_ammesse.json` il motivo è aggiornato: deciderà il Lotto 10. Lì le specie erano scritte male: 35.44 è Entei e 35.45 è Raikou.

## 2. Modifiche (versioni/v059_cani.py)

- **Script nuovo per ogni cane** (103 byte l'uno), senza il controllo della Lega:
  1. se la flag di cattura è già alzata, finisce (sicurezza: l'oggetto è comunque nascosto da quella flag);
  2. testo, verso, lotta (`setwildbattle` specie e livello 45 come prima, `dowildbattle`);
  3. esito della lotta letto con special 0xB7:
     - **cattura (7):** flag di cattura alzata, oggetto rimosso, testo di cattura;
     - **KO del leggendario (1):** testo "crolla, poi si rialza… Puoi riprovare quando vuoi";
     - **qualunque altro esito** (fuga del giocatore, BOATO del leggendario): testo "… torna al suo posto. Puoi riprovare quando vuoi".
- **Testi riscritti in riquadri di due righe.** Prima ne avevano tre o quattro. Prima dicevano anche "esci e torna", ma in emulatore il Pokémon resta al suo posto dopo fuga o KO.
- **Oggetti:** il puntatore allo script di Entei (35.100, oggetto 1), Raikou (26.12, oggetto 10) e Suicune (26.13, oggetto 6) punta allo script nuovo.
- **Vecchi salvataggi fatti dentro una di queste mappe.** SaveBlock1 conserva una copia degli oggetti con il puntatore allo script di quando la mappa è stata caricata. Per questo anche il vecchio script (con il controllo della Lega) diventa un salto a quello nuovo (5 byte). Provato in §4.
- **Doppioni:** nessuno. Le flag di cattura sono le stesse di prima e dello Safari della 0.51. Chi ha catturato Entei dopo la Lega in un vecchio salvataggio ha 0x88F alzata, e l'oggetto non compare.

**Strumento nuovo: `analisi/percorso.py`, percorso a piedi realistico.** Tiene conto di:
- quota delle caselle;
- acqua con SURF (si entra da quota 3) e CASCATA per risalire;
- sporgenze in un solo verso;
- pendii e binari solo con la Bici giusta;
- rocce con SPACCAROCCIA e alberi con TAGLIO;
- persone ferme;
- uscite normali e a freccia;
- connessioni ai bordi.

Restituisce anche la sequenza di direzioni, che `collaudo/vai.py` esegue con i tasti.

| Abilità del giocatore | Raikou | Entei | Suicune |
|---|---|---|---|
| TAGLIO, SPACCAROCCIA (niente SURF) | sì | sì | no |
| + SURF | sì | sì | sì |
| + FORZA, CASCATA, Bici Corsa e Bici Cross | nessun cambiamento | nessun cambiamento | nessun cambiamento |

Alla 5ª medaglia (prima visita a Ravenna) il giocatore ha già TAGLIO (Cervia), SPACCAROCCIA (Rimini) e SURF (Forlì, consegnato in 34.74): non serve nessuna bici e nessuna MN successiva. Che SURF si ottenga davvero in gioco lo verifica il Lotto 3.

## 3. Budget

| | Stima prima | Usato | Resta |
|---|---|---|---|
| Spazio | ~1,5 KB | **1119 byte** (3 script da 103 byte e i testi) | 1248 KB |
| Flag | 0 | 0 | 47 nel pool (41 sicure 0x20–0x4FF) |
| Variabili | 0 | 0 | 47 |
| Strumenti, allenatori | 0 | 0 | 67 numeri di strumento, 18 allenatori liberi |

## 4. Collaudo (solo tasti; fixture dichiarate)

Script: `collaudo/t59.py`, navigatore `collaudo/vai.py`. Risultati in `collaudo/risultati/059/`.

**Partenza:** il savestate `gpre.ss` di una partita precedente (5 medaglie, Lega non vinta, nessun cane catturato), nelle Campagne di Lugo (35.71).

**Fixture (scritture in RAM dichiarate, non prove):**
- **5 MASTER BALL** in testa alla tasca Poké Ball. La cattura avviene comunque in lotta con i tasti; la Master Ball rende solo la prova ripetibile.
- **SURF come quarta mossa di Breloom**, solo per arrivare da Suicune. La squadra del savestate (Blaziken e Breloom) non ha nessun Pokémon che possa imparare SURF, e la MN03 non è nella borsa.

**Viaggio, solo tasti.**
- Dalle Campagne di Lugo a Ravenna: 35.71 → casello 35.99 → Via dei Canali 35.70 → casello 35.98 → Ravenna 34.96/34.94.
- Poi nel Safari: 26.3 → 26.13 → 26.12, fino a Raikou e da lì nella Grotta Ardente fino a Entei.
- Da Ravenna in SURF (usato dal campo: A davanti all'acqua, "sì") fino a Suicune.
- Lotte selvatiche lungo la strada combattute normalmente.

### mGBA, 0.58 (riproduzione del bug)

Per i tre cani: si esce dalla mappa e si rientra (così gli oggetti vengono dalla ROM 0.58), poi si parla con il cane. Risposta per tutti e tre: *«Il richiamo di questo Pokémon si udirà dopo la vittoria alla LEGA ROMAGNOLA…»*, **nessuna lotta**. **Riprodotto.**

### mGBA, 0.59

| Prova | Raikou | Entei | Suicune |
|---|---|---|---|
| Parlando parte la lotta | sì | sì | sì |
| Fuga (FUGA nel menu): testo di fuga, flag 0, Pokémon ancora lì | sì | sì | sì |
| Uscita dalla mappa e rientro dopo la fuga: Pokémon presente | sì | sì | sì |
| Lotta fino alla fine | Raikou usa **BOATO** e chiude la lotta: testo di fuga, flag 0, presente | **KO di Entei**: testo del KO, flag 0, presente anche dopo il rientro | Blaziken va KO, la lotta finisce con il testo di fuga, flag 0, presente |
| Cattura (MASTER BALL dal menu della lotta, "no" al soprannome) | flag 0x884 = 1, sparito, Raikou in squadra | flag 0x88F = 1, sparito, Entei in squadra | flag 0x887 = 1, sparito, Suicune in squadra |
| SALVA in gioco, poi titolo → Continua | flag 1, assente, in squadra | flag 1, assente, in squadra | flag 1, assente, in squadra |
| Uscita dalla mappa e rientro dopo la ricarica | assente, flag 1 | assente, flag 1 | assente, flag 1 |

### Vecchio salvataggio

1. Con la 0.58: si esce dalla mappa di Raikou e si rientra, si salva in gioco dentro 26.12, poi titolo → Continua. Parlando con Raikou risponde "dopo la Lega".
2. Lo **stesso file di salvataggio** aperto con la 0.59: parlando parte la lotta. Esito in §4b.

### VBA-M

Il salvataggio vero viene fatto in mGBA accanto al cane, con le Master Ball della fixture. VBA-M continua dal titolo e poi: parla, fugge, riparla, cattura, salva in gioco, ricarica dal titolo, esce dalla mappa e rientra. Esito in §4b.

- **Correzione dello strumento.** Il primo giro ha mostrato che `collaudo/vb.py` (VBA-M) leggeva il file di salvataggio ma non lo riscriveva: dopo "salva e ricarica" la partita tornava indietro.
- Ora lo scrive al `ping` e all'uscita, come fa mGBA. Nella regressione della 0.58 VBA-M partiva solo da un salvataggio fatto in mGBA, quindi quella regressione non è toccata.

### Regressione (`collaudo/regressione.py`, 0.59 contro 0.58)

- **Partenze da savestate:** schermo, EWRAM, IWRAM (tolto l'orologio), VRAM, tavolozze e OAM sono **uguali** in tutti i punti di controllo.
- **Partenze dal salvataggio vero (mGBA e VBA-M):** il file di salvataggio fatto in gioco è identico byte per byte. Dopo Continua cambiano solo 117 byte di EWRAM, tutti nello stesso posto.
  - **Causa: è un comportamento di Smeraldo, non un bug.** `LoadSaveblockObjEventScripts` copia il puntatore allo script di **tutti i 64** oggetti dalla tabella della mappa, anche oltre il numero di oggetti che la mappa ha davvero.
  - Il salvataggio di prova è nella chiesa di Cesena (34.37), la cui tabella di oggetti (fatta dalla 0.56) è seguita da spazio libero. Nella 0.58 lì c'era 0xFF, nella 0.59 ci sono i testi nuovi.
  - Quei puntatori finiscono in slot che il gioco non usa mai: oltre il numero di oggetti della mappa.
  - Il gioco gira in tutte le partenze. Tabella completa in `collaudo/risultati/059/regressione.md`.

### Cosa non è verificato

- **Ottenere SURF in gioco.** Qui è una fixture; lo controlla il Lotto 3, insieme alle altre MN e alle bici.
- **Il ramo KO di Raikou e di Suicune.** Raikou chiude la lotta con BOATO e la squadra di prova non riesce a mandare KO Suicune. Il ramo KO è lo stesso codice per i tre cani, ed è provato con Entei.
- **La sconfitta del giocatore** (tutta la squadra KO). Il gioco di Smeraldo riporta al Centro Pokémon e la flag di cattura resta bassa: lo dice il codice, non è provato in emulatore.
- **La cattura con Poké Ball normali.** Sono provate le Master Ball della fixture; la formula di cattura è quella di Smeraldo e non è cambiata.
- **Il Safari della 0.51** (34.115, 35.44, 35.45): non toccato, resta scollegato.

## 5. Richieste del prompt (Lotto 2, cani)

| Richiesta | Stato |
|---|---|
| Catturabili già dalla prima visita a Ravenna | **corretto e verificato** (mGBA e VBA-M, 5 medaglie, Lega non vinta) |
| Decidere fra collegare il Safari della 0.51 e spostare i cani nel Safari 26 | deciso: Safari 26, dove già erano, nei posti della proposta (§1) |
| Nessun tratto con strumenti non ottenibili (Bici Cross compresa) | verificato con `analisi/percorso.py` e in emulatore: bastano TAGLIO, SPACCAROCCIA e SURF; nessuna bici. SURF ottenibile in gioco: da verificare nel Lotto 3 |
| Niente duplicati per chi li ha già catturati | stesse flag di cattura; provato che dopo la cattura il cane non ricompare (salvataggio, ricarica, rientro) |
| Una sola volta, nuovo tentativo dopo fuga o sconfitta | verificato: fuga, BOATO e KO lasciano la flag bassa e il cane al suo posto |
| Riassunto in due righe prima di iniziare | fatto (in chat e qui sopra) |
| Kyogre, uccelli, Deoxys/Jirachi/Mewtwo, Regi, tabella | 0.60 e 0.61 |
