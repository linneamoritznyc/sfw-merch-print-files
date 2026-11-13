"""SFW Christmas card, 5 x 7 in at 300 dpi, white on SFW deep green.
Layout after a classic ornate card: double frame, scroll ornaments top, bottom and sides, four 'snowflakes',
two hanging 'stars'. Every ornament is a soil organism:
  scrolls       fungal hyphae, swelling and curling into a volute, branching into short hyphae that end in
                chains of round conidia (spores)
  centrepieces  a colonial flagellate fan: zooids with flagella on a branching stalk
  snowflakes    the sun animalcule Actinophrys (axopodia with granules) and the toothed mouth of Euglypha, end-on
  stars         Arcella seen from above, hanging on a hypha
Each scroll is drawn once and mirrored, so every ornament is exactly symmetric.
All shapes are unioned into one clean vector. Outputs out/christmas/.
"""
import io, math, os
import numpy as np
import cairosvg
from PIL import Image
from shapely.geometry import Point, Polygon, LineString
from shapely.ops import unary_union
from euglypha import text

W, H = 1500, 2100
GREEN, INK = "#22371F", "#FFFFFF"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "christmas")
SHAPES = []


# ------------------------------------------------------------------ primitives
def curve(p0, h0, L, kappa, n=500):
    """Curve by integrating curvature: kappa(u) with u in 0..1, heading in radians, y down."""
    ds = L / n; x, y, h = p0[0], p0[1], h0; pts = [(x, y)]
    for i in range(n):
        h += kappa(i / n) * ds
        x += math.cos(h) * ds; y += math.sin(h) * ds; pts.append((x, y))
    return np.array(pts)


def swell(pts, w0, w1, w2=None, peak=.3):
    """Variable width stroke: w0 at start, w1 at 'peak', w2 at end. Built from overlapping discs and hulls."""
    w2 = w1 * .25 if w2 is None else w2
    pts = np.asarray(pts, float); s = np.linspace(0, 1, len(pts))
    w = np.where(s < peak, w0 + (w1 - w0) * np.sin(s / peak * math.pi / 2), w2 + (w1 - w2) * np.cos((s - peak) / (1 - peak) * math.pi / 2))
    parts = []
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        parts.append(Point(*a).buffer(w[i] / 2, 8).union(Point(*b).buffer(w[i + 1] / 2, 8)).convex_hull)
    SHAPES.append(unary_union(parts))


def line(pts, w):
    SHAPES.append(LineString(pts).buffer(w / 2, 8))


def disc(c, r):
    SHAPES.append(Point(*c).buffer(r, 32))


def ring(c, r, w):
    SHAPES.append(Point(*c).buffer(r + w / 2, 64).difference(Point(*c).buffer(r - w / 2, 64)))


def ellipse(c, a, b, ang, w=None):
    t = np.linspace(0, 2 * math.pi, 48)
    p = np.c_[a * np.cos(t), b * np.sin(t)] @ np.array([[math.cos(ang), math.sin(ang)], [-math.sin(ang), math.cos(ang)]]) + c
    g = Polygon(p)
    SHAPES.append(g if w is None else g.buffer(w / 2).difference(g.buffer(-w / 2)))


class Frame:
    """Local frame: origin o, rotation rot, mirror flag. Local x along the rule, local y pointing into the card."""
    def __init__(self, o, rot, mirror=False):
        self.o, self.rot, self.m = np.array(o, float), rot, mirror

    def __call__(self, p):
        p = np.atleast_2d(np.asarray(p, float)).copy()
        if self.m:
            p[:, 0] *= -1
        c, s = math.cos(self.rot), math.sin(self.rot)
        return p @ np.array([[c, s], [-s, c]]) + self.o

    def heading(self, h):
        if self.m:
            h = math.pi - h
        return h + self.rot


def conidia(F, p, h, n=4, r=7.0):
    """Chain of round spores off a hyphal tip, shrinking outward."""
    x, y = p
    for k in range(n):
        rr = r * (1 - k * .17)
        x += math.cos(h) * (rr * 1.9 if k else rr * 1.2); y += math.sin(h) * (rr * 1.9 if k else rr * 1.2)
        disc(F([(x, y)])[0], rr)


