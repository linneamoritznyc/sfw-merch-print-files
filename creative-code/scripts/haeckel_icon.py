"""Symmetric vector icon from Haeckel, Kunstformen der Natur (1904), plate 13, figure 6 (public domain).

Haeckel's own lines, cut at full scan resolution, mirrored about the stem axis so the icon is exactly
bilaterally symmetric, cleaned, and traced to one vector path.

Usage: python3 haeckel_icon.py PLATE_JPG
Output: ../patterns/haeckel/icon/
"""
import io, os, sys
import numpy as np
import cv2, cairosvg, potrace
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "patterns", "haeckel", "icon")
K = 3840 / 976
BOX = (210, 385, 665, 898)                       # figure 6 on the 976 px thumbnail
DEEP, WHITE, FWG = "#22371F", "#FFFFFF", "#156826"


def cut(scan):
    x0, y0, x1, y1 = [int(v * K) for v in BOX]
    g = cv2.cvtColor(scan[y0:y1, x0:x1], cv2.COLOR_BGR2GRAY).astype(np.float32)
    paper = cv2.GaussianBlur(g, (0, 0), 25)
    ink = (paper - g) > 20
    nlab, lab, st, _ = cv2.connectedComponentsWithStats(cv2.dilate(ink.astype(np.uint8), np.ones((9, 9))))
    main = lab == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])
    return ink & main


def axis(ink):
    """Column that best mirrors the figure onto itself."""
    h, w = ink.shape
    best, bx = -1, w // 2
    for x in range(int(w * .4), int(w * .6)):
        half = min(x, w - x)
        L = ink[:, x - half:x]; R = ink[:, x:x + half][:, ::-1]
        score = (L & R).sum() / max(1, (L | R).sum())
        if score > best:
            best, bx = score, x
    return bx, best


def symmetric(ink, x, side):
    half = min(x, ink.shape[1] - x)
    part = ink[:, x - half:x] if side == "left" else ink[:, x:x + half][:, ::-1]
    return np.hstack([part, part[:, ::-1]])


def clean(m, sigma=2.6):
    m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((3, 3)))
    m = (cv2.GaussianBlur(m.astype(np.float32), (0, 0), sigma) > 0.5).astype(np.uint8)   # melt the print grain
    nlab, lab, st, _ = cv2.connectedComponentsWithStats(m)
    keep = np.zeros_like(m, bool)
    for i in range(1, nlab):
        if st[i, cv2.CC_STAT_AREA] >= 220:          # drop shading specks: clean icon curves only
            keep |= lab == i
    ys, xs = np.nonzero(keep)
    return keep[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def trace(mask):
    pl = potrace.Bitmap(~mask).trace(turdsize=30, alphamax=1.3, opticurve=True, opttolerance=1.0)
    f = lambda p: f"{p.x:.1f},{p.y:.1f}"
    out = []
    for cv in pl:
        out.append("M" + f(cv.start_point))
        for s in cv.segments:
            out.append(("L" + f(s.c) + "L" + f(s.end_point)) if s.is_corner else
                       ("C" + f(s.c1) + " " + f(s.c2) + " " + f(s.end_point)))
        out.append("Z")
    return "".join(out)


def icon_svg(d, w, h, ink, ground, pad=0.08):
    S = max(w, h) * (1 + 2 * pad)
    ox, oy = (S - w) / 2, (S - h) / 2
    bg = f'<rect width="{S:.0f}" height="{S:.0f}" fill="{ground}"/>' if ground else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {S:.0f} {S:.0f}">{bg}'
            f'<path transform="translate({ox:.1f},{oy:.1f})" d="{d}" fill="{ink}" fill-rule="evenodd"/></svg>\n')


def render(svg, px):
    return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(), output_width=px, output_height=px))).convert("RGBA")


def main():
    Image.MAX_IMAGE_PIXELS = None
    os.makedirs(OUT, exist_ok=True)
    ink = cut(cv2.imread(sys.argv[1]))
    x, score = axis(ink)
    ink2 = cv2.resize(ink.astype(np.uint8) * 255, (ink.shape[1] * 2, ink.shape[0] * 2), interpolation=cv2.INTER_CUBIC) > 127
    x2 = x * 2
    sheet = []
    for side in ("left",):
        m = clean(symmetric(ink2, x2, side))
        d = trace(m)
        h, w = m.shape
        for name, inkc, ground in (("deep-on-white", DEEP, WHITE), ("white-on-deep", WHITE, DEEP), ("deep-transparent", DEEP, None)):
            open(os.path.join(OUT, f"haeckel-fan-icon-{side}-{name}.svg"), "w").write(icon_svg(d, w, h, inkc, ground))
        big = render(icon_svg(d, w, h, WHITE, DEEP), 1000)
        smalls = [render(icon_svg(d, w, h, DEEP, WHITE), s) for s in (256, 128, 64, 32)]
        sheet.append((side, big, smalls))
        print(side, "axis", x, "symmetry before", round(score, 3), "path bytes", len(d))
    # preview: both mirror choices, big and at icon sizes
    side, big, smalls = sheet[0]
    import re
    s = open(os.path.join(OUT, "haeckel-fan-icon-left-white-on-deep.svg")).read()
    S = float(re.search(r'viewBox="0 0 (\S+) ', s).group(1))
    x0, y0, zw = S * 0.47, S * 0.20, S * 0.06
    z = s.replace(f'viewBox="0 0 {S:.0f} {S:.0f}"', f'viewBox="{x0:.0f} {y0:.0f} {zw:.0f} {zw:.0f}"', 1)
    zoom = render(z, 1000)
    out = Image.new("RGB", (2080, 1000 + 80 + 256 + 40), "#FFFFFF")
    out.paste(big.convert("RGB"), (40, 40)); out.paste(zoom.convert("RGB"), (1040, 40))
    xx = 40
    for sm in smalls:
        out.paste(sm.convert("RGB"), (xx, 1080 + (256 - sm.height))); xx += sm.width + 30
    out.save(os.path.join(OUT, "haeckel-fan-icon-preview.png"))


if __name__ == "__main__":
    main()
