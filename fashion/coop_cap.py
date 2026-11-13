"""Vintage co-op cap: arched SOIL FOOD WEB, one big organism in satin stitch, small line below, rope, faded twill.
Outputs out/coop/<name>-embroidery.png (flat, transparent, thread colours) and contact.jpg mockups."""
import io, math, os, sys
import numpy as np
import cairosvg
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage as ndi
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fine-art"))
import cutouts  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "coop")
P = {p[0]: p[1] for p in cutouts.PICTOS}
EW, EH = 1600, 900


def svg(body, w=EW, h=EH):
    return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}">{body}</svg>'.encode()))).convert("RGBA")


def arc_text(t, cx, cy, r, size, colour):
    path = f'<path id="a" d="M{cx - r},{cy} A{r},{r} 0 0 1 {cx + r},{cy}" fill="none"/>'
    return path + f'<text font-family="Liberation Serif" font-weight="bold" font-size="{size}" letter-spacing="6" fill="{colour}"><textPath href="#a" startOffset="50%" text-anchor="middle">{t}</textPath></text>'


def satin(mask, colour, ang, rng):
    """Satin stitch: parallel thread lines across the shape, with sheen."""
    h, w = mask.shape; yy, xx = np.mgrid[0:h, 0:w].astype(np.float32); a = math.radians(ang)
    u = xx * math.cos(a) + yy * math.sin(a)
    sheen = .82 + .18 * np.abs(np.sin(u / 3.2)) + .06 * (rng.random((h, w)) - .5)
    edge = mask & ~ndi.binary_erosion(mask, iterations=3)
    out = np.zeros((h, w, 4), np.float32)
    out[..., :3] = np.array(colour, np.float32) * sheen[..., None]
    out[edge, :3] *= .8
    out[..., 3] = mask * 255
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


def embroidery(org, thread, line):
    rng = np.random.default_rng(1)
    img = Image.new("RGBA", (EW, EH), (0, 0, 0, 0))
    c = "#%02x%02x%02x" % thread
    txt = svg(arc_text("SOIL FOOD WEB", EW / 2, 720, 640, 120, c) + f'<text x="{EW / 2}" y="850" font-family="Liberation Serif" font-weight="bold" font-size="78" letter-spacing="10" text-anchor="middle" fill="{c}">{line}</text>')
    m = np.asarray(txt)[..., 3] > 120
    img.alpha_composite(satin(m, thread, 90, rng))
    o = svg(f'<g transform="translate({EW / 2 - 300},{170}) scale(1.5)"><path d="{cutouts.d_of(P[org]())}" fill="#000" fill-rule="evenodd"/></g>')
    om = np.asarray(o)[..., 3] > 120
    img.alpha_composite(satin(om, thread, 25, rng))
    return img


def cap(fabric, emb, rope):
    W, H = 900, 760
    can = Image.new("RGB", (W, H), (240, 240, 238)); d = ImageDraw.Draw(can)
    crown = [(110, 470), (130, 250), (230, 130), (450, 90), (670, 130), (770, 250), (790, 470)]
    d.polygon(crown, fill=fabric)
    d.ellipse((430, 72, 470, 100), fill=tuple(int(v * .85) for v in fabric))
    brim = [(60, 480), (840, 480), (790, 650), (450, 700), (110, 650)]
    d.polygon(brim, fill=tuple(int(v * .92) for v in fabric))
    for k in range(1, 6):
        d.line([(80 + k * 12, 500 + k * 28), (450, 520 + k * 34), (820 - k * 12, 500 + k * 28)], fill=tuple(int(v * .78) for v in fabric), width=2, joint="curve")
    for x in range(110, 790, 14): d.ellipse((x, 466, x + 16, 482), fill=rope)
    fade = np.asarray(can, np.float32); n = ndi.gaussian_filter(np.random.default_rng(3).random((H, W)), 30)
    fade = fade * (1 + (n - .5)[..., None] * .35)
    can = Image.fromarray(np.clip(fade, 0, 255).astype(np.uint8))
    e = emb.resize((560, 315), Image.LANCZOS); can.paste(e, (170, 170), e)
    return can


def main():
    os.makedirs(OUT, exist_ok=True)
    looks = [("Nematode", "SOIL MICROBE DEPT.", (112, 104, 138), (232, 230, 236), (110, 90, 140)),
             ("Tardigrade", "BELOW GROUND", (60, 78, 52), (226, 220, 196), (40, 55, 35)),
             ("Testate amoeba", "SOIL FOOD WEB SCHOOL", (196, 186, 160), (34, 55, 31), (150, 120, 80)),
             ("Mycorrhizal root", "ROOT EXCHANGE", (34, 42, 60), (203, 219, 108), (60, 70, 90))]
    caps = []
    for org, line, fab, thr, rope in looks:
        e = embroidery(org, thr, line); e.save(os.path.join(OUT, f"{org.lower().replace(' ', '-')}-embroidery.png"))
        caps.append(cap(fab, e, rope))
    sh = Image.new("RGB", (2 * 910 + 10, 2 * 770 + 10), "#fff")
    for i, c in enumerate(caps): sh.paste(c, (10 + (i % 2) * 910, 10 + (i // 2) * 770))
    sh.save(os.path.join(OUT, "contact.jpg"), quality=90)


if __name__ == "__main__":
    main()
