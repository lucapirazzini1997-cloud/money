# Pokémon Romagna 0.39

Aprire **Pokemon_Romagna_0_39.gba**, nella cartella principale dello ZIP.
La tua immagine resta la copertina; sono conservate le correzioni della 0.38
per il Cuore del Fumaiolo e il Passo dei Draghi.

## Correzione dell'uscita di Cervia

Gli alberelli sulla strada per la campagna tornano a bloccare il passaggio.
Nella 0.38 si potevano aggirare sul prato a destra: la 0.39 chiude quel varco
con gli alberi di confine. Serve usare Taglio su uno dei due alberelli.
Annullando Taglio o senza un Pokémon che conosca la mossa, la strada resta
chiusa. Uscendo dalla zona e rientrando, gli alberelli ricompaiono secondo
il comportamento nativo e tornano a bloccare la via.

## Salvataggi

Il formato dei salvataggi è invariato. Salvare dal menu, chiudere l'emulatore
e conservare una copia del proprio `.sav`; usare una copia chiamata
`Pokemon_Romagna_0_39.sav` accanto alla nuova ROM. Non trasferire stati rapidi
fra versioni differenti.

Il checkpoint di QA consigliato è
`collaudo/salvataggi_prova_0_39/resume39_celebi_postgame_verificato_native.sav`:
Lega vinta e Sala d'Onore registrata, Celebi catturato nel Box1, GS Ball
consumata e missione riconosciuta da Pino dopo riavvio. Squadra in salute. È una partita del tester e non deve sostituire involontariamente
il proprio salvataggio.

## Ricompilazione

Servono Python 3, le dipendenze di `requirements.txt` e GNU
`binutils-arm-none-eabi`.

```bash
python -m pip install -r requirements.txt
python build39.py
```

Toolchain in una cartella specifica:

```bash
python build39.py --toolchain /percorso/bin
```

La catena completa parte dalla base 0.31 inclusa. L'opzione
`--from-verified38` applica soltanto la nuova patch a una 0.38 già compilata,
verificandone l'hash. Il progetto è un builder Python con risorse e patch
binarie, non il progetto C originale di Smeraldo.

## Stato del collaudo

Leda sconfitta, ottava Medaglia Crinale e MT02 ottenute. Sub ricevuta dal
sommozzatore nella palestra dopo Leda e insegnata ad Azumarill. Geloraggio
insegnato a Swampert. Aldo prima della Via Vittoria sconfitto; attraversate
tutte e tre le sale e battuti i sei allenatori del percorso. Raggiunta la Lega,
provati ritorni e caricamento del salvataggio da avvio pulito. Sconfitti i
quattro Superquattro e, al secondo tentativo, Adriano. Registrata la squadra
nella Sala d'Onore, verificati titolo e salvataggio dopo due riavvii.
Verificati annullamento e fuga al santuario; Celebi catturato nella partita
continua e trasferito nel Box. GS Ball consumata; nessuna duplicazione dopo
riavvio, con dialoghi corretti del santuario e di Pino. I fondali delle Rose
e le missioni del postgame restano aperti.
Rapporto: `collaudo/RELAZIONE_0_39.md`.
