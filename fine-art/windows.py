"""Window compositions: duotone student micrographs in simple windows (circle, arch, half disc, pill, quarter,
square), one or two flat accent shapes (leaf, dot, half disc), faint grid on cream. Calm, lots of space.
Run: python3 windows.py <seed> <count>  -> out/windows/<seed>/NN.png + contact.jpg
"""
import math, os, sys, glob
import numpy as np
from PIL import Image, ImageDraw, ImageOps
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src")
SOURCES = sorted(glob.glob(os.path.join(SRC, "*.jpg")))
CREAM, GRID = (241, 239, 228), (226, 223, 210)
DUOS = [((60, 40, 110), (190, 175, 235)), ((20, 70, 30), (205, 225, 110)), ((30, 60, 55), (160, 205, 185)),
        ((90, 45, 25), (230, 190, 150)), ((25, 35, 70), (150, 175, 220)), ((70, 20, 50), (235, 170, 200)), ((34, 55, 31), (233, 226, 204))]
ACC = [(122, 72, 34), (58, 135, 80), (34, 55, 31), (110, 90, 156), (203, 219, 108), (196, 90, 60)]


def micro(rng, w, h):
    im = Image.open(SOURCES[rng.integers(len(SOURCES))]).convert("L")
    z = rng.uniform(.4, .9); W0, H0 = im.size; cw, ch = W0 * z, H0 * z
    x0, y0 = rng.uniform(0, W0 - cw), rng.uniform(0, H0 - ch)
    im = ImageOps.fit(im.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))), (w, h), Image.LANCZOS)
    g = np.asarray(ImageOps.autocontrast(im, cutoff=1), np.float32) / 255
    g = np.clip((g - ndi.gaussian_filter(g, max(w, h) / 6)) * 1.5 + .5, 0, 1)
    dark, light = DUOS[rng.integers(len(DUOS))]
    a = np.array(dark, np.float32) * (1 - g[..., None]) + np.array(light, np.float32) * g[..., None]
    return Image.fromarray(a.astype(np.uint8))


def window(kind, w, h):
    m = Image.new("L", (w * 2, h * 2), 0); d = ImageDraw.Draw(m); W2, H2 = w * 2, h * 2
    if kind == "circle": d.ellipse((0, 0, W2 - 1, H2 - 1), fill=255)
    elif kind == "arch": d.rectangle((0, W2 // 2, W2, H2), fill=255); d.ellipse((0, 0, W2 - 1, W2 - 1), fill=255)
    elif kind == "half": d.pieslice((0, 0, W2 - 1, H2 * 2 - 1), 180, 360, fill=255)
    elif kind == "pill": d.rounded_rectangle((0, 0, W2 - 1, H2 - 1), radius=min(W2, H2) // 2, fill=255)
    elif kind == "quarter": d.pieslice((-W2, 0, W2 - 1, H2 * 2 - 1), 270, 360, fill=255)
    else: d.rectangle((0, 0, W2, H2), fill=255)
    return m.resize((w, h), Image.LANCZOS)


SIZE = {"circle": (1, 1), "arch": (.78, 1.05), "half": (1, .5), "pill": (.55, 1.1), "quarter": (1, 1), "square": (.9, .9)}


def accent(d, kind, x, y, s, c):
    if kind == "leaf":
        t = np.linspace(0, math.pi, 40)
        pts = [(x + s * .32 * math.sin(a), y - s / 2 + s * (1 - math.cos(a)) / 2) for a in t]
        d.polygon(pts + [(2 * x - px, py) for px, py in pts[::-1]], fill=c)
    elif kind == "dot": d.ellipse((x - s / 2, y - s / 2, x + s / 2, y + s / 2), fill=c)
    else: d.pieslice((x - s / 2, y - s / 2, x + s / 2, y + s / 2), 180, 360, fill=c)


def study(seed, W=1800, H=1200):
    rng = np.random.default_rng(seed)
    page = Image.new("RGB", (W, H), CREAM); d = ImageDraw.Draw(page)
    st = W // 18
    for x in range(0, W, st): d.line([(x, 0), (x, H)], fill=GRID, width=2)
    for y in range(0, H, st): d.line([(0, y), (W, y)], fill=GRID, width=2)
    n = rng.choice([1, 2, 2, 3])
    kinds = list(rng.choice(list(SIZE), n, replace=False))
    base = H * rng.uniform(.55, .8) / (1 if n < 3 else 1.15)
    x = W * rng.uniform(.04, .12); boxes = []
    for k in kinds:
        sw, sh = SIZE[k]; f = min(1, W * .8 / (base * sw), H * .9 / (base * sh)); w, h = int(base * sw * f), int(base * sh * f)
        y = int(H - h - H * rng.uniform(.06, .14)) if rng.random() < .7 else int((H - h) / 2)
        if x + w > W * .97: break
        page.paste(micro(rng, w, h), (int(x), y), window(k, w, h)); boxes.append((x, y, w, h))
        x += w + rng.uniform(-w * .12, W * .05)
    for _ in range(rng.integers(1, 3)):
        if not boxes: break
        bx, by, bw, bh = boxes[rng.integers(len(boxes))]
        s = rng.uniform(.18, .32) * H
        cx, cy = bx + rng.choice([0, bw]) + rng.uniform(-s * .3, s * .3), by + rng.uniform(.3, 1) * bh - s * .3
        accent(d, rng.choice(["leaf", "dot", "half"]), cx, cy, s, ACC[rng.integers(len(ACC))])
    return page


def main(seed0=1, n=24):
    out = os.path.join(HERE, "out", "windows", str(seed0)); os.makedirs(out, exist_ok=True)
    ims = []
    for i in range(n):
        fmt = [(1800, 1200), (1200, 1200), (1200, 1600)][i % 3]
        im = study(seed0 * 1000 + i, *fmt); im.save(os.path.join(out, f"{i + 1:02d}.png")); ims.append(im)
    tw, th = 400, 300; cols = 6
    sheet = Image.new("RGB", (cols * (tw + 12) + 12, ((n + cols - 1) // cols) * (th + 36) + 12), "#ececea"); dd = ImageDraw.Draw(sheet)
    for i, im in enumerate(ims):
        t = im.copy(); t.thumbnail((tw, th), Image.LANCZOS); x, y = 12 + (i % cols) * (tw + 12), 12 + (i // cols) * (th + 36)
        sheet.paste(t, (x + (tw - t.width) // 2, y + (th - t.height) // 2)); dd.text((x, y + th + 10), f"W{seed0}-{i + 1:02d}", fill=(40, 40, 40))
    sheet.save(os.path.join(out, "contact.jpg"), quality=88)


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 1, int(sys.argv[2]) if len(sys.argv) > 2 else 24)
