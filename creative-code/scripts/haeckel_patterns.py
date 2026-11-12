"""Seamless vector patterns from Haeckel, Kunstformen der Natur (1904), plate 13 Flagellata (public domain,
Library of Congress scan LCCN 2015648900 via Wikimedia Commons). Haeckel's lines are used exactly as drawn:
thresholded to one ink, cut out per figure, traced to vector. Nothing is redrawn.

H1 specimen plate  one-ink figures scattered in a seamless repeat, letter labels in EB Garamond

Usage: python3 haeckel_patterns.py PLATE_JPG
Rules from WORKING-WITH-LINNEA.md: white grounds, no labels, no frames, brand colours only.
"""
import io, math, os, sys
import numpy as np
import cv2, cairosvg, potrace
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "patterns", "haeckel")
PLATES = os.path.join(HERE, "..", "source-plates")
C = {"deep": "#22371F", "brown": "#4F3433", "fwgreen": "#156826", "light": "#59A66C", "white": "#FFFFFF"}
K = 3840 / 976                                              # plate thumbnail -> scan

# figure boxes on the 976 px wide thumbnail of the plate
FIGS = {1: (80, 150, 395, 605), 2: (365, 165, 545, 385), 3: (505, 170, 825, 612), 4: (88, 572, 172, 768),
        5: (676, 606, 812, 752), 6: (210, 385, 665, 898), 7: (78, 1052, 238, 1218), 8: (88, 772, 425, 1218),
        9: (318, 912, 595, 1208), 10: (478, 765, 818, 1212), 11: (648, 1036, 828, 1214)}


def cut(scan, n, max_side=2400):
    x0, y0, x1, y1 = [int(v * K) for v in FIGS[n]]
    crop = scan[y0:y1, x0:x1]
    g = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY).astype(np.float32)
    paper = cv2.GaussianBlur(g, (0, 0), 25)
    ink = (paper - g) > 22                                  # darker than the local paper
    ink = cv2.morphologyEx(ink.astype(np.uint8), cv2.MORPH_OPEN, np.ones((2, 2))).astype(bool)
    # keep the figure: merge strokes, take the biggest group, drop neighbours and plate numbers
    merged = cv2.dilate(ink.astype(np.uint8), np.ones((9, 9)))
    nlab, lab, stats, _ = cv2.connectedComponentsWithStats(merged)
    h, w = merged.shape
    keep = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
    m = lab == keep
    near = cv2.dilate(m.astype(np.uint8), np.ones((61, 61))) > 0
    # small strokes (cilia, flagella) near the figure stay; bits cut by the crop edge go
    for i in range(1, nlab):
        x, y, bw, bh, area = stats[i]
        touches = x == 0 or y == 0 or x + bw >= w or y + bh >= h
        long_thin = max(bw, bh) / max(1, min(bw, bh)) > 2.2      # cilia and flagella; plate numbers are compact
        if i != keep and not touches and area > 40 and long_thin and near[lab == i].any():
            m |= lab == i
    ink &= m
    ys, xs = np.nonzero(ink)
    ink = ink[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    s = min(1.0, max_side / max(ink.shape))
    if s < 1:
        ink = cv2.resize(ink.astype(np.uint8) * 255, (int(ink.shape[1] * s), int(ink.shape[0] * s)),
                         interpolation=cv2.INTER_AREA) > 100
    return ink


def interior(ink):
    """Regions enclosed by Haeckel's lines (not reachable from outside): the bodies to fill flat."""
    closed = cv2.morphologyEx(ink.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5)))
    h, w = closed.shape
    pad = np.pad(closed, 1)
    flood = pad.copy()
    cv2.floodFill(flood, None, (0, 0), 2)
    inside = (flood[1:-1, 1:-1] == 0)
    nlab, lab, stats, _ = cv2.connectedComponentsWithStats(inside.astype(np.uint8))
    big = np.zeros_like(inside)
    for i in range(1, nlab):
        if stats[i, cv2.CC_STAT_AREA] > 60:
            big |= lab == i
    return big


