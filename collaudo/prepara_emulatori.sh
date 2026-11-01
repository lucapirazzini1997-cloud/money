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
gcc -O2 h.c -o h -Imgba/include -Imgba/build/include -Lmgba/build -lmgba -Wl,-rpath,"$PWD/mgba/build"
# VBA-M come core libretro (usato da vb.py quando VBAM=1)
[ -d vbam-libretro ] || git clone https://github.com/libretro/vbam-libretro.git && git -C vbam-libretro checkout 115defb3a318258ab84746d45258a1aec19d0b4b
make -C vbam-libretro/src/libretro -j"$(nproc)"
echo "pronto: ./h (mGBA) e vbam-libretro/src/libretro/vbam_libretro.so (VBA-M)"
