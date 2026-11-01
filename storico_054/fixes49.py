"""0.49 - ponti veri dove prima si attraversava l'acqua camminandoci sopra (elevazione sbagliata nelle mappe a 'arte')."""
from gates48 import *
import kit48
import struct
import gates48 as G
import mapkit.art as A

WATER = {0x10, 0x11, 0x12, 0x14, 0x15}


def is_water(cv, x, y):
    a = cv.art[y][x]
    if a is not None: return a[3] in WATER
    k = cv.over[y][x]
    return bool(k) and isinstance(k[0], int) and k[0] < 512 and G._over_beh(cv, k[0]) in G.WATER_BEH


def planks(vertical):
    im = A.bridge_ns()
    return im if vertical else im.transpose(Image.ROTATE_90)


def bridge_ns(cv, cols, ya, yb):
    """Ponte N-S sulle colonne cols tra le righe ya..yb (incluse): solo le celle d'acqua diventano assito."""
    n = 0
    for x in cols:
        for y in range(ya, yb + 1):
            if is_water(cv, x, y):
                cv.over[y][x] = (1, 0, 3) if cv.art[y][x] is None else cv.over[y][x]
                cv.art[y][x] = (planks(True), None, 0, 0x100, False); n += 1
    return n


def bridge_ew(cv, rows, xa, xb):
    n = 0
    for y in rows:
        for x in range(xa, xb + 1):
            if is_water(cv, x, y):
                cv.over[y][x] = (1, 0, 3) if cv.art[y][x] is None else cv.over[y][x]
                cv.art[y][x] = (planks(False), None, 0, 0x100, False); n += 1
    return n


def water_run(cv, x, y0):
    """Prima riga d'acqua risalendo da y0 e ultima riga continua (per scegliere l'estensione del ponte)."""
    ys = [y for y in range(cv.h) if is_water(cv, x, y)]
    return (min(ys), max(ys)) if ys else None


def apply(cvs):
    out = {}
    cv = cvs[(0, 9)]; out['0.9'] = bridge_ns(cv, (19, 20), 0, 8)
    cv = cvs[(34, 93)]
    # fiume di campagna: sulle colonne della strada (T1/T2) e' continuo fra nord e sud
    out['34.93'] = bridge_ns(cv, (19, 20, 21), 0, cv.h - 1)
    cv = cvs[(34, 84)]; out['34.84'] = bridge_ew(cv, (54, 55), 20, 31)
    out['aie'] = aie_sign(cvs)
    out['lampione'] = rimini_lamp(cvs)
    return out


def aie_sign(cvs):
    """Insegna della Casa delle Aie: targa chiara con testo scuro, leggibile (prima testo beige su marrone, minuscolo)."""
    from PIL import ImageDraw, ImageFont
    cv = cvs[(34, 20)]
    xs = range(28, 33); y = 10
    strip = Image.new('RGBA', (16 * len(xs), 16), (0, 0, 0, 0))
    for i, x in enumerate(xs):
        a = cv.art[y][x]
        assert a is not None and a[2] == 1, ('insegna Aie: celle inattese', x)   # cella piena (parete)
        cell = a[0].convert('RGBA').copy()
        if a[1] is not None: cell.alpha_composite(a[1].convert('RGBA'))
        strip.paste(cell, (16 * i, 0))
    d = ImageDraw.Draw(strip); d.fontmode = '1'
    W_ = strip.width
    d.rectangle((3, 2, W_ - 4, 14), fill=(244, 232, 190), outline=(86, 54, 34))
    fnt = ImageFont.truetype(str(ROOT / 'fonts/DejaVuSans.ttf'), 7)
    tw = d.textlength('CASA DELLE AIE', font=fnt)
    d.text(((W_ - tw) / 2, 4), 'CASA DELLE AIE', font=fnt, fill=(122, 28, 22))
    for i, x in enumerate(xs):
        a = cv.art[y][x]
        cv.art[y][x] = (strip.crop((16 * i, 0, 16 * i + 16, 16)), None, a[2], a[3], a[4])
    return 1


