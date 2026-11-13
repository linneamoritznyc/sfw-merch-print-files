"""SFW ornamental plates: single-ink line engraving in the style of the Haeckel fan.
Fine white lines only, contour hatching on the shadow side, mirror-symmetric compositions.
Anatomy follows SOURCES.md (Vorticella, Actinophrys, Aspergillus).

Output: out/ornament/<name>-white.svg / -green.svg / -black.svg (transparent), plus -preview.png on deep green.
Usage: python3 ornament.py
"""
import io, math, os
import numpy as np
import cairosvg
from PIL import Image
from shapely.geometry import Point, Polygon, LineString, box
from shapely import affinity
from shapely.ops import unary_union

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "ornament")
S = 2000
W1, W2, W3 = 2.0, 3.0, 4.6           # fine, medium, contour
INK = "#FFFFFF"
rng = np.random.default_rng(5)


def pts_d(p, close=False):
    p = np.asarray(p)
    return "M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in p) + ("Z" if close else "")


def geom_d(g):
    out = []
    for part in getattr(g, "geoms", [g]):
        if part.is_empty:
            continue
        if part.geom_type == "Polygon":
            out.append(pts_d(np.array(part.exterior.coords), True))
            out += [pts_d(np.array(r.coords), True) for r in part.interiors]
        elif part.geom_type in ("LineString", "LinearRing"):
            out.append(pts_d(np.array(part.coords)))
        elif part.geom_type == "MultiLineString":
            out += [pts_d(np.array(l.coords)) for l in part.geoms]
    return "".join(out)


class Plate:
    def __init__(self):
        self.paths = {}

    def add(self, d, w):
        self.paths.setdefault(w, []).append(d)

    def line(self, p, w=W1):
        self.add(pts_d(p), w)

    def outline(self, g, w=W3):
        self.add(geom_d(g.boundary if g.geom_type in ("Polygon", "MultiPolygon") else g), w)

    def hatch(self, g, light=(-.6, -.8), step=9, depth=.55, w=W1):
        """Contour hatching: inner offset rings, kept only on the side away from the light."""
        if g.is_empty:
            return
        minx, miny, maxx, maxy = g.bounds
        size = max(maxx - minx, maxy - miny)
        lit = affinity.translate(g, -light[0] * size * depth, -light[1] * size * depth)
        shadow = g.difference(lit)
        k = 1
        while k * step < size * .16:
            ring = g.buffer(-k * step)
            if ring.is_empty:
                break
            seg = ring.boundary.intersection(shadow.buffer(-1))
            if not seg.is_empty:
                self.add(geom_d(seg), w * (1 - .4 * min(1, k / 12)))
            k += 1

    def svg(self, ink):
        body = "".join(f'<path d="{"".join(ds)}" fill="none" stroke="{ink}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>'
                       for w, ds in self.paths.items())
        return f'<svg xmlns="http://www.w3.org/2000/svg" width="{S}" height="{S}" viewBox="0 0 {S} {S}">{body}</svg>\n'

    def save(self, name):
        os.makedirs(OUT, exist_ok=True)
        for tag, ink in (("white", "#FFFFFF"), ("green", "#156826"), ("black", "#000000")):
            open(os.path.join(OUT, f"{name}-{tag}.svg"), "w").write(self.svg(ink))
        png = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=self.svg("#FFFFFF").encode(), output_width=S, output_height=S))).convert("RGBA")
        bg = Image.new("RGBA", (S, S), "#22371F"); bg.alpha_composite(png)
        bg.convert("RGB").save(os.path.join(OUT, f"{name}-preview.png"))
        png.save(os.path.join(OUT, f"{name}-white.png"))


def mirror_pts(p, cx=S / 2):
    return [(2 * cx - x, y) for x, y in p]


