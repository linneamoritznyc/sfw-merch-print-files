"""Mycelium constellation: a full-sheet network of dot-and-line hyphae in the Picasso-constellation hand.
Tips grow and branch; when a tip comes near another hypha it fuses to it (anastomosis). Nodes are ink dots;
some nodes bloom into arcs, ladders and fans. Variants colour the dots (synesthetic)."""
import math, os
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from scipy.spatial import cKDTree

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "mycelium")
W, H = 1800, 2400


def grow(rng, n_seeds=5, steps=900):
    nodes, edges = [], []
    tips = []
    for _ in range(n_seeds):
        p = (rng.uniform(.2, .8) * W, rng.uniform(.2, .8) * H); nodes.append(p)
        for a in rng.uniform(0, 2 * math.pi, 3): tips.append((len(nodes) - 1, a))
    for _ in range(steps):
        if not tips: break
        i = rng.integers(len(tips)); ni, a = tips.pop(i)
        x, y = nodes[ni]; a += rng.normal(0, .35); L = rng.uniform(45, 85)
        q = (x + math.cos(a) * L, y + math.sin(a) * L)
        if not (30 < q[0] < W - 30 and 30 < q[1] < H - 30): continue
        tree = cKDTree(nodes); d, j = tree.query(q, k=2)
        if d[0] < 28:                                   # fuse into existing hypha
            if j[0] != ni: edges.append((ni, j[0]))
            continue
        nodes.append(q); nj = len(nodes) - 1; edges.append((ni, nj))
        tips.append((nj, a))
        if rng.random() < .28: tips.append((nj, a + rng.choice([-1, 1]) * rng.uniform(.6, 1.2)))
    return nodes, edges


def draw(seed, paper=(236, 226, 214), ink=(30, 26, 22), colours=None):
    rng = np.random.default_rng(seed)
    nodes, edges = grow(rng)
    im = Image.new("RGB", (W, H), paper); d = ImageDraw.Draw(im)

    def line(a, b, w=3):
        n = max(2, int(math.dist(a, b) / 9))
        pts = [(a[0] + (b[0] - a[0]) * t + rng.normal(0, .9), a[1] + (b[1] - a[1]) * t + rng.normal(0, .9)) for t in np.linspace(0, 1, n)]
        d.line(pts, fill=ink, width=w, joint="curve")

    for i, j in edges: line(nodes[i], nodes[j])
    deg = np.zeros(len(nodes), int)
    for i, j in edges: deg[i] += 1; deg[j] += 1
    for k, (x, y) in enumerate(nodes):
        if rng.random() < .04 and deg[k] >= 2:          # bloom: arc of dots around a node
            r = rng.uniform(40, 80); t0 = rng.uniform(0, 6.28)
            pts = [(x + r * math.cos(t), y + r * math.sin(t)) for t in np.linspace(t0, t0 + rng.uniform(2, 4.5), 8)]
            for a, b in zip(pts, pts[1:]): line(a, b, 2)
            for p in pts:
                c = colours[rng.integers(len(colours))] if colours else ink
                d.ellipse((p[0] - 6, p[1] - 6, p[0] + 6, p[1] + 6), fill=c)
        r = (11 if deg[k] == 1 else 6 + min(deg[k], 4)) * rng.uniform(.8, 1.15); e = rng.uniform(.8, 1.2)
        c = colours[rng.integers(len(colours))] if colours and rng.random() < .7 else ink
        d.ellipse((x - r * e, y - r / e, x + r * e, y + r / e), fill=c)
    a = np.asarray(im, np.float32)
    a += (ndi.gaussian_filter(rng.random((H, W)), 1) - .5)[..., None] * 14
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    looks = [dict(), dict(colours=[(110, 90, 170), (203, 190, 60), (196, 90, 60), (60, 140, 90)]),
             dict(paper=(30, 32, 28), ink=(232, 226, 210), colours=[(185, 169, 218), (214, 220, 110), (240, 150, 120)]),
             dict(paper=(34, 55, 31), ink=(233, 226, 204))]
    ims = [draw(i + 3, **l) for i, l in enumerate(looks)]
    for i, im in enumerate(ims): im.save(os.path.join(OUT, f"mycelium-{i + 1}.png"))
    c = Image.new("RGB", (4 * 460 + 10, 620), "#fff")
    for i, im in enumerate(ims): c.paste(im.resize((450, 600)), (10 + i * 460, 10))
    c.save(os.path.join(OUT, "contact.jpg"), quality=90)
