"""SFW field-guide graphics, set 3: twenty detailed soil organisms in the field-guide style.
Sources for every feature are in SOURCES.md (section "Graphics set 3").

Usage: python3 graphics_set3.py  ->  out/graphics/sfw-*.svg / .png
"""
import math
import numpy as np
from shapely.geometry import Point, Polygon, LineString
from shapely.ops import unary_union
from pages_4_8 import P, circle, ellipse, smooth, blob, stipple, cilia_fringe, DEEP, FWG, LIGHT, WHITE
from graphics_set2 import outline, save, LW

BROWN = "#4F3433"
rng = np.random.default_rng(33)


def hollow(pts, w, fill=WHITE, edge=DEEP, lw=LW):
    """A tube of width w along pts, with an outline."""
    return P(pts, close=False, w=w, stroke=edge) + P(pts, close=False, w=w - 2 * lw, stroke=fill)


def hook(x, y, s, ang):
    """A small curved claw."""
    a = math.radians(ang)
    t = np.array([math.cos(a), math.sin(a)]); n = np.array([-t[1], t[0]])
    pts = [np.array([x, y]) + t * s * u + n * s * .45 * u * u for u in np.linspace(0, 1, 12)]
    return P(pts, close=False, w=LW * 1.2)


def body_along(cl, half):
    cl = np.asarray(cl); t = np.gradient(cl, axis=0); t /= np.linalg.norm(t, axis=1)[:, None]
    n = np.c_[-t[:, 1], t[:, 0]]
    a = cl + n * np.asarray(half)[:, None]; b = cl - n * np.asarray(half)[:, None]
    return [tuple(p) for p in a] + [tuple(p) for p in b[::-1]], n, t


def nematode_body(cl, W, tail=.12, head_round=.04):
    cl = np.asarray(cl); u = np.linspace(0, 1, len(cl))
    half = W / 2 * np.minimum(1, .55 + .45 * np.clip(u / .1, 0, 1) ** .6) * np.where(u > 1 - tail, np.clip((1 - u) / tail, .03, 1), 1)
    pts, n, t = body_along(cl, half)
    return pts, n, t, half


# ------------------------------------------------------------------ 1 bdelloid rotifer
def rotifer():
    Wd, Ht = 1500, 760
    cl = smooth([(260, 330), (420, 360), (640, 400), (880, 410), (1100, 400), (1280, 420), (1420, 470)], 300)
    u = np.linspace(0, 1, len(cl))
    half = np.interp(u, [0, .05, .2, .45, .6, .75, .9, 1], [110, 120, 150, 160, 120, 70, 40, 22])
    pts, n, t = body_along(cl, half)
    b = [P(pts, fill=LIGHT, stroke=FWG, w=LW * 1.5)]
    for k in np.arange(.08, .97, .055):                                   # telescoping pseudosegments
        i = int(k * (len(cl) - 1))
        b.append(P([tuple(cl[i] + n[i] * half[i] * .98), tuple(cl[i] + t[i] * 10), tuple(cl[i] - n[i] * half[i] * .98)], close=False, w=2.2, stroke=FWG))
    gut = body_along(cl[int(.28 * len(cl)):int(.62 * len(cl))], half[int(.28 * len(cl)):int(.62 * len(cl))] * .5)[0]
    b.append(P(gut, fill=WHITE, stroke=FWG, w=2.4)); b.append(stipple(gut, 260, 3, FWG))
    # corona: two ciliated discs at the head
    for dy in (-70, 70):
        c = (200, 330 + dy)
        disc = [(c[0] + 62 * math.cos(q), c[1] + 62 * math.sin(q)) for q in np.linspace(0, 2 * math.pi, 120, endpoint=False)]
        b.append(cilia_fringe(np.array(disc), 26, w=2.2))
        b.append(P(disc, fill=WHITE, stroke=DEEP, w=LW * 1.3))
        b.append(circle(*c, 30, fill=LIGHT, stroke=FWG, w=2.4))
    # mastax with trophi (jaws): two rami, each with tooth ridges
    mx, my = 400, 360
    b.append(ellipse(mx, my, 70, 56, fill=WHITE, w=LW * 1.3))
    for s in (-1, 1):
        ram = [(mx + s * 6 + s * 40 * math.sin(q), my - 40 * math.cos(q)) for q in np.linspace(0, math.pi, 30)]
        b.append(P(ram, fill="none", w=LW * 1.3))
        for k in range(5):
            y = my - 30 + k * 15
            b.append(P([(mx + s * 6, y), (mx + s * 30, y)], close=False, w=2.2))
    b.append(circle(560, 300, 22, fill=WHITE, stroke=FWG))                 # vitellarium / egg
    # foot: spurs and two toes
    tip = cl[-1]
    b.append(P([tuple(cl[-30] - n[-30] * half[-30] * .6), (tip[0] - 10, tip[1] + 50)], close=False, w=LW * 1.6))
    for dy in (-10, 10):
        b.append(P([tuple(tip), (tip[0] + 40, tip[1] + dy * 2.5)], close=False, w=LW * 1.6))
    save("rotifer-bdelloid", "".join(b), Wd, Ht)


