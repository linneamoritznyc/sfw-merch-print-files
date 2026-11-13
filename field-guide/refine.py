"""Quality pass: redraw the weakest graphics at the level of the field-guide plates.
Rules: heavy outer contour, fine inner lines, shading by stipple that gets denser on the shadow side
(light from the upper left), jointed segments, setae, every part from the sources in SOURCES.md.

Usage: python3 refine.py  ->  overwrites out/graphics/sfw-tardigrade, -pseudoscorpion, -rotifer-bdelloid
"""
import math
import numpy as np
from shapely.geometry import Point, Polygon, LineString
from shapely.ops import unary_union
from shapely.prepared import prep
from pages_4_8 import smooth, DEEP, FWG, LIGHT, WHITE
from graphics_set2 import save

rng = np.random.default_rng(7)
HEAVY, MED, FINE = 6.0, 3.2, 2.0


def d(pts, close=True):
    return "M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + ("Z" if close else "")


def shape(geom, fill=WHITE, stroke=DEEP, w=HEAVY):
    out = []
    for g in getattr(geom, "geoms", [geom]):
        if g.geom_type != "Polygon":
            continue
        p = d(np.array(g.exterior.coords)[:-1]) + "".join(d(np.array(r.coords)[:-1]) for r in g.interiors)
        out.append(f'<path d="{p}" fill="{fill}" fill-rule="evenodd" stroke="{stroke}" stroke-width="{w}" stroke-linejoin="round"/>')
    return "".join(out)


def line(pts, w=FINE, c=DEEP):
    return f'<path d="{d(pts, False)}" fill="none" stroke="{c}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>'


def shade(geom, n, r=2.6, c=FWG, light=(-.6, -.8), power=2.2):
    """Engraver stipple: dense on the side away from the light, empty in the highlight."""
    minx, miny, maxx, maxy = geom.bounds
    cx, cy = (minx + maxx) / 2, (miny + maxy) / 2
    span = max(maxx - minx, maxy - miny) / 2
    lx, ly = light
    pg = prep(geom); out = []; tries = 0
    while len(out) < n and tries < n * 60:
        tries += 1
        x, y = rng.uniform(minx, maxx), rng.uniform(miny, maxy)
        t = ((x - cx) * -lx + (y - cy) * -ly) / span          # -1 lit side ... +1 shadow side
        if rng.random() > (min(1.0, max(0.0, (t + 1) / 2))) ** power:
            continue
        if pg.contains(Point(x, y)):
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r * rng.uniform(.75, 1.15):.1f}" fill="{c}"/>')
    return "".join(out)


def tube(pts, w0, w1):
    """Tapering limb segment as a polygon."""
    pts = np.asarray(pts, float); L = len(pts)
    t = np.gradient(pts, axis=0); t /= np.linalg.norm(t, axis=1)[:, None]; n = np.c_[-t[:, 1], t[:, 0]]
    w = np.linspace(w0, w1, L)[:, None] / 2
    return Polygon(np.vstack([pts + n * w, (pts - n * w)[::-1]])).buffer(0)


def seta(x, y, ang, L, w=1.6):
    a = math.radians(ang)
    return line([(x, y), (x + L * math.cos(a), y + L * math.sin(a))], w)


# ------------------------------------------------------------------ tardigrade (eutardigrade, lateral view)
def tardigrade():
    Wd, Ht = 1700, 1150
    body = Polygon(smooth([(230, 560), (290, 420), (430, 320), (650, 265), (900, 255), (1150, 285), (1350, 365),
                           (1470, 490), (1490, 620), (1420, 720), (1220, 780), (900, 795), (600, 785), (380, 730), (255, 650)], 300, closed=True))
    out = []
    legs = [(520, 1), (790, 1), (1060, 1), (1390, 0)]
    def leg_poly(x, rear, dx=0):
        if rear:
            pts = smooth([(x + dx, 650), (x + dx + 8, 760), (x + dx - 4, 850)], 40)
        else:
            pts = smooth([(1380 + dx, 600), (1500 + dx, 700), (1570 + dx, 800)], 40)
        return tube(pts, 170, 120).union(Point(*pts[-1]).buffer(60)), pts
    for far in (True, False):
        for x, normal in legs:
            dx = 60 if far else 0
            lp, pts = leg_poly(x, normal, dx)
            lp = lp.difference(body.buffer(-2))
            out.append(shape(lp, fill=WHITE, stroke=FWG if far else DEEP, w=MED if far else HEAVY * .8))
            tip = np.array(pts[-1]) + (np.array(pts[-1]) - np.array(pts[-6])) / np.linalg.norm(np.array(pts[-1]) - np.array(pts[-6])) * 40; dv = tip - np.array(pts[-6]); dv /= np.linalg.norm(dv); nv = np.array([-dv[1], dv[0]])
            if not far:
                out.append(shade(lp, 260, 2.2, c=FWG, light=(-.9, -.2)))
                for j in (.55, .8):
                    p = np.array(pts[int(j * (len(pts) - 1))])
                    out.append(line([tuple(p - nv * 50), tuple(p + dv * 10), tuple(p + nv * 50)], FINE, FWG))
            c = FWG if far else DEEP
            for sgn in (-1, 1):                                   # two double claws per leg
                base = tip + dv * 6 + nv * sgn * 22
                ang = math.atan2(dv[1], dv[0]) + sgn * .35
                prim = [tuple(base + 74 * u * np.array([math.cos(ang), math.sin(ang)]) + nv * sgn * 26 * u * u) for u in np.linspace(0, 1, 18)]
                sec = [tuple(base + 40 * u * np.array([math.cos(ang + sgn * .75), math.sin(ang + sgn * .75)])) for u in np.linspace(0, 1, 10)]
                out.append(line(prim, MED * 1.3, c)); out.append(line(sec, MED, c))
                out.append(f'<circle cx="{base[0]:.1f}" cy="{base[1]:.1f}" r="8" fill="{c}"/>')
    out.append(shape(body, fill=WHITE, w=HEAVY))
    out.append(shade(body, 2300, 2.3, c=FWG, light=(-.45, -.9), power=2.8))
    for x in (520, 790, 1060, 1290):
        out.append(line(smooth([(x, 262), (x - 24, 520), (x + 4, 788)], 40), FINE, FWG))
    gut = Polygon(smooth([(620, 470), (820, 405), (1110, 420), (1300, 515), (1190, 620), (860, 640), (650, 590)], 160, closed=True))
    out.append(shape(gut, fill=WHITE, stroke=FWG, w=MED))
    out.append(shade(gut, 1100, 3, c=FWG, light=(0, -1), power=1.2))
    for x, y, r in ((720, 335, 22), (930, 315, 20), (1170, 350, 22), (1370, 470, 18), (520, 690, 18), (1330, 680, 20)):
        out.append(shape(Point(x, y).buffer(r), fill=WHITE, stroke=FWG, w=FINE))
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r * .3:.1f}" fill="{FWG}"/>')
    out.append(shape(Point(244, 585).buffer(24), fill=WHITE, w=MED))
    for k in range(12):
        a = k / 12 * 2 * math.pi
        out.append(line([(244 + 24 * math.cos(a), 585 + 24 * math.sin(a)), (244 + 36 * math.cos(a), 585 + 36 * math.sin(a))], FINE))
    out.append(shape(tube([(268, 582), (452, 552)], 24, 20), fill=WHITE, w=MED))
    for sg in (-1, 1):
        out.append(line([(285, 582 + sg * 30), (470, 552 + sg * 52)], MED))
        out.append(line([(425, 552 + sg * 46), (475, 552 + sg * 86)], FINE))
    out.append(shape(Point(532, 545).buffer(70), fill=WHITE, w=MED))
    for k in (-1, 0, 1):
        for j in (0, 1):
            out.append(f'<rect x="{502 + j * 32:.1f}" y="{545 + k * 22 - 6:.1f}" width="22" height="12" rx="5" fill="{DEEP}"/>')
    out.append(f'<circle cx="330" cy="465" r="13" fill="{DEEP}"/><circle cx="326" cy="461" r="4" fill="{WHITE}"/>')
    save("tardigrade", "".join(out), Wd, Ht)


