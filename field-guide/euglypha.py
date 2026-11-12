"""SFW Field Guide, page 1: Euglypha (testate amoeba). A4 portrait, all vector, text converted to outlines.

The drawing is SFW's own, constructed in code and checked against:
  - Leidy, Fresh-water Rhizopods of North America (1879), plate XXXV, Euglypha alveolata
  - modern light-microscope photos: protisten.de, Euglypha tuberculata and E. filifera
Anatomy shown: test of overlapping oval silica scales (idiosomes); ring of toothed apertural scales;
filose pseudopods (filopodia); nucleus with nucleolus at the fundus; contractile vacuoles; food vacuoles.
DRAFT until an SFW mentor has checked it.

Usage: python3 euglypha.py   ->  out/euglypha-field-guide.svg / .png / -preview.png, out/euglypha-icon.svg
"""
import io, math, os
import numpy as np
import cairosvg, uharfbuzz as hb
from PIL import Image
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
FONTS = os.path.join(HERE, "fonts")
W, H = 2480, 3508                               # A4 at 300 dpi
DEEP, FWG, LIGHT, WHITE = "#22371F", "#156826", "#59A66C", "#FFFFFF"
LW = 3.2                                        # base line weight


# ------------------------------------------------------------------ text to outlines
_cache = {}


def font(name):
    if name not in _cache:
        path = os.path.join(FONTS, name)
        tt = TTFont(path); tt.flavor = None
        buf = io.BytesIO(); tt.save(buf)
        _cache[name] = (TTFont(io.BytesIO(buf.getvalue())), hb.Font(hb.Face(hb.Blob(buf.getvalue()))))
    return _cache[name]


def text(s, size, x, y, fnt="eb-garamond-latin-400-normal.woff2", anchor="start", color=DEEP, track=0):
    tt, hf = font(fnt)
    upem = tt["head"].unitsPerEm
    b = hb.Buffer(); b.add_str(s); b.guess_segment_properties(); hb.shape(hf, b, {"kern": True, "liga": True})
    gs = tt.getGlyphSet(); order = tt.getGlyphOrder(); sc = size / upem
    pen_x, parts = 0, []
    pos = []
    for info, p in zip(b.glyph_infos, b.glyph_positions):
        pos.append((order[info.codepoint], pen_x + p.x_offset)); pen_x += p.x_advance + track / 1000 * upem
    w = (pen_x - track / 1000 * upem) * sc
    x0 = x - (w / 2 if anchor == "middle" else w if anchor == "end" else 0)
    for g, gx in pos:
        sp = SVGPathPen(gs); gs[g].draw(TransformPen(sp, (sc, 0, 0, -sc, x0 + gx * sc, y))); parts.append(sp.getCommands())
    return f'<path fill="{color}" d="{" ".join(parts)}"/>', w


def para(lines, size, x, y, lead=1.32, **kw):
    out = []
    for i, l in enumerate(lines):
        out.append(text(l, size, x, y + i * size * lead, **kw)[0])
    return "".join(out), y + (len(lines) - 1) * size * lead


def d_of(pts, close=False):
    return "M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + ("Z" if close else "")


# ------------------------------------------------------------------ the shell (test)
A, B = 1.0, 0.50                     # half-length, max radius (units of half-length)
ZAP = -0.86                          # aperture end (z = -1 would be the tip)


def radius(z):
    """Shell profile: ovoid, a little narrower toward the aperture, open at ZAP."""
    r = B * math.sqrt(max(0.0, 1 - z * z))
    return r * (1 - 0.16 * (1 - (z + 1) / 2) ** 2)


def surface(z, phi):
    r = radius(z)
    return np.array([r * math.cos(phi), r * math.sin(phi), z])


def scale_outline(z0, phi0, dz, dphi, n=28):
    pts = []
    for t in np.linspace(0, 2 * math.pi, n, endpoint=False):
        p = surface(z0 + dz * math.sin(t), phi0 + dphi * math.cos(t))
        pts.append(p)
    return np.array(pts)


def project(p, cx, cy, s):
    """View from the front (+y toward the viewer), fundus up."""
    return np.c_[cx + p[:, 0] * s, cy - p[:, 2] * s]


def profile(cx, cy, s, inset=0.0, n=160):
    zs = np.linspace(ZAP, 0.999, n)
    right = [(cx + (radius(z) - inset) * s, cy - z * s) for z in zs]
    left = [(cx - (radius(z) - inset) * s, cy - z * s) for z in zs[::-1]]
    return right + left


