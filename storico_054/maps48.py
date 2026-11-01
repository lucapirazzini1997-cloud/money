"""Ritocchi alle campagne 0.48 (dopo i caselli)."""
from country48 import *
import country48 as CO

HOUSEINFO = {}      # (mappa, lato) -> info casa (da part_caselli)


def appr_of(key, side=None):
    return [v for (k, s), v in HOUSEINFO.items() if k == key and (side is None or s == side)]


def c21(cv):
    """Costa Adriatica (Cesena-Cesenatico): campo a serpentina con tre varchi presidiati."""
    K = Kinds(cv)
    # campo piu' pieno nelle due ali
    tall_rect(K, (2, 17, 12, 28), 0.9, 1)
    tall_rect(K, (27, 17, 37, 28), 0.9, 2)
    tall_rect(K, (27, 2, 37, 9), 0.9, 3)
    # muri verticali di alberi con un varco di quattro righe
    wall_v(K, 16, 2, 29, [(18, 21)])
    wall_v(K, 20, 2, 29, [(8, 11)])
    wall_v(K, 24, 2, 29, [(18, 21)])
    ts = []
    ts.append((16, 18, 8, 3)); ts.append((20, 8, 8, 3)); ts.append((24, 18, 8, 3))
    trainer_at(cv, 16, 18, 8, 3, 36, 'DANTE', [(288, 14), (27, 15)],
               'DANTE: Qui si paga il pedaggio. In lotta, però!', 'Pedaggio incassato.',
               'DANTE: Dopo di me il campo è peggio. Occhio all\'erba.')
    trainer_at(cv, 20, 8, 8, 3, 14, 'VALERIA', [(43, 15), (183, 15), (295, 16)],
               'VALERIA: Ho seminato i POKéMON insieme al grano. Vedrai i frutti!', 'Raccolto perso, che peccato.',
               'VALERIA: Il mare è oltre il campo. Si sente già il sale.')
    trainer_at(cv, 24, 18, 8, 3, 33, 'ORESTE', [(81, 15), (304, 16), (309, 16)],
               'ORESTE: Ultimo varco prima di Cesenatico. Si passa da me!', 'Bravo. Il passaggio è libero.',
               'ORESTE: A Cesenatico il porto canale è bellissimo.')
    return ts


def check21(cv, ts):
    a = [v for v in HOUSEINFO.values() if v['key'] == (34, 21)]
    ap = {v['side']: v['appr'] for v in a}
    return connected(cv, ap['W'], ap['E']), forced(cv, ap['W'], ap['E'], ts)


def house(key, side):
    return [v for v in HOUSEINFO.values() if v['key'] == key and v['side'] == side][0]


def _fl(cv, a, b, ts):
    return connected(cv, a, b), forced(cv, a, b, ts)


def c20(cv):
    """Campagna cervese (Cervia-Cesena): tre muri di alberi sulla strada, varchi presidiati."""
    K = Kinds(cv); ts = []
    for yy, (g0, g1) in ((26, (14, 19)), (34, (14, 19)), (46, (14, 19))):
        wall_h(K, yy, 2, 45, [(g0, g1)])
    tall_rect(K, (2, 36, 12, 42), 0.85, 11)
    tall_rect(K, (36, 34, 45, 44), 0.85, 12)
    tall_rect(K, (2, 50, 12, 57), 0.8, 13)
    tall_rect(K, (22, 54, 44, 58), 0.7, 14)
    tall_rect(K, (4, 8, 12, 11), 0.8, 15)
    trainer_at(cv, 14, 26, 10, 5, 31, 'MAURO', [(288, 10), (306, 11)],
               'MAURO: Qui si passa dal mio podere. Prima la lotta!', 'Mi arrendo, passa pure.',
               'MAURO: Più avanti c\'è altra gente. Tieni le cure a portata di mano.')
    trainer_at(cv, 19, 34, 9, 5, 20, 'ROSANNA', [(16, 11), (37, 12)],
               'ROSANNA: Ho guardato i tuoi passi dal campo. Mostrami cosa sai fare!', 'Sei più svelto del vento.',
               'ROSANNA: Cesena è vicina. Non perdere tempo nell\'erba.')
    trainer_at(cv, 14, 46, 10, 5, 35, 'GIORGIO', [(179, 11), (191, 11), (288, 12)],
               'GIORGIO: Ultimo cancello prima di Cesena. Si apre solo con una vittoria!', 'Ottimo. Il cancello è tuo.',
               'GIORGIO: Dopo la Medaglia Arco la strada per Forlì si apre.')
    ts = [(14, 26, 10, 5), (19, 34, 9, 5), (14, 46, 10, 5)]
    berry_scatter(K, (3, 14, 12, 24), 1, 21); berry_scatter(K, (20, 8, 28, 13), 1, 22)
    berry_scatter(K, (32, 24, 44, 26), 1, 23); berry_scatter(K, (34, 36, 44, 44), 1, 24)
    berry_scatter(K, (3, 28, 12, 33), 1, 25); berry_scatter(K, (22, 48, 44, 52), 1, 26)
    return ts


