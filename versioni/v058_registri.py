"""Versione 0.58 - Lotto 1, seconda parte: registri e controlli. Non cambia la ROM (stesso SHA della 0.57).

Cosa fa nella build:
  - dichiara le 41 flag 0x20-0x4FF e le 47 variabili verificate sicure (analisi/flag_sicure.py lanciato
    sulla 0.57: nessuno script della ROM, nessun oggetto nascosto, nessuna citazione nel codice o nei dati di
    Smeraldo, nessuna chiamata a FlagSet/FlagGet/FlagClear o VarGet/VarSet/GetVarPointer con quel numero);
  - le ricontrolla sulla ROM che sta costruendo (script e oggetti nascosti, codice di Smeraldo dal registro
    registri/flag_smeraldo.json, chiamate nel codice);
  - riordina il pool delle flag (engine.pool): prima queste 41, poi le flag di allenatore rimaste, tolte quelle
    degli allenatori che combattono in qualunque script (anche con id locale diverso da 0, che la scansione
    della 0.56 non vedeva) e di quelli citati dal codice di Smeraldo (tabella delle rivincite, Pokenav...);
  - apre il pool delle variabili (engine.variabili) per i contatori delle missioni a piu' passi.
I controlli che fanno fallire la build (allenatori, raggiungibilita') sono in registri/controlli.py.
"""
import sys, json, collections
from pathlib import Path
import engine as E
ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / 'analisi'), str(ROOT / 'registri')]

FLAG_SICURE_058 = [0x22, 0x28, 0x2c, 0x34, 0x35, 0x3c, 0x3e, 0x45, 0x96, 0x1ab, 0x1da, 0x1de, 0x1df, 0x1e0, 0x1e1,
                   0x1e2, 0x1e3, 0x278, 0x296, 0x297, 0x298, 0x299, 0x29a, 0x2ae, 0x2b7, 0x2b8, 0x2b9, 0x2ba, 0x2bb,
                   0x2d9, 0x339, 0x467, 0x468, 0x470, 0x472, 0x4b4, 0x4dd, 0x4de, 0x4df, 0x4ec, 0x4ed]
VAR_SICURE_058 = [0x4020, 0x404e, 0x4052, 0x4055, 0x4056, 0x4059, 0x405b, 0x405c, 0x405f, 0x4061, 0x4062, 0x4064,
                  0x4065, 0x4066, 0x4067, 0x4068, 0x406a, 0x406b, 0x406c, 0x406d, 0x406e, 0x4070, 0x4073, 0x4075,
                  0x4076, 0x4077, 0x4078, 0x4079, 0x407a, 0x407c, 0x407d, 0x407e, 0x407f, 0x4080, 0x4081, 0x4083,
                  0x408b, 0x4091, 0x409b, 0x409d, 0x40a1, 0x40a8, 0x40b8, 0x40bb, 0x40f9, 0x40fa, 0x40fb]


def apply(W):
    import flag_sicure as F, controlli as C
    d = bytes(W.d); R = W.rom
    sm = json.load(open(F.SMERALDO_JSON))
    # flag: ricontrollo sulla ROM in costruzione
    usate = E.used_flags()
    hid = F.hidden_items(R, sm['hidden_start'])
    const, _ = F.code_calls(d, hi=F.CODE_BL_END)
    for f in FLAG_SICURE_058:
        assert f not in usate, 'flag %s usata da uno script' % hex(f)
        assert f not in hid, 'flag %s usata da un oggetto nascosto' % hex(f)
        assert hex(f) not in sm['usate'], 'flag %s citata da Smeraldo' % hex(f)
        assert f not in const, 'flag %s usata dal codice' % hex(f)
    # variabili
    sv = F.script_vars(R)
    vconst, _ = F.code_calls(d, hi=F.CODE_BL_END, targets={F.GETVARPTR: 'GetVarPointer', F.VARGET: 'VarGet', F.VARSET: 'VarSet'})
    for v in VAR_SICURE_058:
        assert v not in sv, 'variabile %s usata da uno script' % hex(v)
        assert hex(v) not in sm['variabili'], 'variabile %s citata da Smeraldo' % hex(v)
        assert v not in vconst, 'variabile %s usata dal codice' % hex(v)
    # allenatori da non usare piu' come flag: chi combatte (ovunque) e chi e' citato dal codice di Smeraldo
    ev = C.eventi(R)
    lotte = C.lotte_rom(d) | {t for acc in ev.values() for t in acc['allenatori']}
    smt = {int(t) for t in sm.get('allenatori', {})}
    escludi = {0x500 + t for t in lotte | smt}
    P = E.pool(); prima = len(P.restanti())
    P.riordina(FLAG_SICURE_058, escludi)
    E.variabili(VAR_SICURE_058)
    dopo = P.restanti()
    return dict(flag_sicure=len(FLAG_SICURE_058), variabili_sicure=len(VAR_SICURE_058),
                pool_prima=prima, pool_dopo=len(dopo), prime_flag_del_pool=[hex(f) for f in dopo[:5]],
                allenatori_esclusi_dal_pool=len([f for f in escludi if 0x500 <= f < 0x800]))