def apertural_ring_front(cx, cy, s, n=10, w=LW):
    """Toothed apertural scales seen from the side: the front half of the ring at the mouth."""
    out = []
    z0 = ZAP
    r0 = radius(z0)
    for k in range(n):
        phi = (k + 0.5) / n * 2 * math.pi
        if math.sin(phi) <= 0.05:
            continue
        x = cx + r0 * math.cos(phi) * s
        half = r0 * (math.pi / n) * s * abs(math.sin(phi)) ** 0.6 * 0.95
        top, bot = cy - (z0 + 0.045) * s, cy - (z0 - 0.03) * s
        teeth = 4
        pts = [(x - half, top), (x + half, top), (x + half, bot)]
        for j in range(teeth * 2, -1, -1):
            tx = x - half + j / (teeth * 2) * 2 * half
            pts.append((tx, bot + (0.022 * s if j % 2 else 0)))
        pts.append((x - half, bot))
        out.append(f'<path d="{d_of(pts, True)}" fill="{WHITE}" stroke="{DEEP}" stroke-width="{w * .9:.2f}" stroke-linejoin="round"/>')
    return "".join(out)


def shell_surface(cx, cy, s):
    """Drawing A: focus on the upper surface. Overlapping scales like shingles."""
    out = [f'<path d="{d_of(profile(cx, cy, s), True)}" fill="{WHITE}" stroke="{DEEP}" stroke-width="{LW * 1.6:.2f}"/>']
    rows = 15
    zs = np.linspace(0.93, ZAP + 0.09, rows)
    dz = (zs[0] - zs[1]) * 0.78
    for i, z in enumerate(zs):                 # from the fundus down: lower rows overlap upper ones
        r = radius(z)
        n = max(5, int(round(2 * math.pi * r / (dz * 1.55))))
        dphi = math.pi / n * 1.12
        off = (i % 2) * math.pi / n
        for k in range(n):
            phi = off + k * 2 * math.pi / n
            if math.sin(phi) < -0.05:
                continue
            o = scale_outline(z, phi, dz, dphi)
            vis = o[:, 1] > -0.02
            if vis.mean() < 0.5:
                continue
            P = project(o, cx, cy, s)
            out.append(f'<path d="{d_of(P, True)}" fill="{WHITE}" stroke="{DEEP}" stroke-width="{LW:.2f}" stroke-linejoin="round"/>')
    out.append(apertural_ring_front(cx, cy, s))
    clip = f'<clipPath id="shellclip"><path d="{d_of(profile(cx, cy, s, inset=-0.004), True)}"/></clipPath>'
    body = "".join(out[1:])
    return clip + out[0] + f'<g clip-path="url(#shellclip)">{body}</g>' + \
        f'<path d="{d_of(profile(cx, cy, s), True)}" fill="none" stroke="{DEEP}" stroke-width="{LW * 1.6:.2f}"/>'


