# Pokémon Romagna — progetto completo (versione 0.56)

Hack ROM di Pokémon Smeraldo ambientata in Romagna. Questa cartella contiene tutto per ricostruire la 0.56 byte per byte e sviluppare le versioni successive.

## Partire

```sh
python3 build.py
```

In circa un minuto rifà 0.54 → 0.55 → 0.56 controllando lo SHA-256 di ogni tappa, poi rigenera i registri. Il risultato è `out/Pokemon_Romagna_0_56.gba`, SHA-256 `b09eb6977ca7ceaf81be2a184d719ce6cc25229d2889e4cc3c4fa4714237495f`. Serve solo Python 3 (Pillow per il collaudo).

## Cosa leggere

1. `doc/PROGETTO.md`: struttura, catena di build, come si aggiunge una versione, trama città per città, leggendari ed eventi, indirizzi tecnici, lezioni imparate.
2. `doc/STORIA_VERSIONI.md`: tutte le versioni dalla 0.35 alla 0.56 con gli SHA.
3. `doc/COLLAUDO.md`: come si gioca in emulatore senza intervento umano.
4. `Prompt_Pokemon_Romagna_0_57.txt`: il prompt di sviluppo dalla 0.56, con i lotti di lavoro.
5. `registri/`: flag, variabili, strumenti, mappe e spazio libero della 0.56, da consultare prima di usarne di nuovi.

## Cartelle

| Cartella | Contenuto |
|---|---|
| `basi/` | `rom047.gba` (la 0.47) e `base31.gba` (risorse originali) |
| `storico_054/` | builder storico 0.47 → 0.54 |
| `pezzo_055/` | patch 0.54 → 0.55 ed elenco leggibile delle modifiche (la 0.55 non ha sorgenti) |
| `versioni/` | engine e un modulo per ogni versione dalla 0.56 |
| `registri/` | registri generati e controllo delle flag condivise |
| `strumenti_rom/` | lettura di mappe, script e testi |
| `analisi/` | dump delle mappe, confronto fra ROM, controlli dell'acqua |
| `collaudo/` | piloti per mGBA e VBA-M, libreria di gioco, test e savestate |
| `doc/` | documentazione |
| `relazioni/` | relazioni delle versioni passate (archivio) |
| `rom/` | ROM 0.56 pronta da giocare e patch BPS 0.55 → 0.56 |
