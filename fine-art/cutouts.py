"""Soil life as paper cut-outs: chunky flat silhouettes, rounded like scissor cuts, one colour each.
Testate amoeba, nematode, fungal hyphae with spores, mite, springtail, tardigrade, ciliate, bacteria, mycorrhizal root.
Outputs out/cutouts/: each pictogram as SVG (transparent), a sheet on deep green, plus a contact screenshot.
"""
import io, math, os
import numpy as np
import cairosvg
from PIL import Image
from shapely.geometry import Point, Polygon, LineString, box
from shapely.ops import unary_union
from shapely import affinity

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "cutouts")
GROUND = "#1D3B26"
INKS = {"lilac": "#D2C2F0", "berry": "#9B1D52", "olive": "#7A7F2E", "lime": "#E3F2A0", "sage": "#CFD6C3", "mint": "#9ED9B5"}
S = 400  # unit box


def soft(g, r=6):
    """Scissor-cut softness: round all corners."""
    return g.buffer(r, 24).buffer(-2 * r, 24).buffer(r, 24)


def stroke(pts, w):
    return LineString(pts).buffer(w / 2, 24)


def bez(P, n=80):
    P = np.array(P, float); t = np.linspace(0, 1, n)[:, None]
    return (1 - t) ** 3 * P[0] + 3 * (1 - t) ** 2 * t * P[1] + 3 * (1 - t) * t ** 2 * P[2] + t ** 3 * P[3]


def taper(c, w0, w1):
    c = np.asarray(c); t = np.gradient(c, axis=0); t /= np.linalg.norm(t, axis=1)[:, None]; n = np.c_[-t[:, 1], t[:, 0]]
    w = np.linspace(w0, w1, len(c))[:, None] / 2
    return Polygon(np.r_[c + n * w, (c - n * w)[::-1]]).buffer(0)


def leaf(cx, cy, L, W, ang):
    t = np.linspace(0, math.pi, 30)
    pts = [(L * (1 - math.cos(a)) / 2, W * math.sin(a) ** 1.2) for a in t]
    g = Polygon(pts + [(x, -y) for x, y in pts[::-1]])
    return affinity.translate(affinity.rotate(g, ang, origin=(0, 0)), cx, cy)


# ------------------------------------------------------------------ pictograms (in a 400 box, y down)
def testate():
    body = affinity.scale(Point(200, 170).buffer(1, 64), 125, 135)
    neck = box(150, 250, 250, 310)
    shell = soft(unary_union([body, neck]), 8)
    shell = shell.difference(Point(200, 120).buffer(26))                       # a cut window: the nucleus
    pods = unary_union([taper(bez([(200 + dx, 300), (200 + dx * 1.4, 330), (200 + dx * 2.0, 350), (200 + dx * 2.4, 390)]), 62, 40) for dx in (-45, -15, 15, 45)])
    return soft(unary_union([shell, pods]), 6)


def nematode():
    c = bez([(80, 110), (380, 10), (20, 360), (360, 330)], 200)
    body = taper(c, 120, 14)
    head = Point(*c[0]).buffer(60)
    g = unary_union([body, head])
    g = g.difference(Point(*c[0]).buffer(9))                                   # mouth
    return soft(g, 5)


def hyphae():
    parts = [taper(bez([(70, 380), (110, 250), (150, 200), (200, 120)]), 56, 34),
             taper(bez([(120, 260), (190, 240), (240, 220), (300, 170)]), 40, 28),
             taper(bez([(150, 200), (120, 150), (100, 110), (80, 70)]), 38, 26)]
    for (x, y, r) in [(205, 100, 40), (250, 70, 30), (175, 60, 26), (310, 150, 42), (350, 110, 30), (330, 205, 26), (75, 55, 30), (110, 30, 22), (45, 95, 22)]:
        parts.append(Point(x, y).buffer(r * 1.3))
    parts.append(taper(bez([(20, 385), (120, 365), (260, 365), (360, 390)]), 40, 18))
    return soft(unary_union(parts), 4)


def mite():
    body = affinity.scale(Point(200, 210).buffer(1, 64), 105, 120)
    gn = affinity.scale(Point(200, 85).buffer(1, 32), 34, 30)
    legs = []
    for side in (1, -1):
        for k, (a0, a1) in enumerate([(-40, -75), (-10, -30), (20, 40), (45, 80)]):
            r0 = (200 + side * 90 * math.cos(math.radians(a0)), 210 + 105 * math.sin(math.radians(a0)))
            kn = (r0[0] + side * 65, r0[1] + (k - 1.5) * 25 - 30)
            tip = (kn[0] + side * 30, kn[1] + 70 + (k - 1.5) * 10)
            legs.append(stroke([r0, kn, tip], 32))
    g = unary_union([body, gn] + legs)
    return soft(g.difference(affinity.scale(Point(200, 230).buffer(1, 48), 40, 60)), 5)


def springtail():
    c = bez([(80, 300), (150, 260), (250, 230), (330, 140)], 120)
    body = taper(c[::-1], 140, 80)
    head = Point(335, 135).buffer(62)
    ants = [taper(bez([(345, 105), (350, 60), (330, 40), (300, 25)]), 14, 6), taper(bez([(360, 115), (385, 80), (395, 50), (390, 20)]), 14, 6)]
    furca = taper(bez([(90, 320), (150, 370), (210, 390), (270, 380)]), 34, 16)
    legs = [stroke([(x, 270 - (x - 150) * .35), (x + 10, 340 - (x - 150) * .3)], 26) for x in (190, 235, 280)]
    return soft(unary_union([body, head, furca] + ants + legs), 5)


