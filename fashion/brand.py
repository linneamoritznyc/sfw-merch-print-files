"""SFW core designs: print-ready art (transparent PNG, 3600 x 4800 = 12 x 16 in at 300 dpi) plus flat product mockups.
  look-closer      stacked serif TESTATE, a halftone micrograph window cut into it            (tee back, tote)
  specimen         small typed chest label + big halftone testate amoeba on the back             (tee)
  index            the soil food web cast: 8 cut-outs, numbered, named, field-guide grid         (tee back, poster, tote)
  topo             contour lines from a student micrograph, framed, with a typed caption          (tote, hoodie back)
  four-groups      PROTOZOA / FUNGI / NEMATODES / BACTERIA list with dot labels                     (tee, tote)
  wordmark         Soil Food Web in serif with a hypha growing from the W                          (cap, chest)
Output out/brand/<name>-<ink>.png and contact.jpg
"""
import io, math, os, sys
import numpy as np
import cairosvg
from PIL import Image, ImageOps, ImageDraw
from scipy import ndimage as ndi
from skimage import measure
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fine-art"))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "field-guide"))
import cutouts  # noqa: E402
from euglypha import text  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "fine-art", "src")
OUT = os.path.join(HERE, "out", "brand")
W, H = 3600, 4800


def svg_img(body, w=W, h=H):
    return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}">{body}</svg>'.encode()))).convert("RGBA")


def gray(src, size, box=None):
    im = Image.open(os.path.join(SRC, src + ".jpg")).convert("L")
    if box: w, h = im.size; im = im.crop((int(box[0] * w), int(box[1] * h), int(box[2] * w), int(box[3] * h)))
    g = np.asarray(ImageOps.autocontrast(ImageOps.fit(im, size, Image.LANCZOS), cutoff=1), np.float32) / 255
    return np.clip((g - ndi.gaussian_filter(g, max(size) / 6)) * 1.8 + .5, 0, 1)


def halftone_rgba(g, cell, ink):
    h, w = g.shape; yy, xx = np.mgrid[0:h, 0:w].astype(np.float32); a = math.radians(25)
    u = xx * math.cos(a) + yy * math.sin(a); t = -xx * math.sin(a) + yy * math.cos(a)
    m = np.hypot((u % cell) - cell / 2, (t % cell) - cell / 2) < cell * .7 * np.sqrt(np.clip(1 - g, 0, 1))
    out = np.zeros((h, w, 4), np.uint8); out[m] = ink + (255,)
    return Image.fromarray(out)


def hexc(c): return "#%02x%02x%02x" % c


def mono(t, x, y, s, c, anchor="start", ls=6):
    return f'<text x="{x}" y="{y}" font-family="Courier 10 Pitch" font-size="{s}" letter-spacing="{ls}" text-anchor="{anchor}" fill="{c}">{t}</text>'


# ------------------------------------------------------------------ designs (return RGBA art for a given ink)
def look_closer(ink):
    c = hexc(ink); body = ""
    size = W * 1.0 / (text("TESTATE", 100, 0, 0)[1] / 100)
    for i in range(7): body += text("TESTATE", size, W / 2, 520 + i * size * .9, anchor="middle", color=c, track=-10)[0]
    art = svg_img(body)
    win = Image.new("L", (W, H), 0); ImageDraw.Draw(win).rounded_rectangle((900, 1300, 2700, 3700), radius=900, fill=255)
    art.paste((0, 0, 0, 0), (0, 0), win)                                 # cut a window out of the type
    ht = halftone_rgba(gray("testate-amoeba-encysting-40x-joy-kaluf", (1800, 2400), (.2, .1, .7, .9)), 26, ink)
    m2 = win.crop((900, 1300, 2700, 3700)); art.paste(ht, (900, 1300), m2)
    art.alpha_composite(svg_img(mono("TESTATE AMOEBA, 400X. STUDENT MICROGRAPH, JOY KALUF", W / 2, 4560, 64, c, "middle")))
    return art


