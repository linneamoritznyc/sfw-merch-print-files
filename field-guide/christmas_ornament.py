"""Hyphal scroll ornament for the SFW Christmas card: half drawn once, mirrored, so it is exactly symmetric.
Scrolls are fungal hyphae ending in round spores, leaves are flagellate cells, the centre is a colonial flagellate fan."""
import sys, math, io
import numpy as np
from shapely.geometry import Point, Polygon, LineString
from shapely.ops import unary_union
from shapely import affinity
import cairosvg
from PIL import Image

def curve(p0, h0, L, kappa, n=400):
    ds = L / n; x, y, h = p0[0], p0[1], h0; pts = [(x, y)]
    for i in range(n):
        h += kappa(i / n) * ds; x += math.cos(h) * ds; y += math.sin(h) * ds; pts.append((x, y))
    return np.array(pts)

class Ink:
    def __init__(s): s.g = []
    def swell(s, pts, w0, w1, w2, peak=.3):
        pts = np.asarray(pts, float); u = np.linspace(0, 1, len(pts))
        w = np.where(u < peak, w0 + (w1 - w0) * np.sin(u / peak * math.pi / 2), w2 + (w1 - w2) * np.cos((u - peak) / (1 - peak) * math.pi / 2))
        s.g.append(unary_union([Point(*pts[i]).buffer(w[i] / 2, 10).union(Point(*pts[i + 1]).buffer(w[i + 1] / 2, 10)).convex_hull for i in range(len(pts) - 1)]))
    def disc(s, c, r): s.g.append(Point(*c).buffer(r, 32))
    def leaf(s, base, h, L, wid):
        """flagellate cell as a leaf: teardrop body on the tip, with a flagellum"""
        t = np.linspace(0, math.pi, 40)
        prof = [(L * (1 - math.cos(a)) / 2, wid * math.sin(a) ** 1.3 * (1 - .35 * (1 - math.cos(a)) / 2)) for a in t]
        P = prof + [(x, -y) for x, y in prof[::-1]]
        c, sn = math.cos(h), math.sin(h)
        s.g.append(Polygon([(base[0] + x * c - y * sn, base[1] + x * sn + y * c) for x, y in P]))
    def union(s): return unary_union(s.g)

def tang(c, j):
    t = c[min(j + 2, len(c) - 1)] - c[max(j - 2, 0)]; return math.atan2(t[1], t[0])

def spores(ink, c, h, n, r):
    x, y = c
    for k in range(n):
        rr = r * (1 - .16 * k); d = rr * (1.25 if k == 0 else 1.95)
        x += math.cos(h) * d; y += math.sin(h) * d; ink.disc((x, y), rr)

def half(s=1.0):
    ink = Ink()
    # A: main arm, rises gently then rolls into a big volute curling into the card
    A = curve((s*16, s*64), math.radians(-14), s*520, lambda u: 1/(s*900) + (1/(s*15)) * u ** 3.4)
    ink.swell(A, s*12, s*26, s*9, .3); ink.disc(A[-1], s*14)
    # B: under scroll, S curve curling the other way
    B = curve((s*12, s*84), math.radians(30), s*300, lambda u: -1/(s*700) - (1/(s*13)) * u ** 3.0)
    ink.swell(B, s*10, s*19, s*8, .3); ink.disc(B[-1], s*11)
    # spore-chain hyphae rising from the arm toward the rule
    for f, dh, L, k, n in ((.2, -62, 70, .006, 3), (.38, -55, 80, .008, 4), (.56, -40, 66, .01, 3)):
        j = int(f * len(A)); h = tang(A, j) + math.radians(dh)
        c = curve(A[j], h, s*L, lambda u: k / s * u, 80); ink.swell(c, s*7, s*6, s*3.5, .1)
        spores(ink, c[-1], tang(c, len(c) - 1), n, s*6)
    # flagellate-cell leaves hanging under the arm into the card
    for f, dh, L in ((.3, 70, 46), (.47, 80, 52)):
        j = int(f * len(A)); h = tang(A, j) + math.radians(dh)
        st = curve(A[j], h, s*26, lambda u: 0, 10); ink.swell(st, s*6, s*5, s*4, .2)
        ink.leaf(st[-1], h, s*L, s*12)
        fl = [st[-1] + np.array([math.cos(h), math.sin(h)]) * (s*L + s*36*u) + np.array([-math.sin(h), math.cos(h)]) * s*4*math.sin(u*11) for u in np.linspace(0, 1, 40)]
        ink.swell(fl, s*3, s*2.4, s*.6, .05)
    # spore chain off B toward the centre of the card
    j = int(.45 * len(B)); h = tang(B, j) + math.radians(60)
    c = curve(B[j], h, s*50, lambda u: -.012 / s * u, 60); ink.swell(c, s*6, s*5, s*3, .1)
    spores(ink, c[-1], tang(c, len(c) - 1), 3, s*5.5)
    return ink.union()

def centre(s=1.0):
    ink = Ink()
    # colonial flagellate fan, pointing into the card: the fleur-de-lis
    base = np.array([0, s*64])
    ink.disc(base, s*16)
    n, spread = 9, 120
    for k in range(n):
        q = (k - (n - 1) / 2) / ((n - 1) / 2)
        a = math.radians(90 + q * spread / 2)
        L = s * (150 - 34 * q * q)
        c = curve(base, a, L, lambda u: -q * .0016 / s, 100); ink.swell(c, s*7, s*5, s*3, .1)
        h = tang(c, len(c) - 1); ink.leaf(c[-1], h, s*36, s*10)
        fl = [c[-1] + np.array([math.cos(h), math.sin(h)]) * (s*35 + s*40*u) + np.array([-math.sin(h), math.cos(h)]) * s*4*math.sin(u*11) for u in np.linspace(0, 1, 40)]
        ink.swell(fl, s*2.8, s*2.2, s*.6, .05)
    # small crown toward the rule
    for k in range(5):
        a = math.radians(-90 + (k - 2) * 26)
        c = curve(base + [0, -s*10], a, s*(36 - 6 * abs(k - 2)), lambda u: 0, 20); ink.swell(c, s*6, s*5, s*3, .1)
        ink.disc(c[-1], s*5.5)
    return ink.union()

def ornament(s=1.0):
    h = half(s); g = unary_union([h, affinity.scale(h, -1, 1, origin=(0, 0)), centre(s)])
    return affinity.translate(g, 0, -g.bounds[1])

def d_of(g):
    out = []
    for p in getattr(g, "geoms", [g]):
        for r in [p.exterior] + list(p.interiors):
            out.append("M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in np.array(r.coords)) + "Z")
    return "".join(out)

if __name__ == "__main__":
    g = ornament()
    x0, y0, x1, y1 = g.bounds; print(g.bounds)
    g = affinity.translate(g, -x0 + 40, -y0 + 40); Wd, Hd = int(x1 - x0 + 80), int(y1 - y0 + 80)
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{Wd}" height="{Hd}"><rect width="100%" height="100%" fill="#22371F"/><path fill="#fff" fill-rule="evenodd" d="{d_of(g)}"/></svg>'
    cairosvg.svg2png(bytestring=svg.encode(), write_to=sys.argv[1])
