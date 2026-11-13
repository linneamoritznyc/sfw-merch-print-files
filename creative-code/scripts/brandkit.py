import math, random, collections, os
OUT = '/home/claude/myc/brandkit'; os.makedirs(OUT, exist_ok=True)
COLS = {'white': '#ffffff', 'green': '#46a770', 'darkgreen': '#1e3e2e'}

def walk(W, H, starts, bias, ok, rnd, step=7, cell=5, pb=0.07, wmin=1.2, decay=0.996, turn=0.2, pull=0.07, maxw=8):
    gs_x, gs_y = int(W / cell) + 2, int(H / cell) + 2
    occ = {}
    q = collections.deque((x, y, a, w, i) for i, (x, y, a, w) in enumerate(starts)); bid = len(starts)
    strokes, tips = [], []
    while q:
        x, y, a, w, b = q.popleft(); pts = [(x, y, w)]; steps = 0
        while True:
            ta = bias(x, y, a)
            da = (ta - a + math.pi) % (2 * math.pi) - math.pi
            a += da * pull + rnd.gauss(0, turn)
            nx, ny = x + math.cos(a) * step, y + math.sin(a) * step
            if not ok(nx, ny, rnd): tips.append((x, y)); break
            k = (int(nx / cell), int(ny / cell)); o = occ.get(k)
            if o is not None and o != b and steps > 3: tips.append((x, y)); break
            occ[k] = b; x, y = nx, ny; steps += 1; w = max(wmin, w * decay); pts.append((x, y, w))
            if rnd.random() < pb and bid < 60000:
                q.append((x, y, a + rnd.choice([-1, 1]) * rnd.uniform(0.4, 1.0), max(wmin, w * 0.7), bid)); bid += 1; w *= 0.9
        if len(pts) > 1: strokes.append(pts)
    dots = [(x, y, rnd.uniform(1.4, 2.4)) for x, y in tips if rnd.random() < 0.3]
    return strokes, dots

def paths(strokes, col):
    o = []
    for pts in strokes:
        i = 0
        while i < len(pts) - 1:
            j = i + 1; w0 = pts[i][2]
            while j < len(pts) - 1 and abs(pts[j][2] - w0) < 0.35 and j - i < 60: j += 1
            o.append(f'<path d="M{" ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in pts[i:j+1])}" stroke="{col}" stroke-width="{w0:.2f}"/>')
            i = j
    return o

def write(name, W, H, strokes=(), dots=(), extra=lambda col: []):
    for cn, col in COLS.items():
        o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
             '<g fill="none" stroke-linecap="round" stroke-linejoin="round">'] + paths(strokes, col) + ['</g>']
        o.append(f'<g fill="{col}">' + ''.join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}"/>' for x, y, r in dots) + '</g>')
        o += extra(col); o.append('</svg>')
        open(f'{OUT}/SFW-{name}-{cn}.svg', 'w').write('\n'.join(o))

# 1. divider
def divider(seed=1):
    W, H = 3000, 260; rnd = random.Random(seed)
    starts = [(1500, 130, 0, 6), (1500, 130, math.pi, 6)]
    s, d = walk(W, H, starts, lambda x, y, a: 0 if math.cos(a) > 0 else math.pi,
                lambda x, y, r: 20 < x < W - 20 and abs(y - 130) < 110 * (1 - abs(x - 1500) / 1700) + 12, rnd, pb=0.09, pull=0.12)
    write('divider', W, H, s, d)

# 2. corner growth
def corner(seed=2):
    W = H = 2000; rnd = random.Random(seed)
    starts = [(4, 4, math.pi / 4 + rnd.uniform(-.5, .5), 8) for _ in range(5)]
    s, d = walk(W, H, starts, lambda x, y, a: math.atan2(y, x),
                lambda x, y, r: x > 0 and y > 0 and math.hypot(x, y) < 1700 * (1 - abs(rnd.gauss(0, 0.08))), rnd, pb=0.075)
    write('corner', W, H, s, d)

