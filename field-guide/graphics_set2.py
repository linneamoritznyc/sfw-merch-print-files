"""SFW field-guide graphics, set 2: seven detailed organisms, same style as the field guide.
Each is its own SVG (transparent background) and 2x PNG in out/graphics/.

Checked against (see SOURCES.md):
  Arcella      domed proteinaceous shell of hexagonal units, single central round aperture (Wikipedia, arcella.nl)
  Difflugia    shell agglutinated from mineral grains collected from the soil, terminal aperture, finger-shaped
               lobopodia (arcella.nl); Leuckart & Nitsche wall chart III fig. 2 (Dolan 2023, Protist)
  Vorticella   bell-shaped body, peristome with oral cilia, C-shaped macronucleus, contractile stalk with a
               spasmoneme that coils into a helix (Wikipedia; NIES); wall chart LXVII fig. 3
  Root feeder  stylet with conus, shaft and three basal knobs; median bulb with valve plates (EPPO glossary; IRD)
  Mycorrhiza   intraradical hyphae in the root cortex, arbuscules inside cortical cells, oval lipid vesicles,
               extraradical hyphae with large spores in soil (Moore; mycorrhizas.info)
  Penicillium  stipe, metulae, flask-shaped phialides, basipetal chains of round conidia, brush-shaped (Adelaide)
  Streptomyces substrate mycelium, aerial hyphae ending in spiral spore chains (PMC3972883; PMC5945903)
"""
import io, math, os
import numpy as np
import cairosvg
from PIL import Image
from shapely.geometry import Point, Polygon, LineString
from shapely.ops import unary_union
from pages_4_8 import P, circle, ellipse, smooth, blob, stipple, cilia_fringe, DEEP, FWG, LIGHT, WHITE

LW = 3.2
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "graphics")
rng = np.random.default_rng(21)


def outline(geom, fill=WHITE, stroke=DEEP, w=LW):
    out = []
    for g in getattr(geom, "geoms", [geom]):
        if g.geom_type == "Polygon":
            d = "M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in g.exterior.coords) + "Z"
            for r in g.interiors:
                d += "M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in r.coords) + "Z"
            out.append(f'<path d="{d}" fill="{fill}" fill-rule="evenodd" stroke="{stroke}" stroke-width="{w:.2f}" stroke-linejoin="round"/>')
    return "".join(out)


def save(name, body, w, h):
    s = f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n{body}\n</svg>\n'
    open(os.path.join(OUT, f"sfw-{name}.svg"), "w").write(s)
    Image.open(io.BytesIO(cairosvg.svg2png(bytestring=s.encode(), output_width=w * 2, output_height=h * 2))).save(os.path.join(OUT, f"sfw-{name}.png"))


# ------------------------------------------------------------------ Arcella, from above
def arcella():
    S = 900; c = S / 2; R = 400
    b = [circle(c, c, R, fill=WHITE, w=LW * 1.8)]
    # hexagonal units in rings, shrinking toward the centre as on the dome
    for rr in np.arange(110, R - 14, 26):
        n = int(2 * math.pi * rr / 27)
        off = (rr / 26) % 2 * 0.5
        for k in range(n):
            a = (k + off) / n * 2 * math.pi
            x, y = c + rr * math.cos(a), c + rr * math.sin(a)
            s = 11 * (0.75 + 0.25 * rr / R)
            hexa = [(x + s * math.cos(a + j * math.pi / 3), y + s * math.sin(a + j * math.pi / 3)) for j in range(6)]
            b.append(P(hexa, fill="none", w=1.8))
    b.append(circle(c, c, R - 22, fill="none", w=LW))
    b.append(circle(c, c, 104, fill=WHITE, w=LW * 1.6))                      # collar around the aperture
    b.append(circle(c, c, 74, fill=LIGHT, stroke=FWG, w=LW * 1.4))           # aperture, cytoplasm seen through it
    b.append(stipple([(c + 70 * math.cos(t), c + 70 * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 60)], 120, 2.6, FWG))
    save("arcella-from-above", "".join(b), S, S)


