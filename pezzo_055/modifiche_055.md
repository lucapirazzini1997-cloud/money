# Cosa cambia la 0.55 rispetto alla 0.54

La 0.55 non è stata fatta in questo progetto e non ha sorgenti. Questo file è generato da `analisi/confronta.py` (confronto strutturato 0.54 → 0.55) e da `analisi/modifiche_md.py`. Nel build la 0.55 si ottiene applicando `patch_054_055.bps` alla 0.54.

## Mappe nuove

| Mappa | Nome | Dimensioni | Uscite (x,y → mappa) | Personaggi/oggetti | Eventi a coordinate |
|---|---|---|---|---|---|
| 35.101 | MONTE SPACCATO | 64x40 | 58,20 → 35.91; 4,17 → 35.92; 54,36 → 34.19 | 3 | 1 |
| 35.102 | CAMPAGNA RAVENNATE | 64x52 | 8,46 → 34.85; 58,8 → 34.94 | 3 | 60 |

## Mappe modificate

| Mappa | Nome | Cosa cambia |
|---|---|---|
| 34.19 | CESENA | uscite (nuove verso 35.101), script |
| 34.84 | FORLI | dimensioni, uscite, personaggi/oggetti, cartelli, tileset, caselle, script |
| 34.85 | FAENZA | uscite (nuove verso 35.102), cartelli, tileset, caselle, script |
| 34.94 | RAVENNA | uscite (nuove verso 35.102), cartelli, tileset, caselle, script |
| 34.111 | LUGO | dimensioni, uscite, personaggi/oggetti, cartelli, tileset, caselle, script |
| 35.0 | PONTE SANTERNO | eventi a coordinate, script |
| 35.18 | PASSO DEI DRAGHI | eventi a coordinate, script |
| 35.19 | BAGNO DI ROMAGNA | personaggi/oggetti, cartelli, tileset, caselle, script |
| 35.27 | VIA VITTORIA | eventi a coordinate, script |
| 35.34 | LEGA ROMAGNA | cartelli, tileset, caselle, script |
| 35.61 | FORLIMPOPOLI | nome della zona, script |
| 35.64 | FORLIMPOPOLI | nome della zona, script |
| 35.65 | FORLIMPOPOLI | nome della zona, script |
| 35.66 | FORLIMPOPOLI | nome della zona, script |
| 35.67 | FORLIMPOPOLI | nome della zona, script |
| 35.68 | FORLIMPOPOLI | nome della zona, script |
| 35.69 | FORLIMPOPOLI | nome della zona, script |
| 35.70 | VIA DEI CANALI | personaggi/oggetti, caselle, script |
| 35.71 | CAMPAGNE DI LUGO | personaggi/oggetti, eventi a coordinate, caselle, script |
| 35.72 | SENTIERO FAENZA-LUGO | personaggi/oggetti, eventi a coordinate, script |
| 35.73 | SENTIERO FAENZA-LUGO | personaggi/oggetti, eventi a coordinate, script |
| 35.79 | LIDO DI SAVIO | eventi a coordinate, script |
| 35.91 | CESENA | uscite (nuove verso 35.101), eventi a coordinate, script |
| 35.92 | CESENA | uscite (nuove verso 35.101), script |
| 35.96 | FORLI | eventi a coordinate, script |
| 35.97 | FORLI | eventi a coordinate, script |
| 35.98 | RAVENNA | eventi a coordinate, script |

## Allenatori modificati

198 ILARIO, 199 LEONIA, 200 PIERO, 207 MAURO, 208 GIADA, 209 DIEGO, 210 ELIA, 219 SILVIA, 220 NICO, 221 LUISA, 222 REMO, 228 ELSA, 229 CESARE, 230 MARTA, 231 BRUNO, 239 ALICE, 240 DINO, 241 ERICA, 242 RECLUTA, 250 RECLUTA, 305 VITTORIO

## Strumenti

Nessuna modifica alla tabella degli strumenti.

## Codice e tabelle sotto 0x200000

La 0.55 sposta due tabelle e aggiorna i puntatori che le usano:

- tabella dei layout delle mappe: 0x09fd5634 → 0x095aa02c;
- tabella dei nomi delle zone usata dalla mappa regionale: 0x099b69fc → 0x095cc080.

| Da | A | Prima | Dopo |
|---|---|---|---|
| 0x8490c | 0x8490f | `3456fd09` | `2ca05a09` |
| 0xb4edc | 0xb4edf | `fc699b09` | `80c05c09` |
| 0xb561c | 0xb561f | `fc699b09` | `80c05c09` |
| 0xb56bc | 0xb56bf | `fc699b09` | `80c05c09` |
| 0xb5744 | 0xb5747 | `fc699b09` | `80c05c09` |
| 0xb5860 | 0xb5863 | `fc699b09` | `80c05c09` |
| 0xb58c0 | 0xb58c3 | `fc699b09` | `80c05c09` |
| 0xb590c | 0xb590f | `fc699b09` | `80c05c09` |
| 0xb5980 | 0xb5983 | `fc699b09` | `80c05c09` |
| 0xb59c0 | 0xb59c3 | `fc699b09` | `80c05c09` |
| 0xb5a48 | 0xb5a4b | `fc699b09` | `80c05c09` |
| 0x13d0ac | 0x13d0af | `fc699b09` | `80c05c09` |
| 0x13d0e8 | 0x13d0eb | `fc699b09` | `80c05c09` |
| 0x197084 | 0x197087 | `fc699b09` | `80c05c09` |
| 0x1aa5b0 | 0x1aa5b3 | `3456fd09` | `2ca05a09` |
