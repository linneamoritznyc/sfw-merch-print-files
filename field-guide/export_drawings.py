"""Export every drawing in the field guide as its own graphic for Canva: vector SVG with a transparent
background, plus a 2x PNG. Labels, leader lines, captions and text are left out.

How: each page is rebuilt with the text and label functions switched off, the white page background is
removed, the drawings are found as separate islands, and each island is cut out as a vector viewBox crop.

Usage: python3 export_drawings.py  ->  out/drawings/ (numbered). The named set for Canva is out/graphics/ and
out/sfw-field-guide-graphics.zip.
"""
import io, os, re
import numpy as np
import cairosvg, cv2
from PIL import Image
import euglypha, nematode, fungi, pages_4_8

OUT = os.path.join(euglypha.OUT, "drawings")
W, H = euglypha.W, euglypha.H
NO_TEXT = lambda *a, **k: ("", 0)
NO_LABEL = lambda *a, **k: ""


def silence(mod):
    for name in ("text",):
        if hasattr(mod, name):
            setattr(mod, name, NO_TEXT)
    if hasattr(mod, "label"):
        mod.label = NO_LABEL
    if hasattr(mod, "para"):
        mod.para = lambda *a, **k: ("", 0)


for m in (euglypha, nematode, fungi, pages_4_8):
    silence(m)
pages_4_8.caption = lambda *a, **k: ""
pages_4_8.facts = lambda *a, **k: ""

captured = {}
pages_4_8.finish = lambda name, body: captured.__setitem__(name, body)


def bare(svg_body):
    body = re.sub(r'<rect width="%d" height="%d" fill="#FFFFFF"/>' % (W, H), "", svg_body)
    body = re.sub(r'<rect x="[\d.]+" y="[\d.]+" width="[\d.]+" height="10" fill="#22371F"/>', "", body)   # scale bars
    return body


def svg_doc(body, vb=None):
    vb = vb or (0, 0, W, H)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{vb[2]:.0f}" height="{vb[3]:.0f}" '
            f'viewBox="{vb[0]:.0f} {vb[1]:.0f} {vb[2]:.0f} {vb[3]:.0f}">\n{body}\n</svg>\n')


def islands(body, merge=70, min_area=1500):
    k = 4
    png = cairosvg.svg2png(bytestring=svg_doc(body).encode(), output_width=W // k, output_height=H // k)
    a = np.asarray(Image.open(io.BytesIO(png)).convert("RGBA"))[..., 3] > 10
    m = cv2.dilate(a.astype(np.uint8), np.ones((merge // k, merge // k)))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    boxes = []
    for i in range(1, n):
        x, y, w, h, area = st[i]
        if a[lab == i].sum() * k * k < min_area or min(w, h) * k < 60:
            continue
        pad = 20
        reg = cv2.dilate((lab == i).astype(np.uint8), np.ones((3, 3)))
        cs, _ = cv2.findContours(reg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        clip = "".join("M" + "L".join(f"{px * k:.0f},{py * k:.0f}" for px, py in c[:, 0]) + "Z" for c in cs)
        boxes.append(((x * k - pad, y * k - pad, w * k + 2 * pad, h * k + 2 * pad), clip))
    return sorted(boxes, key=lambda b: (round(b[0][1] / 300), b[0][0]))


def main():
    os.makedirs(OUT, exist_ok=True)
    bodies = {}
    for name, mod in (("01-euglypha", euglypha), ("02-nematode", nematode), ("03-fungi", fungi)):
        s = mod.page()
        bodies[name] = s[s.index(">", s.index("<svg")) + 1:s.rindex("</svg>")]
    pages_4_8.main()
    for i, key in enumerate(["flagellate", "amoeba", "ciliate", "bacteria", "microarthropods"], 4):
        bodies[f"{i:02d}-{key}"] = captured[key]
    index = []
    for page, body in bodies.items():
        body = bare(body)
        for j, ((x, y, w, h), clip) in enumerate(islands(body, merge=48), 1):
            name = f"{page}-{j:02d}"
            s = svg_doc(f'<clipPath id="c"><path d="{clip}"/></clipPath><g clip-path="url(#c)">{body}</g>', (x, y, w, h))
            open(os.path.join(OUT, name + ".svg"), "w").write(s)
            im = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=s.encode(), output_width=int(w * 2), output_height=int(h * 2)))).convert("RGBA")
            im.save(os.path.join(OUT, name + ".png"))
            index.append((name, im))
    # contact sheet with file names
    from PIL import ImageDraw
    cell = 260; cols = 8
    rows = (len(index) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * cell, rows * (cell + 30)), "white"); d = ImageDraw.Draw(sheet)
    for k, (name, im) in enumerate(index):
        t = im.copy(); t.thumbnail((cell - 20, cell - 20))
        x, y = (k % cols) * cell, (k // cols) * (cell + 30)
        sheet.paste(t, (x + (cell - t.width) // 2, y + (cell - t.height) // 2), t); d.text((x + 8, y + cell + 6), name, fill="#22371F")
    sheet.save(os.path.join(OUT, "_contact-sheet.png"))
    print(len(index), "drawings")


if __name__ == "__main__":
    main()
