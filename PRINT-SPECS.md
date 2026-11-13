# SFW print specs for the crispest Printful merch

Sources: Printful help center, file guidelines and blog (Nov 2026), and the embroidery guides from Printify, Fourthwall and Custom Ink. Always check the product's own File guidelines tab too, because each placement has its own pixel size.

## Every file

- **Colour profile:** sRGB IEC61966-2.1, embedded in the PNG. Printful converts sRGB to its own extended CMYK inks. Never send CMYK.
- **Size:** use the exact printfile pixels from the API (`/mockup-generator/printfiles/{product_id}`). Do not upscale. Rebuild the art at size.
- **Resolution:** 300 dpi for paper, stickers, mugs, bottles, phone cases and anything with fine detail. 150 dpi is the floor for apparel. Going above 300 adds nothing.
- **Format:** PNG with transparency for garments. JPG is fine for full-bleed posters, wrapping paper and all-over print, where file size matters (200 MB max).

## DTG (soft, sits in the cotton)

- Best on light cotton. On dark tees the printer lays a white underbase first.
- **No semi-transparent pixels.** Shadows, fades, glows and soft alpha print badly, worst on dark garments. Threshold alpha to 0 or 255. Keep anti-aliasing to a 1 px edge at most.
- Fine detail is fine. Hairlines under about 0.5 pt can break up on dark garments because of the underbase.

## DTFlex (crispest edges, sits on top)

- Use it for dark garments, hoodies, fleece, poly blends and anything where edge sharpness matters most. Printful says it has the crispest edges and the truest colours.
- Avoid big solid blocks on high-flex areas. The film feels firmer there.
- Same file rules as DTG: sRGB, hard alpha, no soft edges.

## Embroidery

- Up to 6 thread colours per placement from the standard 15. Unlimited-colour embroidery is an option.
- Minimum text height 0.25" (6.35 mm). Minimum line 0.05" (1.27 mm). Shapes between 0.05" and 0.5".
- Minimum gap between shapes 0.25" for fill areas.
- Serif fonts under 0.5" lose their serifs. EB Garamond needs 0.5" or more.
- Keep a separate simplified logo for embroidery: thicker roots, no small FOUNDATION word at left-chest size.
- Digitization is a one-time fee per file.

## Sublimation and all-over print

- White cannot be printed. White areas become the fabric colour.
- The design can shift up to 2" in production. Never rely on exact placement near seams.
- Keep logos and text out of seams and edges.

## Paper, mugs, bottles

- 300 dpi at the exact printfile size.
- Mugs wrap: the centre of the file faces away from the handle. Put a logo on each side, or one centred on the front.
- Keep key art inside the safe area marked in the Design Maker.

## Our pipeline checklist

1. Render at the exact printfile pixels, supersampled 2x or more, then downsample with Lanczos.
2. Threshold alpha for garment files: `alpha = 255 if a > 127 else 0`.
3. Embed sRGB: `im.save(path, icc_profile=ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes(), dpi=(300, 300))`.
4. Check thin lines against the method: 0.05" for embroidery, about 1 pt for DTG on dark.
5. Order a sample of every new product before it goes live.