def trace(mask, scale=1.0, ox=0.0, oy=0.0, turd=3):
    pl = potrace.Bitmap(~mask).trace(turdsize=turd, opttolerance=0.25)
    f = lambda p: f"{p.x * scale + ox:.1f},{p.y * scale + oy:.1f}"
    out = []
    for cv in pl:
        out.append("M" + f(cv.start_point))
        for sg in cv.segments:
            out.append(("L" + f(sg.c) + "L" + f(sg.end_point)) if sg.is_corner else
                       ("C" + f(sg.c1) + " " + f(sg.c2) + " " + f(sg.end_point)))
        out.append("Z")
    return "".join(out)


def save(name, svg, T, tiles=3):
    open(os.path.join(OUT, f"{name}-tile.svg"), "w").write(svg)
    tile = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(), output_width=T, output_height=T))).convert("RGB")
    tile.save(os.path.join(OUT, f"{name}-tile.png"), dpi=(300, 300), optimize=True)
    rep = Image.new("RGB", (T * tiles, T * tiles))
    for i in range(tiles):
        for j in range(tiles):
            rep.paste(tile, (i * T, j * T))
    rep.thumbnail((1600, 1600))
    rep.save(os.path.join(OUT, f"{name}-repeat.png"))
    return rep


def wrapped(T, x, y, w, h):
    """Offsets so a motif crossing the tile edge reappears on the other side (seamless)."""
    offs = []
    for dx in (-T, 0, T):
        for dy in (-T, 0, T):
            if x + dx < T and x + dx + w > 0 and y + dy < T and y + dy + h > 0:
                offs.append((dx, dy))
    return offs


def h1_plate(figs, ink_col, ground, name, T=2400):
    # toile: big figures packed close, a few small ones in the gaps (figure, centre x, centre y, height)
    layout = [(6, .25, .27, 1150), (10, .74, .22, 1080), (8, .27, .76, 1080), (3, .76, .72, 1000),
              (11, .51, .50, 330), (5, .99, .47, 300), (7, .51, .99, 300), (4, .02, .02, 300)]
    body = [f'<rect width="{T}" height="{T}" fill="{C[ground]}"/>']
    letters = "ABCDEFGHIJK"
    for k, (n, fx, fy, hgt) in enumerate(layout):
        ink = figs[n]["ink"]
        s = hgt / ink.shape[0]
        w, h = ink.shape[1] * s, hgt
        x, y = fx * T - w / 2, (fy % 1) * T - h / 2
        d = figs[n]["d_ink"]
        for dx, dy in wrapped(T, x, y, w, h):
            body.append(f'<path transform="translate({x + dx:.1f},{y + dy:.1f}) scale({s / figs[n]["sc"]:.4f})" d="{d}" fill="{C[ink_col]}"/>')
    return save(name, f'<svg xmlns="http://www.w3.org/2000/svg" width="{T}" height="{T}" viewBox="0 0 {T} {T}">\n' + "\n".join(body) + "\n</svg>\n", T)


def h2_filled(figs, name, T=3000):
    body = [f'<rect width="{T}" height="{T}" fill="{C["white"]}"/>']
    order = [3, 6, 10, 8, 1, 9, 11, 5]
    R = T * 0.19
    centres = [(T * (i + .5) / 2, T * (j + .5) / 2 + (T / 4 if i % 2 else 0)) for i in range(2) for j in range(2)]
    centres += [(cx + T / 4, (cy + T / 4) % T) for cx, cy in centres]           # second, offset layer
    fills = ["light", "cream", "light", "cream"]
    for k, (cx, cy) in enumerate(centres):
        n = order[k % len(order)]
        f = figs[n]
        s = (R * 1.45) / max(f["ink"].shape)
        w, h = f["ink"].shape[1] * s, f["ink"].shape[0] * s
        for dx, dy in wrapped(T, cx - R, cy - R, 2 * R, 2 * R):
            tf = f'translate({cx + dx - w / 2:.1f},{cy + dy - h / 2:.1f}) scale({s / f["sc"]:.4f})'
            body.append(f'<path transform="{tf}" d="{f["d_fill"]}" fill="{C["light"]}" fill-rule="evenodd"/>')
            body.append(f'<path transform="{tf}" d="{f["d_ink"]}" fill="{C["deep"]}"/>')
    return save(name, f'<svg xmlns="http://www.w3.org/2000/svg" width="{T}" height="{T}" viewBox="0 0 {T} {T}">\n' + "\n".join(body) + "\n</svg>\n", T)