# ------------------------------------------------------------------ 2 tardigrade
def tardigrade():
    Wd, Ht = 1500, 900
    body = smooth([(230, 470), (300, 330), (520, 250), (820, 230), (1100, 260), (1280, 360), (1320, 500),
                   (1180, 600), (900, 620), (560, 620), (330, 590)], 260, closed=True)
    b = []
    legs = [(430, 590), (680, 615), (930, 615), (1250, 540)]
    for k, (x, y) in enumerate(legs):                                        # four pairs; near side drawn
        a = 98 if k < 3 else 40
        r = math.radians(a)
        e = (x + 120 * math.cos(r), y + 120 * math.sin(r))
        leg = LineString([(x, y - 40), e]).buffer(48, 24)
        b.append(outline(leg, fill=LIGHT, stroke=FWG))
        for s in (-1, 1):                                                     # double claws
            b.append(hook(e[0] + s * 18, e[1] + 30, 34, a + s * 30))
            b.append(hook(e[0] + s * 18, e[1] + 30, 22, a + s * 55))
    b.append(P(body, fill=LIGHT, stroke=FWG, w=LW * 1.6))
    for x in (520, 760, 1000):                                                # faint segment folds
        b.append(P(smooth([(x, 255), (x - 20, 420), (x, 610)], 30), close=False, w=2, stroke=FWG))
    # buccal apparatus: mouth, buccal tube, stylets, pharyngeal bulb with placoids
    b.append(ellipse(240, 470, 22, 30, fill=WHITE, w=LW))
    b.append(hollow([(255, 470), (410, 450)], 20))
    for s in (-1, 1):
        b.append(P([(270, 470 + s * 26), (430, 448 + s * 40)], close=False, w=LW * 1.2))
    b.append(ellipse(470, 446, 62, 52, fill=WHITE, w=LW * 1.4))
    for k in (-1, 0, 1):
        b.append(P([(445, 446 + k * 18), (495, 446 + k * 18)], close=False, w=6, stroke=DEEP))
    b.append(circle(330, 380, 10, fill=DEEP, stroke=DEEP))                    # eyespot
    gut = smooth([(540, 380), (800, 340), (1080, 380), (1180, 460), (1000, 520), (700, 520), (540, 470)], 160, closed=True)
    b.append(P(gut, fill=WHITE, stroke=FWG, w=2.4)); b.append(stipple(gut, 380, 3.2, FWG))
    b += [circle(x, y, r, fill=FWG, stroke=FWG) for x, y, r in ((720, 300, 14), (950, 300, 12), (1150, 330, 13))]
    save("tardigrade", "".join(b), Wd, Ht)


# ------------------------------------------------------------------ 3 hypotrich ciliate (Oxytricha type), ventral view
def hypotrich():
    Wd, Ht = 900, 1400; cx = 450
    o = smooth([(cx, 120), (cx + 200, 190), (cx + 260, 500), (cx + 240, 950), (cx + 160, 1250), (cx, 1300),
                (cx - 160, 1250), (cx - 240, 950), (cx - 260, 500), (cx - 200, 190)], 300, closed=True)
    b = [P(o, fill=LIGHT, stroke=FWG, w=LW * 1.5)]
    poly = Polygon(o)
    b.append(stipple(o, 500, 2.4, FWG, avoid=Point(cx, 700).buffer(10)))
    # adoral zone of membranelles: question-mark row along the front and left side
    azm = smooth([(cx + 170, 220), (cx + 30, 150), (cx - 150, 190), (cx - 210, 380), (cx - 150, 520), (cx - 40, 560)], 120)
    for i in range(0, len(azm) - 1, 3):
        p = np.array(azm[i]); q = np.array(azm[min(i + 1, len(azm) - 1)]); tt = (q - p) / (np.linalg.norm(q - p) + 1e-9)
        nn = np.array([tt[1], -tt[0]])
        b.append(P([tuple(p - nn * 18), tuple(p + nn * 26)], close=False, w=LW * 1.3))
    b.append(P(smooth([(cx - 40, 560), (cx + 30, 420), (cx + 60, 300)], 40), close=False, w=LW))     # undulating membrane
    cirrus = lambda x, y, L=46, a=-100: P([(x, y), (x + L * math.cos(math.radians(a)), y + L * math.sin(math.radians(a)))], close=False, w=9)
    for x, y in [(cx - 60, 230), (cx + 10, 220), (cx + 90, 250), (cx + 30, 300), (cx + 120, 320), (cx + 70, 370), (cx + 150, 420), (cx + 110, 470)]:
        b.append(cirrus(x, y, 50))                                                    # 8 frontal
    for x, y in [(cx + 60, 640), (cx + 110, 700), (cx + 40, 760), (cx + 130, 800)]:
        b.append(cirrus(x, y, 44))                                                    # 4 ventral
    for k in range(6):
        b.append(cirrus(cx - 120 + k * 50, 1130 + abs(k - 2.5) * 10, 90, 85))       # 6 transverse
    for s in (-1, 1):                                                                 # marginal rows
        for k in range(26):
            y = 330 + k * 34
            if poly.contains(Point(cx + s * 215, y)) or True:
                x = cx + s * (math.sqrt(max(0, 1 - ((y - 700) / 640) ** 2)) * 245 - 22)
                b.append(P([(x, y), (x + s * 34, y + 14)], close=False, w=5))
    for y in (560, 840):
        b.append(ellipse(cx + 20, y, 60, 90, fill=WHITE, stroke=DEEP, w=LW * 1.2))   # two macronuclear nodules
    b.append(circle(cx - 170, 640, 34, fill=WHITE, stroke=FWG))
    b += [circle(x, y, r, fill=FWG, stroke=FWG) for x, y, r in ((cx - 60, 760, 22), (cx - 120, 920, 18), (cx + 140, 980, 20))]
    save("ciliate-hypotrich-oxytricha", "".join(b), Wd, Ht)