def optical_section(cx, cy, s, rng):
    """Drawing B: focus through the middle of a living cell. Returns svg and label anchor points."""
    out, pts = [], {}
    # shell wall: scales cut edge-on, a beaded double line of overlapping lenses
    prof = np.array(profile(cx, cy, s))
    half = len(prof) // 2
    for side in (prof,):                          # one closed run: right side, over the fundus, left side
        seg = np.array(side)
        d = np.r_[0, np.cumsum(np.hypot(*np.diff(seg, axis=0).T))]
        step = 0.105 * s
        for k, t0 in enumerate(np.arange(0, d[-1] - step * .4, step * .82)):
            a = np.array([np.interp(t0, d, seg[:, 0]), np.interp(t0, d, seg[:, 1])])
            b = np.array([np.interp(min(t0 + step, d[-1]), d, seg[:, 0]), np.interp(min(t0 + step, d[-1]), d, seg[:, 1])])
            m = (a + b) / 2; v = b - a; L = np.linalg.norm(v)
            if L < 1: continue
            n_ = np.array([-v[1], v[0]]) / L * (0.012 * s) * (1 if k % 2 else -1)
            lens = [a, m + n_ * 1.6, b, m - n_ * 0.4]
            out.append(f'<path d="M{a[0]:.1f},{a[1]:.1f}Q{(m + n_ * 3)[0]:.1f},{(m + n_ * 3)[1]:.1f} {b[0]:.1f},{b[1]:.1f}'
                       f'Q{(m - n_)[0]:.1f},{(m - n_)[1]:.1f} {a[0]:.1f},{a[1]:.1f}Z" fill="{WHITE}" stroke="{DEEP}" stroke-width="{LW * .9:.2f}"/>')
    pts["shell"] = (cx + radius(0.25) * s, cy - 0.25 * s)
    # cytoplasm: fills most of the shell, narrows into the mouth
    cyto = []
    for z in np.linspace(ZAP + 0.02, 0.999, 120):
        cyto.append((cx + (radius(z) * 0.86 + 0.0) * s, cy - (z - 0.04) * s))
    for z in np.linspace(0.999, ZAP + 0.02, 120):
        cyto.append((cx - (radius(z) * 0.86) * s, cy - (z - 0.04) * s))
    out.insert(0, f'<path d="{d_of(cyto, True)}" fill="{LIGHT}" stroke="{FWG}" stroke-width="{LW:.2f}"/>')
    pts["cytoplasm"] = (cx - radius(-0.25) * 0.55 * s, cy + 0.25 * s)
    # filopodia: fine, straight, pointed, a few branched
    yap = cy - ZAP * s
    fil = []
    for k, ang in enumerate(np.linspace(-62, 62, 7)):
        a = math.radians(90 + ang + rng.normal(0, 4))
        L = s * rng.uniform(0.42, 0.58)
        x0 = cx + math.cos(a) * 0.05 * s
        e = (x0 + math.cos(a) * L, yap + math.sin(a) * L)
        fil.append(f'<path d="M{x0 - 5:.1f},{yap:.1f}L{e[0]:.1f},{e[1]:.1f}L{x0 + 5:.1f},{yap:.1f}Z" fill="{FWG}"/>')
        if k in (1, 4):
            f = 0.55
            bx, by = x0 + math.cos(a) * L * f, yap + math.sin(a) * L * f
            a2 = a + (0.35 if k == 1 else -0.35)
            e2 = (bx + math.cos(a2) * L * .4, by + math.sin(a2) * L * .4)
            fil.append(f'<path d="M{bx - 3:.1f},{by:.1f}L{e2[0]:.1f},{e2[1]:.1f}L{bx + 3:.1f},{by:.1f}Z" fill="{FWG}"/>')
    out.insert(0, "".join(fil))
    pts["filopodia"] = (cx + math.cos(math.radians(90 - 62)) * 0.40 * s, yap + math.sin(math.radians(90 - 62)) * 0.40 * s)
    # nucleus at the fundus, with nucleolus
    nx, ny, nr = cx, cy - 0.58 * s, 0.17 * s
    out.append(f'<circle cx="{nx:.1f}" cy="{ny:.1f}" r="{nr:.1f}" fill="{WHITE}" stroke="{DEEP}" stroke-width="{LW * 1.3:.2f}"/>')
    out.append(f'<circle cx="{nx:.1f}" cy="{ny:.1f}" r="{nr * .42:.1f}" fill="{DEEP}"/>')
    pts["nucleus"] = (nx + nr, ny)
    # contractile vacuoles, one each side
    for sx in (-1, 1):
        vx, vy = cx + sx * 0.25 * s, cy - 0.18 * s
        out.append(f'<circle cx="{vx:.1f}" cy="{vy:.1f}" r="{0.065 * s:.1f}" fill="{WHITE}" stroke="{FWG}" stroke-width="{LW:.2f}"/>')
    pts["cv"] = (cx + 0.25 * s + 0.065 * s, cy - 0.18 * s)
    # food vacuoles with bacteria inside
    fv = [(-0.12, -0.28, .075), (0.14, -0.42, .06), (-0.04, -0.55, .055), (0.06, 0.02, .05)]
    for fx, fz, fr in fv:
        x, y = cx + fx * s, cy - fz * s
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{fr * s:.1f}" fill="{FWG}"/>')
        for _ in range(3):
            a = rng.uniform(0.2, 1.2); bx, by = x + rng.uniform(-.3, .3) * fr * s, y + rng.uniform(-.3, .3) * fr * s
            L = fr * s * .45
            out.append(f'<path d="M{bx - math.cos(a) * L / 2:.1f},{by - math.sin(a) * L / 2:.1f}L{bx + math.cos(a) * L / 2:.1f},{by + math.sin(a) * L / 2:.1f}" stroke="{WHITE}" stroke-width="{max(5, fr * s * .16):.1f}" stroke-linecap="round"/>')
    pts["food"] = (cx - 0.12 * s - 0.075 * s, cy + 0.28 * s)
    out.append(apertural_ring_front(cx, cy, s))
    pts["mouth"] = (cx + radius(ZAP) * s, cy - ZAP * s)
    return "".join(out), pts


