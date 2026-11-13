"""Constellations of soil life: ink dots joined by shaky pen lines, each organism built from dot-line structures
(arcs, ladders, fans, rings, grids). No text."""
import math, os
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "constellations")
INK = (30, 26, 22)


class Pen:
    def __init__(s, d, rng): s.d, s.rng = d, rng

    def line(s, a, b, w=3):
        n = max(2, int(math.dist(a, b) / 8))
        pts = [(a[0] + (b[0] - a[0]) * t + s.rng.normal(0, .9), a[1] + (b[1] - a[1]) * t + s.rng.normal(0, .9)) for t in np.linspace(0, 1, n)]
        s.d.line(pts, fill=INK, width=w, joint="curve")

    def path(s, pts, w=3):
        for a, b in zip(pts, pts[1:]): s.line(a, b, w)

    def dot(s, p, r=None):
        r = r or s.rng.uniform(5, 10); e = s.rng.uniform(.75, 1.2)
        s.d.ellipse((p[0] - r * e, p[1] - r / e, p[0] + r * e, p[1] + r / e), fill=INK)

    def dotted(s, pts, every=1, r=None):
        s.path(pts)
        for p in pts[::every]: s.dot(p, r)


def arc(cx, cy, r, a0, a1, n):
    return [(cx + r * math.cos(t), cy + r * math.sin(t)) for t in np.linspace(a0, a1, n)]


def nematode(P, cx, cy, s):
    # two parallel wavy lines with rungs and dots, head ring at top, tail fan at bottom
    L = [(cx + s * .18 * math.sin(t * 2.2), cy - s + t * s * 2 / 3.0) for t in np.linspace(0, 3.0, 14)]
    R = [(x + s * .22, y) for x, y in L]
    P.dotted(L); P.dotted(R)
    for a, b in list(zip(L, R))[1::2]: P.line(a, b)
    P.dotted(arc(L[0][0] + s * .11, L[0][1] - s * .05, s * .14, math.pi, 2 * math.pi, 7))
    for k in range(5): P.line(L[-1], (L[-1][0] - s * .25 + k * s * .14, L[-1][1] + s * .35)); P.dot((L[-1][0] - s * .25 + k * s * .14, L[-1][1] + s * .35))


def testate(P, cx, cy, s):
    for k, r in enumerate((s * .9, s * .7, s * .5)):
        pts = arc(cx, cy, r, math.pi * .15, math.pi * 1.85, 12 - k * 2); P.dotted(pts)
    P.dotted(arc(cx, cy, s * .22, 0, 2 * math.pi, 9))
    for k in range(-3, 4): P.line((cx + k * s * .12, cy + s * .55), (cx + k * s * .16, cy + s * 1.25)); P.dot((cx + k * s * .16, cy + s * 1.25))
    for t in np.linspace(0, 2 * math.pi, 6, endpoint=False):
        P.line((cx, cy), (cx + s * .5 * math.cos(t), cy + s * .5 * math.sin(t)))


def hypha(P, cx, cy, s, rng):
    def grow(p, a, L, d):
        pts = [p]
        for _ in range(5):
            a += rng.normal(0, .15); p = (p[0] + math.cos(a) * L / 5, p[1] + math.sin(a) * L / 5); pts.append(p)
        P.dotted(pts, 1, 6)
        if d:
            for k in (2, 4): grow(pts[k], a + rng.choice([-1, 1]) * rng.uniform(.5, .9), L * .6, d - 1)
    grow((cx, cy + s), -math.pi / 2, s * 1.4, 3)


def mite(P, cx, cy, s):
    # ladder body, fan legs, dot ends
    for k in range(6):
        y = cy - s * .5 + k * s * .2
        P.dotted([(cx - s * .45, y), (cx - s * .15, y), (cx + s * .15, y), (cx + s * .45, y)])
    P.path([(cx - s * .45, cy - s * .5), (cx - s * .45, cy + s * .5)]); P.path([(cx + s * .45, cy - s * .5), (cx + s * .45, cy + s * .5)])
    for side in (-1, 1):
        for k in range(4):
            a = math.radians(-60 + k * 40) if side > 0 else math.radians(240 - k * 40)
            st = (cx + side * s * .45, cy - s * .35 + k * s * .23)
            kn = (st[0] + math.cos(a) * s * .4, st[1] + math.sin(a) * s * .3 - s * .15)
            en = (kn[0] + side * s * .25, kn[1] + s * .35)
            P.path([st, kn, en]); P.dot(en, 10)
    P.dotted(arc(cx, cy - s * .65, s * .15, math.pi, 2 * math.pi, 6))


def ciliate(P, cx, cy, s):
    P.dotted(arc(cx, cy, s * .55, 0, 2 * math.pi, 16))
    P.dotted(arc(cx, cy, s * .3, 0, 2 * math.pi, 10))
    for t in np.linspace(0, 2 * math.pi, 22, endpoint=False):
        a = (cx + s * .55 * math.cos(t), cy + s * .55 * math.sin(t)); b = (cx + s * .95 * math.cos(t + .1), cy + s * .95 * math.sin(t + .1))
        P.line(a, b); P.dot(b, 6)
    for k in range(-2, 3): P.line((cx + k * s * .1, cy - s * .3), (cx + k * s * .1, cy + s * .3))


def sheet(seed, paper=(236, 226, 214)):
    rng = np.random.default_rng(seed)
    W, H = 1600, 1600
    im = Image.new("RGB", (W, H), paper); P = Pen(ImageDraw.Draw(im), rng)
    fns = [nematode, testate, lambda P, x, y, s: hypha(P, x, y, s, rng), mite, ciliate]
    picks = rng.permutation(len(fns))[:4]
    for (cx, cy), k in zip([(400, 420), (1180, 420), (400, 1180), (1180, 1180)], picks):
        fns[k](P, cx, cy, 300)
    a = np.asarray(im, np.float32)
    stain = ndi.gaussian_filter(rng.random((H // 10, W // 10)), 2).repeat(10, 0).repeat(10, 1)[:H, :W]
    a *= (1 - (stain > np.quantile(stain, .97)) * .06)[..., None]
    a += (ndi.gaussian_filter(rng.random((H, W)), 1) - .5)[..., None] * 14
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    ims = [sheet(s) for s in (1, 2, 3)]
    for i, im in enumerate(ims): im.save(os.path.join(OUT, f"constellation-{i + 1}.png"))
    c = Image.new("RGB", (3 * 610 + 10, 620), "#fff")
    for i, im in enumerate(ims): c.paste(im.resize((600, 600)), (10 + i * 610, 10))
    c.save(os.path.join(OUT, "contact.jpg"), quality=90)
