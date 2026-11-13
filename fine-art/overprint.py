"""Full-bleed riso overprints from student soil micrographs. No circles.
Each micrograph is split into three spot-ink layers (masses, halftone shading, fine edges), printed with
multiply overprint and a little misregistration, like a real risograph.
Outputs out/overprint/*.png at product sizes (see SIZES).
"""
import os, math, io, sys
import numpy as np
from PIL import Image, ImageOps, ImageChops
from scipy import ndimage as ndi
import cairosvg
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "field-guide"))
from euglypha import text  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SRC, OUT = os.path.join(HERE, "src"), os.path.join(HERE, "out", "overprint")
rng = np.random.default_rng(4)
PAPER = (250, 248, 242)
RISO = {"green": (0, 169, 92), "violet": (118, 91, 167), "blue": (0, 120, 191), "pink": (255, 72, 176),
        "yellow": (255, 232, 0), "black": (30, 30, 30), "teal": (0, 131, 138), "mint": (130, 216, 213)}


def load(name, box=None, size=(2000, 2000)):
    im = Image.open(os.path.join(SRC, name + ".jpg")).convert("L")
    if name == "fungal-hypha-lee-kirk":
        im = im.crop((0, 20, im.width, im.height - 30))
    if box:
        w, h = im.size; im = im.crop((int(box[0] * w), int(box[1] * h), int(box[2] * w), int(box[3] * h)))
    im = ImageOps.fit(im, size, Image.LANCZOS)
    g = np.asarray(ImageOps.autocontrast(im, cutoff=1), np.float32) / 255
    d = ndi.gaussian_filter(g, max(size) / 10) - g          # darkness against the local paper: the organisms
    return g, d


def halftone(v, cell=18, ang=15):
    """Amplitude dots: v in 0..1 -> boolean dot mask."""
    h, w = v.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    a = math.radians(ang)
    u = xx * math.cos(a) + yy * math.sin(a); t = -xx * math.sin(a) + yy * math.cos(a)
    du = (u % cell) - cell / 2; dt = (t % cell) - cell / 2
    return np.hypot(du, dt) < (cell * .72) * np.sqrt(np.clip(v, 0, 1))


def grain(m, p):
    return m & (rng.random(m.shape, dtype=np.float32) < p)


def layers(g, d, scale=1.0):
    """Three plates: solid masses, halftone shading, fine white-space edges."""
    dd = ndi.gaussian_filter(d, 1.5 * scale)
    mass = dd > np.quantile(dd, .78)
    mass = ndi.binary_opening(mass, iterations=max(1, int(2 * scale)))
    shade = np.clip((dd - np.quantile(dd, .4)) / (np.quantile(dd, .97) - np.quantile(dd, .4)), 0, 1)
    e = np.hypot(ndi.sobel(g, 0), ndi.sobel(g, 1))
    edge = e > np.quantile(e, .95)
    return grain(mass, .93), halftone(shade, 14 * scale, 22), grain(edge, .85)


def overprint(plates, size, paper=PAPER, shift=6):
    """plates: list of (bool mask, ink name). Multiply each ink onto the paper with a small misregistration."""
    out = np.ones((size[1], size[0], 3), np.float32) * np.array(paper, np.float32) / 255
    for i, (m, ink) in enumerate(plates):
        dx, dy = rng.integers(-shift, shift + 1, 2)
        m = np.roll(np.roll(m, dy, 0), dx, 1)
        c = np.array(RISO[ink], np.float32) / 255
        out[m] *= c * .92 + .08
    return Image.fromarray((out * 255).astype(np.uint8))


