#!/bin/sh
# Prepara i due emulatori usati dal collaudo, dentro questa cartella.
# Versioni usate per la 0.56: mGBA fd9dc5c2cbf2 (github.com/mgba-emu/mgba), vbam-libretro 115defb3a318 (github.com/libretro/vbam-libretro).
set -e
cd "$(dirname "$0")"
# mGBA come libreria condivisa + pilota h (h.c)
[ -d mgba ] || git clone https://github.com/mgba-emu/mgba.git && git -C mgba checkout fd9dc5c2cbf234365068855851107e762fc6211b
cmake -S mgba -B mgba/build -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED=ON -DBUILD_STATIC=OFF -DBUILD_QT=OFF -DBUILD_SDL=OFF \
      -DBUILD_GL=OFF -DBUILD_GLES2=OFF -DBUILD_GLES3=OFF -DBUILD_TEST=OFF -DBUILD_SUITE=OFF -DBUILD_PYTHON=OFF
make -C mgba/build -j"$(nproc)"
# stesse -D della libreria (ENABLE_DIRECTORIES ecc. cambiano la struttura mCore: senza, ./h va in crash all'avvio)
DEFS=$(grep -o -- '-D[A-Za-z_0-9]\+' mgba/build/CMakeFiles/mgba.dir/flags.make | sort -u | tr '\n' ' ')
gcc -O2 $DEFS h.c -o h -Imgba/include -Imgba/build/include -Lmgba/build -lmgba -Wl,-rpath,"$PWD/mgba/build"
# VBA-M come core libretro (usato da vb.py quando VBAM=1)
[ -d vbam-libretro ] || git clone https://github.com/libretro/vbam-libretro.git && git -C vbam-libretro checkout 115defb3a318258ab84746d45258a1aec19d0b4b
# orologio ripetibile: con VBAM_ORA_FISSA=<secondi unix> l'RTC parte da quell'ora invece che dall'ora vera
# (vb.py la imposta sempre, come ./h con l'RTC finto di mGBA). La modifica si applica una volta sola.
grep -q VBAM_ORA_FISSA vbam-libretro/src/gba/RTC.cpp || sed -i \
  -e 's|^#include "GBA.h"|#include "GBA.h"\n#include <stdlib.h>|' \
  -e 's|    time(&long_time); /\* Get time as long integer. \*/|    time(\&long_time); if (getenv("VBAM_ORA_FISSA")) long_time = (time_t)atoll(getenv("VBAM_ORA_FISSA"));|' \
  vbam-libretro/src/gba/RTC.cpp
make -C vbam-libretro/src/libretro -j"$(nproc)"
echo "pronto: ./h (mGBA) e vbam-libretro/src/libretro/vbam_libretro.so (VBA-M)"
