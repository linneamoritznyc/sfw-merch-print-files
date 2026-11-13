import glob
import numpy as np
from PIL import Image, ImageOps, ImageCms
from scipy.ndimage import gaussian_filter
from scipy.spatial import cKDTree
ICC = ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
files = sorted(glob.glob('/home/claude/merch/micro/*.jpg'))
RAMPS = {
    'green':  [(30, 62, 46), (70, 167, 112), (178, 214, 72), (255, 255, 255)],
    'purple': [(26, 40, 78), (104, 49, 140), (186, 160, 226), (255, 255, 255)],
    'olive':  [(46, 52, 22), (120, 124, 52), (200, 210, 120), (255, 255, 255)],
}
def gradmap(g, ramp):
    g = g[..., None]; stops = np.linspace(0, 1, len(ramp)); out = np.zeros(g.shape[:2] + (3,))
    for (a, ca), (b, cb) in zip(zip(stops, ramp), zip(stops[1:], ramp[1:])):
        k = (g >= a) & (g <= b); u = (g - a) / (b - a)
        out = np.where(k, np.array(ca) + (np.array(cb) - np.array(ca)) * u, out)
    return out

def make(W, H, cell, gap, seed, round_=0.22, ramps=('green', 'green', 'purple', 'olive')):
    """cell: target cell size in px; gap: white channel width in px."""
    rnd = np.random.default_rng(seed)
    pts = []; tries = 0
    while tries < 20000:
        tries += 1
        p = rnd.uniform([-cell * 0.3, -cell * 0.3], [W + cell * 0.3, H + cell * 0.3])
        if all(np.hypot(*(p - q)) > cell * 0.8 for q in pts): pts.append(p)
    pts = np.array(pts)
    yy, xx = np.mgrid[0:H, 0:W]
    d, idx = cKDTree(pts).query(np.dstack([xx, yy]).reshape(-1, 2).astype(np.float32), k=2)
    gapf = (d[:, 1] - d[:, 0]).reshape(H, W); own = idx[:, 0].reshape(H, W)
    sig = cell * round_ * 0.35
    inside = gaussian_filter((gapf > gap).astype(np.float32), sig) > 0.5
    out = np.full((H, W, 3), 255, np.float32)
    for c in np.unique(own):
        sel = (own == c) & inside
        if sel.sum() < 50: continue
        ys, xs = np.where(sel); y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        h, w = y1 - y0, x1 - x0
        im = ImageOps.grayscale(Image.open(files[rnd.integers(len(files))]))
        sm = np.asarray(im.resize((im.width // 8, im.height // 8))).astype(float)
        busy = gaussian_filter(np.abs(sm - gaussian_filter(sm, 6)), 5)
        by, bx = np.unravel_index(np.argmax(busy), busy.shape); by *= 8; bx *= 8
        scale = rnd.uniform(0.45, 0.9)
        cw = int(min(im.width, im.height) * scale * w / max(w, h)); ch = int(cw * h / w)
        cw = min(cw, im.width); ch = min(ch, im.height)
        cx = int(np.clip(bx - cw // 2, 0, im.width - cw)); cy = int(np.clip(by - ch // 2, 0, im.height - ch))
        g = np.asarray(im.crop((cx, cy, cx + cw, cy + ch)).resize((w, h), Image.LANCZOS)).astype(np.float32) / 255
        g = np.clip((g - np.percentile(g, 2)) / (np.percentile(g, 98) - np.percentile(g, 2) + 1e-6), 0, 1) ** 0.9
        rgb = gradmap(g, RAMPS[rnd.choice(ramps)])
        blk = out[y0:y1, x0:x1]; m = sel[y0:y1, x0:x1]; blk[m] = rgb[m]
    # soften only the 1px cell edge (supersample-free antialias)
    edge = gaussian_filter(inside.astype(np.float32), 0.8)[..., None]
    out = out * edge + 255 * (1 - edge)
    return Image.fromarray(out.astype(np.uint8))
