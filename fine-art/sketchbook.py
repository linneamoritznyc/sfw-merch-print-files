"""Sketchbook: fast random studies. Each study rolls a ground, a micrograph treatment, a window shape, flat grainy
shapes, type, line tracings and small labels, then composes them. Run: python3 sketchbook.py <seed> <count>
Writes out/sketchbook/<seed>/study-NN.png and a contact sheet.
"""
import io, math, os, sys, glob
import numpy as np
from PIL import Image, ImageDraw, ImageOps, ImageChops
from scipy import ndimage as ndi
from skimage import measure
import cairosvg
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "field-guide"))
from euglypha import text  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src")
PLATES = os.path.join(HERE, "..", "field-guide", "out", "plates")
W, H = 900, 1200
COL = {"lime": (203, 219, 108), "sage": (179, 190, 177), "cream": (243, 240, 230), "deep": (34, 55, 31), "fwg": (21, 104, 38),
       "light": (89, 166, 108), "teal": (30, 91, 76), "violet": (110, 90, 156), "lilac": (185, 169, 218), "black": (20, 20, 20),
       "white": (255, 255, 255), "brown": (107, 63, 30), "blue": (60, 111, 168), "pink": (240, 120, 150), "grey": (150, 152, 146)}
GROUNDS = ["lime", "sage", "cream", "deep", "black", "violet", "white", "teal"]
WORDS = ["PROTOZOA", "FUNGI", "NEMATODES", "BACTERIA", "SOIL", "HYPHAE", "AMOEBA", "ALIVE", "MICROARTHROPODS", "TESTATE"]
SOURCES = [os.path.basename(f)[:-4] for f in glob.glob(os.path.join(SRC, "*.jpg"))]
CREDIT = {"fungal-hypha-lee-kirk": "Lee Kirk", "fungal-spore-josia-martens": "Josia Martens", "mite-talbot-armstrong-i3": "Talbot Armstrong",
          "nematode-molting-cameron-radman": "Cameron Radman", "reproductive-structure-holly-bain": "Holly Bain",
          "stellate-amoeba-jimena-fuentes": "Jimena Fuentes", "testate-encysted-robert-kenyon": "Robert Kenyon",
          "testate-encysted-sid-jensen": "Sid Jensen", "testate-encysting-jimena-fuentes-i2": "Jimena Fuentes",
          "fungal-spores-in-suspension": "SFW lab", "testate-amoeba-encysting-40x-joy-kaluf": "Joy Kaluf"}


def svg(body, w=W, h=H):
    return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}">{body}</svg>'.encode()))).convert("RGBA")


def micro(rng, size):
    name = SOURCES[rng.integers(len(SOURCES))]
    im = Image.open(os.path.join(SRC, name + ".jpg")).convert("L")
    if name == "fungal-hypha-lee-kirk": im = im.crop((0, 20, im.width, im.height - 30))
    z = rng.uniform(.3, .9); w, h = im.size; cw, ch = w * z, h * z
    x0, y0 = rng.uniform(0, w - cw), rng.uniform(0, h - ch)
    im = ImageOps.fit(im.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))), size, Image.LANCZOS)
    g = np.asarray(ImageOps.autocontrast(im, cutoff=1), np.float32) / 255
    g = np.clip((g - ndi.gaussian_filter(g, max(size) / 8)) * 1.7 + .5, 0, 1)
    return g, name


def halftone(v, cell, ang):
    h, w = v.shape; yy, xx = np.mgrid[0:h, 0:w].astype(np.float32); a = math.radians(ang)
    u = xx * math.cos(a) + yy * math.sin(a); t = -xx * math.sin(a) + yy * math.cos(a)
    return np.hypot((u % cell) - cell / 2, (t % cell) - cell / 2) < cell * .7 * np.sqrt(np.clip(v, 0, 1))


def treat(rng, g, ink, paper):
    """One of several print treatments for a micrograph."""
    k = rng.integers(4)
    if k == 0: m = halftone(1 - g, rng.uniform(5, 11), rng.uniform(0, 90))           # halftone
    elif k == 1: m = g < np.quantile(g, rng.uniform(.25, .45))                       # hard posterise
    elif k == 2: m = (rng.random(g.shape) > g ** 1.4)                                 # stochastic grain
    else:                                                                             # line engraving: horizontal lines thickened by darkness
        yy = np.mgrid[0:g.shape[0], 0:g.shape[1]][0]
        m = np.abs(((yy % 7) - 3.5)) < (1 - g) * 3.4
    out = np.empty(g.shape + (4,), np.uint8); out[:] = paper + (255,); out[m] = ink + (255,)
    return Image.fromarray(out)