# ------------------------------------------------------------------ pseudoscorpion (dorsal view)
def pseudoscorpion():
    Wd, Ht = 1400, 1750; cx = 700
    out = ['<g transform="translate(0,150)">']
    # walking legs: 4 pairs, each trochanter, femur, patella, tibia, tarsus, with a claw pair
    for s in (-1, 1):
        for k, ang in enumerate((-150, -170, 160, 132)):
            a = math.radians(ang if s < 0 else 180 - ang)
            p = [np.array([cx + s * 120, 600 + k * 90])]
            lens = (70, 120, 70, 110, 90)
            for j, L in enumerate(lens):
                a2 = a + s * math.radians(j * (6 if k < 2 else -6))
                p.append(p[-1] + L * np.array([math.cos(a2), math.sin(a2)]))
            for j in range(len(lens)):
                seg = tube([p[j], p[j + 1]], 44 - j * 4, 38 - j * 4).union(Point(*p[j + 1]).buffer(17 - j * 2))
                out.append(shape(seg, fill=LIGHT, w=MED * 1.1))
                out.append(shade(seg, 60, 2, light=(0, -1)))
            tip = p[-1]; dv = (p[-1] - p[-2]) / np.linalg.norm(p[-1] - p[-2])
            for q in (-.5, .5):
                c = math.atan2(dv[1], dv[0]) + q
                out.append(line([tuple(tip), (tip[0] + 22 * math.cos(c), tip[1] + 22 * math.sin(c))], MED))
    # pedipalps: trochanter, femur, patella, then the chela: swollen hand, fixed and movable finger with teeth
    for s in (-1, 1):
        joints = [np.array([cx + s * 80, 520]), np.array([cx + s * 180, 470]), np.array([cx + s * 330, 390]), np.array([cx + s * 400, 290])]
        widths = [(60, 50), (52, 46), (66, 54)]
        for j in range(3):
            seg = tube(smooth([joints[j], (joints[j] + joints[j + 1]) / 2 + np.array([s * 6, 0]), joints[j + 1]], 20), *widths[j])
            out.append(shape(seg, fill=LIGHT, w=HEAVY * .8)); out.append(shade(seg, 90, 2.2, light=(-s * .6, -.8)))
        hand = Polygon(smooth([joints[3] + [s * -40, 20], joints[3] + [s * 60, 10], joints[3] + [s * 90, -90], joints[3] + [s * 40, -170], joints[3] + [s * -20, -150], joints[3] + [s * -50, -60]], 80, closed=True))
        out.append(shape(hand, fill=LIGHT, w=HEAVY)); out.append(shade(hand, 260, 2.4, light=(-s * .6, -.8)))
        base = joints[3] + [s * 10, -160]
        fixed = [tuple(base + [s * -34, 0] + [s * 34 * u * u, -190 * u]) for u in np.linspace(0, 1, 20)]
        moving = [tuple(base + [s * 34, 0] + [s * -30 * u * u, -186 * u]) for u in np.linspace(0, 1, 20)]
        out.append(shape(tube(fixed, 30, 6), fill=LIGHT, w=MED * 1.2))
        out.append(shape(tube(moving, 28, 6), fill=LIGHT, w=MED * 1.2))
        for u in np.linspace(.15, .85, 8):                                   # teeth along the inner edge of each finger
            i = int(u * 19)
            out.append(line([fixed[i], (fixed[i][0] + s * 10, fixed[i][1] - 4)], FINE))
            out.append(line([moving[i], (moving[i][0] - s * 10, moving[i][1] - 4)], FINE))
        out.append(seta(base[0] + s * 30, base[1] - 80, -90 + s * 40, 40))   # trichobothria (sensory setae)
        out.append(seta(base[0] - s * 10, base[1] - 120, -90 - s * 40, 44))
    # carapace with two pairs of eyes, then the abdomen of paired tergites, rounded end, no tail
    cara = Polygon(smooth([(cx - 120, 600), (cx - 130, 470), (cx - 70, 390), (cx + 70, 390), (cx + 130, 470), (cx + 120, 600)], 120, closed=True))
    out.append(shape(cara, fill=LIGHT, w=HEAVY)); out.append(shade(cara, 600, 2.4))
    out.append(line(smooth([(cx - 110, 520), (cx, 535), (cx + 110, 520)], 30), FINE, FWG))   # carapace furrow
    for s in (-1, 1):
        for dy in (0, 26):
            out.append(f'<circle cx="{cx + s * 96:.1f}" cy="{430 + dy:.1f}" r="11" fill="{DEEP}"/><circle cx="{cx + s * 93:.1f}" cy="{427 + dy:.1f}" r="3.5" fill="{WHITE}"/>')
    for s in (-1, 1):                                                          # chelicerae at the front
        out.append(shape(tube([(cx + s * 26, 400), (cx + s * 30, 340)], 34, 20), fill=LIGHT, w=MED))
    abd = Polygon(smooth([(cx - 130, 610), (cx - 175, 800), (cx - 180, 1100), (cx - 130, 1380), (cx, 1450), (cx + 130, 1380), (cx + 180, 1100), (cx + 175, 800), (cx + 130, 610)], 200, closed=True))
    out.append(shape(abd, fill=LIGHT, w=HEAVY)); out.append(shade(abd, 1900, 2.4, light=(-.5, -.85)))
    for y in np.arange(660, 1420, 72):                                        # 11 tergites, divided down the middle
        seg = LineString([(cx - 220, y), (cx + 220, y)]).intersection(abd.buffer(-4))
        if seg.geom_type == "LineString":
            out.append(line(list(seg.coords), MED * .8))
            for s in (-1, 1):
                out.append(seta(cx + s * 120, y - 10, 90 + s * 60, 22))
    out.append(line([(cx, 620), (cx, 1440)], FINE))
    out.append("</g>")
    save("pseudoscorpion", "".join(out).replace(f'fill="{LIGHT}" fill-rule', f'fill="{WHITE}" fill-rule'), Wd, Ht)


