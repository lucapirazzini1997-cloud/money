---
name: consegna-versione
description: Checklist di consegna di una versione di Pokémon Romagna (BPS verificata, zip ricostruito in cartella pulita, SHA in build.py, relazione, documenti, regressione, commit e invio). Uso - /consegna-versione 061
disable-model-invocation: true
argument-hint: "<versione a tre cifre, es. 061>"
---

# Consegna della versione $ARGUMENTS

Segui i passi in ordine. Fermati al primo che fallisce e dillo all'utente con l'uscita del comando.

1. **Collaudo finito.** Tutti i punti del §6 del prompt sono provati su mGBA e VBA-M, con i risultati in
   `collaudo/risultati/$ARGUMENTS/`. Ciò che è solo letto nel codice va nella relazione come "non verificato".
2. **SHA in `build.py`.** Aggiungi `'$ARGUMENTS': '<sha>'` in `SHA` con il commento `# collaudo: collaudo/risultati/$ARGUMENTS`.
3. **Passi automatici**: `sh .claude/skills/consegna-versione/consegna.sh $ARGUMENTS <cartella di appoggio>`
   (usa la cartella scratchpad della sessione). Ricostruisce da zero, crea e verifica la BPS, crea lo zip senza
   `out/`, lo ricostruisce in una cartella pulita controllando lo SHA, e lancia `collaudo/regressione.py` contro la
   versione precedente.
4. **Relazione** `relazioni/RELAZIONE_0_xx.md` in italiano, con la struttura delle precedenti:
   SHA di base e risultato, BPS, causa, modifiche, budget (stima prima / usato / resta, da `out/rapporto_build.json`),
   collaudo con fixture dichiarate, riproduzione sulla versione precedente, vecchio salvataggio, regressione,
   "Cosa non è verificato", tabella delle richieste del prompt con gli stati
   segnalato / riprodotto / corretto / verificato.
5. **Revisione**: lancia il subagente `revisore-relazione` sulla relazione e correggi ciò che segnala.
6. **Documenti**: `doc/PROGETTO.md` (stato, §3, budget), `doc/STORIA_VERSIONI.md`, `doc/COLLAUDO.md`, `LEGGIMI.md`
   (tabella delle patch), registri rigenerati dalla build.
7. **Commit e push** sul branch di lavoro (nessuna ROM: la guardia la blocca), messaggio `0.xx: Lotto N, ...`.
8. **Invio** con SendUserFile: ROM, BPS, zip e relazione (percorsi stampati dallo script).
9. **Riassunto breve in italiano** in chat: causa, cosa cambia nel gioco, prove, fixture, non verificato, budget, SHA.
