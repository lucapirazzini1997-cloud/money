#!/bin/sh
# Passi automatici della consegna: build, BPS verificata, zip ricostruito in cartella pulita, regressione.
# Uso: sh .claude/skills/consegna-versione/consegna.sh 061 [cartella_di_appoggio] [--senza-regressione]
set -e
V=$1; [ -n "$V" ] || { echo "uso: consegna.sh 061 [cartella] [--senza-regressione]"; exit 1; }
ROOT=$(cd "$(dirname "$0")/../../.." && pwd); cd "$ROOT"
S=${2:-${TMPDIR:-/tmp}/consegna_$V}; mkdir -p "$S"; S=$(cd "$S" && pwd)
PREC=$(python3 -c "
import re;t=open('build.py').read();v=re.findall(r\"\('(\d{3})',\s*'v\d{3}_\w+'\)\",t);i=v.index('$V');print(v[i-1] if i else '055')")
c(){ echo "$1" | sed 's/^0//'; }
NUOVA="Pokemon_Romagna_0_$(c $V).gba"; VECCHIA="Pokemon_Romagna_0_$(c $PREC).gba"
BPS="rom/Pokemon_Romagna_0_$(c $PREC)_to_0_$(c $V).bps"

echo "== 1. build completa"
python3 build.py > "$S/build.log" 2>&1 || { tail -20 "$S/build.log"; exit 1; }
grep -q "ok $V " "$S/build.log" || { echo "SHA della $V assente o diverso in build.py:"; grep " $V " "$S/build.log"; exit 1; }

echo "== 2. BPS $BPS"
python3 -c "
import sys;sys.path.insert(0,'.');import bpslib
a=open('out/$VECCHIA','rb').read();b=open('out/$NUOVA','rb').read();p=bpslib.create(a,b)
assert bpslib.apply(a,p)==b,'la BPS non riproduce la ROM';open('$BPS','wb').write(p);print('  ok',len(p),'byte, riapplicata')"

echo "== 3. zip senza out/ e ricostruzione in cartella pulita"
ZIP="$S/Pokemon_Romagna_0_$(c $V)_progetto.zip"; rm -f "$ZIP"
cp "out/$NUOVA" rom/
zip -qr "$ZIP" . -x 'out/*' '.git/*' '*__pycache__*' 'collaudo/mgba/*' 'collaudo/vbam-libretro/*' 'collaudo/h' \
  'collaudo/out57/*' 'collaudo/out_regressione/*' 'collaudo/play/log.txt' 'collaudo/play/t*_*.png' \
  'collaudo/play/t*_*.json' 'collaudo/play/t59_*.sav' 'collaudo/play/t*_*_pres*.sav' 'collaudo/play/leg_*.sav' \
  'collaudo/play/*.ppm' 'collaudo/prepara_emulatori.log' 'storico_054/rom047.gba' 'storico_054/base31.gba' \
  'rom/Pokemon_Romagna_0_56.gba'
rm "rom/$NUOVA"
rm -rf "$S/pulita"; mkdir "$S/pulita"
(cd "$S/pulita" && unzip -q "$ZIP" && python3 build.py > build.log 2>&1) || true
grep -q "ok $V " "$S/pulita/build.log" || { echo "la cartella pulita non rifà lo SHA:"; tail -20 "$S/pulita/build.log"; exit 1; }
echo "  ok: zip $(du -h "$ZIP" | cut -f1), la cartella pulita rifà lo stesso SHA"
rm -rf "$S/pulita"
cp "out/$NUOVA" "$S/"

if [ "$3" != "--senza-regressione" ]; then
  echo "== 4. regressione contro la $PREC"
  python3 collaudo/regressione.py "out/$NUOVA" --rif "out/$VECCHIA" --uscita "$S/regressione" | tail -5
  echo "  tabella: $S/regressione (copiala in collaudo/risultati/$V/ se va tenuta)"
fi
echo "fatto. Da inviare: $S/$NUOVA $ROOT/$BPS $ZIP $ROOT/relazioni/RELAZIONE_0_$(c $V).md"
