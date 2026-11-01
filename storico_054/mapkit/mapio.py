"""Write canvases into the pokeemerald project: layouts, map.json events/connections, tileset registration."""
import json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import gfx, canvas

R = gfx.ROOT


def ts_symbol(folder):
    # folder romagna17_lido -> gTileset_Romagna17Lido
    parts = folder.split('_')
    return 'gTileset_' + ''.join(p[:1].upper() + p[1:] for p in parts)


def register_tileset(folder):
    sym = ts_symbol(folder)
    base = sym[len('gTileset_'):]
    gpath = R / 'src/data/tilesets/graphics.h'
    g = gpath.read_text()
    if f'gTilesetTiles_{base}[]' not in g:
        pals = ''.join(f' INCGFX_U16("data/tilesets/secondary/{folder}/palettes/{i:02d}.pal", ".gbapal"),\n' for i in range(16))
        g += f'\nconst u32 gTilesetTiles_{base}[] = INCGFX_U32("data/tilesets/secondary/{folder}/tiles.png", ".4bpp.lz");\nconst u16 gTilesetPalettes_{base}[][16] = {{\n{pals}}};\n'
        gpath.write_text(g)
    mpath = R / 'src/data/tilesets/metatiles.h'
    m = mpath.read_text()
    if f'gMetatiles_{base}[]' not in m:
        m += f'\nconst u16 gMetatiles_{base}[] = INCBIN_U16("data/tilesets/secondary/{folder}/metatiles.bin");\nconst u16 gMetatileAttributes_{base}[] = INCBIN_U16("data/tilesets/secondary/{folder}/metatile_attributes.bin");\n'
        mpath.write_text(m)
    hpath = R / 'src/data/tilesets/headers.h'
    h = hpath.read_text()
    if f'{sym} =' not in h:
        h += f'\nconst struct Tileset {sym} = {{ .isCompressed = TRUE, .isSecondary = TRUE, .tiles = gTilesetTiles_{base}, .palettes = gTilesetPalettes_{base}, .metatiles = gMetatiles_{base}, .metatileAttributes = gMetatileAttributes_{base}, .callback = NULL }};\n'
        hpath.write_text(h)
    return sym


def load_map(name):
    return json.loads((R / 'data/maps' / name / 'map.json').read_text())


def save_map(name, mj):
    (R / 'data/maps' / name / 'map.json').write_text(json.dumps(mj, indent=2, ensure_ascii=False) + '\n')


def layouts():
    return json.loads((R / 'data/layouts/layouts.json').read_text())


def save_layouts(d):
    (R / 'data/layouts/layouts.json').write_text(json.dumps(d, indent=2, ensure_ascii=False) + '\n')


def write(mapname, cv, grid, idmap, ts_sym, connections=None, extra=None):
    mj = load_map(mapname)
    L = layouts()
    lay = next(l for l in L['layouts'] if l['id'] == mj['layout'])
    lay['width'], lay['height'] = cv.w, cv.h
    lay['primary_tileset'] = 'gTileset_General'
    lay['secondary_tileset'] = ts_sym
    save_layouts(L)
    canvas.write_layout(cv, grid, idmap, str(Path(lay['blockdata_filepath']).parent))
    # border lives where layouts.json says
    mj['object_events'] = cv.npcs
    mj['warp_events'] = cv.warps
    mj['bg_events'] = cv.signs
    mj['coord_events'] = cv.triggers
    if connections is not None:
        mj['connections'] = connections or None
    if extra:
        mj.update(extra)
    save_map(mapname, mj)
    return mj


def old_events(mapname):
    """Events of a map from the 0.12 snapshot."""
    return json.loads((Path('/home/claude/proj/snap012/data/maps') / mapname / 'map.json').read_text())
