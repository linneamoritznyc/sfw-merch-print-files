"""SFW type pairings: six display + text pairings, each shown in the same three uses
(poster headline with body, merch joke, specimen caption). White ground, brand colours."""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
CV = "/mnt/skills/examples/canvas-design/canvas-fonts"
SCR = "/tmp/claude-0/-home-user/4694bf57-0834-52a9-9a56-4d1fe0523221/scratchpad/f"
EB = os.path.join(ROOT, "creative-code", "fonts")
DEEP, GREEN, PURPLE, BROWN = "#1C3A28", "#156826", "#624AA0", "#7A4624"
cv = lambda n: os.path.join(CV, n)

PAIRS = [  # name, display font, display caps?, text font, label font, ink
    ("A  Young Serif + Instrument Sans", cv("YoungSerif-Regular.ttf"), False, cv("InstrumentSans-Regular.ttf"), cv("InstrumentSans-Bold.ttf"), DEEP),
    ("B  Gloock + Work Sans", cv("Gloock-Regular.ttf"), False, cv("WorkSans-Regular.ttf"), cv("WorkSans-Bold.ttf"), DEEP),
    ("C  Instrument Serif + Instrument Sans", cv("InstrumentSerif-Regular.ttf"), False, cv("InstrumentSans-Regular.ttf"), cv("InstrumentSans-Bold.ttf"), PURPLE),
    ("D  Bricolage Grotesque + EB Garamond", cv("BricolageGrotesque-Bold.ttf"), False, os.path.join(EB, "EBGaramond-Regular.ttf"), cv("BricolageGrotesque-Regular.ttf"), GREEN),
    ("E  EB Garamond, done properly + DM Mono", os.path.join(EB, "EBGaramond-Medium.ttf"), False, os.path.join(EB, "EBGaramond-Regular.ttf"), cv("DMMono-Regular.ttf"), DEEP),
    ("F  Libre Baskerville + National Park", cv("LibreBaskerville-Regular.ttf"), False, cv("NationalPark-Regular.ttf"), cv("NationalPark-Bold.ttf"), BROWN),
]


def tracked(d, xy, text, font, fill, track):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill); x += font.getlength(ch) + track


def wrap(text, font, w):
    out, line = [], ""
    for word in text.split():
        t = (line + " " + word).strip()
        if font.getlength(t) <= w: line = t
        else: out.append(line); line = word
    return out + [line]


def row(name, disp, caps, txt, lab, ink, W=2400, H=620):
    im = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(im)
    small = ImageFont.truetype(lab, 26)
    tracked(d, (60, 36), name.upper(), small, "#888", 3)
    # 1 poster headline + body
    x0 = 60
    hf = ImageFont.truetype(disp, 112); bf = ImageFont.truetype(txt, 34)
    y = 110
    for l in ("Life in a", "teaspoon of soil"):
        d.text((x0, y), l, font=hf, fill=ink); y += 118
    y += 24
    for l in wrap("Bacteria, fungi, protozoa and nematodes, photographed by students through the microscope.", bf, 880):
        d.text((x0, y), l, font=bf, fill="#2a2a2a"); y += 46
    # 2 merch joke, centred in a mug-front box
    cx = 1420; jf1 = ImageFont.truetype(disp, 74); jf2 = ImageFont.truetype(disp, 104)
    for i, (t, f) in enumerate((("I'm just here", jf1), ("for the bacteria", jf1))):
        d.text((cx, 140 + i * 82), t, font=f, fill=ink, anchor="ma")
    d.rounded_rectangle((cx - 150, 320, cx + 150, 470), 40, outline="#ddd", width=3)
    d.text((cx, 490), "FUNGI TO BE WITH" if False else "", font=jf2, fill=ink, anchor="ma")
    # 3 specimen caption
    lx = 1820
    lf = ImageFont.truetype(lab, 24); tf = ImageFont.truetype(txt, 30); nf = ImageFont.truetype(disp, 58)
    d.rectangle((lx, 120, lx + 440, 420), fill="#EEF0EA")
    d.text((lx, 440), "Testate amoeba", font=nf, fill=ink)
    tracked(d, (lx, 520), "400X  STUDENT PHOTO", lf, "#555", 3)
    d.text((lx, 560), "Robert Kenyon", font=tf, fill="#555")
    d.line([(40, H - 2), (W - 40, H - 2)], fill="#e6e6e6", width=2)
    return im


def main():
    rows = [row(*p) for p in PAIRS]
    sheet = Image.new("RGB", (2400, sum(r.height for r in rows)), "white"); y = 0
    for r in rows: sheet.paste(r, (0, y)); y += r.height
    os.makedirs(os.path.join(ROOT, "previews"), exist_ok=True)
    sheet.save(os.path.join(ROOT, "previews", "SFW-type-pairings.jpg"), quality=90)


if __name__ == "__main__":
    main()
