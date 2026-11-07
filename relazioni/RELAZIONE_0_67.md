# Pokémon Romagna 0.67: il treno regionale (Lotto 3)

**Base:** 0.66, SHA-256 `d794870a35a619553550d0913395fb5d900e122d50085bc4ec6cab5276b74f84`.

**Risultato:** `Pokemon_Romagna_0_67.gba`, SHA-256 `aa5724473410d034397f8ac75583e6639659c0d23feda031538d99d739fbfe7b`.
- Patch BPS 0.66→0.67: `rom/Pokemon_Romagna_0_66_to_0_67.bps` (CONSEGNA).
- Modulo: `versioni/v067_treno.py`. La build da zero rifà tutti gli SHA.
- Lo SHA è in `build.py` dopo il collaudo (§5).
- **Salvataggi compatibili:** le mappe nuove usano posti liberi (24.39–24.41, 24.50, 24.51, 24.74); nelle città cambiano solo 4 caselle del cartello e la porta di una casa che era chiusa; una flag e una variabile nuove (a 0 nei vecchi salvataggi). Un salvataggio vero della 0.66 fatto davanti alla futura stazione di Cesena: §5.

## 1. Cosa è stato chiesto

- Prompt 0.57, Lotto 3: "Ritorni obbligati a Cesena (dopo Rimini e dopo Imola): rendili meno pesanti. Puoi dare Volo prima oppure aggiungere un treno regionale tra città già visitate, senza aggirare blocchi di trama."
- Alla domanda "VOLO prima o treno?" hai risposto: "Volo in realtà dovrebbe essere ottenibile a Cesena dopo la seconda medaglia […], il treno è comunque una bella idea".
- Bozza delle stazioni, della sala e della carrozza (`bozze/treno.py`): "Va bene".

## 2. Com'era nella 0.66

