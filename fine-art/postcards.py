"""Soil Food Web archival postcards, 6 x 4 in + 1/8 in bleed at 300 dpi (1875 x 1275).
  polaroid   three instant-film prints of student micrographs on a pale wall, typewriter captions
  index      a contact strip of six instant prints, organism names typed under each
  swiss      white card on grey paper: micrograph square top right, tiny text columns, big grotesque title
  back       shared back: caption, credit, divider, address lines
Output out/postcards/<name>.png + contact.jpg
"""
import io, os
import numpy as np
import cairosvg
from PIL import Image, ImageOps, ImageFilter, ImageDraw
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
SRC, OUT = os.path.join(HERE, "src"), os.path.join(HERE, "out", "postcards")
W, H = 1875, 1275
rng = np.random.default_rng(8)
MICRO = {"NEMATODE": ("nematode-molting-cameron-radman", "Cameron Radman"), "TESTATE": ("testate-encysted-robert-kenyon", "Robert Kenyon"),
         "HYPHA": ("fungal-hypha-lee-kirk", "Lee Kirk"), "MITE": ("mite-talbot-armstrong-i3", "Talbot Armstrong"),
         "AMOEBA": ("stellate-amoeba-jimena-fuentes", "Jimena Fuentes"), "SPORE": ("fungal-spore-josia-martens", "Josia Martens")}


def svg(body, w=W, h=H):
    return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}">{body}</svg>'.encode()))).convert("RGBA")


def micro(key, size, tone=None, box=None):
    im = Image.open(os.path.join(SRC, MICRO[key][0] + ".jpg")).convert("RGB")
    if key == "HYPHA": im = im.crop((0, 20, im.width, im.height - 30))
    if box: w, h = im.size; im = im.crop((int(box[0] * w), int(box[1] * h), int(box[2] * w), int(box[3] * h)))
    im = ImageOps.fit(im, size, Image.LANCZOS)
    if tone == "bw":
        g = ImageOps.autocontrast(im.convert("L"), cutoff=1); im = Image.merge("RGB", [g, g, g])
    elif tone == "film":                                       # faded instant-film colour: lift blacks, cool cast
        a = np.asarray(im, np.float32); a = a * .82 + 30; a[..., 2] += 10; a[..., 0] -= 4
        im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    return im