# ------------------------------------------------------------------ 4 Centropyxis, dorsal view
def centropyxis():
    S = 1000; cx, cy = 500, 520
    shell = Polygon(smooth([(cx, 150), (cx + 280, 260), (cx + 340, 520), (cx + 250, 800), (cx, 870), (cx - 250, 800), (cx - 340, 520), (cx - 280, 260)], 200, closed=True))
    b = []
    for a in (-35, 0, 35, -70, 70):                                                    # posterior spines
        r = math.radians(90 + a)
        base = (cx + 300 * math.cos(r) * .9, cy + 330 * math.sin(r) * .95)
        tip = (cx + 460 * math.cos(r), cy + 470 * math.sin(r))
        b.append(P([(base[0] - 16, base[1]), tip, (base[0] + 16, base[1])], fill=WHITE, w=LW))
    b.append(outline(shell, fill=WHITE, w=LW * 1.8))
    grains = []
    for _ in range(5000):
        if len(grains) > 700: break
        x, y = rng.uniform(150, 850), rng.uniform(140, 880); r = rng.uniform(5, 14); p = Point(x, y)
        if shell.buffer(-r).contains(p) and all(p.distance(q) > (r + rq) * .95 for q, rq in grains):
            grains.append((p, r))
    for p, r in grains:
        n = rng.integers(5, 7)
        b.append(P([(p.x + r * math.cos(t), p.y + r * math.sin(t)) for t in np.sort(rng.uniform(0, 6.28, n))], fill=WHITE, w=1.8))
    # eccentric aperture toward the front, with invaginated lip
    b.append(ellipse(cx, 300, 120, 70, fill=WHITE, w=LW * 1.6))
    b.append(ellipse(cx, 308, 92, 50, fill=LIGHT, stroke=FWG, w=LW))
    b.append(P(smooth([(cx - 92, 312), (cx, 340), (cx + 92, 312)], 30), close=False, w=LW * 1.2))
    save("centropyxis", "".join(b), S, S)


# ------------------------------------------------------------------ 5 Trinema
def trinema():
    Wd, Ht = 800, 1000; cx = 400
    shell = Polygon(smooth([(cx, 100), (cx + 230, 220), (cx + 270, 500), (cx + 220, 800), (cx, 900), (cx - 220, 800), (cx - 270, 500), (cx - 230, 220)], 200, closed=True))
    b = [outline(shell, fill=WHITE, w=LW * 1.8)]
    big = []
    for _ in range(4000):
        if len(big) > 60: break
        x, y = rng.uniform(150, 650), rng.uniform(120, 880); r = 34; p = Point(x, y)
        if shell.buffer(-r * .7).contains(p) and all(p.distance(q) > 2 * r * .92 for q in big):
            big.append(p)
    for p in big:
        b.append(circle(p.x, p.y, 34, fill=WHITE, w=2.4))
        b.append(circle(p.x, p.y, 26, fill="none", w=1.4))
    small = []
    for _ in range(6000):
        if len(small) > 120: break
        p = Point(rng.uniform(150, 650), rng.uniform(120, 880))
        if shell.buffer(-12).contains(p) and all(p.distance(q) > 44 for q in big) and all(p.distance(q) > 20 for q in small):
            small.append(p)
    for p in small:
        b.append(circle(p.x, p.y, 9, fill=WHITE, w=1.8))
    # circular aperture near the narrow end, on the ventral face, ringed by tiny scales
    ax, ay = cx + 30, 250
    b.append(circle(ax, ay, 70, fill=WHITE, w=LW * 1.6))
    for k in range(28):
        a = k / 28 * 2 * math.pi
        b.append(circle(ax + 78 * math.cos(a), ay + 78 * math.sin(a), 7, fill=WHITE, w=1.8))
    b.append(circle(ax, ay, 48, fill=LIGHT, stroke=FWG, w=LW))
    b.append(outline(shell, fill="none", w=LW * 1.8))
    save("trinema", "".join(b), Wd, Ht)


# ------------------------------------------------------------------ 6 cercomonad flagellate
def cercomonad():
    Wd, Ht = 1300, 700
    cell = smooth([(420, 360), (480, 260), (600, 230), (720, 270), (800, 340), (770, 430), (660, 470), (520, 450)], 200, closed=True)
    b = []
    b.append(P(smooth([(430, 340), (360, 280), (270, 300), (170, 240), (80, 270)], 120), close=False, w=LW * 1.4))      # anterior flagellum
    b.append(P(smooth([(440, 380), (560, 470), (760, 500), (980, 470), (1220, 520)], 160), close=False, w=LW * 1.4))  # trailing flagellum under the cell
    for a in (-20, 5, 30):                                                                                        # posterior filose pseudopods
        r = math.radians(a)
        b.append(P([(790, 360), (790 + 170 * math.cos(r), 360 + 170 * math.sin(r))], close=False, w=2.4, stroke=FWG))
        b.append(P([(790 + 90 * math.cos(r), 360 + 90 * math.sin(r)), (790 + 90 * math.cos(r) + 60 * math.cos(r + .5), 360 + 90 * math.sin(r) + 60 * math.sin(r + .5))], close=False, w=2, stroke=FWG))
    b.append(P(cell, fill=LIGHT, stroke=FWG, w=LW * 1.5))
    b.append(stipple(cell, 160, 2.6, FWG, avoid=Point(520, 330).buffer(60)))
    b.append(circle(520, 330, 46, fill=WHITE, w=LW * 1.2)); b.append(circle(520, 330, 18, fill=DEEP, stroke=DEEP))
    b += [circle(x, y, r, fill=FWG, stroke=FWG) for x, y, r in ((660, 330, 26), (700, 410, 20))]
    b.append(circle(620, 270, 18, fill=WHITE, stroke=FWG))
    save("flagellate-cercomonad", "".join(b), Wd, Ht)