# ------------------------------------------------------------------ Difflugia, side view, sand-grain shell
def difflugia():
    Wd, Ht = 760, 1080; cx = Wd / 2
    prof = [(cx, 70), (cx + 180, 140), (cx + 250, 360), (cx + 240, 610), (cx + 170, 790), (cx + 110, 870),
            (cx - 110, 870), (cx - 170, 790), (cx - 240, 610), (cx - 250, 360), (cx - 180, 140)]
    shell = Polygon(smooth(prof, 200, closed=True))
    b = []
    # lobopodia from the aperture, behind the shell
    for ang, L in ((-25, 200), (8, 150), (35, 180)):
        a = math.radians(90 + ang)
        tip = (cx + math.cos(a) * L, 860 + math.sin(a) * L)
        lobe = LineString([(cx + 20 * math.sin(math.radians(ang)), 840), tip]).buffer(34, 24)
        b.append(outline(lobe, fill=LIGHT, stroke=FWG))
    b.append(outline(shell, fill=WHITE, w=LW * 1.8))
    # mineral grains packed over the shell surface
    grains = []
    for _ in range(4000):
        if len(grains) > 520: break
        x, y = rng.uniform(*shell.bounds[0::2]), rng.uniform(*shell.bounds[1::2])
        r = rng.uniform(10, 26)
        p = Point(x, y)
        if shell.buffer(-r * .6).contains(p) and all(p.distance(q) > (r + rq) * 0.92 for q, rq in grains):
            grains.append((p, r))
    for p, r in grains:
        n = rng.integers(5, 8)
        pts = [(p.x + r * rng.uniform(.75, 1.05) * math.cos(t), p.y + r * rng.uniform(.75, 1.05) * math.sin(t))
               for t in np.sort(rng.uniform(0, 2 * math.pi, n))]
        b.append(P(pts, fill=LIGHT if rng.random() < .22 else WHITE, w=2.2))
        if r > 20:
            b.append(P([(p.x - r * .3, p.y - r * .2), (p.x + r * .2, p.y - r * .35)], close=False, w=1.8))
    b.append(outline(shell, fill="none", w=LW * 1.8))
    b.append(ellipse(cx, 870, 110, 18, fill=WHITE, w=LW * 1.6))            # round terminal aperture
    save("difflugia-sand-shell", "".join(b), Wd, Ht)


# ------------------------------------------------------------------ Vorticella, with the stalk coiled
def vorticella():
    Wd, Ht = 820, 1240; cx = 410
    b = []
    # contracted stalk: a helix (spasmoneme) running up to the base of the bell
    hel = [(cx + 46 * math.sin(t * 2 * math.pi * 6), 1180 - t * 520) for t in np.linspace(0, 1, 400)]
    b.append(P(hel, close=False, w=LW * 3.2, stroke=DEEP))
    b.append(P(hel, close=False, w=LW * 1.0, stroke=WHITE))
    b.append(P([(cx - 40, 1190), (cx + 40, 1190)], close=False, w=LW * 2))
    # bell-shaped body
    bell = smooth([(cx, 660), (cx + 70, 640), (cx + 170, 560), (cx + 230, 430), (cx + 245, 330), (cx + 210, 300),
                   (cx - 210, 300), (cx - 245, 330), (cx - 230, 430), (cx - 170, 560), (cx - 70, 640)], 200, closed=True)
    b.append(P(bell, fill=LIGHT, stroke=FWG, w=LW * 1.5))
    for k in np.linspace(-0.8, 0.8, 9):                                     # fine pellicle striations
        b.append(P(smooth([(cx + k * 200, 318), (cx + k * 170, 470), (cx + k * 60, 640)], 40), close=False, w=1.6, stroke=FWG))
    # peristome lip and disc with oral cilia
    b.append(ellipse(cx, 300, 250, 44, fill=WHITE, w=LW * 1.5))
    b.append(ellipse(cx, 286, 196, 32, fill=LIGHT, stroke=FWG, w=LW))
    cil = []
    for k in range(90):
        t = k / 90 * 2 * math.pi
        x0, y0 = cx + 190 * math.cos(t), 286 + 30 * math.sin(t)
        ox, oy = math.cos(t), -0.8 + 0.4 * math.sin(t)
        nrm = math.hypot(ox, oy); ox, oy = ox / nrm, oy / nrm
        L = 70
        cil.append(f"M{x0:.1f},{y0:.1f}Q{x0 + ox * L * .5:.1f},{y0 + oy * L * .9:.1f} {x0 + ox * L:.1f},{y0 + oy * L * .55 - 10:.1f}")
    b.append(f'<path d="{"".join(cil)}" fill="none" stroke="{DEEP}" stroke-width="2.2" stroke-linecap="round"/>')
    # buccal funnel, C-shaped macronucleus, food vacuoles, contractile vacuole
    b.append(P(smooth([(cx + 120, 300), (cx + 90, 380), (cx + 30, 430), (cx - 10, 420)], 40), close=False, w=LW * 1.3))
    mac = [(cx - 10 + 95 * math.cos(t), 470 + 55 * math.sin(t)) for t in np.linspace(.35 * math.pi, 1.85 * math.pi, 60)]
    b.append(P(mac, close=False, w=20, stroke=DEEP))
    b.append(P(mac, close=False, w=11, stroke=WHITE))
    for x, y, r in ((cx + 60, 520, 26), (cx - 130, 400, 22), (cx + 150, 430, 20)):
        b.append(circle(x, y, r, fill=FWG, stroke=FWG))
    b.append(circle(cx - 90, 350, 24, fill=WHITE, stroke=FWG))
    save("vorticella-stalked-ciliate", "".join(b), Wd, Ht)


