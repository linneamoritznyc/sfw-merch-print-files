"""One-ink 'field notes' back print: scattered boxes of thresholded student micrographs, a dashed hyphal network
growing through them, a cut-out organism, a serif word, a factual caption. Distressed ink. Shown on washed tees."""
import io, math, os, sys
import numpy as np
import cairosvg
from PIL import Image, ImageOps, ImageDraw
from scipy import ndimage as ndi
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fine-art"))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "field-guide"))
import cutouts  # noqa: E402
from euglypha import text  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "fine-art", "src")
OUT = os.path.join(HERE, "out", "fieldnotes")
W, H = 3000, 3600


def svg_mask(body):
    a = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">{body}</svg>'.encode()))).convert("RGBA")
    return np.asarray(a)[..., 3] > 100


def thresh(src, w, h, q=.45):
    g = np.asarray(ImageOps.autocontrast(ImageOps.fit(Image.open(os.path.join(SRC, src + ".jpg")).convert("L"), (w, h)), cutoff=1), np.float32) / 255
    g = ndi.gaussian_filter(g - ndi.gaussian_filter(g, w / 6), 1.2)
    return g < np.quantile(g, q)


def art(seed, word, caption, picks):
    rng = np.random.default_rng(seed); M = np.zeros((H, W), bool)
    boxes = [(260, 380, 900, 640), (1900, 300, 760, 1100), (1950, 2050, 760, 560)]
    for (x, y, w, h), src in zip(boxes, picks):
        t = thresh(src, w, h); M[y:y + h, x:x + w] |= ~t if rng.random() < .5 else t
        M[y:y + 8, x:x + w] = M[y + h - 8:y + h, x:x + w] = True; M[y:y + h, x:x + 8] = M[y:y + h, x + w - 8:x + w] = True
    body = ""
    def grow(x, y, a, L, d):
        nonlocal body
        pts = []
        for k in range(40):
            pts.append((x, y)); a += rng.normal(0, .06); x += math.cos(a) * L / 40; y += math.sin(a) * L / 40
        body += '<path d="M' + "L".join(f"{u:.0f},{v:.0f}" for u, v in pts) + f'" fill="none" stroke="#000" stroke-width="{8 + d * 4}" stroke-dasharray="{40 + d * 10} 26" stroke-linecap="round"/>'
        if d: [grow(*pts[k], a + s * rng.uniform(.5, .9), L * .6, d - 1) for k, s in ((15, -1), (26, 1))]
        else: body += f'<circle cx="{x:.0f}" cy="{y:.0f}" r="16" fill="#000"/>'
    grow(1500, 3150, -math.pi / 2, 1300, 3)
    body += f'<g transform="translate(330,1400) scale(1.6)"><path d="{cutouts.d_of(cutouts.testate())}" fill="#000"/></g>'
    body += text(word, 300, 260, 1250, color="#000")[0]
    for i, l in enumerate(caption):
        body += f'<text x="260" y="{2900 + i * 64}" font-family="Courier 10 Pitch" font-size="54" fill="#000">{l}</text>'
    body += f'<text x="2710" y="3450" font-family="Courier 10 Pitch" font-size="48" letter-spacing="10" text-anchor="end" fill="#000">SOIL FOOD WEB</text>'
    M |= svg_mask(body)
    # distress: knock out speckles and a few worn patches
    wear = ndi.gaussian_filter(rng.random((H, W)), 1.0)
    patch = ndi.gaussian_filter(rng.random((H // 10, W // 10)), 3).repeat(10, 0).repeat(10, 1)[:H, :W]
    M &= (wear > .22) & (patch < np.quantile(patch, .985))
    return M


def main():
    os.makedirs(OUT, exist_ok=True)
    looks = [(1, "Hyphae", ["Fungal hyphae are thread-like filaments.", "Together they form the mycelium,", "the main body of a fungus."],
              ["fungal-hypha-lee-kirk", "testate-encysting-jimena-fuentes-i2", "fungal-spore-josia-martens"], (98, 82, 74), (232, 222, 200)),
             (2, "Protozoa", ["Single-celled organisms that graze", "on bacteria in the soil."],
              ["stellate-amoeba-jimena-fuentes", "testate-encysted-robert-kenyon", "testate-amoeba-encysting-40x-joy-kaluf"], (70, 82, 60), (232, 226, 204)),
             (3, "Nematodes", ["Microscopic roundworms.", "Some eat bacteria, some eat fungi."],
              ["nematode-molting-cameron-radman", "mite-talbot-armstrong-i3", "testate-encysted-sid-jensen"], (30, 30, 30), (210, 220, 200))]
    sheet = Image.new("RGB", (3 * 910 + 10, 1110), (226, 228, 226))
    for i, (seed, word, cap, picks, shirt, ink) in enumerate(looks):
        M = art(seed, word, cap, picks)
        rgba = np.zeros((H, W, 4), np.uint8); rgba[M] = ink + (255,)
        Image.fromarray(rgba).save(os.path.join(OUT, f"back-{word.lower()}.png"), dpi=(300, 300))
        tee = Image.new("RGB", (900, 1100), (226, 228, 226)); d = ImageDraw.Draw(tee)
        poly = [(300, 60), (380, 40), (450, 75), (520, 40), (600, 60), (820, 200), (740, 360), (690, 320), (690, 1080), (210, 1080), (210, 320), (160, 360), (80, 200)]
        d.polygon(poly, fill=shirt)
        wash = (np.asarray(tee, np.float32) * (1 + (ndi.gaussian_filter(np.random.default_rng(i).random((1100, 900)), 18) - .5)[..., None] * .5))
        tee = Image.fromarray(np.clip(wash, 0, 255).astype(np.uint8))
        a = Image.fromarray(rgba).resize((400, 480), Image.LANCZOS); tee.paste(a, (250, 200), a)
        ImageDraw.Draw(tee).polygon(poly, outline=(80, 80, 80), width=3)
        sheet.paste(tee, (10 + i * 910, 5))
    sheet.save(os.path.join(OUT, "contact.jpg"), quality=90)


if __name__ == "__main__":
    main()
