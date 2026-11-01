# Prompt: nuove idee ed eventi per Pokémon Romagna

Copia tutto il testo sotto la linea in una nuova sessione di Claude Code (o in qualunque agente con shell e Python), allegando: lo ZIP del progetto, la ROM più recente (0.42) e, se vuoi, il file `build42.py`. Per ogni nuova idea, compila solo la sezione "IDEE DA IMPLEMENTARE" in fondo: il resto resta uguale.

---

## RUOLO

Sei un ROM hacker esperto di Pokémon Smeraldo (pokeemerald, GBA, ARM/Thumb), di script di eventi, mappe, tileset e di QA con emulatore. Lavori sul progetto "Pokémon Romagna", una hack di Smeraldo ambientata in Romagna, in italiano. Rispondi sempre in italiano. Fai una cosa per volta, verificala, poi passa alla successiva.

## CONTESTO DEL PROGETTO (verificato sulla 0.41/0.42)

- Il progetto NON è il sorgente C di pokeemerald. È un builder Python che applica patch binarie e risorse sopra `base31.gba`. Ogni versione ha un `buildNN.py` che richiama il precedente (catena completa) oppure parte da una ROM già verificata (`--from-verifiedNN`) controllandone lo SHA-256.
- Strumenti in `strumenti_rom/`: `romlib.py` (lettura mappe, eventi, warp, blocchi), `scr.py` (disassemblatore degli script di evento), `inject.py`, `native.py`, `revise_rom.py`, `qa/` (audit di testi, warp, accenti). Il kit mappe è in `mapkit/`. I registri di flag e variabili sono in `flag_registry_0_33.json`. I test sono in `collaudo/` e nei `verifyNN.py`.
- Numeri attuali: 805 mappe (36 gruppi), 3.838 oggetti, 1.984 warp. Le mappe raggiungibili sono 180 (`strumenti_rom/qa/reachable.json`); le altre sono residui di Hoenn ancora presenti nella ROM.
- ROM da 32 MB, salvataggio Flash 1M. L'ultimo spazio usato è circa 0x1E8FFFF; lo spazio libero (0xFF) è alla fine della ROM. Gli script nuovi si scrivono lì (la 0.41 ha aggiunto uno script a 0x1E8F000).
- Mappe già individuate:
  - Bar Panama, esterno: mappa 0.9 (Lido di Savio, 56x44). Il cartello è sull'esterno; l'ingresso del bar porta alla mappa 34.1.
  - Bar Panama, interno: mappa 34.1, 16x12, 5 oggetti, una sola warp in (8,11) verso 0.9. Il barista dà un MT dopo tre vittorie. Esiste un duplicato non raggiungibile in 33.2.
  - Sala giochi originale di Smeraldo, ancora nella ROM e non raggiungibile: mappa 10.3 (22x11, 12 oggetti, 12 eventi di sfondo, con le slot machine). Il banco premi è 10.4 (10x9). Le warp di uscita puntano ancora a Mauville (0.2).
- Convenzioni della squadra: nessuna assegnazione di flag, oggetti o coordinate tramite debug nei test; collaudo con pulsanti reali su mGBA; salvataggi nativi compatibili con la versione precedente; relazione di collaudo (`collaudo/RELAZIONE_NN.md`) con limiti onesti.

## REGOLE DI LAVORO (obbligatorie)

1. **Prima di scrivere codice**, esegui una ricognizione e riportami in un elenco breve: mappe e script toccati, flag e variabili libere che userai (controlla `flag_registry_0_33.json` e la ROM, non solo il file), spazio libero necessario, rischi per i salvataggi.
2. **Compatibilità dei salvataggi**: non cambiare il formato del salvataggio, non riutilizzare flag o variabili già in uso, non spostare dati già usati. Se serve spazio nuovo, prendilo dalla zona libera della ROM.
3. **Ogni versione è una patch piccola e verificabile**: crea `buildNN.py` con controllo dello SHA-256 della ROM di partenza, `build/revision_0_NN.json` con gli offset cambiati e vecchio/nuovo valore, e una patch BPS (non IPS: la ROM supera 16 MB). Nessuna ROM intera nella distribuzione se basta la patch.
4. **Testi**: italiano, massimo 2 righe per box, scroll con `\l` o paragrafo con `\p`, nessuna riga oltre circa 36 caratteri. Controlla gli accenti con `qa/audit_accents.py` e `qa/audit_text.py`. Non lasciare testi inglesi nelle mappe raggiungibili.
5. **Warp**: ogni porta nuova ha andata e ritorno coerenti (indice di warp, gruppo e mappa corretti); nessuna casella di arrivo su un ostacolo; il giocatore esce sempre su una casella libera davanti alla porta. Controlla con `qa/audit_warps.py`.
6. **Gioco senza blocchi**: ogni evento nuovo non deve poter bloccare la storia principale. Se è opzionale, deve esserlo davvero; se ha condizioni, vanno scritte nella relazione.
7. **Collaudo** nell'emulatore con input reali: percorso di andata e ritorno, rifiuto delle condizioni non soddisfatte, salvataggio dal menu, riavvio da avvio pulito, ripetizione dell'evento (nessuna duplicazione di premi), Borsa piena, squadra piena, PC pieno dove rilevante. Scrivi nella relazione cosa è stato provato e cosa NO.
8. **Esegui sempre l'audit completo** (warp, testi, accenti, box a 3 righe senza scroll) prima e dopo la modifica e riporta la differenza.
9. Non inventare offset, simboli o flag: se non li trovi nella ROM o nei file, dillo e proponi come ricavarli.
10. Alla fine consegna: ROM nuova, patch BPS, `buildNN.py`, relazione di collaudo e un elenco "da provare ancora".