def hypha(F, p0, h0, L, k0, k1, w, spores=4, sr=7.0, curl=False):
    """Thin side hypha. Ends in a spore chain, or curls into a tiny volute."""
    if curl:
        kap = lambda u: k0 + (k1 - k0) * u ** 2.2
    else:
        kap = lambda u: k0 + (k1 - k0) * u
    c = curve(p0, h0, L, kap, 200)
    swell(F(c), w * .9, w, w * .45 if spores else w * .2, peak=.15)
    if spores:
        h = math.atan2(*(c[-1] - c[-4])[::-1])
        conidia(F, c[-1], h, spores, sr)
    elif curl:
        disc(F(c[-1:])[0], w * .9)
    return c


def scroll(F, p0, h0, L, k0, k1, power, w0, w1, knob):
    """Main hyphal scroll: a curve whose curvature rises to a tight volute, ending in a round spore."""
    c = curve(p0, h0, L, lambda u: k0 + (k1 - k0) * u ** power)
    swell(F(c), w0, w1, w1 * .32, peak=.28)
    disc(F(c[-1:])[0], knob)
    for i in (.18, .33, .48):                                    # septa: fine cross walls along the hypha
        j = int(i * len(c)); t = c[j + 1] - c[j - 1]; t /= np.linalg.norm(t); n = np.array([-t[1], t[0]])
        wl = w0 + (w1 - w0) * .9
        line(F([c[j] - n * wl * .9, c[j] + n * wl * .9]), 2.2)
    return c


# ------------------------------------------------------------------ ornaments (drawn as right half, local y into card)
def half_main(F, s=1.0):
    a = scroll(F, (s * 18, s * 34), math.radians(-8), s * 470, -1 / (s * 420), -1 / (s * 13), 3.0, s * 7, s * 19, s * 10)
    b = scroll(F, (s * 14, s * 56), math.radians(28), s * 260, -1 / (s * 260), 1 / (s * 11), 2.6, s * 6, s * 13, s * 8)
    for frac, dh, L, k, sp in ((.22, -60, 70, .010, 3), (.40, -50, 90, .012, 4), (.55, 55, 80, -.016, 3)):
        j = int(frac * len(a)); t = a[j + 1] - a[j - 1]; h = math.atan2(t[1], t[0]) + math.radians(dh)
        hypha(F, a[j], h, s * L, 0, k / s, s * 5, spores=sp, sr=s * 5.5)
    j = int(.55 * len(b)); t = b[j + 1] - b[j - 1]; h = math.atan2(t[1], t[0]) + math.radians(55)
    hypha(F, b[j], h, s * 70, 0, .02 / s, s * 4.5, spores=0, curl=True)
    return a, b


def flagellate_fan(F, s=1.0, n=11, spread=110, L=150):
    """Colonial flagellate fan along local +y: stalk splits into rays, each with an oval zooid and a flagellum."""
    swell(F([(0, s * 10), (0, s * 46)]), s * 14, s * 12, s * 9, peak=.2)
    base = np.array([0, s * 46])
    for k in range(n):
        a = math.radians(90 + (k - (n - 1) / 2) * spread / (n - 1))
        Lk = s * L * (1 - .18 * (abs(k - (n - 1) / 2) / ((n - 1) / 2)) ** 2)
        bend = (k - (n - 1) / 2) / ((n - 1) / 2) * .0012 / s
        c = curve(base, a, Lk, lambda u: -bend, 120)
        swell(F(c), s * 5, s * 4.2, s * 2.6, peak=.1)
        h = math.atan2(*(c[-1] - c[-3])[::-1])
        zc = c[-1] + s * 13 * np.array([math.cos(h), math.sin(h)])
        ellipse(F([zc])[0], s * 13, s * 8, F.heading(h))
        fl = [zc + np.array([math.cos(h), math.sin(h)]) * (s * 12 + s * 34 * u) + np.array([-math.sin(h), math.cos(h)]) * s * 4 * math.sin(u * 10) for u in np.linspace(0, 1, 40)]
        swell(F(fl), s * 3, s * 2.4, s * .6, peak=.05)
    disc(F([base])[0], s * 9)


