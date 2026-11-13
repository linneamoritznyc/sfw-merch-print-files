"""Vectorize one figure from a public-domain plate as single-ink line art (like the Haeckel fan).
Usage: python3 trace_plate.py SCAN.jpg x0 y0 x1 y1 NAME   (box in scan pixels)
Writes out/plates/NAME-{white,green,black}.svg and NAME-preview.png (white on deep green).
"""
import io, os, sys
import numpy as np, cv2, cairosvg, potrace
from PIL import Image

src, x0, y0, x1, y1, name = sys.argv[1], *map(int, sys.argv[2:6]), sys.argv[6]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "plates")
im = cv2.imread(src)[y0:y1, x0:x1]
im = cv2.resize(im, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(np.float32)
paper = cv2.GaussianBlur(g, (0, 0), 30)
ink = (paper - g) > 14
ink = cv2.morphologyEx(ink.astype(np.uint8), cv2.MORPH_OPEN, np.ones((2, 2))).astype(bool)
ink = (cv2.GaussianBlur(ink.astype(np.float32), (0, 0), 1.1) > .45)
n, lab, st, _ = cv2.connectedComponentsWithStats(cv2.dilate(ink.astype(np.uint8), np.ones((15, 15))))
keep = np.zeros_like(ink)
big = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])
for i in range(1, n):
    if i == big or st[i, cv2.CC_STAT_AREA] > st[big, cv2.CC_STAT_AREA] * .08:
        keep |= lab == i
ink &= keep
for i, (x, y, w, h, a) in enumerate(cv2.connectedComponentsWithStats(ink.astype(np.uint8))[2][1:], 1):
    pass
pl = potrace.Bitmap(~ink).trace(turdsize=12, alphamax=1.2, opticurve=True, opttolerance=.5)
f = lambda p: f"{p.x:.1f},{p.y:.1f}"
d = []
for c in pl:
    d.append("M" + f(c.start_point))
    for s in c.segments:
        d.append(("L" + f(s.c) + "L" + f(s.end_point)) if s.is_corner else ("C" + f(s.c1) + " " + f(s.c2) + " " + f(s.end_point)))
    d.append("Z")
H, W = ink.shape
pad = int(max(W, H) * .08); S = max(W, H) + 2 * pad
ox, oy = (S - W) / 2, (S - H) / 2
os.makedirs(OUT, exist_ok=True)
svg = lambda ink_c: (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {S} {S}" width="{S}" height="{S}">'
                     f'<path transform="translate({ox:.0f},{oy:.0f})" fill="{ink_c}" fill-rule="evenodd" d="{"".join(d)}"/></svg>\n')
for tag, c in (("white", "#FFFFFF"), ("green", "#156826"), ("black", "#000000")):
    open(os.path.join(OUT, f"{name}-{tag}.svg"), "w").write(svg(c))
png = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg("#FFFFFF").encode(), output_width=1600, output_height=1600))).convert("RGBA")
bg = Image.new("RGBA", png.size, "#22371F"); bg.alpha_composite(png); bg.convert("RGB").save(os.path.join(OUT, f"{name}-preview.png"))
print(name, S)
