"""Global placement of outdoor maps; connections are derived from shared edges."""

# name: (map id constant, x, y, w, h)
MAPS = {
    'LittlerootTown': ('MAP_LITTLEROOT_TOWN', 0, 0, 44, 36),
    'Route101': ('MAP_ROUTE101', 0, 36, 30, 40),
    'Romagna_PassaggioCostiero': ('MAP_ROMAGNA_PASSAGGIO_COSTIERO', 30, 36, 14, 40),
    'OldaleTown': ('MAP_OLDALE_TOWN', 0, 76, 44, 40),
    'Romagna_SentieroSaline': ('MAP_ROMAGNA_SENTIERO_SALINE', -24, 84, 24, 18),
    'Romagna_Saline': ('MAP_ROMAGNA_SALINE', -72, 76, 48, 40),
    'Romagna_ViaSavio': ('MAP_ROMAGNA_VIA_SAVIO', 4, 116, 30, 40),
    'Romagna_Cesena': ('MAP_ROMAGNA_CESENA', -12, 156, 54, 44),
    'Romagna_StradaMare': ('MAP_ROMAGNA_STRADA_MARE', 42, 164, 44, 26),
    'Romagna_Cesenatico': ('MAP_ROMAGNA_CESENATICO', 86, 152, 46, 44),
    'Romagna_Riviera': ('MAP_ROMAGNA_RIVIERA', 92, 196, 34, 44),
    'Romagna_RiminiPorto': ('MAP_ROMAGNA_RIMINI_PORTO', 88, 240, 44, 38),
    'Romagna_RiminiCentro': ('MAP_ROMAGNA_RIMINI_CENTRO', 36, 236, 52, 46),
    'Romagna_Befane': ('MAP_ROMAGNA_BEFANE', 44, 282, 32, 22),
    'Romagna_Ippodromo': ('MAP_ROMAGNA_IPPODROMO', -52, 166, 40, 28),
    'Romagna_VersoForli': ('MAP_ROMAGNA_VERSO_FORLI', -102, 170, 50, 22),
    'Romagna_Forli': ('MAP_ROMAGNA_FORLI', -160, 160, 58, 46),
}

# pairs that are actually linked (both directions are written)
LINKS = [
    ('LittlerootTown', 'Route101'), ('LittlerootTown', 'Romagna_PassaggioCostiero'),
    ('Route101', 'OldaleTown'), ('Romagna_PassaggioCostiero', 'OldaleTown'),
    ('OldaleTown', 'Romagna_SentieroSaline'), ('Romagna_SentieroSaline', 'Romagna_Saline'),
    ('OldaleTown', 'Romagna_ViaSavio'), ('Romagna_ViaSavio', 'Romagna_Cesena'),
    ('Romagna_Cesena', 'Romagna_StradaMare'), ('Romagna_StradaMare', 'Romagna_Cesenatico'),
    ('Romagna_Cesenatico', 'Romagna_Riviera'), ('Romagna_Riviera', 'Romagna_RiminiPorto'),
    ('Romagna_RiminiPorto', 'Romagna_RiminiCentro'), ('Romagna_RiminiCentro', 'Romagna_Befane'),
    ('Romagna_Cesena', 'Romagna_Ippodromo'), ('Romagna_Ippodromo', 'Romagna_VersoForli'),
    ('Romagna_VersoForli', 'Romagna_Forli'),
]


def add(name, mid, x, y, w, h, links=()):
    MAPS[name] = (mid, x, y, w, h)
    for l in links:
        LINKS.append((name, l))


def connection(a, b):
    """Connection entry for map a towards map b, or None if they don't share an edge."""
    ida, ax, ay, aw, ah = MAPS[a]
    idb, bx, by, bw, bh = MAPS[b]
    if by == ay + ah and bx < ax + aw and bx + bw > ax:
        return dict(map=idb, offset=bx - ax, direction='down')
    if by + bh == ay and bx < ax + aw and bx + bw > ax:
        return dict(map=idb, offset=bx - ax, direction='up')
    if bx == ax + aw and by < ay + ah and by + bh > ay:
        return dict(map=idb, offset=by - ay, direction='right')
    if bx + bw == ax and by < ay + ah and by + bh > ay:
        return dict(map=idb, offset=by - ay, direction='left')
    return None


def connections(name):
    out = []
    for a, b in LINKS:
        other = b if a == name else a if b == name else None
        if other is None:
            continue
        c = connection(name, other)
        if c is None:
            raise ValueError('maps do not touch: %s %s' % (name, other))
        out.append(c)
    return out


def size(name):
    return MAPS[name][3], MAPS[name][4]


def edge_overlap(a, b):
    """Local coordinates range on map a's edge shared with b: (side, start, end)."""
    c = connection(a, b)
    ida, ax, ay, aw, ah = MAPS[a]
    idb, bx, by, bw, bh = MAPS[b]
    if c['direction'] in ('up', 'down'):
        s, e = max(ax, bx) - ax, min(ax + aw, bx + bw) - ax
    else:
        s, e = max(ay, by) - ay, min(ay + ah, by + bh) - ay
    return c['direction'], s, e
