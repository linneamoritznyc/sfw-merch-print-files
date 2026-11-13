"""Idea batch: quick studies in new directions, all from the soil-life cut-outs and student micrographs.
  knit      intarsia sweater: one organism charted in knit stitches on heather yarn
  buti      embroidered motifs: small organisms in a half-drop with a stitched border band
  mosaic    tile phone case: grid of tiles, each an organism on a different green
  patch     woven cap patch: 'Soil Microbe Club' with a tiny soil-profile scene
  stamp     postage stamps: perforated, each a micrograph duotone with a value and name
  label     seed-packet / specimen label with micrograph window
Output out/ideas/*.png + contact.jpg
"""
import io, math, os, sys, glob
import numpy as np
import cairosvg
from PIL import Image, ImageDraw, ImageOps, ImageFilter
from scipy import ndimage as ndi
from shapely import affinity
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "field-guide"))
import cutouts  # noqa: E402
from euglypha import text  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "ideas")
SRC = os.path.join(HERE, "src")
rng = np.random.default_rng(12)
P = {p[0]: p[1] for p in cutouts.PICTOS}


def mask_of(fn, size, pad=.08, rot=0):
    g = fn()
    if rot: g = affinity.rotate(g, rot, origin=(200, 200))
    d = cutouts.d_of(g); s = size * (1 - 2 * pad) / 400
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}"><g transform="translate({size * pad},{size * pad}) scale({s})"><path d="{d}" fill="#000" fill-rule="evenodd"/></g></svg>'
    return np.asarray(Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode()))).convert("RGBA"))[:, :, 3] > 128


def svg_img(body, w, h):
    return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}">{body}</svg>'.encode()))).convert("RGBA")


def knit(name="Tardigrade", yarn=(150, 172, 92), cols=((235, 230, 214), (118, 92, 168), (40, 110, 50))):
    """Intarsia: chart at stitch resolution, each stitch drawn as a V."""
    sw, sh = 60, 80; st = 16
    m = np.zeros((sh, sw), np.uint8)
    big = mask_of(P[name], 46, .02)
    m[18:64, 7:53][big] = 1
    edge = ndi.binary_dilation(m == 1, iterations=1) & (m == 0); m[edge] = 3
    inner = ndi.binary_erosion(m == 1, iterations=4); m[inner & (rng.random(m.shape) < .0) ] = 2
    for y in range(18, 64, 6): m[y, 7:53][m[y, 7:53] == 1] = 2                 # purple stripes like petal shading
    img = Image.new("RGB", (sw * st, sh * st)); d = ImageDraw.Draw(img)
    for y in range(sh):
        for x in range(sw):
            c = yarn if m[y, x] == 0 else cols[m[y, x] - 1]
            c = tuple(int(v + rng.normal(0, 9)) for v in c)
            d.polygon([(x * st, y * st), (x * st + st / 2, y * st + st * .9), (x * st + st / 2, y * st + st * 1.4), (x * st, y * st + st * .5)], fill=c)
            d.polygon([(x * st + st, y * st), (x * st + st / 2, y * st + st * .9), (x * st + st / 2, y * st + st * 1.4), (x * st + st, y * st + st * .5)], fill=tuple(int(v * .9) for v in c))
    return img


def buti(W=960, H=1280, ground="#2F5A2C", thread="#EEE8D6"):
    body = f'<rect width="{W}" height="{H}" fill="{ground}"/>'
    names = ["Testate amoeba", "Fungal hyphae", "Mycorrhizal root", "Ciliate"]
    k = 0
    for r, y in enumerate(range(140, H, 220)):
        for x in range(120 + (110 if r % 2 else 0), W, 220):
            d = cutouts.d_of(P[names[k % 4]]()); k += 1
            body += f'<g transform="translate({x - 60},{y - 60}) scale(.3)"><path d="{d}" fill="none" stroke="{thread}" stroke-width="10" stroke-dasharray="14 7" stroke-linejoin="round"/></g>'
    for yb in (40, H - 70):
        body += f'<rect x="0" y="{yb}" width="{W}" height="30" fill="none" stroke="{thread}" stroke-width="3" stroke-dasharray="8 5"/>'
        for x in range(10, W, 30): body += f'<path d="M{x},{yb + 6} l10,9 l-10,9 l-10,-9 Z" fill="{thread}"/>'
    return svg_img(body, W, H)


