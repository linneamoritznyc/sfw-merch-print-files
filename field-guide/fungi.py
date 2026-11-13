"""SFW Field Guide, page 3: fungal hyphae. A4, vector, text as outlines.

SFW's own drawing, constructed in code. Content follows standard mycology:
  hyphae are tubes of even width (about 2 to 10 µm) that grow at the tip and branch; septate hyphae have cross
  walls (septa); aseptate hyphae (Mucoromycota, arbuscular mycorrhizal fungi) have none; clamp connections at the
  septa mark Basidiomycota; hyphae are clear (hyaline) or brown (pigmented).
  Look-alikes, drawn at the same scale: actinobacteria (filaments about 1 µm, much thinner), root hairs (single
  cells growing out of a root, about 10 µm or wider, unbranched).
DRAFT until an SFW mentor has checked it.

Usage: python3 fungi.py  ->  out/fungi-field-guide.svg / .png / -preview.png
"""
import io, math, os
import numpy as np
import cairosvg
from PIL import Image
from shapely.geometry import LineString, Polygon
from shapely.ops import unary_union
from euglypha import text, para, d_of, label, DEEP, FWG, LIGHT, WHITE, W, H, HERE, OUT

BROWN = "#4F3433"
LW = 3.2
G6 = "eb-garamond-latin-600-normal.woff2"


