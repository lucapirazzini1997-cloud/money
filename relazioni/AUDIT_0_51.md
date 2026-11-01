# Pokémon Romagna 0.51 — Audit (Fase 0)

ROM esaminata: `Pokemon_Romagna_0_51.gba` (SHA-256 `58e13a7b…3859`). Non ho modificato niente: questo è solo l'audit.

**Come ho lavorato:**
- **Analisi statica.** Ho letto tutti gli script delle mappe raggiungibili partendo dal Lido: 273 mappe e 2295 testi. Ho estratto allenatori, livelli, selvatici, flag e oggetti.
- **Partita vera in emulatore.** Nuova partita dal titolo, solo tasti e nessuna scrittura in RAM. Il nome del giocatore è "AAAAAAA", ho scelto TORCHIC e poi ho catturato uno SHROOMISH. Le lotte le gioca un mio programma che sceglie la mossa più efficace.

## 1. Problemi trovati

| # | Area | Problema | Gravità | Come l'ho visto |
|---|------|----------|---------|-----------------|
| 1 | Flag | **0x622** è usata sia dal Farfetch'd cromatico dell'Arco (0.49) sia da Regice (Camera di Brina). Se ne catturi uno, l'altro sparisce. | Alta | Statico |
| 2 | Flag | **0x627** è usata sia dall'AIPOM della Katun (0.51) sia da Registeel. Stesso effetto. | Alta | Statico |
| 3 | Flag | **0x623** e **0x628** (PONYTA e MARILL delle giostre, 0.51) sono anche le flag di due strumenti nelle Camere di Brina e di Metallo. | Media | Statico |
| 4 | Flag | **0x61d, 0x620, 0x621** (Cava dei Sigilli: strumento, Regirock, strumento) nascondono anche 3 oggetti a Cesena (34.19, gfx 86). | Media | Statico |
| 5 | Lingua | **Interfaccia di sistema in inglese**:<br>• lotta: "Foe MUDKIP used TACKLE!", "What will…", FIGHT/BAG/POKéMON/RUN, "It's super effective!", "gained … EXP. Points", "Delete a move…"<br>• menu START, zaino, OPZIONI, scheda allenatore, YES/NO, squadra ("Choose a POKéMON", SUMMARY/SWITCH)<br>• nomi di mosse e strumenti (TACKLE, POTION…), con nomi misti: "TAGLIO" ma "ROCK SMASH"<br>• messaggi sul campo ("There's nothing to CUT.") | Alta | Emulatore |
| 6 | Lingua | **Dialoghi ancora in inglese**, 61 testi:<br>• Club Cavo al 2° piano del Centro della Lega (40)<br>• Centro Pokémon della Lega (11)<br>• alberi di bacche a Cesena (6)<br>• pensione: Costa Adriatica e Route 117 (2)<br>• sale post-Lega (2) | Media | Statico |
| 7 | Nomi zona | Nomi rimasti in inglese:<br>• "ROUTE 117" sulla pensione (22.0)<br>• "FARAWAY ISLAND" e "NAVEL ROCK" sulle isole del post-Lega (nei testi sono ISOLA MIRAGGIO e ISOLA OMBELICO)<br>• la zona 87 (25.24–25.60, post-Lega) ha il nome vuoto | Bassa | Statico |
| 8 | Oggetti | Strumenti che non si ottengono in nessuna mappa raggiungibile:<br>• **Bici Cross**, quindi le aree Nord e Nord-ovest del Safari restano chiuse<br>• **Amo Buono** e **Super Amo**<br>• **MN Flash** e **MN Cascata**. Cascata servirebbe solo per la cascata del Safari Sud-est; non c'è nessuna grotta buia. | Media | Statico |
| 9 | Mappe | Mappe orfane:<br>• vecchio Safari: 34.115, 35.44, 35.45<br>• **34.18 "La Rocca" di Cesena**, già disegnata ma senza ingresso<br>• 34.10, sentiero delle Saline<br>• 34.13, vecchia scala della loggia di Cervia | Bassa | Statico |
| 10 | Trama | **Lugo è raggiungibile subito dopo la 5ª medaglia**, senza nessun evento del Team Emilia a Ravenna. Avevi deciso il contrario. Sono arrivato in palestra passando da Pianura, Ravenna, Via dei Canali e Campagne di Lugo. | Media | Emulatore |
| 11 | Difficoltà | Il **rivale a Forlì** (4 Pokémon, Lv 27–29) ti ferma appena entri da Via Emilia Ovest. Arrivi dopo 5 allenatori (Lv 22–26) e il Centro di Forlì non è raggiungibile prima della lotta. Con la squadra stanca il bot ha perso più volte di fila: è un muro. | Media | Emulatore |
| 12 | Difficoltà | **Saline di Cervia**: selvatici fino al Lv 15 prima della 1ª palestra (Lv 9). In Pineta sono Lv 2–7. | Media | Statico |
| 13 | Difficoltà | **RIVA** (1ª palestra, acqua): MARILL Lv 9 usa Ricciolscudo, Baccarancio e 2 Pozioni. TORCHIC da solo al Lv 15 perde. Con uno SHROOMISH in squadra la vittoria è facile. È una scelta di design, ma chi sceglie Fuoco è penalizzato. | Bassa | Emulatore |
| 14 | Difficoltà | **Capocolle** (Lv 18–22) viene dopo Rimini, la cui capopalestra è Lv 26: è un calo. | Bassa | Statico |
| 15 | Difficoltà | **Sentiero del Fumaiolo**: selvatici Lv 33–36 contro allenatori Lv 42–45. | Bassa | Statico |
| 16 | Gioco | Non c'è nessun modo di ricordare le mosse dimenticate. In partita il mio BLAZIKEN ha perso Doppiocalcio e non ha imparato Altocalcio: non si recuperano. | Media | Emulatore |
| 17 | Gioco (nota) | Le MT non si consumano. Credo sia voluto: lo segnalo solo. | — | Emulatore |