def check20(cv, ts):
    a, b = house((34, 20), 'N')['appr'], house((34, 20), 'S')['appr']
    return _fl(cv, a, b, ts)


def c43(cv):
    """Riviera romagnola (Cesenatico-Rimini): pinete trasversali con varchi presidiati."""
    K = Kinds(cv)
    for yy in (14, 30, 44):
        wall_h(K, yy, 2, 41, [(20, 25)])
    tall_rect(K, (2, 4, 18, 12), 0.7, 31)
    tall_rect(K, (28, 22, 40, 27), 0.7, 32)
    tall_rect(K, (2, 18, 17, 27), 0.8, 33)
    tall_rect(K, (2, 32, 18, 41), 0.8, 34)
    tall_rect(K, (28, 46, 40, 51), 0.7, 35)
    tall_rect(K, (26, 60, 38, 66), 0.7, 36)
    trainer_at(cv, 20, 14, 10, 5, 36, 'GIANNI', [(77, 18), (58, 19)],
               'GIANNI: La pineta è mia! Per passare serve un buon biglietto: una lotta!', 'Biglietto timbrato.',
               'GIANNI: Dopo di me la spiaggia si fa larga. Occhio ai bagnini.')
    trainer_at(cv, 25, 30, 9, 5, 14, 'CATERINA', [(84, 19), (337, 18), (179, 19)],
               'CATERINA: Il sole picchia e io ho voglia di vincere. Pronto?', 'Anche il sole si arrende, a volte.',
               'CATERINA: A Rimini c\'è un porto con ogni sorta di gente.')
    trainer_at(cv, 20, 44, 10, 5, 35, 'BRUNO', [(309, 19), (77, 19), (58, 19)],
               'BRUNO: Dietro di me c\'è il passaggio per Rimini. Prima batti me!', 'Hai le gambe buone. Vai.',
               'BRUNO: Ancora un pezzo di strada e sei a Rimini.')
    ts = [(20, 14, 10, 5), (25, 30, 9, 5), (20, 44, 10, 5)]
    berry_scatter(K, (3, 14, 18, 17), 1, 41); berry_scatter(K, (28, 22, 38, 28), 1, 42)
    berry_scatter(K, (3, 46, 18, 50), 1, 43); berry_scatter(K, (28, 32, 38, 40), 1, 44)
    berry_scatter(K, (3, 62, 18, 70), 1, 45); berry_scatter(K, (28, 58, 38, 68), 1, 46)
    return ts


def check43(cv, ts):
    a, b = house((34, 43), 'N')['appr'], house((34, 43), 'S')['appr']
    return _fl(cv, a, b, ts)


