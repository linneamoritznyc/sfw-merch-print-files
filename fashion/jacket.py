"""All-over-print zip jacket: tapered hyphal swooshes off the centre zip, ending in spore chains, mirror symmetric.
Chest mark: a small springtail. Sleeve mark: coiled nematode in a ring. Back: one big pair of hyphal swooshes.
Outputs out/jacket/: front-art-<way>.svg and back-art-<way>.svg (full-bleed vector, to be fitted to the Printful
AOP zip jacket template panels), and mockup-<way>.png (flat front + back).
"""
import io, math, os, sys
import numpy as np
import cairosvg
from PIL import Image
from shapely.geometry import Polygon, Point, LineString, box
from shapely.ops import unary_union
from shapely import affinity
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fine-art"))
import cutouts  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "jacket")
W, H = 2400, 2400            # art canvas, centre zip at x = 1200
WAYS = {"olive": ("#4F5A2E", "#E6DEC8"), "forest": ("#22371F", "#CBDB6C"), "black": ("#161816", "#B3BEB1"), "lilac": ("#8E7BB8", "#F1ECDC")}


def bez(P, n=200):
    P = np.array(P, float); t = np.linspace(0, 1, n)[:, None]
    return (1 - t) ** 3 * P[0] + 3 * (1 - t) ** 2 * t * P[1] + 3 * (1 - t) * t ** 2 * P[2] + t ** 3 * P[3]


def swoosh(c, w0, wmax, w1, peak=.35):
    """Crescent along curve c: tapers at both ends, fattest at 'peak'."""
    t = np.gradient(c, axis=0); t /= np.linalg.norm(t, axis=1)[:, None]; n = np.c_[-t[:, 1], t[:, 0]]
    u = np.linspace(0, 1, len(c))
    w = np.where(u < peak, w0 + (wmax - w0) * np.sin(u / peak * math.pi / 2), w1 + (wmax - w1) * np.cos((u - peak) / (1 - peak) * math.pi / 2))
    return Polygon(np.r_[c + n * w[:, None] / 2, (c - n * w[:, None] / 2)[::-1]]).buffer(0)


def spores(c, n=4, r=26):
    e = c[-1]; d = (c[-1] - c[-6]); d /= np.linalg.norm(d); out = []; p = e.copy()
    for k in range(n):
        rr = r * (1 - .18 * k); p = p + d * (rr * (1.3 if k == 0 else 2.05)); out.append(Point(*p).buffer(rr, 48))
    return unary_union(out)


def half_front():
    """Right half seen from the front (x from zip 1200 to 2400)."""
    parts = []
    # big lower swoosh: from the zip at chest, sweeping out and down across the body to the hem
    c1 = bez([(1230, 980), (1700, 900), (2050, 1300), (1760, 2050)])
    parts += [swoosh(c1, 20, 230, 14, .3), spores(c1, 4, 30)]
    # upper swoosh: from the collar out over the shoulder and down the sleeve
    c2 = bez([(1250, 420), (1700, 380), (2150, 700), (2330, 1250)])
    parts += [swoosh(c2, 16, 150, 10, .35), spores(c2, 3, 24)]
    # thin hypha branching off the big swoosh with a short spore chain
    c3 = bez([(1620, 1180), (1820, 1220), (1950, 1420), (1980, 1600)])
    parts += [swoosh(c3, 30, 46, 8, .2), spores(c3, 3, 16)]
    return unary_union(parts)


def front_art():
    r = half_front()
    l = affinity.scale(r, -1, 1, origin=(1200, 0))
    chest = affinity.translate(affinity.scale(cutouts.springtail(), .32, .32, origin=(0, 0)), 1310, 560)   # wearer's left chest
    return unary_union([r, l]), chest


def sleeve_mark(cx, cy, R):
    ring = Point(cx, cy).buffer(R).difference(Point(cx, cy).buffer(R - 12))
    nem = affinity.translate(affinity.scale(cutouts.nematode(), R * 1.3 / 400, R * 1.3 / 400, origin=(0, 0)), cx - R * .65, cy - R * .65)
    return unary_union([ring, nem])