def centre_ornament(o, rot, s=1.0):
    for m in (False, True):
        half_main(Frame(o, rot, m), s)
    F = Frame(o, rot)
    flagellate_fan(F, s * .8)
    disc(F([(0, s * 30)])[0], s * 14)
    for k in range(5):
        a = math.radians(-90 + (k - 2) * 22)
        c = curve((0, s * 18), a, s * 34, lambda u: 0, 30)
        swell(F(c), s * 4, s * 3.4, s * 2, peak=.1)
        disc(F(c[-1:])[0], s * 4.5)


def side_ornament(o, rot, s=1.0):
    for m in (False, True):
        F = Frame(o, rot, m)
        a = scroll(F, (s * 10, s * 22), math.radians(-5), s * 300, -1 / (s * 360), -1 / (s * 10), 3.0, s * 6, s * 15, s * 8)
        scroll(F, (s * 8, s * 40), math.radians(35), s * 160, -1 / (s * 220), 1 / (s * 9), 2.6, s * 5, s * 10, s * 6.5)
        j = int(.4 * len(a)); t = a[j + 1] - a[j - 1]; h = math.atan2(t[1], t[0]) + math.radians(-55)
        hypha(F, a[j], h, s * 70, 0, .012 / s, s * 4.5, spores=3, sr=s * 5)
    F = Frame(o, rot)
    disc(F([(0, s * 26)])[0], s * 12)
    for k in range(5):
        a = math.radians(90 + (k - 2) * 24)
        c = curve((0, s * 34), a, s * 56, lambda u: 0, 30)
        swell(F(c), s * 4, s * 3.4, s * 2, peak=.1)
        disc(F(c[-1:])[0], s * 5)


def corner(o, rot, s=1.0):
    for m in (False, True):
        scroll(Frame(o, rot, m), (0, 0), 0, s * 150, 0, -1 / (s * 10), 3.2, s * 9, s * 9, s * 6)
    F = Frame(o, rot)
    disc(F([(0, 0)])[0], s * 9)
    for k in range(3):
        a = math.radians(90 + (k - 1) * 30)
        c = curve((0, s * 10), a, s * 44, lambda u: 0, 20)
        swell(F(c), s * 4, s * 3.4, s * 2, peak=.1); disc(F(c[-1:])[0], s * 4.5)


def actinophrys(c, R):
    c = np.array(c, float)
    for k in range(32):
        a = k / 32 * 2 * math.pi
        L = R * (1.0 if k % 2 == 0 else .74)
        u = np.array([math.cos(a), math.sin(a)])
        swell([c + u * R * .44, c + u * L], R * .045, R * .04, R * .01, peak=.05)
        for f in (.6, .78, .94):
            if f * R < L - 4:
                disc(c + u * f * R, R * .028)
    ring(c, R * .42, R * .04)
    for k in range(9):
        a = k / 9 * 2 * math.pi + .2
        ring(c + R * .27 * np.array([math.cos(a), math.sin(a)]), R * .07, R * .02)
    ring(c, R * .14, R * .03); disc(c, R * .07)


def euglypha_mouth(c, R):
    c = np.array(c, float)
    for k in range(14):
        a = (k + .5) / 14 * 2 * math.pi
        ellipse(c + R * .84 * np.array([math.cos(a), math.sin(a)]), R * .16, R * .1, a, R * .03)
    for k in range(10):
        a0, a1 = (k - .46) / 10 * 2 * math.pi, (k + .46) / 10 * 2 * math.pi
        outer = [c + R * .64 * np.array([math.cos(t), math.sin(t)]) for t in np.linspace(a0, a1, 12)]
        teeth = [c + (R * .32 - (R * .08 if j % 2 else 0)) * np.array([math.cos(a0 + j / 8 * (a1 - a0)), math.sin(a0 + j / 8 * (a1 - a0))]) for j in range(8, -1, -1)]
        g = Polygon(outer + teeth)
        SHAPES.append(g.buffer(R * .016).difference(g.buffer(-R * .016)))
    ring(c, R * .16, R * .03); disc(c, R * .07)


