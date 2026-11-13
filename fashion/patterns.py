"""SFW textile repeats for chill pants. All vector, all mirror-symmetric, all seamless.
Motifs are soil organisms:
  medallion   Arcella seen from above (scalloped test, ring of pores, toothed aperture) in a half-drop repeat,
              with 4-way fungal sprigs ending in spores between them        (after a block-printed resort shirt)
  lattice     a diagonal lattice of flagellate cells, alternating up and down  (after a monogram jacquard)
  tile        a knit-style square tile: an 8-fold sun animalcule star framed by dotted rules
  sprig       small all-over ditsy repeat of hyphal sprigs and spores
  trim        side-stripe / waistband trim: rules and a spore-dot chain
Output out/patterns/<name>-<colourway>.svg + .png (tile at 150 dpi) and out/pants/<look>.png flats.
"""
import io, math, os
import numpy as np
import cairosvg
from PIL import Image, ImageDraw
from shapely.geometry import Point, Polygon, LineString, box
from shapely.ops import unary_union
from shapely import affinity

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
DEEP, FWG, LIGHT, WHITE, BLACK, PALE = "#22371F", "#156826", "#59A66C", "#FFFFFF", "#0E100E", "#E9F1E4"
WAYS = {   # ground, motif, detail
    "forest": (DEEP, WHITE, LIGHT),
    "foodweb": (FWG, WHITE, DEEP),
    "white": (WHITE, FWG, DEEP),
    "night": (BLACK, LIGHT, WHITE),
}


# ------------------------------------------------------------------ geometry helpers
def ring(c, r, w):
    return Point(c).buffer(r + w / 2, 64).difference(Point(c).buffer(r - w / 2, 64))


def disc(c, r):
    return Point(c).buffer(r, 48)


def line(pts, w):
    return LineString(pts).buffer(w / 2, 16)


def rot(g, a, c=(0, 0)):
    return affinity.rotate(g, a, origin=c)


def mirror4(g):
    """4-fold mirror symmetry about the origin: x mirror, y mirror, both."""
    return unary_union([g, affinity.scale(g, -1, 1, origin=(0, 0)), affinity.scale(g, 1, -1, origin=(0, 0)), affinity.scale(g, -1, -1, origin=(0, 0))])


def radial(g, n):
    return unary_union([rot(g, k * 360 / n) for k in range(n)])


# ------------------------------------------------------------------ motifs, centred on the origin
def arcella(R):
    """Returns (body, detail): body is the pale disc, detail is cut/drawn on top in the detail colour."""
    sc = unary_union([disc((R * .86 * math.cos(a), R * .86 * math.sin(a)), R * .2) for a in np.linspace(0, 2 * math.pi, 18, endpoint=False)])
    body = unary_union([disc((0, 0), R * .9), sc])
    det = [ring((0, 0), R * .74, R * .035)]
    for k in range(24):                                      # ring of pores on the test
        a = k / 24 * 2 * math.pi
        det.append(disc((R * .63 * math.cos(a), R * .63 * math.sin(a)), R * .045))
    det.append(ring((0, 0), R * .5, R * .05))
    teeth = Polygon([((R * .3 if k % 2 == 0 else R * .22) * math.cos(a), (R * .3 if k % 2 == 0 else R * .22) * math.sin(a)) for k, a in enumerate(np.linspace(0, 2 * math.pi, 40, endpoint=False))])
    det.append(teeth.difference(disc((0, 0), R * .17)))           # toothed rim round the aperture
    det.append(ring((0, 0), R * .14, R * .04))
    det.append(disc((0, 0), R * .06))
    for k in range(18):                                       # dot in each scallop
        a = (k + .0) / 18 * 2 * math.pi
        det.append(disc((R * .92 * math.cos(a), R * .92 * math.sin(a)), R * .035))
    return body, unary_union(det)


