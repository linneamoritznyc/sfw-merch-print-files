"""Workout leggings from the crayon doodle soil: a seamless tile (strokes wrap around the edges) and a mockup.
Output out/leggings/doodle-tile-<way>.png (2400 x 2400, 8 in at 300 dpi, seamless) and mockup.jpg
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fine-art"))
import doodle  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "leggings")
T = 2400
WAYS = {"sage-cream": ((89, 120, 80), (240, 236, 214)), "cream-forest": ((233, 226, 204), (34, 55, 31)),
        "lime-black": ((203, 219, 108), (22, 24, 22)), "lilac-forest": ((185, 169, 218), (34, 55, 31))}

# make strokes wrap around the tile instead of clipping, so the tile repeats with no seam
doodle.W = doodle.H = T
_src = doodle.Crayon.line.__code__
import types


def wrapped_line(s, pts, w=24):
    rng = s.rng; pts = np.asarray(pts, float)
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1); L = seg.sum()
    if L < 2: return
    n = int(L / 1.5)
    t = np.interp(np.linspace(0, L, n), np.r_[0, np.cumsum(seg)], np.arange(len(pts)))
    i = np.clip(t.astype(int), 0, len(pts) - 2); f = (t - i)[:, None]
    p = pts[i] * (1 - f) + pts[i + 1] * f
    from scipy import ndimage as ndi
    p += ndi.gaussian_filter1d(rng.normal(0, 2.2, (n, 2)), 14) * 5
    ww = w * (.8 + .4 * ndi.gaussian_filter1d(rng.random(n), 20))
    for (x, y), r in zip(p, ww):
        k = 40
        ox, oy = rng.uniform(-r / 2, r / 2, k), rng.uniform(-r / 2, r / 2, k)
        np.add.at(s.m, (np.mod((y + oy).astype(int), T), np.mod((x + ox).astype(int), T)), .35)


doodle.Crayon.line = wrapped_line


def tile(seed, ink, paper):
    rng = np.random.default_rng(seed); c = doodle.Crayon(rng); c.m = np.zeros((T, T), np.float32)
    for _ in range(3): doodle.hypha(c, rng.uniform(0, T), rng.uniform(0, T), rng.uniform(0, 6.28), rng.uniform(900, 1300), 2)
    for _ in range(2): doodle.spiral(c, rng.uniform(0, T), rng.uniform(0, T), rng.uniform(180, 260))
    for _ in range(2): doodle.amoeba(c, rng.uniform(0, T), rng.uniform(0, T), rng.uniform(140, 200))
    for _ in range(2): doodle.urn(c, rng.uniform(0, T), rng.uniform(0, T), rng.uniform(180, 240))
    for _ in range(14):
        x, y, r = rng.uniform(0, T), rng.uniform(0, T), rng.uniform(14, 30)
        c.line([(x + r * np.cos(a), y + r * np.sin(a)) for a in np.linspace(0, 6.4, 24)], 14)
    return c.render(ink, paper)


def mockup(tiles):
    """Flat leggings pair per colourway, the tile repeated at real scale (8 in tile on ~38 in inseam)."""
    LEG = [(-150, 0), (150, 0), (165, 120), (20, 140), (0, 160), (-20, 140), (-165, 120)]
    W, H = 420, 1000
    out = Image.new("RGB", (len(tiles) * (W + 20) + 20, H + 40), (230, 230, 228))
    for i, (way, t) in enumerate(tiles.items()):
        scale = 120 / T * 1.0                              # 8 in tile ~ 120 px when the legging is ~1000 px tall
        tt = t.resize((480, 480), Image.LANCZOS)
        fab = Image.new("RGB", (W, H))
        for x in range(0, W, tt.width):
            for y in range(0, H, tt.height): fab.paste(tt, (x, y))
        m = Image.new("L", (W, H), 0); d = ImageDraw.Draw(m)
        d.polygon([(40, 20), (380, 20), (395, 140), (360, 980), (250, 980), (215, 230), (205, 230), (170, 980), (60, 980), (25, 140)], fill=255)
        can = Image.new("RGB", (W, H), (230, 230, 228)); can.paste(fab, (0, 0), m)
        dd = ImageDraw.Draw(can); dd.rectangle((40, 20, 380, 70), fill=tuple(int(v * .8) for v in t.getpixel((5, 5))))
        dd.polygon([(40, 20), (380, 20), (395, 140), (360, 980), (250, 980), (215, 230), (205, 230), (170, 980), (60, 980), (25, 140)], outline=(80, 80, 80), width=2)
        out.paste(can, (20 + i * (W + 20), 20))
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    tiles = {}
    for i, (way, (ink, paper)) in enumerate(WAYS.items()):
        t = tile(7, ink, paper); t.save(os.path.join(OUT, f"doodle-tile-{way}.png"), dpi=(300, 300)); tiles[way] = t
    t = tiles["sage-cream"]; check = Image.new("RGB", (1200, 1200))
    s = t.resize((600, 600), Image.LANCZOS)
    for x in (0, 600):
        for y in (0, 600): check.paste(s, (x, y))
    check.save(os.path.join(OUT, "seam-check.jpg"), quality=88)
    mockup(tiles).save(os.path.join(OUT, "mockup.jpg"), quality=90)


if __name__ == "__main__":
    main()