# ------------------------------------------------------------------ 7 Mucor
def mucor():
    Wd, Ht = 1000, 1300
    b = [hollow(smooth([(60, 1220), (300, 1180), (560, 1230), (940, 1190)], 120), 24)]   # aseptate hypha, no cross walls
    # intact sporangium
    b.append(hollow(smooth([(320, 1190), (300, 900), (320, 560)], 80), 22))
    b.append(circle(320, 470, 120, fill=LIGHT, stroke=FWG, w=LW * 1.6))
    b.append(stipple([(320 + 112 * math.cos(q), 470 + 112 * math.sin(q)) for q in np.linspace(0, 6.28, 80)], 160, 6, WHITE))
    b.append(P(smooth([(300, 560), (320, 520), (340, 560)], 20), close=False, w=LW))
    # burst sporangium: dome-shaped columella with collar, spores spilling
    b.append(hollow(smooth([(700, 1210), (720, 900), (690, 640)], 80), 22))
    col = [(690 + 80 * math.cos(q), 600 - 95 * math.sin(q)) for q in np.linspace(0, math.pi, 50)]
    b.append(P(col + [(610, 640), (770, 640)], fill=WHITE, w=LW * 1.5))
    b.append(P([(600, 640), (612, 610)], close=False, w=LW * 1.4)); b.append(P([(780, 640), (768, 610)], close=False, w=LW * 1.4))
    for _ in range(40):
        a = rng.uniform(-.2, math.pi + .2); r = rng.uniform(110, 240)
        b.append(ellipse(690 + r * math.cos(a), 590 - r * math.sin(a), 11, 8, rng.uniform(0, 180), fill=LIGHT, stroke=FWG, w=2))
    save("mucor-sporangia", "".join(b), Wd, Ht)


# ------------------------------------------------------------------ 8 Aspergillus
def aspergillus():
    Wd, Ht = 900, 1300; cx = 450
    b = [hollow([(cx - 160, 1240), (cx + 160, 1240)], 26), P(smooth([(cx - 60, 1240), (cx - 20, 1215), (cx + 20, 1215), (cx + 60, 1240)], 30), fill=WHITE, w=LW * 1.3)]
    b.append(hollow([(cx, 1215), (cx, 600)], 28))
    b.append(circle(cx, 520, 90, fill=WHITE, w=LW * 1.6))                                     # vesicle
    for k in range(17):                                                                       # phialides with conidial chains
        a = math.radians(-180 + k * 180 / 16 - 2)
        p0 = (cx + 90 * math.cos(a), 520 + 90 * math.sin(a))
        p1 = (cx + 150 * math.cos(a), 520 + 150 * math.sin(a))
        b.append(P([p0, p1], close=False, w=18)); b.append(P([p0, p1], close=False, w=11, stroke=WHITE))
        for j in range(9):
            r = 165 + j * 27
            b.append(circle(cx + r * math.cos(a), 520 + r * math.sin(a), 13, fill=LIGHT, stroke=FWG, w=2.2))
    save("aspergillus-head", "".join(b), Wd, Ht)


# ------------------------------------------------------------------ 9 Trichoderma
def trichoderma():
    Wd, Ht = 1000, 1300
    b = []
    def branch(p, ang, L, d):
        e = (p[0] + L * math.cos(ang), p[1] + L * math.sin(ang))
        b.append(hollow([p, e], 20 - (3 - d) * 2))
        if d == 0:
            for s in (-0.5, 0, 0.5):                                         # whorl of flask-shaped phialides
                a2 = ang + s
                q = (e[0] + 70 * math.cos(a2), e[1] + 70 * math.sin(a2))
                b.append(P([(e[0] + 9 * math.cos(a2 + 1.57), e[1] + 9 * math.sin(a2 + 1.57)), q,
                            (e[0] - 9 * math.cos(a2 + 1.57), e[1] - 9 * math.sin(a2 + 1.57))], fill=WHITE, w=2.4))
                cxl, cyl = q[0] + 26 * math.cos(a2), q[1] + 26 * math.sin(a2)
                for _ in range(9):                                             # small terminal cluster of conidia
                    b.append(ellipse(cxl + rng.normal(0, 13), cyl + rng.normal(0, 13), 9, 7, rng.uniform(0, 180), fill=LIGHT, stroke=FWG, w=2))
            return
        for s in (-1, 1):
            branch(e, ang + s * .55, L * .62, d - 1)
        branch(e, ang, L * .5, d - 1)
    branch((500, 1260), -math.pi / 2, 420, 2)
    save("trichoderma-conidiophore", "".join(b), Wd, Ht)