def sprig(L, w):
    """4-way fungal sprig: hyphae with side branches ending in spore chains."""
    arm = [line([(0, 0), (L, 0)], w)]
    for f in (.45, .72):
        for s in (1, -1):
            arm.append(line([(L * f, 0), (L * f + L * .18, s * L * .18)], w * .8))
            arm.append(disc((L * f + L * .18 + L * .05, s * (L * .18 + L * .05)), w * 1.1))
    for k in range(3):
        arm.append(disc((L + w * 1.4 + k * w * 2.6, 0), w * (1.15 - k * .2)))
    g = radial(unary_union(arm), 4)
    return unary_union([g, rot(radial(line([(0, 0), (L * .35, 0)], w * .7), 4), 45), disc((0, 0), w * 1.8)])


def flagellate(L):
    """Teardrop cell with a nucleus and a wavy flagellum, pointing up (-y)."""
    t = np.linspace(0, math.pi, 50)
    prof = [(L * .32 * math.sin(a) * (1 - .35 * (1 - math.cos(a)) / 2), -L * .5 * (1 - math.cos(a)) / 2 * 1.0) for a in t]
    body = Polygon(prof + [(-x, y) for x, y in prof[::-1]])
    body = affinity.translate(body, 0, L * .05)
    fl = line([(L * .04 * math.sin(u * 9), L * .05 + u * L * .5) for u in np.linspace(0, 1, 40)], L * .045)
    return unary_union([body, fl]), disc((0, -L * .12), L * .07)


def sun_star(R):
    """8-fold sun animalcule star for a knit tile."""
    g = [ring((0, 0), R * .3, R * .06), disc((0, 0), R * .12)]
    for k in range(16):
        a = k / 16 * 360
        L = R * (1 if k % 2 == 0 else .7)
        g.append(rot(line([(R * .36, 0), (L, 0)], R * .055), a))
        g.append(rot(disc((L, 0), R * .07 if k % 2 == 0 else R * .05), a))
        if k % 2 == 0:
            g.append(rot(line([(R * .62, 0), (R * .78, R * .12)], R * .04), a))
            g.append(rot(line([(R * .62, 0), (R * .78, -R * .12)], R * .04), a))
    for k in range(8):
        g.append(rot(disc((R * .2, 0), R * .04), k * 45 + 22.5))
    return unary_union(g)


def bezier(P0, P1, P2, P3, n=60):
    t = np.linspace(0, 1, n)[:, None]
    return (1 - t) ** 3 * np.array(P0) + 3 * (1 - t) ** 2 * t * np.array(P1) + 3 * (1 - t) * t ** 2 * np.array(P2) + t ** 3 * np.array(P3)


def difflugia(L):
    """Testate amoeba Difflugia: an urn-shaped shell built of sand grains, aperture at the top. Returns (body, detail)."""
    t = np.linspace(0, 1, 60)
    # right half profile from aperture (top) to fundus (bottom)
    prof = np.r_[bezier((L * .14, -L * .5), (L * .12, -L * .3), (L * .42, -L * .2), (L * .38, L * .12)),
                 bezier((L * .38, L * .12), (L * .36, L * .4), (L * .12, L * .52), (0, L * .5))]
    body = Polygon(list(map(tuple, prof)) + [(-x, y) for x, y in prof[::-1]])
    det = [line([(-L * .17, -L * .5), (L * .17, -L * .5)], L * .05)]
    rng = np.random.default_rng(3)
    pts = []
    for _ in range(400):                                       # sand grains, mirrored
        x, y = rng.uniform(.04, .34) * L, rng.uniform(-.3, .44) * L
        r = rng.uniform(.018, .034) * L
        if body.buffer(-L * .05).contains(Point(x, y)) and all((x - a) ** 2 + (y - b) ** 2 > (r + c + L * .012) ** 2 for a, b, c in pts):
            pts.append((x, y, r))
    for x, y, r in pts:
        det += [disc((x, y), r), disc((-x, y), r)]
    det.append(line([(0, -L * .44), (0, L * .44)], L * .02))
    return body, unary_union(det)


