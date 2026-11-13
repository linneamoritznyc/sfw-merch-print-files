"""SFW field-guide graphics, set 4: twenty more detailed soil organisms. Sources in SOURCES.md ("Graphics set 4").

Usage: python3 graphics_set4.py
"""
import math
import numpy as np
from shapely.geometry import Point, Polygon, LineString, box
from shapely.ops import unary_union
from pages_4_8 import P, circle, ellipse, smooth, blob, stipple, cilia_fringe, DEEP, FWG, LIGHT, WHITE
from graphics_set2 import outline, save, LW
from graphics_set3 import hollow, hook, body_along, nematode_body, trapped_nematode, head_frame

BROWN = "#4F3433"
rng = np.random.default_rng(44)


def scatter_scales(shell, n, rx, ry, fill=WHITE, w=2.2, align=None):
    out, cs = [], []
    for _ in range(n * 40):
        if len(cs) >= n: break
        p = Point(rng.uniform(*shell.bounds[0::2]), rng.uniform(*shell.bounds[1::2]))
        if shell.buffer(-min(rx, ry) * .6).contains(p) and all(p.distance(q) > (rx + ry) * .8 for q in cs):
            cs.append(p)
    for p in cs:
        a = align(p) if align else rng.uniform(0, 180)
        out.append(ellipse(p.x, p.y, rx * rng.uniform(.8, 1.1), ry * rng.uniform(.8, 1.1), a, fill=fill, w=w))
    return "".join(out)


# 1 Nebela: pear-shaped shell covered in recycled plates of other testate amoebae
def nebela():
    Wd, Ht = 800, 1100; cx = 400
    shell = Polygon(smooth([(cx, 1000), (cx + 260, 820), (cx + 280, 520), (cx + 160, 260), (cx + 80, 140), (cx - 80, 140), (cx - 160, 260), (cx - 280, 520), (cx - 260, 820)], 220, closed=True))
    b = [outline(shell, fill=WHITE, w=LW * 1.8)]
    b.append(scatter_scales(shell, 120, 26, 26, w=2))
    b.append(scatter_scales(shell, 70, 30, 14, w=2))
    b.append(ellipse(cx, 140, 84, 22, fill=WHITE, w=LW * 1.8))                      # aperture with organic collar
    b.append(ellipse(cx, 140, 64, 13, fill=LIGHT, stroke=FWG, w=LW))
    b.append(outline(shell, fill="none", w=LW * 1.8))
    save("testate-amoeba-nebela", "".join(b), Wd, Ht)


# 2 Assulina: compressed brown ovoid shell of overlapping elliptical silica plates, toothed oval aperture
def assulina():
    Wd, Ht = 760, 1000; cx = 380
    shell = Polygon(smooth([(cx, 940), (cx + 250, 760), (cx + 270, 450), (cx + 170, 180), (cx, 110), (cx - 170, 180), (cx - 270, 450), (cx - 250, 760)], 220, closed=True))
    b = [outline(shell, fill=BROWN, stroke=DEEP, w=LW * 1.8)]
    for row, y in enumerate(np.arange(880, 150, -46)):                                   # imbricate rows, diagonal
        for k in range(-7, 8):
            x = cx + k * 52 + (26 if row % 2 else 0)
            if shell.buffer(-20).contains(Point(x, y)):
                b.append(ellipse(x, y, 30, 20, -25, fill="#7a5a58", stroke=WHITE, w=2))
    b.append(ellipse(cx, 150, 90, 28, fill=WHITE, stroke=DEEP, w=LW * 1.6))
    teeth = [(cx + (90 - (8 if j % 2 else 0)) * math.cos(t), 150 + (28 - (4 if j % 2 else 0)) * math.sin(t)) for j, t in enumerate(np.linspace(0, 2 * math.pi, 40))]
    b.append(P(teeth, fill="none", w=2))
    b.append(outline(shell, fill="none", stroke=DEEP, w=LW * 1.8))
    save("testate-amoeba-assulina", "".join(b), Wd, Ht)