# ------------------------------------------------------------------ root-feeding nematode head
def root_feeder_head():
    Wd, Ht = 1500, 600; y0 = 300; L = 1300; x0 = 100
    X = lambda u: x0 + u * L
    edge = lambda u: 190 * min(1, .5 + .5 * min(1, u / .2) ** .6)
    us = np.linspace(.02, 1.06, 160)
    top = [(X(u), y0 - edge(u)) for u in us]; bot = [(X(u), y0 + edge(u)) for u in us]
    cap = [(X(.02) - 60 * math.sin(t), y0 - edge(.02) * math.cos(t)) for t in np.linspace(0, math.pi, 30)]
    b = [P(top[::-1] + cap + bot, fill=WHITE, w=LW * 1.6, close=False)]
    # lip region with annuli and cephalic framework
    for u in np.arange(.04, .16, .025):
        h = edge(u)
        b.append(P([(X(u), y0 - h), (X(u) + 6, y0 - h * .55)], close=False, w=2.2))
        b.append(P([(X(u), y0 + h), (X(u) + 6, y0 + h * .55)], close=False, w=2.2))
    b.append(P(smooth([(X(.03), y0 - 70), (X(.09), y0 - 60), (X(.12), y0 - 40)], 20), close=False, w=LW * 1.4))
    b.append(P(smooth([(X(.03), y0 + 70), (X(.09), y0 + 60), (X(.12), y0 + 40)], 20), close=False, w=LW * 1.4))
    # stylet: pointed conus, shaft, three basal knobs
    b.append(P([(X(.01), y0), (X(.12), y0 - 9), (X(.12), y0 + 9)], fill=DEEP, w=LW))
    b.append(P([(X(.12), y0 - 6), (X(.21), y0 - 6), (X(.21), y0 + 6), (X(.12), y0 + 6)], fill=DEEP, w=LW))
    for dy in (-26, 0, 26):
        b.append(ellipse(X(.225), y0 + dy, 16, 14, fill=DEEP, stroke=DEEP))
    # protractor muscles from knobs forward
    for s in (-1, 1):
        b.append(P([(X(.23), y0 + s * 36), (X(.12), y0 + s * 120)], close=False, w=1.8))
    # pharynx: procorpus, median bulb with valve plates, isthmus, gland lobe
    pu = [.235, .40, .44, .50, .56, .60, .80, .86, 1.06]
    pv = [.10, .14, .40, .46, .40, .12, .12, .42, .40]
    uu = np.linspace(.235, 1.06, 200); vv = np.interp(uu, pu, pv)
    poly = [(X(u), y0 - v * 190) for u, v in zip(uu, vv)] + [(X(u), y0 + v * 190) for u, v in zip(uu[::-1], vv[::-1])]
    b.append(P(poly, fill=LIGHT, stroke=FWG, w=LW * 1.2))
    b.append(P([(X(.235), y0), (X(.80), y0)], close=False, w=LW * .8))
    bx = X(.50)
    for s in (-1, 1):
        b.append(f'<path d="M{bx - 40:.1f},{y0 + s * 34:.1f}Q{bx:.1f},{y0 + s * 6:.1f} {bx + 40:.1f},{y0 + s * 34:.1f}" fill="none" stroke="{DEEP}" stroke-width="{LW * 1.8:.2f}" stroke-linecap="round"/>')
    b.append(ellipse(bx, y0, 30, 14, fill=WHITE, stroke=DEEP, w=LW * 1.4))
    b.append(f'<rect x="{X(.68) - 14:.1f}" y="{y0 - 80:.1f}" width="28" height="160" rx="10" fill="{FWG}"/>')   # nerve ring
    b.append(circle(X(.93), y0 + 30, 26, fill=WHITE, stroke=FWG))                                              # gland nucleus
    save("nematode-root-feeder-stylet", "".join(b), Wd, Ht)


