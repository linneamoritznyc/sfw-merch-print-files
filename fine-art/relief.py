"""Soil relief: a cluster of angular painted shards (like a cut plywood wall relief), each shard pierced with holes
that are real soil pores traced from a student micrograph of an aggregate. Painted face with brush grain,
raw wood edges showing inside every hole, cast shadow on a white wall.
Output out/relief/<name>.png + contact.jpg
"""
import os, sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps
from scipy import ndimage as ndi
from scipy.spatial import Voronoi
from skimage import measure
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union
from shapely import affinity

HERE = os.path.dirname(os.path.abspath(__file__))
SRC, OUT = os.path.join(HERE, "src"), os.path.join(HERE, "out", "relief")
W, H = 2400, 1800


def pores(src, rng):
    im = ImageOps.fit(Image.open(os.path.join(SRC, src + ".jpg")).convert("L"), (W // 2, H // 2), Image.LANCZOS)
    g = np.asarray(ImageOps.autocontrast(im, cutoff=1), np.float32) / 255
    g = ndi.gaussian_filter(g - ndi.gaussian_filter(g, 60), 4)
    out = []
    for c in measure.find_contours(g, np.quantile(g, .72)):
        if len(c) < 30: continue
        p = Polygon(c[:, ::-1] * 2)
        if p.is_valid and 1500 < p.area < 90000: out.append(p.simplify(3))
    return out


def shards(rng, n=26):
    blob = affinity.scale(Point(W / 2, H / 2).buffer(1, 64), W * .42, H * .38)
    pts = []
    while len(pts) < n:
        p = (rng.uniform(0, W), rng.uniform(0, H))
        if blob.contains(Point(p)): pts.append(p)
    vor = Voronoi(np.r_[pts, [[-5e3, -5e3], [5e3, -5e3], [5e3, 5e3], [-5e3, 5e3]]])
    out = []
    for i in range(n):
        reg = vor.regions[vor.point_region[i]]
        if -1 in reg or not reg: continue
        P = Polygon([vor.vertices[j] for j in reg]).intersection(blob.buffer(rng.uniform(40, 160)))
        if P.is_empty or P.geom_type != "Polygon": continue
        P = affinity.rotate(P, rng.normal(0, 4))
        P = affinity.scale(P, .93, .93).buffer(-6, join_style=2)
        if P.area > 8000: out.append(P)
    return out


def draw_poly(d, g, fill):
    for p in getattr(g, "geoms", [g]):
        if p.geom_type != "Polygon" or p.is_empty: continue
        d.polygon(list(p.exterior.coords), fill=fill)
        for r in p.interiors: d.polygon(list(r.coords), fill=0 if isinstance(fill, int) else None)


def mask(g):
    m = Image.new("L", (W, H), 0); d = ImageDraw.Draw(m)
    for p in getattr(g, "geoms", [g]):
        if p.geom_type != "Polygon" or p.is_empty: continue
        d.polygon(list(p.exterior.coords), fill=255)
        for r in p.interiors: d.polygon(list(r.coords), fill=0)
    return m


def relief(name, src, paint, seed):
    rng = np.random.default_rng(seed)
    P = pores(src, rng); S = shards(rng)
    pieces = []
    for s in S:
        holes = [h for h in P if s.buffer(-28).contains(h)]
        g = s.difference(unary_union(holes).buffer(6, join_style=1)) if holes else s
        if rng.random() < .3:                                   # some shards get a big cut-out outline, like a frame
            inner = s.buffer(-40, join_style=2)
            if not inner.is_empty and inner.area > 20000: g = g.difference(inner.difference(inner.buffer(-60)))
        pieces.append(g)
    allp = unary_union(pieces)
    wall = Image.new("RGB", (W, H), (240, 239, 236))
    sh = mask(affinity.translate(allp, 22, 30)).filter(ImageFilter.GaussianBlur(18))
    wall.paste((150, 150, 148), (0, 0), sh.point(lambda v: int(v * .55)))
    wood = mask(affinity.translate(allp, 7, 9))
    wall.paste((92, 52, 32), (0, 0), wood)
    face = mask(allp)
    grain = ndi.gaussian_filter(rng.random((H, W)), (.6, 6)).astype(np.float32)
    grain = (grain - grain.mean()) / grain.std()
    paint_img = np.ones((H, W, 3), np.float32) * np.array(paint, np.float32) * (1 + .08 * grain[..., None])
    paint_img += (ndi.gaussian_filter(rng.random((H // 8, W // 8)), 2).repeat(8, 0).repeat(8, 1)[:H, :W, None] - .5) * 30
    wall.paste(Image.fromarray(np.clip(paint_img, 0, 255).astype(np.uint8)), (0, 0), face)
    os.makedirs(OUT, exist_ok=True); wall.save(os.path.join(OUT, f"{name}.png"))
    return wall


def main():
    ims = [relief("aggregate-blue", "testate-encysting-jimena-fuentes-i2", (52, 82, 170), 3),
           relief("aggregate-green", "testate-encysted-robert-kenyon", (34, 95, 52), 5),
           relief("aggregate-lime", "fungal-spores-in-suspension", (190, 205, 70), 9),
           relief("aggregate-lilac", "testate-encysted-sid-jensen", (140, 120, 190), 12)]
    sheet = Image.new("RGB", (2 * 1210 + 10, 2 * 910 + 10), "#fff")
    for i, im in enumerate(ims): sheet.paste(im.resize((1200, 900), Image.LANCZOS), (10 + (i % 2) * 1205, 10 + (i // 2) * 905))
    sheet.save(os.path.join(OUT, "contact.jpg"), quality=90)


if __name__ == "__main__":
    main()