def type_layer(lines, size, y0, px, track=40, fnt="eb-garamond-latin-600-normal.woff2"):
    W, H = size
    svg = "".join(text(t, px, W / 2, y0 + i * px * .92, fnt=fnt, anchor="middle", color="#000", track=track)[0] for i, t in enumerate(lines))
    png = cairosvg.svg2png(bytestring=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">{svg}</svg>'.encode())
    return np.asarray(Image.open(io.BytesIO(png)).convert("RGBA"))[:, :, 3] > 128


def save(im, name, dpi):
    os.makedirs(OUT, exist_ok=True)
    im.save(os.path.join(OUT, name + ".png"), dpi=(dpi, dpi))
    p = im.copy(); p.thumbnail((900, 900)); p.save(os.path.join(OUT, name + "-preview.jpg"), quality=88)


# ------------------------------------------------------------------ designs
def powered_by_protozoa():
    """Poster 18 x 24 in: a testate amoeba, three inks, the slogan overprinted in violet."""
    size = (3600, 4800)
    g, d = load("testate-amoeba-encysting-40x-joy-kaluf", (.18, .05, .78, .95), size)
    mass, shade, edge = layers(g, d, 2.2)
    words = type_layer(["POWERED", "BY PROTOZOA"], size, 3950, 520, 60)
    im = overprint([(shade, "blue"), (mass, "green"), (edge, "violet"), (words, "pink")], size, shift=10)
    save(im, "poster-powered-by-protozoa-18x24", 200)


def kaleidoscope(name, src, box, inks, paper=PAPER):
    """Square, 8-fold mirror symmetric, for pillow, bandana, puzzle. 18 in at 250 dpi."""
    S = 4500; h = S // 2
    g, d = load(src, box, (h, h))
    mass, shade, edge = layers(g, d, 1.6)
    out = []
    for m in (mass, shade, edge):
        tri = np.triu(np.ones((h, h), bool))                  # keep one triangle, mirror it across the diagonal
        q = np.where(tri, m, m.T)
        quad = np.block([[q[::-1, ::-1], q[::-1, :]], [q[:, ::-1], q]])
        out.append(quad)
    im = overprint(list(zip(out, inks)), (S, S), paper, shift=8)
    save(im, name, 250)


def horizons():
    """Tall strip: soil horizons, each band a different micrograph in a different ink. Beach towel 30 x 60 in, socks, wrapping."""
    W, H = 3000, 6000
    bands = [("fungal-spore-josia-martens", (.2, .2, .9, .7), ("yellow", "green")),
             ("nematode-molting-cameron-radman", (.0, .0, .8, .5), ("mint", "blue")),
             ("testate-encysting-jimena-fuentes-i2", (.0, .2, .7, .9), ("pink", "violet")),
             ("stellate-amoeba-jimena-fuentes", (.25, .1, .8, .9), ("yellow", "teal")),
             ("mite-talbot-armstrong-i3", (.1, .1, .9, .9), ("mint", "violet")),
             ("fungal-hypha-lee-kirk", (.1, .3, .9, .9), ("yellow", "green"))]
    hs = [1300, 800, 1100, 700, 1200, 900]
    plates = {}
    y = 0
    full = [np.zeros((H, W), bool) for _ in range(3)]
    inks_by_plate = []
    canvas = np.ones((H, W, 3), np.float32) * np.array(PAPER, np.float32) / 255
    for (src, box, (ink1, ink2)), bh in zip(bands, hs):
        g, d = load(src, box, (W, bh))
        mass, shade, edge = layers(g, d, 1.4)
        for m, ink in ((shade, ink1), (mass, ink2), (edge, ink2)):
            dx, dy = rng.integers(-6, 7, 2)
            mm = np.zeros((H, W), bool); mm[y:y + bh] = np.roll(np.roll(m, dy, 0), dx, 1)
            c = np.array(RISO[ink], np.float32) / 255
            canvas[mm] *= c * .92 + .08
        y += bh
        if y < H:                                             # thin wavy horizon line between bands
            xs = np.arange(W); yy = (y + 18 * np.sin(xs / 210 + y)).astype(int)
            for t in range(-4, 5):
                canvas[np.clip(yy + t, 0, H - 1), xs] *= np.array(RISO["black"], np.float32) / 255 * .9 + .1
    save(Image.fromarray((canvas * 255).astype(np.uint8)), "horizons-30x60", 100)


def field(name, src, box, inks, size=(5400, 3600), paper=PAPER, dpi=150):
    """Full-bleed landscape field: blanket 60 x 50 / desk mat / weekender."""
    g, d = load(src, box, size)
    mass, shade, edge = layers(g, d, 2.0)
    save(overprint([(shade, inks[0]), (mass, inks[1]), (edge, inks[2])], size, paper, shift=10), name, dpi)


if __name__ == "__main__" and "students" not in sys.argv:
    powered_by_protozoa()
    kaleidoscope("kaleido-hypha-pillow-18", "fungal-hypha-lee-kirk", (.05, .25, .75, .95), ("yellow", "green", "violet"))
    kaleidoscope("kaleido-mite-bandana-18", "mite-talbot-armstrong-i3", (.15, .05, .85, .95), ("mint", "violet", "black"))
    kaleidoscope("kaleido-stellate-puzzle-18", "stellate-amoeba-jimena-fuentes", (.3, .15, .8, .85), ("pink", "blue", "black"))
    horizons()
    field("field-spores-blanket", "fungal-spores-in-suspension", None, ("mint", "blue", "pink"))
    field("field-aggregate-deskmat", "testate-encysted-robert-kenyon", None, ("yellow", "green", "black"), size=(5400, 2700))


# ------------------------------------------------------------------ mugs and student notebooks from kaleidoscopes
KALEIDOS = [  # name, source, crop, inks (shade, mass, edge), paper
    ("stellate", "stellate-amoeba-jimena-fuentes", (.3, .15, .8, .85), ("pink", "blue", "black"), PAPER),
    ("hypha", "fungal-hypha-lee-kirk", (.05, .25, .75, .95), ("yellow", "green", "violet"), PAPER),
    ("testate", "testate-encysting-jimena-fuentes-i2", (.0, .2, .6, .9), ("mint", "violet", "black"), PAPER),
    ("nematode", "nematode-molting-cameron-radman", (.0, .0, .7, .55), ("yellow", "teal", "blue"), PAPER),
    ("mite", "mite-talbot-armstrong-i3", (.2, .1, .8, .9), ("pink", "green", "black"), PAPER),
    ("spore", "fungal-spore-josia-martens", (.25, .1, .85, .7), ("mint", "violet", "green"), PAPER),
]


def kaleido_img(src, box, inks, paper, S=2400):
    h = S // 2
    g, d = load(src, box, (h, h))
    planes = []
    for m in layers(g, d, 1.1):
        q = np.where(np.triu(np.ones((h, h), bool)), m, m.T)
        planes.append(np.block([[q[::-1, ::-1], q[::-1, :]], [q[:, ::-1], q]]))
    return overprint(list(zip(planes, inks)), (S, S), paper, shift=5)


def tiled(k, W, H, size, x0=0, y0=0):
    t = k.resize((size, size), Image.LANCZOS)
    out = Image.new("RGB", (W, H))
    for x in range(x0 - size, W, size):
        for y in range(y0 - size, H, size):
            out.paste(t, (x, y))
    return out


def student_set():
    for name, src, box, inks, paper in KALEIDOS:
        k = kaleido_img(src, box, inks, paper)
        save(k, f"kaleido-{name}", 300)
        # 11 oz mug wrap, 9 x 3.5 in at 300 dpi: one full kaleidoscope centred on each side
        save(tiled(k, 2700, 1050, 1050, x0=(2700 // 2 - 1050 // 2) % 1050, y0=0), f"mug-11oz-{name}", 300)
        # notebook cover 5.75 x 8 in plus 1/8 in bleed, 300 dpi: one kaleidoscope across the front, repeated down
        save(tiled(k, 1800, 2475, 1800, x0=0, y0=(2475 - 1800) // 2), f"notebook-{name}", 300)


if __name__ == "__main__" and "students" in sys.argv:
    student_set()
