"""Riso-style soil: real student micrographs separated into spot inks on black, like a multi-drum risograph.
Every blob of soil life becomes one flat ink with print grain; edges and small particles print white.
Outputs out/riso/:
  circle-<n>.png            single fields of view, transparent outside the circle (stickers, pins, patches)
  poster-grid.png           2 x 4 grid on black, A-ratio
  allover.png               seamless scatter of circles for all-over print (tote, scarf, phone case)
  sticker-sheet.png         12 circles on white with cut margin
"""
import os, math
import numpy as np
from PIL import Image, ImageDraw, ImageOps
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
SRC, OUT = os.path.join(HERE, "src"), os.path.join(HERE, "out", "riso")
rng = np.random.default_rng(21)
BLACK = np.array([10, 10, 10])
INKS = {"mint": (78, 196, 140), "lilac": (196, 176, 240), "lime": (200, 226, 70), "white": (250, 250, 245), "pink": (240, 120, 150)}
PALETTES = [("mint", "lilac", "lime"), ("mint", "lime", "lilac"), ("lilac", "mint", "lime"), ("mint", "pink", "lime")]

FIELDS = [  # source, centre (fractions), radius (fraction of short side)
    ("fungal-hypha-lee-kirk", (.55, .55), .45), ("testate-encysting-jimena-fuentes-i2", (.5, .5), .38),
    ("testate-encysted-robert-kenyon", (.4, .45), .42), ("nematode-molting-cameron-radman", (.5, .35), .4),
    ("fungal-spore-josia-martens", (.4, .45), .3), ("mite-talbot-armstrong-i3", (.5, .5), .45),
    ("stellate-amoeba-jimena-fuentes", (.55, .5), .32), ("testate-encysted-sid-jensen", (.6, .5), .4),
    ("testate-amoeba-encysting-40x-joy-kaluf", (.4, .55), .35), ("reproductive-structure-holly-bain", (.5, .5), .45),
    ("fungal-spores-in-suspension", (.5, .5), .4), ("testate-encysted-robert-kenyon", (.75, .35), .25),
]


def grain(mask, density):
    """Riso grain: stochastic dither so flat inks look printed."""
    return mask & (rng.random(mask.shape) < density)


def riso(src, centre, rad, pal, n=1400):
    im = Image.open(os.path.join(SRC, src + ".jpg")).convert("L")
    if src == "fungal-hypha-lee-kirk":
        im = im.crop((0, 20, im.width, im.height - 30))
    s = min(im.size) * rad
    cx, cy = im.width * centre[0], im.height * centre[1]
    im = im.crop((int(cx - s), int(cy - s), int(cx + s), int(cy + s))).resize((n, n), Image.LANCZOS)
    g = np.asarray(ImageOps.autocontrast(im, cutoff=1), float) / 255
    bg = ndi.gaussian_filter(g, n / 10)
    d = bg - g                                                # how much darker than the local paper: the organisms
    d = ndi.gaussian_filter(d, 1.2)
    stuff = d > np.quantile(d, .72)
    stuff = ndi.binary_opening(stuff, iterations=2)
    lab, k = ndi.label(stuff)
    sizes = ndi.sum(stuff, lab, range(1, k + 1))
    out = np.tile(BLACK, (n, n, 1)).astype(float)
    order = np.argsort(-sizes)
    for rank, i in enumerate(order):
        m = lab == (i + 1)
        if sizes[i] < 60:
            out[grain(m, .9)] = INKS["white"]; continue
        ink = pal[0] if rank < 2 else pal[1] if rank % 3 == 0 else pal[2] if rank % 3 == 1 else pal[0]
        dens = .55 + .45 * np.clip((d[m] - d[m].min()) / (np.ptp(d[m]) + 1e-9), 0, 1)
        sel = np.zeros_like(m); sel[m] = rng.random(m.sum()) < dens
        out[sel] = INKS[ink]
        inner = m & ~ndi.binary_erosion(m, iterations=3)       # white printed rim on each organism
        out[grain(inner, .8)] = INKS["white"]
    edges = np.hypot(ndi.sobel(g, 0), ndi.sobel(g, 1))
    e = (edges > np.quantile(edges, .965)) & ~stuff
    out[grain(e, .75)] = INKS["white"]
    bright = (g - bg) > np.quantile(g - bg, .995)              # bright particles and halos
    out[grain(ndi.binary_dilation(bright), .85)] = INKS["white"]
    img = Image.fromarray(out.astype(np.uint8)).convert("RGBA")
    mask = Image.new("L", (n * 2, n * 2), 0); ImageDraw.Draw(mask).ellipse((0, 0, n * 2 - 1, n * 2 - 1), fill=255)
    mask = mask.resize((n, n), Image.LANCZOS)
    img.putalpha(mask)
    ring = Image.new("RGBA", (n, n), (0, 0, 0, 0)); ImageDraw.Draw(ring).ellipse((2, 2, n - 3, n - 3), outline=(250, 250, 245, 255), width=3)
    img.alpha_composite(ring)
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    circles = []
    for i, (src, c, r) in enumerate(FIELDS):
        img = riso(src, c, r, PALETTES[i % len(PALETTES)])
        img.save(os.path.join(OUT, f"circle-{i + 1:02d}.png"))
        circles.append(img)
    # poster grid 2 x 4 on black, A-ratio landscape
    W, H = 4961, 3508
    page = Image.new("RGBA", (W, H), (10, 10, 10, 255))
    d = 1080; gx = (W - 4 * d) // 5; gy = (H - 2 * d) // 3
    for k in range(8):
        r, c = divmod(k, 4)
        page.alpha_composite(circles[k].resize((d, d), Image.LANCZOS), (gx + c * (d + gx), gy + r * (d + gy)))
    page.convert("RGB").save(os.path.join(OUT, "poster-grid.png"), dpi=(150, 150))
    # seamless all-over scatter, 3000 px tile
    T = 3000
    tile = Image.new("RGBA", (T, T), (10, 10, 10, 255))
    placed = []
    for _ in range(4000):
        if len(placed) >= 14: break
        dd = int(rng.uniform(520, 900)); x, y = rng.uniform(0, T), rng.uniform(0, T)
        ok = all(min(abs(x - px), T - abs(x - px)) ** 2 + min(abs(y - py), T - abs(y - py)) ** 2 > ((dd + pd) / 2 + 30) ** 2 for px, py, pd in placed)
        if ok: placed.append((x, y, dd))
    for j, (x, y, dd) in enumerate(placed):
        c = circles[j % len(circles)].resize((dd, dd), Image.LANCZOS).rotate(rng.uniform(0, 360))
        for ox in (-T, 0, T):
            for oy in (-T, 0, T):
                tile.alpha_composite(c, (int(x - dd / 2 + ox), int(y - dd / 2 + oy))) if -dd < x - dd / 2 + ox < T and -dd < y - dd / 2 + oy < T else None
    tile.convert("RGB").save(os.path.join(OUT, "allover.png"), dpi=(300, 300))
    # sticker sheet 5.83 x 8.27 in at 300 dpi, 3 x 4, white with cut margin
    SW, SH = 1749, 2481
    sheet = Image.new("RGBA", (SW, SH), (255, 255, 255, 255))
    d = 470
    for k in range(12):
        r, c = divmod(k, 3)
        x = 120 + c * (d + 80); y = 120 + r * (d + 110)
        sheet.alpha_composite(circles[k].resize((d, d), Image.LANCZOS), (x, y))
    sheet.convert("RGB").save(os.path.join(OUT, "sticker-sheet.png"), dpi=(300, 300))


if __name__ == "__main__":
    main()
