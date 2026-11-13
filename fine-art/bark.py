"""Shedding plates: nested flaking layers grown from a student micrograph, each ring a different crust."""
import os, glob
import numpy as np
from PIL import Image, ImageOps
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sorted(glob.glob(os.path.join(HERE, "src", "*.jpg")))
OUT = os.path.join(HERE, "out", "bark")
W, H = 1200, 1600
LAYERS = [(150, 170, 160), (214, 190, 60), (196, 200, 110), (200, 180, 160), (150, 120, 105), (160, 70, 45), (110, 120, 95)]


def field(rng, src):
    im = ImageOps.fit(Image.open(src).convert("L"), (W // 2, H // 2), Image.LANCZOS)
    g = np.asarray(ImageOps.autocontrast(im, cutoff=1), np.float32) / 255
    n = ndi.gaussian_filter(rng.random((H // 2, W // 2)), 30)
    f = ndi.gaussian_filter(g, 22) * .6 + (n - n.min()) / np.ptp(n) * .4
    f = np.asarray(Image.fromarray(((f - f.min()) / np.ptp(f) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC), np.float32) / 255
    return f


def grain(rng, s=1.0):
    return ndi.gaussian_filter(rng.random((H, W)), s) - .5


def piece(seed):
    rng = np.random.default_rng(seed)
    f = field(rng, SRC[seed % len(SRC)])
    # two big calm fields (grey-green, yellow), then small islands that flake in 3-4 nested rings
    qs = [np.quantile(f, .5), np.quantile(f, .86), np.quantile(f, .9), np.quantile(f, .94), np.quantile(f, .975)]
    lvl = np.digitize(f, qs)
    pal = np.array([(150, 168, 160), (214, 190, 70), (232, 220, 200), (150, 120, 105), (176, 92, 70), (160, 60, 40)], np.float32)
    isl = ndi.gaussian_filter(rng.random((H, W)), 40); isl = isl > np.quantile(isl, .45)
    lvl = np.where((lvl >= 2) & ~isl, 1, lvl)
    img = pal[lvl]
    g1, g2 = grain(rng, .7), grain(rng, 3)
    img *= (1 + g1[..., None] * .35 + g2[..., None] * .4)
    edge = np.zeros((H, W), bool)
    for k in range(len(qs)):
        if k == 0: pass
        b = lvl > k; e = b & ~ndi.binary_erosion(b, iterations=3)
        edge |= e
        sh = ndi.shift(b.astype(np.float32), (6, 5), order=0) > .5
        img[sh & ~b] *= .7
    img[edge] = img[edge] * .55 + np.array([235, 225, 200]) * .45
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    ims = [piece(s) for s in (1, 4, 7, 10)]
    for i, im in enumerate(ims): im.save(os.path.join(OUT, f"bark-{i + 1}.png"))
    sh = Image.new("RGB", (4 * 380 + 10, 510), "#fff")
    for i, im in enumerate(ims): sh.paste(im.resize((370, 493)), (10 + i * 380, 8))
    sh.save(os.path.join(OUT, "contact.jpg"), quality=90)
