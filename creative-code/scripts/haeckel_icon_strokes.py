"""Clean-stroke vector icon of Haeckel's plate 13, figure 6 (1904, public domain).

Haeckel's lines are reduced to their centrelines, every centreline becomes a smooth curve, and all curves
are stroked at one even weight, like a web icon. The left half is drawn and mirrored, so the icon is exactly
symmetric. The composition is Haeckel's; only the line quality is redrawn.

Usage: python3 haeckel_icon_strokes.py PLATE_JPG
Output: ../patterns/haeckel/icon/haeckel-fan-strokes-*.svg and a preview.
"""
import io, os, sys
import numpy as np
import cv2, cairosvg
from PIL import Image, ImageDraw
from skimage.morphology import skeletonize

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "patterns", "haeckel", "icon")
K = 3840 / 976
BOX = (210, 385, 665, 898)
DEEP, WHITE = "#22371F", "#FFFFFF"
NB = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]


def figure(scan):
    x0, y0, x1, y1 = [int(v * K) for v in BOX]
    g = cv2.cvtColor(scan[y0:y1, x0:x1], cv2.COLOR_BGR2GRAY).astype(np.float32)
    ink = (cv2.GaussianBlur(g, (0, 0), 25) - g) > 20
    nlab, lab, st, _ = cv2.connectedComponentsWithStats(cv2.dilate(ink.astype(np.uint8), np.ones((9, 9))))
    return ink & (lab == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA]))


def axis(ink):
    h, w = ink.shape
    best, bx = -1, w // 2
    for x in range(int(w * .4), int(w * .6)):
        half = min(x, w - x)
        L = ink[:, x - half:x]; R = ink[:, x:x + half][:, ::-1]
        sc = (L & R).sum() / max(1, (L | R).sum())
        if sc > best:
            best, bx = sc, x
    return bx


def chains(skel):
    """Split a 1-px skeleton into pixel chains between endpoints and junctions."""
    sk = skel.copy()
    H, W = sk.shape
    deg = np.zeros_like(sk, np.uint8)
    p = np.pad(sk, 1).astype(np.uint8)
    for dy, dx in NB:
        deg += p[1 + dy:H + 1 + dy, 1 + dx:W + 1 + dx]
    deg = deg * sk
    nodes = sk & (deg != 2)
    visited = np.zeros_like(sk)
    out = []

    def walk(y, x, py, px):
        path = [(y, x)]
        while True:
            visited[y, x] = True
            nxt = None
            for dy, dx in NB:
                ny, nx = y + dy, x + dx
                if 0 <= ny < H and 0 <= nx < W and sk[ny, nx] and (ny, nx) != (py, px) and (ny, nx) != path[0]:
                    if nodes[ny, nx]:
                        path.append((ny, nx)); return path
                    if not visited[ny, nx]:
                        nxt = (ny, nx); break
            if nxt is None:
                return path
            py, px = y, x
            y, x = nxt
            path.append((y, x))

    for y, x in zip(*np.nonzero(nodes)):
        for dy, dx in NB:
            ny, nx = y + dy, x + dx
            if 0 <= ny < H and 0 <= nx < W and sk[ny, nx] and not visited[ny, nx] and not nodes[ny, nx]:
                visited[y, x] = True
                out.append([(y, x)] + walk(ny, nx, y, x))
    for y, x in zip(*np.nonzero(sk & ~visited & ~nodes)):     # closed loops
        if not visited[y, x]:
            out.append(walk(y, x, -1, -1))
    return out


def smooth_d(pts, eps=1.2):
    a = np.array([[x, y] for y, x in pts], np.float32).reshape(-1, 1, 2)
    a = cv2.approxPolyDP(a, eps, False).reshape(-1, 2)
    if len(a) < 2:
        return ""
    if len(a) == 2:
        return f"M{a[0][0]:.1f},{a[0][1]:.1f}L{a[1][0]:.1f},{a[1][1]:.1f}"
    # Catmull-Rom to cubic Bezier
    p = np.vstack([a[0], a, a[-1]])
    s = f"M{a[0][0]:.1f},{a[0][1]:.1f}"
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        c1 = p1 + (p2 - p0) / 6; c2 = p2 - (p3 - p1) / 6
        s += f"C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    return s


WEIGHTS = (1.8, 2.8, 4.2, 6.0)                   # stroke weight steps, in figure px


