# SFW creative code

Pattern and generative art work for the SFW merch store. Every file in `../files` is a final print file that is already on Printful.

## Folders

- `scripts/` holds the Python generators (Pillow, NumPy, SciPy). Most of them read from `source-micrographs/` and `logos/`.
- `source-micrographs/` holds the student 40x micrographs and the ciliates/rotifer/tardigrade video still.
- `patterns/` holds outputs: mosaics, tiles, all-over prints, mycelium growth, microbe-library palettes and panoramas.
- `weekender/` holds the weekender bag cut-out design and related cut-out experiments.
- `logos/` holds the brand logos. Use the flower logo. The leaf logo is retired.

## Key scripts

- `teehq.py` builds the Voronoi micrograph collage (`field()`).
- `nbcentre.py` builds the microbe pattern with a white logo in a cleared patch (`cover()`).
- `grow2.py` grows the space-filling mycelium.
- `deskmosaic.py` builds the pixel mosaic desk mat.
- `archival.py` builds the high-res tone field and line screen used for the panoramas.
- `cutout.py` builds the weekender cut-out design.
- `aop*.py`, `discs.py` and `tee_quilt*.py` build the seamless tiles and all-over patterns.

Paths inside the scripts point to `/home/claude/merch/...`. Change them to the folders here.

## Brand rules

- Use the colourful flower logo. On microbe patterns the logo is white.
- No beige. No coloured circle or halo behind the logo.
- Text is EB Garamond, no italics. No text on phone cases.
- No fades and no outlines.