def tardigrade():
    body = soft(unary_union([affinity.scale(Point(200, 180).buffer(1, 64), 150, 85), Point(330, 175).buffer(55)]), 8)
    legs = []
    for x in (95, 165, 235, 300):
        leg = box(x - 20, 230, x + 20, 300)
        claws = unary_union([leaf(x - 14 + j * 10, 300, 34, 6, 80 + (j - 1.5) * 18) for j in range(4)])
        legs += [leg, claws]
    g = unary_union([body] + legs)
    return soft(g.difference(Point(345, 160).buffer(9)), 4)


def ciliate():
    k = affinity.scale(Point(200, 200).buffer(1, 64), 130, 105)
    notch = affinity.scale(Point(270, 150).buffer(1, 32), 55, 40)
    body = k.difference(notch)
    cil = []
    for a in np.linspace(0, 2 * math.pi, 22, endpoint=False):
        p = (200 + 130 * math.cos(a), 200 + 105 * math.sin(a))
        if notch.buffer(10).contains(Point(p)): continue
        cil.append(stroke([p, (200 + 172 * math.cos(a + .06), 200 + 140 * math.sin(a + .06))], 18))
    g = unary_union([body] + cil).difference(Point(170, 215).buffer(30))
    return soft(g, 3)


def bacteria():
    """A chain of rod bacteria dividing, with a few cocci: fat capsules side by side, slightly fanned."""
    parts = []
    for i, (x, a, l) in enumerate([(55, -16, 220), (155, -5, 290), (255, 6, 250), (350, 16, 200)]):
        y0 = 210
        r1 = affinity.rotate(stroke([(x, y0 - l / 2), (x, y0 - 22)], 62), a, origin=(x, y0))
        r2 = affinity.rotate(stroke([(x, y0 + 22), (x, y0 + l / 2)], 62), a, origin=(x, y0))
        parts += [r1, r2]
    for x, y, r in [(360, 60, 26), (30, 360, 22), (380, 350, 18)]:
        parts.append(Point(x, y).buffer(r))
    return unary_union([soft(p, 3) for p in parts])


def mycorrhiza():
    root = taper(bez([(200, 10), (215, 140), (185, 260), (200, 380)]), 110, 64)
    cap = Point(200, 385).buffer(30)
    hy = []
    for y, s in [(90, 1), (150, -1), (210, 1), (270, -1), (330, 1)]:
        c = bez([(200, y), (200 + s * 70, y - 10), (200 + s * 120, y + 30), (200 + s * 170, y + 10)])
        hy.append(taper(c, 34, 20)); hy.append(Point(*c[-1]).buffer(30))
        hy.append(taper(bez([c[40], c[40] + [s * 10, -40], c[40] + [s * 30, -60], c[40] + [s * 40, -70]]), 24, 14))
    return soft(unary_union([root, cap] + hy), 4)


PICTOS = [("Testate amoeba", testate, "lilac"), ("Nematode", nematode, "berry"), ("Fungal hyphae", hyphae, "olive"),
          ("Mite", mite, "lime"), ("Springtail", springtail, "sage"), ("Tardigrade", tardigrade, "lilac"),
          ("Ciliate", ciliate, "lime"), ("Bacteria", bacteria, "berry"), ("Mycorrhizal root", mycorrhiza, "mint")]


def d_of(g):
    out = []
    for p in getattr(g, "geoms", [g]):
        for r in [p.exterior] + list(p.interiors):
            out.append("M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in np.array(r.coords)) + "Z")
    return "".join(out)


def main():
    import sys
    sys.path.insert(0, os.path.join(HERE, "..", "field-guide"))
    from euglypha import text
    os.makedirs(OUT, exist_ok=True)
    W, H = 3000, 1700
    body = f'<rect width="{W}" height="{H}" fill="{GROUND}"/>'
    pos = [(120, 100), (1100, 100), (2120, 100), (520, 640), (1500, 640), (2400, 640), (120, 1180), (1100, 1180), (2120, 1180)]
    for (name, fn, ink), (x, y) in zip(PICTOS, pos):
        g = fn(); d = d_of(g)
        slug = name.lower().replace(" ", "-")
        for tag, col in list(INKS.items())[:0] + [("color", INKS[ink]), ("white", "#FFFFFF"), ("green", "#156826"), ("black", "#000000")]:
            open(os.path.join(OUT, f"{slug}-{tag}.svg"), "w").write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {S} {S}" width="{S}" height="{S}"><path d="{d}" fill="{col}" fill-rule="evenodd"/></svg>\n')
        body += f'<g transform="translate({x},{y})"><path d="{d}" fill="{INKS[ink]}" fill-rule="evenodd"/></g>'
        body += f'<circle cx="{x + 440}" cy="{y + 392}" r="9" fill="{INKS["lime"]}"/>'
        body += f'<g transform="translate({x + 452},{y + 372}) rotate(-90)">{text(name, 34, 0, 0, color=INKS["lime"])[0]}</g>'
    body += f'<line x1="60" y1="{H - 90}" x2="{W - 60}" y2="{H - 90}" stroke="{INKS["lime"]}" stroke-width="2" opacity=".5"/>'
    body += f'<circle cx="72" cy="{H - 52}" r="9" fill="{INKS["lime"]}"/>' + text("Pictograms of soil life", 34, 95, H - 40, color=INKS["lime"])[0]
    body += text("Soil Food Web", 34, W - 60, H - 40, anchor="end", color=INKS["lime"])[0]
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{body}</svg>\n'
    open(os.path.join(OUT, "sheet.svg"), "w").write(svg)
    Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(), output_width=W, output_height=H))).convert("RGB").save(os.path.join(OUT, "sheet.png"))


if __name__ == "__main__":
    main()