# ------------------------------------------------------------------ bdelloid rotifer (feeding, lateral view)
def rotifer():
    Wd, Ht = 1700, 900
    cl = np.array(smooth([(330, 420), (470, 440), (700, 470), (950, 470), (1180, 470), (1360, 490), (1520, 540)], 300))
    u = np.linspace(0, 1, len(cl))
    half = np.interp(u, [0, .06, .22, .45, .58, .72, .86, 1], [95, 120, 165, 175, 140, 90, 52, 30])
    t = np.gradient(cl, axis=0); t /= np.linalg.norm(t, axis=1)[:, None]; n = np.c_[-t[:, 1], t[:, 0]]
    body = Polygon(np.vstack([cl + n * half[:, None], (cl - n * half[:, None])[::-1]])).buffer(0)
    out = []
    # corona: two trochal discs on short pedicels, each with a ring of beating cilia (drawn as a blurred wreath)
    for dy in (-85, 85):
        c = np.array([215, 400 + dy])
        ped = tube([(330, 420 + dy * .5), tuple(c + [30, 0])], 70, 56)
        out.append(shape(ped, fill=WHITE, w=MED))
        out.append(shade(ped, 60, 2.2))
        cil = []
        for k in range(110):
            a = k / 110 * 2 * math.pi
            p0 = c + 62 * np.array([math.cos(a), math.sin(a)])
            p1 = c + 92 * np.array([math.cos(a + .18), math.sin(a + .18)])
            cil.append(f"M{p0[0]:.1f},{p0[1]:.1f}Q{c[0] + 92 * math.cos(a - .05):.1f},{c[1] + 92 * math.sin(a - .05):.1f} {p1[0]:.1f},{p1[1]:.1f}")
        out.append(f'<path d="{"".join(cil)}" fill="none" stroke="{DEEP}" stroke-width="{FINE}" stroke-linecap="round"/>')
        disc = Point(*c).buffer(62)
        out.append(shape(disc, fill=WHITE, w=MED))
        out.append(shade(disc, 90, 2.2, power=1.5))
    out.append(shape(body, fill=WHITE, w=HEAVY))
    out.append(shade(body, 3000, 2.3, light=(-.3, -.95)))
    # pseudosegments: telescoping cuticle folds
    for k in np.arange(.1, .97, .05):
        i = int(k * (len(cl) - 1))
        a, b = cl[i] + n[i] * half[i] * .97, cl[i] - n[i] * half[i] * .97
        out.append(line([tuple(a), tuple(cl[i] + t[i] * 14), tuple(b)], FINE, FWG))
    # rostrum with its sensory cilia at the front top
    out.append(shape(tube([(360, 360), (300, 300), (290, 260)], 46, 26), fill=WHITE, w=MED))
    for k in range(6):
        out.append(seta(282 + k * 4, 252, -110 + k * 8, 24, FINE))
    # mastax: muscular bulb with ramate trophi, two rami each with ridged unci
    mx, my = 470, 440
    out.append(shape(Point(mx, my).buffer(78).intersection(Point(mx, my).buffer(78)), fill=WHITE, w=MED * 1.2))
    for s in (-1, 1):
        ram = [(mx + s * (8 + 46 * math.sin(q)), my - 54 * math.cos(q)) for q in np.linspace(0, math.pi, 30)]
        out.append(line(ram, MED * 1.3))
        for k in range(7):
            y = my - 40 + k * 13
            out.append(line([(mx + s * 8, y), (mx + s * 36, y - 3)], FINE))
    # stomach syncytium with food, eggs (vitellarium)
    gut = Polygon(np.vstack([cl[70:190] + n[70:190] * half[70:190, None] * .48, (cl[70:190] - n[70:190] * half[70:190, None] * .48)[::-1]])).buffer(30).buffer(-30)
    out.append(shape(gut, fill=WHITE, stroke=FWG, w=MED))
    out.append(shade(gut, 500, 3, c=FWG, power=1))
    out.append(shape(Point(760, 360).buffer(40), fill=WHITE, stroke=DEEP, w=MED))
    out.append(shape(Point(760, 360).buffer(14), fill=FWG, stroke=FWG, w=1))
    # foot: telescoping segments, a pair of spurs, toes
    tip = cl[-1]
    out.append(shape(tube([tuple(cl[-24] - n[-24] * 10), (tip[0] - 20, tip[1] + 70)], 18, 8), fill=LIGHT, w=MED))
    for dy in (-12, 12):
        out.append(shape(tube([tuple(tip), (tip[0] + 54, tip[1] + dy * 2.4)], 16, 6), fill=LIGHT, w=MED))
    save("rotifer-bdelloid", "".join(out), Wd, Ht)




