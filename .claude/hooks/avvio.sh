#!/bin/sh
# Hook SessionStart: controlla le ROM di base e prepara gli emulatori del collaudo.
# Le ROM di base non sono nel repository (pubblico): in una sessione nuova vanno rimesse a mano in basi/.
cd "$(dirname "$0")/../.." || exit 0
ok=1
for c in "rom047.gba d26c0fd48f75fe1db4e36865f56b7ea9c9fd7914954d72e06ccfbaf45930122d" \
         "base31.gba c880c7034f02c6fd9ea6ee37a4ce35f7cee57042dd5121732e84627cf8a60948"; do
  set -- $c
  if [ ! -f "basi/$1" ]; then echo "ATTENZIONE: manca basi/$1: la build non parte. Chiedi all'utente la ROM."; ok=0
  elif [ "$(sha256sum "basi/$1" | cut -d' ' -f1)" != "$2" ]; then echo "ATTENZIONE: basi/$1 ha uno SHA diverso da quello atteso."; ok=0; fi
done
[ $ok = 1 ] && echo "ROM di base presenti e corrette."
if [ ! -x collaudo/h ] || [ ! -d collaudo/vbam-libretro ]; then
  if [ -n "$CLAUDE_CODE_REMOTE" ]; then
    nohup sh collaudo/prepara_emulatori.sh > collaudo/prepara_emulatori.log 2>&1 &
    echo "Emulatori assenti: compilazione avviata in sottofondo (log: collaudo/prepara_emulatori.log). Attendi 'collaudo/h' prima dei collaudi."
  else
    echo "Emulatori assenti: lancia sh collaudo/prepara_emulatori.sh prima dei collaudi."
  fi
else
  echo "Emulatori del collaudo pronti."
fi
exit 0