- **VOLO** (verificato leggendo la ROM): l'MN la dà il dojo di Cesena (34.25, oggetto 6) a chi batte i suoi 5 allenatori, senza medaglie. La tabella delle medaglie delle MN della hack (ROM 0x1600000, letta dal menu della squadra a 0x1b590c) chiede per VOLO la **2ª medaglia** (0x868), non la 6ª di Smeraldo. Avevi ragione: dopo Rimini si può già tornare a Cesena in volo, se si è presa l'MN.
- Le città sulla mappa del Volo seguono le medaglie (script `R22_FlyGuard` della 0.22): Cesena dalla 2ª, Rimini e Cesenatico dalla 3ª, Forlì dalla 4ª, Faenza dalla 5ª, Ravenna e Lugo dalla 6ª, Imola dalla 7ª (o dalla 6ª se c'è la flag 0x4D9: nel salvataggio di prova `prog_imola`, con 6 medaglie, Imola è già sulla mappa), Bagno dall'8ª.
- **Stazioni:** nessuna. La vecchia "stazione" di Ravenna (35.59) oggi è San Vitale.

## 3. Modifiche (versioni/v067_treno.py)

### 3.1 La linea
Rimini – Cesena – Forlì – Faenza – Imola, come la Bologna–Ancona vera.

### 3.2 Le stazioni in città
In ogni città una casa con la porta chiusa diventa la stazione:

| Città | Casa (x, y) | Porta | Sala |
|---|---|---|---|
| Cesena 34.17 | 80–83, 6–8 | (82,8) | 24.39 |
| Rimini 34.47 | 52–55, 9–11 | (54,11) | 24.40 |
| Forlì 34.68 | 70–73, 52–55 | (72,55) | 24.41 |
| Faenza 34.85 | 38–41, 2–5 | (40,5) | 24.50 |
| Imola 35.1 | 55–58, 16–19 | (57,19) | 24.51 |

- **Il cartello:** blu, con STAZIONE in bianco (palette 4 del primario), largo una casa, sopra la facciata.
  - Le cinque città hanno già pieni i 512 tile del loro tileset secondario (misurato: 510–511 usati, nessun doppione nemmeno specchiato). Il cartello sta in 8 tile del **primario** (183, 197, 219, 235, 237, 258, 290, 306). Li ho scelti con tre controlli:
    - nessuna mappa li usa;
    - nessun metatile del primario li richiama;
    - nessuno dei 6344 `setmetatile` degli script tocca un metatile che li usa.
  - Sono tile vuoti in Smeraldo e fuori dalle zone animate del primario.
  - La grafica del primario è riscritta compressa (LZ con soli letterali, 18 KB) e ripuntata.
  - Il cartello è nello strato alto di 4 metatile nuovi, con il tipo di strato "coperto", così non copre il giocatore quando sta sulla porta.
- **La porta:** stesso disegno, comportamento 0x60 (come le altre porte della hack), collisione 0. Il cartello "La porta è chiusa a chiave" su quella casella è tolto, e c'è un'uscita nuova verso la sala.
- **Come sono fatti i metatile nuovi:** i 5 metatile nuovi (4 del cartello e la porta) stanno in una **copia** della tabella dei metatile della città, nei posti 1019–1023. Questi posti non li usano né la mappa, né il suo bordo, né i suoi script. Il tileset secondario nuovo ha la stessa grafica, le stesse palette e la stessa animazione; cambiano solo i puntatori ai metatile. Le altre mappe con lo stesso tileset non cambiano.
- **Gruppo 33:** nel gruppo 33 le mappe 33.18, 33.48, 33.69 e 33.86 puntano alla **stessa intestazione** di Cesena, Rimini, Forlì e Faenza. Sono la stessa mappa e hanno anche loro la stazione.

### 3.3 La sala del binario (5 mappe, 13×12)
È il layout 118 di Smeraldo (sala con il binario), usato com'è; musica 0x168, interno, regione della città.
- **CAPOTRENO** (7,8):
  - Saluta ("Stazione di CESENA! Dove vuoi andare?").
  - Chiede una città alla volta, nell'ordine della linea: "Un biglietto per FORLÌ?" (sì/no).
  - Offre solo le città che sono sulla **mappa del Volo**, cioè le stesse flag di visita (0x872, 0x873, 0x876–0x878), e mai la città dove si è. Così il treno porta solo dove si può già andare in volo e non aggira blocchi.
  - Se nessuna città è sbloccata lo dice; se si rifiuta tutto saluta.
  - Il biglietto è gratis.
- **Viaggiatore in attesa** (1,9) e **viaggiatrice** sull'altro binario (10,2), che è solo decorazione.
- **Biglietteria automatica** (12,8): fuori servizio, elenca le fermate.
- Uscita (6,11)/(7,11) verso la porta della città.

### 3.4 La carrozza (24.74, 16×12)
- È l'atrio del Centro Spaziale di Smeraldo (layout 275): parete con 14 finestrini, 8 tavolini con gli sgabelli. Dai tavolini è tolto il razzo disegnato.
- Tileset nuovo (19 metatile, 57 tile).
- **La scena:** script di frame sulla variabile del viaggio (1–5 = stazione d'arrivo).
  1. Al primo viaggio il VIAGGIATORE (10,3) parla della VIA EMILIA e della piadina (flag nuova).
  2. Il CAPOTRENO fa quattro passi fino al giocatore e annuncia "Prossima fermata: …".
  3. La variabile torna a 0 e si arriva sul binario della stazione scelta (6,4).

### 3.5 Differenze dalla bozza (dichiarate)
- Il **tabellone** (2–3,4) sta dietro la ringhiera: nessuna casella lo raggiunge. Ho tolto i due cartelli e le fermate le dice la biglietteria.
- Testo del viaggiatore in attesa: in bozza non c'era. "Aspetto il regionale per FAENZA… da qui al mare" stava male a Faenza e a Rimini; ora è uguale per tutte le stazioni.

## 4. Budget (da `out/rapporto_build.json`)

| | Stima prima | Usato | Resta |
|---|---|---|---|
| Spazio | ~60 KB | 150 KB (grafica del primario 18 KB; per città: copia della tabella dei metatile 9 KB e layout ~10 KB; carrozza; eventi, script, testi) | 793 KB |
| Flag | 1 | 1 (0x3C, primo viaggio fatto) | 35 nel pool, tutte sicure |
| Variabili | 1 | 1 (0x4055, viaggio in corso) | 43 |
| Posti per mappe nuove | 6 | 6 (24.39–24.41, 24.50, 24.51, 24.74) | 5 (34.10, 34.13, 34.18, 24.75, 24.76; le prime tre hanno il layout condiviso) |
| Tile liberi del primario (vuoti, mai usati) | 8 | 8 | circa 27 |
| Allenatori, strumenti | 0 | 0 | 10, 67 |

La stima dello spazio era bassa: non avevo contato la copia di tabella e layout per ogni città.

## 5. Collaudo (solo tasti; fixture dichiarate)

RISULTATI

## 6. Richieste

| Richiesta | Stato |
|---|---|
| Ritorni a Cesena meno pesanti (treno tra città già visitate, senza aggirare blocchi) | **corretto e verificato** |
| Mappe mostrate finite e approvate prima del modulo | **fatto** ("Va bene"); differenze dichiarate (§3.5) |
| Testi in italiano, massimo 2 righe e 30 caratteri | **verificato** per i testi nuovi (`testi.txt`, 176 riquadri) |
| Due testi vecchi del Fumaiolo con direzioni sbagliate e "non e" senza accento (dalla 0.66) | **non fatto**: insieme ai testi lunghi, nella versione delle barriere |