def rimini_lamp(cvs):
    """Rimini: un lampione e un riquadro di selciato 'bucavano' il tetto di una casa (colonna 30, righe 20-21): ripristino tetto e finestra."""
    cv = cvs.setdefault((34, 47), V.live_canvas((34, 47)))
    for y in (20, 21):
        assert cv.art[y][29] is not None and cv.art[y][30] is not None
        cv.art[y][30] = cv.art[y][29]
    return 2


# ----------------------------------------------------------------------------- eventi cromatici (nativi gia' presenti nella ROM 0.44)
NATIVE_SHINY_WILD = 0x09730055      # dopo setwildbattle: l'incontro selvatico diventa cromatico (come lo SHUCKLE di Forlimpopoli)
NATIVE_SHINY_GIFT = 0x09730069      # setvar 8004=specie, 8005=livello, 8006=specie -> regala un cromatico (0x800D==2: niente posto)


def shiny_wild_script(name, species, level, done_flag, intro, caught, ko, fled):
    """Incontro selvatico cromatico ripetibile finche' non viene catturato (flag done_flag)."""
    s = Script(name).emit(b'\x6a')
    s.flag(done_flag, 'done')
    s.msg(intro)
    s.var(0x8004, species).var(0x8005, level)
    s.emit(b'\xa1' + H(species) + H(2) + b'\xc5')                       # playmoncry + waitmoncry
    s.emit(b'\xb6' + H(species) + bytes([level]) + H(0))                 # setwildbattle
    s.emit(b'\x23' + struct.pack('<I', NATIVE_SHINY_WILD))               # callnative
    s.emit(b'\x29' + H(0x8c1) + b'\xb7' + b'\x2a' + H(0x8c1))            # setflag 8c1; dowildbattle; clearflag 8c1
    s.emit(b'\x26' + H(0x800d) + H(0xb7))                                # specialvar 800d, 0xb7 (esito)
    s.cmp(7, 'caught').cmp(1, 'ko')
    s.msg(fled).end()
    s.label('ko').msg(ko).end()
    s.label('caught').set(done_flag).msg(caught).end()
    s.label('done').end()
    return s.save()


def arco(cvs):
    """Arco di Augusto (Rimini): sotto l'arcata ti piomba addosso un FARFETCH'D cromatico (Lv 26)."""
    cv = cvs.setdefault((34, 47), V.live_canvas((34, 47)))
    f = kit48.POOL.flag('arco farfetchd cromatico')
    p = shiny_wild_script('Arco FARFETCHD', 83, 26, f,
        "Sotto l'Arco di Augusto qualcosa di bianco piomba dal cielo: un FARFETCH'D dalle piume che brillano!",
        "Hai catturato il FARFETCH'D cromatico! L'Arco di Augusto ha visto di peggio.",
        "Il FARFETCH'D si ritira sul cornicione dell'arco. Puoi riprovare: ripassa sotto l'arcata.",
        "Il FARFETCH'D vola via sopra i tetti. Ripassa sotto l'arco: potrebbe tornare.")
    for x in (70, 71):
        assert cv.art[33][x] is not None
        cv.bcoords.append(dict(x=x, y=33, elev=0, var=0x400e, val=0, script=p))
    return f


def pokecenters():
    """Centri Pokemon 1F identici agli originali: i layout personalizzati (pavimento rifatto) tornano al layout di Smeraldo."""
    van = W.rom.map(3, 1)
    assert (van['width'], van['height']) == (14, 9)
    custom = W.rom.map(34, 26)['layout']
    n = 0
    for g in (2, 33, 34, 35):
        for num in range(0, 140):
            try: m = W.rom.map(g, num)
            except Exception: continue
            if m['layout'] != custom: continue
            hp = m['header']
            struct.pack_into('<I', W.d, hp, B + van['layout'])
            struct.pack_into('<H', W.d, hp + 18, van['layout_id'])
            n += 1
    assert n >= 10, n
    return n
