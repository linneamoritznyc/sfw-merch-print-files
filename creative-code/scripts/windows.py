import glob, math, sys
import numpy as np
from PIL import Image, ImageOps, ImageCms
from scipy.ndimage import gaussian_filter, zoom
from scipy.spatial import cKDTree
B = '/home/claude/merch/brand/'
ICC = ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
S = 3600
rnd = np.random.default_rng(int(sys.argv[1]) if len(sys.argv) > 1 else 3)
files = sorted(glob.glob('/home/claude/merch/micro/*.jpg'))

RAMPS = {
    'green':  [(30, 62, 46), (70, 167, 112), (178, 214, 72), (255, 255, 255)],
    'purple': [(26, 40, 78), (104, 49, 140), (186, 160, 226), (255, 255, 255)],
    'olive':  [(46, 52, 22), (120, 124, 52), (200, 210, 120), (255, 255, 255)],
}
def gradmap(gray, ramp):
    g = gray[..., None]; stops = np.linspace(0, 1, len(ramp)); out = np.zeros(gray.shape + (3,))
    for (a, ca), (b, cb) in zip(zip(stops, ramp), zip(stops[1:], ramp[1:])):
        k = (g >= a) & (g <= b); u = (g - a) / (b - a)
        out = np.where(k, np.array(ca) + (np.array(cb) - np.array(ca)) * u, out)
    return out

# organic cells: smoothed voronoi with rounded gaps
n = 34; pts = []
while len(pts) < n:
    p = rnd.uniform(0.04, 0.96, 2)
    if all(np.hypot(*(p - q)) > 0.11 for q in pts): pts.append(p)
pts = np.array(pts)
R = 900
yy, xx = np.mgrid[0:R, 0:R] / R
d, idx = cKDTree(pts).query(np.dstack([xx, yy]).reshape(-1, 2), k=2)
gap = (d[:, 1] - d[:, 0]).reshape(R, R)
own = idx[:, 0].reshape(R, R)
inside = gaussian_filter((gap > 0.022).astype(float), 9)
mask = zoom(inside, S / R, order=3) > 0.5
ownS = zoom(own, S / R, order=0)

out = np.full((S, S, 3), 255, np.float32)
for c in range(n):
    sel = (ownS == c) & mask
    if not sel.any(): continue
    ys, xs = np.where(sel); y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    h, w = y1 - y0, x1 - x0
    im = ImageOps.grayscale(Image.open(files[rnd.integers(len(files))]))
    # centre the crop on the busiest part of the micrograph
    sm = np.asarray(im.resize((im.width // 8, im.height // 8))).astype(float)
    busy = gaussian_filter(np.abs(sm - gaussian_filter(sm, 6)), 5)
    by, bx = np.unravel_index(np.argmax(busy), busy.shape); by *= 8; bx *= 8
    scale = rnd.uniform(0.55, 1.1)
    cw = int(min(im.width, im.height) * scale * w / max(w, h)); ch = int(cw * h / w)
    cx = np.clip(bx - cw // 2, 0, im.width - cw); cy = np.clip(by - ch // 2, 0, im.height - ch)
    crop = im.crop((cx, cy, cx + cw, cy + ch)).resize((w, h), Image.LANCZOS)
    g = np.asarray(crop).astype(np.float32) / 255
    g = (g - np.percentile(g, 2)) / (np.percentile(g, 98) - np.percentile(g, 2) + 1e-6)
    g = np.clip(g, 0, 1) ** 0.9
    ramp = RAMPS[rnd.choice(['green', 'green', 'purple', 'olive'])]
    rgb = gradmap(g, ramp)
    blk = out[y0:y1, x0:x1]; m = sel[y0:y1, x0:x1]
    blk[m] = rgb[m]
img = Image.fromarray(out.astype(np.uint8))
img.save(B + 'SFW-art-windows.png', icc_profile=ICC, dpi=(300, 300))
img.resize((1400, 1400), Image.LANCZOS).save(B + 'SFW-art-windows-preview.jpg', quality=90)
img.crop((1200, 1200, 2400, 2400)).save(B + 'SFW-art-windows-detail.jpg', quality=92)
