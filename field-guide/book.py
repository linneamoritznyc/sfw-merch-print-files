"""SFW Field Guide as a book: front cover, 8 organism pages, back cover. A4 portrait.
Outputs out/sfw-field-guide-book.pptx (for Canva) and out/sfw-field-guide-book.pdf.
Every slide carries its sources, with links, in the speaker notes.

Usage: python3 book.py   (run euglypha.py, nematode.py, fungi.py, pages_4_8.py first)
"""
import io, os
import cairosvg
from PIL import Image
from pptx import Presentation
from pptx.util import Mm
from euglypha import text, aperture_view, DEEP, FWG, LIGHT, WHITE, W, H, HERE, OUT

G6 = "eb-garamond-latin-600-normal.woff2"
LOGOS = os.path.join(HERE, "..", "creative-code", "logos")

USDA_PROTOZOA = "https://webarchive.library.unt.edu/eot2008/20090115191603/http:/soils.usda.gov/sqi/concepts/soil_biology/protozoa.html"
USDA_NEMATODES = "https://webarchive.library.unt.edu/eot2008/20090305025704/http:/soils.usda.gov/sqi/concepts/soil_biology/nematodes.html"
USDA_BACTERIA = "https://webarchive.library.unt.edu/web/20130216082737/http:/soils.usda.gov/sqi/concepts/soil_biology/bacteria.html"

PAGES = [
    ("euglypha", "No. 1 Euglypha (testate amoeba)", [
        ("Shell of silica scales made by the cell; toothed scales at the mouth; species sizes", "https://arcella.nl/euglypha/"),
        ("Euglypha rotunda: 8 to 14 apertural plates, shell 22 to 60 µm", "https://arcella.nl/euglypha-rotunda"),
        ("Euglypha strigosa: 10 to 13 apertural plates, shell 45 to 100 µm", "https://arcella.nl/?p=3010"),
        ("Leidy (1879), Fresh-water Rhizopods of North America, plate XXXV, Euglypha alveolata", "https://archive.org/details/freshwaterrhizop00leid"),
        ("Modern light-microscope photos, Euglypha tuberculata", "https://www.protisten.de/home-new/testatamoeboids-infra/cercozoa-testate2/imbricatea2/euglyphida2/euglypha-tuberculata"),
        ("Modern light-microscope photos, Euglypha filifera", "https://www.protisten.de/home-new/testatamoeboids-infra/cercozoa-testate2/imbricatea2/euglyphida2/euglypha-filifera/")]),
    ("nematode", "No. 2 Bacterial-feeding nematode", [
        ("Size about 1 mm long and 50 µm wide; release of ammonium (USDA Soil Biology Primer, Nematodes)", USDA_NEMATODES),
        ("Bacterial feeders excrete excess nitrogen as ammonia (UC Davis Nemaplex, The Role of Nematodes in Soil Fertility)", "https://nemaplex.ucdavis.edu/Ecology/fertil.htm"),
        ("Bacterial feeders release more inorganic N than fungal feeders (eOrganic)", "https://eorganic.org/node/4495"),
        ("Plant-parasitic nematodes, stylet and size (APS Introduction to Nematodes)", "https://apsnet.org/edcenter/Pages/IntroNematodes.aspx")]),
    ("fungi", "No. 3 Fungal hyphae", [
        ("Hyphae average 4 to 6 µm wide (Hyphae overview)", "https://graphsearch.epfl.ch/en/concept/51480"),
        ("Actinobacteria 1 to 1.5 µm; beneficial fungi usually wider than 2.5 µm (Soil Food Web teaching material)", "https://pt.soilfoodweb.com/?p=2331"),
        ("Root hairs about 10 to 17 µm wide (Root hair)", "https://www.wikipedia.org/wiki/Root_hair")]),
    ("flagellate", "No. 4 Flagellates", [
        ("Flagellates are the smallest protozoa; protozoa release ammonium (USDA Soil Biology Primer, Protozoa)", USDA_PROTOZOA),
        ("Bodo saltans: 5 to 8 µm, two unequal flagella from a flagellar pocket, kinetoplast near their base (fine-structure study)", "https://archive.org/download/biostor-266060/biostor-266060.pdf"),
        ("Short flagellum sweeps food in, long flagellum moves the cell (Kinetoplastids)", "https://www.microscopemaster.com/kinetoplastids.html")]),
    ("amoeba", "No. 5 Naked amoebae", [
        ("Amoebae are between flagellates and ciliates in size (USDA Soil Biology Primer, Protozoa)", USDA_PROTOZOA),
        ("About 10,000 to 100,000 naked amoebae per gram of soil (Soil Ecology Wiki, Naked amoebae)", "https://soil.evs.buffalo.edu/index.php/Naked_amoebae"),
        ("Small, flexible amoebae graze bacteria in pores others cannot reach", "https://www.academia.edu/94782295")]),
    ("ciliate", "No. 6 Ciliates", [
        ("Ciliates are the largest and least numerous protozoa (USDA Soil Biology Primer, Protozoa)", USDA_PROTOZOA),
        ("Colpoda division cyst gives 2, 4 (most often) or 8 cells (Archiv für Protistenkunde 88, 1936)", "https://www.zobodat.at/pdf/Archiv-fuer-Protistenkunde_88_1936_0366-0373.pdf"),
        ("Some colpodean ciliates are as small as 10 µm (Ciliate)", "https://www.wikipedia.org/wiki/Ciliate"),
        ("Many ciliates point to low oxygen, Soil Food Web method (Elaine Ingham, 2015)", "https://lists.ibiblio.org/sympa/arc/permaculture/2015-08/msg00064.html"),
        ("Ciliates as indicators of anaerobic conditions (practitioner using the method)", "https://humankindoregon.com/soil-science")]),
    ("bacteria", "No. 7 Bacteria", [
        ("100 million to 1 billion bacteria per teaspoon of productive soil (USDA Soil Biology Primer, Bacteria)", USDA_BACTERIA),
        ("Direct counts are about 10^9 to 10^11 bacteria per gram (Introduction to Microbiology, University of Reading)", "https://futurelearn.com/info/courses/introduction-to-microbiology/0/steps/51421"),
        ("Actinobacteria filament width 1 to 1.5 µm (Soil Food Web teaching material)", "https://pt.soilfoodweb.com/?p=2331")]),
    ("microarthropods", "No. 8 Microarthropods", [
        ("Oribatid mites 0.2 to 1 mm (Massey University, Soil mites)", "https://soilbugs.massey.ac.nz/acari.php"),
        ("Springtails 0.2 to 5 mm (Massey University, Soil mites and other animals)", "https://www.massey.ac.nz/~maminor/mites.html"),
        ("Springtail anatomy: ventral tube, catch and spring (collembola.org, F. Janssens)", "https://collembola.org/taxa/collembo.htm"),
        ("Ventral tube on abdominal segment 1, spring on segment 4 (EvoDevo 5:2, 2014)", "https://link.springer.com/doi/10.1186/2041-9139-5-2"),
        ("Mites and springtails shred litter and graze fungi (SARE, Farming with Soil Life)", "https://www.sare.org/publications/farming-with-soil-life/mesofauna-arthropods/")]),
]


