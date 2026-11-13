"""Cubist soil: a nematode, a testate amoeba and fungal hyphae, each seen from several sides at once.
The picture plane is cut by straight lines into facets; inside each facet the organisms are shown from a
slightly different viewpoint (shifted, turned, rescaled), in flat colour planes with hatching and dot textures.
All vector. Output out/cubist/<name>.svg + .png
"""
import io, math, os, sys
import numpy as np
import cairosvg
from PIL import Image
from shapely.geometry import Polygon, LineString, Point, box, MultiLineString
from shapely.ops import polygonize, unary_union
from shapely import affinity

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "cubist")
INK = "#141414"
PAL = {"deep": "#22371F", "fwg": "#156826", "light": "#59A66C", "sage": "#B3BEB1", "cream": "#F3F0E6",
       "violet": "#6E5A9C", "lilac": "#B9A9DA", "blue": "#3C6FA8", "soil": "#4F3433", "ochre": "#C9A54A"}


def bez(P, n=200):
    P = np.array(P, float); t = np.linspace(0, 1, n)[:, None]
    return (1 - t) ** 3 * P[0] + 3 * (1 - t) ** 2 * t * P[1] + 3 * (1 - t) * t ** 2 * P[2] + t ** 3 * P[3]


def tube(c, w0, w1, tail=.12, head=.04):
    """Body outline around centreline c: blunt head, long taper to the tail."""
    t = np.gradient(c, axis=0); t /= np.linalg.norm(t, axis=1)[:, None]; n = np.c_[-t[:, 1], t[:, 0]]
    u = np.linspace(0, 1, len(c))
    w = np.where(u < head, w0 * np.sqrt(u / head) + 2, np.where(u > 1 - tail, w1 * (1 - u) / tail + 2, w1 + (w0 - w1) * (1 - u)))
    return Polygon(np.r_[c + n * w[:, None] / 2, (c - n * w[:, None] / 2)[::-1]]).buffer(0)


