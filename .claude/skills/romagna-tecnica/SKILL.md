---
name: romagna-tecnica
description: Conoscenze tecniche di Pokémon Romagna (hack di Smeraldo) - opcode degli script, indirizzi RAM, API di versioni/engine.py, libreria di collaudo (leg.py, vai.py, percorso.py), regole delle fixture e trappole già incontrate. Usala prima di scrivere un modulo versioni/vXXX_*.py, uno script di collaudo, o di leggere/scrivere la RAM del gioco.
user-invocable: false
---

# Pokémon Romagna: riferimento tecnico

Le regole di processo stanno in `Prompt_Pokemon_Romagna_0_57.txt` (radice). Qui solo i fatti tecnici.

## Mappe
**Ogni mappa nuova o ridisegnata va mostrata all'utente finita (immagine con allenatori, cartelli, rocce, uscite) e si aspetta il sì prima di scrivere il modulo.** Bozze in `bozze/` (con `strumenti_rom/tela.py`).

## Catena di build
`basi/` → 0.54 (`storico_054/build54.py`) → 0.55 (`pezzo_055/patch_054_055.bps`) → moduli `versioni/vXXX_*.py`
(ognuno espone `apply(W) -> dict`) → `registri/genera.py` (controllo stretto delle flag condivise) →
`registri/controlli.py` (allenatori, raggiungibilità, budget in `out/rapporto_build.json`).
- `python3 build.py` completa; `python3 build.py --da 055` riparte da `out/Pokemon_Romagna_0_55.gba`.
- Una versione nuova: modulo nuovo + riga in `VERSIONI`. Lo SHA in `SHA` solo dopo il collaudo.
- I moduli con SHA sono congelati (l'hook `guardia.py` li blocca): si corregge con un modulo nuovo.
- Una flag condivisa fra mappe fa fallire `genera`: se è voluta va in `registri/flag_condivise_ammesse.json`.
- Mappe volutamente irraggiungibili: `registri/irraggiungibili_ammesse.json` (con motivo).

## versioni/engine.py
- `H(x)` u16 LE, `P(x)` puntatore ROM (`B = 0x08000000` + offset), `W.alloc(raw)`, `W.text(t, width=30)`.
- `Script(nome)`: `emit(b)`, `label(k)`, `jump(k, cond)`, `call(k, cond)`,
  `flag(x, label, present=True)` (salta se la flag è 1; `present=False` se è 0),
  `cmp(v, label, cond=1, var=0x800d)`, `set(f)`, `clear(f)`, `var(v, x)`,
  `msg(t)` (msgbox normale), `ask(t)` (sì/no → 0x800d), `checkitem/additem/removeitem/checkspace/giveitem`,
  `end()` = `6b 02` (releaseall + end), `save()` → offset dello script.
- Testi: `W.text` va a capo a 30 caratteri e mette 2 righe per riquadro; `\n\n` = nuovo paragrafo.
  **Massimo 2 righe per riquadro**, in italiano, maiuscolo per nomi di Pokémon, mosse e luoghi chiave.
- `engine.pool().flag(perché)` / `engine.variabili().var(perché)`: flag e variabili nuove solo dal pool, mai riusate.
- `add_object`, `add_bg`, `set_bg_script`, `live(key)` per le mappe; `W.rom.map(g, n)` → dict con `objects`, `events`.

## Opcode che servono spesso
lock `6a`, faceplayer `5a`, releaseall `6b`, end `02`, goto `05`, goto_if `06`, call `04`, return `03`,
checkflag `2b`, setflag `29`, clearflag `2a`, setvar `16`, compare `21`,
playmoncry `a1 specie(u16) modo(u16)`, waitmoncry `c5`,
setwildbattle `b6 specie(u16) livello(u8) strumento(u16)`, dowildbattle `b7`,
removeobject `53 id(u16)`, specialvar `26 var(u16) special(u16)`.
- Esito della lotta: `26 0d80 b700` → 0x800D: **1 = KO/vinta, 4 = fuga, 7 = catturato**
  (Ruggito del selvatico chiude con un esito diverso da 1 e 7: va trattato come fuga).
- Flag 0x8C1 (FLAG_SYS_CTRL_OBJ_DELETE): impostarla attorno a `dowildbattle` perché l'oggetto resti dopo fuga/KO.
- Script di campo: roccia 0x290B6B (serve 0x869), albero TAGLIO 0x290A67, masso FORZA 0x290C74 (serve 0x86D).
  Grafiche oggetto: 86 roccia, 82 albero, 87 masso.
- Flag di storia: medaglie 0x867–0x86E (0x86E = 8ª, consegna anche SUB), Lega vinta 0x864.

## Salvataggi e compatibilità
- SaveBlock1 conserva i template degli oggetti **con il puntatore allo script**: un salvataggio fatto dentro la mappa
  usa il vecchio script finché la mappa non si ricarica. Quindi il vecchio script si sovrascrive con
  `05 <puntatore al nuovo>` (5 byte), dopo aver verificato i byte vecchi con un `assert`.
- `LoadSaveblockObjEventScripts` copia 64 puntatori anche oltre il numero di oggetti: differenze innocue in EWRAM.
- Continua ripristina anche l'oggetto del giocatore da SaveBlock1: una fixture di posizione deve scrivere sia la
  posizione (mappa a +9/+10) sia le coordinate dell'oggetto (+0xC/+0x10/+0x14, con scarto +7).

## RAM (Smeraldo)
| Cosa | Indirizzo |
|---|---|
| avatar giocatore (byte 5 = id oggetto, flag & 8 = in SURF) | 0x02037590 |
| oggetti evento (passo 0x24) | 0x02037350 |
| testo dei messaggi sul campo | 0x02021FC4 |
| testo della lotta (`pl.msg`) | 0x02022E2C |
| callback principale (cb2) | 0x030022C4 |
| cb2 sul campo | 0x08085D9D, 0x08085D91 |
| cb2 in lotta | 0x080383E9 |
| cb2 di transizione | 0x08036F75, 0x08086035 |
| menu azioni di lotta (`== pl.ACT`) | 0x03005D60 |
| cursore del menu START (SALVA = 4) | 0x0203760E |
| squadra (100 byte a testa, sottostrutture cifrate, `pl.ORDERS`) | 0x020244EC |
| tasca Ball | sb1 + 0x650 (quantità in XOR con la chiave a sb2 + 0xAC) |

## Comportamenti delle caselle (analisi/percorso.py)
cascata 0x13, sporgenze 0x38–0x3B, frecce di uscita 0x62–0x65 (si sta sulla casella e si spinge),
immersione da 0x11/0x12/0x14. Connessioni: dir 5 = immersione (dalla mappa in superficie),
dir 6 = risalita (dalla mappa sott'acqua). In gioco: A sull'acqua profonda per immergersi,
**B sott'acqua per risalire**, poi "sì".

## Collaudo (solo tasti; fixture dichiarate)
- `collaudo/h` = mGBA pilotato; `collaudo/vb.py` = VBA-M (libretro, `VBAM=1`).
  `vb.py` scrive il `.sav` solo se è cambiato: lavora sempre su copie temporanee (`leg_tmp.sav`), mai sul master.
- `analisi/percorso.py ROM g.n:x,y --abilita surf,forza,... --flag ... --meta ...`: ricerca di percorso realistica
  (stati `(mappa, x, y, z, surf)`; abilità surf, spacca, taglio, forza, cascata, corsa, cross, sub, flash).
- `collaudo/vai.py`: `vai(g, mappa, x, y, ab)` naviga a tasti ripianificando dalla posizione vera
  (rocce, massi, surf, sub, uscite, lotte selvatiche con fuga). `stato(g)`, `ow(g)`, `guarda(g, x, y)`.
  `vai.FLAG_ALZATE` (dalla 0.63): flag da dare per alzate al pianificatore quando uno script di mappa nasconde oggetti
  (percorso.py non legge gli script di mappa). VBA-M non legge i savestate di mGBA: si riparte da un `.sav` fatto in mGBA.
- `collaudo/leg.py`: `parla`, `presente`, `testo`, `chiudi_testi` (**solo B**: con A si riparla al leggendario),
  `menu_lotta`, `fuggi`, `ko`, `salva`, `ricarica(sav, rom)`, `specie_squadra`, `leggi`;
  fixture: `fixture` (5 MASTER BALL), `fixture_surf`, `fixture_mossa`, `fixture_flag`, `fixture_posizione`.
- Procedura fixture: scritture in RAM dichiarate → SALVA vero in gioco → titolo → Continua. Mai come prova di una
  vittoria o di uno sblocco.
- Alla domanda "Usare il prossimo Pokémon?" (testo con 'prossimo') rispondere A, non fuggire.
- Un savestate fatto con un'altra ROM conserva i vecchi puntatori degli script: prima del test uscire e rientrare
  dalla mappa.
- `collaudo/regressione.py ROM --rif ROM_PRECEDENTE`: 17 savestate in mGBA + salvataggio vero in mGBA e VBA-M.
- Per fermare un emulatore: `ps aux | grep ... | awk '{print $2}' | xargs kill` (mai `pkill -f`: chiude anche la shell).
