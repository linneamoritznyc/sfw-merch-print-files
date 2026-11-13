"""New garment types, each dressed in an SFW art direction the team liked.
Flat concept renders on one sheet: out/garments/contact.jpg (+ each piece as png).
"""
import os, sys, io
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
FA = os.path.join(HERE, "..", "fine-art", "out")
JK = os.path.join(HERE, "out", "jackets")
OUT = os.path.join(HERE, "out", "garments")
C = 700  # cell


def load(p, scale=1.0):
    im = Image.open(p).convert("RGB")
    return im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.LANCZOS)


def tile(src, w, h, ox=0, oy=0):
    f = Image.new("RGB", (w, h))
    for x in range(-ox, w, src.width):
        for y in range(-oy, h, src.height): f.paste(src, (x, y))
    return f


def piece(polys, fill, outline=(70, 70, 70), extra=None, bg=(232, 232, 229)):
    can = Image.new("RGB", (C, C), bg)
    m = Image.new("L", (C, C), 0); d = ImageDraw.Draw(m)
    for p in polys: d.polygon(p, fill=255)
    sh = m.filter(ImageFilter.GaussianBlur(10)).point(lambda v: v * .25)
    can.paste((150, 150, 148), (8, 10), sh) if False else None
    can.paste(fill, (0, 0), m)
    dd = ImageDraw.Draw(can)
    for p in polys: dd.polygon(p, outline=outline, width=3)
    if extra: extra(dd)
    return can


def main():
    os.makedirs(OUT, exist_ok=True)
    knit_mite = load(os.path.join(FA, "knit", "mite-swatch.png"), .45)
    knit_tard = load(os.path.join(FA, "knit", "tardigrade-swatch.png"), .3)
    topo = load(os.path.join(JK, "contour-back.png"), .35)
    doodle = load(os.path.join(FA, "doodle", "doodle-2.png"), .3)
    camo = load(os.path.join(FA, "camo", "soil-camo-forest.png"), .3)
    import cairosvg
    lsvg = open(os.path.join(FA, "linocut", "soil-garden-rect-7.svg")).read().replace('<path', '<rect width="3000" height="3600" fill="#22371F"/><path', 1).replace('fill="#B7CF5E"', 'fill="#A9C8A0"')
    lino = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=lsvg.encode(), output_width=620, output_height=744))).convert("RGB")
    cuts = load(os.path.join(FA, "cutouts", "sheet-v3.png"), .25)
    fleece = load(os.path.join(FA, "fleece", "contact.jpg"))
    fleece = fleece.crop((0, 0, fleece.width // 4, fleece.height)).resize((330, 440))

    P = {}
    # garden apron: bib, straps, two specimen pockets
    P["garden-apron"] = piece([[(250, 90), (450, 90), (470, 260), (560, 300), (560, 650), (140, 650), (140, 300), (230, 260)]],
                              tile(doodle, C, C), extra=lambda d: (d.line([(250, 90), (180, 20)], fill=(60, 60, 60), width=8), d.line([(450, 90), (520, 20)], fill=(60, 60, 60), width=8),
                                                                    d.rectangle((180, 420, 330, 560), outline=(60, 60, 60), width=4), d.rectangle((370, 420, 520, 560), outline=(60, 60, 60), width=4)))
    # bucket hat in soil camo
    P["bucket-hat"] = piece([[(220, 230), (480, 230), (500, 400), (200, 400)], [(90, 400), (610, 400), (660, 500), (40, 500)]], tile(camo, C, C))
    # knit beanie with the mite
    P["knit-beanie"] = piece([[(170, 560), (170, 300), (230, 180), (350, 140), (470, 180), (530, 300), (530, 560)]], tile(load(os.path.join(FA, "knit", "mite-swatch.png"), .32), C, C, -150, -70),
                             extra=lambda d: d.rectangle((170, 470, 530, 560), outline=(60, 60, 60), width=3))
    # crew socks, knit tardigrade
    sock = [(230, 80), (360, 80), (360, 470), (470, 520), (480, 620), (300, 620), (230, 560)]
    P["crew-socks"] = piece([sock], tile(load(os.path.join(FA, "knit", "tardigrade-swatch.png"), .12), C, C, -228, -100))
    # topo fanny pack
    P["fanny-pack"] = piece([[(130, 300), (570, 300), (600, 360), (580, 470), (120, 470), (100, 360)]], tile(topo, C, C),
                            extra=lambda d: (d.line([(20, 330), (100, 360)], fill=(30, 30, 30), width=12), d.line([(600, 360), (690, 330)], fill=(30, 30, 30), width=12), d.line([(130, 340), (570, 340)], fill=(180, 180, 175), width=4)))
    # linocut bandana
    P["bandana"] = piece([[(80, 140), (620, 140), (350, 600)]], tile(lino, C, C, -40, 20))
    # cut-out pictogram overshirt / chore coat
    P["chore-coat"] = piece([[(240, 80), (460, 80), (600, 160), (660, 520), (590, 540), (560, 320), (560, 660), (140, 660), (140, 320), (110, 540), (40, 520), (100, 160)]], tile(cuts, C, C, 60, 40),
                            extra=lambda d: (d.line([(350, 90), (350, 660)], fill=(30, 30, 30), width=4), [d.ellipse((340, y, 360, y + 20), fill=(220, 210, 180)) for y in (180, 300, 420, 540)]))
    # fleece sweatpants / track shorts
    P["fleece-shorts"] = piece([[(160, 160), (540, 160), (580, 520), (380, 540), (350, 360), (320, 540), (120, 520)]], tile(fleece, C, C),
                               extra=lambda d: d.rectangle((160, 160, 540, 210), fill=(34, 55, 31)))
    names = list(P)
    for k, im in P.items(): im.save(os.path.join(OUT, f"{k}.png"))
    sheet = Image.new("RGB", (4 * (C + 10) + 10, 2 * (C + 60) + 10), "#f4f4f1"); d = ImageDraw.Draw(sheet)
    for i, k in enumerate(names):
        x, y = 10 + (i % 4) * (C + 10), 10 + (i // 4) * (C + 60)
        sheet.paste(P[k], (x, y)); d.text((x + 10, y + C + 15), k.upper().replace("-", " "), fill=(30, 30, 30))
    sheet.save(os.path.join(OUT, "contact.jpg"), quality=90)


if __name__ == "__main__":
    main()
