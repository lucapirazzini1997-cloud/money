# Pokémon Romagna 0.53: interfaccia in italiano

Base: ROM 0.52 (SHA-256 `d2412f7c…ed4b`). La tua 0.44 (`f62af7e2…777a`) non è stata toccata.
Risultato: `Pokemon_Romagna_0_53.gba`, SHA-256 `5a5f643482236881674d999c0758d308cfe895dadb29c78df078b1f6f728f142`.
- Il builder estratto dal pacchetto, con `rom047.gba` e `base31.gba` accanto, rifà lo stesso SHA.
- La patch BPS 0.52→0.53 è verificata.

## Cosa cambia

**1. Nomi.**
- Riscritti sul posto, con la stessa lunghezza massima degli originali:
  - 353 mosse (es. ATT. RAPIDO, SPACCAROCCIA, GIGASSORBIM.);
  - 296 strumenti (es. SUPER AMO, PORTA{POKéBLOCK});
  - 77 abilità;
  - 18 tipi (6 lettere: VOLANT, COLEOT, SPETTR…);
  - 60 classi di allenatore (es. ALLENATORE, MONTANARO, CAPOPALESTRA).
- Le 25 nature (ARDITA, SCHIVA…) sono testi nuovi.

**2. Descrizioni.**
- 354 mosse e 302 strumenti, comprese MT e MN.
- 78 abilità.
- Ognuna va a capo misurando i pixel con il font vero del gioco, entro la larghezza dei riquadri: zaino 3 righe da 104 px, mosse 2 righe da 147 px, abilità 1 riga da 148 px.
- Tre descrizioni della hack uscivano dal riquadro dello zaino e le ho accorciate:
  - REGOLATORE: "Regolatore preso al Team EMILIA, al quarto piano."
  - FATTURA: "Fattura del corriere: nomina i tecnici Befane."
  - MAPPA ROMAGNA: "Mappa della Romagna: per orientarti ovunque."

**3. Lotta.**
- Tutti i 363 messaggi della tabella di lotta, più quelli fuori tabella:
  - "Appare PSYDUCK selvatico!", "ALLENATORE ALDO ti sfida!", "Vai! COMBUSKEN!", "… usa SPACCAROCCIA!", "Preso! … è stato catturato!", evoluzione;
  - menu LOTTA / ZAINO / POKéMON / FUGA, "Cosa deve fare …?", TIPO/;
  - le statistiche e la finestra del salire di livello.
- Il prefisso "Foe"/"Wild" è diventato "Nemico " (es. "Nemico SWELLOW usa DOPPIOTEAM!"), anche per i selvatici. In italiano andrebbe dopo il nome, ma il gioco lo mette sempre prima.
- Le variazioni di statistica ora dicono "ELUSIONE di Nemico SWELLOW in aumento!" o "in forte calo!".

**4. Menu e schermate.**
- Menu di avvio e zaino: tasche STRUMENTI / POKé BALL / MT E MN / BACCHE / STRUM. BASE, USA / GETTA / REGISTRA / DAI…
- Squadra, riepilogo POKéMON: INFO POKéMON, ABILITÀ POKéMON, MOSSE LOTTA, "Natura INGENUA, incontrato al Lv2, …".
- Opzioni, salvataggio, scheda allenatore.
- PC: PC DI QUALCUNO, PRENDI / DEPOSITA POKéMON…
- Negozio, pesca, schiusa delle uova, testi dell'interfaccia del POKéDEX.
- Script comuni: "Hai ottenuto: …", "Lo ZAINO è pieno…", SURF, CASCATA, SUB, invio al PC.
- In tutto 602 testi. Quelli inglesi restano nella ROM: cambiano solo i puntatori, quindi nulla viene spostato o sovrascritto.

**Salvataggi:** non tocca nessun dato del salvataggio. I salvataggi della 0.52 funzionano.

