"""Photogram soil, hand-made feel. Silhouettes are cut from real student micrographs (actual hyphae, amoebae,
spores, nematodes), enlarged, laid in layers. Ink bleeds along the cloth, edges wander, exposure is uneven,
there is weave and dust. Nothing geometric.
Run: python3 photogram2.py <seed> <count>
"""
import glob, math, os, sys
import numpy as np
from PIL import Image, ImageOps
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src")
W, H = 1000, 2000
SOURCES = sorted(glob.glob(os.path.join(SRC, "*.jpg")))
DYES = [[(150, 140, 60), (120, 130, 140), (178, 160, 72), (112, 122, 150)],
        [(120, 150, 80), (150, 140, 170), (188, 196, 110), (90, 110, 120)],
        [(172, 150, 92), (130, 120, 110), (150, 170, 92), (125, 135, 160)]]
INKS = [[(58, 78, 196), (118, 76, 150), (40, 60, 150)], [(60, 70, 160), (96, 140, 205), (126, 80, 160)]]


def noise(rng, h, w, scale, octaves=3):
    out = np.zeros((h, w), np.float32)
    for o in range(octaves):
        s = max(2, int(scale / 2 ** o))
        n = rng.random((h // s + 2, w // s + 2)).astype(np.float32)
        out += np.asarray(Image.fromarray((n * 255).astype(np.uint8)).resize((w + 2 * s, h + 2 * s), Image.BICUBIC), np.float32)[s:s + h, s:s + w] / 255 / 2 ** o
    return (out - out.min()) / (np.ptp(out) + 1e-6)


def silhouette(rng, size):
    """Real organism shapes from a micrograph: dark structures against the local background."""
    im = Image.open(SOURCES[rng.integers(len(SOURCES))]).convert("L")
    if "lee-kirk" in im.filename if hasattr(im, "filename") else False: pass
    w, h = im.size; z = rng.uniform(.35, .8)
    cw, ch = w * z, h * z; x0, y0 = rng.uniform(0, w - cw), rng.uniform(0, h - ch)
    im = ImageOps.fit(im.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))), size, Image.LANCZOS)
    g = np.asarray(ImageOps.autocontrast(im, cutoff=1), np.float32) / 255
    d = ndi.gaussian_filter(ndi.gaussian_filter(g, size[0] / 10) - g, 2)
    m = d > np.quantile(d, rng.uniform(.8, .9))
    m = ndi.binary_opening(m, iterations=2)
    lab, k = ndi.label(m)
    if k:
        sizes = ndi.sum(m, lab, range(1, k + 1))
        m = np.isin(lab, 1 + np.where(sizes > sizes.max() * .08)[0])
    return m.astype(np.float32)


def bleed(rng, m, amt):
    """Ink wicking into cloth: displace the mask with noise, soften, then uneven threshold."""
    h, w = m.shape
    dx = (noise(rng, h, w, 60) - .5) * amt; dy = (noise(rng, h, w, 60) - .5) * amt
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    m = ndi.map_coordinates(m, [yy + dy, xx + dx], order=1, mode="constant")
    m = ndi.gaussian_filter(m, rng.uniform(1.2, 3.5))
    thr = .35 + .3 * noise(rng, h, w, 40)
    return np.clip((m - thr) * 4 + .5, 0, 1) * (.7 + .3 * noise(rng, h, w, 12))


def cloth(rng, pal):
    img = np.zeros((H, W, 3), np.float32); ws = []
    for _ in pal: ws.append(noise(rng, H, W, 260) ** 3)
    ws = np.array(ws); ws /= ws.sum(0, keepdims=True)
    for c, k in zip(pal, ws): img += np.array(c, np.float32) * k[:, :, None]
    yy, xx = np.mgrid[0:H, 0:W]
    weave = (np.sin(xx * 1.9) * np.sin(yy * 1.9)) * 4 + (rng.random((H, W)) - .5) * 10
    return img + weave[:, :, None]


def study(seed):
    rng = np.random.default_rng(seed)
    img = cloth(rng, DYES[rng.integers(len(DYES))])
    inks = INKS[rng.integers(len(INKS))]
    for layer, (n, alpha, soft) in enumerate([(3, .4, 10), (3, .55, 4), (2, .8, 1)]):
        acc = np.zeros((H, W), np.float32)
        for _ in range(n):
            s = int(rng.uniform(700, 1500))
            m = silhouette(rng, (s, s))
            if rng.random() < .5: m = m[:, ::-1]
            m = ndi.rotate(m, rng.uniform(-60, 60), reshape=False, order=1)
            x, y = int(rng.uniform(-s * .4, W - s * .6)), int(rng.uniform(-s * .4, H - s * .6))
            xs0, ys0 = max(0, x), max(0, y); xs1, ys1 = min(W, x + s), min(H, y + s)
            acc[ys0:ys1, xs0:xs1] = np.maximum(acc[ys0:ys1, xs0:xs1], m[ys0 - y:ys1 - y, xs0 - x:xs1 - x])
        a = bleed(rng, ndi.gaussian_filter(acc, soft), rng.uniform(10, 26)) * alpha
        col = np.array(inks[layer % len(inks)], np.float32)
        img = img * (1 - a[:, :, None]) + col * a[:, :, None]
    fade = noise(rng, H, W, 400)[:, :, None]                       # uneven sun fade
    img = img * (.9 + .15 * fade)
    dust = rng.random((H, W)) < .0006
    img[ndi.binary_dilation(dust, iterations=1)] = img[ndi.binary_dilation(dust, iterations=1)] * .6
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))


def main(seed0=1, n=6):
    out = os.path.join(HERE, "out", "photogram2", str(seed0)); os.makedirs(out, exist_ok=True)
    ims = [study(seed0 * 100 + i) for i in range(n)]
    for i, im in enumerate(ims): im.save(os.path.join(out, f"study-{i + 1:02d}.png"))
    tw, th = 300, 600
    sheet = Image.new("RGB", (n * (tw + 12) + 12, th + 24), "#eee")
    for i, im in enumerate(ims): sheet.paste(im.resize((tw, th), Image.LANCZOS), (12 + i * (tw + 12), 12))
    sheet.save(os.path.join(out, "contact.jpg"), quality=90)


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 1, int(sys.argv[2]) if len(sys.argv) > 2 else 6)
