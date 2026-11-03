# Pokémon Romagna 0.62: MN e strumenti chiave (Lotto 3, prima parte)

**Base:** 0.61, SHA-256 `f3e7802535125bdc473bd328e4cf7f2b7aeb030f71a1fabb81675614acd63cbe`.

**Risultato:** `Pokemon_Romagna_0_62.gba`, SHA-256 `b8ebd0918981becb7c3d77c649d78bf92e7a29d5ec8eec14def17dd772ac9080`.
- Patch BPS 0.61→0.62: `rom/Pokemon_Romagna_0_61_to_0_62.bps` (653 byte), verificata riapplicandola.
- Modulo: `versioni/v062_strumenti.py`. La build da zero rifà tutti gli SHA, controlli compresi; lo zip senza `out/` ricostruito in una cartella pulita rifà lo stesso SHA.
- Lo SHA è in `build.py` dopo il collaudo (§4).
- **Salvataggi compatibili:** cambiano solo i puntatori ai testi dentro script che esistevano già (stessi script, stesse flag); il salvataggio vero della regressione carica in mGBA e VBA-M.

## 1. Cosa chiedeva il prompt

Lotto 3: verificare che SUB, CASCATA, FLASH, Bici Cross e Super Amo si ottengano; altrimenti consegnarli in un punto sensato o togliere gli ostacoli che li richiedono.

## 2. Analisi

Nuovo strumento `analisi/doni.py`: per ogni mappa reale segue gli script (oggetti, cartelli, coordinate, script di mappa, con call/goto) e annota chi consegna ogni strumento. Risultato sulla 0.61:

| Strumento | Chi lo consegna | Condizione | Stato trovato |
|---|---|---|---|
| CASCATA (MN07) | Safari Ravenna 26.3, oggetto 1 | 8ª medaglia; flag 0x630 | in italiano |
| SUB (MN08) | sommozzatore, Bagno di Romagna 35.26, oggetto 4 | 8ª medaglia; flag 0x4E6 | in italiano, ma **due testi con riquadri di 3 righe** (`analisi/righe.py` sulla 0.61, in `righe.txt`) |
| FLASH (MN05) | montanaro della Grotta Granito 24.7 (dall'Appennino Romagnolo 0.21), oggetto 1 | nessuna; flag 0x6D | **testi in inglese** (script di Smeraldo; copia in `flash_0_61.txt`) |
| BICI CROSS | Cesenatico 34.42, oggetto 2 | nessuna; flag 0x629 | in italiano |
| AMO VECCHIO | pescatore, Cesenatico 34.22, oggetto 4 | nessuna; flag 0x26F | in italiano |
| AMO BUONO | Rimini 34.44, oggetto 5 | nessuna | in italiano |
| SUPER AMO | pescatore, Ravenna 34.96, oggetto 13 | 5ª medaglia; flag 0x62F | in italiano |

Restano nella ROM anche gli script di Smeraldo che consegnano gli stessi strumenti (WATTSON, WALLACE e altri), su oggetti nascosti o in mappe dove non servono: non sono stati toccati.

**Errore mio durante il lavoro, corretto prima della consegna:** all'inizio avevo usato numeri sbagliati per gli ami (0x105/0x106/0x10F invece di 0x106/0x107/0x108). Così avevo concluso che il SUPER AMO non si ottenesse e avevo aggiunto un pescatore nuovo a Cesenatico. La prima prova a tasti ha mostrato "Hai ottenuto: CHIAVE SOTT." e ha svelato l'errore (prova su una build intermedia, mai consegnata; il log non è conservato). Con i numeri giusti tutti e tre gli ami si ottengono già, quindi il pescatore nuovo è stato tolto: nella 0.62 non c'è.

Le zone buie, dove FLASH serve, sono la Grotta Granito B1F/B2F (24.8, 24.9) e la Via Vittoria di Smeraldo B1F/B2F (24.44, 24.45). Che senza FLASH si passi lo stesso, solo al buio, l'ho letto nel codice di Smeraldo: non è provato (vedi §5).

## 3. Modifiche (versioni/v062_strumenti.py)

- **FLASH**: i testi del montanaro in italiano, in riquadri di due righe (due testi nuovi su tre puntatori: il testo "dopo" serve a due rami). Lo script e la flag 0x6D restano quelli di prima.
- **SUB**: il testo "Batti LEDA…" (prima della consegna) e quello dopo la consegna, in riquadri di due righe.
- `analisi/righe.py` (nuovo) controlla i testi degli script di una mappa e segnala i riquadri oltre le due righe. Sui doni di questa versione (34.22, 34.42, 34.44, 34.96, 26.3, 35.26, 24.7) ora non segnala nulla; sulla 0.61 segnalava i due testi di SUB e il primo di FLASH (`collaudo/risultati/062/righe.txt`).

## 4. Budget

| | Stima prima | Usato | Resta |
|---|---|---|---|
| Spazio | < 1 KB | meno di 1 KB (5 testi) | 1240 KB |
| Flag | 0–1 | 0 | 47 nel pool |
| Variabili | 0 | 0 | 47 |
| Strumenti, allenatori | 0 | 0 | 67 numeri di strumento, 18 allenatori liberi |

## 5. Collaudo (solo tasti; fixture dichiarate)

Script: `collaudo/t62.py` con `leg.py` e `vai.py`. Risultati in `collaudo/risultati/062/`.

**Partenza:** il savestate `prog_imola.ss` (partita vera, 6 medaglie).

**Fixture (scritture in RAM dichiarate, non prove), poi SALVA in gioco e Continua dal titolo:**
- **posizione** di partenza a pochi passi da ogni personaggio, nella sua stessa mappa (Cesenatico, Rimini, Ravenna, Safari Ravenna, Bagno di Romagna); per FLASH nell'Appennino Romagnolo 0.21, da cui si entra a piedi nella Grotta Granito. Il "sì" della prima riga della tabella quindi non è una prova di raggiungibilità dal resto del gioco;
- **7ª e 8ª medaglia** (0x86D, 0x86E) solo nei salvataggi del Safari e di Bagno di Romagna (per CASCATA e SUB);
- **5ª medaglia tolta** (0x86B a 0) solo nel salvataggio per il rifiuto del SUPER AMO.

Lo strumento si controlla leggendo la BORSA in RAM (tasche strumenti, strumenti chiave e MT/MN). Il resto si fa solo con i tasti: si cammina fino al personaggio, si parla, si salva in gioco e si ricarica dal titolo. Per FLASH si entra a piedi dall'Appennino Romagnolo alla Grotta Granito.

| Prova | AMO VECCHIO | BICI CROSS | AMO BUONO | SUPER AMO | CASCATA | SUB | FLASH |
|---|---|---|---|---|---|---|---|
| Si arriva al personaggio a tasti | sì | sì | sì | sì | sì | sì | sì (da 0.21) |
| "Hai ottenuto" e strumento nella BORSA | sì | sì | sì | sì | sì | sì | sì |
| Riparlando: nessun nuovo "Hai ottenuto" | sì (ripete il saluto "Ti presto il mio AMO VECCHIO", ma non lo dà) | sì | sì | sì | sì (benvenuto del Safari) | sì | sì |
| SALVA, titolo, Continua: strumento ancora nella BORSA, flag a 1 | sì | sì | sì (nessuna flag nello script) | sì | sì | sì | sì |
| Dopo la ricarica: uscita dalla mappa, rientro, si riparla: nessun nuovo "Hai ottenuto", strumento nella BORSA (**solo mGBA**) | sì (via 34.42) | sì (via 34.22) | sì (via 34.45) | sì (via 34.108) | sì (via 34.94) | sì (via 35.19) | sì (via 0.21) |

Le prime quattro righe danno gli stessi risultati in **mGBA** e in **VBA-M** (`t62_doni.json`, `t62_doni_vbam.json`); l'ultima riga, aggiunta dopo la rilettura del revisore, è stata eseguita solo in mGBA (`t62_doni.json`). "Nella BORSA" vuol dire che il numero dello strumento c'è in una tasca: la quantità non è letta.

**Rifiuti (solo mGBA):**
- SUPER AMO senza la 5ª medaglia: "Torna quando avrai la quinta medaglia…", nessuno strumento (`t62_prima.json`).
- SUB con 6 medaglie: "Sono un sommozzatore della riviera. Batti LEDA e ti insegnerò a scendere sul fondo del mare.", nessuno strumento, flag 0 (`t62_sub_prima.json`). La divisione in riquadri non si vede nel json: le due righe per riquadro sono controllate da `analisi/righe.py`, non con le schermate.

### Regressione (`collaudo/regressione.py`, 0.62 contro 0.61)

Tutte le partenze sono uguali alla 0.61, compreso il salvataggio vero in mGBA e in VBA-M (`regressione.md`).

### Cosa non è verificato
- L'**uso** delle MN fuori dalla lotta: risalire una cascata con CASCATA, immergersi con SUB, illuminare con FLASH, pescare con gli ami, saltare con la BICI CROSS. Qui è provato solo che gli strumenti si ottengono. SUB e CASCATA erano già stati usati nel collaudo del Lotto 2, ma con fixture.
- Quale medaglia serve per usare FLASH fuori dalla lotta: non l'ho né letta né provata. Per questo il testo nuovo non nomina nessuna medaglia.
- Come si arriva **all'Appennino Romagnolo (0.21)**: la prova parte già lì per fixture. Il registro ottimista lo dà raggiungibile da Lugo e dalla Pianura Romagnola; con il percorso realistico non è confermato, perché `analisi/percorso.py` si ferma a Ponte Santerno (vedi sotto).
- I rifiuti e l'uscita con rientro sono provati solo in mGBA.
- La divisione dei testi nuovi in riquadri di due righe è controllata leggendo i byte dei testi (`righe.txt`), non guardando le schermate.
- Il passaggio al buio senza FLASH (letto nel codice di Smeraldo, non provato).

### Segnalato per il resto del Lotto 3
- Il pescatore dell'AMO VECCHIO (34.22), riparlandoci, ripete "Ti presto il mio AMO VECCHIO" senza darlo: testo da cambiare.
- `analisi/percorso.py` dalla partenza raggiunge solo 186 mappe: si ferma a Ponte Santerno (35.0) → Imola, dove gli eventi a coordinate e i passaggi degli script non sono modellati. Va migliorato prima delle prove di raggiungibilità delle prossime versioni.

## 6. Richieste del prompt

| Richiesta | Stato |
|---|---|
| SUB, CASCATA, FLASH, Bici Cross, Super Amo si ottengono | **verificato** (mGBA e VBA-M) per tutti; anche AMO VECCHIO e AMO BUONO |
| Consegnarli in un punto sensato se mancano | non serviva: c'erano già tutti. Corretti i testi di FLASH (inglese) e di SUB (più di 2 righe) |
| Testi in italiano, massimo 2 righe per riquadro | **corretto** per i doni toccati: testi visti a tasti in italiano; le due righe per riquadro sono controllate sui byte (`righe.txt`), non sulle schermate |
| Uscire e rientrare dalle mappe | **verificato** (solo mGBA) per i sette personaggi |