# ------------------------------------------------------------------ predatory mite (Mesostigmata) holding a nematode
def predatory_mite():
    Wd, Ht = 1500, 1600; cx, cy = 750, 960
    out = []
    idio = Polygon(smooth([(cx, cy - 330), (cx + 165, cy - 270), (cx + 200, cy - 40), (cx + 175, cy + 230), (cx, cy + 330),
                           (cx - 175, cy + 230), (cx - 200, cy - 40), (cx - 165, cy - 270)], 220, closed=True))
    # legs: four pairs of six segments, attached under the front half, leg I held forward like antennae
    for s_ in (-1, 1):
        for k, (ang, L) in enumerate(((-112, 470), (-158, 420), (162, 420), (122, 480))):
            a = math.radians(ang if s_ < 0 else 180 - ang)
            p = [np.array([cx + s_ * 120, cy - 230 + k * 95])]
            for j in range(6):
                a2 = a + s_ * math.radians(j * (5 if k < 2 else -5))
                p.append(p[-1] + L / 6 * np.array([math.cos(a2), math.sin(a2)]))
            for j in range(6):
                seg = tube([p[j], p[j + 1]], 42 - j * 4.5, 36 - j * 4.5).union(Point(*p[j + 1]).buffer(18 - j * 2))
                out.append(shape(seg, fill=WHITE, w=MED)); out.append(shade(seg, 40, 1.8, light=(0, -1)))
                mid = (p[j] + p[j + 1]) / 2; dv = (p[j + 1] - p[j]) / np.linalg.norm(p[j + 1] - p[j]); nv = np.array([-dv[1], dv[0]])
                for q in (-1, 1):
                    e = mid + nv * q * (20 - j * 2.4)
                    out.append(line([tuple(e), tuple(e + nv * q * 28 + dv * 16)], 1.6))
            tip = p[-1]; dv = (p[-1] - p[-2]) / np.linalg.norm(p[-1] - p[-2])
            for q in (-.55, .55):
                c = math.atan2(dv[1], dv[0]) + q
                out.append(line([tuple(tip), (tip[0] + 26 * math.cos(c), tip[1] + 26 * math.sin(c))], MED))
            out.append(f'<circle cx="{tip[0]:.1f}" cy="{tip[1]:.1f}" r="7" fill="{DEEP}"/>')
    out.append(shape(idio, fill=WHITE, w=HEAVY))
    shield = idio.buffer(-24)
    out.append(shape(shield, fill="none", stroke=FWG, w=MED))
    out.append(shade(shield, 2600, 2.1, light=(-.5, -.85)))
    for k in range(10):                                                  # paired dorsal setae with pores
        y = cy - 270 + k * 60
        w = 150 * math.sqrt(max(0, 1 - ((y - cy) / 340) ** 2))
        for s_ in (-1, 1):
            for f in (.35, .75):
                x = cx + s_ * w * f
                out.append(line([(x, y), (x + s_ * 6, y - 26)], 1.8))
                out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{DEEP}"/>')
    # prey nematode
    cl = np.array(smooth([(80, 230), (400, 320), (750, 285), (1050, 320), (1420, 230)], 320))
    u = np.linspace(0, 1, len(cl)); t = np.gradient(cl, axis=0); t /= np.linalg.norm(t, axis=1)[:, None]; n = np.c_[-t[:, 1], t[:, 0]]
    half = 30 * np.minimum(1, .5 + .5 * np.clip(u / .08, 0, 1)) * np.minimum(1, np.clip((1 - u) / .12, .05, 1))
    worm = Polygon(np.vstack([cl + n * half[:, None], (cl - n * half[:, None])[::-1]])).buffer(0)
    out.append(shape(worm, fill=WHITE, w=MED)); out.append(shade(worm, 500, 1.8, light=(0, -1)))
    out.append(line([tuple(p) for p in cl[4:70]], FINE))
    out.append(shape(Point(*cl[70]).buffer(12), fill=WHITE, w=FINE))
    # gnathosoma on top: base, palps, chelicerae ending in pincers that grip the worm
    gn = Polygon(list(map(tuple, smooth([(cx - 70, cy - 300), (cx - 58, cy - 430), (cx + 58, cy - 430), (cx + 70, cy - 300)], 40))) + [(cx, cy - 290)]).buffer(0)
    out.append(shape(gn, fill=WHITE, w=MED)); out.append(shade(gn, 120, 1.8))
    for s_ in (-1, 1):
        pal = tube(smooth([(cx + s_ * 52, cy - 400), (cx + s_ * 92, cy - 480), (cx + s_ * 100, cy - 560)], 30), 30, 18)
        out.append(shape(pal, fill=WHITE, w=MED))
        for q in range(3):
            y = cy - 440 - q * 40
            out.append(line([(cx + s_ * (88 + q * 5), y), (cx + s_ * (120 + q * 5), y - 14)], 1.6))
        ch = tube(smooth([(cx + s_ * 20, cy - 410), (cx + s_ * 22, cy - 540), (cx + s_ * 14, cy - 630)], 30), 30, 18)
        out.append(shape(ch, fill=WHITE, w=MED))
        tip = np.array([cx + s_ * 14, cy - 630])
        out.append(line([tuple(tip), (tip[0] - s_ * 6, tip[1] - 30), (tip[0] + s_ * 10, tip[1] - 46)], MED * 1.3))
    save("predatory-mite", "".join(out), Wd, Ht)