def paper(base, amt=6):
    a = np.ones((H, W, 3), np.float32) * np.array(base, np.float32)
    a += ndi.gaussian_filter(rng.normal(0, 1, (H, W)), 1.2)[:, :, None] * amt
    a += (ndi.gaussian_filter(rng.random((H // 20 + 1, W // 20 + 1)), 3).repeat(20, 0).repeat(20, 1)[:H, :W, None] - .5) * amt * 3
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")


def instant(key, w, label, rot=0, box=None):
    """Instant-film print: square image in a white frame with a deep bottom margin and a typed caption."""
    m = int(w * .06); iw = w - 2 * m; h = int(w * 1.2)
    card = Image.new("RGBA", (w, h), (246, 245, 240, 255))
    card.paste(micro(key, (iw, iw), "film", box), (m, m))
    card.alpha_composite(svg(f'<text x="{w / 2}" y="{iw + m + (h - iw - m) * .62}" font-family="Courier 10 Pitch" font-size="{w * .07:.0f}" letter-spacing="{w * .03:.0f}" text-anchor="middle" fill="#3a3a3a">{label}</text>', w, h))
    shadow = Image.new("RGBA", (w + 80, h + 80), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rectangle((44, 52, w + 44, h + 52), fill=(40, 50, 60, 90))
    shadow = shadow.filter(ImageFilter.GaussianBlur(14))
    shadow.alpha_composite(card, (40, 40))
    return shadow.rotate(rot, Image.BICUBIC, expand=True)


def polaroid():
    page = paper((196, 214, 228))
    words = [("NEMATODE", "LOOK", -2.5), ("TESTATE", "CLOSER", 1.5), ("HYPHA", "SOIL", -1)]
    for i, (k, lab, r) in enumerate(words):
        p = instant(k, 520, lab, r)
        page.alpha_composite(p, (110 + i * 570, 170 + (i % 2) * 40))
    page.alpha_composite(svg('<text x="1765" y="1190" font-family="Courier 10 Pitch" font-size="30" letter-spacing="8" text-anchor="end" fill="#3a3a3a">SOIL FOOD WEB</text>'))
    return page


def index():
    page = paper((236, 234, 226))
    keys = list(MICRO)
    for i, k in enumerate(keys):
        r, c = divmod(i, 3)
        page.alpha_composite(instant(k, 420, k, rng.uniform(-1.2, 1.2)), (150 + c * 540, 60 + r * 560))
    return page


def swiss():
    page = paper((214, 212, 204), 5)
    cw, ch = 1150, 1060; cx, cy = (W - cw) // 2 + 60, (H - ch) // 2
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).rectangle((cx - 40, cy + 30, cx + cw - 60, cy + ch + 20), fill=(0, 0, 0, 70))
    page.alpha_composite(sh.filter(ImageFilter.GaussianBlur(30)))
    card = paper((233, 232, 228), 3).crop((0, 0, cw, ch))
    card.paste(micro("TESTATE", (470, 470), "bw", (.08, .02, .45, .5)), (cw - 470 - 14, 14))
    t = lambda x, y, s, txt, wgt=500, anchor="start": f'<text x="{x}" y="{y}" font-family="Inter" font-weight="{wgt}" font-size="{s}" text-anchor="{anchor}" fill="#151515">{txt}</text>'
    body = t(18, 34, 15, "SOIL FOOD WEB") + t(18, 52, 15, "SCHOOL") + t(18, 70, 15, "STUDENT MICROGRAPHS")
    body += t(18, 560, 15, "No. 01")
    lines = ["A TESTATE AMOEBA", "IN ITS SHELL,", "FROM A SOIL SAMPLE.", "", "PHOTOGRAPHED BY", "ROBERT KENYON,", "SOIL FOOD WEB", "SCHOOL STUDENT."]
    for i, l in enumerate(lines): body += t(cw - 470 - 14, 540 + i * 19, 15, l)
    body += f'<text x="14" y="{ch - 34}" font-family="Inter Display" font-weight="600" font-size="150" letter-spacing="-7" fill="#151515">Look Closer</text>'
    body += f'<text x="{cw - 14}" y="{ch - 34}" font-family="Inter Display" font-weight="600" font-size="150" letter-spacing="-6" text-anchor="end" fill="#151515">01</text>'
    card.alpha_composite(svg(body, cw, ch))
    page.alpha_composite(card, (cx, cy))
    return page


def back():
    page = paper((246, 245, 240), 3)
    t = lambda x, y, s, txt, f="Inter", wgt=500, anchor="start", fill="#151515": f'<text x="{x}" y="{y}" font-family="{f}" font-weight="{wgt}" font-size="{s}" text-anchor="{anchor}" fill="{fill}">{txt}</text>'
    body = f'<line x1="{W / 2}" y1="140" x2="{W / 2}" y2="{H - 140}" stroke="#151515" stroke-width="2"/>'
    for i in range(4): body += f'<line x1="{W / 2 + 80}" y1="{560 + i * 120}" x2="{W - 140}" y2="{560 + i * 120}" stroke="#151515" stroke-width="2"/>'
    body += f'<rect x="{W - 300}" y="140" width="160" height="200" fill="none" stroke="#151515" stroke-width="2" stroke-dasharray="8 6"/>'
    body += t(140, 180, 22, "SOIL FOOD WEB SCHOOL", wgt=600) + t(140, 212, 22, "Student micrographs")
    body += t(140, H - 200, 26, "LOOK CLOSER", f="Courier 10 Pitch", wgt=400)
    body += t(140, H - 160, 20, "Photographs taken by students through the microscope.", wgt=400)
    body += t(140, H - 132, 20, "school.soilfoodweb.com", wgt=400)
    page.alpha_composite(svg(body))
    return page


def main():
    os.makedirs(OUT, exist_ok=True)
    cards = {"polaroid": polaroid(), "index": index(), "swiss": swiss(), "back": back()}
    for k, im in cards.items(): im.convert("RGB").save(os.path.join(OUT, f"postcard-{k}.png"), dpi=(300, 300))
    tw, th = 750, 510
    sheet = Image.new("RGB", (2 * tw + 30, 2 * th + 30), "#fafaf5")
    for i, im in enumerate(cards.values()): sheet.paste(im.convert("RGB").resize((tw, th), Image.LANCZOS), (10 + (i % 2) * (tw + 10), 10 + (i // 2) * (th + 10)))
    sheet.save(os.path.join(OUT, "contact.jpg"), quality=90)


if __name__ == "__main__":
    main()
