# Relazione 0.43: sala giochi dietro il Bar Panama

Base: ROM 0.42 (SHA-256 e9b52525…daecb9). Risultato: `Pokemon_Romagna_0_43.gba`, SHA-256 in `revision_0_43.json`. Patch BPS `Pokemon_Romagna_0_42_to_0_43.bps` (verificata con decoder indipendente: ricostruisce la 0.43, CRC corretti).

## Cosa cambia
- **Bar Panama (mappa 34.1)**: tessera (0,1) nel muro nord diventa una porta rossa passabile (metatile generale 0x21). Nuova warp indice 1 in (0,1) verso la sala (10.3, warp 0). Nuovo oggetto 6, un buttafuori in (0,2), nascosto dalla flag 0x14B. Barista (oggetto 1): al primo colloquio rivela la porta, regala il Portamonete se manca, imposta la flag 0x14B e fa sparire il buttafuori; poi continua con il suo script originale (missione 3 vittorie → 3 MT, intatta).
- **Sala giochi (mappa 10.3, ex Mauville)**: le due uscite (11,10) e (12,10) ora portano alla warp 1 del bar. Script d'ingresso della mappa rimosso (toccava flag di Mauville 0x86x/0x4dx). Sezione mappa portata a 0 (come il bar).
- **Testi**: tutti i testi della sala tradotti in italiano per sostituzione di puntatori (24 testi della sala + 2 testi comuni "Borsa piena"). Nessun inglese rimasto nei testi raggiungibili dalla sala. Menu di sistema (EXIT, CANCEL, "500 COINS") restano in inglese come nel resto del gioco.
- **Banco premi a decorazioni** (commesso 4): sostituito da uno script nuovo con premi in oggetti. Bambola (oggetto 5): sostituita da una battuta.
- **Cambio gettoni**: invariato (¥1000 → 50 gettoni, ¥10000 → 500 gettoni). Slot machine e roulette: script e speciali originali, invariati.

## Premi
Banco nuovo (sì/no a catena): 5 SUPER POTION 300 gettoni; 3 REVIVE 600; 1 RARE CANDY 2500; 1 PP UP 3000.
Banco MT (originale di Smeraldo, invariato): TM32 Double Team 1500; TM29 Psychic 3500; TM35 Flamethrower 4000; TM24 Thunderbolt 4000; TM13 Ice Beam 4000. Attenzione: Thunderbolt, Ice Beam e Flamethrower sono gli stessi MT che il barista regala dopo tre vittorie.

## Flag e variabili
- Nuova: 0x14B (libera: nessuno script di nessuna mappa la riferisce; audit su tutte le mappe più inventario base32).
- Riusate dagli script originali della sala: 0xE1 (gettoni regalati una sola volta), 0xE2 (bambola, ora non più usata). Non risultano usate dai contenuti raggiungibili di Romagna. Variabili: solo temporanee 0x4001, 0x4002, 0x8000–0x800D.
- Formato del salvataggio invariato.
- La mappa 33.2 condivide l'intestazione del bar e mostra le stesse modifiche (non raggiungibile).

## Spazio
Scritto a partire da 0x1E8F100 (prima zona libera). Elenco in `revision_0_43.json`. Byte modificati in aree preesistenti: 171, tutti puntatori a testi/script, due byte di intestazione, una tessera della mappa.

## Audit prima/dopo
- Warp rotte nelle mappe raggiungibili: 0 → 0. Andata e ritorno bar↔sala verificati su tutte e 4 le warp.
- Testi inglesi nelle mappe raggiungibili: 1 → 1 (resta quello della 16.10, non toccato). Nella sala: 0.
- Box a 3 righe senza pagina (scansione dei byte grezzi) sui testi della sala e del bar: 0. Restano i 2 falsi positivi della mappa 2.1.

## Provato
Solo controlli statici: decodifica degli script nuovi, puntatori nel file, warp, patch BPS, audit.

## NON provato (da fare in emulatore con tasti reali)
1. Se la porta rossa si vede e si attraversa; se il buttafuori sparisce subito dopo il discorso del barista e non reimpedisce il passaggio dopo il caricamento.
2. Animazione di uscita dalla porta quando si torna dalla sala (la tessera ha comportamento "porta animata").
3. Slot machine, roulette, cambio gettoni, Portamonete pieno.
4. Banco premi: acquisto, gettoni insufficienti, Borsa piena, rifiuto.
5. Banco MT: testi con nome MT e mossa.
6. Barista con Borsa piena (il Portamonete non deve andare perso e la porta non si apre).
7. Salvataggio dal menu, riavvio da avvio pulito, ripetizione del colloquio (nessun secondo Portamonete).
8. Musica della sala (id 426) e assenza del nome "Mauville" nella mappa/Pokénav.
9. Sprite del buttafuori (usato l'id 33, già presente nel bar): cambiarlo se non piace.
