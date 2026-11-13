"""Two-pass screenprint: a huge cropped silhouette of real soil life in a flat colour, overprinted by a coarse black
halftone of a student micrograph (hyphae, nematode, amoeba). Crops run off the edges. White paper.
Run: python3 screenprint.py <seed> <count> -> out/screenprint/<seed>/NN.png + contact.jpg
"""
import math, os, sys, glob
import numpy as np
from PIL import Image, ImageOps, ImageDraw
from scipy import ndimage as ndi
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import photogram2 as pg  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src")
W, H = 1500, 2000
SOURCES = sorted(glob.glob(os.path.join(SRC, "*.jpg")))
FLATS = [(104, 140, 98), (89, 166, 108), (203, 219, 108), (185, 169, 218), (196, 110, 70), (34, 55, 31), (150, 175, 220)]
INKS = [(20, 20, 20), (34, 55, 31), (60, 40, 110)]


def crop(rng, size, zoom=(.25, .55)):
    im = Image.open(SOURCES[rng.integers(len(SOURCES))]).convert("L")
    z = rng.uniform(*zoom); w, h = im.size; cw = w * z; ch = cw * size[1] / size[0]
    ch = min(ch, h); x0, y0 = rng.uniform(0, w - cw), rng.uniform(0, h - ch)
    im = im.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize(size, Image.LANCZOS)
    if rng.random() < .5: im = im.rotate(rng.choice([90, 180, 270]), expand=False)
    g = np.asarray(ImageOps.autocontrast(im, cutoff=1), np.float32) / 255
    return np.clip((g - ndi.gaussian_filter(g, size[0] / 6)) * 1.9 + .5, 0, 1)


def halftone(v, cell, ang):
    h, w = v.shape; yy, xx = np.mgrid[0:h, 0:w].astype(np.float32); a = math.radians(ang)
    u = xx * math.cos(a) + yy * math.sin(a); t = -xx * math.sin(a) + yy * math.cos(a)
    return np.hypot((u % cell) - cell / 2, (t % cell) - cell / 2) < cell * .72 * np.sqrt(np.clip(v, 0, 1))


def study(seed):
    rng = np.random.default_rng(seed)
    img = np.ones((H, W, 3), np.float32) * 252
    # pass 1: flat silhouette, huge, cropped
    s = int(rng.uniform(1.4, 2.2) * W)
    m = pg.silhouette(rng, (s, s)); m = ndi.binary_closing(m > .5, iterations=6)
    m = ndi.binary_fill_holes(m) if rng.random() < .6 else m
    m = ndi.gaussian_filter(m.astype(np.float32), 2) > .5
    x, y = int(rng.uniform(-s * .55, W - s * .45)), int(rng.uniform(-s * .4, H - s * .5))
    full = np.zeros((H, W), bool)
    xs0, ys0, xs1, ys1 = max(0, x), max(0, y), min(W, x + s), min(H, y + s)
    full[ys0:ys1, xs0:xs1] = m[ys0 - y:ys1 - y, xs0 - x:xs1 - x]
    flat = np.array(FLATS[rng.integers(len(FLATS))], np.float32)
    img[full] = flat
    # pass 2: coarse halftone of another micrograph, only its dark structures, multiplied over
    g = crop(rng, (W, H))
    dark = np.clip((np.quantile(g, .45) - g) / .35, 0, 1)
    dark = ndi.gaussian_filter(dark, 3)
    mask = halftone(dark, rng.uniform(12, 20), rng.uniform(10, 50))
    ink = np.array(INKS[rng.integers(len(INKS))], np.float32)
    img[mask] = img[mask] * (ink / 255) * .9 + ink * .1
    img += (rng.random((H, W))[..., None] - .5) * 6
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))


def main(seed0=1, n=12):
    out = os.path.join(HERE, "out", "screenprint", str(seed0)); os.makedirs(out, exist_ok=True)
    ims = []
    for i in range(n):
        im = study(seed0 * 100 + i); im.save(os.path.join(out, f"{i + 1:02d}.png")); ims.append(im)
    tw, th = 330, 440; cols = 6
    sheet = Image.new("RGB", (cols * (tw + 12) + 12, ((n + cols - 1) // cols) * (th + 36) + 12), "#e6e6e3"); d = ImageDraw.Draw(sheet)
    for i, im in enumerate(ims):
        x, y = 12 + (i % cols) * (tw + 12), 12 + (i // cols) * (th + 36)
        sheet.paste(im.resize((tw, th), Image.LANCZOS), (x, y)); d.text((x, y + th + 10), f"S{seed0}-{i + 1:02d}", fill=(40, 40, 40))
    sheet.save(os.path.join(out, "contact.jpg"), quality=88)


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 1, int(sys.argv[2]) if len(sys.argv) > 2 else 12)
