"""Jam: cut-paper collage. Under layer = pale wash + blue watercolour blooms + a real micrograph patch + dry-brush
hypha strokes. Top layer = a rust sheet with big soft leaf/amoeba-shaped holes cut out of it."""
import math, os, sys, glob
import numpy as np
from PIL import Image, ImageOps, ImageDraw
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sorted(glob.glob(os.path.join(HERE, "src", "*.jpg")))
OUT = os.path.join(HERE, "out", "jam")
W, H = 1200, 1500


def blobs(rng, n, scale):
    n_ = ndi.gaussian_filter(rng.random((H // 6, W // 6)), scale)
    n_ = np.asarray(Image.fromarray(((n_ - n_.min()) / np.ptp(n_) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC), np.float32) / 255
    return n_


def leaf_holes(rng, k):
    m = Image.new("L", (W, H), 0); d = ImageDraw.Draw(m)
    for _ in range(k):
        cx, cy, L, wd, a = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(600, 1100), rng.uniform(.28, .42), rng.uniform(0, 6.28)
        t = np.linspace(0, math.pi, 60)
        prof = [(L * (1 - math.cos(u)) / 2 - L / 2, L * wd * math.sin(u) ** 1.2) for u in t]
        pts = prof + [(x, -y * rng.uniform(.6, 1.0)) for x, y in prof[::-1]]
        ca, sa = math.cos(a), math.sin(a)
        d.polygon([(cx + x * ca - y * sa, cy + x * sa + y * ca) for x, y in pts], fill=255)
    return np.asarray(m, np.float32) / 255 > .5


def jam(seed, rust=(122, 62, 50)):
    rng = np.random.default_rng(seed)
    img = np.ones((H, W, 3), np.float32) * np.array([214, 206, 150], np.float32)             # khaki wash
    pale = blobs(rng, 0, 4) > .55; img[pale] = img[pale] * .2 + np.array([236, 236, 230]) * .8
    blue = blobs(rng, 0, 5); a = np.clip((blue - .45) * 3, 0, 1) * (.75 + .25 * blobs(rng, 0, 1))
    img = img * (1 - a[..., None]) + np.array([120, 140, 220], np.float32) * a[..., None]   # watercolour blue
    # a real micrograph patch, warm-toned, softly masked
    im = Image.open(SRC[rng.integers(len(SRC))]).convert("L")
    g = np.asarray(ImageOps.autocontrast(ImageOps.fit(im, (700, 700)), cutoff=1), np.float32) / 255
    x, y = int(rng.uniform(0, W - 700)), int(rng.uniform(0, H - 700))
    tone = np.array([235, 225, 195], np.float32) * g[..., None] + np.array([90, 100, 50], np.float32) * (1 - g[..., None])
    mk = ndi.gaussian_filter((blobs(rng, 0, 3)[:700, :700] > .45).astype(np.float32), 6)[..., None]
    img[y:y + 700, x:x + 700] = img[y:y + 700, x:x + 700] * (1 - mk) + tone * mk
    # dry-brush hyphae: bundles of broken thin strokes
    for _ in range(rng.integers(2, 4)):
        x0, y0, a0, L = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(0, 6.28), rng.uniform(600, 1100)
        for k in range(rng.integers(5, 10)):
            off = (k - 4) * rng.uniform(5, 9); pts = []; a = a0; px, py = x0 - math.sin(a0) * off, y0 + math.cos(a0) * off
            for s in range(160):
                pts.append((px, py)); a += .004; px += math.cos(a) * L / 160; py += math.sin(a) * L / 160
            for (p, q), keep in zip(zip(pts, pts[1:]), rng.random(159) < rng.uniform(.5, .85)):
                if not keep: continue
                xi, yi = int(p[0]), int(p[1])
                if 0 <= xi < W - 3 and 0 <= yi < H - 3: img[yi:yi + 2, xi:xi + 3] = (25, 25, 30)
    # rust sheet with cut holes on top
    holes = leaf_holes(rng, rng.integers(5, 8))
    sheet = ~holes
    img[sheet] = np.array(rust, np.float32)
    img += (rng.random((H, W))[..., None] - .5) * 8
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    ims = [jam(s, c) for s, c in ((1, (122, 62, 50)), (2, (34, 55, 31)), (3, (122, 62, 50)), (4, (60, 40, 90)))]
    for i, im in enumerate(ims): im.save(os.path.join(OUT, f"jam-{i + 1}.png"))
    sh = Image.new("RGB", (4 * 410 + 10, 520), "#eee")
    for i, im in enumerate(ims): sh.paste(im.resize((400, 500)), (10 + i * 410, 10))
    sh.save(os.path.join(OUT, "contact.jpg"), quality=90)
