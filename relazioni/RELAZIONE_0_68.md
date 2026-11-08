# Pokémon Romagna 0.68: ostacoli (Lotto 3)

**Base:** 0.67, SHA-256 `aa5724473410d034397f8ac75583e6639659c0d23feda031538d99d739fbfe7b`.

**Risultato:** `Pokemon_Romagna_0_68.gba`, SHA-256 `d4a65459b46f01b9c23e84c593ebda2a1669c5cdf4602ac6825af81a996bd964`.
- Patch BPS 0.67→0.68: `rom/Pokemon_Romagna_0_67_to_0_68.bps` (58 byte), verificata riapplicandola (`consegna.sh`, log in `collaudo/risultati/068/consegna.txt`). Lo zip senza `out/` ricostruito in una cartella pulita rifà lo stesso SHA.
- Modulo: `versioni/v068_ostacoli.py`; bozza approvata: `bozze/ostacoli.py`.
- Lo SHA è in `build.py` dopo il collaudo (§5).
- **Salvataggi compatibili:** cambiano solo 9 caselle di due mappe; nessuna flag, variabile o testo nuovo. Due salvataggi veri della 0.67 (in casa e nella Pineta): §5.

## 1. Cosa è stato chiesto

- Prompt 0.57, Lotto 3: "Ostacoli: la TV che sbarra la strada appena entri in casa del protagonista; la Poké Ball irraggiungibile nella Pineta del Savio (rendila raggiungibile o spostala)."
- Bozza con le immagini prima e dopo (`bozze/ostacoli.py`): "Sì va bene".

## 2. Com'era nella 0.67

- **Casa del protagonista (1.0, 14×10):** è la casa della mamma che cura la squadra ("Prima di partire, riposati un po'"). Dalla porta di Lido di Savio (0.9, 8,16) si arriva sulla casella (9,9); la TV occupa (8–9, 7–8), quindi la casella sopra l'arrivo è bloccata e il primo passo in avanti non si fa: bisogna girare a destra. Letto dalla mappa (collisione) e confermato a tasti nella 0.68 sulla posizione nuova (§5); nella 0.67 non l'ho riprodotto a tasti.
- **Pineta del Savio (0.16):** la Poké Ball (oggetto 7, 36,24, flag 0x2D, una POZIONE) sta in una radura di sabbia (34–36, 22–24) chiusa da alberi e, in basso, da una siepe (34–36, 25). `analisi/percorso.py` con tutte le abilità (SURF, SPACCAROCCIA, TAGLIO, FORZA, CASCATA, bici, FLASH): **non raggiunta**. Le altre due Poké Ball della Pineta, (3,13) e (10,15), si raggiungono.

## 3. Modifiche (versioni/v068_ostacoli.py)

| Mappa | Casella | Prima | Dopo | Cosa |
|---|---|---|---|---|
| 1.0 | (6–7, 7–8) | pavimento | TV | la TV due caselle a sinistra |
| 1.0 | (8–9, 7–8) | TV | pavimento | il pavimento che c'era in (6–7, 7–8): il disegno si ripete ogni 2 caselle, resta allineato |
| 0.16 | (34,25) | siepe 0x3616 | erba bassa 0x3001 | la radura si collega al sentiero (33,25) |

- Le due mappe hanno blocchi e numero di layout propri (il modulo lo controlla su tutte le mappe): la modifica è sul posto, senza spazio nuovo.
- Il rifacimento completo dell'interno della casa resta nel Lotto 4.

## 4. Budget (da `out/rapporto_build.json`)

Invariato rispetto alla 0.67: 793 KB, 35 flag, 43 variabili, 67 strumenti, 10 allenatori liberi; posti per mappe nuove 24.75, 24.76 (più 34.10, 34.13, 34.18 con layout condiviso).

## 5. Collaudo (solo tasti; fixture dichiarate)

**Script e risultati**
- `collaudo/t68.py`, con `leg.py` e `vai.py`; risultati in `collaudo/risultati/068/` (json di ogni parte, `log_t68.txt`).
- ROM finale `d4a65459…d964` in mGBA e VBA-M (VBA-M riparte dal salvataggio vero fatto in mGBA).

**Fixture dichiarate:** solo la posizione di partenza (Lido di Savio 8,17 davanti alla porta; Pineta 19,5; per i vecchi salvataggi casa 9,9 e Pineta 33,25), scritta prima di un SALVA vero. Partenze da `prog_imola.ss`. `vai.py` cammina **senza abilità**.

| Prova | mGBA | VBA-M |
|---|---|---|
| Casa: Su dalla strada → dentro, su (9,9); Su → (9,8), dove prima c'era la TV | ok | ok |
| Casa: alle scale (12,2), in camera (1.1), di nuovo giù, alla porta; Giù → fuori a Lido di Savio (8,17) | ok | ok |
| Pineta: a piedi senza abilità da (19,5) alla radura (35,24) passando dalla siepe aperta; A sulla Poké Ball: "Hai ottenuto: POZIONE!", flag 0x2D a 1, la Ball sparisce | ok | ok |
| Vecchio salvataggio vero della 0.67 in casa (9,9), caricato nella 0.68: la TV si vede subito al posto nuovo (schermata `t68_vecchio67_casa_prima.png`); Su → (9,8) | ok | ok |
| Vecchio salvataggio vero della 0.67 nella Pineta (33,25): Destra → (34,25) (la siepe è aperta subito); POZIONE raccolta | ok | ok |

**Controlli statici**
- `confronto_067_068.txt`: fra 0.67 e 0.68 cambiano 18 byte, cioè le 9 caselle della tabella del §3; nessun byte fuori dai blocchi delle due mappe.
- `analisi/percorso.py` sulla 0.68 senza abilità: la Poké Ball (36,24) si raggiunge; in casa da (9,9) si arriva alle scale e alla mamma.
- Build: raggiungibilità "nuove 0, problemi 0".

### Regressione (`collaudo/regressione.py`, 0.68 contro 0.67)
Le 19 partenze (17 savestate in mGBA e il salvataggio vero in mGBA e VBA-M) girano, sono vive, la callback resta nella ROM e sono **uguali** alla 0.67 in tutti i punti di controllo (schermo, EWRAM, IWRAM, VRAM, tavolozze, OAM): nessuna partenza passa per le due mappe cambiate (`regressione.md`).

### Cosa non è verificato
- Nella 0.67 il blocco della TV è letto dalla collisione della mappa, non riprodotto a tasti.
- La schermata in VBA-M della casa: la posizione della TV è provata dal passo (9,9)→(9,8), non guardata.

## 6. Richieste

| Richiesta | Stato |
|---|---|
| TV che sbarra la strada in casa del protagonista | **corretto e verificato** (mGBA e VBA-M) |
| Poké Ball irraggiungibile nella Pineta del Savio | **corretto e verificato** (mGBA e VBA-M) |
| Mappe mostrate finite e approvate prima del modulo | **fatto** ("Sì va bene") |
| Due testi vecchi del Fumaiolo, "non e" senza accento, testo lungo della guida di Forlì | **non fatto**: nella prossima versione (barriere e testi lunghi) |
| Prossimo nel Lotto 3 | barriere (requisito, messaggio chiaro, via di ritorno) e testi lunghi; poi la consegna di Smeargle con squadra e PC pieni (non verificata dalla 0.56) |