## 2. Curva dei livelli (allenatori, Pokémon più alto)

| Tappa | Allenatori | Selvatici | Capopalestra / rivale |
|-------|-----------|-----------|----------------------|
| Lido – Pineta | 4–12 | 2–7 | ALDO 4 |
| Cervia + Saline | 6–9 | 5–15 | **RIVA 9** |
| Campagna Cervese | 10–18 | 8–12 | ALDO 12 |
| Cesena / Cesenatico / Costa | 12–18 | 10–20 | **VIOLA 17** |
| Riviera – Rimini | 17–26 | 17–19 (acqua 34–38, dopo Surf) | ALDO 20, **AURELIO 26** |
| Capocolle – Forlimpopoli | 19–22 | 18–22 | — |
| Via Emilia Ovest – Forlì | 22–32 | 21–32 | ALDO 27–29, **IVANO 32** |
| Faenza | 32–40 | 28–32 | **ADA 40** |
| Pianura – Ravenna – Canali – Campagne di Lugo | 29–40 | 21–33 | — |
| Lugo | 38–43 | — | **ALIDA 43** |
| Ponte Santerno – Imola | 38–45 | — | ALDO 41, **RINO 45** |
| Fumaiolo – Passo dei Draghi | 42–50 | 33–42 | ALDO 45 |
| Bagno di Romagna | 44–48 | — | **LEDA 48** |
| Via Vittoria | 48–52 | 48–54 | ALDO 51 |
| Lega | 49–58 | — | Campione 58 |
| Post-Lega: San Marino, Imola Lv 61, KYOGRE Lv 70 a Rimini | 60–65 | 53–56 | — |

## 3. Partita in emulatore: dove sono arrivato