# ------------------------------------------------------------------ 10 Fusarium spores
def fusarium():
    Wd, Ht = 1400, 800
    b = []
    def macro(x, y, L, rot, septa=5):
        a = math.radians(rot); R = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])
        v = np.linspace(-1, 1, 120)
        mid = np.c_[L / 2 * v, -70 * (1 - v ** 2)]                       # curved centre line (canoe / sickle)
        th = 30 * (1 - np.abs(v) ** 2.2) + 3                              # widest in the middle, tapering ends
        top, bot = mid + np.c_[0 * v, -th], mid + np.c_[0 * v, th]
        top[-6:, 1] -= np.linspace(0, 14, 6)                              # apical cell slightly hooked
        bot[:5] += np.c_[np.zeros(5), np.linspace(10, 0, 5)]              # notched foot cell at the base
        pts = np.vstack([top, bot[::-1]]) @ R.T + [x, y]
        out = P([tuple(p) for p in pts], fill=LIGHT, stroke=FWG, w=LW * 1.4)
        for k in range(1, septa + 1):
            i = int(k / (septa + 1) * 119)
            q = np.vstack([top[i], bot[i]]) @ R.T + [x, y]
            out += P([tuple(q[0]), tuple(q[1])], close=False, w=LW, stroke=DEEP)
        return out
    b.append(macro(420, 300, 520, -8)); b.append(macro(900, 260, 460, 12, 4)); b.append(macro(700, 560, 560, -2))
    b.append(hollow([(1050, 720), (1150, 600), (1200, 520)], 22))                      # phialide with microconidia
    b.append(P([(1190, 530), (1240, 470)], close=False, w=12));
    for x, y in ((1260, 430), (1300, 470), (1250, 380), (1320, 410)):
        b.append(ellipse(x, y, 22, 14, rng.uniform(0, 180), fill=LIGHT, stroke=FWG, w=2.4))
    save("fusarium-spores", "".join(b), Wd, Ht)


# ------------------------------------------------------------------ nematode helper for trap scenes
def trapped_nematode(cl, W):
    pts, n, t, half = nematode_body(cl, W)
    out = [P(pts, fill=WHITE, w=LW * 1.4)]
    k = int(len(cl) * .2)
    out.append(P([tuple(p) for p in cl[3:k]], close=False, w=2))
    out.append(ellipse(cl[k][0], cl[k][1], W * .22, W * .17, math.degrees(math.atan2(t[k][1], t[k][0])), fill=WHITE, w=2.2))
    gut = body_along(cl[k + 6:int(len(cl) * .86)], half[k + 6:int(len(cl) * .86)] * .45)[0]
    out.append(P(gut, fill=LIGHT, stroke=FWG, w=2))
    return out


# ------------------------------------------------------------------ 11 Arthrobotrys adhesive network
def arthrobotrys():
    Wd, Ht = 1400, 900
    b = [hollow(smooth([(40, 760), (400, 720), (800, 770), (1360, 730)], 160), 22)]
    loops = [(330, 560), (520, 520), (700, 560), (880, 520), (1060, 560)]
    for i, (x, y) in enumerate(loops):
        b.append(hollow(smooth([(x - 70, 740), (x - 90, y), (x, y - 110), (x + 90, y), (x + 70, 740)], 80), 20))
        if i:
            b.append(hollow(smooth([(loops[i - 1][0] + 85, loops[i - 1][1] - 20), (x - 30, y - 120), (x - 85, y - 10)], 60), 20))
    b += trapped_nematode(smooth([(160, 300), (400, 420), (620, 480), (860, 420), (1100, 470), (1300, 380)], 300), 52)
    for x in (560, 820):                                                                 # adhesive contact points
        b.append(circle(x, 452, 14, fill=FWG, stroke=FWG))
    save("nematode-trapping-fungus-net", "".join(b), Wd, Ht)


# ------------------------------------------------------------------ 12 Drechslerella constricting ring
def constricting_ring():
    Wd, Ht = 1400, 900
    b = [hollow(smooth([(40, 780), (500, 740), (900, 790), (1360, 750)], 160), 22)]
    b.append(hollow([(700, 760), (700, 560)], 18))
    rc = (700, 470)
    ring = Point(rc).buffer(98).difference(Point(rc).buffer(60))
    b.append(outline(ring, fill=LIGHT, stroke=FWG, w=LW * 1.4))
    for a in (90, 210, 330):                                                             # three ring cells
        r = math.radians(a)
        b.append(P([(rc[0] + 60 * math.cos(r), rc[1] + 60 * math.sin(r)), (rc[0] + 98 * math.cos(r), rc[1] + 98 * math.sin(r))], close=False, w=LW))
    b += trapped_nematode(smooth([(140, 380), (420, 440), (700, 470), (980, 430), (1260, 470)], 300), 58)
    b.append(outline(ring.difference(Point(rc).buffer(0)), fill="none", stroke=FWG, w=LW * 1.4))
    save("nematode-trapping-fungus-ring", "".join(b), Wd, Ht)


# ------------------------------------------------------------------ 13 ectomycorrhiza
def ectomycorrhiza():
    Wd, Ht = 1000, 1400; cx = 500
    from shapely.geometry import box
    root = LineString([(cx, -400), (cx, 1020)]).buffer(230, 48).intersection(box(0, 40, Wd, Ht))
    mantle = root.buffer(60).intersection(box(0, 40, Wd, Ht))
    b = []
    for _ in range(26):                                                                  # extramatrical hyphae into soil
        y = rng.uniform(120, 1200); s = rng.choice([-1, 1])
        x0 = cx + s * (240 + 50); pts = [(x0, y)]
        for _ in range(5):
            pts.append((pts[-1][0] + s * rng.uniform(30, 60), pts[-1][1] + rng.normal(0, 25)))
        b.append(P(pts, close=False, w=3, stroke=FWG))
    b.append(outline(mantle, fill=LIGHT, stroke=FWG, w=LW * 1.4))
    hy = []
    for _ in range(900):                                                                 # dense hyphal sheath
        x, y = rng.uniform(cx - 320, cx + 320), rng.uniform(20, 1340)
        if mantle.contains(Point(x, y)) and not root.contains(Point(x, y)):
            a = rng.uniform(0, math.pi); L = 22
            hy.append(f"M{x:.1f},{y:.1f}l{L * math.cos(a):.1f},{L * math.sin(a):.1f}")
    b.append(f'<path d="{"".join(hy)}" stroke="{FWG}" stroke-width="2.2" fill="none" stroke-linecap="round"/>')
    b.append(outline(root, fill=WHITE, w=LW * 1.6))
    # cortical cells; the Hartig net runs between them (thick green walls), never into the stele
    stele = LineString([(cx, -400), (cx, 900)]).buffer(64, 24).intersection(box(0, 40, Wd, Ht))
    for col in range(3):
        for s in (-1, 1):
            x0 = cx + s * (80 + col * 52)
            for y in np.arange(60, 1000 - col * 40, 90):
                cell = Polygon([(x0, y), (x0 + s * 50, y), (x0 + s * 50, y + 86), (x0, y + 86)])
                if root.buffer(-6).contains(cell):
                    wall = FWG if col < 2 else DEEP
                    b.append(outline(cell, fill=WHITE, stroke=wall, w=6 if col < 2 else 2.4))
    b.append(outline(stele, fill=LIGHT, stroke=DEEP, w=LW))
    save("ectomycorrhiza-root-tip", "".join(b), Wd, Ht)