# 3 Paramecium: slipper shape, cilia, oral groove, macro and micronucleus, two star-shaped contractile vacuoles
def paramecium():
    Wd, Ht = 1500, 700
    o = smooth([(150, 350), (300, 230), (700, 200), (1150, 230), (1360, 330), (1300, 440), (900, 470), (600, 460), (420, 420), (300, 450)], 300, closed=True)
    b = [cilia_fringe(np.array(o), 34, w=2), P(o, fill=LIGHT, stroke=FWG, w=LW * 1.5)]
    b.append(stipple(o, 500, 2.4, FWG))
    b.append(P(smooth([(300, 440), (500, 400), (700, 360), (760, 330)], 60), close=False, w=LW * 2.4))     # oral groove
    b.append(ellipse(800, 330, 130, 70, -5, fill=WHITE, w=LW * 1.4))                                       # macronucleus
    b.append(circle(690, 290, 20, fill=DEEP, stroke=DEEP))                                                  # micronucleus
    for x in (420, 1180):                                                                                   # contractile vacuoles with radiating canals
        b.append(circle(x, 330, 28, fill=WHITE, stroke=FWG, w=LW))
        for k in range(8):
            a = k / 8 * 2 * math.pi
            b.append(P([(x + 30 * math.cos(a), 330 + 30 * math.sin(a)), (x + 80 * math.cos(a), 330 + 60 * math.sin(a))], close=False, w=3, stroke=FWG))
    for x, y in ((1000, 300), (1050, 400), (560, 330)):
        b.append(circle(x, y, 22, fill=FWG, stroke=FWG))
    save("ciliate-paramecium", "".join(b), Wd, Ht)


# 4 Chlamydomonas: two equal flagella, cup chloroplast, pyrenoid, red eyespot, 2 contractile vacuoles, central nucleus
def chlamydomonas():
    Wd, Ht = 800, 1100; cx, cy = 400, 650
    b = [P(smooth([(cx - 20, 380), (cx - 140, 240), (cx - 220, 80)], 60), close=False, w=LW * 1.4),
         P(smooth([(cx + 20, 380), (cx + 140, 240), (cx + 220, 80)], 60), close=False, w=LW * 1.4)]
    b.append(ellipse(cx, cy, 220, 280, fill=WHITE, w=LW * 1.8))
    cup = Point(cx, cy).buffer(250).difference(Point(cx, cy - 60).buffer(150))
    cup = unary_union(cup).intersection(Polygon([(cx - 230, cy - 290), (cx + 230, cy - 290), (cx + 230, cy + 290), (cx - 230, cy + 290)]))
    cup = cup.intersection(Polygon(smooth([(cx, cy - 280), (cx + 220, cy), (cx, cy + 280), (cx - 220, cy)], 120, closed=True)).buffer(-10))
    b.append(outline(cup, fill=FWG, stroke=DEEP, w=LW))
    b.append(circle(cx, cy + 150, 54, fill=LIGHT, stroke=DEEP, w=LW * 1.4))                     # pyrenoid
    b.append(circle(cx, cy - 60, 70, fill=WHITE, w=LW * 1.4)); b.append(circle(cx, cy - 60, 26, fill=DEEP, stroke=DEEP))   # nucleus
    b.append(ellipse(cx + 170, cy - 90, 18, 30, 20, fill="#B8433A", stroke=DEEP, w=2))          # eyespot (the one non-palette red: its true colour)
    for s in (-1, 1):
        b.append(circle(cx + s * 40, 410, 18, fill=WHITE, stroke=FWG, w=2.4))                   # contractile vacuoles at the flagellar base
    save("alga-chlamydomonas", "".join(b), Wd, Ht)


# 5 Actinophrys: spherical, vacuolated outer cytoplasm, one central nucleus, stiff axopodia from the nucleus surface
def actinophrys():
    S = 1100; c = S / 2; R = 220
    b = []
    for k in range(44):
        a = k / 44 * 2 * math.pi + rng.normal(0, .02)
        p0 = (c + 70 * math.cos(a), c + 70 * math.sin(a)); p1 = (c + 520 * math.cos(a), c + 520 * math.sin(a))
        b.append(P([p0, p1], close=False, w=3))
        for f in (.45, .62, .8):
            q = (c + 520 * f * math.cos(a), c + 520 * f * math.sin(a))
            if f * 520 > R + 10:
                b.append(circle(*q, 4, fill=DEEP, stroke=DEEP))
    b.append(circle(c, c, R, fill=WHITE, w=LW * 1.6))
    vac = []
    for _ in range(3000):
        if len(vac) > 90: break
        a = rng.uniform(0, 6.28); r = rng.uniform(95, R - 22); rr = rng.uniform(12, 24)
        p = Point(c + r * math.cos(a), c + r * math.sin(a))
        if all(p.distance(q) > rr + qr + 3 for q, qr in vac) and r + rr < R - 4:
            vac.append((p, rr))
    for p, rr in vac:
        b.append(circle(p.x, p.y, rr, fill=LIGHT, stroke=FWG, w=2))
    b.append(circle(c, c, 72, fill=WHITE, w=LW * 1.4)); b.append(circle(c, c, 26, fill=DEEP, stroke=DEEP))
    b.append(circle(c + R - 10, c - 60, 34, fill=WHITE, stroke=FWG, w=LW))                    # contractile vacuole bulge
    save("heliozoan-actinophrys", "".join(b), S, S)


