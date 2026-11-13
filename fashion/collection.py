"""SFW runway collection 01, 'Under the Lens'.
Prints: real student micrographs, posterised to two or three inks, mirrored into seamless symmetric repeats.
Output:
  out/prints/<print>-<colourway>.png   seamless 4000 px tiles (repeat for all-over print, 150 dpi = 26.7 in)
  out/lineup.png                       runway line-up of eight looks wearing the prints
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "fine-art", "src")
OUT = os.path.join(HERE, "out")

DEEP, FWG, LIGHT, WHITE, BLACK = (34, 55, 31), (21, 104, 38), (89, 166, 108), (255, 255, 255), (12, 14, 12)
WAYS = {"forest": (DEEP, LIGHT, WHITE), "night": (BLACK, FWG, LIGHT), "field": (WHITE, LIGHT, FWG), "moss": (FWG, DEEP, WHITE)}

PRINTS = {   # name: (source, crop box as fractions, smoothing, levels)
    "hypha": ("fungal-spore-josia-martens", (.30, .10, .80, .60), 1.2, (.42, .62)),
    "testate": ("testate-amoeba-encysting-40x-joy-kaluf", (.15, .05, .75, .85), 1.0, (.40, .60)),
    "stellate": ("stellate-amoeba-jimena-fuentes", (.30, .20, .75, .80), 1.0, (.45, .66)),
    "nematode": ("nematode-molting-cameron-radman", (.05, .05, .75, .55), 1.4, (.45, .62)),
    "aggregate": ("testate-encysting-jimena-fuentes-i2", (0, .15, .60, .95), 1.6, (.38, .58)),
}


def posterise(name, colours, n=2000):
    src, (a, b, c, d), sig, (t1, t2) = PRINTS[name]
    im = Image.open(os.path.join(SRC, src + ".jpg")).convert("L")
    w, h = im.size
    im = im.crop((int(a * w), int(b * h), int(c * w), int(d * h)))
    s = min(im.size); im = im.crop((0, 0, s, s)).resize((n, n), Image.LANCZOS)
    g = np.asarray(ImageOps.autocontrast(im, cutoff=1), float) / 255
    g = g - ndi.gaussian_filter(g, n / 12) * .6                         # flatten uneven microscope light
    g = ndi.gaussian_filter(g, sig * n / 1000)
    g = (g - g.min()) / (np.ptp(g) + 1e-9)
    q1, q2 = np.quantile(g, t1), np.quantile(g, t2)
    lvl = np.where(g < q1, 0, np.where(g < q2, 1, 2))
    out = np.array(colours)[lvl].astype(np.uint8)
    tile = Image.fromarray(out)
    full = Image.new("RGB", (2 * n, 2 * n))                            # mirror into a seamless symmetric repeat
    full.paste(tile, (0, 0)); full.paste(ImageOps.mirror(tile), (n, 0))
    full.paste(ImageOps.flip(tile), (0, n)); full.paste(ImageOps.flip(ImageOps.mirror(tile)), (n, n))
    return full


def fabric(tile, w, h, scale=.25):
    t = tile.resize((int(tile.width * scale), int(tile.height * scale)), Image.LANCZOS)
    f = Image.new("RGB", (w, h))
    for x in range(0, w, t.width):
        for y in range(0, h, t.height):
            f.paste(t, (x, y))
    return f


# ------------------------------------------------------------------ garments as flat shapes on a figure column
def P(pts, x, y, s):
    return [(x + px * s, y + py * s) for px, py in pts]


GARMENTS = {
    "zip hoodie": [[(-60, 0), (-30, -10), (0, 8), (30, -10), (60, 0), (110, 120), (130, 330), (95, 335), (75, 150), (70, 360), (-70, 360), (-75, 150), (-95, 335), (-130, 330), (-110, 120)]],
    "vest": [[(-55, 0), (-25, -8), (0, 30), (25, -8), (55, 0), (60, 90), (78, 120), (78, 380), (-78, 380), (-78, 120), (-60, 90)]],
    "leggings": [[(-62, 0), (62, 0), (68, 120), (52, 470), (18, 470), (4, 140), (-4, 140), (-18, 470), (-52, 470), (-68, 120)]],
    "skirt": [[(-55, 0), (55, 0), (120, 330), (-120, 330)]],
    "tee": [[(-55, 0), (-25, -6), (0, 10), (25, -6), (55, 0), (115, 50), (95, 120), (68, 95), (68, 300), (-68, 300), (-68, 95), (-95, 120), (-115, 50)]],
    "trousers": [[(-64, 0), (64, 0), (80, 470), (20, 470), (4, 120), (-4, 120), (-20, 470), (-80, 470)]],
    "dress": [[(-48, 0), (-22, -6), (0, 12), (22, -6), (48, 0), (60, 60), (50, 170), (130, 640), (-130, 640), (-50, 170), (-60, 60)]],
    "coat": [[(-62, 0), (-30, -12), (0, 20), (30, -12), (62, 0), (115, 120), (135, 420), (100, 425), (82, 180), (95, 720), (-95, 720), (-82, 180), (-100, 425), (-135, 420), (-115, 120)]],
    "bandana": [[(-60, 0), (60, 0), (0, 70)]],
    "scrunchie": [],
}

LOOKS = [  # (top garment, print, way, bottom garment, print, way, accessory)
    ("coat", "hypha", "forest", None, None, None, None),
    ("zip hoodie", "testate", "night", "leggings", "testate", "night", None),
    ("dress", "stellate", "field", None, None, None, "bandana"),
    ("vest", "aggregate", "moss", "trousers", "hypha", "forest", None),
    ("tee", "nematode", "field", "skirt", "nematode", "night", None),
    ("zip hoodie", "hypha", "moss", "trousers", "hypha", "moss", None),
    ("dress", "testate", "forest", None, None, None, None),
    ("coat", "stellate", "night", "leggings", "aggregate", "night", "bandana"),
]


def lineup(tiles):
    Wd, Hd = 6400, 2400
    page = Image.new("RGB", (Wd, Hd), WHITE)
    dr = ImageDraw.Draw(page)
    s = 1.55
    for i, (top, tp, tw, bot, bp, bw, acc) in enumerate(LOOKS):
        cx = int(Wd / (len(LOOKS) + 1) * (i + 1)); ytop = 420
        # figure: a quiet grey column, head and limbs
        grey = (226, 228, 224)
        dr.ellipse((cx - 34, ytop - 210, cx + 34, ytop - 120), fill=grey)
        dr.rectangle((cx - 14, ytop - 125, cx + 14, ytop), fill=grey)
        dr.polygon(P([(-18, 760), (-8, 1180), (-30, 1200), (-40, 760)], cx, ytop, s), fill=grey)
        dr.polygon(P([(18, 760), (8, 1180), (30, 1200), (40, 760)], cx, ytop, s), fill=grey)
        dr.polygon(P([(-62, 0), (62, 0), (64, 760), (-64, 760)], cx, ytop, s * .98), fill=grey)
        dr.polygon(P([(-62, 10), (-110, 380), (-95, 385), (-50, 60)], cx, ytop, s), fill=grey)
        dr.polygon(P([(62, 10), (110, 380), (95, 385), (50, 60)], cx, ytop, s), fill=grey)
        layers = []
        if bot:
            layers.append((bot, bp, bw, 290 if top in ("vest",) else 300 if top == "tee" else 330))
        layers.append((top, tp, tw, 0))
        for g, pr, way, yoff in layers:
            for poly in GARMENTS[g]:
                pts = P(poly, cx, ytop + yoff * s, s)
                m = Image.new("L", page.size, 0); ImageDraw.Draw(m).polygon(pts, fill=255)
                fab = fabric(tiles[(pr, way)], Wd, Hd, .14 + .02 * (i % 3))
                page.paste(fab, (0, 0), m)
                dr.line(pts + pts[:1], fill=(60, 60, 60), width=3)
            if g in ("zip hoodie", "coat"):
                dr.line([(cx, ytop + 8 * s), (cx, ytop + (360 if g == "zip hoodie" else 720) * s)], fill=(60, 60, 60), width=4)
        if acc == "bandana":
            pts = P(GARMENTS["bandana"][0], cx, ytop - 150, 1.0)
            m = Image.new("L", page.size, 0); ImageDraw.Draw(m).polygon(pts, fill=255)
            page.paste(fabric(tiles[("hypha", "forest")], Wd, Hd, .08), (0, 0), m)
        dr.text((cx - 20, 2240), f"{i + 1:02d}", fill=DEEP)
    return page


def main():
    os.makedirs(os.path.join(OUT, "prints"), exist_ok=True)
    tiles = {}
    for name in PRINTS:
        for way, cols in WAYS.items():
            t = posterise(name, cols)
            t.save(os.path.join(OUT, "prints", f"{name}-{way}.png"), dpi=(150, 150))
            tiles[(name, way)] = t
    lineup(tiles).save(os.path.join(OUT, "lineup.png"))
    sheet = Image.new("RGB", (5 * 520 + 40, 4 * 520 + 40), WHITE)       # swatch board
    for i, name in enumerate(PRINTS):
        for j, way in enumerate(WAYS):
            sheet.paste(fabric(tiles[(name, way)], 500, 500, .125), (20 + i * 520, 20 + j * 520))
    sheet.save(os.path.join(OUT, "swatches.png"))


if __name__ == "__main__":
    main()