def mosaic(W=720, H=1440):
    greens = ["#22371F", "#156826", "#2F5A2C", "#3F6B2A", "#1E5B4C", "#4C6B3A"]
    flowers = ["#E9E4D4", "#CBDB6C", "#D2C2F0", "#C9822E", "#F0A0B0"]
    t = 120; body = ""
    for y in range(0, H, t):
        for x in range(0, W, t):
            body += f'<rect x="{x + 2}" y="{y + 2}" width="{t - 4}" height="{t - 4}" rx="6" fill="{greens[rng.integers(len(greens))]}"/>'
            nm = list(P)[rng.integers(len(P))]
            body += f'<g transform="translate({x + 18},{y + 18}) scale(.21) rotate({rng.integers(-20, 20)} 200 200)"><path d="{cutouts.d_of(P[nm]())}" fill="{flowers[rng.integers(len(flowers))]}" fill-rule="evenodd"/></g>'
    return svg_img(body, W, H)


def patch(W=1100, H=640):
    body = f'<rect x="20" y="20" width="{W - 40}" height="{H - 40}" rx="40" fill="#F1ECDC" stroke="#2F5A2C" stroke-width="10"/>'
    body += f'<rect x="38" y="38" width="{W - 76}" height="{H - 76}" rx="28" fill="none" stroke="#2F5A2C" stroke-width="3" stroke-dasharray="10 6"/>'
    body += text("Soil Microbe", 92, W / 2, 170, anchor="middle", color="#9B1D52")[0] + text("Social Club", 92, W / 2, 262, anchor="middle", color="#9B1D52")[0]
    # tiny soil profile: grass line, horizons, a nematode and hyphae
    body += f'<path d="M140,360 Q{W / 2},330 {W - 140},360 L{W - 140},520 L140,520 Z" fill="#8A6A3A"/>'
    body += f'<path d="M140,360 Q{W / 2},330 {W - 140},360 L{W - 140},400 Q{W / 2},380 140,400 Z" fill="#3F6B2A"/>'
    for x in range(150, W - 140, 22): body += f'<path d="M{x},360 l6,-26 l6,26" fill="#156826"/>'
    body += f'<g transform="translate(250,400) scale(.28)"><path d="{cutouts.d_of(P["Nematode"]())}" fill="#F1ECDC"/></g>'
    body += f'<g transform="translate(620,395) scale(.3)"><path d="{cutouts.d_of(P["Fungal hyphae"]())}" fill="#E3D27A"/></g>'
    body += text("LOOK CLOSER", 26, W / 2, 575, fnt="eb-garamond-latin-600-normal.woff2", anchor="middle", color="#2F5A2C", track=200)[0]
    im = svg_img(body, W, H)
    a = np.asarray(im).astype(np.float32); yy = np.mgrid[0:H, 0:W][0]
    a[:, :, :3] *= (1 - .05 * (yy % 4 < 2))[:, :, None]                    # woven ribs
    return Image.fromarray(a.astype(np.uint8))


