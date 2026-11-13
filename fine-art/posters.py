"""SFW fine art posters from the microbe library. A-series ratio, 3508 x 4961 px (A1 at 150 dpi, A2 at 212 dpi).
Every image is a real soil micrograph by a Soil Food Web School student, toned in SFW greens. Nothing generated.
Usage: python3 posters.py   -> out/<name>.png + .pdf
"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps
from scipy.spatial import Voronoi
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "field-guide"))
from euglypha import text  # noqa: E402
import cairosvg  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SRC, OUT = os.path.join(HERE, "src"), os.path.join(HERE, "out")
W, H = 3508, 4961
rng = np.random.default_rng(7)

# tone ramp after the SFW microscopy look: deep green -> food web green -> light green -> pale
RAMP = [(0.0, (16, 52, 33)), (.35, (21, 104, 38)), (.62, (89, 166, 108)), (.82, (190, 218, 140)), (1.0, (244, 248, 226))]
CREDIT = {
    "fungal-hypha-lee-kirk": "Lee Kirk", "fungal-spore-josia-martens": "Josia Martens",
    "mite-talbot-armstrong-i3": "Talbot Armstrong", "nematode-molting-cameron-radman": "Cameron Radman",
    "reproductive-structure-holly-bain": "Holly Bain", "stellate-amoeba-jimena-fuentes": "Jimena Fuentes",
    "testate-encysted-robert-kenyon": "Robert Kenyon", "testate-encysted-sid-jensen": "Sid Jensen",
    "testate-encysting-jimena-fuentes-i2": "Jimena Fuentes", "fungal-spores-in-suspension": "SFW",
    "testate-amoeba-encysting-40x-joy-kaluf": "Joy Kaluf",
}


def tone(im, contrast=1.25, gamma=1.0):
    g = np.asarray(ImageOps.autocontrast(im.convert("L"), cutoff=1), float) / 255
    g = np.clip((g - .5) * contrast + .5, 0, 1) ** gamma
    out = np.zeros(g.shape + (3,))
    for (a, ca), (b, cb) in zip(RAMP, RAMP[1:]):
        m = (g >= a) & (g <= b); t = ((g - a) / (b - a))[m][:, None]
        out[m] = np.array(ca) * (1 - t) + np.array(cb) * t
    return Image.fromarray(out.astype(np.uint8))


def load(name, crop=None):
    im = Image.open(os.path.join(SRC, name + ".jpg")).convert("RGB")
    if name == "fungal-hypha-lee-kirk":
        im = im.crop((0, 20, im.width, im.height - 30))       # remove camera header and footer text
    return im.crop(crop) if crop else im


def circle(im, d):
    s = min(im.size); im = im.crop(((im.width - s) // 2, (im.height - s) // 2, (im.width + s) // 2, (im.height + s) // 2)).resize((d, d), Image.LANCZOS)
    m = Image.new("L", (d * 4, d * 4), 0); ImageDraw.Draw(m).ellipse((0, 0, d * 4 - 1, d * 4 - 1), fill=255)
    return im, m.resize((d, d), Image.LANCZOS)


def caption(page, title, lines, y, color="#22371F", x=None):
    svg = [text(title, 64, x or W / 2, y, anchor="middle" if x is None else "start", color=color)[0]]
    for i, l in enumerate(lines):
        svg.append(text(l, 40, x or W / 2, y + 80 + i * 58, anchor="middle" if x is None else "start", color=color)[0])
    layer = cairosvg.svg2png(bytestring=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">{"".join(svg)}</svg>'.encode())
    import io
    page.alpha_composite(Image.open(io.BytesIO(layer)).convert("RGBA"))


def save(page, name):
    os.makedirs(OUT, exist_ok=True)
    rgb = page.convert("RGB")
    rgb.save(os.path.join(OUT, name + ".png"), dpi=(150, 150))
    rgb.save(os.path.join(OUT, name + ".pdf"), resolution=150)
    rgb.resize((W // 4, H // 4), Image.LANCZOS).save(os.path.join(OUT, name + "-preview.jpg"), quality=88)


# ------------------------------------------------------------------ 1 cubist: one hypha seen from many planes at once
def fractured_hypha():
    src = tone(load("fungal-spore-josia-martens"), 1.35)
    page = Image.new("RGBA", (W, H), (244, 248, 226, 255))
    R = 1450; cx, cy = W // 2, 2150
    pts = np.r_[rng.uniform(-1, 1, (26, 2)) * R, [[0, 0]]]
    pts = pts[np.linalg.norm(pts, axis=1) < R * 1.05]
    vor = Voronoi(np.r_[pts, [[-9e3, -9e3], [9e3, -9e3], [9e3, 9e3], [-9e3, 9e3]]])
    disc = Image.new("L", (W, H), 0); ImageDraw.Draw(disc).ellipse((cx - R, cy - R, cx + R, cy + R), fill=255)
    sw, sh = src.size
    for i, p in enumerate(pts):
        reg = vor.regions[vor.point_region[i]]
        if -1 in reg or not reg:
            continue
        poly = [(cx + vor.vertices[j][0], cy + vor.vertices[j][1]) for j in reg]
        # each facet: the same micrograph, scaled, rotated and shifted a little, like a cubist plane
        z = rng.uniform(.75, 1.6); a = rng.normal(0, 9)
        view = src.rotate(a, Image.BICUBIC, expand=False, center=(sw * .55, sh * .5)).resize((int(sw * z * .62), int(sh * z * .62)), Image.LANCZOS)
        ox = cx - view.width // 2 + int(rng.normal(0, 90)); oy = cy - view.height // 2 + int(rng.normal(0, 90))
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); lay.paste(view, (ox, oy))
        m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).polygon(poly, fill=255)
        from PIL import ImageChops
        m = ImageChops.multiply(m, disc)
        shade = Image.new("RGBA", (W, H), (16, 52, 33, int(rng.uniform(0, 70))))
        lay = Image.alpha_composite(lay, Image.composite(shade, Image.new("RGBA", (W, H), (0, 0, 0, 0)), m))
        page.paste(lay, (0, 0), m)
        ImageDraw.Draw(page).line(poly + poly[:1], fill=(244, 248, 226, 255), width=7)
    caption(page, "Hypha, from several sides", ["Fungal spore and hypha in soil, light microscope.", "Micrograph: Josia Martens, Soil Food Web School student. Recomposed in code."], 4180)
    save(page, "01-hypha-from-several-sides")


# ------------------------------------------------------------------ 2 scale: a nematode approaching the eye
def approach():
    src = tone(load("nematode-molting-cameron-radman"), 1.2)
    page = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    sizes = [260, 380, 540, 760, 1060, 1480]
    y = 900
    for k, d in enumerate(sizes):
        z = .28 + k * .14
        cw, ch = src.width * (1 - z), src.height * (1 - z)
        crop = src.crop((int(src.width * .08 + (src.width * .5 - cw / 2) * z), int((src.height - ch) / 2 - src.height * .12 * z), int(src.width * .08 + (src.width * .5 - cw / 2) * z + cw), int((src.height - ch) / 2 - src.height * .12 * z + ch)))
        im, m = circle(crop, d)
        x = W // 2 - d // 2 + int((k - 2.5) * -60)
        page.paste(im, (x, y), m); y += d + 70
        if y > 4100: break
    caption(page, "Approach", ["A moulting nematode at six distances, light microscope.", "Micrograph: Cameron Radman, Soil Food Web School student."], 4560)
    save(page, "02-approach")


# ------------------------------------------------------------------ 3 typology: an archive of 48 fields of view
def archive():
    names = list(CREDIT)
    page = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    cols, rows, d, gap = 6, 8, 440, 90
    x0 = (W - (cols * d + (cols - 1) * gap)) // 2; y0 = 330
    for r in range(rows):
        for c in range(cols):
            im = tone(load(names[(r * cols + c) % len(names)]), rng.uniform(1.1, 1.5))
            s = int(min(im.size) * rng.uniform(.25, .55)); x = int(rng.uniform(0, im.width - s)); y = int(rng.uniform(0, im.height - s))
            cell, m = circle(im.crop((x, y, x + s, y + s)), d)
            page.paste(cell, (x0 + c * (d + gap), y0 + r * (d + gap)), m)
    caption(page, "Forty-eight fields of view", ["Soil under the light microscope: fungi, amoebae, testate amoebae, nematodes, mites.", "Micrographs by Soil Food Web School students."], 4560)
    save(page, "03-forty-eight-fields-of-view")


# ------------------------------------------------------------------ 4 target: concentric rings, each a different organism
def target():
    names = ["stellate-amoeba-jimena-fuentes", "testate-encysted-robert-kenyon", "fungal-hypha-lee-kirk", "mite-talbot-armstrong-i3", "testate-amoeba-encysting-40x-joy-kaluf", "nematode-molting-cameron-radman", "fungal-spore-josia-martens"]
    page = Image.new("RGBA", (W, H), (34, 55, 31, 255))
    cx, cy = W // 2, 2200; R = 1500
    for k, n in enumerate(names):
        r = int(R * (1 - k / len(names)))
        im, m = circle(tone(load(n), 1.3), 2 * r)
        page.paste(im, (cx - r, cy - r), m)
        ImageDraw.Draw(page).ellipse((cx - r, cy - r, cx + r, cy + r), outline=(34, 55, 31, 255), width=22)
    caption(page, "Target", ["Seven soil organisms nested from the outside in: amoeba, testate amoeba,", "fungus, mite, testate amoeba, nematode, fungal spore.", "Micrographs by Soil Food Web School students."], 4130, color="#F4F8E2")
    save(page, "04-target")


if __name__ == "__main__":
    for f in sys.argv[1:] or ["fractured_hypha", "approach", "archive", "target"]:
        globals()[f]()