# ------------------------------------------------------------------ nematode head helper
def head_frame(x0, y0, L, R):
    X = lambda u: x0 + u * L
    edge = lambda u: R * min(1, .55 + .45 * min(1, u / .2) ** .6)
    us = np.linspace(.02, 1.06, 160)
    top = [(X(u), y0 - edge(u)) for u in us]; bot = [(X(u), y0 + edge(u)) for u in us]
    cap = [(X(.02) - L * .045 * math.sin(t), y0 - edge(.02) * math.cos(t)) for t in np.linspace(0, math.pi, 30)]
    out = [P(top[::-1] + cap + bot, fill=WHITE, w=LW * 1.6, close=False)]
    for u in np.arange(.05, 1.0, .03):
        h = edge(u)
        out.append(P([(X(u), y0 - h), (X(u), y0 - h + 12)], close=False, w=2))
        out.append(P([(X(u), y0 + h), (X(u), y0 + h - 12)], close=False, w=2))
    return out, X, edge


# ------------------------------------------------------------------ 14 fungal-feeding nematode head (Aphelenchus)
def fungal_feeder_head():
    Wd, Ht = 1500, 600; y0 = 300
    b, X, edge = head_frame(100, y0, 1300, 180)
    b.append(P([(X(.01), y0), (X(.20), y0 - 5), (X(.20), y0 + 5)], fill=DEEP, w=2))        # slender stylet, no basal knobs
    for s in (-1, 1):
        b.append(P([(X(.20), y0 + s * 8), (X(.11), y0 + s * 100)], close=False, w=1.8))
    pu = [.20, .36, .42, .50, .58, .63, .9, 1.06]; pv = [.08, .1, .74, .82, .74, .1, .1, .5]
    uu = np.linspace(.2, 1.06, 220); vv = np.interp(uu, pu, pv)
    poly = [(X(u), y0 - v * 180) for u, v in zip(uu, vv)] + [(X(u), y0 + v * 180) for u, v in zip(uu[::-1], vv[::-1])]
    b.append(P(poly, fill=LIGHT, stroke=FWG, w=LW * 1.2))
    bx = X(.50)                                                                                 # very large median bulb with valve
    for s in (-1, 1):
        b.append(f'<path d="M{bx - 50:.1f},{y0 + s * 44:.1f}Q{bx:.1f},{y0 + s * 6:.1f} {bx + 50:.1f},{y0 + s * 44:.1f}" fill="none" stroke="{DEEP}" stroke-width="{LW * 2:.2f}" stroke-linecap="round"/>')
    b.append(ellipse(bx, y0, 36, 16, fill=WHITE, stroke=DEEP, w=LW * 1.4))
    b.append(P([(X(.2), y0), (X(.9), y0)], close=False, w=2.2))
    b.append(f'<rect x="{X(.72) - 14:.1f}" y="{y0 - 74:.1f}" width="28" height="148" rx="10" fill="{FWG}"/>')
    save("nematode-fungal-feeder-head", "".join(b), Wd, Ht)


# ------------------------------------------------------------------ 15 predatory nematode head (Mononchus)
def predator_head():
    Wd, Ht = 1500, 640; y0 = 320
    b, X, edge = head_frame(100, y0, 1300, 200)
    # large buccal cavity, about twice as long as wide, thick sclerotised walls
    cav = [(X(.02), y0 - 110), (X(.30), y0 - 100), (X(.33), y0 - 40), (X(.33), y0 + 40), (X(.30), y0 + 100), (X(.02), y0 + 110)]
    b.append(P(cav, fill=WHITE, w=LW * 3.4, close=False))
    b.append(P([(X(.05), y0 - 86), (X(.29), y0 - 78), (X(.30), y0 - 30)], close=False, w=LW * 1.2))
    b.append(P([(X(.05), y0 + 86), (X(.29), y0 + 78), (X(.30), y0 + 30)], close=False, w=LW * 1.2))
    b.append(P([(X(.10), y0 - 96), (X(.17), y0 - 40), (X(.21), y0 - 96)], fill=DEEP, w=LW))     # large dorsal tooth, anterior
    # muscular cylindrical pharynx, no bulb
    b.append(P([(X(.33), y0 - 70), (X(1.06), y0 - 76), (X(1.06), y0 + 76), (X(.33), y0 + 70)], fill=LIGHT, stroke=FWG, w=LW * 1.2))
    b.append(P([(X(.33), y0), (X(1.06), y0)], close=False, w=2.2))
    for u in np.arange(.38, 1.04, .06):
        b.append(P([(X(u), y0 - 66), (X(u) + 30, y0 - 20)], close=False, w=1.6, stroke=FWG))
        b.append(P([(X(u), y0 + 66), (X(u) + 30, y0 + 20)], close=False, w=1.6, stroke=FWG))
    b.append(f'<rect x="{X(.60) - 14:.1f}" y="{y0 - 92:.1f}" width="28" height="184" rx="10" fill="{FWG}"/>')
    save("nematode-predator-head", "".join(b), Wd, Ht)


