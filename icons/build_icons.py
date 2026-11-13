"""SFW soil-life icon set. One stroke weight, round caps and joins, 512 x 512 grid, single colour.
Each icon keeps only the features that identify the organism, taken from the checked field guide
(see ../field-guide/SOURCES.md). Outputs SVG (recolourable in Canva) and transparent PNG, in deep green,
Food Web Green and white, plus a preview sheet.

Usage: python3 build_icons.py
"""
import io, math, os
import numpy as np
import cairosvg
from PIL import Image, ImageDraw
from shapely.geometry import LineString, Point
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
S = 512
SW = 16                                   # stroke weight
COLOURS = {"deep-green": "#22371F", "food-web-green": "#156826", "white": "#FFFFFF"}


def pts(p):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in p)


def line(p, w=SW):
    return f'<polyline points="{pts(p)}" stroke-width="{w}"/>'


def poly(p, w=SW):
    return f'<polygon points="{pts(p)}" stroke-width="{w}"/>'


def outline(geom, w=SW):
    out = []
    for g in getattr(geom, "geoms", [geom]):
        out.append(poly(list(g.exterior.coords)[:-1], w))
        for r in g.interiors:
            out.append(poly(list(r.coords)[:-1], w))
    return "".join(out)


def circ(x, y, r, w=SW, fill=False):
    f = ' fill="currentColor"' if fill else ""
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" stroke-width="{w}"{f}/>'


def ell(x, y, rx, ry, rot=0, w=SW, fill=False):
    f = ' fill="currentColor"' if fill else ""
    return f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" transform="rotate({rot} {x:.1f} {y:.1f})" stroke-width="{w}"{f}/>'


