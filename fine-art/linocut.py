"""Linocut soil garden: a dense one-colour block of soil life, carved like a lino print for a hoodie back or tote.
Each organism is a solid shape with carved inner contour lines (nested offsets), packed between hyphal fronds
and mycorrhizal roots. One ink. Output out/linocut/<name>-<ink>.svg + preview png.
"""
import io, math, os, sys
import numpy as np
import cairosvg
from PIL import Image
from shapely.geometry import Point, LineString, box
from shapely.ops import unary_union
from shapely import affinity
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cutouts  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "linocut")
W, H = 3000, 3600


def carve(g, step=16, gap=5, rings=3):
    """Solid shape with nested carved lines inside, like gouged lino."""
    out = g
    for k in range(1, rings + 1):
        inner = g.buffer(-k * step)
        if inner.is_empty: break
        out = out.difference(inner.boundary.buffer(gap / 2))
    return out


def frond(rng, x, y, L, ang, w):
    parts, pts = [], []
    a = math.radians(ang); curl = rng.normal(0, .0035); px, py = x, y
    for k in range(70):
        pts.append((px, py)); a += curl * 10; px += math.cos(a) * L / 70; py += math.sin(a) * L / 70
    parts.append(LineString(pts).buffer(w, 8))
    for k in range(5, 68, 5):
        bx, by = pts[k]; side = 1 if (k // 5) % 2 else -1
        ba = math.atan2(pts[k + 1][1] - by, pts[k + 1][0] - bx) + side * math.radians(rng.uniform(45, 65))
        bl = L * .2 * (1 - k / 80)
        tip = (bx + math.cos(ba) * bl, by + math.sin(ba) * bl)
        parts.append(LineString([(bx, by), tip]).buffer(w * .8, 8)); parts.append(Point(tip).buffer(w * 1.8))
    return unary_union(parts)


def garden(seed, frame="arch"):
    rng = np.random.default_rng(seed)
    if frame == "arch":
        F = unary_union([box(300, 1300, W - 300, H - 250), Point(W / 2, 1300).buffer(W / 2 - 300, 128)])
    else:
        F = box(250, 250, W - 250, H - 250).buffer(120, 32).buffer(-120, 32)
    placed = []
    # fronds rising from the bottom, like the stems in a flower block
    for _ in range(14):
        x = rng.uniform(350, W - 350)
        placed.append(frond(rng, x, H - 260, rng.uniform(900, 2000), -90 + rng.normal(0, 18), rng.uniform(9, 14)))
    occupied = unary_union(placed).buffer(10)
    organisms = []
    for _ in range(400):
        if len(organisms) >= 26: break
        name, fn, _ = cutouts.PICTOS[rng.integers(len(cutouts.PICTOS))]
        s = rng.uniform(.6, 1.25)
        g = affinity.rotate(affinity.scale(fn(), s, s, origin=(200, 200)), rng.uniform(-35, 35), origin=(200, 200))
        g = affinity.translate(g, rng.uniform(200, W - 600), rng.uniform(250, H - 600))
        if not F.buffer(-30).contains(g): continue
        if any(g.buffer(28).intersects(o) for o in organisms): continue
        organisms.append(g)
    org = unary_union(organisms)
    stems = unary_union(placed).difference(org.buffer(28))
    carved = unary_union([carve(o, 15, 6, 3) for o in organisms])
    # small spores to fill gaps
    spores = []
    for _ in range(3000):
        if len(spores) > 160: break
        p = Point(rng.uniform(300, W - 300), rng.uniform(300, H - 300)); r = rng.uniform(7, 18)
        c = p.buffer(r)
        if F.contains(c) and not c.buffer(14).intersects(org) and not c.buffer(10).intersects(stems) and all(not c.buffer(10).intersects(q) for q in spores[-60:]):
            spores.append(c)
    border = F.boundary.buffer(10)
    art = unary_union([carved, stems.intersection(F), unary_union(spores), border])
    return art


def d_of(g):
    out = []
    for p in getattr(g, "geoms", [g]):
        if p.geom_type != "Polygon" or p.is_empty: continue
        for r in [p.exterior] + list(p.interiors):
            out.append("M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in np.array(r.coords)) + "Z")
    return "".join(out)


def main():
    os.makedirs(OUT, exist_ok=True)
    looks = [("arch", 3, "#B7CF5E", "#2F4A2B"), ("rect", 7, "#A9C8A0", "#22371F"), ("arch", 11, "#22371F", "#B7CF5E"), ("rect", 5, "#E9E4D4", "#4F6B3A")]
    prev = []
    for frame, seed, ink, ground in looks:
        d = d_of(garden(seed, frame).simplify(.6))
        name = f"soil-garden-{frame}-{seed}"
        open(os.path.join(OUT, f"{name}.svg"), "w").write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}"><path d="{d}" fill="{ink}" fill-rule="evenodd"/></svg>\n')
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}"><rect width="{W}" height="{H}" fill="{ground}"/><path d="{d}" fill="{ink}" fill-rule="evenodd"/></svg>'
        im = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(), output_width=W // 4, output_height=H // 4))).convert("RGB")
        prev.append(im)
    sheet = Image.new("RGB", (4 * (W // 4) + 50, H // 4 + 20), "#ddd")
    for i, im in enumerate(prev): sheet.paste(im, (10 + i * (W // 4 + 10), 10))
    sheet.save(os.path.join(OUT, "contact.jpg"), quality=90)


if __name__ == "__main__":
    main()
