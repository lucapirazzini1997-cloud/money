"""Bozza Lotto 4: Lido di Savio (0.9) piu' simile al paese vero, con gli edifici di oggi.

Richiesta: "rendila piu' simile a quella originale ma mantenendo le strutture che ci sono gia'"; scelte: spiaggia
con i bagni, Viale Romagna con negozi, foce del Savio, piu' pini e meno prato; casa di ALDO con l'esterno A; chiesa
aperta. Stesse misure (56x44), stesse uscite; solo pezzi che la mappa ha gia' (nessun tile nuovo).
  - FOCE DEL SAVIO: capanni da pesca sulla riva nord vicino al mare, due pontili alla foce;
  - VIALE ROMAGNA (x 18-20): alberi e lampioni ai lati, bancarelle, cartello;
  - PINI nei giardini e lungo le vie; meno prato vuoto;
  - SPIAGGIA: tre bagni (cabine, file regolari di ombrelloni, cartello con il nome), lungomare con i lampioni;
  - casa di ALDO: resta azzurra, con l'orto (variante A di bozze/casa_rivale.py);
  - CHIESA: la porta (8,38) si apre (interno in bozze/chiesa_lido.py).
Uso: python3 bozze/lido.py ROM_071 CARTELLA
"""
import sys, struct
from pathlib import Path
sys.path[:0] = [str(Path(__file__).resolve().parent.parent / 'strumenti_rom'), str(Path(__file__).resolve().parent)]
import numpy as np
import romlib

LIDO = (0, 9)
# timbri: (x, y, w, h) nella mappa di oggi
PINO = (0, 8, 2, 2)
ALBERO = (38, 33, 1, 2)
LAMPIONE = (39, 33, 1, 2)
OMBRELLONE = (45, 27, 1, 2)
CABINA_R, CABINA_A, CABINA_V = (42, 21, 1, 2), (42, 30, 1, 2), (42, 36, 1, 2)
CAPANNO = (9, 0, 3, 3)
PONTILE = (35, 5, 2, 2)
BANCARELLA = (26, 22, 2, 2)
CARTELLO = (38, 36, 1, 1)
PANCHINA = (22, 23, 1, 1)


class Mappa:
    def __init__(self, d):
        self.rom = romlib.Rom(bytes(d)); self.m = self.rom.map(*LIDO)
        self.orig = self.rom.blocks(self.m); self.a = self.orig.copy()
        self.erba = int(self.orig[10, 23]); self.sabbia = int(self.orig[25, 45]); self.strada = int(self.orig[9, 10])
        self.cartelli = []                     # (x, y, testo) nuovi

    def timbro(self, t, x, y):
        sx, sy, w, h = t
        self.a[y:y + h, x:x + w] = self.orig[sy:sy + h, sx:sx + w]

    def riempi(self, x, y, w, h, v): self.a[y:y + h, x:x + w] = v

    def cartello(self, x, y, testo):
        self.timbro(CARTELLO, x, y); self.cartelli.append((x, y, testo))


