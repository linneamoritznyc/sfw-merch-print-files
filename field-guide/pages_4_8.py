"""SFW Field Guide, pages 4 to 8. A4, vector, text as outlines. SFW's own drawings, constructed in code from
standard descriptions. Each page must be checked by an SFW mentor before it is published.

 4 Flagellates        Bodo-type kinetoplastid: anterior flagellum, long trailing flagellum, flagellar pocket,
                      kinetoplast, nucleus, contractile vacuole, food vacuoles
 5 Naked amoebae      lobose amoeba: clear ectoplasm, granular endoplasm, lobopodia, nucleus with nucleolus,
                      contractile vacuole, food vacuoles, uroid; soil shapes (limax, polypodial, flattened)
 6 Ciliates           Colpoda: kidney shape, ciliary rows, oral opening on the concave side, macronucleus,
                      micronucleus, contractile vacuole at the rear; resting cyst; division cyst with 4 daughters
 7 Bacteria           shapes (coccus, diplococcus, chain, rod, flagellated rod, curved rod, spiral,
                      actinobacteria); what they look like at 400x next to a hypha and a flagellate, same scale
 8 Microarthropods    oribatid mite (prodorsum, sensilli, notogaster, 4 leg pairs, chelicerae) and springtail
                      (antennae, 3 leg pairs, ventral tube, spring folded under the abdomen)

Usage: python3 pages_4_8.py
"""
import io, math, os
import numpy as np
import cairosvg
from PIL import Image
from shapely.geometry import Polygon, Point, LineString
from euglypha import text, para, d_of, label, DEEP, FWG, LIGHT, WHITE, W, H, HERE, OUT

BROWN = "#4F3433"
LW = 3.2
G6 = "eb-garamond-latin-600-normal.woff2"
M = 170
rng = np.random.default_rng(11)


# ------------------------------------------------------------------ page frame
def header(no, title, sub, taxo):
    return "".join([f'<rect width="{W}" height="{H}" fill="{WHITE}"/>',
                    text("SOIL FOOD WEB FIELD GUIDE", 34, M, 230, fnt=G6, track=180, color=FWG)[0],
                    text(f"No. {no}", 34, W - M, 230, fnt=G6, anchor="end", track=120, color=FWG)[0],
                    text(title, 140, M - 4, 405)[0], text(sub, 54, M, 500)[0], text(taxo, 38, M, 568, color=FWG)[0]])


def caption(t, x, y):
    return text(t, 40, x, y, anchor="middle", fnt=G6)[0]


def facts(items, y, fs=36, x=M, indent=220, gap=1.7):
    out = []
    for head, lines in items:
        out.append(text(head, fs, x, y, fnt=G6, color=FWG)[0])
        t, yl = para(lines, fs, x + indent, y)
        out.append(t); y = yl + fs * gap
    return "".join(out)


def finish(name, body):
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n{body}\n</svg>\n'
    open(os.path.join(OUT, f"{name}-field-guide.svg"), "w").write(svg)
    png = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(), output_width=W, output_height=H))).convert("RGBA")
    logo = Image.open(os.path.join(HERE, "..", "creative-code", "logos", "SFW-logo-flower-colour.png")).convert("RGBA")
    logo.thumbnail((230, 230)); png.alpha_composite(logo, (W - 170 - logo.width, H - 150 - logo.height))
    png.convert("RGB").save(os.path.join(OUT, f"{name}-field-guide.png"), dpi=(300, 300), optimize=True)
    pv = png.convert("RGB"); pv.thumbnail((1240, 1754)); pv.save(os.path.join(OUT, f"{name}-field-guide-preview.png"))
    return png.convert("RGB")


# ------------------------------------------------------------------ drawing helpers
def P(pts, fill="none", stroke=DEEP, w=LW, close=True, extra=""):
    return f'<path d="{d_of(pts, close)}" fill="{fill}" stroke="{stroke}" stroke-width="{w:.2f}" stroke-linejoin="round" stroke-linecap="round"{extra}/>'


def circle(x, y, r, fill=WHITE, stroke=DEEP, w=LW):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{w:.2f}"/>'