def window(rng, w, h):
    """Mask for the micrograph window: rect, arch, half disc, lens, quarter, tall pill."""
    m = Image.new("L", (w, h), 0); d = ImageDraw.Draw(m); k = rng.integers(6)
    if k == 0: d.rectangle((0, 0, w, h), fill=255)
    elif k == 1: d.rectangle((0, w // 2, w, h), fill=255); d.ellipse((0, 0, w, w), fill=255)
    elif k == 2: d.pieslice((0, 0, w, 2 * h), 180, 360, fill=255)
    elif k == 3:
        d.chord((-w * .5, 0, w * 1.0, h), 270, 90, fill=255); m2 = Image.new("L", (w, h), 0); ImageDraw.Draw(m2).chord((0, 0, w * 1.5, h), 90, 270, fill=255); m = ImageChops.multiply(m, m2)
    elif k == 4: d.pieslice((-w, -h, w, h), 0, 90, fill=255)
    else: d.rounded_rectangle((0, 0, w, h), radius=w // 2, fill=255)
    return m


def grain(img, rng, amt=.18):
    a = np.asarray(img).astype(np.float32); n = ndi.gaussian_filter(rng.random(a.shape[:2]).astype(np.float32), .7); n = (n - n.mean()) / (n.std() + 1e-6)
    a[:, :, :3] *= (1 + amt * .25 * n)[:, :, None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def shapes(rng, cols):
    out = ""
    for _ in range(rng.integers(1, 4)):
        c = cols[rng.integers(len(cols))]; hexc = "#%02x%02x%02x" % COL[c]
        x, y, s = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(120, 420); k = rng.integers(5)
        if k == 0: out += f'<path d="M{x - s},{y} A{s},{s} 0 0 1 {x + s},{y} Z" fill="{hexc}"/>'
        elif k == 1: out += f'<circle cx="{x}" cy="{y}" r="{s * .6}" fill="{hexc}"/>'
        elif k == 2: out += f'<path d="M{x},{y - s} Q{x + s},{y} {x},{y + s} Q{x - s},{y} {x},{y - s} Z" fill="{hexc}"/>'
        elif k == 3: out += f'<rect x="{x - s}" y="{y - s * .22}" width="{2 * s}" height="{s * .44}" rx="{s * .22}" fill="{hexc}" transform="rotate({rng.uniform(-60, 60)} {x} {y})"/>'
        else: out += f'<path d="M{x},{y} L{x + s},{y} A{s},{s} 0 0 1 {x},{y + s} Z" fill="{hexc}"/>'
    return out


def contours(g, ink, ox, oy, rng):
    s = ndi.gaussian_filter(g, 2.5); out = ""
    for c in measure.find_contours(s, np.quantile(s, rng.uniform(.12, .25))):
        if len(c) < 50: continue
        out += '<path d="M' + "L".join(f"{ox + x:.1f},{oy + y:.1f}" for y, x in c[::2]) + f'" fill="none" stroke="#{"%02x%02x%02x" % ink}" stroke-width="{rng.uniform(2, 5):.1f}" stroke-linejoin="round"/>'
    return out


def study(seed):
    rng = np.random.default_rng(seed)
    gname = GROUNDS[rng.integers(len(GROUNDS))]; ground = COL[gname]
    dark = gname in ("deep", "black", "violet", "teal")
    pal = [c for c in COL if c != gname]
    ink = COL["white"] if dark else COL[["deep", "black", "brown", "teal", "violet"][rng.integers(5)]]
    page = Image.new("RGBA", (W, H), ground + (255,))
    # 1. maybe a full-bleed faint micrograph field
    if rng.random() < .45:
        g, _ = micro(rng, (W, H)); sub = COL[pal[rng.integers(len(pal))]]
        page = Image.alpha_composite(page, Image.blend(page, treat(rng, g, sub, ground), .55))
    # 2. type
    word = WORDS[rng.integers(len(WORDS))]; mode = rng.integers(4); tcol = "#%02x%02x%02x" % ink
    body = ""
    if mode == 0:     # repeated stack
        sz = W * 1.04 / (text(word, 100, 0, 0)[1] / 100); y = sz * .8
        while y < H + sz: body += text(word, sz, W / 2, y, anchor="middle", color=tcol, track=-10)[0]; y += sz * .86
    elif mode == 1:   # one giant word cropped off the edge
        sz = rng.uniform(380, 620); body += text(word.split()[0], sz, rng.uniform(-80, 60), rng.uniform(H * .45, H * .95), color=tcol)[0]
    elif mode == 2:   # outline giant word
        sz = W * 1.1 / (text(word, 100, 0, 0)[1] / 100); body += text(word, sz, W / 2, H * rng.uniform(.4, .8), anchor="middle", color="none")[0].replace('fill="none"', f'fill="none" stroke="{tcol}" stroke-width="3"')
    else:             # small editorial label block
        body += text(word, 64, 60, 120, fnt="eb-garamond-latin-600-normal.woff2", color=tcol, track=120)[0]
        body += text("observations from the soil", 30, 60, 165, color=tcol)[0]
    under = rng.random() < .5
    if under: page.alpha_composite(svg(body))
    # 3. micrograph window
    if rng.random() < .85:
        ww, wh = int(rng.uniform(.4, .85) * W), int(rng.uniform(.3, .65) * H)
        x, y = int(rng.uniform(0, W - ww)), int(rng.uniform(0, H - wh))
        g, name = micro(rng, (ww, wh))
        tile = treat(rng, g, COL[pal[rng.integers(len(pal))]], COL[pal[rng.integers(len(pal))]])
        page.paste(tile, (x, y), window(rng, ww, wh))
        if rng.random() < .5:
            page.alpha_composite(svg(contours(g, COL[["brown", "white", "pink", "deep"][rng.integers(4)]], x, y, rng)))
        if rng.random() < .6:
            page.alpha_composite(svg(text(CREDIT.get(name, ""), 22, x + ww - 10, y + wh - 14, anchor="end", color="#fff" if dark else tcol)[0] + text("400x", 22, x + 12, y + 30, color="#fff" if dark else tcol)[0]))
    # 4. flat shapes with grain
    if rng.random() < .7:
        page.alpha_composite(grain(svg(shapes(rng, pal)), rng))
    # 5. grid
    if rng.random() < .3:
        d = ImageDraw.Draw(page); st = int(rng.choice([75, 90, 112]))
        for v in range(0, W, st): d.line([(v, 0), (v, H)], fill=(255, 255, 255, 120), width=1)
        for v in range(0, H, st): d.line([(0, v), (W, v)], fill=(255, 255, 255, 120), width=1)
    # 6. a cut-out organism
    if rng.random() < .4:
        import cutouts
        name, fn, ink = cutouts.PICTOS[rng.integers(len(cutouts.PICTOS))]
        sc = rng.uniform(.6, 1.4); x, y = rng.uniform(-60, W - 300), rng.uniform(-60, H - 300)
        c = "#%02x%02x%02x" % COL[pal[rng.integers(len(pal))]]
        page.alpha_composite(grain(svg(f'<g transform="translate({x},{y}) scale({sc})"><path d="{cutouts.d_of(fn())}" fill="{c}" fill-rule="evenodd"/></g>'), rng))
    # 7. a second, smaller micrograph window
    if rng.random() < .3:
        ww, wh = int(rng.uniform(.2, .4) * W), int(rng.uniform(.15, .3) * H)
        x, y = int(rng.uniform(0, W - ww)), int(rng.uniform(0, H - wh))
        g2, _ = micro(rng, (ww, wh))
        page.paste(treat(rng, g2, COL[pal[rng.integers(len(pal))]], COL[pal[rng.integers(len(pal))]]), (x, y), window(rng, ww, wh))
    if not under:
        if rng.random() < .3:   # off-register second pass of the type
            sec = "#%02x%02x%02x" % COL[pal[rng.integers(len(pal))]]
            page.alpha_composite(svg(f'<g transform="translate({rng.integers(-9, 9)},{rng.integers(-9, 9)})">' + body.replace(tcol, sec) + '</g>'))
        page.alpha_composite(svg(body))
    # 8. vertical dot labels
    if rng.random() < .45:
        lc = "#fff" if dark else tcol
        lb = ""
        for k in range(rng.integers(1, 4)):
            x, y = rng.uniform(40, W - 40), rng.uniform(300, H - 60)
            lb += f'<circle cx="{x}" cy="{y}" r="6" fill="{lc}"/><g transform="translate({x + 8},{y - 14}) rotate(-90)">' + text(["Soil Food Web", "400x", "observed in compost", "student micrograph", "field note"][rng.integers(5)], 22, 0, 0, color=lc)[0] + '</g>'
        page.alpha_composite(svg(lb))
    return page.convert("RGB")


def main(seed0=0, n=24):
    out = os.path.join(HERE, "out", "sketchbook", str(seed0)); os.makedirs(out, exist_ok=True)
    ims = []
    for i in range(n):
        im = study(seed0 * 1000 + i); im.save(os.path.join(out, f"study-{i + 1:02d}.png")); ims.append(im)
    cols = 6; tw, th = 300, 400
    sheet = Image.new("RGB", (cols * (tw + 12) + 12, math.ceil(n / cols) * (th + 40) + 12), "#e9e9e9")
    d = ImageDraw.Draw(sheet)
    for i, im in enumerate(ims):
        r, c = divmod(i, cols); t = im.resize((tw, th), Image.LANCZOS); x, y = 12 + c * (tw + 12), 12 + r * (th + 40)
        sheet.paste(t, (x, y)); d.text((x, y + th + 8), f"{seed0}-{i + 1:02d}", fill=(40, 40, 40))
    sheet.save(os.path.join(out, "contact.jpg"), quality=88)


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 0, int(sys.argv[2]) if len(sys.argv) > 2 else 24)