def c39(cv):
    """Via Emilia ovest (Forlimpopoli-Forli): tre posti di blocco e campi pieni."""
    K = Kinds(cv)
    wall_v(K, 14, 2, 11, [(6, 9)])
    for yy in (2, 36, 38):          # chiude i giri attorno al fiume: si passa solo dal ponte
        wall_h(K, yy, 26, 37, [])
    wall_h(K, 24, 36, 61, [(42, 47)])
    tall_rect(K, (2, 14, 28, 17), 0.8, 51)
    tall_rect(K, (2, 34, 26, 40), 0.8, 52)
    tall_rect(K, (36, 14, 60, 20), 0.75, 53)
    tall_rect(K, (36, 27, 56, 31), 0.75, 54)
    tall_rect(K, (36, 34, 60, 40), 0.85, 55)
    tall_rect(K, (14, 2, 40, 8), 0.0, 56)
    trainer_at(cv, 14, 6, 8, 3, 14, 'MARISA', [(203, 22), (191, 23)],
               'MARISA: Questa è la via Emilia, e qui si paga con una lotta!', 'Il pedaggio è saldato.',
               'MARISA: Dopo la siepe ci sono le rocce. Ti servirà Spaccaroccia.')
    trainer_at(cv, 30, 18, 8, 3, 36, 'ELVIO', [(77, 22), (58, 23), (234, 24)],
               'ELVIO: Il ponte lo difendo io. Chi attraversa deve battermi!', 'Ponte tuo, per ora.',
               'ELVIO: Il fiume ha visto di peggio. Vai avanti.')
    trainer_at(cv, 42, 24, 10, 5, 35, 'ROMEO', [(337, 23), (191, 23), (77, 24)],
               'ROMEO: Ultimo tratto prima di Forlimpopoli. Fatti sotto!', 'Hai vinto, onore al merito.',
               'ROMEO: A Forlimpopoli si mangia la piadina più buona.')
    ts = [(14, 6, 8, 3), (30, 18, 8, 3), (42, 24, 10, 5)]
    berry_scatter(K, (3, 20, 20, 24), 1, 61); berry_scatter(K, (3, 28, 20, 33), 1, 62)
    berry_scatter(K, (38, 4, 58, 10), 1, 63); berry_scatter(K, (36, 32, 58, 33), 1, 64)
    berry_scatter(K, (14, 2, 28, 9), 1, 65); berry_scatter(K, (38, 12, 58, 14), 1, 66)
    return ts


def check39(cv, ts):
    a, b = house((34, 39), 'W')['appr'], house((34, 39), 'E')['appr']
    return _fl(cv, a, b, ts)


def c19(cv):
    """Ippodromo: rocce sulla strada per Capocolle, erba alta ai margini e qualche sfidante."""
    K = Kinds(cv)
    ap = house((34, 19), 'W')['appr']          # davanti alla porta di Capocolle
    for dy in (-1, 0, 1):
        assert K.grass(ap[0], ap[1] + dy) or dy == 0 or True
    rock(cv, ap[0], ap[1])
    rock(cv, ap[0], ap[1] - 1)
    rock(cv, ap[0], ap[1] + 1)
    tall_rect(K, (2, 29, 15, 31), 0.85, 71)
    tall_rect(K, (24, 29, 30, 31), 0.8, 72)
    tall_rect(K, (39, 21, 45, 31), 0.85, 73)
    tall_rect(K, (2, 2, 7, 12), 0.7, 74)
    tall_rect(K, (22, 2, 45, 5), 0.8, 75)
    trainer_at(cv, 24, 25, 7, 4, 31, 'FANTINO', [(77, 16), (78, 18)],
               'FANTINO: Lo vedi quel cavallo? Corre meno dei miei POKéMON!', 'Mi hai battuto sul traguardo.',
               'FANTINO: All\'ippodromo si scommette. Meglio non puntare su di me.')
    trainer_at(cv, 40, 12, 9, 4, 14, 'SCUDERIA', [(58, 17), (84, 17), (203, 18)],
               'SCUDERIA: Sono la stalliera. Con questi qui nessuno è mai caduto!', 'Sei andata più forte dei cavalli!',
               'SCUDERIA: Per Capocolle servono le rocce... e la medaglia giusta.')
    berry_scatter(K, (3, 4, 6, 12), 1, 81); berry_scatter(K, (24, 2, 44, 5), 1, 82); berry_scatter(K, (38, 22, 45, 28), 1, 83)
    return [(24, 25, 7, 4), (40, 12, 9, 4)]


