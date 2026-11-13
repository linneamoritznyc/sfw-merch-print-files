"""Archival pieces: quiet, tonal, wrong-scale compositions from real student micrographs.
  fragment     black jacket, one giant nematode cropped off the shoulder and down the sleeve, tonal grey halftone,
               rest of the jacket empty; small stamped specimen tag at the hem
  slide        bone jacket, one tall microscope-slide strip down the back across the seam, typed slide label
  tonal-topo   olive on olive contour lines only on the left sleeve and back hem
  ghost        black jacket, a testate amoeba printed twice, slightly off register, in two near-blacks
Output out/archive/<name>-front.png / -back.png and contact.jpg (flat mockups)
"""
import os, sys
import numpy as np
from PIL import Image, ImageOps, ImageDraw
from scipy import ndimage as ndi
from skimage import measure
sys.argv = sys.argv[:1] if __name__ != "__main__" else sys.argv
import jackets  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "archive")
SRC = os.path.join(jackets.FA, "src")
S = jackets.S


def gray(src, size, box=None):
    im = Image.open(os.path.join(SRC, src + ".jpg")).convert("L")
    if box: w, h = im.size; im = im.crop((int(box[0] * w), int(box[1] * h), int(box[2] * w), int(box[3] * h)))
    g = np.asarray(ImageOps.autocontrast(ImageOps.fit(im, size, Image.LANCZOS), cutoff=1), np.float32) / 255
    return np.clip((g - ndi.gaussian_filter(g, max(size) / 6)) * 1.8 + .5, 0, 1)


def halftone(g, cell, ang=20):
    h, w = g.shape; yy, xx = np.mgrid[0:h, 0:w].astype(np.float32); a = np.radians(ang)
    u = xx * np.cos(a) + yy * np.sin(a); t = -xx * np.sin(a) + yy * np.cos(a)
    return np.hypot((u % cell) - cell / 2, (t % cell) - cell / 2) < cell * .7 * np.sqrt(np.clip(1 - g, 0, 1))


def tag(page, x, y, lines, ink, ground):
    t = "".join(f'<text x="{x + 18}" y="{y + 38 + i * 30}" font-family="Courier 10 Pitch" font-size="24" letter-spacing="3" fill="{ink}">{l}</text>' for i, l in enumerate(lines))
    box = f'<rect x="{x}" y="{y}" width="330" height="{30 * len(lines) + 30}" fill="{ground}" stroke="{ink}" stroke-width="2"/>'
    page.alpha_composite(jackets.svg_img(box + t))


def fragment():
    def art(back):
        page = Image.new("RGBA", (S, S), (20, 21, 20, 255))
        if not back:
            g = gray("nematode-molting-cameron-radman", (2600, 2600), (.05, .0, .6, .55))
            m = halftone(g, 22)
            arr = np.zeros((2600, 2600, 4), np.uint8); arr[m] = (70, 72, 68, 255)
            page.alpha_composite(Image.fromarray(arr).rotate(-38, expand=False).crop((0, 0, 1300, 2400)), (1300, 0))
        tag(page, 1700 if not back else 260, 1930, ["SPECIMEN 014", "NEMATODA", "C. RADMAN, 400X"], "#8A8C86", "#141514")
        return page.convert("RGB")
    return art(False), art(True)


def slide():
    def art(back):
        page = Image.new("RGBA", (S, S), (226, 220, 204, 255))
        if back:
            g = gray("testate-encysting-jimena-fuentes-i2", (520, 1700))
            a = np.empty((1700, 520, 4), np.uint8); a[:] = (226, 220, 204, 255)
            col = np.array([62, 66, 58]); a[..., :3] = (np.array([226, 220, 204]) * g[..., None] + col * (1 - g[..., None])).astype(np.uint8)
            page.alpha_composite(Image.fromarray(a), (940, 330))
            d = ImageDraw.Draw(page); d.rectangle((900, 300, 1500, 2060), outline=(62, 66, 58, 255), width=3)
            tag(page, 1035, 2090, ["SLIDE 07", "TESTATE AMOEBA", "J. FUENTES"], "#3E423A", "#E2DCCC")
        else:
            tag(page, 1340, 560, ["SOIL FOOD WEB", "ARCHIVE"], "#3E423A", "#E2DCCC")
        return page.convert("RGB")
    return art(False), art(True)


def tonal_topo():
    def art(back):
        page = Image.new("RGBA", (S, S), (74, 82, 52, 255))
        g = ndi.gaussian_filter(gray("testate-encysted-robert-kenyon", (600, 600)), 8)
        body = ""
        for lv in np.linspace(.25, .75, 8):
            for c in measure.find_contours(g, lv):
                if len(c) < 40: continue
                pts = c[::2] * 4
                if back: pts = pts * [.35, 1] + [1700, 0]          # band across back hem
                else: pts = pts * [.5, .55] + [0, 1100]           # wearer's left sleeve / lower arm
                body += '<path d="M' + "L".join(f"{x:.0f},{y:.0f}" for y, x in pts) + '" fill="none" stroke="#5E6840" stroke-width="7"/>'
        page.alpha_composite(jackets.svg_img(body))
        if back:
            page = page.convert("RGB"); a = np.asarray(page).copy(); a[:1700] = (74, 82, 52); page = Image.fromarray(a).convert("RGBA")
        return page.convert("RGB")
    return art(False), art(True)


def ghost():
    def art(back):
        page = Image.new("RGBA", (S, S), (16, 16, 16, 255))
        g = gray("testate-encysted-robert-kenyon", (1600, 1600), (.1, .0, .45, .5))
        m = g < np.quantile(g, .3)
        for (dx, dy), c in (((0, 0), (40, 40, 40, 255)), ((18, -12), (56, 54, 50, 255))):
            a = np.zeros((1600, 1600, 4), np.uint8); a[m] = c
            page.alpha_composite(Image.fromarray(a), ((400 if back else 700) + dx, (420 if back else 600) + dy))
        if back: tag(page, 1880, 2080, ["NO. 03"], "#5A5A56", "#101010")
        return page.convert("RGB")
    return art(False), art(True)


PIECES = {"fragment": fragment, "slide": slide, "tonal-topo": tonal_topo, "ghost": ghost}


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for k, fn in PIECES.items():
        f, b = fn(); f.save(os.path.join(OUT, f"{k}-front.png")); b.save(os.path.join(OUT, f"{k}-back.png"))
        r = Image.new("RGB", (1210, 600), (228, 228, 226))
        r.paste(jackets.mock(f, True).resize((600, 600), Image.LANCZOS), (0, 0)); r.paste(jackets.mock(b, False).resize((600, 600), Image.LANCZOS), (610, 0))
        rows.append(r)
    sheet = Image.new("RGB", (2 * 1220 + 10, 2 * 610 + 10), "#fff")
    for i, r in enumerate(rows): sheet.paste(r, (5 + (i % 2) * 1220, 5 + (i // 2) * 610))
    sheet.save(os.path.join(OUT, "contact.jpg"), quality=90)


if __name__ == "__main__":
    main()