def arcella_star(c, R, top):
    c = np.array(c, float)
    line([top, (c[0], c[1] + (R if top[1] > c[1] else -R))], 3.5)
    ring(c, R, R * .06)
    for rr in (R * .58, R * .8):
        n = int(rr / R * 24)
        for k in range(n):
            a = k / n * 2 * math.pi + (rr / R)
            q = c + rr * np.array([math.cos(a), math.sin(a)]); s = R * .075
            hexa = Polygon([q + s * np.array([math.cos(a + j * math.pi / 3), math.sin(a + j * math.pi / 3)]) for j in range(6)])
            SHAPES.append(hexa.buffer(R * .01).difference(hexa.buffer(-R * .012)))
    ring(c, R * .32, R * .05); disc(c, R * .13)


# ------------------------------------------------------------------ card
def place(g, o, rot):
    from shapely import affinity
    g = affinity.rotate(g, rot, origin=(0, 0))
    return affinity.translate(g, *o)


def frame():
    from christmas_ornament import ornament
    m1, m2 = 64, 88
    for m, w in ((m1, 5), (m2, 2.4)):
        r = Polygon([(m, m), (W - m, m), (W - m, H - m), (m, H - m)])
        SHAPES.append(r.buffer(w / 2, join_style=2).difference(r.buffer(-w / 2, join_style=2)))
    big, small = ornament(1.0), ornament(.58)
    SHAPES.append(place(big, (W / 2, m2 + 16), 0))
    SHAPES.append(place(big, (W / 2, H - m2 - 16), 180))
    SHAPES.append(place(small, (m2 + 14, H / 2), -90))
    SHAPES.append(place(small, (W - m2 - 14, H / 2), 90))
    for c in ((m2 + 22, m2 + 22), (W - m2 - 22, m2 + 22), (m2 + 22, H - m2 - 22), (W - m2 - 22, H - m2 - 22)):
        disc(c, 9)
    x = m2 + 24
    for y0, y1 in ((150, H / 2 - 300), (H / 2 + 300, H - 150)):
        for xx in (x, W - x):
            swell([(xx, y) for y in np.linspace(y0, y1, 60)], 1, 4, 1, peak=.5)
    actinophrys((320, 590), 104); euglypha_mouth((W - 320, 590), 100)
    euglypha_mouth((320, H - 590), 100); actinophrys((W - 320, H - 590), 104)
    arcella_star((W / 2, 600), 80, (W / 2, 445))
    arcella_star((W / 2, H - 600), 80, (W / 2, H - 445))


def to_d(g):
    out = []
    for p in getattr(g, "geoms", [g]):
        for r in [p.exterior] + list(p.interiors):
            out.append("M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in np.array(r.coords)) + "Z")
    return "".join(out)


def build():
    SHAPES.clear(); frame()
    return to_d(unary_union(SHAPES).simplify(.25))


def card(d, with_text=True, bg=True):
    body = (f'<rect width="{W}" height="{H}" fill="{GREEN}"/>' if bg else "") + f'<path fill="{INK}" fill-rule="evenodd" d="{d}"/>'
    if with_text:
        for t, sz, y in (("Merry Christmas", 124, 950), ("&", 92, 1075), ("Happy New Year", 124, 1215)):
            body += text(t, sz, W / 2, y, anchor="middle", color=INK)[0]
        body += text("SOIL FOOD WEB FOUNDATION", 28, W / 2, 1335, fnt="eb-garamond-latin-600-normal.woff2", anchor="middle", color=INK, track=240)[0]
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{body}</svg>\n'


def main():
    os.makedirs(OUT, exist_ok=True)
    d = build()
    for tag, wt in (("with-text", True), ("no-text", False)):
        svg = card(d, wt)
        open(os.path.join(OUT, f"sfw-christmas-card-{tag}.svg"), "w").write(svg)
        im = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(), output_width=W, output_height=H))).convert("RGB")
        im.save(os.path.join(OUT, f"sfw-christmas-card-{tag}.png"), dpi=(300, 300))
        cairosvg.svg2pdf(bytestring=svg.encode(), write_to=os.path.join(OUT, f"sfw-christmas-card-{tag}.pdf"))
    open(os.path.join(OUT, "sfw-christmas-frame-white.svg"), "w").write(card(d, False, False))


if __name__ == "__main__":
    main()
