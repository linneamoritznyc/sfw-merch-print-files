"""Spray-stencil soil: a dyed soil-horizon gradient (soil brown at the top through lilac and green to teal at the
bottom) with soft sprayed stencils of soil life over it: branching hyphae fronds, mycorrhizal roots, nematodes,
mites, springtails, testate amoebae. Some stencils bleach lighter, some spray darker.
Run: python3 spray.py <seed> <count>  -> out/spray/<seed>/study-NN.png + contact.jpg
"""
import io, math, os, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from shapely.geometry import LineString, Point
from shapely.ops import unary_union
from shapely import affinity
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cutouts  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1000, 2000
HORIZONS = [  # top to bottom
    [(110, 58, 40), (150, 120, 170), (120, 150, 80), (40, 110, 120)],
    [(90, 52, 45), (130, 90, 110), (89, 166, 108), (21, 70, 60)],
    [(70, 45, 40), (185, 169, 218), (160, 180, 90), (30, 91, 76)],
    [(34, 55, 31), (89, 166, 108), (203, 219, 108), (110, 90, 156)],
]


def dye(rng, pal):
    """Vertical horizon gradient with blotchy dye noise."""
    y = np.linspace(0, 1, H)[:, None] * np.ones((1, W))
    n = ndi.gaussian_filter(rng.random((H // 8, W // 8)), 6); n = (n - n.min()) / np.ptp(n)
    n = np.asarray(Image.fromarray((n * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC), np.float32) / 255
    t = np.clip(y + (n - .5) * .35, 0, 1) * (len(pal) - 1)
    i = np.clip(t.astype(int), 0, len(pal) - 2); f = (t - i)[:, :, None]
    P = np.array(pal, np.float32)
    return P[i] * (1 - f) + P[i + 1] * f


def frond(rng, x, y, L, ang, w):
    """Hyphal frond: a curving stem with alternating side branches, like a fern leaf stencil."""
    parts = []; pts = []
    a = math.radians(ang); curl = rng.normal(0, .004)
    px, py = x, y
    for k in range(60):
        pts.append((px, py)); a += curl * 10; px += math.cos(a) * L / 60; py += math.sin(a) * L / 60
    parts.append(LineString(pts).buffer(w, 8))
    for k in range(4, 58, 4):
        bx, by = pts[k]; side = 1 if (k // 4) % 2 else -1
        ba = a - curl * 10 * (60 - k) + side * math.radians(rng.uniform(40, 65))
        bl = L * .28 * (1 - k / 70)
        tip = (bx + math.cos(ba) * bl, by + math.sin(ba) * bl)
        parts.append(LineString([(bx, by), ((bx + tip[0]) / 2 + side * 6, (by + tip[1]) / 2), tip]).buffer(w * .9, 8))
        parts.append(Point(tip).buffer(w * 1.6))
    return unary_union(parts)


def raster(g, blur):
    m = Image.new("L", (W, H), 0); d = ImageDraw.Draw(m)
    for p in getattr(g, "geoms", [g]):
        if p.geom_type != "Polygon" or p.is_empty: continue
        d.polygon(list(p.exterior.coords), fill=255)
        for r in p.interiors: d.polygon(list(r.coords), fill=0)
    a = np.asarray(m, np.float32) / 255
    return ndi.gaussian_filter(a, blur)


def spray(img, mask, rng, colour, strength):
    """Airbrush: soft mask, speckled at the edges, blended toward a colour (lighter = bleach, darker = spray)."""
    speck = rng.random(mask.shape) < (mask * 1.4)
    a = np.clip(mask * .75 + speck * .25 * mask, 0, 1) * strength
    return img * (1 - a[:, :, None]) + np.array(colour, np.float32) * a[:, :, None]


def study(seed):
    rng = np.random.default_rng(seed)
    pal = HORIZONS[rng.integers(len(HORIZONS))]
    img = dye(rng, pal)
    light = (235, 230, 220); dark = (20, 40, 30)
    # big pale bleach fronds high up, dark sprayed fronds low down, like the understory
    for _ in range(rng.integers(3, 6)):
        g = frond(rng, rng.uniform(0, W), rng.uniform(200, 1100), rng.uniform(400, 800), rng.uniform(-150, -30), rng.uniform(8, 16))
        col = [light, (190, 215, 235), (215, 225, 160)][rng.integers(3)]
        img = spray(img, raster(g, rng.uniform(4, 10)), rng, col, rng.uniform(.45, .75))
    for _ in range(rng.integers(5, 9)):
        g = frond(rng, rng.uniform(-100, W + 100), rng.uniform(1500, 2100), rng.uniform(500, 1000), rng.uniform(-110, -70), rng.uniform(8, 14))
        img = spray(img, raster(g, rng.uniform(3, 7)), rng, dark, rng.uniform(.35, .65))
    # soil organisms as stencils
    for _ in range(rng.integers(3, 7)):
        name, fn, _ = cutouts.PICTOS[rng.integers(len(cutouts.PICTOS))]
        g = fn(); s = rng.uniform(.6, 1.6)
        g = affinity.translate(affinity.rotate(affinity.scale(g, s, s, origin=(200, 200)), rng.uniform(-40, 40), origin=(200, 200)), rng.uniform(-150, W - 250), rng.uniform(0, H - 300))
        col = light if rng.random() < .55 else [(185, 169, 218), (200, 226, 120), dark][rng.integers(3)]
        img = spray(img, raster(g, rng.uniform(3, 9)), rng, col, rng.uniform(.4, .8))
    # overall overspray grain
    img += (rng.random(img.shape[:2])[:, :, None] - .5) * 14
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))


def main(seed0=1, n=8):
    out = os.path.join(HERE, "out", "spray", str(seed0)); os.makedirs(out, exist_ok=True)
    ims = []
    for i in range(n):
        im = study(seed0 * 100 + i); im.save(os.path.join(out, f"study-{i + 1:02d}.png")); ims.append(im)
    tw, th = 250, 500
    sheet = Image.new("RGB", (n * (tw + 12) + 12, th + 50), "#eee"); d = ImageDraw.Draw(sheet)
    for i, im in enumerate(ims):
        sheet.paste(im.resize((tw, th), Image.LANCZOS), (12 + i * (tw + 12), 12)); d.text((12 + i * (tw + 12), th + 22), f"S{seed0}-{i + 1:02d}", fill=(40, 40, 40))
    sheet.save(os.path.join(out, "contact.jpg"), quality=90)


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 1, int(sys.argv[2]) if len(sys.argv) > 2 else 8)