# 6 Vampyrella: orange-bodied amoeba with radiating filopodia, attached to an algal cell, extracting its contents
def vampyrella():
    Wd, Ht = 1200, 900
    b = [ellipse(780, 520, 300, 160, -8, fill=LIGHT, stroke=FWG, w=LW * 1.6)]
    b.append(stipple([(780 + 280 * math.cos(t), 520 + 140 * math.sin(t)) for t in np.linspace(0, 6.28, 80)], 300, 3, FWG))
    b.append(ellipse(590, 470, 40, 22, -40, fill=WHITE, stroke=DEEP, w=LW))                    # hole dissolved in the algal wall
    cx, cy = 430, 380
    for k in range(36):
        a = k / 36 * 2 * math.pi; L = rng.uniform(170, 260)
        b.append(P([(cx + 90 * math.cos(a), cy + 90 * math.sin(a)), (cx + (90 + L) * math.cos(a), cy + (90 + L) * math.sin(a))], close=False, w=2.2, stroke=DEEP))
    b.append(circle(cx, cy, 120, fill="#D98A3A", stroke=DEEP, w=LW * 1.6))                    # orange body (its true colour)
    b.append(stipple([(cx + 110 * math.cos(t), cy + 110 * math.sin(t)) for t in np.linspace(0, 6.28, 60)], 160, 3, DEEP))
    b.append(P(smooth([(520, 420), (560, 450), (590, 470)], 20), close=False, w=10, stroke="#D98A3A"))
    save("amoeba-vampyrella", "".join(b), Wd, Ht)


# 7 Rhizopus: stolons, rhizoids, sporangiophores in groups, sporangia with apophysis and columella
def rhizopus():
    Wd, Ht = 1300, 1200
    b = [hollow(smooth([(80, 1000), (420, 930), (760, 960), (1220, 920)], 160), 22)]
    for x0 in (380, 900):
        for dx in (-40, 0, 40):                                                                 # rhizoids at the node
            b.append(P(smooth([(x0, 950), (x0 + dx, 1030), (x0 + dx * 2, 1110), (x0 + dx * 2.6, 1170)], 40), close=False, w=5))
            b.append(P([(x0 + dx * 2, 1110), (x0 + dx * 2 + 40, 1150)], close=False, w=3))
        for k, dx in enumerate((-110, 0, 110)):
            top = (x0 + dx * 1.5, 420 - (k == 1) * 160)
            b.append(hollow(smooth([(x0 + dx * .3, 950), (x0 + dx, 700), top], 60), 20))
            if k != 1:
                b.append(circle(top[0], top[1] - 70, 96, fill=LIGHT, stroke=FWG, w=LW * 1.5))
                b.append(stipple([(top[0] + 88 * math.cos(t), top[1] - 70 + 88 * math.sin(t)) for t in np.linspace(0, 6.28, 60)], 120, 5, WHITE))
            else:                                                                               # burst: apophysis and columella
                b.append(P([(top[0] - 20, top[1]), (top[0] - 50, top[1] - 40), (top[0] + 50, top[1] - 40), (top[0] + 20, top[1])], fill=WHITE, w=LW))
                col = [(top[0] + 60 * math.cos(q), top[1] - 40 - 80 * math.sin(q)) for q in np.linspace(0, math.pi, 40)]
                b.append(P(col, fill=WHITE, w=LW * 1.4))
    save("rhizopus", "".join(b), Wd, Ht)