def nematode_curve(L, w):
    """One nematode as a tapering S, head at the start."""
    c = bezier((0, 0), (L * .45, -L * .05), (L * .1, L * .55), (L * .55, L * .7), 120)
    parts = []
    for i in range(len(c) - 1):
        u = i / len(c)
        ww = w * (.55 + .45 * math.sin(math.pi * min(1, u * 1.15)) ** .5) if u < .87 else w * (1 - (u - .87) / .13) * .9 + 1
        parts.append(Point(c[i]).buffer(ww / 2, 8).union(Point(c[i + 1]).buffer(ww / 2, 8)).convex_hull)
    return unary_union(parts), c


def lyre(L, w):
    """Two nematodes mirrored into a lyre around a spore column."""
    g, c = nematode_curve(L, w)
    g = affinity.translate(g, L * .08, -L * .35)
    both = unary_union([g, affinity.scale(g, -1, 1, origin=(0, 0))])
    dots = [disc((0, -L * .42 + k * L * .16), w * (.55 if k % 2 else .8)) for k in range(6)]
    return both, unary_union(dots)


def ogee(T, w):
    """Wavy hyphae forming an ogee net through the repeat, with spores along them."""
    g = []
    for x0 in (-T / 2, 0, T / 2, T):
        pts = [(x0 + T / 4 * math.sin(y / T * 2 * math.pi), y) for y in np.linspace(-T * .1, T * 1.1, 160)]
        g.append(line(pts, w))
        pts = [(x0 - T / 4 * math.sin(y / T * 2 * math.pi), y) for y in np.linspace(-T * .1, T * 1.1, 160)]
        g.append(line(pts, w))
    return unary_union(g)


# ------------------------------------------------------------------ tiles
def wrap(g, T):
    """Make g seamless in a T x T cell by adding wrapped copies, then clip to the cell."""
    parts = [affinity.translate(g, dx, dy) for dx in (-T, 0, T) for dy in (-T, 0, T)]
    return unary_union(parts).intersection(box(0, 0, T, T))


def wrap2(g, Tw, Th):
    parts = [affinity.translate(g, dx, dy) for dx in (-Tw, 0, Tw) for dy in (-Th, 0, Th)]
    return unary_union(parts).intersection(box(0, 0, Tw, Th))


def at(g, x, y):
    return affinity.translate(g, x, y)


def medallion_tile():
    T = 1000
    body, det = arcella(215)
    B, D, S = [], [], []
    for x, y in ((T / 4, T / 4), (3 * T / 4, 3 * T / 4)):        # half-drop
        B.append(at(body, x, y)); D.append(at(det, x, y))
    db, dd = difflugia(190)
    for x, y in ((3 * T / 4, T / 4), (T / 4, 3 * T / 4)):
        B.append(at(db, x, y)); D.append(at(dd, x, y))
    for x, y in ((0, 0), (T / 2, 0), (0, T / 2), (T / 2, T / 2)):  # spore triplets where the cells meet
        S.append(at(unary_union([disc((0, -26), 10), disc((0, 0), 13), disc((0, 26), 10)]), x, y))
    return T, T, [("detail", wrap(unary_union(S), T)), ("motif", wrap(unary_union(B), T)), ("detail", wrap(unary_union(D), T))]


def lattice_tile():
    T = 600
    up, nu = flagellate(170)
    dn, nd = rot(up, 180), rot(nu, 180)
    lines = unary_union([line([(-T, -T), (2 * T, 2 * T)], 7), line([(-T, 2 * T), (2 * T, -T)], 7),
                         line([(-T, T), (T, 3 * T)], 7), line([(T, -T), (3 * T, T)], 7), line([(-T, 0), (0, -T)], 7),
                         line([(0, T), (T, 0)], 7)])
    # diamonds centred at (0,0),(T/2,T/2) with cells up; (T/2,0),(0,T/2) with cells down
    M = [at(up, 0, 0), at(up, T / 2, T / 2), at(dn, T / 2, 0), at(dn, 0, T / 2)]
    N = [at(nu, 0, 0), at(nu, T / 2, T / 2), at(nd, T / 2, 0), at(nd, 0, T / 2)]
    knots = [at(disc((0, 0), 12), x, y) for x, y in ((T / 4, T / 4), (3 * T / 4, T / 4), (T / 4, 3 * T / 4), (3 * T / 4, 3 * T / 4))]
    return T, T, [("detail", wrap(lines, T)), ("motif", wrap(unary_union(M), T)), ("ground", wrap(unary_union(N), T)), ("motif", wrap(unary_union(knots), T))]


