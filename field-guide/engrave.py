"""SFW field-guide organisms as engravings: white line on deep green, the look of the Haeckel fan.

Technique (all vector, all coded):
  - every stroke is a tapered filled shape that swells in the middle and thins to a point, like a burin line
  - bodies are modelled with cross-contour hatching that follows the form, dense on the shadow side
  - a slight smooth wobble on every line, so nothing looks mechanical
  - cilia and flagella as long flowing tapered curves
Anatomy as in the field guide (SOURCES.md). Output: out/engraved/<name>-{white,green,black}.svg, -preview.png.
"""
import io, math, os
import numpy as np
import cairosvg
from PIL import Image
from shapely.geometry import Point, Polygon, LineString
from shapely import affinity
from shapely.ops import unary_union

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "engraved")
S = 2400
rng = np.random.default_rng(11)


def spline(ctrl, n=200, closed=False):
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


def wobble(p, amp=1.2, freq=3):
    p = np.asarray(p, float)
    if len(p) < 3:
        return p
    t = np.gradient(p, axis=0); nrm = np.linalg.norm(t, axis=1)[:, None]; t = t / np.maximum(nrm, 1e-9)
    n = np.c_[-t[:, 1], t[:, 0]]
    s = np.linspace(0, 1, len(p)); ph = rng.uniform(0, 6.28)
    return p + n * (amp * np.sin(s * freq * 2 * math.pi + ph))[:, None]


class Plate:
    def __init__(self, w=S, h=S):
        self.w, self.h = w, h
        self.fills = []

    def stroke(self, pts, w, taper=(0.15, 0.15), wob=1.0):
        """Tapered burin stroke along pts, max width w."""
        p = wobble(pts, wob) if wob else np.asarray(pts, float)
        if len(p) < 2:
            return
        if len(p) == 2:
            p = np.linspace(p[0], p[1], 12)
        t = np.gradient(p, axis=0); t /= np.maximum(np.linalg.norm(t, axis=1)[:, None], 1e-9)
        n = np.c_[-t[:, 1], t[:, 0]]
        s = np.linspace(0, 1, len(p))
        a, b = taper
        prof = np.minimum(1, np.minimum(s / max(a, 1e-3), (1 - s) / max(b, 1e-3))) ** .7
        hw = (w / 2) * np.maximum(prof, .08)
        poly = np.vstack([p + n * hw[:, None], (p - n * hw[:, None])[::-1]])
        self.fills.append("M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in poly) + "Z")

    def ring(self, geom, w, wob=.8):
        for g in getattr(geom, "geoms", [geom]):
            if g.is_empty: continue
            c = np.array(g.exterior.coords)
            self.stroke(c, w, taper=(0.0001, 0.0001), wob=wob)
            for r in g.interiors:
                self.stroke(np.array(r.coords), w * .7, taper=(0.0001, 0.0001), wob=wob)

    def dot(self, x, y, r):
        self.fills.append(f"M{x - r:.1f},{y:.1f}a{r:.1f},{r:.1f} 0 1,0 {2 * r:.1f},0a{r:.1f},{r:.1f} 0 1,0 {-2 * r:.1f},0Z")

    def svg(self, ink):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}">'
                f'<path fill="{ink}" d="{"".join(self.fills)}"/></svg>\n')

    def save(self, name):
        os.makedirs(OUT, exist_ok=True)
        for tag, ink in (("white", "#FFFFFF"), ("green", "#156826"), ("black", "#000000")):
            open(os.path.join(OUT, f"{name}-{tag}.svg"), "w").write(self.svg(ink))
        png = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=self.svg("#FFFFFF").encode(), output_width=self.w, output_height=self.h))).convert("RGBA")
        bg = Image.new("RGBA", png.size, "#22371F"); bg.alpha_composite(png)
        bg.convert("RGB").save(os.path.join(OUT, f"{name}-preview.png"))
        png.save(os.path.join(OUT, f"{name}-white.png"))


def hatch_blob(pl, geom, light=(-.6, -.8), spacing=11, w=2.6, reach=.5):
    """Contour hatching: tapered partial rings hugging the shadow side of a shape."""
    minx, miny, maxx, maxy = geom.bounds
    size = max(maxx - minx, maxy - miny)
    c = np.array(geom.centroid.coords[0]); L = np.array(light, float); L /= np.linalg.norm(L)
    k = 1
    while k * spacing < size * reach * .5:
        ring = geom.buffer(-k * spacing)
        if ring.is_empty: break
        for g in getattr(ring, "geoms", [ring]):
            pts = np.array(g.exterior.coords)
            d = (pts - c) @ (-L) / (size / 2)                       # +1 on the shadow side
            thr = -.1 + k * spacing / (size * reach * .5) * .9       # deeper rings cover less of the outline
            keep = d > thr
            runs, cur = [], []
            for p, kp in zip(pts, keep):
                if kp: cur.append(p)
                elif len(cur) > 6: runs.append(cur); cur = []
                else: cur = []
            if len(cur) > 6: runs.append(cur)
            for r in runs:
                pl.stroke(np.array(r), w * (1 - .5 * min(1, k / 10)), taper=(.3, .3))
        k += 1