def back_art():
    parts = []
    for s in (1, -1):
        c = bez([(1200 + s * 30, 300), (1200 + s * 700, 260), (1200 + s * 1000, 900), (1200 + s * 560, 1900)])
        parts += [swoosh(c, 18, 300, 14, .32), spores(c, 4, 36)]
        c2 = bez([(1200 + s * 30, 1150), (1200 + s * 260, 1180), (1200 + s * 420, 1500), (1200 + s * 360, 2100)])
        parts += [swoosh(c2, 14, 120, 10, .3), spores(c2, 3, 22)]
    return unary_union(parts)


def d_of(g):
    out = []
    for p in getattr(g, "geoms", [g]):
        if p.geom_type != "Polygon" or p.is_empty: continue
        for r in [p.exterior] + list(p.interiors):
            out.append("M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in np.array(r.coords)) + "Z")
    return "".join(out)


def svg(ground, ink, shapes):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}"><rect width="{W}" height="{H}" fill="{ground}"/>' + "".join(f'<path d="{d_of(g)}" fill="{ink}" fill-rule="evenodd"/>' for g in shapes) + "</svg>\n"


# flat jacket silhouette on the art canvas (front), for the mockup only
BODY = Polygon([(700, 330), (950, 250), (1050, 120), (1350, 120), (1450, 250), (1700, 330), (2050, 600), (2300, 1500), (2330, 2150), (2120, 2180),
                (1950, 1300), (1900, 2150), (500, 2150), (450, 1300), (280, 2180), (70, 2150), (100, 1500), (350, 600)])
HOOD = Polygon([(980, 260), (930, 60), (1200, -40), (1470, 60), (1420, 260), (1200, 200)])


def mockup(ground, ink, front, chest, back):
    sil = unary_union([BODY, HOOD])
    def flat(art_shapes, extra=""):
        body = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-100 -100 {W + 200} {H + 200}" width="1200" height="1200"><defs><clipPath id="j"><path d="{d_of(sil)}"/></clipPath></defs><rect x="-100" y="-100" width="{W + 200}" height="{H + 200}" fill="#E4E4E2"/>'
        body += f'<g clip-path="url(#j)"><rect width="{W}" height="{H}" fill="{ground}"/>' + "".join(f'<path d="{d_of(g)}" fill="{ink}" fill-rule="evenodd"/>' for g in art_shapes) + extra + "</g>"
        body += f'<path d="{d_of(sil)}" fill="none" stroke="#333" stroke-width="6"/>'
        return body + "</svg>"
    zip_ = f'<line x1="1200" y1="200" x2="1200" y2="2150" stroke="#222" stroke-width="10"/>'
    f = flat([front, chest, sleeve_mark(2160, 1820, 70)], zip_)
    b = flat([back])
    fi = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=f.encode()))).convert("RGB")
    bi = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=b.encode()))).convert("RGB")
    m = Image.new("RGB", (2420, 1200), "#E4E4E2"); m.paste(fi, (0, 0)); m.paste(bi, (1220, 0))
    return m


def main():
    os.makedirs(OUT, exist_ok=True)
    front, chest = front_art(); back = back_art(); sl = sleeve_mark(2160, 1820, 70)
    sheets = []
    for way, (g, ink) in WAYS.items():
        open(os.path.join(OUT, f"front-art-{way}.svg"), "w").write(svg(g, ink, [front, chest, sl]))
        open(os.path.join(OUT, f"back-art-{way}.svg"), "w").write(svg(g, ink, [back]))
        m = mockup(g, ink, front, chest, back); m.save(os.path.join(OUT, f"mockup-{way}.png")); sheets.append(m)
    s = Image.new("RGB", (1210 * 2 + 10, 610 * 2 + 10), "#fff")
    for i, m in enumerate(sheets): s.paste(m.resize((1210, 600), Image.LANCZOS), (5 + (i % 2) * 1210, 5 + (i // 2) * 610))
    s.save(os.path.join(OUT, "contact.jpg"), quality=90)


if __name__ == "__main__":
    main()