# ------------------------------------------------------------------ Paramecium
def paramecium():
    Wd, Ht = 1600, 800
    o = np.array(smooth([(150, 400), (300, 260), (700, 225), (1150, 255), (1390, 360), (1330, 490), (920, 530), (620, 520), (440, 470), (300, 500)], 300, closed=True))
    body = Polygon(o).buffer(0)
    ring = LineString(np.vstack([o, o[:1]])); cil = []
    N = 520
    for i in range(N):
        p = np.array(ring.interpolate(i / N * ring.length).coords[0]); q = np.array(ring.interpolate(i / N * ring.length + 1).coords[0])
        tt = (q - p) / np.linalg.norm(q - p); nn = np.array([tt[1], -tt[0]])
        if body.contains(Point(*(p + nn * 3))): nn = -nn
        e = p + nn * 26 + tt * 10
        cil.append(f"M{p[0]:.1f},{p[1]:.1f}L{e[0]:.1f},{e[1]:.1f}")
    out = [f'<path d="{"".join(cil)}" stroke="{DEEP}" stroke-width="1.6" fill="none" stroke-linecap="round"/>']
    out.append(shape(body, fill=WHITE, w=HEAVY * .8))
    out.append(shape(body.buffer(-14), fill="none", stroke=FWG, w=FINE))           # pellicle with trichocysts
    tri = []
    for i in range(0, N, 3):
        p = np.array(ring.interpolate(i / N * ring.length).coords[0])
        c = np.array(body.centroid.coords[0]); v = (c - p) / np.linalg.norm(c - p)
        tri.append(f"M{(p + v * 16)[0]:.1f},{(p + v * 16)[1]:.1f}L{(p + v * 30)[0]:.1f},{(p + v * 30)[1]:.1f}")
    out.append(f'<path d="{"".join(tri)}" stroke="{FWG}" stroke-width="1.4" fill="none"/>')
    out.append(shade(body.buffer(-34), 2400, 2.2, light=(-.3, -.95)))
    groove = Polygon(smooth([(300, 480), (480, 430), (680, 380), (780, 350), (760, 395), (560, 450), (380, 500)], 80, closed=True))
    out.append(shape(groove, fill=WHITE, stroke=DEEP, w=MED)); out.append(shade(groove, 260, 2, power=1))
    out.append(shape(Point(790, 360).buffer(26), fill=WHITE, w=MED))                 # cytostome and gullet
    mac = Polygon(smooth([(700, 340), (820, 300), (920, 330), (900, 400), (780, 410)], 80, closed=True))
    out.append(shape(mac, fill=WHITE, w=MED)); out.append(shade(mac, 300, 2, power=1))
    out.append(f'<circle cx="690" cy="300" r="16" fill="{DEEP}"/>')
    for x in (430, 1200):
        for k in range(9):
            a = k / 9 * 2 * math.pi
            canal = Polygon(smooth([(x + 26 * math.cos(a - .12), 370 + 26 * math.sin(a - .12)), (x + 90 * math.cos(a), 370 + 70 * math.sin(a)), (x + 26 * math.cos(a + .12), 370 + 26 * math.sin(a + .12))], 20, closed=True))
            out.append(shape(canal, fill=WHITE, stroke=FWG, w=FINE))
        out.append(shape(Point(x, 370).buffer(30), fill=WHITE, stroke=DEEP, w=MED))
    for x, y, r in ((1000, 300, 26), (1080, 430, 22), (600, 330, 20), (1150, 300, 18)):
        out.append(shape(Point(x, y).buffer(r), fill=WHITE, stroke=FWG, w=FINE))
        out.append(shade(Point(x, y).buffer(r - 3), 30, 2, power=.5))
    save("ciliate-paramecium", "".join(out), Wd, Ht)


# ------------------------------------------------------------------ earthworm
def earthworm():
    Wd, Ht = 1800, 700
    cl = np.array(smooth([(90, 350), (450, 270), (900, 380), (1350, 340), (1720, 280)], 500))
    u = np.linspace(0, 1, len(cl)); t = np.gradient(cl, axis=0); t /= np.linalg.norm(t, axis=1)[:, None]; n = np.c_[-t[:, 1], t[:, 0]]
    half = 70 * np.minimum(1, .45 + .55 * np.clip(u / .07, 0, 1) ** .7) * np.minimum(1, .45 + .55 * np.clip((1 - u) / .06, 0, 1))
    half = half * np.where((u > .2) & (u < .3), 1.16, 1)
    body = Polygon(np.vstack([cl + n * half[:, None], (cl - n * half[:, None])[::-1]])).buffer(30).buffer(-30)
    out = [shape(body, fill=WHITE, w=HEAVY)]
    out.append(shade(body, 5200, 2.2, light=(0, -1), power=2.4))
    seg = []
    for k in np.arange(.02, .985, .0085):
        i = int(k * (len(cl) - 1))
        if .2 < k < .3: continue
        p, q = cl[i] + n[i] * half[i] * .97, cl[i] - n[i] * half[i] * .97
        c1 = cl[i] + t[i] * 10
        seg.append(f"M{p[0]:.1f},{p[1]:.1f}Q{c1[0]:.1f},{c1[1]:.1f} {q[0]:.1f},{q[1]:.1f}")
        for f in (.55, .78):
            s0 = cl[i] - n[i] * half[i] * f
            seg.append(f"M{s0[0]:.1f},{s0[1]:.1f}l{-n[i][0] * 11 + t[i][0] * 4:.1f},{-n[i][1] * 11 + t[i][1] * 4:.1f}")
    out.append(f'<path d="{"".join(seg)}" fill="none" stroke="{DEEP}" stroke-width="1.8" stroke-linecap="round"/>')
    i0, i1 = int(.2 * len(cl)), int(.3 * len(cl))
    clit = Polygon(np.vstack([cl[i0:i1] + n[i0:i1] * half[i0:i1, None], (cl[i0:i1] - n[i0:i1] * half[i0:i1, None])[::-1]]))
    out.append(shape(clit, fill=LIGHT, w=MED * 1.2)); out.append(shade(clit, 700, 2.4, c=DEEP, light=(0, -1), power=1.6))
    out.append(line([tuple(cl[i] - n[i] * half[i] * .9) for i in range(i0 + 3, i1 - 3)], 1.6, DEEP))
    h, tt, nn = cl[0], t[0], n[0]
    pro = Point(*(h - tt * 26 + nn * 8)).buffer(30)
    pro = Polygon([(x, y) for x, y in pro.exterior.coords]).difference(body.buffer(-3))
    out.append(shape(pro, fill=WHITE, w=MED))
    out.append(line([tuple(cl[i] + n[i] * half[i] * .2) for i in range(3, len(cl) - 3)], 1.2, FWG))   # dorsal blood vessel
    save("earthworm", "".join(out), Wd, Ht)