# ------------------------------------------------------------------ 1 colony of stalked ciliates (vorticellid colony)
def bell(pl, base, ang, size, contracted=False):
    """One zooid: bell-shaped body with peristome, crown of oral cilia, C-shaped macronucleus, food vacuoles."""
    t = np.array([math.cos(ang), math.sin(ang)]); n = np.array([-t[1], t[0]])
    P = lambda u, v: tuple(np.array(base) + t * u * size + n * v * size)
    if contracted:
        g = Point(*P(.45, 0)).buffer(size * .42)
        pl.outline(g); pl.hatch(g, step=7)
        for k in range(14):
            a = k / 14 * 2 * math.pi
            c = np.array(P(.45, 0)); pl.line([tuple(c + .3 * size * np.array([math.cos(a), math.sin(a)])), tuple(c + .38 * size * np.array([math.cos(a + .2), math.sin(a + .2)]))], W1)
        return
    prof = [P(0, 0)] + [P(u, .5 * (u ** .8) * (1.05 - .25 * u)) for u in np.linspace(.02, 1, 30)]
    body = Polygon(prof + [P(1, 0)] + [P(u, -.5 * (u ** .8) * (1.05 - .25 * u)) for u in np.linspace(1, .02, 30)])
    pl.outline(body); pl.hatch(body, step=8)
    for v in np.linspace(-.3, .3, 7):                                      # pellicle striations
        pl.line([P(.12, v * .2), P(.6, v * .75), P(.98, v * 1.3)], W1 * .8)
    rim = [P(1 + .05 * math.sin(q) ** 2, .5 * math.cos(q) * 1.1) for q in np.linspace(0, 2 * math.pi, 50)]
    pl.add(pts_d(rim, True), W2)                                           # peristome lip
    for k in range(34):                                                    # crown of oral cilia
        q = k / 33 * math.pi
        a0 = np.array(P(1.02, .53 * math.cos(q)))
        spread = math.cos(q)
        tip = a0 + t * size * .32 + n * size * spread * .28
        mid = a0 + t * size * .2 + n * size * spread * .08
        pl.add(f"M{a0[0]:.1f},{a0[1]:.1f}Q{mid[0]:.1f},{mid[1]:.1f} {tip[0]:.1f},{tip[1]:.1f}", W1)
    mac = [P(.5 + .22 * math.cos(q), .22 * math.sin(q)) for q in np.linspace(.4 * math.pi, 1.8 * math.pi, 30)]
    pl.line(mac, W2 * 1.4)
    for u, v, r in ((.72, .15, .055), (.42, -.18, .05), (.8, -.2, .045)):
        pl.outline(Point(*P(u, v)).buffer(r * size), W1)


def stalk(pl, a, b, w):
    a, b = np.array(a), np.array(b); t = (b - a) / np.linalg.norm(b - a); n = np.array([-t[1], t[0]])
    pl.line([tuple(a + n * w / 2), tuple(b + n * w / 2)], W2); pl.line([tuple(a - n * w / 2), tuple(b - n * w / 2)], W2)
    L = np.linalg.norm(b - a); k = max(2, int(L / 46))
    pl.line([tuple(a + t * L * u + n * w * .22 * math.sin(u * k * 2 * math.pi)) for u in np.linspace(0, 1, k * 16)], W1 * .9)   # spasmoneme


def colony():
    pl = Plate()
    cx = S / 2

    def grow(p, ang, L, d, path, mirror):
        e = (p[0] + L * math.cos(ang), p[1] + L * math.sin(ang))
        stalk(pl, p, e, 14 + d * 3)
        if d == 0:
            bell(pl, e, ang, 140, contracted=(path in ("lrl",)), )
            return
        spread = math.radians(20 + 7 * d)
        sgn = -1 if mirror else 1
        grow(e, ang - sgn * spread, L * .72, d - 1, path + "l", mirror)
        grow(e, ang + sgn * spread * .55, L * .7, d - 1, path + "r", mirror)

    stalk(pl, (cx, 1960), (cx, 1300), 30)
    pl.outline(Polygon([(cx - 70, 1960), (cx + 70, 1960), (cx + 20, 1930), (cx - 20, 1930)]))
    for mirror in (False, True):
        a0 = -math.pi / 2 - .3 if not mirror else -math.pi / 2 + .3
        grow((cx, 1300), a0, 330, 3, "", mirror)
    pl.save("vorticellid-colony")


