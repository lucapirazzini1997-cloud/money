# Pokémon Romagna 0.38

Aprire **Pokemon_Romagna_0_38.gba**, nella cartella principale del pacchetto.
La copertina resta l'immagine fornita dall'utente, già introdotta nella 0.37.
START/A apre il menu dopo l'introduzione animata.

Questa versione corregge due blocchi trovati durante la partita continua:
accesso al Cuore del Fumaiolo dopo Bassi e accesso al Passo dei Draghi dopo
Groudon. Le guide necessarie al trasferimento restano disponibili; i requisiti
di storia restano gli stessi. I ritorni collocano il giocatore davanti alla
guida, su una casella libera.

## Salvataggi

Salvare dal menu del gioco, chiudere l'emulatore e conservare una copia del
proprio `.sav`. Usare una copia chiamata `Pokemon_Romagna_0_38.sav` accanto
alla nuova ROM. La compatibilità è stata provata con salvataggi nativi della
0.37 prima e dopo Bassi. Non trasferire stati rapidi fra ROM diverse.

Il checkpoint di collaudo consigliato è
`collaudo/salvataggi_prova_0_38/resume38_bagno_prima_ottava_native.sav`:
Centro Pokémon di Bagno, sette medaglie, Fumaiolo concluso, Groudon nel Box1,
sei Pokémon curati. È una partita del tester: non sostituire involontariamente
il proprio salvataggio con questo file.

## Ricompilazione

Servono Python 3, le dipendenze di `requirements.txt` e GNU
`binutils-arm-none-eabi`.

```bash
python -m pip install -r requirements.txt
python build38.py
```

Con una toolchain in un percorso specifico:

```bash
python build38.py --toolchain /percorso/bin
```

Il comando completo ricostruisce la catena dalla base 0.31 inclusa.
`--from-verified37` applica soltanto la nuova patch a una 0.37 già compilata,
controllandone l'hash. Il progetto è un builder Python con risorse e patch
binarie, non il progetto C originale di Smeraldo.

## Collaudo

Autodromo completato, Aldo nell'Appennino sconfitto, nodi e Bassi superati,
fuga e nuovo incontro con Groudon verificati, Groudon catturato, Bagno raggiunta.
Il salvataggio finale è stato riaperto da avvio pulito. L'ottava palestra,
Via Vittoria, Lega e postgame restano da completare nella partita continua.
Dettagli e limiti: `collaudo/RELAZIONE_0_38.md`.
