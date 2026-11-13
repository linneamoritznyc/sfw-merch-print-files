"""SFW Field Guide, page 2: bacterial-feeding nematode (rhabditid type, female). A4, vector, text as outlines.

SFW's own drawing, constructed in code. Anatomy follows the standard rhabditid plan:
  lip region (6 lips, 3 seen in side view); open tubular stoma, no stylet; pharynx = corpus with a median
  swelling, isthmus ringed by the nerve ring, basal bulb with a valve (grinder); excretory pore near the nerve
  ring; granular intestine; vulva near mid-body with paired (didelphic) reflexed gonads and eggs; rectum, anus,
  conical pointed tail. Feeding-group heads: open stoma (bacteria), thin stylet (fungi), knobbed stylet (roots),
  wide stoma with tooth (predator).
To check against: Cobb (1914) USDA drawings; modern photos and keys. DRAFT until an SFW mentor has checked it.

Usage: python3 nematode.py  ->  out/nematode-field-guide.svg / .png / -preview.png
"""
import io, math, os
import numpy as np
import cairosvg
from PIL import Image
from euglypha import text, para, d_of, label, DEEP, FWG, LIGHT, WHITE, W, H, HERE, OUT

LW = 3.2
G6 = "eb-garamond-latin-600-normal.woff2"


