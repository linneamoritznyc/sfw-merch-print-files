# SFW Field Guide

Accurate, original vector drawings of soil organisms. One page per organism, A4, 300 dpi, text as outlines.
Each drawing is SFW's own, constructed in code and checked against a historical plate and modern photos.
Every page stays a DRAFT until an SFW mentor has checked it.

| No. | Organism | Script | Checked against |
|---|---|---|---|
| 1 | Euglypha (testate amoeba) | euglypha.py | Leidy 1879 pl. XXXV; protisten.de photos of E. tuberculata and E. filifera |
| 3 | Fungal hyphae | fungi.py | standard mycology: septa, aseptate hyphae, clamp connections, look-alikes at one scale |
| 2 | Bacterial-feeding nematode (rhabditid) | nematode.py | standard rhabditid anatomy; still to check against Cobb 1914 (USDA) and modern keys |
| 4 | Flagellates (Bodo type) | pages_4_8.py | standard protistology descriptions |
| 5 | Naked amoebae | pages_4_8.py | standard protistology descriptions |
| 6 | Ciliates (Colpoda) | pages_4_8.py | standard descriptions; cysts per Colpoda life cycle |
| 7 | Bacteria | pages_4_8.py | standard microbiology; same-scale comparison |
| 8 | Microarthropods (oribatid mite, springtail) | pages_4_8.py | standard soil zoology |

Outputs in `out/`: full page SVG and PNG, a preview, and the end-on mouth as a standalone symmetric icon.
Fonts: EB Garamond (OFL, licence in `fonts/`). Scientific names are set in italic, the convention in biology.

Fact check: see `SOURCES.md` for each claim, its source, and what changed.
