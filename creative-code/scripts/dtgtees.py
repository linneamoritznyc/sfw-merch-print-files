import numpy as np, math
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageCms
from scipy.ndimage import gaussian_filter, percentile_filter
Image.MAX_IMAGE_PIXELS = None
B = '/home/claude/merch/brand/'
ICC = ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
W, H = 3600, 4800                     # 12x16 in @300
GREEN = (70, 167, 112); PURPLE = (104, 49, 140); NAVY = (26, 40, 78); MAROON = (110, 40, 46)
LAV = (186, 160, 226); WHITE = (255, 255, 255)
f_big = ImageFont.truetype(B + 'ebg600.ttf', 300)
f_mid = ImageFont.truetype(B + 'ebg500.ttf', 120)

src = Image.open('/mnt/user-data/uploads/1cd60aff-image.png').convert('L')
src = src.crop((8, 8, src.width - 8, src.height - 8))
sw, sh = src.size
sm = np.asarray(src.resize((sw // 4, sh // 4))).astype(np.float32)
BGF = Image.fromarray(gaussian_filter(percentile_filter(sm, 90, size=25), 6)).resize((sw, sh), Image.BICUBIC)

def tone(box, w, h):
    reg = src.crop(box).resize((w, h), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 100, 2))
    b = np.asarray(BGF.crop(box).resize((w, h), Image.BICUBIC)).astype(np.float32)
    g = np.asarray(reg).astype(np.float32)
    t = np.clip((b - g) / (b * 0.75), 0, 1)
    return np.clip((t - 0.10) / 0.9, 0, 1) ** 0.8

def halftone(t, cell=12, angle=22.5, ss=3):
    """opaque round dots, size by tone. returns bool mask."""
    h, w = t.shape
    big = Image.new('L', (w * ss, h * ss), 0); d = ImageDraw.Draw(big)
    a = math.radians(angle); ca, sa = math.cos(a), math.sin(a)
    diag = int(math.hypot(w, h)) + cell
    for i in range(-diag, diag, cell):
        for j in range(-diag, diag, cell):
            x = w / 2 + i * ca - j * sa; y = h / 2 + i * sa + j * ca
            if not (0 <= x < w and 0 <= y < h): continue
            v = t[int(y), int(x)]
            if v < 0.04: continue
            r = cell * 0.5 * math.sqrt(v) * 1.15
            d.ellipse([(x - r) * ss, (y - r) * ss, (x + r) * ss, (y + r) * ss], fill=255)
    return np.asarray(big.resize((w, h), Image.LANCZOS)) > 127

def spaced(d, y, text, font, fill, sp=40, W=W):
    tot = sum(d.textlength(c, font=font) for c in text) + sp * (len(text) - 1); x = (W - tot) / 2
    for c in text: d.text((x, y), c, font=font, fill=fill); x += d.textlength(c, font=font) + sp

def save(P, name):
    P = P.crop(P.getbbox()); P.save(B + name, icc_profile=ICC, dpi=(300, 300)); return P

# 1. White tee: two-colour gradient map (green shadows -> purple mids), colour-to-colour, prints as-is on white
def design_gradient():
    box = (int(sw * 0.30), 0, int(sw * 0.98), sh); iw = 3400; ih = int(iw * (box[3] - box[1]) / (box[2] - box[0]))
    t = tone(box, iw, ih)
    c1, c2 = np.array(LAV, np.float32), np.array(PURPLE, np.float32); c3 = np.array(NAVY, np.float32)
    rgb = np.where(t[..., None] < 0.5, c1 + (c2 - c1) * (t[..., None] / 0.5), c2 + (c3 - c2) * ((t[..., None] - 0.5) / 0.5))
    a = np.where(t > 0.06, 255, 0).astype(np.uint8)
    P = Image.new('RGBA', (W, ih + 700), (0, 0, 0, 0)); d = ImageDraw.Draw(P)
    P.paste(Image.fromarray(np.dstack([rgb.astype(np.uint8), a]), 'RGBA'), ((W - iw) // 2, 0))
    spaced(d, ih + 160, 'SOIL FOOD WEB', f_big, NAVY + (255,))
    return save(P, 'SFW-dtg-gradient-white.png')

# 2. Dark tee: white halftone micrograph that fades out by dot size (no transparency)
def design_halftone_fade(ink=WHITE, name='SFW-dtg-halftone-fade-navy.png'):
    box = (int(sw * 0.30), 0, int(sw * 0.98), sh); iw = 3400; ih = int(iw * (box[3] - box[1]) / (box[2] - box[0]))
    t = tone(box, iw, ih)
    yy, xx = np.mgrid[0:ih, 0:iw]
    fall = np.clip(1.25 - np.hypot((xx - iw / 2) / (iw * 0.55), (yy - ih / 2) / (ih * 0.62)), 0, 1)
    t2 = np.clip(t * 1.1, 0, 1) * fall
    m = halftone(t2, cell=12)
    P = Image.new('RGBA', (W, ih + 700), (0, 0, 0, 0)); d = ImageDraw.Draw(P)
    layer = np.zeros((ih, iw, 4), np.uint8); layer[m] = ink + (255,)
    P.paste(Image.fromarray(layer, 'RGBA'), ((W - iw) // 2, 0))
    spaced(d, ih + 160, 'SOIL FOOD WEB', f_big, ink + (255,))
    return save(P, name)

# 3. Vintage tour-tee: one-ink halftone block + big type, distress as 100% knockouts
def design_tour(ink=GREEN, name='SFW-dtg-tour-green.png'):
    box = (int(sw * 0.42), 0, int(sw * 0.86), sh); iw = 2900; ih = int(iw * (box[3] - box[1]) / (box[2] - box[0]))
    t = tone(box, iw, ih)
    m = halftone(np.clip(t * 1.15, 0, 1), cell=14, angle=45)
    blk = np.zeros((ih, iw), bool); blk[:] = True
    img = blk & ~m          # ink block with microbes knocked out as fabric colour
    P = Image.new('RGBA', (W, ih + 1300), (0, 0, 0, 0)); d = ImageDraw.Draw(P)
    spaced(d, 0, 'SOIL FOOD WEB', f_big, ink + (255,))
    layer = np.zeros((ih, iw, 4), np.uint8); layer[img] = ink + (255,)
    P.paste(Image.fromarray(layer, 'RGBA'), ((W - iw) // 2, 420))
    spaced(d, 420 + ih + 120, 'FROM THE MICROSCOPE', f_mid, ink + (255,), sp=24)
    # distress: random 100% knockouts
    rnd = np.random.default_rng(4)
    a = np.asarray(P.split()[3]).copy()
    noise = gaussian_filter(rnd.random(a.shape), 2.2)
    a[noise > np.percentile(noise, 93)] = 0
    P.putalpha(Image.fromarray(a))
    return save(P, name)

# 4. Light tee: full-tone photographic duotone in brand green (colour fades to fabric white = white tee only)
def design_photo(ink=GREEN, name='SFW-dtg-photo-green-white.png'):
    box = (int(sw * 0.30), 0, int(sw * 0.98), sh); iw = 3400; ih = int(iw * (box[3] - box[1]) / (box[2] - box[0]))
    t = tone(box, iw, ih); inkA = np.array(ink, np.float32)
    rgb = 255 * (1 - t[..., None]) + inkA * t[..., None]; a = np.where(t > 0.05, 255, 0).astype(np.uint8)
    P = Image.new('RGBA', (W, ih + 700), (0, 0, 0, 0)); d = ImageDraw.Draw(P)
    P.paste(Image.fromarray(np.dstack([rgb.astype(np.uint8), a]), 'RGBA'), ((W - iw) // 2, 0))
    spaced(d, ih + 160, 'SOIL FOOD WEB', f_big, ink + (255,))
    return save(P, name)

def tee(P, shirt):
    M = Image.new('RGB', (1400, 1600), (232, 232, 232)); d = ImageDraw.Draw(M)
    d.polygon([(380, 120), (560, 80), (840, 80), (1020, 120), (1330, 330), (1220, 560), (1080, 480), (1080, 1520), (320, 1520), (320, 480), (180, 560), (70, 330)], fill=shirt)
    d.ellipse([560, 40, 840, 170], fill=(232, 232, 232))
    pw = 660; p = P.resize((pw, int(pw * P.height / P.width)), Image.LANCZOS); M.paste(p, ((1400 - pw) // 2, 290), p)
    return M

if __name__ == '__main__':
    a = design_gradient(); b = design_halftone_fade(); c = design_tour(); e = design_photo()
    mocks = [tee(a, (250, 250, 248)), tee(b, (30, 38, 66)), tee(c, (250, 250, 248)), tee(e, (250, 250, 248))]
    row = Image.new('RGB', (1400 * 4, 1600), (232, 232, 232))
    for i, m in enumerate(mocks): row.paste(m, (i * 1400, 0))
    row.resize((2400, 686), Image.LANCZOS).save(B + 'SFW-dtg-tees-preview.jpg', quality=90)
    for nm, P in (('gradient', a), ('halftone', b), ('tour', c)):
        P.convert('RGBA').crop((900, 600, 2100, 1500)).save(B + f'SFW-dtg-detail-{nm}.png')