# ------------------------------------------------------------------ body frame: (u along body, v across) -> page
class Body:
    def __init__(self, ctrl, width, n=600):
        p = np.asarray(ctrl, float)
        # Catmull-Rom centreline
        q = np.vstack([2 * p[0] - p[1], p, 2 * p[-1] - p[-2]])
        pts = []
        for i in range(len(q) - 3):
            p0, p1, p2, p3 = q[i:i + 4]
            for t in np.linspace(0, 1, n // (len(q) - 3), endpoint=False):
                pts.append(0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
        pts.append(q[-2])
        c = np.array(pts)
        d = np.r_[0, np.cumsum(np.hypot(*np.diff(c, axis=0).T))]
        self.u = d / d[-1]; self.c = c; self.len = d[-1]; self.W = width
        t = np.gradient(c, axis=0); t /= np.linalg.norm(t, axis=1)[:, None]
        self.n = np.c_[-t[:, 1], t[:, 0]]

    def half(self, u):
        u = np.asarray(u, float)
        head = 0.42 + 0.58 * np.clip(u / 0.16, 0, 1) ** 0.6           # blunt lip region widening to full body
        tail = np.clip((1 - u) / 0.075, 0, 1) ** 0.85                  # conical tail after the anus
        return self.W / 2 * np.minimum(head, np.where(u > 0.925, tail, 1.0))

    def at(self, u, v):
        """u in [0,1] head to tail, v in [-1,1] across (+ = ventral)."""
        u = np.clip(np.asarray(u, float), 0, 1); v = np.asarray(v, float)
        x = np.interp(u, self.u, self.c[:, 0]); y = np.interp(u, self.u, self.c[:, 1])
        nx = np.interp(u, self.u, self.n[:, 0]); ny = np.interp(u, self.u, self.n[:, 1])
        h = self.half(u)
        return np.c_[x + nx * v * h, y + ny * v * h]

    def band(self, u0, u1, v0, v1, n=80):
        """Closed outline of the region u0..u1, v0(u)..v1(u) (v0, v1 numbers or functions of u)."""
        us = np.linspace(u0, u1, n)
        f = lambda v: (v(us) if callable(v) else np.full_like(us, v))
        a = self.at(us, f(v1)); b = self.at(us[::-1], f(v0)[::-1])
        return np.vstack([a, b])

    def outline(self):
        us = np.linspace(0, 1, 400)
        top, bot = self.at(us, -1), self.at(us[::-1], 1)
        c0 = self.at(0, 0)[0]; h0 = self.half(0.0)
        tang = (self.c[3] - self.c[0]) / np.linalg.norm(self.c[3] - self.c[0]); n0 = self.n[0]
        cap = [c0 + n0 * h0 * math.sin(a) - tang * h0 * 0.85 * math.cos(a) for a in np.linspace(math.pi / 2, -math.pi / 2, 30)]
        return np.vstack([top, bot, np.array(cap)])


def path(pts, fill="none", stroke=DEEP, w=LW, close=True, extra=""):
    return f'<path d="{d_of(pts, close)}" fill="{fill}" stroke="{stroke}" stroke-width="{w:.2f}" stroke-linejoin="round"{extra}/>'


def whole_body(rng):
    """Drawing A: whole female in a gentle S curve, about 1 mm."""
    ctrl = [(230, 1010), (640, 900), (1080, 1000), (1520, 1090), (1940, 990), (2250, 1050)]
    b = Body(ctrl, width=96)
    out = [path(b.outline(), fill=WHITE, w=LW * 1.5)]
    # intestine
    gut = b.band(0.175, 0.915, -0.55, 0.55)
    out.append(path(gut, fill=LIGHT, stroke=FWG, w=LW * .8))
    us = rng.uniform(0.18, 0.91, 900); vs = rng.uniform(-0.45, 0.45, 900)
    g = b.at(us, vs)
    out.append("".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.6" fill="{FWG}"/>' for x, y in g))
    # gonads: didelphic, reflexed; eggs in the uteri either side of the vulva
    for sgn in (-1, 1):
        us_ = np.linspace(0.52 + sgn * 0.03, 0.52 + sgn * 0.20, 60)
        arm = np.vstack([b.at(us_, 0.10), b.at(us_[::-1], -0.12)])     # out along the gut and folded back
        out.append(path(arm, fill=WHITE, stroke=DEEP, w=LW * .8))
        for k in range(2):
            ue = 0.52 + sgn * (0.045 + k * 0.045)
            e = b.at(np.linspace(ue - 0.018, ue + 0.018, 2), 0)
            cx_, cy_ = e.mean(0); ang = math.degrees(math.atan2(*(e[1] - e[0])[::-1]))
            out.append(f'<ellipse cx="{cx_:.1f}" cy="{cy_:.1f}" rx="{0.019 * b.len:.1f}" ry="{b.W * .36:.1f}" '
                       f'transform="rotate({ang:.1f} {cx_:.1f} {cy_:.1f})" fill="{WHITE}" stroke="{DEEP}" stroke-width="{LW:.2f}"/>')
    vul = b.at([0.52, 0.52], [0.55, 1.0])
    out.append(path(vul, close=False, w=LW * 1.2))
    # pharynx: corpus with median swelling, isthmus, basal bulb
    prof = lambda u: np.interp(u, [0.0, 0.07, 0.085, 0.105, 0.115, 0.14, 0.15, 0.165, 0.175],
                               [0.18, 0.30, 0.42, 0.30, 0.18, 0.18, 0.46, 0.46, 0.20])
    ph = b.band(0.012, 0.175, lambda u: -prof(u), lambda u: prof(u), n=120)
    out.append(path(ph, fill=WHITE, stroke=DEEP, w=LW))
    out.append(path(b.at(np.linspace(0.0, 0.03, 10), 0), close=False, w=LW * 1.4))           # stoma
    out.append(path(b.at(np.linspace(0.03, 0.16, 40), 0), close=False, w=LW * .7))            # lumen
    nr = b.at([0.125, 0.125], [-0.9, 0.9]); out.append(path(nr, close=False, w=LW * 3, stroke=FWG))
    # rectum and anus
    out.append(path(b.at(np.linspace(0.915, 0.93, 6), np.linspace(0, 1, 6)), close=False, w=LW))
    pts = {"head": b.at(0.0, 0)[0], "pharynx": b.at(0.06, -0.3)[0], "bulb": b.at(0.157, -0.46)[0],
           "gut": b.at(0.33, -0.5)[0], "vulva": b.at(0.52, 1.0)[0], "egg": b.at(0.61, -0.36)[0],
           "anus": b.at(0.93, 1.0)[0], "tail": b.at(0.975, 0)[0], "len": b.len}
    return "".join(out), pts


def smooth1(a, k=7):
    a = np.asarray(a, float); ker = np.ones(k) / k
    return np.convolve(np.pad(a, k // 2, mode="edge"), ker, mode="valid")


def head_detail(x0, y0, L):
    """Drawing B: head and pharynx, straight, enlarged. x0,y0 = lip tip on the axis, L = length to end of bulb.
    The body continues to the right, so its edges stay open there."""
    Wd = L * 0.15
    X = lambda u: x0 + u * L
    edge = lambda u: Wd * np.minimum(1, 0.62 + 0.38 * np.clip(u / 0.22, 0, 1) ** .6)
    out = []
    us = np.linspace(0.025, 1.12, 200)
    top = [(X(u), y0 - e) for u, e in zip(us, edge(us))]
    bot = [(X(u), y0 + e) for u, e in zip(us, edge(us))]
    # three lips in side view: rounded bumps across the front
    e0 = edge(0.025); lip = []
    for j in range(3):
        ya, yb = y0 - e0 + j * 2 * e0 / 3, y0 - e0 + (j + 1) * 2 * e0 / 3
        for t in np.linspace(0, math.pi, 16):
            lip.append((X(0.025) - math.sin(t) * L * 0.028, ya + (yb - ya) * (1 - math.cos(t)) / 2))
    outline = top[::-1] + lip + bot
    out.append(path(outline, fill=WHITE, w=LW * 1.5, close=False))
    for u in np.arange(0.07, 1.12, 0.024):                       # cuticle annuli: short ticks inside both edges
        h = float(edge(u))
        out.append(path([(X(u), y0 - h), (X(u), y0 - h + 10)], close=False, w=2.2))
        out.append(path([(X(u), y0 + h), (X(u), y0 + h - 10)], close=False, w=2.2))
    # stoma: open tube with thick walls
    for sg in (-1, 1):
        out.append(path([(X(0.0), y0 + sg * Wd * .12), (X(0.14), y0 + sg * Wd * .07)], close=False, w=LW * 2.2))
    # pharynx, smooth: corpus, median swelling, isthmus, basal bulb
    pu = [0.14, 0.30, 0.38, 0.46, 0.54, 0.60, 0.74, 0.79, 0.87, 0.95, 0.99, 1.0]
    pv = [0.20, 0.27, 0.42, 0.44, 0.30, 0.15, 0.15, 0.40, 0.52, 0.42, 0.20, 0.15]
    uu = np.linspace(0.14, 1.0, 220); vv = smooth1(np.interp(uu, pu, pv), 15)
    poly = [(X(u), y0 - v * Wd) for u, v in zip(uu, vv)] + [(X(u), y0 + v * Wd) for u, v in zip(uu[::-1], vv[::-1])]
    out.append(path(poly, fill=WHITE, w=LW * 1.2))
    out.append(path([(X(0.14), y0), (X(0.83), y0)], close=False, w=LW * .8))     # lumen
    # nerve ring: a band around the isthmus
    nr = X(0.67)
    out.append(f'<rect x="{nr - L * .018:.1f}" y="{y0 - Wd * .42:.1f}" width="{L * .036:.1f}" height="{Wd * .84:.1f}" rx="{L * .012:.1f}" fill="{LIGHT}" stroke="{FWG}" stroke-width="{LW:.2f}"/>')
    out.append(path([(X(0.60), y0), (X(0.74), y0)], close=False, w=LW * .8))
    # valve (grinder) in the basal bulb: three curved plates meeting at the lumen
    bx = X(0.87)
    for sg in (-1, 1):
        out.append(f'<path d="M{bx - Wd * .22:.1f},{y0 + sg * Wd * .30:.1f}Q{bx - Wd * .02:.1f},{y0 + sg * Wd * .02:.1f} {bx + Wd * .22:.1f},{y0 + sg * Wd * .30:.1f}" fill="none" stroke="{DEEP}" stroke-width="{LW * 1.8:.2f}" stroke-linecap="round"/>')
    out.append(path([(bx - Wd * .25, y0), (bx + Wd * .25, y0)], close=False, w=LW * 1.8))
    # excretory pore and duct (ventral side = bottom)
    ex = X(0.71)
    out.append(path([(ex, y0 + float(edge(0.71))), (ex - L * .025, y0 + Wd * .45)], close=False, w=LW))
    # intestine continuing past the frame
    gut = [(X(1.0), y0 - Wd * .5), (X(1.12), y0 - Wd * .58), (X(1.12), y0 + Wd * .58), (X(1.0), y0 + Wd * .5)]
    out.append(path(gut, fill=LIGHT, stroke=FWG, w=LW))
    pts = {"lips": (X(0.0), y0 - Wd * .45), "stoma": (X(0.08), y0 - Wd * .10), "corpus": (X(0.24), y0 + Wd * .24),
           "swelling": (X(0.42), y0 - Wd * .44), "nerve": (nr, y0 - Wd * .42), "isthmus": (X(0.57), y0 + Wd * .18),
           "bulb": (bx, y0 + Wd * .52), "valve": (bx, y0 - Wd * .15), "pore": (ex, y0 + float(edge(0.71))),
           "gut": (X(1.08), y0 + Wd * .58)}
    return "".join(out), pts, Wd


def feeding_head(cx, top, Wd, kind):
    """Drawing C: a head pointing up. kind = bacteria | fungi | roots | predator."""
    H_ = Wd * 3.2
    out = []
    left = [(cx - Wd * min(1, 0.6 + 0.4 * (t / 0.35) ** .6), top + t * H_) for t in np.linspace(0, 1, 40)]
    right = [(cx + (cx - x), y) for x, y in left]                 # mirror of the left edge, top to bottom
    body = left + right
    capp = [(cx - Wd * .6 * math.cos(t), top - Wd * .22 * math.sin(t)) for t in np.linspace(0, math.pi, 20)]
    out.append(path(left[::-1] + capp + right, fill=WHITE, w=LW * 1.4, close=False))
    if kind == "bacteria":
        for s in (-1, 1):
            out.append(path([(cx + s * Wd * .12, top), (cx + s * Wd * .08, top + H_ * .38)], close=False, w=LW * 2))
        out.append(path([(cx, top + H_ * .38), (cx, top + H_ * .95)], close=False, w=LW * .8))
    elif kind == "fungi":
        out.append(path([(cx, top + Wd * .05), (cx, top + H_ * .30)], close=False, w=LW * 1.3))
        out.append(path([(cx, top + H_ * .30), (cx, top + H_ * .95)], close=False, w=LW * .8))
    elif kind == "roots":
        out.append(path([(cx, top + Wd * .05), (cx, top + H_ * .36)], close=False, w=LW * 2.4))
        for s in (-1, 0, 1):
            out.append(f'<circle cx="{cx + s * Wd * .13:.1f}" cy="{top + H_ * .38:.1f}" r="{Wd * .09:.1f}" fill="{DEEP}"/>')
        out.append(path([(cx, top + H_ * .40), (cx, top + H_ * .95)], close=False, w=LW * .8))
    elif kind == "predator":
        cav = [(cx - Wd * .42, top + Wd * .05), (cx - Wd * .38, top + H_ * .34), (cx + Wd * .38, top + H_ * .34), (cx + Wd * .42, top + Wd * .05)]
        out.append(path(cav, fill=WHITE, w=LW * 2.2, close=False))
        out.append(path([(cx - Wd * .38, top + H_ * .14), (cx - Wd * .12, top + H_ * .10), (cx - Wd * .36, top + H_ * .24)], fill=DEEP, w=LW))
        out.append(path([(cx, top + H_ * .34), (cx, top + H_ * .95)], close=False, w=LW * .8))
    return "".join(out)


def page():
    rng = np.random.default_rng(3)
    M = 170
    body = [f'<rect width="{W}" height="{H}" fill="{WHITE}"/>']
    body.append(text("SOIL FOOD WEB FIELD GUIDE", 34, M, 230, fnt=G6, track=180, color=FWG)[0])
    body.append(text("No. 2", 34, W - M, 230, fnt=G6, anchor="end", track=120, color=FWG)[0])
    body.append(text("Bacterial-feeding nematode", 128, M - 4, 400)[0])
    body.append(text("A roundworm that grazes on bacteria and releases nitrogen for plants", 52, M, 500)[0])
    body.append(text("Nematoda  ·  Rhabditida  ·  for example Rhabditis, Cephalobus, Acrobeles", 40, M, 570, color=FWG)[0])
    # A whole body
    a, p = whole_body(rng)
    body.append(a)
    body += [label(p["head"], 240, 790, ["Head"], side="right"),
             label(p["pharynx"], 520, 760, ["Pharynx"], side="right"),
             label(p["bulb"], 840, 780, ["Basal bulb"], side="right"),
             label(p["gut"], 1080, 840, ["Intestine"], side="right"),
             label(p["vulva"], 1500, 1250, ["Vulva"], side="right"),
             label(p["egg"], 1680, 870, ["Egg"], side="right"),
             label(p["anus"], 2010, 1250, ["Anus"], side="right"),
             label(p["tail"], 2150, 900, ["Tail"], side="left")]
    um = p["len"] / 1000                        # this drawing shows a worm about 1 mm long
    body.append(f'<rect x="{M:.1f}" y="1330" width="{100 * um:.1f}" height="10" fill="{DEEP}"/>')
    body.append(text("100 µm", 34, M + 50 * um, 1312, anchor="middle")[0])
    body.append(text("A  Whole worm, female, about 1 mm", 40, W / 2, 1420, anchor="middle", fnt=G6)[0])
    # B head and pharynx
    bsvg, q, Wd = head_detail(330, 1850, 1600)
    body.append(bsvg)
    up, dn = 1850 - Wd - 90, 1850 + Wd + 120
    body += [label(q["lips"], 190, up, ["Lips"], side="right"),
             label(q["stoma"], 420, up, ["Open mouth tube,", "no stylet"], side="right"),
             label(q["swelling"], 900, up, ["Median swelling"], side="right"),
             label(q["nerve"], 1300, up, ["Nerve ring"], side="right"),
             label(q["valve"], 1650, up, ["Valve that crushes", "bacteria"], side="right"),
             label(q["corpus"], 600, dn, ["Corpus"], side="right"),
             label(q["isthmus"], 1010, dn, ["Isthmus"], side="right"),
             label(q["pore"], 1330, dn, ["Excretory pore"], side="right"),
             label(q["bulb"], 1700, dn, ["Basal bulb"], side="right"),
             label(q["gut"], 2030, dn, ["Intestine"], side="right")]
    body.append(text("B  Head and pharynx, where you identify it", 40, W / 2, 2290, anchor="middle", fnt=G6)[0])
    # C feeding groups
    y3, wd = 2520, 70
    for i, (kind, name) in enumerate([("bacteria", "Bacteria"), ("fungi", "Fungi"), ("roots", "Roots"), ("predator", "Predator")]):
        cx = M + 110 + i * 240
        body.append(feeding_head(cx, y3, wd, kind))
        body.append(text(name, 36, cx, y3 + wd * 3.2 + 70, anchor="middle")[0])
    sub = ["Open tube", "Thin stylet", "Stylet with knobs", "Wide mouth, tooth"]
    for i, s_ in enumerate(sub):
        body.append(text(s_, 28, M + 110 + i * 240, y3 + wd * 3.2 + 112, anchor="middle", color=FWG)[0])
    body.append(text("C  What each group eats, read from the head", 40, M + 470, y3 + wd * 3.2 + 210, anchor="middle", fnt=G6)[0])
    # facts
    fx, fy, fs = 1260, 2470, 36
    facts = [("Size", ["Typically about 1 mm long and 50 µm wide."]),
             ("Where", ["Water films around soil particles,", "around roots and in compost."]),
             ("Eats", ["Bacteria, sucked in through the open", "mouth and crushed in the basal bulb."]),
             ("Role", ["It eats more nitrogen than it needs and", "releases the rest as ammonium, a form", "plant roots can take up."]),
             ("At 400x", ["Look at the head: an open tube, no stylet,", "and a round bulb that pumps as it feeds."])]
    y = fy
    for head, lines in facts:
        body.append(text(head, fs, fx, y, fnt=G6, color=FWG)[0])
        t, yl = para(lines, fs, fx + 210, y)
        body.append(t)
        y = yl + fs * 1.7
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n' + "\n".join(body) + "\n</svg>\n"


def main():
    os.makedirs(OUT, exist_ok=True)
    svg = page()
    open(os.path.join(OUT, "nematode-field-guide.svg"), "w").write(svg)
    png = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(), output_width=W, output_height=H))).convert("RGBA")
    logo = Image.open(os.path.join(HERE, "..", "creative-code", "logos", "SFW-logo-flower-colour.png")).convert("RGBA")
    logo.thumbnail((230, 230)); png.alpha_composite(logo, (W - 170 - logo.width, H - 270 - logo.height + 120))
    png.convert("RGB").save(os.path.join(OUT, "nematode-field-guide.png"), dpi=(300, 300), optimize=True)
    pv = png.convert("RGB"); pv.thumbnail((1240, 1754)); pv.save(os.path.join(OUT, "nematode-field-guide-preview.png"))


if __name__ == "__main__":
    main()
