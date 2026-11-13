"""Litter layer: a panel of narrow strips in rows, each strip cut once or twice on the diagonal; every piece is a crop
of a student micrograph toned in a dried-leaf earth colour. Mounted on a wall with a shadow."""
import os, glob
import numpy as np
from PIL import Image, ImageOps, ImageDraw, ImageFilter
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sorted(glob.glob(os.path.join(HERE, "src", "*.jpg")))
OUT = os.path.join(HERE, "out", "litter")
EARTH = [(170, 96, 64), (196, 150, 104), (150, 128, 110), (214, 190, 160), (128, 104, 92), (160, 140, 150), (182, 120, 80),
         (150, 156, 120), (226, 214, 190), (110, 90, 80), (196, 170, 140), (140, 120, 140)]


def tex(rng, w, h, col):
    im = Image.open(SRC[rng.integers(len(SRC))]).convert("L")
    z = rng.uniform(.15, .4); W0, H0 = im.size; cw, ch = W0 * z, W0 * z * h / max(w, 1)
    ch = min(ch, H0 - 1); x0, y0 = rng.uniform(0, W0 - cw), rng.uniform(0, H0 - ch)
    g = np.asarray(ImageOps.autocontrast(im.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((w, h)), cutoff=2), np.float32) / 255
    g = (g - ndi.gaussian_filter(g, 20)) * .9
    c = np.array(col, np.float32) * (1 + g[..., None] * .55) * rng.uniform(.9, 1.06)
    return np.clip(c, 0, 255)


def panel(seed, W=1200, H=1800, rows=5, cols=13):
    rng = np.random.default_rng(seed)
    img = np.zeros((H, W, 3), np.float32); rh = H / rows; cw = W / cols
    for r in range(rows):
        x = 0.0
        while x < W - 2:
            w = cw * rng.choice([.7, 1, 1, 1.3])
            x0, x1, y0, y1 = int(x), int(min(W, x + w)), int(r * rh), int((r + 1) * rh)
            sw, sh = x1 - x0, y1 - y0
            if sw < 4: break
            # split the strip by 0-2 diagonal cuts into pieces, each its own texture
            cuts = sorted(rng.uniform(.15, .85, rng.integers(0, 3)))
            yy, xx = np.mgrid[0:sh, 0:sw]
            region = np.zeros((sh, sw), int)
            for k, c in enumerate(cuts):
                tilt = rng.uniform(-.9, .9) * sh * .4
                line = c * sh + tilt * (xx / max(sw, 1) - .5)
                region[yy > line] = k + 1
            out = np.zeros((sh, sw, 3), np.float32)
            for k in range(len(cuts) + 1):
                t = tex(rng, sw, sh, EARTH[rng.integers(len(EARTH))]); out[region == k] = t[region == k]
            edge = (np.abs(np.diff(region, axis=0, prepend=region[:1])) > 0)
            out[edge] *= .7
            out[:, :2] *= .75; out[:2] *= .8
            img[y0:y1, x0:x1] = out
            x += w
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))


def mount(p):
    W, H = p.width + 500, p.height + 500
    wall = Image.new("RGB", (W, H), (240, 239, 236))
    sh = Image.new("L", (W, H), 0); ImageDraw.Draw(sh).rectangle((260, 290, 260 + p.width, 290 + p.height), fill=120)
    wall.paste((170, 168, 164), (0, 0), sh.filter(ImageFilter.GaussianBlur(25)))
    wall.paste(p, (250, 250)); return wall


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    ims = [mount(panel(s)) for s in (1, 2, 3)]
    for i, im in enumerate(ims): im.save(os.path.join(OUT, f"litter-{i + 1}.png"))
    sh = Image.new("RGB", (3 * 510 + 10, 710), "#fff")
    for i, im in enumerate(ims): sh.paste(im.resize((500, 700)), (10 + i * 510, 5))
    sh.save(os.path.join(OUT, "contact.jpg"), quality=90)
