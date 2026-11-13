"""Streams: vertical flowing bands that swell and pinch, each filled with an engraved texture
(hatch, cross-hatch, stipple, waves, solid, blank), one ink on paper, ragged cut-out silhouette."""
import math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage as ndi

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "streams")
W, H = 1100, 2000


def smooth_noise(rng, n, s):
    return ndi.gaussian_filter1d(rng.normal(0, 1, n), s)


def textures(rng):
    yy, xx = np.mgrid[0:H, 0:W]
    T = []
    T.append(((xx + yy) % 14) < 5)                                   # diagonal hatch
    T.append(((xx - yy) % 12) < 4)                                   # other diagonal
    T.append((((xx + yy) % 16) < 4) | (((xx - yy) % 16) < 4))        # cross hatch
    d = np.hypot((xx % 18) - 9, (yy % 18) - 9) < 4.2                 # stipple
    T.append(d)
    T.append(np.hypot((xx % 11) - 5.5, ((yy + 5 * (xx // 11 % 2)) % 11) - 5.5) < 2.2)  # fine stipple
    T.append(((yy + 6 * np.sin(xx / 9)) % 13) < 4)                   # waves
    T.append(np.ones((H, W), bool))                                  # solid
    T.append((yy % 10) < 3)                                          # horizontal rule
    T.append(np.zeros((H, W), bool))                                 # blank
    return T


def piece(seed, ink=(28, 26, 22), paper=(236, 228, 208)):
    rng = np.random.default_rng(seed)
    n = rng.integers(7, 11)
    # band boundaries x_k(y): each a smooth wandering curve, sorted left to right
    ys = np.arange(H)
    walls = []
    for k in range(n + 1):
        base = W * k / n
        wob = smooth_noise(rng, H, rng.uniform(80, 160)) * rng.uniform(1500, 3200)
        walls.append(base + wob * (0 if k in (0, n) else 1))
    walls = np.sort(np.array(walls), axis=0)
    outline = smooth_noise(rng, H, 120) * 2600
    walls[0] += 80 + np.abs(outline) * .5; walls[-1] -= 80 + np.abs(smooth_noise(rng, H, 140) * 2600) * .5
    T = textures(rng); order = rng.permutation(len(T))
    img = np.zeros((H, W), bool); xx = np.arange(W)[None, :]
    band = np.full((H, W), -1)
    for k in range(n):
        inside = (xx >= walls[k][:, None]) & (xx < walls[k + 1][:, None])
        band[inside] = k
        img |= inside & T[order[k % len(T)]]
    edge = np.zeros_like(img)
    for k in range(n + 1):
        xi = np.clip(walls[k].astype(int), 0, W - 1)
        for t in range(-2, 3): edge[ys, np.clip(xi + t, 0, W - 1)] = True
    shape = band >= 0
    img = (img | edge) & shape
    # ragged paper silhouette
    rag = ndi.gaussian_filter(rng.random((H, W)), 2) > .5
    shape = ndi.binary_opening(shape | (ndi.binary_dilation(shape, iterations=6) & rag), iterations=2)
    a = np.empty((H, W, 3), np.uint8); a[:] = (245, 245, 243)
    a[shape] = paper; a[img & shape] = ink
    im = Image.fromarray(a)
    sh = Image.fromarray((ndi.binary_dilation(shape, iterations=4) * 90).astype(np.uint8)).filter(ImageFilter.GaussianBlur(10))
    can = Image.new("RGB", (W, H), (245, 245, 243)); can.paste((200, 200, 196), (8, 10), sh); can.paste(im, (0, 0), Image.fromarray((shape * 255).astype(np.uint8)))
    return can


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    looks = [((28, 26, 22), (236, 228, 208)), ((34, 55, 31), (233, 226, 204)), ((60, 40, 110), (232, 228, 236)), ((236, 228, 208), (30, 30, 28))]
    ims = [piece(i + 1, *c) for i, c in enumerate(looks)]
    for i, im in enumerate(ims): im.save(os.path.join(OUT, f"streams-{i + 1}.png"))
    s = Image.new("RGB", (4 * 330 + 10, 610), "#f5f5f3")
    for i, im in enumerate(ims): s.paste(im.resize((320, 582)), (10 + i * 330, 14))
    s.save(os.path.join(OUT, "contact.jpg"), quality=90)