# 8 Alternaria: dark muriform conidia with a beak, in a short chain
def alternaria():
    Wd, Ht = 700, 1300; cx = 350
    b = [hollow([(cx, 1270), (cx, 1080)], 22, fill=BROWN)]
    y = 1080
    for k, L in enumerate((260, 230, 200)):
        top, bot = y - L, y
        body = Polygon(smooth([(cx, bot), (cx + 70, bot - L * .2), (cx + 64, bot - L * .55), (cx + 26, bot - L * .8), (cx + 10, top + 10), (cx - 10, top + 10), (cx - 26, bot - L * .8), (cx - 64, bot - L * .55), (cx - 70, bot - L * .2)], 120, closed=True))
        b.append(outline(body, fill=BROWN, stroke=DEEP, w=LW * 1.4))
        for j in range(1, 6):                                                                    # transverse septa
            yy = bot - L * .8 * j / 6
            seg = LineString([(cx - 100, yy), (cx + 100, yy)]).intersection(body)
            if not seg.is_empty:
                b.append(P(list(seg.coords) if seg.geom_type == "LineString" else list(seg.geoms[0].coords), close=False, w=2.6, stroke=WHITE))
        for j in (2, 4):                                                                         # longitudinal septa
            yy0, yy1 = bot - L * .8 * (j - 1) / 6, bot - L * .8 * j / 6
            b.append(P([(cx + (8 if j == 2 else -8), yy0), (cx + (8 if j == 2 else -8), yy1)], close=False, w=2.6, stroke=WHITE))
        y = top + 6
    save("alternaria-conidia-chain", "".join(b), Wd, Ht)


# 9 Basidium: four sterigmata, each with a basidiospore and its hilar appendix
def basidium():
    Wd, Ht = 900, 1200; cx = 450
    b = [P(smooth([(cx - 60, 1180), (cx - 70, 900), (cx - 90, 620), (cx - 60, 540), (cx + 60, 540), (cx + 90, 620), (cx + 70, 900), (cx + 60, 1180)], 120), fill=LIGHT, stroke=FWG, w=LW * 1.6)]
    b.append(stipple([(cx - 60, 1170), (cx - 85, 620), (cx + 85, 620), (cx + 60, 1170)], 200, 2.6, FWG))
    for k, xo in enumerate((-75, -25, 25, 75)):
        base = (cx + xo, 545)
        tip = (cx + xo * 2.1, 400)
        b.append(P(smooth([base, (cx + xo * 1.5, 470), tip], 20), close=False, w=10))
        b.append(P(smooth([base, (cx + xo * 1.5, 470), tip], 20), close=False, w=4, stroke=LIGHT))
        sx, sy = tip[0] + (14 if xo > 0 else -14), tip[1] - 90
        b.append(ellipse(sx, sy, 46, 78, 12 if xo > 0 else -12, fill=WHITE, w=LW * 1.4))
        b.append(P([tip, (tip[0] + (10 if xo > 0 else -10), tip[1] - 16)], close=False, w=LW * 1.4))   # hilar appendix
    save("fungus-basidium-four-spores", "".join(b), Wd, Ht)


# 10 Arbuscular mycorrhizal spore: layered wall continuous with the subtending hypha, oil droplets inside
def am_spore():
    S = 1000; cx, cy = 500, 430
    b = [hollow(smooth([(500, 980), (520, 820), (500, 700)], 40), 60, fill=WHITE)]
    for r, f, w in ((330, BROWN, LW * 2), (300, "#7a5a58", LW), (270, LIGHT, LW)):
        b.append(circle(cx, cy, r, fill=f, stroke=DEEP, w=w))
    b.append(P([(470, 760), (530, 760)], close=False, w=LW * 1.6))                              # curved septum closing the hypha
    for _ in range(26):
        a = rng.uniform(0, 6.28); r = rng.uniform(0, 210)
        b.append(circle(cx + r * math.cos(a), cy + r * math.sin(a), rng.uniform(14, 34), fill=WHITE, stroke=FWG, w=2.2))
    save("mycorrhiza-am-spore", "".join(b), S, S)


# 11 Yeast: budding cells with bud scars and vacuoles
def yeast():
    Wd, Ht = 1100, 800
    b = []
    cells = [(330, 400, 150, 120, 10), (580, 330, 110, 90, -20), (730, 270, 60, 52, -20), (450, 600, 100, 82, 40), (820, 520, 130, 104, 0)]
    for x, y, rx, ry, a in cells:
        b.append(ellipse(x, y, rx, ry, a, fill=LIGHT, stroke=FWG, w=LW * 1.4))
        b.append(ellipse(x + rx * .1, y, rx * .38, ry * .38, a, fill=WHITE, stroke=FWG, w=2))
        b.append(stipple([(x + rx * .85 * math.cos(t), y + ry * .85 * math.sin(t)) for t in np.linspace(0, 6.28, 40)], int(rx / 2), 2.4, FWG))
    for x, y in ((240, 330), (270, 500), (900, 450)):
        b.append(circle(x, y, 12, fill=WHITE, stroke=DEEP, w=2.4))                                # bud scars
    save("yeast-budding", "".join(b), Wd, Ht)


