"""Field map collage, after a layered outdoor-brand poster: a soil sample read like a map.
Layers: lime/sage halftone of a student micrograph, a giant pale nematode silhouette as the 'land', a survey grid,
framed inset panels (grey halftone micrograph + brown line tracing of the organism + labels), big outline type.
Output out/fieldmap/<name>.png at product sizes.
"""
import io, math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageOps, ImageFilter
from scipy import ndimage as ndi
from skimage import measure
import cairosvg
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "field-guide"))
from euglypha import text  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SRC, OUT = os.path.join(HERE, "src"), os.path.join(HERE, "out", "fieldmap")
LIME, SAGE, PALE, GREY, BROWN, WHITE, INKG = (203, 214, 122), (160, 166, 146), (233, 230, 222), (128, 128, 124), (107, 63, 30), (255, 255, 255), (60, 64, 54)


def gray(name, box=None, size=(1000, 1000)):
    im = Image.open(os.path.join(SRC, name + ".jpg")).convert("L")
    if name == "fungal-hypha-lee-kirk":
        im = im.crop((0, 20, im.width, im.height - 30))
    if box:
        w, h = im.size; im = im.crop((int(box[0] * w), int(box[1] * h), int(box[2] * w), int(box[3] * h)))
    im = ImageOps.fit(im, size, Image.LANCZOS)
    g = np.asarray(ImageOps.autocontrast(im, cutoff=1), np.float32) / 255
    flat = g - ndi.gaussian_filter(g, max(size) / 8) + .5
    return np.clip((flat - .5) * 1.6 + .5, 0, 1)


def halftone(v, cell, ang=30):
    h, w = v.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    a = math.radians(ang)
    u = xx * math.cos(a) + yy * math.sin(a); t = -xx * math.sin(a) + yy * math.cos(a)
    return np.hypot((u % cell) - cell / 2, (t % cell) - cell / 2) < cell * .7 * np.sqrt(np.clip(v, 0, 1))


def duo(mask, ink, paper):
    out = np.empty(mask.shape + (3,), np.uint8); out[:] = paper; out[mask] = ink
    return Image.fromarray(out)


def svg_layer(W, H, body):
    png = cairosvg.svg2png(bytestring=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">{body}</svg>'.encode())
    return Image.open(io.BytesIO(png)).convert("RGBA")


def trace(g, thr_q=.18, min_len=60):
    """Brown line tracing of the organisms: contours of the dark structures, smoothed."""
    s = ndi.gaussian_filter(g, 3)
    cs = measure.find_contours(s, np.quantile(s, thr_q))
    return [c[:, ::-1] for c in cs if len(c) > min_len]


def panel(page, x, y, w, h, src, box, title, sub, credit):
    g = gray(src, box, (w, h))
    tile = duo(halftone(1 - g, 9, 45), (92, 94, 88), (150, 152, 146))
    page.paste(tile, (x, y))
    d = ImageDraw.Draw(page)
    for c in trace(g):
        pts = [(x + px, y + py) for px, py in c[::2]]
        if len(pts) > 2: d.line(pts, fill=BROWN, width=7, joint="curve")
    grid = ImageDraw.Draw(page)
    for k in range(1, 4):
        grid.line([(x + w * k / 4, y), (x + w * k / 4, y + h)], fill=(235, 235, 230), width=2)
        grid.line([(x, y + h * k / 4), (x + w, y + h * k / 4)], fill=(235, 235, 230), width=2)
    d.rectangle((x, y, x + w, y + h), outline=WHITE, width=4)
    lab = svg_layer(page.width, page.height,
                    text(title, 46, x + 70, y + 66, fnt="eb-garamond-latin-600-normal.woff2", color="#fff", track=80)[0]
                    + text(sub, 34, x + 70, y + 112, color="#fff")[0]
                    + text(credit, 32, x + w - 24, y + h - 26, anchor="end", color="#fff")[0]
                    + f'<circle cx="{x + 40}" cy="{y + 52}" r="14" fill="none" stroke="#fff" stroke-width="4"/><line x1="{x + 40}" y1="{y + 30}" x2="{x + 40}" y2="{y + 74}" stroke="#fff" stroke-width="4"/><line x1="{x + 18}" y1="{y + 52}" x2="{x + 62}" y2="{y + 52}" stroke="#fff" stroke-width="4"/>')
    page.alpha_composite(lab)


def nematode_land(W, H):
    """Giant nematode silhouette crossing the sheet, like the land on a map."""
    t = np.linspace(0, 1, 600)
    P = np.array([(-.1 * W, .18 * H), (.9 * W, -.05 * H), (.1 * W, .75 * H), (1.1 * W, .62 * H)])
    c = ((1 - t) ** 3)[:, None] * P[0] + (3 * (1 - t) ** 2 * t)[:, None] * P[1] + (3 * (1 - t) * t ** 2)[:, None] * P[2] + (t ** 3)[:, None] * P[3]
    tg = np.gradient(c, axis=0); tg /= np.linalg.norm(tg, axis=1)[:, None]; n = np.c_[-tg[:, 1], tg[:, 0]]
    wdt = W * .2 * np.where(t < .06, np.sqrt(t / .06), np.where(t > .8, (1 - t) / .2, 1)) + 4
    poly = np.r_[c + n * wdt[:, None] / 2, (c - n * wdt[:, None] / 2)[::-1]]
    m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).polygon([tuple(p) for p in poly], fill=255)
    return m.filter(ImageFilter.GaussianBlur(1.5)), c


