"""Soil camo: a real student micrograph of soil aggregates posterised into camo blobs (pale ground, olive, rust),
each rust and olive blob ringed with a broken black outline, then rendered with a fuzzy knit/fleece edge.
Run: python3 camo.py -> out/camo/*.png + contact.jpg
"""
import glob, os
import numpy as np
from PIL import Image, ImageOps
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
SRC, OUT = os.path.join(HERE, "src"), os.path.join(HERE, "out", "camo")
W, H = 1600, 2400
WAYS = {
    "desert": [(214, 200, 130), (150, 140, 70), (190, 110, 50), (28, 26, 20)],
    "forest": [(150, 170, 110), (60, 100, 55), (34, 55, 31), (16, 22, 14)],
    "lilac": [(205, 195, 225), (140, 120, 180), (90, 140, 90), (34, 30, 45)],
    "sfw": [(203, 219, 108), (89, 166, 108), (21, 104, 38), (20, 30, 18)],
}
SOURCES = ["testate-encysting-jimena-fuentes-i2", "testate-encysted-robert-kenyon", "fungal-spores-in-suspension", "mite-talbot-armstrong-i3"]


def camo(src, pal, seed, knit=6):
    rng = np.random.default_rng(seed)
    im = ImageOps.fit(Image.open(os.path.join(SRC, src + ".jpg")).convert("L"), (W // 2, H // 2), Image.LANCZOS)
    g = np.asarray(ImageOps.autocontrast(im, cutoff=1), np.float32) / 255
    g = g - ndi.gaussian_filter(g, 80) * .7
    g = ndi.gaussian_filter(g, 5)
    g = np.asarray(Image.fromarray(((g - g.min()) / np.ptp(g) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC), np.float32) / 255
    q1, q2 = np.quantile(g, .38), np.quantile(g, .62)
    rust = g < q1; olive = (g >= q1) & (g < q2)
    rust = ndi.binary_opening(rust, iterations=4); olive = ndi.binary_opening(olive, iterations=4)
    # broken black outline around every blob
    ring = (ndi.binary_dilation(rust, iterations=9) & ~rust) | (ndi.binary_dilation(olive, iterations=7) & ~olive & ~rust)
    br = ndi.gaussian_filter(rng.random((H, W)), 14); ring &= br > np.quantile(br, .25)
    cn = ndi.gaussian_filter(rng.random((H, W)), 30); core = ndi.binary_erosion(rust, iterations=22) & (cn > np.quantile(cn, .55))
    lvl = np.zeros((H, W), np.uint8)
    lvl[olive] = 1; lvl[rust] = 2; lvl[ring] = 3; lvl[core] = 3
    # knit: sample on a coarse stitch grid with jitter, then upscale nearest
    sh, sw = H // knit, W // knit
    yy = (np.arange(sh)[:, None] * knit + rng.integers(0, knit, (sh, sw))).clip(0, H - 1)
    xx = (np.arange(sw)[None, :] * knit + rng.integers(0, knit, (sh, sw))).clip(0, W - 1)
    small = lvl[yy, xx]
    img = np.array(pal, np.float32)[small]
    img += (rng.random(img.shape[:2])[:, :, None] - .5) * 18
    out = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).resize((W, H), Image.NEAREST)
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    ims = []
    for i, (way, pal) in enumerate(WAYS.items()):
        im = camo(SOURCES[i % len(SOURCES)], pal, i)
        im.save(os.path.join(OUT, f"soil-camo-{way}.png"), dpi=(150, 150)); ims.append(im)
    sheet = Image.new("RGB", (4 * 410 + 10, 610), "#ddd")
    for i, im in enumerate(ims): sheet.paste(im.resize((400, 600), Image.LANCZOS), (10 + i * 410, 5))
    sheet.save(os.path.join(OUT, "contact.jpg"), quality=90)


if __name__ == "__main__":
    main()