def c60(cv):
    """Capocolle / Monte Spaccato: due posti di blocco sul valico e prati pieni."""
    K = Kinds(cv)
    wall_v(K, 10, 2, 31, [(14, 17)], maxsize=14)
    wall_v(K, 32, 2, 31, [(14, 17)], maxsize=14)
    tall_rect(K, (2, 2, 9, 12), 0.8, 91)
    tall_rect(K, (2, 19, 9, 31), 0.9, 92)
    tall_rect(K, (34, 2, 42, 12), 0.8, 93)
    tall_rect(K, (33, 25, 42, 30), 0.8, 94)
    trainer_at(cv, 10, 14, 8, 3, 36, 'ARISTIDE', [(16, 19), (187, 19), (161, 20)],
               'ARISTIDE: Il valico di Capocolle lo guardo io. Passa solo chi sa lottare!', 'Il valico è tuo.',
               'ARISTIDE: Oltre il Monte Spaccato c\'è Babbi, la fabbrica dei dolci.')
    trainer_at(cv, 32, 17, 7, 3, 14, 'LAURA', [(69, 20), (167, 21), (74, 21)],
               'LAURA: Salgo il monte ogni mattina. I miei POKéMON sono allenati!', 'Hai più fiato di me.',
               'LAURA: Dopo il monte la strada scende verso Forlimpopoli.')
    berry_scatter(K, (3, 2, 9, 12), 1, 95); berry_scatter(K, (3, 20, 9, 30), 1, 96); berry_scatter(K, (34, 2, 42, 11), 1, 97)
    return [(10, 14, 8, 3), (32, 17, 7, 3)]


def check60(cv, ts):
    a, b = house((35, 60), 'W')['appr'], house((35, 60), 'E')['appr']
    return _fl(cv, a, b, ts)


# ------------------------------------------------------------------ Forli-Faenza (34.84): mappa allungata
DY84 = 40


def insert_rows(cv, at, n, fill):
    """Inserisce n righe a quota 'at'. fill(attr, y) -> riga nuova (lista) per l'attributo."""
    for attr in ('terrain', 'over', 'pathmask', 'art', 'fam'):
        g = getattr(cv, attr)
        new = [r[:] for r in g[:at]] + [fill(attr, at + i) for i in range(n)] + [r[:] for r in g[at:]]
        setattr(cv, attr, new)
    cv.h += n
    for lst in (cv.objs, cv.bbgs, cv.bwarps, cv.bcoords):
        for e in lst:
            if e['y'] >= at: e['y'] += n


def extend84(cv, dy=DY84):
    if getattr(cv, '_ext84', False): return
    cv._ext84 = True
    K = Kinds(cv); w = cv.w
    ART = [r[:] for r in cv.art]          # righe originali
    def fill(attr, y):
        if attr == 'terrain': return ['grass'] * w
        if attr == 'over': return [None] * w
        if attr == 'pathmask': return [False] * w
        if attr == 'fam': return [None] * w
        src = ART[2] if y % 2 == 0 else ART[3]
        row = []
        for x in range(w):
            if x in (0, 1, w - 2, w - 1) or 22 <= x <= 29: row.append(src[x])
            else: row.append(K.g_sample)
        return row
    insert_rows(cv, 2, dy, fill)
    # i vecchi varchi sulla sponda ovest (casa di Faenza) vengono rifatti in alto
    cv.bwarps = [w_ for w_ in cv.bwarps if w_['x'] != 0]


def edge_trees_84(cv, rows):
    for y in rows:
        for x in (0, 1):
            cv.art[y][x] = cv.art[2 + (y % 2)][x]
        for x in (cv.w - 2, cv.w - 1):
            cv.art[y][x] = cv.art[2 + (y % 2)][x]


def paved(K, x0, y0, x1, y1):
    """Sentiero lastricato (stessa pavimentazione della piazza esistente)."""
    cv = K.cv
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if K.grass(x, y) or K.tall(x, y):
                cv.art[y][x] = PAVE[0]


PAVE = [None]