# 3. root fringe hanging from the top edge
def fringe(seed=3):
    W, H = 3000, 900; rnd = random.Random(seed)
    starts = [(x, 2, math.pi / 2 + rnd.uniform(-.2, .2), rnd.uniform(4, 7)) for x in range(60, W, 140)]
    lim = {}
    def ok(x, y, r):
        k = int(x // 140); lim.setdefault(k, rnd.uniform(380, 860))
        return 0 < x < W and 0 < y < lim[k]
    s, d = walk(W, H, starts, lambda x, y, a: math.pi / 2, ok, rnd, pb=0.05, pull=0.05)
    write('root-fringe', W, H, s, d)

# 4. soil horizon bands (filled)
def horizon(seed=4):
    W, H = 3000, 900; rnd = random.Random(seed)
    def band(y0, amp):
        ph = [rnd.uniform(0, 6) for _ in range(4)]
        pts = [(x, y0 + amp * sum(math.sin(x / W * math.pi * (k + 2) + ph[k]) / (k + 1) for k in range(4))) for x in range(0, W + 1, 20)]
        return 'M0,%d ' % H + ' '.join(f'L{x},{y:.1f}' for x, y in pts) + f' L{W},{H} Z'
    bands = [band(140, 40), band(330, 55), band(530, 60), band(720, 50)]
    ops = [0.25, 0.45, 0.7, 1.0]
    write('horizon-bands', W, H, extra=lambda col: [f'<path d="{b}" fill="{col}" fill-opacity="{o}"/>' for b, o in zip(bands, ops)])

# 5. spore scatter
def spores(seed=5):
    W, H = 2400, 1400; rnd = random.Random(seed); el = []
    def extra(col):
        rr = random.Random(seed); o = []
        for _ in range(140):
            x = rr.gauss(W / 2, W / 4.5); y = rr.gauss(H / 2, H / 4.5); r = rr.choice([4, 6, 9, 14, 22, 34]) * rr.uniform(0.8, 1.2)
            if rr.random() < 0.25 and r > 14:
                o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="none" stroke="{col}" stroke-width="{max(2, r/7):.1f}"/>')
                o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r*0.3:.1f}" fill="{col}"/>')
            else:
                o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{col}"/>')
        return o
    write('spore-scatter', W, H, extra=extra)

# 6. mycelium numeral: growth radiating from a big EB Garamond figure
def numeral(ch='1', seed=6):
    from fontTools.ttLib import TTFont
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.recordingPen import DecomposingRecordingPen
    from PIL import Image, ImageDraw, ImageFont
    W = H = 2400; rnd = random.Random(seed)
    fpath = '/home/claude/merch/brand/ebg500.ttf'
    f = TTFont(fpath); gs = f.getGlyphSet(); gname = f.getBestCmap()[ord(ch)]
    upm = f['head'].unitsPerEm; scale = 1500 / upm
    pen = SVGPathPen(gs); gs[gname].draw(pen)
    adv = gs[gname].width * scale
    tx, ty = (W - adv) / 2, H / 2 + 1500 * 0.35
    glyph = lambda col: [f'<path transform="translate({tx:.1f},{ty:.1f}) scale({scale:.4f},{-scale:.4f})" d="{pen.getCommands()}" fill="{col}"/>']
    # mask to find the glyph edge
    m = Image.new('L', (W, H), 0); dd = ImageDraw.Draw(m)
    fnt = ImageFont.truetype(fpath, 1500); bb = dd.textbbox((0, 0), ch, font=fnt)
    # place mask using the same metrics: draw via font at baseline ty
    dd.text((tx, ty), ch, font=fnt, fill=255, anchor='ls')
    px = m.load(); starts = []
    for _ in range(4000):
        x, y = rnd.uniform(0, W), rnd.uniform(0, H)
        if px[int(x), int(y)] and not px[min(W - 1, int(x + 12)), int(y)] or (px[int(x), int(y)] and not px[max(0, int(x - 12)), int(y)]):
            a = 0 if px[max(0, int(x - 12)), int(y)] else math.pi
            starts.append((x, y, a + rnd.uniform(-.6, .6), 4))
        if len(starts) > 70: break
    cx, cy = W / 2, H / 2
    s, d = walk(W, H, starts, lambda x, y, a: math.atan2(y - cy, x - cx),
                lambda x, y, r: 0 < x < W and 0 < y < H and not px[int(x), int(y)] and math.hypot(x - cx, y - cy) < 1150 * (1 - abs(rnd.gauss(0, 0.1))), rnd, pb=0.06)
    write(f'numeral-{ch}', W, H, s, d, extra=glyph)

if __name__ == '__main__':
    divider(); corner(); fringe(); horizon(); spores(); numeral('1')