# ------------------------------------------------------------------ arbuscular mycorrhiza in a root
def mycorrhiza():
    Wd, Ht = 1500, 1000
    b = []
    top, bot = 260, 700
    b.append(f'<rect x="40" y="{top}" width="{Wd - 80}" height="{bot - top}" rx="30" fill="{WHITE}" stroke="{DEEP}" stroke-width="{LW * 1.8}"/>')
    # cortical cells in two rows, central vascular strand
    rows = [(top + 10, top + 150), (top + 150, top + 290)]
    cells = []
    for r, (y_a, y_b) in enumerate(rows):
        xs = np.cumsum(rng.uniform(140, 190, 12)) + 40 - (70 if r else 0)
        for x_a, x_b in zip(xs[:-1], xs[1:]):
            if x_b < Wd - 40:
                cells.append((x_a, y_a, x_b, y_b))
                b.append(f'<rect x="{x_a + 4:.1f}" y="{y_a + 4:.1f}" width="{x_b - x_a - 8:.1f}" height="{y_b - y_a - 8:.1f}" rx="18" fill="{WHITE}" stroke="{DEEP}" stroke-width="2.4"/>')
    b.append(f'<rect x="40" y="{top + 300}" width="{Wd - 80}" height="{bot - top - 310}" rx="20" fill="{LIGHT}" stroke="{FWG}" stroke-width="{LW}"/>')
    # intraradical hyphae running between cells
    hy = smooth([(60, top + 150), (300, top + 140), (560, top + 160), (820, top + 145), (1080, top + 155), (1440, top + 148)], 300)
    b.append(P(hy, close=False, w=10, stroke=FWG))
    # arbuscules in some cells: dichotomous little trees
    def tree(x, y, size, ang, d):
        if d == 0 or size < 6: return []
        e = (x + size * math.cos(ang), y + size * math.sin(ang))
        out = [f"M{x:.1f},{y:.1f}L{e[0]:.1f},{e[1]:.1f}"]
        for s in (-1, 1):
            out += tree(e[0], e[1], size * .68, ang + s * .5, d - 1)
        return out
    for i, (xa, ya, xb, yb) in enumerate(cells):
        if i % 3 == 1 and yb < top + 300:
            x = (xa + xb) / 2; y = yb - 18 if ya < top + 100 else ya + 18
            ang = -math.pi / 2 if ya < top + 100 else math.pi / 2
            segs = tree(x, y + (0 if ya < top + 100 else 0), 34, ang, 6)
            b.append(f'<path d="{"".join(segs)}" fill="none" stroke="{FWG}" stroke-width="3" stroke-linecap="round"/>')
        elif i % 5 == 3:
            b.append(ellipse((xa + xb) / 2, (ya + yb) / 2, 46, 32, fill=WHITE, stroke=FWG, w=LW * 1.3))   # vesicle
            b.append(stipple([((xa + xb) / 2 + 40 * math.cos(t), (ya + yb) / 2 + 26 * math.sin(t)) for t in np.linspace(0, 6.28, 40)], 30, 3, FWG))
    # entry point and extraradical hyphae with spores in the soil above
    ext = [smooth([(420, top), (400, 170), (300, 100), (160, 70)], 80), smooth([(400, 170), (520, 110), (640, 60)], 60),
           smooth([(980, top), (1010, 180), (1120, 120), (1260, 90)], 80), smooth([(1010, 180), (950, 90)], 30)]
    for l in ext:
        b.append(P(l, close=False, w=10, stroke=FWG))
    for x, y, r in ((160, 70, 40), (640, 60, 34), (1260, 90, 46)):
        b.append(circle(x, y, r, fill=WHITE, stroke=FWG, w=LW * 2))
        b.append(circle(x, y, r - 12, fill=LIGHT, stroke=FWG, w=LW))
    b.append(P([(420, top - 4), (420, top + 40)], close=False, w=14, stroke=FWG))
    b.append(P([(980, top - 4), (980, top + 40)], close=False, w=14, stroke=FWG))
    save("mycorrhiza-in-root", "".join(b), Wd, Ht)


