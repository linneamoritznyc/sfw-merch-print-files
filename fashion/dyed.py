"""Hand-dyed soil pants: brown-to-lilac-to-green-to-teal horizon fade, big stencils sprayed over it.
Stencil = crisp edge + soft overspray halo + speckle. Shapes are real micrograph silhouettes (amoebae, hyphae,
spore clusters) and branching hyphal fronds. Pale bleached shapes high, dark shapes low.
Output out/dyed/<seed>.png (full panel art) + contact.jpg (on a pants silhouette)
"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fine-art"))
import photogram2 as pg  # noqa: E402
from shapely.geometry import LineString, Point  # noqa: E402
from shapely.ops import unary_union  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "dyed")
W, H = 1400, 2800
PALS = [[(112, 58, 44), (120, 70, 60), (150, 135, 175), (120, 155, 80), (40, 115, 120), (30, 70, 90)],
        [(95, 52, 40), (140, 90, 120), (180, 170, 210), (90, 150, 100), (30, 90, 80), (20, 60, 60)],
        [(70, 50, 40), (110, 70, 50), (170, 150, 90), (89, 166, 108), (34, 90, 70), (20, 40, 35)]]


def noise(rng, scale):
    return pg.noise(rng, H, W, scale)


def dye(rng, pal):
    y = np.linspace(0, 1, H)[:, None] * np.ones((1, W), np.float32)
    t = np.clip(y + (noise(rng, 220) - .5) * .45, 0, 1) * (len(pal) - 1)
    i = np.clip(t.astype(int), 0, len(pal) - 2); f = (t - i)[..., None]
    P = np.array(pal, np.float32)
    img = P[i] * (1 - f) + P[i + 1] * f
    return img * (.85 + .3 * noise(rng, 120)[..., None])


def frond(rng, x, y, L, ang, w):
    pts, a = [], math.radians(ang); bend = rng.normal(0, .004)
    for k in range(60):
        pts.append((x, y)); a += bend * 10; x += math.cos(a) * L / 60; y += math.sin(a) * L / 60
    parts = [LineString(pts).buffer(w, 8)]
    for k in range(3, 58, 3):
        bx, by = pts[k]; s = 1 if (k // 3) % 2 else -1
        ba = math.atan2(pts[k + 1][1] - by, pts[k + 1][0] - bx) + s * math.radians(rng.uniform(35, 60))
        bl = L * .32 * (1 - k / 70) * rng.uniform(.8, 1.1)
        tip = (bx + math.cos(ba) * bl, by + math.sin(ba) * bl)
        parts.append(LineString([(bx, by), tip]).buffer(w * rng.uniform(1.0, 1.8), 8))
    return unary_union(parts)


def raster(g):
    m = Image.new("L", (W, H), 0); d = ImageDraw.Draw(m)
    for p in getattr(g, "geoms", [g]):
        if p.geom_type == "Polygon" and not p.is_empty: d.polygon(list(p.exterior.coords), fill=255)
    return np.asarray(m, np.float32) / 255


def place_silhouette(rng, s, x, y):
    m = pg.silhouette(rng, (s, s))
    m = ndi.binary_closing(m > .5, iterations=4).astype(np.float32)
    m = ndi.rotate(m, rng.uniform(-50, 50), reshape=False, order=1)
    out = np.zeros((H, W), np.float32)
    xs0, ys0 = max(0, x), max(0, y); xs1, ys1 = min(W, x + s), min(H, y + s)
    if xs1 > xs0 and ys1 > ys0: out[ys0:ys1, xs0:xs1] = m[ys0 - y:ys1 - y, xs0 - x:xs1 - x]
    return out


def stencil(img, rng, m, colour, strength):
    edge = ndi.gaussian_filter(m, 1.2)
    halo = ndi.gaussian_filter(m, rng.uniform(14, 28))
    speck = (rng.random(m.shape) < halo * 1.1) * .5
    a = np.clip(np.maximum(edge * .9, halo * .45) + speck * halo, 0, 1) * strength
    a *= .8 + .2 * noise(rng, 30)
    return img * (1 - a[..., None]) + np.array(colour, np.float32) * a[..., None]


def piece(seed):
    rng = np.random.default_rng(seed)
    img = dye(rng, PALS[seed % len(PALS)])
    pale = [(200, 215, 230), (215, 220, 170), (225, 200, 220), (190, 225, 200)]
    for _ in range(4):                                         # big pale bleached shapes, upper half
        if rng.random() < .5:
            m = place_silhouette(rng, int(rng.uniform(700, 1100)), int(rng.uniform(-300, W - 500)), int(rng.uniform(-200, 1000)))
        else:
            m = raster(frond(rng, rng.uniform(0, W), rng.uniform(300, 1300), rng.uniform(500, 900), rng.uniform(-170, -10), rng.uniform(16, 26)))
        img = stencil(img, rng, m, pale[rng.integers(len(pale))], rng.uniform(.55, .8))
    for _ in range(9):                                         # dark sprayed fronds, lower half, rising
        g = frond(rng, rng.uniform(-100, W + 100), rng.uniform(H - 100, H + 200), rng.uniform(700, 1300), -90 + rng.normal(0, 18), rng.uniform(10, 18))
        img = stencil(img, rng, raster(g), [(20, 50, 45), (40, 80, 60), (25, 45, 70)][rng.integers(3)], rng.uniform(.45, .75))
    for _ in range(3):                                         # light fronds over the dark, like the reference
        g = frond(rng, rng.uniform(0, W), rng.uniform(H - 200, H + 100), rng.uniform(600, 1000), -90 + rng.normal(0, 20), rng.uniform(8, 14))
        img = stencil(img, rng, raster(g), (150, 200, 120), rng.uniform(.4, .6))
    img += (rng.random((H, W))[..., None] - .5) * 10
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))


PANTS = [(140, 40), (1260, 40), (1300, 400), (1250, 2760), (820, 2760), (730, 760), (670, 760), (580, 2760), (150, 2760), (100, 400)]


def main(seeds=(1, 2, 3, 4)):
    os.makedirs(OUT, exist_ok=True)
    ims = []
    for s in seeds:
        art = piece(s); art.save(os.path.join(OUT, f"panel-{s}.png"))
        can = Image.new("RGB", (W, H), (238, 238, 235)); m = Image.new("L", (W, H), 0)
        ImageDraw.Draw(m).polygon(PANTS, fill=255); can.paste(art, (0, 0), m)
        d = ImageDraw.Draw(can); d.polygon(PANTS, outline=(200, 190, 170), width=6)
        d.line([(140, 150), (1260, 150)], fill=(200, 190, 170), width=5); d.line([(700, 150), (700, 600)], fill=(200, 190, 170), width=5)
        ims.append(can)
    sheet = Image.new("RGB", (len(ims) * 470 + 20, 960), (238, 238, 235))
    for i, im in enumerate(ims): sheet.paste(im.resize((450, 900), Image.LANCZOS), (20 + i * 470, 30))
    sheet.save(os.path.join(OUT, "contact.jpg"), quality=90)


if __name__ == "__main__":
    main()