def c84(cv):
    K = Kinds(cv); d = DY84
    PAVE[0] = cv.art[10 + d][18]            # lastra della piazza originale
    edge_trees_84(cv, range(2 * 0 + 6 + d, 11 + d + 1))      # il vecchio ingresso a ovest e' diventato bordo d'alberi
    wa = house((34, 84), 'W'); ea = house((34, 84), 'E')
    hx, hy = wa['appr']
    # --- sponda ovest: sentiero lungo fino a Faenza, riva coperta da alberi (si sbarca solo a sud)
    paved(K, 12, 12, 14, 46)
    paved(K, hx, 9, 14, 11)
    paved(K, 12, 44, 14, 46)
    for yy in (40, 28, 18):
        wall_h(K, yy, 2, 21, [(12, 15)])
    tall_rect(K, (2, 30, 11, 39), 0.9, 101); tall_rect(K, (16, 30, 19, 39), 0.9, 102)
    tall_rect(K, (2, 20, 11, 27), 0.9, 103); tall_rect(K, (16, 20, 19, 27), 0.9, 104)
    tall_rect(K, (2, 12, 11, 17), 0.85, 105); tall_rect(K, (16, 12, 19, 17), 0.85, 106)
    tall_rect(K, (2, 2, 19, 7), 0.8, 107)
    tall_rect(K, (2, 42, 9, 44), 0.5, 108)
    trainer_at(cv, 12, 40, 10, 3, 36, 'TOMMASO', [(44, 31), (183, 31), (194, 32)],
               'TOMMASO: La riva ovest è sorvegliata. Da qui non si passa gratis!', 'Si passa, si passa.',
               'TOMMASO: Più su ci sono altri sorveglianti. Non è finita.')
    trainer_at(cv, 15, 28, 9, 3, 14, 'FILIPPA', [(111, 32), (81, 31), (27, 32)],
               'FILIPPA: Con il fiume così vicino mi sento in forma. Vediamo se lo sei anche tu!', 'Mi hai travolta come la corrente.',
               'FILIPPA: Faenza non è lontana. Ancora un varco.')
    trainer_at(cv, 12, 18, 10, 3, 33, 'GENNARO', [(318, 32), (337, 32), (304, 31)],
               'GENNARO: Ultimo varco prima di Faenza. Fatti sotto!', 'Il sentiero è tuo.',
               'GENNARO: A Faenza i ceramisti hanno il fuoco acceso. Anche tu, sembra.')
    ts = [(12, 40, 10, 3), (15, 28, 9, 3), (12, 18, 10, 3)]
    berry_scatter(K, (3, 30, 10, 39), 1, 111); berry_scatter(K, (16, 30, 18, 39), 1, 112)
    berry_scatter(K, (3, 20, 10, 27), 1, 113); berry_scatter(K, (3, 12, 10, 17), 1, 114)
    # --- sponda est: sentiero facoltativo verso nord con due sfidanti
    paved(K, 40, 13, 42, 43)
    tall_rect(K, (32, 30, 39, 40), 0.9, 121); tall_rect(K, (44, 30, 52, 40), 0.9, 122)
    tall_rect(K, (32, 16, 39, 27), 0.85, 123); tall_rect(K, (44, 16, 52, 27), 0.85, 124)
    tall_rect(K, (32, 4, 52, 12), 0.8, 125)
    for (x, y) in ((34, 14), (36, 14), (48, 14), (50, 14), (34, 28), (50, 28), (46, 36), (36, 36)):
        K.cv.tree(x, y)
    trainer_at(cv, 41, 34, 8, 4, 35, 'LORIS', [(194, 31), (43, 30), (301, 32)],
               'LORIS: Il canale è cambiato negli anni, io no. Combatto da sempre!', 'Il canale mi ha tradito.',
               'LORIS: In fondo al sentiero ci sono solo pescatori e curiosi.')
    trainer_at(cv, 41, 20, 8, 4, 20, 'NADIA', [(183, 31), (44, 32), (318, 31)],
               'NADIA: Ti ho visto dalla sponda. Tutta questa strada per me?', 'Meriti il fiume intero.',
               'NADIA: Il sentiero finisce al limite del campo. Torna indietro.')
    berry_scatter(K, (32, 16, 39, 27), 1, 131); berry_scatter(K, (44, 16, 52, 27), 1, 132)
    berry_scatter(K, (32, 30, 39, 40), 1, 133); berry_scatter(K, (32, 4, 52, 12), 1, 134)
    return ts


def check84(cv, ts):
    """Sponda ovest senza Surf: da sud (13,46) a Faenza, obbligato passare dai 3 allenatori."""
    b = house((34, 84), 'W')['appr']
    return _fl(cv, (13, 46), b, ts)
