import math, random, sys
from PIL import Image, ImageDraw

SS = 2
PAL = {
    'green': (70, 167, 112), 'lime': (160, 200, 70), 'mint': (150, 220, 180),
    'purple': (120, 60, 160), 'lilac': (186, 160, 226), 'pink': (232, 120, 150),
    'coral': (236, 110, 80), 'ochre': (232, 172, 60), 'yellow': (246, 212, 90),
    'teal': (40, 140, 150), 'sky': (120, 170, 230), 'maroon': (120, 50, 60),
    'white': (255, 255, 255),
}
def L(c, t): return tuple(int(v + (255 - v) * t) for v in c)
def D(c, t): return tuple(int(v * (1 - t)) for v in c)
def pick(rnd, avoid=()):
    return rnd.choice([k for k in PAL if k not in avoid and k != 'white'])

def tf(cx, cy, rot, pts):
    c, s = math.cos(rot), math.sin(rot)
    return [(cx + x * c - y * s, cy + x * s + y * c) for x, y in pts]

def blob(r, rnd, k=5, amp=0.15, n=120, sx=1, sy=1):
    ph = [rnd.uniform(0, 6.28) for _ in range(k)]
    am = [rnd.uniform(0, amp) / (i + 1) ** 0.7 for i in range(k)]
    out = []
    for i in range(n):
        a = 2 * math.pi * i / n
        rr = r * (1 + sum(am[j] * math.sin((j + 2) * a + ph[j]) for j in range(k)))
        out.append((rr * math.cos(a) * sx, rr * math.sin(a) * sy))
    return out

def scale(pts, f): return [(x * f, y * f) for x, y in pts]