def specimen(ink):
    c = hexc(ink); art = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ht = halftone_rgba(gray("testate-encysted-robert-kenyon", (3000, 3000), (.08, .0, .48, .52)), 30, ink)
    m = Image.new("L", (3000, 3000), 0); ImageDraw.Draw(m).rectangle((0, 0, 3000, 3000), fill=255)
    art.paste(ht, (300, 500), m)
    body = f'<rect x="300" y="500" width="3000" height="3000" fill="none" stroke="{c}" stroke-width="10"/>'
    body += mono("SPECIMEN 01", 300, 3720, 110, c) + mono("TESTATE AMOEBA IN ITS SHELL", 300, 3860, 70, c) + mono("SOIL FOOD WEB SCHOOL / STUDENT MICROGRAPH / R. KENYON", 300, 3960, 54, c)
    body += mono("400X", 3300, 3720, 110, c, "end")
    art.alpha_composite(svg_img(body))
    return art


def index(ink):
    c = hexc(ink); body = ""
    cast = [p for p in cutouts.PICTOS if p[0] != "Mite"][:8]
    cw, ch = 1500, 1000
    for i, (name, fn, _) in enumerate(cast):
        r, k = divmod(i, 2); x = 300 + k * (cw + 0); y = 450 + r * ch
        body += f'<g transform="translate({x + 60},{y + 30}) scale(2.0)"><path d="{cutouts.d_of(fn())}" fill="{c}" fill-rule="evenodd"/></g>'
        body += mono(f"{i + 1:02d}", x + 1000, y + 160, 80, c) + f'<g transform="translate({x + 1000},{y + 900}) rotate(-90)">{mono(name.upper(), 0, 0, 62, c)}</g>'
    body += f'<line x1="300" y1="4500" x2="3300" y2="4500" stroke="{c}" stroke-width="6"/>' + mono("THE SOIL FOOD WEB", 300, 4640, 70, c) + mono("FIELD INDEX", 3300, 4640, 70, c, "end")
    return svg_img(body)


def topo(ink):
    c = hexc(ink)
    g = ndi.gaussian_filter(gray("testate-encysted-robert-kenyon", (700, 800)), 8)
    body = f'<rect x="300" y="300" width="3000" height="3600" fill="none" stroke="{c}" stroke-width="10"/>'
    for lv in np.linspace(.2, .8, 10):
        for cc in measure.find_contours(g, lv):
            if len(cc) < 40: continue
            body += '<path d="M' + "L".join(f"{300 + x * 4.28:.0f},{300 + y * 4.5:.0f}" for y, x in cc[::2]) + f'" fill="none" stroke="{c}" stroke-width="9" stroke-dasharray="40 18" stroke-linecap="round"/>'
    body += mono("SOIL AGGREGATE, TRACED", 300, 4120, 90, c) + mono("FROM A STUDENT MICROGRAPH", 300, 4250, 70, c) + mono("SOIL FOOD WEB", 3300, 4120, 90, c, "end")
    return svg_img(f'<clipPath id="k"><rect x="300" y="300" width="3000" height="3600"/></clipPath><g clip-path="url(#k)">{body[body.index("/>") + 2:body.index("<text")]}</g>' + body[:body.index("/>") + 2] + body[body.index("<text"):])


def four_groups(ink):
    c = hexc(ink); body = ""
    groups = [("PROTOZOA", "amoebae, ciliates, flagellates"), ("FUNGI", "hyphae and spores"), ("NEMATODES", "the small worms"), ("BACTERIA", "the most numerous")]
    for i, (g, d) in enumerate(groups):
        y = 1100 + i * 900
        body += text(g, 560, 300, y, color=c, track=-10)[0]
        body += f'<circle cx="320" cy="{y + 150}" r="22" fill="{c}"/>' + mono(d.upper(), 370, y + 172, 64, c)
    body += mono("SOIL FOOD WEB", 300, 4600, 80, c)
    return svg_img(body)


