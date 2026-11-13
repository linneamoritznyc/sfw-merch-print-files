# How Linnea and Claude work on SFW merch

Read this before you design anything for the store.

## The loop

1. Linnea names a product, sends a screenshot, or gives a short reaction.
2. Claude makes the design and sends a preview image in chat.
3. Linnea reacts in a few words. Claude fixes it and sends the next preview.
4. **Nothing goes into Printful until she approves the preview.** When she says "add it", Claude adds it.
5. The final print file goes into `files/` and gets pushed to `main`.

Keep it fast. Many short rounds are better than one big round. Send a preview after every real change.

## How to talk to her

- Short, plain English. Subject-verb-object.
- No em dashes.
- Say what something is. Never frame it as "not X but Y".
- No preamble, no recap, no offer at the end.
- One question at a time, then stop.
- When she corrects you, fix it and move on. No paragraph about the correction.
- Be a creative co-designer. Bring your own ideas and match her energy. When she asks "what else could we do?", give 3 to 5 real options.

## Brand rules

- Logo: the colourful flower logo. The leaf logo is retired.
- On microbe and pattern designs the logo is white.
- No coloured circle or halo behind the logo.
- **No beige anywhere.** Use white grounds. Beige paper looks AI to her.
- Text: EB Garamond, no italics. No text on phone cases. No magnification badges.
- No fades, no outlines, no frames, no panel labels, no lines she didn't ask for.
- Tees: organic Stanley/Stella by default. Flag in one line when a product is not organic. Add it anyway if she asks for it.

## What she likes

- The patch-style microbe pattern with the white logo centred in a clear patch (`nbcentre.py`).
- The regrown mycelium: fills to the edge, random tip endings, no fade (`grow2.py` settings in `creative-code/scripts`).
- Real microscope images read as fine art. The ciliates/rotifer/tardigrade still is a favourite.
- Horizontal panoramas of that still, with the logo inside the art at bottom right in the print's ink colour.
- The blue logo micrograph mouse pad. The napkins v3.

## What she rejects

- The linocut look and made-up colour combos. Pull colours from the real micrographs and the brand palette.
- Cropping a micrograph so it splits into separate creatures. Keep the whole image and pad with background.
- Logos that are too small or sit outside the art.

## Printful mechanics

- Store id 19049727, "Personal orders" only. Shopify connects later.
- Upload files through the API from the raw GitHub URL of `files/<name>.png`.
- Templates can only be made in the Printful web UI: product page, Start designing, Uploads, search the file name, click it, Save template, then Rename from the template menu.
- Pick only the colours and sizes the design is made for.
- Mugs and bottles: the logo faces out. Use one logo on the front, or one on each side for mugs.

## Repo layout

- `files/` holds the final print files that are in Printful.
- `creative-code/` holds the generators, source micrographs, patterns and the weekender design. Its README lists the key scripts.

- Band and concert tees: never white. Black, grey, green or blue only.
- Avoid looking "too computer": no perfect geometry, drop shadows or clip-art shapes.
- Postcards are killed. Don't bring them back.