def render(svg):
    return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(), output_width=W, output_height=H))).convert("RGBA")


def cover():
    M = 170
    b = [f'<rect width="{W}" height="{H}" fill="{WHITE}"/>',
         text("SOIL FOOD WEB FOUNDATION", 40, W / 2, 330, fnt=G6, anchor="middle", track=220, color=FWG)[0],
         text("Field Guide", 230, W / 2, 620, anchor="middle")[0],
         text("to Soil Life", 150, W / 2, 800, anchor="middle")[0],
         aperture_view(W / 2, 1720, 620, w=6),
         text("Eight organisms you will meet at the microscope", 60, W / 2, 2640, anchor="middle")[0],
         text("Testate amoebae  ·  Nematodes  ·  Fungi  ·  Flagellates", 42, W / 2, 2760, anchor="middle", color=FWG)[0],
         text("Naked amoebae  ·  Ciliates  ·  Bacteria  ·  Microarthropods", 42, W / 2, 2830, anchor="middle", color=FWG)[0]]
    im = render(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{"".join(b)}</svg>')
    logo = Image.open(os.path.join(LOGOS, "SFW-logo-flower-colour.png")).convert("RGBA"); logo.thumbnail((300, 300))
    im.alpha_composite(logo, ((W - logo.width) // 2, H - 170 - logo.height))
    return im.convert("RGB")


def back():
    M = 260
    lines = ["Every organism in this guide is drawn to show what you",
             "actually see at the microscope: the parts that tell you",
             "what it is, its true size, and what it does in the soil.",
             "",
             "Each fact is checked against a published source.",
             "The sources are listed in the notes of each page."]
    b = [f'<rect width="{W}" height="{H}" fill="{DEEP}"/>',
         text("Field Guide to Soil Life", 110, W / 2, 900, anchor="middle", color=WHITE)[0]]
    for i, l in enumerate(lines):
        if not l:
            continue
        b.append(text(l, 52, W / 2, 1150 + i * 78, anchor="middle", color=WHITE)[0])
    im = render(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{"".join(b)}</svg>')
    logo = Image.open(os.path.join(LOGOS, "SFW-logo-flower-white-3000.png")).convert("RGBA"); logo.thumbnail((420, 420))
    im.alpha_composite(logo, ((W - logo.width) // 2, H - 560 - logo.height + 380))
    return im.convert("RGB")


def main():
    cv, bk = cover(), back()
    cv.save(os.path.join(OUT, "book-cover.png"), dpi=(300, 300)); bk.save(os.path.join(OUT, "book-back.png"), dpi=(300, 300))
    slides = [("book-cover", "Front cover", [])] + PAGES + [("book-back", "Back cover", [])]
    prs = Presentation()
    prs.slide_width, prs.slide_height = Mm(210), Mm(297)
    blank = prs.slide_layouts[6]
    pdf_pages = []
    for key, title, sources in slides:
        path = os.path.join(OUT, f"{key}.png" if key.startswith("book-") else f"{key}-field-guide.png")
        s = prs.slides.add_slide(blank)
        s.shapes.add_picture(path, 0, 0, width=prs.slide_width, height=prs.slide_height)
        tf = s.notes_slide.notes_text_frame
        tf.text = title + (". Sources:" if sources else ". Soil Food Web Foundation, Field Guide to Soil Life.")
        for i, (label_, url) in enumerate(sources, 1):
            p = tf.add_paragraph()
            r1 = p.add_run(); r1.text = f"{i}. {label_}: "
            r2 = p.add_run(); r2.text = url; r2.hyperlink.address = url
        pdf_pages.append(Image.open(path).convert("RGB"))
    prs.save(os.path.join(OUT, "sfw-field-guide-book.pptx"))
    pdf_pages[0].save(os.path.join(OUT, "sfw-field-guide-book.pdf"), save_all=True, append_images=pdf_pages[1:], resolution=300)
    sheet = Image.new("RGB", (5 * 500, 2 * 707), "white")
    for k, im in enumerate(pdf_pages):
        t = im.copy(); t.thumbnail((490, 693)); sheet.paste(t, ((k % 5) * 500 + 5, (k // 5) * 707 + 7))
    sheet.save(os.path.join(OUT, "book-spreads-preview.png"))


if __name__ == "__main__":
    main()
