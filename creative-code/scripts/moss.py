import sys, math
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter, zoom
sys.path.insert(0, '/home/claude/merch/brand')
from dtgtees import tone, src, sw, sh, B, ICC

S = 3600
box = (int(sw * 0.36), 0, int(sw * 0.36) + sh, sh)
T0 = tone(box, 900, 900)
rnd = np.random.default_rng(11)

def field(sig, n=S):
    return gaussian_filter(zoom(gaussian_filter(T0, sig), n / 900, order=3), 2)

# brand-anchored moss greens: deep shadow, body, lit, highlight
DEEPG = np.array((30, 62, 46)); BODY = np.array((70, 140, 90)); LIT = np.array((120, 180, 110)); HI = np.array((190, 222, 140))

def moss(bg=(255, 255, 255, 0), name='SFW-art-moss.png', thr=0.13):
    f = field(2.4)
    noise = gaussian_filter(rnd.random((S, S)), 6); noise = (noise - noise.mean()) / noise.std()
    g = f + 0.035 * noise
    im = Image.new('RGBA', (S, S), bg); d = ImageDraw.Draw(im)
    # sample granules: dense inside, sparse crumbs near the edge
    N = 260000
    xs = rnd.uniform(0, S, N); ys = rnd.uniform(0, S, N)
    v = g[ys.astype(int), xs.astype(int)]
    keep = (v > thr) | ((v > thr - 0.05) & (rnd.random(N) < 0.18))
    xs, ys, v = xs[keep], ys[keep], v[keep]
    order = np.argsort(ys); xs, ys, v = xs[order], ys[order], v[order]
    rs = rnd.uniform(5, 13, len(xs)) * (0.8 + 0.6 * np.clip(v, 0, 0.6))
    for x, y, r, vv in zip(xs, ys, rs, v):
        k = np.clip((vv - thr) * 3, 0, 1)                      # denser areas a touch darker
        base = (BODY * (1 - 0.35 * k) + DEEPG * 0.35 * k).astype(int)
        d.ellipse([x - r + 1.5, y - r + 2.5, x + r + 1.5, y + r + 2.5], fill=tuple(DEEPG) + (255,))
        d.ellipse([x - r, y - r, x + r, y + r], fill=tuple(base) + (255,))
        r2 = r * 0.6; d.ellipse([x - r2 - r * 0.25, y - r2 - r * 0.3, x + r2 - r * 0.25, y + r2 - r * 0.3], fill=tuple(LIT) + (255,))
        r3 = r * 0.22; d.ellipse([x - r3 - r * 0.4, y - r3 - r * 0.45, x + r3 - r * 0.4, y + r3 - r * 0.45], fill=tuple(HI) + (255,))
    im.save(B + name, icc_profile=ICC, dpi=(300, 300)); return im

def quilt(name='SFW-art-quilt.png'):
    f = field(3.0)
    N = 22
    ridge = (0.5 - 0.5 * np.cos(2 * math.pi * f * N))         # periodic bands follow contours
    ridge = ridge ** 3                                          # sharp raised seams
    h = gaussian_filter(ridge, 2.2) * 18 + f * 40
    gy, gx = np.gradient(h)
    L = np.array([-0.6, -0.7, 0.9]); L /= np.linalg.norm(L)
    nz = 1 / np.sqrt(gx ** 2 + gy ** 2 + 1)
    shade = np.clip((-gx * L[0] - gy * L[1] + L[2]) * nz, 0, 1)
    base = np.array((150, 196, 150), np.float32)               # pale sage cloth
    dark = np.array((46, 96, 70), np.float32); light = np.array((232, 244, 222), np.float32)
    s = shade[..., None]
    rgb = np.where(s < 0.72, dark + (base - dark) * (s / 0.72), base + (light - base) * ((s - 0.72) / 0.28))
    im = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8))
    im.save(B + name, icc_profile=ICC, dpi=(300, 300)); return im

if __name__ == '__main__':
    a = moss(); b = quilt()
    pv = Image.new('RGB', (2 * 1100 + 60, 1100 + 40), (236, 238, 236))
    q = Image.new('RGBA', a.size, (246, 248, 244, 255)); q.alpha_composite(a)
    pv.paste(q.convert('RGB').resize((1100, 1100), Image.LANCZOS), (20, 20))
    pv.paste(b.resize((1100, 1100), Image.LANCZOS), (1140, 20))
    pv.save(B + 'SFW-art-moss-quilt-preview.jpg', quality=90)
    q.convert('RGB').crop((1300, 1300, 2300, 2300)).save(B + 'SFW-art-moss-detail.jpg', quality=92)
    b.crop((1300, 1300, 2300, 2300)).save(B + 'SFW-art-quilt-detail.jpg', quality=92)
