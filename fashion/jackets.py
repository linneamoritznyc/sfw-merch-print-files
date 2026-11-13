"""Original AOP zip jacket concepts, each built from SFW's own visual language.
  horizons   soil profile colour-blocked from collar (leaf litter) to hem (subsoil), roots and hyphae crossing the bands
  fieldmap   halftone micrograph field, survey grid, inset micrograph panels with labels, big outline SOIL on the back
  doodle     crayon soil doodles all over (hyphae, coiled nematodes, amoebae, testate urns)
  camo       soil camo from a real micrograph of aggregates
  knit       knit ground with one big knit organism across the back, small one on the chest
  sketch     sketchbook study: serif word down the sleeves, micrograph window on the back, flat grainy shapes
Outputs out/jackets/<concept>-front.png, -back.png (2400 x 2400 art) and contact.jpg mockups.
"""
import io, math, os, sys
import numpy as np
import cairosvg
from PIL import Image, ImageDraw, ImageOps, ImageChops
from scipy import ndimage as ndi
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fine-art"))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "field-guide"))
import cutouts, doodle, camo, knit, fieldmap  # noqa: E402
from euglypha import text  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "jackets")
FA = os.path.join(HERE, "..", "fine-art")
S = 2400


def svg_img(body, w=S, h=S):
    return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}">{body}</svg>'.encode()))).convert("RGBA")


def fit(im):
    return ImageOps.fit(im.convert("RGB"), (S, S), Image.LANCZOS)


# ------------------------------------------------------------------ concepts
def horizons():
    bands = [("#3F6B2A", 0), ("#22371F", 420), ("#4F3433", 860), ("#7A5A3A", 1400), ("#B5893B", 1950)]
    rng = np.random.default_rng(2)
    def art(back):
        body = ""
        for i, (c, y) in enumerate(bands):
            pts = " ".join(f"{x},{y + 30 * math.sin(x / 260 + i * 1.7)}" for x in range(0, S + 60, 60))
            body += f'<polygon points="0,{S} {pts} {S},{S}" fill="{c}"/>'
        # roots from the collar down, hyphae branching off, in cream
        for x0 in ([1200] if back else [900, 1500]):
            x, y, a = x0, 380, math.pi / 2; pts = []
            for k in range(120):
                pts.append((x, y)); a += rng.normal(0, .05); x += math.cos(a) * 16; y += math.sin(a) * 16
            body += '<path d="M' + "L".join(f"{p[0]:.0f},{p[1]:.0f}" for p in pts) + f'" fill="none" stroke="#E9E4D4" stroke-width="{16 if back else 10}" stroke-linecap="round"/>'
            for k in range(8, 118, 7):
                bx, by = pts[k]; s = 1 if k % 2 else -1; L = rng.uniform(120, 320)
                ex, ey = bx + s * L, by + L * .5
                body += f'<path d="M{bx:.0f},{by:.0f} Q{bx + s * L * .5:.0f},{by - 20:.0f} {ex:.0f},{ey:.0f}" fill="none" stroke="#E9E4D4" stroke-width="5" stroke-linecap="round"/><circle cx="{ex:.0f}" cy="{ey:.0f}" r="9" fill="#CBDB6C"/>'
        labels = ["leaf litter", "humus", "topsoil", "subsoil", "parent material"]
        for (c, y), t in zip(bands, labels):
            body += f'<circle cx="160" cy="{y + 200}" r="9" fill="#E9E4D4"/>' + text(t, 40, 185, y + 213, color="#E9E4D4")[0]
        return svg_img(body).convert("RGB")
    return art(False), art(True)


def fieldmap_art():
    front = fieldmap.fieldmap("jacket-fieldmap-front", 2400, 2400, word="", panels=[(1350, 500, 650, 520, "testate-amoeba-encysting-40x-joy-kaluf", (.25, .3, .65, .8), "TESTATE", "400x", "Joy Kaluf")])
    back = fieldmap.fieldmap("jacket-fieldmap-back", 2400, 2400, word="SOIL", panels=[(260, 1500, 800, 640, "nematode-molting-cameron-radman", (0, 0, .55, .45), "NEMATODE", "moulting, 400x", "Cameron Radman"), (1340, 1500, 800, 640, "fungal-spore-josia-martens", (.3, .25, .85, .7), "FUNGAL SPORE", "400x", "Josia Martens")])
    return fit(front), fit(back)


def doodle_art():
    a = doodle.compose(7, (89, 120, 80), (240, 236, 214)); b = doodle.compose(9, (89, 120, 80), (240, 236, 214))
    return fit(a), fit(b)


