"""Riassunto dei json di t66 (mGBA e VBA-M) per la relazione: una riga per prova con i campi che contano."""
import json, os, sys
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'play')
def corto(v, n=160):
    s = json.dumps(v, ensure_ascii=False); return s if len(s) <= n else s[:n] + '...'
for parte in ('aldo', 'sentiero', 'santuario', 'ridracoli', 'crea65', 'vecchio65'):
    for suf in ('', '_vbam'):
        f = os.path.join(P, 't66_%s%s.json' % (parte, suf))
        if not os.path.exists(f): continue
        print('==', parte, 'VBA-M' if suf else 'mGBA')
        for k, v in json.load(open(f)).items():
            if isinstance(v, dict):
                w = {kk: v[kk] for kk in ('ok', 'arrivo', 'pos', 'testi', 'lotta', 'vinta', 'cattura', 'posizioni', 'fixture_dopo_sconfitta',
                                         'var_nuova', 'groudon_fatto', 'groudon_ogg', 'bassi', 'strumento_tevere', 'in_lotta', 'oggetti') if kk in v}
            else: w = v
            print('  %-24s %s' % (k, corto(w, int(sys.argv[1]) if len(sys.argv) > 1 else 220)))
