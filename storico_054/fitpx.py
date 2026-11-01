"""A capo in base alla larghezza in pixel (tabelle dei font della ROM), con limiti presi dai testi inglesi originali."""
from text_codec import CHAR
FONTS = (0x7dec78, 0x7ef078, 0x7ff478, 0x7f7278, 0x7e6e78)
_INV = {}
for k, v in CHAR.items():
    if isinstance(v, str) and len(v) == 1 and v not in _INV: _INV[v] = k
_INV['È'] = 5
def width(d, s, t):
    return sum(d[t + _INV.get(c, 0xbb)] for c in s)
def limits(d, lines_list):
    return {t: max(width(d, l, t) for l in lines_list) for t in FONTS}
def wrap(d, text, lim, max_lines):
    words = text.split(' '); lines = []; cur = ''
    for w in words:
        cand = (cur + ' ' + w).strip()
        if all(width(d, cand, t) <= lim[t] for t in FONTS): cur = cand
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines if len(lines) <= max_lines and all(all(width(d, l, t) <= lim[t] for t in FONTS) for l in lines) else None
