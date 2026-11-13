"""One organism per product: cut out of a student micrograph, printed in two or three riso inks on a plain ground,
with a small specimen label. No repeats, no circles.
Outputs out/specimen/: mug-11oz-<name>.png (9 x 3.5 in) and notebook-<name>.png (5.75 x 8 in + bleed), 300 dpi.
"""
import os, sys
import numpy as np
from PIL import Image, ImageOps
from scipy import ndimage as ndi
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from overprint import load, layers, overprint, type_layer, RISO, rng  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "specimen")

SPECIMENS = [  # name, source, crop box, inks (shade, mass, edge), ground, label lines
    ("stellate-amoeba", "stellate-amoeba-jimena-fuentes", (.40, .28, .70, .68), ("pink", "blue", "violet"), (250, 248, 242),
     ["STELLATE AMOEBA", "Student micrograph by Jimena Fuentes"]),
    ("testate-amoeba", "testate-encysted-robert-kenyon", (.12, .05, .40, .45), ("mint", "violet", "black"), (250, 248, 242),
     ["TESTATE AMOEBA", "Student micrograph by Robert Kenyon"]),
    ("nematode", "nematode-molting-cameron-radman", (.18, .10, .98, .48), ("yellow", "green", "black"), (250, 248, 242),
     ["NEMATODE", "Student micrograph by Cameron Radman"]),
    ("fungal-spore", "fungal-spore-josia-martens", (.36, .32, .80, .58), ("yellow", "teal", "black"), (250, 248, 242),
     ["FUNGAL SPORE", "Student micrograph by Josia Martens"]),
]


def cutout(src, box, size):
    g, d = load(src, box, size)
    dd = ndi.gaussian_filter(d, 3)
    m = dd > np.quantile(dd, .80)
    m = ndi.binary_closing(m, iterations=6)
    lab, k = ndi.label(m)
    if k:
        sizes = ndi.sum(m, lab, range(1, k + 1))
        keep = np.isin(lab, 1 + np.argsort(-sizes)[:1])
        m = ndi.binary_fill_holes(ndi.binary_dilation(keep, iterations=10))
    return g, d, m


def specimen_plate(spec, W, H, box_px, label_y, label_px=(56, 30)):
    name, src, box, inks, ground, label = spec
    bw, bh = box_px
    g, d, m = cutout(src, box, (bw, bh))
    mass, shade, edge = layers(g, d, 1.2)
    planes = []
    ox, oy = (W - bw) // 2, (H - bh) // 2 - (H // 14 if label_y else 0)
    for p in (shade & m, mass & m, edge & m):
        full = np.zeros((H, W), bool); full[oy:oy + bh, ox:ox + bw] = p; planes.append(full)
    plates = list(zip(planes, inks))
    if label_y:
        plates.append((type_layer([label[0]], (W, H), label_y, label_px[0], 160), "black"))
        plates.append((type_layer([label[1]], (W, H), label_y + label_px[0] * 1.3, label_px[1], 20, fnt="eb-garamond-latin-400-normal.woff2"), "black"))
    return overprint(plates, (W, H), ground, shift=4)


def main():
    os.makedirs(OUT, exist_ok=True)
    for spec in SPECIMENS:
        nb = specimen_plate(spec, 1800, 2475, (1500, 1500), 2080)
        nb.save(os.path.join(OUT, f"notebook-{spec[0]}.png"), dpi=(300, 300))
        # mug: organism on the front (left half when printed, faces a right-handed drinker), label on the back
        W, H = 2700, 1050
        art = specimen_plate(spec, W // 2, H, (1100, 900), 0)
        lab = specimen_plate((spec[0], spec[1], spec[2], spec[3], spec[4], spec[5]), W // 2, H, (2, 2), 470, (60, 32))
        mug = Image.new("RGB", (W, H), spec[4]); mug.paste(lab, (0, 0)); mug.paste(art, (W // 2, 0))
        mug.save(os.path.join(OUT, f"mug-11oz-{spec[0]}.png"), dpi=(300, 300))


if __name__ == "__main__":
    main()
