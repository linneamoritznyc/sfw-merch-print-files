import math, random, sys
from PIL import Image, ImageDraw, ImageFilter

SS = 2
W, H = 3600, 2000
PAL = {
    'terracotta': (196, 92, 62), 'rust': (150, 62, 44), 'ochre': (214, 160, 64),
    'rose': (214, 120, 118), 'teal': (40, 110, 118), 'teal_l': (128, 184, 182),
    'green': (70, 167, 112), 'deep': (34, 84, 58), 'lime': (150, 190, 70),
    'maroon': (82, 51, 51), 'purple': (104, 49, 140), 'lilac': (176, 150, 214),
    'navy': (26, 40, 78), 'sky': (150, 180, 220), 'white': (255, 255, 255),
}
def lighten(c, t): return tuple(int(v + (255 - v) * t) for v in c)
def darken(c, t): return tuple(int(v * (1 - t)) for v in c)

def blob(cx, cy, r, rnd, k=6, amp=0.18, n=90, sx=1, sy=1, rot=0):
    ph = [rnd.uniform(0, 6.28) for _ in range(k)]
    am = [rnd.uniform(0, amp) / (i + 1) ** 0.6 for i in range(k)]
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        rr = r * (1 + sum(am[j] * math.sin((j + 2) * a + ph[j]) for j in range(k)))
        x, y = rr * math.cos(a) * sx, rr * math.sin(a) * sy
        pts.append((cx + x * math.cos(rot) - y * math.sin(rot), cy + x * math.sin(rot) + y * math.cos(rot)))
    return pts

def inside(pts, x, y):
    c = False; j = len(pts) - 1
    for i in range(len(pts)):
        xi, yi = pts[i]; xj, yj = pts[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi + 1e-9) + xi: c = not c
        j = i
    return c

# ---------- organisms ----------
def heliozoan(d, cx, cy, r, rnd, col):
    for i in range(rnd.randint(70, 120)):
        a = rnd.uniform(0, 6.28); L = r * rnd.uniform(0.9, 1.0)
        w = max(1, int(r * 0.012))
        d.line([(cx + 0.45 * r * math.cos(a), cy + 0.45 * r * math.sin(a)),
                (cx + L * math.cos(a), cy + L * math.sin(a))], fill=lighten(col, 0.25), width=w)
        d.ellipse([cx + L * math.cos(a) - w, cy + L * math.sin(a) - w, cx + L * math.cos(a) + w, cy + L * math.sin(a) + w], fill=lighten(col, 0.25))
    d.polygon(blob(cx, cy, r * 0.5, rnd, amp=0.06), fill=col)
    for i in range(rnd.randint(14, 26)):
        a = rnd.uniform(0, 6.28); q = rnd.uniform(0, 0.38) * r; s = r * rnd.uniform(0.025, 0.06)
        d.ellipse([cx + q * math.cos(a) - s, cy + q * math.sin(a) - s, cx + q * math.cos(a) + s, cy + q * math.sin(a) + s], fill=darken(col, 0.25))

def testate(d, cx, cy, r, rnd, col):
    rot = rnd.uniform(0, 6.28)
    pts = blob(cx, cy, r, rnd, amp=0.08, sx=1, sy=rnd.uniform(0.65, 0.9), rot=rot)
    d.polygon(pts, fill=col)
    pc = lighten(col, 0.55); placed = []
    for _ in range(900):
        x, y = cx + rnd.uniform(-r, r), cy + rnd.uniform(-r, r)
        s = r * rnd.uniform(0.06, 0.13)
        if not inside(pts, x, y): continue
        if any(math.hypot(x - a, y - b) < s + t + r * 0.03 for a, b, t in placed): continue
        e = blob(x, y, s, rnd, amp=0.15, n=24)
        if all(inside(pts, px, py) for px, py in e[::3]):
            d.polygon(e, fill=pc); placed.append((x, y, s))

def ciliate(d, cx, cy, r, rnd, col):
    rot = rnd.uniform(0, 6.28); sy = rnd.uniform(0.38, 0.55)
    pts = blob(cx, cy, r, rnd, amp=0.06, n=160, sx=1, sy=sy, rot=rot)
    cc = lighten(col, 0.7); w = max(1, int(r * 0.022))
    for i, (x, y) in enumerate(pts):
        a = math.atan2(y - cy, x - cx) + rnd.uniform(-0.3, 0.3); L = r * rnd.uniform(0.12, 0.2)
        d.line([(x, y), (x + L * math.cos(a), y + L * math.sin(a))], fill=cc, width=w)
    d.polygon(pts, fill=col)
    for _ in range(rnd.randint(25, 45)):
        u, v = rnd.uniform(-0.8, 0.8), rnd.uniform(-0.7, 0.7) * sy
        x = cx + r * (u * math.cos(rot) - v * math.sin(rot)); y = cy + r * (u * math.sin(rot) + v * math.cos(rot))
        s = r * rnd.uniform(0.03, 0.06)
        d.ellipse([x - s, y - s, x + s, y + s], fill=darken(col, 0.22))