def tile_tile():
    T = 700
    db, dd = difflugia(250)
    ly, lyd = lyre(340, 20)
    dots = unary_union([disc((x, 0), 7) for x in np.arange(0, T, 28)] + [disc((0, y), 7) for y in np.arange(0, T, 28)])
    corner = unary_union([disc((0, 0), 18)] + [disc((dx, dy), 9) for dx, dy in ((34, 0), (-34, 0), (0, 34), (0, -34))])
    M = unary_union([at(db, T / 2, T / 2 + 20), at(ly, T / 2, T / 2)])
    return T, T, [("motif", wrap(M, T)), ("ground", wrap(at(dd, T / 2, T / 2 + 20), T)), ("detail", wrap(unary_union([dots, corner]), T))]


def sprig_tile():
    """Ditsy all-over: small Difflugia and nematode lyres, alternating up and down in a half-drop."""
    T = 520
    db, dd = difflugia(120)
    ly, lyd = lyre(170, 9)
    M = [at(db, T / 4, T / 4), at(rot(db, 180), 3 * T / 4, 3 * T / 4), at(ly, 3 * T / 4, T / 4), at(rot(ly, 180), T / 4, 3 * T / 4)]
    G = [at(dd, T / 4, T / 4), at(rot(dd, 180), 3 * T / 4, 3 * T / 4)]
    D = [at(lyd, 3 * T / 4, T / 4), at(rot(lyd, 180), T / 4, 3 * T / 4)]
    return T, T, [("motif", wrap(unary_union(M), T)), ("ground", wrap(unary_union(G), T)), ("detail", wrap(unary_union(D), T))]


def trim_tile():
    Tw, Th = 400, 300
    g = [box(-10, 20, Tw + 10, 50), box(-10, Th - 50, Tw + 10, Th - 20), box(-10, 100, Tw + 10, 112), box(-10, Th - 112, Tw + 10, Th - 100)]
    dots = [disc((x, Th / 2), 16 if i % 2 == 0 else 8) for i, x in enumerate(np.arange(0, Tw, 50))]
    return Tw, Th, [("motif", wrap2(unary_union(g), Tw, Th)), ("detail", wrap2(unary_union(dots), Tw, Th))]


TILES = {"medallion": medallion_tile, "lattice": lattice_tile, "tile": tile_tile, "sprig": sprig_tile, "trim": trim_tile}


def d_of(g):
    out = []
    for p in getattr(g, "geoms", [g]):
        if p.is_empty or p.geom_type != "Polygon":
            continue
        for r in [p.exterior] + list(p.interiors):
            out.append("M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in np.array(r.coords)) + "Z")
    return "".join(out)


def svg_of(Tw, Th, layers, way):
    ground, motif, detail = WAYS[way]
    col = {"ground": ground, "motif": motif, "detail": detail}
    body = f'<rect width="{Tw}" height="{Th}" fill="{ground}"/>' + "".join(f'<path fill="{col[k]}" fill-rule="evenodd" d="{d_of(g)}"/>' for k, g in layers)
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{Tw}" height="{Th}" viewBox="0 0 {Tw} {Th}">{body}</svg>\n'


def png(svg, w, h):
    return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(), output_width=w, output_height=h))).convert("RGB")


def fabric(tile, w, h):
    f = Image.new("RGB", (w, h))
    for x in range(0, w, tile.width):
        for y in range(0, h, tile.height):
            f.paste(tile, (x, y))
    return f


# ------------------------------------------------------------------ chill pants flats
PANTS = [(-170, 0), (170, 0), (185, 120), (215, 1000), (25, 1000), (0, 260), (-25, 1000), (-215, 1000), (-185, 120)]


