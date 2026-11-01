# Pokémon Romagna 0.36

Questa revisione rende visibili il quadro del MIC di Faenza e il registratore
del mausoleo di Ravenna, rende specifici
gli indizi di Dario per il corso che assegna Surf e sostituisce un riferimento
obsoleto al «prossimo capitolo» con indicazioni per Ravenna. Conserva i
contenuti della 0.35 e non introduce nuove medaglie, flag o mappe.

ROM corrente: `build/Pokemon_Romagna_0_36.gba`.

SHA-256: `4658aa1acfa3644d669b492f92b7b69a3ab86e2acd05c17cc2cc7c95b82e8acd`.

## Ricompilazione completa

Occorrono Python 3, NumPy e Pillow, specificati in `requirements.txt`.

```sh
python -m pip install -r requirements.txt
python build36.py
python verify34.py
python test_contracts34.py
python verify35.py
python verify36.py
```

Il builder ricostruisce prima le versioni 0.32–0.35 e verifica gli hash delle
basi. `base31.gba`, risorse e moduli sono inclusi: non occorre procurarsi
un'altra base. È il builder Python del progetto disponibile, non il progetto
C originale di Pokémon Smeraldo.

`python build36.py --from-verified35` è una scorciatoia per lo sviluppo: controlla
comunque l'hash della ROM 0.35 già presente. La consegna viene verificata con la
compilazione completa, non soltanto con questa scorciatoia.

## Salvataggi

Conservare una copia del proprio `.sav`. Salvare dal gioco, chiudere l'emulatore,
poi usare una copia con lo stesso nome della nuova ROM, cambiando soltanto
l'estensione in `.sav`. Evitare stati rapidi `.ss0` tra versioni diverse.
I salvataggi inclusi sono copie di collaudo: non sostituire il proprio salvataggio
con quelli a meno di voler ripartire dal checkpoint del tester.

Leggere `collaudo/RELAZIONE_0_36.md` per le prove realmente eseguite e i limiti.
La partita continua non è ancora stata completata fino alla Lega sulla versione
finale. Autodromo cronometrato, passaporto, nuove rivincite e rifacimenti estesi
delle città restano interventi proposti, non contenuti aggiunti nella 0.36.