def stipple(pl, geom, n, r=2.2, light=(-.6, -.8), power=2.0):
    minx, miny, maxx, maxy = geom.bounds
    c = np.array(geom.centroid.coords[0]); L = np.array(light, float); L /= np.linalg.norm(L)
    size = max(maxx - minx, maxy - miny) / 2
    from shapely.prepared import prep
    pg = prep(geom); got = 0; tries = 0
    while got < n and tries < n * 60:
        tries += 1
        x, y = rng.uniform(minx, maxx), rng.uniform(miny, maxy)
        t = ((np.array([x, y]) - c) @ (-L)) / size
        if rng.random() > min(1, max(0, (t + 1) / 2)) ** power: continue
        if pg.contains(Point(x, y)):
            pl.dot(x, y, r * rng.uniform(.7, 1.2)); got += 1


# ------------------------------------------------------------------ Colpoda
def colpoda():
    pl = Plate(); cx, cy = S / 2, S / 2 + 40
    A, B = 760, 520
    th0, depth, wid = 1.5 * math.pi - .28, B * .3, .42
    pts = []
    for t in np.linspace(0, 2 * math.pi, 600, endpoint=False):
        x, y = A * math.cos(t), B * math.sin(t)
        if x < 0: y *= 1 - .1 * (-x / A)
        d = (t - th0 + math.pi) % (2 * math.pi) - math.pi
        y += depth * math.exp(-(d / wid) ** 2)
        pts.append((cx + x, cy + y))
    pts = np.array(pts); body = Polygon(pts)
    rot = lambda g: affinity.rotate(g, -14, origin=(cx, cy))
    # cilia: hundreds of flowing tapered strokes, a metachronal wave running round the cell
    ring = LineString(np.vstack([pts, pts[:1]]))
    N = 420
    for i in range(N):
        s = i / N * ring.length
        p = np.array(ring.interpolate(s).coords[0]); q = np.array(ring.interpolate(s + 1).coords[0])
        t = (q - p) / np.linalg.norm(q - p); n = np.array([t[1], -t[0]])
        if body.contains(Point(*(p + n * 3))): n = -n
        L = 120 + 18 * math.sin(i / N * 2 * math.pi * 3)
        bend = math.radians(32 + 16 * math.sin(i / N * 2 * math.pi * 22))
        dvec = n * math.cos(bend) + t * math.sin(bend)
        c = [p, p + n * L * .45 + t * L * .06, p + dvec * L * .85, p + dvec * L + t * L * .12]
        pl.stroke(spline(c, 24), 3.0, taper=(.05, .9), wob=.6)
    pl.ring(body, 7)
    pl.ring(body.buffer(-22), 2.4)                                           # pellicle
    # kineties: rows of basal bodies as fine dotted curves
    for k in np.linspace(-.85, .85, 15):
        row = []
        for x in np.arange(-A * .95, A * .95, 6):
            u = x / A
            y = k * B * math.sqrt(max(0, 1 - u * u)) * .93 + .1 * B * (1 - u * u)
            row.append((cx + x, cy + y))
        row = [p for p in row if body.buffer(-40).contains(Point(*p))]
        for j in range(0, len(row), 3):
            pl.dot(row[j][0], row[j][1], 2.4)
    hatch_blob(pl, body.buffer(-30), spacing=12, w=3.0, reach=.42)
    # oral vestibulum on the concave side, oral cilia sweeping into it
    notch = pts[int(th0 / (2 * math.pi) * 600)]
    pocket = LineString([tuple(notch + [0, -30]), tuple(notch + [30, 150]), tuple(notch + [90, 260])]).buffer(64).intersection(body.buffer(-6))
    pl.ring(pocket, 4)
    hatch_blob(pl, pocket, light=(0, -1), spacing=8, w=2.2, reach=1.2)
    for k in range(16):
        u = k / 15
        a0 = notch + np.array([-60 + 130 * u, 10 + 24 * math.sin(u * math.pi)])
        pl.stroke(spline([a0, a0 + [10, 60], notch + [40 + 50 * (u - .5), 150 + 30 * math.sin(u * math.pi)]], 16), 2.6, taper=(.1, .8))
    # macronucleus, food vacuoles with bacteria, contractile vacuole at the rear
    nuc = Point(cx + 110, cy + 90).buffer(118, 96)
    pl.ring(nuc, 4.4); hatch_blob(pl, nuc, spacing=9, w=2.2, reach=.7); stipple(pl, nuc, 240, 2.4)
    pl.dot(cx - 40, cy + 170, 16)
    for fx, fy, r in ((-.55, .05, 70), (-.3, .45, 64), (.45, -.38, 66), (.52, .42, 56), (-.65, -.35, 46), (.15, -.42, 44)):
        g = Point(cx + fx * A, cy + fy * B).buffer(r, 64)
        pl.ring(g, 3.2); hatch_blob(pl, g, spacing=7, w=1.8, reach=.8)
        for _ in range(3):
            a = rng.uniform(0, math.pi); x, y = cx + fx * A + rng.uniform(-.35, .35) * r, cy + fy * B + rng.uniform(-.35, .35) * r
            pl.stroke([(x - math.cos(a) * r * .28, y - math.sin(a) * r * .28), (x + math.cos(a) * r * .28, y + math.sin(a) * r * .28)], 7, taper=(.3, .3), wob=0)
    cv = Point(cx + A * .82, cy - B * .04).buffer(58, 64)
    pl.ring(cv, 3.6); pl.ring(cv.buffer(-14), 1.8)
    pl.fills = [f'<g transform="rotate(-14 {cx} {cy})">'] if False else pl.fills
    pl.save("colpoda")