def camo_art():
    return fit(camo.camo("testate-encysting-jimena-fuentes-i2", camo.WAYS["desert"], 3)), fit(camo.camo("testate-encysted-robert-kenyon", camo.WAYS["desert"], 4))


def knit_art():
    rng = np.random.default_rng(5); g, body, stripe, line = knit.YARNS["Mite"]
    cols = [g, body, stripe, line]
    back = knit.render(knit.chart(cutouts.mite, 100, 100, (14, 18, 72)), cols, rng)
    m = np.zeros((100, 100), np.uint8)
    small = knit.chart(cutouts.mite, 100, 100, (62, 18, 18))
    front = knit.render(small, cols, rng)
    return fit(front), fit(back)


def sketch_art():
    def art(back):
        page = Image.new("RGBA", (S, S), (203, 219, 108, 255))
        body = ""
        for side in (1, -1):        # word running down each sleeve
            x = 1200 + side * 980
            body += f'<g transform="translate({x},{300}) rotate(90)">' + text("HYPHAE", 230, 0, 0, color="#22371F")[0] + "</g>"
        page.alpha_composite(svg_img(body))
        if back:
            g = np.asarray(ImageOps.autocontrast(ImageOps.fit(Image.open(os.path.join(FA, "src", "fungal-spore-josia-martens.jpg")).convert("L"), (1100, 1300)), cutoff=1), np.float32) / 255
            yy, xx = np.mgrid[0:1300, 0:1100]
            ht = np.hypot((xx % 12) - 6, (yy % 12) - 6) < 8.4 * np.sqrt(1 - g)
            tile = np.empty((1300, 1100, 4), np.uint8); tile[:] = (185, 169, 218, 255); tile[ht] = (34, 55, 31, 255)
            win = Image.new("L", (1100, 1300), 0); ImageDraw.Draw(win).rectangle((0, 550, 1100, 1300), fill=255); ImageDraw.Draw(win).ellipse((0, 0, 1100, 1100), fill=255)
            page.paste(Image.fromarray(tile), (650, 650), win)
            page.alpha_composite(svg_img('<circle cx="1750" cy="760" r="260" fill="#156826"/><path d="M500,2050 A300,300 0 0 1 1100,2050 Z" fill="#E9E4D4"/>' + text("observations from the soil", 50, 1200, 2250, anchor="middle", color="#22371F")[0]))
        else:
            page.alpha_composite(svg_img(f'<g transform="translate(1320,520) scale(.5)"><path d="{cutouts.d_of(cutouts.testate())}" fill="#22371F"/></g><path d="M300,1700 A260,260 0 0 1 820,1700 Z" fill="#9B1D52"/>'))
        return page.convert("RGB")
    return art(False), art(True)


def contour_art():
    """Topo lines traced from a real micrograph of soil aggregates, like quilted stitching, on black."""
    from skimage import measure
    def art(src, seed):
        g = np.asarray(ImageOps.autocontrast(ImageOps.fit(Image.open(os.path.join(FA, "src", src + ".jpg")).convert("L"), (600, 600)), cutoff=1), np.float32) / 255
        g = ndi.gaussian_filter(g, 9)
        body = f'<rect width="{S}" height="{S}" fill="#151715"/>'
        for lv in np.linspace(np.quantile(g, .1), np.quantile(g, .9), 9):
            for c in measure.find_contours(g, lv):
                if len(c) < 40: continue
                body += '<path d="M' + "L".join(f"{x * 4:.0f},{y * 4:.0f}" for y, x in c[::2]) + '" fill="none" stroke="#B3BEB1" stroke-width="6" stroke-dasharray="22 10" stroke-linecap="round"/>'
        return svg_img(body).convert("RGB")
    return art("testate-encysted-robert-kenyon", 1), art("testate-encysting-jimena-fuentes-i2", 2)


def patchwork_art():
    """Patchwork of rectangles, each a different micrograph and print treatment, in earthy patch colours."""
    import sketchbook
    def art(seed):
        rng = np.random.default_rng(seed); page = Image.new("RGB", (S, S))
        cols = [(80, 40, 45), (196, 178, 140), (40, 46, 70), (150, 110, 70), (60, 70, 55), (30, 30, 30), (120, 130, 100)]
        def split(x, y, w, h, d):
            if d == 0 or w < 500 or h < 500:
                g, _ = sketchbook.micro(rng, (int(w), int(h)))
                ink = cols[rng.integers(len(cols))]; paper = cols[rng.integers(len(cols))]
                if ink == paper: paper = (225, 215, 190)
                page.paste(sketchbook.treat(rng, g, ink, paper).convert("RGB"), (int(x), int(y)))
                ImageDraw.Draw(page).rectangle((x, y, x + w, y + h), outline=(20, 20, 20), width=6)
                return
            if w > h: k = rng.uniform(.35, .65) * w; split(x, y, k, h, d - 1); split(x + k, y, w - k, h, d - 1)
            else: k = rng.uniform(.35, .65) * h; split(x, y, w, k, d - 1); split(x, y + k, w, h - k, d - 1)
        split(0, 0, S, S, 4)
        return page
    return art(1), art(2)