# ------------------------------------------------------------------ potworm (enchytraeid), transparent body
def enchytraeid():
    Wd, Ht = 1700, 650
    cl = np.array(smooth([(90, 330), (450, 250), (850, 370), (1250, 290), (1620, 330)], 500))
    u = np.linspace(0, 1, len(cl)); t = np.gradient(cl, axis=0); t /= np.linalg.norm(t, axis=1)[:, None]; n = np.c_[-t[:, 1], t[:, 0]]
    half = 64 * np.minimum(1, .5 + .5 * np.clip(u / .06, 0, 1)) * np.minimum(1, .5 + .5 * np.clip((1 - u) / .05, 0, 1)) * np.where((u > .18) & (u < .25), 1.14, 1)
    body = Polygon(np.vstack([cl + n * half[:, None], (cl - n * half[:, None])[::-1]])).buffer(24).buffer(-24)
    out = [shape(body, fill=WHITE, w=HEAVY * .8)]
    gut = Polygon(np.vstack([cl[60:-30] + n[60:-30] * half[60:-30, None] * .42, (cl[60:-30] - n[60:-30] * half[60:-30, None] * .42)[::-1]])).buffer(10).buffer(-10)
    out.append(shape(gut, fill=WHITE, stroke=FWG, w=MED)); out.append(shade(gut, 1600, 2.4, power=1))
    out.append(shade(body.difference(gut.buffer(6)), 900, 1.8, light=(0, -1), power=3))
    segs = []
    for k in np.arange(.025, .98, .022):
        i = int(k * (len(cl) - 1))
        p, q = cl[i] + n[i] * half[i] * .96, cl[i] - n[i] * half[i] * .96
        segs.append(f"M{p[0]:.1f},{p[1]:.1f}L{q[0]:.1f},{q[1]:.1f}")
        for side in (1, -1):                                           # four setal bundles per segment, straight setae
            s0 = cl[i] + n[i] * half[i] * side * .72
            for j in (-1, 0, 1):
                dd = n[i] * side * 30 + t[i] * j * 9
                segs.append(f"M{s0[0]:.1f},{s0[1]:.1f}l{dd[0]:.1f},{dd[1]:.1f}")
    out.append(f'<path d="{"".join(segs)}" stroke="{DEEP}" stroke-width="1.6" fill="none" stroke-linecap="round"/>')
    i0, i1 = int(.18 * len(cl)), int(.25 * len(cl))
    clit = Polygon(np.vstack([cl[i0:i1] + n[i0:i1] * half[i0:i1, None], (cl[i0:i1] - n[i0:i1] * half[i0:i1, None])[::-1]]))
    out.append(shape(clit, fill=LIGHT, w=MED)); out.append(shade(clit, 260, 2.2, c=DEEP, power=1.5))
    out.append(shape(Point(*cl[30]).buffer(30), fill=WHITE, stroke=FWG, w=FINE))   # pharyngeal pad
    save("potworm-enchytraeid", "".join(out), Wd, Ht)


# ------------------------------------------------------------------ Chlamydomonas
def chlamydomonas():
    Wd, Ht = 900, 1250; cx, cy = 450, 760
    out = []
    for s_ in (-1, 1):                                                       # two equal flagella, breast-stroke pose
        fl = smooth([(cx + s_ * 24, cy - 300), (cx + s_ * 120, cy - 430), (cx + s_ * 260, cy - 500), (cx + s_ * 330, cy - 640)], 80)
        out.append(line(fl, MED * 1.1))
    cell = Polygon(smooth([(cx, cy - 310), (cx + 180, cy - 230), (cx + 240, cy), (cx + 190, cy + 250), (cx, cy + 320), (cx - 190, cy + 250), (cx - 240, cy), (cx - 180, cy - 230)], 200, closed=True))
    papilla = Point(cx, cy - 305).buffer(26)
    out.append(shape(cell.union(papilla), fill=WHITE, w=HEAVY))
    out.append(shape(cell.buffer(-12), fill="none", stroke=FWG, w=FINE))     # cell wall, double line
    cup = cell.buffer(-26).difference(Polygon(smooth([(cx, cy - 330), (cx + 140, cy - 160), (cx + 130, cy + 40), (cx, cy + 120), (cx - 130, cy + 40), (cx - 140, cy - 160)], 120, closed=True)))
    out.append(shape(cup, fill=WHITE, stroke=FWG, w=MED))
    out.append(shade(cup, 2400, 2.2, c=FWG, light=(-.4, -.9), power=1.4))     # chloroplast, densely stippled
    pyr = Point(cx, cy + 190).buffer(60)
    out.append(shape(pyr, fill=WHITE, w=MED)); out.append(shape(pyr.buffer(-14).difference(pyr.buffer(-26)), fill=FWG, stroke=FWG, w=1))   # starch sheath
    out.append(shade(pyr.buffer(-28), 40, 2, c=DEEP, power=.5))
    nuc = Point(cx, cy - 40).buffer(70)
    out.append(shape(nuc, fill=WHITE, w=MED)); out.append(shade(nuc, 160, 2, c=DEEP, power=1)); out.append(shape(Point(cx, cy - 40).buffer(22), fill=DEEP, stroke=DEEP, w=1))
    out.append(f'<ellipse cx="{cx + 185:.1f}" cy="{cy - 100:.1f}" rx="16" ry="34" transform="rotate(18 {cx + 185} {cy - 100})" fill="#B8433A" stroke="{DEEP}" stroke-width="2"/>')
    for s_ in (-1, 1):
        out.append(shape(Point(cx + s_ * 46, cy - 250).buffer(20), fill=WHITE, stroke=DEEP, w=FINE))
    save("alga-chlamydomonas", "".join(out), Wd, Ht)


