"""Scrive pezzo_055/modifiche_055.md da pezzo_055/modifiche_055.json (uscita di confronta.py) e registri/mappe.json."""
import json
from pathlib import Path
R = Path(__file__).resolve().parent.parent
j = json.load(open(R / 'pezzo_055/modifiche_055.json'))
names = json.load(open(R / 'registri/mappe.json'))
nm = lambda k: names.get(k, {}).get('nome', '?')
VOCI = dict(warp='uscite', coord='eventi a coordinate', oggetti='personaggi/oggetti', cartelli='cartelli', tileset='tileset',
            caselle_cambiate='caselle', script_blocchi='script', dim='dimensioni', regione='nome della zona')
L = ['# Cosa cambia la 0.55 rispetto alla 0.54', '',
     'La 0.55 non è stata fatta in questo progetto e non ha sorgenti. Questo file è generato da `analisi/confronta.py` '
     '(confronto strutturato 0.54 → 0.55) e da `analisi/modifiche_md.py`. Nel build la 0.55 si ottiene applicando '
     '`patch_054_055.bps` alla 0.54.', '',
     '## Mappe nuove', '', '| Mappa | Nome | Dimensioni | Uscite (x,y → mappa) | Personaggi/oggetti | Eventi a coordinate |',
     '|---|---|---|---|---|---|']
for m in j['mappe_nuove']:
    L.append('| %s | %s | %dx%d | %s | %d | %d |' % (m['mappa'], nm(m['mappa']), m['dim'][0], m['dim'][1],
             '; '.join('%d,%d → %d.%d' % tuple(w[:4]) for w in m['warp']), m['oggetti'], m['coord']))
L += ['', '## Mappe modificate', '', '| Mappa | Nome | Cosa cambia |', '|---|---|---|']
for m in j['mappe_cambiate']:
    det = []
    for k, v in m.items():
        if k == 'mappa': continue
        if k == 'warp':
            ch = sorted({'%d.%d' % (w[2], w[3]) for w in v['dopo']} - {'%d.%d' % (w[2], w[3]) for w in v['prima']})
            det.append('uscite' + (' (nuove verso %s)' % ', '.join(ch) if ch else ''))
        else: det.append(VOCI.get(k, k))
    L.append('| %s | %s | %s |' % (m['mappa'], nm(m['mappa']), ', '.join(det)))
L += ['', '## Allenatori modificati', '', ', '.join('%d %s' % (a['id'], a['nome']) for a in j['allenatori']), '',
      '## Strumenti', '', 'Nessuna modifica alla tabella degli strumenti.' if not j['strumenti'] else str(j['strumenti']), '',
      '## Codice e tabelle sotto 0x200000', '',
      'La 0.55 sposta due tabelle e aggiorna i puntatori che le usano:', '',
      '- tabella dei layout delle mappe: 0x09fd5634 → 0x095aa02c;',
      '- tabella dei nomi delle zone usata dalla mappa regionale: 0x099b69fc → 0x095cc080.', '',
      '| Da | A | Prima | Dopo |', '|---|---|---|---|']
for c in j['codice']: L.append('| %s | %s | `%s` | `%s` |' % (c['da'], c['a'], c['prima'], c['dopo']))
(R / 'pezzo_055/modifiche_055.md').write_text('\n'.join(L) + '\n')
print('scritto pezzo_055/modifiche_055.md')
