"""Knit soil life: every SFW cut-out organism charted in knit stitches.
Each organism: a knit swatch (portrait) and a patch (square, stitched border, transparent outside), 4 thread
colours each so they work as embroidered patches. Output out/knit/<slug>-swatch.png, <slug>-patch.png, contact.jpg
"""
import io, os, sys
import numpy as np
import cairosvg
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from shapely import affinity
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cutouts  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "knit")
ST = 24  # px per stitch
YARNS = {  # ground, body, stripe, outline
    "Testate amoeba": ((203, 219, 108), (236, 230, 214), (118, 92, 168), (34, 55, 31)),
    "Nematode": ((150, 172, 92), (240, 236, 222), (196, 90, 130), (34, 55, 31)),
    "Fungal hyphae": ((118, 92, 168), (230, 210, 120), (240, 236, 222), (34, 30, 45)),
    "Mite": ((190, 200, 110), (240, 236, 222), (90, 140, 200), (34, 55, 31)),
    "Springtail": ((89, 166, 108), (240, 236, 222), (210, 160, 70), (22, 40, 26)),
    "Tardigrade": ((150, 172, 92), (235, 230, 214), (118, 92, 168), (40, 110, 50)),
    "Ciliate": ((60, 90, 150), (230, 230, 150), (240, 236, 222), (20, 30, 50)),
    "Bacteria": ((240, 228, 200), (160, 60, 100), (240, 236, 222), (60, 30, 40)),
    "Mycorrhizal root": ((110, 80, 60), (158, 217, 181), (240, 236, 222), (40, 30, 20)),
}


def chart(fn, sw, sh, box):
    """Rasterise the organism to a stitch grid. box = (x0, y0, size) in stitches."""
    x0, y0, s = box
    d = cutouts.d_of(fn())
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{sw}" height="{sh}"><g transform="translate({x0},{y0}) scale({s / 400})"><path d="{d}" fill="#000" fill-rule="evenodd"/></g></svg>'
    a = np.asarray(Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(), output_width=sw * 4, output_height=sh * 4))).convert("RGBA"))[:, :, 3]
    a = a.reshape(sh, 4, sw, 4).mean((1, 3)) > 100
    m = np.zeros((sh, sw), np.uint8)
    m[a] = 1
    stripe_rows = (np.arange(sh) % 6 == 3)[:, None] & a
    m[stripe_rows] = 2
    m[ndi.binary_dilation(a, iterations=1) & ~a] = 3
    return m


def render(m, cols, rng, alpha_mask=None):
    sh, sw = m.shape
    img = Image.new("RGBA", (sw * ST, sh * ST), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    for y in range(sh):
        for x in range(sw):
            if alpha_mask is not None and not alpha_mask[y, x]: continue
            c = cols[m[y, x]]
            c = tuple(int(np.clip(v + rng.normal(0, 8), 0, 255)) for v in c)
            dk = tuple(int(v * .82) for v in c)
            X, Y = x * ST, y * ST
            d.rectangle((X, Y, X + ST, Y + ST), fill=tuple(int(v * .6) for v in c) + (255,))
            d.polygon([(X + 1, Y), (X + ST / 2, Y + ST * .55), (X + ST / 2, Y + ST * 1.05), (X + 1, Y + ST * .5)], fill=c + (255,))
            d.polygon([(X + ST - 1, Y), (X + ST / 2, Y + ST * .55), (X + ST / 2, Y + ST * 1.05), (X + ST - 1, Y + ST * .5)], fill=dk + (255,))
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    rng = np.random.default_rng(3)
    thumbs = []
    for name, fn, _ in cutouts.PICTOS:
        g, body, stripe, line = YARNS[name]
        slug = name.lower().replace(" ", "-")
        cols = [g, body, stripe, line]
        sw = render(chart(fn, 48, 64, (4, 12, 40)), cols, rng)
        sw.convert("RGB").save(os.path.join(OUT, f"{slug}-swatch.png"), dpi=(300, 300))
        # patch: square, rounded, two-stitch border in outline colour, transparent outside
        N = 48
        m = chart(fn, N, N, (5, 5, 38))
        yy, xx = np.mgrid[0:N, 0:N]
        r = 8
        inside = np.ones((N, N), bool)
        for cy, cx in ((r, r), (r, N - 1 - r), (N - 1 - r, r), (N - 1 - r, N - 1 - r)):
            corner = ((yy < r) if cy == r else (yy > N - 1 - r)) & ((xx < r) if cx == r else (xx > N - 1 - r))
            inside &= ~(corner & ((yy - cy) ** 2 + (xx - cx) ** 2 > r * r))
        border = inside & ~ndi.binary_erosion(inside, iterations=2)
        m[border] = 3
        pt = render(m, cols, rng, inside)
        pt.save(os.path.join(OUT, f"{slug}-patch.png"), dpi=(300, 300))
        flat = np.zeros((N, N, 4), np.uint8); flat[..., :3] = np.array(cols, np.uint8)[m]; flat[..., 3] = inside * 255
        Image.fromarray(flat).resize((N * ST, N * ST), Image.NEAREST).save(os.path.join(OUT, f"{slug}-patch-flat.png"), dpi=(300, 300))
        thumbs.append((sw, pt))
    cw = 300
    sheet = Image.new("RGB", (9 * (cw + 12) + 12, 400 + cw + 36), "#e8e8e8")
    for i, (sw, pt) in enumerate(thumbs):
        sheet.paste(sw.convert("RGB").resize((cw, 400), Image.LANCZOS), (12 + i * (cw + 12), 12))
        p = pt.resize((cw, cw), Image.LANCZOS); sheet.paste(p, (12 + i * (cw + 12), 424), p)
    sheet.save(os.path.join(OUT, "contact.jpg"), quality=90)


if __name__ == "__main__":
    main()
