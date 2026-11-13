"""Fleece print: flat wavy hyphal ribbons and soil-life cut-outs in an earthy multicolour palette, after a retro
fleece pullover. Seamless tile. Output out/fleece/<name>.svg + swatch png.
"""
import io, math, os, sys
import numpy as np
import cairosvg
from PIL import Image
from shapely.geometry import LineString, Point, box
from shapely.ops import unary_union
from shapely import affinity
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cutouts  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "fleece")
T = 1600
WAYS = {
    "retro": {"ground": "#4C5F9E", "ribbon": ["#C9822E", "#B5893B"], "blob": "#3F6B2A", "org": "#F1E6CC"},
    "forest": {"ground": "#22371F", "ribbon": ["#8A6A3A", "#59A66C"], "blob": "#156826", "org": "#E9E4D4"},
    "lilac": {"ground": "#8E7BB8", "ribbon": ["#CBDB6C", "#E9E4D4"], "blob": "#3F6B2A", "org": "#F6F1E4"},
    "ochre": {"ground": "#B5893B", "ribbon": ["#4C5F9E", "#22371F"], "blob": "#59A66C", "org": "#F1E6CC"},
}


def wrap(g):
    return unary_union([affinity.translate(g, dx, dy) for dx in (-T, 0, T) for dy in (-T, 0, T)]).intersection(box(0, 0, T, T))


def ribbon(rng, y0, amp, w):
    pts = [(x, y0 + amp * math.sin(x / T * 2 * math.pi * 2 + rng.uniform(0, 6)) + amp * .4 * math.sin(x / T * 2 * math.pi * 3)) for x in np.linspace(-T, 2 * T, 900)]
    return LineString(pts).buffer(w, 16)


def blob(rng, x, y, r):
    a = np.linspace(0, 2 * math.pi, 80, endpoint=False)
    k = 1 + .22 * np.sin(3 * a + rng.uniform(0, 6)) + .12 * np.sin(5 * a + rng.uniform(0, 6))
    from shapely.geometry import Polygon
    return Polygon(np.c_[x + r * k * np.cos(a), y + r * k * 1.3 * np.sin(a)])


def tile(seed):
    rng = np.random.default_rng(seed)
    ribbons = [[], []]
    for i, y0 in enumerate(np.linspace(200, T - 200, 4)):
        ribbons[i % 2].append(ribbon(rng, y0 + rng.uniform(-40, 40), rng.uniform(90, 160), rng.uniform(22, 30)))
    R = [unary_union(r) for r in ribbons]
    blobs, orgs = [], []
    allr = unary_union(R)
    for _ in range(600):
        if len(blobs) >= 5: break
        b = blob(rng, rng.uniform(0, T), rng.uniform(0, T), rng.uniform(110, 160))
        if not any(b.buffer(30).intersects(o) for o in blobs): blobs.append(b)
    B = unary_union(blobs)
    for _ in range(800):
        if len(orgs) >= 6: break
        name, fn, _ = cutouts.PICTOS[rng.integers(len(cutouts.PICTOS))]
        s = rng.uniform(.7, .95)
        g = affinity.translate(affinity.rotate(affinity.scale(fn(), s, s, origin=(200, 200)), rng.uniform(-30, 30), origin=(200, 200)), rng.uniform(-200, T - 200), rng.uniform(-200, T - 200))
        if g.buffer(20).intersects(B) or any(g.buffer(30).intersects(o) for o in orgs): continue
        orgs.append(g)
    O = unary_union(orgs)
    # ribbons pass behind blobs and organisms
    R = [r.difference(B.buffer(12)).difference(O.buffer(14)) for r in R]
    return [("ribbon0", wrap(R[0])), ("ribbon1", wrap(R[1])), ("blob", wrap(B)), ("org", wrap(O))]


def d_of(g):
    out = []
    for p in getattr(g, "geoms", [g]):
        if p.geom_type != "Polygon" or p.is_empty: continue
        for r in [p.exterior] + list(p.interiors):
            out.append("M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in np.array(r.coords)) + "Z")
    return "".join(out)


def main():
    os.makedirs(OUT, exist_ok=True)
    layers = tile(4)
    sw = []
    for way, c in WAYS.items():
        col = {"ribbon0": c["ribbon"][0], "ribbon1": c["ribbon"][1], "blob": c["blob"], "org": c["org"]}
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {T} {T}" width="{T}" height="{T}"><rect width="{T}" height="{T}" fill="{c["ground"]}"/>' + "".join(f'<path d="{d_of(g)}" fill="{col[k]}" fill-rule="evenodd"/>' for k, g in layers) + "</svg>\n"
        open(os.path.join(OUT, f"fleece-{way}.svg"), "w").write(svg)
        t = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(), output_width=900, output_height=900))).convert("RGB")
        s = Image.new("RGB", (900, 1200))
        for x in range(0, 900, 900):
            for y in range(0, 1200, 900): s.paste(t, (x, y))
        sw.append(s)
    sheet = Image.new("RGB", (4 * 910 + 10, 1220), "#ddd")
    for i, s in enumerate(sw): sheet.paste(s, (10 + i * 910, 10))
    sheet.save(os.path.join(OUT, "contact.jpg"), quality=88)


if __name__ == "__main__":
    main()