def ellipse(x, y, rx, ry, rot=0, fill=WHITE, stroke=DEEP, w=LW):
    return (f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" transform="rotate({rot:.1f} {x:.1f} {y:.1f})" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{w:.2f}"/>')


def smooth(ctrl, n=160, closed=False):
    p = np.asarray(ctrl, float)
    q = np.vstack([p[-1], p, p[0], p[1]]) if closed else np.vstack([2 * p[0] - p[1], p, 2 * p[-1] - p[-2]])
    out = []
    for i in range(len(q) - 3):
        p0, p1, p2, p3 = q[i:i + 4]
        for t in np.linspace(0, 1, max(4, n // (len(q) - 3)), endpoint=False):
            out.append(0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    if not closed:
        out.append(q[-2])
    return np.array(out)


def blob(cx, cy, R, lobes, n=240):
    """Closed outline: circle of radius R with smooth lobes [(angle_deg, extra_fraction, width_rad)]."""
    pts = []
    for t in np.linspace(0, 2 * math.pi, n, endpoint=False):
        r = R
        for a, h, wd in lobes:
            d = (t - math.radians(a) + math.pi) % (2 * math.pi) - math.pi
            r += R * h * math.exp(-(d / wd) ** 2)
        pts.append((cx + r * math.cos(t), cy + r * math.sin(t)))
    return np.array(pts)


def stipple(poly, n, r, color, avoid=None):
    g = Polygon(poly)
    if avoid is not None:
        g = g.difference(avoid)
    minx, miny, maxx, maxy = g.bounds
    out, k = [], 0
    while len(out) < n and k < n * 30:
        k += 1
        x, y = rng.uniform(minx, maxx), rng.uniform(miny, maxy)
        if g.contains(Point(x, y)):
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{color}"/>')
    return "".join(out)


def flagellum(p0, direction, length, amp, waves, w=LW * 1.3, color=DEEP):
    a = math.radians(direction); t = np.array([math.cos(a), math.sin(a)]); n = np.array([-t[1], t[0]])
    s = np.linspace(0, 1, 120)
    pts = [np.array(p0) + t * length * u + n * amp * math.sin(u * waves * 2 * math.pi) * min(1, u * 4) for u in s]
    return P(pts, close=False, w=w, stroke=color)


def cilia_fringe(outline, L, w=LW * .8, every=1, wave=14):
    ring = LineString(np.vstack([outline, outline[:1]]))
    poly = Polygon(outline)
    N = int(ring.length / (L * 0.24))
    segs = []
    for i in range(0, N, every):
        s = i / N * ring.length
        p = np.array(ring.interpolate(s).coords[0]); q = np.array(ring.interpolate(s + 1).coords[0])
        t = (q - p) / np.linalg.norm(q - p); n = np.array([t[1], -t[0]])
        if poly.contains(Point(*(p + n * 3))):
            n = -n
        bend = math.radians(25 + 12 * math.sin(i / N * 2 * math.pi * wave))
        d = n * math.cos(bend) + t * math.sin(bend)
        e = p + d * L; c = p + n * L * 0.6
        segs.append(f"M{p[0]:.1f},{p[1]:.1f}Q{c[0]:.1f},{c[1]:.1f} {e[0]:.1f},{e[1]:.1f}")
    return f'<path d="{"".join(segs)}" fill="none" stroke="{DEEP}" stroke-width="{w:.2f}" stroke-linecap="round"/>'


def food_vac(x, y, r):
    s = circle(x, y, r, fill=FWG, stroke=FWG)
    for k in range(2):
        a = rng.uniform(0.3, 1.3); bx, by = x + rng.uniform(-.3, .3) * r, y + rng.uniform(-.3, .3) * r; L = r * .5
        s += f'<path d="M{bx - math.cos(a) * L / 2:.1f},{by - math.sin(a) * L / 2:.1f}L{bx + math.cos(a) * L / 2:.1f},{by + math.sin(a) * L / 2:.1f}" stroke="{WHITE}" stroke-width="{max(5, r * .2):.1f}" stroke-linecap="round"/>'
    return s


def nucleus(x, y, r):
    return circle(x, y, r, fill=WHITE, w=LW * 1.3) + circle(x, y, r * .4, fill=DEEP, stroke=DEEP)


# ------------------------------------------------------------------ small "how it moves" icons (shared by 4, 5, 6)
def icon_flagellate(cx, cy, s):
    body = smooth([(cx - s * .30, cy), (cx - s * .05, cy - s * .16), (cx + s * .30, cy - s * .05), (cx + s * .22, cy + s * .14), (cx - s * .10, cy + s * .14)], closed=True)
    return (P(body, fill=LIGHT, stroke=FWG) + flagellum((cx - s * .28, cy - s * .03), 200, s * .35, s * .05, 1.2)
            + flagellum((cx - s * .26, cy + s * .03), 20, s * .85, s * .04, 1.6))


def icon_amoeba(cx, cy, s):
    return P(blob(cx, cy, s * .26, [(0, .55, .35), (100, .35, .3), (200, .45, .35), (290, .3, .3)]), fill=LIGHT, stroke=FWG)


def icon_ciliate(cx, cy, s):
    o = blob(cx, cy, s * .3, [(270, -.18, .35)], n=160) * np.array([1, .7]) + np.array([0, cy * .3])
    return P(o, fill=LIGHT, stroke=FWG) + cilia_fringe(o, s * .07, w=2.6)


def three_groups(y, highlight):
    out = []
    items = [("Flagellates", "One or a few whips", icon_flagellate), ("Amoebae", "Flowing pseudopods", icon_amoeba),
             ("Ciliates", "Many short hairs", icon_ciliate)]
    for i, (name, how, fn) in enumerate(items):
        cx = M + 330 + i * 720
        out.append(fn(cx, y, 360))
        out.append(text(name, 38, cx, y + 230, anchor="middle", fnt=G6, color=FWG if name == highlight else DEEP)[0])
        out.append(text(how, 32, cx, y + 278, anchor="middle")[0])
    return "".join(out)


# ------------------------------------------------------------------ 4 flagellates
def page_flagellate():
    b = [header(4, "Flagellates", "The smallest protozoa in soil",
                "Protozoa  ·  for example Bodo, Cercomonas, Spumella")]
    cx, cy, s = 1000, 1120, 820
    body = smooth([(cx - s * .42, cy - s * .02), (cx - s * .2, cy - s * .2), (cx + s * .18, cy - s * .2), (cx + s * .42, cy - s * .02),
                   (cx + s * .3, cy + s * .17), (cx - s * .05, cy + s * .2), (cx - s * .34, cy + s * .12)], closed=True)
    b.append(P(body, fill=LIGHT, stroke=FWG, w=LW * 1.4))
    pocket = (cx - s * .38, cy - s * .06)
    b.append(ellipse(pocket[0] + 22, pocket[1], 34, 20, -20, fill=WHITE, stroke=DEEP))
    b.append(flagellum(pocket, 200, s * .45, s * .05, 1.1, w=LW * 1.5))             # short anterior flagellum
    tr = smooth([pocket, (cx - s * .2, cy + s * .26), (cx + s * .25, cy + s * .30), (cx + s * .65, cy + s * .22), (cx + s * .9, cy + s * .30)])
    b.append(P(tr, close=False, w=LW * 1.5))                                        # long trailing flagellum
    b.append(ellipse(cx - s * .27, cy - s * .04, 42, 18, -15, fill=DEEP, stroke=DEEP))   # kinetoplast
    b.append(nucleus(cx - s * .02, cy - s * .03, 70))
    b.append(circle(cx - s * .2, cy - s * .12, 30, fill=WHITE, stroke=FWG))
    b.append(food_vac(cx + s * .2, cy - s * .02, 44)); b.append(food_vac(cx + s * .28, cy + s * .1, 34))
    b += [label((pocket[0] - s * .3, pocket[1] - s * .12), M + 440, 800, ["Short front flagellum"], side="left"),
          label((cx - s * .27, cy - s * .04 - 18), 900, 760, ["Kinetoplast, at the base", "of the flagella"], side="right"),
          label((cx - s * .02 + 70, cy - s * .03), 1560, 790, ["Nucleus"], side="right"),
          label((cx - s * .2 - 26, cy - s * .12 - 14), M + 440, 640, ["Contractile vacuole"], side="left"),
          label((cx + s * .2 + 40, cy - s * .02 - 20), 1860, 900, ["Food vacuole", "with bacteria"], side="right"),
          label(tuple(tr[110]), 1700, 1470, ["Long trailing flagellum"], side="right"),
          label((pocket[0] + 10, pocket[1] + 16), M + 440, 1430, ["Flagellar pocket"], side="left")]
    b.append(caption("A  A Bodo-type flagellate, about 1000x", W / 2, 1620))
    b.append(three_groups(1880, "Flagellates"))
    b.append(caption("B  The three protozoa groups, and how they move", W / 2, 2290))
    b.append(facts([("Size", ["The smallest protozoa. Bodo saltans, a common one, is about 5 to 8 µm long."]),
                    ("Where", ["The water films around soil particles."]),
                    ("Eats", ["Bacteria. The short flagellum sweeps food in, the long one drives the cell."]),
                    ("Role", ["Bacteria hold more nitrogen than a flagellate needs, so it releases the rest", "as ammonium, a form plant roots can take up."]),
                    ("At 400x", ["Tiny cells that jerk and spin fast. The flagella are often too thin to see.", "Count them by their quick, twitching movement."])], 2460))
    return finish("flagellate", "".join(b))


# ------------------------------------------------------------------ 5 naked amoebae
def page_amoeba():
    b = [header(5, "Naked amoebae", "Shape-shifting cells that flow toward their food",
                "Protozoa  ·  Amoebozoa and others  ·  without a shell")]
    cx, cy, R = 1060, 1130, 300
    outline = blob(cx, cy, R, [(-10, .65, .38), (55, .25, .3), (115, .32, .32), (190, .18, .5), (250, .3, .3), (320, .22, .3)])
    b.append(P(outline, fill=WHITE, stroke=DEEP, w=LW * 1.5))
    from shapely import affinity
    inner = np.array(affinity.translate(Polygon(outline).buffer(-30), -45, 6).intersection(Polygon(outline).buffer(-18)).exterior.coords)
    b.append(P(inner, fill=LIGHT, stroke=FWG, w=LW))
    nx, ny = cx - 30, cy + 10
    b.append(stipple(inner, 420, 4.2, FWG, avoid=Point(nx, ny).buffer(105).union(Point(cx + 120, cy - 120).buffer(50))))
    b.append(nucleus(nx, ny, 80))
    b.append(circle(cx - 170, cy - 60, 40, fill=WHITE, stroke=FWG))
    b.append(food_vac(cx + 120, cy - 120, 46)); b.append(food_vac(cx + 60, cy + 150, 36))
    # uroid: wrinkled rear end, opposite the leading lobe
    ux, uy = cx - R * 1.1, cy + R * .25
    b.append(P(blob(ux + 8, uy, 26, [(a_, .25, .25) for a_ in (120, 180, 240)]), fill=WHITE, stroke=DEEP))
    lead = (cx + R * 1.55, cy - R * .25)
    b += [label((cx + R * 1.5, cy - R * .15), 1880, 780, ["Clear front edge", "(ectoplasm)"], side="right"),
          label(tuple(outline[int(240 * 115 / 360)]), 1600, 1580, ["Lobe-shaped pseudopod"], side="right"),
          label((nx + 80, ny), 1880, 1300, ["Nucleus with", "nucleolus"], side="right"),
          label((cx + 60 + 30, cy + 150 + 10), 1880, 1500, ["Food vacuole"], side="right"),
          label((cx - 170 - 40, cy - 60), M + 440, 860, ["Contractile vacuole"], side="left"),
          label((cx - 200, cy + 120), M + 440, 1240, ["Granular inner", "cytoplasm"], side="left"),
          label((ux - 30, uy + 10), M + 440, 1500, ["Rear end (uroid)"], side="left")]
    b.append(caption("A  A lobose amoeba, flowing to the right, about 400x", W / 2, 1640))
    # B soil shapes
    y = 1950
    shapes = [("Limax", "Slug-shaped, one pseudopod", lambda x: P(smooth([(x - 150, y), (x - 60, y - 55), (x + 120, y - 45), (x + 170, y), (x + 120, y + 45), (x - 60, y + 50)], closed=True), fill=LIGHT, stroke=FWG)),
              ("Many lobes", "Several pseudopods at once", lambda x: icon_amoeba(x, y, 400)),
              ("Flat fan", "Spread thin, wide front", lambda x: P(np.vstack([[(x - 70 + 190 * math.cos(t) * .9, y + 15 + 190 * math.sin(t) * .55) for t in np.linspace(-1.25, 1.25, 50)], [(x - 60, y + 45), (x - 90, y + 15), (x - 60, y - 15)]]), fill=LIGHT, stroke=FWG)),
              ("With a shell", "Testate amoeba, see No. 1", lambda x: P(smooth([(x, y - 110), (x + 65, y - 60), (x + 70, y + 40), (x + 30, y + 95), (x - 30, y + 95), (x - 70, y + 40), (x - 65, y - 60)], closed=True), fill=WHITE, stroke=DEEP, w=LW * 1.4))]
    for i, (name, how, fn) in enumerate(shapes):
        x = M + 230 + i * 540
        b.append(fn(x))
        b.append(text(name, 38, x, y + 200, anchor="middle", fnt=G6, color=FWG)[0])
        b.append(text(how, 30, x, y + 245, anchor="middle")[0])
    b.append(caption("B  Shapes you will meet in soil", W / 2, 2340))
    b.append(facts([("Size", ["Between flagellates and ciliates in size. About 10,000 to 100,000 live in a gram", "of soil."]),
                    ("Where", ["Water films and the tiny pores inside soil crumbs, where other", "predators cannot reach the bacteria."]),
                    ("Eats", ["Mainly bacteria. It flows around its food and swallows it."]),
                    ("Role", ["Releases plant-available nitrogen, like the other protozoa."]),
                    ("At 400x", ["A cell that slowly changes shape. Watch for a clear cap at the front", "and grainy cytoplasm flowing in behind it."])], 2510))
    return finish("amoeba", "".join(b))


# ------------------------------------------------------------------ 6 ciliates
def colpoda_outline(cx, cy, A, Bh, n=300):
    th0, depth, wid = 1.5 * math.pi - 0.28, Bh * 0.30, 0.42
    pts = []
    for t in np.linspace(0, 2 * math.pi, n, endpoint=False):
        x, y = A * math.cos(t), Bh * math.sin(t)
        if x < 0:
            y *= 1 - 0.10 * (-x / A)
        d = (t - th0 + math.pi) % (2 * math.pi) - math.pi
        y += depth * math.exp(-(d / wid) ** 2)
        pts.append((cx + x, cy + y))
    return np.array(pts), (cx + A * math.cos(th0), cy + Bh * math.sin(th0) + depth)


def page_ciliate():
    b = [header(6, "Ciliates", "Fast swimmers covered in rows of tiny hairs",
                "Protozoa  ·  Ciliophora  ·  for example Colpoda")]
    cx, cy, A, Bh = 1080, 1130, 520, 360
    o, notch = colpoda_outline(cx, cy, A, Bh)
    poly = Polygon(o)
    b.append(cilia_fringe(o, 62, w=LW * .85))
    b.append(P(o, fill=LIGHT, stroke=FWG, w=LW * 1.4))
    # ciliary rows (kineties): curved dotted rows
    dots = []
    for k in np.linspace(-0.85, 0.85, 9):
        for x in np.arange(-A * .95, A * .95, 26):
            u = x / A
            y = cy + k * Bh * math.sqrt(max(0, 1 - u * u)) * .9 + 0.12 * Bh * (1 - u * u)
            if poly.buffer(-20).contains(Point(cx + x, y)):
                dots.append(f'<circle cx="{cx + x:.1f}" cy="{y:.1f}" r="3.2" fill="{FWG}"/>')
    b.append("".join(dots))
    # oral opening on the concave side, with longer oral cilia
    ox, oy = notch
    pocket = smooth([(ox - 80, oy - 6), (ox - 30, oy + 60), (ox + 30, oy + 95), (ox + 90, oy + 4)])
    b.append(P(pocket, fill=WHITE, stroke=DEEP, w=LW * 1.4, close=True))
    b.append("".join(P([(ox - 60 + k * 18, oy + 2 + abs(k - 4) * 2), (ox - 45 + k * 15, oy + 50 - abs(k - 4) * 6)], close=False, w=2.6) for k in range(9)))
    b.append(P(smooth([(ox - 40, cy - Bh * .2), (cx - A * .05, cy), (cx + A * .15, cy + Bh * .1)]), close=False, w=0))
    b.append(nucleus(cx + A * .12, cy + Bh * .12, 95))
    b.append(circle(cx + A * .12 - 125, cy + Bh * .12 + 70, 22, fill=DEEP, stroke=DEEP))       # micronucleus
    b.append(circle(cx + A * .82, cy - Bh * .05, 42, fill=WHITE, stroke=FWG))                  # contractile vacuole, rear
    for fx, fy, r in [(-.55, .05, 44), (-.3, .42, 40), (.45, -.38, 42), (.5, .42, 36), (-.62, -.32, 30)]:
        b.append(food_vac(cx + fx * A, cy + fy * Bh, r))
    b += [label((cx - A * .97, cy - Bh * .3), M + 440, 760, ["Cilia all over the cell"], side="left"),
          label((ox + 10, oy + 60), 820, 690, ["Mouth (oral cavity)", "on the curved-in side"], side="right"),
          label((cx + A * .12 + 95, cy + Bh * .12), 1960, 1380, ["Macronucleus"], side="right"),
          label((cx + A * .12 - 125, cy + Bh * .12 + 92), 1350, 1560, ["Micronucleus"], side="right"),
          label((cx + A * .82 + 42, cy - Bh * .05), 1960, 990, ["Contractile vacuole", "at the rear"], side="right"),
          label((cx - .3 * A, cy + .42 * Bh + 40), M + 440, 1560, ["Food vacuole"], side="left"),
          label((cx - A * .4, cy - Bh * .55), 1500, 690, ["Rows of cilia bases"], side="right")]
    b.append(caption("A  Colpoda, a common soil ciliate, about 400x", W / 2, 1680))
    # B cysts
    y = 2000
    x1, x2 = M + 380, M + 1160
    b.append(circle(x1, y, 170, fill=WHITE, w=LW * 2.2) + circle(x1, y, 150, fill=WHITE, w=LW))
    b.append(P(blob(x1, y, 110, [(40, .1, .5), (200, .08, .5)]), fill=LIGHT, stroke=FWG) + nucleus(x1 + 10, y, 38))
    b.append(text("Resting cyst", 38, x1, y + 250, anchor="middle", fnt=G6, color=FWG)[0])
    b.append(text("Thick wall. How it survives dry soil.", 30, x1, y + 295, anchor="middle")[0])
    b.append(circle(x2, y, 170, fill=WHITE, w=LW * 1.4))
    for qx, qy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
        b.append(P(blob(x2 + qx * 70, y + qy * 70, 62, [(45 * qx * qy, .05, .5)]), fill=LIGHT, stroke=FWG))
    b.append(text("Division cyst", 38, x2, y + 250, anchor="middle", fnt=G6, color=FWG)[0])
    b.append(text("Usually 4 new cells, sometimes 2 or 8.", 30, x2, y + 295, anchor="middle")[0])
    b.append(icon_ciliate(M + 1880, y, 520))
    b.append(text("Active cell", 38, M + 1880, y + 250, anchor="middle", fnt=G6, color=FWG)[0])
    b.append(text("Swims when the soil is wet.", 30, M + 1880, y + 295, anchor="middle")[0])
    b.append(caption("B  Three stages of Colpoda", W / 2, 2400))
    b.append(facts([("Size", ["Ciliates are the largest and least numerous protozoa. Some colpodeans,", "the group Colpoda belongs to, are as small as 10 µm."]),
                    ("Where", ["Water-filled pores and water films."]),
                    ("Eats", ["Bacteria, swept into the mouth by the cilia."]),
                    ("Role", ["Releases nitrogen like the other protozoa. In the Soil Food Web method,", "many ciliates point to soil that is short of oxygen."]),
                    ("At 400x", ["Fast, gliding swimmers that change direction often. Look for the", "fringe of cilia and the notch of the mouth."])], 2570))
    return finish("ciliate", "".join(b))


# ------------------------------------------------------------------ 7 bacteria
def rod(x, y, L, w, ang, fill=LIGHT, stroke=FWG):
    g = LineString([(-L / 2 + w / 2, 0), (L / 2 - w / 2, 0)]).buffer(w / 2, 16)
    pts = np.array(g.exterior.coords)
    a = math.radians(ang)
    R = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])
    pts = pts @ R.T + np.array([x, y])
    return P(pts, fill=fill, stroke=stroke)


def page_bacteria():
    b = [header(7, "Bacteria", "Tiny, countless, and the base of the soil food web",
                "Bacteria and actinobacteria  ·  single cells about 1 µm across")]
    # A shapes, enlarged
    cells = []
    y0, dx = 900, 700
    def cell(i, j):
        return M + 280 + j * dx, y0 + i * 380
    x, y = cell(0, 0); cells.append(("Coccus", "Round", circle(x, y, 70, fill=LIGHT, stroke=FWG)))
    x, y = cell(0, 1); cells.append(("Diplococcus", "Pairs", circle(x - 62, y, 62, fill=LIGHT, stroke=FWG) + circle(x + 62, y, 62, fill=LIGHT, stroke=FWG)))
    x, y = cell(0, 2); cells.append(("Chain", "Cells that stay joined", "".join(circle(x - 165 + k * 66, y + 12 * math.sin(k), 32, fill=LIGHT, stroke=FWG) for k in range(6))))
    x, y = cell(1, 0); cells.append(("Rod (bacillus)", "The most common shape", rod(x, y, 260, 90, -10)))
    fl = "".join(flagellum((x + 120 * math.cos(math.radians(a)), y + 50 * math.sin(math.radians(a))), a, 150, 14, 1.5, w=2.6)
                 for a in (20, 70, 120, 160, 200, 250, 300, 340)) if False else ""
    xr, yr = cell(1, 1); yr -= 20
    fl = "".join(flagellum((xr + 110 * math.cos(math.radians(a)), yr - 20 + 40 * math.sin(math.radians(a))), a, 90, 10, 1.2, w=2.6)
                 for a in (25, 75, 115, 165, 205, 255, 295, 345))
    cells.append(("Rod with flagella", "Swims", fl + rod(xr, yr, 240, 80, 0)))
    x, y = cell(1, 2)
    vib = smooth([(x - 120, y + 30), (x - 40, y - 25), (x + 50, y - 25), (x + 120, y + 30)])
    cells.append(("Curved rod", "Comma shape", P(np.array(LineString(vib).buffer(38, 16).exterior.coords), fill=LIGHT, stroke=FWG)))
    x, y = cell(2, 0)
    sp = [(x - 170 + u * 340, y + 40 * math.sin(u * 3 * 2 * math.pi)) for u in np.linspace(0, 1, 200)]
    cells.append(("Spiral", "Corkscrew", P(np.array(LineString(sp).buffer(16, 12).exterior.coords), fill=LIGHT, stroke=FWG)))
    x, y = cell(2, 1)
    br = [[(x - 200, y + 40), (x + 160, y + 20)], [(x - 60, y + 32), (x + 10, y - 80)], [(x + 60, y + 25), (x + 140, y - 60)]]
    act = "".join(P(np.array(LineString(l).buffer(10, 8).exterior.coords), fill=LIGHT, stroke=FWG) for l in br)
    act += "".join(circle(x + 140 + k * 9, y - 60 - k * 20, 12, fill=LIGHT, stroke=FWG) for k in range(1, 4))
    cells.append(("Actinobacteria", "Branching threads, spore chains", act))
    x, y = cell(2, 2)
    col = "".join(rod(x + rng.normal(0, 45), y - 20 + rng.normal(0, 28), 70, 30, rng.uniform(0, 180)) for _ in range(14))
    cells.append(("Colony", "Cells living together on a surface", col))
    for k, (name, how, svg) in enumerate(cells):
        i, j = divmod(k, 3)
        x, y = cell(i, j)
        b.append(svg)
        b.append(text(name, 36, x, y + 140, anchor="middle", fnt=G6, color=FWG)[0])
        b.append(text(how, 30, x, y + 182, anchor="middle")[0])
    b.append(caption("A  Shapes, greatly enlarged", W / 2, 1930))
    # B at the same size: 1 µm = 14 px
    um = 14.0
    yb = 2240
    b.append(f'<path d="M{M},{yb - 30}L{W - M},{yb - 110}" stroke="none"/>')
    hyp = LineString([(M, yb + 60), (M + 1200, yb - 40)]).buffer(2.5 * um, 16)
    b.append(P(np.array(hyp.exterior.coords), fill=WHITE, stroke=DEEP))
    for k in range(1, 6):
        t = k / 6; px, py = M + 1200 * t, yb + 60 - 100 * t
        b.append(f'<path d="M{px - 4:.1f},{py - 2.5 * um:.1f}L{px + 4:.1f},{py + 2.5 * um:.1f}" stroke="{DEEP}" stroke-width="{LW:.2f}"/>')
    fx, fy = M + 1600, yb + 20
    fb = smooth([(fx - 3 * um, fy), (fx - um, fy - 2 * um), (fx + 3 * um, fy - um), (fx + 2 * um, fy + 1.5 * um), (fx - um, fy + 1.5 * um)], closed=True)
    b.append(P(fb, fill=LIGHT, stroke=FWG) + flagellum((fx - 3 * um, fy), 200, 4 * um, 6, 1.2, w=2.4) + flagellum((fx - 3 * um, fy + 4), 15, 10 * um, 6, 1.5, w=2.4))
    for _ in range(70):
        x, y = rng.uniform(M, W - M - 300), rng.uniform(yb - 140, yb + 160)
        if hyp.distance(Point(x, y)) < 20 or math.hypot(x - fx, y - fy) < 120:
            continue
        b.append(rod(x, y, 2 * um, um, rng.uniform(0, 180), fill=FWG, stroke=FWG) if rng.random() < .6 else circle(x, y, um / 2, fill=FWG, stroke=FWG))
    b.append(f'<rect x="{W - M - 140 - 10 * um:.1f}" y="{yb + 210}" width="{10 * um:.1f}" height="10" fill="{DEEP}"/>')
    b.append(text("10 µm", 32, W - M - 140 - 5 * um, yb + 195, anchor="middle")[0])
    b += [label((M + 700, yb - 25), M + 520, yb - 210, ["Fungal hypha"], side="right"),
          label((fx + 2.5 * um, fy - 1.5 * um), fx + 120, yb - 210, ["Flagellate"], side="right")]
    b.append(caption("B  At 400x: bacteria next to a fungal hypha and a flagellate, all at the same size", W / 2, yb + 330))
    b.append(facts([("Size", ["About 0.5 to 2 µm. 100 million to 1 billion live in a teaspoon of productive soil."]),
                    ("Eats", ["Mostly simple sugars and other easy food from roots and decaying material."]),
                    ("Role", ["Make sticky substances that glue soil particles into tiny crumbs, hold nutrients,", "and feed the protozoa and nematodes that release those nutrients to plants."]),
                    ("At 400x", ["Dots and short rods, some moving. You count bacteria, you do not identify them."])], 2760))
    return finish("bacteria", "".join(b))


# ------------------------------------------------------------------ 8 microarthropods
def leg(base, ang, segs, w, curl, out):
    p = np.array(base, float); a = math.radians(ang)
    pts = [p.copy()]
    for k, L in enumerate(segs):
        a += math.radians(curl[k])
        p = p + L * np.array([math.cos(a), math.sin(a)]); pts.append(p.copy())
    for k in range(len(pts) - 1):
        g = LineString([pts[k], pts[k + 1]]).buffer(w * (1 - 0.12 * k), 12)
        out.append(P(np.array(g.exterior.coords), fill=WHITE, stroke=DEEP, w=LW))
    tip = pts[-1]; d = (pts[-1] - pts[-2]) / np.linalg.norm(pts[-1] - pts[-2])
    out.append(P([tip, tip + d * 16 + np.array([-d[1], d[0]]) * 8], close=False, w=LW))


def page_arthropods():
    b = [header(8, "Microarthropods", "The shredders: mites and springtails",
                "Arthropoda  ·  oribatid mites (Acari) and springtails (Collembola)")]
    # A oribatid mite, top view
    cx, cy = 720, 1180
    legs = []
    for side in (-1, 1):
        for k, (ang, L) in enumerate([(-140, 70), (-170, 64), (165, 64), (135, 74)]):
            base = (cx + side * (90 if k < 2 else 150), cy - 180 + k * 70 + (0 if k < 2 else 90))
            a = ang if side < 0 else 180 - ang
            leg(base, a, [L, L * .9, L * .8, L * .75, L * .6], 15, [0, side * (-10 if k < 2 else 10)] * 3, legs)
    b += legs
    noto = blob(cx, cy + 70, 230, [(90, .08, .8)]) * np.array([1, 1])
    b.append(P(noto, fill=WHITE, stroke=DEEP, w=LW * 1.6))
    pro = smooth([(cx - 120, cy - 120), (cx - 70, cy - 260), (cx, cy - 300), (cx + 70, cy - 260), (cx + 120, cy - 120)])
    b.append(P(np.vstack([pro, [(cx, cy - 150)]]), fill=WHITE, stroke=DEEP, w=LW * 1.4))
    b.append(P(smooth([(cx - 120, cy - 140), (cx, cy - 165), (cx + 120, cy - 140)]), close=False, w=LW * 1.4))
    for s_ in (-1, 1):
        b.append(P([(cx + s_ * 55, cy - 210), (cx + s_ * 110, cy - 300)], close=False, w=LW))
        b.append(ellipse(cx + s_ * 114, cy - 306, 9, 15, s_ * 30, fill=DEEP, stroke=DEEP))
        for k in range(4):
            sx, sy = cx + s_ * (60 + k * 22), cy + 10 + k * 70
            b.append(P([(sx, sy), (sx + s_ * 22, sy - 16)], close=False, w=LW))
    b.append(P([(cx - 14, cy - 300), (cx - 8, cy - 330), (cx + 8, cy - 330), (cx + 14, cy - 300)], close=False, w=LW * 1.2))
    b += [label((cx + 114, cy - 322), 1060, 690, ["Sensory hair (sensillus)"], side="right"),
          label((cx + 60, cy - 240), 1060, 790, ["Front shield", "(prodorsum)"], side="right"),
          label((cx + 150, cy + 200), 1000, 1580, ["Back shield, hard", "and rounded"], side="right"),
          label((cx - 290, cy - 210), M + 440, 760, ["8 legs"], side="left"),
          label((cx - 10, cy - 330), 420, 640, ["Mouthparts"], side="left")]
    b.append(caption("A  Oribatid mite, from above", 720, 1720))
    # B springtail, side view
    sx, sy = 1820, 1180
    seg = [(sx - 300, sy - 20, 60, 70), (sx - 220, sy - 30, 55, 72), (sx - 150, sy - 30, 50, 75), (sx - 85, sy - 25, 50, 78),
           (sx - 20, sy - 20, 50, 80), (sx + 45, sy - 15, 50, 80), (sx + 110, sy - 10, 50, 78), (sx + 170, sy - 5, 45, 70), (sx + 220, sy + 5, 40, 58)]
    head = ellipse(sx - 370, sy - 10, 75, 62, -10)
    for k, (x, y, hw, hh) in enumerate(seg):
        b.append(ellipse(x, y + 10, hw * .78, hh * .78, 0))
    b.append(head)
    b.append(circle(sx - 395, sy - 35, 12, fill=DEEP, stroke=DEEP))
    ant = [(sx - 420, sy - 60)]
    a = -120
    for L in (60, 70, 70, 80):
        a += 12; p = ant[-1]; ant.append((p[0] + L * math.cos(math.radians(a)), p[1] + L * math.sin(math.radians(a))))
    for k in range(4):
        g = LineString([ant[k], ant[k + 1]]).buffer(11 - k * 1.5, 10)
        b.append(P(np.array(g.exterior.coords), fill=WHITE, stroke=DEEP))
    legs = []
    for k, x in enumerate((sx - 300, sx - 220, sx - 150)):
        leg((x, sy + 55), 100 + k * 8, [55, 50, 45, 35], 12, [0, -20, 25, 0], legs)
    b += legs
    b.append(P([(sx - 100, sy + 62), (sx - 92, sy + 105), (sx - 68, sy + 105), (sx - 62, sy + 62)], fill=LIGHT, stroke=FWG))   # ventral tube
    furca = smooth([(sx + 110, sy + 66), (sx + 70, sy + 96), (sx - 10, sy + 106), (sx - 50, sy + 100)])
    b.append(P(np.array(LineString(furca).buffer(10, 10).exterior.coords), fill=WHITE, stroke=DEEP))
    b += [label(ant[3], 1500, 690, ["Antennae"], side="right"),
          label((sx - 395, sy - 35), 1300, 900, ["Eye patch"], side="left"),
          label((sx - 80, sy + 105), 1500, 1520, ["Ventral tube"], side="right"),
          label((sx + 40, sy + 108), 1900, 1560, ["Spring, folded under the", "body, flicks it into a jump"], side="right"),
          label((sx - 240, sy + 150), 1300, 1460, ["6 legs"], side="left")]
    b.append(caption("B  Springtail, from the side", 1820, 1720))
    b.append(facts([("Size", ["Oribatid mites 0.2 to 1 mm, springtails 0.2 to 5 mm. Many are just visible to the eye."]),
                    ("Where", ["Leaf litter, the top few centimetres of soil, and the larger pores."]),
                    ("Eats", ["Fungi, decaying plant material and bacteria. Some mites hunt nematodes and springtails."]),
                    ("Role", ["Shred litter so fungi and bacteria can reach it, spread spores, and release nutrients", "as they graze."]),
                    ("To tell", ["Mites have 8 legs and no antennae. Springtails have 6 legs, antennae, and jump."]),
                    ("To see", ["Use low power, 10x to 40x, or a stereo microscope. They are too big for 400x."])], 2100))
    return finish("microarthropods", "".join(b))


def main():
    os.makedirs(OUT, exist_ok=True)
    for f in (page_flagellate, page_amoeba, page_ciliate, page_bacteria, page_arthropods):
        f()


if __name__ == "__main__":
    main()
