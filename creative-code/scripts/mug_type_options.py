"""Type options for the funny mugs: the same joke on the front of an 11 oz mug in different fonts and layouts.
Character space is left empty (a pale outline marks where the watercolor character goes)."""
import io, os
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
SCR = os.environ.get("SCR", "/tmp")
SM = "/home/user/SFW-SocialMedia/assets/font"
CV = "/mnt/skills/examples/canvas-design/canvas-fonts"
FONTS = os.path.join(ROOT, "creative-code", "fonts")
OUT = os.path.join(ROOT, "previews")
W, H = 1350, 1050
DEEP, PURPLE, LAV, LIME, BROWN, WHITE = "#1C3A28", "#624AA0", "#C4B6E8", "#CEE26E", "#7A4624", "#FFFFFF"


def woff_to_ttf(src, dst, wght=None):
    if not os.path.exists(dst):
        f = TTFont(src); f.flavor = None
        if wght and "fvar" in f:
            from fontTools.varLib.instancer import instantiateVariableFont
            f = instantiateVariableFont(f, {"wght": wght})
        f.save(dst)
    return dst


def fonts():
    os.makedirs(os.path.join(SCR, "f"), exist_ok=True)
    j = lambda n: os.path.join(SCR, "f", n)
    return {
        "EB Garamond SemiBold, caps": (os.path.join(FONTS, "EBGaramond-SemiBold.ttf"), True, 0),
        "EB Garamond Medium, upper + lower": (os.path.join(FONTS, "EBGaramond-Medium.ttf"), False, 0),
        "Montserrat Bold, caps": (woff_to_ttf(os.path.join(SM, "montserrat-latin-variable.woff2"), j("mont700.ttf"), 700), True, 4),
        "Source Sans 3 SemiBold, caps": (woff_to_ttf(os.path.join(SM, "source-sans-3-latin-600-normal.woff2"), j("ss600.ttf")), True, 4),
        "Young Serif (new)": (os.path.join(CV, "YoungSerif-Regular.ttf"), True, 0),
        "Gloock (new)": (os.path.join(CV, "Gloock-Regular.ttf"), True, 0),
        "Bricolage Grotesque Bold (new)": (os.path.join(CV, "BricolageGrotesque-Bold.ttf"), True, 0),
        "National Park Bold (new)": (os.path.join(CV, "NationalPark-Bold.ttf"), True, 2),
        "Lora Bold (new)": (os.path.join(CV, "Lora-Bold.ttf"), False, 0),
    }


def fit(path, lines, maxw, size):
    while True:
        f = ImageFont.truetype(path, size)
        if max(f.getlength(l) for l in lines) <= maxw or size < 30: return f
        size -= 4


def front(path, caps, track, ground, ink):
    im = Image.new("RGB", (W, H), ground); d = ImageDraw.Draw(im)
    top = ["DON'T TALK TO ME", "UNTIL I'VE HAD MY"]; bot = ["COMPOST TEA"]
    if not caps: top = ["Don't talk to me", "until I've had my"]; bot = ["compost tea"]
    f1 = fit(path, top, W - 260, 110); f2 = fit(path, bot, W - 260, 150)
    def line(t, f, y):
        if track:
            x = (W - (f.getlength(t) + track * (len(t) - 1))) / 2
            for ch in t: d.text((x, y), ch, font=f, fill=ink); x += f.getlength(ch) + track
        else:
            d.text((W / 2, y), t, font=f, fill=ink, anchor="ma")
    y = 70
    for t in top: line(t, f1, y); y += f1.size * 1.08
    d.rounded_rectangle((W / 2 - 230, y + 30, W / 2 + 230, H - 70 - f2.size * 1.25), 60, outline=LAV if ground == WHITE else "#3E5A48", width=4)
    line(bot[0], f2, H - 70 - f2.size)
    return im


def main():
    F = fonts(); cells = []
    for name, (p, caps, tr) in F.items():
        cells.append((name, front(p, caps, tr, WHITE, DEEP)))
    cells.append(("EB Garamond SemiBold on deep green", front(F["EB Garamond SemiBold, caps"][0], True, 0, DEEP, WHITE)))
    cells.append(("Montserrat Bold on purple", front(F["Montserrat Bold, caps"][0], True, 4, PURPLE, WHITE)))
    cells.append(("Young Serif on lime", front(F["Young Serif (new)"][0], True, 0, LIME, DEEP)))
    cols = 4; tw, th = 540, 420; lab = ImageFont.truetype(F["Source Sans 3 SemiBold, caps"][0], 24)
    sheet = Image.new("RGB", (cols * (tw + 20) + 20, ((len(cells) + cols - 1) // cols) * (th + 60) + 20), "#E9E9E6"); d = ImageDraw.Draw(sheet)
    for i, (name, im) in enumerate(cells):
        x, y = 20 + (i % cols) * (tw + 20), 20 + (i // cols) * (th + 60)
        sheet.paste(im.resize((tw, th), Image.LANCZOS), (x, y)); d.text((x, y + th + 12), f"{i + 1}. {name}", font=lab, fill="#222")
    os.makedirs(OUT, exist_ok=True); sheet.save(os.path.join(OUT, "SFW-mug-funny-type-options.jpg"), quality=90)


if __name__ == "__main__":
    main()
