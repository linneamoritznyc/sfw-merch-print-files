"""Editorial student series: one word repeated in big serif type, an organism abstracted into a few flat grainy shapes.
PROTOZOA (testate amoeba: a dome shell over a lens body), FUNGI (hyphal cells and spores), NEMATODES (a body of
overlapping arcs), BACTERIA (rods and cocci). Lime ground, SFW greens, white.
Outputs out/editorial/notebook-<word>.png (5.75 x 8 in + bleed) and mug-11oz-<word>.png (9 x 3.5 in), 300 dpi.
"""
import io, math, os, sys
import numpy as np
import cairosvg
from PIL import Image
from scipy import ndimage as ndi
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "field-guide"))
from euglypha import text  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "editorial")
LIME, DEEP, FWG, TEAL, WHITE = "#CBDB6C", "#22371F", "#156826", "#1E5B4C", "#FFFFFF"
rng = np.random.default_rng(9)


def render(W, H, body):
    png = cairosvg.svg2png(bytestring=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">{body}</svg>'.encode())
    return Image.open(io.BytesIO(png)).convert("RGBA")


def grainy(layer, amount=.16):
    """Print grain on flat shapes: speckle the alpha a little and darken randomly."""
    a = np.asarray(layer).astype(np.float32)
    n = ndi.gaussian_filter(rng.random(a.shape[:2]).astype(np.float32), .8)
    n = (n - n.mean()) / n.std()
    a[:, :, :3] *= (1 - amount * .5 + amount * .25 * n)[:, :, None]
    a[:, :, 3] *= np.clip(1 - .12 * np.maximum(0, -n), 0, 1)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def words(W, H, word, size, lead, y0, colour, x_overhang=0):
    out = ""
    y = y0
    while y < H + size:
        out += text(word, size, W / 2 + x_overhang, y, anchor="middle", color=colour, track=-10)[0]
        y += size * lead
    return out


# ---------- organisms as flat shapes, each returns svg in a unit box centred on (cx, cy) with scale s
def protozoa(cx, cy, s):
    """Testate amoeba: a dome shell (half disc), a lens of cytoplasm below, the white aperture as a quarter disc."""
    return (f'<path d="M{cx - s},{cy} A{s},{s} 0 0 1 {cx + s},{cy} Z" fill="{TEAL}"/>'
            f'<path d="M{cx - s * .9},{cy + s * .08} Q{cx - s * .05},{cy + s * 1.9} {cx + s * .05},{cy + s * .08} Z" fill="{FWG}"/>'
            f'<path d="M{cx + s * .05},{cy + s * .08} Q{cx + s * .1},{cy + s * 1.15} {cx + s * .9},{cy + s * .08} Z" fill="{WHITE}"/>'
            f'<circle cx="{cx}" cy="{cy - s * .45}" r="{s * .16}" fill="{LIME}"/>')


def fungi(cx, cy, s):
    """A hypha of capsule cells climbing diagonally, branching, with round spores."""
    out = ""
    for i, (x, y, a, col) in enumerate([(-.9, .9, -40, TEAL), (-.35, .35, -40, FWG), (.2, -.2, -40, TEAL), (.75, -.75, -40, FWG), (.15, .55, 25, WHITE), (.7, .25, 25, TEAL)]):
        w, h = s * .7, s * .34
        out += f'<rect x="{cx + x * s - w / 2}" y="{cy + y * s - h / 2}" width="{w}" height="{h}" rx="{h / 2}" fill="{col}" transform="rotate({a} {cx + x * s} {cy + y * s})"/>'
    for x, y, r, col in [(1.15, -1.15, .2, WHITE), (1.45, -1.45, .15, FWG), (1.1, .1, .17, WHITE)]:
        out += f'<circle cx="{cx + x * s}" cy="{cy + y * s}" r="{r * s}" fill="{col}"/>'
    return out


def nematodes(cx, cy, s):
    """A nematode as three overlapping arcs of a thick body, head a white half disc, tail a tapering leaf."""
    return (f'<path d="M{cx - s * 1.3},{cy - s * .2} A{s * .65},{s * .65} 0 0 1 {cx},{cy - s * .2} L{cx - s * .4},{cy - s * .2} A{s * .25},{s * .25} 0 0 0 {cx - s * .9},{cy - s * .2} Z" fill="{TEAL}"/>'
            f'<path d="M{cx},{cy - s * .2} A{s * .65},{s * .65} 0 0 0 {cx + s * 1.3},{cy - s * .2} L{cx + s * .9},{cy - s * .2} A{s * .25},{s * .25} 0 0 1 {cx + s * .4},{cy - s * .2} Z" fill="{FWG}"/>'
            f'<path d="M{cx - s * 1.3},{cy - s * .2} A{s * .2},{s * .2} 0 0 0 {cx - s * .9},{cy - s * .2} Z" fill="{WHITE}"/>'
            f'<path d="M{cx + s * 1.3},{cy - s * .2} Q{cx + s * 1.25},{cy + s * .9} {cx + s * .7},{cy + s * 1.2} Q{cx + s * 1.0},{cy + s * .6} {cx + s * .9},{cy - s * .2} Z" fill="{WHITE}"/>')


def bacteria(cx, cy, s):
    """Rods and cocci, packed like a colony."""
    out = ""
    for x, y, a, col in [(-.6, -.5, 0, TEAL), (.5, -.75, 90, FWG), (-.2, .35, 35, FWG), (.75, .3, -20, TEAL)]:
        w, h = s * .95, s * .38
        out += f'<rect x="{cx + x * s - w / 2}" y="{cy + y * s - h / 2}" width="{w}" height="{h}" rx="{h / 2}" fill="{col}" transform="rotate({a} {cx + x * s} {cy + y * s})"/>'
    for x, y, r, col in [(-.95, .55, .2, WHITE), (-.6, .95, .16, TEAL), (.15, -.2, .18, WHITE), (.2, 1.0, .22, WHITE), (1.15, -.35, .15, FWG)]:
        out += f'<circle cx="{cx + x * s}" cy="{cy + y * s}" r="{r * s}" fill="{col}"/>'
    return out


SERIES = {"PROTOZOA": protozoa, "FUNGI": fungi, "NEMATODES": nematodes, "BACTERIA": bacteria}


def piece(W, H, word, shape, size, lead, cx, cy, s, label_y=None):
    bg = Image.new("RGBA", (W, H), LIME)
    bg.alpha_composite(render(W, H, words(W, H, word, size, lead, size * .78, DEEP)))
    bg.alpha_composite(grainy(render(W, H, shape(cx, cy, s))))
    if label_y:
        bg.alpha_composite(render(W, H, text("SOIL FOOD WEB", 34, W / 2, label_y, fnt="eb-garamond-latin-600-normal.woff2", anchor="middle", color=DEEP, track=260)[0]))
    return bg.convert("RGB")


def fit_size(word, W, frac=1.04):
    w = text(word, 100, 0, 0)[1]
    return 100 * W * frac / w


def main():
    os.makedirs(OUT, exist_ok=True)
    previews = []
    for word, shape in SERIES.items():
        W, H = 1800, 2475
        sz = fit_size(word, W)
        nb = piece(W, H, word, shape, sz, .86, W / 2, H * .47, W * (.42 if word in ('PROTOZOA',) else .36))
        nb.save(os.path.join(OUT, f"notebook-{word.lower()}.png"), dpi=(300, 300))
        MW, MH = 2700, 1050
        msz = fit_size(word, MW / 2, .98)
        half = piece(MW // 2, MH, word, shape, msz, .86, MW / 4, MH * .5, MH * .3)
        back = piece(MW // 2, MH, word, lambda *a: "", msz, .86, 0, 0, 0)
        mug = Image.new("RGB", (MW, MH)); mug.paste(back, (0, 0)); mug.paste(half, (MW // 2, 0))
        mug.save(os.path.join(OUT, f"mug-11oz-{word.lower()}.png"), dpi=(300, 300))
        previews.append((nb, mug))
    sheet = Image.new("RGB", (4 * 470 + 30, 900), "#2A8C7A")
    for i, (nb, mug) in enumerate(previews):
        a = nb.copy(); a.thumbnail((450, 620)); sheet.paste(a, (15 + i * 470, 15))
        b = mug.copy(); b.thumbnail((450, 180)); sheet.paste(b, (15 + i * 470, 680))
    sheet.save(os.path.join(OUT, "contact.jpg"), quality=90)


if __name__ == "__main__":
    main()
