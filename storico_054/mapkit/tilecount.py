def count_tiles(im):
    """Unique 8x8 tiles (with flips) of an RGBA image."""
    px=im.load(); seen=set(); n=0
    for ty in range(0,im.height,8):
        for tx in range(0,im.width,8):
            t=tuple(px[tx+x,ty+y] for y in range(8) for x in range(8))
            if all(c[3]==0 for c in t): continue
            forms=[t, tuple(t[y*8+7-x] for y in range(8) for x in range(8)), tuple(t[(7-y)*8+x] for y in range(8) for x in range(8)), tuple(t[(7-y)*8+7-x] for y in range(8) for x in range(8))]
            if any(f in seen for f in forms): continue
            seen.add(t); n+=1
    return n