# ------------------------------------------------------------------ 16 earthworm
def earthworm():
    Wd, Ht = 1600, 600
    cl = smooth([(80, 300), (400, 250), (800, 320), (1200, 300), (1520, 250)], 400)
    u = np.linspace(0, 1, len(cl))
    half = 60 * np.minimum(1, .5 + .5 * np.clip(u / .06, 0, 1)) * np.minimum(1, .45 + .55 * np.clip((1 - u) / .05, 0, 1))
    half = half * np.where((u > .22) & (u < .32), 1.18, 1)
    pts, n, t = body_along(cl, half)
    b = [P(pts, fill=LIGHT, stroke=FWG, w=LW * 1.5)]
    seg = []
    for k in np.arange(.025, .985, .011):
        i = int(k * (len(cl) - 1))
        if .22 < k < .32: continue
        p, q = cl[i] + n[i] * half[i] * .98, cl[i] - n[i] * half[i] * .98
        seg.append(f"M{p[0]:.1f},{p[1]:.1f}Q{cl[i][0] + t[i][0] * 8:.1f},{cl[i][1] + t[i][1] * 8:.1f} {q[0]:.1f},{q[1]:.1f}")
        for f in (.55, .8):                                                                # 4 pairs of setae per segment, ventral side
            s0 = cl[i] - n[i] * half[i] * f
            seg.append(f"M{s0[0]:.1f},{s0[1]:.1f}l{-n[i][0] * 10:.1f},{-n[i][1] * 10:.1f}")
    b.append(f'<path d="{"".join(seg)}" fill="none" stroke="{FWG}" stroke-width="2.2" stroke-linecap="round"/>')
    i0, i1 = int(.22 * len(cl)), int(.32 * len(cl))
    clit = body_along(cl[i0:i1], half[i0:i1])[0]
    b.append(P(clit, fill=FWG, stroke=DEEP, w=LW * 1.3))                                   # clitellum, the saddle
    h = cl[0]; tt = t[0]; nn = n[0]
    pro = [tuple(h + tt * 4 + nn * 30), tuple(h - tt * 36 + nn * 10), tuple(h - tt * 30 - nn * 14), tuple(h + tt * 6 - nn * 6)]
    b.append(P(smooth(pro, 40), fill=LIGHT, stroke=FWG, w=LW * 1.3))                       # prostomium over the mouth
    b.append(P(smooth([tuple(cl[3] - n[3] * half[3] * .9), tuple(cl[12] - n[12] * 10), tuple(cl[20] + n[20] * half[20] * .9)], 40), close=False, w=2.6, stroke=DEEP))
    save("earthworm", "".join(b), Wd, Ht)


# ------------------------------------------------------------------ 17 root nodule section
def root_nodule():
    Wd, Ht = 1300, 1100
    b = [f'<rect x="40" y="820" width="1220" height="180" rx="40" fill="{LIGHT}" stroke="{FWG}" stroke-width="{LW * 1.5}"/>']
    nod = Point(650, 470).buffer(380)
    b.append(outline(nod, fill=WHITE, w=LW * 1.8))
    b.append(outline(Point(650, 470).buffer(340), fill="none", w=LW))
    zone = Point(650, 470).buffer(300)
    cells = []
    for gx in np.arange(360, 960, 64):
        for gy in np.arange(180, 780, 64):
            x, y = gx + (32 if int(gy / 64) % 2 else 0), gy
            c = Point(x, y).buffer(30, 6)
            if zone.contains(c):
                cells.append((x, y))
    for k, (x, y) in enumerate(cells):
        infected = (k * 7) % 5 != 0
        b.append(circle(x, y, 30, fill=LIGHT if infected else WHITE, stroke=FWG, w=2.2))
        if infected:
            for _ in range(11):                                                             # bacteroids in symbiosomes
                a = rng.uniform(0, 6.28); r = rng.uniform(0, 20)
                px, py = x + r * math.cos(a), y + r * math.sin(a); ang = rng.uniform(0, 180)
                b.append(ellipse(px, py, 5, 2.6, ang, fill=FWG, stroke=FWG, w=1))
    b.append(P(smooth([(1080, 820), (1000, 760), (900, 700), (820, 640)], 60), close=False, w=5, stroke=DEEP))      # infection thread
    b.append(P(smooth([(1080, 820), (1110, 700), (1150, 560)], 40), close=False, w=14, stroke=FWG))               # root hair
    save("root-nodule-section", "".join(b), Wd, Ht)