# ------------------------------------------------------------------ yeast, budding
def yeast():
    Wd, Ht = 1300, 1000
    out = []
    cells = [((430, 560), 190, 150, 15, [(270, 520), (330, 690)]), ((662, 432), 112, 90, -30, []), ((790, 362), 62, 50, -30, []),
             ((345, 810), 104, 84, 70, []), ((960, 690), 170, 132, -5, [(1110, 640), (900, 570)])]
    for (x, y), rx, ry, a, scars in cells:
        e = Point(x, y).buffer(1)
        from shapely import affinity
        e = affinity.rotate(affinity.scale(Point(x, y).buffer(1, 64), rx, ry), a)
        out.append(shape(e, fill=WHITE, w=HEAVY * .8))
        out.append(shape(e.buffer(-10), fill="none", stroke=FWG, w=FINE))
        out.append(shade(e.buffer(-12), int(rx * ry / 22), 2.1, light=(-.5, -.85)))
        v = affinity.rotate(affinity.scale(Point(x + rx * .12, y - ry * .05).buffer(1, 48), rx * .38, ry * .4), a)
        out.append(shape(v, fill=WHITE, stroke=DEEP, w=MED))
        for _ in range(3):
            g = Point(x + rng.uniform(-.3, .3) * rx, y + rng.uniform(-.25, .25) * ry).buffer(rng.uniform(7, 12))
            if not g.intersects(v):
                out.append(shape(g, fill=FWG, stroke=FWG, w=1))
        for sx, sy in scars:
            out.append(shape(Point(sx, sy).buffer(16).difference(Point(sx, sy).buffer(8)), fill=DEEP, stroke=DEEP, w=1))
    save("yeast-budding", "".join(out), Wd, Ht)


# ------------------------------------------------------------------ hypotrich ciliate (Oxytricha type), ventral view
def hypotrich():
    Wd, Ht = 1000, 1500; cx = 500
    o = Polygon(smooth([(cx, 120), (cx + 210, 200), (cx + 270, 520), (cx + 250, 980), (cx + 170, 1290), (cx, 1350), (cx - 170, 1290), (cx - 250, 980), (cx - 270, 520), (cx - 210, 200)], 300, closed=True))
    out = [shape(o, fill=WHITE, w=HEAVY)]
    out.append(shade(o.buffer(-20), 3200, 2.1, light=(-.4, -.9)))
    azm = smooth([(cx + 190, 230), (cx + 40, 150), (cx - 160, 200), (cx - 220, 400), (cx - 160, 560), (cx - 40, 600)], 160)
    for i in range(0, len(azm) - 1, 2):                                      # adoral zone of membranelles: question-mark row of plates
        p = np.array(azm[i]); q = np.array(azm[i + 1]); tt = (q - p) / (np.linalg.norm(q - p) + 1e-9); nn = np.array([tt[1], -tt[0]])
        out.append(shape(tube([tuple(p - nn * 14), tuple(p + nn * 34)], 7, 4), fill=DEEP, stroke=DEEP, w=1))
    buccal = Polygon(smooth([(cx - 40, 600), (cx + 10, 470), (cx + 60, 320), (cx + 110, 260), (cx + 90, 380), (cx + 30, 560)], 80, closed=True))
    out.append(shape(buccal, fill=WHITE, stroke=DEEP, w=MED)); out.append(shade(buccal, 220, 2, power=.8))
    def cirrus(x, y, L, a):
        a = math.radians(a); tip = (x + L * math.cos(a), y + L * math.sin(a))
        return shape(tube([(x, y), tip], 15, 4), fill=DEEP, stroke=DEEP, w=1)
    for x, y in [(cx - 60, 250), (cx + 10, 235), (cx + 90, 262), (cx + 30, 320), (cx + 130, 330), (cx + 80, 390), (cx + 165, 440), (cx + 120, 495)]:
        out.append(cirrus(x, y, 62, -100))                                   # 8 frontal cirri
    for x, y in [(cx + 60, 680), (cx + 120, 740), (cx + 40, 800), (cx + 140, 850)]:
        out.append(cirrus(x, y, 54, -95))                                    # 4 ventral cirri
    for k in range(6):
        out.append(cirrus(cx - 130 + k * 52, 1170 + abs(k - 2.5) * 12, 120, 86))   # 6 transverse cirri
    for s_ in (-1, 1):                                                       # left and right marginal rows
        for k in range(28):
            y = 330 + k * 34
            x = cx + s_ * (math.sqrt(max(0, 1 - ((y - 740) / 660) ** 2)) * 258 - 26)
            out.append(cirrus(x, y, 42, 90 - s_ * 55))
    for y in (580, 870):
        mac = Polygon(smooth([(cx - 10, y - 100), (cx + 70, y - 60), (cx + 80, y + 50), (cx + 20, y + 100), (cx - 50, y + 50), (cx - 60, y - 50)], 80, closed=True))
        out.append(shape(mac, fill=WHITE, w=MED)); out.append(shade(mac, 220, 2, c=DEEP, power=1))
    out.append(shape(Point(cx - 190, 680).buffer(38), fill=WHITE, stroke=DEEP, w=MED))
    for x, y, r in ((cx - 70, 790, 26), (cx - 140, 960, 22), (cx + 160, 1010, 24), (cx - 30, 1060, 20)):
        out.append(shape(Point(x, y).buffer(r), fill=WHITE, stroke=FWG, w=FINE)); out.append(shade(Point(x, y).buffer(r - 3), 25, 2, power=.4))
    save("ciliate-hypotrich-oxytricha", "".join(out), Wd, Ht)