# 12 Pythium: coenocytic hyphae, sporangium with exit tube and vesicle of zoospores, oogonium with oospore and antheridium
def pythium():
    Wd, Ht = 1400, 900
    b = [hollow(smooth([(60, 700), (400, 650), (800, 700), (1340, 660)], 160), 22)]
    b.append(hollow([(300, 660), (300, 520)], 20))
    b.append(circle(300, 420, 100, fill=WHITE, w=LW * 1.6))                                      # sporangium
    b.append(hollow(smooth([(380, 360), (460, 300), (520, 230)], 30), 16))                       # exit tube
    b.append(circle(560, 180, 95, fill=WHITE, stroke=FWG, w=LW))                                 # thin vesicle
    for _ in range(12):
        a = rng.uniform(0, 6.28); r = rng.uniform(0, 60)
        x, y = 560 + r * math.cos(a), 180 + r * math.sin(a)
        b.append(ellipse(x, y, 16, 11, rng.uniform(0, 180), fill=LIGHT, stroke=FWG, w=2))
        b.append(P([(x, y), (x + 20, y - 18)], close=False, w=1.6))
    b.append(hollow([(950, 690), (960, 520)], 20))
    b.append(circle(960, 420, 110, fill=WHITE, w=LW * 1.6))                                      # oogonium
    b.append(circle(960, 420, 74, fill=LIGHT, stroke=DEEP, w=LW * 3))                            # thick-walled oospore
    b.append(circle(985, 400, 22, fill=WHITE, stroke=FWG, w=2))
    b.append(hollow(smooth([(1150, 680), (1160, 520), (1080, 380)], 40), 16))                    # antheridial hypha
    b.append(ellipse(1065, 360, 40, 26, -40, fill=WHITE, w=LW * 1.3))                            # antheridium pressed on the oogonium
    save("oomycete-pythium", "".join(b), Wd, Ht)


# 13 Root-knot nematode female: white, pear-shaped, prominent neck, embedded in a root
def root_knot():
    Wd, Ht = 1100, 1000
    b = []                                                                             # no root block: transparent like the rest
    body = Polygon(smooth([(520, 220), (560, 330), (700, 420), (790, 600), (740, 800), (540, 880), (340, 800), (290, 600), (380, 420), (480, 330)], 200, closed=True))
    b.append(outline(body, fill=WHITE, stroke=DEEP, w=LW * 1.8))
    b.append(P([(520, 240), (520, 300)], close=False, w=6))                                        # stylet in the neck
    b.append(ellipse(520, 360, 28, 22, fill=WHITE, w=LW))                                          # median bulb
    for _ in range(14):                                                                            # giant feeding cells around the head
        pass
    for x, y in ((380, 210), (640, 230), (470, 120)):
        b.append(ellipse(x, y, 90, 60, rng.uniform(0, 60), fill=WHITE, stroke=FWG, w=LW))
        b.append(stipple([(x + 80 * math.cos(t), y + 50 * math.sin(t)) for t in np.linspace(0, 6.28, 40)], 40, 3, FWG))
    b.append(stipple(list(body.buffer(-40).exterior.coords), 300, 3, FWG))
    save("nematode-root-knot-female", "".join(b), Wd, Ht)