def smooth(ctrl, n=120, closed=False):
    p = np.asarray(ctrl, float)
    q = np.vstack([p[-1], p, p[0], p[1]]) if closed else np.vstack([2 * p[0] - p[1], p, 2 * p[-1] - p[-2]])
    out = []
    for i in range(len(q) - 3):
        p0, p1, p2, p3 = q[i:i + 4]
        for t in np.linspace(0, 1, max(4, n // (len(q) - 3)), endpoint=False):
            out.append(0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    if not closed:
        out.append(q[-2])
    return out


def wave(p0, ang, L, amp, waves, n=60):
    a = math.radians(ang); t = np.array([math.cos(a), math.sin(a)]); nn = np.array([-t[1], t[0]])
    return [tuple(np.array(p0) + t * L * u + nn * amp * math.sin(u * waves * 2 * math.pi) * min(1, u * 3)) for u in np.linspace(0, 1, n)]


def blob(cx, cy, R, lobes, n=200):
    out = []
    for t in np.linspace(0, 2 * math.pi, n, endpoint=False):
        r = R
        for a, h, wd in lobes:
            d = (t - math.radians(a) + math.pi) % (2 * math.pi) - math.pi
            r += R * h * math.exp(-(d / wd) ** 2)
        out.append((cx + r * math.cos(t), cy + r * math.sin(t)))
    return out


# ------------------------------------------------------------------ icons
def testate_amoeba():
    """Euglypha, side view: ovoid shell of overlapping scales in rows, toothed mouth, fine pseudopods."""
    cx, cy, A, B = 256, 210, 160, 118
    prof = []
    for t in np.linspace(-0.88 * math.pi / 2 * 1.0, math.pi / 2, 60):
        prof.append((B * math.cos(t) * (1 - .1 * max(0, -math.sin(t))), cy - A * math.sin(t)))
    right = [(cx + x, y) for x, y in prof][::-1]
    left = [(cx - x, y) for x, y in prof]
    out = [poly(right + left)]
    for i, y in enumerate(np.linspace(cy - A + 50, cy + A * .82 - 30, 6)):
        t = math.asin(max(-1, min(1, (cy - y) / A)))
        hw = B * math.cos(t) - 14
        n = 4 if i % 2 == 0 else 3
        w_ = 2 * hw / n
        for k in range(n):
            x0 = cx - hw + k * w_
            out.append(line(smooth([(x0 + 4, y - 10), (x0 + w_ / 2, y + 14), (x0 + w_ - 4, y - 10)], 20), SW * .65))
    by = cy + A * .88 * 1.0
    mx = B * math.cos(-0.88 * math.pi / 2) * .9 - 2
    out.append(line([(cx - mx + k * 2 * mx / 8, by + (12 if k % 2 else 0)) for k in range(9)], SW * .7))
    for a in (-36, -12, 12, 36):
        r = math.radians(90 + a)
        out.append(line([(cx, by + 12), (cx + math.cos(r) * 110, by + 12 + math.sin(r) * 110)], SW * .55))
    return out


def testate_mouth():
    """Testate amoeba mouth end-on: ring of toothed plates. Symmetric."""
    c, R = 256, 200
    out = [circ(c, c, R)]
    n = 10
    for k in range(n):
        a = k / n * 2 * math.pi
        out.append(line([(c + 118 * math.cos(a), c + 118 * math.sin(a)), (c + 60 * math.cos(a), c + 60 * math.sin(a))], SW * .8))
        for ring, rr in ((0, 160),):
            b = (k + .5) / n * 2 * math.pi
            out.append(ell(c + rr * math.cos(b), c + rr * math.sin(b), 26, 16, math.degrees(b) + 90, SW * .7))
    out.append(circ(c, c, 118, SW * .8))
    teeth = [(c + (60 - (10 if j % 2 else 0)) * math.cos(j / 40 * 2 * math.pi), c + (60 - (10 if j % 2 else 0)) * math.sin(j / 40 * 2 * math.pi)) for j in range(40)]
    out.append(poly(teeth, SW * .7))
    return out


def arcella():
    """Arcella, top view: round domed shell with a round central mouth and a fine pore pattern."""
    c = 256
    out = [circ(c, c, 200), circ(c, c, 64), circ(c, c, 82, SW * .6)]
    for rr, n in ((120, 14), (160, 20)):
        for k in range(n):
            a = k / n * 2 * math.pi
            out.append(circ(c + rr * math.cos(a), c + rr * math.sin(a), 5, 0, fill=True))
    return out


def nematode():
    """Bacterial-feeding nematode: unsegmented body, open mouth, pharynx with a round basal bulb, pointed tail."""
    cl = smooth([(70, 150), (170, 110), (260, 180), (330, 300), (420, 350), (460, 330)], 200)
    cl = np.array(cl); t = np.gradient(cl, axis=0); t /= np.linalg.norm(t, axis=1)[:, None]; nn = np.c_[-t[:, 1], t[:, 0]]
    u = np.linspace(0, 1, len(cl))
    half = 22 * np.minimum(1, .55 + .45 * np.clip(u / .15, 0, 1) ** .6) * np.where(u > .85, np.clip((1 - u) / .15, 0.0, 1), 1)
    a, b = cl + nn * half[:, None], cl - nn * half[:, None]
    t0 = t[0]; h0 = half[0]
    cap = [tuple(cl[0] - nn[0] * h0 * math.sin(q) * -1 - t0 * h0 * math.cos(q)) for q in np.linspace(-math.pi / 2, math.pi / 2, 12)]
    out = [poly([tuple(p) for p in a] + [tuple(p) for p in b[::-1]] + cap)]
    k = int(len(cl) * .30)
    out.append(line([tuple(p) for p in cl[3:k - 4]], SW * .55))
    out.append(ell(cl[k][0], cl[k][1], 15, 11, math.degrees(math.atan2(t[k][1], t[k][0])), SW * .6))
    return out


def fungal_hypha():
    """Septate fungal hypha: even-width tube, cross walls, branches, rounded tips."""
    lines_ = [[(60, 380), (190, 300), (320, 250), (452, 152)], [(190, 300), (222, 170), (250, 96)], [(320, 250), (380, 330), (440, 380)]]
    tube = unary_union([LineString(l).buffer(26, 16) for l in lines_])
    out = [outline(tube)]
    for l in lines_:
        ls = LineString(l)
        for d in np.arange(70, ls.length - 40, 80):
            p = np.array(ls.interpolate(d).coords[0]); q = np.array(ls.interpolate(d + 1).coords[0])
            tt = (q - p) / np.linalg.norm(q - p); nn = np.array([-tt[1], tt[0]])
            if all(LineString(o).distance(Point(*p)) > 30 for o in lines_ if o is not l):
                out.append(line([tuple(p - nn * 20), tuple(p + nn * 20)], SW * .7))
    return out


def flagellate():
    """Bodo-type flagellate: bean-shaped cell, short front flagellum, long trailing flagellum."""
    body = smooth([(150, 210), (220, 160), (330, 170), (390, 230), (350, 300), (240, 310), (165, 270)], closed=True)
    out = [poly(body), circ(270, 240, 34, SW * .8), circ(270, 240, 11, 0, fill=True)]
    out.append(line(wave((158, 225), 200, 120, 14, 1.2)))
    out.append(line(smooth([(150, 244), (170, 340), (280, 390), (390, 372), (470, 404)])))
    return out


def naked_amoeba():
    """Lobose amoeba: lobed pseudopods, nucleus, contractile vacuole."""
    o = blob(256, 256, 120, [(-10, .6, .4), (70, .3, .32), (150, .38, .34), (230, .22, .4), (300, .3, .3)])
    return [poly(o), circ(240, 262, 40, SW * .8), circ(240, 262, 13, 0, fill=True), circ(170, 200, 20, SW * .7)]


def ciliate():
    """Colpoda: kidney shape, cilia all round, mouth notch on the concave side, macronucleus."""
    cx, cy, A, Bh = 256, 266, 170, 120
    th0 = 1.5 * math.pi - .28
    o = []
    for t in np.linspace(0, 2 * math.pi, 160, endpoint=False):
        x, y = A * math.cos(t), Bh * math.sin(t)
        d = (t - th0 + math.pi) % (2 * math.pi) - math.pi
        y += 40 * math.exp(-(d / .42) ** 2)
        o.append((cx + x, cy + y))
    out = [poly(o)]
    ring = np.array(o + o[:1]); seg = np.diff(ring, axis=0); L = np.hypot(*seg.T)
    for i in range(0, 160, 4):
        p = np.array(o[i]); tt = seg[i] / L[i]; nn = np.array([tt[1], -tt[0]])
        out.append(line([tuple(p + nn * 8), tuple(p + nn * 34 + tt * 8)], SW * .55))
    out.append(circ(cx + 20, cy + 14, 42, SW * .8))
    return out


def ciliate_cyst():
    """Resting cyst: thick double wall, rounded cell inside."""
    return [circ(256, 256, 190, SW * 1.4), circ(256, 256, 160, SW * .7),
            *([poly(blob(256, 256, 110, [(40, .1, .6), (200, .08, .6)]))]), circ(266, 256, 34, SW * .8)]


def bacteria():
    """Rods and cocci, about 1 µm cells, the commonest soil shapes."""
    def rod(x, y, L, w, a):
        r = math.radians(a); h = L / 2 - w / 2
        return outline(LineString([(x - h * math.cos(r), y - h * math.sin(r)), (x + h * math.cos(r), y + h * math.sin(r))]).buffer(w / 2, 16))
    return [rod(180, 170, 190, 72, -25), rod(330, 310, 190, 72, 35), rod(160, 360, 150, 64, 70),
            circ(370, 140, 38), circ(430, 206, 30)]


def actinobacteria():
    """Actinobacteria: very thin branching filaments ending in coiled spore chains."""
    out = [line([(60, 420), (300, 300), (440, 260)], SW), line([(180, 360), (230, 200)], SW), line([(320, 292), (360, 160)], SW)]
    for (x, y) in ((230, 200), (360, 160)):
        for k in range(5):
            out.append(circ(x + 18 * math.sin(k * 1.3), y - 26 - k * 26, 13, SW * .7))
    return out


def mite():
    """Oribatid mite, top view: front shield, rounded back shield, 8 jointed legs, two sensory hairs."""
    cx, cy = 256, 280
    out = [ell(cx, cy + 30, 120, 132), poly(smooth([(cx - 70, cy - 90), (cx - 40, cy - 170), (cx, cy - 190), (cx + 40, cy - 170), (cx + 70, cy - 90)]) + [(cx, cy - 80)])]
    for s in (-1, 1):
        for k, (ang, L) in enumerate([(-140, 64), (-170, 60), (165, 60), (135, 70)]):
            bx, by = cx + s * (60 if k < 2 else 110), cy - 100 + k * 40 + (0 if k < 2 else 60)
            a = math.radians(ang if s < 0 else 180 - ang)
            p1 = (bx + L * math.cos(a), by + L * math.sin(a))
            a2 = a + s * math.radians(-25 if k < 2 else 25)
            p2 = (p1[0] + L * math.cos(a2), p1[1] + L * math.sin(a2))
            out.append(line([(bx, by), p1, p2], SW * .8))
        out.append(line([(cx + s * 30, cy - 140), (cx + s * 70, cy - 200)], SW * .6))
        out.append(circ(cx + s * 74, cy - 206, 9, 0, fill=True))
    return out


def springtail():
    """Springtail, side view: antennae, 6 legs, ventral tube, spring folded under the body."""
    out = [ell(140, 230, 52, 44)]
    body = smooth([(180, 200), (280, 186), (380, 200), (450, 240), (440, 280), (330, 290), (200, 280), (176, 250)], closed=True)
    out.append(poly(body))
    out.append(line([(110, 196), (80, 140), (66, 80)], SW * .8))
    for x in (230, 280, 330, 380):
        out.append(line([(x, 192), (x + 4, 286)], SW * .45))
    out.append(circ(128, 216, 8, 0, fill=True))
    for x in (200, 240, 280):
        out.append(line([(x, 282), (x - 10, 330), (x + 6, 372)], SW * .8))
    out.append(line([(312, 288), (312, 322)], SW))
    out.append(line(smooth([(420, 286), (380, 320), (300, 336), (240, 330)]), SW * .8))
    return out


def root_tip():
    """Root tip: root cap at the end, root hairs a little way above it, no hairs at the very tip."""
    out = [poly(smooth([(220, 40), (226, 300), (236, 400), (256, 460), (276, 400), (286, 300), (292, 40)]) + [(256, 40)])]
    for k in range(3):
        out.append(line(smooth([(232 + k * 4, 440 - k * 26), (256, 452 - k * 26), (280 - k * 4, 440 - k * 26)]), SW * .6))
    for y in range(110, 300, 34):
        for s in (-1, 1):
            out.append(line([(256 + s * 34, y), (256 + s * 100, y - 26)], SW * .55))
    return out


def microscope():
    """Compound microscope: eyepiece, tube, objective, stage, arm, base, focus knob."""
    return [line([(160, 72), (226, 72)], SW * 1.3),                      # eyepiece
            line([(193, 80), (236, 250)], SW * 2.6),                      # tube
            line([(238, 258), (244, 296)], SW * 1.5),                     # objective
            line([(170, 322), (346, 322)], SW * 1.3),                     # stage
            line(smooth([(232, 150), (330, 170), (366, 280), (330, 400)]), SW * 2.0),   # arm
            line([(150, 440), (400, 440)], SW * 2.2),                     # base
            line([(330, 400), (310, 440)], SW * 2.0),
            circ(364, 270, 24, SW)]                                       # focus knob


ICONS = [("testate-amoeba", testate_amoeba), ("testate-amoeba-mouth", testate_mouth), ("arcella", arcella),
         ("nematode", nematode), ("fungal-hypha", fungal_hypha), ("flagellate", flagellate), ("naked-amoeba", naked_amoeba),
         ("ciliate", ciliate), ("ciliate-cyst", ciliate_cyst), ("bacteria", bacteria), ("actinobacteria", actinobacteria),
         ("oribatid-mite", mite), ("springtail", springtail), ("root-tip", root_tip), ("microscope", microscope)]


def svg_for(name, fn, colour):
    res = fn()
    head = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {S} {S}" width="{S}" height="{S}">'
    g = f'<g fill="none" stroke="{colour}" stroke-linecap="round" stroke-linejoin="round" color="{colour}">'
    if False:
        outer, inner, septa = res
        body = "".join(outer)
        # hollow tube: knock out the inside, then the cross walls
        mask = (f'<mask id="m"><rect width="{S}" height="{S}" fill="white"/><g fill="none" stroke="black" stroke-linecap="round" stroke-linejoin="round">'
                + "".join(inner) + '</g></mask>')
        walls = "".join(f'<line x1="{x - 12 * math.cos(math.radians(a + 90)):.1f}" y1="{y - 12 * math.sin(math.radians(a + 90)):.1f}" '
                        f'x2="{x + 12 * math.cos(math.radians(a + 90)):.1f}" y2="{y + 12 * math.sin(math.radians(a + 90)):.1f}" stroke-width="{SW * .8}"/>'
                        for x, y, a in septa)
        return head + "<defs>" + mask + "</defs>" + g + f'<g mask="url(#m)">{body}</g>' + walls + "</g></svg>\n"
    return head + g + "".join(res).replace('fill="currentColor"', f'fill="{colour}"') + "</g></svg>\n"


def main():
    sheet_cells = []
    for colour_name, hexc in COLOURS.items():
        d = os.path.join(HERE, colour_name); os.makedirs(d, exist_ok=True)
        for name, fn in ICONS:
            s = svg_for(name, fn, hexc)
            open(os.path.join(d, f"sfw-icon-{name}.svg"), "w").write(s)
            im = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=s.encode(), output_width=1024, output_height=1024)))
            im.save(os.path.join(d, f"sfw-icon-{name}.png"))
            if colour_name == "deep-green":
                sheet_cells.append((name, im))
    # preview: all icons large, plus a row at small sizes
    cols, cell = 5, 300
    rows = math.ceil(len(sheet_cells) / cols)
    sheet = Image.new("RGB", (cols * cell, rows * (cell + 40) + 140), "white")
    dr = ImageDraw.Draw(sheet)
    for k, (name, im) in enumerate(sheet_cells):
        x, y = (k % cols) * cell, (k // cols) * (cell + 40)
        t = im.resize((cell - 60, cell - 60), Image.LANCZOS); sheet.paste(t, (x + 30, y + 20), t)
        dr.text((x + 30, y + cell - 30), name, fill="#22371F")
    x = 20
    for name, im in sheet_cells:
        t = im.resize((48, 48), Image.LANCZOS); sheet.paste(t, (x, rows * (cell + 40) + 40), t); x += 62
    x = 20
    for name, im in sheet_cells:
        t = im.resize((24, 24), Image.LANCZOS); sheet.paste(t, (x, rows * (cell + 40) + 100), t); x += 62
    sheet.save(os.path.join(HERE, "icons-preview.png"))


if __name__ == "__main__":
    main()
