import math, random, collections, sys

def grow(seed, S=3000, R=1330, cell=5, pb=0.075):
    """Same growth as the regrown sticker (myc_rand), returns walker polylines with widths."""
    rnd = random.Random(seed); c = S / 2; Rp = R
    gs = int(S / cell) + 2; occ = [[-1] * gs for _ in range(gs)]
    q = collections.deque(); bid = 0
    for k in range(9):
        a = k / 9 * 2 * math.pi + rnd.uniform(-.15, .15); q.append((c, c, a, 9.0, bid)); bid += 1
    strokes = []; tips = []
    while q:
        x, y, a, w, b = q.popleft()
        lim = Rp * max(0.62, 1 - abs(rnd.gauss(0, 0.09))); steps = 0
        pts = [(x, y, w, math.hypot(x - c, y - c) / Rp)]
        while True:
            out = math.atan2(y - c, x - c); da = (out - a + math.pi) % (2 * math.pi) - math.pi
            a += da * 0.06 + rnd.gauss(0, 0.2)
            nx = x + math.cos(a) * 8; ny = y + math.sin(a) * 8
            r = math.hypot(nx - c, ny - c)
            if r > lim: tips.append((x, y, True)); break
            gx, gy = int(nx / cell), int(ny / cell); o = occ[gy][gx]
            if o != -1 and o != b and steps > 3 and r > Rp * 0.12: tips.append((x, y, False)); break
            occ[gy][gx] = b
            x, y = nx, ny; steps += 1; w = max(1.5, w * 0.997)
            pts.append((x, y, w, r / Rp))
            if rnd.random() < pb and bid < 200000:
                q.append((x, y, a + rnd.choice([-1, 1]) * rnd.uniform(0.4, 1.0), max(1.5, w * 0.7), bid)); bid += 1; w *= 0.9
        if len(pts) > 1: strokes.append(pts)
    dots = []
    for x, y, end in tips:
        if rnd.random() < 0.30: dots.append((x, y, rnd.uniform(1.5, 2.25)))
    return strokes, dots

def mix(a, b, t): return '#%02x%02x%02x' % tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3))

def svg(strokes, dots, ink, trunk=None, bg=None, S=3000):
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {S} {S}" width="{S}" height="{S}">']
    if bg: out.append(f'<circle cx="{S/2}" cy="{S/2}" r="{S/2}" fill="{bg}"/>')
    out.append('<g fill="none" stroke-linecap="round" stroke-linejoin="round">')
    for pts in strokes:
        # split each walker into chunks of similar width and colour
        i = 0
        while i < len(pts) - 1:
            j = i + 1; w0 = pts[i][2]
            while j < len(pts) - 1 and abs(pts[j][2] - w0) < 0.35 and j - i < 60: j += 1
            seg = pts[i:j + 1]; t = min(1, seg[0][3])
            col = mix(trunk, ink, t) if trunk else mix(ink, ink, 0)
            d = 'M' + ' '.join(f'{p[0]:.1f},{p[1]:.1f}' for p in seg)
            out.append(f'<path d="{d}" stroke="{col}" stroke-width="{w0:.2f}"/>')
            i = j
    out.append('</g>')
    out.append(f'<g fill="{mix(ink, ink, 0)}">' + ''.join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}"/>' for x, y, r in dots) + '</g>')
    out.append('</svg>')
    return '\n'.join(out)

if __name__ == '__main__':
    GREEN_BG = '#0c3418'; INK = (196, 232, 206); TRUNK = (160, 214, 180)
    WHITE = (255, 255, 255); GREEN = (70, 167, 112)
    for n, seed in enumerate((21, 34, 5), 1):
        s, d = grow(seed)
        open(f'SFW-mycelium-circle-{n}-on-green.svg', 'w').write(svg(s, d, INK, TRUNK, GREEN_BG))
        open(f'SFW-mycelium-circle-{n}-white.svg', 'w').write(svg(s, d, WHITE))
        open(f'SFW-mycelium-circle-{n}-green.svg', 'w').write(svg(s, d, GREEN))