def pediastrum(d, cx, cy, r, rnd, col):
    rings = [(0, 1), (0.36, 6), (0.68, 12)]
    rot = rnd.uniform(0, 6.28); lc = lighten(col, 0.35)
    for rad, n in rings:
        for i in range(n):
            a = rot + 2 * math.pi * i / n
            x, y = cx + rad * r * math.cos(a), cy + rad * r * math.sin(a)
            s = r * (0.17 if rad < 0.7 else 0.19)
            if rad > 0.6:
                for h in (-0.32, 0.32):
                    hx, hy = x + s * 1.5 * math.cos(a + h), y + s * 1.5 * math.sin(a + h)
                    d.line([(x, y), (hx, hy)], fill=col, width=int(s * 0.38))
                    d.ellipse([hx - s * 0.2, hy - s * 0.2, hx + s * 0.2, hy + s * 0.2], fill=col)
            d.polygon(blob(x, y, s, rnd, amp=0.1, n=30), fill=col)
            d.ellipse([x - s * 0.3, y - s * 0.3, x + s * 0.3, y + s * 0.3], fill=lc)

def amoeba(d, cx, cy, r, rnd, col):
    r=r*0.72
    pts = blob(cx, cy, r, rnd, k=7, amp=0.5, n=200)
    d.polygon(pts, fill=col)
    d.polygon(blob(cx, cy, r * 0.62, rnd, k=5, amp=0.3, n=120), fill=lighten(col, 0.2))
    s = r * 0.13; ox, oy = rnd.uniform(-0.2, 0.2) * r, rnd.uniform(-0.2, 0.2) * r
    d.ellipse([cx + ox - s, cy + oy - s, cx + ox + s, cy + oy + s], fill=darken(col, 0.3))

def diatom(d, cx, cy, r, rnd, col):
    rot = rnd.uniform(0, 6.28); n = 120; w = rnd.uniform(0.16, 0.24)
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n; x = math.cos(t); y = w * math.sin(t) * (abs(math.sin(t)) ** 0.0) * (1 - 0.0)
        y = w * math.copysign(abs(math.sin(t)) ** 0.8, math.sin(t))
        pts.append((cx + r * (x * math.cos(rot) - y * math.sin(rot)), cy + r * (x * math.sin(rot) + y * math.cos(rot))))
    d.polygon(pts, fill=col)
    lc = lighten(col, 0.5)
    for k in range(-14, 15):
        u = k / 16; hw = w * (1 - u * u) ** 0.8 * 0.8
        a = (u, -hw); b = (u, hw)
        P = [(cx + r * (p[0] * math.cos(rot) - p[1] * math.sin(rot)), cy + r * (p[0] * math.sin(rot) + p[1] * math.cos(rot))) for p in (a, b)]
        d.line(P, fill=lc, width=max(1, int(r * 0.012)))
    a, b = (-0.9, 0), (0.9, 0)
    d.line([(cx + r * (p[0] * math.cos(rot)), cy + r * (p[0] * math.sin(rot))) for p in (a, b)], fill=darken(col, 0.2), width=max(2, int(r * 0.03)))

def nematode(d, cx, cy, r, rnd, col):
    a0 = rnd.uniform(0, 6.28); n = 140; L = r * 2.4; amp = r * 0.28; ph = rnd.uniform(0, 6)
    pts = []
    for i in range(n):
        t = i / (n - 1); s = (t - 0.5) * L
        off = amp * math.sin(t * 2 * math.pi * 1.3 + ph)
        x = s * math.cos(a0) - off * math.sin(a0); y = s * math.sin(a0) + off * math.cos(a0)
        pts.append((cx + x, cy + y, r * 0.11 * (math.sin(math.pi * t) ** 0.4)))
    for x, y, w in pts: d.ellipse([x - w, y - w, x + w, y + w], fill=col)
    for i in range(0, n, 6):
        x, y, w = pts[i]; s = w * 0.35
        d.ellipse([x - s, y - s, x + s, y + s], fill=lighten(col, 0.3))

def bacteria(d, cx, cy, r, rnd, col):
    base = rnd.uniform(0, 6.28); done = []
    for _ in range(60):
        if len(done) >= 6: break
        a = base + rnd.uniform(-0.5, 0.5); L = r * rnd.uniform(0.3, 0.45); w = r * 0.09
        x, y = cx + rnd.uniform(-0.55, 0.55) * r, cy + rnd.uniform(-0.55, 0.55) * r
        if any(math.hypot(x - p, y - q) < r * 0.32 for p, q in done): continue
        done.append((x, y))
        x2, y2 = x + L * math.cos(a), y + L * math.sin(a)
        d.line([(x, y), (x2, y2)], fill=col, width=int(2 * w))
        for p in ((x, y), (x2, y2)): d.ellipse([p[0] - w, p[1] - w, p[0] + w, p[1] + w], fill=col)