# 14 Dorylaim head: hollow, movable odontostyle with guiding ring, cylindrical pharynx widening behind
def dorylaim_head():
    Wd, Ht = 1500, 600; y0 = 300
    b, X, edge = head_frame(100, y0, 1300, 180)
    b.append(P([(X(.02), y0 - 9), (X(.20), y0 - 9), (X(.20), y0 + 9), (X(.02), y0 + 9), (X(-.01), y0)], fill=WHITE, w=LW * 1.4))   # hollow odontostyle
    b.append(P([(X(.02), y0), (X(.20), y0)], close=False, w=2))
    b.append(P([(X(.20), y0 - 6), (X(.33), y0 - 6), (X(.33), y0 + 6), (X(.20), y0 + 6)], fill=DEEP, w=2))                          # odontophore
    for s in (-1, 1):
        b.append(P([(X(.09), y0 + s * 14), (X(.09), y0 + s * 40)], close=False, w=LW * 1.6))                                         # guiding ring
        b.append(P([(X(.115), y0 + s * 14), (X(.115), y0 + s * 40)], close=False, w=LW * 1.6))
    pu = [.33, .62, .68, 1.06]; pv = [.12, .14, .42, .42]
    uu = np.linspace(.33, 1.06, 160); vv = np.interp(uu, pu, pv)
    poly = [(X(u), y0 - v * 180) for u, v in zip(uu, vv)] + [(X(u), y0 + v * 180) for u, v in zip(uu[::-1], vv[::-1])]
    b.append(P(poly, fill=LIGHT, stroke=FWG, w=LW * 1.2))
    b.append(P([(X(.33), y0), (X(1.06), y0)], close=False, w=2.2))
    b.append(f'<rect x="{X(.48) - 14:.1f}" y="{y0 - 70:.1f}" width="28" height="140" rx="10" fill="{FWG}"/>')
    save("nematode-omnivore-dorylaim-head", "".join(b), Wd, Ht)


# 15 Enchytraeid potworm: white, transparent, segments, four bundles of straight setae per segment, clitellum
def enchytraeid():
    Wd, Ht = 1600, 600
    cl = smooth([(80, 300), (420, 220), (800, 340), (1200, 260), (1520, 300)], 400)
    u = np.linspace(0, 1, len(cl))
    half = 72 * np.minimum(1, .55 + .45 * np.clip(u / .05, 0, 1)) * np.minimum(1, .5 + .5 * np.clip((1 - u) / .05, 0, 1)) * np.where((u > .2) & (u < .27), 1.15, 1)
    pts, n, t = body_along(cl, half)
    b = [P(pts, fill=WHITE, stroke=DEEP, w=LW * 1.5)]
    gut = body_along(cl[40:-20], half[40:-20] * .4)[0]
    b.append(P(gut, fill=LIGHT, stroke=FWG, w=2))
    segs = []
    for k in np.arange(.03, .98, .025):
        i = int(k * (len(cl) - 1))
        p, q = cl[i] + n[i] * half[i] * .98, cl[i] - n[i] * half[i] * .98
        segs.append(f"M{p[0]:.1f},{p[1]:.1f}L{q[0]:.1f},{q[1]:.1f}")
        for side, f in ((1, .7), (-1, .7)):                                               # setal bundles, straight
            s0 = cl[i] + n[i] * half[i] * side * f
            for j in (-1, 0, 1):
                d = n[i] * side * 34 + t[i] * j * 10
                segs.append(f"M{s0[0]:.1f},{s0[1]:.1f}l{d[0]:.1f},{d[1]:.1f}")
    b.append(f'<path d="{"".join(segs)}" stroke="{DEEP}" stroke-width="2" fill="none" stroke-linecap="round"/>')
    i0, i1 = int(.2 * len(cl)), int(.27 * len(cl))
    b.append(P(body_along(cl[i0:i1], half[i0:i1])[0], fill=LIGHT, stroke=DEEP, w=LW))
    save("potworm-enchytraeid", "".join(b), Wd, Ht)


# 16 Predatory mite (Mesostigmata) feeding on a nematode
def predatory_mite():
    Wd, Ht = 1300, 1100; cx, cy = 650, 560
    b = []
    b += trapped_nematode(smooth([(120, 120), (380, 230), (650, 250), (900, 200), (1160, 110)], 260), 46)
    legs = []
    for s in (-1, 1):
        for k, ang in enumerate((-125, -160, 160, 125)):
            bx, by = cx + s * 100, cy - 120 + k * 80
            a = math.radians(ang if s < 0 else 180 - ang)
            pts = [(bx, by)]
            for j, L in enumerate((90, 80, 70, 60)):
                a2 = a + s * math.radians(-10 + j * 8)
                pts.append((pts[-1][0] + L * math.cos(a2), pts[-1][1] + L * math.sin(a2)))
            b.append(hollow(pts, 22))
            b.append(hook(pts[-1][0], pts[-1][1], 18, math.degrees(a)))
    b.append(ellipse(cx, cy + 40, 170, 220, fill=LIGHT, stroke=FWG, w=LW * 1.6))
    b.append(ellipse(cx, cy + 30, 140, 190, fill="none", stroke=FWG, w=2))                    # dorsal shield
    for k in range(10):
        a = rng.uniform(0, 6.28); r = rng.uniform(40, 130)
        x, y = cx + r * math.cos(a), cy + 40 + r * 1.2 * math.sin(a)
        b.append(P([(x, y), (x + 16, y - 10)], close=False, w=2))
    for s in (-1, 1):                                                                          # chelicerae reaching for the prey
        b.append(P([(cx + s * 16, cy - 170), (cx + s * 26, cy - 250), (cx + s * 8, cy - 295)], close=False, w=12))
    save("predatory-mite", "".join(b), Wd, Ht)