def squiggle_art():
    """Charcoal ground; white hyphae squiggles, stippled spore clouds, hatched amoeba blobs, rust patches."""
    def art(seed):
        rng = np.random.default_rng(seed); body = f'<rect width="{S}" height="{S}" fill="#3A3C38"/>'
        for _ in range(7):
            x, y, r = rng.uniform(0, S), rng.uniform(0, S), rng.uniform(120, 240)
            pts = " ".join(f"{x + r * (1 + .3 * math.sin(3 * t + seed)) * math.cos(t):.0f},{y + r * (1 + .3 * math.sin(3 * t + seed)) * math.sin(t):.0f}" for t in np.linspace(0, 6.28, 40))
            body += f'<polygon points="{pts}" fill="#7A3A2A"/>'
        for _ in range(16):
            x, y, a = rng.uniform(0, S), rng.uniform(0, S), rng.uniform(0, 6.28); pts = []
            for k in range(90):
                pts.append((x, y)); a += .25 * math.sin(k / 4 + seed) + rng.normal(0, .05); x += math.cos(a) * 18; y += math.sin(a) * 18
            p = "M" + "L".join(f"{u:.0f},{v:.0f}" for u, v in pts)
            body += f'<path d="{p}" fill="none" stroke="#ECE8DC" stroke-width="16" stroke-linecap="round"/><path d="{p}" fill="none" stroke="#3A3C38" stroke-width="5" stroke-linecap="round"/>'
        for _ in range(9):
            cx, cy, r = rng.uniform(0, S), rng.uniform(0, S), rng.uniform(100, 200)
            for _ in range(160):
                a, rr = rng.uniform(0, 6.28), r * math.sqrt(rng.random())
                body += f'<circle cx="{cx + rr * math.cos(a):.0f}" cy="{cy + rr * math.sin(a):.0f}" r="{rng.uniform(3, 7):.1f}" fill="#ECE8DC"/>'
        for _ in range(5):
            cx, cy, r = rng.uniform(0, S), rng.uniform(0, S), rng.uniform(90, 160)
            body += f'<clipPath id="h{_}"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath><g clip-path="url(#h{_})">' + "".join(f'<line x1="{cx - r}" y1="{cy - r + k}" x2="{cx + r}" y2="{cy + r + k}" stroke="#ECE8DC" stroke-width="5"/>' for k in range(-2 * int(r), 2 * int(r), 22)) + f'</g><circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#ECE8DC" stroke-width="7"/>'
        return svg_img(body).convert("RGB")
    return art(1), art(2)


def cracks_art():
    """Dried soil crack polygons (Voronoi), lime plates with blue-violet crack lines, like a sherpa fleece."""
    from scipy.spatial import Voronoi
    def art(seed):
        rng = np.random.default_rng(seed); pts = rng.uniform(-300, S + 300, (140, 2))
        vor = Voronoi(pts); body = f'<rect width="{S}" height="{S}" fill="#4A3F9A"/>'
        for i, reg in enumerate(vor.point_region):
            r = vor.regions[reg]
            if -1 in r or not r: continue
            poly = np.array([vor.vertices[j] for j in r]); c = poly.mean(0)
            poly = c + (poly - c) * rng.uniform(.82, .9)
            from scipy.interpolate import splprep, splev
            P = np.r_[poly, poly[:1]]
            try:
                tck, _ = splprep([P[:, 0], P[:, 1]], s=len(P) * 400, per=True); xs, ys = splev(np.linspace(0, 1, 60), tck)
            except Exception: xs, ys = P[:, 0], P[:, 1]
            body += '<path d="M' + "L".join(f"{x:.0f},{y:.0f}" for x, y in zip(xs, ys)) + 'Z" fill="#B9C93A"/>'
        return svg_img(body).convert("RGB")
    return art(3), art(4)