def build(scan, min_len=24, stroke=2.6):
    ink = figure(scan)
    x = axis(ink)
    half = ink[:, :x]
    m = cv2.morphologyEx(half.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5)))
    m = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 1.8) > 0.40       # smooth the print grain, join gaps
    nlab, lab, st, _ = cv2.connectedComponentsWithStats(m.astype(np.uint8))
    for i in range(1, nlab):
        if st[i, cv2.CC_STAT_AREA] < 60:
            m[lab == i] = False
    sk = skeletonize(m)
    dist = cv2.distanceTransform(m.astype(np.uint8), cv2.DIST_L2, 5)
    paths = [c for c in chains(sk) if len(c) >= min_len]
    groups = {w: [] for w in WEIGHTS}
    for c in paths:
        t = 2 * np.median([dist[y, x] for y, x in c])                   # the drawn line's own thickness
        w = min(WEIGHTS, key=lambda v: abs(v - t))
        d = smooth_d(c, eps=1.6)
        if d:
            groups[w].append(d)
    ds = groups
    ys, xs = np.nonzero(m)
    top, bot, left = ys.min(), ys.max(), xs.min()
    w = 2 * (x - left); h = bot - top
    return ds, x, left, top, w, h, stroke, sum(len(v) for v in ds.values())


def svg(d, x, left, top, w, h, stroke, ink, ground, pad=0.08):
    S = max(w, h) * (1 + 2 * pad)
    ox, oy = (S - w) / 2 - left, (S - h) / 2 - top
    bg = f'<rect width="{S:.0f}" height="{S:.0f}" fill="{ground}"/>' if ground else ""
    k = stroke / 2.6
    paths = ""
    for wt, parts in d.items():
        if not parts:
            continue
        st = f'fill="none" stroke="{ink}" stroke-width="{wt * k:.2f}" stroke-linecap="round" stroke-linejoin="round"'
        dd = "".join(parts)
        # left half as drawn, right half its mirror about the axis x
        paths += f'<path {st} d="{dd}"/><path {st} transform="translate({2 * x},0) scale(-1,1)" d="{dd}"/>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {S:.0f} {S:.0f}">{bg}'
            f'<g transform="translate({ox:.1f},{oy:.1f})">{paths}</g></svg>\n')


def main():
    os.makedirs(OUT, exist_ok=True)
    args = build(cv2.imread(sys.argv[1]))
    d, x, left, top, w, h, stroke, n = args
    for name, ink, ground in (("deep-on-white", DEEP, WHITE), ("white-on-deep", WHITE, DEEP), ("deep-transparent", DEEP, None)):
        open(os.path.join(OUT, f"haeckel-fan-strokes-{name}.svg"), "w").write(svg(d, x, left, top, w, h, stroke, ink, ground))
    s = svg(d, x, left, top, w, h, stroke, WHITE, DEEP)
    full = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=s.encode(), output_width=1200, output_height=1200))).convert("RGB")
    import re
    S = float(re.search(r'viewBox="0 0 (\S+) ', s).group(1))
    x0, y0, zw = S * 0.47, S * 0.20, S * 0.06
    z = s.replace(f'viewBox="0 0 {S:.0f} {S:.0f}"', f'viewBox="{x0:.0f} {y0:.0f} {zw:.0f} {zw:.0f}"', 1)
    zoom = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=z.encode(), output_width=1200, output_height=1200))).convert("RGB")
    sw = svg(d, x, left, top, w, h, stroke * 1.6, DEEP, WHITE)
    smalls = [Image.open(io.BytesIO(cairosvg.svg2png(bytestring=sw.encode(), output_width=p, output_height=p))).convert("RGB") for p in (256, 128, 64)]
    out = Image.new("RGB", (2440, 1200 + 300), "white")
    out.paste(full, (0, 0)); out.paste(zoom, (1240, 0))
    xx = 40
    for sm in smalls:
        out.paste(sm, (xx, 1220 + 256 - sm.height)); xx += sm.width + 40
    ImageDraw.Draw(out).rectangle([x0 * 1200 / S, y0 * 1200 / S, (x0 + zw) * 1200 / S, (y0 + zw) * 1200 / S], outline="#59A66C", width=4)
    out.save(os.path.join(OUT, "haeckel-fan-strokes-preview.png"))
    print("strokes", n, "svg kB", round(len(s) / 1024))


if __name__ == "__main__":
    main()
