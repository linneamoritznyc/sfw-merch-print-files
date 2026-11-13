"""Clothes and bags, dressed in the SFW art directions the team liked (sketchbook studies, topo, knit, doodle,
cut-outs, camo). Flat concept renders. Output out/products/<name>.png + contact.jpg
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
FA = os.path.join(HERE, "..", "fine-art", "out")
OUT = os.path.join(HERE, "out", "products")
C = 700
LINE = (60, 60, 60)


def load(p, w=None):
    im = Image.open(p).convert("RGB")
    if w: im = im.resize((w, int(im.height * w / im.width)), Image.LANCZOS)
    return im


def fill(src, mode="fit", box=(0, 0, C, C)):
    """mode fit: one image covers the box; tile: repeat."""
    can = Image.new("RGB", (C, C), src.getpixel((2, 2)))
    x0, y0, x1, y1 = box
    if mode == "fit":
        s = max((x1 - x0) / src.width, (y1 - y0) / src.height)
        im = src.resize((int(src.width * s) + 1, int(src.height * s) + 1), Image.LANCZOS)
        can.paste(im, (x0 - (im.width - (x1 - x0)) // 2, y0 - (im.height - (y1 - y0)) // 2))
    else:
        for x in range(0, C, src.width):
            for y in range(0, C, src.height): can.paste(src, (x, y))
    return can


def draw(polys, f, extra=None):
    can = Image.new("RGB", (C, C), (232, 232, 229))
    m = Image.new("L", (C, C), 0); d = ImageDraw.Draw(m)
    for p in polys: d.polygon(p, fill=255)
    can.paste(f, (0, 0), m)
    dd = ImageDraw.Draw(can)
    for p in polys: dd.polygon(p, outline=LINE, width=3)
    if extra: extra(dd)
    return can


HOODIE = [(250, 110), (300, 60), (400, 60), (450, 110), (560, 150), (650, 470), (590, 490), (540, 300), (540, 640), (160, 640), (160, 300), (110, 490), (50, 470), (140, 150)]
CREW = [(270, 110), (430, 110), (560, 150), (650, 470), (590, 490), (540, 300), (540, 640), (160, 640), (160, 300), (110, 490), (50, 470), (140, 150)]
VEST = [(270, 100), (320, 100), (350, 160), (380, 100), (430, 100), (540, 180), (520, 640), (180, 640), (160, 180)]
SHIRT = [(280, 90), (420, 90), (570, 140), (650, 460), (590, 480), (540, 290), (540, 650), (160, 650), (160, 290), (110, 480), (50, 460), (130, 140)]
JOGGER = [(200, 80), (500, 80), (530, 230), (520, 600), (540, 640), (400, 640), (360, 270), (340, 270), (300, 640), (160, 640), (180, 600), (170, 230)]
TOTE = [(200, 230), (500, 230), (520, 640), (180, 640)]
BACKPACK = [(230, 140), (470, 140), (520, 200), (530, 620), (500, 650), (200, 650), (170, 620), (180, 200)]
DUFFEL = [(110, 300), (590, 300), (630, 340), (630, 560), (590, 590), (110, 590), (70, 560), (70, 340)]
CROSSBODY = [(220, 330), (480, 330), (500, 360), (500, 540), (480, 560), (220, 560), (200, 540), (200, 360)]
DRAWSTRING = [(210, 150), (490, 150), (500, 640), (200, 640)]
SLEEVE = [(130, 200), (570, 200), (570, 530), (130, 530)]


def main():
    os.makedirs(OUT, exist_ok=True)
    sk = lambda b, n: load(os.path.join(FA, "sketchbook", str(b), f"study-{n:02d}.png"))
    topo = load(os.path.join(HERE, "out", "jackets", "contour-back.png"))
    knit = load(os.path.join(FA, "knit", "tardigrade-swatch.png"), 220)
    doodle = load(os.path.join(FA, "doodle", "doodle-3.png"), 520)
    cuts = load(os.path.join(FA, "cutouts", "sheet-v3.png"), 760)
    camo = load(os.path.join(FA, "camo", "soil-camo-sfw.png"), 400)
    P = {}
    P["hoodie-fungi"] = draw([HOODIE], fill(sk(1, 11), "fit", (140, 60, 560, 640)), lambda d: d.line([(350, 110), (350, 640)], fill=LINE, width=2))
    P["crewneck-soil"] = draw([CREW], fill(sk(1, 5), "fit", (50, 110, 650, 640)))
    P["puffer-vest-topo"] = draw([VEST], fill(topo, "fit", (160, 100, 540, 640)), lambda d: [d.line([(170, y), (530, y)], fill=(70, 74, 70), width=2) for y in range(180, 640, 70)])
    P["camp-shirt-bacteria"] = draw([SHIRT], fill(sk(1, 13), "fit", (130, 90, 570, 650)), lambda d: (d.line([(350, 100), (350, 650)], fill=LINE, width=2), [d.ellipse((342, y, 358, y + 16), fill=(240, 236, 222)) for y in (200, 310, 420, 530)]))
    P["joggers-doodle"] = draw([JOGGER], fill(doodle, "tile"), lambda d: d.rectangle((200, 80, 500, 125), fill=(34, 55, 31)))
    P["tote-amoeba"] = draw([TOTE], fill(sk(1, 9), "fit", (180, 230, 520, 640)), lambda d: (d.arc((240, 90, 340, 370), 180, 360, fill=LINE, width=10), d.arc((360, 90, 460, 370), 180, 360, fill=LINE, width=10)))
    P["backpack-camo"] = draw([BACKPACK], fill(camo, "tile"), lambda d: (d.rounded_rectangle((240, 380, 460, 600), 30, outline=LINE, width=3), d.arc((280, 60, 420, 220), 180, 360, fill=LINE, width=10)))
    P["duffel-topo"] = draw([DUFFEL], fill(topo, "fit", (70, 300, 630, 590)), lambda d: (d.line([(110, 330), (590, 330)], fill=(170, 170, 165), width=4), d.arc((230, 170, 470, 440), 180, 360, fill=LINE, width=12)))
    P["crossbody-knit"] = draw([CROSSBODY], fill(knit, "tile"), lambda d: (d.line([(220, 340), (80, 40)], fill=LINE, width=8), d.line([(480, 340), (620, 40)], fill=LINE, width=8)))
    P["drawstring-cutouts"] = draw([DRAWSTRING], fill(cuts, "fit", (200, 150, 500, 640)), lambda d: (d.line([(210, 160), (150, 640)], fill=(240, 236, 222), width=6), d.line([(490, 160), (550, 640)], fill=(240, 236, 222), width=6)))
    P["laptop-sleeve-soil"] = draw([SLEEVE], fill(sk(1, 19), "fit", (130, 200, 570, 530)))
    P["tote-hyphae"] = draw([TOTE], fill(sk(1, 12), "fit", (180, 230, 520, 640)), lambda d: (d.arc((240, 90, 340, 370), 180, 360, fill=LINE, width=10), d.arc((360, 90, 460, 370), 180, 360, fill=LINE, width=10)))
    for k, im in P.items(): im.save(os.path.join(OUT, f"{k}.png"))
    names = list(P); cols = 4
    sheet = Image.new("RGB", (cols * (C + 10) + 10, ((len(names) + cols - 1) // cols) * (C + 50) + 10), "#f4f4f1"); d = ImageDraw.Draw(sheet)
    for i, k in enumerate(names):
        x, y = 10 + (i % cols) * (C + 10), 10 + (i // cols) * (C + 50)
        sheet.paste(P[k], (x, y)); d.text((x + 10, y + C + 12), k.upper().replace("-", " "), fill=(30, 30, 30))
    sheet.save(os.path.join(OUT, "contact.jpg"), quality=88)


if __name__ == "__main__":
    main()