def disegna(d):
    M = Mappa(d); o = M.orig
    # ---------------- foce del Savio: capanni da pesca sulla riva nord, pontili alla foce
    for x in (33, 37):
        M.riempi(x, 0, 3, 3, M.erba); M.timbro(CAPANNO, x, 0)
    M.riempi(28, 0, 3, 3, M.erba)                      # il capanno di (28,0) si sposta verso la foce (33,0)
    for x in (44, 48): M.timbro(PONTILE, x, 5)
    M.cartello(41, 2, "FOCE DEL SAVIO\nI capanni da pesca calano le\nreti quando sale la marea.")
    # ---------------- Viale Romagna (x 18-20): alberi e lampioni ai lati, bancarelle
    for y in (11, 15, 24, 33):
        for x in (17, 21):
            if (M.a[y:y + 2, x] == M.erba).all(): M.timbro(ALBERO, x, y)
    for y in (13, 26, 36):
        for x in (17, 21):
            if (M.a[y:y + 2, x] == M.erba).all(): M.timbro(LAMPIONE, x, y)
    M.timbro(BANCARELLA, 22, 26)
    M.cartello(17, 10, "VIALE ROMAGNA\nNegozi, gelati e alberghi fino\nalla PINETA.")
    # ---------------- pini nei giardini
    for x, y in [(1, 17), (4, 17), (9, 17), (12, 17), (31, 10), (31, 16), (31, 37), (36, 37), (26, 37),
                 (10, 37), (15, 22)]:
        if (M.a[y:y + 2, x:x + 2] == M.erba).all(): M.timbro(PINO, x, y)
    # boschetto di pini al posto delle aiuole a sinistra del laboratorio (NORA resta raggiungibile)
    M.riempi(4, 22, 5, 7, M.erba)
    for x, y in [(4, 22), (7, 22), (4, 25), (6, 27)]: M.timbro(PINO, x, y)
    # ---------------- casa di ALDO: orto a destra, alberi a sinistra (variante A)
    import casa_rivale
    _, a2 = casa_rivale.lido_variante_a(d)
    M.a[10:18, 22:29] = a2[10:18, 22:29]
    # ---------------- spiaggia: tre bagni
    M.riempi(42, 21, 10, 20, M.sabbia)
    for y0, cab, nome in ((22, CABINA_R, 'BAGNO ADRIATICO'), (28, CABINA_A, 'BAGNO SAVIO'), (34, CABINA_V, 'BAGNO PINETA')):
        for y in (y0, y0 + 3): M.timbro(cab, 42, y)
        M.cartello(43, y0, "%s\nLettini e ombrelloni in fila,\ncome in tutta la riviera." % nome)
        for y in (y0, y0 + 3):
            for x in (45, 47, 49):
                M.timbro(OMBRELLONE, x, y)
    for y in (22, 28, 34): M.a[y + 2, 42] = o[23, 42]   # sabbia fra le cabine
    M.a[31, 50:52] = o[31, 50:52]                        # pattini
    M.timbro((50, 22, 1, 2), 51, 21)                     # torretta del bagnino
    # lungomare: lampioni regolari
    for y in (24, 30, 36):
        if (M.a[y:y + 2, 39] == M.erba).all(): M.timbro(LAMPIONE, 39, y)
    # porte chiuse con un nome: negozi del viale
    M.porte = {(13, 35): "BAZAR DEL LIDO\nSecchielli, palette e salvagenti.\nChiuso per la pausa pranzo.",
               (33, 35): "PIADINERIA\nLa piastra e' ancora fredda:\napre stasera!"}
    return M


if __name__ == '__main__':
    import sprite
    from PIL import ImageDraw
    d = open(sys.argv[1], 'rb').read(); out = Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
    M = disegna(d)
    r2 = romlib.Rom(bytes(d)); dd = r2.data
    struct.pack_into('<%dH' % M.a.size, dd, M.m['blocks'], *[int(x) for x in M.a.flat])
    m2 = r2.map(*LIDO)
    im = r2.render(m2, events=False, scale=1)
    sprite.disegna(bytes(dd), im, [(o['x'], o['y'], o['gfx']) for o in m2['objects']], 1)
    im = im.resize((im.width * 2, im.height * 2), 0); dr = ImageDraw.Draw(im)
    for x, y, _ in M.cartelli: dr.rectangle((x * 32, y * 32, x * 32 + 31, y * 32 + 31), outline=(255, 220, 0), width=2)
    dr.rectangle((8 * 32, 38 * 32, 8 * 32 + 31, 38 * 32 + 31), outline=(0, 255, 220), width=2)
    im.save(out / 'lido_nuova.png')
    romlib.Rom(bytes(d)).render(romlib.Rom(bytes(d)).map(*LIDO), events=False, scale=2).save(out / 'lido_oggi.png')
    print('cartelli', len(M.cartelli))