# ------------------------------------------------------------------ 18 Pinnularia diatom
def pinnularia():
    Wd, Ht = 600, 1500; cx = 300
    v = smooth([(cx, 60), (cx + 130, 140), (cx + 140, 600), (cx + 150, 750), (cx + 140, 900), (cx + 130, 1360), (cx, 1440),
                (cx - 130, 1360), (cx - 140, 900), (cx - 150, 750), (cx - 140, 600), (cx - 130, 140)], 300, closed=True)
    poly = Polygon(v)
    b = [P(v, fill=LIGHT, stroke=FWG, w=LW * 1.5)]
    for y in np.arange(130, 1400, 30):                                                     # broad striae, radiate at centre
        if 660 < y < 840: continue
        d = (y - 750) / 690
        tilt = 18 * (1 if d < 0 else -1) * (1 - abs(d)) ** 2
        for s in (-1, 1):
            p0 = (cx + s * 40, y); p1 = (cx + s * 132, y + tilt)
            if poly.contains(Point(*p1)):
                b.append(P([p0, p1], close=False, w=9, stroke=WHITE))
                b.append(P([p0, p1], close=False, w=2, stroke=FWG))
    b.append(ellipse(cx, 750, 60, 90, fill=WHITE, stroke=FWG, w=2))                         # central area
    b.append(P([(cx, 100), (cx + 4, 720)], close=False, w=LW * 1.3))                         # raphe, two branches
    b.append(P([(cx + 4, 780), (cx, 1400)], close=False, w=LW * 1.3))
    b.append(circle(cx + 2, 750, 12, fill=DEEP, stroke=DEEP))                                # central nodule
    for y, s in ((100, -1), (1400, 1)):                                                      # hooked terminal fissures
        b.append(P(smooth([(cx, y), (cx + 12, y + s * 26), (cx + 34, y + s * 20)], 20), close=False, w=LW * 1.3))
    save("diatom-pinnularia", "".join(b), Wd, Ht)


# ------------------------------------------------------------------ 19 Nostoc
def nostoc():
    Wd, Ht = 1300, 900
    b = [P(blob(650, 450, 380, [(0, .1, .6), (120, .08, .5), (240, .12, .5)], 200) * np.array([1.4, 1.0]) + np.array([-260, 0]), fill=WHITE, stroke=FWG, w=LW, extra=' stroke-dasharray="14 10"')]
    for ctrl in ([(260, 300), (460, 220), (700, 260), (880, 360), (1020, 300)],
                 [(240, 560), (420, 480), (620, 560), (820, 640), (1040, 580)],
                 [(380, 700), (560, 760), (760, 720)]):
        line = LineString(smooth(ctrl, 200))
        n = int(line.length / 40)
        for k in range(n):
            p = line.interpolate(k * 40 + 20)
            if k in (n // 2,) or (k == 0):
                b.append(circle(p.x, p.y, 26, fill=WHITE, stroke=DEEP, w=LW * 1.8))         # heterocyst: thick wall
                b.append(circle(p.x, p.y, 8, fill=DEEP, stroke=DEEP))
            elif k in (n // 4, 3 * n // 4):
                b.append(ellipse(p.x, p.y, 30, 22, 0, fill=FWG, stroke=DEEP, w=LW * 1.3))  # akinete, midway between heterocysts
                b.append(stipple([(p.x + 24 * math.cos(q), p.y + 16 * math.sin(q)) for q in np.linspace(0, 6.28, 30)], 20, 2.4, WHITE))
            else:
                b.append(circle(p.x, p.y, 19, fill=LIGHT, stroke=FWG, w=2.4))               # bead-like vegetative cells
    save("cyanobacteria-nostoc", "".join(b), Wd, Ht)


# ------------------------------------------------------------------ 20 Dictyostelium
def dictyostelium():
    Wd, Ht = 1100, 1500; cx = 420
    b = [P(list(map(tuple, smooth([(cx - 120, 1440), (cx - 60, 1400), (cx + 60, 1400), (cx + 120, 1440)], 40))) + [(cx - 120, 1440)], fill=WHITE, w=LW * 1.4)]  # basal disc
    for k in range(50):                                                                       # tapering stalk of cells
        y = 1400 - k * 24; w = 30 - k * .38
        b.append(f'<rect x="{cx - w:.1f}" y="{y - 24:.1f}" width="{2 * w:.1f}" height="24" fill="{WHITE}" stroke="{DEEP}" stroke-width="2"/>')
    b.append(P(smooth([(cx - 60, 230), (cx, 205), (cx + 60, 230)], 20), close=False, w=LW * 1.4))  # lower cup
    b.append(circle(cx, 120, 160, fill=LIGHT, stroke=FWG, w=LW * 1.6))                            # sorus of spores
    for _ in range(170):
        a = rng.uniform(0, 6.28); r = 150 * math.sqrt(rng.random())
        b.append(ellipse(cx + r * math.cos(a), 120 + r * math.sin(a), 10, 6, rng.uniform(0, 180), fill=WHITE, stroke=FWG, w=1.6))
    # migrating slug, the stage before the fruiting body
    slug = smooth([(620, 1400), (700, 1350), (900, 1340), (1040, 1360), (1060, 1400), (900, 1420), (700, 1430)], 120, closed=True)
    b.append(P(slug, fill=LIGHT, stroke=FWG, w=LW * 1.3))
    b.append(P(smooth([(620, 1430), (500, 1440), (380, 1450)], 30), close=False, w=3, stroke=FWG, extra=' stroke-dasharray="6 8"'))  # slime trail
    save("slime-mould-dictyostelium", '<g transform="translate(0,100)">' + "".join(b) + "</g>", Wd, Ht + 100)


def main():
    for f in (rotifer, tardigrade, hypotrich, centropyxis, trinema, cercomonad, mucor, aspergillus, trichoderma, fusarium,
              arthrobotrys, constricting_ring, ectomycorrhiza, fungal_feeder_head, predator_head, earthworm, root_nodule,
              pinnularia, nostoc, dictyostelium):
        f()


if __name__ == "__main__":
    main()
