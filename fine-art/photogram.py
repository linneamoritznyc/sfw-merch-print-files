"""Photogram soil: fungal spore heads (Aspergillus-type conidiophores, which radiate like umbels) and hyphae laid
in layers on mottled dyed cloth, like a sun print. Back layers soft, front layers crisp.
Run: python3 photogram.py <seed> <count> -> out/photogram/<seed>/study-NN.png + contact.jpg
"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from shapely.geometry import LineString, Point
from shapely.ops import unary_union
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from spray import raster, W, H  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DYES = [[(150, 140, 60), (120, 130, 140), (175, 160, 70), (110, 120, 150)],
        [(120, 150, 80), (150, 140, 170), (190, 200, 110), (90, 110, 120)],
        [(170, 150, 90), (130, 120, 110), (150, 170, 90), (125, 135, 160)]]
INKS = [[(70, 90, 200), (120, 80, 150)], [(60, 70, 160), (90, 140, 200)], [(110, 70, 160), (60, 110, 180)]]


def mottle(rng, pal):
    img = np.zeros((H, W, 3), np.float32)
    w = []
    for c in pal:
        n = ndi.gaussian_filter(rng.random((H // 10, W // 10)), rng.uniform(4, 8))
        n = np.asarray(Image.fromarray(((n - n.min()) / np.ptp(n) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC), np.float32) / 255
        w.append(n ** 3)
    w = np.array(w); w /= w.sum(0, keepdims=True)
    for c, k in zip(pal, w): img += np.array(c, np.float32) * k[:, :, None]
    return img


def conidiophore(rng, x, y, L, ang, w):
    """Stalk ending in a radiating head of spore chains."""
    a = math.radians(ang); bend = rng.normal(0, .3)
    stalk = [(x + math.cos(a + bend * t * t) * L * t, y + math.sin(a + bend * t * t) * L * t) for t in np.linspace(0, 1, 40)]
    hx, hy = stalk[-1]; ha = a + bend
    parts = [LineString(stalk).buffer(w, 8), Point(hx, hy).buffer(w * 3.2)]
    n = rng.integers(14, 24); R = L * rng.uniform(.28, .42)
    for k in range(n):
        b = ha + (k / (n - 1) - .5) * math.radians(rng.uniform(200, 300))
        r = R * rng.uniform(.75, 1.1)
        parts.append(LineString([(hx, hy), (hx + math.cos(b) * r, hy + math.sin(b) * r)]).buffer(w * .55, 6))
        for j in range(3):
            rr = r + (j + 1) * w * 2.6
            parts.append(Point(hx + math.cos(b) * rr, hy + math.sin(b) * rr).buffer(w * (1.3 - .25 * j)))
    return unary_union(parts)


def hypha(rng, x, y, L, ang, w):
    pts, a = [], math.radians(ang)
    for k in range(80):
        pts.append((x, y)); a += rng.normal(0, .06); x += math.cos(a) * L / 80; y += math.sin(a) * L / 80
    g = [LineString(pts).buffer(w, 8)]
    for k in range(10, 78, 12):
        bx, by = pts[k]; b = a + rng.choice([-1, 1]) * rng.uniform(.6, 1.1)
        g.append(LineString([(bx, by), (bx + math.cos(b) * L * .15, by + math.sin(b) * L * .15)]).buffer(w * .7, 8))
    return unary_union(g)


def study(seed):
    rng = np.random.default_rng(seed)
    img = mottle(rng, DYES[rng.integers(len(DYES))])
    inks = INKS[rng.integers(len(INKS))]
    for layer, (blur, alpha, n) in enumerate([(14, .35, 5), (6, .5, 5), (1.5, .75, 4)]):
        g = []
        for _ in range(n):
            g.append(conidiophore(rng, rng.uniform(0, W), rng.uniform(H * .3, H * 1.05), rng.uniform(380, 720), -90 + rng.normal(0, 30), rng.uniform(6, 10)))
        for _ in range(2):
            g.append(hypha(rng, rng.uniform(0, W), rng.uniform(0, H), rng.uniform(600, 1200), rng.uniform(0, 360), rng.uniform(5, 8)))
        m = raster(unary_union(g), blur)
        col = np.array(inks[layer % 2], np.float32)
        a = m * alpha
        img = img * (1 - a[:, :, None]) + col * a[:, :, None]
    img += (rng.random(img.shape[:2])[:, :, None] - .5) * 12
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))


def main(seed0=1, n=6):
    out = os.path.join(HERE, "out", "photogram", str(seed0)); os.makedirs(out, exist_ok=True)
    ims = [study(seed0 * 100 + i) for i in range(n)]
    for i, im in enumerate(ims): im.save(os.path.join(out, f"study-{i + 1:02d}.png"))
    tw, th = 300, 600
    sheet = Image.new("RGB", (n * (tw + 12) + 12, th + 24), "#eee")
    for i, im in enumerate(ims): sheet.paste(im.resize((tw, th), Image.LANCZOS), (12 + i * (tw + 12), 12))
    sheet.save(os.path.join(out, "contact.jpg"), quality=90)


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 1, int(sys.argv[2]) if len(sys.argv) > 2 else 6)
