"""Crayon doodle soil: wobbly, grainy, hand-drawn sage lines on cream. Branching hyphae, coiled nematodes as
spirals, amoebae with radiating pseudopods, spores as little rings, testate shells as wobbly urns.
Rendered as a dry-media stroke (stamped grainy dabs along a jittered path). Run: python3 doodle.py
"""
import math, os
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "doodle")
W, H = 1600, 2200


class Crayon:
    def __init__(s, rng):
        s.rng = rng; s.m = np.zeros((H, W), np.float32)

    def line(s, pts, w=15):
        rng = s.rng; pts = np.asarray(pts, float)
        seg = np.linalg.norm(np.diff(pts, axis=0), axis=1); L = seg.sum()
        if L < 2: return
        n = int(L / 1.5)
        t = np.interp(np.linspace(0, L, n), np.r_[0, np.cumsum(seg)], np.arange(len(pts)))
        i = np.clip(t.astype(int), 0, len(pts) - 2); f = (t - i)[:, None]
        p = pts[i] * (1 - f) + pts[i + 1] * f
        wob = ndi.gaussian_filter1d(rng.normal(0, 2.2, (n, 2)), 14) * 5
        p += wob
        ww = w * (.8 + .4 * ndi.gaussian_filter1d(rng.random(n), 20))
        for (x, y), r in zip(p, ww):
            k = 40
            ox, oy = rng.uniform(-r / 2, r / 2, k), rng.uniform(-r / 2, r / 2, k)
            xs = np.clip((x + ox).astype(int), 0, W - 1); ys = np.clip((y + oy).astype(int), 0, H - 1)
            np.add.at(s.m, (ys, xs), .35)

    def render(s, ink, paper):
        m = ndi.gaussian_filter(s.m, 1.1)
        tooth = ndi.gaussian_filter(s.rng.random((H, W)), .6)
        a = ((m > .22) & (tooth > .4)).astype(np.float32)
        a = np.clip(a + ((m > .5) & (tooth > .28)), 0, 1)
        img = np.array(paper, np.float32) * (1 - a[:, :, None]) + np.array(ink, np.float32) * a[:, :, None]
        return Image.fromarray(img.astype(np.uint8))


def hypha(c, x, y, ang, L, depth=3):
    pts = []; a = ang
    for k in range(40):
        pts.append((x, y)); a += c.rng.normal(0, .05); x += math.cos(a) * L / 40; y += math.sin(a) * L / 40
    c.line(pts)
    if depth:
        for k in c.rng.choice(range(10, 38), 2, replace=False):
            hypha(c, *pts[k], a + c.rng.choice([-1, 1]) * c.rng.uniform(.5, 1.0), L * .55, depth - 1)
    else:
        ex, ey = pts[-1]; c.line([(ex + 12 * math.cos(t), ey + 12 * math.sin(t)) for t in np.linspace(0, 6.4, 30)], 18)


def spiral(c, x, y, R, turns=3):
    c.line([(x + R * t / (turns * 6.28) * math.cos(t), y + R * t / (turns * 6.28) * math.sin(t)) for t in np.linspace(0, turns * 6.28, 220)])
    c.line([(x + R * math.cos(turns * 6.28) + k * 3, y + k * 1) for k in range(30)], 20)


def amoeba(c, x, y, R):
    n = c.rng.integers(9, 14)
    ring = [(x + R * (1 + .15 * math.sin(5 * t)) * math.cos(t), y + R * (1 + .15 * math.sin(5 * t)) * math.sin(t)) for t in np.linspace(0, 6.3, 80)]
    c.line(ring)
    for k in range(n):
        a = k / n * 6.28 + c.rng.normal(0, .1); l = R * c.rng.uniform(.8, 1.6)
        c.line([(x + R * math.cos(a), y + R * math.sin(a)), (x + (R + l * .5) * math.cos(a + .08), y + (R + l * .5) * math.sin(a + .08)), (x + (R + l) * math.cos(a), y + (R + l) * math.sin(a))], 20)


def urn(c, x, y, s):
    prof = [(x + s * .2, y - s), (x + s * .22, y - s * .6), (x + s * .55, y - s * .3), (x + s * .5, y + s * .4), (x, y + s * .6)]
    full = prof + [(2 * x - px, py) for px, py in prof[::-1]] + [prof[0]]
    c.line(np.array(full))
    for k in range(6): c.line([(x - s * .25 + k * s * .1, y - s * .1), (x - s * .25 + k * s * .1, y + s * .3)], 14)


def compose(seed, ink, paper):
    rng = np.random.default_rng(seed); c = Crayon(rng)
    for _ in range(5): hypha(c, rng.uniform(0, W), rng.uniform(0, H), rng.uniform(0, 6.28), rng.uniform(600, 1000))
    for _ in range(4): spiral(c, rng.uniform(150, W - 150), rng.uniform(150, H - 150), rng.uniform(110, 220))
    for _ in range(3): amoeba(c, rng.uniform(200, W - 200), rng.uniform(200, H - 200), rng.uniform(90, 160))
    for _ in range(3): urn(c, rng.uniform(150, W - 150), rng.uniform(150, H - 150), rng.uniform(120, 190))
    for _ in range(30):
        x, y, r = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(14, 30)
        c.line([(x + r * math.cos(t), y + r * math.sin(t)) for t in np.linspace(0, 6.4, 24)], 14)
    return c.render(ink, paper)


def main():
    os.makedirs(OUT, exist_ok=True)
    looks = [((150, 172, 140), (248, 246, 232)), ((89, 120, 80), (240, 236, 214)), ((250, 248, 236), (110, 130, 96)), ((118, 92, 168), (238, 240, 220))]
    ims = []
    for i, (ink, paper) in enumerate(looks):
        im = compose(i + 1, ink, paper); im.save(os.path.join(OUT, f"doodle-{i + 1}.png")); ims.append(im)
    sheet = Image.new("RGB", (4 * 410 + 10, 574), "#ddd")
    for i, im in enumerate(ims): sheet.paste(im.resize((400, 550), Image.LANCZOS), (10 + i * 410, 12))
    sheet.save(os.path.join(OUT, "contact.jpg"), quality=90)


if __name__ == "__main__":
    main()