def wordmark(ink):
    c = hexc(ink); body = text("Soil Food Web", 560, W / 2, 2500, anchor="middle", color=c)[0]
    # a hypha growing up from the top of the W, branching, ending in spores
    rng = np.random.default_rng(4)
    def grow(x, y, a, L, w, d):
        nonlocal body
        pts = []; aa = a
        for k in range(30):
            pts.append((x, y)); aa += rng.normal(0, .05); x += math.cos(aa) * L / 30; y += math.sin(aa) * L / 30
        body += '<path d="M' + "L".join(f"{u:.0f},{v:.0f}" for u, v in pts) + f'" fill="none" stroke="{c}" stroke-width="{w}" stroke-linecap="round"/>'
        if d: [grow(*pts[k], aa + s * rng.uniform(.5, .9), L * .55, w * .7, d - 1) for k, s in ((12, -1), (20, 1))]
        else: body += f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{w * 1.4:.0f}" fill="{c}"/>'
    grow(2560, 2150, -math.pi / 2 - .15, 700, 22, 3)
    body += mono("SCHOOL", W / 2, 2800, 90, c, "middle", 40)
    return svg_img(body)


DESIGNS = {"look-closer": look_closer, "specimen": specimen, "index": index, "topo": topo, "four-groups": four_groups, "wordmark": wordmark}

# ------------------------------------------------------------------ mockups
TEE = [(330, 110), (430, 90), (470, 130), (530, 130), (570, 90), (670, 110), (820, 250), (740, 360), (690, 320), (690, 900), (310, 900), (310, 320), (260, 360), (180, 250)]
TOTE = [(260, 300), (740, 300), (760, 920), (240, 920)]


def flat(shape, colour, art, box, extra=None):
    can = Image.new("RGB", (1000, 1000), (232, 232, 229)); d = ImageDraw.Draw(can)
    d.polygon(shape, fill=colour, outline=(80, 80, 80), width=3)
    if extra: extra(d)
    x0, y0, x1, y1 = box; a = art.copy(); a.thumbnail((x1 - x0, y1 - y0), Image.LANCZOS)
    can.paste(a, (x0 + (x1 - x0 - a.width) // 2, y0), a)
    return can


def main():
    os.makedirs(OUT, exist_ok=True)
    plan = [("look-closer", "tee", (34, 55, 31), (233, 226, 204)), ("specimen", "tee", (20, 20, 20), (179, 190, 177)), ("index", "tote", (233, 226, 204), (34, 55, 31)),
            ("topo", "tote", (20, 20, 20), (179, 190, 177)), ("four-groups", "tee", (233, 226, 204), (34, 55, 31)), ("wordmark", "tee", (179, 190, 177), (34, 55, 31))]
    cells = []
    for name, prod, ground, ink in plan:
        art = DESIGNS[name](ink); art.save(os.path.join(OUT, f"{name}-{'%02x%02x%02x' % ink}.png"), dpi=(300, 300))
        if prod == "tee":
            box = (380, 230, 620, 450) if name == "wordmark" else (360, 200, 640, 820)
            cells.append(flat(TEE, ground, art, box))
        else:
            cells.append(flat(TOTE, ground, art, (300, 340, 700, 880), lambda d: (d.arc((340, 120, 480, 420), 180, 360, fill=(60, 60, 60), width=12), d.arc((520, 120, 660, 420), 180, 360, fill=(60, 60, 60), width=12))))
    sheet = Image.new("RGB", (3 * 1010 + 10, 2 * 1010 + 10), "#fff")
    for i, c in enumerate(cells): sheet.paste(c, (10 + (i % 3) * 1010, 10 + (i // 3) * 1010))
    sheet.save(os.path.join(OUT, "contact.jpg"), quality=90)


if __name__ == "__main__":
    main()