def pants(tile, trim, scale, cuff=None):
    w, h = 520, 1080
    page = Image.new("RGB", (w, h), WHITE)
    pts = [(w / 2 + x, 40 + y) for x, y in PANTS]
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).polygon(pts, fill=255)
    t = tile.resize((int(tile.width * scale), int(tile.height * scale)), Image.LANCZOS)
    page.paste(fabric(t, w, h), (0, 0), m)
    # waistband and side stripes in trim
    tr = trim.resize((int(trim.width * .11), int(trim.height * .11)), Image.LANCZOS)
    band = fabric(tr, w, h)
    trv = fabric(tr.rotate(90, expand=True), w, h)
    wb = Image.new("L", (w, h), 0); ImageDraw.Draw(wb).polygon([(w / 2 - 170, 40), (w / 2 + 170, 40), (w / 2 + 172, 74), (w / 2 - 172, 74)], fill=255)
    page.paste(band, (0, 0), wb)
    for sx in (-1, 1):
        sm = Image.new("L", (w, h), 0)
        a = (w / 2 + sx * 186, 74 + 40); b = (w / 2 + sx * 215, 1040)
        ImageDraw.Draw(sm).polygon([(a[0] - sx * 33, a[1]), a, b, (b[0] - sx * 33, b[1])], fill=255)
        page.paste(trv, (0, 0), sm)
    d = ImageDraw.Draw(page)
    d.line(pts + pts[:1], fill=(40, 40, 40), width=3)
    d.line([(w / 2, 74), (w / 2, 300)], fill=(40, 40, 40), width=2)
    for x in (-60, 60):
        d.line([(w / 2 + x, 74), (w / 2 + x * 1.1, 170)], fill=(240, 240, 240), width=4)   # drawstring
    return page


def main():
    os.makedirs(os.path.join(OUT, "patterns"), exist_ok=True); os.makedirs(os.path.join(OUT, "pants"), exist_ok=True)
    pngs = {}
    for name, fn in TILES.items():
        Tw, Th, layers = fn()
        for way in WAYS:
            s = svg_of(Tw, Th, layers, way)
            open(os.path.join(OUT, "patterns", f"{name}-{way}.svg"), "w").write(s)
            im = png(s, Tw * 2, Th * 2); im.save(os.path.join(OUT, "patterns", f"{name}-{way}.png"), dpi=(150, 150))
            pngs[(name, way)] = im
    # swatch board
    names = [n for n in TILES if n != "trim"]
    sw = Image.new("RGB", (len(WAYS) * 620 + 20, len(names) * 620 + 200), WHITE)
    for i, n in enumerate(names):
        for j, way in enumerate(WAYS):
            t = pngs[(n, way)]; t = t.resize((int(t.width * .3), int(t.height * .3)), Image.LANCZOS)
            sw.paste(fabric(t, 600, 600), (20 + j * 620, 20 + i * 620))
    for j, way in enumerate(WAYS):
        t = pngs[("trim", way)]; t = t.resize((int(t.width * .3), int(t.height * .3)), Image.LANCZOS)
        sw.paste(fabric(t, 600, 160), (20 + j * 620, 20 + len(names) * 620))
    sw.save(os.path.join(OUT, "patterns", "swatch-board.png"))
    # pants line-up
    looks = [("medallion", "forest", "trim", "white", .09), ("lattice", "foodweb", "trim", "forest", .13), ("tile", "white", "trim", "foodweb", .12),
             ("medallion", "white", "trim", "forest", .09), ("sprig", "forest", "trim", "foodweb", .2), ("lattice", "night", "trim", "night", .13)]
    row = Image.new("RGB", (len(looks) * 540 + 20, 1100), WHITE)
    for i, (p, w, tn, tw, sc) in enumerate(looks):
        img = pants(pngs[(p, w)], pngs[(tn, tw)], sc)
        img.save(os.path.join(OUT, "pants", f"pants-{p}-{w}.png"))
        row.paste(img, (20 + i * 540, 10))
    row.save(os.path.join(OUT, "pants", "pants-lineup.png"))


if __name__ == "__main__":
    main()