def smooth(ctrl, n=120):
    p = np.asarray(ctrl, float)
    q = np.vstack([2 * p[0] - p[1], p, 2 * p[-1] - p[-2]])
    out = []
    for i in range(len(q) - 3):
        p0, p1, p2, p3 = q[i:i + 4]
        for t in np.linspace(0, 1, max(4, n // (len(q) - 3)), endpoint=False):
            out.append(0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(q[-2])
    return np.array(out)


def rings(geom):
    gs = getattr(geom, "geoms", [geom])
    d = ""
    for g in gs:
        d += d_of(np.array(g.exterior.coords)[:-1], True)
        for r in g.interiors:
            d += d_of(np.array(r.coords)[:-1], True)
    return d


def tube_net(lines, width, fill=WHITE, stroke=DEEP, septa=True, step=None, w=LW, clamps=False):
    """Hyphae as one joined tube network. lines: list of centreline point arrays."""
    shape = unary_union([LineString(l).buffer(width / 2, 24) for l in lines])
    out = [f'<path d="{rings(shape)}" fill="{fill}" stroke="{stroke}" stroke-width="{w * 1.3:.2f}" stroke-linejoin="round" fill-rule="evenodd"/>']
    marks = []
    if septa:
        step = step or width * 4.5
        for l in lines:
            ln = LineString(l)
            for s in np.arange(step, ln.length - width * 1.2, step):
                p = np.array(ln.interpolate(s).coords[0]); q = np.array(ln.interpolate(s + 1).coords[0])
                t = (q - p) / np.linalg.norm(q - p); n = np.array([-t[1], t[0]])
                a, b = p - n * width * 0.48, p + n * width * 0.48
                out.append(f'<path d="M{a[0]:.1f},{a[1]:.1f}L{b[0]:.1f},{b[1]:.1f}" stroke="{stroke}" stroke-width="{w:.2f}"/>')
                marks.append((p, t, n))
                if clamps:
                    out.append(clamp(p, t, n, width, stroke, w))
    return "".join(out), shape, marks


def clamp(p, t, n, width, stroke=DEEP, w=LW):
    """Clamp connection: a small hook on one side that bridges the septum."""
    a = p - t * width * 0.55 + n * width * 0.5
    b = p + t * width * 0.55 + n * width * 0.5
    c1 = a + n * width * 0.55 - t * width * 0.05
    c2 = b + n * width * 0.55 + t * width * 0.05
    return (f'<path d="M{a[0]:.1f},{a[1]:.1f}C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {b[0]:.1f},{b[1]:.1f}" '
            f'fill="{WHITE}" stroke="{stroke}" stroke-width="{w * 1.2:.2f}"/>')


def network():
    """Drawing A: a branching septate hypha with tips, as seen in a soil sample."""
    main = smooth([(200, 1180), (560, 1060), (950, 1010), (1350, 930), (1760, 900), (2280, 760)])
    b1 = smooth([(560, 1060), (640, 900), (700, 760), (760, 690)])
    b2 = smooth([(950, 1010), (1050, 1130), (1180, 1230), (1300, 1280)])
    b3 = smooth([(1350, 930), (1420, 800), (1520, 720), (1600, 690)])
    b4 = smooth([(1760, 900), (1880, 1010), (2000, 1080), (2080, 1100)])
    b5 = smooth([(700, 760), (800, 760), (900, 790)])
    svg, shape, marks = tube_net([main, b1, b2, b3, b4, b5], 44, step=190)
    pts = {"tip": (b3[-1] + (b3[-1] - b3[-4]) / np.linalg.norm(b3[-1] - b3[-4]) * 22),
           "septum": marks[0][0] + marks[0][2] * 22, "branch": np.array([1350, 930]) + np.array([24, -30]),
           "wall": main[25] + np.array([0, 22])}
    return svg, pts


def close_up(cx, cy, length, width, kind):
    """Drawing B panels, horizontal tube segments, same scale."""
    l = np.array([(cx - length / 2, cy), (cx + length / 2, cy)])
    if kind == "septate":
        return tube_net([l], width, step=length / 4)[0]
    if kind == "aseptate":
        return tube_net([l], width, septa=False)[0]
    if kind == "clamp":
        return tube_net([l], width, step=length / 4, clamps=True)[0]
    if kind == "pigmented":
        s, shape, _ = tube_net([l], width, fill=BROWN, stroke=DEEP, step=length / 4)
        # septa show light against the dark wall
        out = f'<path d="{rings(shape)}" fill="{BROWN}" stroke="{DEEP}" stroke-width="{LW * 1.3:.2f}"/>'
        for k in (1, 2, 3):
            x = cx - length / 2 + k * length / 4
            out += f'<path d="M{x:.1f},{cy - width * .45:.1f}L{x:.1f},{cy + width * .45:.1f}" stroke="{WHITE}" stroke-width="{LW:.2f}"/>'
        return out


def page():
    M = 170
    body = [f'<rect width="{W}" height="{H}" fill="{WHITE}"/>']
    body.append(text("SOIL FOOD WEB FIELD GUIDE", 34, M, 230, fnt=G6, track=180, color=FWG)[0])
    body.append(text("No. 3", 34, W - M, 230, fnt=G6, anchor="end", track=120, color=FWG)[0])
    body.append(text("Fungal hyphae", 150, M - 4, 410)[0])
    body.append(text("The threads that hold soil together", 58, M, 510)[0])
    body.append(text("Fungi  ·  hyphae are the feeding threads, a network of them is mycelium", 40, M, 580, color=FWG)[0])
    # A network
    a, p = network()
    body.append(a)
    body += [label(p["tip"], 1720, 640, ["Growing tip"], side="right"),
             label(p["septum"], 200, 1330, ["Cross wall (septum)"], side="right"),
             label(p["branch"], 1180, 760, ["Branch"], side="left"),
             label(p["wall"], 760, 1330, ["Even width along the whole thread"], side="right")]
    body.append(text("A  A septate hypha, branching, about 400x", 40, W / 2, 1460, anchor="middle", fnt=G6)[0])
    # B close-ups, all the same width
    y = 1640; w_ = 84; L_ = 1000
    panels = [("septate", "Septate", ["Cross walls at intervals.", "Most soil fungi."]),
              ("aseptate", "Aseptate", ["No cross walls. Arbuscular", "mycorrhizal fungi, Mucor."]),
              ("clamp", "Clamp connection", ["A hook over each cross wall.", "Basidiomycetes."]),
              ("pigmented", "Brown (pigmented)", ["Dark wall, often older or", "decay-resistant hyphae."])]
    for i, (kind, title, lines) in enumerate(panels):
        cx = M + L_ / 2 + 10
        cy = y + i * 175
        body.append(close_up(cx, cy, L_, w_, kind))
        body.append(text(title, 40, M + L_ + 110, cy - 14, fnt=G6, color=FWG)[0])
        body.append(text(" ".join(lines), 34, M + L_ + 110, cy + 36)[0])
    body.append(text("B  Four kinds to tell apart", 40, W / 2, 2330, anchor="middle", fnt=G6)[0])
    # C look-alikes at one scale: 1 µm = 9 px
    um = 9.0
    yc = 2530
    x0 = M
    items = [("Actinobacteria", 1.0, "About 1 µm. Much thinner,", "branches at sharp angles."),
             ("Fungal hypha", 5.0, "About 2 to 10 µm. Even width,", "cross walls or none."),
             ("Root hair", 12.0, "About 10 µm or wider. Grows", "out of a root, no branches.")]
    for i, (name, wum, l1, l2) in enumerate(items):
        yy = yc + i * 165
        wpx = wum * um
        if name == "Root hair":
            body.append(tube_net([np.array([(x0 + 90, yy), (x0 + 780, yy)])], wpx, septa=False)[0])
            body.append(f'<rect x="{x0:.1f}" y="{yy - 75:.1f}" width="110" height="150" rx="18" fill="{LIGHT}" stroke="{FWG}" stroke-width="{LW:.2f}"/>')
            body.append(text("root", 30, x0 + 55, yy + 10, anchor="middle", color=WHITE)[0])
        elif name == "Actinobacteria":
            body.append(tube_net([np.array([(x0, yy), (x0 + 780, yy)]), np.array([(x0 + 300, yy), (x0 + 380, yy - 50)]),
                                  np.array([(x0 + 560, yy), (x0 + 650, yy + 45)])], max(wpx, 6), septa=False, w=2.6)[0])
        else:
            body.append(tube_net([np.array([(x0, yy), (x0 + 780, yy)])], wpx, step=180)[0])
        body.append(text(name, 36, x0 + 870, yy - 8, fnt=G6, color=FWG)[0])
        body.append(text(l1 + " " + l2, 32, x0 + 870, yy + 38)[0])
    body.append(f'<rect x="{x0 + 690:.1f}" y="{yc + 470:.1f}" width="{10 * um:.1f}" height="10" fill="{DEEP}"/>')
    body.append(text("10 µm", 32, x0 + 690 + 5 * um, yc + 455, anchor="middle")[0])
    body.append(text("C  Easy to mix up: all three at the same size", 40, W / 2, yc + 570, anchor="middle", fnt=G6)[0])
    # facts
    fy, fs = 3200, 34
    facts = [("Eats", "Dead plant material, even tough lignin and cellulose. Mycorrhizal fungi get sugars from roots."),
             ("Role", "Binds soil crumbs together, holds nutrients in the soil, and reaches water and nutrients for roots."),
             ("At 400x", "Look for an even-width tube with cross walls or none. Measure the width against a bacterium.")]
    for k, (h_, t_) in enumerate(facts):
        body.append(text(h_, fs, M, fy + k * fs * 1.6, fnt=G6, color=FWG)[0])
        body.append(text(t_, fs, M + 190, fy + k * fs * 1.6)[0])
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n' + "\n".join(body) + "\n</svg>\n"


def main():
    os.makedirs(OUT, exist_ok=True)
    svg = page()
    open(os.path.join(OUT, "fungi-field-guide.svg"), "w").write(svg)
    png = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(), output_width=W, output_height=H))).convert("RGBA")
    logo = Image.open(os.path.join(HERE, "..", "creative-code", "logos", "SFW-logo-flower-colour.png")).convert("RGBA")
    logo.thumbnail((230, 230)); png.alpha_composite(logo, (W - 170 - logo.width, H - 150 - logo.height))
    png.convert("RGB").save(os.path.join(OUT, "fungi-field-guide.png"), dpi=(300, 300), optimize=True)
    pv = png.convert("RGB"); pv.thumbnail((1240, 1754)); pv.save(os.path.join(OUT, "fungi-field-guide-preview.png"))


if __name__ == "__main__":
    main()
