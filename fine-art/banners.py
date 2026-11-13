"""Pixel banners: soil organisms charted as big square pixels, two inks, with a word box and small type.
Tall 1:3 banners. Output out/banners/<name>.png + contact.jpg
"""
import io, os, sys
import numpy as np
import cairosvg
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "field-guide"))
import cutouts  # noqa: E402
from euglypha import text  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "banners")
W, H = 1000, 3000
P = {p[0]: p[1] for p in cutouts.PICTOS}
PINK, LIME, BLACK, CREAM, FOREST = (238, 150, 196), (214, 240, 92), (18, 18, 18), (238, 236, 226), (34, 55, 31)


def grid(fn, n):
    d = cutouts.d_of(fn())
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{n * 4}" height="{n * 4}"><g transform="scale({n * 4 / 400})"><path d="{d}" fill="#000" fill-rule="evenodd"/></g></svg>'
    a = np.asarray(Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode()))).convert("RGBA"))[:, :, 3]
    return a.reshape(n, 4, n, 4).mean((1, 3)) > 90


def svg_img(body):
    return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">{body}</svg>'.encode()))).convert("RGBA")


def banner(organism, word, ground, body_c, edge_c, ink, seed):
    rng = np.random.default_rng(seed)
    page = Image.new("RGBA", (W, H), ground + (255,)); d = ImageDraw.Draw(page)
    n = 30; g = grid(P[organism], n); px = 30
    edge = g & ~ndi.binary_erosion(g)
    ox, oy = (W - n * px) // 2, 420
    for y in range(n):
        for x in range(n):
            if g[y, x]:
                c = edge_c if edge[y, x] else body_c
                d.rectangle((ox + x * px, oy + y * px, ox + x * px + px - 1, oy + y * px + px - 1), fill=c)
    # a hyphal stem of pixels from the organism to the bottom, with stray pixels like spores
    sx = ox + (n // 2) * px
    x = sx; y = oy + n * px
    while y < 2500:
        d.rectangle((x, y, x + px - 1, y + px - 1), fill=edge_c)
        if rng.random() < .25:
            k = rng.choice([-1, 1]); L = rng.integers(2, 6)
            for j in range(1, L): d.rectangle((x + k * j * px, y - j * px, x + k * j * px + px - 1, y - j * px + px - 1), fill=edge_c)
            d.rectangle((x + k * L * px, y - L * px, x + k * L * px + px - 1, y - L * px + px - 1), fill=body_c)
        x += rng.choice([-1, 0, 0, 1]) * px; y += px
    for _ in range(14):
        a, b = rng.integers(2, W // px - 2), rng.integers(14, 90)
        d.rectangle((a * px, b * px, a * px + px - 1, b * px + px - 1), fill=body_c)
    c = "#%02x%02x%02x" % ink
    body = text("Soil", 120, 60, 200, color=c)[0] + text("Food Web", 120, 280, 200, color=c)[0]
    tw = text(word, 120, 0, 0)[1]
    body += f'<rect x="{W - tw - 110}" y="2620" width="{tw + 50}" height="150" fill="#%02x%02x%02x"/>' % ink
    body += text(word, 120, W - 85, 2730, anchor="end", color="#%02x%02x%02x" % ground)[0]
    body += f'<text x="60" y="2900" font-family="Inter" font-weight="500" font-size="34" fill="{c}">{organism}</text>'
    body += f'<text x="60" y="2945" font-family="Inter" font-weight="500" font-size="34" fill="{c}">Student micrograph collection</text>'
    page.alpha_composite(svg_img(body))
    return page.convert("RGB")


def main():
    os.makedirs(OUT, exist_ok=True)
    plan = [("Testate amoeba", "shelter", BLACK, PINK, LIME, CREAM, 1), ("Fungal hyphae", "connect", LIME, PINK, FOREST, FOREST, 2),
            ("Nematode", "cycle", CREAM, PINK, FOREST, FOREST, 3), ("Ciliate", "graze", (40, 20, 40), PINK, LIME, CREAM, 4),
            ("Mycorrhizal root", "exchange", LIME, FOREST, PINK, FOREST, 5)]
    ims = []
    for org, word, gr, b, e, ink, sd in plan:
        im = banner(org, word, gr, b, e, ink, sd); im.save(os.path.join(OUT, f"banner-{word}.png")); ims.append(im)
    sheet = Image.new("RGB", (len(ims) * 330 + 30, 1000), "#dedcd4")
    for i, im in enumerate(ims): sheet.paste(im.resize((300, 900), Image.LANCZOS), (30 + i * 330, 50))
    sheet.save(os.path.join(OUT, "contact.jpg"), quality=90)


if __name__ == "__main__":
    main()