def d_of(g):
    out = []
    for p in getattr(g, "geoms", [g]):
        if p.is_empty: continue
        if p.geom_type == "Polygon":
            for r in [p.exterior] + list(p.interiors):
                out.append("M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in np.array(r.coords)) + "Z")
        elif p.geom_type in ("LineString", "LinearRing"):
            out.append("M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in np.array(p.coords)))
        elif hasattr(p, "geoms"):
            out.append(d_of(p))
    return "".join(out)


class Pic:
    def __init__(s, W, H):
        s.W, s.H, s.el = W, H, []

    def fill(s, g, col):
        if not g.is_empty: s.el.append(f'<path d="{d_of(g)}" fill="{col}" fill-rule="evenodd"/>')

    def stroke(s, g, w, col=INK):
        if not g.is_empty: s.el.append(f'<path d="{d_of(g)}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>')

    def svg(s):
        return f'<svg xmlns="http://www.w3.org/2000/svg" width="{s.W}" height="{s.H}" viewBox="0 0 {s.W} {s.H}">{"".join(s.el)}</svg>\n'


def facets(W, H, rng, n=13):
    lines = [LineString([(0, 0), (W, 0), (W, H), (0, H), (0, 0)])]
    for _ in range(n):
        a = rng.uniform(0, math.pi); cx, cy = rng.uniform(.15, .85) * W, rng.uniform(.15, .85) * H
        dx, dy = math.cos(a) * 9e3, math.sin(a) * 9e3
        lines.append(LineString([(cx - dx, cy - dy), (cx + dx, cy + dy)]))
    merged = unary_union(lines)
    return [p for p in polygonize(merged) if p.area > 2000]


def hatch(g, step, ang, w=4):
    if g.is_empty: return g
    minx, miny, maxx, maxy = g.bounds; c = ((minx + maxx) / 2, (miny + maxy) / 2); R = math.hypot(maxx - minx, maxy - miny)
    ls = [LineString([(c[0] - R, c[1] + k), (c[0] + R, c[1] + k)]) for k in np.arange(-R, R, step)]
    return affinity.rotate(MultiLineString(ls), ang, origin=c).intersection(g)


def dots(g, step, r):
    if g.is_empty: return g
    minx, miny, maxx, maxy = g.bounds
    pts = [Point(x + (step / 2 if int(y / step) % 2 else 0), y).buffer(r, 8) for y in np.arange(miny, maxy, step) for x in np.arange(minx, maxx, step)]
    return unary_union(pts).intersection(g)


def compose(name, seed, W=3000, H=4000, ground=("cream", "sage", "light", "fwg", "deep", "violet", "lilac", "blue", "ochre", "soil")):
    rng = np.random.default_rng(seed)
    pic = Pic(W, H)
    F = facets(W, H, rng)
    # organisms in a base view
    nem_c = bez([(W * .08, H * .30), (W * .75, H * .10), (W * .15, H * .80), (W * .92, H * .72)], 400)
    nem = tube(nem_c, 210, 170, tail=.18, head=.03)
    gut = LineString(nem_c[25:-70])
    pharynx = LineString(nem_c[4:40]); bulb = Point(*nem_c[40]).buffer(62)
    shell_c = (W * .66, H * .40)
    shell = affinity.rotate(affinity.scale(Point(shell_c).buffer(1, 96), 330, 440), -18, origin=shell_c)
    pores = unary_union([Point(shell_c[0] + 250 * math.cos(a) * .82, shell_c[1] + 330 * math.sin(a) * .82).buffer(26) for a in np.linspace(0, 2 * math.pi, 22, endpoint=False)])
    pores = affinity.rotate(pores, -18, origin=shell_c)
    mouth = affinity.rotate(affinity.scale(Point(shell_c[0], shell_c[1] + 360).buffer(1, 48), 110, 40), -18, origin=shell_c)
    hyphae = [LineString(bez([(0, H * y0), (W * .3, H * (y0 - .1)), (W * .7, H * (y0 + .12)), (W, H * (y0 + .02))], 200)) for y0 in (.12, .55, .92)]
    base = {"nem": nem, "gut": gut, "phar": pharynx, "bulb": bulb, "shell": shell, "pores": pores, "mouth": mouth, "hyph": hyphae}

    def view(k):
        """Each facet sees the scene from a slightly different side: shifted, turned, rescaled."""
        dx, dy = rng.normal(0, 55, 2); a = rng.normal(0, 4); s = rng.uniform(.94, 1.07)
        f = lambda g: affinity.scale(affinity.rotate(affinity.translate(g, dx, dy), a, origin=(W / 2, H / 2)), s, s, origin=(W / 2, H / 2))
        return {key: ([f(h) for h in v] if isinstance(v, list) else f(v)) for key, v in base.items()}

    names = list(ground)
    for i, P in enumerate(F):
        V = view(i)
        bg = PAL[names[rng.integers(len(names))]]
        pic.fill(P, bg)
        tex = rng.random()
        if tex < .3:
            pic.stroke(hatch(P, rng.uniform(22, 40), rng.uniform(0, 180), 3.5), 3.5, INK)
        elif tex < .5:
            pic.fill(dots(P, rng.uniform(26, 40), rng.uniform(4, 8)), INK)
        # organisms in this facet's own colours
        body_col = PAL[names[rng.integers(len(names))]]
        while body_col == bg:
            body_col = PAL[names[rng.integers(len(names))]]
        sh_col = PAL[names[rng.integers(len(names))]]
        while sh_col in (bg, body_col):
            sh_col = PAL[names[rng.integers(len(names))]]
        pic.fill(V["shell"].intersection(P), sh_col)
        pic.fill(V["pores"].intersection(P), bg)
        pic.fill(V["mouth"].intersection(P), INK)
        pic.stroke(V["shell"].boundary.intersection(P), 9)
        pic.fill(V["nem"].intersection(P), body_col)
        if rng.random() < .45:
            pic.stroke(hatch(V["nem"].intersection(P), 18, rng.uniform(0, 180)), 3)
        pic.stroke(V["nem"].boundary.intersection(P), 10)
        pic.stroke(V["gut"].intersection(P), 6)
        pic.stroke(V["phar"].intersection(P), 6)
        pic.stroke(V["bulb"].boundary.intersection(P), 6)
        for h in V["hyph"]:
            pic.stroke(h.intersection(P), 7)
    for P in F:                                                  # facet edges, thin
        pic.stroke(P.boundary, 3)
    os.makedirs(OUT, exist_ok=True)
    svg = pic.svg()
    open(os.path.join(OUT, name + ".svg"), "w").write(svg)
    im = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(), output_width=W, output_height=H))).convert("RGB")
    im.save(os.path.join(OUT, name + ".png"), dpi=(300, 300))
    return im


if __name__ == "__main__":
    ims = [compose(f"soil-from-several-sides-{s}", s) for s in (3, 8, 15)]
    sheet = Image.new("RGB", (3 * 760 + 40, 1030), "#ddd")
    for i, im in enumerate(ims):
        t = im.copy(); t.thumbnail((750, 1000)); sheet.paste(t, (10 + i * 770, 15))
    sheet.save(os.path.join(OUT, "contact.jpg"), quality=90)