def capsule(w, h, n=80):
    # rounded rod centred at 0, length w, width h
    r = h / 2; pts = []
    for i in range(n // 2 + 1):
        a = -math.pi / 2 + math.pi * i / (n // 2); pts.append((w / 2 - r + r * math.cos(a), r * math.sin(a)))
    for i in range(n // 2 + 1):
        a = math.pi / 2 + math.pi * i / (n // 2); pts.append((-w / 2 + r + r * math.cos(a), r * math.sin(a)))
    return pts

def dot(d, x, y, s, col): d.ellipse([x - s, y - s, x + s, y + s], fill=col)

def wave(d, pts, col, w):
    d.line(pts, fill=col, width=int(w), joint='curve')
    dot(d, *pts[0], w / 2, col); dot(d, *pts[-1], w / 2, col)

def tail(cx, cy, rot, x0, length, amp, waves, n=40):
    pts = []
    for i in range(n):
        t = i / (n - 1); x = x0 + t * length; y = amp * math.sin(t * waves * 2 * math.pi) * (0.4 + 0.6 * t)
        pts.append((x, y))
    return tf(cx, cy, rot, pts)

# ---------------- organisms ----------------
def bacillus(d, cx, cy, r, rnd, col, acc):
    rot = rnd.uniform(0, 6.28); w, h = 1.9 * r, 0.7 * r
    if rnd.random() < 0.6:
        for k in (-0.2, 0, 0.2):
            wave(d, tail(cx, cy, rot + k * 0.6, w / 2 - h * 0.2, r * 0.9, r * 0.08, 2.2), L(col, 0.35), r * 0.035)
    d.polygon(tf(cx, cy, rot, capsule(w, h)), fill=col)
    d.polygon(tf(cx, cy, rot, capsule(w - h * 0.28, h * 0.72)), fill=L(col, 0.35))
    pts = [(-w * 0.28 + w * 0.56 * i / 30, h * 0.12 * math.sin(i / 30 * 6.28 * 2.5)) for i in range(31)]
    wave(d, tf(cx, cy, rot, pts), acc, r * 0.07)

def paramecium(d, cx, cy, r, rnd, col, acc):
    rot = rnd.uniform(0, 6.28)
    body = []
    for i in range(140):
        a = 2 * math.pi * i / 140
        x = r * math.cos(a); y = r * 0.48 * math.sin(a) * (1 + 0.18 * math.cos(a)) - r * 0.08 * math.cos(2 * a) * (math.sin(a) > 0)
        body.append((x, y))
    cc = L(col, 0.55)
    for i in range(0, 140, 2):
        x, y = body[i]; a = math.atan2(y / 0.5, x); Lc = r * 0.14
        p = tf(cx, cy, rot, [(x, y), (x + Lc * math.cos(a), y + Lc * math.sin(a))])
        d.line(p, fill=cc, width=max(2, int(r * 0.03)))
    d.polygon(tf(cx, cy, rot, body), fill=col)
    d.polygon(tf(cx, cy, rot, scale(body, 0.84)), fill=L(col, 0.3))
    nx, ny = tf(cx, cy, rot, [(r * 0.05, -r * 0.02)])[0]
    d.polygon(tf(nx, ny, rot, blob(r * 0.2, rnd, amp=0.1, sx=1.3, sy=0.9)), fill=acc)
    dot(d, nx, ny, r * 0.06, L(acc, 0.5))
    for _ in range(4):
        u, v = rnd.uniform(-0.7, 0.7) * r, rnd.uniform(-0.25, 0.25) * r
        if abs(u) < r * 0.3: continue
        x, y = tf(cx, cy, rot, [(u, v)])[0]; dot(d, x, y, r * rnd.uniform(0.06, 0.09), D(col, 0.15))

def amoeba(d, cx, cy, r, rnd, col, acc):
    b = blob(r * 0.8, rnd, k=4, amp=0.32, n=160)
    d.polygon(tf(cx, cy, 0, b), fill=col)
    d.polygon(tf(cx, cy, 0, scale(b, 0.8)), fill=L(col, 0.32))
    dot(d, cx, cy, r * 0.2, acc); dot(d, cx, cy, r * 0.08, L(acc, 0.55))
    for _ in range(4):
        a = rnd.uniform(0, 6.28); q = r * rnd.uniform(0.3, 0.45)
        dot(d, cx + q * math.cos(a), cy + q * math.sin(a), r * rnd.uniform(0.05, 0.09), L(col, 0.7))

def sunny(d, cx, cy, r, rnd, col, acc):
    n = rnd.choice([34, 40, 46]); sc = L(col, 0.45)
    for i in range(n):
        a = 2 * math.pi * i / n
        p = [(cx + r * 0.5 * math.cos(a), cy + r * 0.5 * math.sin(a)), (cx + r * 0.95 * math.cos(a), cy + r * 0.95 * math.sin(a))]
        d.line(p, fill=sc, width=max(2, int(r * 0.022)))
    dot(d, cx, cy, r * 0.58, col); dot(d, cx, cy, r * 0.46, L(col, 0.3))
    for i in range(6):
        a = 2 * math.pi * i / 6 + 0.3; dot(d, cx + r * 0.27 * math.cos(a), cy + r * 0.27 * math.sin(a), r * 0.08, acc)
    dot(d, cx, cy, r * 0.11, D(col, 0.15))

def pediastrum(d, cx, cy, r, rnd, col, acc):
    rot = rnd.uniform(0, 6.28); lc = L(col, 0.4)
    for rad, n in ((0, 1), (0.36, 6), (0.68, 12)):
        for i in range(n):
            a = rot + 2 * math.pi * i / n; x, y = cx + rad * r * math.cos(a), cy + rad * r * math.sin(a)
            s = r * 0.18
            if rad > 0.6:
                for hh in (-0.32, 0.32):
                    hx, hy = x + s * 1.45 * math.cos(a + hh), y + s * 1.45 * math.sin(a + hh)
                    d.line([(x, y), (hx, hy)], fill=col, width=int(s * 0.42)); dot(d, hx, hy, s * 0.22, col)
            dot(d, x, y, s, col); dot(d, x, y, s * 0.42, lc)

def testate(d, cx, cy, r, rnd, col, acc):
    b = blob(r * 0.85, rnd, k=3, amp=0.06, n=100, sy=rnd.uniform(0.8, 0.95))
    rot = rnd.uniform(0, 6.28)
    d.polygon(tf(cx, cy, rot, b), fill=col)
    pc = L(col, 0.6); placed = []
    for _ in range(600):
        u, v = rnd.uniform(-0.7, 0.7) * r, rnd.uniform(-0.65, 0.65) * r
        if u * u + v * v > (0.68 * r) ** 2: continue
        s = r * rnd.uniform(0.07, 0.12)
        if any(math.hypot(u - a, v - b2) < s + t + r * 0.05 for a, b2, t in placed): continue
        placed.append((u, v, s)); x, y = tf(cx, cy, rot, [(u, v)])[0]; dot(d, x, y, s, pc)

def euglena(d, cx, cy, r, rnd, col, acc):
    rot = rnd.uniform(0, 6.28); body = []
    for i in range(120):
        a = 2 * math.pi * i / 120; x = r * 0.85 * math.cos(a)
        w = 0.36 * r * math.sin(a) * (1 - 0.55 * (math.cos(a) + 1) / 2)
        body.append((x, w))
    wave(d, tail(cx, cy, rot + math.pi, r * 0.8, r * 1.1, r * 0.12, 1.8), L(col, 0.4), r * 0.04)
    d.polygon(tf(cx, cy, rot, body), fill=col)
    d.polygon(tf(cx, cy, rot, scale(body, 0.78)), fill=L(col, 0.3))
    for i in range(5):
        x, y = tf(cx, cy, rot, [(r * (0.35 - 0.16 * i), r * 0.04 * (-1) ** i)])[0]; dot(d, x, y, r * 0.075, D(col, 0.1))
    x, y = tf(cx, cy, rot, [(-r * 0.58, 0)])[0]; dot(d, x, y, r * 0.07, (220, 60, 60))

def spirillum(d, cx, cy, r, rnd, col, acc):
    rot = rnd.uniform(0, 6.28)
    pts = tf(cx, cy, rot, [(-r + 2 * r * i / 50, r * 0.3 * math.sin(i / 50 * 2 * math.pi * 1.5)) for i in range(51)])
    wave(d, pts, col, r * 0.26); wave(d, pts, L(col, 0.35), r * 0.1)

def cocci(d, cx, cy, r, rnd, col, acc):
    pts = [(0, 0)]
    for _ in range(300):
        if len(pts) >= 9: break
        bx, by = rnd.choice(pts); a = rnd.uniform(0, 6.28); x, y = bx + 0.36 * r * math.cos(a), by + 0.36 * r * math.sin(a)
        if x * x + y * y > (0.65 * r) ** 2: continue
        if all(math.hypot(x - p, y - q) > 0.34 * r for p, q in pts): pts.append((x, y))
    for x, y in pts:
        dot(d, cx + x, cy + y, r * 0.18, col); dot(d, cx + x - r * 0.05, cy + y - r * 0.05, r * 0.06, L(col, 0.5))

def chain(d, cx, cy, r, rnd, col, acc):
    rot = rnd.uniform(0, 6.28); n = rnd.randint(5, 7)
    for i in range(n):
        t = i / (n - 1); x, y = tf(cx, cy, rot, [(-r * 0.85 + 1.7 * r * t, r * 0.25 * math.sin(t * 3.5))])[0]
        dot(d, x, y, r * 0.15, col); dot(d, x, y, r * 0.06, L(col, 0.5))

KINDS = [(bacillus, 0.9), (paramecium, 1.0), (amoeba, 1.0), (sunny, 0.95), (pediastrum, 0.9),
         (testate, 0.85), (euglena, 1.0), (spirillum, 0.8), (cocci, 0.7), (chain, 0.75)]

def tile(seed, T=2400, bg=(30, 62, 46), n=70, avoid=('maroon',), out=None, big=1.0):
    rnd = random.Random(seed)
    im = Image.new('RGB', (T * SS, T * SS), bg); d = ImageDraw.Draw(im)
    sizes = sorted([(95 + 120 * rnd.random() ** 1.5) * big for _ in range(n)], reverse=True)
    placed = []
    def tdist(a, b):
        dx = abs(a[0] - b[0]); dy = abs(a[1] - b[1]); dx = min(dx, T - dx); dy = min(dy, T - dy); return math.hypot(dx, dy)
    for r in sizes:
        for _ in range(2500):
            p = (rnd.uniform(0, T), rnd.uniform(0, T))
            if all(tdist(p, (x, y)) > (r + q) * 1.02 + 30 * big for x, y, q in placed):
                placed.append((p[0], p[1], r)); break
    order = list(range(len(KINDS))); rnd.shuffle(order)
    for i, (x, y, r) in enumerate(placed):
        fn, f = KINDS[order[i % len(order)]]
        col = PAL[pick(rnd, avoid)]; acc = PAL[pick(rnd, avoid + tuple(k for k, v in PAL.items() if v == col))]
        state = rnd.getstate()
        for ox in (-T, 0, T):
            for oy in (-T, 0, T):
                if (x + ox < -r * 1.6 or x + ox > T + r * 1.6 or y + oy < -r * 1.6 or y + oy > T + r * 1.6): continue
                rnd.setstate(state)
                fn(d, (x + ox) * SS, (y + oy) * SS, r * f * SS, rnd, col, acc)
    im = im.resize((T, T), Image.LANCZOS)
    if out: im.save(out)
    return im

if __name__ == '__main__':
    tile(int(sys.argv[1]) if len(sys.argv) > 1 else 1, out='/tmp/cute.png')