## Test (onesto)
Tutto provato in emulatore con la ROM 0.53:
- **Lotta contro il rivale a Forlì:** "ALLENATORE ALDO ti sfida!", "manda in campo SWELLOW!", "Vai! COMBUSKEN!", menu LOTTA/ZAINO/POKéMON/FUGA, mosse con "PP 30/30 TIPO/NORMAL", "COMBUSKEN usa ATT. RAPIDO!", "Nemico SWELLOW usa DOPPIOTEAM!", "ELUSIONE… in aumento!" (prima della correzione la parola era minuscola, l'ho rifatta maiuscola).
- **Lotta selvatica in Via dei Canali:**
  - "Appare PSYDUCK selvatico!", lancio della POKé BALL dallo zaino e "Preso! PSYDUCK è stato catturato!".
  - In un'altra prova, dallo stesso punto: "Nemico PSYDUCK è esausto!", "BRELOOM ottiene 342 punti ESP.!", "BLAZIKEN sale al LV. 47!".
  - La finestra delle statistiche l'ho tradotta dopo averla vista in inglese. Non l'ho riguardata.
- **Zaino:** tutte e 5 le tasche, descrizioni intere dentro il riquadro, "Torna al gioco." Il primo giro aveva descrizioni tagliate: ho misurato la larghezza vera della finestra e rifatto gli a capo.
- **Riepilogo:** le 3 pagine, la descrizione dell'abilità e quella della mossa. Ho accorciato "VELOC." e "PRECIS." perché uscivano.
- **Opzioni:** "VELOCITÀ TESTO" ora è BASSA / MED. / ALTA. Prima LENTA/MEDIA/VELOCE si sovrapponevano.
- **Salvataggio:** "Vuoi salvare la partita?", SÌ/NO, "SALVATAGGIO IN CORSO… NON SPEGNERE LA CONSOLE.". Ho riavviato l'emulatore da zero e caricato il salvataggio dal titolo: stessa posizione e stessa squadra.
- **Centro POKéMON di Cesenatico e PC:** "accende il PC", "A quale PC vuoi accedere?", "Sistema di Memoria POKéMON aperto.", menu PRENDI/DEPOSITA POKéMON con le descrizioni, apertura del BOX.
- **Builder:** estratto in una cartella pulita, rifà lo stesso SHA.

**Fixture dichiarati:** ho usato i savestate della partita 0.52 (Forlì, Cesenatico, Via dei Canali, Centro POKéMON). Il nome del giocatore lì è "AAAAAAA".

## Non tradotto (resta in inglese)
- **Scritte disegnate come grafica, non come testo:** PROFILE, ABILITY, TRAINER MEMO, MOVES, DESCRIPTION, EFFECT, ITEM, RIBBON, STATS nel riepilogo; le icone dei tipi (GRASS, FIGHT); SEEN/OWN/AREA/CRY/SIZE del POKéDEX; TRAINER CARD e BADGES; PKMN DATA / CLOSE BOX nel PC. Servono immagini ridisegnate.
- **Voci del POKéDEX** (le descrizioni delle 386 specie) e le categorie ("SEED POKéMON"): sono tante, possono essere una versione a parte.
- **Funzioni che nella hack non si usano:** gare, Lotta Frontier, collegamento via cavo e wireless, Dono Segreto, base segreta e decorazioni, POKéNAV, frasi rapide, crediti, nastri.
- **Nomi delle classi dei capi del Frontier** (alcuni restano in inglese o abbreviati).

## Non verificato in emulatore
- **Schermate mai aperte:** negozio (testi solo controllati nella ROM), evoluzione, schiusa di un uovo, soprannome dopo la cattura, insegnamento di una MT, Maestra delle mosse con le nuove descrizioni, "Cosa vuoi fare?" con le LETTERE.
- **Messaggi di lotta rari:** ne ho visti una decina, gli altri li ho controllati solo per larghezza nella ROM.
- **Lotte in doppio** con "Nemico"/"Alleato".

## File
- `Pokemon_Romagna_0_53.gba`
- `Pokemon_Romagna_0_52_to_0_53.bps` (da applicare alla 0.52)
- `builder_0_53.tar.gz`: richiede `rom047.gba` e `base31.gba` accanto a `build53.py`. Uso: `python3 build53.py --out out`