# 17 Pseudoscorpion: chelate pedipalps, eight legs, no tail
def pseudoscorpion():
    Wd, Ht = 1300, 1300; cx = 650
    b = []
    for s in (-1, 1):
        pal = [(cx + s * 90, 470), (cx + s * 260, 380), (cx + s * 330, 220), (cx + s * 300, 120)]
        b.append(hollow(pal[:3], 46))
        claw = Polygon(smooth([(cx + s * 300, 240), (cx + s * 380, 170), (cx + s * 360, 60), (cx + s * 320, 40), (cx + s * 300, 140), (cx + s * 260, 200)], 60, closed=True))
        b.append(outline(claw, fill=LIGHT, stroke=FWG, w=LW * 1.4))
        b.append(P([(cx + s * 300, 140), (cx + s * 280, 50)], close=False, w=LW * 1.4))        # movable finger
        for k, ang in enumerate((-150, -170, 170, 150)):
            a = math.radians(ang if s < 0 else 180 - ang)
            p0 = (cx + s * 90, 560 + k * 80)
            p1 = (p0[0] + 140 * math.cos(a), p0[1] + 140 * math.sin(a) - 30)
            p2 = (p1[0] + 110 * math.cos(a + s * .6), p1[1] + 110 * math.sin(a + s * .6) + 60)
            b.append(hollow([p0, p1, p2], 22))
    b.append(ellipse(cx, 480, 110, 90, fill=LIGHT, stroke=FWG, w=LW * 1.5))                 # carapace
    for s in (-1, 1):
        b.append(circle(cx + s * 50, 430, 10, fill=DEEP, stroke=DEEP))
    abd = Polygon(smooth([(cx, 560), (cx + 140, 620), (cx + 170, 860), (cx + 110, 1100), (cx, 1160), (cx - 110, 1100), (cx - 170, 860), (cx - 140, 620)], 160, closed=True))
    b.append(outline(abd, fill=LIGHT, stroke=FWG, w=LW * 1.5))
    for y in np.arange(640, 1140, 50):                                                        # tergites, rounded end, no tail
        seg = LineString([(cx - 200, y), (cx + 200, y)]).intersection(abd.buffer(-6))
        if not seg.is_empty and seg.geom_type == "LineString":
            b.append(P(list(seg.coords), close=False, w=2.4, stroke=FWG))
    save("pseudoscorpion", "".join(b), Wd, Ht)


# 18 Bacillus endospores: central, subterminal, terminal, and terminal swelling the cell
def endospores():
    Wd, Ht = 1300, 700
    b = []
    rods = [(200, "central"), (500, "subterminal"), (800, "terminal"), (1100, "swollen")]
    for x, kind in rods:
        r = LineString([(x, 140), (x, 560)]).buffer(70, 24)
        if kind == "swollen":
            r = r.union(Point(x, 540).buffer(95))
        b.append(outline(r, fill=LIGHT, stroke=FWG, w=LW * 1.5))
        y = {"central": 350, "subterminal": 470, "terminal": 540, "swollen": 540}[kind]
        rr = 95 if kind == "swollen" else 55
        b.append(ellipse(x, y, rr * .78, rr, fill=WHITE, stroke=DEEP, w=LW * 2.2))
        b.append(ellipse(x, y, rr * .52, rr * .72, fill=FWG, stroke=DEEP, w=LW))
    save("bacteria-bacillus-endospores", "".join(b), Wd, Ht)