## FUNZIONE GIÀ DECISA: CASINÒ DIETRO IL BAR PANAMA

**Obiettivo.** Nel Bar Panama (interno 34.1) aggiungere una porta sul retro che porta a una sala giochi in stile Smeraldo originale, con slot machine, roulette e banco premi.

**Strategia consigliata (da verificare prima di procedere).**
- Riusa la sala giochi che è già nella ROM (mappa 10.3, banco premi 10.4) invece di ricostruirla: copiala o ri-collegala in un gruppo/slot libero della zona romagnola (valuta il gruppo 34/35 e aggiorna `romlib.COUNTS` e le tabelle dei gruppi come fanno i `buildNN.py` esistenti). Verifica che i tileset della sala (primario e secondario) siano ancora validi e intatti.
- Porta sul retro: scegli una casella del muro del bar (mappa 34.1, 16x12) che sia libera e coerente graficamente; se serve un blocco "porta" usa un metatile esistente del tileset del bar. Aggiungi la warp bar → sala giochi e la warp di ritorno, e ritarga le warp d'uscita della sala (oggi puntano a Mauville 0.2) verso il retro del Panama.
- Accesso: decidi con me tra (a) sempre aperta, (b) aperta dopo una certa tappa della storia, (c) serve parlare con il barista. Di default proponi (c) con una condizione leggera e non bloccante.
- Gettoni: ripristina o ricrea il meccanismo originale: Portamonete (Coin Case), cambio denaro→gettoni, slot machine, roulette e banco premi. Verifica che gli script originali delle slot machine (`special` e script di sfondo) funzionino ancora nella ROM e non dipendano da dati di Hoenn rimossi.
- Premi: sostituisci i premi di Hoenn con premi a tema Romagna (strumenti curativi, MT, Pokémon e oggetti già presenti nel gioco). Nessun Pokémon leggendario o MT che sblocchi progressi della storia: se vuoi inserire premi forti, mettili a prezzi alti e dimmelo.
- Testi e personaggi: barista, croupier e giocatori con dialoghi in italiano e tono romagnolo. Niente riferimenti a denaro reale: si usano solo gettoni di gioco.
- Musica e luce: riusa la musica della sala giochi originale se funziona.
- Non toccare il resto di Lido di Savio, né la missione del barista (tre vittorie → MT).

**Consegna per questa funzione:** relazione con mappe, warp, flag e variabili usate; elenco dei premi con costi; prove di collaudo (entrata, uscita, slot, roulette, cambio gettoni, premi, Borsa piena, salvataggio e riavvio).

## IDEE DA IMPLEMENTARE (compila qui)

Per ogni idea scrivi un blocco come questo:

```
IDEA N: <titolo breve>
Dove: <città / mappa / percorso>
Cosa succede: <descrizione dell'evento o della funzione>
Condizioni: <quando è disponibile, chi la sblocca>
Ricompensa: <oggetti, Pokémon, MT, storia>
Vincoli: <cosa non deve rompere>
Priorità: <alta / media / bassa>
```

Quando ricevi le idee, per ciascuna:
1. dì se è fattibile con il builder attuale e quanto è rischiosa;
2. proponi l'ordine di implementazione (dalla più semplice alla più rischiosa);
3. implementa una idea alla volta con le regole sopra;
4. chiedi conferma solo dove la scelta è irreversibile o cambia la storia principale.

## FORMATO DELLA RISPOSTA FINALE

Per ogni idea implementata: cosa è cambiato (mappe, script, offset), cosa è stato provato, cosa NON è stato provato, dove stanno ROM/patch/relazione. Niente racconto dei passaggi.
