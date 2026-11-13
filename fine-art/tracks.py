"""Tracks: branching wavy channels (hyphae as rivers) drawn in shaky ink, the space between scattered with small
ring marks: open, half-filled, filled, barred. Marks cluster along the channels."""
import math, os
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "tracks")
W, H = 1200, 1650


def piece(seed, ink=(40, 38, 34), paper=(238, 236, 214)):
    rng = np.random.default_rng(seed)
    im = Image.new("RGB", (W, H), paper); d = ImageDraw.Draw(im)
    lines = []

    def river(x, y, a, L, w, depth):
        pts = []
        for k in range(int(L / 6)):
            pts.append((x + rng.normal(0, .8), y + rng.normal(0, .8)))
            a += rng.normal(0, .09) + .02 * math.sin(k / 6)
            x += math.cos(a) * 6; y += math.sin(a) * 6
        d.line(pts, fill=ink, width=w, joint="curve"); lines.extend(pts[::4])
        if depth:
            for k in rng.choice(range(5, len(pts) - 3), rng.integers(2, 5), replace=False):
                river(*pts[k], a + rng.choice([-1, 1]) * rng.uniform(.5, 1.1), L * rng.uniform(.3, .55), max(2, w - 1), depth - 1)

    for _ in range(rng.integers(3, 5)):
        river(rng.uniform(0, W), rng.uniform(-50, 200), math.pi / 2 + rng.normal(0, .5), rng.uniform(1100, 1700), 6, 3)
    P = np.array(lines)
    marks = []
    for _ in range(700):
        if rng.random() < .65 and len(P):
            px, py = P[rng.integers(len(P))]; x, y = px + rng.normal(0, 40), py + rng.normal(0, 40)
        else:
            x, y = rng.uniform(0, W), rng.uniform(0, H)
        if 15 < x < W - 15 and 15 < y < H - 15 and all((x - a) ** 2 + (y - b) ** 2 > 40 ** 2 for a, b in marks[-120:]):
            marks.append((x, y))
    for x, y in marks:
        r = 15; kind = rng.choice(4, p=[.62, .14, .14, .10])
        d.ellipse((x - r, y - r, x + r, y + r), outline=ink, width=3)
        if kind == 1: d.chord((x - r, y - r, x + r, y + r), 90, 270, fill=ink)
        elif kind == 2: d.ellipse((x - r, y - r, x + r, y + r), fill=ink)
        elif kind == 3: d.line([(x - r + 2, y), (x + r - 2, y)], fill=ink, width=3)
    a = np.asarray(im, np.float32); a += (ndi.gaussian_filter(rng.random((H, W)), 1) - .5)[..., None] * 18
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    looks = [((40, 38, 34), (238, 236, 214)), ((34, 55, 31), (226, 232, 200)), ((233, 226, 204), (34, 55, 31)), ((90, 50, 40), (232, 222, 200))]
    ims = [piece(i + 2, *c) for i, c in enumerate(looks)]
    for i, im in enumerate(ims): im.save(os.path.join(OUT, f"tracks-{i + 1}.png"))
    s = Image.new("RGB", (4 * 380 + 10, 540), "#f5f5f3")
    for i, im in enumerate(ims): s.paste(im.resize((370, 509)), (10 + i * 380, 15))
    s.save(os.path.join(OUT, "contact.jpg"), quality=90)