# ------------------------------------------------------------------ 2 sun animalcule, radial
def sun_animalcule():
    pl = Plate(); c = np.array([S / 2, S / 2]); R = 330
    jit = rng.normal(0, .012, 61); lens = rng.uniform(760, 920, 61)
    for k in range(120):                                                    # stiff axopodia from the nucleus surface
        h = k if k <= 60 else 120 - k
        a = k / 120 * 2 * math.pi + (jit[h] if k <= 60 else -jit[h])
        u = np.array([math.cos(a + math.pi / 2), math.sin(a + math.pi / 2)])
        L = lens[h]
        pl.line([tuple(c + u * 120), tuple(c + u * L)], W1)
        for f in np.arange(R + 40, L, 70):
            g = c + u * (f + (k % 3) * 12)
            pl.add(geom_d(Point(*g).buffer(5).boundary), W1)                 # extrusome granules
    body = Point(*c).buffer(R, 128)
    pl.outline(body, W3 * 1.2)
    vac = []                                                                # foamy vacuolated outer cytoplasm, packed
    for _ in range(9000):
        if len(vac) > 170: break
        a = rng.uniform(0, 2 * math.pi); r = rng.uniform(150, R - 14); rr = rng.uniform(14, 34)
        p = c + r * np.array([math.cos(a), math.sin(a)])
        if r + rr < R - 6 and all(np.linalg.norm(p - q) > rr + qr + 3 for q, qr in vac):
            vac.append((p, rr))
    for p, rr in vac:
        g = Point(*p).buffer(rr, 32); pl.outline(g, W1 * 1.2)
        pl.hatch(g, step=5, w=W1 * .8)
    nuc = Point(*c).buffer(120, 96); pl.outline(nuc, W3)
    for r in range(60, 116, 9): pl.add(geom_d(Point(*c).buffer(r, 96).boundary), W1 * .8)
    pl.outline(Point(*c).buffer(46), W2)
    pl.save("sun-animalcule-actinophrys")


# ------------------------------------------------------------------ 3 Aspergillus head, radial chains
def aspergillus():
    pl = Plate(); cx = S / 2; vy = 760
    st = [(cx - 26, 1960), (cx - 22, 1100), (cx - 30, 880)]
    pl.line(st, W3); pl.line(mirror_pts(st), W3)
    for y in (1300, 1600):
        pl.line([(cx - 22, y), (cx + 22, y)], W2)
    foot = [(cx - 26, 1960), (cx - 140, 1960)]
    pl.line(foot, W3); pl.line(mirror_pts(foot), W3)
    ves = Point(cx, vy).buffer(150, 128)
    pl.outline(ves); pl.hatch(ves, step=7)
    stp = Polygon(st + mirror_pts(st)[::-1]); pl.hatch(stp, light=(-1, 0), step=6, depth=.9)
    for k in range(57):                                                    # phialides and long chains of round conidia
        a = math.radians(-198 + k * 216 / 56)
        u = np.array([math.cos(a), math.sin(a)]); n = np.array([-u[1], u[0]])
        p0 = np.array([cx, vy]) + u * 150; p1 = np.array([cx, vy]) + u * 230
        ph = Polygon([tuple(p0 + n * 14), tuple(p1 + n * 7), tuple(p1 - n * 7), tuple(p0 - n * 14)])
        pl.outline(ph, W2)
        r = 12
        for j in range(int(22 - abs(k - 28) * .2)):
            q = p1 + u * (r + j * 2 * r * .95)
            g = Point(*q).buffer(r - 1, 24)
            pl.outline(g, W1 * 1.3)
            if j % 2 == 0:
                pl.add(geom_d(Point(*(q - u * 4 + n * 3)).buffer(r * .45).boundary), W1 * .7)
    pl.save("aspergillus-radiant")


if __name__ == "__main__":
    colony(); sun_animalcule(); aspergillus()