def chestband_art():
    """Dark fleece with one band across the chest: a hyphae micrograph thresholded to cream stripes."""
    def art(seed):
        page = Image.new("RGB", (S, S), (30, 44, 40))
        g = np.asarray(ImageOps.autocontrast(ImageOps.fit(Image.open(os.path.join(FA, "src", "fungal-hypha-lee-kirk.jpg")).convert("L"), (S, 560)), cutoff=1), np.float32) / 255
        e = np.hypot(ndi.sobel(ndi.gaussian_filter(g, 2), 0), ndi.sobel(ndi.gaussian_filter(g, 2), 1))
        m = e > np.quantile(e, .78)
        band = np.empty((560, S, 3), np.uint8); band[:] = (30, 44, 40); band[m] = (222, 214, 196)
        y0 = 760 if seed == 1 else 980
        page.paste(Image.fromarray(band), (0, y0))
        if seed == 1:
            page.paste(Image.new("RGB", (150, 70), (34, 55, 31)), (1340, 520))
            ImageDraw.Draw(page).rectangle((1340, 520, 1490, 590), outline=(222, 214, 196), width=4)
        return page
    return art(1), art(2)


def rings_art():
    """Fungal fairy rings / colony growth rings: concentric wobbly rings all over."""
    def art(seed):
        rng = np.random.default_rng(seed); body = f'<rect width="{S}" height="{S}" fill="#6E6A3A"/>'
        centres = [(rng.uniform(0, S), rng.uniform(0, S)) for _ in range(22)]
        for cx, cy in centres:
            R = rng.uniform(150, 330); ph = rng.uniform(0, 6)
            for k, r in enumerate(np.arange(R, 10, -26)):
                pts = " ".join(f"{cx + r * (1 + .05 * math.sin(4 * t + ph)) * math.cos(t):.0f},{cy + r * (1 + .05 * math.sin(4 * t + ph)) * math.sin(t):.0f}" for t in np.linspace(0, 6.28, 70))
                body += f'<polygon points="{pts}" fill="{["#2F4A2B", "#C9B98A", "#4F6B3A"][k % 3]}"/>'
        return svg_img(body).convert("RGB")
    return art(1), art(2)


CONCEPTS = {"horizons": horizons, "fieldmap": fieldmap_art, "doodle": doodle_art, "camo": camo_art, "knit": knit_art, "sketch": sketch_art, "contour": contour_art, "patchwork": patchwork_art, "squiggle": squiggle_art, "cracks": cracks_art, "chestband": chestband_art, "rings": rings_art}

# ------------------------------------------------------------------ mockup: flat zip hoodie silhouette
BODY = [(720, 360), (980, 280), (1420, 280), (1680, 360), (2020, 620), (2280, 1550), (2300, 2200), (2080, 2230), (1930, 1350),
        (1900, 2230), (500, 2230), (470, 1350), (320, 2230), (100, 2200), (120, 1550), (380, 620)]
HOOD = [(900, 330), (860, 120), (1000, 20), (1200, -10), (1400, 20), (1540, 120), (1500, 330)]
CUFF = 70; HEM = 110


def mock(art, front=True):
    can = Image.new("RGB", (S, 2400), (228, 228, 226))
    m = Image.new("L", (S, 2400), 0); d = ImageDraw.Draw(m)
    d.polygon([(x, y + 80) for x, y in BODY], fill=255); d.polygon([(x, y + 80) for x, y in HOOD], fill=255)
    can.paste(art, (0, 0), m)
    dd = ImageDraw.Draw(can)
    dk = tuple(int(v * .7) for v in art.getpixel((1200, 2280)))
    dd.rectangle((500, 2230 + 80 - HEM, 1900, 2230 + 80), fill=dk)
    for cx in ((100, 320), (2080, 2300)): dd.polygon([(cx[0], 2200 + 80 - CUFF), (cx[1], 2230 + 80 - CUFF), (cx[1], 2230 + 80), (cx[0], 2200 + 80)], fill=dk)
    if front:
        dd.line([(1200, 330 + 80), (1200, 2230 + 80)], fill=(30, 30, 30), width=12)
        for x in (1120, 1280): dd.line([(x, 360 + 80), (x - 10, 700 + 80)], fill=(235, 235, 230), width=8)
    dd.polygon([(x, y + 80) for x, y in BODY], outline=(60, 60, 60), width=5)
    return can


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for name, fn in CONCEPTS.items():
        f, b = fn()
        f.save(os.path.join(OUT, f"{name}-front.png")); b.save(os.path.join(OUT, f"{name}-back.png"))
        row = Image.new("RGB", (2 * 600 + 10, 600), (228, 228, 226))
        row.paste(mock(f, True).resize((600, 600), Image.LANCZOS), (0, 0)); row.paste(mock(b, False).resize((600, 600), Image.LANCZOS), (610, 0))
        rows.append(row)
    sheet = Image.new("RGB", (3 * 1220 + 10, 4 * 610 + 10), "#fff")
    for i, r in enumerate(rows): sheet.paste(r, (5 + (i % 3) * 1220, 5 + (i // 3) * 610))
    sheet.save(os.path.join(OUT, "contact.jpg"), quality=88)


if __name__ == "__main__":
    main()