def patch(figs, ink_col, ground, name, W=3000, logo_frac=0.40, T=1000):
    """Toile over a square panel with whole figures cleared from a centre patch and the white flower logo there."""
    layout = [(6, .25, .27, 1150), (10, .74, .22, 1080), (8, .27, .76, 1080), (3, .76, .72, 1000),
              (11, .51, .50, 330), (5, .99, .47, 300), (7, .51, .99, 300), (4, .02, .02, 300)]
    k = T / 2400
    body = [f'<rect width="{W}" height="{W}" fill="{C[ground]}"/>']
    R = W * logo_frac * 0.47
    c = W / 2
    for ox in range(-T, W + T, T):
        for oy in range(-T, W + T, T):
            for n, fx, fy, hgt in layout:
                f = figs[n]
                h = hgt * k; s = h / f["ink"].shape[0]; w = f["ink"].shape[1] * s
                x, y = ox + fx * T - w / 2, oy + fy * T - h / 2
                if x > W or y > W or x + w < 0 or y + h < 0:
                    continue
                # nearest point of the figure box to the centre: drop the whole figure if it reaches the patch
                nx, ny = min(max(c, x), x + w), min(max(c, y), y + h)
                if math.hypot(nx - c, ny - c) < R:
                    continue
                body.append(f'<path transform="translate({x:.1f},{y:.1f}) scale({s:.4f})" d="{f["d_ink"]}" fill="{C[ink_col]}"/>')
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{W}" viewBox="0 0 {W} {W}">\n' + "\n".join(body) + "\n</svg>\n"
    open(os.path.join(OUT, f"{name}.svg"), "w").write(svg)
    im = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(), output_width=W, output_height=W))).convert("RGBA")
    logo = Image.open(os.path.join(HERE, "..", "logos", "SFW-logo-flower-white-3000.png")).convert("RGBA")
    ls = int(W * logo_frac); logo = logo.resize((ls, ls), Image.LANCZOS)
    im.alpha_composite(logo, ((W - ls) // 2, (W - ls) // 2))
    im.convert("RGB").save(os.path.join(OUT, f"{name}.png"), dpi=(300, 300), optimize=True)
    return im.convert("RGB")


def main():
    Image.MAX_IMAGE_PIXELS = None
    scan = cv2.imread(sys.argv[1])
    os.makedirs(OUT, exist_ok=True); os.makedirs(PLATES, exist_ok=True)
    figs = {}
    for n in FIGS:
        ink = cut(scan, n)
        fill = interior(ink) & ~ink
        figs[n] = {"ink": ink, "sc": 1.0, "d_ink": trace(ink), "d_fill": trace(fill)}
        # one-ink transparent PNG of each figure, exactly as drawn
        a = (ink * 255).astype(np.uint8)
        rgba = np.dstack([np.full_like(a, 0x22), np.full_like(a, 0x37), np.full_like(a, 0x1F), a])
        Image.fromarray(rgba).save(os.path.join(PLATES, f"haeckel-1904-plate13-fig{n:02d}.png"))
    pt = patch(figs, "white", "deep", "h1-haeckel-toile-patch-logo-white-on-deep")
    t = pt.copy(); t.thumbnail((1200, 1200)); t.save(os.path.join(OUT, "h1-haeckel-toile-patch-logo-preview.png"))
    reps = [h1_plate(figs, "deep", "white", "h1-haeckel-toile-deep-on-white"),
            h1_plate(figs, "white", "deep", "h1-haeckel-toile-white-on-deep"),
            h1_plate(figs, "fwgreen", "white", "h1-haeckel-toile-fwgreen-on-white")]
    th, pad = 640, 24
    sheet = Image.new("RGB", (3 * th + 4 * pad, th + 2 * pad), "#FFFFFF")
    for k, r in enumerate(reps):
        t = r.copy(); t.thumbnail((th, th)); sheet.paste(t, (pad + k * (th + pad), pad))
    sheet.save(os.path.join(OUT, "haeckel-sheet.png"))


if __name__ == "__main__":
    main()