# 19 Myxobacteria fruiting body (Chondromyces): stalk with a head of sporangioles
def myxobacteria():
    Wd, Ht = 900, 1300; cx = 450
    b = [P(smooth([(cx - 220, 1250), (cx, 1220), (cx + 220, 1250)], 40), close=False, w=LW * 1.6)]
    stalk = [(cx - 40, 1230), (cx - 30, 800), (cx - 16, 520), (cx + 16, 520), (cx + 30, 800), (cx + 40, 1230)]
    b.append(P(smooth(stalk, 80), fill=LIGHT, stroke=FWG, w=LW * 1.5))
    for x in np.arange(cx - 30, cx + 31, 15):
        b.append(P([(x, 1220), (x * .6 + cx * .4, 540)], close=False, w=1.6, stroke=FWG))
    for k in range(34):                                                                      # sporangioles around the head
        a = rng.uniform(-math.pi, 0); r = rng.uniform(80, 250)
        x, y = cx + r * math.cos(a) * .9, 470 + r * math.sin(a) * 1.0
        b.append(P([(cx, 520), (x, y)], close=False, w=3, stroke=FWG))
    for k in range(34):
        a = rng.uniform(-math.pi, 0); r = rng.uniform(100, 260)
        x, y = cx + r * math.cos(a) * .9, 470 + r * math.sin(a)
        b.append(ellipse(x, y, 30, 44, math.degrees(a) + 90, fill=WHITE, stroke=DEEP, w=LW * 1.2))
        b.append(stipple([(x + 22 * math.cos(t), y + 34 * math.sin(t)) for t in np.linspace(0, 6.28, 30)], 10, 2.4, FWG))
    save("myxobacteria-fruiting-body", "".join(b), Wd, Ht)


# 20 Lichen cross section: upper cortex, algal layer, medulla, lower cortex, rhizines
def lichen():
    Wd, Ht = 1500, 900
    b = []
    top, ac, med, low, bot = 120, 230, 380, 660, 740
    b.append(f'<rect x="40" y="{top}" width="1420" height="{bot - top}" rx="40" fill="{WHITE}" stroke="{DEEP}" stroke-width="{LW * 1.6}"/>')
    b.append(f'<rect x="40" y="{top}" width="1420" height="{ac - top}" rx="40" fill="{LIGHT}" stroke="{FWG}" stroke-width="2"/>')   # upper cortex
    hyp = []
    for _ in range(500):
        x, y = rng.uniform(60, 1440), rng.uniform(top + 10, ac - 10); a = rng.uniform(-.4, .4)
        hyp.append(f"M{x:.1f},{y:.1f}l{30 * math.cos(a):.1f},{30 * math.sin(a):.1f}")
    for _ in range(260):                                                                      # loose medulla hyphae
        x, y = rng.uniform(60, 1440), rng.uniform(med + 20, low - 20); a = rng.uniform(0, 6.28)
        hyp.append(f"M{x:.1f},{y:.1f}q{40 * math.cos(a):.1f},{40 * math.sin(a):.1f} {70 * math.cos(a + .5):.1f},{70 * math.sin(a + .5):.1f}")
    b.append(f'<path d="{"".join(hyp)}" stroke="{FWG}" stroke-width="2.2" fill="none" stroke-linecap="round"/>')
    for _ in range(170):                                                                      # algal layer: round green photobiont cells
        x, y = rng.uniform(70, 1430), rng.uniform(ac + 20, med - 10)
        b.append(circle(x, y, rng.uniform(12, 18), fill=FWG, stroke=DEEP, w=1.6))
    b.append(f'<rect x="40" y="{low}" width="1420" height="{bot - low}" rx="30" fill="{LIGHT}" stroke="{FWG}" stroke-width="2"/>')    # lower cortex
    for x in range(120, 1440, 150):                                                           # rhizines anchoring the thallus
        b.append(P(smooth([(x, bot), (x + 10, 800), (x - 10, 860)], 20), close=False, w=10))
        b.append(P([(x - 10, 860), (x - 40, 880)], close=False, w=5)); b.append(P([(x - 10, 860), (x + 20, 885)], close=False, w=5))
    save("lichen-cross-section", "".join(b), Wd, Ht)


def main():
    for f in (nebela, assulina, paramecium, chlamydomonas, actinophrys, vampyrella, rhizopus, alternaria, basidium, am_spore,
              yeast, pythium, root_knot, dorylaim_head, enchytraeid, predatory_mite, pseudoscorpion, endospores, myxobacteria, lichen):
        f()


if __name__ == "__main__":
    main()