# ------------------------------------------------------------------ cercomonad flagellate
def cercomonad():
    Wd, Ht = 1500, 800
    out = []
    out.append(line(smooth([(470, 360), (380, 300), (280, 320), (180, 260), (70, 290)], 120), MED * 1.1))          # anterior flagellum
    out.append(line(smooth([(480, 400), (600, 500), (820, 530), (1080, 500), (1400, 560)], 160), MED * 1.1))       # trailing flagellum under the cell
    for a, L in ((-25, 230), (0, 260), (24, 220), (45, 170)):                 # filose pseudopods, branched
        r = math.radians(a); p0 = np.array([880, 380]); p1 = p0 + L * np.array([math.cos(r), math.sin(r)])
        out.append(line([tuple(p0), tuple(p1)], FINE, DEEP))
        m = p0 + (p1 - p0) * .55
        out.append(line([tuple(m), tuple(m + 70 * np.array([math.cos(r + .55), math.sin(r + .55)]))], 1.6))
    cell = Polygon(smooth([(450, 380), (530, 260), (680, 225), (820, 270), (900, 370), (850, 470), (700, 510), (540, 490)], 220, closed=True))
    out.append(shape(cell, fill=WHITE, w=HEAVY))
    out.append(shade(cell.buffer(-10), 1500, 2.1, light=(-.4, -.9)))
    nuc = Point(560, 360).buffer(50); out.append(shape(nuc, fill=WHITE, w=MED)); out.append(shape(Point(560, 360).buffer(20), fill=DEEP, stroke=DEEP, w=1))
    out.append(shape(Point(520, 330).buffer(10), fill=DEEP, stroke=DEEP, w=1))                                          # basal bodies
    for x, y, r in ((700, 330, 32), (760, 430, 24), (650, 440, 20)):
        out.append(shape(Point(x, y).buffer(r), fill=WHITE, stroke=FWG, w=FINE)); out.append(shade(Point(x, y).buffer(r - 3), 30, 2, power=.4))
    out.append(shape(Point(680, 270).buffer(20), fill=WHITE, stroke=DEEP, w=FINE))
    save("flagellate-cercomonad", "".join(out), Wd, Ht)


# ------------------------------------------------------------------ Fusarium spores
def fusarium():
    Wd, Ht = 1500, 900
    out = []
    def macro(x, y, L, rot, septa=5):
        a = math.radians(rot); R = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])
        v = np.linspace(-1, 1, 160)
        mid = np.c_[L / 2 * v, -80 * (1 - v ** 2)]
        th = 34 * (1 - np.abs(v) ** 2.4) + 3
        tt = np.gradient(mid, axis=0); tt /= np.linalg.norm(tt, axis=1)[:, None]; nn = np.c_[-tt[:, 1], tt[:, 0]]
        top, bot = mid + nn * th[:, None], mid - nn * th[:, None]
        apex = mid[-1] + np.array([10, 10]); foot = mid[0] + np.array([-14, -2])
        pts = np.vstack([top, [apex], bot[::-1], [foot + np.array([4, 10]), foot, foot + np.array([6, -10])]]) @ R.T + [x, y]
        g = Polygon(pts).buffer(0)
        o = shape(g, fill=WHITE, w=MED * 1.3) + shade(g, int(L * 1.6), 2, light=(-.3, -.95))
        for k in range(1, septa + 1):
            i = int(k / (septa + 1) * 159)
            q = np.vstack([top[i], bot[i]]) @ R.T + [x, y]
            o += line([tuple(q[0]), tuple(q[1])], MED, DEEP)
        return o
    out.append(macro(430, 320, 600, -8)); out.append(macro(980, 260, 520, 12, 4)); out.append(macro(720, 640, 640, -2))
    ph = tube(smooth([(1180, 860), (1250, 740), (1300, 640)], 40), 30, 16)
    out.append(shape(ph, fill=WHITE, w=MED)); out.append(shade(ph, 60, 2))
    for x, y, a in ((1320, 590, 30), (1370, 640, -10), (1330, 530, 70), (1410, 570, 20), (1290, 470, 50)):
        from shapely import affinity
        e = affinity.rotate(affinity.scale(Point(x, y).buffer(1, 32), 26, 16), a)
        out.append(shape(e, fill=WHITE, w=MED)); out.append(shade(e, 20, 1.8, power=.6))
    save("fusarium-spores", "".join(out), Wd, Ht)


# ------------------------------------------------------------------ Alternaria conidia in a chain
def alternaria():
    Wd, Ht = 800, 1400; cx = 400
    out = []
    ph = tube([(cx, 1380), (cx, 1180)], 36, 30)
    out.append(shape(ph, fill="#7a5a58", w=MED)); out.append(line([(cx - 16, 1260), (cx + 16, 1260)], MED, WHITE))
    y = 1180
    for k, L in enumerate((290, 250, 210)):
        top, bot = y - L, y
        body = Polygon(smooth([(cx, bot), (cx + 80, bot - L * .2), (cx + 74, bot - L * .55), (cx + 30, bot - L * .8), (cx + 12, top + 10), (cx - 12, top + 10), (cx - 30, bot - L * .8), (cx - 74, bot - L * .55), (cx - 80, bot - L * .2)], 140, closed=True))
        out.append(shape(body, fill="#7a5a58", stroke=DEEP, w=MED * 1.4))
        out.append(shade(body, int(L * 2.2), 2.2, c=DEEP, light=(-.6, -.8), power=1.4))
        rows = [bot - L * .8 * j / 6 for j in range(1, 6)]
        for yy in rows:
            seg = LineString([(cx - 120, yy), (cx + 120, yy)]).intersection(body.buffer(-4))
            if seg.geom_type == "LineString":
                out.append(line(list(seg.coords), MED, WHITE))
        for j in range(5):
            if j in (1, 3):
                x0 = cx + (14 if j == 1 else -18)
                out.append(line([(x0, rows[j]), (x0 + 4, rows[j - 1] if j else bot - 6)], MED, WHITE))
            if j == 2:
                out.append(line([(cx - 30, rows[2]), (cx - 24, rows[1])], MED, WHITE)); out.append(line([(cx + 30, rows[2]), (cx + 26, rows[1])], MED, WHITE))
        out.append(shape(tube([(cx, top + 12), (cx, top - 10)], 18, 14), fill="#7a5a58", w=MED))   # beak
        y = top - 6
    save("alternaria-conidia-chain", "".join(out), Wd, Ht)


if __name__ == "__main__":
    tardigrade(); pseudoscorpion(); rotifer(); predatory_mite(); paramecium(); earthworm(); enchytraeid()
    chlamydomonas(); yeast(); hypotrich(); cercomonad(); fusarium(); alternaria()