| Tappa | Esito | Note |
|-------|-------|------|
| Intro, laboratorio, starter, ALDO | OK | Scelta di TORCHIC, prima lotta vinta |
| Pineta (tunnel della 0.50) | OK | Guardie e tunnel funzionano |
| Saline e Team Emilia: ELIO, RITA, BRUNO, poi MUSA | OK | Senza questo RIVA non ti fa lottare: corretto |
| **Medaglia 1, RIVA** | OK al 2° tentativo | Puzzle delle valvole OK |
| Torre di Cervia, MN Taglio | OK | Serve il rapporto del MUSA |
| Campagna Cervese: albero da tagliare | OK | |
| Cesena, Cesenatico: Biblioteca, mercato, museo, chiave, grattacielo, DARIO | OK | La porta del grattacielo si apre con la chiave della curatrice |
| **Medaglia 2, VIOLA** | OK | |
| Rimini: Ada, capitaneria, corriere, Le Befane, ING. NERI | OK | La MN Spaccaroccia arriva solo tornando da Ada dopo NERI |
| **Medaglia 3, AURELIO** | OK | |
| Via Emilia Ovest: roccia, rivale a Forlì | OK dopo varie sconfitte | Vedi problema 11 |
| Forlì: municipio, Nello, museo, motore | OK | |
| **Medaglia 4, IVANO** | OK | |
| Faenza: referente, rilievi, 3 allenatori | OK | |
| **Medaglia 5, ADA** | OK al 2° tentativo | |
| Lugo (strada di campagna) | Arrivato | Vedi problema 10 |
| Medaglia 6, ALIDA | **Non vinta** | 4 sconfitte con 2 soli Pokémon (BLAZIKEN 48, BRELOOM 41). Il limite è la squadra del mio bot, non la ROM. |
| Medaglie 7–8, Lega | **Non giocate** | Ho solo controllato le catene di flag: ognuna si attiva in una mappa raggiungibile (Imola: Irene e manifesto; Bagno: santuari del Fumaiolo) |

**Fixture dichiarati:** nessuna scrittura in RAM e nessuno stato costruito a mano. Ho usato i savestate dell'emulatore solo per riprendere da dove ero arrivato. Dopo ogni sconfitta il gioco mi ha rimandato al Centro Pokémon come previsto e ho rigiocato.

**Non verificato:**
- medaglie 6–8 e Lega in emulatore;
- catture vere dei leggendari;
- salvataggio e ricarica dal menu del gioco: ho usato solo i savestate dell'emulatore;
- larghezza delle righe in pixel. Ho confrontato i testi con le righe più lunghe dei testi originali di Smeraldo e nessuno le supera; nessun riquadro supera le 2 righe.

## 4. Cosa propongo per la Fase 1, in ordine

1. **Flag** (problemi 1–4): flag nuove e libere per Arco e giostre, e un controllo nel builder che rifiuti qualsiasi flag già usata nella ROM. Salvataggi: chi ha già preso Farfetch'd o AIPOM si ritroverebbe Regice o Registeel nascosti. Rimetto visibili i Regi se la loro flag di cattura non risulta.
2. **Italiano**: tradurre i 61 dialoghi e i 3 nomi di zona. Interfaccia di lotta, menu e nomi di mosse e strumenti sono un lavoro grosso (tabelle e stringhe di sistema). Ti chiedo se lo vuoi tutto in italiano o solo i dialoghi.
3. **Bici Cross**: negozio con scelta Corsa/Cross. Più **Amo Buono** a Rimini (è già nella tua lista del porto) e **Super Amo** più avanti.
4. **Rivale rinominabile** e **NPC che fa ricordare e dimenticare le mosse**: Cesena o Forlì, raggiungibile presto.
5. **Lugo**: bloccare l'accesso finché non si finiscono gli eventi di Ravenna, come avevi deciso.
6. **Forlì**: far partire il rivale dopo un'infermiera, o curare la squadra prima della lotta.
7. **Saline di Cervia**: abbassare i selvatici a Lv 5–10 prima della 1ª medaglia.