def fieldmap(name, W, H, word="SOIL", panels=None, base=("fungal-spores-in-suspension", None)):
    page = Image.new("RGBA", (W, H), SAGE + (255,))
    g = gray(base[0], base[1], (W, H))
    page.paste(duo(halftone(g, 12, 30), LIME, SAGE), (0, 0))
    land, spine = nematode_land(W, H)
    pale = Image.new("RGBA", (W, H), PALE + (255,))
    page.paste(pale, (0, 0), land)
    # faint halftone texture on the land
    tex = duo(halftone(gray("testate-encysted-sid-jensen", None, (W, H)) * .35, 10, 15), (214, 210, 200), PALE)
    page.paste(tex, (0, 0), Image.fromarray((np.asarray(land) * .6).astype(np.uint8)))
    d = ImageDraw.Draw(page)
    step = W // 10
    for x in range(0, W, step): d.line([(x, 0), (x, H)], fill=(255, 255, 255, 255), width=2)
    for y in range(0, H, step): d.line([(0, y), (W, y)], fill=(255, 255, 255, 255), width=2)
    # small location marks along the nematode, like towns
    for i in (120, 260, 430):
        px, py = spine[i]; d.rectangle((px - 14, py - 9, px + 14, py + 9), fill=LIME + (255,), outline=INKG + (255,), width=3)
    # giant outline word
    svg = text(word, int(W * .42), W / 2, H * .62, fnt="eb-garamond-latin-400-normal.woff2", anchor="middle", color="none", track=30)[0]
    svg = svg.replace('fill="none"', 'fill="none" stroke="#ffffff" stroke-width="5"')
    page.alpha_composite(svg_layer(W, H, svg))
    for p in panels or []:
        panel(page, *p)
    page.alpha_composite(svg_layer(W, H, text("SOIL FOOD WEB", int(W * .045), W - W * .05, H - H * .04, fnt="eb-garamond-latin-600-normal.woff2", anchor="end", color="#fff", track=120)[0]))
    os.makedirs(OUT, exist_ok=True)
    rgb = page.convert("RGB"); rgb.save(os.path.join(OUT, name + ".png"), dpi=(300, 300))
    p = rgb.copy(); p.thumbnail((1000, 1000)); p.save(os.path.join(OUT, name + "-preview.jpg"), quality=90)
    return rgb


if __name__ == "__main__":
    # notebook / poster, portrait 3000 x 4000
    fieldmap("fieldmap-portrait", 3000, 4000, panels=[
        (1700, 520, 1000, 820, "testate-amoeba-encysting-40x-joy-kaluf", (.25, .3, .65, .8), "TESTATE AMOEBA", "400x, soil extract", "Joy Kaluf"),
        (240, 1950, 1000, 820, "nematode-molting-cameron-radman", (.0, .0, .55, .45), "NEMATODE", "moulting, 400x", "Cameron Radman"),
        (1500, 2700, 1100, 900, "fungal-spore-josia-martens", (.3, .25, .85, .7), "FUNGAL SPORE", "400x, compost", "Josia Martens"),
    ])