# ------------------------------------------------------------------ Penicillium brush
def penicillium():
    Wd, Ht = 900, 1250; cx = 450
    b = [P([(cx, 1220), (cx, 640)], close=False, w=30, stroke=DEEP), P([(cx, 1215), (cx, 645)], close=False, w=22, stroke=WHITE)]
    for k in (1, 2, 3, 4):
        y = 1220 - k * 130
        b.append(P([(cx - 11, y), (cx + 11, y)], close=False, w=2.6))                 # septa in the stipe
    # metulae fanning from the top of the stipe, phialides on each, chains of conidia
    for ma in (-24, -8, 8, 24):
        a = math.radians(-90 + ma)
        m0 = (cx, 640); m1 = (cx + 150 * math.cos(a), 640 + 150 * math.sin(a))
        b.append(P([m0, m1], close=False, w=24, stroke=DEEP)); b.append(P([m0, m1], close=False, w=16, stroke=WHITE))
        for pa in (-9, 9):
            a2 = a + math.radians(pa)
            p0 = m1; p1 = (m1[0] + 70 * math.cos(a2), m1[1] + 70 * math.sin(a2))
            flask = [p0, (p0[0] + 12 * math.cos(a2 + 1.57), p0[1] + 12 * math.sin(a2 + 1.57)),
                     (p1[0] + 5 * math.cos(a2 + 1.57), p1[1] + 5 * math.sin(a2 + 1.57)), p1,
                     (p1[0] - 5 * math.cos(a2 + 1.57), p1[1] - 5 * math.sin(a2 + 1.57)),
                     (p0[0] - 12 * math.cos(a2 + 1.57), p0[1] - 12 * math.sin(a2 + 1.57))]
            b.append(P(flask, fill=WHITE, w=2.6))
            n = 9 - int(abs(ma) / 12)
            for j in range(n):                                   # newest conidium at the base of the chain
                r = 13
                cxj = p1[0] + (r + j * 2 * r * .96) * math.cos(a2) + 6 * math.sin(j * .9) * math.cos(a2 + 1.57)
                cyj = p1[1] + (r + j * 2 * r * .96) * math.sin(a2) + 6 * math.sin(j * .9) * math.sin(a2 + 1.57)
                b.append(circle(cxj, cyj, r, fill=LIGHT, stroke=FWG, w=2.4))
    save("penicillium-brush", "".join(b), Wd, Ht)


# ------------------------------------------------------------------ Streptomyces
def streptomyces():
    Wd, Ht = 1400, 900
    b = []
    sub = [smooth([(40, 760), (300, 720), (600, 780), (900, 730), (1360, 770)], 200),
           smooth([(300, 720), (380, 820), (520, 860)], 60), smooth([(900, 730), (980, 830), (1120, 850)], 60),
           smooth([(600, 780), (640, 860)], 30)]
    for l in sub:
        b.append(P(l, close=False, w=12, stroke=DEEP)); b.append(P(l, close=False, w=6, stroke=WHITE))
    aer = [((250, 735), [(250, 735), (230, 560), (280, 420)]), ((560, 770), [(560, 770), (600, 560), (560, 360)]),
           ((870, 735), [(870, 735), (900, 560), (980, 430)]), ((1150, 750), [(1150, 750), (1130, 600), (1180, 470)])]
    for base, ctrl in aer:
        l = smooth(ctrl, 80)
        b.append(P(l, close=False, w=12, stroke=DEEP)); b.append(P(l, close=False, w=6, stroke=WHITE))
        tip = np.array(l[-1]); d = (tip - np.array(l[-6])); d /= np.linalg.norm(d); n = np.array([-d[1], d[0]])
        spores = []
        for k in range(22):                                   # spiral chain of spores, seen side-on
            ph = k * 0.62
            p = tip + d * (14 + k * 9.5) + n * 26 * math.sin(ph)
            spores.append((math.cos(ph), p))
        for depth, p in sorted(spores, key=lambda q: q[0]):   # back of the coil first
            b.append(circle(p[0], p[1], 9.5, fill=LIGHT if depth > 0 else WHITE, stroke=FWG, w=2.2))
    save("streptomyces-spore-spirals", "".join(b), Wd, Ht)


def main():
    os.makedirs(OUT, exist_ok=True)
    for f in (arcella, difflugia, vorticella, root_feeder_head, mycorrhiza, penicillium, streptomyces):
        f()


if __name__ == "__main__":
    main()
