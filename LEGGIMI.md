# Pokémon Romagna — progetto completo (versione 0.71)

Hack ROM di Pokémon Smeraldo ambientata in Romagna. Questa cartella contiene tutto per ricostruire la 0.71 byte per byte e sviluppare le versioni successive.

## Partire

```sh
python3 build.py
```

In circa tre minuti rifà 0.54 → 0.55 → 0.56 → 0.57 → 0.58 → 0.59 → 0.60 → 0.61 → 0.62 → 0.63 → 0.64 → 0.65 → 0.66 → 0.67 → 0.68 → 0.69 → 0.70 → 0.71 controllando lo SHA-256 di ogni tappa, poi rigenera i registri e fa i controlli del Lotto 1 (allenatori, raggiungibilità, budget). Il risultato è `out/Pokemon_Romagna_0_71.gba`, SHA-256 `17c5a9e607717a67975abefe65ed561113073725cd5d54564589bbe28dbf642a`. Servono Python 3 e numpy (Pillow per il collaudo).

**ROM:** il repository è pubblico, quindi le ROM non ci sono. Metti a mano `basi/rom047.gba` e `basi/base31.gba` (la build ne controlla lo SHA).

## Cosa leggere

1. `doc/PROGETTO.md`: struttura, catena di build, come si aggiunge una versione, trama città per città, leggendari ed eventi, indirizzi tecnici, lezioni imparate.
2. `doc/STORIA_VERSIONI.md`: tutte le versioni dalla 0.35 alla 0.71 con gli SHA.
3. `doc/COLLAUDO.md`: come si gioca in emulatore senza intervento umano.
4. `Prompt_Pokemon_Romagna_0_57.txt`: il prompt di sviluppo dalla 0.56, con i lotti di lavoro.
5. `registri/`: flag, variabili, strumenti, mappe, spazio libero, allenatori, raggiungibilità e risorse libere: da consultare prima di usarne di nuovi.
6. `relazioni/RELAZIONE_0_57.md` e `RELAZIONE_0_58.md`: il Lotto 1; `RELAZIONE_0_59.md`, `RELAZIONE_0_60.md` e `RELAZIONE_0_61.md`: Lotto 2 (cani; Kyogre e uccelli; Regi, Deoxys, Jirachi, Mewtwo). Lotto 3: da `RELAZIONE_0_62.md` a `RELAZIONE_0_69.md`, chiuso da `CHIUSURA_LOTTO_3.md` (SMEARGLE con squadra e PC pieni, guide di Ridracoli; nessuna ROM nuova). Lotto 4: `RELAZIONE_0_70.md` (casa del protagonista), `RELAZIONE_0_71.md` (esterno del laboratorio).

## Cartelle

| Cartella | Contenuto |
|---|---|
| `basi/` | `rom047.gba` (la 0.47) e `base31.gba` (risorse originali) |
| `storico_054/` | builder storico 0.47 → 0.54 |
| `pezzo_055/` | patch 0.54 → 0.55 ed elenco leggibile delle modifiche (la 0.55 non ha sorgenti) |
| `versioni/` | engine e un modulo per ogni versione dalla 0.56 |
| `registri/` | registri generati, controllo delle flag condivise e controlli del Lotto 1 (`controlli.py`) |
| `strumenti_rom/` | lettura di mappe, script e testi |
| `analisi/` | dump delle mappe, confronto fra ROM, spazio libero, raggiungibilità (grafo e a piedi), flag e variabili sicure |
| `collaudo/` | piloti per mGBA e VBA-M, libreria di gioco, `regressione.py`, test, savestate e risultati |
| `doc/` | documentazione |
| `relazioni/` | relazioni delle versioni passate (archivio) |
| `.claude/` | automazioni per Claude Code: `hooks/guardia.py` (blocca modifiche ai moduli di versioni consegnate e ai pezzi congelati, ROM nei commit, `pkill -f`), `hooks/avvio.sh` (all'avvio controlla le ROM di base e prepara gli emulatori), skill `romagna-tecnica` (riferimento tecnico) e `/consegna-versione` (checklist e `consegna.sh`: build, BPS verificata, zip ricostruito in cartella pulita, regressione), subagente `revisore-relazione` |
| `rom/` | patch BPS 0.55 → 0.56 → 0.57 → 0.58 → 0.59 → 0.60 → 0.61 → 0.62 → 0.63 → 0.64 → 0.65 → 0.66 → 0.67 → 0.68 → 0.69 → 0.70 → 0.71; nel pacchetto zip anche la ROM 0.71 pronta da giocare (nel repository pubblico le ROM non ci sono) |