def stamps(W=1200, H=900):
    srcs = sorted(glob.glob(os.path.join(SRC, "*.jpg")))
    page = Image.new("RGBA", (W, H), (238, 234, 222, 255))
    pals = [((21, 104, 38), (232, 240, 210)), ((110, 90, 156), (236, 230, 246)), ((176, 90, 40), (246, 236, 220)), ((30, 91, 76), (220, 236, 230))]
    picks = [("NEMATODE", "nematode-molting-cameron-radman"), ("TESTATE", "testate-encysted-robert-kenyon"), ("HYPHA", "fungal-hypha-lee-kirk"), ("MITE", "mite-talbot-armstrong-i3"), ("SPORE", "fungal-spore-josia-martens"), ("AMOEBA", "stellate-amoeba-jimena-fuentes")]
    for i in range(6):
        r, c = divmod(i, 3); x, y = 70 + c * 370, 60 + r * 420; w, h = 320, 380
        st = Image.new("RGBA", (w, h), (255, 255, 255, 255)); d = ImageDraw.Draw(st)
        for k in range(0, w, 16): d.ellipse((k - 6, -6, k + 6, 6), fill=(0, 0, 0, 0)); d.ellipse((k - 6, h - 6, k + 6, h + 6), fill=(0, 0, 0, 0))
        for k in range(0, h, 16): d.ellipse((-6, k - 6, 6, k + 6), fill=(0, 0, 0, 0)); d.ellipse((w - 6, k - 6, w + 6, k + 6), fill=(0, 0, 0, 0))
        g = np.asarray(ImageOps.autocontrast(ImageOps.fit(Image.open(os.path.join(SRC, picks[i][1] + ".jpg")).convert("L"), (w - 50, h - 110)), cutoff=1), np.float32) / 255
        ink, paper = pals[i % 4]
        duo = (np.array(paper) * g[:, :, None] + np.array(ink) * (1 - g[:, :, None])).astype(np.uint8)
        st.paste(Image.fromarray(duo), (25, 25))
        page.alpha_composite(st, (x, y))
        page.alpha_composite(svg_img(text(picks[i][0], 30, x + 25, y + h - 45, fnt="eb-garamond-latin-600-normal.woff2", color="#222", track=120)[0] + text(f"{(i + 1) * 4}", 40, x + w - 30, y + h - 40, anchor="end", color="#222")[0], W, H))
    return page


def seed_packet(W=800, H=1150):
    srcs = sorted(glob.glob(os.path.join(SRC, "*.jpg")))
    page = Image.new("RGBA", (W, H), (233, 226, 204, 255))
    g = np.asarray(ImageOps.autocontrast(ImageOps.fit(Image.open(os.path.join(SRC, "fungal-spores-in-suspension.jpg")).convert("L"), (W - 160, 620)), cutoff=1), np.float32) / 255
    duo = (np.array((233, 226, 204)) * g[:, :, None] + np.array((21, 104, 38)) * (1 - g[:, :, None])).astype(np.uint8)
    win = Image.new("L", (W - 160, 620), 0); ImageDraw.Draw(win).rounded_rectangle((0, 0, W - 161, 619), radius=(W - 160) // 2, fill=255)
    page.paste(Image.fromarray(duo), (80, 200), win)
    body = text("FUNGAL SPORES", 54, W / 2, 120, fnt="eb-garamond-latin-600-normal.woff2", anchor="middle", color="#22371F", track=160)[0]
    body += text("Field notes from the soil", 30, W / 2, 165, anchor="middle", color="#22371F")[0]
    body += f'<line x1="80" y1="870" x2="{W - 80}" y2="870" stroke="#22371F" stroke-width="2"/>'
    for i, t in enumerate(["Fungal spores in a soil extract", "Student micrograph", "Look closer"]):
        body += f'<circle cx="96" cy="{925 + i * 52}" r="7" fill="#9B1D52"/>' + text(t, 32, 116, 936 + i * 52, color="#22371F")[0]
    body += text("SOIL FOOD WEB", 26, W / 2, H - 40, fnt="eb-garamond-latin-600-normal.woff2", anchor="middle", color="#22371F", track=260)[0]
    page.alpha_composite(svg_img(body, W, H))
    return page


def main():
    os.makedirs(OUT, exist_ok=True)
    outs = {"knit-tardigrade": knit(), "knit-mite": knit("Mite", (190, 200, 110), ((240, 236, 222), (90, 140, 200), (34, 55, 31))),
            "buti-embroidery": buti(), "mosaic-phonecase": mosaic(), "patch-social-club": patch(), "stamps": stamps(), "seed-packet": seed_packet()}
    for k, im in outs.items(): im.convert("RGB").save(os.path.join(OUT, k + ".png"))
    th = 560
    tiles = []
    for im in outs.values():
        t = im.convert("RGB"); t = t.resize((int(t.width * th / t.height), th), Image.LANCZOS); tiles.append(t)
    sheet = Image.new("RGB", (sum(t.width for t in tiles) + 12 * (len(tiles) + 1), th + 24), "#e6e6e6"); x = 12
    for t in tiles: sheet.paste(t, (x, 12)); x += t.width + 12
    sheet.save(os.path.join(OUT, "contact.jpg"), quality=90)


if __name__ == "__main__":
    main()
