import sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy.ndimage import gaussian_filter, zoom
from scipy.spatial import Delaunay
sys.path.insert(0, '/home/claude/merch/brand')
from dtgtees import tone, tee, src, sw, sh, B, ICC
from skimage import measure

S = 3600
GREEN = (70, 167, 112); PURPLE = (104, 49, 140); NAVY = (26, 40, 78); LIME = (178, 214, 72)
LAV = (186, 160, 226); MAROON = (82, 51, 51); DEEP = (30, 62, 46)

box = (int(sw * 0.36), 0, int(sw * 0.36) + sh, sh)        # square crop of the cluster
T0 = tone(box, 900, 900)                                   # low-res field; we smooth it into curves

def field(sig):
    f = gaussian_filter(T0, sig)
    return zoom(f, S * 2 / 900, order=3)                    # smooth bicubic to 2x print size

def finish(rgba2x):
    im = Image.fromarray(rgba2x, 'RGBA').resize((S, S), Image.LANCZOS)
    a = np.asarray(im.split()[3]); im.putalpha(Image.fromarray(np.where(a > 127, 255, 0).astype(np.uint8)))
    return im

# A. liquid layers: nested smooth blobs, flat brand colours
def liquid():
    f = field(3.2); out = np.zeros(f.shape + (4,), np.uint8)
    for lv, col in ((0.10, LAV), (0.22, PURPLE), (0.36, GREEN), (0.52, NAVY)):
        out[f > lv] = col + (255,)
    return finish(out)

# B. gradient bloom: one smooth silhouette filled with a sweeping gradient
def bloom():
    f = field(2.6); m = f > 0.14
    H2 = f.shape[0]; yy, xx = np.mgrid[0:H2, 0:H2] / H2
    g = np.clip((xx * 0.55 + yy * 0.45), 0, 1)[..., None]
    stops = [(0, np.array(LIME)), (0.45, np.array(GREEN)), (0.75, np.array(PURPLE)), (1, np.array(NAVY))]
    rgb = np.zeros((H2, H2, 3))
    for (a, ca), (b, cb) in zip(stops, stops[1:]):
        k = (g >= a) & (g <= b); u = (g - a) / (b - a)
        rgb = np.where(k, ca + (cb - ca) * u, rgb)
    inner = f > 0.42                     # dense cores in solid navy for depth
    rgb[inner] = NAVY
    out = np.dstack([rgb.astype(np.uint8), (m * 255).astype(np.uint8)])
    return finish(out)

# C. cubist facets: triangulated, each facet flat-filled by the tone under it
def facets():
    rnd = np.random.default_rng(7)
    f = gaussian_filter(T0, 1.2)
    pts = [(0, 0), (899, 0), (0, 899), (899, 899)]
    while len(pts) < 2600:
        x, y = rnd.uniform(0, 899, 2)
        if rnd.random() < 0.15 + 0.85 * f[int(y), int(x)]: pts.append((x, y))
    pts = np.array(pts); tri = Delaunay(pts)
    pal = [None, LAV, PURPLE, GREEN, NAVY]
    im = Image.new('RGBA', (S * 2, S * 2), (0, 0, 0, 0)); d = ImageDraw.Draw(im); k = S * 2 / 899
    for s in tri.simplices:
        p = pts[s]; c = p.mean(0); v = f[int(c[1]), int(c[0])]
        i = 0 if v < 0.08 else 1 if v < 0.2 else 2 if v < 0.35 else 3 if v < 0.55 else 4
        if i: d.polygon([(x * k, y * k) for x, y in p], fill=pal[i] + (255,))
    return finish(np.asarray(im))

# D. topographic: many smooth contour lines, one colour, weight grows with depth
def topo():
    f = field(4.0)
    im = Image.new('RGBA', (S * 2, S * 2), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for i, lv in enumerate(np.linspace(0.05, 0.6, 16)):
        for c in measure.find_contours(f, lv):
            if len(c) < 30: continue
            d.line([(x, y) for y, x in c[::2]], fill=PURPLE + (255,), width=int(6 + i * 1.2), joint='curve')
    return finish(np.asarray(im))

if __name__ == '__main__':
    designs = [('liquid', liquid(), (250, 250, 248)), ('bloom', bloom(), (250, 250, 248)),
               ('facets', facets(), (250, 250, 248)), ('topo', topo(), (250, 250, 248))]
    mocks = []
    for nm, P, sh_ in designs:
        P.save(B + f'SFW-abstract-{nm}.png', icc_profile=ICC, dpi=(300, 300))
        mocks.append(tee(P, sh_))
        q = Image.new('RGBA', P.size, sh_ + (255,)); q.alpha_composite(P)
        q.convert('RGB').crop((1200, 1200, 2400, 2400)).save(B + f'SFW-abstract-{nm}-detail.jpg', quality=92)
    row = Image.new('RGB', (1400 * 4, 1600), (232, 232, 232))
    for i, m in enumerate(mocks): row.paste(m, (i * 1400, 0))
    row.resize((2400, 686), Image.LANCZOS).save(B + 'SFW-abstract-preview.jpg', quality=90)