# ------------------------------------------------------------------ bacterial-feeding nematode
def nematode():
    pl = Plate(S, 1400)
    cl = spline([(150, 760), (520, 560), (900, 640), (1250, 860), (1600, 820), (1950, 580), (2260, 640)], 900)
    u = np.linspace(0, 1, len(cl))
    t = np.gradient(cl, axis=0); t /= np.linalg.norm(t, axis=1)[:, None]; n = np.c_[-t[:, 1], t[:, 0]]
    half = 64 * np.minimum(1, .5 + .5 * np.clip(u / .09, 0, 1) ** .6) * np.where(u > .9, np.clip((1 - u) / .1, .02, 1) ** 1.1, 1)
    left, right = cl + n * half[:, None], cl - n * half[:, None]
    pl.stroke(left, 7, taper=(.01, .2)); pl.stroke(right, 7, taper=(.01, .2))
    cap = [tuple(cl[0] - t[0] * half[0] * .9 * math.cos(q) + n[0] * half[0] * math.sin(q)) for q in np.linspace(-math.pi / 2, math.pi / 2, 30)]
    pl.stroke(cap, 7, taper=(.2, .2))
    # cross-contour hatching across the body, heavier on the lower (shadow) side: makes it read as a tube
    for k in np.arange(0.03, .97, .0065):
        i = int(k * (len(cl) - 1))
        vs = np.linspace(-.15, 1, 18)
        arc = [tuple(cl[i] - n[i] * half[i] * v + t[i] * half[i] * .28 * (1 - v * v)) for v in vs]
        pl.stroke(arc, 2.0, taper=(.6, .15), wob=.3)
    # pharynx: lumen, corpus with median swelling, isthmus, basal bulb with valve
    i_b = int(.15 * len(cl))
    pl.stroke(cl[3:i_b], 2.4, taper=(.1, .1))
    prof = np.interp(u[:i_b + 30], [0, .06, .08, .1, .115, .135, .145, .16, .17], [.2, .3, .44, .3, .18, .18, .5, .5, .2])
    for sgn in (1, -1):
        pl.stroke(cl[2:i_b + 30] + sgn * n[2:i_b + 30] * (half[2:i_b + 30] * prof[2:])[:, None], 3.2, taper=(.05, .05))
    bb = cl[int(.152 * len(cl))]
    pl.ring(Point(*bb).buffer(26), 3)
    pl.stroke([tuple(bb - t[i_b] * 14), tuple(bb + t[i_b] * 14)], 4, taper=(.3, .3), wob=0)
    nr = int(.125 * len(cl))
    for f in np.linspace(-.85, .85, 9):
        pl.dot(*(cl[nr] + n[nr] * half[nr] * f), 4)
    # intestine: granules in the gut, two walls
    i0, i1 = int(.2 * len(cl)), int(.88 * len(cl))
    for sgn in (1, -1):
        pl.stroke(cl[i0:i1] + sgn * n[i0:i1] * (half[i0:i1] * .5)[:, None], 2.4, taper=(.02, .02))
    for _ in range(1600):
        k = rng.uniform(.2, .88); i = int(k * (len(cl) - 1)); v = rng.uniform(-.45, .45)
        p = cl[i] + n[i] * half[i] * v
        pl.dot(p[0], p[1], rng.uniform(1.6, 3.2) * (1 + .6 * (v < 0)))
    # eggs either side of the vulva, vulva, anus, pointed tail
    for k in (.44, .5, .58, .64):
        i = int(k * (len(cl) - 1))
        e = affinity.rotate(affinity.scale(Point(*cl[i]).buffer(1, 48), 52, 34), math.degrees(math.atan2(t[i][1], t[i][0])), origin=tuple(cl[i]))
        pl.ring(e, 3.2); hatch_blob(pl, e, spacing=6, w=1.6, reach=.9)
    iv = int(.54 * len(cl)); pl.stroke([tuple(cl[iv] - n[iv] * half[iv] * .5), tuple(cl[iv] - n[iv] * half[iv] * 1.02)], 4, taper=(.2, .2), wob=0)
    ia = int(.9 * len(cl)); pl.stroke([tuple(cl[ia] - n[ia] * half[ia] * .2), tuple(cl[ia] - n[ia] * half[ia] * 1.02)], 3.4, taper=(.2, .2), wob=0)
    pl.save("nematode-bacterial-feeder")


if __name__ == "__main__":
    colpoda(); nematode()
