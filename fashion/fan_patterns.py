"""SFW textile repeats built only from the Haeckel flagellate fan (the engraved colonial flagellate the team loves).
Every repeat is seamless and mirror-symmetric.
  rosette    four fans meeting at their stalks, a round medallion in a half-drop          (block-print shirt)
  monogram   fans up and down, interlocking crowns between stalks, tight brick              (monogram jacquard)
  damask     fan over fan, crowns meeting, columns in half-drop                            (damask)
  stripe     a band of small fans alternating up and down, for side stripes and waistbands
Output out/fan/<name>-<colourway>.svg (vector) and .png (tile, 300 dpi).
"""
import io, os, re
import cairosvg
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "fan")
FAN = os.path.join(HERE, "..", "creative-code", "patterns", "haeckel", "icon", "canva", "sfw-haeckel-flagellate-fan-black.svg")

WAYS = {   # ground, ink
    "sage-black": ("#B3BEB1", "#111111"),
    "forest-white": ("#22371F", "#FFFFFF"),
    "white-green": ("#FFFFFF", "#156826"),
    "sage-forest": ("#B3BEB1", "#22371F"),
    "black-lightgreen": ("#111111", "#59A66C"),
}

# fan geometry in its own file: stalk base at (2254, 4200), crown top at y 308, half width 1710
BX, BY, FH = 2254, 4200, 3892
raw = open(FAN).read()
TR = re.search(r'transform="([^"]+)"', raw).group(1)
D = re.search(r' d="([^"]+)"', raw).group(1)


def fan(x, y, h, rot=0, flip=False):
    """Fan with its stalk base at (x, y), height h, rotated rot degrees; flip mirrors left-right."""
    s = h / FH
    fx = -s if flip else s
    return f'<use href="#fan" transform="translate({x:.2f},{y:.2f}) rotate({rot}) scale({fx:.6f},{s:.6f}) translate({-BX},{-BY})"/>'


def tile_svg(w, h, items, ground, ink):
    copies = []
    for dx in (-w, 0, w):
        for dy in (-h, 0, h):
            copies.append(f'<g transform="translate({dx},{dy})">{"".join(items)}</g>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'<defs><path id="fan" transform="{TR}" d="{D}"/><clipPath id="c"><rect width="{w}" height="{h}"/></clipPath></defs>'
            f'<rect width="{w}" height="{h}" fill="{ground}"/><g clip-path="url(#c)" fill="{ink}" fill-rule="evenodd">{"".join(copies)}</g></svg>\n')


def rosette():
    h = 300; R = 2 * h + 40; w, H = R * 1.06, R * 1.06        # half-drop: second rosette in the centre of the cell
    items = []
    for cx, cy in ((0, 0), (w / 2, H / 2)):
        for a in (0, 90, 180, 270):
            items.append(fan(cx, cy, h, a))
    for cx, cy in ((w / 2, 0), (0, H / 2)):                     # small four-fan knot between the rosettes
        for a in (45, 135, 225, 315):
            items.append(fan(cx, cy, h * .42, a))
    return w, H, items


def monogram():
    h = 300; w = h * .98; H = h * 1.02
    items = [fan(0, 0, h), fan(w, 0, h), fan(w / 2, -H, h, 180), fan(w / 2, 0, h, 180)]
    # shift so the up fan bases sit on the bottom edge of the cell
    return w, H, [f'<g transform="translate(0,{H})">{"".join(items)}</g>']


def damask():
    h = 300; w = h * 1.0; H = 2 * h
    items = []
    for x, y0 in ((0, 0), (w, 0), (w / 2, H / 2)):
        items += [fan(x, y0 + h * 1.0, h), fan(x, y0 - h * 1.0, h, 180)]
    return w * 1.0, H, items


def stripe():
    h = 120; w = h * 1.0; H = h * 2.3
    items = [fan(0, H / 2 + h * .05 + h / 2, h), fan(w / 2, H / 2 - h * .05 - h / 2, h, 180)]
    rule = f'<rect x="-10" y="6" width="{w + 20}" height="8"/><rect x="-10" y="{H - 14}" width="{w + 20}" height="8"/>'
    return w, H, items + [rule]


PATTERNS = {"rosette": rosette, "monogram": monogram, "damask": damask, "stripe": stripe}


def main():
    os.makedirs(OUT, exist_ok=True)
    board = []
    for name, fn in PATTERNS.items():
        w, h, items = fn()
        for way, (g, ink) in WAYS.items():
            svg = tile_svg(w, h, items, g, ink)
            open(os.path.join(OUT, f"{name}-{way}.svg"), "w").write(svg)
            k = 2400 / max(w, h)                              # tile at about 8 in, 300 dpi
            im = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(), output_width=int(w * k), output_height=int(h * k)))).convert("RGB")
            im.save(os.path.join(OUT, f"{name}-{way}.png"), dpi=(300, 300))
            board.append((name, way, im, w, h))
    # swatch board: each tile repeated at the scale it would sit on a garment
    cell = 640
    names, ways = list(PATTERNS), list(WAYS)
    sheet = Image.new("RGB", (len(ways) * (cell + 20) + 20, len(names) * (cell + 20) + 20), "white")
    for name, way, im, w, h in board:
        sc = (1.0 if name != "stripe" else 1.0) * cell / 2.2 / max(w, h) * max(w, h) / max(w, h)
        t = im.resize((max(1, int(w * .9)), max(1, int(h * .9))), Image.LANCZOS)
        sw = Image.new("RGB", (cell, cell))
        for x in range(0, cell, t.width):
            for y in range(0, cell, t.height):
                sw.paste(t, (x, y))
        sheet.paste(sw, (20 + ways.index(way) * (cell + 20), 20 + names.index(name) * (cell + 20)))
    sheet.save(os.path.join(OUT, "swatch-board.png"))


if __name__ == "__main__":
    main()
