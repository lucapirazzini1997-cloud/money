# Storia delle versioni

Dalla 0.35 alla 0.58. Gli SHA-256 sono quelli delle ROM conservate; le relazioni complete sono in `relazioni/`.

**Chi l'ha fatta:** "progetto" = costruita con i builder di questo progetto; "esterna" = ricevuta già fatta, senza sorgenti.

| Versione | SHA-256 | Base | Chi | Contenuto |
|---|---|---|---|---|
| 0.35 | `9c3ac0a0bc607548f7c2b8f21b8d7ebcdfb2836e854670d317cb245b1786c2d9` | 0.34 | progetto (prima serie) | Rocca di Ravaldino sbloccata, fiume all'argine solo con Surf |
| 0.36 | `4658aa1acfa3644d669b492f92b7b69a3ab86e2acd05c17cc2cc7c95b82e8acd` | 0.35 | progetto (prima serie) | Quadro del MIC di Faenza, registratore del mausoleo di Ravenna, indizi per Surf |
| 0.37–0.39 | — | — | progetto (prima serie) | Copertina con la foto dell'utente, introduzione animata, Cuore del Fumaiolo e Passo dei Draghi |
| 0.40 | `cfab4c0a7940c742b988427b2c8d7d48017c8005e8f5ea75465c92d4291d3f73` | 0.39 | progetto (prima serie) | Passaggio tra i coralli dell'Isola delle Rose. Pacchetto `Pokemon_Romagna_0_40_progetto_e_ROM.zip` |
| 0.41 | `4bea77c249c76dc22fd1701b5c045e37f838638cf73ee947b2ca82c8d418d036` | 0.40 | ricevuta | Base della 0.42 |
| 0.42 | `e9b5252552f23e4be52ca7037671545622a48ed69c6fbac22636278529daecb9` | 0.41 | progetto | Correzioni di testi (infermiera di Faenza, cartello della Foce del Savio) |
| 0.43 | `b70f62f7c367a67a22a6b0f25ac996c9283a68136350182b70caf28133e6b83d` | 0.42 | progetto | Sala giochi dietro il Bar Panama (flag 0x14b) |
| 0.44 | `f62af7e22095d85835ad9a66523ca2678d5040d34977ce5a83418f4b389f777a` | 0.43? | **esterna** | ROM dell'utente; analizzata in `RAPPORTO_ANALISI_0_44.md`. Da qui riparte tutto |
| 0.45 | `d23a091c0e0f3dd99b8971b1039871701c86ff8a037ebcfb50468e0ab5cc080e` | 0.44 | progetto | Correzioni sulla 0.44 (passo A) |
| 0.46 | `4078342ecbbd4e3a0e7baa9183f88f77496f0d1e1b16de1d53a706c19c0f466b` | 0.45 | progetto | Progressione Ravenna → Lugo → Faenza, Cava dei Tre Sigilli |
| 0.47 | `d26c0fd48f75fe1db4e36865f56b7ea9c9fd7914954d72e06ccfbaf45930122d` | 0.46 | progetto | Volo a Forlimpopoli, oggetti delle Befane, MOSSOMETRO, cartelli di Forlimpopoli, rivale di Rimini. **È `basi/rom047.gba`** |
| 0.48 | `2246619d46cd206623b353e0e17470cee56d0f7b94ef2d1bb51449ac597978b0` | 0.47 | progetto | Case ai cambi di luogo, campagne piene, bacche |
| 0.49 | `cefab56d0f5ff0641f1c2a22c6af5c70d1ea42029a11aea6b116562df1d8afcc` | 0.48 | progetto | Acqua non camminabile, ponti veri, Arco di Augusto, Centri Pokémon originali, Farfetch'd shiny |
| 0.50 | `e346182555162637e65f0998295d3922bda5955ce5ccc95c0b453cb0c26b5b04` | 0.49 | progetto | Passaggi allineati alla direzione di marcia, blocchi del Lido |
| 0.51 | `58e13a7bb40eaefb0564dc49d991116eb03a576066377e41dd0501bf8e523859` | 0.50 | progetto | Mirabilandia e Safari separati, cani leggendari, giostre con i cromatici. Audit completo in `AUDIT_0_51.md` |
| 0.52 | `d2412f7c250dd6568dce1a99ad7fc9236e9702ef188557eb269b88b9413aed4b` | 0.51 | progetto | Correzioni dell'audit (fase 1): Befane, Amo Buono, nome del rivale a inizio partita |
| 0.53 | `5a5f643482236881674d999c0758d308cfe895dadb29c78df078b1f6f728f142` | 0.52 | progetto | Interfaccia in italiano |
| 0.54 | `a06532552a9f79744d889e948d21d713043f29a32847e78d7febae9bbdc92906` | 0.53 | progetto | Blocco "nel nulla" dopo il rivale in laboratorio (gSelectedObjectEvent) |
| 0.55 | `2bfaa8a3ada9f8bbaa1112028f85f6d1d85e00d5bc71668e1444508b45e44ad6` | 0.54 | **esterna** | Monte Spaccato, Campagna Ravennate, Forlì/Lugo/Bagno di Romagna rifatte, acqua della Pianura. Dettaglio in `pezzo_055/modifiche_055.md`. Le ROM "Storia 1" e "Storia 2" sono identiche a questa |
| 0.56 | `b09eb6977ca7ceaf81be2a184d719ce6cc25229d2889e4cc3c4fa4714237495f` | 0.55 | progetto | Pennelli e Smeargle, tre codici e MT17, rosone e Pietralunare, nome del rivale per i salvataggi vecchi |
| 0.57 | `47f53668d8b5861956938cd041fb892e541b86031e4ac7b4337e8328923897c4` | 0.56 | progetto | Lotto 1: 671 KB di spazio recuperato (blocchi di zeri → zone dell'engine). Il gioco non cambia. Collaudata (con la 0.58) in mGBA e VBA-M, anche con le zone avvelenate |
| 0.58 | `47f53668d8b5861956938cd041fb892e541b86031e4ac7b4337e8328923897c4` (= 0.57) | 0.57 | progetto | Lotto 1: flag e variabili sicure (41 + 47), pool riordinato, registro allenatori e raggiungibilità che fanno fallire la build, cammino a piedi, `regressione.py`, budget. Stessa ROM della 0.57 |

## Note sulla catena

- **Due rami di builder.** I builder 0.42–0.43 partivano dalla 0.41. Dalla 0.45 si riparte dalla 0.44 dell'utente; dalla 0.48 il builder storico parte da `rom047.gba` (la 0.47) e da `base31.gba`, una ROM base da cui si leggono le risorse originali (grafica, mappe, tileset).
- **Riproducibilità oggi.** `build.py` rifà byte per byte la 0.54, la 0.55 (con la patch), la 0.56, la 0.57 e la 0.58. Nel builder storico ogni `buildXX.py` è cumulativo: `build54.py` contiene da solo tutte le modifiche dalla 0.47 alla 0.54. I file `build48.py` … `build53.py` restano come storia e per rifare le versioni intermedie.
- **Versioni senza sorgenti:** 0.44 e 0.55. Per entrambe esiste solo la ROM; per la 0.55 c'è anche la patch dalla 0.54 e l'elenco delle modifiche.
- **Versioni vecchie:** non si riparte dalla 0.40 o dalla 0.44 solo perché compaiono nei documenti. La versione di partenza è l'ultima di questa tabella.