def aperture_view(cx, cy, R, n=10, w=LW):
    """Drawing C: the mouth seen end-on. Ring of n toothed apertural scales, body scales behind. Symmetric."""
    out = [f'<circle cx="{cx}" cy="{cy}" r="{R:.1f}" fill="{WHITE}" stroke="{DEEP}" stroke-width="{w * 1.6:.2f}"/>']
    # body scales seen end-on, two rings
    for ring, (rr, m, sc) in enumerate([(0.83, 2 * n, 0.15), (0.64, 2 * n, 0.13)]):
        for k in range(m):
            a = (k + 0.5 * ring) / m * 2 * math.pi
            x, y = cx + rr * R * math.cos(a), cy + rr * R * math.sin(a)
            out.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{sc * R:.1f}" ry="{sc * R * .62:.1f}" '
                       f'transform="rotate({math.degrees(a) + 90:.1f} {x:.1f} {y:.1f})" fill="{WHITE}" stroke="{DEEP}" stroke-width="{w:.2f}"/>')
    # apertural plates: each a rounded plate with 4 teeth pointing into the mouth
    ro, ri = 0.50 * R, 0.24 * R
    for k in range(n):
        a0, a1 = (k - 0.47) / n * 2 * math.pi, (k + 0.47) / n * 2 * math.pi
        pts = [(cx + ro * math.cos(t), cy + ro * math.sin(t)) for t in np.linspace(a0, a1, 14)]
        teeth = 4
        for j in range(teeth * 2, -1, -1):
            t = a0 + j / (teeth * 2) * (a1 - a0)
            r = ri - (0.045 * R if j % 2 else 0)
            pts.append((cx + r * math.cos(t), cy + r * math.sin(t)))
        out.append(f'<path d="{d_of(pts, True)}" fill="{WHITE}" stroke="{DEEP}" stroke-width="{w:.2f}" stroke-linejoin="round"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{ri * 0.62:.1f}" fill="{LIGHT}"/>')
    return "".join(out)


def one_scale(cx, cy, L):
    """Drawing D: a single oval silica scale, thickened rim."""
    return (f'<ellipse cx="{cx}" cy="{cy}" rx="{L * .36:.1f}" ry="{L / 2:.1f}" fill="{WHITE}" stroke="{DEEP}" stroke-width="{LW * 1.6:.2f}"/>'
            f'<ellipse cx="{cx}" cy="{cy}" rx="{L * .30:.1f}" ry="{L / 2 - L * .06:.1f}" fill="none" stroke="{DEEP}" stroke-width="{LW * .8:.2f}"/>')


def label(anchor, tx, ty, lines, side="right", size=40):
    ax, ay = anchor
    lx = tx - 16 if side == "right" else tx + 16
    s = f'<path d="M{ax:.1f},{ay:.1f}L{lx:.1f},{ty - size * .32:.1f}" stroke="{DEEP}" stroke-width="2.5" fill="none"/>'
    s += f'<circle cx="{ax:.1f}" cy="{ay:.1f}" r="6" fill="{DEEP}"/>'
    for i, l in enumerate(lines):
        s += text(l, size, tx, ty + i * size * 1.2, anchor="start" if side == "right" else "end")[0]
    return s


