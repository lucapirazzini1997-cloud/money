# Pokémon Romagna 0.37

La schermata titolo classica è sostituita dalla fotografia fornita dall'utente.
È una schermata statica: l'immagine completa viene adattata a 240 × 160 pixel
con sottili bande laterali e colori GBA a 15 bit. START oppure A apre il menu.
L'introduzione animata che precede il titolo resta quella già presente.

La ROM da aprire è `Pokemon_Romagna_0_37.gba`, nella cartella principale.
I contenuti di gioco della 0.36 sono conservati. Questa revisione cambia solo
l'ingresso della schermata titolo e aggiunge codice e immagine in spazio libero.

## Ricompilazione

Servono Python 3, le dipendenze in `requirements.txt` e
GNU `binutils-arm-none-eabi` (assembler, linker, objcopy e nm).

```
python -m pip install -r requirements.txt
python build37.py
```

Per una toolchain in una cartella specifica:

```
python build37.py --toolchain /percorso/bin
```

Il builder riproduce le revisioni precedenti dalla base 0.31 inclusa e ne
controlla gli hash. Il progetto disponibile è un builder Python con risorse
e patch binarie, non il progetto C originale di Smeraldo.

Per sviluppo rapido, dopo una compilazione 0.36 già verificata, è disponibile
`--from-verified36`. La ROM completa è stata riprodotta anche senza questa opzione.

## Partita esistente

Salvare dal menu del gioco, chiudere l'emulatore e conservare una copia del `.sav`.
Usarne una copia chiamata `Pokemon_Romagna_0_37.sav` accanto alla nuova ROM.
Non trasferire stati rapidi tra versioni. I salvataggi di collaudo inclusi sono
del tester e non devono sostituire involontariamente la propria partita.

È stato provato il caricamento del checkpoint al Centro di Forlì con sette
medaglie, Ridracoli ripristinata, Forza appresa e usata, sei Pokémon validi e
curati. Verificata anche la persistenza di una sequenza di valvole parziale.
Il checkpoint di QA corrente è in
`collaudo/salvataggi_prova_0_37/resume37_ridracoli_completata_forli_native.sav`.
Non sono stati provati tutti
i salvataggi possibili. Il collaudo continuo fino alla Lega rimane aperto.

Per lo stato complessivo e le prove leggere `collaudo/RELAZIONE_0_37.md`.