def vorticella(d, cx, cy, r, rnd, col):
    base = (cx + rnd.uniform(-0.2, 0.2) * r, cy + r * 0.95); lc = lighten(col, 0.45)
    for k in range(rnd.randint(2, 4)):
        tx, ty = cx + rnd.uniform(-0.6, 0.6) * r, cy - rnd.uniform(0.1, 0.6) * r
        n = 60; pts = []
        for i in range(n + 1):
            t = i / n; x = base[0] + (tx - base[0]) * t + r * 0.04 * math.sin(t * 40); y = base[1] + (ty - base[1]) * t
            pts.append((x, y))
        d.line(pts, fill=lc, width=max(2, int(r * 0.025)))
        bw = r * 0.26; ang = math.atan2(ty - base[1], tx - base[0])
        bell = []
        for i in range(30):
            t = i / 29; y = -1.35 * bw * t; x = bw * (0.14 + 0.86 * t ** 0.6)
            bell.append((-x, y))
        for i in range(12):
            u = -1 + 2 * i / 11; bell.append((u * bw, -1.35 * bw - 0.12 * bw * (1 - u * u)))
        for i in range(29, -1, -1):
            t = i / 29; y = -1.35 * bw * t; x = bw * (0.14 + 0.86 * t ** 0.6)
            bell.append((x, y))
        rot = ang + math.pi / 2
        P = [(tx + p[0] * math.cos(rot) - p[1] * math.sin(rot), ty + p[0] * math.sin(rot) + p[1] * math.cos(rot)) for p in bell]
        d.polygon(P, fill=col)
        for j in range(5):
            s2 = r * 0.03; u = rnd.uniform(-0.5, 0.5) * bw; v = -rnd.uniform(0.2, 0.8) * bw
            x = tx + u * math.cos(rot) - v * math.sin(rot); y = ty + u * math.sin(rot) + v * math.cos(rot)
            d.ellipse([x - s2, y - s2, x + s2, y + s2], fill=lighten(col, 0.35))

def radiolarian(d, cx, cy, r, rnd, col):
    n = rnd.choice([6, 8, 10, 12]); lc = lighten(col, 0.6)
    for i in range(n):
        a = 2 * math.pi * i / n; L = r
        d.line([(cx, cy), (cx + L * math.cos(a), cy + L * math.sin(a))], fill=col, width=max(2, int(r * 0.05)))
        tx, ty = cx + L * math.cos(a), cy + L * math.sin(a); s = r * 0.08
        d.ellipse([tx - s, ty - s, tx + s, ty + s], fill=col)
    d.ellipse([cx - r * .62, cy - r * .62, cx + r * .62, cy + r * .62], fill=col)
    for ring, m in ((0.45, 14), (0.22, 7)):
        for i in range(m):
            a = 2 * math.pi * (i + 0.5 * ring) / m; s = r * 0.075
            x, y = cx + ring * r * math.cos(a), cy + ring * r * math.sin(a)
            d.ellipse([x - s, y - s, x + s, y + s], fill=lc)

KINDS = [
    (heliozoan, ['terracotta', 'rust', 'ochre', 'purple', 'maroon']),
    (testate, ['maroon', 'rust', 'teal', 'ochre', 'navy']),
    (ciliate, ['terracotta', 'teal', 'rose', 'purple', 'green']),
    (pediastrum, ['green', 'lime', 'deep']),
    (amoeba, ['rose', 'lilac', 'teal_l', 'sky']),
    (diatom, ['ochre', 'teal', 'deep', 'navy']),
    (nematode, ['maroon', 'ochre', 'rust', 'deep']),
    (bacteria, ['terracotta', 'purple', 'teal', 'green']),
    (vorticella, ['purple', 'navy', 'teal', 'green']),
]

def sheet(seed, out, pal_filter=None, bg=(255, 255, 255), density=1.0, logo=None):
    rnd = random.Random(seed)
    im = Image.new('RGB', (W * SS, H * SS), bg); d = ImageDraw.Draw(im)
    placed = []
    sizes = sorted([60 + 260 * rnd.random() ** 2.2 for i in range(int(150 * density))], reverse=True)
    rs = [s for s in sizes]
    for i, r in enumerate(rs):
        for _ in range(1500):
            x, y = rnd.uniform(r * 0.6, W - r * 0.6), rnd.uniform(r * 0.6, H - r * 0.6)
            if logo and math.hypot(x - logo[0], y - logo[1]) < logo[2] + r: continue
            if all(math.hypot(x - a, y - b) > (r + q) * 0.95 + 26 for a, b, q in placed):
                placed.append((x, y, r)); break
    kinds = KINDS[:]
    for i, (x, y, r) in enumerate(placed):
        fn, cols = kinds[i % len(kinds)] if i < len(kinds) else rnd.choice(kinds)
        if pal_filter: cols = [c for c in cols if c in pal_filter] or [rnd.choice(pal_filter)]
        col = PAL[rnd.choice(cols)]
        rr = r * (0.55 if fn is nematode else 0.9)
        fn(d, x * SS, y * SS, rr * SS, rnd, col)
    im = im.resize((W, H), Image.LANCZOS)
    im.save(out)
    return im

if __name__ == '__main__':
    sheet(int(sys.argv[1]) if len(sys.argv) > 1 else 3, '/tmp/proto.png')