def page():
    rng = np.random.default_rng(7)
    M = 170
    body = [f'<rect width="{W}" height="{H}" fill="{WHITE}"/>']
    # header
    body.append(text("SOIL FOOD WEB FIELD GUIDE", 34, M, 230, fnt="eb-garamond-latin-600-normal.woff2", track=180, color=FWG)[0])
    body.append(text("No. 1", 34, W - M, 230, fnt="eb-garamond-latin-600-normal.woff2", anchor="end", track=120, color=FWG)[0])
    body.append(text("Euglypha", 190, M - 6, 420, fnt="eb-garamond-latin-400-italic.woff2")[0])
    body.append(text("A shelled amoeba that builds its house from glass", 58, M, 560)[0])
    body.append(text("Testate amoeba  ·  Rhizaria  ·  Cercozoa  ·  Euglyphida", 40, M, 630, color=FWG)[0])
    # drawings A and B
    s = 580
    ax, bx, cy0 = 820, 1660, 1330
    body.append(shell_surface(ax, cy0, s))
    bsvg, pts = optical_section(bx, cy0, s, rng)
    body.append(bsvg)
    body.append(text("A  Shell surface", 40, ax, cy0 + s * 1.56, anchor="middle", fnt="eb-garamond-latin-600-normal.woff2")[0])
    body.append(text("B  Living cell, mid focus", 40, bx, cy0 + s * 1.56, anchor="middle", fnt="eb-garamond-latin-600-normal.woff2")[0])
    # labels
    L = [label((ax - radius(0.45) * s + 40, cy0 - 0.45 * s), ax - 0.62 * s, cy0 - 0.72 * s, ["Shell of", "overlapping", "silica scales"], side="left"),
         label((ax - radius(ZAP) * s + 12, cy0 - ZAP * s + 4), ax - 0.62 * s, cy0 + 0.60 * s, ["Toothed scales", "around the mouth"], side="left"),
         label(pts["nucleus"], W - M - 250, cy0 - 0.90 * s, ["Nucleus"]),
         label(pts["cv"], W - M - 250, cy0 - 0.62 * s, ["Contractile", "vacuole"]),
         label(pts["shell"], W - M - 250, cy0 - 0.12 * s, ["Shell wall,", "scales edge-on"]),
         label((bx + 0.13 * s, cy0 + 0.42 * s), W - M - 250, cy0 + 0.30 * s, ["Food vacuole"]),
         label(pts["filopodia"], W - M - 250, cy0 + 1.16 * s, ["Fine, pointed", "pseudopods"])]
    body += L
    # scale bar: this drawing shows a shell about 60 µm long (2 * s = 60 µm)
    um = 2 * s / 60
    sbx, sby = ax - 10 * um, cy0 + 1.22 * s
    body.append(f'<rect x="{sbx:.1f}" y="{sby:.1f}" width="{20 * um:.1f}" height="10" fill="{DEEP}"/>')
    body.append(text("20 µm", 34, ax, sby - 18, anchor="middle")[0])
    # row 2: drawings C and D
    y2 = 2620
    body.append(aperture_view(M + 250, y2, 230))
    body.append(text("C  The mouth, end-on", 40, M + 250, y2 + 320, anchor="middle", fnt="eb-garamond-latin-600-normal.woff2")[0])
    body.append(one_scale(M + 680, y2, 300))
    body.append(text("D  One scale", 40, M + 680, y2 + 320, anchor="middle", fnt="eb-garamond-latin-600-normal.woff2")[0])
    # facts
    fx, fy, fs = 1180, y2 - 250, 38
    facts = [("Size", ["Shell about 30 to 100 µm long,", "depending on the species."]),
             ("Where", ["Moist soil, leaf litter and moss."]),
             ("Eats", ["Bacteria, fungi and small algae,", "caught with fine pointed pseudopods."]),
             ("Shell", ["Silica scales the cell makes itself.", "It stores a full new set before it divides."]),
             ("At 400x", ["A clear, glassy shell. Focus on the surface", "for the scale pattern, then on the middle", "for the cell. Look for the toothed mouth."])]
    y = fy
    for head, lines in facts:
        body.append(text(head, fs, fx, y, fnt="eb-garamond-latin-600-normal.woff2", color=FWG)[0])
        t, yl = para(lines, fs, fx + 220, y)
        body.append(t); y = yl + fs * 1.75
    # footer
    body.append(f'<rect x="{M}" y="{H - 290}" width="{W - 2 * M}" height="3" fill="{LIGHT}"/>')
    body.append(text("Drawn by the Soil Food Web Foundation. Checked against Leidy (1879), plate XXXV, and modern light-microscope photos.", 30, M, H - 220, color=DEEP)[0])
    body.append(text("Draft. To be checked by an SFW mentor before publishing.", 30, M, H - 175, color=FWG)[0])
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n' + "\n".join(body) + "\n</svg>\n"


def icon():
    S = 1000
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {S} {S}">'
            + aperture_view(S / 2, S / 2, S * 0.46, w=7) + "</svg>\n")


def main():
    os.makedirs(OUT, exist_ok=True)
    svg = page()
    open(os.path.join(OUT, "euglypha-field-guide.svg"), "w").write(svg)
    png = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(), output_width=W, output_height=H))).convert("RGB")
    png.save(os.path.join(OUT, "euglypha-field-guide.png"), dpi=(300, 300), optimize=True)
    # the page is full-size text; logo goes bottom right
    logo = Image.open(os.path.join(HERE, "..", "creative-code", "logos", "SFW-logo-flower-colour.png")).convert("RGBA")
    logo.thumbnail((230, 230))
    png = png.convert("RGBA"); png.alpha_composite(logo, (W - 170 - logo.width, H - 270 - logo.height + 120))
    png.convert("RGB").save(os.path.join(OUT, "euglypha-field-guide.png"), dpi=(300, 300), optimize=True)
    pv = png.convert("RGB"); pv.thumbnail((1240, 1754)); pv.save(os.path.join(OUT, "euglypha-field-guide-preview.png"))
    open(os.path.join(OUT, "euglypha-icon.svg"), "w").write(icon())


if __name__ == "__main__":
    main()
