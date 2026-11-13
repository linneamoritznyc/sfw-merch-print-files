import math, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
sys.path.insert(0, '/home/claude/merch/brand')
import cute
Image.MAX_IMAGE_PIXELS = None
B = '/home/claude/merch/brand/'
S = 1000
DEEP = (30, 62, 46); NAVY = (26, 40, 78); VIOLET = (154, 138, 210); WHITE = (250, 250, 248)
GREEN = (70, 167, 112); MAROON = (82, 51, 51); PURPLE = (104, 49, 140)

lg = Image.open('/home/claude/merch/logos/SFW-logo-flower-colour.png').convert('RGBA')
lg = lg.crop(lg.getbbox())

def fabric(col, seed=0, weave=True):
    rnd = np.random.default_rng(seed)
    a = np.ones((S, S, 3), np.float32) * np.array(col, np.float32)
    n = rnd.normal(0, 4, (S, S, 1)).astype(np.float32)
    if weave:
        yy, xx = np.mgrid[0:S, 0:S]
        n += (((xx // 3 + yy // 3) % 2) * 3 - 1.5)[..., None]
    return Image.fromarray(np.clip(a + n, 0, 255).astype(np.uint8))

def satin(mask, col, angle=35, pitch=5, seed=1):
    """thread look: fine parallel stitches with sheen, inside a mask (L image)."""
    w, h = mask.size
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    a = math.radians(angle)
    u = xx * math.cos(a) + yy * math.sin(a)
    ph = (u % pitch) / pitch
    shade = 0.82 + 0.3 * np.sin(ph * math.pi)
    v = -xx * math.sin(a) + yy * math.cos(a)
    brk = ((v + (np.floor(u / pitch) * 37) % 23) % 23 < 0.9)  # stitch ends
    shade = shade - brk * 0.18
    c = np.array(col, np.float32)[None, None, :] * shade[..., None]
    c = np.clip(c + 255 * 0.06 * (shade[..., None] - 0.9), 0, 255)
    img = Image.fromarray(c.astype(np.uint8))
    return img, mask

def place(base, img, mask, xy, shadow=True):
    if shadow:
        sh = Image.new('L', base.size, 0); sh.paste(mask, (xy[0] + 3, xy[1] + 4))
        sh = sh.filter(ImageFilter.GaussianBlur(4))
        dark = Image.new('RGB', base.size, (0, 0, 0))
        base.paste(dark, (0, 0), sh.point(lambda p: int(p * 0.35)))
    base.paste(img, xy, mask)

def logo_layers(size, simplify=True):
    """split colour logo into its 3 inks, thickened for stitching."""
    l = lg.resize((size, int(size * lg.height / lg.width)), Image.LANCZOS)
    a = np.asarray(l).astype(np.int32); al = a[..., 3] > 110
    rgb = a[..., :3]
    cols = {'green': GREEN, 'maroon': MAROON, 'purple': PURPLE}
    out = {}
    for k, c in cols.items():
        dd = np.abs(rgb - np.array(c)).sum(-1)
        m = al & (dd < 120)
        out[k] = m
    if simplify:
        h = a.shape[0]
        # drop the small FOUNDATION word: green pixels in the band under the wordmark, right half
        g = out['green']; ys, xs = np.where(g)
        band = (np.arange(h)[:, None] > h * 0.60) & (np.arange(h)[:, None] < h * 0.71) & (np.arange(a.shape[1])[None, :] > a.shape[1] * 0.45)
        out['green'] = g & ~band
        for k in out:
            im = Image.fromarray((out[k] * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5 if k != 'green' else 3))
            out[k] = np.asarray(im) > 127
    return {k: Image.fromarray((v * 255).astype(np.uint8)) for k, v in out.items()}, l.size

# ---------- A: embroidered left chest logo on deep green ----------
def panel_embroidery(bg=DEEP, inks=None, size=560, title=None):
    base = fabric(bg, 1)
    layers, (w, h) = logo_layers(size)
    xy = ((S - w) // 2, (S - h) // 2)
    ang = {'green': 35, 'maroon': -40, 'purple': 80}
    inks = inks or {'green': GREEN, 'maroon': (190, 150, 140) if bg == DEEP else MAROON, 'purple': (176, 140, 220)}
    for k in ('green', 'maroon', 'purple'):
        img, m = satin(layers[k], inks[k], angle=ang[k], pitch=5)
        place(base, img, m, xy)
    return base

# ---------- B: one-ink screen print, white logo on violet ----------
def panel_oneink(bg=VIOLET, ink=WHITE, size=620):
    base = fabric(bg, 2)
    l = lg.resize((size, int(size * lg.height / lg.width)), Image.LANCZOS)
    m = l.split()[3].point(lambda p: 255 if p > 110 else 0)
    rnd = np.random.default_rng(3)
    tex = (rnd.random((m.size[1], m.size[0])) > 0.06).astype(np.uint8) * 255   # ink speckle
    m = ImageChops.multiply(m, Image.fromarray(tex).filter(ImageFilter.GaussianBlur(0.6)).point(lambda p: 255 if p > 90 else 0))
    inkimg = Image.new('RGB', m.size, ink)
    base.paste(inkimg, ((S - m.size[0]) // 2, (S - m.size[1]) // 2), m)
    return base

# ---------- C: round embroidered patch ----------
def panel_patch(bg=NAVY, patch=DEEP, rim=GREEN):
    base = fabric(bg, 4)
    R = 360; c = S // 2
    m = Image.new('L', (S, S), 0); ImageDraw.Draw(m).ellipse([c - R, c - R, c + R, c + R], fill=255)
    tw = fabric(patch, 5, weave=True)
    sh = m.filter(ImageFilter.GaussianBlur(8)).point(lambda p: int(p * 0.45))
    base.paste((0, 0, 0), (6, 8), sh) if False else None
    shadow = Image.new('L', (S, S), 0); shadow.paste(sh, (6, 9))
    base.paste(Image.new('RGB', (S, S), (0, 0, 0)), (0, 0), shadow)
    base.paste(tw, (0, 0), m)
    # merrowed rim: radial satin
    yy, xx = np.mgrid[0:S, 0:S]; rr = np.hypot(xx - c, yy - c); th = np.arctan2(yy - c, xx - c)
    ring = (rr > R - 26) & (rr <= R)
    sheen = 0.8 + 0.3 * np.sin((th * 260) % (2 * math.pi))
    rc = np.clip(np.array(rim)[None, None, :] * sheen[..., None], 0, 255).astype(np.uint8)
    base.paste(Image.fromarray(rc), (0, 0), Image.fromarray((ring * 255).astype(np.uint8)))
    layers, (w, h) = logo_layers(480)
    allm = ImageChops.lighter(ImageChops.lighter(layers['green'], layers['maroon']), layers['purple'])
    img, mm = satin(allm, (246, 246, 240), angle=30, pitch=5)
    place(base, img, mm, ((S - w) // 2, (S - h) // 2 + 10))
    return base

# ---------- D: single-ink halftone micrograph ----------
def panel_halftone(bg=WHITE, ink=NAVY):
    base = fabric(bg, 6)
    p = Image.open(B + 'SFW-panorama-micro-3-24x10.png').convert('L')
    p = p.crop((1600, 0, 1600 + 3000, 3000)).resize((760, 760), Image.LANCZOS)
    m = p.point(lambda v: 255 if v < 140 else 0)
    base.paste(Image.new('RGB', m.size, ink), (120, 120), m)
    return base

# ---------- E: two-ink print: big Pediastrum + EB Garamond ----------
def panel_twoink(bg=NAVY):
    base = fabric(bg, 7)
    lay = Image.new('RGB', (S * 2, S * 2), (0, 0, 0)); d = ImageDraw.Draw(lay)
    rnd = random.Random(2)
    cute.pediastrum(d, S, S * 0.86, 640, rnd, (255, 255, 255), (0, 0, 0))
    m = lay.convert('L').resize((S, S), Image.LANCZOS)
    # pediastrum: ink 1 green; inner dots knock out to fabric
    g = np.asarray(m) > 200; inner = (np.asarray(m) > 60) & ~g
    base_a = np.asarray(base).copy()
    base_a[g] = GREEN
    base = Image.fromarray(base_a)
    d2 = ImageDraw.Draw(base)
    f = ImageFont.truetype(B + 'ebg500.ttf', 64)
    t = 'SOIL  FOOD  WEB'
    tw = d2.textlength(t, font=f); d2.text(((S - tw) / 2, 850), t, font=f, fill=WHITE)
    return base

# ---------- F: tiny embroidered creatures, sleeve/hem accents ----------
def panel_tiny(bg=WHITE):
    base = fabric(bg, 8)
    rnd = random.Random(9)
    items = [(cute.paramecium, (300, 380), 170, (232, 120, 150), (120, 60, 160)),
             (cute.pediastrum, (660, 330), 150, GREEN, GREEN),
             (cute.amoeba, (330, 690), 160, (120, 170, 230), PURPLE),
             (cute.euglena, (690, 690), 170, (232, 172, 60), MAROON)]
    for fn, (x, y), r, col, acc in items:
        lay = Image.new('RGBA', (S * 2, S * 2), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        fn(d, x * 2, y * 2, r * 2, rnd, col, acc)
        lay = lay.resize((S, S), Image.LANCZOS)
        rgb = lay.convert('RGB'); m = lay.split()[3].point(lambda p: 255 if p > 120 else 0)
        st, _ = satin(m, (128, 128, 128), angle=rnd.choice([30, -35, 60]), pitch=4)
        tex = ImageChops.multiply(rgb, st.point(lambda p: min(255, int(p * 1.9))))
        place(base, tex, m, (0, 0))
    return base

def board():
    P = [panel_embroidery(), panel_oneink(), panel_patch(), panel_halftone(), panel_twoink(), panel_tiny()]
    g = 30; W = 3 * S + 4 * g; H = 2 * S + 3 * g
    c = Image.new('RGB', (W, H), (232, 232, 232))
    for i, p in enumerate(P):
        c.paste(p, (g + (i % 3) * (S + g), g + (i // 3) * (S + g)))
    return c

if __name__ == '__main__':
    b = board(); b.save(B + 'SFW-stitch-print-explore.png')
    b.resize((b.width // 2, b.height // 2), Image.LANCZOS).save(B + 'SFW-stitch-print-explore.jpg', quality=90)
