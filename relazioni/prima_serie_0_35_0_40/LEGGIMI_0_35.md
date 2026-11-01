# Pokémon Romagna 0.35

Corregge il blocco della Rocca di Ravaldino e il fiume attraversabile a piedi all'argine: ora il quadro consente di completare la missione e l'acqua richiede Surf. Sono conservati tutti i contenuti della 0.34.

ROM: `build/Pokemon_Romagna_0_35.gba`. SHA-256: `9c3ac0a0bc607548f7c2b8f21b8d7ebcdfb2836e854670d317cb245b1786c2d9`.

## Compilazione completa

```sh
python -m pip install -r requirements.txt
python build35.py
python verify34.py
python test_contracts34.py
python verify35.py
```

Il builder ricostruisce 0.32, 0.33 e 0.34 con verifica dei rispettivi hash, poi applica la correzione 0.35. Non serve scaricare una base aggiuntiva: `base31.gba`, tutti i moduli e le risorse disponibili sono inclusi. È il progetto Python disponibile, non un decomp C di Smeraldo. `--from-verified34` è soltanto una scorciatoia di sviluppo.

Leggere `collaudo/RELAZIONE_0_35.md` e `collaudo/PUNTO_DI_RIPRESA_0_35.md`. Le altre relazioni descrivono versioni precedenti. I test `verify34`/`test_contracts34` verificano il livello ereditato; `verify35` verifica la correzione corrente. Il risultato della ricompilazione dall'archivio esportato è in `collaudo/ricompilazione_da_zip_0_35.json`.

Usare un salvataggio nativo `.sav` e una copia di sicurezza; evitare stati rapidi fra ROM differenti. La 0.35 non imposta flag di storia o vittorie nel salvataggio: il quadro segue i prerequisiti originali. Una partita continua completa fino al postgame resta da collaudare.
